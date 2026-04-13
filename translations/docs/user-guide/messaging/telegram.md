---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 与 Telegram 集成，成为一个功能齐全的对话机器人。连接后，您可以从任何设备与您的 Agent 聊天、发送自动转录的语音备忘录、接收定时任务结果，并在群聊中使用该 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API Token。

1.  打开 Telegram 并搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2.  发送 `/newbot`
3.  选择一个**显示名称**（例如，"Hermes Agent"）—— 可以是任何名称
4.  选择一个**用户名** —— 必须是唯一的并以 `bot` 结尾（例如，`my_hermes_bot`）
5.  BotFather 会回复您的 **API Token**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请妥善保管您的机器人 Token。任何拥有此 Token 的人都可以控制您的机器人。如果泄露，请立即通过 BotFather 中的 `/revoke` 命令撤销它。
:::

## 步骤 2：自定义您的机器人（可选）

这些 BotFather 命令可以改善用户体验。向 @BotFather 发送消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的"这个机器人能做什么？"文本 |
| `/setabouttext` | 机器人资料页面上的简短文本 |
| `/setuserpic` | 为您的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否查看所有群组消息（见步骤 3） |

:::tip
对于 `/setcommands`，一个有用的初始集合：

```
help - 显示帮助信息
new - 开始新的对话
sethome - 将此聊天设置为家庭频道
```
:::

## 步骤 3：隐私模式（对群组至关重要）

Telegram 机器人有一个**默认启用的隐私模式**。这是在群组中使用机器人时最常见的困惑来源。

**隐私模式开启时**，您的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自身消息的消息
- 服务消息（成员加入/离开、置顶消息等）
- 机器人是管理员的频道中的消息

**隐私模式关闭时**，机器人会接收群组中的每条消息。

### 如何禁用隐私模式

1.  向 **@BotFather** 发送消息
2.  发送 `/mybots`
3.  选择您的机器人
4.  转到 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，您必须从任何群组中移除并重新添加机器人**。Telegram 在机器人加入群组时会缓存隐私状态，除非移除并重新添加机器人，否则不会更新。
:::

:::tip
禁用隐私模式的替代方法：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，始终会接收所有消息，这避免了需要切换全局隐私模式。
:::

## 步骤 4：查找您的用户 ID

Hermes Agent 使用数字 Telegram 用户 ID 来控制访问。您的用户 ID **不是**您的用户名 —— 它是一个像 `123456789` 这样的数字。

**方法 1（推荐）：** 向 [@userinfobot](https://t.me/userinfobot) 发送消息 —— 它会立即回复您的用户 ID。

**方法 2：** 向 [@get_id_bot](https://t.me/get_id_bot) 发送消息 —— 另一个可靠的选择。

保存这个数字；下一步您会需要它。

## 步骤 5：配置 Hermes

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

出现提示时选择 **Telegram**。向导会询问您的机器人 Token 和允许的用户 ID，然后为您写入配置。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

### 启动消息网关

```bash
hermes gateway
```

机器人应在几秒钟内上线。在 Telegram 上发送消息以进行验证。

## Webhook 模式

默认情况下，Hermes 使用**长轮询**连接到 Telegram —— 消息网关向 Telegram 服务器发出出站请求以获取新更新。这对于本地和始终在线的部署效果很好。

对于**云部署**（Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在入站 HTTP 流量时自动唤醒挂起的机器，但不能在出站连接时唤醒。由于轮询是出站的，轮询机器人永远无法休眠。Webhook 模式翻转了方向 —— Telegram 将更新推送到您机器人的 HTTPS URL，从而支持空闲时休眠的部署。

| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 消息网关 → Telegram（出站） | Telegram → 消息网关（入站） |
| 最适合 | 本地、始终在线的服务器 | 具有自动唤醒功能的云平台 |
| 设置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可以在消息之间休眠 |

### 配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
# TELEGRAM_WEBHOOK_SECRET=mysecret  # 可选，推荐
```

| 变量 | 必需 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 将发送更新的公共 HTTPS URL。URL 路径会自动提取（例如，从上面的示例中提取 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | 否 | 用于验证更新是否确实来自 Telegram 的密钥 Token。**强烈建议**用于生产部署。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，消息网关会启动一个 HTTP webhook 服务器而不是轮询。当未设置时，使用轮询模式 —— 与之前版本的行为没有变化。

### 云部署示例（Fly.io）

1.  将环境变量添加到您的 Fly.io 应用密钥中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```
2. 在 `fly.toml` 中暴露 webhook 端口：

```toml
[[services]]
  internal_port = 8443
  protocol = "tcp"

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

3. 部署：

```bash
fly deploy
```

消息网关日志应显示：`[telegram] Connected to Telegram (webhook mode)`。

## 主频道

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令，将其指定为**主频道**。定时任务（cron 作业）会将结果发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::tip
群组聊天 ID 是负数（例如 `-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

## 语音消息

### 接收语音（语音转文本）

你在 Telegram 上发送的语音消息会被 Hermes 配置的 STT 提供商自动转录，并以文本形式注入到对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper` — 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

### 发送语音（文本转语音）

当 Agent 通过 TTS 生成音频时，它会以 Telegram 原生的**语音气泡**形式发送 — 即圆形、可内联播放的那种。

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式 — 无需额外设置
- **Edge TTS**（默认的免费提供商）输出 MP3，需要 **ffmpeg** 来转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有 ffmpeg，Edge TTS 音频将作为普通音频文件发送（仍然可播放，但使用矩形播放器而不是语音气泡）。

在你的 `config.yaml` 中的 `tts.provider` 键下配置 TTS 提供商。

## 群组聊天使用

Hermes Agent 可以在 Telegram 群组聊天中工作，但需要注意以下几点：

- **隐私模式**决定了机器人可以看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用 — 即使在群组中，也只有授权用户可以触发机器人
- 你可以通过 `telegram.require_mention: true` 来防止机器人响应普通的群组闲聊
- 当 `telegram.require_mention: true` 时，群组消息在以下情况下会被接受：
  - 斜杠命令
  - 回复机器人消息
  - `@机器人用户名` 提及
  - 匹配你在 `telegram.mention_patterns` 中配置的正则表达式唤醒词
- 如果 `telegram.require_mention` 未设置或为 false，Hermes 将保持之前的开放群组行为，并响应它能看到的普通群组消息

### 群组触发配置示例

将此添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
```

此示例允许所有通常的直接触发方式，以及以 `chompy` 开头的消息，即使它们没有使用 `@提及`。

### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时检查文本消息和媒体标题
- 无效的正则表达式模式会被忽略，并在消息网关日志中发出警告，而不是导致机器人崩溃
- 如果你希望模式仅匹配消息开头，请使用 `^` 锚定

## 私聊话题（Bot API 9.4）

Telegram Bot API 9.4（2026 年 2 月）引入了**私聊话题** — 机器人可以直接在 1 对 1 私聊中创建论坛式话题线程，无需超级群组。这让你可以在与 Hermes 的现有私聊中运行多个隔离的工作空间。

### 使用场景

如果你同时处理多个长期运行的项目，话题可以保持它们的上下文分离：

- **话题 "网站"** — 处理你的生产 Web 服务
- **话题 "研究"** — 文献综述和论文探索
- **话题 "通用"** — 杂项任务和快速问题

每个话题都有自己的会话、历史和上下文 — 与其他话题完全隔离。

### 配置

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra.dm_topics` 下添加话题：

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: 123456789        # 你的 Telegram 用户 ID
        topics:
        - name: General
          icon_color: 7322096
        - name: Website
          icon_color: 9367192
        - name: Research
          icon_color: 16766590
          skill: arxiv              # 在此话题中自动加载一个技能
```

**字段：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情符号 ID |
| `skill` | 否 | 在此话题中启动新会话时自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充 — 不要手动设置 |

### 工作原理

1. 在消息网关启动时，Hermes 会为每个尚未分配 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml` — 后续重启将跳过 API 调用
3. 每个话题映射到一个隔离的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题中的消息都有自己的对话历史、记忆刷新和上下文窗口

### 技能绑定

带有 `skill` 字段的话题会在该话题中启动新会话时自动加载该技能。这就像在对话开始时输入 `/skill-name` 一样 — 技能内容被注入到第一条消息中，后续消息会在对话历史中看到它。

例如，一个带有 `skill: arxiv` 的话题，每当其会话重置时（由于空闲超时、每日重置或手动 `/reset`），都会预加载 arxiv 技能。

:::tip
在配置之外创建的话题（例如，通过手动调用 Telegram API）会在收到 `forum_topic_created` 服务消息时自动被发现。你也可以在消息网关运行时将话题添加到配置中 — 它们会在下一次缓存未命中时被拾取。
:::
## 群组论坛话题技能绑定

启用**话题模式**的超级群组（也称为“论坛话题”）已经实现了按话题的会话隔离——每个 `thread_id` 对应其独立的对话。但你可能希望在特定群组话题中收到消息时**自动加载一个技能**，就像私聊话题技能绑定的工作方式一样。

### 使用场景

一个为不同工作流设置了论坛话题的团队超级群组：

- **工程**话题 → 自动加载 `software-development` 技能
- **研究**话题 → 自动加载 `arxiv` 技能
- **通用**话题 → 无技能，通用助手

### 配置

在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra.group_topics` 下添加话题绑定：

```yaml
platforms:
  telegram:
    extra:
      group_topics:
      - chat_id: -1001234567890       # 超级群组 ID
        topics:
        - name: Engineering
          thread_id: 5
          skill: software-development
        - name: Research
          thread_id: 12
          skill: arxiv
        - name: General
          thread_id: 1
          # 无技能 — 通用目的
```

**字段说明：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 话题的人类可读标签（仅用于信息展示） |
| `thread_id` | 是 | Telegram 论坛话题 ID — 在 `t.me/c/<group_id>/<thread_id>` 链接中可见 |
| `skill` | 否 | 在此话题的新会话中自动加载的技能 |

### 工作原理

1.  当消息到达已映射的群组话题时，Hermes 会在 `group_topics` 配置中查找匹配的 `chat_id` 和 `thread_id`
2.  如果匹配的条目有 `skill` 字段，则该技能会自动加载到会话中——与私聊话题技能绑定完全相同
3.  没有 `skill` 键的话题仅获得会话隔离（现有行为，保持不变）
4.  未映射的 `thread_id` 值或 `chat_id` 值会静默跳过——不报错，不加载技能

### 与私聊话题的差异

| | 私聊话题 | 群组话题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 话题创建 | 如果 `thread_id` 缺失，Hermes 通过 API 创建话题 | 管理员在 Telegram UI 中创建话题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛话题已内置此功能） |

:::tip
要查找话题的 `thread_id`，请在 Telegram Web 或 Desktop 中打开该话题并查看 URL：`https://t.me/c/1234567890/5` —— 最后一个数字（`5`）就是 `thread_id`。超级群组的 `chat_id` 是群组 ID 加上前缀 `-100`（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::

## 近期 Bot API 功能

- **Bot API 9.4 (2026年2月):** 私聊话题 —— 机器人可以通过 `createForumTopic` 在 1 对 1 私聊中创建论坛话题。请参阅上文的[私聊话题](#private-chat-topics-bot-api-94)。
- **隐私政策:** Telegram 现在要求机器人拥有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置，或者 Telegram 可能会自动生成一个占位符。如果你的机器人是面向公众的，这一点尤其重要。
- **消息流式传输:** Bot API 9.x 增加了对长响应流式传输的支持，这可以改善长篇幅 Agent 回复的感知延迟。

## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘用于切换模型：

1.  **提供商选择** —— 显示每个可用提供商及其模型数量的按钮（例如，“OpenAI (15)”、“✓ Anthropic (12)”表示当前提供商）。
2.  **模型选择** —— 分页显示的模型列表，带有 **Prev**/**Next** 导航、一个返回提供商的 **Back** 按钮以及 **Cancel**。

当前模型和提供商显示在顶部。所有导航都通过原地编辑同一条消息完成（不会弄乱聊天记录）。

:::tip
如果你知道确切的模型名称，可以直接输入 `/model <name>` 来跳过选择器。你也可以输入 `/model <name> --global` 来使更改在所有会话中持久生效。
:::

## Webhook 模式

默认情况下，Telegram 适配器通过**长轮询**连接——消息网关向 Telegram 的服务器发起出站连接。这种方式在任何地方都有效，但会保持一个持久连接。

**Webhook 模式**是一种替代方案，Telegram 通过 HTTPS 将更新推送到你的服务器。这对于**无服务器和云部署**（Fly.io, Railway 等）非常理想，因为入站 HTTP 请求可以唤醒挂起的机器。

### 配置

设置 `TELEGRAM_WEBHOOK_URL` 环境变量以启用 webhook 模式：

```bash
# 必需 — 你的公共 HTTPS 端点
TELEGRAM_WEBHOOK_URL=https://app.fly.dev/telegram

# 可选 — 本地监听端口（默认：8443）
TELEGRAM_WEBHOOK_PORT=8443

# 可选 — 用于更新验证的密钥令牌（如果未设置则自动生成）
TELEGRAM_WEBHOOK_SECRET=my-secret-token
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
telegram:
  webhook_mode: true
```

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动一个 HTTP 服务器，监听 `0.0.0.0:<port>`，并向 Telegram 注册 webhook URL。URL 路径从 webhook URL 中提取（默认为 `/telegram`）。

:::warning
Telegram 要求 webhook 端点具有**有效的 TLS 证书**。自签名证书将被拒绝。请使用反向代理（nginx, Caddy）或提供 TLS 终止的平台（Fly.io, Railway, Cloudflare Tunnel）。
:::

## DNS-over-HTTPS 备用 IP

在某些受限网络中，`api.telegram.org` 可能解析到一个无法访问的 IP。Telegram 适配器包含一个**备用 IP** 机制，该机制会透明地重试连接到备用 IP，同时保留正确的 TLS 主机名和 SNI。

### 工作原理

1.  如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2.  否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的备用 IP。
3.  DoH 返回的、与系统 DNS 结果不同的 IP 将用作备用 IP。
4.  如果 DoH 也被阻止，则使用一个硬编码的种子 IP (`149.154.167.220`) 作为最后手段。
5.  一旦某个备用 IP 成功，它就会变得“粘性”——后续请求直接使用它，而无需先重试主路径。
### 配置

```bash
# 显式指定备用 IP（逗号分隔）
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

或在 `~/.hermes/config.yaml` 中配置：

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::tip
通常你不需要手动配置此项。通过 DoH 的自动发现功能可以处理大多数受限制网络场景。只有在你的网络也屏蔽了 DoH 时，才需要设置 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 代理支持

如果你的网络需要通过 HTTP 代理才能访问互联网（在企业环境中很常见），Telegram 适配器会自动读取标准的代理环境变量，并通过代理路由所有连接。

### 支持的变量

适配器按顺序检查以下环境变量，并使用第一个已设置的变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

### 配置

在启动消息网关前，在你的环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或将其添加到 `~/.hermes/.env`：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理同时适用于主传输层和所有备用 IP 传输层。无需额外的 Hermes 配置 —— 只要设置了环境变量，就会自动使用。

:::note
这涵盖了 Hermes 用于 Telegram 连接的自定义备用传输层。其他地方使用的标准 `httpx` 客户端本身已原生支持代理环境变量。
:::

## 消息反应

机器人可以给消息添加表情符号反应，作为视觉处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果在处理过程中发生错误

反应功能**默认是禁用的**。在 `config.yaml` 中启用：

```yaml
telegram:
  reactions: true
```

或通过环境变量启用：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是叠加的）不同，Telegram 的 Bot API 在一次调用中会替换机器人的所有反应。从 👀 到 ✅/❌ 的转换是原子性的 —— 你不会同时看到两者。
:::

:::tip
如果机器人在群组中没有添加反应的权限，反应调用会静默失败，消息处理会正常继续。
:::

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全不响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| 机器人响应“未授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。请使用 @userinfobot 仔细核对。 |
| 机器人忽略群组消息 | 隐私模式很可能已开启。请禁用它（步骤 3）或将机器人设为群组管理员。**更改隐私设置后，记得移除并重新添加机器人。** |
| 语音消息未转录 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件，不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| 机器人 Token 被撤销/无效 | 通过 BotFather 的 `/revoke` 然后 `/newbot` 或 `/token` 命令生成新的 Token。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可公开访问（用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量路由到由 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（它们不需要是相同的数字）。确保 SSL/TLS 已启用 —— Telegram 只向 HTTPS URL 发送数据。检查防火墙规则。 |

## 执行批准

当 Agent 尝试运行一个潜在危险的命令时，它会在聊天中向你请求批准：

> ⚠️ 此命令可能具有危险性（递归删除）。回复 "yes" 以批准。

回复 "yes"/"y" 批准，或回复 "no"/"n" 拒绝。

## 安全

:::warning
务必设置 `TELEGRAM_ALLOWED_USERS` 以限制谁可以与你的机器人交互。如果不设置，作为安全措施，消息网关默认会拒绝所有用户。
:::

切勿公开分享你的机器人 Token。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。

更多详细信息，请参阅[安全文档](/user-guide/security)。你也可以使用[私信配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更动态的用户授权方式。