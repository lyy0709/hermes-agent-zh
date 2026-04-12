---
sidebar_position: 15
---

# 企业微信回调（自建应用）

通过回调/Webhook 模式，将 Hermes 作为自建企业应用连接到企业微信。

:::info 企业微信机器人 vs 企业微信回调
Hermes 支持两种企业微信集成模式：
- **[企业微信机器人](wecom.md)** — 机器人模式，通过 WebSocket 连接。设置更简单，可在群聊中工作。
- **企业微信回调**（本页） — 自建应用模式，接收加密的 XML 回调。在用户的企业微信侧边栏中显示为一等应用。支持多企业路由。
:::

## 工作原理

1.  在企业微信管理后台注册一个自建应用
2.  企业微信将加密的 XML 推送到你的 HTTP 回调端点
3.  Hermes 解密消息，将其加入 Agent 处理队列
4.  立即确认（静默 — 不向用户显示任何内容）
5.  Agent 处理请求（通常需要 3–30 分钟）
6.  回复通过企业微信 `message/send` API 主动发送

## 先决条件

-   拥有管理员权限的企业微信企业账户
-   `aiohttp` 和 `httpx` Python 包（默认安装已包含）
-   一个可公开访问的服务器用于回调 URL（或使用 ngrok 等隧道工具）

## 设置

### 1. 在企业微信中创建自建应用

1.  访问 [企业微信管理后台](https://work.weixin.qq.com/) → **应用管理** → **创建应用**
2.  记下你的 **企业 ID**（显示在管理后台顶部）
3.  在应用设置中，创建一个 **企业密钥**
4.  从应用概览页面记下 **AgentId**
5.  在 **接收消息** 下，配置回调 URL：
    -   URL: `http://你的公网IP:8645/wecom/callback`
    -   Token: 生成一个随机令牌（企业微信会提供一个）
    -   EncodingAESKey: 生成一个密钥（企业微信会提供一个）

### 2. 配置环境变量

添加到你的 `.env` 文件：

```bash
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_CORP_SECRET=your-corp-secret
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-callback-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-aes-key

# 可选
WECOM_CALLBACK_HOST=0.0.0.0
WECOM_CALLBACK_PORT=8645
WECOM_CALLBACK_ALLOWED_USERS=user1,user2
```

### 3. 启动消息网关

```bash
hermes gateway start
```

回调适配器将在配置的端口上启动一个 HTTP 服务器。企业微信将通过 GET 请求验证回调 URL，然后开始通过 POST 发送消息。

## 配置参考

在 `config.yaml` 的 `platforms.wecom_callback.extra` 下设置这些值，或使用环境变量：

| 设置项 | 默认值 | 描述 |
|---------|---------|-------------|
| `corp_id` | — | 企业微信企业 Corp ID（必需） |
| `corp_secret` | — | 自建应用的企业密钥（必需） |
| `agent_id` | — | 自建应用的 AgentId（必需） |
| `token` | — | 回调验证令牌（必需） |
| `encoding_aes_key` | — | 用于回调加密的 43 字符 AES 密钥（必需） |
| `host` | `0.0.0.0` | HTTP 回调服务器的绑定地址 |
| `port` | `8645` | HTTP 回调服务器的端口 |
| `path` | `/wecom/callback` | 回调端点的 URL 路径 |

## 多应用路由

对于运行多个自建应用的企业（例如，跨不同部门或子公司），请在 `config.yaml` 中配置 `apps` 列表：

```yaml
platforms:
  wecom_callback:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8645
      apps:
        - name: "dept-a"
          corp_id: "ww_corp_a"
          corp_secret: "secret-a"
          agent_id: "1000002"
          token: "token-a"
          encoding_aes_key: "key-a-43-chars..."
        - name: "dept-b"
          corp_id: "ww_corp_b"
          corp_secret: "secret-b"
          agent_id: "1000003"
          token: "token-b"
          encoding_aes_key: "key-b-43-chars..."
```

用户通过 `corp_id:user_id` 进行作用域划分，以防止跨企业冲突。当用户发送消息时，适配器会记录他们属于哪个应用（企业），并通过正确的应用的访问令牌路由回复。

## 访问控制

限制哪些用户可以与应用交互：

```bash
# 允许特定用户
WECOM_CALLBACK_ALLOWED_USERS=zhangsan,lisi,wangwu

# 或允许所有用户
WECOM_CALLBACK_ALLOW_ALL_USERS=true
```

## 端点

适配器暴露以下端点：

| 方法 | 路径 | 用途 |
|--------|------|---------|
| GET | `/wecom/callback` | URL 验证握手（企业微信在设置期间发送此请求） |
| POST | `/wecom/callback` | 加密消息回调（企业微信将用户消息发送到此端点） |
| GET | `/health` | 健康检查 — 返回 `{"status": "ok"}` |

## 加密

所有回调负载都使用 EncodingAESKey 通过 AES-CBC 加密。适配器处理：

-   **入站**：解密 XML 负载，验证 SHA1 签名
-   **出站**：通过主动 API 发送回复（非加密回调响应）

加密实现与腾讯官方的 WXBizMsgCrypt SDK 兼容。

## 限制

-   **无流式传输** — 回复在 Agent 完成后作为完整消息到达
-   **无输入状态指示** — 回调模型不支持显示输入状态
-   **仅限文本** — 目前支持文本消息；图片/文件/语音尚未实现
-   **响应延迟** — Agent 会话需要 3–30 分钟；用户在处理完成后才能看到回复