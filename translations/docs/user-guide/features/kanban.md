---
sidebar_position: 12
title: "看板（多 Agent 面板）"
description: "基于持久化 SQLite 的任务面板，用于协调多个 Hermes 人格"
---

# 看板 — 多 Agent 人格协作

> **需要引导教程？** 阅读 [看板教程](./kanban-tutorial) — 包含四个用户场景（独立开发者、舰队耕作、带重试的角色流水线、熔断器）以及每个场景的仪表盘截图。本页是参考文档；教程是叙述性指南。

Hermes 看板是一个持久化的任务面板，在所有 Hermes 人格之间共享，允许多个具名 Agent 协作处理工作，而无需依赖脆弱的进程内子 Agent 集群。每个任务都是 `~/.hermes/kanban.db` 中的一行；每次交接都是任何人都可以读写的一行；每个工作者都是一个拥有自己身份标识的完整操作系统进程。

### 两个界面：模型通过工具交流，你通过 CLI 交流

看板有两个入口，都基于同一个 `~/.hermes/kanban.db`：

- **Agent 通过专用的 `kanban_*` 工具集驱动看板** — `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock`。调度器在生成每个工作者时，其模式中已包含这些工具；编排者人格也可以显式启用 `kanban` 工具集。模型通过直接调用工具来读取和路由任务，*而不是*通过 shell 执行 `hermes kanban`。请参阅下面的 [工作者如何与看板交互](#how-workers-interact-with-the-board)。
- **你（以及脚本和定时任务）通过 CLI 上的 `hermes kanban …`**、斜杠命令 `/kanban …` 或仪表盘来驱动看板。这些是供人类和自动化流程使用的——即那些背后没有工具调用模型的场景。

两个界面都通过同一个 `kanban_db` 层进行路由，因此读取操作看到的是统一的视图，写入操作不会产生偏差。本页其余部分展示 CLI 示例，因为它们易于复制粘贴，但每个 CLI 命令都有模型使用的等效工具调用。

这种形式覆盖了 `delegate_task` 无法处理的工作负载：

- **研究分类** — 并行研究人员 + 分析师 + 撰稿人，人工介入循环。
- **计划运维** — 每日重复简报，数周内构建日志。
- **数字孪生** — 持久化的具名助手（`inbox-triage`、`ops-review`），随时间积累记忆。
- **工程流水线** — 分解 → 在并行工作树中实现 → 审查 → 迭代 → PR。
- **舰队工作** — 一个专家管理 N 个主体（50 个社交账户，12 个监控服务）。

关于完整的设计原理、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种经典协作模式，请参阅代码仓库中的 `docs/hermes-kanban-v1-spec.pdf`。

## 看板 vs. `delegate_task`

它们看起来相似；但它们是不同的原语。

| | `delegate_task` | 看板 |
|---|---|---|
| 形式 | RPC 调用（分叉 → 合并） | 持久化消息队列 + 状态机 |
| 父级 | 阻塞直到子级返回 | 在 `create` 后即发即弃 |
| 子级身份 | 匿名子 Agent | 具有持久化记忆的具名人格 |
| 可恢复性 | 无 — 失败即失败 | 阻塞 → 解除阻塞 → 重新运行；崩溃 → 回收 |
| 人工介入 | 不支持 | 在任何时间点评论 / 解除阻塞 |
| 每个任务的 Agent 数 | 一次调用 = 一个子 Agent | 任务生命周期内的 N 个 Agent（重试、审查、跟进） |
| 审计追踪 | 在上下文压缩时丢失 | SQLite 中永久保存的持久化行 |
| 协调方式 | 分层（调用者 → 被调用者） | 对等 — 任何人格都可以读写任何任务 |

**一句话区分：** `delegate_task` 是一个函数调用；看板是一个工作队列，其中每次交接都是任何人格（或人类）可以查看和编辑的一行。

**在以下情况使用 `delegate_task`：** 父级 Agent 在继续之前需要一个简短的推理答案，没有人工参与，结果返回到父级的上下文中。

**在以下情况使用看板：** 工作跨越 Agent 边界，需要在重启后存活，可能需要人工输入，可能被不同角色接手，或者需要在事后可被发现。

它们可以共存：一个看板工作者在其运行期间内部可能会调用 `delegate_task`。

## 核心概念

- **看板** — 一个独立的任务队列，拥有自己的 SQLite 数据库、工作空间目录和调度器循环。单个安装可以拥有多个看板（例如，每个项目、仓库或领域一个）；请参阅下面的 [看板（多项目）](#boards-multi-project)。单项目用户停留在 `default` 看板上，并且在本文档部分之外永远不会看到“看板”这个词。
- **任务** — 包含标题、可选正文、一个分配者（人格名称）、状态（`triage | todo | ready | running | blocked | done | archived`）、可选的租户命名空间、可选的幂等性密钥（用于重试自动化的去重）的行。
- **链接** — 记录父级 → 子级依赖关系的 `task_links` 行。当所有父级都处于 `done` 状态时，调度器会将任务从 `todo` 提升为 `ready`。
- **评论** — Agent 间的通信协议。Agent 和人类追加评论；当工作者（重新）生成时，它会读取完整的评论线程作为其上下文的一部分。
- **工作空间** — 工作者在其中操作的目录。有三种类型：
  - `scratch`（默认）— `~/.hermes/kanban/workspaces/<id>/` 下的新临时目录（或在非默认看板下为 `~/.hermes/kanban/boards/<slug>/workspaces/<id>/`）。**任务完成时删除** — scratch 设计上是临时的，因此当工作者（或 `hermes kanban complete <id>`）将任务标记为完成时，目录会被清除。如果你想保留工作者的输出，请改用 `worktree:` 或 `dir:<path>`。在安装上首次创建 scratch 工作空间时，调度器会记录警告并在任务上发出 `tip_scratch_workspace` 事件（可通过 `hermes kanban show <id>` 查看）。
  - `dir:<path>` — 一个现有的共享目录（Obsidian 保险库、邮件操作目录、每个账户的文件夹）。**必须是绝对路径。** 像 `dir:../tenants/foo/` 这样的相对路径在调度时会被拒绝，因为它们会根据调度器当前所在的任何 CWD 进行解析，这是不明确的，并且是一个混淆代理的逃逸向量。路径在其他方面是受信任的——这是你的机器，你的文件系统，工作者以你的用户 ID 运行。这是受信任的本地用户威胁模型；看板设计上是单主机的。**完成时保留。**
  - `worktree` — 用于编码任务的 `.worktrees/<id>/` 下的 git 工作树。使用 `worktree:<path>` 来固定确切的目标路径。工作者端的 `git worktree add` 会创建它，并在提供时使用 `--branch` 参数。**完成时保留。**
- **调度器** — 一个长期运行的循环，每 N 秒（默认 60 秒）执行一次：回收过期的声明，回收崩溃的工作者（PID 消失但 TTL 尚未过期），提升就绪任务，原子性地声明，生成分配的人格。默认情况下在**消息网关内部**运行（`kanban.dispatch_in_gateway: true`）。一个调度器每次扫描所有看板；工作者生成时带有固定的 `HERMES_KANBAN_BOARD` 环境变量，因此它们看不到其他看板。在同一任务上连续 `kanban.failure_limit` 次（默认：2）生成失败后，调度器会自动将其阻塞，并将最后一个错误作为原因——防止在那些人格不存在、工作空间无法挂载等任务上产生抖动。
- **租户** — 看板*内部*的可选字符串命名空间。一个专家舰队可以为多个业务（`--tenant business-a`）服务，通过工作空间路径和记忆键前缀实现数据隔离。租户是软过滤器；看板是硬隔离边界。
## 看板（多项目）

看板让你可以将不相关的工作流（每个项目、代码库或领域一个）分离到独立的队列中。新安装的 Hermes 只有一个名为 `default` 的看板（为了向后兼容，数据库位于 `~/.hermes/kanban.db`）。只想要一个工作流的用户永远不需要了解看板；这个功能是可选的。

每个看板的隔离是绝对的：

-   每个看板有独立的 SQLite 数据库（`~/.hermes/kanban/boards/<slug>/kanban.db`）。
-   独立的 `workspaces/` 和 `logs/` 目录。
-   为任务启动的 Worker **只能**看到其所属看板的任务——调度器会在子进程环境中设置 `HERMES_KANBAN_BOARD`，Worker 可以访问的每个 `kanban_*` 工具都会读取这个变量。
-   不允许跨看板链接任务（保持模式简单；如果你确实需要跨项目引用，请使用自由文本提及并手动按 ID 查找）。

### 通过 CLI 管理看板

```bash
# 查看磁盘上有什么。全新安装只显示 "default"。
hermes kanban boards list

# 创建新看板。
hermes kanban boards create atm10-server \
    --name "ATM10 Server" \
    --description "Minecraft modded server ops" \
    --icon 🎮 \
    --switch                   # 可选：使其成为活动看板

# 在不切换的情况下对特定看板进行操作。
hermes kanban --board atm10-server list
hermes kanban --board atm10-server create "Restart ATM server" --assignee ops

# 更改后续调用中哪个看板是"当前"看板。
hermes kanban boards switch atm10-server
hermes kanban boards show             # 当前谁处于活动状态？

# 重命名显示名称（slug 是不可变的——它是目录名）。
hermes kanban boards rename atm10-server "ATM10 (Prod)"

# 归档（默认）——将看板的目录移动到 boards/_archived/<slug>-<ts>/。
# 通过将目录移回可以恢复。
hermes kanban boards rm atm10-server

# 硬删除——`rm -rf` 看板目录。无法恢复。
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（优先级从高到低）：

1.  CLI 调用中显式的 `--board <slug>`。
2.  `HERMES_KANBAN_BOARD` 环境变量（由调度器在启动 Worker 时设置，因此 Worker 无法看到其他看板）。
3.  `~/.hermes/kanban/current` —— 由 `hermes kanban boards switch` 持久化的 slug。
4.  `default`。

Slug 会经过验证：小写字母数字 + 连字符 + 下划线，1-64 个字符，必须以字母数字开头。大写输入会自动转换为小写。任何其他字符（斜杠、空格、点、`..`）都会在 CLI 层被拒绝，因此路径遍历技巧无法命名看板。

### 通过仪表板管理看板

`hermes dashboard` → Kanban 标签页会在存在多个看板（或任何看板有任务）时在顶部显示看板切换器。单看板用户只看到一个小的 `+ New board` 按钮；切换器在需要时才会显示。

-   **看板下拉菜单** —— 选择活动看板。你的选择会保存到浏览器的 `localStorage` 中，因此在重新加载时它会持续存在，而不会改变你已打开终端中 CLI 的 `current` 指针。
-   **+ 新看板** —— 打开一个模态框，要求输入 slug、显示名称、描述和图标。可以选择自动切换到新看板。
-   **归档** —— 仅在非 `default` 看板上显示。确认后，将看板目录移动到 `boards/_archived/`。

所有仪表板 API 端点都接受 `?board=<slug>` 用于看板范围限定。事件 WebSocket 在连接时固定到一个看板；在 UI 中切换会针对新看板打开一个新的 WebSocket。

## 文件附件

任务可以携带文件附件——PDF、图像、源文档——这样 Worker 就拥有了所需的原始材料，而无需你将路径粘贴到正文中并希望它能找到它们。

-   **上传** —— 在仪表板抽屉中打开一个任务，并使用 **附件** 部分的 *上传文件* 按钮（一次可以上传多个文件）。每次上传上限为 25 MB。
-   **存储** —— 文件存储在默认看板的 `<hermes-home>/kanban/attachments/<task_id>/` 下，或命名看板的 `<hermes-home>/kanban/boards/<slug>/attachments/<task_id>/` 下。设置 `HERMES_KANBAN_ATTACHMENTS_ROOT` 可以固定到自定义位置。
-   **Worker 看到的内容** —— 当调度器将任务交给 Worker 时，Worker 的上下文中包含一个 **附件** 部分，列出每个文件的名称及其**绝对路径**。Worker 拥有完整的文件/终端工具访问权限，因此它可以直接读取附件（`read_file`，或像 `pdftotext` 这样的 shell 工具）。
-   **下载 / 移除** —— 抽屉列出每个附件，并带有下载链接和移除 (×) 控件。移除附件会同时删除元数据行和磁盘上的文件。

:::note 远程终端后端
附件路径直接在**本地**终端后端解析，这是 Kanban Worker 的默认设置。如果你在远程后端（Docker、Modal）上运行 Worker，请将看板的 `attachments/` 目录挂载到沙盒中，以便 Worker 上下文中的绝对路径可以访问。
:::

## 快速开始

以下命令是**你**（人类）设置看板和创建任务。一旦任务被分配，调度器就会将分配的个人资料作为 Worker 启动，从那时起**模型通过 `kanban_*` 工具调用来驱动任务，而不是 CLI 命令**——参见 [Worker 如何与看板交互](#how-workers-interact-with-the-board)。

```bash
# 1. 创建看板（你）
hermes kanban init

# 2. 启动消息网关（托管嵌入式调度器）
hermes gateway start

# 3. 创建任务（你——或通过 kanban_create 的编排 Agent）
hermes kanban create "research AI funding landscape" --assignee researcher

# 4. 实时查看活动（你）
hermes kanban watch

# 5. 查看看板（你）
hermes kanban list
hermes kanban stats
```

当调度器获取到 `t_abcd` 并启动 `researcher` 个人资料时，该 Worker 的模型做的第一件事就是调用 `kanban_show()` 来读取其任务。它不会运行 `hermes kanban show t_abcd`。

### 消息网关嵌入式调度器（默认）

调度器在消息网关进程内部运行。无需安装，无需管理单独的服务——只要消息网关启动，就绪的任务会在下一个周期（默认为 60 秒）被拾取。
```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # 默认值
  dispatch_interval_seconds: 60    # 默认值
```

可以通过设置环境变量 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 在运行时覆盖配置标志，用于调试。标准的消息网关监管方式适用：直接运行 `hermes gateway start`，或者将消息网关配置为 systemd 用户单元（参见消息网关文档）。如果没有运行的消息网关，`ready` 状态的任务将保持原状，直到有消息网关启动——`hermes kanban create` 在创建时会对此发出警告。

将 `hermes kanban daemon` 作为独立进程运行的方式**已弃用**；请使用消息网关。如果你确实无法运行消息网关（例如无头主机策略禁止长时间运行的服务等），可以使用 `--force` 参数作为逃生舱口，在下一个发布周期内继续使用旧的独立守护进程，但**不支持**同时对同一个 `kanban.db` 运行消息网关内嵌的调度器**和**独立守护进程，这会导致任务认领竞争。

### 幂等创建（用于自动化 / Webhook）

```bash
# 第一次调用创建任务。后续任何使用相同 key 的调用
# 将返回现有任务 ID，而不是重复创建。
hermes kanban create "nightly ops review" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

### 批量 CLI 命令

所有生命周期命令都接受多个 ID，因此你可以用一个命令清理一批任务：

```bash
hermes kanban complete t_abc t_def t_hij --result "batch wrap"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "need input" --ids t_def t_hij
```

## 工作进程如何与看板交互

**工作进程不会通过 shell 调用 `hermes kanban`。** 当调度器生成一个工作进程时，它会在子进程的环境中设置 `HERMES_KANBAN_TASK=t_abcd`，这个环境变量会激活模型架构中一个专用的**看板工具集**。同样的工具集也适用于在其工具集配置中启用了 `kanban` 的编排器配置文件。这些工具通过 Python 的 `kanban_db` 层直接读取和修改看板，与 CLI 的方式相同。运行中的工作进程像调用其他工具一样调用这些工具；它从不接触也不需要 `hermes kanban` CLI。

| 工具 | 用途 | 必需参数 |
|---|---|---|
| `kanban_show` | 读取当前任务（标题、正文、先前尝试、父任务交接、评论、完整预格式化的 `worker_context`）。默认为环境变量中的任务 ID。 | — |
| `kanban_list` | 列出任务摘要，支持按 `assignee`、`status`、`tenant`、归档可见性过滤和限制数量。用于编排器发现看板工作。 | — |
| `kanban_complete` | 完成任务，附带结构化的 `summary` + `metadata` 交接。 | `summary` / `result` 至少一个 |
| `kanban_block` | 因需要人工输入而升级任务，附带 `reason`。 | `reason` |
| `kanban_heartbeat` | 在长时间操作期间发送存活信号。纯副作用。 | — |
| `kanban_comment` | 向任务线程追加持久化注释。 | `task_id`, `body` |
| `kanban_create` | （编排器）将任务分解为子任务，指定 `assignee`，可选的 `parents`、`skills` 等。 | `title`, `assignee` |
| `kanban_link` | （编排器）事后添加 `parent_id → child_id` 依赖边。 | `parent_id`, `child_id` |
| `kanban_unblock` | （编排器）将阻塞的任务移回 `ready` 状态。 | `task_id` |

一个典型的工作进程轮次如下：

```
# 模型按顺序调用工具：
kanban_show()                                     # 无参数 — 使用 HERMES_KANBAN_TASK
# （模型读取返回的 worker_context，通过终端/文件工具完成工作）
kanban_heartbeat(note="halfway through — 4 of 8 files transformed")
# （更多工作）
kanban_complete(
    summary="migrated limiter.py to token-bucket; added 14 tests, all pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
)
```

一个**编排器**工作进程则进行任务分解：

```
kanban_show()
kanban_create(
    title="research ICP funding 2024-2026",
    assignee="researcher-a",
    body="focus on seed + series A, North America, AI-adjacent",
)
# → 返回 {"task_id": "t_r1", ...}
kanban_create(title="research ICP funding — EU angle", assignee="researcher-b", body="…")
# → 返回 {"task_id": "t_r2", ...}
kanban_create(
    title="synthesize findings into launch brief",
    assignee="writer",
    parents=["t_r1", "t_r2"],                     # 当两个父任务都完成时，此任务提升为 ready 状态
    body="one-pager, 300 words, neutral tone",
)
kanban_complete(summary="decomposed into 2 research tasks + 1 writer; linked dependencies")
```

标记为“（编排器）”的工具——`kanban_list`、`kanban_create`、`kanban_link`、`kanban_unblock` 以及对其他任务的 `kanban_comment`——可通过同一个工具集使用；惯例（由 `kanban-orchestrator` 技能强制执行）是：工作进程配置文件不进行任务分解或路由无关工作，而编排器配置文件不执行具体实现工作。由调度器生成的工作进程在破坏性生命周期操作上仍然受限于其任务范围，无法修改无关任务。

### 为什么使用工具而不是通过 shell 调用 `hermes kanban`

三个原因：

1.  **后端可移植性。** 那些终端工具指向远程后端（Docker / Modal / Singularity / SSH）的工作进程，会在容器*内部*运行 `hermes kanban complete`，而容器内可能没有安装 `hermes`，也没有挂载 `~/.hermes/kanban.db`。看板工具在 Agent 自己的 Python 进程中运行，无论终端后端是什么，总是能访问到 `~/.hermes/kanban.db`。
2.  **避免 shell 引用的脆弱性。** 通过 shlex + argparse 传递 `--metadata '{"files": [...]}'` 是一个潜在的隐患。结构化的工具参数完全避免了这个问题。
3.  **更好的错误处理。** 工具结果是模型可以进行推理的结构化 JSON，而不是它必须解析的 stderr 字符串。

**对普通会话零架构影响。** 一个常规的 `hermes chat` 会话在其架构中**没有**任何 `kanban_*` 工具，除非活动配置文件明确启用了 `kanban` 工具集用于编排器工作。由调度器生成的任务工作进程获得任务范围内的工具，因为设置了 `HERMES_KANBAN_TASK`；编排器配置文件通过配置获得更广泛的路由接口。对于从不接触看板的用户，没有工具膨胀的问题。
`kanban-worker` 和 `kanban-orchestrator` 这两个技能教会模型在何时以及以何种顺序调用工具。

### 推荐的任务交接证据

`kanban_complete(summary=..., metadata={...})` 在设计上具有灵活性：
`summary` 是供人类阅读的收尾总结，而 `metadata` 是供机器读取的交接信息，下游 Agent、审核人员或仪表板可以直接复用，无需从文本中提取。

对于工程和审核任务，建议采用以下可选的元数据结构：

```json
{
  "changed_files": ["path/to/file.py"],
  "verification": ["pytest tests/hermes_cli/test_kanban_db.py -q"],
  "dependencies": ["parent task id or external issue, if any"],
  "blocked_reason": null,
  "retry_notes": "what failed before, if this was a retry",
  "residual_risk": ["what was not tested or still needs human review"]
}
```

这些键名是一种约定，并非严格的模式要求。其有用的特性在于，每个工作者都留下了足够的证据，让下一位读者能快速回答四个问题：

1.  改变了什么？
2.  如何验证的？
3.  如果失败，如何解除阻塞或重试？
4.  还有哪些风险被有意保留？

请勿将秘密、原始日志、Token、OAuth 材料以及无关的对话记录放入 `metadata` 中。应存储指针和摘要。如果任务没有文件变更或测试，请在 `summary` 中明确说明，并使用 `metadata` 记录确实存在的证据，例如源 URL、问题 ID 或人工审核步骤。

### 工作者技能

任何需要能够处理看板任务的配置文件都必须加载 `kanban-worker` 技能。它教会工作者完整的生命周期流程，使用的是**工具调用**，而非 CLI 命令：

1.  启动时，调用 `kanban_show()` 来读取标题、正文、父任务交接信息、先前尝试记录以及完整的评论线程。
2.  通过终端工具执行 `cd $HERMES_KANBAN_WORKSPACE`，并在该目录下进行工作。
3.  在长时间操作期间，每隔几分钟调用一次 `kanban_heartbeat(note="...")`。**如果你的工作可能运行超过 1 小时，请至少每小时调用一次 `kanban_heartbeat`** —— 调度器会回收那些运行时间超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）且在过去一小时内没有心跳的任务，假设工作者崩溃且未进行清理。回收是良性的（任务会回到 `ready` 状态等待重新调度，不会增加失败计数），但你会丢失当前运行的进度。
4.  完成后调用 `kanban_complete(summary="...", metadata={...})`，如果遇到阻塞则调用 `kanban_block(reason="...")`。

最后的 `kanban_complete` / `kanban_block` 调用是工作者协议的一部分。如果工作者进程在任务仍处于 `running` 状态时以状态码 0 退出，调度器会将其视为协议违规，发出 `protocol_violation` 事件，并在下一次检查时自动阻塞该任务，而不是重新将其放入循环中。这通常意味着模型写了一个纯文本答案就退出了，没有使用看板工具接口。

`kanban-worker` 是一个捆绑技能，在安装和更新时会同步到每个配置文件中——无需单独的技能中心安装步骤。请验证你用于看板工作者的任何配置文件（`researcher`、`writer`、`ops` 等）中是否存在该技能：

```bash
hermes -p <your-worker-profile> skills list | grep kanban-worker
```

如果捆绑副本缺失，请为该配置文件恢复它：

```bash
hermes -p <your-worker-profile> skills reset kanban-worker --restore
```

调度器在启动每个工作者时也会自动传递 `--skills kanban-worker` 参数，因此即使配置文件的默认技能配置不包含它，工作者也始终能获得该模式库。

### 为特定任务固定额外技能

有时单个任务需要执行者配置文件默认不携带的专家上下文——例如需要 `translation` 技能的翻译工作、需要 `github-code-review` 的审核任务、需要 `security-pr-audit` 的安全审计。与其每次都编辑执行者的配置文件，不如直接将技能附加到任务上。

**通过编排器 Agent**（通常情况——一个 Agent 将工作路由给另一个 Agent），使用 `kanban_create` 工具的 `skills` 数组：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)

kanban_create(
    title="audit auth flow",
    assignee="reviewer",
    skills=["security-pr-audit", "github-code-review"],
)
```

**通过人工（CLI / 斜杠命令）**，对每个技能重复使用 `--skill`：

```bash
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

**通过仪表板**，在内联创建表单的 **skills** 字段中，以逗号分隔输入技能名称。

这些技能是内置 `kanban-worker` 的**附加项**——调度器会为每个技能（以及内置技能）发出一个 `--skills <name>` 标志，因此工作者启动时会加载所有技能。技能名称必须与执行者配置文件上实际安装的技能匹配（运行 `hermes skills list` 查看可用技能）；不支持运行时安装。

### 编排器技能

**一个行为良好的编排器不会自己完成工作。** 它将用户的目标分解为任务，链接它们，将每个任务分配给你已设置的配置文件之一，然后退居幕后。`kanban-orchestrator` 技能将此编码为工具调用模式：反诱惑规则、一个步骤 0 的配置文件发现提示词（调度器对未知的执行者名称会静默失败，因此编排器必须将每张卡片都基于你机器上实际存在的配置文件），以及一个围绕 `kanban_create` / `kanban_link` / `kanban_comment` 的分解手册。

一个典型的编排器回合（两个并行研究者交接给一个写作者）：

```
# 用户目标："draft a launch post on the ICP funding landscape"
kanban_create(title="research ICP funding, NA angle",  assignee="researcher-a", body="…")  # → t_r1
kanban_create(title="research ICP funding, EU angle",  assignee="researcher-b", body="…")  # → t_r2
kanban_create(
    title="synthesize ICP funding research into launch post draft",
    assignee="writer",
    parents=["t_r1", "t_r2"],        # 当两个研究者都完成时，此任务提升为 'ready' 状态
    body="one-pager, neutral tone, cite sources inline",
)                                     # → t_w1
# 可选：为后续发现的跨任务依赖添加链接，无需重新创建任务
kanban_link(parent_id="t_r1", child_id="t_followup")
kanban_complete(
    summary="decomposed into 2 parallel research tasks → 1 synthesis task; writer starts when both researchers finish",
)
```
`kanban-orchestrator` 是一个捆绑技能。它会在安装和更新时同步到每个配置文件中，因此没有单独的技能中心安装步骤。请验证它是否存在于你的编排器配置文件中：

```bash
hermes -p orchestrator skills list | grep kanban-orchestrator
```

如果捆绑副本缺失，请为该配置文件恢复它：

```bash
hermes -p orchestrator skills reset kanban-orchestrator --restore
```

为了获得最佳效果，请将其与一个工具集仅限于看板操作（`kanban`、`gateway`、`memory`）的配置文件配对，这样编排器即使尝试也无法执行实施任务。

## 仪表板 (GUI)

`/kanban` CLI 和斜杠命令足以无头运行看板，但可视化看板通常是人工参与环节的合适界面：分类、跨配置文件监督、阅读评论线程以及在列之间拖拽卡片。Hermes 将其作为 **捆绑的仪表板插件** 提供，位于 `plugins/kanban/` —— 不是核心功能，也不是独立服务 —— 遵循 [扩展仪表板](./extending-the-dashboard) 中概述的模型。

通过以下命令打开它：

```bash
hermes kanban init      # 一次性：如果不存在则创建 kanban.db
hermes dashboard        # "Kanban" 标签页出现在导航栏中，位于 "Skills" 之后
```

### 插件提供的内容

- 一个 **Kanban** 标签页，每个状态显示一列：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（加上切换开启时的 `archived`）。
  - `triage` 是粗略想法的暂存列。默认情况下（`kanban.auto_decompose: true`），调度器会自动对到达此处的任务运行 **分解器** —— 编排器配置文件读取粗略想法，查看你的配置文件列表（包含描述），并将任务展开为一个小的子任务图，路由到最合适的专家。原始任务作为每个子任务的父任务保持活动状态，以便在所有任务完成时编排器重新唤醒以判断完成情况。切换页面顶部的 **Orchestration: Auto/Manual** 药丸（或设置 `kanban.auto_decompose: false`）切换到手动模式，在此模式下，分类任务将保持不动，直到你点击卡片上的 **⚗ Decompose** 或运行 `hermes kanban decompose <id>`。对于不需要展开的任务（或没有编排器配置文件的设置），**✨ Specify** 按钮通过相同的 LLM 机制执行单任务规范重写（标题 + 包含目标、方法、验收标准的正文）。请参阅下面的 [自动与手动编排](#auto-vs-manual-orchestration)。
- 卡片显示任务 ID、标题、优先级徽章、租户标签、分配的配置文件、评论/链接计数、**进度药丸**（当任务有依赖项时显示 `N/M` 个子任务完成）以及“N 前创建”。每个卡片的复选框支持多选。
- **Running 列内的每个配置文件泳道** —— 工具栏复选框可切换 Running 列按分配者进行子分组。
- **通过 WebSocket 实时更新** —— 插件以短轮询间隔跟踪仅追加的 `task_events` 表；当任何配置文件（CLI、消息网关或其他仪表板标签页）采取行动时，看板会立即反映变化。重新加载会进行防抖处理，因此一系列事件只会触发一次重新获取。
- **拖放** 卡片在列之间移动以更改状态。放置操作会发送 `PATCH /api/plugins/kanban/tasks/:id`，该请求通过 CLI 使用的相同 `kanban_db` 代码路由 —— 三个界面永远不会偏离。移动到破坏性状态（`done`、`archived`、`blocked`）会提示确认。触摸设备使用基于指针的回退方案，因此看板可在平板电脑上使用。
- **内联创建** —— 点击任何列标题上的 `+` 以输入标题、分配者、优先级，以及（可选）从所有现有任务的下拉列表中选择父任务。按 Enter 创建任务，Shift+Enter 在标题字段中插入换行符，或按 Escape 取消。从 Triage 列创建会自动将新任务暂存在分类中。
- **多选与批量操作** —— shift/ctrl-点击卡片或勾选其复选框以将其添加到选择中。顶部会出现一个批量操作栏，包含批量状态转换、归档和重新分配（通过配置文件下拉列表或“(unassign)”）。破坏性批量操作会先确认。每个 ID 的部分失败会报告，而不会中止其余操作。
- **点击卡片**（不带 shift/ctrl）以打开侧边抽屉（按 Escape 或点击外部关闭），其中包含：
  - **可编辑标题** —— 点击标题进行重命名。
  - **可编辑分配者 / 优先级** —— 点击元数据行进行重写。
  - **可编辑描述** —— 默认以 Markdown 渲染（标题、粗体、斜体、行内代码、代码块、`http(s)` / `mailto:` 链接、项目符号列表），并带有一个“编辑”按钮，可切换为文本区域。Markdown 渲染是一个微小的、XSS 安全的渲染器 —— 每次替换都在 HTML 转义的输入上运行，只有 `http(s)` / `mailto:` 链接会通过，并且始终设置 `target="_blank"` + `rel="noopener noreferrer"`。
  - **依赖关系编辑器** —— 父任务和子任务的芯片列表，每个都带有 `×` 以取消链接，加上每个其他任务的下拉列表以添加新的父任务或子任务。循环尝试会在服务器端被拒绝，并显示明确消息。
  - **状态操作行**（→ triage / → ready / → running / block / unblock / complete / archive），破坏性转换会提示确认。对于 **Triage** 列中的卡片，该行还暴露了两个 LLM 驱动的操作：**⚗ Decompose** 将任务展开为一个子任务图，根据描述路由到专家配置文件（编排器驱动的路径），而 **✨ Specify** 执行单任务规范重写。当 LLM 认为任务无法从展开中受益时，Decompose 会回退到 specify 风格的提升，因此它是严格的超集。两者都可以通过 CLI（`hermes kanban decompose <id>` / `specify <id>` / `--all`）、任何消息网关平台（`/kanban decompose <id>`）以及通过 `POST /api/plugins/kanban/tasks/:id/decompose` 和 `…/specify` 以编程方式访问。在 `config.yaml` 中的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 下配置模型。
  - 结果部分（同样以 Markdown 渲染）、按 Enter 提交的评论线程、最后 20 个事件。
- **工具栏过滤器** —— 自由文本搜索、租户下拉列表（默认为 `config.yaml` 中的 `dashboard.kanban.default_tenant`）、分配者下拉列表、“显示已归档”切换开关、“按配置文件泳道”切换开关，以及一个 **Nudge dispatcher** 按钮，这样你就不必等待下一个 60 秒的滴答。
视觉上，目标是熟悉的 Linear / Fusion 布局：深色主题、带计数的列标题、彩色状态点、优先级和租户的胶囊标签。插件仅读取主题 CSS 变量（`--color-*`、`--radius`、`--font-mono` 等），因此它会根据当前激活的仪表板主题自动换肤。

### 自动与手动编排

看板有两种方式处理你拖放到 Triage 列的任务：

**自动（默认）** — `kanban.auto_decompose: true`。消息网关内嵌的调度器在每个 tick 运行**分解器**，上限为 `kanban.auto_decompose_per_tick`（默认每个 tick 3 个任务），这样批量加载的待处理任务就不会突发消耗辅助 LLM。分解器读取粗略想法，查看已安装的配置文件及其描述，并要求 LLM 生成 JSON 任务图：生成哪些任务、分配给谁以及它们之间的依赖关系。原始的待处理任务成为图中每个叶子节点的父任务，因此它会一直保持活动状态，直到整个图完成——然后提升回 `ready` 状态，以便其分配者（编排器配置文件）可以判断完成情况，并在工作未完成时添加更多任务。这就是“丢下一句话，然后走开”的流程。

**手动** — `kanban.auto_decompose: false`。待处理任务会一直停留在待处理状态，直到你采取行动。点击卡片上的 **⚗ Decompose** 按钮，运行 `hermes kanban decompose <id>`（或 `--all`），或在聊天中使用 `/kanban decompose <id>`。这与看板在分解器之前的行为相匹配，适用于当你想要完全控制何时运行什么时。

可以通过看板页面顶部的 **Orchestration: Auto/Manual** 胶囊标签（翠绿色 = 自动，灰暗色 = 手动）在两种模式之间切换，或直接编辑 `config.yaml`。两种模式都与 `hermes kanban specify` 共存——当你不想进行扇出时，它仍然可以作为单任务规范重写使用。

分解器的路由决策取决于配置文件描述，这是每个配置文件的标签原语，你可以通过 `hermes profile create --description "..."`、`hermes profile describe <name> --text "..."`、`hermes profile describe <name> --auto`（根据配置文件已安装的技能 + 模型由 LLM 生成）或仪表板扩展的 **Orchestration settings** 面板中的每个配置文件编辑器来设置。没有描述的配置文件仍然会出现在列表中——它们可以通过名称路由，只是精度较低。分解器**永远不会**将子任务分配给 `assignee=None`：当 LLM 选择未知配置文件时，子任务会被路由到 `kanban.default_assignee`（如果未设置，则回退到当前激活的默认配置文件）。

配置旋钮（均在 `~/.hermes/config.yaml` 的 `kanban:` 下）：

| 键 | 默认值 | 用途 |
|---|---|---|
| `auto_decompose` | `true` | 调度器每个 tick 自动运行分解器。 |
| `auto_decompose_per_tick` | `3` | 每个调度器 tick 分解任务数的上限。超出部分推迟到下一个 tick。 |
| `orchestrator_profile` | `""` | 拥有分解权限的配置文件。空 = 回退到当前激活的默认配置文件。 |
| `default_assignee` | `""` | 当 LLM 选择未知配置文件时，子任务的分配目标。空 = 回退到当前激活的默认配置文件。 |

以及两个辅助 LLM 插槽：

| 键 | 用途 |
|---|---|
| `auxiliary.kanban_decomposer` | 生成任务图的模型（由 Decompose 调用）。设置 `provider`/`model` 以覆盖主聊天模型。 |
| `auxiliary.profile_describer` | 自动生成配置文件描述的模型（由 `hermes profile describe --auto` 调用）。 |

### 架构

GUI 严格是一个**通过数据库读取 + 通过 kanban_db 写入**的层，没有自己的领域逻辑：

<!-- ascii-guard-ignore -->
```
┌────────────────────────┐      WebSocket (tails task_events)
│   React SPA (plugin)   │ ◀──────────────────────────────────┐
│   HTML5 drag-and-drop  │                                    │
└──────────┬─────────────┘                                    │
           │ REST over fetchJSON                              │
           ▼                                                  │
┌────────────────────────┐     writes call kanban_db.*        │
│  FastAPI router        │     directly — same code path      │
│  plugins/kanban/       │     the CLI /kanban verbs use      │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── append task_events ──────────┘
│  (WAL, shared)         │
└────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

### REST 接口

所有路由都挂载在 `/api/plugins/kanban/` 下，并受仪表板的临时会话令牌保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=<name>&include_archived=…` | 按状态列分组的完整看板，以及用于过滤器下拉列表的租户 + 分配者 |
| `GET` | `/tasks/:id` | 任务 + 评论 + 事件 + 链接 |
| `POST` | `/tasks` | 创建（包装 `kanban_db.create_task`，接受 `triage: bool` 和 `parents: [id, …]`） |
| `PATCH` | `/tasks/:id` | 状态 / 分配者 / 优先级 / 标题 / 正文 / 结果 |
| `POST` | `/tasks/bulk` | 对 `ids` 中的每个 id 应用相同的补丁（状态 / 归档 / 分配者 / 优先级）。每个 id 的失败会报告，但不会中止兄弟任务 |
| `POST` | `/tasks/:id/comments` | 追加评论 |
| `POST` | `/tasks/:id/specify` | 运行待处理规范器——辅助 LLM 充实任务正文并将其从 `triage` 提升到 `todo`。返回 `{ok, task_id, reason, new_title}`；`ok=false` 时附带“不在待处理状态”/无辅助客户端/LLM 错误等人类可读原因，返回 200，而非 4xx |
| `POST` | `/tasks/:id/decompose` | 运行看板分解器——辅助 LLM 生成任务图，助手原子性地创建子任务 + 链接根任务 + 将 `triage → todo` 翻转。返回 `{ok, task_id, reason, fanout, child_ids, new_title}`。与 `/specify` 相同的 LLM 错误返回 200 的约定。 |
| `GET` | `/profiles` | 列出已安装的配置文件及其描述（供仪表板的配置文件描述编辑器和编排器选择器使用）。 |
| `PATCH` | `/profiles/:name` | 设置或清除配置文件的描述（用户编写——`description_auto: false`）。返回 `{ok, profile, description}`。 |
| `POST` | `/profiles/:name/describe-auto` | 通过 `auxiliary.profile_describer` 为配置文件生成描述。以 `description_auto: true` 持久化，以便仪表板可以显示“待审核”徽章。 |
| `GET` | `/orchestration` | 读取看板编排设置（`orchestrator_profile`、`default_assignee`、`auto_decompose`）以及回退后的*已解析*有效值。 |
| `PUT` | `/orchestration` | 更新 `config.yaml` 中三个编排键的一个或多个。验证非空配置文件名称确实存在。 |
| `POST` | `/links` | 添加依赖关系（`parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 移除依赖关系 |
| `POST` | `/dispatch?max=…&dry_run=…` | 轻推调度器——跳过 60 秒等待 |
| `GET` | `/config` | 从 `config.yaml` 读取 `dashboard.kanban` 首选项——`default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` |
| `WS` | `/events?since=<event_id>` | `task_events` 行的实时流 |
每个处理器都是一个轻量封装——该插件约 700 行 Python 代码（包含路由器、WebSocket 尾部、批量批处理器和配置读取器），不添加任何新的业务逻辑。一个微小的 `_conn()` 辅助函数会在每次读写时自动初始化 `kanban.db`，因此无论是用户首次打开仪表盘、直接调用 REST API，还是运行 `hermes kanban init`，新安装都能正常工作。

### 仪表盘配置

在 `~/.hermes/config.yaml` 中，`dashboard.kanban` 下的任何这些键都会更改选项卡的默认值——插件在加载时通过 `GET /config` 读取它们：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # 预选租户过滤器
    lane_by_profile: true             # "按配置文件划分泳道" 切换的默认值
    include_archived_by_default: false
    render_markdown: true             # 设置为 false 以使用纯文本 <pre> 渲染
```

每个键都是可选的，并回退到显示的默认值。

### 安全模型

仪表盘的 HTTP 认证中间件[明确跳过 `/api/plugins/`](./extending-the-dashboard#backend-api-routes)——插件路由在设计上是未经认证的，因为仪表盘默认绑定到 localhost。这意味着看板的 REST 接口可以从主机上的任何进程访问。

WebSocket 额外增加了一步：它要求将仪表盘的临时会话 Token 作为 `?token=…` 查询参数（浏览器无法在升级请求上设置 `Authorization`），这与浏览器内 PTY 桥接器使用的模式相匹配。

如果你运行 `hermes dashboard --host 0.0.0.0`，每个插件路由——包括看板——都将可以从网络访问。**不要在共享主机上这样做。** 看板包含任务正文、评论和工作空间路径；攻击者访问这些路由将获得对整个协作表面的读取权限，并且还可以创建/重新分配/归档任务。

`~/.hermes/kanban.db` 中的任务特意设计为与配置文件无关（这是协调原语）。如果你使用 `hermes -p <profile> dashboard` 打开仪表盘，看板仍会显示主机上任何其他配置文件创建的任务。同一用户拥有所有配置文件，但如果存在多个人格，这一点值得注意。

### 实时更新

`task_events` 是一个仅追加的 SQLite 表，具有单调递增的 `id`。WebSocket 端点保存每个客户端最后看到的事件 id，并在新行到达时推送。当一批事件到达时，前端重新加载（非常廉价的）看板端点——这比尝试根据每种事件类型修补本地状态更简单、更正确。WAL 模式意味着读取循环永远不会阻塞调度器的 `BEGIN IMMEDIATE` 声明事务。

### 扩展它

该插件使用标准的 Hermes 仪表盘插件契约——完整的清单参考、Shell 插槽、页面作用域插槽和 Plugin SDK，请参阅[扩展仪表盘](./extending-the-dashboard)。额外的列、自定义卡片样式、租户过滤布局或完整的 `tab.override` 替换，都可以在不分叉此插件的情况下实现。

要禁用而不删除：在 `config.yaml` 中添加 `dashboard.plugins.kanban.enabled: false`（或删除 `plugins/kanban/dashboard/manifest.json`）。

### 范围边界

GUI 特意设计得很精简。插件所做的一切都可以通过 CLI 访问；插件只是让人类操作更舒适。自动分配、预算、治理门禁和组织结构图视图仍属于用户空间——一个路由器配置文件、另一个插件或重用 `tools/approval.py`——正如设计规范中超出范围部分所列出的那样。

## CLI 命令参考

这是**你**（或脚本、定时任务、仪表盘）用来驱动看板的接口。在调度器内部运行的 Worker 使用 `kanban_*` [工具接口](#how-workers-interact-with-the-board)进行相同的操作——这里的 CLI 和那里的工具都通过 `kanban_db` 路由，因此这两个接口在构造上是一致的。

```
hermes kanban init                                     # 创建 kanban.db + 打印守护进程提示
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|worktree:<path>|dir:<path>]
                                [--branch <name>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--max-retries N]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived]
        [--workflow-template-id <id>] [--current-step-key <key>]
        [--sort created|created-desc|priority|priority-desc|status|assignee|title|updated]
        [--json]
hermes kanban show <id> [--json]
hermes kanban assign <id> <profile>                    # 或 'none' 以取消分配
hermes kanban link <parent_id> <child_id>
hermes kanban unlink <parent_id> <child_id>
hermes kanban claim <id> [--ttl SECONDS]
hermes kanban comment <id> "<text>" [--author NAME]

# 批量动词 —— 接受多个 id：
hermes kanban complete <id>... [--result "..."]
hermes kanban block <id> "<reason>" [--ids <id>...]
hermes kanban unblock <id>...
hermes kanban archive <id>...

hermes kanban tail <id>                                # 跟随单个任务的事件流
hermes kanban watch [--assignee P] [--tenant T]        # 将 ALL 事件实时流式传输到终端
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # 长时间操作的 Worker 活跃信号
hermes kanban runs <id> [--json]                       # 尝试历史记录（每次运行一行）
hermes kanban assignees [--json]                       # 磁盘上的配置文件 + 每个分配者的任务计数
hermes kanban dispatch [--dry-run] [--max N]           # 一次性调度
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # 已弃用 —— 独立调度器（改用 `hermes gateway start`）
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # 按状态 + 按分配者计数
hermes kanban log <id> [--tail BYTES]                  # 来自 ~/.hermes/kanban/logs/ 的 Worker 日志
hermes kanban notify-subscribe <id>                    # 消息网关桥接钩子（由网关中的 /kanban 使用）
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # Worker 看到的上下文
hermes kanban specify [<id> | --all] [--tenant T]      # 将待办列中的想法具体化
        [--author NAME] [--json]                       #   为完整规范并提升为待办事项
hermes kanban gc [--event-retention-days N]            # 工作空间 + 旧事件 + 旧日志
        [--log-retention-days N]
```
所有命令在交互式 CLI 和消息网关中也可作为斜杠命令使用（参见下面的 [`/kanban` 斜杠命令](#kanban-slash-command)）。

`--max-retries` 是针对调度器的每个任务断路器覆盖设置。`--max-retries 1` 会在第一次非成功尝试时阻塞任务，而 `--max-retries 3` 允许两次重试，并在第三次失败时阻塞。省略此参数则使用 `config.yaml` 中的 `kanban.failure_limit`，然后是内置默认值。

### 并发、调度和子任务提升配置

| 配置键 | 默认值 | 作用 |
|------------|---------|--------------|
| `kanban.max_in_progress` | 未设置（无限制） | 限制同时运行的任务数量。当看板上已有 N 个任务正在运行时，调度器会跳过生成更多任务 —— 这对于慢速工作者（本地 LLM、资源受限的主机）很有用，这样它们可以在更多任务堆积和超时之前完成手头的工作。无效或小于 1 的值会记录警告并表现为无限制。 |
| `kanban.auto_promote_children` | `true` | 当 `decompose_triage_task()` 生成没有父任务阻塞依赖的子任务后，它们会自动提升到 `ready` 状态，以便调度器可以拾取它们。设置为 `false` 则需要手动审核 —— 子任务将保持在 `todo` 状态，直到你提升它们。 |
| `kanban.default_workdir` | 未设置 | 当 `--workspace` 或任务本身都没有覆盖时，应用于新任务的看板级默认工作目录。每个任务的 `workspace:` 设置仍然优先。 |

```yaml
kanban:
  max_in_progress: 2
  auto_promote_children: false
  default_workdir: ~/work/active-project
```

### 定时任务启动 (`scheduled_at`)

在任务上设置 `scheduled_at` 以延迟调度到特定时间。调度器会跳过 `scheduled_at` 在未来时间的就绪任务，并在该时间戳之后的第一个调度周期拾取它们。

```bash
hermes kanban create "nightly backup audit" \
  --assignee ops --scheduled-at "2026-06-01T03:00:00Z"
```

### 重生防护

当任务在前一次运行中遇到配额/认证/429 错误（`blocker_auth`），或在防护窗口内成功完成运行（`recent_success`），或最近的任务评论链接到 GitHub PR（`active_pr`）时，调度器会拒绝重新生成就绪任务。这可以防止在人工跟进同一错误或任务时重复出现工作者风暴。请参阅[事件参考](#event-reference)中的 `respawn_guarded` 行。

### 拖拽删除和批量删除（仪表板）

仪表板在看板页面上暴露了一个**垃圾桶放置区** —— 将任何卡片拖入其中即可删除任务（级联删除 `task_events`、子任务链接和订阅）。确认提示可防止意外操作。批量删除也可以通过 `DELETE /api/plugins/kanban/tasks` 并附带 JSON 请求体 `{"ids": ["t_abc", "t_def", ...]}` 来实现。

### 工作者可见性端点

仪表板插件 API 现在暴露了三个用于外部监控的只读端点：

| 端点 | 返回内容 |
|----------|---------|
| `GET /api/plugins/kanban/workers/active` | 当前已生成的工作者，包含 PID、配置文件、任务 ID、启动时间、最后心跳 |
| `GET /api/plugins/kanban/runs/{id}` | 单次运行详情 —— 任务 ID、状态、开始/结束时间、退出代码、日志路径 |
| `GET /api/plugins/kanban/inspect` | 调度器组合快照 —— 积压任务、进行中任务数量与 `max_in_progress` 对比、最近事件 |

所有三个端点都受到与看板插件 API 其余部分相同的仪表板插件认证保护。

### Kanban Swarm 拓扑助手

`hermes kanban swarm` 一次性创建持久的 **Kanban Swarm v1** 图：一个已完成的根/白板卡片、N 个并行的工作者卡片、一个依赖所有工作者的验证者卡片，以及一个依赖验证者的合成者卡片。共享的 Swarm 上下文（"白板"）作为结构化 JSON 评论存储在根卡片上，以便任何工作者都可以读取。

```bash
hermes kanban swarm "Design a multi-region failover plan" \
  --workers researcher,architect,sre \
  --verifier reviewer --synthesizer writer
```

生成的图会正常调度 —— 工作者并行运行，验证者在所有工作者完成后唤醒，合成者在验证者标记工作无误后唤醒。

## `/kanban` 斜杠命令 {#kanban-slash-command}

每个 `hermes kanban <action>` 动词也可以作为 `/kanban <action>` 访问 —— 无论是在交互式 `hermes chat` 会话**内部**，还是从任何网关平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、SMS）。两种界面都调用完全相同的 `hermes_cli.kanban.run_slash()` 入口点，该入口点复用 `hermes kanban` 的 argparse 树，因此参数界面、标志和输出格式在 CLI、`/kanban` 和 `hermes kanban` 之间是相同的。你无需离开聊天界面即可驱动看板。

```
/kanban list
/kanban show t_abcd
/kanban create "write launch post" --assignee writer --parent t_research
/kanban comment t_abcd "looks good, ship it"
/kanban unblock t_abcd
/kanban dispatch --max 3
/kanban specify t_abcd                  # 将一句话分类任务充实为真正的规范
/kanban specify --all --tenant engineering  # 一次性处理某个租户下的所有分类任务
```

多词参数的引用方式与在 shell 中相同 —— `run_slash` 使用 `shlex.split` 解析行的其余部分，因此 `"..."` 和 `'...'` 都有效。

### 运行中用法：`/kanban` 绕过运行中 Agent 防护

网关通常会在 Agent 仍在思考时排队处理斜杠命令和用户消息 —— 这就是防止你在第一个回合进行中意外启动第二个回合的机制。**`/kanban` 明确豁免于此防护。** 看板位于 `~/.hermes/kanban.db` 中，而不是在运行中 Agent 的状态中，因此读取操作（`list`、`show`、`context`、`tail`、`watch`、`stats`、`runs`）和写入操作（`comment`、`unblock`、`block`、`assign`、`archive`、`create`、`link`、…）都会立即执行，即使在回合进行中也是如此。

这种分离的整个意义在于：

- 一个工作者因等待对等方而阻塞 → 你从手机发送 `/kanban unblock t_abcd`，调度器会在下一个调度周期拾取该对等方。被阻塞的工作者不会被中断 —— 它只是不再被阻塞。
- 你发现一个需要人工上下文的卡片 → `/kanban comment t_xyz "use the 2026 schema, not 2025"` 会出现在任务线程中，该任务的*下一次*运行将在 `kanban_show()` 中读取它。
- 你想知道你的工作舰队在做什么而不停止编排器 → `/kanban list --mine` 或 `/kanban stats` 会检查看板而不影响你的主对话。
### 在 `/kanban create` 时自动订阅（仅限消息网关）

当你通过消息网关使用 `/kanban create "…"` 创建任务时，发起聊天的会话（平台 + 聊天 ID + 线程 ID）会自动订阅该任务的终止事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）。你将在每个终止事件发生时收到一条消息——包括 `completed` 事件中 worker 结果摘要的第一行——而无需轮询或记住任务 ID。

```
你> /kanban create "转录今天的播客" --assignee transcriber
机器人> 已创建 t_9fc1a3  (就绪, 负责人=transcriber)
     （已订阅 — 当 t_9fc1a3 完成或阻塞时你会收到通知）

… 大约 8 分钟后 …

机器人> ✓ t_9fc1a3 由 transcriber 完成
     转录了 42 分钟，已保存至 podcast/2026-05-04.md
```

一旦任务达到 `done` 或 `archived` 状态，订阅会自动移除。如果你使用 `--json`（机器输出）通过脚本创建任务，则会跳过自动订阅——假设脚本调用者希望通过 `/kanban notify-subscribe` 显式管理订阅。

### 消息中的输出截断

消息网关平台有实际的消息长度限制。如果 `/kanban list`、`/kanban show` 或 `/kanban tail` 产生的输出超过约 3800 个字符，响应将被截断，并带有 `… (已截断；请在终端中使用 \`hermes kanban …\` 获取完整输出)` 的页脚。CLI 界面没有此类限制。

### 自动补全

在交互式 CLI 中，输入 `/kanban ` 并按 Tab 键会循环显示内置的子命令列表（`list`、`ls`、`show`、`create`、`assign`、`link`、`unlink`、`claim`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`、`dispatch`、`context`、`init`、`gc`）。上面 CLI 参考中列出的其余动词（`watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-subscribe`、`notify-list`、`notify-unsubscribe`、`daemon`）也有效——它们只是尚未加入自动补全提示列表。

## 协作模式

看板支持以下八种模式，无需任何新的原语：

| 模式 | 形态 | 示例 |
|---|---|---|
| **P1 扇出** | N 个同级任务，相同角色 | "并行研究 5 个角度" |
| **P2 流水线** | 角色链：scout → editor → writer | 每日简报汇编 |
| **P3 投票 / 法定人数** | N 个同级任务 + 1 个聚合任务 | 3 个研究者 → 1 个审阅者挑选 |
| **P4 长期运行的日志** | 相同配置 + 共享目录 + 定时任务 | Obsidian 知识库 |
| **P5 人在回路** | worker 阻塞 → 用户评论 → 解除阻塞 | 模糊决策 |
| **P6 `@提及`** | 从文本中内联路由 | `@reviewer 看看这个` |
| **P7 线程作用域的工作区** | 线程中的 `/kanban here` | 每个项目的消息网关线程 |
| **P8 舰队耕作** | 一个配置，N 个主题 | 50 个社交账户 |
| **P9 分类指定器** | 粗略想法 → `triage` → `hermes kanban specify` 扩展正文 → `todo` | "将这个一句话想法转化为一个详细说明的任务" |

关于每种模式的具体示例，请参阅 `docs/hermes-kanban-v1-spec.pdf`。

## 多租户使用

当一个专业舰队服务于多个业务时，为每个任务打上租户标签：

```bash
hermes kanban create "月度报告" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

Worker 会收到 `$HERMES_TENANT` 环境变量，并通过前缀对其记忆写入进行命名空间隔离。看板、调度器和配置定义都是共享的；只有数据是作用域隔离的。

## 消息网关通知

当你从消息网关（Telegram、Discord、Slack 等）运行 `/kanban create …` 时，发起聊天的会话会自动订阅新任务。消息网关的后台通知器每隔几秒轮询一次 `task_events`，并将每个终止事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）的一条消息发送到该聊天会话。已完成的任务还会发送 worker 的 `--result` 的第一行，这样你无需使用 `/kanban show` 就能看到结果。

你可以从 CLI 显式管理订阅——当脚本/定时任务希望通知一个非其发起的聊天会话时，这很有用：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务达到 `done` 或 `archived` 状态，订阅会自动移除；无需手动清理。

## 运行记录 — 每次尝试一行

任务是工作的逻辑单元；**运行记录** 是执行它的一次尝试。当调度器认领一个就绪任务时，它会在 `task_runs` 中创建一行，并将 `tasks.current_run_id` 指向它。当该次尝试结束时——完成、阻塞、崩溃、超时、生成失败、被回收——运行记录行会以一个 `outcome` 关闭，并且任务的指针被清除。一个被尝试了三次的任务会有三行 `task_runs` 记录。

为什么需要两个表而不是直接修改任务：你需要 **完整的尝试历史** 来进行实际的事后分析（"第二次审阅者尝试得以批准，第三次合并了"），并且你需要一个干净的地方来挂载每次尝试的元数据——哪些文件被更改、哪些测试运行了、审阅者记录了哪些发现。这些是运行事实，而不是任务事实。

运行记录也是 **结构化交接** 的所在。当一个 worker 完成任务时（通过 `kanban_complete(...)`），它可以传递：

- `summary`（工具参数）/ `--summary`（CLI）——人工交接；记录在运行记录上；下游子任务在其 `build_worker_context` 中可以看到它。
- `metadata`（工具参数）/ `--metadata`（CLI）——运行记录上的自由格式 JSON 字典；子任务可以看到它与摘要一起序列化。
- `result`（工具参数）/ `--result`（CLI）——记录在任务行上的简短日志行（遗留字段，为向后兼容而保留）。

下游子任务读取每个父任务最近一次完成的运行记录的摘要 + 元数据。重试的 worker 读取其自身任务之前的尝试（结果、摘要、错误），这样它们就不会重复已经失败的路径。

```
# worker 实际做的事情 —— 一个工具调用，来自 agent 循环内部：
kanban_complete(
    summary="实现了令牌桶，基于 user_id 的键，带 IP 回退，所有测试通过",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
    result="速率限制器已发布",
)
```
当您（人类）需要完成一个工作者无法完成的任务时——例如被放弃的任务，或者您从仪表板手动标记为完成的任务——可以通过 CLI 执行相同的交接操作：

```bash
hermes kanban complete t_abcd \
    --result "rate limiter shipped" \
    --summary "implemented token bucket, keys on user_id with IP fallback, all tests pass" \
    --metadata '{"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14}'

# 查看重试任务的尝试历史：
hermes kanban runs t_abcd
#   #  OUTCOME       PROFILE           ELAPSED  STARTED
#   1  blocked       worker               12s  2026-04-27 14:02
#        → BLOCKED: need decision on rate-limit key
#   2  completed     worker                8m   2026-04-27 15:18
#        → implemented token bucket, keys on user_id with IP fallback
```

运行记录会在仪表板（抽屉中的“运行历史”部分，每次尝试显示为一行彩色记录）和 REST API 中公开（`GET /api/plugins/kanban/tasks/:id` 返回一个 `runs[]` 数组）。使用 `PATCH /api/plugins/kanban/tasks/:id` 并附带 `{status: "done", summary, metadata}` 会将两者转发给内核，因此仪表板的“标记完成”按钮与 CLI 命令等效。`task_events` 表中的行会携带它们所属的 `run_id`，以便 UI 可以按尝试进行分组，并且 `completed` 事件在其有效负载中嵌入了第一行摘要（上限为 400 个字符），这样消息网关通知器就可以在不进行第二次 SQL 往返的情况下渲染结构化的交接信息。

**批量关闭注意事项。** `hermes kanban complete a b c --summary X` 会被拒绝——结构化交接是针对每次运行的，因此将相同的摘要复制粘贴到 N 个任务几乎总是错误的。对于常见的“我完成了一堆管理任务”的情况，*不带* `--summary` / `--metadata` 的批量关闭仍然有效。

**状态变更回收的运行。** 如果您在仪表板中将一个正在运行的任务从 `running` 拖走（回到 `ready`，或直接到 `todo`），或者归档一个仍在运行的任务，正在进行的运行将以 `outcome='reclaimed'` 关闭，而不是被孤立。当 `tasks.current_run_id` 为 `NULL` 时，`task_runs` 行始终处于终止状态，反之亦然——这个不变量在 CLI、仪表板、调度器和通知器中都成立。

**从未被认领的完成任务的合成运行。** 完成或阻塞一个从未被认领的任务（例如，人类从仪表板使用摘要关闭一个 `ready` 任务，或者 CLI 用户运行 `hermes kanban complete <ready-task> --summary X`）否则会丢失交接信息。相反，内核会插入一个零持续时间的运行行（`started_at == ended_at`），携带摘要/元数据/原因，以便尝试历史保持完整。`completed` / `blocked` 事件的 `run_id` 指向该行。

**实时抽屉刷新。** 当仪表板的 WebSocket 事件流报告用户当前正在查看的任务有新事件时，抽屉会自行重新加载（通过一个按任务计数的事件计数器，该计数器被编织到其 `useEffect` 依赖项列表中）。不再需要关闭并重新打开抽屉来查看运行的新行或更新的结果。

### 向前兼容性

`tasks` 表上的两个可为空的列是为 v2 工作流路由保留的：`workflow_template_id`（此任务属于哪个模板）和 `current_step_key`（该模板中哪个步骤处于活动状态）。v1 内核在路由时会忽略它们，但允许客户端写入它们，因此 v2 版本可以添加路由机制而无需进行另一次模式迁移。

## 事件参考

每次转换都会向 `task_events` 追加一行。每行都带有一个可选的 `run_id`，以便 UI 可以按尝试对事件进行分组。种类分为三个集群，便于过滤（`hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期**（任务作为逻辑单元发生了什么变化）：

| 种类 | 有效负载 | 何时发生 |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | 任务插入。`run_id` 为 `NULL`。 |
| `promoted` | — | `todo → ready`，因为所有父任务都达到 `done`。`run_id` 为 `NULL`。 |
| `claimed` | `{lock, expires, run_id}` | 调度器原子性地为生成认领了一个 `ready` 任务。 |
| `completed` | `{result_len, summary?}` | 工作者写入了 `--result` / `--summary` 并且任务达到 `done`。`summary` 是第一行交接信息（400 字符上限）；完整版本位于运行行上。如果在从未被认领的任务上调用 `complete_task` 并带有交接字段，则会合成一个零持续时间的运行，以便 `run_id` 仍然指向某个内容。 |
| `blocked` | `{reason}` | 工作者或人类将任务翻转为 `blocked`。当在从未被认领的任务上调用 `--reason` 时，会合成一个零持续时间的运行。 |
| `unblocked` | — | `blocked → ready`，手动或通过 `/unblock`。`run_id` 为 `NULL`。 |
| `archived` | — | 从默认看板隐藏。如果任务仍在运行，则携带作为副作用被回收的运行的 `run_id`。 |

**编辑**（人类驱动的非转换更改）：

| 种类 | 有效负载 | 何时发生 |
|---|---|---|
| `assigned` | `{assignee}` | 负责人变更（包括取消分配）。 |
| `edited` | `{fields}` | 标题或正文更新。 |
| `reprioritized` | `{priority}` | 优先级变更。 |
| `status` | `{status}` | 仪表板拖放直接写入状态（例如 `todo → ready`）。当从 `running` 拖走时，携带被回收的运行的 `run_id`；否则 `run_id` 为 NULL。 |

**工作者遥测**（关于执行过程，而非逻辑任务）：

| 种类 | 有效负载 | 何时发生 |
|---|---|---|
| `spawned` | `{pid}` | 调度器成功启动了一个工作者进程。 |
| `heartbeat` | `{note?}` | 工作者在长时间操作期间调用 `hermes kanban heartbeat $TASK` 以发出存活信号。 |
| `reclaimed` | `{stale_lock}` | 认领 TTL 过期但未完成；任务返回 `ready`。 |
| `crashed` | `{pid, claimer}` | 工作者 PID 不再存活，但 TTL 尚未过期。 |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | 超过 `max_runtime_seconds`；调度器发送 SIGTERM（然后在 5 秒宽限期后发送 SIGKILL）并重新排队。 |
| `stale` | `{elapsed_seconds, last_heartbeat_at, heartbeat_age_seconds, timeout_seconds, pid, terminated}` | 任务运行时间超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）*并且* 在过去一小时内没有收到 `kanban_heartbeat`。调度器向本地主机上的工作者（如果有）发送 SIGTERM，将任务重置为 `ready` 以重新调度。*不* 增加失败计数器（stale 是调度器侧的缺席检测，不是工作者故障）。运行长时间操作的工作者应至少每小时调用一次 `kanban_heartbeat` 以避免此情况。 |
| `respawn_guarded` | `{reason}` | 调度器拒绝在此刻重新生成此就绪任务。原因：`blocker_auth`（上次失败是配额/认证/429 错误——等待速率窗口重置）、`recent_success`（在过去一小时内发生了完成的运行——等待审查后再重新运行）、`active_pr`（最近的评论中出现了 GitHub PR URL——先前的工作者已经打开了 PR）。任务保持在 `ready`；下一次时刻有机会再次生成。如果底层条件持续存在，正常的 `consecutive_failures` 断路器将在 `failure_limit` 次失败后通过 `gave_up` 自动阻塞。 |
| `spawn_failed` | `{error, failures}` | 一次生成尝试失败（缺少 PATH、工作空间无法挂载等）。计数器递增；任务返回 `ready` 以重试。 |
| `protocol_violation` | `{pid, claimer, exit_code}` | 工作者在任务仍为 `running` 时成功退出，通常是因为它在没有调用 `kanban_complete` 或 `kanban_block` 的情况下应答。调度器还会发出 `gave_up` 并立即自动阻塞，而不是重试。 |
| `gave_up` | `{failures, effective_limit, limit_source, error}` | 在 N 次连续非成功尝试后断路器触发。任务自动阻塞并显示最后一个错误。有效限制解析为任务 `max_retries`，然后是调度器 `failure_limit` / `kanban.failure_limit`，最后是内置默认值。 |
`hermes kanban tail <id>` 显示单个任务的这些信息。`hermes kanban watch` 则在整个看板范围内流式输出它们。

## 不在范围内

Kanban 设计上是单主机的。`~/.hermes/kanban.db` 是一个本地的 SQLite 文件，并且调度器在同一台机器上生成工作进程。不支持在两个主机之间运行共享看板——没有用于协调“主机 A 上的工作进程 X，主机 B 上的工作进程 Y”的底层原语，并且崩溃检测路径假设 PID 是主机本地的。如果你需要多主机支持，请在每个主机上运行一个独立的看板，并使用 `delegate_task` / 消息队列来桥接它们。

## 设计规范

完整的设计——架构、并发正确性、与其他系统的比较、实施计划、风险、待解决问题——位于 `docs/hermes-kanban-v1-spec.pdf` 中。在提交任何行为变更的 PR 之前，请先阅读该文档。