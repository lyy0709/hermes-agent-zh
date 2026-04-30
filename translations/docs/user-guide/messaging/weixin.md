---
sidebar_position: 15
title: "微信"
description: "通过 iLink Bot API 将 Hermes Agent 连接到个人微信账号"
---

# 微信

将 Hermes 连接到 [微信](https://weixin.qq.com/)，腾讯的个人即时通讯平台。该适配器使用腾讯的 **iLink Bot API** 连接个人微信账号——这与企业微信不同。消息通过长轮询方式传递，因此不需要公共端点或 Webhook。

:::info
此适配器适用于**个人微信账号**。如果您需要企业微信，请改用 [企业微信适配器](./wecom.md)。
:::

:::warning iLink 机器人身份——普通微信群可能无法使用
二维码登录会将 Hermes 连接到一个 **iLink 机器人身份**（例如 `a5ace6fd482e@im.bot`），**而不是**一个完全可脚本化的普通个人微信账号。这意味着：

- iLink 机器人身份通常**无法像普通联系人一样被邀请加入普通微信群**。
- 对于大多数机器人类型的账号，iLink 通常**不会将普通微信群事件**（包括对用于二维码登录的个人账号的 `@` 提及）传递给消息网关。
- `@` 提及用于扫描二维码的个人微信账号**并不等于** `@` 提及 iLink 机器人——机器人是一个独立的身份。
- 下面的 `WEIXIN_GROUP_POLICY` / `WEIXIN_GROUP_ALLOWED_USERS` 设置仅在 iLink 实际为您的账号类型返回群组事件时才生效。如果它不返回，无论策略如何，群组消息都不会到达 Hermes。

实际上，大多数部署只能可靠地实现与 iLink 机器人的私聊。如果配置后群组消息传递仍然无效，限制在于 iLink 端，而不是 Hermes。每当 `WEIXIN_GROUP_POLICY` 设置为 `disabled` 以外的任何值时，消息网关在启动时都会记录一条 `WARNING` 日志。
:::

## 前提条件

- 一个个人微信账号
- Python 包：`aiohttp` 和 `cryptography`
- 当 Hermes 安装了 `messaging` 额外组件时，包含终端二维码渲染功能

安装所需的依赖项：

```bash
pip install aiohttp cryptography
# 可选：用于终端二维码显示
pip install hermes-agent[messaging]
```

## 设置

### 1. 运行设置向导

连接微信账号最简单的方法是通过交互式设置：

```bash
hermes gateway setup
```

提示时选择 **Weixin**。向导将：

1. 从 iLink Bot API 请求二维码
2. 在终端中显示二维码（或提供 URL）
3. 等待您使用微信手机应用扫描二维码
4. 提示您在手机上确认登录
5. 自动将账号凭据保存到 `~/.hermes/weixin/accounts/`

确认后，您将看到类似以下的消息：

```
微信连接成功，account_id=your-account-id
```

向导会存储 `account_id`、`token` 和 `base_url`，因此您无需手动配置它们。

### 2. 配置环境变量

初始二维码登录后，至少在 `~/.hermes/.env` 中设置账号 ID：

```bash
WEIXIN_ACCOUNT_ID=your-account-id

# 可选：覆盖 token（通常从二维码登录自动保存）
# WEIXIN_TOKEN=your-bot-token

# 可选：限制访问
WEIXIN_DM_POLICY=open
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2

# 可选：恢复旧版的多行分割行为
# WEIXIN_SPLIT_MULTILINE_MESSAGES=true

# 可选：定时任务/通知的主频道
WEIXIN_HOME_CHANNEL=chat_id
WEIXIN_HOME_CHANNEL_NAME=Home
```

### 3. 启动消息网关

```bash
hermes gateway
```

适配器将恢复保存的凭据，连接到 iLink API，并开始长轮询消息。

## 功能特性

- **长轮询传输**——无需公共端点、Webhook 或 WebSocket
- **二维码登录**——通过 `hermes gateway setup` 进行扫描连接设置
- **私聊消息**——可配置的访问策略；群组消息传递取决于 iLink 是否实际为连接的身份传递群组事件（对于 iLink 机器人账号通常不是这样——请参阅上面的警告）
- **媒体支持**——图片、视频、文件和语音消息
- **AES-128-ECB 加密 CDN**——所有媒体传输的自动加密/解密
- **上下文 Token 持久化**——跨重启的磁盘支持的回复连续性
- **Markdown 格式化**——保留 Markdown，包括标题、表格和代码块，因此支持 Markdown 的微信客户端可以原生渲染
- **智能消息分块**——消息在限制内保持为单个气泡；只有超大的有效载荷才会在逻辑边界处分割
- **输入状态指示器**——在 Agent 处理时在微信客户端显示“正在输入…”状态
- **SSRF 防护**——下载前验证出站媒体 URL
- **消息去重**——5 分钟滑动窗口防止重复处理
- **带退避的自动重试**——从瞬时 API 错误中恢复

## 配置选项

在 `config.yaml` 的 `platforms.weixin.extra` 下设置这些选项：

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `account_id` | — | iLink Bot 账号 ID（必需） |
| `token` | — | iLink Bot token（必需，从二维码登录自动保存） |
| `base_url` | `https://ilinkai.weixin.qq.com` | iLink API 基础 URL |
| `cdn_base_url` | `https://novac2c.cdn.weixin.qq.com/c2c` | 媒体传输的 CDN 基础 URL |
| `dm_policy` | `open` | 私聊访问策略：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `disabled` | 群组访问策略：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID（当 dm_policy=allowlist 时） |
| `group_allow_from` | `[]` | 允许的群组 ID（当 group_policy=allowlist 时） |
| `split_multiline_messages` | `false` | 当为 `true` 时，将多行回复分割成多个聊天消息（旧版行为）。当为 `false` 时，将多行回复保持为一条消息，除非超过长度限制。 |

## 访问策略

### 私聊策略

控制谁可以向机器人发送私聊消息：

| 值 | 行为 |
|-------|----------|
| `open` | 任何人都可以向机器人发送私聊消息（默认） |
| `allowlist` | 只有 `allow_from` 中的用户 ID 可以发送私聊消息 |
| `disabled` | 忽略所有私聊消息 |
| `pairing` | 配对模式（用于初始设置） |
```bash
WEIXIN_DM_POLICY=allowlist
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2
```

### 群组策略

控制当 iLink 为已连接身份传递群组事件时，机器人响应哪些群组。对于通过二维码登录的 iLink 机器人身份（例如 `...@im.bot`），通常根本不会传递群组事件，因此此策略可能无效——请参阅页面顶部的 iLink 机器人限制警告。

| 值 | 行为 |
|-------|----------|
| `open` | 机器人在所有群组中响应（如果事件被传递） |
| `allowlist` | 机器人仅在 `group_allow_from` 中列出的群组 ID 中响应（如果事件被传递） |
| `disabled` | 忽略所有群组消息（默认） |

```bash
WEIXIN_GROUP_POLICY=allowlist
# 注意：这是一个以逗号分隔的群聊 ID 列表，而不是成员用户 ID，
# 尽管变量名包含 "USERS"。配置时请记住这一点。
WEIXIN_GROUP_ALLOWED_USERS=group_id_1,group_id_2
```

:::note
对于微信，默认的群组策略是 `disabled`（与企业微信默认 `open` 不同）。这是有意为之——个人微信账号可能加入了许多群组，而 iLink 机器人身份通常根本无法接收普通的微信群消息。如果您将 `WEIXIN_GROUP_POLICY` 设置为 `disabled` 以外的任何值，消息网关会在启动时记录一条 `WARNING` 日志。
:::

## 媒体支持

### 入站（接收）

适配器接收来自用户的媒体附件，从微信 CDN 下载，解密，并在本地缓存以供 Agent 处理：

| 类型 | 处理方式 |
|------|-----------------|
| **图片** | 下载，AES 解密，并缓存为 JPEG。 |
| **视频** | 下载，AES 解密，并缓存为 MP4。 |
| **文件** | 下载，AES 解密，并缓存。保留原始文件名。 |
| **语音** | 如果有可用的文本转录，则提取为文本。否则，音频（SILK 格式）会被下载并缓存。 |

**引用消息：** 来自引用（回复）消息的媒体也会被提取，以便 Agent 了解用户正在回复的内容上下文。

### AES-128-ECB 加密 CDN

微信媒体文件通过加密的 CDN 传输。适配器透明地处理此过程：

- **入站：** 使用 `encrypted_query_param` URL 从 CDN 下载加密媒体，然后使用消息负载中提供的每个文件的密钥通过 AES-128-ECB 解密。
- **出站：** 文件在本地使用随机的 AES-128-ECB 密钥加密，上传到 CDN，加密引用包含在出站消息中。
- AES 密钥为 16 字节（128 位）。密钥可能以原始 base64 或十六进制编码形式到达——适配器处理两种格式。
- 这需要 `cryptography` Python 包。

无需配置——加密和解密会自动进行。

### 出站（发送）

| 方法 | 发送内容 |
|--------|--------------|
| `send` | 带有 Markdown 格式的文本消息 |
| `send_image` / `send_image_file` | 原生图片消息（通过 CDN 上传） |
| `send_document` | 文件附件（通过 CDN 上传） |
| `send_video` | 视频消息（通过 CDN 上传） |

所有出站媒体都经过加密 CDN 上传流程：

1.  生成随机 AES-128 密钥
2.  使用 AES-128-ECB + PKCS#7 填充加密文件
3.  从 iLink API (`getuploadurl`) 请求上传 URL
4.  将密文上传到 CDN
5.  发送带有加密媒体引用的消息

## 上下文 Token 持久化

iLink Bot API 要求每个出站消息都回显给定对等方的 `context_token`。适配器维护一个磁盘支持的上下文 Token 存储：

-   Token 按账户+对等方保存到 `~/.hermes/weixin/accounts/<account_id>.context-tokens.json`
-   启动时，恢复先前保存的 Token
-   每个入站消息都会更新该发送者的存储 Token
-   出站消息自动包含最新的上下文 Token

这确保了即使在消息网关重启后，回复的连续性。

## Markdown 格式化

通过 iLink Bot API 连接的微信客户端可以直接渲染 Markdown，因此适配器保留 Markdown 而不是重写它：

-   **标题** 保持为 Markdown 标题 (`#`, `##`, ...)
-   **表格** 保持为 Markdown 表格
-   **代码块** 保持为围栏代码块
-   **过多的空行** 在围栏代码块外被压缩为双换行符

## 消息分块

只要消息符合平台限制，就会作为单个聊天消息传递。只有超大的负载才会被拆分传递：

-   最大消息长度：**4000 个字符**
-   低于限制的消息即使包含多个段落或换行符也保持完整
-   超长消息在逻辑边界（段落、空行、代码块）处拆分
-   尽可能保持代码块完整（除非代码块本身超过限制，否则不会在块中间拆分）
-   超大的单个块会回退到基础适配器的截断逻辑
-   0.3 秒的块间延迟可防止在发送多个块时触发微信的速率限制

## 输入状态指示器

适配器在微信客户端中显示输入状态：

1.  当消息到达时，适配器通过 `getconfig` API 获取 `typing_ticket`
2.  输入状态票据按用户缓存 10 分钟
3.  `send_typing` 发送输入开始信号；`stop_typing` 发送输入停止信号
4.  当 Agent 处理消息时，消息网关会自动触发输入状态指示器

## 长轮询连接

适配器使用 HTTP 长轮询（而非 WebSocket）来接收消息：

### 工作原理

1.  **连接：** 验证凭据并启动轮询循环
2.  **轮询：** 调用带有 35 秒超时的 `getupdates`；服务器会保持请求直到消息到达或超时到期
3.  **分发：** 入站消息通过 `asyncio.create_task` 并发分发
4.  **同步缓冲区：** 一个持久的同步游标 (`get_updates_buf`) 被保存到磁盘，以便适配器在重启后从正确的位置恢复

### 重试行为

发生 API 错误时，适配器使用简单的重试策略：
| 条件 | 行为 |
|-----------|----------|
| 临时错误（第1-2次） | 2秒后重试 |
| 重复错误（3次以上） | 退避30秒，然后重置计数器 |
| 会话过期 (`errcode=-14`) | 暂停10分钟（可能需要重新登录） |
| 超时 | 立即重新轮询（正常的长轮询行为） |

### 去重

入站消息使用消息ID进行去重，时间窗口为5分钟。这可以防止在网络波动或轮询响应重叠时重复处理。

### Token 锁

一个 Weixin 消息网关实例一次只能使用一个给定的 token。适配器在启动时获取一个作用域锁，并在关闭时释放。如果另一个网关已经在使用相同的 token，启动将失败并显示信息性错误消息。

## 所有环境变量

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `WEIXIN_ACCOUNT_ID` | ✅ | — | iLink Bot 账户 ID（来自二维码登录） |
| `WEIXIN_TOKEN` | ✅ | — | iLink Bot token（二维码登录后自动保存） |
| `WEIXIN_BASE_URL` | — | `https://ilinkai.weixin.qq.com` | iLink API 基础 URL |
| `WEIXIN_CDN_BASE_URL` | — | `https://novac2c.cdn.weixin.qq.com/c2c` | 用于媒体传输的 CDN 基础 URL |
| `WEIXIN_DM_POLICY` | — | `open` | 私聊访问策略：`open`、`allowlist`、`disabled`、`pairing` |
| `WEIXIN_GROUP_POLICY` | — | `disabled` | 群聊访问策略：`open`、`allowlist`、`disabled` |
| `WEIXIN_ALLOWED_USERS` | — | _(空)_ | 用于私聊白名单的逗号分隔的用户 ID |
| `WEIXIN_GROUP_ALLOWED_USERS` | — | _(空)_ | 用于群聊白名单的逗号分隔的**群聊 ID**（非成员用户 ID）。变量名是历史遗留的——它期望的是群聊 ID，而不是用户 ID。 |
| `WEIXIN_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `WEIXIN_HOME_CHANNEL_NAME` | — | `Home` | 主频道的显示名称 |
| `WEIXIN_ALLOW_ALL_USERS` | — | — | 网关级别的标志，允许所有用户（由设置向导使用） |

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `Weixin startup failed: aiohttp and cryptography are required` | 安装两者：`pip install aiohttp cryptography` |
| `Weixin startup failed: WEIXIN_TOKEN is required` | 运行 `hermes gateway setup` 完成二维码登录，或手动设置 `WEIXIN_TOKEN` |
| `Weixin startup failed: WEIXIN_ACCOUNT_ID is required` | 在 `.env` 文件中设置 `WEIXIN_ACCOUNT_ID` 或运行 `hermes gateway setup` |
| `Another local Hermes gateway is already using this Weixin token` | 先停止另一个网关实例——每个 token 只允许一个轮询器 |
| 会话过期 (`errcode=-14`) | 您的登录会话已过期。重新运行 `hermes gateway setup` 扫描新的二维码 |
| 设置过程中二维码过期 | 二维码最多自动刷新3次。如果持续过期，请检查网络连接 |
| Bot 不响应私聊 | 检查 `WEIXIN_DM_POLICY`——如果设置为 `allowlist`，发送者必须在 `WEIXIN_ALLOWED_USERS` 中 |
| Bot 忽略群聊消息 | 群聊策略默认为 `disabled`。设置 `WEIXIN_GROUP_POLICY=open` 或 `allowlist`——但请注意，通过二维码登录的 iLink bot 身份 (`...@im.bot`) 通常根本无法接收普通的微信群聊消息。如果网关日志显示没有群聊消息的原始入站事件，则限制在 iLink 端，而非 Hermes。 |
| 媒体下载/上传失败 | 确保已安装 `cryptography`。检查对 `novac2c.cdn.weixin.qq.com` 的网络访问 |
| `Blocked unsafe URL (SSRF protection)` | 出站媒体 URL 指向私有/内部地址。只允许公共 URL |
| 语音消息显示为文本 | 如果微信提供了转录文本，适配器会使用该文本。这是预期行为 |
| 消息出现重复 | 适配器通过消息 ID 去重。如果看到重复消息，请检查是否运行了多个网关实例 |
| `iLink POST ... HTTP 4xx/5xx` | 来自 iLink 服务的 API 错误。检查您的 token 有效性和网络连接 |
| 终端二维码不显示 | 重新安装并包含 messaging 额外依赖：`pip install hermes-agent[messaging]`。或者，打开二维码上方打印的 URL |