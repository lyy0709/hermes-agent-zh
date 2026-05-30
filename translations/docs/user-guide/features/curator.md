---
sidebar_position: 3
title: "技能管理员"
description: "为 Agent 创建的技能提供后台维护——使用跟踪、陈旧性、归档和 LLM 驱动的审查"
---

# 技能管理员

技能管理员是 **Agent 创建的技能** 的后台维护流程。它跟踪每个技能的查看、使用和修补频率，将长期未使用的技能在 `活跃 → 陈旧 → 归档` 状态之间移动，并定期生成一个简短的辅助模型审查，提出合并或修补偏离的建议。

它的存在是为了防止通过 [自我改进循环](/user-guide/features/skills#agent-managed-skills-skill_manage-tool) 创建的技能无限堆积。每次 Agent 解决一个新问题并保存一个技能时，该技能就会进入 `~/.hermes/skills/`。如果没有维护，最终会积累数十个狭窄的、近乎重复的技能，污染目录并浪费 Token。

技能管理员 **绝不触碰** 捆绑技能（随仓库发布）或从 Hub 安装的技能（来自 [agentskills.io](https://agentskills.io)）。它只审查 Agent 自身创建的技能。它也 **绝不自动删除** ——最坏的结果是归档到 `~/.hermes/skills/.archive/`，这是可恢复的。

跟踪 [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 运行方式

技能管理员由非活动检查触发，而非定时任务守护进程。在 CLI 会话开始时，以及在消息网关的定时任务线程的周期性触发中，Hermes 会检查：

1. 距离上次技能管理员运行是否已过去足够时间（`interval_hours`，默认 **7 天**），以及
2. Agent 是否已空闲足够长时间（`min_idle_hours`，默认 **2 小时**）。

如果两者都为真，它会生成一个 `AIAgent` 的后台分支——这与记忆/技能自我改进提示使用的模式相同。该分支在其自己的提示词缓存中运行，绝不接触活跃的会话。

:::info 首次运行行为
在全新安装（或在 `hermes update` 后，预技能管理员安装的首次触发）时，技能管理员 **不会立即运行**。首次观察将 `last_run_at` 设置为“现在”，并将第一次真正的运行推迟一个完整的 `interval_hours`。这为您提供了一个完整的间隔时间来审查您的技能库，固定任何重要内容，或在技能管理员接触它们之前完全退出。

如果您想在技能管理员真正运行之前查看它 *会* 做什么，请运行 `hermes curator run --dry-run` ——它会生成相同的审查报告，而不修改库。
:::

一次运行分为两个阶段：

1.  **自动转换**（确定性的，无需 LLM）。未使用超过 `stale_after_days`（30 天）的技能变为 `陈旧`；未使用超过 `archive_after_days`（90 天）的技能被移动到 `~/.hermes/skills/.archive/`。
2.  **LLM 审查**（单次辅助模型运行，`max_iterations=8`）。分支出的 Agent 会调查 Agent 创建的技能，可以使用 `skill_view` 读取其中任何一个，并决定每个技能是保留、修补（通过 `skill_manage`）、合并重叠的技能，还是通过终端工具归档。合并将技能视为一个完整的包：如果一个技能有 `references/`、`templates/`、`scripts/`、`assets/` 或指向这些路径的相对链接，技能管理员必须要么将其作为独立包保留，要么重新安置所需的支持文件并重写路径，要么将整个包原封不动地归档——而不是仅将 `SKILL.md` 扁平化到另一个技能的 `references/` 文件中。

固定的技能对技能管理员的自动转换和 Agent 自身的 `skill_manage` 工具都是禁止访问的。请参阅下面的 [固定技能](#pinning-a-skill)。

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

相同的选择器在网络仪表板的 **Models** 选项卡下可用。

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
早期版本使用了一个独立的 `curator.auxiliary.{provider,model}` 块。该路径仍然有效，但会发出弃用日志行——请迁移到上面的 `auxiliary.curator`，以便技能管理员与其他所有辅助任务共享相同的基础设施（`hermes model`、仪表板 Models 选项卡、`base_url`、`api_key`、`timeout`、`extra_body`）。
:::

## CLI

```bash
hermes curator status         # 上次运行时间、计数、固定列表、最近最少使用的前 5 个
hermes curator run            # 立即触发审查（阻塞直到 LLM 流程完成）
hermes curator run --background  # 触发即忘：在后台线程中启动 LLM 流程
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
## 备份与回滚

在每次实际的策展运行之前，Hermes 会在 `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz` 路径下创建 `~/.hermes/skills/` 的 tar.gz 快照。如果某次运行归档或合并了你不想被触及的内容，你可以用一个命令撤销整个运行：

```bash
hermes curator rollback        # 恢复最新的快照（需确认）
hermes curator rollback -y     # 跳过确认提示
hermes curator rollback --list # 查看所有快照及其原因和大小
```

回滚操作本身是可逆的：在替换技能树之前，Hermes 会创建另一个标记为 `pre-rollback to <target-id>` 的快照，因此错误的回滚可以通过使用 `--id` 参数向前回滚到该快照来撤销。

你也可以随时使用 `hermes curator backup --reason "before-refactor"` 手动创建快照。`--reason` 字符串会保存在快照的 `manifest.json` 中，并在 `--list` 中显示。

快照会根据 `curator.backup.keep`（默认为 5）进行清理，以控制磁盘使用量：

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

设置 `curator.backup.enabled: false` 以禁用自动快照。当备份被禁用时，手动命令 `hermes curator backup` 只有在先设置 `enabled: true` 后才有效——该标志对称地控制两条路径，因此无法在变更性运行时意外跳过运行前快照。

`hermes curator status` 也会列出五个最近最少使用的技能——这是快速查看哪些技能可能即将过期的便捷方法。

相同的子命令在运行中的会话（CLI 或消息网关平台）中也可作为 `/curator` 斜杠命令使用。

## "Agent 创建"的含义

策展器只管理在 `~/.hermes/skills/.usage.json` 中明确标记为 **agent-created** 的技能。一个技能必须满足以下所有条件才符合资格：

1. 其名称 **不** 在 `~/.hermes/skills/.bundled_manifest` 中（随仓库分发的捆绑技能）。
2. 其名称 **不** 在 `~/.hermes/skills/.hub/lock.json` 中（通过 Hub 安装的技能）。
3. 其 `.usage.json` 条目具有 `"created_by": "agent"` 或 `"agent_created": true`。

目前，只有 **后台自我改进审查分支** 会设置此标记——当它在定期审查运行（约每 10 个 Agent 回合）期间创建新的伞状技能时。后台分支以 `"background_review"` 的写入来源运行（通过 `tools/skill_provenance.py`），这是唯一触发 `skill_manage` 中 `mark_agent_created()` 调用的路径。

前台 Agent 在对话期间通过 `skill_manage(action="create")` 创建的技能 **不会** 被标记为 agent-created——它们被视为用户导向的，策展器有意不触碰它们。

:::warning 你手写的技能不会被策展
如果你手动创建了 `SKILL.md` 或将 Hermes 指向外部技能目录，该技能的 `.usage.json` 条目将具有 `created_by: null`（或该字段缺失）。策展器不会触碰它。这同样适用于前台 Agent 应你请求创建的技能。

**要查看策展器实际管理哪些技能**，请运行 `hermes curator status`。如果 agent-created 计数为 0，则当前没有技能在策展器的管辖范围内——LLM 审查运行将被跳过，报告将显示 `Model: (not resolved) via (not resolved)` 和 `Duration: 0s`。
:::

属于 agent-created 的技能遵循完整的生命周期：

- `active` → (30 天未使用) `stale` → (90 天未使用) `archived`
- 已固定的技能绕过所有自动状态转换
- 归档的技能可通过 `hermes curator restore <name>` 恢复

如果你想保护某个特定技能不被触碰——例如你依赖的手写技能——请使用 `hermes curator pin <name>`。参见下一节。

## 固定技能

固定可以保护技能不被删除——无论是策展器的自动归档运行还是 Agent 的 `skill_manage(action="delete")` 工具调用。一旦技能被固定：

- **策展器** 在自动状态转换（`active → stale → archived`）期间跳过它，并且其 LLM 审查运行会被指示不触碰它。
- **Agent 的 `skill_manage` 工具** 拒绝对其执行 `delete` 操作，并提示用户使用 `hermes curator unpin <name>`。补丁和编辑仍然可以进行，因此 Agent 可以在发现问题时改进已固定技能的内容，而无需进行固定/取消固定/重新固定的繁琐操作。

使用以下命令进行固定和取消固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志作为 `"pinned": true` 存储在技能在 `~/.hermes/skills/.usage.json` 中的条目上，因此它在会话之间持续存在。

只有 **agent-created** 技能可以被固定——捆绑和通过 Hub 安装的技能首先就不受策展器变更的影响，如果你尝试固定它们，`hermes curator pin` 会拒绝并给出解释性消息。

如果你想要比"不删除"更强的保证——例如，在 Agent 仍读取技能时完全冻结其内容——请直接使用你的编辑器编辑 `~/.hermes/skills/<name>/SKILL.md`。固定功能只防护工具驱动的删除，而不防护你自己的文件系统访问。

## 使用遥测

策展器在 `~/.hermes/skills/.usage.json` 维护一个伴生文件，每个技能对应一个条目：

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

- `view_count`: Agent 对该技能调用 `skill_view`。
- `use_count`: 技能被加载到对话的提示词中。
- `patch_count`: 对技能运行 `skill_manage patch/edit/write_file/remove_file`。

捆绑和通过 Hub 安装的技能明确排除在遥测写入之外。

## 每次运行报告

每次策展器运行都会在 `~/.hermes/logs/curator/` 下写入一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # 机器可读：完整保真度、统计信息、LLM 输出
    └── REPORT.md     # 人类可读摘要
```
`REPORT.md` 是快速查看特定运行结果的便捷方式——哪些技能发生了状态转换、LLM 评审员说了什么、修补了哪些技能。便于审计，无需在 `agent.log` 中搜索。

:::note 没有候选技能？报告显示 `(not resolved)`
当策展人**没有由 Agent 创建的技能**可供评审时，将完全跳过 LLM 评审环节。报告头部将显示 `Model: (not resolved) via (not resolved)` 和 `Duration: 0s`——这**并不**表示配置错误或模型解析失败。它仅意味着没有候选技能，因此从未调用任何模型。自动转换阶段仍会正常运行并正常报告其计数。
:::

### 摘要中的重命名映射

如果一次运行将多个技能整合到一个总称下（或合并了近似重复项），运行结束时打印的用户可见摘要会包含一个明确的重命名映射，显示策展人应用的每个 `旧名称 → 新名称` 对。这是在每个技能转换行之外额外提供的信息，因此当一波重命名发生时，你可以一目了然地发现它们，而无需对比 JSON 报告。该提示也会在 `hermes curator pin` 下显示，以便你如果需要锁定新标签，可以立即固定总称名称。

## 恢复已归档的技能

如果策展人归档了你仍然需要的技能：

```bash
hermes curator restore <skill-name>
```

这将把技能从 `~/.hermes/skills/.archive/` 移回活动树，并将其状态重置为 `active`。如果此后已安装同名的捆绑或从 Hub 安装的技能（会遮蔽上游），恢复操作将被拒绝。

## 按执行环境禁用

策展人默认启用。要关闭它：

- **仅针对一个配置文件：** 编辑 `~/.hermes/config.yaml`（或活动配置文件的配置）并设置 `curator.enabled: false`。
- **仅针对一次运行：** `hermes curator pause` —— 暂停状态会跨会话保持；使用 `resume` 重新启用。

如果 `min_idle_hours` 尚未过去，策展人也会拒绝运行，因此在活跃的开发机器上，它自然只会在空闲时段运行。

## 另请参阅

- [技能系统](/user-guide/features/skills) —— 技能的一般工作原理以及创建它们的自我改进循环
- [记忆](/user-guide/features/memory) —— 维护长期记忆的并行后台评审
- [捆绑技能目录](/reference/skills-catalog)
- [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) —— 原始提案和设计讨论