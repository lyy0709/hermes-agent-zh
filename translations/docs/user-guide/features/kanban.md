---
sidebar_position: 12
title: "看板（多 Agent 协作板）"
description: "基于持久化 SQLite 的任务板，用于协调多个 Hermes 人格配置"

# 看板 — 多 Agent 人格配置协作

> **需要引导教程？** 阅读 [看板教程](./kanban-tutorial) — 包含四个用户场景（独立开发者、舰队式运营、带重试的角色流水线、熔断器），并附有每个场景的仪表盘截图。本页是参考文档；教程是叙述性指南。

Hermes 看板是一个持久化的任务板，在所有 Hermes 人格配置之间共享，允许多个具名 Agent 协作处理工作，而无需依赖脆弱的进程内子 Agent 集群。每个任务都是 `~/.hermes/kanban.db` 中的一行；每次交接都是任何人都可以读写的一行；每个工作者都是一个拥有自己身份的完整操作系统进程。

这种形态覆盖了 `delegate_task` 无法处理的工作负载：

- **研究分类** — 并行研究员 + 分析师 + 写作者，人在回路。
- **定时运维** — 每日重复简报，数周内构建日志。
- **数字孪生** — 持久的具名助手（`inbox-triage`、`ops-review`），随时间积累记忆。
- **工程流水线** — 分解 → 在并行工作树中实现 → 评审 → 迭代 → 提交 PR。
- **舰队式工作** — 一个专家管理 N 个主体（50 个社交账户，12 个监控服务）。

关于完整的设计原理、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种经典协作模式，请参阅代码仓库中的 `docs/hermes-kanban-v1-spec.pdf`。

## 看板 vs. `delegate_task`

它们看起来相似；但它们不是同一种原语。

| | `delegate_task` | 看板 |
|---|---|---|
| 形态 | RPC 调用（分叉 → 汇合） | 持久化消息队列 + 状态机 |
| 父进程 | 阻塞直到子进程返回 | `create` 后即发即弃 |
| 子进程身份 | 匿名子 Agent | 具有持久记忆的具名人格配置 |
| 可恢复性 | 无 — 失败即失败 | 阻塞 → 解除阻塞 → 重新运行；崩溃 → 回收 |
| 人在回路 | 不支持 | 可在任意节点评论 / 解除阻塞 |
| 每个任务的 Agent 数 | 一次调用 = 一个子 Agent | 任务生命周期内 N 个 Agent（重试、评审、跟进） |
| 审计追踪 | 在上下文压缩时丢失 | SQLite 中的持久化行，永久保存 |
| 协调方式 | 分层（调用者 → 被调用者） | 对等 — 任何人格配置都可读写任何任务 |

**一句话区分：** `delegate_task` 是一个函数调用；看板是一个工作队列，其中每次交接都是一行，任何人格配置（或人）都可以查看和编辑。

**在以下情况使用 `delegate_task`：** 父 Agent 在继续之前需要一个简短的推理答案，没有人员参与，结果返回到父进程的上下文中。

**在以下情况使用看板：** 工作跨越 Agent 边界，需要在重启后存活，可能需要人工输入，可能由不同的角色接手，或者需要在事后可被发现。

它们可以共存：一个看板工作者在其运行期间内部可以调用 `delegate_task`。

## 核心概念

- **任务** — 包含标题、可选正文、一个指派人（人格配置名称）、状态（`triage | todo | ready | running | blocked | done | archived`）、可选的租户命名空间、可选的幂等键（用于重试自动化的去重）的一行数据。
- **链接** — `task_links` 行，记录父任务 → 子任务的依赖关系。当所有父任务都处于 `done` 状态时，调度器会将子任务从 `todo` 提升为 `ready`。
- **评论** — Agent 间的通信协议。Agent 和人员追加评论；当工作者（重新）启动时，它会读取完整的评论线程作为其上下文的一部分。
- **工作空间** — 工作者在其中操作的目录。有三种类型：
  - `scratch`（默认）— `~/.hermes/kanban/workspaces/<id>/` 下的全新临时目录。
  - `dir:<path>` — 一个现有的共享目录（Obsidian 保险库、邮件操作目录、每个账户的文件夹）。**必须是绝对路径。** 像 `dir:../tenants/foo/` 这样的相对路径在调度时会被拒绝，因为它们会根据调度器当时所在的当前工作目录进行解析，这是不明确的，并且是一个混淆代理的逃逸向量。除此之外，路径是受信任的 — 这是你的机器，你的文件系统，工作者以你的用户 ID 运行。这是受信任的本地用户威胁模型；看板在设计上是单主机的。
  - `worktree` — 用于编码任务的 `.worktrees/<id>/` 下的 git 工作树。由工作者端的 `git worktree add` 创建。
- **调度器** — 一个长期运行的循环，每 N 秒（默认 60 秒）执行一次：回收过期的认领、回收崩溃的工作者（PID 消失但 TTL 尚未过期）、提升就绪任务、原子性地认领任务、生成指派的配置。默认在**消息网关内部**运行（`kanban.dispatch_in_gateway: true`）。在同一任务上连续约 5 次生成失败后，调度器会自动将其阻塞，并将最后一个错误作为原因 — 防止因配置不存在、工作空间无法挂载等任务而导致的系统颠簸。
- **租户** — 可选的字符串命名空间。一个专家舰队可以为多个业务提供服务（`--tenant business-a`），通过工作空间路径和记忆键前缀实现数据隔离。

## 快速开始

```bash
# 1. 创建看板
hermes kanban init

# 2. 启动消息网关（托管嵌入式调度器）
hermes gateway start

# 3. 创建一个任务
hermes kanban create "研究 AI 融资前景" --assignee researcher

# 4. 实时查看活动
hermes kanban watch

# 5. 查看看板
hermes kanban list
hermes kanban stats
```

### 消息网关嵌入式调度器（默认）

调度器在消息网关进程内部运行。无需安装任何东西，也无需管理单独的服务 — 只要消息网关在运行，就绪的任务就会在下一个调度周期（默认 60 秒）被拾取。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # 默认值
  dispatch_interval_seconds: 60    # 默认值
```

可以通过 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 在运行时覆盖配置标志以进行调试。标准的消息网关监控方式适用：直接运行 `hermes gateway start`，或者将消息网关配置为 systemd 用户单元（参见消息网关文档）。如果没有运行的消息网关，`ready` 状态的任务将保持原状，直到有消息网关启动 — `hermes kanban create` 在创建时会对此发出警告。
将 `hermes kanban daemon` 作为独立进程运行的方式**已弃用**；请使用消息网关。如果你确实无法运行消息网关（无头主机策略禁止长时间运行的服务等），`--force` 参数提供了一个临时解决方案，可以在一个发布周期内继续使用旧的独立守护进程，但**同时**运行一个嵌入消息网关的调度器**和**一个独立的守护进程来操作同一个 `kanban.db` 会导致任务声明竞争，这是不受支持的。

### 幂等创建（用于自动化 / Webhook）

```bash
# 首次调用创建任务。任何后续使用相同 key 的调用
# 将返回现有任务 ID 而不是重复创建。
hermes kanban create "nightly ops review" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

### 批量 CLI 动词

所有生命周期动词都接受多个 ID，因此你可以用一个命令清理一批任务：

```bash
hermes kanban complete t_abc t_def t_hij --result "batch wrap"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "need input" --ids t_def t_hij
```

## 工作进程如何与看板交互

当调度器生成一个工作进程时，它会在子进程的环境中设置 `HERMES_KANBAN_TASK`。这个环境变量是专用**看板工具集**的入口——包含 7 个普通 Agent 模式永远看不到的工具：

| 工具 | 用途 |
|---|---|
| `kanban_show` | 读取当前任务（标题、正文、先前尝试、父任务交接、评论、完整的 `worker_context`）。默认为环境中的任务 ID。 |
| `kanban_complete` | 完成任务，附带 `summary` + `metadata` 结构化交接。 |
| `kanban_block` | 因需要人工输入而阻塞任务。 |
| `kanban_heartbeat` | 在长时间操作期间发送存活信号。 |
| `kanban_comment` | 追加到任务讨论线程。 |
| `kanban_create` | （编排器）创建子任务。 |
| `kanban_link` | （编排器）事后添加依赖关系边。 |

**为什么用工具而不是直接调用 `hermes kanban` 命令？** 三个原因：

1.  **后端可移植性。** 工作进程的终端工具可能指向远程后端（Docker / Modal / Singularity / SSH），在容器内部运行 `hermes kanban complete` 时，`hermes` 可能未安装且数据库未挂载。看板工具在 Agent 自身的 Python 进程中运行，无论终端后端如何，始终能访问 `~/.hermes/kanban.db`。
2.  **避免 shell 引用的脆弱性。** 通过 shlex + argparse 传递 `--metadata '{"files": [...]}'` 是一个潜在的隐患。结构化的工具参数避免了这个问题。
3.  **更好的错误处理。** 工具结果是模型可以推理的结构化 JSON，而不是它必须解析的 stderr 字符串。

**对普通会话的零模式占用。** 一个常规的 `hermes chat` 会话在其模式中**没有**任何 `kanban_*` 工具。每个工具的 `check_fn` 仅在设置了 `HERMES_KANBAN_TASK` 时返回 True，而这仅在调度器生成此进程时发生。对于从不接触看板的用户，没有工具膨胀问题。

`kanban-worker` 和 `kanban-orchestrator` 技能会教导模型何时以及按什么顺序调用哪个工具。

### 工作进程技能

任何应该能够处理看板任务的配置文件都必须加载 `kanban-worker` 技能。它教导工作进程完整的生命周期：

1.  生成时，调用 `kanban_show()` 读取标题、正文、父任务交接、先前尝试和完整的评论线程。
2.  `cd $HERMES_KANBAN_WORKSPACE` 并在那里工作。
3.  在长时间操作期间，每隔几分钟调用一次 `kanban_heartbeat(note="...")`。
4.  使用 `kanban_complete(summary="...", metadata={...})` 完成任务，或者如果遇到阻塞，使用 `kanban_block(reason="...")`。

通过以下命令加载：

```bash
hermes skills install devops/kanban-worker
```

调度器在生成每个工作进程时也会自动传递 `--skills kanban-worker`，因此即使配置文件的默认技能配置不包含它，工作进程也始终可以使用该模式库。

### 为特定任务固定额外技能

有时单个任务需要指派人配置文件默认不携带的专家上下文——例如需要 `translation` 技能的翻译工作、需要 `github-code-review` 的审查任务、需要 `security-pr-audit` 的安全审计。与其每次都编辑指派人配置文件，不如直接将技能附加到任务上：

```bash
# CLI — 为每个额外技能重复 --skill 参数
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

# 多个技能
hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

在仪表板的行内创建表单中，将技能以逗号分隔输入到 **skills** 字段。从另一个 Agent（编排器模式）中，使用 `kanban_create(skills=[...])`：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)
```

这些技能是**附加**到内置的 `kanban-worker` 之上的——调度器为每个技能（以及内置技能）发出一个 `--skills <name>` 标志，因此工作进程生成时会加载所有这些技能。技能名称必须与指派人配置文件上实际安装的技能匹配（运行 `hermes skills list` 查看可用技能）；没有运行时安装。

### 编排器技能

一个**行为良好的编排器不会自己完成工作。** 它将用户的目标分解为任务，链接它们，将每个任务分配给专家，然后退居幕后。`kanban-orchestrator` 技能编码了这一点：反诱惑规则、一个标准的专家名册（`researcher`、`writer`、`analyst`、`backend-eng`、`reviewer`、`ops`）和一个分解手册。

将其加载到你的编排器配置文件中：

```bash
hermes skills install devops/kanban-orchestrator
```

为了获得最佳效果，将其与一个工具集仅限于看板操作（`kanban`、`gateway`、`memory`）的配置文件配对，这样编排器即使尝试也无法执行实现任务。

## 仪表板（GUI）

`/kanban` CLI 和斜杠命令足以无头运行看板，但可视化看板通常是人工介入的合适界面：分类、跨配置文件监督、阅读评论线程以及在列之间拖拽卡片。Hermes 将此作为**捆绑的仪表板插件**提供，位于 `plugins/kanban/` —— 不是核心功能，也不是独立服务 —— 遵循[扩展仪表板](./extending-the-dashboard)中概述的模式。
使用以下命令打开：

```bash
hermes kanban init      # 一次性操作：如果不存在则创建 kanban.db
hermes dashboard        # 导航栏中会出现 "Kanban" 标签页，位于 "Skills" 之后
```

### 插件提供的功能

- 一个 **Kanban** 标签页，按状态显示列：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（当切换开关打开时，还有 `archived`）。
  - `triage` 是存放粗略想法的暂存列，需要规格制定者来完善。使用 `hermes kanban create --triage`（或通过 Triage 列的内联创建）创建的任务会放在这里，调度器会忽略它们，直到人工或规格制定者将其提升到 `todo` / `ready`。
- 卡片显示任务 ID、标题、优先级徽章、租户标签、分配的用户档案、评论/链接数量、**进度胶囊**（当任务有依赖项时显示 `N/M` 个子项完成）以及“N 前创建”。每张卡片都有一个复选框，支持多选。
- **Running 列内按用户档案分组** — 工具栏复选框可切换 Running 列是否按分配者进行子分组。
- **通过 WebSocket 实时更新** — 插件以短轮询间隔跟踪仅追加的 `task_events` 表；当任何用户档案（CLI、消息网关或另一个仪表板标签页）进行操作时，看板会立即反映变化。重新加载会进行防抖处理，因此一连串事件只会触发一次重新获取。
- **拖放**卡片在列之间移动以更改状态。放置操作会发送 `PATCH /api/plugins/kanban/tasks/:id`，该请求会路由到与 CLI 使用的相同 `kanban_db` 代码 — 三个界面永远不会出现不一致。移动到破坏性状态（`done`、`archived`、`blocked`）时会提示确认。触摸设备使用基于指针的备用方案，因此看板在平板电脑上也可用。
- **内联创建** — 点击任何列标题上的 `+` 来输入标题、分配者、优先级，以及（可选）从包含所有现有任务的下拉菜单中选择父任务。从 Triage 列创建会自动将新任务置于 triage 状态。
- **多选与批量操作** — 按住 Shift/Ctrl 点击卡片或勾选其复选框以将其添加到选择中。顶部会出现一个批量操作栏，包含批量状态转换、归档和重新分配（通过用户档案下拉菜单或“(取消分配)”）。破坏性批量操作会先确认。每个 ID 的部分失败会被报告，而不会中止其余操作。
- **点击卡片**（不按 Shift/Ctrl）打开侧边抽屉（按 Escape 或点击外部关闭），其中包含：
  - **可编辑标题** — 点击标题进行重命名。
  - **可编辑分配者 / 优先级** — 点击元数据行进行修改。
  - **可编辑描述** — 默认以 Markdown 渲染（标题、粗体、斜体、行内代码、代码块、`http(s)` / `mailto:` 链接、项目符号列表），带有一个“编辑”按钮，点击后会切换为文本区域。Markdown 渲染器是一个小巧、XSS 安全的渲染器 — 每次替换都在 HTML 转义的输入上运行，只有 `http(s)` / `mailto:` 链接会通过，并且始终设置 `target="_blank"` + `rel="noopener noreferrer"`。
  - **依赖关系编辑器** — 父任务和子任务的标签列表，每个都有一个 `×` 来取消链接，以及包含所有其他任务的下拉菜单来添加新的父任务或子任务。循环依赖尝试会在服务器端被拒绝，并显示明确的消息。
  - **状态操作行**（→ triage / → ready / → running / block / unblock / complete / archive），破坏性转换会提示确认。
  - 结果部分（同样以 Markdown 渲染）、按 Enter 提交的评论线程、最近 20 个事件。
- **工具栏过滤器** — 自由文本搜索、租户下拉菜单（默认为 `config.yaml` 中的 `dashboard.kanban.default_tenant`）、分配者下拉菜单、“显示已归档”切换开关、“按用户档案分组”切换开关，以及一个**提醒调度器**按钮，这样你就不必等待下一个 60 秒的调度周期。

视觉上，目标是熟悉的 Linear / Fusion 布局：深色主题、带计数的列标题、彩色状态点、优先级和租户的胶囊标签。插件仅读取主题 CSS 变量（`--color-*`、`--radius`、`--font-mono`、...），因此它会根据当前激活的仪表板主题自动换肤。

### 架构

GUI 严格是一个**通过数据库读取 + 通过 kanban_db 写入**的层，没有自己的领域逻辑：

```
┌────────────────────────┐      WebSocket (跟踪 task_events)
│   React SPA (插件)     │ ◀──────────────────────────────────┐
│   HTML5 拖放           │                                    │
└──────────┬─────────────┘                                    │
           │ 通过 fetchJSON 的 REST                           │
           ▼                                                  │
┌────────────────────────┐     写入操作调用 kanban_db.*       │
│  FastAPI 路由器        │     直接调用 — 与 CLI /kanban      │
│  plugins/kanban/       │     动词使用的代码路径相同         │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── 追加 task_events ────────────┘
│  (WAL, 共享)           │
└────────────────────────┘
```

### REST 接口

所有路由都挂载在 `/api/plugins/kanban/` 下，并受仪表板的临时会话令牌保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=<name>&include_archived=…` | 按状态列分组的完整看板，以及用于过滤器下拉菜单的租户 + 分配者 |
| `GET` | `/tasks/:id` | 任务 + 评论 + 事件 + 链接 |
| `POST` | `/tasks` | 创建（包装 `kanban_db.create_task`，接受 `triage: bool` 和 `parents: [id, …]`） |
| `PATCH` | `/tasks/:id` | 状态 / 分配者 / 优先级 / 标题 / 正文 / 结果 |
| `POST` | `/tasks/bulk` | 对 `ids` 中的每个 ID 应用相同的补丁（状态 / 归档 / 分配者 / 优先级）。每个 ID 的失败会被报告，而不会中止其他操作 |
| `POST` | `/tasks/:id/comments` | 追加评论 |
| `POST` | `/links` | 添加依赖关系（`parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 移除依赖关系 |
| `POST` | `/dispatch?max=…&dry_run=…` | 提醒调度器 — 跳过 60 秒等待 |
| `GET` | `/config` | 从 `config.yaml` 读取 `dashboard.kanban` 首选项 — `default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` |
| `WS` | `/events?since=<event_id>` | `task_events` 行的实时流 |
每个处理器都是一个轻量封装——该插件约 700 行 Python 代码（路由 + WebSocket 尾部 + 批量批处理器 + 配置读取器），不添加任何新的业务逻辑。一个微小的 `_conn()` 辅助函数会在每次读写时自动初始化 `kanban.db`，因此全新安装后，无论用户是先打开仪表板、直接访问 REST API，还是运行 `hermes kanban init`，都能正常工作。

### 仪表板配置

在 `~/.hermes/config.yaml` 中，`dashboard.kanban` 下的任何这些键都会更改标签页的默认值——插件在加载时通过 `GET /config` 读取它们：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # 预选租户过滤器
    lane_by_profile: true             # "按配置文件划分泳道" 开关的默认值
    include_archived_by_default: false
    render_markdown: true             # 设置为 false 以进行纯 <pre> 渲染
```

每个键都是可选的，并回退到显示的默认值。

### 安全模型

仪表板的 HTTP 认证中间件[明确跳过 `/api/plugins/`](./extending-the-dashboard#backend-api-routes)——插件路由在设计上是未经认证的，因为仪表板默认绑定到 localhost。这意味着看板的 REST 接口可以从主机上的任何进程访问。

WebSocket 额外增加了一步：它要求将仪表板的临时会话令牌作为 `?token=…` 查询参数（浏览器无法在升级请求上设置 `Authorization`），这与浏览器内 PTY 桥接器使用的模式相匹配。

如果你运行 `hermes dashboard --host 0.0.0.0`，每个插件路由——包括看板——都将可以从网络访问。**不要在共享主机上这样做。** 看板包含任务正文、评论和工作区路径；攻击者访问这些路由将获得对整个协作表面的读取访问权限，并且还可以创建/重新分配/归档任务。

`~/.hermes/kanban.db` 中的任务特意设计为与配置文件无关（这是协调原语）。如果你使用 `hermes -p <profile> dashboard` 打开仪表板，看板仍然会显示主机上任何其他配置文件创建的任务。所有配置文件属于同一用户，但如果存在多个角色，这一点值得注意。

### 实时更新

`task_events` 是一个仅追加的 SQLite 表，具有单调递增的 `id`。WebSocket 端点保存每个客户端最后看到的事件 id，并在新行到达时推送。当一批事件到达时，前端重新加载（非常廉价的）看板端点——这比尝试根据每种事件类型修补本地状态更简单、更正确。WAL 模式意味着读取循环永远不会阻塞调度器的 `BEGIN IMMEDIATE` 声明事务。

### 扩展它

该插件使用标准的 Hermes 仪表板插件契约——完整的清单参考、shell 插槽、页面作用域插槽和 Plugin SDK，请参阅[扩展仪表板](./extending-the-dashboard)。额外的列、自定义卡片样式、租户过滤的布局或完整的 `tab.override` 替换，都可以在不分叉此插件的情况下实现。

要禁用而不删除：在 `config.yaml` 中添加 `dashboard.plugins.kanban.enabled: false`（或删除 `plugins/kanban/dashboard/manifest.json`）。

### 范围边界

GUI 特意设计得很轻量。插件所做的一切都可以通过 CLI 访问；插件只是让人类操作更舒适。自动分配、预算、治理门禁和组织结构图视图仍属于用户空间——一个路由器配置文件、另一个插件或重用 `tools/approval.py`——正如设计规范中"范围外"部分所列出的那样。

## CLI 命令参考

```
hermes kanban init                                     # 创建 kanban.db + 打印守护进程提示
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|dir:<path>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived] [--json]
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

hermes kanban tail <id>                                # 跟踪单个任务的事件流
hermes kanban watch [--assignee P] [--tenant T]        # 将 ALL 事件实时流式传输到终端
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # 长时间操作的 worker 活跃度信号
hermes kanban runs <id> [--json]                       # 尝试历史记录（每次运行一行）
hermes kanban assignees [--json]                       # 磁盘上的配置文件 + 每个分配者的任务计数
hermes kanban dispatch [--dry-run] [--max N]           # 单次传递
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # 已弃用 —— 独立调度器（改用 `hermes gateway start`）
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # 按状态 + 按分配者计数
hermes kanban log <id> [--tail BYTES]                  # 来自 ~/.hermes/kanban/logs/ 的 worker 日志
hermes kanban notify-subscribe <id>                    # 消息网关桥接钩子（由网关中的 /kanban 使用）
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # worker 看到的内容
hermes kanban gc [--event-retention-days N]            # 工作区 + 旧事件 + 旧日志
        [--log-retention-days N]
```
所有命令也可作为消息网关中的斜杠命令使用（`/kanban list`、`/kanban comment t_abc "need docs"` 等）。斜杠命令会绕过运行中 Agent 的防护，因此你可以在主 Agent 仍在聊天时，使用 `/kanban unblock` 来解除被卡住的工作者。

## 协作模式

看板支持以下八种模式，无需引入新的原语：

| 模式 | 形态 | 示例 |
|---|---|---|
| **P1 扇出** | N 个同级，相同角色 | "并行研究 5 个角度" |
| **P2 流水线** | 角色链：侦察员 → 编辑 → 写手 | 每日简报汇编 |
| **P3 投票 / 法定人数** | N 个同级 + 1 个聚合器 | 3 个研究员 → 1 个审阅者挑选 |
| **P4 长期运行日志** | 相同配置 + 共享目录 + 定时任务 | Obsidian 知识库 |
| **P5 人在回路** | 工作者阻塞 → 用户评论 → 解除阻塞 | 模糊决策 |
| **P6 `@提及`** | 从文本内容中内联路由 | `@reviewer 看看这个` |
| **P7 线程作用域的工作空间** | 在某个线程中使用 `/kanban here` | 每个项目的消息网关线程 |
| **P8 舰队耕作** | 一个配置，N 个主体 | 50 个社交账户 |
| **P9 分类指定器** | 粗略想法 → `triage` → 指定器扩展正文 → `todo` | "将这个一句话想法转化为一个规范任务" |

每种模式的具体示例，请参阅 `docs/hermes-kanban-v1-spec.pdf`。

## 多租户使用

当一个专家舰队服务于多个业务时，为每个任务标记租户：

```bash
hermes kanban create "monthly report" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

工作者会接收到 `$HERMES_TENANT` 环境变量，并通过前缀对其记忆写入进行命名空间隔离。看板、调度器和配置定义都是共享的；只有数据是作用域隔离的。

## 消息网关通知

当你在消息网关（Telegram、Discord、Slack 等）中运行 `/kanban create …` 时，发起聊天的会话会自动订阅新任务。消息网关的后台通知器每隔几秒轮询 `task_events` 表，并将每个终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）的一条消息发送到该聊天会话。已完成的任务还会发送工作者 `--result` 的第一行，这样你无需执行 `/kanban show` 就能看到结果。

你可以从 CLI 显式管理订阅——当脚本/定时任务想要通知一个并非由其发起的聊天会话时，这很有用：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务达到 `done` 或 `archived` 状态，订阅会自动移除；无需手动清理。

## 运行记录 —— 每次尝试对应一行

任务是工作的逻辑单元；**运行记录** 是对其执行的一次尝试。当调度器认领一个就绪任务时，它会在 `task_runs` 表中创建一行，并将 `tasks.current_run_id` 指向它。当该次尝试结束时——无论是完成、阻塞、崩溃、超时、启动失败还是被回收——运行记录行都会以一个 `outcome` 关闭，并且任务的指针会被清空。一个尝试了三次的任务会有三行 `task_runs` 记录。

为什么需要两个表而不是直接修改任务：你需要 **完整的尝试历史** 来进行实际的事后分析（"第二次审阅尝试批准了，第三次合并了"），并且你需要一个干净的地方来挂载每次尝试的元数据——哪些文件被更改、哪些测试运行了、审阅者记录了哪些发现。这些是运行事实，而不是任务事实。

运行记录也是 **结构化交接** 的存放位置。当工作者完成任务时，可以传递：

- `--result "<简短日志行>"` —— 像以前一样放在任务行上（为了向后兼容）。
- `--summary "<人工交接摘要>"` —— 放在运行记录上；下游子任务在其 `build_worker_context` 中可以看到它。
- `--metadata '{"changed_files": [...], "tests_run": 12}'` —— 运行记录上的 JSON 字典；子任务可以看到序列化后的摘要和元数据。

下游子任务读取每个父任务最近一次已完成的运行记录的摘要和元数据。重试的工作者读取其自身任务的先前尝试（结果、摘要、错误），这样它们就不会重复已经失败的路径。

```bash
# 工作者完成并附带结构化交接：
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

运行记录在仪表板（抽屉中的"运行历史"部分，每次尝试对应一个彩色行）和 REST API（`GET /api/plugins/kanban/tasks/:id` 返回一个 `runs[]` 数组）中公开。`PATCH /api/plugins/kanban/tasks/:id` 附带 `{status: "done", summary, metadata}` 会将两者转发给内核，因此仪表板上的"标记完成"按钮在功能上等同于 CLI。`task_events` 行携带它们所属的 `run_id`，以便 UI 可以按尝试对它们进行分组，并且 `completed` 事件在其有效载荷中嵌入了第一行摘要（上限为 400 个字符），这样消息网关通知器无需进行第二次 SQL 往返就能渲染结构化交接。

**批量关闭注意事项。** `hermes kanban complete a b c --summary X` 会被拒绝——结构化交接是针对每次运行的，因此将相同的摘要复制粘贴到 N 个任务几乎总是错误的。对于常见的"我完成了一堆管理任务"的情况，**不带** `--summary` / `--metadata` 的批量关闭仍然有效。

**状态变更导致的回收运行。** 如果你在仪表板中将一个正在运行的任务从 `running` 状态拖走（回到 `ready`，或直接到 `todo`），或者归档一个仍在运行的任务，正在进行的运行将以 `outcome='reclaimed'` 关闭，而不是变成孤儿。当 `tasks.current_run_id` 为 `NULL` 时，`task_runs` 行始终处于终端状态，反之亦然——这个不变量在 CLI、仪表板、调度器和通知器中都成立。
**从未被认领任务的合成运行记录。** 完成或阻塞一个从未被认领的任务（例如，用户从仪表板关闭一个状态为 `ready` 的任务并提供了总结，或者 CLI 用户运行 `hermes kanban complete <ready-task> --summary X`）原本会导致交接信息丢失。为了避免这种情况，内核会插入一个持续时间为零的运行记录行（`started_at == ended_at`），其中包含总结/元数据/原因，从而保持尝试历史的完整性。`completed` / `blocked` 事件的 `run_id` 指向该行。

**实时抽屉刷新。** 当仪表板的 WebSocket 事件流报告用户当前正在查看的任务有新事件时，抽屉会自行重新加载（通过一个针对每个任务的事件计数器，该计数器被编织到其 `useEffect` 的依赖项列表中）。不再需要关闭并重新打开抽屉来查看运行的新记录行或更新的结果。

### 向前兼容性

`tasks` 表上的两个可为空的列是为 v2 工作流路由预留的：`workflow_template_id`（此任务属于哪个模板）和 `current_step_key`（该模板中哪个步骤处于活动状态）。v1 内核在路由时会忽略它们，但允许客户端写入它们，因此 v2 版本可以添加路由机制而无需再次进行模式迁移。

## 事件参考

每次状态转换都会向 `task_events` 表追加一行。每一行都带有一个可选的 `run_id`，以便 UI 可以按尝试对事件进行分组。事件种类分为三个集群，便于过滤（例如 `hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期**（任务作为一个逻辑单元发生了什么变化）：

| 种类 | 负载 | 何时发生 |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | 任务被插入。`run_id` 为 `NULL`。 |
| `promoted` | — | `todo → ready`，因为所有父任务都达到了 `done` 状态。`run_id` 为 `NULL`。 |
| `claimed` | `{lock, expires, run_id}` | 调度器原子性地认领了一个 `ready` 任务以进行派生。 |
| `completed` | `{result_len, summary?}` | Worker 写入了 `--result` / `--summary` 并且任务达到了 `done` 状态。`summary` 是第一行的交接信息（上限 400 字符）；完整版本位于运行记录行上。如果在从未被认领的任务上调用 `complete_task` 并提供了交接字段，则会合成一个持续时间为零的运行记录，以便 `run_id` 仍然指向某个记录。 |
| `blocked` | `{reason}` | Worker 或用户将任务翻转为 `blocked` 状态。如果在从未被认领的任务上调用并提供了 `--reason`，则会合成一个持续时间为零的运行记录。 |
| `unblocked` | — | `blocked → ready`，手动或通过 `/unblock` 命令。`run_id` 为 `NULL`。 |
| `archived` | — | 从默认看板中隐藏。如果任务仍在运行，则附带因副作用而被回收的运行记录的 `run_id`。 |

**编辑**（由人工驱动的、非状态转换的更改）：

| 种类 | 负载 | 何时发生 |
|---|---|---|
| `assigned` | `{assignee}` | 负责人变更（包括取消分配）。 |
| `edited` | `{fields}` | 标题或正文更新。 |
| `reprioritized` | `{priority}` | 优先级变更。 |
| `status` | `{status}` | 仪表板拖放直接写入状态（例如 `todo → ready`）。当从 `running` 状态拖走时，附带被回收的运行记录的 `run_id`；否则 `run_id` 为 NULL。 |

**Worker 遥测**（关于执行过程，而非逻辑任务）：

| 种类 | 负载 | 何时发生 |
|---|---|---|
| `spawned` | `{pid}` | 调度器成功启动了一个 worker 进程。 |
| `heartbeat` | `{note?}` | Worker 调用 `hermes kanban heartbeat $TASK` 以在长时间操作期间发出存活信号。 |
| `reclaimed` | `{stale_lock}` | 认领 TTL 过期但未完成；任务返回 `ready` 状态。 |
| `crashed` | `{pid, claimer}` | Worker PID 不再存活，但 TTL 尚未过期。 |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | 超出 `max_runtime_seconds`；调度器发送 SIGTERM（然后在 5 秒宽限期后发送 SIGKILL）并重新排队。 |
| `spawn_failed` | `{error, failures}` | 一次派生尝试失败（缺少 PATH、工作空间无法挂载等）。计数器递增；任务返回 `ready` 状态以重试。 |
| `gave_up` | `{failures, error}` | 在连续 N 次 `spawn_failed` 后，断路器触发。任务自动阻塞并附带最后一个错误。默认 N = 5；可通过 `--failure-limit` 覆盖。 |

`hermes kanban tail <id>` 显示单个任务的这些事件。`hermes kanban watch` 在整个看板范围内流式传输这些事件。

## 范围之外

看板设计上是单主机的。`~/.hermes/kanban.db` 是一个本地 SQLite 文件，调度器在同一台机器上派生 worker。不支持在两个主机之间运行共享看板——没有用于协调“主机 A 上的 worker X，主机 B 上的 worker Y”的协调原语，并且崩溃检测路径假设 PID 是主机本地的。如果需要多主机支持，请在每个主机上运行一个独立的看板，并使用 `delegate_task` / 消息队列来桥接它们。

## 设计规范

完整的设计——架构、并发正确性、与其他系统的比较、实施计划、风险、开放性问题——位于 `docs/hermes-kanban-v1-spec.pdf` 中。在提交任何行为变更的 PR 之前，请先阅读该文档。