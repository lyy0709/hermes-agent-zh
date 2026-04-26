---
sidebar_position: 13
title: "Webhooks"
description: "接收来自 GitHub、GitLab 等服务的事件，以触发 Hermes Agent 运行"
---

# Webhooks

接收来自外部服务（GitHub、GitLab、JIRA、Stripe 等）的事件，并自动触发 Hermes Agent 运行。Webhook 适配器运行一个 HTTP 服务器，用于接收 POST 请求、验证 HMAC 签名、将有效载荷转换为 Agent 提示词，并将响应路由回源服务或另一个配置的平台。

Agent 处理事件后，可以通过在 PR 上发布评论、向 Telegram/Discord 发送消息或记录结果来做出响应。

## 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/WNYe5mD4fY8"
    title="Hermes Agent — Webhooks 教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

---

## 快速开始

1. 通过 `hermes gateway setup` 或环境变量启用
2. 在 `config.yaml` 中定义路由 **或** 使用 `hermes webhook subscribe` 动态创建
3. 将你的服务指向 `http://your-server:8644/webhooks/<route-name>`

---

## 设置

有两种方式可以启用 Webhook 适配器。

### 通过设置向导

```bash
hermes gateway setup
```

按照提示启用 Webhooks、设置端口和全局 HMAC 密钥。

### 通过环境变量

添加到 `~/.hermes/.env`：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # 默认值
WEBHOOK_SECRET=your-global-secret
```

### 验证服务器

一旦消息网关运行：

```bash
curl http://localhost:8644/health
```

预期响应：

```json
{"status": "ok", "platform": "webhook"}
```

---

## 配置路由 {#configuring-routes}

路由定义了如何处理不同的 Webhook 来源。每个路由都是 `config.yaml` 中 `platforms.webhook.extra.routes` 下的一个命名条目。

### 路由属性

| 属性 | 必需 | 描述 |
|----------|----------|-------------|
| `events` | 否 | 要接受的事件类型列表（例如 `["pull_request"]`）。如果为空，则接受所有事件。事件类型从 `X-GitHub-Event`、`X-GitLab-Event` 或有效载荷中的 `event_type` 读取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果未在路由上设置，则回退到全局 `secret`。仅用于测试时，可设置为 `"INSECURE_NO_AUTH"`（跳过验证）。 |
| `prompt` | 否 | 使用点号表示法访问有效载荷的模板字符串（例如 `{pull_request.title}`）。如果省略，则完整的 JSON 有效载荷将被转储到提示词中。 |
| `skills` | 否 | 为 Agent 运行加载的技能名称列表。 |
| `deliver` | 否 | 发送响应的位置：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、`mattermost`、`homeassistant`、`email`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 或 `log`（默认）。 |
| `deliver_extra` | 否 | 额外的交付配置 —— 键取决于 `deliver` 类型（例如 `repo`、`pr_number`、`chat_id`）。值支持与 `prompt` 相同的 `{dot.notation}` 模板。 |
| `deliver_only` | 否 | 如果为 `true`，则完全跳过 Agent —— 渲染后的 `prompt` 模板将成为直接发送的字面消息。零 LLM 成本，亚秒级交付。有关用例，请参阅[直接交付模式](#direct-delivery-mode)。要求 `deliver` 是一个真实的目标（不是 `log`）。 |

### 完整示例

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "global-fallback-secret"
      routes:
        github-pr:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            Review this pull request:
            Repository: {repository.full_name}
            PR #{number}: {pull_request.title}
            Author: {pull_request.user.login}
            URL: {pull_request.html_url}
            Diff URL: {pull_request.diff_url}
            Action: {action}
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
        deploy-notify:
          events: ["push"]
          secret: "deploy-secret"
          prompt: "New push to {repository.full_name} branch {ref}: {head_commit.message}"
          deliver: "telegram"
```

### 提示词模板

提示词使用点号表示法来访问 Webhook 有效载荷中的嵌套字段：

- `{pull_request.title}` 解析为 `payload["pull_request"]["title"]`
- `{repository.full_name}` 解析为 `payload["repository"]["full_name"]`
- `{__raw__}` —— 特殊标记，将**整个有效载荷**作为缩进的 JSON 转储（截断为 4000 个字符）。对于监控警报或需要完整上下文的通用 Webhook 很有用。
- 缺失的键将保留为字面字符串 `{key}`（无错误）
- 嵌套的字典和列表会被 JSON 序列化并截断为 2000 个字符

你可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} by {pull_request.user.login}: {__raw__}"
```

如果路由没有配置 `prompt` 模板，则整个有效载荷将作为缩进的 JSON 转储（截断为 4000 个字符）。

相同的点号表示法模板适用于 `deliver_extra` 值。

### 论坛主题交付

当将 Webhook 响应交付到 Telegram 时，你可以通过在 `deliver_extra` 中包含 `message_thread_id`（或 `thread_id`）来定位特定的论坛主题：

```yaml
webhooks:
  routes:
    alerts:
      events: ["alert"]
      prompt: "Alert: {__raw__}"
      deliver: "telegram"
      deliver_extra:
        chat_id: "-1001234567890"
        message_thread_id: "42"
```

如果 `deliver_extra` 中没有提供 `chat_id`，则交付将回退到为目标平台配置的主频道。

---

## GitHub PR 审查（逐步指南） {#github-pr-review}
本教程将指导你为每个拉取请求设置自动代码审查。

### 1. 在 GitHub 中创建 Webhook

1.  进入你的仓库 → **Settings** → **Webhooks** → **Add webhook**
2.  将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3.  将 **Content type** 设置为 `application/json`
4.  将 **Secret** 设置为与你的路由配置匹配的值（例如 `github-webhook-secret`）
5.  在 **Which events?** 下，选择 **Let me select individual events** 并勾选 **Pull requests**
6.  点击 **Add webhook**

### 2. 添加路由配置

将 `github-pr` 路由添加到你的 `~/.hermes/config.yaml` 中，如上文示例所示。

### 3. 确保 `gh` CLI 已认证

`github_comment` 交付类型使用 GitHub CLI 来发布评论：

```bash
gh auth login
```

### 4. 测试

在仓库中打开一个拉取请求。Webhook 触发，Hermes 处理事件，并在 PR 上发布一条审查评论。

---

## GitLab Webhook 设置 {#gitlab-webhook-setup}

GitLab Webhook 的工作方式类似，但使用不同的认证机制。GitLab 将密钥作为纯文本的 `X-Gitlab-Token` 头发送（精确字符串匹配，而非 HMAC）。

### 1. 在 GitLab 中创建 Webhook

1.  进入你的项目 → **Settings** → **Webhooks**
2.  将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3.  输入你的 **Secret token**
4.  选择 **Merge request events**（以及你想要的任何其他事件）
5.  点击 **Add webhook**

### 2. 添加路由配置

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        gitlab-mr:
          events: ["merge_request"]
          secret: "your-gitlab-secret-token"
          prompt: |
            Review this merge request:
            Project: {project.path_with_namespace}
            MR !{object_attributes.iid}: {object_attributes.title}
            Author: {object_attributes.last_commit.author.name}
            URL: {object_attributes.url}
            Action: {object_attributes.action}
          deliver: "log"
```

---

## 交付选项 {#delivery-options}

`deliver` 字段控制在处理完 Webhook 事件后，Agent 的响应发送到哪里。

| 交付类型 | 描述 |
|-------------|-------------|
| `log` | 将响应记录到消息网关的日志输出中。这是默认选项，适用于测试。 |
| `github_comment` | 通过 `gh` CLI 将响应作为 PR/issue 评论发布。需要 `deliver_extra.repo` 和 `deliver_extra.pr_number`。必须在网关主机上安装并认证 `gh` CLI（`gh auth login`）。 |
| `telegram` | 将响应路由到 Telegram。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应路由到 Discord。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应路由到 Slack。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应路由到 Signal。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应路由到 SMS。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `whatsapp` | 将响应路由到 WhatsApp。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `matrix` | 将响应路由到 Matrix。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `mattermost` | 将响应路由到 Mattermost。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `homeassistant` | 将响应路由到 Home Assistant。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `email` | 将响应路由到 Email。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `dingtalk` | 将响应路由到 DingTalk。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `feishu` | 将响应路由到 Feishu/Lark。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `wecom` | 将响应路由到 WeCom。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `weixin` | 将响应路由到 Weixin (WeChat)。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `bluebubbles` | 将响应路由到 BlueBubbles (iMessage)。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |

对于跨平台交付，目标平台也必须在消息网关中启用并连接。如果 `deliver_extra` 中没有提供 `chat_id`，响应将被发送到该平台配置的主频道。

---

## 直接交付模式 {#direct-delivery-mode}

默认情况下，每个 Webhook POST 请求都会触发一次 Agent 运行——负载成为提示词，Agent 处理它，然后 Agent 的响应被交付。这会在每次事件上消耗 LLM Token。

对于你只想**推送纯文本通知**的用例——无需推理，无需 Agent 循环，只需交付消息——请在路由上设置 `deliver_only: true`。渲染后的 `prompt` 模板成为字面消息体，适配器将其直接分派到配置的交付目标。

### 何时使用直接交付

-   **外部服务推送** — Supabase/Firebase Webhook 在数据库变更时触发 → 立即在 Telegram 中通知用户
-   **监控告警** — Datadog/Grafana 告警 Webhook → 推送到 Discord 频道
-   **Agent 间通知** — Agent A 通知 Agent B 的用户一个长时间运行的任务已完成
-   **后台作业完成** — 定时任务完成 → 将结果发布到 Slack

优势：

-   **零 LLM Token** — 从不调用 Agent
-   **亚秒级交付** — 只需一次适配器调用，无需推理循环
-   **与 Agent 模式相同的安全性** — HMAC 认证、速率限制、幂等性和正文大小限制仍然适用
-   **同步响应** — POST 请求在交付成功后返回 `200 OK`，如果目标拒绝则返回 `502`，因此你的上游服务可以智能地重试

### 示例：从 Supabase 推送至 Telegram

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "global-secret"
      routes:
        antenna-matches:
          secret: "antenna-webhook-secret"
          deliver: "telegram"
          deliver_only: true
          prompt: "🎉 New match: {match.user_name} matched with you!"
          deliver_extra:
            chat_id: "{match.telegram_chat_id}"
```
你的 Supabase 边缘函数使用 HMAC-SHA256 对负载进行签名，并 POST 到 `https://your-server:8644/webhooks/antenna-matches`。Webhook 适配器会验证签名，根据负载渲染模板，发送到 Telegram，并返回 `200 OK`。

### 示例：通过 CLI 动态订阅

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

### 响应码

| 状态码 | 含义 |
|--------|---------|
| `200 OK` | 发送成功。响应体：`{"status": "delivered", "route": "...", "target": "...", "delivery_id": "..."}` |
| `200 OK` (status=duplicate) | `X-GitHub-Delivery` ID 在幂等性 TTL（1 小时）内重复。不会重新发送。 |
| `401 Unauthorized` | HMAC 签名无效或缺失。 |
| `400 Bad Request` | JSON 请求体格式错误。 |
| `404 Not Found` | 未知的路由名称。 |
| `413 Payload Too Large` | 请求体超过 `max_body_bytes` 限制。 |
| `429 Too Many Requests` | 路由速率限制已超。 |
| `502 Bad Gateway` | 目标适配器拒绝了消息或引发了异常。错误已在服务器端记录；响应体为通用的 `Delivery failed`，以避免泄露适配器内部信息。 |

### 配置注意事项

- `deliver_only: true` 要求 `deliver` 是一个真实的目标。`deliver: log`（或省略 `deliver`）会在启动时被拒绝——如果适配器发现配置错误的路由，它将拒绝启动。
- 在直接发送模式下，`skills` 字段会被忽略（没有 Agent 运行，因此没有可以注入技能的对象）。
- 模板渲染使用与 Agent 模式相同的 `{dot.notation}` 语法，包括 `{__raw__}` Token。
- 幂等性使用相同的 `X-GitHub-Delivery` / `X-Request-ID` 请求头——使用相同 ID 的重试会返回 `status=duplicate` 并且**不会**重新发送。

---

## 动态订阅 (CLI) {#dynamic-subscriptions}

除了 `config.yaml` 中的静态路由，你还可以使用 `hermes webhook` CLI 命令动态创建 Webhook 订阅。这在 Agent 自身需要设置事件驱动触发器时特别有用。

### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

这将返回 Webhook URL 和一个自动生成的 HMAC 密钥。配置你的服务以 POST 到该 URL。

### 列出订阅

```bash
hermes webhook list
```

### 移除订阅

```bash
hermes webhook remove github-issues
```

### 测试订阅

```bash
hermes webhook test github-issues
hermes webhook test github-issues --payload '{"issue": {"number": 42, "title": "Test"}}'
```

### 动态订阅的工作原理

- 订阅存储在 `~/.hermes/webhook_subscriptions.json`
- Webhook 适配器在每次收到请求时都会热重载此文件（基于修改时间，开销可忽略）
- 来自 `config.yaml` 的静态路由始终优先于同名的动态路由
- 动态订阅使用与静态路由相同的路由格式和功能（事件、提示词模板、技能、发送）
- 无需重启消息网关——订阅后立即生效

### Agent 驱动的订阅

当 Agent 在 `webhook-subscriptions` 技能的引导下，可以通过终端工具创建订阅。要求 Agent “为 GitHub issues 设置一个 webhook”，它将运行相应的 `hermes webhook subscribe` 命令。

---

## 安全性 {#security}

Webhook 适配器包含多层安全措施：

### HMAC 签名验证

适配器使用适合每个来源的方法验证传入的 Webhook 签名：

- **GitHub**: `X-Hub-Signature-256` 请求头——以 `sha256=` 为前缀的 HMAC-SHA256 十六进制摘要
- **GitLab**: `X-Gitlab-Token` 请求头——纯文本密钥字符串匹配
- **通用**: `X-Webhook-Signature` 请求头——原始的 HMAC-SHA256 十六进制摘要

如果配置了密钥但不存在可识别的签名请求头，请求将被拒绝。

### 密钥是必需的

每个路由都必须有一个密钥——可以直接在路由上设置，也可以从全局 `secret` 继承。没有密钥的路由会导致适配器在启动时失败并报错。仅用于开发/测试时，你可以将密钥设置为 `"INSECURE_NO_AUTH"` 以完全跳过验证。

### 速率限制

默认情况下，每个路由的速率限制为**每分钟 30 个请求**（固定窗口）。全局配置如下：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # 每分钟请求数
```

超过限制的请求会收到 `429 Too Many Requests` 响应。

### 幂等性

发送 ID（来自 `X-GitHub-Delivery`、`X-Request-ID` 或时间戳回退）会被缓存**1 小时**。重复的发送（例如 Webhook 重试）会以 `200` 响应静默跳过，防止 Agent 重复运行。

### 请求体大小限制

超过 **1 MB** 的负载会在读取请求体之前被拒绝。配置如下：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### 提示词注入风险

:::warning
Webhook 负载包含攻击者控制的数据——PR 标题、提交消息、问题描述等都可能包含恶意指令。当暴露在互联网上时，请在沙盒环境（Docker、VM）中运行消息网关。考虑使用 Docker 或 SSH 终端后端进行隔离。
:::

---

## 故障排除 {#troubleshooting}

### Webhook 未到达

- 验证端口已暴露且可从 Webhook 源访问
- 检查防火墙规则——端口 `8644`（或你配置的端口）必须开放
- 验证 URL 路径是否匹配：`http://your-server:8644/webhooks/<route-name>`
- 使用 `/health` 端点确认服务器正在运行

### 签名验证失败

- 确保路由配置中的密钥与 Webhook 源中配置的密钥完全匹配
- 对于 GitHub，密钥是基于 HMAC 的——检查 `X-Hub-Signature-256`
- 对于 GitLab，密钥是纯文本 Token 匹配——检查 `X-Gitlab-Token`
- 检查消息网关日志中的 `Invalid signature` 警告
### 事件被忽略

- 检查事件类型是否在路由的 `events` 列表中
- GitHub 事件使用诸如 `pull_request`、`push`、`issues` 等值（即 `X-GitHub-Event` 头的值）
- GitLab 事件使用诸如 `merge_request`、`push` 等值（即 `X-GitLab-Event` 头的值）
- 如果 `events` 为空或未设置，则接受所有事件

### Agent 无响应

- 在前台运行消息网关以查看日志：`hermes gateway run`
- 检查提示词模板是否正确渲染
- 验证投递目标是否已配置并已连接

### 重复响应

- 幂等性缓存应能防止此问题 —— 检查 Webhook 源是否发送了投递 ID 头（`X-GitHub-Delivery` 或 `X-Request-ID`）
- 投递 ID 会缓存 1 小时

### `gh` CLI 错误（GitHub 评论投递）

- 在消息网关主机上运行 `gh auth login`
- 确保经过身份验证的 GitHub 用户对仓库具有写入权限
- 检查 `gh` 是否已安装并在 PATH 中

---

## 环境变量 {#environment-variables}

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 Webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 用于接收 Webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定自身密钥时用作后备） | _(无)_ |