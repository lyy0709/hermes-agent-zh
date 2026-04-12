---
sidebar_position: 8
sidebar_label: "SMS (Twilio)"
title: "SMS (Twilio)"
description: "通过 Twilio 将 Hermes Agent 设置为短信聊天机器人"
---

# SMS 设置 (Twilio)

Hermes 通过 [Twilio](https://www.twilio.com/) API 连接到短信服务。人们向您的 Twilio 电话号码发送短信，即可获得 AI 回复 —— 与 Telegram 或 Discord 相同的对话体验，但通过标准短信实现。

:::info 共享凭据
短信消息网关与可选的[电话技能](/docs/reference/skills-catalog)共享凭据。如果您已经为语音通话或一次性短信设置了 Twilio，那么该网关可以使用相同的 `TWILIO_ACCOUNT_SID`、`TWILIO_AUTH_TOKEN` 和 `TWILIO_PHONE_NUMBER`。
:::

---

## 先决条件

- **Twilio 账户** — [在 twilio.com 注册](https://www.twilio.com/try-twilio)（提供免费试用）
- **一个具有短信功能的 Twilio 电话号码**
- **一个可公开访问的服务器** — 当短信到达时，Twilio 会向您的服务器发送 Webhook
- **aiohttp** — `pip install 'hermes-agent[sms]'`

---

## 步骤 1：获取您的 Twilio 凭据

1.  前往 [Twilio 控制台](https://console.twilio.com/)
2.  从仪表板复制您的 **Account SID** 和 **Auth Token**
3.  前往 **Phone Numbers → Manage → Active Numbers** — 记下您的 E.164 格式电话号码（例如，`+15551234567`）

---

## 步骤 2：配置 Hermes

### 交互式设置（推荐）

```bash
hermes gateway setup
```

从平台列表中选择 **SMS (Twilio)**。向导将提示您输入凭据。

### 手动设置

添加到 `~/.hermes/.env`：

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# 安全性：限制为特定电话号码（推荐）
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 可选：为定时任务交付设置一个主频道
SMS_HOME_CHANNEL=+15559876543
```

---

## 步骤 3：配置 Twilio Webhook

Twilio 需要知道将接收到的消息发送到哪里。在 [Twilio 控制台](https://console.twilio.com/)中：

1.  前往 **Phone Numbers → Manage → Active Numbers**
2.  点击您的电话号码
3.  在 **Messaging → A MESSAGE COMES IN** 下，设置：
    - **Webhook**: `https://your-server:8080/webhooks/twilio`
    - **HTTP Method**: `POST`

:::tip 暴露您的 Webhook
如果您在本地运行 Hermes，请使用隧道来暴露 Webhook：

```bash
# 使用 cloudflared
cloudflared tunnel --url http://localhost:8080

# 使用 ngrok
ngrok http 8080
```

将生成的公共 URL 设置为您的 Twilio Webhook。
:::

**将 `SMS_WEBHOOK_URL` 设置为您在 Twilio 中配置的相同 URL。** 这是 Twilio 签名验证所必需的 —— 没有它，适配器将拒绝启动：

```bash
# 必须与 Twilio 控制台中的 Webhook URL 匹配
SMS_WEBHOOK_URL=https://your-server:8080/webhooks/twilio
```

Webhook 端口默认为 `8080`。可以通过以下方式覆盖：

```bash
SMS_WEBHOOK_PORT=3000
```

---

## 步骤 4：启动消息网关

```bash
hermes gateway
```

您应该会看到：

```
[sms] Twilio webhook server listening on 0.0.0.0:8080, from: +1555***4567
```

如果您看到 `Refusing to start: SMS_WEBHOOK_URL is required`，请将 `SMS_WEBHOOK_URL` 设置为在 Twilio 控制台中配置的公共 URL（参见步骤 3）。

向您的 Twilio 号码发送短信 —— Hermes 将通过短信回复。

---

## 环境变量

| 变量 | 必需 | 描述 |
|----------|----------|-------------|
| `TWILIO_ACCOUNT_SID` | 是 | Twilio Account SID（以 `AC` 开头） |
| `TWILIO_AUTH_TOKEN` | 是 | Twilio Auth Token（也用于 Webhook 签名验证） |
| `TWILIO_PHONE_NUMBER` | 是 | 您的 Twilio 电话号码（E.164 格式） |
| `SMS_WEBHOOK_URL` | 是 | 用于 Twilio 签名验证的公共 URL —— 必须与 Twilio 控制台中的 Webhook URL 匹配 |
| `SMS_WEBHOOK_PORT` | 否 | Webhook 监听端口（默认：`8080`） |
| `SMS_WEBHOOK_HOST` | 否 | Webhook 绑定地址（默认：`0.0.0.0`） |
| `SMS_INSECURE_NO_SIGNATURE` | 否 | 设置为 `true` 以禁用签名验证（仅限本地开发 —— **不适用于生产环境**） |
| `SMS_ALLOWED_USERS` | 否 | 允许聊天的逗号分隔的 E.164 格式电话号码 |
| `SMS_ALLOW_ALL_USERS` | 否 | 设置为 `true` 以允许任何人（不推荐） |
| `SMS_HOME_CHANNEL` | 否 | 用于定时任务/通知交付的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | 否 | 主频道的显示名称（默认：`Home`） |

---

## 短信特定行为

- **仅纯文本** — Markdown 会被自动剥离，因为短信会将其渲染为字面字符
- **1600 字符限制** — 较长的回复会在自然边界（换行符，然后是空格）处拆分为多条消息
- **防止回显** — 来自您自己 Twilio 号码的消息会被忽略，以防止循环
- **电话号码脱敏** — 电话号码在日志中会被脱敏以保护隐私

---

## 安全性

### Webhook 签名验证

Hermes 通过验证 `X-Twilio-Signature` 标头（HMAC-SHA1）来验证入站 Webhook 确实来自 Twilio。这可以防止攻击者注入伪造消息。

**`SMS_WEBHOOK_URL` 是必需的。** 将其设置为在 Twilio 控制台中配置的公共 URL。没有它，适配器将拒绝启动。

对于没有公共 URL 的本地开发，您可以禁用验证：

```bash
# 仅限本地开发 —— 不适用于生产环境
SMS_INSECURE_NO_SIGNATURE=true
```

### 用户允许列表

**默认情况下，消息网关拒绝所有用户。** 配置允许列表：

```bash
# 推荐：限制为特定电话号码
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 或者允许所有人（不推荐用于具有终端访问权限的机器人）
SMS_ALLOW_ALL_USERS=true
```

:::warning
短信没有内置加密。除非您了解安全影响，否则不要将短信用于敏感操作。对于敏感用例，请优先使用 Signal 或 Telegram。
:::

---

## 故障排除

### 消息未到达

1.  检查您的 Twilio Webhook URL 是否正确且可公开访问
2.  验证 `TWILIO_ACCOUNT_SID` 和 `TWILIO_AUTH_TOKEN` 是否正确
3.  检查 Twilio 控制台 → **Monitor → Logs → Messaging** 中的交付错误
4.  确保您的电话号码在 `SMS_ALLOWED_USERS` 中（或设置了 `SMS_ALLOW_ALL_USERS=true`）

### 回复未发送

1.  检查 `TWILIO_PHONE_NUMBER` 是否正确设置（E.164 格式，带 `+`）
2.  验证您的 Twilio 账户是否具有支持短信功能的号码
3.  检查 Hermes 消息网关日志中是否有 Twilio API 错误

### Webhook 端口冲突

如果端口 8080 已被占用，请更改它：

```bash
SMS_WEBHOOK_PORT=3001
```

更新 Twilio 控制台中的 Webhook URL 以匹配。