---
sidebar_position: 11
title: "飞书 / Lark"
description: "将 Hermes Agent 设置为飞书或 Lark 机器人"
---

# 飞书 / Lark 设置

Hermes Agent 可作为功能齐全的机器人集成到飞书和 Lark 中。连接后，您可以在私聊或群聊中与 Agent 对话，在家庭聊天中接收定时任务结果，并通过常规的消息网关流程发送文本、图片、音频和文件附件。

该集成支持两种连接模式：

- `websocket` — 推荐；Hermes 建立出站连接，您无需公开的 webhook 端点
- `webhook` — 当您希望飞书/Lark 通过 HTTP 向您的网关推送事件时很有用

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| 私聊 | Hermes 响应每条消息。 |
| 群聊 | Hermes 仅在聊天中被 @提及 时响应。 |
| 共享群聊 | 默认情况下，在共享聊天中，每个用户的会话历史是隔离的。 |

这种共享聊天的行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅在您明确希望每个聊天共享一个会话时，才将其设置为 `false`。

## 步骤 1：创建飞书 / Lark 应用

### 推荐：扫码创建（一条命令）

```bash
hermes gateway setup
```

选择 **飞书 / Lark** 并使用您的飞书或 Lark 手机应用扫描二维码。Hermes 将自动创建一个具有正确权限的机器人应用并保存凭证。

### 备选：手动设置

如果扫码创建不可用，向导将回退到手动输入：

1. 打开飞书或 Lark 开发者控制台：
   - 飞书：[https://open.feishu.cn/](https://open.feishu.cn/)
   - Lark：[https://open.larksuite.com/](https://open.larksuite.com/)
2. 创建一个新应用。
3. 在 **凭证与基础信息** 中，复制 **App ID** 和 **App Secret**。
4. 为应用启用 **机器人** 能力。
5. 运行 `hermes gateway setup`，选择 **飞书 / Lark**，并在提示时输入凭证。

:::warning
请妥善保管 App Secret。任何拥有它的人都可以冒充您的应用。
:::

## 步骤 2：选择连接模式

### 推荐：WebSocket 模式

当 Hermes 在您的笔记本电脑、工作站或私有服务器上运行时，使用 WebSocket 模式。无需公开 URL。官方的 Lark SDK 会建立并维护一个持久的出站 WebSocket 连接，并自动重连。

```bash
FEISHU_CONNECTION_MODE=websocket
```

**要求：** 必须安装 `websockets` Python 包。SDK 内部处理连接生命周期、心跳和自动重连。

**工作原理：** 适配器在后台执行器线程中运行 Lark SDK 的 WebSocket 客户端。入站事件（消息、回应、卡片操作）被分派到主 asyncio 循环。断开连接时，SDK 会自动尝试重连。

### 可选：Webhook 模式

仅当您已经在可访问的 HTTP 端点后运行 Hermes 时，才使用 webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 webhook 模式下，Hermes 启动一个 HTTP 服务器（通过 `aiohttp`）并在以下路径提供飞书端点：

```text
/feishu/webhook
```

**要求：** 必须安装 `aiohttp` Python 包。

您可以自定义 webhook 服务器的绑定地址和路径：

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1   # 默认：127.0.0.1
FEISHU_WEBHOOK_PORT=8765         # 默认：8765
FEISHU_WEBHOOK_PATH=/feishu/webhook  # 默认：/feishu/webhook
```

当飞书发送 URL 验证挑战（`type: url_verification`）时，webhook 会自动响应，以便您可以在飞书开发者控制台中完成订阅设置。

## 步骤 3：配置 Hermes

### 选项 A：交互式设置

```bash
hermes gateway setup
```

选择 **飞书 / Lark** 并填写提示信息。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# 可选但强烈推荐
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 接受：

- `feishu` 用于飞书中国版
- `lark` 用于 Lark 国际版

## 步骤 4：启动消息网关

```bash
hermes gateway
```

然后从飞书/Lark 向机器人发送消息以确认连接已激活。

## 家庭聊天

在飞书/Lark 聊天中使用 `/set-home` 将其标记为家庭频道，用于接收定时任务结果和跨平台通知。

您也可以预先配置它：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

## 安全

### 用户白名单

在生产环境中，请设置飞书 Open ID 的白名单：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果您将白名单留空，任何能接触到该机器人的用户都可能使用它。在群聊中，消息处理前会检查发送者的 open_id 是否在白名单中。

### Webhook 加密密钥

在 webhook 模式下运行时，设置一个加密密钥以启用入站 webhook 负载的签名验证：

```bash
FEISHU_ENCRYPT_KEY=your-encrypt-key
```

此密钥可在您飞书应用配置的 **事件订阅** 部分找到。设置后，适配器会使用以下签名算法验证每个 webhook 请求：

```
SHA256(timestamp + nonce + encrypt_key + body)
```

计算出的哈希值会与 `x-lark-signature` 头部使用时序安全比较进行比对。签名无效或缺失的请求将被拒绝，并返回 HTTP 401。

:::tip
在 WebSocket 模式下，签名验证由 SDK 自身处理，因此 `FEISHU_ENCRYPT_KEY` 是可选的。在 webhook 模式下，强烈建议在生产环境中使用。
:::

### 验证 Token

一个额外的身份验证层，用于检查 webhook 负载内部的 `token` 字段：

```bash
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

此 token 同样可在您飞书应用配置的 **事件订阅** 部分找到。设置后，每个入站 webhook 负载的 `header` 对象中必须包含匹配的 `token`。不匹配的 token 将被拒绝，并返回 HTTP 401。

`FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` 可以一起使用，以实现深度防御。
## 群消息策略

`FEISHU_GROUP_POLICY` 环境变量控制 Hermes 在群聊中是否以及如何响应：

```bash
FEISHU_GROUP_POLICY=allowlist   # 默认值
```

| 值 | 行为 |
|-------|----------|
| `open` | Hermes 响应任何群中任何用户的 @ 提及。 |
| `allowlist` | Hermes 仅响应 `FEISHU_ALLOWED_USERS` 中列出的用户的 @ 提及。 |
| `disabled` | Hermes 完全忽略所有群消息。 |

在所有模式下，消息在被处理之前，必须在群中明确 @ 提及该机器人（或 @all）。私聊消息绕过此限制。

### 用于 @ 提及检测的机器人身份

为了在群聊中精确检测 @ 提及，适配器需要知道机器人的身份。可以显式提供：

```bash
FEISHU_BOT_OPEN_ID=ou_xxx
FEISHU_BOT_USER_ID=xxx
FEISHU_BOT_NAME=MyBot
```

如果未设置任何一项，适配器将在启动时尝试通过应用信息 API 自动发现机器人名称。为此，需要授予 `admin:app.info:readonly` 或 `application:application:self_manage` 权限范围。

## 交互式卡片操作

当用户点击机器人发送的交互式卡片上的按钮或进行交互时，适配器会将这些事件作为合成的 `/card` 命令事件进行路由：

- 按钮点击变为：`/card button {"key": "value", ...}`
- 卡片定义中操作的 `value` 负载作为 JSON 包含在内。
- 卡片操作会进行去重，窗口期为 15 分钟，以防止重复处理。

卡片操作事件以 `MessageType.COMMAND` 类型分发，因此它们会流经正常的命令处理流水线。

**命令审批**也是通过这种方式工作的——当 Agent 需要运行危险命令时，它会发送一个带有“允许一次”/“会话内允许”/“始终允许”/“拒绝”按钮的交互式卡片。用户点击按钮后，卡片操作回调将审批决定传回给 Agent。

### 必需的飞书应用配置

交互式卡片需要在飞书开发者控制台进行**三个**配置步骤。缺少任何一项都会导致用户点击卡片按钮时出现错误 **200340**。

1.  **订阅卡片操作事件：**
    在**事件订阅**中，将 `card.action.trigger` 添加到您的已订阅事件中。

2.  **启用交互式卡片功能：**
    在**应用功能 > 机器人**中，确保**交互式卡片**开关已启用。这告诉飞书您的应用可以接收卡片操作回调。

3.  **配置卡片请求 URL（仅限 Webhook 模式）：**
    在**应用功能 > 机器人 > 消息卡片请求 URL** 中，将 URL 设置为与您的事件 Webhook 相同的端点（例如 `https://your-server:8765/feishu/webhook`）。在 WebSocket 模式下，这由 SDK 自动处理。

:::warning
如果没有完成所有三个步骤，飞书将能够成功*发送*交互式卡片（发送仅需要 `im:message:send` 权限），但点击任何按钮都会返回错误 200340。卡片看起来可以工作——只有当用户与之交互时才会出现错误。
:::

## 文档评论智能回复

除了聊天之外，适配器还可以回复在**飞书/Lark 文档**上留下的 `@` 提及。当用户评论文档（本地文本选择或整篇文档评论）并 @ 提及机器人时，Hermes 会读取文档内容以及周围的评论线程，并在该线程中内联发布 LLM 回复。

该功能由 `drive.notice.comment_add_v1` 事件驱动，处理程序会：

- 并行获取文档内容和评论时间线（整篇文档线程为 20 条消息，本地选择线程为 12 条）。
- 运行 Agent，并使用限定在该单次评论会话范围内的 `feishu_doc` + `feishu_drive` 工具集。
- 将回复分块（每块 4000 字符）并作为线程回复发布。
- 按文档缓存会话 1 小时，上限为 50 条消息，以便同一文档上的后续评论能保持上下文。

### 三层访问控制

文档评论回复是**仅限显式授权**的——没有隐式的允许所有模式。权限按以下顺序解析（每个字段首次匹配即生效）：

1.  **精确文档** —— 限定于特定文档 Token 的规则。
2.  **通配符** —— 匹配文档模式的规则。
3.  **顶层** —— 工作区的默认规则。

每条规则有两种策略可用：

- **`allowlist`** —— 用户/租户的静态列表。
- **`pairing`** —— 静态列表 ∪ 运行时批准的存储。适用于管理员可以实时授予访问权限的逐步推广场景。

规则存储在 `~/.hermes/feishu_comment_rules.json` 中（配对授权存储在 `~/.hermes/feishu_comment_pairing.json` 中），支持基于修改时间的缓存热重载——编辑会在下一个评论事件时生效，无需重启消息网关。

CLI：

```bash
# 检查当前规则和配对状态
python -m gateway.platforms.feishu_comment_rules status

# 模拟对特定文档 + 用户的访问检查
python -m gateway.platforms.feishu_comment_rules check <fileType:fileToken> <user_open_id>

# 在运行时管理配对授权
python -m gateway.platforms.feishu_comment_rules pairing list
python -m gateway.platforms.feishu_comment_rules pairing add <user_open_id>
python -m gateway.platforms.feishu_comment_rules pairing remove <user_open_id>
```

### 必需的飞书应用配置

除了已授予的聊天/卡片权限外，还需添加文档评论事件：

- 在**事件订阅**中订阅 `drive.notice.comment_add_v1`。
- 授予 `docs:doc:readonly` 和 `drive:drive:readonly` 权限范围，以便处理程序可以读取文档内容。

## 媒体支持

### 入站（接收）

适配器接收并缓存来自用户的以下媒体类型：

| 类型 | 扩展名 | 处理方式 |
|------|-----------|-------------------|
| **图片** | .jpg, .jpeg, .png, .gif, .webp, .bmp | 通过飞书 API 下载并在本地缓存 |
| **音频** | .ogg, .mp3, .wav, .m4a, .aac, .flac, .opus, .webm | 下载并缓存；自动提取小文本文件的内容 |
| **视频** | .mp4, .mov, .avi, .mkv, .webm, .m4v, .3gp | 作为文档下载并缓存 |
| **文件** | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx 等 | 作为文档下载并缓存 |
富文本（帖子）消息中的媒体内容，包括内嵌图片和文件附件，也会被提取并缓存。

对于小型基于文本的文档（.txt、.md），文件内容会自动注入到消息文本中，以便 Agent 无需使用工具即可直接读取。

### 出站（发送）

| 方法 | 发送内容 |
|--------|--------------|
| `send` | 文本或富文本帖子消息（根据 Markdown 内容自动检测） |
| `send_image` / `send_image_file` | 将图片上传到飞书，然后以原生图片气泡形式发送（可选标题） |
| `send_document` | 将文件上传到飞书 API，然后作为文件附件发送 |
| `send_voice` | 将音频文件作为飞书文件附件上传 |
| `send_video` | 上传视频并作为原生媒体消息发送 |
| `send_animation` | GIF 会被降级为文件附件（飞书没有原生 GIF 气泡） |

文件上传路由根据扩展名自动处理：

- `.ogg`, `.opus` → 作为 `opus` 音频上传
- `.mp4`, `.mov`, `.avi`, `.m4v` → 作为 `mp4` 媒体上传
- `.pdf`, `.doc(x)`, `.xls(x)`, `.ppt(x)` → 以其文档类型上传
- 其他所有文件 → 作为通用流文件上传

## Markdown 渲染和帖子回退

当出站文本包含 Markdown 格式（标题、粗体、列表、代码块、链接等）时，适配器会自动将其作为飞书**帖子**消息发送，其中嵌入 `md` 标签，而不是纯文本。这能在飞书客户端中实现富文本渲染。

如果飞书 API 拒绝帖子负载（例如，由于不支持的 Markdown 结构），适配器会自动回退为发送纯文本，并去除 Markdown 格式。这种两阶段回退机制确保消息总能送达。

纯文本消息（未检测到 Markdown）将作为简单的 `text` 消息类型发送。

## ACK 表情符号反应

当适配器收到入站消息时，它会立即添加一个 ✅（OK）表情符号反应，以表示消息已收到并正在处理。这为 Agent 完成响应前提供了视觉反馈。

该反应是持久性的——在响应发送后仍保留在消息上，作为接收标记。

用户对机器人消息的反应也会被跟踪。如果用户在机器人发送的消息上添加或移除了表情符号反应，它将被路由为合成文本事件（`reaction:added:EMOJI_TYPE` 或 `reaction:removed:EMOJI_TYPE`），以便 Agent 可以响应用户反馈。

## 突发保护和批处理

适配器包含对快速消息突发的防抖处理，以避免压垮 Agent：

### 文本批处理

当用户快速连续发送多条文本消息时，它们会在被分发前合并为单个事件：

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | 0.6秒 |
| 每批最大消息数 | `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | 8 |
| 每批最大字符数 | `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | 4000 |

### 媒体批处理

快速连续发送的多个媒体附件（例如，拖拽多张图片）会合并为单个事件：

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 0.8秒 |

### 按聊天序列化

同一聊天内的消息按顺序处理（一次一个），以保持对话连贯性。每个聊天都有自己的锁，因此不同聊天中的消息可以并发处理。

## 速率限制（Webhook 模式）

在 Webhook 模式下，适配器强制执行每 IP 速率限制以防止滥用：

- **窗口：** 60 秒滑动窗口
- **限制：** 每个（app_id, 路径, IP）三元组在每个窗口内 120 个请求
- **跟踪上限：** 最多跟踪 4096 个唯一键（防止内存无限增长）

超过限制的请求将收到 HTTP 429（请求过多）响应。

### Webhook 异常跟踪

适配器跟踪每个 IP 地址的连续错误响应。在 6 小时窗口内，同一 IP 连续出现 25 次错误后，会记录一条警告。这有助于检测配置错误的客户端或探测尝试。

其他 Webhook 保护措施：
- **正文大小限制：** 最大 1 MB
- **正文读取超时：** 30 秒
- **Content-Type 强制要求：** 仅接受 `application/json`

## WebSocket 调优

使用 `websocket` 模式时，您可以自定义重连和 ping 行为：

```yaml
platforms:
  feishu:
    extra:
      ws_reconnect_interval: 120   # 重连尝试之间的秒数（默认：120）
      ws_ping_interval: 30         # WebSocket ping 之间的秒数（可选；未设置时使用 SDK 默认值）
```

| 设置 | 配置键 | 默认值 | 描述 |
|---------|-----------|---------|-------------|
| 重连间隔 | `ws_reconnect_interval` | 120秒 | 重连尝试之间的等待时间 |
| Ping 间隔 | `ws_ping_interval` | _(SDK 默认)_ | WebSocket 保活 ping 的频率 |

## 按群组访问控制

除了全局的 `FEISHU_GROUP_POLICY`，您还可以在 config.yaml 中使用 `group_rules` 为每个群聊设置细粒度规则：

```yaml
platforms:
  feishu:
    extra:
      default_group_policy: "open"     # 未在 group_rules 中的群组的默认策略
      admins:                          # 可以管理机器人设置的用户
        - "ou_admin_open_id"
      group_rules:
        "oc_group_chat_id_1":
          policy: "allowlist"          # open | allowlist | blacklist | admin_only | disabled
          allowlist:
            - "ou_user_open_id_1"
            - "ou_user_open_id_2"
        "oc_group_chat_id_2":
          policy: "admin_only"
        "oc_group_chat_id_3":
          policy: "blacklist"
          blacklist:
            - "ou_blocked_user"
```

| 策略 | 描述 |
|--------|-------------|
| `open` | 群组中的任何人都可以使用机器人 |
| `allowlist` | 只有群组 `allowlist` 中的用户可以使用机器人 |
| `blacklist` | 除了群组 `blacklist` 中的用户，其他人都可以使用机器人 |
| `admin_only` | 只有全局 `admins` 列表中的用户才能在此群组中使用机器人 |
| `disabled` | 机器人忽略此群组中的所有消息 |
未在 `group_rules` 中列出的群组将回退到 `default_group_policy`（默认为 `FEISHU_GROUP_POLICY` 的值）。

## 去重

入站消息使用消息 ID 进行去重，TTL 为 24 小时。去重状态在重启后持久化到 `~/.hermes/feishu_seen_message_ids.json`。

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 缓存大小 | `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 2048 条 |

## 所有环境变量

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `FEISHU_APP_ID` | ✅ | — | 飞书/Lark 应用 ID |
| `FEISHU_APP_SECRET` | ✅ | — | 飞书/Lark 应用密钥 |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu`（国内版）或 `lark`（国际版） |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` 或 `webhook` |
| `FEISHU_ALLOWED_USERS` | — | _(空)_ | 用户白名单，逗号分隔的 open_id 列表 |
| `FEISHU_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `FEISHU_ENCRYPT_KEY` | — | _(空)_ | 用于 Webhook 签名验证的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | _(空)_ | 用于 Webhook 负载认证的验证令牌 |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | 群组消息策略：`open`、`allowlist`、`disabled` |
| `FEISHU_BOT_OPEN_ID` | — | _(空)_ | Bot 的 open_id（用于 @提及检测） |
| `FEISHU_BOT_USER_ID` | — | _(空)_ | Bot 的 user_id（用于 @提及检测） |
| `FEISHU_BOT_NAME` | — | _(空)_ | Bot 的显示名称（用于 @提及检测） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook 服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | Webhook 服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | Webhook 端点路径 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | 跟踪的最大去重消息 ID 数 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | 文本突发防抖静默期 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | 每个文本批次合并的最大消息数 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | 每个文本批次合并的最大字符数 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | 媒体突发防抖静默期 |

WebSocket 和按群组 ACL 设置通过 `config.yaml` 中的 `platforms.feishu.extra` 配置（参见上文的 [WebSocket 调优](#websocket-tuning) 和 [按群组访问控制](#per-group-access-control)）。

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `lark-oapi not installed` | 安装 SDK：`pip install lark-oapi` |
| `websockets not installed; websocket mode unavailable` | 安装 websockets：`pip install websockets` |
| `aiohttp not installed; webhook mode unavailable` | 安装 aiohttp：`pip install aiohttp` |
| `FEISHU_APP_ID or FEISHU_APP_SECRET not set` | 设置这两个环境变量或通过 `hermes gateway setup` 配置 |
| `Another local Hermes gateway is already using this Feishu app_id` | 同一时间只能有一个 Hermes 实例使用相同的 app_id。请先停止其他消息网关。 |
| Bot 在群组中不响应 | 确保 Bot 被 @提及，检查 `FEISHU_GROUP_POLICY`，如果策略是 `allowlist` 则验证发送者是否在 `FEISHU_ALLOWED_USERS` 中 |
| `Webhook rejected: invalid verification token` | 确保 `FEISHU_VERIFICATION_TOKEN` 与飞书应用“事件订阅”配置中的令牌匹配 |
| `Webhook rejected: invalid signature` | 确保 `FEISHU_ENCRYPT_KEY` 与飞书应用配置中的加密密钥匹配 |
| 富文本消息显示为纯文本 | 飞书 API 拒绝了富文本负载；这是正常的回退行为。查看日志获取详情。 |
| Bot 未收到图片/文件 | 为你的飞书应用授予 `im:message` 和 `im:resource` 权限范围 |
| Bot 身份未自动检测 | 授予 `admin:app.info:readonly` 范围，或手动设置 `FEISHU_BOT_OPEN_ID` / `FEISHU_BOT_NAME` |
| 点击审批按钮时出现错误 200340 | 在飞书开发者控制台中启用**交互卡片**能力并配置**卡片请求地址**。参见上文的 [必需的飞书应用配置](#required-feishu-app-configuration)。 |
| `Webhook rate limit exceeded` | 同一 IP 每分钟请求超过 120 次。这通常是配置错误或循环导致的。 |

## 工具集

飞书 / Lark 使用 `hermes-feishu` 平台预设，其中包含与 Telegram 和其他基于消息网关的平台相同的核心工具。