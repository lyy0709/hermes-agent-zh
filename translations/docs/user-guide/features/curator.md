---
sidebar_position: 3
title: "技能策展器"
description: "对 Agent 创建技能的背景维护——使用跟踪、陈旧性、归档和 LLM 驱动的审查"
---

# 技能策展器

技能策展器是用于 **Agent 创建技能** 的后台维护流程。它跟踪每个技能被查看、使用和修补的频率，将长期未使用的技能在 `活跃 → 陈旧 → 已归档` 状态间移动，并定期启动一个简短的辅助模型审查，提出合并或修补偏离的建议。

它的存在是为了防止通过[自我改进循环](/docs/user-guide/features/skills#agent-managed-skills-skill_manage-tool)创建的技能无限堆积。每次 Agent 解决一个新问题并保存一个技能时，该技能就会进入 `~/.hermes/skills/`。如果没有维护，最终会积累数十个狭窄的近似重复项，污染目录并浪费 Token。

技能策展器 **绝不触碰** 捆绑技能（随仓库发布）或从 Hub 安装的技能（来自 [agentskills.io](https://agentskills.io)）。它只审查 Agent 自身创建的技能。它也 **绝不自动删除** ——最坏的结果是归档到 `~/.hermes/skills/.archive/`，这是可恢复的。

跟踪 [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 运行机制

技能策展器由非活动检查触发，而非定时任务守护进程。在 CLI 会话开始时，以及在消息网关的定时任务线程的循环周期中，Hermes 会检查：

1.  自上次策展器运行以来是否已过去足够时间（`interval_hours`，默认 **7 天**），以及
2.  Agent 是否已空闲足够长时间（`min_idle_hours`，默认 **2 小时**）。

如果两者都为真，它会生成一个 `AIAgent` 的后台分支——这与记忆/技能自我改进提示使用的模式相同。该分支在其自己的提示词缓存中运行，绝不接触活跃的对话。

一次运行包含两个阶段：

1.  **自动状态转换**（确定性的，不使用 LLM）。未使用超过 `stale_after_days`（30 天）的技能变为 `陈旧`；未使用超过 `archive_after_days`（90 天）的技能被移动到 `~/.hermes/skills/.archive/`。
2.  **LLM 审查**（单次辅助模型运行，`max_iterations=8`）。分支 Agent 会调查 Agent 创建的技能，可以使用 `skill_view` 读取其中任何一个，并针对每个技能决定是保留、修补（通过 `skill_manage`）、合并重叠的技能，还是通过终端工具归档。

已固定的技能对技能策展器的自动转换和 Agent 自身的 `skill_manage` 工具都是禁区。请参阅下面的[固定技能](#pinning-a-skill)。

## 配置

所有设置都位于 `config.yaml` 中的 `curator:` 下（不在 `.env` 中——这不是机密）。默认值：

```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 天
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
```

要完全禁用，请设置 `curator.enabled: false`。

### 在更便宜的辅助模型上运行审查

技能策展器的 LLM 审查流程是一个常规的辅助任务槽位——`auxiliary.curator`——与视觉、压缩、会话搜索等并列。"Auto" 意味着"使用我的主聊天模型"；覆盖此槽位可以将审查流程固定到特定的提供商 + 模型。

**最简单的方式——`hermes model`：**

```bash
hermes model                   # → "辅助模型 — 侧任务路由"
                               # → 选择 "Curator" → 选择提供商 → 选择模型
```

相同的选择器在 Web 仪表板的 **Models** 选项卡下可用。

**直接配置 config.yaml（等效）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # 宽松设置 — 审查可能需要几分钟
```

保留 `provider: auto`（默认值）会将审查流程路由到您的主聊天模型，与其他所有辅助任务的行为一致。

:::note 旧版配置
早期版本使用了一次性的 `curator.auxiliary.{provider,model}` 块。该路径仍然有效，但会发出弃用日志行——请迁移到上面的 `auxiliary.curator`，以便技能策展器与其他所有辅助任务共享相同的基础设施（`hermes model`、仪表板 Models 选项卡、`base_url`、`api_key`、`timeout`、`extra_body`）。
:::

## CLI

```bash
hermes curator status         # 上次运行时间、计数、固定列表、LRU 前 5 名
hermes curator run            # 立即触发审查（默认后台运行）
hermes curator run --sync     # 同上，但阻塞直到 LLM 流程完成
hermes curator pause          # 暂停运行直到恢复
hermes curator resume
hermes curator pin <skill>    # 永不自动转换此技能
hermes curator unpin <skill>
hermes curator restore <skill>  # 将已归档技能移回活跃状态
```

`hermes curator status` 还会列出五个最近最少使用的技能——这是快速查看哪些技能可能即将变陈旧的方法。

相同的子命令在运行中的会话（CLI 或消息网关平台）内可作为 `/curator` 斜杠命令使用。

## "Agent 创建"的含义

如果一个技能的名称 **不** 在以下文件中，则被视为 Agent 创建：

-   `~/.hermes/skills/.bundled_manifest`（安装时从仓库复制的技能），以及
-   `~/.hermes/skills/.hub/lock.json`（通过 `hermes skills install` 安装的技能）。

`~/.hermes/skills/` 中的所有其他内容都是技能策展器的处理对象。这包括：

-   Agent 在对话期间通过 `skill_manage(action="create")` 保存的技能。
-   您手动创建的、手写 `SKILL.md` 的技能。
-   通过您为 Hermes 指定的外部技能目录添加的技能。

如果您想保护某个特定技能不被触碰——例如您依赖的手写技能——请使用 `hermes curator pin <name>`。请参阅下一节。

## 固定技能

固定是对自动化和 Agent 驱动更改的硬性防护。一旦技能被固定：

-   **技能策展器** 在自动转换（`活跃 → 陈旧 → 已归档`）期间跳过它，并且其 LLM 审查流程被指示不要动它。
-   **Agent 的 `skill_manage` 工具** 拒绝对其进行任何写入操作。对 `edit`、`patch`、`delete`、`write_file` 和 `remove_file` 的调用会返回一个拒绝信息，告诉模型要求用户运行 `hermes curator unpin <name>`。这可以防止 Agent 在对话中静默重写一个技能。

使用以下命令固定和取消固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志作为 `"pinned": true` 存储在技能在 `~/.hermes/skills/.usage.json` 中的条目上，因此可以在会话间保留。

只有 **Agent 创建** 的技能可以被固定——捆绑和从 Hub 安装的技能首先就不受技能策展器变更的影响，如果您尝试固定它们，`hermes curator pin` 会拒绝并给出解释性消息。

如果您需要自己更新一个固定的技能，请直接用编辑器编辑 `~/.hermes/skills/<name>/SKILL.md`。固定只保护 Agent 的工具路径，而不保护您自己的文件系统访问。

## 使用遥测

技能策展器在 `~/.hermes/skills/.usage.json` 维护一个伴随文件，每个技能有一个条目：

```json
{
  "my-skill": {
    "use_count": 12,
    "view_count": 34,
    "last_used_at": "2026-04-24T18:12:03Z",
    "last_viewed_at": "2026-04-23T09:44:17Z",
    "patch_count": 3,
    "last_patched_at": "2026-04-20T22:01:55Z",
    "created_at": "2026-03-01T14:20:00Z",
    "state": "active",
    "pinned": false,
    "archived_at": null
  }
}
```

计数器在以下情况下递增：

-   `view_count`：Agent 对该技能调用 `skill_view`。
-   `use_count`：技能被加载到对话的提示词中。
-   `patch_count`：在技能上运行 `skill_manage patch/edit/write_file/remove_file`。

捆绑和从 Hub 安装的技能明确排除在遥测写入之外。

## 每次运行报告

每次技能策展器运行都会在 `~/.hermes/logs/curator/` 下写入一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # 机器可读：完整保真度、统计信息、LLM 输出
    └── REPORT.md     # 人类可读摘要
```

`REPORT.md` 是查看给定运行所做操作的快速方式——哪些技能转换了状态，LLM 审查者说了什么，修补了哪些技能。对于无需 grep `agent.log` 的审计很有用。

## 恢复已归档技能

如果技能策展器归档了您仍然需要的技能：

```bash
hermes curator restore <skill-name>
```

这将技能从 `~/.hermes/skills/.archive/` 移回活跃树，并将其状态重置为 `active`。如果之后有捆绑或从 Hub 安装的同名技能被安装（会遮蔽上游），恢复操作会拒绝。

## 按执行环境禁用

技能策展器默认启用。要关闭它：

-   **仅针对一个配置文件：** 编辑 `~/.hermes/config.yaml`（或活跃配置文件的配置）并设置 `curator.enabled: false`。
-   **仅针对一次运行：** `hermes curator pause` ——暂停状态在会话间持续；使用 `resume` 重新启用。

如果 `min_idle_hours` 尚未过去，技能策展器也会拒绝运行，因此在活跃的开发机器上，它自然只会在安静时段运行。

## 另请参阅

-   [技能系统](/docs/user-guide/features/skills) —— 技能的一般工作原理以及创建它们的自我改进循环
-   [记忆](/docs/user-guide/features/memory) —— 维护长期记忆的并行后台审查
-   [捆绑技能目录](/docs/reference/skills-catalog)
-   [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) —— 原始提案和设计讨论