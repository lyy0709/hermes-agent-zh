---
sidebar_position: 5
title: "Microsoft Teams"
description: "将 Hermes Agent 设置为 Microsoft Teams 机器人"
---

# Microsoft Teams 设置

将 Hermes Agent 作为机器人连接到 Microsoft Teams。与 Slack 的 Socket 模式不同，Teams 通过调用**公共 HTTPS Webhook** 来传递消息，因此您的实例需要一个可公开访问的端点——可以是开发隧道（本地开发）或真实域名（生产环境）。

## 机器人的响应方式

| 上下文 | 行为 |
|---------|----------|
| **个人聊天 (DM)** | 机器人响应每条消息。无需 @提及。 |
| **群组聊天** | 机器人仅在 @提及时响应。 |
| **频道** | 机器人仅在 @提及时响应。 |

Teams 将 @提及作为带有 `<at>BotName</at>` 标签的常规消息传递，Hermes 在处理前会自动去除这些标签。

---

## 步骤 1：安装 Teams CLI

`@microsoft/teams.cli` 可自动完成机器人注册——无需使用 Azure 门户。

```bash
npm install -g @microsoft/teams.cli@preview
teams login
```

要验证登录并查找您自己的 AAD 对象 ID（`TEAMS_ALLOWED_USERS` 需要）：

```bash
teams status --verbose
```

---

## 步骤 2：暴露 Webhook 端口

Teams 无法向 `localhost` 传递消息。对于本地开发，请使用任何隧道工具来获取公共 HTTPS URL。默认端口是 `3978`——如果需要，可以使用 `TEAMS_PORT` 更改它。

```bash
# devtunnel (Microsoft)
devtunnel create hermes-bot --allow-anonymous
devtunnel port create hermes-bot -p 3978 --protocol https  # 如果更改了端口，请将 3978 替换为 TEAMS_PORT
devtunnel host hermes-bot

# ngrok
ngrok http 3978  # 如果更改了端口，请将 3978 替换为 TEAMS_PORT

# cloudflared
cloudflared tunnel --url http://localhost:3978  # 如果更改了端口，请将 3978 替换为 TEAMS_PORT
```

复制输出中的 `https://` URL——您将在下一步中使用它。在开发期间保持隧道运行。

对于生产环境，请将机器人的端点指向您服务器的公共域名（参见[生产部署](#production-deployment)）。

---

## 步骤 3：创建机器人

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://<your-tunnel-url>/api/messages"
```

CLI 会输出您的 `CLIENT_ID`、`CLIENT_SECRET` 和 `TENANT_ID`，以及步骤 6 的安装链接。保存客户端密钥——它不会再次显示。

---

## 步骤 4：配置环境变量

添加到 `~/.hermes/.env`：

```bash
# 必需
TEAMS_CLIENT_ID=<your-client-id>
TEAMS_CLIENT_SECRET=<your-client-secret>
TEAMS_TENANT_ID=<your-tenant-id>

# 限制对特定用户的访问（推荐）
# 使用来自 `teams status --verbose` 的 AAD 对象 ID
TEAMS_ALLOWED_USERS=<your-aad-object-id>
```

---

## 步骤 5：启动消息网关

```bash
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d gateway
```

这将启动消息网关。默认的 Webhook 端口是 `3978`（可使用 `TEAMS_PORT` 覆盖）。检查它是否正在运行：

```bash
curl http://localhost:3978/health   # 应返回：ok
docker logs -f hermes
```

查找：
```
[teams] Webhook server listening on 0.0.0.0:3978/api/messages
```

---

## 步骤 6：在 Teams 中安装应用

```bash
teams app get <teamsAppId> --install-link
```

在浏览器中打开打印的链接——它直接在 Teams 客户端中打开。安装后，向您的机器人发送一条直接消息——它已准备就绪。

---

## 配置参考

### 环境变量

| 变量 | 描述 |
|----------|-------------|
| `TEAMS_CLIENT_ID` | Azure AD 应用（客户端）ID |
| `TEAMS_CLIENT_SECRET` | Azure AD 客户端密钥 |
| `TEAMS_TENANT_ID` | Azure AD 租户 ID |
| `TEAMS_ALLOWED_USERS` | 允许使用机器人的逗号分隔的 AAD 对象 ID |
| `TEAMS_ALLOW_ALL_USERS` | 设置为 `true` 以跳过允许列表并允许任何人 |
| `TEAMS_HOME_CHANNEL` | 用于定时任务/主动消息传递的会话 ID |
| `TEAMS_HOME_CHANNEL_NAME` | 主频道的显示名称 |
| `TEAMS_PORT` | Webhook 端口（默认：`3978`） |

### config.yaml

或者，通过 `~/.hermes/config.yaml` 配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      client_id: "your-client-id"
      client_secret: "your-secret"
      tenant_id: "your-tenant-id"
      port: 3978
```

---

## 功能

### 交互式审批卡片

当 Agent 需要运行潜在危险的命令时，它会发送一张带有四个按钮的自适应卡片，而不是要求您输入 `/approve`：

- **允许一次** — 批准此特定命令
- **允许会话** — 批准此模式用于会话的其余部分
- **始终允许** — 永久批准此模式
- **拒绝** — 拒绝该命令

单击按钮会内联解决审批，并用决定替换卡片。

---

## 生产部署

对于永久服务器，请跳过 devtunnel，并使用您服务器的公共 HTTPS 端点注册您的机器人：

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://your-domain.com/api/messages"
```

如果您已经创建了机器人，只需要更新端点：

```bash
teams app update --id <teamsAppId> --endpoint "https://your-domain.com/api/messages"
```

确保您配置的端口（`TEAMS_PORT`，默认 `3978`）可以从互联网访问，并且您的 TLS 证书有效——Teams 会拒绝自签名证书。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `health` 端点有效但机器人不响应 | 检查您的隧道是否仍在运行，以及机器人的消息传递端点是否与隧道 URL 匹配 |
| 日志中出现 `KeyError: 'teams'` | 重启容器——此问题在当前版本中已修复 |
| 机器人响应身份验证错误 | 验证 `TEAMS_CLIENT_ID`、`TEAMS_CLIENT_SECRET` 和 `TEAMS_TENANT_ID` 是否都正确设置 |
| `No inference provider configured` | 检查 `ANTHROPIC_API_KEY`（或其他提供商密钥）是否在 `~/.hermes/.env` 中设置 |
| 机器人收到消息但忽略它们 | 您的 AAD 对象 ID 可能不在 `TEAMS_ALLOWED_USERS` 中。运行 `teams status --verbose` 来查找它 |
| 隧道 URL 在重启时更改 | 如果您使用命名隧道（`devtunnel create hermes-bot`），devtunnel URL 是持久的。ngrok 和 cloudflared 每次运行都会生成一个新的 URL，除非您有付费计划——当 URL 更改时，使用 `teams app update` 更新机器人端点 |
| Teams 显示“此机器人未响应” | Webhook 返回了错误。检查 `docker logs hermes` 以获取回溯信息 |
| 日志中出现 `[teams] Failed to connect` | SDK 身份验证失败。仔细检查您的凭据以及租户 ID 是否与您在 `teams login` 中使用的帐户匹配 |

---

## 安全

:::warning
**始终设置 `TEAMS_ALLOWED_USERS`**，并填入授权用户的 AAD 对象 ID。如果没有此设置，任何能够找到或安装您的机器人都可以与之交互。

将 `TEAMS_CLIENT_SECRET` 视为密码——定期通过 Azure 门户或 Teams CLI 轮换它。
:::

- 将凭据存储在 `~/.hermes/.env` 中，权限设置为 `600` (`chmod 600 ~/.hermes/.env`)
- 机器人仅接受来自 `TEAMS_ALLOWED_USERS` 中用户的消息；未经授权的消息会被静默丢弃
- 您的公共端点 (`/api/messages`) 由 Teams Bot Framework 进行身份验证——没有有效 JWT 的请求会被拒绝