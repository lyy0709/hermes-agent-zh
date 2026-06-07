# Kanban 教程

通过浏览器中打开的仪表盘，逐步演示 Hermes Kanban 系统设计的四种使用场景。如果你还没有阅读 [Kanban 概览](./kanban)，请先阅读那里——本教程假设你了解任务、运行、负责人和调度器的概念。

## 设置

```bash
hermes kanban init           # 可选；首次运行 `hermes kanban <任何命令>` 会自动初始化
hermes dashboard             # 在浏览器中打开 http://127.0.0.1:9119
# 点击左侧导航栏中的 Kanban
```

仪表盘是**你**观察系统最舒适的地方。调度器生成的 Agent 工作者永远不会看到仪表盘或 CLI——它们通过专用的 `kanban_*` [工具集](./kanban#how-workers-interact-with-the-board)（`kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock`）来驱动看板。所有三个界面——仪表盘、CLI、工作者工具——都通过同一个每看板的 SQLite 数据库路由（默认看板为 `~/.hermes/kanban.db`，之后创建的任何看板为 `~/.hermes/kanban/boards/<slug>/kanban.db`），因此无论变更来自哪一方，每个看板都是一致的。

本教程全程使用 `default` 看板。如果你想要多个隔离的队列（每个项目/仓库/领域一个），请参阅概览中的 [看板（多项目）](./kanban#boards-multi-project)——相同的 CLI / 仪表盘 / 工作者流程适用于每个看板，并且工作者在物理上无法看到其他看板上的任务。

在整个教程中，**标记为 `bash` 的代码块是*你*运行的命令。** 标记为 `# worker tool calls` 的代码块是生成的工作者模型发出的工具调用——在这里展示是为了让你可以看到端到端的循环，而不是因为你会自己运行它们。

## 看板概览

![Kanban 看板概览](/img/kanban-tutorial/01-board-overview.png)

六个列，从左到右：

- **Triage** —— 原始想法。默认情况下，调度器会自动在此处的任务上运行**分解器**：内置分解器使用 `auxiliary.kanban_decomposer`，读取你的配置文件花名册 + 描述，并生成一个子任务图，路由到最合适的专家。原始任务作为父任务保持活动状态，以便其负责人（`kanban.orchestrator_profile`，或未设置时的活动默认配置文件）在所有任务完成时唤醒以判断完成情况。点击看板页面顶部的 **Orchestration: Auto/Manual** 药丸切换模式。在手动模式下，点击卡片上的 **⚗ Decompose**，或运行 `hermes kanban decompose <id>` / `/kanban decompose <id>`。对于不需要展开的单个任务，**✨ Specify** 会执行一次性的规范重写（目标、方法、验收标准）并提升到 `todo`。在 `config.yaml` 中的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 下配置模型。请参阅主 Kanban 指南中的 [自动与手动编排](./kanban#auto-vs-manual-orchestration)。
- **Todo** —— 已创建但等待依赖项，或尚未分配。
- **Ready** —— 已分配并等待调度器认领。
- **In progress** —— 一个工作者正在积极运行该任务。当“按配置文件分道”开启时（默认），此列按负责人进行子分组，以便你可以一目了然地看到每个工作者在做什么。
- **Blocked** —— 工作者请求人工输入，或断路器跳闸。
- **Done** —— 已完成。

顶部栏有用于搜索、租户和负责人的过滤器，以及一个 `Lanes by profile` 切换按钮和一个 `Nudge dispatcher` 按钮，该按钮立即运行一个调度周期，而不是等待守护进程的下一个间隔。点击任何卡片会在右侧打开其抽屉。

### 平铺视图

如果配置文件道很杂乱，请关闭“按配置文件分道”，进行中列将折叠为按认领时间排序的单个平铺列表：

![关闭按配置文件分道的看板](/img/kanban-tutorial/02-board-flat.png)

## 场景 1 —— 独立开发者交付功能

你正在构建一个功能。经典流程：设计模式、实现 API、编写测试。三个具有父→子依赖关系的任务。

```bash
SCHEMA=$(hermes kanban create "设计认证模式" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --body "为认证模块设计用户/会话/令牌模式。" \
    --json | jq -r .id)

API=$(hermes kanban create "实现认证 API 端点" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --parent $SCHEMA \
    --body "POST /register, POST /login, POST /refresh, POST /logout。" \
    --json | jq -r .id)

hermes kanban create "编写认证集成测试" \
    --assignee qa-dev --tenant auth-project --priority 2 \
    --parent $API \
    --body "覆盖成功路径、错误密码、过期令牌、并发刷新。"
```

因为 `API` 将 `SCHEMA` 作为其父任务，而 `tests` 将 `API` 作为其父任务，所以只有 `SCHEMA` 从 `ready` 开始。其他两个任务停留在 `todo` 中，直到它们的父任务完成。这是依赖提升引擎在发挥作用——在有待测试的 API 之前，没有其他工作者会接手编写测试。

在下一个调度器周期（默认为 60 秒，或者如果你点击 **Nudge dispatcher** 则立即执行）中，`backend-dev` 配置文件将作为工作者生成，其环境中包含 `HERMES_KANBAN_TASK=$SCHEMA`。以下是工作者工具调用循环在 Agent 内部的样子：

```python
# 工作者工具调用 —— 不是你运行的命令
kanban_show()
# → 返回标题、正文、worker_context、父任务、先前尝试、评论

# （工作者读取 worker_context，使用终端/文件工具来设计模式，
#  编写迁移，运行自己的检查，提交 —— 实际工作发生在这里）

kanban_heartbeat(note="模式已起草，正在编写迁移")

kanban_complete(
    summary="users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); "
            "刷新令牌存储为 type='refresh' 的会话",
    metadata={
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["bcrypt 用于哈希", "JWT 用于会话令牌",
                      "7天刷新，15分钟访问"],
    },
)
```
`kanban_show` 默认将 `task_id` 设为 `$HERMES_KANBAN_TASK`，因此 worker 无需知道自己的 ID。`kanban_complete` 将摘要和元数据写入当前的 `task_runs` 行，关闭该次运行，并将任务状态转为 `done` —— 所有这些操作都通过 `kanban_db` 在一次原子性操作中完成。

当 `SCHEMA` 任务进入 `done` 状态时，依赖引擎会自动将 `API` 任务提升为 `ready` 状态。API worker 在接手任务时，会调用 `kanban_show()`，并看到附加在父级交接信息上的 `SCHEMA` 任务的摘要和元数据 —— 这样它无需重新阅读冗长的设计文档就能了解架构决策。

点击看板上的已完成的架构任务，抽屉会显示所有信息：

![Solo dev — completed schema task drawer](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的“运行历史”部分是关键新增内容。一次尝试：结果 `completed`，worker `@backend-dev`，持续时间，时间戳，以及完整的交接摘要。元数据块（`changed_files`、`decisions`）也存储在运行记录中，并会展示给任何读取此父级任务的后续 worker。

你可以随时从终端检查相同的数据 —— 这些命令是**你**在看板上的查看操作，而不是 worker 的操作：

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  OUTCOME       PROFILE       ELAPSED  STARTED
# 1  completed     backend-dev        0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 场景 2 — 团队并行处理

你有三个 worker（翻译员、转录员、文案）和一堆独立的任务。你希望三者并行处理并展示可见的进度。这是最简单的看板用例，也是原始设计优化的场景。

创建工作：

```bash
for lang in Spanish French German; do
    hermes kanban create "Translate homepage to $lang" \
        --assignee translator --tenant content-ops
done
for i in 1 2 3 4 5; do
    hermes kanban create "Transcribe Q3 customer call #$i" \
        --assignee transcriber --tenant content-ops
done
for sku in 1001 1002 1003 1004; do
    hermes kanban create "Generate product description: SKU-$sku" \
        --assignee copywriter --tenant content-ops
done
```

启动消息网关然后离开 —— 它托管着嵌入式调度器，该调度器会在同一个 kanban.db 上处理所有三个专业配置的任务：

```bash
hermes gateway start
```

现在将看板过滤到 `content-ops`（或直接搜索“Transcribe”），你会看到：

![Fleet view filtered to transcribe tasks](/img/kanban-tutorial/07-fleet-transcribes.png)

两个转录任务已完成，一个正在运行，两个处于就绪状态等待下一次调度器轮询。“进行中”列按配置分组（默认的“按配置划分泳道”），因此你可以看到每个 worker 的活跃任务，而无需扫描混合列表。当前任务一完成，调度器就会将下一个就绪任务提升为运行状态。三个守护进程并行处理三个受指派人池，整个内容队列无需进一步人工干预即可清空。

**场景 1 中提到的关于结构化交接的一切在这里仍然适用。** 翻译员 worker 完成任务后发出 `kanban_complete(summary="translated 4 pages, style matched existing marketing voice", metadata={"duration_seconds": 720, "tokens_used": 2100})` —— 这对于分析和任何依赖于此任务的下游任务都很有用。

## 场景 3 — 带重试的角色流水线

这正是看板相对于扁平 TODO 列表的价值所在。产品经理编写规范。工程师实现它。评审员拒绝了第一次尝试。工程师修改后再次尝试。评审员批准。

按 `auth-project` 过滤的仪表板视图：

![Pipeline view for a multi-role feature](/img/kanban-tutorial/08-pipeline-auth.png)

三阶段链一目了然：`Spec: password reset flow`（已完成，pm），`Implement password reset flow`（已完成，backend-dev），`Review password reset PR`（就绪，reviewer）。每个任务的底部都有其父级任务（绿色显示），子级任务作为依赖项。

有趣的是实现任务，因为它曾被阻塞并重试。以下是完整的三 Agent 编排，显示为每个 worker 的模型进行的工具调用：

```python
# --- PM worker 在 $SPEC 上启动并编写验收标准 ---
# worker 工具调用
kanban_show()
kanban_complete(
    summary="spec approved; POST /forgot-password sends email, "
            "GET /reset/:token renders form, POST /reset applies new password",
    metadata={"acceptance": [
        "expired token returns 410",
        "reused last-3 password returns 400 with message",
        "successful reset invalidates all active sessions",
    ]},
)
# → $SPEC 完成；$IMPL 自动从 todo 提升为 ready

# --- Engineer worker 在 $IMPL 上启动（第一次尝试）---
# worker 工具调用
kanban_show()   # 在 worker_context 中读取 $SPEC 的摘要和验收元数据
# （工程师编写代码，运行测试，提交 PR）
# 评审员反馈到达 —— 工程师认为问题确实存在并阻塞任务
kanban_block(
    reason="Review: password strength check missing, reset link isn't "
           "single-use (can be replayed within 30min)",
)
# → $IMPL 转为 blocked 状态；运行 1 关闭，结果 outcome='blocked'
```

现在你（人类，或单独的评审员配置）阅读阻塞原因，确定修复方向明确，然后从仪表板的“Unblock”按钮解除阻塞 —— 或者通过 CLI / 斜杠命令：

```bash
hermes kanban unblock $IMPL
# 或从聊天中：/kanban unblock $IMPL
```

调度器将 `$IMPL` 提升回 `ready` 状态，并在下一次轮询时，重新启动 `backend-dev` worker。这第二次启动是同一任务上的**一次新运行**：

```python
# --- Engineer worker 在 $IMPL 上启动（第二次尝试）---
# worker 工具调用
kanban_show()
# → worker_context 现在包含了运行 1 的阻塞原因，因此这个 worker 知道
#   需要修复哪两件事，而不是重新阅读整个规范
# （工程师添加 zxcvbn 强度检查，使重置令牌变为一次性使用，重新运行测试）
kanban_complete(
    summary="added zxcvbn strength check, reset tokens are now single-use "
            "(stored + deleted on success)",
    metadata={
        "changed_files": [
            "auth/reset.py",
            "auth/tests/test_reset.py",
            "migrations/003_single_use_reset_tokens.sql",
        ],
        "tests_run": 11,
        "review_iteration": 2,
    },
)
```
点击实现任务。抽屉显示**两次尝试**：

![包含两次运行（先阻塞后完成）的实现任务](/img/kanban-tutorial/04b-drawer-retry-history-scrolled.png)

- **运行 1** — 被 `@backend-dev` `blocked`。审查反馈就在结果下方："缺少密码强度检查，重置链接不是单次使用（可在30分钟内重放）"。
- **运行 2** — 由 `@backend-dev` `completed`。新的摘要，新的元数据。

每次运行都是 `task_runs` 表中的一行，包含自己的结果、摘要和元数据。重试历史不是一个事后添加在"最新状态"任务之上的概念层——它是主要的表示形式。当重试的工作器打开任务时，`build_worker_context` 会向其展示之前的尝试，因此第二次尝试的工作器能看到第一次尝试被阻塞的原因，并解决这些具体问题，而不是从头开始重新运行。

接下来由审查者接手。当他们打开 `Review password reset PR` 时，会看到：

![审查者在抽屉中查看流水线](/img/kanban-tutorial/09-drawer-pipeline-review.png)

父链接指向已完成的实现。当审查者的工作器在 `Review password reset PR` 上启动并调用 `kanban_show()` 时，返回的 `worker_context` 包含父任务最近一次已完成运行的摘要和元数据——因此审查者在查看差异之前，就能读到"添加了 zxcvbn 强度检查，重置令牌现在是单次使用"，并已掌握变更文件列表。

## 故事 4 — 熔断器和崩溃恢复

真实的工作器会失败。缺少凭据、OOM 终止、瞬时网络错误。调度器有两道防线：一个**熔断器**，在连续 N 次失败后自动阻塞任务，以免看板永远无意义地重试；以及**崩溃检测**，用于回收那些工作器 PID 在 TTL 到期前就已消失的任务。

### 熔断器 — 看似永久性的故障

一个部署任务，因为配置文件的执行环境中未设置 `AWS_ACCESS_KEY_ID` 而无法启动其工作器：

```bash
hermes kanban create "Deploy to staging (missing creds)" \
    --assignee deploy-bot --tenant ops \
    --max-retries 3
```

调度器尝试启动工作器。启动失败（`RuntimeError: AWS_ACCESS_KEY_ID not set`）。调度器释放认领权，增加失败计数器，并在下一个时间片再次尝试。因为此示例设置了 `--max-retries 3`，所以在连续三次失败后熔断器触发：任务进入 `blocked` 状态，结果为 `gave_up`。如果省略该标志，Hermes 使用 `kanban.failure_limit`（默认值：2）。在人工解除阻塞之前，不再重试。

点击被阻塞的任务：

![熔断器 — 2 次 spawn_failed + 1 次 gave_up](/img/kanban-tutorial/11-drawer-gave-up.png)

三次运行，`error` 字段都是相同的错误。前两次是 `spawn_failed`（可重试），第三次是 `gave_up`（终止）。上方的事件日志显示了完整序列：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

在终端上：

```bash
hermes kanban runs t_ef5d
# #   OUTCOME        PROFILE        ELAPSED  STARTED
# 1   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
# 2   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
# 3   gave_up        deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
```

如果配置了 Telegram / Discord / Slack，消息网关会在 `gave_up` 事件时发送通知，这样你无需检查看板就能得知故障。

### 崩溃恢复 — 工作器中途死亡

有时启动成功，但工作器进程后来死亡——段错误、OOM、`systemctl stop`。调度器轮询 `kill(pid, 0)` 并检测到死亡的 pid；认领权被释放，任务返回 `ready` 状态，下一个时间片将其分配给一个新的工作器。

种子数据中的示例是一个内存耗尽的迁移：

```bash
# 工作器认领任务，开始扫描 240 万行，在约 230 万行时被 OOM 终止
# 调度器检测到死亡 pid，释放认领权，增加尝试计数器
# 使用分块策略重试成功
```

抽屉显示了完整的两段尝试历史：

![崩溃与恢复 — 1 次 crashed + 1 次 completed](/img/kanban-tutorial/06-drawer-crash-recovery.png)

运行 1 — `crashed`，错误为 `OOM kill at row 2.3M (process 99999 gone)`。运行 2 — `completed`，其元数据中包含 `"strategy": "chunked with LIMIT + WHERE id > last_id"`。重试的工作器在其上下文中看到了运行 1 的崩溃，并选择了更安全的策略；元数据使得未来的观察者（或事后分析撰写者）能清楚地了解发生了什么变化。

## 结构化交接 — 为什么 `summary` 和 `metadata` 很重要

在上述每个故事中，工作器在最后都调用了 `kanban_complete(summary=..., metadata=...)`。这不是装饰——这是工作流各阶段之间的主要交接渠道。

当任务 B 上的工作器启动并调用 `kanban_show()` 时，它返回的 `worker_context` 包含：

- B 的**先前尝试**（之前的运行：结果、摘要、错误、元数据），这样重试的工作器就不会重复失败的老路。
- **父任务结果** — 对于每个父任务，最近一次已完成运行的摘要和元数据 — 这样下游工作器就能看到上游工作完成的原因和方式。

这取代了困扰扁平看板系统的"在评论和工作输出中翻找"的繁琐操作。产品经理在规范的元数据中编写验收标准，工程师的工作器在父任务交接中就能结构性地看到它们。工程师记录了他们运行了哪些测试以及通过了多少，审查者的工作器在打开差异文件之前就已经掌握了这个列表。

之所以存在批量关闭保护，是因为这些数据是按运行存储的。`hermes kanban complete a b c --summary X`（你从 CLI 执行）会被拒绝——将相同的摘要复制粘贴到三个任务几乎总是错误的。不带交接标志的批量关闭仍然适用于常见的"我完成了一堆管理任务"的情况。工具界面根本不暴露批量变体；出于同样的原因，`kanban_complete` 也始终是单任务操作。
## 查看正在运行的任务

为了完整性——这里展示一个仍在进行中的任务抽屉（来自故事1的API实现，已被 `backend-dev` 认领但尚未完成）：

![已认领、进行中的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

状态为 `Running`。活跃的运行会出现在运行历史部分，其结果为 `active` 且没有 `ended_at`。如果此工作进程死亡或超时，调度器将以适当的结果关闭此运行，并在下一次认领时开启一个新的运行——尝试记录行永远不会消失。

## 后续步骤

- [看板概览](./kanban) —— 完整的数据模型、事件词汇表和 CLI 参考。
- `hermes kanban --help` —— 每个子命令，每个标志。
- `hermes kanban watch --kinds completed,gave_up,timed_out` —— 在整个看板上实时流式传输终端事件。
- `hermes kanban notify-subscribe <task> --platform telegram --chat-id <id>` —— 当特定任务完成时，通过消息网关接收通知。