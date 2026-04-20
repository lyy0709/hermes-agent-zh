---
sidebar_position: 11
sidebar_label: "通过 Webhook 进行 GitHub PR 评审"
title: "使用 Webhook 实现 GitHub PR 评论自动化"
description: "将 Hermes 连接到 GitHub，使其自动获取 PR 差异、评审代码变更并发布评论——由 Webhook 触发，无需手动提示"
---

# 使用 Webhook 实现 GitHub PR 评论自动化

本指南将引导您将 Hermes Agent 连接到 GitHub，使其在 PR 被打开或更新时，自动获取差异、分析代码变更并发布评论——整个过程由 Webhook 事件触发，无需手动提示。

当 PR 被打开或更新时，GitHub 会向您的 Hermes 实例发送一个 Webhook POST 请求。Hermes 会运行 Agent，并附带一个提示词，指示其通过 `gh` CLI 获取差异，然后将响应发布回 PR 讨论串。

:::tip 想要更简单的设置，无需公共端点？
如果您没有公共 URL 或者只是想快速开始，请查看[构建 GitHub PR 评审 Agent](./github-pr-review-agent.md)——它使用定时任务按计划轮询 PR，可在 NAT 和防火墙后工作。
:::

:::info 参考文档
有关完整的 Webhook 平台参考（所有配置选项、交付类型、动态订阅、安全模型），请参阅 [Webhooks](/docs/user-guide/messaging/webhooks)。
:::

:::warning 提示词注入风险
Webhook 负载包含攻击者控制的数据——PR 标题、提交消息和描述可能包含恶意指令。当您的 Webhook 端点暴露在互联网上时，请在沙盒环境（Docker、SSH 后端）中运行消息网关。请参阅下面的[安全注意事项](#security-notes)部分。
:::

---

## 先决条件

- 已安装并运行 Hermes Agent (`hermes gateway`)
- 在消息网关主机上已安装并认证 [`gh` CLI](https://cli.github.com/) (`gh auth login`)
- 您的 Hermes 实例有一个可公开访问的 URL（如果在本地运行，请参阅[使用 ngrok 进行本地测试](#local-testing-with-ngrok)）
- 对 GitHub 仓库拥有管理员访问权限（管理 Webhook 所需）

---

## 步骤 1 — 启用 Webhook 平台

将以下内容添加到您的 `~/.hermes/config.yaml`：

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644          # 默认值；如果其他服务占用此端口，请更改
      rate_limit: 30      # 每个路由每分钟的最大请求数（非全局限制）

      routes:
        github-pr-review:
          secret: "your-webhook-secret-here"   # 必须与 GitHub Webhook 密钥完全匹配
          events:
            - pull_request

          # Agent 被指示在评审前获取实际的差异。
          # {number} 和 {repository.full_name} 从 GitHub 负载中解析。
          prompt: |
            收到一个拉取请求事件（操作：{action}）。

            PR #{number}: {pull_request.title}
            作者: {pull_request.user.login}
            分支: {pull_request.head.ref} → {pull_request.base.ref}
            描述: {pull_request.body}
            网址: {pull_request.html_url}

            如果操作是 "closed" 或 "labeled"，请在此停止，不要发布评论。

            否则：
            1. 运行：gh pr diff {number} --repo {repository.full_name}
            2. 评审代码变更的正确性、安全问题和清晰度。
            3. 撰写一个简洁、可操作的评审评论并发布。

          deliver: github_comment
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
```

**关键字段：**

| 字段 | 描述 |
|---|---|
| `secret` (路由级别) | 此路由的 HMAC 密钥。如果省略，则回退到全局的 `extra.secret`。 |
| `events` | 要接受的 `X-GitHub-Event` 标头值列表。空列表 = 接受所有。 |
| `prompt` | 模板；`{field}` 和 `{nested.field}` 从 GitHub 负载中解析。 |
| `deliver` | `github_comment` 通过 `gh pr comment` 发布。`log` 仅写入消息网关日志。 |
| `deliver_extra.repo` | 从负载解析为例如 `org/repo`。 |
| `deliver_extra.pr_number` | 从负载解析为 PR 编号。 |

:::note 负载不包含代码
GitHub Webhook 负载包含 PR 元数据（标题、描述、分支名称、URL），但**不包含差异**。上面的提示词指示 Agent 运行 `gh pr diff` 来获取实际的变更。`terminal` 工具已包含在默认的 `hermes-webhook` 工具集中，因此无需额外配置。
:::

---

## 步骤 2 — 启动消息网关

```bash
hermes gateway
```

您应该看到：

```
[webhook] Listening on 0.0.0.0:8644 — routes: github-pr-review
```

验证其是否正在运行：

```bash
curl http://localhost:8644/health
# {"status": "ok", "platform": "webhook"}
```

---

## 步骤 3 — 在 GitHub 上注册 Webhook

1.  转到您的仓库 → **Settings** → **Webhooks** → **Add webhook**
2.  填写：
    - **Payload URL:** `https://your-public-url.example.com/webhooks/github-pr-review`
    - **Content type:** `application/json`
    - **Secret:** 与您在路由配置中为 `secret` 设置的值相同
    - **Which events?** → Select individual events → 勾选 **Pull requests**
3.  点击 **Add webhook**

GitHub 将立即发送一个 `ping` 事件来确认连接。它会被安全地忽略——`ping` 不在您的 `events` 列表中——并返回 `{"status": "ignored", "event": "ping"}`。它仅在 DEBUG 级别记录，因此在默认日志级别下不会出现在控制台中。

---

## 步骤 4 — 打开一个测试 PR

创建一个分支，推送一个变更，并打开一个 PR。在 30-90 秒内（取决于 PR 大小和模型），Hermes 应该会发布一条评审评论。

要实时跟踪 Agent 的进度：

```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

---

## 使用 ngrok 进行本地测试

如果 Hermes 在您的笔记本电脑上运行，请使用 [ngrok](https://ngrok.com/) 将其暴露：

```bash
ngrok http 8644
```

复制 `https://...ngrok-free.app` URL 并将其用作您的 GitHub Payload URL。在免费的 ngrok 套餐中，每次 ngrok 重启时 URL 都会更改——每次会话都需要更新您的 GitHub Webhook。付费的 ngrok 账户可以获得静态域名。
你可以直接用 `curl` 对静态路由进行冒烟测试——无需 GitHub 账号或真实的 PR。

:::tip 本地测试时使用 `deliver: log`
在测试时，将配置中的 `deliver: github_comment` 改为 `deliver: log`。否则，Agent 会尝试向测试负载中的假 `org/repo#99` 仓库发布评论，这将导致失败。当你对提示词输出满意后，再切换回 `deliver: github_comment`。
:::

```bash
SECRET="your-webhook-secret-here"
BODY='{"action":"opened","number":99,"pull_request":{"title":"Test PR","body":"Adds a feature.","user":{"login":"testuser"},"head":{"ref":"feat/x"},"base":{"ref":"main"},"html_url":"https://github.com/org/repo/pull/99"},"repository":{"full_name":"org/repo"}}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -hex | awk '{print "sha256="$2}')

curl -s -X POST http://localhost:8644/webhooks/github-pr-review \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: $SIG" \
  -d "$BODY"
# 期望输出: {"status":"accepted","route":"github-pr-review","event":"pull_request","delivery_id":"..."}
```

然后观察 Agent 运行：
```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

:::note
`hermes webhook test <name>` 仅适用于通过 `hermes webhook subscribe` 创建的**动态订阅**。它不会读取 `config.yaml` 中的路由。
:::

---

## 过滤特定操作

GitHub 会为许多操作发送 `pull_request` 事件：`opened`、`synchronize`、`reopened`、`closed`、`labeled` 等。`events` 列表仅通过 `X-GitHub-Event` 头部值进行过滤——它无法在路由级别按操作子类型进行过滤。

步骤 1 中的提示词已经通过指示 Agent 对 `closed` 和 `labeled` 事件提前停止来处理这个问题。

:::warning Agent 仍然会运行并消耗 Token
“在此停止”的指令阻止了有意义的审查，但无论是什么操作，Agent 仍然会为每个 `pull_request` 事件运行完成。GitHub webhook 只能按事件类型（`pull_request`、`push`、`issues` 等）过滤——不能按操作子类型（`opened`、`closed`、`labeled`）过滤。没有针对子操作的路由级过滤器。对于高流量的仓库，要么接受这个成本，要么使用 GitHub Actions 工作流在上游进行过滤，有条件地调用你的 webhook URL。
:::

> 没有 Jinja2 或条件模板语法。`{field}` 和 `{nested.field}` 是唯一支持的替换。其他任何内容都会按原样传递给 Agent。

---

## 使用技能确保一致的审查风格

加载一个 [Hermes 技能](/docs/user-guide/features/skills) 来赋予 Agent 一致的审查人格。在 `config.yaml` 的 `platforms.webhook.extra.routes` 内，为你的路由添加 `skills`：

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        github-pr-review:
          secret: "your-webhook-secret-here"
          events: [pull_request]
          prompt: |
            A pull request event was received (action: {action}).
            PR #{number}: {pull_request.title} by {pull_request.user.login}
            URL: {pull_request.html_url}

            If the action is "closed" or "labeled", stop here and do not post a comment.

            Otherwise:
            1. Run: gh pr diff {number} --repo {repository.full_name}
            2. Review the diff using your review guidelines.
            3. Write a concise, actionable review comment and post it.
          skills:
            - review
          deliver: github_comment
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
```

> **注意：** 只会加载列表中找到的第一个技能。Hermes 不会堆叠多个技能——后续条目将被忽略。

---

## 将响应发送到 Slack 或 Discord

将路由内的 `deliver` 和 `deliver_extra` 字段替换为目标平台：

```yaml
# 在 platforms.webhook.extra.routes.<route-name> 内：

# Slack
deliver: slack
deliver_extra:
  chat_id: "C0123456789"   # Slack 频道 ID（省略则使用配置的主频道）

# Discord
deliver: discord
deliver_extra:
  chat_id: "987654321012345678"  # Discord 频道 ID（省略则使用主频道）
```

目标平台也必须在消息网关中启用并连接。如果省略 `chat_id`，响应将发送到该平台配置的主频道。

有效的 `deliver` 值：`log` · `github_comment` · `telegram` · `discord` · `slack` · `signal` · `sms`

---

## GitLab 支持

同一个适配器也适用于 GitLab。GitLab 使用 `X-Gitlab-Token` 进行身份验证（纯字符串匹配，非 HMAC）——Hermes 会自动处理两者。

对于事件过滤，GitLab 将 `X-GitLab-Event` 设置为诸如 `Merge Request Hook`、`Push Hook`、`Pipeline Hook` 等值。在 `events` 中使用确切的头部值：

```yaml
events:
  - Merge Request Hook
```

GitLab 的负载字段与 GitHub 不同——例如，MR 标题是 `{object_attributes.title}`，MR 编号是 `{object_attributes.iid}`。发现完整负载结构最简单的方法是使用 GitLab webhook 设置中的**测试**按钮，结合**最近交付**日志。或者，从你的路由配置中省略 `prompt`——这样 Hermes 会将完整的负载作为格式化 JSON 直接传递给 Agent，而 Agent 的响应（在消息网关日志中通过 `deliver: log` 可见）将描述其结构。

---

## 安全注意事项

- **切勿在生产环境中使用 `INSECURE_NO_AUTH`**——它会完全禁用签名验证。它仅用于本地开发。
- **定期轮换你的 webhook 密钥**，并在 GitHub（webhook 设置）和你的 `config.yaml` 中更新它。
- **速率限制** 默认每个路由为 30 次/分钟（可通过 `extra.rate_limit` 配置）。超出限制将返回 `429`。
- **重复交付**（webhook 重试）通过 1 小时幂等性缓存进行去重。缓存键是 `X-GitHub-Delivery`（如果存在），然后是 `X-Request-ID`，然后是毫秒级时间戳。当两个交付 ID 头部都未设置时，重试**不会**被去重。
- **提示词注入：** PR 标题、描述和提交消息是攻击者可控的。恶意 PR 可能试图操纵 Agent 的行为。当暴露在公共互联网时，请在沙盒环境（Docker、VM）中运行消息网关。
---

## 故障排除

| 症状 | 检查项 |
|---|---|
| `401 Invalid signature` | config.yaml 中的密钥与 GitHub webhook 密钥不匹配 |
| `404 Unknown route` | URL 中的路由名称与 `routes:` 中的键不匹配 |
| `429 Rate limit exceeded` | 每个路由每分钟 30 个请求的限制被超出 — 从 GitHub UI 重新投递测试事件时常见；等待一分钟或提高 `extra.rate_limit` |
| 未发布评论 | `gh` 未安装、不在 PATH 中或未认证 (`gh auth login`) |
| Agent 运行但无评论 | 检查消息网关日志 — 如果 Agent 输出为空或仅为 "SKIP"，仍会尝试投递 |
| 端口已被占用 | 更改 config.yaml 中的 `extra.port` |
| Agent 运行但仅审查 PR 描述 | 提示词未包含 `gh pr diff` 指令 — 差异内容不在 webhook 有效载荷中 |
| 看不到 ping 事件 | 被忽略的事件仅在 DEBUG 日志级别返回 `{"status":"ignored","event":"ping"}` — 检查 GitHub 的投递日志（仓库 → Settings → Webhooks → 你的 webhook → Recent Deliveries） |

**GitHub 的 Recent Deliveries 标签页**（仓库 → Settings → Webhooks → 你的 webhook）显示每次投递的确切请求头、有效载荷、HTTP 状态和响应体。这是在不接触服务器日志的情况下诊断故障的最快方法。

---

## 完整配置参考

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"         # 绑定地址 (默认: 0.0.0.0)
      port: 8644               # 监听端口 (默认: 8644)
      secret: ""               # 可选的全局备用密钥
      rate_limit: 30           # 每个路由每分钟请求数
      max_body_bytes: 1048576  # 有效载荷大小限制，单位字节 (默认: 1 MB)

      routes:
        <route-name>:
          secret: "required-per-route"
          events: []            # [] = 接受所有；否则列出 X-GitHub-Event 值
          prompt: ""            # 从有效载荷解析 {field} / {nested.field}
          skills: []            # 加载第一个匹配的技能（仅一个）
          deliver: "log"        # log | github_comment | telegram | discord | slack | signal | sms
          deliver_extra: {}     # github_comment 的 repo + pr_number；其他方式的 chat_id
```

---

## 下一步

- **[基于定时任务的 PR 审查](./github-pr-review-agent.md)** — 按计划轮询 PR，无需公共端点
- **[Webhook 参考](/docs/user-guide/messaging/webhooks)** — webhook 平台的完整配置参考
- **[构建插件](/docs/guides/build-a-hermes-plugin)** — 将审查逻辑打包成可共享的插件
- **[配置文件](/docs/user-guide/profiles)** — 使用具有独立记忆和配置的专用审查员配置文件运行