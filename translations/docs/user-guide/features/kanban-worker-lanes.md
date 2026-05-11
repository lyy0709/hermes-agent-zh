# 看板工作通道

**工作通道**是看板调度器可以将任务路由到的一类进程。每个通道都有一个身份标识（指派人字符串）、一个生成机制，以及一份关于生成后必须如何处理任务的契约。

本页即是这份契约。它面向两类读者：

- **操作员**：选择将哪些通道接入看板（创建哪些配置文件，使用哪些指派人）。
- **插件/集成开发者**：希望添加新的通道形态（包装 Codex / Claude Code / OpenCode 的 CLI 工作器、容器化的审查工作器、通过 API 拉取任务的非 Hermes 服务）。

如果你正在编写工作器代码本身——即运行在通道*内部*的 Agent——那么 [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能提供了更深入的程序细节。

## 层级关系

```text
Hermes 看板  =  规范的任务生命周期 + 审计追踪
工作通道    =  一个已分配卡片的执行器实现
审查员      =  把关“完成”状态的人或人类代理
GitHub PR   =  可向上游提交的工件（可选，用于代码通道）
```

Hermes 看板拥有生命周期的最终状态——`ready` → `running` → `blocked` / `done` / `archived`。工作通道执行工作，但从不拥有该状态；它们所做的一切都通过 `kanban_*` 工具（或者，对于非 Hermes 的外部工作器，通过 API）流回看板内核。审查员把关从“代码变更已编写”到“任务完成”的转换。

## 通道提供的内容

要成为看板工作通道，集成必须提供三样东西：

### 1. 一个指派人字符串

调度器将 `task.assignee` 与 Hermes 配置文件名称（默认通道形态）或已注册的不可生成标识符（插件通道形态——见下文[添加外部 CLI 工作器通道](#添加外部-cli-工作器通道)）进行匹配。指派人无法解析的任务将保持在 `ready` 状态，并记录 `skipped_nonspawnable` 事件，以便看板操作员可以修复它们；它们不会被静默丢弃或由任意回退机制执行。

### 2. 一个生成机制

对于 Hermes 配置文件通道，调度器的 `_default_spawn` 在任务固定的工作空间内运行 `hermes -p <assignee> chat -q <prompt>`（或者当 `hermes` 垫片不在 `$PATH` 上时，运行等效的模块形式），并设置以下环境变量：

| 变量 | 携带内容 |
|---|---|
| `HERMES_KANBAN_TASK` | 工作器正在操作的任务 ID |
| `HERMES_KANBAN_DB` | 每个看板的 SQLite 文件的绝对路径 |
| `HERMES_KANBAN_BOARD` | 看板标识符 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 看板工作空间树的根目录 |
| `HERMES_KANBAN_WORKSPACE` | *此*任务工作空间的绝对路径 |
| `HERMES_KANBAN_RUN_ID` | 当前运行的 ID（用于生命周期门控） |
| `HERMES_KANBAN_CLAIM_LOCK` | 声明锁字符串 (`<host>:<pid>:<uuid>`) |
| `HERMES_PROFILE` | 工作器自身的配置文件名称（用于 `kanban_comment` 的作者归属） |
| `HERMES_TENANT` | 租户命名空间（如果任务有的话） |

对于非 Hermes 通道（通过插件注册），插件提供自己的 `spawn_fn` 可调用对象，该对象接收 `task`、`workspace` 和 `board` 参数，并返回一个可选的 PID 用于崩溃检测。

### 3. 一个生命周期终止器

每个声明必须以以下方式之一结束：

- `kanban_complete(summary=..., metadata=...)` —— 任务成功，状态翻转为 `done`。
- `kanban_block(reason=...)` —— 任务等待人工输入，状态翻转为 `blocked`。当 `kanban_unblock` 运行时，调度器会重新生成工作器。
- 工作器进程退出且未调用任何工具。内核回收它并发出 `crashed`（PID 死亡）、`gave_up`（连续失败断路器触发）或 `timed_out`（超过 max_runtime）。这是失败路径；健康的工作器不会在此结束。

看板内核强制要求每次运行必须且只能由其中一种方式终止。一个既不调用上述工具又正常退出的工作器将被视为崩溃。

## 输出与“需要审查”的约定

对于大多数涉及代码变更的任务，工作器完成的那一刻工作并非真正*完成*——它需要人工审查。看板内核并不强制区分这一点（“涉及代码变更的任务”是模糊的，并且强制每个代码工作器阻塞而非完成会破坏不需要审查的工作流）。这是一个叠加在上层的约定：

- **阻塞而非完成**，`reason` 前缀为 `review-required: `，以便仪表板 / `hermes kanban show` 将该行显示为等待审查。
- **首先将结构化元数据放入 `kanban_comment`**，因为 `kanban_block` 只携带人类可读的 `reason`。评论是持久的注释渠道——每个与审计相关的字段（changed_files、tests_run、diff_path 或 PR url、决策）都应放在那里。
- **审查员要么批准并解除阻塞**，这将重新生成工作器并附带评论线程以供后续跟进；要么通过另一条评论要求更改，下一次工作器运行会将其视为 `kanban_show` 上下文的一部分。

[`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能提供了 `kanban_complete`（真正终结性任务——拼写错误修复、文档变更、研究报告）和 `review-required` 阻塞模式的工作示例。

## 日志与审计追踪

调度器将每个任务的工作器 stdout/stderr 写入 `<board-root>/logs/<task_id>.log`。可以从看板元数据审计日志：

- `task_runs` 行包含 `log_path`、退出代码（如果可用）、摘要和元数据。
- `task_events` 行包含每个状态转换（`promoted`、`claimed`、`heartbeat`、`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`reclaimed`、`claim_extended`）。
- `kanban_show` 返回两者，因此审查员（或后续工作器）在读取任务时可以获得完整历史记录，而无需访问仪表板。

仪表板使用摘要、元数据块和退出状态徽章呈现运行历史记录。CLI 用户可以运行 `hermes kanban tail <task_id>` 来实时跟踪，或运行 `hermes kanban runs <task_id>` 查看历史尝试列表。

## 现有通道形态

### Hermes 配置文件通道（默认）

这是目前每个看板工作器采用的形态：指派人是一个配置文件名称，调度器生成 `hermes -p <profile>`，工作器自动加载 [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能以及 `KANBAN_GUIDANCE` 系统提示词块，并使用 `kanban_*` 工具来终止运行。除了定义配置文件外，无需其他设置。

当你为你的工作器群创建配置文件时，请选择与你希望编排器路由到的*角色*相匹配的名称。编排器（当存在时）通过 `hermes profile list` 发现你的配置文件名称——系统没有假设固定的名册（有关编排器侧的契约，请参阅 [`kanban-orchestrator`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-orchestrator/SKILL.md) 技能）。

### 编排器配置文件通道

这是配置文件通道的一个特化：编排器是一个 Hermes 配置文件，其工具集包含 `kanban` 但不包含用于实现的 `terminal` / `file` / `code` / `web`。它的工作是通过 `kanban_create` + `kanban_link` 将高级目标分解为子任务，然后退居幕后。编排器技能编码了反诱惑规则。

## 添加外部 CLI 工作器通道

将非 Hermes CLI 工具（Codex CLI、Claude Code CLI、OpenCode CLI、本地编码模型运行器等）作为看板工作器通道接入，*目前还不是一条铺好的道路*。调度器的生成函数是可插拔的（`spawn_fn` 是 `dispatch_once` 的一个参数），插件可以为非 Hermes 指派人注册自己的 `spawn_fn`，但周围的集成工作——将 CLI 的退出代码包装到 `kanban_complete` / `kanban_block` 调用中，将 CLI 的工作空间/沙盒约定映射到调度器的 `HERMES_KANBAN_WORKSPACE` 环境变量，处理身份验证和每个 CLI 的策略——仍然是每个集成需要设计的工作。

如果你考虑添加 CLI 通道，请提交一个问题，描述具体的 CLI 和你试图实现的工作流。上述契约是任何此类通道必须满足的约束；实现形态（每个 CLI 一个插件 vs 一个由配置参数化的通用 CLI 运行器插件）是开放的。

与此相关的历史问题是 [#19931](https://github.com/NousResearch/hermes-agent/issues/19931) 和已关闭但未合并的 Codex 特定 PR [#19924](https://github.com/NousResearch/hermes-agent/pull/19924)——这些描述了最初的架构提案，但并未落地一个运行器。

## 调度器处理的故障模式

这样通道作者就不必重新实现这些：

- **陈旧声明 TTL** —— 一个声明后从不心跳/完成/阻塞的工作器，在 `DEFAULT_CLAIM_TTL_SECONDS`（默认 15 分钟）后会被重新声明——但前提是工作器进程确实已死亡。一个存活的工作器（慢速模型在一个无工具调用的 LLM 调用中花费 20 分钟以上）会获得声明*延长*而不是被终止；只有死亡的 PID 才会被重新声明。
- **崩溃的工作器** —— 其主机本地 PID 已消失的工作器会被 `detect_crashed_workers` 检测到并回收；任务会增加 `consecutive_failures`，并且在断路器触发时可能自动阻塞。
- **运行级重试** —— 当任务被重试时（阻塞后、崩溃后、重新声明后），工作器可以在终止工具上使用 `expected_run_id` 参数，如果其自身的运行已被取代，则快速失败。
- **每个任务的最大运行时间** —— `task.max_runtime_seconds` 硬性限制每次运行的挂钟时间，无论 PID 是否存活。捕获真正死锁的工作器，否则存活 PID 的延长机制会让它们继续运行。
- **滞留任务检测** —— 一个 `ready` 任务，其指派人从未在 `kanban.stranded_threshold_seconds`（默认 30 分钟）内产生声明，会在 `hermes kanban diagnostics` 中显示为 `stranded_in_ready` 警告。严重性在阈值的 2 倍时升级为错误，在 6 倍时升级为严重。在一个信号中捕获拼写错误的指派人、已删除的配置文件和宕机的外部工作器池——与身份无关，无需为每个看板维护允许列表。

## 相关链接

- [看板概述](./kanban) —— 面向用户的介绍。
- [看板教程](./kanban-tutorial) —— 打开仪表板的演练。
- [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) —— 工作器进程加载的技能。
- [`kanban-orchestrator`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-orchestrator/SKILL.md) —— 编排器侧。