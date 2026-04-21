---
sidebar_position: 10
title: "教程：GitHub PR 审查 Agent"
description: "构建一个自动化的 AI 代码审查器，监控你的代码库、审查拉取请求并交付反馈——全程无需手动操作"
---

# 教程：构建一个 GitHub PR 审查 Agent

**问题所在：** 你的团队创建 PR 的速度比你审查的速度还快。PR 等待审查的时间长达数天。初级开发者合并了包含错误的代码，因为没人有时间检查。你每天早上都在追赶代码差异，而不是进行构建。

**解决方案：** 一个全天候监控你代码库的 AI Agent，审查每个新 PR 的错误、安全问题和代码质量，并发送摘要给你——这样你只需将时间花在真正需要人工判断的 PR 上。

**你将构建的内容：**

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│   定时任务   ──▶  Hermes Agent  ──▶  GitHub API  ──▶  审查交付     │
│   (每2小时)       + gh CLI           (PR 差异)        (Telegram,  │
│                    + 技能                              Discord,   │
│                    + 记忆                             本地)       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

本指南使用**定时任务**来按计划轮询 PR——无需服务器或公共端点。可在 NAT 和防火墙后工作。

:::tip 想要实时审查？
如果你有可用的公共端点，请查看[使用 Webhook 实现自动化 GitHub PR 评论](./webhook-github-pr-review.md)——当 PR 被创建或更新时，GitHub 会立即将事件推送给 Hermes。
:::

---

## 先决条件

- **已安装 Hermes Agent** — 参见[安装指南](/docs/getting-started/installation)
- **运行消息网关**以支持定时任务：
  ```bash
  hermes gateway install   # 作为服务安装
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
使用 `deliver: "local"` 将审查保存到 `~/.hermes/cron/output/`。在连接通知之前进行测试非常有用。
:::

---

## 步骤 1：验证设置

确保 Hermes 可以访问 GitHub。启动一个聊天会话：

```bash
hermes
```

用一个简单的命令测试：

```
运行：gh pr list --repo NousResearch/hermes-agent --state open --limit 3
```

你应该能看到一个打开的 PR 列表。如果这能正常工作，你就准备好了。

---

## 步骤 2：尝试手动审查

仍在聊天会话中，让 Hermes 审查一个真实的 PR：

```
审查这个拉取请求。阅读差异，检查错误、安全问题和代码质量。具体说明行号并引用有问题的代码。

运行：gh pr diff 3888 --repo NousResearch/hermes-agent
```

Hermes 将：
1. 执行 `gh pr diff` 以获取代码变更
2. 通读整个差异
3. 生成一个包含具体发现的结构化审查报告

如果你对质量满意，就可以开始自动化了。

---

## 步骤 3：创建一个审查技能

技能为 Hermes 提供了一致的审查指南，这些指南在会话和定时任务运行之间持续存在。没有它，审查质量会参差不齐。

```bash
mkdir -p ~/.hermes/skills/code-review
```

创建 `~/.hermes/skills/code-review/SKILL.md`：

```markdown
---
name: code-review
description: 审查拉取请求的错误、安全问题和代码质量
---

# 代码审查指南

审查拉取请求时：

## 检查内容
1. **错误** — 逻辑错误、差一错误、空值/未定义处理
2. **安全** — 注入、身份验证绕过、代码中的密钥、SSRF
3. **性能** — N+1 查询、无限循环、内存泄漏
4. **风格** — 命名约定、死代码、缺少错误处理
5. **测试** — 变更是否经过测试？测试是否覆盖边缘情况？

## 输出格式
对于每个发现：
- **文件:行号** — 确切位置
- **严重性** — 严重 / 警告 / 建议
- **问题所在** — 一句话描述
- **修复方法** — 如何修复

## 规则
- 要具体。引用有问题的代码。
- 除非影响可读性，否则不要标记风格上的吹毛求疵。
- 如果 PR 看起来不错，就如实说明。不要捏造问题。
- 以以下内容结尾：APPROVE / REQUEST_CHANGES / COMMENT
```

验证它是否已加载——启动 `hermes`，你应该能在启动时的技能列表中看到 `code-review`。

---

## 步骤 4：教它你的约定

这是让审查器真正有用的地方。启动一个会话，教 Hermes 你团队的标准：

```
记住：在我们的后端代码库中，我们使用 Python 和 FastAPI。
所有端点必须有类型注解和 Pydantic 模型。
我们不允许原始 SQL——只允许 SQLAlchemy ORM。
测试文件放在 tests/ 目录下，并且必须使用 pytest fixtures。
```

```
记住：在我们的前端代码库中，我们使用 TypeScript 和 React。
不允许使用 `any` 类型。所有组件必须有 props 接口。
我们使用 React Query 进行数据获取，从不使用 useEffect 进行 API 调用。
```

这些记忆将永久保存——审查器将强制执行你的约定，而无需每次都被告知。

---

## 步骤 5：创建自动化定时任务

现在将所有部分连接起来。创建一个每 2 小时运行一次的定时任务：

```bash
hermes cron create "0 */2 * * *" \
  "检查新的打开状态的 PR 并审查它们。

要监控的代码库：
- myorg/backend-api
- myorg/frontend-app

步骤：
1. 运行：gh pr list --repo REPO --state open --limit 5 --json number,title,author,createdAt
2. 对于过去 4 小时内创建或更新的每个 PR：
   - 运行：gh pr diff NUMBER --repo REPO
   - 使用代码审查指南审查差异
3. 将输出格式化为：

## PR 审查 — 今日

### [代码库] #[编号]: [标题]
**作者：** [姓名] | **裁决：** APPROVE/REQUEST_CHANGES/COMMENT
[发现]

如果未找到新的 PR，请说：没有新的 PR 需要审查。" \
  --name "pr-review" \
  --deliver telegram \
  --skill code-review
```

验证它是否已安排：

```bash
hermes cron list
```

### 其他有用的时间表

| 时间表 | 何时 |
|----------|------|
| `0 */2 * * *` | 每 2 小时 |
| `0 9,13,17 * * 1-5` | 每天三次，仅限工作日 |
| `0 9 * * 1` | 每周一早上汇总 |
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

不交付到 Telegram，而是让 Agent 在 PR 本身发表评论：

将此添加到你的定时任务提示词中：

```
审查后，发布你的审查：
- 对于问题：gh pr review NUMBER --repo REPO --comment --body "你的审查内容"
- 对于严重问题：gh pr review NUMBER --repo REPO --request-changes --body "你的审查内容"
- 对于干净的 PR：gh pr review NUMBER --repo REPO --approve --body "看起来不错"
```

:::caution
确保 `gh` 拥有 `repo` 范围的 Token。评论将以 `gh` 认证的用户身份发布。
:::

### 每周 PR 仪表板

创建一个周一早上的所有代码库概览：

```bash
hermes cron create "0 9 * * 1" \
  "生成每周 PR 仪表板：
- myorg/backend-api
- myorg/frontend-app
- myorg/infra

为每个代码库显示：
1. 打开的 PR 数量和最旧的 PR 存在时间
2. 本周合并的 PR
3. 陈旧的 PR（超过 5 天）
4. 没有分配审查者的 PR

格式化为清晰的摘要。" \
  --name "weekly-dashboard" \
  --deliver telegram
```

### 多代码库监控

通过在提示词中添加更多代码库来扩展规模。Agent 会按顺序处理它们——无需额外设置。

---

## 故障排除

### "gh: command not found"
消息网关在最小化环境中运行。确保 `gh` 在系统 PATH 中并重启消息网关。

### 审查过于笼统
1. 添加 `code-review` 技能（步骤 3）
2. 通过记忆教 Hermes 你的约定（步骤 4）
3. 它对你的技术栈了解得越多，审查就越好

### 定时任务不运行
```bash
hermes gateway status    # 消息网关在运行吗？
hermes cron list         # 任务启用了吗？
```

### 速率限制
GitHub 允许认证用户每小时进行 5,000 次 API 请求。每个 PR 审查使用约 3-5 次请求（列表 + 差异 + 可选评论）。即使每天审查 100 个 PR 也远在限制之内。

---

## 下一步是什么？

- **[基于 Webhook 的 PR 审查](./webhook-github-pr-review.md)** — 当 PR 被打开时获得即时审查（需要公共端点）
- **[每日简报机器人](/docs/guides/daily-briefing-bot)** — 将 PR 审查与你的早间新闻摘要结合起来
- **[构建一个插件](/docs/guides/build-a-hermes-plugin)** — 将审查逻辑封装成可共享的插件
- **[配置文件](/docs/user-guide/profiles)** — 运行一个具有自己记忆和配置的专用审查者配置文件
- **[备用提供商](/docs/user-guide/features/fallback-providers)** — 确保即使一个提供商宕机，审查也能运行