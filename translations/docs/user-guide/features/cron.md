---
sidebar_position: 5
title: "定时任务（Cron）"
description: "使用自然语言安排自动化任务，通过统一的 cron 工具进行管理，并可附加一个或多个技能"
---

# 定时任务（Cron）

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来管理 cron，该工具采用操作风格，而不是独立的 schedule/list/remove 工具。

## Cron 当前功能

Cron 任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为零个、一个或多个任务附加技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在新的 Agent 会话中运行，使用正常的静态工具列表
- 在**无 Agent 模式**下运行 —— 按计划运行脚本，其标准输出原样传递，无需 LLM 参与（参见下面的[无 Agent 模式](#无-agent-模式纯脚本任务)部分）

所有这些功能都通过 `cronjob` 工具提供给 Hermes 自身，因此您可以用自然语言创建、暂停、编辑和删除任务 —— 无需 CLI。

:::warning
Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行中禁用了 cron 管理工具，以防止失控的调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的订阅项" --skill blogwatcher
/cron add "every 1h" "使用两个技能并合并结果" --skill blogwatcher --skill maps
```

### 通过独立 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的订阅项" --skill blogwatcher
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
    name="早晨订阅",
)
```

### 多个技能

技能按顺序加载。提示词将成为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="查找新的本地活动和附近有趣的地方，然后将它们合并成一份简短的简报。",
    schedule="every 6h",
    name="本地简报",
)
```

当您希望计划的 Agent 继承可重用的工作流，而不必将完整的技能文本塞入 cron 提示词本身时，这非常有用。

## 在项目目录中运行任务

Cron 任务默认在脱离任何代码仓库的环境中运行 —— 不会加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，并且终端/文件/代码执行工具将从消息网关启动时的工作目录运行。传递 `--workdir`（CLI）或 `workdir=`（工具调用）来更改此设置：

```bash
# 独立 CLI（schedule 和 prompt 是位置参数）
hermes cron create "every 1d at 09:00" \
  "审核开放的 PR，总结 CI 健康状况，并发布到 #eng 频道" \
  --workdir /home/me/projects/acme
```

```python
# 在聊天中，通过 cronjob 工具
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="审核开放的 PR，总结 CI 健康状况，并发布到 #eng 频道",
)
```

当设置 `workdir` 时：

- 该目录中的 `AGENTS.md`、`CLAUDE.md` 和 `.cursorrules` 将被注入到系统提示词中（发现顺序与交互式 CLI 相同）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 都将使用该目录作为其工作目录（通过 `TERMINAL_CWD`）
- 路径必须是存在的绝对目录 —— 相对路径和不存在的目录在创建/更新时会被拒绝
- 在编辑时传递 `--workdir ""`（或通过工具传递 `workdir=""`）以清除它并恢复旧的行为

:::note 序列化
带有 `workdir` 的任务在调度器触发时按顺序运行，而不是在并行池中。这是有意为之 —— `TERMINAL_CWD` 是进程全局的，因此两个带有工作目录的任务同时运行会破坏彼此的当前工作目录。没有工作目录的任务仍像以前一样并行运行。
:::

## 编辑任务

您无需删除并重新创建任务来更改它们。

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

- `pause` —— 保留任务但停止调度它
- `resume` —— 重新启用任务并计算下一次运行时间
- `run` —— 在下一个调度器触发时运行任务
- `remove` —— 完全删除任务
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

每次触发时，Hermes 会：

1.  从 `~/.hermes/cron/jobs.json` 加载任务
2.  根据当前时间检查 `next_run_at`
3.  为每个到期任务启动一个全新的 `AIAgent` 会话
4.  （可选）将一个或多个附加的技能注入到该新会话中
5.  运行提示词直至完成
6.  交付最终响应
7.  更新运行元数据和下一次计划运行时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可防止调度器触发重叠，避免同一批任务被重复运行。

## 交付选项

在调度任务时，您需要指定输出的去向：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 返回至任务创建处 | 消息平台上的默认选项 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认选项 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定特定 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 特定 Telegram 话题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 主频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 特定 Discord 频道 | 按频道名称 |
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

Agent 的最终响应会自动交付。您无需在定时任务的提示词中调用 `send_message`。

### 响应包装

默认情况下，交付的定时任务输出会附带页眉和页脚进行包装，以便接收者知道它来自计划任务：

```
定时任务响应：Morning feeds
-------------

<agent 输出内容在此>

注意：Agent 无法看到此消息，因此无法回复。
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
检查 nginx 是否在运行。如果一切正常，仅用 [SILENT] 回复。
否则，报告问题。
```

无论是否存在 `[SILENT]` 标记，失败的任务总是会交付——只有成功的运行才能被静默。

## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果您的脚本需要更长时间——例如，为了包含随机延迟以避免类似机器人的时间模式——您可以增加此超时时间：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序为：环境变量 → config.yaml → 120 秒默认值。

## 无 Agent 模式（仅脚本任务）

对于不需要 LLM 推理的重复性任务——经典的看门狗、磁盘/内存警报、心跳、CI 探针——请在创建时传递 `no_agent=True`。调度器按计划运行您的脚本并直接交付其标准输出，完全跳过 Agent：

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

语义：

-   脚本标准输出（已修剪）→ 作为消息逐字交付。
-   **空的标准输出 → 静默触发**，不进行交付。这是看门狗模式：“只在出现问题时才说些什么”。
-   非零退出或超时 → 交付错误警报，因此损坏的看门狗不会静默失败。
-   最后一行出现 `{"wakeAgent": false}` → 静默触发（与 LLM 任务使用的门控相同）。
-   无 Token，无模型，无提供商回退——任务从不接触推理层。

`.sh` / `.bash` 文件在 `/bin/bash` 下运行；其他任何文件在当前 Python 解释器 (`sys.executable`) 下运行。脚本必须位于 `~/.hermes/scripts/` 中（与预运行脚本门控的沙盒规则相同）。

### Agent 会为您设置这些

`cronjob` 工具的架构向 Hermes 直接暴露了 `no_agent`，因此您可以在聊天中描述一个看门狗，并让 Agent 来设置它：

```text
如果 RAM 超过 85%，每 5 分钟在 Telegram 上提醒我一次。
```

Hermes 将通过 `write_file` 将检查脚本写入 `~/.hermes/scripts/`，然后调用：

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

当消息内容完全由脚本决定时（看门狗、阈值警报、心跳），它会自动选择 `no_agent=True`。同一个工具还允许 Agent 暂停、恢复、编辑和删除任务——因此整个生命周期都可以通过聊天驱动，无需任何人接触 CLI。

有关工作示例，请参阅[仅脚本定时任务指南](/docs/guides/cron-script-only)。

## 提供商恢复

定时任务继承您配置的回退提供商和凭据池轮换。如果主 API 密钥受到速率限制或提供商返回错误，定时任务 Agent 可以：

-   **回退到备用提供商**，如果您在 `config.yaml` 中配置了 `fallback_providers`（或旧的 `fallback_model`）
-   **轮换到同一提供商的下一个凭据**，根据您的[凭据池策略](/docs/user-guide/configuration#credential-pool-strategies)
这意味着高频运行或在高峰时段运行的定时任务更具弹性——单个被限速的 API 密钥不会导致整个运行失败。

## 调度格式

Agent 的最终响应会自动发送——你**不需要**在针对同一目标的定时任务提示词中包含 `send_message`。如果定时任务运行调用了 `send_message` 到调度器已经计划发送的完全相同的目标，Hermes 会跳过那个重复的发送，并告诉模型将面向用户的内容放在最终响应中。仅在需要发送到额外或不同目标时才使用 `send_message`。

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
0 9 * * 1-5     → 工作日（周一至周五）上午 9:00
0 */6 * * *     → 每 6 小时
30 8 1 * *      → 每月 1 号上午 8:30
0 0 * * 0       → 每周日午夜
```

### ISO 时间戳

```text
2026-03-15T09:00:00    → 2026 年 3 月 15 日上午 9:00 运行一次
```

## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
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
# → 像配置 Telegram/Discord 等平台一样切换工具集的开关
```

可以通过 `cronjob.create` 上的 `enabled_toolsets` 字段（或通过 `cronjob.update` 对现有任务）进行更精细的每任务控制：

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # 仅 web + file，没有 terminal/browser 等
        prompt="Summarize this week's AI news: ...")
```

当在任务上设置了 `enabled_toolsets` 时，它优先；否则 `hermes tools` 中 cron 平台的配置优先；否则 Hermes 回退到内置默认值。这对于成本控制很重要：将 `moa`、`browser`、`delegation` 等工具带入每个微小的“获取新闻”任务，会在每次 LLM 调用时增加工具模式提示词的长度。

### 完全跳过 Agent：`wakeAgent`

如果你的定时任务附加了预检查脚本（通过 `script=`），脚本可以在运行时决定 Hermes 是否应该调用 Agent。输出一个最终的标准输出行，格式如下：

```text
{"wakeAgent": false}
```

……然后定时任务会完全跳过本次 Agent 运行。这对于频繁的轮询（每 1-5 分钟）很有用，这些轮询只需要在实际状态发生变化时才唤醒 LLM——否则你会为重复的零内容 Agent 轮转付费。

```python
# 预检查脚本
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # 跳过本次执行
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

当省略 `wakeAgent` 时，默认为 `true`（像往常一样唤醒 Agent）。

### 链式任务：`context_from`

定时任务可以通过在 `context_from` 中列出其他一个或多个任务的名称（或 ID）来使用它们最近一次成功的输出：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

被引用任务最近一次完成的输出会作为上下文注入到本次运行的提示词上方。每个上游条目必须是有效的任务 ID 或名称（参见 `cronjob action="list"`）。注意：链式读取的是*最近一次完成的*输出——它不会等待在同一时间点正在运行的上游任务。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

任务可能将 `model` 和 `provider` 存储为 `null`。当省略这些字段时，Hermes 会在执行时从全局配置中解析它们。只有当设置了每任务覆盖时，它们才会出现在任务记录中。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 自包含的提示词仍然重要

:::warning 重要
定时任务在完全全新的 Agent 会话中运行。提示词必须包含 Agent 所需的一切，这些内容不是由附加的技能提供的。
:::

**不好：** `"Check on that server issue"`

**好：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

## 安全性

在创建和更新时，会扫描计划任务提示词中是否存在提示词注入和凭据泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露有效负载的提示词会被阻止。