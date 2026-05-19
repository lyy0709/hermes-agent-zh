---
sidebar_position: 7
title: "会话"
description: "会话持久化、恢复、搜索、管理以及各平台的会话追踪"
---

# 会话

Hermes Agent 会自动将每次对话保存为会话。会话支持对话恢复、跨会话搜索以及完整的对话历史管理。

## 会话工作原理

每次对话——无论是来自 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Teams 还是任何其他消息平台——都会作为包含完整消息历史的会话存储下来。会话通过两个互补的系统进行追踪：

1.  **SQLite 数据库** (`~/.hermes/state.db`) —— 结构化的会话元数据，支持 FTS5 全文搜索
2.  **JSONL 转录文件** (`~/.hermes/sessions/`) —— 原始对话转录，包括工具调用（消息网关）

SQLite 数据库存储：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一的、人类可读的名称）
- 模型名称和配置
- 系统提示词快照
- 完整的消息历史（角色、内容、工具调用、工具结果）
- Token 计数（输入/输出）
- 时间戳（开始时间、结束时间）
- 父会话 ID（用于由压缩触发的会话拆分）

### 计入上下文的内容

Hermes 存储会话历史以便恢复对话，但它不会持续重新发送它处理过的每一个字节。在每一轮交互中，模型看到的是选定的系统提示词、当前的对话窗口，以及 Hermes 为该轮交互明确注入的任何内容。

媒体附件作为轮次范围内的输入处理：

- 图像可以原生附加到下一次模型调用，或者在活动模型不支持原生视觉时，预先分析为文本描述。
- 当配置了语音转文本时，音频会被转录为文本。
- 文本文档可以包含其提取的文本；其他文档类型通常由保存的本地路径和简短说明表示。
- 附件路径和提取/派生的文本可以出现在转录中，但原始的图像、音频或二进制文件字节不会重复复制到未来的提示词中。

例如，如果用户发送一张图片并要求 Hermes 用它制作一个表情包，Hermes 可能会用视觉模型检查一次该图片并运行一个图像处理脚本。未来的轮次不会自动在上下文中携带原始的 JPEG 文件。它们只携带写入对话的任何内容，例如用户的请求、简短的图片描述、本地缓存路径或最终的助手回复。

上下文增长最常见的原因不是媒体文件本身。而是冗长的文本：粘贴的转录稿、完整的日志、大量的工具输出、冗长的差异对比、重复的状态报告以及详细的证明转储。相比于将大型工件复制到聊天中，更推荐使用摘要、文件路径、精选摘录以及基于工具的查找。

:::tip
当会话变长时使用 `/compress`，需要新线程时使用 `/new`，而 `hermes sessions prune` 仅在你希望从存储中删除旧的已结束会话时使用。压缩会减少活动上下文；它不是隐私删除。
:::

### 会话来源

每个会话都标有其来源平台：

| 来源 | 描述 |
|--------|-------------|
| `cli` | 交互式 CLI (`hermes` 或 `hermes chat`) |
| `telegram` | Telegram 信使 |
| `discord` | Discord 服务器/私信 |
| `slack` | Slack 工作区 |
| `whatsapp` | WhatsApp 信使 |
| `signal` | Signal 信使 |
| `matrix` | Matrix 房间和私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件 (IMAP/SMTP) |
| `sms` | 通过 Twilio 的短信 |
| `dingtalk` | 钉钉信使 |
| `feishu` | 飞书信使 |
| `wecom` | 企业微信 |
| `weixin` | 微信（个人微信） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器的 Apple iMessage |
| `qqbot` | QQ 机器人（腾讯 QQ）通过官方 API v2 |
| `homeassistant` | Home Assistant 对话 |
| `webhook` | 传入的 Webhook |
| `api-server` | API 服务器请求 |
| `acp` | ACP 编辑器集成 |
| `cron` | 定时任务 |
| `batch` | 批量处理运行 |

## CLI 会话恢复

使用 `--continue` 或 `--resume` 从 CLI 恢复之前的对话：

### 继续上一个会话

```bash
# 恢复最近的 CLI 会话
hermes --continue
hermes -c

# 或者使用 chat 子命令
hermes chat --continue
hermes chat -c
```

这会从 SQLite 数据库中查找最近的 `cli` 会话并加载其完整的对话历史。

### 按名称恢复

如果你给会话设置了标题（见下面的[会话命名](#session-naming)），你可以按名称恢复它：

```bash
# 恢复一个命名的会话
hermes -c "my project"

# 如果存在谱系变体（my project, my project #2, my project #3），
# 这会自动恢复最近的一个
hermes -c "my project"   # → 恢复 "my project #3"
```

### 恢复特定会话

```bash
# 按 ID 恢复特定会话
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# 按标题恢复
hermes --resume "refactoring auth"

# 或者使用 chat 子命令
hermes chat --resume 20250305_091523_a1b2c3d4
```

会话 ID 在你退出 CLI 会话时会显示，也可以通过 `hermes sessions list` 找到。

### 恢复时的对话摘要

当你恢复一个会话时，Hermes 会在输入提示符之前，在一个样式化的面板中显示先前对话的紧凑摘要：

<img className="docs-terminal-figure" src="/img/docs/session-recap.svg" alt="恢复 Hermes 会话时显示的'先前对话'摘要面板的样式化预览。" />
<p className="docs-figure-caption">恢复模式会显示一个包含最近用户和助手轮次的紧凑摘要面板，然后将你返回到实时提示符。</p>

摘要：
- 显示**用户消息**（金色 `●`）和**助手回复**（绿色 `◆`）
- **截断**长消息（用户消息 300 字符，助手消息 200 字符 / 3 行）
- **折叠工具调用**为数量及工具名称（例如，`[3 tool calls: terminal, web_search]`）
- **隐藏**系统消息、工具结果和内部推理
- **限制**为最近的 10 次交互，并带有 "... N earlier messages ..." 指示器
- 使用**暗淡的样式**以区别于活动对话
要禁用完整回顾并保持最小化单行行为，请在 `~/.hermes/config.yaml` 中设置：

```yaml
display:
  resume_display: minimal   # 默认值：full
```

:::tip
会话 ID 遵循格式 `YYYYMMDD_HHMMSS_<hex>` — CLI/TUI 会话使用 6 位十六进制后缀（例如 `20250305_091523_a1b2c3`），消息网关会话使用 8 位后缀（例如 `20250305_091523_a1b2c3d4`）。你可以通过 ID（完整或唯一前缀）或标题来恢复会话 — 两者都适用于 `-c` 和 `-r` 参数。
:::

## 跨平台交接

在 CLI 会话中使用 `/handoff <platform>` 将实时对话转移到消息平台的主频道。Agent 会从 CLI 中断的地方无缝衔接 — 相同的会话 ID、完整的角色感知转录、工具调用等所有内容。

```bash
# 在 CLI 会话内部
/handoff telegram
```

执行过程：

1.  CLI 验证 `<platform>` 是否已启用并设置了主频道（在目标聊天中运行一次 `/sethome` 进行配置）。
2.  CLI 将会话标记为待处理状态，并**阻塞轮询消息网关**。如果 Agent 正在响应中，则会拒绝 — 请等待当前响应完成。
3.  消息网关监听器认领交接任务，并向目标适配器请求一个新线程：
    -   **Telegram** — 打开一个新的论坛主题（如果聊天中启用了 Bot API 9.4+ 的主题模式，则为私聊主题；或论坛超级群组主题）。
    -   **Discord** — 在主文本频道下创建一个 1440 分钟自动归档的线程。
    -   **Slack** — 发布一条种子消息，并使用其 `ts` 作为线程锚点。
    -   **WhatsApp / Signal / Matrix / SMS** — 无原生线程支持，直接回退到主频道。
4.  消息网关将目标键重新绑定到你现有的 CLI 会话 ID，然后伪造一个合成用户回合，要求 Agent 确认并总结。回复将出现在新线程中。
5.  当消息网关确认成功后，CLI 会打印一个 `/resume` 提示并干净地退出：

   ```
   ↻ 交接完成。会话现已在 telegram 上激活。
     稍后可通过以下命令在此 CLI 上恢复：/resume my-session-title
   ```

6.  从此刻起，对话将在该平台上进行。在新线程中回复 — 该频道中任何授权用户共享同一会话，并且之后线程中的任何真实用户消息都可以无缝加入，因为线程会话的键不包含 `user_id`。

**恢复回 CLI：** 当你想回到桌面环境时，只需运行 `/resume <title>`（或在 shell 中运行 `hermes -r "<title>"`），即可从平台中断处继续。

**失败模式：**
- 未配置主频道 → CLI 拒绝并给出 `/sethome` 提示。
- 平台未启用 / 消息网关未运行 → CLI 在 60 秒后超时，并显示明确消息，你的 CLI 会话保持不变。
- 线程创建失败（权限不足、主题模式关闭） → 直接回退到主频道，交接仍能完成；没有线程隔离，但交接本身有效。
- `adapter.send` 失败（速率限制、临时 API 错误） → 交接被标记为失败并附带原因；该行记录会被清除，以便重试。

**值得了解的局限性：** 对于不支持线程且拥有多用户群组主频道的平台，合成回合会以私聊风格的会话形式进行键控。这对于自用私聊主频道（典型设置）有效，但对于真正共享的群组聊天并不理想。线程功能覆盖了 Telegram / Discord / Slack — 这是最常见的情况 — 因此大多数设置不会遇到此问题。

## 会话命名

为会话设置易于理解的标题，以便轻松查找和恢复。

### 自动生成标题

Hermes 在首次交流后会自动为每个会话生成一个简短的描述性标题（3–7 个词）。这使用一个快速的辅助模型在后台线程中运行，因此不会增加延迟。当你使用 `hermes sessions list` 或 `hermes sessions browse` 浏览会话时，会看到自动生成的标题。

自动标题功能每个会话仅触发一次，如果你已手动设置标题，则会跳过。

### 手动设置标题

在任何聊天会话（CLI 或消息网关）中使用 `/title` 斜杠命令：

```
/title my research project
```

标题会立即应用。如果会话尚未在数据库中创建（例如，在发送第一条消息之前运行 `/title`），它会被排队并在会话启动后应用。

你也可以从命令行重命名现有会话：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

-   **唯一性** — 任何两个会话不能共享相同的标题
-   **最多 100 个字符** — 保持列表输出整洁
-   **已清理** — 控制字符、零宽字符和 RTL 覆盖符会自动剥离
-   **普通 Unicode 字符均可** — 表情符号、中日韩文字、带重音符号的字符均可使用

### 压缩时的自动谱系

当会话的上下文被压缩时（通过 `/compress` 手动或自动），Hermes 会创建一个新的延续会话。如果原始会话有标题，新会话会自动获得一个带编号的标题：

```
"my project" → "my project #2" → "my project #3"
```

当你按名称恢复时（`hermes -c "my project"`），它会自动选择谱系中最新的会话。

### 消息平台中的 `/title`

`/title` 命令在所有消息网关平台（Telegram、Discord、Slack、WhatsApp）中均有效：

-   `/title My Research` — 设置会话标题
-   `/title` — 显示当前标题

## 会话管理命令

Hermes 通过 `hermes sessions` 提供了一套完整的会话管理命令：

### 列出会话

```bash
# 列出最近的会话（默认：最近 20 个）
hermes sessions list

# 按平台筛选
hermes sessions list --source telegram

# 显示更多会话
hermes sessions list --limit 50
```

当会话有标题时，输出会显示标题、预览和相对时间戳：

```
Title                  Preview                                  Last Active   ID
────────────────────────────────────────────────────────────────────────────────────────────────
refactoring auth       Help me refactor the auth module please   2h ago        20250305_091523_a
my project #3          Can you check the test failures?          yesterday     20250304_143022_e
—                      What's the weather in Las Vegas?          3d ago        20250303_101500_f
```
当没有会话标题时，会使用更简单的格式：

```
预览                                            最后活跃   来源   ID
──────────────────────────────────────────────────────────────────────────────────────
请帮我重构认证模块                                2小时前   cli   20250305_091523_a
拉斯维加斯的天气怎么样？                           3天前    tele  20250303_101500_f
```

### 导出会话

```bash
# 将所有会话导出到 JSONL 文件
hermes sessions export backup.jsonl

# 导出特定平台的会话
hermes sessions export telegram-history.jsonl --source telegram

# 导出单个会话
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

导出的文件每行包含一个 JSON 对象，其中包含完整的会话元数据和所有消息。

### 删除会话

```bash
# 删除特定会话（需要确认）
hermes sessions delete 20250305_091523_a1b2c3d4

# 无需确认直接删除
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### 重命名会话

```bash
# 设置或更改会话标题
hermes sessions rename 20250305_091523_a1b2c3d4 "debugging auth flow"

# 多词标题在 CLI 中不需要引号
hermes sessions rename 20250305_091523_a1b2c3d4 debugging auth flow
```

如果标题已被其他会话使用，则会显示错误。

### 清理旧会话

```bash
# 删除超过 90 天（默认值）的已结束会话
hermes sessions prune

# 自定义时间阈值
hermes sessions prune --older-than 30

# 仅清理特定平台的会话
hermes sessions prune --source telegram --older-than 60

# 跳过确认
hermes sessions prune --older-than 30 --yes
```

:::info
清理操作仅删除**已结束**的会话（已明确结束或自动重置的会话）。活跃会话永远不会被清理。
:::

### 会话统计

```bash
hermes sessions stats
```

输出：

```
总会话数：142
总消息数：3847
  cli：89 个会话
  telegram：38 个会话
  discord：15 个会话
数据库大小：12.4 MB
```

要进行更深入的分析——Token 使用量、成本估算、工具使用细分和活动模式——请使用 [`hermes insights`](/docs/reference/cli-commands#hermes-insights)。

## 会话搜索工具

Agent 内置了一个 `session_search` 工具，它使用 SQLite 的 FTS5 引擎对所有过去的对话进行全文搜索——并允许 Agent 滚动浏览它找到的任何会话。无需调用 LLM，无需摘要，无需截断。每种调用形式都返回数据库中的实际消息。

### 三种调用形式

该工具根据你设置的参数推断你想要什么。没有 `mode` 参数。

**1. 发现 —— 传递 `query`：**

```python
session_search(query="auth refactor", limit=3)
```

运行 FTS5，按会话谱系对命中结果去重，返回前 N 个会话。每个结果包含：

- `session_id`、`title`、`when`、`source`
- `snippet` —— FTS5 高亮显示的匹配片段
- `bookend_start` —— 会话的前 3 条用户+助手消息（目标/启动）
- `messages` —— FTS5 匹配位置前后约 5 条消息，锚点消息被标记（上下文中的命中）
- `bookend_end` —— 会话的最后 3 条用户+助手消息（解决方案/决策）
- `match_message_id`、`messages_before`、`messages_after`

书签 + 窗口共同重构了从目标 → 匹配 → 解决方案的过程，而无需支付整个转录的成本。在真实的会话数据库上，典型的耗时：15–50 毫秒。

**2. 滚动 —— 传递 `session_id` + `around_message_id`：**

```python
session_search(session_id="20260510_174648_805cc2", around_message_id=590803, window=10)
```

返回以锚点为中心、前后 ±`window` 条消息的窗口。不使用 FTS5，没有书签——只有切片。在发现调用之后，当你需要比默认的 ±5 窗口更多上下文时使用。

- 要**向前**滚动：将 `messages[-1].id` 作为 `around_message_id` 传回
- 要**向后**滚动：将 `messages[0].id` 作为 `around_message_id` 传回
- 边界消息作为方向标记出现在两个窗口中
- 当 `messages_before` 或 `messages_after` 小于 `window` 时，表示你已到达会话的开始或结尾

每次滚动调用的典型耗时：1–2 毫秒。

**3. 浏览 —— 无参数：**

```python
session_search()
```

按时间顺序返回最近的会话（标题、预览、时间戳）。当用户询问“我之前在做什么”但没有指定主题时很有用。

### FTS5 查询语法

搜索支持标准的 FTS5 查询语法：

- 简单关键词：`docker deployment`（FTS5 默认为 AND）
- 短语：`"exact phrase"`
- 布尔运算：`docker OR kubernetes`、`python NOT java`
- 前缀：`deploy*`

### 可选参数

- `sort` —— `newest` 或 `oldest`，在 FTS5 排名之上。省略则仅按相关性排序（默认；适合探索性回忆）。使用 `newest` 处理“我们上次把 X 留在了哪里”这类问题，使用 `oldest` 处理“X 是如何开始的”这类问题。
- `role_filter` —— 要包含的角色，用逗号分隔。发现模式默认为 `user,assistant`（工具输出通常是噪音）。传递 `user,assistant,tool` 以包含工具输出（调试工具行为），或传递 `tool` 以仅搜索工具输出。

### 使用时机

Agent 被提示自动使用会话搜索：

> *“当用户引用过去对话中的内容，或者你怀疑存在相关的先前上下文时，在使用户重复之前，请使用 session_search 来回忆它。”*

## 按平台的会话跟踪

### 消息网关会话

在消息平台上，会话由一个从消息源构建的确定性会话密钥来标识：

| 聊天类型 | 默认密钥格式 | 行为 |
|-----------|--------------------|----------|
| Telegram 私聊 | `agent:main:telegram:dm:<chat_id>` | 每个私聊一个会话 |
| Discord 私聊 | `agent:main:discord:dm:<chat_id>` | 每个私聊一个会话 |
| WhatsApp 私聊 | `agent:main:whatsapp:dm:<canonical_identifier>` | 每个私聊用户一个会话（当存在映射时，LID/电话号码别名会合并为一个身份） |
| 群聊 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 当平台暴露用户 ID 时，群内每个用户一个会话 |
| 群组线程/主题 | `agent:main:<platform>:group:<chat_id>:<thread_id>` | 所有线程参与者共享一个会话（默认）。使用 `thread_sessions_per_user: true` 时为每个用户一个会话。 |
| 频道 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 当平台暴露用户 ID 时，频道内每个用户一个会话 |
当 Hermes 无法获取共享聊天的参与者标识符时，它会回退到为该房间使用一个共享会话。

### 共享与隔离的群组会话

默认情况下，Hermes 在 `config.yaml` 中设置 `group_sessions_per_user: true`。这意味着：

- Alice 和 Bob 可以在同一个 Discord 频道中与 Hermes 对话，而不会共享对话历史记录
- 一个用户冗长且大量使用工具的任务不会污染另一个用户的上下文窗口
- 中断处理也保持按用户进行，因为运行中的 Agent 密钥与隔离的会话密钥相匹配

如果你想要一个共享的“房间大脑”，请设置：

```yaml
group_sessions_per_user: false
```

这将使群组/频道恢复为每个房间使用单个共享会话，这会保留共享的对话上下文，但也会共享 Token 成本、中断状态和上下文增长。

### 会话重置策略

消息网关会话会根据可配置的策略自动重置：

- **idle** — 在 N 分钟不活动后重置
- **daily** — 每天在特定小时重置
- **both** — 以先到者为准（空闲或每日）重置
- **none** — 从不自动重置

在会话自动重置之前，Agent 会获得一个回合来保存对话中任何重要的记忆或技能。

无论策略如何，具有**活动后台进程**的会话永远不会自动重置。

## 存储位置

| 内容 | 路径 | 描述 |
|------|------|-------------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话元数据 + 带有 FTS5 的消息 |
| 消息网关对话记录 | `~/.hermes/sessions/` | 每个会话的 JSONL 对话记录 + sessions.json 索引 |
| 消息网关索引 | `~/.hermes/sessions/sessions.json` | 将会话密钥映射到活动会话 ID |

SQLite 数据库使用 WAL 模式，支持并发读取者和单个写入者，这非常适合消息网关的多平台架构。

### 数据库模式

`state.db` 中的关键表：

- **sessions** — 会话元数据（id、source、user_id、model、title、时间戳、Token 计数）。标题具有唯一索引（允许 NULL 标题，只有非 NULL 标题必须唯一）。
- **messages** — 完整的消息历史记录（role、content、tool_calls、tool_name、token_count）
- **messages_fts** — 用于跨消息内容进行全文搜索的 FTS5 虚拟表

## 会话过期与清理

### 自动清理

- 消息网关会话根据配置的重置策略自动重置
- 重置前，Agent 会从即将过期的会话中保存记忆和技能
- 选择加入的自动清理：当 `sessions.auto_prune` 为 `true` 时，早于 `sessions.retention_days`（默认 90 天）的已结束会话会在 CLI/消息网关启动时被清理
- 在确实删除了行的清理操作之后，`state.db` 会执行 `VACUUM` 以回收磁盘空间（SQLite 不会在普通 DELETE 操作后缩小文件）
- 清理操作最多每 `sessions.min_interval_hours`（默认 24）运行一次；最后一次运行的时间戳在 `state.db` 内部跟踪，因此在同一 `HERMES_HOME` 下的每个 Hermes 进程之间共享

默认是**关闭**的 — 会话历史记录对于 `session_search` 的回忆很有价值，静默删除可能会让用户感到意外。在 `~/.hermes/config.yaml` 中启用：

```yaml
sessions:
  auto_prune: true          # 选择加入 — 默认为 false
  retention_days: 90        # 保留已结束会话的天数
  vacuum_after_prune: true  # 清理扫描后回收磁盘空间
  min_interval_hours: 24    # 不要比这个时间间隔更频繁地重新运行扫描
```

无论时间长短，活动会话永远不会被自动清理。

### 手动清理

```bash
# 清理超过 90 天的会话
hermes sessions prune

# 删除特定会话
hermes sessions delete <session_id>

# 清理前导出（备份）
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```

:::tip
数据库增长缓慢（典型情况：数百个会话占用 10-15 MB），并且会话历史记录为跨过去对话的 `session_search` 回忆提供支持，因此自动清理功能默认是禁用的。如果你运行繁重的消息网关/定时任务工作负载，并且 `state.db` 显著影响性能（观察到的故障模式：384 MB 的 state.db 包含约 1000 个会话，导致 FTS5 插入和 `/resume` 列表变慢），请启用它。使用 `hermes sessions prune` 进行一次性清理，而无需开启自动扫描。
:::