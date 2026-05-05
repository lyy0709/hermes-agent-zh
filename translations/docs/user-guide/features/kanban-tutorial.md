# Kanban 教程

通过浏览器中打开的仪表盘，逐步演示 Hermes Kanban 系统设计的四种使用场景。如果你还没阅读过 [Kanban 概览](./kanban)，请先阅读那里——本教程假设你了解任务、运行、负责人和调度器的概念。

## 设置

```bash
hermes kanban init           # 可选；首次运行 `hermes kanban <任何命令>` 会自动初始化
hermes dashboard             # 在浏览器中打开 http://127.0.0.1:9119
# 点击左侧导航栏中的 Kanban
```

仪表盘是**你**观察系统最舒适的地方。调度器生成的 Agent 工作者永远不会看到仪表盘或 CLI——它们通过专用的 `kanban_*` [工具集](./kanban#how-workers-interact-with-the-board)（`kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`）来驱动看板。所有三个界面——仪表盘、CLI、工作者工具——都通过同一个每看板的 SQLite 数据库路由（默认看板为 `~/.hermes/kanban.db`，后续创建的任何看板为 `~/.hermes/kanban/boards/<slug>/kanban.db`），因此无论变更来自哪一方，每个看板都是一致的。

本教程全程使用 `default` 看板。如果你想要多个隔离的队列（每个项目/仓库/领域一个），请参阅概览中的 [看板（多项目）](./kanban#boards-multi-project)——相同的 CLI/仪表盘/工作者流程适用于每个看板，并且工作者在物理上无法看到其他看板上的任务。

在整个教程中，**标记为 `bash` 的代码块是*你*运行的命令。** 标记为 `# worker tool calls` 的代码块是生成的工作者模型发出的工具调用——这里展示出来是为了让你能看到端到端的循环，而不是因为你需要自己运行它们。

## 看板概览

![Kanban 看板概览](/img/kanban-tutorial/01-board-overview.png)

六个列，从左到右：

- **Triage** —— 原始想法，在任何人开始工作之前，指定者会完善规范。
- **Todo** —— 已创建但等待依赖项，或尚未分配。
- **Ready** —— 已分配并等待调度器认领。
- **In progress** —— 工作者正在积极运行任务。当“按配置文件分道”开启时（默认），此列按负责人分组，以便一目了然地看到每个工作者在做什么。
- **Blocked** —— 工作者请求人工输入，或断路器跳闸。
- **Done** —— 已完成。

顶部栏有搜索、租户和负责人的过滤器，以及一个 `Lanes by profile` 切换按钮和一个 `Nudge dispatcher` 按钮，该按钮立即运行一次调度周期，而不是等待守护进程的下一个间隔。点击任何卡片会在右侧打开其抽屉。

### 平铺视图

如果配置文件分道显得杂乱，可以关闭“按配置文件分道”，进行中列将折叠为按认领时间排序的单个平铺列表：

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
    --body "覆盖正常路径、错误密码、过期令牌、并发刷新。"
```

因为 `API` 将 `SCHEMA` 作为其父任务，而 `tests` 将 `API` 作为其父任务，所以只有 `SCHEMA` 从 `ready` 状态开始。其他两个任务停留在 `todo` 状态，直到它们的父任务完成。这是依赖关系提升引擎在发挥作用——在有待测试的 API 之前，不会有其他工作者接手编写测试。

在下一个调度器周期（默认为 60 秒，或者如果你点击 **Nudge dispatcher** 则立即执行）中，`backend-dev` 配置文件将作为工作者生成，其环境变量中包含 `HERMES_KANBAN_TASK=$SCHEMA`。以下是工作者从 Agent 内部看到的工具调用循环：

```python
# worker tool calls —— 不是你运行的命令
kanban_show()
# → 返回标题、正文、worker_context、父任务、先前尝试、评论

# （工作者读取 worker_context，使用终端/文件工具设计模式，
#  编写迁移，运行自己的检查，提交——实际工作发生在这里）

kanban_heartbeat(note="模式草稿完成，正在编写迁移")

kanban_complete(
    summary="users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); "
            "刷新令牌存储为 type='refresh' 的会话",
    metadata={
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["bcrypt 用于哈希", "JWT 用于会话令牌",
                      "7 天刷新，15 分钟访问"],
    },
)
```

`kanban_show` 默认将 `task_id` 设为 `$HERMES_KANBAN_TASK`，因此工作者无需知道自己的 ID。`kanban_complete` 将摘要 + 元数据写入当前的 `task_runs` 行，关闭该运行，并将任务转换为 `done` 状态——所有这些都在一次原子操作中通过 `kanban_db` 完成。

当 `SCHEMA` 达到 `done` 状态时，依赖关系引擎会自动将 `API` 提升到 `ready` 状态。当 API 工作者接手时，它将调用 `kanban_show()` 并看到 `SCHEMA` 的摘要和元数据附加在父任务交接中——因此它无需重新阅读冗长的设计文档就能了解模式决策。

点击看板上已完成的模式任务，抽屉会显示所有内容：

![独立开发者 —— 已完成的模式任务抽屉](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的运行历史部分是关键补充。一次尝试：结果 `completed`，工作者 `@backend-dev`，持续时间，时间戳，以及完整的交接摘要。元数据块（`changed_files`、`decisions`）也存储在运行中，并呈现给任何读取此父任务的下游工作者。
你可以随时从终端查看相同的数据——这些命令是**你**在看板上的窥视，而不是工作进程：

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  OUTCOME       PROFILE       ELAPSED  STARTED
# 1  completed     backend-dev        0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 故事 2 — 舰队式作业

你有三个工作进程（一个翻译员、一个转录员、一个文案）和一堆独立的任务。你希望三者并行工作并展示可见的进度。这是最简单的看板用例，也是原始设计优化的场景。

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

启动消息网关然后离开——它托管着嵌入式调度器，该调度器会在同一个 `kanban.db` 上拾取所有三个专业配置的任务：

```bash
hermes gateway start
```

现在将看板过滤到 `content-ops`（或者直接搜索 "Transcribe"），你会得到这个：

![过滤到转录任务的舰队视图](/img/kanban-tutorial/07-fleet-transcribes.png)

两个转录任务已完成，一个正在运行，两个就绪等待下一个调度器周期。"进行中"列按配置分组（默认的"按配置划分泳道"），因此你无需扫描混合列表就能看到每个工作进程的活跃任务。一旦当前任务完成，调度器会立即将下一个就绪任务提升为运行状态。三个守护进程并行处理三个受指派人池，整个内容队列无需进一步人工干预即可清空。

**故事 1 中关于结构化交接的一切在这里仍然适用。** 翻译员工作进程完成调用时发出 `kanban_complete(summary="translated 4 pages, style matched existing marketing voice", metadata={"duration_seconds": 720, "tokens_used": 2100})` —— 这对分析和任何依赖此任务的下游任务都很有用。

## 故事 3 — 带重试的角色流水线

这就是看板相对于扁平 TODO 列表的价值所在。产品经理编写规范。工程师实现它。评审员拒绝第一次尝试。工程师修改后再次尝试。评审员批准。

按 `auth-project` 过滤的仪表板视图：

![多角色功能的流水线视图](/img/kanban-tutorial/08-pipeline-auth.png)

三阶段链一目了然：`Spec: password reset flow`（已完成，产品经理），`Implement password reset flow`（已完成，后端开发），`Review password reset PR`（就绪，评审员）。每个任务底部都有其父任务（绿色显示），子任务作为依赖项。

有趣的是实现任务，因为它曾被阻塞并重试。以下是完整的三 Agent 编排，显示为每个工作进程模型进行的工具调用：

```python
# --- PM worker spawns on $SPEC and writes the acceptance criteria ---
# worker tool calls
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
# → $SPEC is done; $IMPL auto-promotes from todo to ready

# --- Engineer worker spawns on $IMPL (first attempt) ---
# worker tool calls
kanban_show()   # reads $SPEC's summary + acceptance metadata in worker_context
# (engineer writes code, runs tests, opens PR)
# Reviewer feedback arrives — engineer decides the concerns are valid and blocks
kanban_block(
    reason="Review: password strength check missing, reset link isn't "
           "single-use (can be replayed within 30min)",
)
# → $IMPL transitions to blocked; run 1 closes with outcome='blocked'
```

现在你（人类，或单独的评审员配置）阅读阻塞原因，确定修复方向明确，然后从仪表板的"解除阻塞"按钮解除阻塞——或者通过 CLI / 斜杠命令：

```bash
hermes kanban unblock $IMPL
# or from a chat: /kanban unblock $IMPL
```

调度器将 `$IMPL` 提升回 `ready` 状态，并在下一个周期重新生成 `backend-dev` 工作进程。这第二次生成是同一任务上的**新运行**：

```python
# --- Engineer worker spawns on $IMPL (second attempt) ---
# worker tool calls
kanban_show()
# → worker_context now includes the run 1 block reason, so this worker knows
#   which two things to fix instead of re-reading the whole spec
# (engineer adds zxcvbn check, makes reset tokens single-use, re-runs tests)
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

- **运行 1** — 被 `@backend-dev` `blocked`。评审反馈就在结果下方："password strength check missing, reset link isn't single-use (can be replayed within 30min)"。
- **运行 2** — 被 `@backend-dev` `completed`。新的摘要，新的元数据。

每次运行都是 `task_runs` 表中的一行，有自己的结果、摘要和元数据。重试历史不是事后才想到的、叠加在"最新状态"任务之上的概念层——它是主要的表示形式。当重试工作进程打开任务时，`build_worker_context` 会向其显示先前的尝试，因此第二次尝试的工作进程能看到第一次尝试被阻塞的原因，并针对这些具体发现进行修复，而不是从头重新运行。
审阅者接下来接手。当他们打开 `Review password reset PR` 时，会看到：

![审阅者的流水线抽屉视图](/img/kanban-tutorial/09-drawer-pipeline-review.png)

父链接指向已完成的实现。当审阅者的 worker 在 `Review password reset PR` 上启动并调用 `kanban_show()` 时，返回的 `worker_context` 包含了父任务最近一次已完成运行的摘要 + 元数据 —— 因此审阅者在查看差异之前，就已经读到"添加了 zxcvbn 强度检查，重置令牌现在为单次使用"，并且手头有了已更改文件的列表。

## 故事 4 —— 熔断器和崩溃恢复

真实的 worker 会失败。缺少凭据、OOM 终止、瞬时网络错误。调度器有两道防线：一个**熔断器**，在连续 N 次失败后自动阻塞任务，使看板不会永远无谓重试；以及**崩溃检测**，它会回收那些 worker PID 在其 TTL 过期前就消失的任务。

### 熔断器 —— 看似永久性的故障

一个部署任务，因为配置文件的执行环境中未设置 `AWS_ACCESS_KEY_ID` 而无法启动其 worker：

```bash
hermes kanban create "Deploy to staging (missing creds)" \
    --assignee deploy-bot --tenant ops
```

调度器尝试启动 worker。启动失败（`RuntimeError: AWS_ACCESS_KEY_ID not set`）。调度器释放任务声明，增加失败计数器，并在下一个 tick 重试。在连续三次失败后（默认的 `failure_limit`），熔断器触发：任务进入 `blocked` 状态，结果为 `gave_up`。在人工解除阻塞之前，不再重试。

点击被阻塞的任务：

![熔断器 —— 2 次 spawn_failed + 1 次 gave_up](/img/kanban-tutorial/11-drawer-gave-up.png)

三次运行，`error` 字段都是相同的错误。前两次是 `spawn_failed`（可重试），第三次是 `gave_up`（终止）。上方的事件日志显示了完整序列：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

在终端中：

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

### 崩溃恢复 —— worker 中途死亡

有时启动成功，但 worker 进程后来死亡 —— 段错误、OOM、`systemctl stop`。调度器轮询 `kill(pid, 0)` 并检测到死亡的 pid；声明被释放，任务回到 `ready` 状态，下一个 tick 会将其分配给一个新的 worker。

种子数据中的示例是一个内存耗尽的迁移：

```bash
# Worker 声明任务，开始扫描 240 万行，在约 230 万行时被 OOM 终止
# 调度器检测到死亡 pid，释放声明，增加尝试计数器
# 使用分块策略重试成功
```

抽屉显示了完整的两次尝试历史：

![崩溃与恢复 —— 1 次 crashed + 1 次 completed](/img/kanban-tutorial/06-drawer-crash-recovery.png)

运行 1 —— `crashed`，错误为 `OOM kill at row 2.3M (process 99999 gone)`。运行 2 —— `completed`，其元数据中包含 `"strategy": "chunked with LIMIT + WHERE id > last_id"`。重试的 worker 在其上下文中看到了运行 1 的崩溃，并选择了更安全的策略；元数据使得未来的观察者（或事后分析撰写者）能清楚地知道发生了什么变化。

## 结构化交接 —— 为什么 `summary` 和 `metadata` 很重要

在上述每个故事中，worker 在结束时都调用了 `kanban_complete(summary=..., metadata=...)`。这不是装饰 —— 这是工作流各阶段之间的主要交接渠道。

当任务 B 上的 worker 启动并调用 `kanban_show()` 时，它获取的 `worker_context` 包含：

- B 的**先前尝试**（之前的运行：结果、摘要、错误、元数据），以便重试的 worker 不会重复失败路径。
- **父任务结果** —— 对于每个父任务，最近一次已完成运行的摘要和元数据 —— 以便下游 worker 了解上游工作完成的原因和方式。

这取代了困扰扁平看板系统的"在评论和工作输出中翻找"的繁琐过程。产品经理在规范的元数据中编写验收标准，工程师的 worker 在父任务交接中结构化地看到它们。工程师记录了他们运行了哪些测试以及通过了多少，审阅者的 worker 在打开差异之前就已经掌握了这个列表。

批量关闭保护的存在是因为这些数据是按运行存储的。`hermes kanban complete a b c --summary X`（你，从 CLI 执行）会被拒绝 —— 将相同的摘要复制粘贴到三个任务几乎总是错误的。不带交接标志的批量关闭仍然适用于常见的"我完成了一堆管理任务"的情况。工具界面根本不暴露批量变体；出于同样的原因，`kanban_complete` 始终是一次一个任务。

## 检查当前正在运行的任务

为了完整性 —— 这是一个仍在进行中的任务的抽屉（来自故事 1 的 API 实现，由 `backend-dev` 声明但尚未完成）：

![已声明、进行中的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

状态为 `Running`。活动运行出现在"运行历史"部分，结果为 `active` 且没有 `ended_at`。如果此 worker 死亡或超时，调度器将以适当的结果关闭此运行，并在下一次声明时打开一个新的运行 —— 尝试记录永远不会消失。

## 后续步骤

- [看板概述](./kanban) —— 完整的数据模型、事件词汇表和 CLI 参考。
- `hermes kanban --help` —— 每个子命令，每个标志。
- `hermes kanban watch --kinds completed,gave_up,timed_out` —— 在整个看板上实时流式传输终端事件。
- `hermes kanban notify-subscribe <task> --platform telegram --chat-id <id>` —— 当特定任务完成时获取消息网关通知。