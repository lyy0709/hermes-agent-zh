---
sidebar_position: 14
title: "企业微信 (WeCom)"
description: "通过 AI Bot WebSocket 消息网关将 Hermes Agent 连接到企业微信"
---

# 企业微信 (WeCom)

将 Hermes 连接到 [企业微信](https://work.weixin.qq.com/) (WeCom)，腾讯的企业级通讯平台。该适配器使用企业微信的 AI Bot WebSocket 消息网关进行实时双向通信——无需公共端点或 Webhook。

## 前提条件

- 一个企业微信组织账号
- 在企业微信管理后台创建的 AI Bot
- 来自机器人凭证页面的 Bot ID 和 Secret
- Python 包：`aiohttp` 和 `httpx`

## 设置

### 步骤 1：创建一个 AI Bot

#### 推荐：扫码创建（一条命令）

```bash
hermes gateway setup
```

选择 **WeCom** 并使用企业微信手机应用扫描二维码。Hermes 将自动创建一个具有正确权限的机器人应用并保存凭证。

设置向导将：
1. 在终端中显示二维码
2. 等待您使用企业微信手机应用扫描
3. 自动获取 Bot ID 和 Secret
4. 引导您完成访问控制配置

#### 备选方案：手动设置

如果扫码创建不可用，向导将回退到手动输入：

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 导航到 **应用管理** → **创建应用** → **AI Bot**
3. 配置机器人名称和描述
4. 从凭证页面复制 **Bot ID** 和 **Secret**
5. 运行 `hermes gateway setup`，选择 **WeCom**，并在提示时输入凭证

:::warning
请妥善保管 Bot Secret。任何拥有它的人都可以冒充您的机器人。
:::

### 步骤 2：配置 Hermes

#### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

选择 **WeCom** 并按照提示操作。向导将引导您完成：
- 机器人凭证（通过二维码扫描或手动输入）
- 访问控制设置（允许列表、配对模式或开放访问）
- 用于通知的主频道

#### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
WECOM_BOT_ID=your-bot-id
WECOM_SECRET=your-secret

# 可选：限制访问
WECOM_ALLOWED_USERS=user_id_1,user_id_2

# 可选：用于定时任务/通知的主频道
WECOM_HOME_CHANNEL=chat_id
```

### 步骤 3：启动消息网关

```bash
hermes gateway
```

## 功能特性

- **WebSocket 传输** — 持久连接，无需公共端点
- **私聊和群聊** — 可配置的访问策略
- **按群组发送者允许列表** — 对每个群组中谁可以交互进行细粒度控制
- **媒体支持** — 图片、文件、语音、视频的上传和下载
- **AES 加密媒体** — 自动解密入站附件
- **引用上下文** — 保留回复线程
- **Markdown 渲染** — 富文本响应
- **回复模式流式传输** — 将响应与入站消息上下文关联
- **自动重连** — 连接断开时使用指数退避

## 配置选项

在 `config.yaml` 的 `platforms.wecom.extra` 下设置这些选项：

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `bot_id` | — | 企业微信 AI Bot ID（必需） |
| `secret` | — | 企业微信 AI Bot Secret（必需） |
| `websocket_url` | `wss://openws.work.weixin.qq.com` | WebSocket 消息网关 URL |
| `dm_policy` | `open` | 私聊访问策略：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `open` | 群聊访问策略：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID（当 dm_policy=allowlist 时） |
| `group_allow_from` | `[]` | 允许的群组 ID（当 group_policy=allowlist 时） |
| `groups` | `{}` | 按群组配置（见下文） |

## 访问策略

### 私聊策略

控制谁可以向机器人发送私聊消息：

| 值 | 行为 |
|-------|----------|
| `open` | 任何人都可以私聊机器人（默认） |
| `allowlist` | 只有 `allow_from` 中的用户 ID 可以私聊 |
| `disabled` | 忽略所有私聊消息 |
| `pairing` | 配对模式（用于初始设置） |

```bash
WECOM_DM_POLICY=allowlist
```

### 群聊策略

控制机器人在哪些群组中响应：

| 值 | 行为 |
|-------|----------|
| `open` | 机器人在所有群组中响应（默认） |
| `allowlist` | 机器人只在 `group_allow_from` 列出的群组 ID 中响应 |
| `disabled` | 忽略所有群组消息 |

```bash
WECOM_GROUP_POLICY=allowlist
```

### 按群组发送者允许列表

为了进行细粒度控制，您可以限制在特定群组内允许哪些用户与机器人交互。这在 `config.yaml` 中配置：

```yaml
platforms:
  wecom:
    enabled: true
    extra:
      bot_id: "your-bot-id"
      secret: "your-secret"
      group_policy: "allowlist"
      group_allow_from:
        - "group_id_1"
        - "group_id_2"
      groups:
        group_id_1:
          allow_from:
            - "user_alice"
            - "user_bob"
        group_id_2:
          allow_from:
            - "user_charlie"
        "*":
          allow_from:
            - "user_admin"
```

**工作原理：**

1. `group_policy` 和 `group_allow_from` 控制一个群组是否被允许。
2. 如果一个群组通过了顶级检查，`groups.<group_id>.allow_from` 列表（如果存在）会进一步限制该群组内哪些发送者可以与机器人交互。
3. 通配符 `"*"` 群组条目作为未明确列出的群组的默认配置。
4. 允许列表条目支持 `*` 通配符以允许所有用户，且条目不区分大小写。
5. 条目可以选择使用 `wecom:user:` 或 `wecom:group:` 前缀格式——前缀会被自动去除。

如果未为群组配置 `allow_from`，则该群组中的所有用户都被允许（假设该群组本身通过了顶级策略检查）。

## 媒体支持

### 入站（接收）

适配器接收来自用户的媒体附件，并在本地缓存以供 Agent 处理：

| 类型 | 处理方式 |
|------|-----------------|
| **图片** | 下载并缓存在本地。支持基于 URL 和 base64 编码的图片。 |
| **文件** | 下载并缓存。文件名从原始消息中保留。 |
| **语音** | 如果可用，则提取语音消息的文本转录。 |
| **混合消息** | 解析企业微信混合类型消息（文本 + 图片）并提取所有组件。 |

**引用消息：** 来自引用（回复）消息的媒体也会被提取，因此 Agent 可以了解用户正在回复的内容。

### AES 加密媒体解密

企业微信使用 AES-256-CBC 加密一些入站媒体附件。适配器会自动处理：

- 当入站媒体项包含 `aeskey` 字段时，适配器会下载加密的字节并使用 AES-256-CBC 和 PKCS#7 填充进行解密。
- AES 密钥是 `aeskey` 字段的 base64 解码值（必须恰好为 32 字节）。
- IV 从密钥的前 16 字节派生。
- 这需要 `cryptography` Python 包（`pip install cryptography`）。

无需配置——当接收到加密媒体时，解密会透明地进行。

### 出站（发送）

| 方法 | 发送内容 | 大小限制 |
|--------|--------------|------------|
| `send` | Markdown 文本消息 | 4000 字符 |
| `send_image` / `send_image_file` | 原生图片消息 | 10 MB |
| `send_document` | 文件附件 | 20 MB |
| `send_voice` | 语音消息（仅 AMR 格式用于原生语音） | 2 MB |
| `send_video` | 视频消息 | 10 MB |

**分块上传：** 文件通过三步协议（初始化 → 分块 → 完成）以 512 KB 块上传。适配器会自动处理。

**自动降级：** 当媒体超过原生类型的大小限制但低于绝对 20 MB 文件限制时，它会自动作为通用文件附件发送：

- 图片 > 10 MB → 作为文件发送
- 视频 > 10 MB → 作为文件发送
- 语音 > 2 MB → 作为文件发送
- 非 AMR 音频 → 作为文件发送（企业微信仅支持 AMR 用于原生语音）

超过绝对 20 MB 限制的文件会被拒绝，并向聊天发送信息性消息。

## 回复模式流式响应

当机器人通过企业微信回调接收到消息时，适配器会记住入站请求 ID。如果在请求上下文仍然活跃时发送响应，适配器会使用企业微信的回复模式（`aibot_respond_msg`）进行流式传输，以将响应直接关联到入站消息。这为企业微信客户端提供了更自然的对话体验。

如果入站请求上下文已过期或不可用，适配器会回退到通过 `aibot_send_msg` 主动发送消息。

回复模式也适用于媒体：上传的媒体可以作为对原始消息的回复发送。

## 连接与重连

适配器与企业微信消息网关 `wss://openws.work.weixin.qq.com` 保持持久的 WebSocket 连接。

### 连接生命周期

1. **连接：** 打开 WebSocket 连接并发送带有 bot_id 和 secret 的 `aibot_subscribe` 认证帧。
2. **心跳：** 每 30 秒发送应用级 ping 帧以保持连接活跃。
3. **监听：** 持续读取入站帧并分派消息回调。

### 重连行为

连接丢失时，适配器使用指数退避进行重连：

| 尝试次数 | 延迟 |
|---------|-------|
| 第 1 次重试 | 2 秒 |
| 第 2 次重试 | 5 秒 |
| 第 3 次重试 | 10 秒 |
| 第 4 次重试 | 30 秒 |
| 第 5 次及以上重试 | 60 秒 |

每次成功重连后，退避计数器重置为零。所有待处理的请求 Future 在断开连接时都会失败，因此调用者不会无限期挂起。

### 去重

入站消息使用消息 ID 进行去重，时间窗口为 5 分钟，最大缓存 1000 条条目。这可以防止在重连或网络波动期间重复处理消息。

## 所有环境变量

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `WECOM_BOT_ID` | ✅ | — | 企业微信 AI Bot ID |
| `WECOM_SECRET` | ✅ | — | 企业微信 AI Bot Secret |
| `WECOM_ALLOWED_USERS` | — | _(空)_ | 用于消息网关级允许列表的逗号分隔用户 ID |
| `WECOM_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `WECOM_WEBSOCKET_URL` | — | `wss://openws.work.weixin.qq.com` | WebSocket 消息网关 URL |
| `WECOM_DM_POLICY` | — | `open` | 私聊访问策略 |
| `WECOM_GROUP_POLICY` | — | `open` | 群聊访问策略 |

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `WECOM_BOT_ID and WECOM_SECRET are required` | 设置两个环境变量或在设置向导中配置 |
| `WeCom startup failed: aiohttp not installed` | 安装 aiohttp：`pip install aiohttp` |
| `WeCom startup failed: httpx not installed` | 安装 httpx：`pip install httpx` |
| `invalid secret (errcode=40013)` | 验证 secret 是否与您的机器人凭证匹配 |
| `Timed out waiting for subscribe acknowledgement` | 检查到 `openws.work.weixin.qq.com` 的网络连接 |
| 机器人在群组中不响应 | 检查 `group_policy` 设置并确保群组 ID 在 `group_allow_from` 中 |
| 机器人忽略群组中的某些用户 | 检查 `groups` 配置部分中的按群组 `allow_from` 列表 |
| 媒体解密失败 | 安装 `cryptography`：`pip install cryptography` |
| `cryptography is required for WeCom media decryption` | 入站媒体是 AES 加密的。安装：`pip install cryptography` |
| 语音消息作为文件发送 | 企业微信仅支持 AMR 格式用于原生语音。其他格式会自动降级为文件。 |
| `File too large` 错误 | 企业微信对所有文件上传有 20 MB 的绝对限制。压缩或拆分文件。 |
| 图片作为文件发送 | 图片 > 10 MB 超过了原生图片限制，会自动降级为文件附件。 |
| `Timeout sending message to WeCom` | WebSocket 可能已断开连接。检查日志中的重连消息。 |
| `WeCom websocket closed during authentication` | 网络问题或凭证错误。验证 bot_id 和 secret。 |