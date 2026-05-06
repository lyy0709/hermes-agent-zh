---
sidebar_position: 3
title: "技能管理员"
description: "对 Agent 创建技能的背景维护——使用跟踪、陈旧度、归档和 LLM 驱动的审查"
---

# 技能管理员

技能管理员是对 **Agent 创建技能** 的一项背景维护流程。它跟踪每个技能的查看、使用和修补频率，将长期未使用的技能在 `活跃 → 陈旧 → 归档` 状态间移动，并定期启动一个简短的辅助模型审查，提出合并或修补偏离的建议。

它的存在是为了防止通过[自我改进循环](/docs/user-guide/features/skills#agent-managed-skills-skill_manage-tool)创建的技能无限堆积。每次 Agent 解决一个新问题并保存一个技能时，该技能就会存放在 `~/.hermes/skills/` 中。如果没有维护，最终会积累大量狭窄且近乎重复的技能，污染目录并浪费 Token。

技能管理员 **绝不触碰** 捆绑技能（随仓库发布）或从中心安装的技能（来自 [agentskills.io](https://agentskills.io)）。它只审查 Agent 自身创作的技能。它也 **绝不自动删除** —— 最坏的结果是归档到 `~/.hermes/skills/.archive/`，这是可恢复的。

跟踪 [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 运行机制

技能管理员由非活动检查触发，而非定时任务守护进程。在 CLI 会话开始时，以及在消息网关的定时任务线程的周期性触发中，Hermes 会检查是否满足以下条件：

1. 距离上次技能管理员运行已过去足够时间 (`interval_hours`，默认 **7 天**)，且
2. Agent 已空闲足够长时间 (`min_idle_hours`，默认 **2 小时**)。

如果两者都为真，它会启动一个 `AIAgent` 的后台分支——这与记忆/技能自我改进提示所使用的模式相同。该分支在其自己的提示词缓存中运行，绝不接触活跃的会话。

:::info 首次运行行为
在全新安装（或预技能管理员版本在 `hermes update` 后首次触发）时，技能管理员 **不会立即运行**。首次观察会将 `last_run_at` 设置为“现在”，并将第一次真正的运行推迟一个完整的 `interval_hours` 周期。这为您提供了一个完整的周期来审查您的技能库，固定任何重要内容，或在技能管理员接触它们之前完全退出。

如果您想在技能管理员实际运行之前查看它 *将会* 做什么，请运行 `hermes curator run --dry-run` —— 它会生成相同的审查报告，但不会修改技能库。
:::

一次运行包含两个阶段：

1.  **自动转换**（确定性的，无需 LLM）。未使用超过 `stale_after_days` (30) 的技能变为 `陈旧`；未使用超过 `archive_after_days` (90) 的技能将被移动到 `~/.hermes/skills/.archive/`。
2.  **LLM 审查**（单次辅助模型运行，`max_iterations=8`）。分支 Agent 会调查 Agent 创建的技能，可以使用 `skill_view` 读取其中任何一个，并针对每个技能决定是保留、修补（通过 `skill_manage`）、合并重叠的技能，还是通过终端工具归档。

固定的技能对技能管理员的自动转换和 Agent 自身的 `skill_manage` 工具都是禁止访问的。请参阅下面的[固定技能](#pinning-a-skill)。

## 配置

所有设置都位于 `config.yaml` 中的 `curator:` 下（不在 `.env` 中——这不是秘密）。默认值：

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

技能管理员的 LLM 审查流程是一个常规的辅助任务槽位——`auxiliary.curator`——与视觉、压缩、会话搜索等并列。“自动”意味着“使用我的主聊天模型”；覆盖此槽位可以将审查流程固定到特定的提供商 + 模型。

**最简单的方式——`hermes model`：**

```bash
hermes model                   # → "辅助模型 — 侧任务路由"
                               # → 选择 "Curator" → 选择提供商 → 选择模型
```

相同的选择器在 Web 仪表板的 **Models** 选项卡下可用。

**直接配置 config.yaml（等效方式）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # 宽松设置 — 审查可能需要几分钟
```

保留 `provider: auto`（默认值）会将审查流程路由到您的主聊天模型，与其他所有辅助任务的行为一致。

:::note 旧版配置
早期版本使用了一个独立的 `curator.auxiliary.{provider,model}` 块。该路径仍然有效，但会输出弃用日志行——请迁移到上面的 `auxiliary.curator`，以便技能管理员与其他所有辅助任务共享相同的管道（`hermes model`、仪表板 Models 选项卡、`base_url`、`api_key`、`timeout`、`extra_body`）。
:::

## CLI

```bash
hermes curator status         # 上次运行时间、计数、固定列表、最近最少使用的前 5 项
hermes curator run            # 立即触发审查（默认在后台运行）
hermes curator run --sync     # 同上，但阻塞直到 LLM 流程完成
hermes curator run --dry-run  # 仅预览 — 报告而不进行任何修改
hermes curator backup         # 手动拍摄 ~/.hermes/skills/ 的快照
hermes curator rollback       # 从最新的快照恢复
hermes curator rollback --list     # 列出可用的快照
hermes curator rollback --id <ts>  # 恢复特定的快照
hermes curator rollback -y         # 跳过确认提示
hermes curator pause          # 暂停运行直到恢复
hermes curator resume
hermes curator pin <skill>    # 永不自动转换此技能
hermes curator unpin <skill>
hermes curator restore <skill>  # 将归档的技能移回活跃状态
```

## 备份和回滚

在每次真正的技能管理员运行之前，Hermes 会在 `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz` 处拍摄 `~/.hermes/skills/` 的 tar.gz 快照。如果某次运行归档或合并了您不希望被触及的内容，您可以使用一个命令撤销整个运行：

```bash
hermes curator rollback        # 恢复最新的快照（带确认）
hermes curator rollback -y     # 跳过提示
hermes curator rollback --list # 查看所有快照及其原因 + 大小
```
回滚操作本身是可逆的：在替换技能树之前，Hermes 会拍摄另一个标记为 `pre-rollback to <target-id>` 的快照，因此错误的回滚可以通过 `--id` 参数向前滚动到该快照来撤销。

你也可以随时使用 `hermes curator backup --reason "before-refactor"` 手动创建快照。`--reason` 字符串会保存在快照的 `manifest.json` 中，并在 `--list` 命令中显示。

快照会被修剪到 `curator.backup.keep`（默认为 5）的数量，以限制磁盘使用：

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

将 `curator.backup.enabled` 设置为 `false` 以禁用自动快照。当备份被禁用时，手动命令 `hermes curator backup` 仍然有效，但前提是你需要先将 `enabled` 设置为 `true` —— 这个标志对称地控制着两条路径，因此不可能在变更性运行中意外跳过运行前的快照。

`hermes curator status` 也会列出五个最近最少使用的技能 —— 这是快速查看哪些技能可能即将过期的好方法。

在运行中的会话（CLI 或消息网关平台）中，相同的子命令可以作为 `/curator` 斜杠命令使用。

## "Agent 创建"的含义

如果一个技能的名称**不**在以下文件中，则被视为 Agent 创建的：

- `~/.hermes/skills/.bundled_manifest`（安装时从仓库复制的技能），以及
- `~/.hermes/skills/.hub/lock.json`（通过 `hermes skills install` 安装的技能）。

`~/.hermes/skills/` 目录中的其他所有内容都是 curator 可以处理的对象。这包括：

- Agent 在对话期间通过 `skill_manage(action="create")` 保存的技能。
- 你手动编写的 `SKILL.md` 文件创建的技能。
- 通过你为 Hermes 指定的外部技能目录添加的技能。

:::warning 你手写的技能与 Agent 保存的技能看起来相同
这里的来源是**二元的**（捆绑/中心安装 vs. 其他所有）。curator 无法区分你为私有工作流手动编写的技能与自改进循环在会话中保存的技能。两者都属于 "Agent 创建" 的范畴。

在第一次实际运行之前（默认在安装后 7 天），请花点时间：

1. 运行 `hermes curator run --dry-run` 以准确查看 curator 会提议什么。
2. 使用 `hermes curator pin <name>` 来保护你不想被触及的任何内容。
3. 或者，如果你更愿意自己管理技能库，可以在 `config.yaml` 中设置 `curator.enabled: false`。

存档总是可以通过 `hermes curator restore <name>` 恢复，但事先固定比事后追查合并更容易。
:::

如果你想保护某个特定技能不被触及 —— 例如你依赖的手写技能 —— 请使用 `hermes curator pin <name>`。请参阅下一节。

## 固定技能

固定可以保护技能不被删除 —— 包括 curator 的自动存档过程以及 Agent 的 `skill_manage(action="delete")` 工具调用。一旦技能被固定：

- **curator** 在自动转换（`active → stale → archived`）期间会跳过它，并且其 LLM 审查过程会被指示不要动它。
- **Agent 的 `skill_manage` 工具** 会拒绝对其执行 `delete` 操作，并提示用户使用 `hermes curator unpin <name>`。补丁和编辑仍然可以通过，因此 Agent 可以在发现问题时改进固定技能的内容，而无需进行固定/取消固定/重新固定的繁琐操作。

使用以下命令进行固定和取消固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志作为 `"pinned": true` 存储在技能在 `~/.hermes/skills/.usage.json` 中的条目上，因此它会在会话之间持续存在。

只有 **Agent 创建的** 技能可以被固定 —— 捆绑和中心安装的技能首先就不受 curator 变更的影响，如果你尝试固定它们，`hermes curator pin` 会拒绝并给出解释性消息。

如果你想要比 "不删除" 更强的保证 —— 例如，在 Agent 仍然读取技能时完全冻结其内容 —— 请直接使用编辑器编辑 `~/.hermes/skills/<name>/SKILL.md`。固定保护的是工具驱动的删除，而不是你自己的文件系统访问。

## 使用遥测

curator 在 `~/.hermes/skills/.usage.json` 维护一个伴生文件，每个技能有一个条目：

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

- `view_count`：Agent 对该技能调用 `skill_view`。
- `use_count`：技能被加载到对话的提示词中。
- `patch_count`：在技能上运行 `skill_manage patch/edit/write_file/remove_file`。

捆绑和中心安装的技能明确排除在遥测写入之外。

## 每次运行报告

每次 curator 运行都会在 `~/.hermes/logs/curator/` 下写入一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # 机器可读：完整保真度、统计信息、LLM 输出
    └── REPORT.md     # 人类可读的摘要
```

`REPORT.md` 是查看给定运行做了什么的好方法 —— 哪些技能发生了转换，LLM 审查者说了什么，它修补了哪些技能。对于审计来说很方便，无需 grep `agent.log`。

## 恢复已存档的技能

如果 curator 存档了你仍然需要的内容：

```bash
hermes curator restore <skill-name>
```

这将把技能从 `~/.hermes/skills/.archive/` 移回活动树，并将其状态重置为 `active`。如果之后有捆绑或中心安装的技能以相同名称安装（会遮蔽上游），恢复操作将被拒绝。

## 按执行环境禁用

curator 默认是启用的。要关闭它：

- **仅针对一个配置文件：** 编辑 `~/.hermes/config.yaml`（或活动配置文件的配置）并设置 `curator.enabled: false`。
- **仅针对一次运行：** `hermes curator pause` —— 暂停会在会话之间持续；使用 `resume` 重新启用。

如果 `min_idle_hours` 尚未过去，curator 也会拒绝运行，因此在活跃的开发机器上，它自然只会在安静时段运行。
## 另请参阅

- [技能系统](/docs/user-guide/features/skills) — 技能的一般工作原理以及创建它们的自我改进循环
- [记忆](/docs/user-guide/features/memory) — 维护长期记忆的并行后台审查
- [捆绑技能目录](/docs/reference/skills-catalog)
- [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) — 原始提案和设计讨论