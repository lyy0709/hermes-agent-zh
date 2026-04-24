---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言安排自动化任务，通过一个 cron 工具进行管理，并可附加一个或多个技能"
---

# 定时任务 (Cron)

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来管理定时任务，它采用动作风格的操作，而不是独立的 schedule/list/remove 工具。

## 当前定时任务的功能

定时任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为零个、一个或多个任务附加技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在全新的 Agent 会话中运行，使用正常的静态工具列表

:::warning
由定时任务运行的会话不能递归创建更多定时任务。Hermes 在定时任务执行期间禁用了 cron 管理工具，以防止失控的调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的订阅源内容" --skill blogwatcher
/cron add "every 1h" "使用两个技能并合并结果" --skill blogwatcher --skill maps
```

### 通过独立的 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的订阅源内容" --skill blogwatcher
hermes cron create "every 1h" "使用两个技能并合并结果" \
  --skill blogwatcher \
  --skill maps \
  --name "技能组合"
```

### 通过自然对话

像平常一样询问 Hermes：

```text
每天早上 9 点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 发送摘要给我。
```

Hermes 将在内部使用统一的 `cronjob` 工具。

## 基于技能的定时任务

定时任务可以在运行提示词之前加载一个或多个技能。

### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="检查配置的订阅源并总结任何新内容。",
    schedule="0 9 * * *",
    name="早晨订阅源",
)
```

### 多个技能

技能按顺序加载。提示词成为在这些技能之上分层的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="查找新的本地活动和附近有趣的地方，然后将它们合并成一个简短的简报。",
    schedule="every 6h",
    name="本地简报",
)
```

当你希望一个定时 Agent 继承可重用的工作流，而不必将完整的技能文本塞进 cron 提示词本身时，这很有用。

## 编辑任务

你不需要为了修改任务而删除并重新创建它们。

### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "使用修订后的任务"
/cron edit <job_id> --skill blogwatcher --skill maps
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "使用修订后的任务"
hermes cron edit <job_id> --skill blogwatcher --skill maps
hermes cron edit <job_id> --add-skill maps
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复的 `--skill` 会替换任务附加的技能列表
- `--add-skill` 会追加到现有列表而不替换它
- `--remove-skill` 会移除特定的附加技能
- `--clear-skills` 会移除所有附加技能

## 生命周期操作

定时任务现在拥有比简单的创建/删除更完整的生命周期。

### 聊天

```bash
/cron list
/cron pause <job_id>
/cron resume <job_id>
/cron run <job_id>
/cron remove <job_id>
```

### 独立 CLI

```bash
hermes cron list
hermes cron pause <job_id>
hermes cron resume <job_id>
hermes cron run <job_id>
hermes cron remove <job_id>
hermes cron status
hermes cron tick
```

它们的作用：

- `pause` — 保留任务但停止调度它
- `resume` — 重新启用任务并计算下一次运行时间
- `run` — 在下一个调度器 tick 时触发任务
- `remove` — 完全删除任务

## 工作原理

**定时任务执行由消息网关守护进程处理。** 网关每 60 秒触发一次调度器，在隔离的 Agent 会话中运行所有到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：为服务器安装开机启动的系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为

每次 tick 时，Hermes：

1.  从 `~/.hermes/cron/jobs.json` 加载任务
2.  根据当前时间检查 `next_run_at`
3.  为每个到期任务启动一个全新的 `AIAgent` 会话
4.  可选地将一个或多个附加技能注入到该新会话中
5.  运行提示词直至完成
6.  交付最终响应
7.  更新运行元数据和下一次计划时间

`~/.hermes/cron/.tick.lock` 处的文件锁可防止重叠的调度器 tick 重复运行同一批任务。

## 交付选项

安排任务时，你需要指定输出发送到哪里：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 发送回任务创建的地方 | 消息平台上的默认选项 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认选项 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定的特定 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 特定的 Telegram 话题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 主频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 特定的 Discord 频道 | 通过频道名称 |
| `"slack"` | Slack 主频道 | |
| `"whatsapp"` | WhatsApp 主频道 | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix 主房间 | |
| `"mattermost"` | Mattermost 主频道 | |
| `"email"` | 电子邮件 | |
| `"sms"` | 通过 Twilio 发送短信 | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | 钉钉 | |
| `"feishu"` | 飞书/Lark | |
| `"wecom"` | 企业微信 | |
| `"weixin"` | 微信 | |
| `"bluebubbles"` | BlueBubbles (iMessage) | |
| `"qqbot"` | QQ 机器人 (腾讯 QQ) | |

Agent 的最终响应会自动交付。你不需要在 cron 提示词中调用 `send_message`。

### 响应包装

默认情况下，交付的 cron 输出会带有页眉和页脚包装，以便接收者知道它来自定时任务：

```
定时任务响应：早晨订阅源
-------------

<agent 输出内容在此>

注意：Agent 无法看到此消息，因此无法回复它。
```

要交付原始的 Agent 输出而不带包装，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，则完全抑制交付。输出仍会保存在本地以供审计（在 `~/.hermes/cron/output/` 中），但不会向交付目标发送任何消息。

这对于只应在出现问题时才报告的监控任务很有用：

```text
检查 nginx 是否在运行。如果一切正常，仅用 [SILENT] 响应。
否则，报告问题。
```

失败的任务无论是否有 `[SILENT]` 标记都会交付——只有成功的运行才能被静默。

## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果你的脚本需要更长时间——例如，为了包含随机延迟以避免类似机器人的时间模式——你可以增加这个时间：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序是：环境变量 → config.yaml → 120 秒默认值。

## 提供商恢复

定时任务继承你配置的备用提供商和凭据池轮换。如果主 API 密钥被限速或提供商返回错误，cron Agent 可以：

- **回退到备用提供商**，如果你在 `config.yaml` 中配置了 `fallback_providers`（或旧的 `fallback_model`）
- **轮换到同一提供商的下一个凭据**，根据你的[凭据池策略](/docs/user-guide/configuration#credential-pool-strategies)

这意味着高频运行或在高峰时段运行的定时任务更具弹性——单个被限速的密钥不会导致整个运行失败。

## 计划格式

Agent 的最终响应会自动交付——你**不**需要在 cron 提示词中为同一目的地包含 `send_message`。如果定时任务运行调用了 `send_message` 到调度器已经要交付的精确目标，Hermes 会跳过那个重复的发送，并告诉模型将面向用户的内容放在最终响应中。仅对额外或不同的目标使用 `send_message`。

### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（重复性）

```text
every 30m    → 每 30 分钟
every 2h     → 每 2 小时
every 1d     → 每天
```

### Cron 表达式

```text
0 9 * * *       → 每天上午 9:00
0 9 * * 1-5     → 工作日上午 9:00
0 */6 * * *     → 每 6 小时
30 8 1 * *      → 每月 1 日上午 8:30
0 0 * * 0       → 每周日午夜
```

### ISO 时间戳

```text
2026-03-15T09:00:00    → 2026 年 3 月 15 日上午 9:00 运行一次
```

## 重复行为

| 计划类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性 (`30m`, 时间戳) | 1 | 运行一次 |
| 间隔 (`every 2h`) | 永远 | 运行直到被移除 |
| Cron 表达式 | 永远 | 运行直到被移除 |

你可以覆盖它：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

## 以编程方式管理任务

面向 Agent 的 API 是一个工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update`，传递 `skills=[]` 以移除所有附加技能。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存在 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

任务可能将 `model` 和 `provider` 存储为 `null`。当省略这些字段时，Hermes 会在执行时从全局配置中解析它们。它们仅在设置了每任务覆盖时才会出现在任务记录中。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 自包含的提示词仍然重要

:::warning 重要
定时任务在完全全新的 Agent 会话中运行。提示词必须包含 Agent 所需的一切，这些内容不是由附加技能已经提供的。
:::

**不好：** `"检查那个服务器问题"`

**好：** `"以用户 'deploy' 身份 SSH 到服务器 192.168.1.100，使用 'systemctl status nginx' 检查 nginx 是否在运行，并验证 https://example.com 返回 HTTP 200。"`

## 安全性

定时任务提示词在创建和更新时会扫描提示词注入和凭据泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露负载的提示词会被阻止。