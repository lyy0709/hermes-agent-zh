---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言安排自动化任务，通过一个 cron 工具进行管理，并可附加一个或多个技能"
---

# 定时任务 (Cron)

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来管理 cron，该工具采用操作风格，而不是独立的 schedule/list/remove 工具。

## 当前 cron 的功能

Cron 任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为零个、一个或多个任务附加技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在具有正常静态工具列表的全新 Agent 会话中运行

:::warning
Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行过程中禁用了 cron 管理工具，以防止失控的调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的订阅源项目" --skill blogwatcher
/cron add "every 1h" "使用两个技能并合并结果" --skill blogwatcher --skill maps
```

### 通过独立的 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的订阅源项目" --skill blogwatcher
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

## 基于技能的 Cron 任务

Cron 任务可以在运行提示词之前加载一个或多个技能。

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
    prompt="查找新的本地事件和附近有趣的地方，然后将它们合并成一个简短的简报。",
    schedule="every 6h",
    name="本地简报",
)
```

当你希望一个定时 Agent 继承可重用的工作流，而不必将完整的技能文本塞进 cron 提示词本身时，这很有用。

## 在项目目录中运行任务

Cron 任务默认在脱离任何代码仓库的情况下运行——不加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，并且终端 / 文件 / 代码执行工具从消息网关启动时所在的任何工作目录运行。传递 `--workdir` (CLI) 或 `workdir=` (工具调用) 来改变这一点：

```bash
# 独立 CLI (schedule 和 prompt 是位置参数)
hermes cron create "every 1d at 09:00" \
  "审计开放的 PR，总结 CI 健康状况，并发布到 #eng 频道" \
  --workdir /home/me/projects/acme
```

```python
# 在聊天中，通过 cronjob 工具
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="审计开放的 PR，总结 CI 健康状况，并发布到 #eng 频道",
)
```

当设置了 `workdir` 时：

- 来自该目录的 `AGENTS.md`、`CLAUDE.md` 和 `.cursorrules` 会被注入到系统提示词中（发现顺序与交互式 CLI 相同）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 都使用该目录作为它们的工作目录（通过 `TERMINAL_CWD`）
- 路径必须是存在的绝对目录——相对路径和不存在的目录在创建/更新时会被拒绝
- 在编辑时传递 `--workdir ""`（或通过工具传递 `workdir=""`）以清除它并恢复旧的行为

:::note 序列化
带有 `workdir` 的任务在调度器触发时按顺序运行，而不是在并行池中。这是故意的——`TERMINAL_CWD` 是进程全局的，因此两个 workdir 任务同时运行会相互破坏对方的当前工作目录。没有 workdir 的任务仍然像以前一样并行运行。
:::

## 编辑任务

你不需要为了更改任务而删除并重新创建它们。

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

Cron 任务现在拥有比简单的创建/删除更完整的生命周期。

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
- `resume` — 重新启用任务并计算下一次未来运行时间
- `run` — 在下一个调度器触发时运行任务
- `remove` — 完全删除任务

## 工作原理

**Cron 执行由消息网关守护进程处理。** 消息网关每 60 秒触发一次调度器，在隔离的 Agent 会话中运行任何到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：为服务器安装启动时系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```
### 消息网关调度器行为

每次调度时，Hermes 会：

1.  从 `~/.hermes/cron/jobs.json` 加载任务
2.  根据当前时间检查 `next_run_at`
3.  为每个到期的任务启动一个全新的 `AIAgent` 会话
4.  （可选）将一个或多个附加的技能注入到该新会话中
5.  运行提示词直至完成
6.  交付最终响应
7.  更新运行元数据和下一次计划时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可防止重叠的调度器运行导致同一批任务被重复执行。

## 交付选项

在调度任务时，你需要指定输出的去向：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 返回至任务创建处 | 消息平台上的默认选项 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认选项 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定特定的 Telegram 聊天 | 直接交付 |
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

Agent 的最终响应会自动交付。你无需在定时任务的提示词中调用 `send_message`。

### 响应包装

默认情况下，交付的定时任务输出会附带页眉和页脚进行包装，以便接收者知道它来自一个计划任务：

```
定时任务响应：Morning feeds
-------------

<agent 输出内容在此>

注意：Agent 无法看到此消息，因此无法回复它。
```

要交付原始的 Agent 输出而不进行包装，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，则交付会被完全抑制。输出仍会保存在本地以供审计（在 `~/.hermes/cron/output/` 中），但不会向交付目标发送任何消息。

这对于仅应在出现问题时才报告的监控任务非常有用：

```text
检查 nginx 是否在运行。如果一切正常，仅用 [SILENT] 响应。
否则，报告问题。
```

无论是否存在 `[SILENT]` 标记，失败的任务总是会交付——只有成功的运行才能被静默。

## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果你的脚本需要更长时间——例如，为了包含随机延迟以避免类似机器人的时间模式——你可以增加此值：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序是：环境变量 → config.yaml → 120 秒默认值。

## 提供商恢复

定时任务继承你配置的备用提供商和凭据池轮换。如果主 API 密钥受到速率限制或提供商返回错误，定时任务 Agent 可以：

*   **回退到备用提供商**：如果你在 `config.yaml` 中配置了 `fallback_providers`（或旧的 `fallback_model`）
*   **轮换到下一个凭据**：对于同一提供商，使用你[凭据池](/docs/user-guide/configuration#credential-pool-strategies)中的下一个凭据

这意味着高频运行或在高峰时段运行的定时任务更具弹性——单个受速率限制的密钥不会导致整个运行失败。

## 计划格式

Agent 的最终响应会自动交付——你**不**需要在定时任务提示词中为同一目的地包含 `send_message`。如果定时任务运行调用了 `send_message` 到调度器已经要交付的精确目标，Hermes 会跳过该重复发送，并告诉模型将面向用户的内容放在最终响应中。仅对额外或不同的目标使用 `send_message`。

### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（重复）

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
| 间隔 (`every 2h`) | forever | 持续运行直到被移除 |
| Cron 表达式 | forever | 持续运行直到被移除 |

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

对于 `update`，传递 `skills=[]` 以移除所有附加的技能。

## 定时任务可用的工具集

定时任务在全新的 Agent 会话中运行每个任务，没有附加聊天平台。默认情况下，定时任务 Agent 获得**你在 `hermes tools` 中为 `cron` 平台配置的工具集**——不是 CLI 默认值，也不是所有可用的工具。

```bash
hermes tools
# → 在 curses UI 中选择 "cron" 平台
# → 像为 Telegram/Discord/等平台一样切换工具集的开关
```
更精细的每任务控制可通过 `cronjob.create` 的 `enabled_toolsets` 字段实现（或通过 `cronjob.update` 对现有任务进行设置）：

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # 仅 web + file，无 terminal/browser 等
        prompt="Summarize this week's AI news: ...")
```

当任务设置了 `enabled_toolsets` 时，该设置优先；否则使用 `hermes tools` 的 cron 平台配置；再否则 Hermes 回退到内置默认值。这对于成本控制很重要：在每个微小的“获取新闻”任务中都携带 `moa`、`browser`、`delegation` 会膨胀每次 LLM 调用的工具模式提示词。

### 完全跳过 Agent：`wakeAgent`

如果你的定时任务附加了预检查脚本（通过 `script=`），脚本可以在运行时决定 Hermes 是否应该调用 Agent。输出一个最终的标准输出行，格式如下：

```text
{"wakeAgent": false}
```

……这样 cron 就会完全跳过本次触发的 Agent 运行。这对于频繁轮询（每 1-5 分钟）很有用，这些轮询只需要在实际状态发生变化时才唤醒 LLM —— 否则你会为一次次无内容的 Agent 轮转付费。

```python
# 预检查脚本
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # 跳过本次触发
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

当省略 `wakeAgent` 时，默认为 `true`（照常唤醒 Agent）。

### 任务链：`context_from`

一个定时任务可以通过在 `context_from` 中列出其他一个或多个任务的名称（或 ID）来使用它们最近一次成功的输出：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

被引用任务最近一次完成的输出会作为本次运行的上下文注入到提示词上方。每个上游条目必须是有效的任务 ID 或名称（参见 `cronjob action="list"`）。注意：链式读取的是*最近一次完成的*输出 —— 它不会等待在同一触发时刻正在运行的上游任务。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

任务可能将 `model` 和 `provider` 存储为 `null`。当这些字段被省略时，Hermes 会在执行时从全局配置中解析它们。它们只在设置了每任务覆盖时才会出现在任务记录中。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 自包含的提示词仍然重要

:::warning 重要
定时任务在完全新的 Agent 会话中运行。提示词必须包含 Agent 所需的一切，除非已由附加的技能提供。
:::

**不好：** `"Check on that server issue"`

**好：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

## 安全性

计划任务的提示词在创建和更新时会进行扫描，以检测提示词注入和凭证泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露负载的提示词会被阻止。