---
title: "Webhook 订阅"
sidebar_label: "Webhook 订阅"
description: "创建和管理 Webhook 订阅，用于事件驱动的 Agent 激活，或用于直接推送通知（零 LLM 成本）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Webhook 订阅

创建和管理 Webhook 订阅，用于事件驱动的 Agent 激活，或用于直接推送通知（零 LLM 成本）。当用户希望外部服务触发 Agent 运行或将通知推送到聊天时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/webhook-subscriptions` |
| 版本 | `1.1.0` |
| 标签 | `webhook`, `events`, `automation`, `integrations`, `notifications`, `push` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Webhook 订阅

创建动态 Webhook 订阅，以便外部服务（GitHub、GitLab、Stripe、CI/CD、IoT 传感器、监控工具）可以通过向 URL 发送 POST 事件来触发 Hermes Agent 运行。

## 设置（首次必需）

必须先启用 Webhook 平台，然后才能创建订阅。使用以下命令检查：
```bash
hermes webhook list
```

如果显示 "Webhook platform is not enabled"，请按以下方式设置：

### 选项 1：设置向导
```bash
hermes gateway setup
```
按照提示启用 Webhook、设置端口并设置全局 HMAC 密钥。

### 选项 2：手动配置
添加到 `~/.hermes/config.yaml`：
```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "generate-a-strong-secret-here"
```

### 选项 3：环境变量
添加到 `~/.hermes/.env`：
```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644
WEBHOOK_SECRET=generate-a-strong-secret-here
```

配置后，启动（或重启）消息网关：
```bash
hermes gateway run
# 或者如果使用 systemd：
systemctl --user restart hermes-gateway
```

验证其是否正在运行：
```bash
curl http://localhost:8644/health
```

## 命令

所有管理都通过 `hermes webhook` CLI 命令进行：

### 创建订阅
```bash
hermes webhook subscribe <name> \
  --prompt "Prompt template with {payload.fields}" \
  --events "event1,event2" \
  --description "What this does" \
  --skills "skill1,skill2" \
  --deliver telegram \
  --deliver-chat-id "12345" \
  --secret "optional-custom-secret"
```

返回 Webhook URL 和 HMAC 密钥。用户配置其服务以 POST 到该 URL。

### 列出订阅
```bash
hermes webhook list
```

### 移除订阅
```bash
hermes webhook remove <name>
```

### 测试订阅
```bash
hermes webhook test <name>
hermes webhook test <name> --payload '{"key": "value"}'
```

## 提示词模板

提示词支持使用 `{dot.notation}` 来访问嵌套的有效负载字段：

- `{issue.title}` — GitHub issue 标题
- `{pull_request.user.login}` — PR 作者
- `{data.object.amount}` — Stripe 支付金额
- `{sensor.temperature}` — IoT 传感器读数

如果未指定提示词，则完整的 JSON 有效负载将被转储到 Agent 提示词中。

## 常见模式

### GitHub：新 issue
```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue #{issue.number}: {issue.title}\n\nAction: {action}\nAuthor: {issue.user.login}\nBody:\n{issue.body}\n\nPlease triage this issue." \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

然后在 GitHub 仓库设置 → Webhooks → 添加 webhook：
- 有效负载 URL：返回的 webhook_url
- 内容类型：application/json
- 密钥：返回的 secret
- 事件："Issues"

### GitHub：PR 审查
```bash
hermes webhook subscribe github-prs \
  --events "pull_request" \
  --prompt "PR #{pull_request.number} {action}: {pull_request.title}\nBy: {pull_request.user.login}\nBranch: {pull_request.head.ref}\n\n{pull_request.body}" \
  --skills "github-code-review" \
  --deliver github_comment
```

### Stripe：支付事件
```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed" \
  --prompt "Payment {data.object.status}: {data.object.amount} cents from {data.object.receipt_email}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

### CI/CD：构建通知
```bash
hermes webhook subscribe ci-builds \
  --events "pipeline" \
  --prompt "Build {object_attributes.status} on {project.name} branch {object_attributes.ref}\nCommit: {commit.message}" \
  --deliver discord \
  --deliver-chat-id "1234567890"
```

### 通用监控告警
```bash
hermes webhook subscribe alerts \
  --prompt "Alert: {alert.name}\nSeverity: {alert.severity}\nMessage: {alert.message}\n\nPlease investigate and suggest remediation." \
  --deliver origin
```

### 直接投递（无 Agent，零 LLM 成本）

对于您只想将通知推送到用户聊天中的用例——无需推理，无 Agent 循环——添加 `--deliver-only`。渲染后的 `--prompt` 模板成为字面消息正文，并直接分派到目标适配器。

用于：
- 外部服务推送通知（Supabase/Firebase webhooks → Telegram）
- 应原样转发的监控告警
- Agent 间通信，其中一个 Agent 告诉另一个 Agent 的用户某事
- 任何 LLM 往返将是浪费精力的 Webhook

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

POST 在成功投递时返回 `200 OK`，在目标失败时返回 `502`——因此上游服务可以智能地重试。HMAC 认证、速率限制和幂等性仍然适用。

要求 `--deliver` 是一个真实的目标（telegram、discord、slack、github_comment 等）——`--deliver log` 会被拒绝，因为仅记录的直接投递没有意义。

## 安全性

- 每个订阅都会获得一个自动生成的 HMAC-SHA256 密钥（或使用 `--secret` 提供您自己的密钥）
- Webhook 适配器验证每个传入 POST 的签名
- 来自 config.yaml 的静态路由不能被动态订阅覆盖
- 订阅持久化到 `~/.hermes/webhook_subscriptions.json`

## 工作原理

1. `hermes webhook subscribe` 写入 `~/.hermes/webhook_subscriptions.json`
2. Webhook 适配器在每次传入请求时热重载此文件（基于修改时间门控，开销可忽略）
3. 当 POST 到达匹配路由时，适配器格式化提示词并触发 Agent 运行
4. Agent 的响应被投递到配置的目标（Telegram、Discord、GitHub 评论等）

## 故障排除

如果 Webhook 不工作：

1. **消息网关在运行吗？** 使用 `systemctl --user status hermes-gateway` 或 `ps aux | grep gateway` 检查
2. **Webhook 服务器在监听吗？** `curl http://localhost:8644/health` 应返回 `{"status": "ok"}`
3. **检查消息网关日志：** `grep webhook ~/.hermes/logs/gateway.log | tail -20`
4. **签名不匹配？** 验证您服务中的密钥是否与 `hermes webhook list` 返回的密钥匹配。GitHub 发送 `X-Hub-Signature-256`，GitLab 发送 `X-Gitlab-Token`。
5. **防火墙/NAT？** Webhook URL 必须可从服务访问。对于本地开发，请使用隧道（ngrok、cloudflared）。
6. **事件类型错误？** 检查 `--events` 过滤器是否匹配服务发送的内容。使用 `hermes webhook test <name>` 验证路由是否有效。