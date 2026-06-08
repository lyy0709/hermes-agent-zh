---
sidebar_position: 23
title: "Microsoft Graph Webhook 监听器"
description: "在 Hermes 中接收 Microsoft Graph 变更通知（会议、日历、聊天等）"
---

# Microsoft Graph Webhook 监听器

`msgraph_webhook` 消息网关平台是一个入站事件监听器。它是 Hermes 接收来自 Microsoft Graph 的**变更通知**的方式——"Teams 会议已结束"、"此聊天中收到新消息"、"此日历事件已更新"。不同于 `teams` 平台（用户可与之聊天的聊天机器人）——这个平台是 M365 告诉 Hermes 发生了某事，而不是一个人。

目前主要的消费者是 Teams 会议摘要流水线：当会议生成转录文本时 Graph 会通知，流水线获取它，然后 Hermes 将摘要发布回 Teams。其他 Graph 资源（`/chats/.../messages`、`/users/.../events`）使用相同的监听器——流水线消费者会通过他们自己的 PR 落地。

## 先决条件

- Microsoft Graph 应用程序凭据——[注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration)
- Microsoft Graph 可以访问的**公共 HTTPS URL**（Graph 不调用私有端点）。开发隧道可用于测试；生产环境需要具有有效证书的真实域名。
- 用作 `clientState` 值的强共享密钥。使用 `openssl rand -hex 32` 生成，并将其放入 `~/.hermes/.env` 作为 `MSGRAPH_WEBHOOK_CLIENT_STATE`。

## 快速开始

最小 `~/.hermes/config.yaml`：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8646
      client_state: "replace-with-a-strong-secret"
      accepted_resources:
        - "communications/onlineMeetings"
```

或通过 `~/.hermes/.env` 中的环境变量（启动时自动合并）：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<generate-with-openssl-rand-hex-32>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

注意：绑定主机从 `config.yaml` 中的 `extra.host` 读取（参见上面的示例）；没有 `MSGRAPH_WEBHOOK_HOST` 环境变量覆盖。

启动网关：`hermes gateway run`。监听器暴露：

- `POST /msgraph/webhook` —— 来自 Graph 的变更通知
- `GET /msgraph/webhook?validationToken=...` —— Graph 订阅验证握手
- `GET /health` —— 就绪探针，包含已接受/重复计数器

将监听器公开暴露（反向代理、开发隧道、入口）。您用于 Graph 订阅的通知 URL 是您的公共 HTTPS 源地址后跟 `/msgraph/webhook`：

```
https://ops.example.com/msgraph/webhook
```

## 配置

所有设置都放在 `platforms.msgraph_webhook.extra` 下：

| 设置 | 默认值 | 描述 |
|---------|---------|-------------|
| `host` | `0.0.0.0` | HTTP 监听器的绑定地址。非回环绑定需要 `allowed_source_cidrs`；回环地址（`127.0.0.1` / `::1`）是最简单的开发隧道/反向代理设置。 |
| `port` | `8646` | 绑定端口。 |
| `webhook_path` | `/msgraph/webhook` | Graph POST 请求的 URL 路径。 |
| `health_path` | `/health` | 就绪端点。 |
| `client_state` | — | Graph 在每个通知中回显的共享密钥。使用 `hmac.compare_digest` 进行比较——用 `openssl rand -hex 32` 生成。 |
| `accepted_resources` | `[]`（接受所有） | Graph 资源路径/模式的白名单。尾随 `*` 作为前缀匹配。开头的 `/` 可以容忍。示例：`["communications/onlineMeetings", "chats/*/messages"]`。 |
| `max_seen_receipts` | `5000` | 通知 ID 的去重缓存大小。达到上限时驱逐最旧的条目。 |
| `allowed_source_cidrs` | `[]` | 非回环绑定所必需。仅当监听器绑定到回环地址并由本地隧道/反向代理前置时才留空。 |

大多数设置也有等效的环境变量（`MSGRAPH_WEBHOOK_*`），在网关启动时合并到配置中（例外是 `host`，它仅通过配置——参见上面的说明）——参见[环境变量参考](/reference/environment-variables#microsoft-graph-teams-meetings)。

## 安全加固

### clientState 是主要的身份验证检查

每个 Graph 通知都包含您的订阅注册时使用的 `clientState` 字符串。监听器拒绝任何 `clientState` 不匹配的通知，使用时序安全比较。这是微软记录的机制——将该值视为强共享密钥。

如果 `client_state` 未设置，监听器拒绝启动。

### 源 IP 白名单（生产部署）

对于生产环境，将监听器限制在微软发布的 Graph webhook 源 IP 范围。微软在 [Office 365 IP 地址和 URL Web 服务](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) 下记录了出口范围。将它们配置为：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 0.0.0.0
      client_state: "..."
      allowed_source_cidrs:
        - "52.96.0.0/14"
        - "52.104.0.0/14"
        # ...添加当前的 Microsoft 365 "Common" + "Teams" 类别出口范围
```

或作为环境变量：

```bash
MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS="52.96.0.0/14,52.104.0.0/14"
```

绑定非回环主机（如 `0.0.0.0`、`::` 或 LAN IP）而没有 `allowed_source_cidrs` 会在启动时被拒绝。如果您在同一台机器上使用开发隧道或反向代理，请将 Hermes 绑定到 `127.0.0.1` 或 `::1`，并将白名单留空。无效的 CIDR 字符串会记录警告并被忽略。**每季度审查微软 IP 列表**——它会变化。

### HTTPS 终止

监听器使用普通 HTTP。在您的反向代理（Caddy、Nginx、Cloudflare Tunnel、AWS ALB）处终止 TLS，并通过本地网络代理到监听器。Graph 拒绝传送到非 HTTPS 端点，因此没有未加密流量从 Graph 本身到达您的路径。

### 响应卫生

成功时，监听器返回 `202 Accepted` 并带有空正文——内部计数器不进入线路响应。操作员可以通过 `/health` 观察计数，该端点受与 webhook 路径相同的源 IP 规则保护。

状态码表：

| 结果 | 状态 |
|---------|--------|
| 通知已接受或已去重 | 202 |
| 验证握手（带有 `validationToken` 的 GET） | 200（回显令牌） |
| 批次中每个项目都 clientState 失败 | 403 |
| 格式错误的 JSON / 缺少 `value` 数组 / 未知资源 | 400 |
| 源 IP 不在白名单中 | 403 |
| 没有 `validationToken` 的裸 GET | 400 |

## 故障排除

| 问题 | 检查内容 |
|---------|---------------|
| Graph 订阅验证失败 | 公共 URL 可访问，`/msgraph/webhook` 路径匹配，带有 `validationToken` 的 GET 在 10 秒内逐字回显令牌为 `text/plain`。 |
| 通知 POST 但未摄取任何内容 | `client_state` 与您注册订阅时使用的值匹配。如果值已漂移，重新运行 `openssl rand -hex 32` 并创建新订阅。检查 `accepted_resources` 是否包含 Graph 正在发送的资源路径。 |
| 每个通知都返回 403 | `clientState` 不匹配（伪造的，或订阅注册时使用了不同的值）。使用 `hermes teams-pipeline subscribe --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE" ...` 重新创建订阅（随流水线运行时 PR 一起提供）。 |
| 监听器在 `0.0.0.0` 上拒绝启动 | 将 `allowed_source_cidrs` 设置为微软当前的 webhook 出口范围，或将 Hermes 绑定到 `127.0.0.1` / `::1` 并在您的隧道或反向代理后面。 |
| 监听器启动但 `curl http://localhost:8646/health` 挂起 | 端口绑定冲突。检查 `ss -tlnp \| grep 8646` 并在需要时更改 `port:`。 |
| 来自微软的真实 Graph 请求被 403 | 源 IP 白名单太窄。扩大列表以包含当前的微软出口范围。如果您仍在验证隧道路径，请将 Hermes 绑定到回环地址，并让隧道处理公共暴露。 |

## 相关文档

- [注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration) —— Azure 应用注册先决条件
- [环境变量 → Microsoft Graph](/reference/environment-variables#microsoft-graph-teams-meetings) —— 完整环境变量列表
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams) —— 允许用户在 Teams 中与 Hermes 聊天的不同平台