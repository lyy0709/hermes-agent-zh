# Kanban 教程

通过浏览器中打开的仪表盘，逐步演示 Hermes Kanban 系统设计的四种使用场景。如果你还没有阅读 [Kanban 概览](./kanban)，请先阅读那里——本教程假设你了解任务、运行、负责人和调度器的概念。

## 设置

```bash
hermes kanban init           # 可选；首次执行 `hermes kanban <任何命令>` 会自动初始化
hermes dashboard             # 在浏览器中打开 http://127.0.0.1:9119
# 点击左侧导航栏中的 Kanban
```

仪表盘是学习该系统最舒适的地方。你在这里看到的所有内容也可以通过 CLI 上的 `hermes kanban <动词>` 获得——这两个界面共享同一个位于 `~/.hermes/kanban.db` 的 SQLite 数据库。

## 看板概览

![Kanban 看板概览](/img/kanban-tutorial/01-board-overview.png)

六个列，从左到右：

- **待处理** —— 原始想法，在任何人开始工作之前，规范制定者会完善规范。
- **待办** —— 已创建但等待依赖项，或尚未分配。
- **就绪** —— 已分配并等待调度器认领。
- **进行中** —— 一个工作者正在积极执行任务。当“按配置文件分道”开启时（默认），此列按负责人分组，因此你可以一目了然地看到每个工作者正在做什么。
- **阻塞** —— 工作者请求人工输入，或断路器跳闸。
- **已完成** —— 已完成。

顶部栏有搜索、租户和负责人的过滤器，以及一个 `按配置文件分道` 切换按钮和一个 `轻推调度器` 按钮，该按钮立即运行一次调度周期，而不是等待守护进程的下一个间隔。点击任何卡片会在右侧打开其抽屉。

### 平铺视图

如果配置文件分道显得杂乱，可以关闭“按配置文件分道”，进行中列将折叠为按认领时间排序的单个平铺列表：

![关闭按配置文件分道的看板](/img/kanban-tutorial/02-board-flat.png)

## 场景 1 —— 独立开发者交付功能

你正在构建一个功能。经典流程：设计模式、实现 API、编写测试。三个任务具有父→子依赖关系。

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

因为 `API` 将 `SCHEMA` 作为其父任务，而 `tests` 将 `API` 作为其父任务，所以只有 `SCHEMA` 开始时处于 `就绪` 状态。其他两个任务停留在 `待办` 状态，直到它们的父任务完成。这是依赖关系提升引擎在发挥作用——在有待测试的 API 之前，不会有其他工作者接手编写测试的任务。

认领模式任务，完成工作，交接：

```bash
hermes kanban claim $SCHEMA

# (你设计模式，提交等)

hermes kanban complete $SCHEMA \
    --summary "users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); 刷新令牌存储为 type='refresh' 的会话" \
    --metadata '{
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["bcrypt 用于哈希", "JWT 用于会话令牌", "7天刷新，15分钟访问"]
    }'
```

当 `SCHEMA` 进入 `已完成` 状态时，依赖关系引擎会自动将 `API` 提升到 `就绪` 状态。API 工作者在接手时，将在其上下文中读取 `SCHEMA` 的摘要和元数据——因此它无需重新阅读冗长的设计文档就能了解模式决策。

在看板上点击已完成的模式任务，抽屉会显示所有内容：

![独立开发者 —— 已完成的模式任务抽屉](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的运行历史部分是关键补充。一次尝试：结果 `已完成`，工作者 `@backend-dev`，持续时间，时间戳，以及完整的交接摘要。元数据块（`changed_files`，`decisions`）也存储在运行记录上，并呈现给任何读取此父任务的下游工作者。

在 CLI 上：

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  结果         配置文件       耗时     开始时间
# 1  已完成       backend-dev        0s  2026-04-27 19:34
#    → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 场景 2 —— 批量处理

你有三个工作者（一个翻译员、一个转录员、一个文案撰稿人）和一堆独立任务。你希望三者并行处理并显示可见的进度。这是最简单的看板使用场景，也是原始设计优化的场景。

创建工作：

```bash
for lang in Spanish French German; do
    hermes kanban create "将主页翻译成 $lang" \
        --assignee translator --tenant content-ops
done
for i in 1 2 3 4 5; do
    hermes kanban create "转录 Q3 客户通话 #$i" \
        --assignee transcriber --tenant content-ops
done
for sku in 1001 1002 1003 1004; do
    hermes kanban create "生成产品描述: SKU-$sku" \
        --assignee copywriter --tenant content-ops
done
```

启动消息网关然后离开——它托管嵌入式调度器，该调度器在同一个 kanban.db 上为所有三个专业配置文件的任务提供服务：

```bash
hermes gateway start
```

现在将看板过滤到 `content-ops`（或直接搜索“Transcribe”），你会看到：

![批量视图过滤到转录任务](/img/kanban-tutorial/07-fleet-transcribes.png)

两个转录已完成，一个正在运行，两个就绪等待下一个调度器周期。进行中列按配置文件分组（“按配置文件分道”默认开启），因此你可以看到每个工作者的活动任务，而无需扫描混合列表。一旦当前任务完成，调度器将立即将下一个就绪任务提升为运行状态。三个守护进程并行处理三个负责人池中的任务，整个内容队列无需进一步人工输入即可清空。
**关于结构化交接的所有内容，故事 1 中的描述在此处仍然适用。** 翻译工作者完成一个调用时，可以传递 `--summary "translated 4 pages, style matched existing marketing voice"` 和 `--metadata '{"duration_seconds": 720, "tokens_used": 2100}'` —— 这对于分析和任何依赖于此任务的下游任务都很有用。

## 故事 3 — 带重试的角色流水线

这就是看板相对于扁平 TODO 列表的价值所在。产品经理编写规范。工程师实现它。评审员拒绝了第一次尝试。工程师进行修改后再次尝试。评审员批准。

按 `auth-project` 过滤的仪表板视图：

![多角色功能的流水线视图](/img/kanban-tutorial/08-pipeline-auth.png)

可以同时看到三个阶段：`Spec: password reset flow`（已完成，pm）、`Implement password reset flow`（已完成，backend-dev）、`Review password reset PR`（就绪，reviewer）。每个任务底部都有其父任务（绿色显示），子任务则作为依赖项。

有趣的是实现任务，因为它曾被阻塞并重试：

```bash
# PM 完成规范，并在元数据中包含验收标准
hermes kanban complete $SPEC \
    --summary "spec approved; POST /forgot-password sends email, GET /reset/:token renders form, POST /reset applies new password" \
    --metadata '{"acceptance": [
        "expired token returns 410",
        "reused last-3 password returns 400 with message",
        "successful reset invalidates all active sessions"
    ]}'

# 工程师认领并实现，但评审因缺少强度检查而阻塞了它
hermes kanban claim $IMPL
hermes kanban block $IMPL "Review: password strength check missing, reset link isn't single-use (can be replayed within 30min)"

# 工程师迭代、解决、完成
hermes kanban unblock $IMPL
hermes kanban claim $IMPL
hermes kanban complete $IMPL \
    --summary "added zxcvbn strength check, reset tokens are now single-use (stored + deleted on success)" \
    --metadata '{
        "changed_files": ["auth/reset.py", "auth/tests/test_reset.py", "migrations/003_single_use_reset_tokens.sql"],
        "tests_run": 11,
        "review_iteration": 2
    }'
```

点击实现任务。抽屉显示了**两次尝试**：

![包含两次运行的实现任务 — 先阻塞后完成](/img/kanban-tutorial/04b-drawer-retry-history-scrolled.png)

-   **运行 1** — 被 `@backend-dev` `blocked`。评审反馈就在结果下方："password strength check missing, reset link isn't single-use (can be replayed within 30min)"。
-   **运行 2** — 被 `@backend-dev` `completed`。新的摘要，新的元数据。

每次运行都是 `task_runs` 表中的一行，拥有自己的结果、摘要和元数据。重试历史不是一个事后才想到的、叠加在“最新状态”任务之上的概念层 —— 它是主要的表示形式。当重试的工作者打开任务时，`build_worker_context` 会向其展示之前的尝试，因此第二次尝试的工作者能看到第一次尝试被阻塞的原因，并针对这些具体发现进行处理，而不是从头开始重新运行。

接下来评审员接手。当他们打开 `Review password reset PR` 时，会看到：

![评审员看到的流水线抽屉视图](/img/kanban-tutorial/09-drawer-pipeline-review.png)

父链接是已完成的实现任务。当评审员的工作者调用 `build_worker_context` 时，它会拉取父任务最近一次完成运行的摘要和元数据 —— 因此评审员在查看差异之前，就能读到 "added zxcvbn strength check, reset tokens are now single-use"，并掌握已更改文件的列表。

## 故事 4 — 熔断器和崩溃恢复

真实的工作者会失败。缺少凭据、内存溢出终止、瞬时网络错误。调度器有两道防线：一个**熔断器**，在连续 N 次失败后自动阻塞任务，以免看板永远无谓地重试；以及**崩溃检测**，它会回收那些工作者进程在其 TTL 到期前就已消失的任务。

### 熔断器 — 看似永久性的故障

一个部署任务，因为配置文件的执行环境中没有设置 `AWS_ACCESS_KEY_ID` 而无法启动其工作者：

```bash
hermes kanban create "Deploy to staging (missing creds)" \
    --assignee deploy-bot --tenant ops
```

调度器尝试启动工作者。启动失败（`RuntimeError: AWS_ACCESS_KEY_ID not set`）。调度器释放认领，增加失败计数器，并在下一个周期再次尝试。在连续三次失败后（默认的 `failure_limit`），熔断器触发：任务进入 `blocked` 状态，结果为 `gave_up`。在人工解除阻塞之前，不再重试。

点击被阻塞的任务：

![熔断器 — 2 次 spawn_failed + 1 次 gave_up](/img/kanban-tutorial/11-drawer-gave-up.png)

三次运行，`error` 字段都是相同的错误。前两次是 `spawn_failed`（可重试），第三次是 `gave_up`（终止）。上方的事件日志显示了完整的序列：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

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

如果集成了 Telegram / Discord / Slack，在 `gave_up` 事件发生时，消息网关会发送通知，这样你无需检查看板就能得知故障。

### 崩溃恢复 — 工作者中途死亡

有时启动成功，但工作者进程后来死亡 —— 段错误、内存溢出、`systemctl stop`。调度器轮询 `kill(pid, 0)` 并检测到死亡的进程 ID；认领被释放，任务回到 `ready` 状态，下一个周期会将其分配给一个新的工作者。

种子数据中的示例是一个内存耗尽的迁移任务：

```bash
# Worker claims, starts scanning 2.4M rows, OOM kills it at ~2.3M
# Dispatcher detects dead pid, releases claim, increments attempt counter
# Retry with a chunked strategy succeeds
```
抽屉显示了完整的两次尝试历史：

![崩溃与恢复 — 1 次崩溃 + 1 次完成](/img/kanban-tutorial/06-drawer-crash-recovery.png)

运行 1 — `crashed`，错误为 `OOM kill at row 2.3M (process 99999 gone)`。运行 2 — `completed`，其元数据中包含 `"strategy": "chunked with LIMIT + WHERE id > last_id"`。重试的 worker 在其上下文中看到了运行 1 的崩溃，并选择了更安全的策略；元数据使得未来的观察者（或事后分析撰写者）能够清楚地了解发生了什么变化。

## 结构化交接 — 为什么 `--summary` 和 `--metadata` 很重要

在上述每个故事中，worker 在完成任务时都传递了 `--summary` 和 `--metadata`。这并非装饰 — 它是工作流各阶段之间的主要交接渠道。

当处理任务 B 的 worker 读取其上下文时，它会获得：

- B 的**先前尝试**（之前的运行：结果、摘要、错误、元数据），以便重试的 worker 不会重复失败路径。
- **父任务结果** — 对于每个父任务，最近一次已完成运行的摘要和元数据 — 以便下游 worker 了解上游工作完成的原因和方式。

这取代了困扰扁平看板系统的“在评论和工作输出中翻找”的繁琐操作。项目经理在规范的元数据中编写验收标准，工程师的 worker 可以结构化地看到它们。工程师记录了他们运行了哪些测试以及通过了多少，而评审者的 worker 在打开差异文件之前就已经掌握了这个列表。

批量关闭保护机制的存在是因为这些数据是按运行记录的。`hermes kanban complete a b c --summary X` 会被拒绝 — 将相同的摘要复制粘贴到三个任务几乎总是错误的。不带交接标志的批量关闭仍然适用于常见的“我完成了一堆管理任务”的情况。

## 检查当前正在运行的任务

为了完整性 — 这里是一个仍在进行中的任务的抽屉（故事 1 中的 API 实现，已被 `backend-dev` 认领但尚未完成）：

![已认领、进行中的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

状态为 `Running`。活动运行出现在“运行历史”部分，结果为 `active` 且没有 `ended_at`。如果此 worker 死亡或超时，调度器将使用适当的结果关闭此运行，并在下一次认领时打开一个新的运行 — 尝试记录永远不会消失。

## 后续步骤

- [看板概述](./kanban) — 完整的数据模型、事件词汇表和 CLI 参考。
- `hermes kanban --help` — 每个子命令，每个标志。
- `hermes kanban watch --kinds completed,gave_up,timed_out` — 在整个看板上实时流式传输终端事件。
- `hermes kanban notify-subscribe <task> --platform telegram --chat-id <id>` — 当特定任务完成时，获取消息网关的 ping 通知。