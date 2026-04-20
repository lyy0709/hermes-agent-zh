---
sidebar_position: 10
title: "教程：GitHub PR 审查 Agent"
description: "构建一个自动化的 AI 代码审查器，监控你的代码库、审查拉取请求并交付反馈——完全无需手动操作"
---

# 教程：构建一个 GitHub PR 审查 Agent

**问题所在：** 你的团队创建 PR 的速度比你审查的速度还快。PR 等待审查的时间长达数天。初级开发者合并了有 bug 的代码，因为没人有时间检查。你每天早晨都在追赶代码差异，而不是构建新功能。

**解决方案：** 一个全天候监控你代码库的 AI Agent，审查每个新 PR 的 bug、安全问题和代码质量，并发送摘要给你——这样你只需将时间花在真正需要人工判断的 PR 上。

**你将构建的内容：**

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
│  定时任务    │────▶│  Hermes Agent │────▶│  GitHub API  │────▶│  审查结果    │
│  (每 2 小时) │     │  + gh CLI     │     │  (PR 差异)   │     │  发送到      │
│              │     │  + 技能       │     │              │     │  Telegram/   │
│              │     │  + 记忆       │     │              │     │  Discord/    │
│              │     │               │     │              │     │  本地文件    │
└──────────────┘     └───────────────┘     └──────────────┘     └──────────────┘
```

本指南使用**定时任务**按计划轮询 PR——无需服务器或公共端点。可在 NAT 和防火墙后工作。

:::tip 想要实时审查？
如果你有可用的公共端点，请查看[使用 Webhook 实现自动化 GitHub PR 评论](./webhook-github-pr-review.md)——当 PR 被创建或更新时，GitHub 会立即将事件推送给 Hermes。
:::

---

## 先决条件

- **已安装 Hermes Agent** — 参见[安装指南](/docs/getting-started/installation)
- **消息网关正在运行**以支持定时任务：
  ```bash
  hermes gateway install   # 安装为服务
  # 或
  hermes gateway           # 在前台运行
  ```
- **已安装并认证 GitHub CLI (`gh`)**：
  ```bash
  # 安装
  brew install gh        # macOS
  sudo apt install gh    # Ubuntu/Debian

  # 认证
  gh auth login
  ```
- **已配置消息传递**（可选）— [Telegram](/docs/user-guide/messaging/telegram) 或 [Discord](/docs/user-guide/messaging/discord)

:::tip 没有消息传递？没问题
使用 `deliver: "local"` 将审查结果保存到 `~/.hermes/cron/output/`。非常适合在连接通知之前进行测试。
:::

---

## 步骤 1：验证设置

确保 Hermes 可以访问 GitHub。启动一个聊天会话：

```bash
hermes
```

用一个简单的命令测试：

```
Run: gh pr list --repo NousResearch/hermes-agent --state open --limit 3
```

你应该能看到一个打开的 PR 列表。如果这能正常工作，你就准备好了。

---

## 步骤 2：尝试手动审查

仍在聊天会话中，让 Hermes 审查一个真实的 PR：

```
Review this pull request. Read the diff, check for bugs, security issues,
and code quality. Be specific about line numbers and quote problematic code.

Run: gh pr diff 3888 --repo NousResearch/hermes-agent
```

Hermes 将：
1. 执行 `gh pr diff` 以获取代码变更
2. 通读整个差异
3. 生成一个包含具体发现的结构化审查报告

如果你对审查质量满意，就可以开始自动化了。

---

## 步骤 3：创建一个审查技能

技能为 Hermes 提供了一致的审查指南，这些指南在会话和定时任务运行之间持续存在。没有技能，审查质量会参差不齐。

```bash
mkdir -p ~/.hermes/skills/code-review
```

创建 `~/.hermes/skills/code-review/SKILL.md`：

```markdown
---
name: code-review
description: Review pull requests for bugs, security issues, and code quality
---

# 代码审查指南

审查拉取请求时：

## 检查内容
1. **Bug** — 逻辑错误、差一错误、空值/未定义处理
2. **安全** — 注入、认证绕过、代码中的密钥、SSRF
3. **性能** — N+1 查询、无限循环、内存泄漏
4. **风格** — 命名约定、死代码、缺少错误处理
5. **测试** — 变更是否经过测试？测试是否覆盖边界情况？

## 输出格式
对于每个发现：
- **文件:行号** — 确切位置
- **严重性** — 严重 / 警告 / 建议
- **问题描述** — 一句话
- **修复建议** — 如何修复

## 规则
- 要具体。引用有问题的代码。
- 除非影响可读性，否则不要标记风格上的吹毛求疵。
- 如果 PR 看起来不错，就如实说明。不要捏造问题。
- 以以下内容结尾：APPROVE / REQUEST_CHANGES / COMMENT
```

验证它是否已加载——启动 `hermes`，你应该能在启动时的技能列表中看到 `code-review`。

---

## 步骤 4：教它你的团队规范

这才是让审查员真正有用的地方。启动一个会话，教 Hermes 你团队的标准：

```
Remember: In our backend repo, we use Python with FastAPI.
All endpoints must have type annotations and Pydantic models.
We don't allow raw SQL — only SQLAlchemy ORM.
Test files go in tests/ and must use pytest fixtures.
```

```
Remember: In our frontend repo, we use TypeScript with React.
No `any` types allowed. All components must have props interfaces.
We use React Query for data fetching, never useEffect for API calls.
```

这些记忆会永久保存——审查员将强制执行你的规范，而无需每次都被告知。

---

## 步骤 5：创建自动化定时任务

现在将所有部分连接起来。创建一个每 2 小时运行一次的定时任务：

```bash
hermes cron create "0 */2 * * *" \
  "Check for new open PRs and review them.

Repos to monitor:
- myorg/backend-api
- myorg/frontend-app

Steps:
1. Run: gh pr list --repo REPO --state open --limit 5 --json number,title,author,createdAt
2. For each PR created or updated in the last 4 hours:
   - Run: gh pr diff NUMBER --repo REPO
   - Review the diff using the code-review guidelines
3. Format output as:

## PR Reviews — today

### [repo] #[number]: [title]
**Author:** [name] | **Verdict:** APPROVE/REQUEST_CHANGES/COMMENT
[findings]

If no new PRs found, say: No new PRs to review." \
  --name "pr-review" \
  --deliver telegram \
  --skill code-review
```

验证它已安排：

```bash
hermes cron list
```

### 其他有用的时间表

| 时间表 | 何时 |
|----------|------|
| `0 */2 * * *` | 每 2 小时 |
| `0 9,13,17 * * 1-5` | 每天三次，仅限工作日 |
| `0 9 * * 1` | 每周一早晨汇总 |
| `30m` | 每 30 分钟（高流量代码库） |

---

## 步骤 6：按需运行

不想等待计划时间？手动触发它：

```bash
hermes cron run pr-review
```

或者在聊天会话中：

```
/cron run pr-review
```

---

## 更进一步

### 直接将审查发布到 GitHub

不发送到 Telegram，而是让 Agent 在 PR 本身上发表评论：

将此添加到你的定时任务提示词中：

```
After reviewing, post your review:
- For issues: gh pr review NUMBER --repo REPO --comment --body "YOUR_REVIEW"
- For critical issues: gh pr review NUMBER --repo REPO --request-changes --body "YOUR_REVIEW"
- For clean PRs: gh pr review NUMBER --repo REPO --approve --body "Looks good"
```

:::caution
确保 `gh` 拥有 `repo` 范围的 Token。评论将以 `gh` 认证的用户身份发布。
:::

### 每周 PR 仪表板

创建一个周一早晨所有代码库的概览：

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly PR dashboard:
- myorg/backend-api
- myorg/frontend-app
- myorg/infra

For each repo show:
1. Open PR count and oldest PR age
2. PRs merged this week
3. Stale PRs (older than 5 days)
4. PRs with no reviewer assigned

Format as a clean summary." \
  --name "weekly-dashboard" \
  --deliver telegram
```

### 多代码库监控

通过在提示词中添加更多代码库来扩展规模。Agent 会按顺序处理它们——无需额外设置。

---

## 故障排除

### "gh: command not found"
消息网关在最小化环境中运行。确保 `gh` 在系统 PATH 中，并重启消息网关。

### 审查过于笼统
1. 添加 `code-review` 技能（步骤 3）
2. 通过记忆教 Hermes 你的规范（步骤 4）
3. 它对你的技术栈了解得越多，审查就越好

### 定时任务不运行
```bash
hermes gateway status    # 消息网关在运行吗？
hermes cron list         # 任务启用了吗？
```

### 速率限制
GitHub 允许认证用户每小时 5,000 次 API 请求。每个 PR 审查使用约 3-5 次请求（列表 + 差异 + 可选评论）。即使每天审查 100 个 PR，也远在限制之内。

---

## 下一步是什么？

- **[基于 Webhook 的 PR 审查](./webhook-github-pr-review.md)** — 当 PR 被创建时获得即时审查（需要公共端点）
- **[每日简报机器人](/docs/guides/daily-briefing-bot)** — 将 PR 审查与你的早晨新闻摘要结合起来
- **[构建一个插件](/docs/guides/build-a-hermes-plugin)** — 将审查逻辑封装成可共享的插件
- **[配置文件](/docs/user-guide/profiles)** — 运行一个具有自己记忆和配置的专用审查员配置文件
- **[备用提供商](/docs/user-guide/features/fallback-providers)** — 确保即使一个提供商宕机，审查也能运行