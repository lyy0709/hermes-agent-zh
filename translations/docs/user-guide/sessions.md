---
sidebar_position: 7
title: "会话"
description: "会话持久化、恢复、搜索、管理以及各平台的会话追踪"
---

# 会话

Hermes Agent 会自动将每次对话保存为会话。会话支持对话恢复、跨会话搜索以及完整的对话历史管理。

## 会话工作原理

每次对话——无论是来自 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix 还是任何其他消息平台——都会作为包含完整消息历史的会话存储下来。会话通过两个互补的系统进行追踪：

1.  **SQLite 数据库** (`~/.hermes/state.db`) —— 存储结构化的会话元数据，支持 FTS5 全文搜索
2.  **JSONL 转录文件** (`~/.hermes/sessions/`) —— 存储原始对话转录，包括工具调用（消息网关）

SQLite 数据库存储：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一、人类可读的名称）
- 模型名称和配置
- 系统提示词快照
- 完整的消息历史（角色、内容、工具调用、工具结果）
- Token 计数（输入/输出）
- 时间戳（开始时间、结束时间）
- 父会话 ID（用于因压缩而触发的会话拆分）

### 会话来源

每个会话都标有其来源平台：

| 来源 | 描述 |
|--------|-------------|
| `cli` | 交互式 CLI (`hermes` 或 `hermes chat`) |
| `telegram` | Telegram 消息应用 |
| `discord` | Discord 服务器/私信 |
| `slack` | Slack 工作区 |
| `whatsapp` | WhatsApp 消息应用 |
| `signal` | Signal 消息应用 |
| `matrix` | Matrix 房间和私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件 (IMAP/SMTP) |
| `sms` | 通过 Twilio 的短信 |
| `dingtalk` | 钉钉消息应用 |
| `feishu` | 飞书/ Lark 消息应用 |
| `wecom` | 企业微信 |
| `weixin` | 微信（个人版） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器的 Apple iMessage |
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

如果你为会话设置了标题（见下文[会话命名](#session-naming)），可以按名称恢复：

```bash
# 恢复一个已命名的会话
hermes -c "my project"

# 如果存在衍生变体（my project, my project #2, my project #3），
# 这会自动恢复最新的一个
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

退出 CLI 会话时会显示会话 ID，也可以通过 `hermes sessions list` 找到。

### 恢复时的对话摘要

当你恢复一个会话时，Hermes 会在输入提示符之前，在一个样式化的面板中显示先前对话的紧凑摘要：

<img className="docs-terminal-figure" src="/img/docs/session-recap.svg" alt="恢复 Hermes 会话时显示的'先前对话'摘要面板的样式化预览。" />
<p className="docs-figure-caption">恢复模式会显示一个紧凑的摘要面板，包含最近的用户和助手轮次，然后将你返回到实时提示符。</p>

摘要：
- 显示**用户消息**（金色 `●`）和**助手回复**（绿色 `◆`）
- **截断**长消息（用户消息 300 字符，助手回复 200 字符 / 3 行）
- **折叠工具调用**为数量及工具名称（例如，`[3 tool calls: terminal, web_search]`）
- **隐藏**系统消息、工具结果和内部推理
- **限制**为最近的 10 次交流，并带有 "... N earlier messages ..." 指示器
- 使用**暗淡的样式**以区别于活跃对话

要禁用摘要并保持最小化的单行行为，请在 `~/.hermes/config.yaml` 中设置：

```yaml
display:
  resume_display: minimal   # 默认值: full
```

:::tip
会话 ID 遵循格式 `YYYYMMDD_HHMMSS_<8-char-hex>`，例如 `20250305_091523_a1b2c3d4`。你可以按 ID 或按标题恢复——两者都适用于 `-c` 和 `-r`。
:::

## 会话命名

为会话设置人类可读的标题，以便轻松查找和恢复它们。

### 自动生成的标题

Hermes 会在第一次交流后，自动为每个会话生成一个简短的描述性标题（3-7 个词）。这使用一个快速的辅助模型在后台线程中运行，因此不会增加延迟。在使用 `hermes sessions list` 或 `hermes sessions browse` 浏览会话时，你会看到自动生成的标题。

自动命名每个会话只触发一次，如果你已经手动设置了标题，则会跳过。

### 手动设置标题

在任何聊天会话（CLI 或消息网关）中使用 `/title` 斜杠命令：

```
/title my research project
```

标题会立即应用。如果会话尚未在数据库中创建（例如，在发送第一条消息之前运行了 `/title`），它会被排队并在会话开始时应用。

你也可以从命令行重命名现有会话：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

- **唯一性** —— 任何两个会话不能共享相同的标题
- **最多 100 个字符** —— 保持列表输出整洁
- **经过清理** —— 控制字符、零宽字符和 RTL 覆盖符会被自动剥离
- **正常的 Unicode 字符都可以** —— 表情符号、中日韩文字、带重音符号的字符都可以使用

### 压缩时的自动衍生

当会话的上下文被压缩时（通过 `/compress` 手动或自动），Hermes 会创建一个新的延续会话。如果原始会话有标题，新会话会自动获得一个带编号的标题：
```
"我的项目" → "我的项目 #2" → "我的项目 #3"
```

当你通过名称恢复会话时（`hermes -c "我的项目"`），它会自动选择该谱系中最新的会话。

### 消息平台中的 /title 命令

`/title` 命令在所有消息网关平台（Telegram、Discord、Slack、WhatsApp）中都有效：

- `/title 我的研究` — 设置会话标题
- `/title` — 显示当前标题

## 会话管理命令

Hermes 通过 `hermes sessions` 提供了一套完整的会话管理命令：

### 列出会话

```bash
# 列出最近的会话（默认：最近20个）
hermes sessions list

# 按平台筛选
hermes sessions list --source telegram

# 显示更多会话
hermes sessions list --limit 50
```

当会话有标题时，输出会显示标题、预览和相对时间戳：

```
标题                  预览                                      最后活跃时间   ID
────────────────────────────────────────────────────────────────────────────────────────────────
重构认证模块           请帮我重构认证模块                          2小时前      20250305_091523_a
我的项目 #3            你能检查一下测试失败吗？                     昨天         20250304_143022_e
—                     拉斯维加斯的天气怎么样？                     3天前        20250303_101500_f
```

当没有会话有标题时，会使用更简单的格式：

```
预览                                            最后活跃时间   来源   ID
──────────────────────────────────────────────────────────────────────────────────────
请帮我重构认证模块                                 2小时前      cli   20250305_091523_a
拉斯维加斯的天气怎么样？                            3天前       tele  20250303_101500_f
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
# 删除特定会话（带确认）
hermes sessions delete 20250305_091523_a1b2c3d4

# 无需确认直接删除
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### 重命名会话

```bash
# 设置或更改会话标题
hermes sessions rename 20250305_091523_a1b2c3d4 "调试认证流程"

# 在 CLI 中，多词标题不需要引号
hermes sessions rename 20250305_091523_a1b2c3d4 调试认证流程
```

如果该标题已被其他会话使用，则会显示错误。

### 清理旧会话

```bash
# 删除超过 90 天（默认）的已结束会话
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

Agent 内置了一个 `session_search` 工具，它使用 SQLite 的 FTS5 引擎对所有过去的对话进行全文搜索。

### 工作原理

1.  FTS5 搜索匹配的消息并按相关性排序
2.  按会话对结果进行分组，取前 N 个唯一的会话（默认为 3）
3.  加载每个会话的对话，截断至约 100K 字符，并围绕匹配项居中显示
4.  发送到快速摘要模型以生成聚焦摘要
5.  返回每个会话的摘要，包含元数据和周围上下文

### FTS5 查询语法

搜索支持标准的 FTS5 查询语法：

-   简单关键词：`docker deployment`
-   短语：`"exact phrase"`
-   布尔运算：`docker OR kubernetes`，`python NOT java`
-   前缀：`deploy*`

### 使用时机

Agent 被提示自动使用会话搜索：

> *"当用户引用过去对话中的内容，或者你怀疑存在相关的先前上下文时，请使用 session_search 来回忆它，而不是要求用户重复。"*

## 按平台的会话跟踪

### 消息网关会话

在消息平台上，会话由一个根据消息来源构建的确定性会话密钥来标识：

| 聊天类型 | 默认密钥格式 | 行为 |
|-----------|--------------------|----------|
| Telegram 私聊 | `agent:main:telegram:dm:<chat_id>` | 每个私聊一个会话 |
| Discord 私聊 | `agent:main:discord:dm:<chat_id>` | 每个私聊一个会话 |
| WhatsApp 私聊 | `agent:main:whatsapp:dm:<chat_id>` | 每个私聊一个会话 |
| 群聊 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 当平台暴露用户 ID 时，群内每个用户一个会话 |
| 群组线程/主题 | `agent:main:<platform>:group:<chat_id>:<thread_id>` | 线程所有参与者共享一个会话（默认）。使用 `thread_sessions_per_user: true` 时为每个用户一个会话。 |
| 频道 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 当平台暴露用户 ID 时，频道内每个用户一个会话 |

当 Hermes 无法为共享聊天获取参与者标识符时，它会回退到为该房间使用一个共享会话。

### 共享与隔离的群组会话

默认情况下，Hermes 在 `config.yaml` 中使用 `group_sessions_per_user: true`。这意味着：

-   Alice 和 Bob 可以在同一个 Discord 频道中与 Hermes 对话，而无需共享对话历史记录
-   一个用户长时间、大量使用工具的任务不会污染另一个用户的上下文窗口
-   中断处理也保持按用户进行，因为正在运行的 Agent 密钥与隔离的会话密钥匹配

如果你想要一个共享的“房间大脑”来代替，请设置：
```yaml
group_sessions_per_user: false
```

这将把群组/频道恢复为每个房间共享单个会话，这保留了共享的对话上下文，但也共享了 Token 成本、中断状态和上下文增长。

### 会话重置策略

消息网关会话会根据可配置的策略自动重置：

- **idle** — 在 N 分钟不活动后重置
- **daily** — 每天在特定小时重置
- **both** — 以先到者为准（空闲或每日）重置
- **none** — 永不自动重置

在会话自动重置之前，Agent 会获得一个回合来保存对话中任何重要的记忆或技能。

无论策略如何，具有**活动后台进程**的会话永远不会自动重置。

## 存储位置

| 内容 | 路径 | 描述 |
|------|------|-------------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话元数据 + 带有 FTS5 的消息 |
| 消息网关记录 | `~/.hermes/sessions/` | 每个会话的 JSONL 记录 + sessions.json 索引 |
| 消息网关索引 | `~/.hermes/sessions/sessions.json` | 将会话键映射到活动会话 ID |

SQLite 数据库使用 WAL 模式支持并发读取者和单个写入者，这非常适合消息网关的多平台架构。

### 数据库模式

`state.db` 中的关键表：

- **sessions** — 会话元数据（id、source、user_id、model、title、时间戳、Token 计数）。标题有唯一索引（允许 NULL 标题，只有非 NULL 标题必须唯一）。
- **messages** — 完整的消息历史记录（角色、内容、tool_calls、tool_name、token_count）
- **messages_fts** — 用于跨消息内容进行全文搜索的 FTS5 虚拟表

## 会话过期和清理

### 自动清理

- 消息网关会话根据配置的重置策略自动重置
- 重置前，Agent 会保存即将过期会话中的记忆和技能
- 已结束的会话会保留在数据库中，直到被清理

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
数据库增长缓慢（典型情况：数百个会话占用 10-15 MB）。清理主要用于删除不再需要用于搜索回忆的旧对话。
:::