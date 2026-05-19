---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 与 Telegram 集成，成为一个功能齐全的对话机器人。连接后，您可以从任何设备与您的 Agent 聊天、发送自动转录的语音备忘录、接收定时任务结果，并在群聊中使用该 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/) 构建，支持文本、语音、图片和文件附件。

## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API Token。

1.  打开 Telegram 并搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2.  发送 `/newbot`
3.  选择一个**显示名称**（例如，"Hermes Agent"）—— 可以是任何名称
4.  选择一个**用户名** —— 必须是唯一的，并以 `bot` 结尾（例如，`my_hermes_bot`）
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
| `/setabouttext` | 机器人个人资料页面上的简短文本 |
| `/setuserpic` | 为您的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否查看所有群组消息（见步骤 3） |

:::tip
对于 `/setcommands`，一个有用的初始命令集：

```
help - 显示帮助信息
new - 开始新的会话
sethome - 将此聊天设置为主频道
```
:::

## 步骤 3：隐私模式（群组使用关键）

Telegram 机器人有一个**隐私模式**，**默认是启用的**。这是在群组中使用机器人时最常见的困惑来源。

**隐私模式开启时**，您的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自身消息的回复
- 服务消息（成员加入/离开、置顶消息等）
- 机器人是管理员的频道中的消息

**隐私模式关闭时**，机器人会接收群组中的每条消息。

### 如何禁用隐私模式

1.  向 **@BotFather** 发送消息
2.  发送 `/mybots`
3.  选择您的机器人
4.  进入 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，您必须从任何群组中移除并重新添加机器人。** Telegram 在机器人加入群组时会缓存隐私状态，除非移除并重新添加机器人，否则不会更新。
:::

:::tip
禁用隐私模式的替代方案：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，始终会接收所有消息，这避免了需要切换全局隐私模式。
:::

## 步骤 4：查找您的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。您的用户 ID **不是**您的用户名 —— 它是一个像 `123456789` 这样的数字。

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

机器人应在几秒钟内上线。在 Telegram 上给它发送一条消息进行验证。

## 从基于 Docker 的终端发送生成的文件

如果您的终端后端是 `docker`，请注意，Telegram 附件是由**消息网关进程**发送的，而不是从容器内部发送的。这意味着最终的 `MEDIA:/...` 路径必须在运行消息网关的主机上可读。

常见的陷阱：

- Agent 在 Docker 内部将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt`
- Telegram 发送失败，因为 `/workspace/report.txt` 只存在于容器内部，而不在主机上

推荐模式：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

然后：

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中输出**主机可见**的路径，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果您已经有一个 `docker_volumes:` 部分，请将新的挂载添加到同一个列表中。YAML 中的重复键会静默覆盖较早的键。

### 支持的 `MEDIA:` 文件扩展名

消息网关从 Agent 回复中提取 `MEDIA:/path/to/file` 标签，并将引用的文件作为平台原生附件发送。所有消息网关平台支持的扩展名：

| 类别 | 扩展名 |
|---|---|
| 图片 | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| 音频 | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| 视频 | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **文档** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **办公软件** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **压缩包** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **电子书 / 安装包** | `epub`, `apk`, `ipa` |

此列表中的任何文件都会在支持它的平台（Telegram、Discord、Signal、Slack、WhatsApp、Feishu、Matrix 等）上作为原生附件发送；在不支持原生附件的平台上，它会回退到链接或纯文本指示器。**粗体**的类别是在最近几个版本中添加的 —— 如果您之前依赖模型说 `here is the file: /path/to/report.docx`，请改用 `MEDIA:/path/to/report.docx` 以实现原生发送。
## Webhook 模式

默认情况下，Hermes 使用**长轮询**连接到 Telegram —— 消息网关向 Telegram 的服务器发起出站请求以获取新更新。这对于本地和始终在线的部署效果很好。

对于**云部署**（Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在收到入站 HTTP 流量时自动唤醒挂起的机器，但不会因出站连接而唤醒。由于轮询是出站的，轮询模式的机器人永远无法休眠。Webhook 模式颠倒了方向 —— Telegram 将更新推送到你机器人的 HTTPS URL，从而支持空闲时休眠的部署。

| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 消息网关 → Telegram（出站） | Telegram → 消息网关（入站） |
| 最适合 | 本地、始终在线的服务器 | 支持自动唤醒的云平台 |
| 设置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可以在消息之间休眠 |

### 配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # 必需
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
```

| 变量 | 必需 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 将发送更新到的公开 HTTPS URL。URL 路径会自动提取（例如，从上面的示例中提取 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | Telegram 在每个 Webhook 请求中回显用于验证的密钥令牌。没有它，消息网关将拒绝启动 —— 参见 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，消息网关会启动一个 HTTP Webhook 服务器而不是轮询。当未设置时，使用轮询模式 —— 与之前版本的行为没有变化。

### 云部署示例（Fly.io）

1. 将环境变量添加到你的 Fly.io 应用密钥中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在你的 `fly.toml` 中暴露 Webhook 端口：

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

## 代理支持

如果 Telegram 的 API 被屏蔽，或者你需要通过代理路由流量，请设置 Telegram 专用的代理 URL。这优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

**选项 1：config.yaml（推荐）**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**选项 2：环境变量**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

支持的协议：`http://`、`https://`、`socks5://`。

该代理同时适用于主要的 Telegram 连接和备用 IP 传输。如果未设置 Telegram 专用代理，消息网关将回退到 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或 macOS 系统代理自动检测）。

## 主频道

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令将其指定为**主频道**。定时任务（cron 作业）将其结果发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群组聊天 ID 是负数（例如，`-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

### 话题模式下的定时任务投递

如果你在机器人私聊中启用了话题模式，投递到根聊天的定时任务消息会落在仅限系统的“大厅”中 —— 在那里回复不会打开会话，并且你会看到“主聊天保留给系统命令使用”的通知。创建一个专门的论坛话题（例如 `Cron`）并设置：

```bash
TELEGRAM_CRON_THREAD_ID=<话题线程ID>
```

`TELEGRAM_CRON_THREAD_ID` 仅对定时任务投递覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID`。在该话题中的回复会继续该话题现有的会话。

## 语音消息

### 接收语音（语音转文本）

你在 Telegram 上发送的语音消息会自动由 Hermes 配置的 STT 提供商转录，并作为文本注入到对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper` —— 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

#### 跳过 STT：将原始音频文件传递给 Agent

如果你更希望**Agent 本身**处理音频 —— 用于说话人分离、自定义转录工具，或者仅仅是存档录音 —— 在 `~/.hermes/config.yaml` 中设置 `stt.enabled: false`：

```yaml
stt:
  enabled: false
```

禁用 STT 后，消息网关仍会将语音/音频附件下载到 Hermes 的音频缓存中，但**不会转录它**。Agent 会收到一条带有如下标记的消息：

```
[用户发送了一条语音消息：/home/<用户>/.hermes/cache/audio/<哈希>.ogg]
```

然后，你的工具或技能可以直接读取该路径（例如，将其交给本地说话人分离流水线、更丰富的转录模型，或上传到长期存储）。文件扩展名反映了 Telegram 传递的原始格式（语音笔记为 `.ogg`，音频附件为 `.mp3`/`.m4a`/等）。

这自然与下面的[本地 Bot API 服务器](#large-files-20mb--via-local-bot-api-server)部分搭配使用，该部分将 Telegram 的 20MB getFile 上限提升到 2GB —— 当你想处理的录音超过几分钟时长时非常有用。

### 发送语音（文本转语音）

当 Agent 通过 TTS 生成音频时，它会以 Telegram 原生的**语音气泡**形式投递 —— 那种圆形的、可内联播放的类型。

- **OpenAI 和 ElevenLabs** 原生生成 Opus —— 无需额外设置
- **Edge TTS**（默认的免费提供商）输出 MP3，需要 **ffmpeg** 来转换为 Opus：
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有安装 ffmpeg，Edge TTS 音频会作为常规音频文件发送（仍然可以播放，但会使用矩形播放器而非语音气泡）。

在 `config.yaml` 文件的 `tts.provider` 键下配置 TTS 提供商。

## 通过本地 Bot API 服务器处理大文件（>20MB）

Telegram 的**公共** Bot API 将 `getFile` 下载限制在 **20 MB**，因此任何大于此限制的语音便签、音频文件、视频或文档都会被 Hermes 静默拒绝，并回复“文件过大”。解决此问题的文档化方法是运行一个**本地** [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) 守护进程——这是 Telegram 使用的相同服务器软件，但在你的网络上运行。本地服务器将文件上限提高到 **2 GB**，并且当 Hermes 检测到配置了自定义 `base_url` 时，会自动解除其内部限制。

这解锁了以下工作流：

- 向机器人发送长语音备忘录（45 分钟会议、播客）
- 上传大型视频用于视觉工具处理
- 归档原始音频用于离线流水线，如说话人分离、对齐或训练数据

### 步骤 1：获取 Telegram API 凭证

本地服务器直接与 Telegram 的 MTProto 层通信（而非公共 Bot API），因此需要 **MTProto 凭证**：

1. 访问 [my.telegram.org/apps](https://my.telegram.org/apps) 并使用你的 Telegram 账户登录。
2. 创建一个新应用程序（任何名称和简短描述均可）。
3. 复制 `api_id` 和 `api_hash`——两者都是必需的。

### 步骤 2：运行 telegram-bot-api 服务器

社区维护的 [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker 镜像是最简单的途径。一个最小的 `docker-compose.yaml`（使用 `--local` 模式以启用更高的限制）：

```yaml
services:
  tg-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: tg-bot-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"   # 仅绑定到环回地址；参见安全说明
    environment:
      TELEGRAM_API_ID: "12345"           # 来自步骤 1 的 api_id
      TELEGRAM_API_HASH: "abcdef..."     # 来自步骤 1 的 api_hash
      TELEGRAM_LOCAL: "1"                # 启用 --local 模式（将 20MB 提升至 2GB）
    volumes:
      - ./tg-bot-api-data:/var/lib/telegram-bot-api
```

启动它：

```bash
docker compose up -d tg-bot-api
docker logs --tail 20 tg-bot-api
```

:::warning 安全
本地 Bot API 服务器在 URL 路径中接收你的机器人令牌（例如 `/bot<TOKEN>/getMe`），**没有额外的身份验证**。任何能访问该端口的人都可以完全控制你的机器人——读取它能看到的每条消息、以其身份发送消息等。将容器绑定到 `127.0.0.1` 和/或在私有网络前放置反向代理。**切勿将端口 8081 暴露给公共互联网。**
:::

### 步骤 3：将机器人从公共 API 注销（一次性操作）

一个机器人一次只能在一个 Bot API 服务器上处于活动状态。如果你的机器人已经在 `api.telegram.org` 上运行（几乎肯定如此），你必须在本地服务器接受它之前，明确地将其从那里注销：

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# 预期响应：{"ok":true,"result":true}
```

这是一个一次性的迁移步骤——无需在每次重启时重复。Telegram 会将 `logOut` 之后收到的任何消息通过新服务器传递。

验证本地服务器可以代表机器人与 Telegram 通信：

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# 预期响应：{"ok":true,"result":{"id":...,"is_bot":true,...}}
```

### 步骤 4：将 Hermes 指向本地服务器

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra` 下添加 URL：

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # 参见下面的步骤 5——仅当机器人的数据目录
                              # 对 Hermes 进程可读时才设置此项
```

:::caution 使用 `platforms.telegram.extra`，而非 `telegram.extra`
目前只有 `platforms.<name>.extra` 形式会深度合并到平台配置中。直接放在顶级 `telegram.extra` 块下的键会被静默丢弃。
:::

当设置 `base_url` 时，Hermes 会：

- 针对本地服务器构建 python-telegram-bot 客户端
- 自动将其内部文档/音频大小限制从 20 MB 提升至 2 GB
- 在“文件过大”错误消息中报告活动限制（`Maximum: 2048 MB.`），以便清楚你处于哪种模式

重启消息网关并查找确认日志行：

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

### 步骤 5：`local_mode`——磁盘上的文件访问

本地服务器有**两种方式**来传递文件：

1. **不使用 `--local`**（默认）：文件通过 HTTP 在 `/file/bot<TOKEN>/<path>` 提供，与公共 Bot API 相同。20MB 的上限仍然有效。仅适用于网络修复（例如当 `api.telegram.org` 无法访问但你可以自托管时）；这不是你为了提升大小限制所需要的。
2. **使用 `--local`**（通过上面的 `TELEGRAM_LOCAL=1` 设置）：文件被写入服务器的文件系统，并且 `getFile` 响应返回一个**绝对路径**而非 HTTP URL。20MB 的上限被解除。然后 Hermes 必须**从磁盘**读取字节，而非通过 HTTP。

为了使磁盘读取路径正常工作，请在上面的配置中设置 `local_mode: true` **并**确保 Hermes 进程可以读取服务器返回的路径。两种场景：

- **同一台机器**——telegram-bot-api 和 Hermes 在同一主机上运行。将数据卷绑定挂载到 Hermes 可以读取的目录（例如 `/var/lib/telegram-bot-api`），并确保文件所有权匹配。容器会将其权限降级到其内部的 `telegram-bot-api` 用户（uid 因镜像而异）；最简单的修复方法是在 compose 服务中添加 `user: "<UID>:<GID>"`，使文件归 Hermes 已经运行的 uid 所有。
- **不同的机器**——机器人服务器运行在一台主机上（例如 NAS、单独的 VM），而 Hermes 运行在另一台上。服务器的数据目录必须与 Hermes 机器共享，且共享的**绝对路径**必须与服务器报告的路径相同（通常是 `/var/lib/telegram-bot-api`）。NFS 对此效果很好；如果你不想在文件系统级别处理 uid 不匹配，使用带有 `uid=` 挂载重新映射的 CIFS/SMB 会更友好。
如果设置了 `local_mode: true` 但 Hermes 无法 `stat` 返回的文件路径（权限问题或挂载错误），python-telegram-bot 会静默回退到向本地服务器发起 HTTP `getFile` 请求——在 `--local` 模式下，服务器会响应 `404 Not Found`。症状会在 `gateway.log` 中显示为：

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

如果你看到这个，说明容量限制解除功能正常，但文件共享功能异常。请以消息网关运行用户的身份，在 Hermes 主机上验证 `ls -la /var/lib/telegram-bot-api/<TOKEN>/voice/`，并确认单个文件可以通过 `cat` 命令读取且没有权限错误。

### 步骤 6：测试

向机器人发送一个大于 20 MB 的语音便签或音频文件。跟踪消息网关日志：

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

你应该能看到一行 `[Telegram] Cached user voice at /home/<user>/.hermes/cache/audio/...` 并且**没有**“太大”的拒绝信息。结合 `stt.enabled: false`（上文所述），原始音频文件的路径随后会进入 Agent 的入站消息中，供下游处理。

## 群聊使用

Hermes Agent 可以在 Telegram 群聊中工作，但需要注意以下几点：

- **隐私模式**决定了机器人能看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用——即使在群组中，也只有授权用户才能触发机器人
- 你可以通过设置 `telegram.require_mention: true` 来防止机器人响应普通的群聊闲聊
- 当 `telegram.require_mention: true` 时，群组消息在以下情况下会被接受：
  - 回复机器人消息
  - `@机器人用户名` 提及
  - `/命令@机器人用户名`（Telegram 包含机器人名称的机器人菜单命令形式）
  - 匹配你在 `telegram.mention_patterns` 中配置的正则表达式唤醒词
- 在拥有多个 Hermes 机器人的群组中，`telegram.exclusive_bot_mentions` 可以保持路由的确定性。当一条消息明确提及一个或多个 Telegram 机器人用户名时，只有被提及的机器人配置文件会处理它；其他 Hermes 机器人在回复和唤醒词回退逻辑运行之前会忽略它。此功能默认启用。
- 使用 `telegram.ignored_threads` 可以让 Hermes 在特定的 Telegram 论坛话题中保持静默，即使群组在其他情况下允许自由响应或提及触发的回复
- 如果 `telegram.require_mention` 未设置或设为 false，Hermes 将保持之前的开放群组行为，并响应它能看到的普通群组消息

### 一个群组中的多个 Hermes 机器人

如果你在同一个 Telegram 群组中运行多个 Hermes 配置文件，请为每个配置文件创建一个 Telegram 机器人令牌，并为每个配置文件启动一个消息网关。不要在多个运行中的消息网关中重复使用同一个机器人令牌；Telegram 会拒绝对同一令牌的并发轮询。

推荐的群组配置：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

在此设置下，像 `@research_bot @ops_bot summarize this` 这样的群组消息只会被 `research_bot` 和 `ops_bot` 处理。群组中的其他 Hermes 机器人将保持静默，即使该消息是对它们之前消息的回复，或者在其他情况下匹配了共享的唤醒词。

仅在需要旧版行为（即显式提及不应覆盖回复和唤醒词触发器）的遗留群组中，才设置 `exclusive_bot_mentions: false`。

要运行多个配置文件，请为每个配置文件运行一次消息网关命令。例如：

```bash
# 默认配置文件
hermes gateway start
hermes gateway status
hermes gateway stop

# 命名配置文件
hermes -p research gateway start
hermes -p research gateway status
hermes -p research gateway stop
```

对于小型固定集群，可以使用 shell 循环或脚本，为默认配置文件调用 `hermes gateway <action>`，并为每个命名配置文件调用 `hermes -p <profile> gateway <action>`。这比假设单个进程级命令可以控制每个服务管理器上的每个命名配置文件更可靠。

### 故障排除：私聊正常但群聊无效

如果机器人在私聊中响应但在群组中保持静默，请按顺序检查以下关卡：

1.  **Telegram 消息投递：** 关闭 BotFather 隐私模式，将机器人提升为管理员，或直接提及机器人。对于 Telegram 从未投递给机器人的群组消息，Hermes 无法响应。
2.  **更改隐私设置后重新加入：** 更改 BotFather 隐私设置后，将机器人从群组中移除并重新添加。Telegram 可能会为现有的群组成员关系保留旧的投递行为。
3.  **Hermes 授权：** 确保发送者列在 `TELEGRAM_ALLOWED_USERS` 或 `TELEGRAM_GROUP_ALLOWED_USERS` 中，或者通过 `TELEGRAM_GROUP_ALLOWED_CHATS` 允许该群聊。
4.  **提及过滤器：** 如果设置了 `telegram.require_mention: true`，普通的群聊闲聊将被忽略，除非消息是斜杠命令、回复机器人、`@机器人用户名` 提及，或者匹配配置的 `mention_patterns`。
5.  **多机器人路由：** 如果群组包含多个机器人，请确保每个 Hermes 配置文件使用唯一的机器人令牌，并保持 `exclusive_bot_mentions` 启用，除非你特意需要旧版的共享触发行为。

负数的聊天 ID 对于 Telegram 群组和超级群组是正常的。如果你使用聊天范围授权，请将这些 ID 放在 `TELEGRAM_GROUP_ALLOWED_CHATS` 中，而不是发送者用户白名单中。

### 群组触发配置示例

将此添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```

此示例允许所有通常的直接触发器，以及以 `chompy` 开头的消息，即使它们没有使用 `@提及`。
在提及和自由响应检查运行之前，Telegram 话题 `31` 和 `42` 中的消息总是被忽略。

### 关于 `mention_patterns` 的说明

-   模式使用 Python 正则表达式
-   匹配不区分大小写
-   模式会同时检查文本消息和媒体标题
-   无效的正则表达式模式会在消息网关日志中发出警告并被忽略，而不是导致机器人崩溃
-   如果你希望模式仅在消息开头匹配，请使用 `^` 锚定
## 私聊主题（Bot API 9.4）

Telegram Bot API 9.4（2026年2月）引入了**私聊主题**——机器人可以直接在1对1私聊中创建论坛式主题线程，无需超级群组。这让你可以在与 Hermes 的现有私聊中运行多个独立的工作空间。

### 使用场景

如果你同时处理多个长期项目，主题可以保持它们的上下文分离：

- **主题"网站"** —— 处理你的生产环境 Web 服务
- **主题"研究"** —— 文献综述和论文探索
- **主题"通用"** —— 杂项任务和快速问题

每个主题都有自己的会话、历史记录和上下文——与其他主题完全隔离。

### 配置

:::caution 前提条件
在配置中添加主题之前，用户必须**在与机器人的私聊中启用主题模式**：

1.  在 Telegram 中打开与 Hermes 机器人的私聊
2.  点击顶部的机器人名称打开聊天信息
3.  启用**主题**（将聊天切换为论坛的开关）

如果没有启用此设置，Hermes 将在启动时记录 `The chat is not a forum` 并跳过主题创建。这是 Telegram 客户端的设置——机器人无法以编程方式启用它。
:::

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra.dm_topics` 下添加主题：

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
          skill: arxiv              # 在此主题中自动加载一个技能
```

**字段说明：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 主题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 主题图标的自定义表情符号 ID |
| `skill` | 否 | 在此主题的新会话中自动加载的技能 |
| `thread_id` | 否 | 主题创建后自动填充——不要手动设置 |

### 工作原理

1.  在消息网关启动时，Hermes 会为每个尚未分配 `thread_id` 的主题调用 `createForumTopic`
2.  `thread_id` 会自动保存回 `config.yaml`——后续重启将跳过 API 调用
3.  每个主题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4.  每个主题中的消息都有自己的对话历史记录、记忆刷新和上下文窗口

### 根私聊处理

默认情况下，发送到根私聊（在任何主题之外）的消息会被正常处理。设置 `ignore_root_dm: true` 可以将根私聊变为一个大厅——对于配置了私聊主题的用户，普通消息会被静默忽略，而系统命令（`/start`、`/help`、`/status` 等）仍然有效。

```yaml
platforms:
  telegram:
    extra:
      ignore_root_dm: true
      dm_topics:
        - chat_id: 123456789
          topics:
            - name: General
```

此检查是**按聊天进行的**：只有 `dm_topics` 中至少有一条记录的用户，其根私聊才会受到影响。未配置主题的用户不受影响。

### 技能绑定

带有 `skill` 字段的主题会在该主题中启动新会话时自动加载该技能。这就像在对话开始时输入 `/skill-name` 一样——技能内容被注入到第一条消息中，后续消息会在对话历史记录中看到它。

例如，一个带有 `skill: arxiv` 的主题，每当其会话重置时（由于空闲超时、每日重置或手动 `/reset`），都会预加载 arxiv 技能。

:::tip
在配置之外创建的主题（例如，通过手动调用 Telegram API）会在收到 `forum_topic_created` 服务消息时自动被发现。你也可以在消息网关运行时将主题添加到配置中——它们会在下一次缓存未命中时被拾取。
:::

## 多会话私聊模式 (`/topic`)

一种 ChatGPT 风格的多会话私聊——一个机器人，多个并行对话。与上面由操作员策划的 `extra.dm_topics` 不同，此模式是**用户驱动的**：无需配置，无需预先声明的主题名称。最终用户通过 `/topic` 启用它，然后点击 Telegram 的 **+** 按钮创建任意数量的主题，每个主题都是一个完全独立的 Hermes 会话。

### `/topic` 子命令

| 形式 | 上下文 | 效果 |
|------|---------|--------|
| `/topic` | 根私聊，尚未启用 | 检查 BotFather 功能，启用多会话模式，创建置顶的系统主题 |
| `/topic` | 根私聊，已启用 | 显示状态：可恢复的未链接会话 |
| `/topic` | 在主题内部 | 显示当前主题的会话绑定 |
| `/topic help` | 任意 | 内联用法说明 |
| `/topic off` | 根私聊 | 禁用多会话模式并清除此聊天的所有主题绑定 |
| `/topic <session-id>` | 在主题内部 | 将之前的 Telegram 会话恢复到当前主题 |

只有授权用户（通过 `TELEGRAM_ALLOWED_USERS` / 平台认证配置允许列表）可以运行 `/topic`。未经授权的发送者会收到拒绝提示，而不是激活。

### 私聊主题 vs 多会话私聊模式

| | `extra.dm_topics`（配置驱动） | `/topic`（用户驱动） |
|---|---|---|
| 谁激活它 | 操作员，在 `config.yaml` 中 | 最终用户，通过发送 `/topic` |
| 主题列表 | 配置中声明的固定集合 | 用户自由创建/删除主题 |
| 主题名称 | 由操作员选择 | 由用户选择；自动重命名以匹配 Hermes 会话标题 |
| 根私聊行为 | 正常聊天（如果 `ignore_root_dm: true` 则为大厅） | 变为系统大厅（非命令消息被拒绝） |
| 主要用例 | 带有可选技能绑定的永久工作空间 | 临时并行会话 |
| 持久性 | 配置中的 `extra.dm_topics` | `telegram_dm_topic_mode` + `telegram_dm_topic_bindings` SQLite 表 |

这两个功能可以在同一个机器人上共存——你可以从用户的私聊运行 `/topic`，而 `extra.dm_topics` 继续为其他聊天管理操作员声明的主题。

### 前提条件

在 **@BotFather** 中，打开你的机器人 → **机器人设置 → 线程设置**：
1. 开启**主题模式**（启用 `has_topics_enabled`）
2. **不要**禁止用户创建主题（保持 `allows_users_to_create_topics` 开启）

当用户首次运行 `/topic` 时，Hermes 会调用 `getMe` 来验证这两个标志。如果任一标志未开启，Hermes 会发送 BotFather 主题设置页面的截图并解释需要切换哪些设置——在满足前提条件之前不会激活功能。

### 激活流程

在根私信中发送：

```
/topic
```

Hermes 将：

1. 检查 `getMe().has_topics_enabled` 和 `allows_users_to_create_topics`
2. 如果两者都为真，则为此私信启用多会话主题模式
3. 创建并置顶一个**系统**主题用于状态/命令（尽力而为）
4. 回复一个用户可以恢复的先前未链接的 Telegram 会话列表

激活后，**根私信成为一个大厅**：普通提示词将被拒绝，并引导用户指向**所有消息**。系统命令（`/status`、`/sessions`、`/usage`、`/help` 等）在根私信中仍然有效。

### 创建新主题（最终用户流程）

1. 在 Telegram 中打开机器人私信
2. 点击机器人界面顶部的**所有消息**，然后发送任何消息
3. Telegram 会为该消息创建一个新主题
4. Hermes 在该主题内回复——该主题现在是一个独立的会话

每个主题都有自己的对话历史、模型状态、工具执行和会话 ID。隔离键为 `agent:main:telegram:dm:{chat_id}:{thread_id}`——与配置驱动的私信主题隔离相同。

### 自动重命名主题

当 Hermes 为某个主题生成会话标题时（通过自动标题流水线，在第一次交互之后），Telegram 主题本身会被重命名以匹配——例如，“新主题”变为“数据库迁移计划”。重命名是尽力而为的：失败会被记录，但不会中断会话。

要禁用此功能并保持您手动选择的主题名称不变，请设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

当此标志开启时，Hermes 仍然会生成内部会话标题（供 `hermes sessions`、TUI 等使用），但从不编辑 Telegram 主题名称。当您在 BotFather 主题模式下手动组织主题，并且不希望每次首次回复都覆盖标题时，这很有用。

### 在主题内使用 `/new`

重置当前主题的会话（新的会话 ID，全新的历史记录），而不影响其他主题。Hermes 会回复一个提醒，说明对于并行工作，通常您需要的是创建另一个主题（通过**所有消息**）。

### 恢复先前的会话

在主题内发送：

```
/topic <session-id>
```

这将当前主题绑定到现有的 Hermes 会话，而不是重新开始。适用于继续在启用主题模式之前开始的对话。限制：

- 目标会话必须属于同一个 Telegram 用户
- 目标会话必须尚未绑定到另一个主题

Hermes 会确认会话标题并重播最后一条助手消息以提供上下文。

要发现会话 ID，请在根私信中发送 `/topic`（无参数）——Hermes 会列出用户未链接的 Telegram 会话。

### 在主题内使用 `/topic`（无参数）

显示当前主题的绑定信息：会话标题、会话 ID，以及关于 `/new` 与创建另一个主题的提示。

### 底层原理

- 激活状态持久化到 `state.db` 中的 `telegram_dm_topic_mode(chat_id, user_id, enabled, ...)`
- 每个主题绑定持久化到 `telegram_dm_topic_bindings(chat_id, thread_id, session_id, ...)`，并在 `session_id` 上设置 `ON DELETE CASCADE`——清理会话会自动清除其主题绑定
- 主题模式的 SQLite 迁移是**可选的**：它在首次调用 `/topic` 时运行，从不在消息网关启动时运行。在此配置文件中用户运行 `/topic` 之前，`state.db` 保持不变
- 每个传入的私信消息都会查找其 `(chat_id, thread_id)` 绑定。如果存在，查找会通过 `SessionStore.switch_session()` 将消息路由到绑定的会话，从而保持磁盘上会话键到会话 ID 的映射一致性
- 在主题内使用 `/new` 会重写绑定行以指向新的会话 ID，因此下一条消息会保持在新的会话上
- 在 `extra.dm_topics` 中声明的主题**永远不会自动重命名**——即使启用了多会话模式，操作员选择的名称也会被保留
- 设置 `extra.disable_topic_auto_rename: true` 以关闭聊天中**所有**主题的自动重命名（包括通过主题模式创建的临时主题）
- 在启用论坛功能的私信中，置顶的“常规”主题被视为根大厅，无论 Telegram 传递其消息时是否带有 `message_thread_id=1` 或没有 thread_id
- 根大厅提醒的速率限制为每聊天每 30 秒一条消息——忘记主题模式已开启并在根私信中输入十个提示词的用户不会收到十条回复
- BotFather 设置截图的速率限制为每聊天每 5 分钟发送一次——在主题设置仍被禁用时重复尝试 `/topic` 不会重新上传同一张图片
- 在主题内启动的 `/background <prompt>` 会将其结果发送回同一主题；后台会话不会触发所属主题的自动重命名
- `/topic` 本身受机器人的用户授权检查控制——未经授权的私信会收到拒绝信息，而不是激活功能

### 禁用多会话模式

在根私信中发送 `/topic off`。Hermes 会将对应行关闭，清除该聊天的 `(thread_id → session_id)` 绑定，并且根私信将恢复为正常的 Hermes 聊天。Telegram 中的现有主题不会被删除——它们只是不再被作为独立会话进行管理。稍后重新运行 `/topic` 可以重新开启。

如果您需要手动清理（例如，跨多个聊天进行批量重置），请直接删除行：

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0 WHERE chat_id = '<your_chat_id>'; \
   DELETE FROM telegram_dm_topic_bindings WHERE chat_id = '<your_chat_id>';"
```

### 降级 Hermes

如果您降级到早于 `/topic` 功能的 Hermes 版本，该功能将停止工作——`telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` 表仍保留在 `state.db` 中，但会被旧代码忽略。私信将恢复为原生的每线程隔离（每个 `message_thread_id` 仍然通过 `build_session_key` 获得自己的会话），因此您现有的 Telegram 主题将继续作为并行会话工作。根私信不再是大厅——那里的消息会像以前一样进入 Agent。重新升级会完全恢复之前的多会话模式。
## 群组论坛话题技能绑定

启用**话题模式**的超级群组（也称为“论坛话题”）已经实现了每个话题的会话隔离——每个 `thread_id` 对应其独立的对话。但你可能希望**在特定群组话题中收到消息时自动加载一个技能**，就像 DM 话题技能绑定的工作方式一样。

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
2.  如果匹配的条目有 `skill` 字段，则该技能会自动加载到会话中——与 DM 话题技能绑定完全相同
3.  没有 `skill` 键的话题仅获得会话隔离（现有行为，不变）
4.  未映射的 `thread_id` 值或 `chat_id` 值会静默跳过——不报错，不加载技能

### 与 DM 话题的差异

| | DM 话题 | 群组话题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 话题创建 | 如果 `thread_id` 缺失，Hermes 通过 API 创建话题 | 管理员在 Telegram UI 中创建话题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛话题已内置此功能） |

:::tip
要查找话题的 `thread_id`，请在 Telegram Web 或 Desktop 中打开该话题并查看 URL：`https://t.me/c/1234567890/5` —— 最后一个数字 (`5`) 就是 `thread_id`。超级群组的 `chat_id` 是群组 ID 加上 `-100` 前缀（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::

## 近期 Bot API 特性

- **Bot API 9.4 (2026年2月):** 私聊话题 —— 机器人可以通过 `createForumTopic` 在 1 对 1 DM 聊天中创建论坛话题。Hermes 将此用于两个不同的功能：由操作员策划的[私聊话题](#private-chat-topics-bot-api-94)（配置驱动，固定话题列表）和用户驱动的[多会话 DM 模式](#multi-session-dm-mode-topic)（通过 `/topic` 激活，用户可创建无限话题）。
- **隐私政策:** Telegram 现在要求机器人拥有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置，或者 Telegram 可能会自动生成一个占位符。如果你的机器人是面向公众的，这一点尤其重要。
- **Bot API 9.5 (2026年3月): 通过 `sendMessageDraft` 实现原生流式传输。** Hermes 支持 Telegram 的原生流式草稿 API，作为私聊的可选传输方式。默认方式仍然是传统的 `editMessageText` 路径，因为草稿预览在某些 Telegram 客户端上可能会明显折叠和重新渲染。

### 流式传输方式 (`gateway.streaming.transport`)

当启用流式传输时 (`gateway.streaming.enabled: true`)，Hermes 会选择以下四种传输方式之一：

| 值 | 行为 |
|---|---|
| `auto` | 在支持的聊天（当前为 Telegram DMs）上使用原生草稿流式传输；否则使用传统的基于编辑的路径。如果草稿帧失败，会优雅地回退。 |
| `draft` | 强制使用原生草稿。如果聊天不支持草稿（例如群组/话题），则记录降级并回退到编辑方式。 |
| `edit` (默认) | 对所有聊天类型都使用传统的渐进式 `editMessageText` 轮询。 |
| `off` | 完全禁用流式传输（仅最终回复，无渐进式更新）。 |

在 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  streaming:
    enabled: true
    transport: edit    # edit | auto | draft | off
```

**在 DM 中使用 `edit`（默认）你会看到什么** —— 消息网关发送一条普通的预览消息，并通过 `editMessageText` 逐步更新它，避免 Telegram 的草稿预览折叠/回滚效果。

**在 DM 中使用 `auto` 或 `draft` 你会看到什么** —— Telegram 显示一个逐 Token 更新的动画草稿预览。当回复完成时，它会作为一条常规消息发送，并且草稿预览会在客户端自然清除。草稿没有消息 ID，所以最终答案才是留在聊天历史记录中的内容。

**那群组、超级群组、论坛话题呢？** Telegram 将 `sendMessageDraft` 限制在私聊（DMs）中。消息网关会透明地回退到基于编辑的路径来处理其他所有情况——用户体验与之前相同。

**如果草稿帧失败怎么办？** 任何失败（瞬时网络错误、服务器端拒绝、较旧的 python-telegram-bot 安装）都会将该响应的其余部分切换回基于编辑的路径。下一次响应会重新尝试。

## 渲染：表格和链接预览

Telegram 的 MarkdownV2 没有原生的表格语法——如果原始传递，管道表格会渲染为反斜杠转义的乱码。Hermes 会自动规范化 Markdown 表格：

- **小型表格** 被扁平化为**行组项目符号** —— 每一行在列标题下变成一个可读的项目符号列表。适用于 2–4 列和短单元格。
- **较大或较宽的表格** 回退到带有对齐列的**围栏代码块**，这样就不会崩溃。会添加一行提示词，以便 Agent 知道在 Telegram 上更倾向于使用散文式的后续回复，而不是更多的表格。
无需配置——适配器会根据每条消息自动选择合适的回退方案。如果你想要传统的“始终使用代码块”行为，可以在 `config.yaml` 中设置 `telegram.pretty_tables: false` 来禁用表格规范化（默认值：`true`）。

**链接预览。** Telegram 会自动为机器人消息中的 URL 生成链接预览。如果你希望抑制这些预览（例如，过长的 `/tools` 输出、Agent 回复中提及了十个链接等）：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

启用后，Hermes 会为每条外发消息附加 Telegram 的 `LinkPreviewOptions(is_disabled=True)`，并在较旧的 `python-telegram-bot` 版本上回退到传统的 `disable_web_page_preview` 参数。

## 群组白名单

Telegram 群组和论坛聊天有两个独立的门控机制可以配置：

- **发送者用户 ID** (`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`) —— 仅适用于群组/论坛消息的发送者范围白名单。当你希望特定用户能够在群组中调用机器人，但又不将他们添加到 `TELEGRAM_ALLOWED_USERS`（这会同时授予他们私聊访问权限）时，使用此选项。
- **聊天 ID** (`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`) —— 聊天范围白名单。这些群组/论坛的任何成员都可以与机器人交互。适用于团队/支持机器人，其中群组成员身份本身就是访问信号。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 全局访问权限（私聊 + 群组）。这里的用户始终可以调用机器人。
        allow_from:
          - "123456789"
        # 仅在群组/论坛中允许的发送者 ID。不授予私聊访问权限。
        group_allow_from:
          - "987654321"
        # 整个群组/论坛 —— 任何成员都获得授权。
        group_allowed_chats:
          - "-1001234567890"
```

等效的环境变量：

```bash
TELEGRAM_ALLOWED_USERS="123456789"
TELEGRAM_GROUP_ALLOWED_USERS="987654321"
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

行为：

- `TELEGRAM_ALLOWED_USERS` 涵盖所有聊天类型（私聊、群组、论坛）。
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅在群组/论坛中授权列出的发送者。除非他们也在 `TELEGRAM_ALLOWED_USERS` 中列出，否则仍然无法私聊机器人。
- `TELEGRAM_GROUP_ALLOWED_CHATS` 中的聊天会授权该聊天的每个成员，无论发送者是谁。
- 在任何这些列表中使用 `*` 以允许任何发送者/聊天。
- 此机制层叠在现有的提及/模式触发器以及 `group_topics` + `ignored_threads` 之上。

### 从 PR #17686 之前迁移

在此拆分之前，`TELEGRAM_GROUP_ALLOWED_USERS` 是唯一的控制旋钮，用户在其中放置**聊天 ID**。为了向后兼容，`TELEGRAM_GROUP_ALLOWED_USERS` 中形状为聊天 ID（以 `-` 开头）的值仍会被视为聊天 ID，并且会记录一次弃用警告。迁移方法：

```bash
# 旧方式（仍然有效，但已弃用）
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# 新方式
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

## 斜杠命令访问控制

默认情况下，每个被允许的用户都可以运行每个斜杠命令。要将你的白名单拆分为**管理员**（拥有完整的斜杠命令访问权限）和**普通用户**（仅能运行你明确启用的命令），请在平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 现有的白名单（保持不变）
        allow_from:
          - "123456789"     # 管理员
          - "555555555"     # 普通用户
          - "777777777"     # 普通用户

        # 新增 —— 管理员获得所有斜杠命令（内置 + 插件）
        allow_admin_from:
          - "123456789"

        # 新增 —— 非管理员允许用户只能运行这些斜杠命令。
        # /help 和 /whoami 始终允许，以便用户可以查看其访问权限。
        user_allowed_commands:
          - status
          - model
          - history

        # 可选：为群组设置独立的管理员/命令列表
        group_allow_admin_from:
          - "123456789"
        group_user_allowed_commands:
          - status
```

**行为：**

- 在某个范围（私聊或群组）的 `allow_admin_from` 中列出的用户可以运行**每个**已注册的斜杠命令——包括内置命令和插件注册的命令——通过实时注册表。
- 在 `allow_from` 中但**不在** `allow_admin_from` 中的用户只能运行 `user_allowed_commands` 中列出的命令，加上始终允许的基础命令：`/help` 和 `/whoami`。
- 普通聊天（非斜杠消息）不受影响。非管理员用户仍然可以正常与 Agent 对话，只是不能触发任意命令。
- **向后兼容：** 如果某个范围未设置 `allow_admin_from`，则该范围的斜杠命令门控将被禁用。现有安装无需更改即可继续工作。
- 私聊管理员状态并不意味着群组管理员状态。每个范围都有自己的管理员列表。
- 如果只设置了 `group_allow_admin_from`，私聊范围将保持无限制（向后兼容）模式。

使用 `/whoami` 查看当前活动范围、你的层级（管理员 / 用户 / 无限制）以及你可以运行的斜杠命令。

## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1.  **提供商选择** —— 按钮显示每个可用的提供商及其模型数量（例如，“OpenAI (15)”、“✓ Anthropic (12)”表示当前提供商）。
2.  **模型选择** —— 分页的模型列表，带有 **Prev**/**Next** 导航、返回提供商的 **Back** 按钮以及 **Cancel**。

当前模型和提供商会显示在顶部。所有导航都通过原地编辑同一条消息完成（不会使聊天混乱）。

:::tip
如果你知道确切的模型名称，可以直接输入 `/model <name>` 来跳过选择器。你也可以输入 `/model <name> --global` 来跨会话持久化更改。
:::

## DNS-over-HTTPS 回退 IP

在某些受限网络中，`api.telegram.org` 可能解析到一个无法访问的 IP。Telegram 适配器包含一个**回退 IP** 机制，该机制会透明地重试连接到备用 IP，同时保留正确的 TLS 主机名和 SNI。
### 工作原理

1. 如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2. 否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的备用 IP。
3. DoH 返回的、与系统 DNS 结果不同的 IP 将被用作备用 IP。
4. 如果 DoH 也被屏蔽，则使用硬编码的种子 IP (`149.154.167.220`) 作为最后手段。
5. 一旦某个备用 IP 成功，它就会变得“粘性”——后续请求将直接使用它，而无需先重试主路径。

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
通常你不需要手动配置此项。通过 DoH 的自动发现机制可以处理大多数受限网络场景。只有在你的网络也屏蔽了 DoH 时，才需要设置 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 代理支持

如果你的网络需要通过 HTTP 代理才能访问互联网（在企业环境中很常见），Telegram 适配器会自动读取标准的代理环境变量，并通过该代理路由所有连接。

### 支持的变量

适配器按顺序检查以下环境变量，并使用第一个已设置的变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

### 配置

在启动消息网关之前，在你的环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或将其添加到 `~/.hermes/.env`：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理同时适用于主传输层和所有备用 IP 传输层。无需额外的 Hermes 配置——只要设置了环境变量，就会自动使用。

:::note
这涵盖了 Hermes 用于 Telegram 连接的自定义备用传输层。其他地方使用的标准 `httpx` 客户端本身已经支持代理环境变量。
:::

## 消息反应

机器人可以给消息添加表情符号反应，作为视觉处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果在处理过程中发生错误

反应功能**默认禁用**。在 `config.yaml` 中启用：

```yaml
telegram:
  reactions: true
```

或通过环境变量启用：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是叠加的）不同，Telegram 的 Bot API 在一次调用中会替换机器人的所有反应。从 👀 到 ✅/❌ 的转换是原子性的——你不会同时看到两者。
:::

:::tip
如果机器人在群组中没有添加反应的权限，反应调用会静默失败，消息处理会正常继续。
:::

## 按频道提示词

为特定的 Telegram 群组或论坛主题分配临时的系统提示词。该提示词在每次对话轮次运行时注入——永远不会持久化到对话历史记录中——因此更改会立即生效。

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      你是一个研究助手。专注于学术来源、引用和简洁的综述。
    "42":  |
      这个主题用于创意写作反馈。请保持热情并提供建设性意见。
```

键是聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级别的提示词会覆盖群组级别的提示词：

- 在群组 `-1001234567890` 内的主题 `42` 中的消息 → 使用主题 `42` 的提示词
- 在主题 `99`（没有显式条目）中的消息 → 回退到群组 `-1001234567890` 的提示词
- 在没有条目的群组中的消息 → 不应用频道提示词

数字形式的 YAML 键会自动规范化为字符串。

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全不响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| 机器人响应“未授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。使用 @userinfobot 仔细核对。 |
| 机器人忽略群组消息 | 隐私模式可能已开启。禁用它（步骤 3）或让机器人成为群组管理员。**更改隐私设置后，记得移除并重新添加机器人。** |
| 语音消息未转录 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件，不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| 机器人 Token 被撤销/无效 | 通过 BotFather 中的 `/revoke` 然后 `/newbot` 或 `/token` 生成新的 Token。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可公开访问（用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量路由到由 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（它们不需要是相同的数字）。确保 SSL/TLS 处于活动状态——Telegram 只发送到 HTTPS URL。检查防火墙规则。 |

## 执行批准

当 Agent 尝试运行可能危险的命令时，它会在聊天中向你请求批准：

> ⚠️ 此命令可能危险（递归删除）。回复“yes”以批准。

回复“yes”/“y”批准，或回复“no”/“n”拒绝。

## 交互式提示（澄清）

当 Agent 调用 `clarify` 工具时——询问你更喜欢哪种方法、获取任务后反馈或在做出重要决定前确认——Telegram 会使用**内联键盘按钮**呈现问题：

> ❓ 我应该为仪表板使用哪个框架？
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ 其他（输入答案）]

点击按钮进行回答，或点击**其他**以输入自由格式的响应（你发送的下一条消息将成为答案）。开放式的 `clarify` 调用（没有预设选项）会跳过按钮，只捕获你的下一条消息。

通过 `~/.hermes/config.yaml` 中的 `agent.clarify_timeout` 配置响应超时（默认为 `600` 秒）。如果你在超时时间内没有响应，Agent 会使用一个哨兵消息解除阻塞并进行调整，而不是一直等待。
## 安全

:::warning
务必设置 `TELEGRAM_ALLOWED_USERS` 以限制可以与你的机器人交互的用户。如果不设置，作为安全措施，消息网关默认会拒绝所有用户。
:::

切勿公开分享你的机器人令牌。如果令牌泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。

更多详细信息，请参阅[安全文档](/user-guide/security)。你也可以使用[私聊配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更动态的用户授权方式。