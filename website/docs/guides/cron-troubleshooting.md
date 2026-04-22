---
sidebar_position: 12
title: "定时任务故障排除"
description: "诊断和修复常见的 Hermes 定时任务问题——任务未触发、交付失败、技能加载错误和性能问题"
---

# 定时任务故障排除

当定时任务未按预期运行时，请按顺序进行以下检查。大多数问题属于以下四类之一：时间安排、交付、权限或技能加载。

---

## 任务未触发

### 检查 1：验证任务是否存在且处于活动状态

```bash
hermes cron list
```

查找任务并确认其状态为 `[active]`（而不是 `[paused]` 或 `[completed]`）。如果显示 `[completed]`，则重复次数可能已耗尽——编辑任务以重置它。

### 检查 2：确认时间表正确

格式错误的时间表会静默地默认为一次性任务或被完全拒绝。测试你的表达式：

| 你的表达式 | 应评估为 |
|----------------|-------------------|
| `0 9 * * *` | 每天上午 9:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `every 2h` | 从现在起每 2 小时 |
| `30m` | 从现在起 30 分钟后 |
| `2025-06-01T09:00:00` | 2025 年 6 月 1 日 9:00 AM UTC |

如果任务触发一次然后从列表中消失，这是一个一次性时间表（`30m`、`1d` 或 ISO 时间戳）——这是预期行为。

### 检查 3：消息网关是否在运行？

定时任务由消息网关的后台计时器线程触发，该线程每 60 秒计时一次。常规的 CLI 聊天会话**不会**自动触发定时任务。

如果你期望任务自动触发，则需要一个正在运行的消息网关（`hermes gateway` 或 `hermes serve`）。对于一次性调试，你可以使用 `hermes cron tick` 手动触发计时。

### 检查 4：检查系统时钟和时区

任务使用本地时区。如果你的机器时钟错误或处于与预期不同的时区，任务将在错误的时间触发。验证：

```bash
date
hermes cron list   # 将 next_run 时间与本地时间进行比较
```

---

## 交付失败

### 检查 1：验证交付目标是否正确

交付目标区分大小写，并且需要配置正确的平台。配置错误的目标会静默丢弃响应。

| 目标 | 要求 |
|--------|----------|
| `telegram` | `~/.hermes/.env` 中的 `TELEGRAM_BOT_TOKEN` |
| `discord` | `~/.hermes/.env` 中的 `DISCORD_BOT_TOKEN` |
| `slack` | `~/.hermes/.env` 中的 `SLACK_BOT_TOKEN` |
| `whatsapp` | 已配置 WhatsApp 消息网关 |
| `signal` | 已配置 Signal 消息网关 |
| `matrix` | 已配置 Matrix 主服务器 |
| `email` | 在 `config.yaml` 中配置了 SMTP |
| `sms` | 已配置 SMS 提供商 |
| `local` | 对 `~/.hermes/cron/output/` 具有写权限 |
| `origin` | 交付到创建任务的聊天会话 |

其他支持的平台包括 `mattermost`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 和 `webhook`。你也可以使用 `platform:chat_id` 语法（例如，`telegram:-1001234567890`）定位到特定的聊天会话。

如果交付失败，任务仍会运行——只是不会发送到任何地方。检查 `hermes cron list` 中更新的 `last_error` 字段（如果可用）。

### 检查 2：检查 `[SILENT]` 的使用

如果你的定时任务没有产生输出，或者 Agent 以 `[SILENT]` 响应，则交付会被抑制。这对于监控任务是故意的——但要确保你的提示词没有意外地抑制所有内容。

提示词说“如果没有变化，用 [SILENT] 响应”也会静默地吞掉非空响应。检查你的条件逻辑。

### 检查 3：平台 Token 权限

每个消息平台机器人需要特定的权限才能接收消息。如果交付静默失败：

- **Telegram**：机器人必须是目标群组/频道的管理员
- **Discord**：机器人必须拥有在目标频道发送消息的权限
- **Slack**：机器人必须被添加到工作区并拥有 `chat:write` 作用域

### 检查 4：响应包装

默认情况下，定时任务响应会包装有页眉和页脚（`config.yaml` 中的 `cron.wrap_response: true`）。某些平台或集成可能无法很好地处理这一点。要禁用：

```yaml
cron:
  wrap_response: false
```

---

## 技能加载失败

### 检查 1：验证技能是否已安装

```bash
hermes skills list
```

技能必须先安装，然后才能附加到定时任务。如果缺少某个技能，请先使用 `hermes skills install <skill-name>` 或在 CLI 中通过 `/skills` 安装它。

### 检查 2：检查技能名称与技能文件夹名称

技能名称区分大小写，并且必须与已安装技能的文件夹名称匹配。如果你的任务指定了 `ai-funding-daily-report`，但技能文件夹是 `ai-funding-daily-report`，请从 `hermes skills list` 确认确切的名称。

### 检查 3：需要交互式工具的技能

定时任务运行时禁用了 `cronjob`、`messaging` 和 `clarify` 工具集。这可以防止递归创建定时任务、直接发送消息（交付由调度程序处理）和交互式提示。如果一个技能依赖这些工具集，它将无法在定时任务上下文中工作。

检查技能的文档以确认它可以在非交互式（无头）模式下工作。

### 检查 4：多技能排序

当使用多个技能时，它们按顺序加载。如果技能 A 依赖于技能 B 的上下文，请确保 B 先加载：

```bash
/cron add "0 9 * * *" "..." --skill context-skill --skill target-skill
```

在这个例子中，`context-skill` 在 `target-skill` 之前加载。

---

## 任务错误和失败

### 检查 1：查看最近的任务输出

如果一个任务运行并失败，你可能会在以下位置看到错误上下文：

1. 任务交付的聊天会话（如果交付成功）
2. `~/.hermes/logs/agent.log` 中的调度程序消息（或 `errors.log` 中的警告）
3. 通过 `hermes cron list` 获取的任务 `last_run` 元数据

### 检查 2：常见错误模式

**脚本的“没有那个文件或目录”**
`script` 路径必须是绝对路径（或相对于 Hermes 配置目录）。验证：
```bash
ls ~/.hermes/scripts/your-script.py   # 必须存在
hermes cron edit <job_id> --script ~/.hermes/scripts/your-script.py
```

**任务执行时“未找到技能”**
技能必须安装在运行调度程序的机器上。如果你在多台机器之间移动，技能不会自动同步——使用 `hermes skills install <skill-name>` 重新安装它们。

**任务运行但未交付任何内容**
可能是交付目标问题（见上面的交付失败）或静默抑制的响应（`[SILENT]`）。

**任务挂起或超时**
调度程序使用基于不活动的超时（默认 600 秒，可通过 `HERMES_CRON_TIMEOUT` 环境变量配置，`0` 表示无限制）。只要 Agent 在主动调用工具，它就可以运行——计时器仅在持续不活动后触发。长时间运行的任务应使用脚本来处理数据收集，并且只交付结果。

### 检查 3：锁争用

调度程序使用基于文件的锁定来防止重叠的计时。如果两个消息网关实例正在运行（或者 CLI 会话与消息网关冲突），任务可能会被延迟或跳过。

终止重复的消息网关进程：
```bash
ps aux | grep hermes
# 终止重复的进程，只保留一个
```

### 检查 4：jobs.json 的权限

任务存储在 `~/.hermes/cron/jobs.json` 中。如果你的用户无法读取/写入此文件，调度程序将静默失败：

```bash
ls -la ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json   # 你的用户应该拥有它
```

---

## 性能问题

### 任务启动缓慢

每个定时任务都会创建一个新的 AIAgent 会话，这可能涉及提供商身份验证和模型加载。对于时间敏感的时间表，请增加缓冲时间（例如，使用 `0 8 * * *` 而不是 `0 9 * * *`）。

### 太多重叠的任务

调度程序在每个计时内按顺序执行任务。如果多个任务在同一时间到期，它们会一个接一个地运行。考虑错开时间表（例如，使用 `0 9 * * *` 和 `5 9 * * *` 而不是都在 `0 9 * * *`）以避免延迟。

### 脚本输出过大

输出数兆字节数据的脚本会减慢 Agent 的速度，并可能达到 Token 限制。在脚本级别进行过滤/总结——只发出 Agent 需要推理的内容。

---

## 诊断命令

```bash
hermes cron list                    # 显示所有任务、状态、next_run 时间
hermes cron run <job_id>            # 安排在下一次计时运行（用于测试）
hermes cron edit <job_id>           # 修复配置问题
hermes logs                         # 查看最近的 Hermes 日志
hermes skills list                  # 验证已安装的技能
```

---

## 获取更多帮助

如果你已经按照本指南操作但问题仍然存在：

1. 使用 `hermes cron run <job_id>` 运行任务（在下一个消息网关计时时触发），并观察聊天输出中的错误
2. 检查 `~/.hermes/logs/agent.log` 中的调度程序消息和 `~/.hermes/logs/errors.log` 中的警告
3. 在 [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 提交问题，包含：
   - 任务 ID 和时间表
   - 交付目标
   - 你的预期与实际发生的情况
   - 日志中的相关错误消息

---

*有关完整的定时任务参考，请参阅[使用定时任务自动化一切](/docs/guides/automate-with-cron)和[定时任务](/docs/user-guide/features/cron)。*