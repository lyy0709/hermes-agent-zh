---
sidebar_position: 23
title: "Microsoft Graph Webhook 监听器"
description: "在 Hermes 中接收 Microsoft Graph 变更通知（会议、日历、聊天等）"
---

# Microsoft Graph Webhook 监听器

`msgraph_webhook` 消息网关平台是一个入站事件监听器。它是 Hermes 接收来自 Microsoft Graph 的**变更通知**的方式——例如“Teams 会议已结束”、“此聊天中收到新消息”、“此日历事件已更新”。它与 `teams` 平台（用户可与之聊天的聊天机器人）不同——这个平台是 M365 告诉 Hermes 发生了某事，而不是一个人。

目前主要的消费者是 Teams 会议摘要流水线：当会议生成转录文本时，Graph 会发出通知，流水线获取该文本，然后 Hermes 将摘要发布回 Teams。其他 Graph 资源（`/chats/.../messages`、`/users/.../events`）使用相同的监听器——流水线消费者会通过他们自己的 PR 落地。

## 先决条件

- Microsoft Graph 应用程序凭据——[注册 Microsoft Graph 应用程序](/docs/guides/microsoft-graph-app-registration)
- 一个 Microsoft Graph 可以访问的**公共 HTTPS URL**（Graph 不会调用私有端点）。开发隧道适用于测试；生产环境需要一个具有有效证书的真实域名。
- 一个用作 `clientState` 值的强共享密钥。使用 `openssl rand -hex 32` 生成，并将其放入 `~/.hermes/.env` 中，作为 `MSGRAPH_WEBHOOK_CLIENT_STATE`。

## 快速开始

最小 `~/.hermes/config.yaml` 配置：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      port: 8646
      client_state: "replace-with-a-strong-secret"
      accepted_resources:
        - "communications/onlineMeetings"
```

或者通过 `~/.hermes/.env` 中的环境变量（在启动时自动合并）：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<generate-with-openssl-rand-hex-32>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

启动消息网关：`hermes gateway run`。监听器暴露以下端点：

- `POST /msgraph/webhook` —— 来自 Graph 的变更通知
- `GET /msgraph/webhook?validationToken=...` —— Graph 订阅验证握手
- `GET /health` —— 就绪探针，包含已接受/重复计数器

将监听器公开暴露（反向代理、开发隧道、入口）。用于 Graph 订阅的通知 URL 是你的公共 HTTPS 源地址后跟 `/msgraph/webhook`：

```
https://ops.example.com/msgraph/webhook
```

## 配置

所有设置都放在 `platforms.msgraph_webhook.extra` 下：

| 设置 | 默认值 | 描述 |
|---------|---------|-------------|
| `host` | `0.0.0.0` | HTTP 监听器的绑定地址。 |
| `port` | `8646` | 绑定端口。 |
| `webhook_path` | `/msgraph/webhook` | Graph 发送 POST 请求的 URL 路径。 |
| `health_path` | `/health` | 就绪端点。 |
| `client_state` | — | Graph 在每个通知中回显的共享密钥。使用 `hmac.compare_digest` 进行比较——使用 `openssl rand -hex 32` 生成。 |
| `accepted_resources` | `[]`（接受所有） | Graph 资源路径/模式的白名单。尾随的 `*` 作为前缀匹配。开头的 `/` 会被容忍。示例：`["communications/onlineMeetings", "chats/*/messages"]`。 |
| `max_seen_receipts` | `5000` | 用于通知 ID 的去重缓存大小。达到上限时，最旧的条目将被逐出。 |
| `allowed_source_cidrs` | `[]`（允许所有） | 可选的源 IP 白名单。见下文。 |

每个设置也有等效的环境变量（`MSGRAPH_WEBHOOK_*`），在消息网关启动时会合并到配置中——参见[环境变量参考](/docs/reference/environment-variables#microsoft-graph-teams-meetings)。

## 安全加固

### clientState 是主要的身份验证检查

每个 Graph 通知都包含你的订阅注册时使用的 `clientState` 字符串。监听器会拒绝任何 `clientState` 不匹配的通知，并使用时序安全比较。这是 Microsoft 记录的机制——请将此值视为强共享密钥。

如果 `client_state` 未设置，监听器将接受每个格式正确的 POST 请求。**在生产环境中不要在没有设置的情况下运行。**

### 源 IP 白名单（生产部署）

对于生产环境，将监听器限制在 Microsoft 发布的 Graph webhook 源 IP 范围内。Microsoft 在 [Office 365 IP 地址和 URL Web 服务](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) 下记录了出口范围。按如下方式配置它们：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      client_state: "..."
      allowed_source_cidrs:
        - "52.96.0.0/14"
        - "52.104.0.0/14"
        # ...添加当前的 Microsoft 365 "Common" + "Teams" 类别出口范围
```

或者作为环境变量：

```bash
MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS="52.96.0.0/14,52.104.0.0/14"
```

空的白名单 = 接受来自任何地方的请求（默认；保留开发隧道工作流）。无效的 CIDR 字符串会记录警告并被忽略。**请每季度审查 Microsoft IP 列表**——它会变化。

### HTTPS 终止

监听器使用纯 HTTP。在你的反向代理（Caddy、Nginx、Cloudflare Tunnel、AWS ALB）处终止 TLS，并通过本地网络代理到监听器。Graph 拒绝向非 HTTPS 端点发送数据，因此来自 Graph 本身的未加密流量没有路径可以到达你。

### 响应规范

成功时，监听器返回 `202 Accepted` 并带有空响应体——内部计数器不会出现在网络响应中。操作员可以通过 `/health` 观察计数。

状态码表：

| 结果 | 状态码 |
|---------|--------|
| 通知被接受或去重 | 202 |
| 验证握手（带有 `validationToken` 的 GET 请求） | 200（回显令牌） |
| 批次中每个项目都 clientState 验证失败 | 403 |
| 格式错误的 JSON / 缺少 `value` 数组 / 未知资源 | 400 |
| 源 IP 不在白名单中 | 403 |
| 没有 `validationToken` 的裸 GET 请求 | 400 |

## 故障排除

| 问题 | 检查内容 |
|---------|---------------|
| Graph 订阅验证失败 | 公共 URL 可访问，`/msgraph/webhook` 路径匹配，带有 `validationToken` 的 GET 请求在 10 秒内原样回显令牌作为 `text/plain`。 |
| 通知 POST 成功但未摄取任何内容 | `client_state` 与你注册订阅时使用的值匹配。如果值已漂移，请重新运行 `openssl rand -hex 32` 并创建新订阅。检查 `accepted_resources` 是否包含 Graph 正在发送的资源路径。 |
| 每个通知都返回 403 | `clientState` 不匹配（伪造的，或订阅注册时使用了不同的值）。使用 `hermes teams-pipeline subscribe --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE" ...` 重新创建订阅（随流水线运行时 PR 一起提供）。 |
| 监听器启动但 `curl http://localhost:8646/health` 挂起 | 端口绑定冲突。检查 `ss -tlnp \| grep 8646` 并在需要时更改 `port:`。 |
| 来自 Microsoft 的真实 Graph 请求收到 403 | 源 IP 白名单太窄。暂时移除 `allowed_source_cidrs`，确认流量畅通，然后扩大列表以包含当前的 Microsoft 出口范围。 |

## 相关文档

- [注册 Microsoft Graph 应用程序](/docs/guides/microsoft-graph-app-registration) —— Azure 应用注册先决条件
- [环境变量 → Microsoft Graph](/docs/reference/environment-variables#microsoft-graph-teams-meetings) —— 完整的环境变量列表
- [Microsoft Teams 机器人设置](/docs/user-guide/messaging/teams) —— 允许用户在 Teams 中与 Hermes 聊天的不同平台