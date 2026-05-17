---
sidebar_position: 5
title: "定时任务（Cron）"
description: "使用自然语言安排自动化任务，通过一个 cron 工具进行管理，并可附加一个或多个技能"
---

# 定时任务（Cron）

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来管理 cron，采用操作风格，而不是独立的 schedule/list/remove 工具。

## 当前 cron 的功能

Cron 任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为零个、一个或多个任务附加技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在新的 Agent 会话中运行，使用正常的静态工具列表
- 在**无 Agent 模式**下运行 —— 按计划运行脚本，其 stdout 原样输出，无需 LLM 参与（参见下面的[无 Agent 模式](#无-agent-模式仅脚本任务)部分）

所有这些功能都通过 `cronjob` 工具提供给 Hermes 本身，因此您可以用自然语言创建、暂停、编辑和删除任务 —— 无需 CLI。

:::warning
Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行中禁用了 cron 管理工具，以防止失控的调度循环。
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

技能按顺序加载。提示词成为在这些技能之上叠加的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="寻找新的本地活动和附近有趣的地方，然后将它们合并成一个简短的简报。",
    schedule="every 6h",
    name="本地简报",
)
```

当您希望计划的 Agent 继承可重用的工作流，而不必将完整的技能文本塞入 cron 提示词本身时，这非常有用。

## 在项目目录中运行任务

Cron 任务默认在脱离任何仓库的情况下运行 —— 不加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，并且终端/文件/代码执行工具从消息网关启动时的工作目录运行。传递 `--workdir`（CLI）或 `workdir=`（工具调用）来更改此设置：

```bash
# 独立 CLI（schedule 和 prompt 是位置参数）
hermes cron create "every 1d at 09:00" \
  "审计开放的 PR，总结 CI 健康状况，并发布到 #eng" \
  --workdir /home/me/projects/acme
```

```python
# 在聊天中，通过 cronjob 工具
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="审计开放的 PR，总结 CI 健康状况，并发布到 #eng",
)
```

当设置了 `workdir` 时：

- 来自该目录的 `AGENTS.md`、`CLAUDE.md` 和 `.cursorrules` 会被注入到系统提示词中（发现顺序与交互式 CLI 相同）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 都使用该目录作为其工作目录（通过 `TERMINAL_CWD`）
- 路径必须是存在的绝对目录 —— 相对路径和缺失的目录在创建/更新时会被拒绝
- 在编辑时传递 `--workdir ""`（或通过工具传递 `workdir=""`）以清除它并恢复旧的行为

:::note 序列化
带有 `workdir` 的任务在调度器触发时按顺序运行，而不是在并行池中运行。这是故意的 —— `TERMINAL_CWD` 是进程全局的，因此两个 workdir 任务同时运行会相互破坏对方的 cwd。没有 workdir 的任务仍然像以前一样并行运行。
:::

## 编辑任务

您不需要为了更改任务而删除并重新创建它们。

:::tip 任务引用
下面的 `<job_id>` 占位符（以及[生命周期操作](#生命周期操作)中）也接受任务的名称（不区分大小写）—— 当您记得 `morning-digest` 但不记得十六进制 ID 时很方便。确切的 job ID 优先于名称匹配；如果引用不是 ID 且一个名称匹配多个任务，命令会拒绝并打印候选 ID，以便您进行区分。
:::

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

Cron 任务现在拥有比仅创建/删除更完整的生命周期。

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
- `resume` — 重新启用任务并计算下一次未来的运行时间
- `run` — 在调度器下一次触发时运行任务
- `remove` — 完全删除任务

## 工作原理

**定时任务执行由消息网关守护进程处理。** 网关每 60 秒触发一次调度器，在独立的 Agent 会话中运行所有到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：为服务器安装开机启动的系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为

每次触发时，Hermes：

1.  从 `~/.hermes/cron/jobs.json` 加载任务
2.  根据当前时间检查 `next_run_at`
3.  为每个到期任务启动一个新的 `AIAgent` 会话
4.  可选地将一个或多个附加技能注入到该新会话中
5.  运行提示词直至完成
6.  传递最终响应
7.  更新运行元数据和下一次计划时间

`~/.hermes/cron/.tick.lock` 处的文件锁可防止调度器触发重叠，避免同一批任务被重复运行。

## 传递选项

调度任务时，您需要指定输出发送到哪里：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 发送回任务创建的地方 | 消息平台上的默认选项 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认选项 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定的特定 Telegram 聊天 | 直接传递 |
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
| `"all"` | 扇出到每个已连接的主频道 | 在触发时解析 |
| `"telegram,discord"` | 扇出到一组特定的频道 | 逗号分隔的列表 |
| `"origin,all"` | 传递到原始频道 **加上** 其他每个已连接的频道 | 组合任何标记 |

Agent 的最终响应会自动传递。您无需在定时任务提示词中调用 `send_message`。

### 路由意图 (`all`)

`all` 允许您将一个定时任务发送到您配置的每个消息频道，而无需按名称枚举它们。它**在触发时解析**，因此，在您设置 `TELEGRAM_HOME_CHANNEL` 之前创建的任务，将在您设置后的下一次触发时获取 Telegram。

语义：`all` 扩展为每个配置了主频道的平台。零个也可以；任务只是不产生任何传递目标，并在上游记录为传递失败。

`all` 可以与显式目标组合。`origin,all` 传递到原始聊天 *加上* 其他每个已连接的主频道，通过 `(platform, chat_id, thread_id)` 进行去重。

### 响应包装

默认情况下，传递的定时任务输出会包装一个页眉和页脚，以便接收者知道它来自一个计划任务：

```
定时任务响应：Morning feeds
-------------

<agent 输出在此>

注意：Agent 无法看到此消息，因此无法回复它。
```

要传递原始的 Agent 输出而不进行包装，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，则传递会被完全抑制。输出仍会保存在本地以供审计（在 `~/.hermes/cron/output/` 中），但不会向传递目标发送任何消息。

这对于仅应在出现问题时才报告的监控任务非常有用：

```text
检查 nginx 是否在运行。如果一切正常，仅用 [SILENT] 回复。
否则，报告问题。
```

失败的任务无论是否有 `[SILENT]` 标记都会传递——只有成功的运行才能被静默。

## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果您的脚本需要更长时间——例如，为了包含随机延迟以避免类似机器人的时间模式——您可以增加此值：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序是：环境变量 → config.yaml → 120 秒默认值。

## 无 Agent 模式（仅脚本任务）

对于不需要 LLM 推理的重复性任务——经典的看门狗、磁盘/内存警报、心跳、CI ping——在创建时传递 `no_agent=True`。调度器按计划运行您的脚本并直接传递其标准输出，完全跳过 Agent：

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

语义：

-   脚本标准输出（修剪后）→ 作为消息逐字传递。
-   **空的标准输出 → 静默触发**，不传递。这是看门狗模式：“只在出现问题时才说些什么”。
-   非零退出或超时 → 传递错误警报，因此损坏的看门狗不会静默失败。
-   最后一行有 `{"wakeAgent": false}` → 静默触发（与 LLM 任务使用的门相同）。
-   没有 Token，没有模型，没有提供商回退——任务从不接触推理层。

`.sh` / `.bash` 文件在 `/bin/bash` 下运行；其他任何文件在当前 Python 解释器 (`sys.executable`) 下运行。脚本必须位于 `~/.hermes/scripts/` 中（与预运行脚本门相同的沙盒规则）。
### Agent 会为你设置好这些

`cronjob` 工具的 schema 直接向 Hermes 暴露了 `no_agent` 参数，因此你可以在聊天中描述一个看门狗任务，然后让 Agent 来帮你配置：

```text
如果内存使用率超过 85%，每 5 分钟通过 Telegram 通知我。
```

Hermes 会通过 `write_file` 将检查脚本写入 `~/.hermes/scripts/`，然后调用：

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

当消息内容完全由脚本决定时（如看门狗、阈值警报、心跳检测），它会自动选择 `no_agent=True`。同一个工具也允许 Agent 暂停、恢复、编辑和删除任务——因此整个生命周期都可以通过聊天驱动，无需任何人接触 CLI。

有关实际示例，请参阅[纯脚本定时任务指南](/docs/guides/cron-script-only)。

## 使用 `context_from` 链接任务

定时任务在独立的会话中运行，没有之前运行的记忆。但有时一个任务的输出正是下一个任务所需要的。`context_from` 参数会自动建立这种连接——在运行时，任务 B 的提示词会预先附加任务 A 的最新输出作为上下文。

```python
# 任务 1：收集原始数据
cronjob(
    action="create",
    prompt="从 Hacker News 获取前 10 个 AI/ML 故事。以 Markdown 格式（包含标题、URL 和分数）将它们保存到 ~/.hermes/data/briefs/raw.md。",
    schedule="0 7 * * *",
    name="AI News Collector",
)

# 任务 2：分类——接收任务 1 的输出作为上下文
# 从以下命令获取任务 1 的 ID：cronjob(action="list")
cronjob(
    action="create",
    prompt="读取 ~/.hermes/data/briefs/raw.md。根据参与潜力和新颖性为每个故事评分（1-10 分）。将前 5 名输出到 ~/.hermes/data/briefs/ranked.md。",
    schedule="30 7 * * *",
    context_from="<job1_id>",
    name="AI News Triage",
)

# 任务 3：发布——接收任务 2 的输出作为上下文
cronjob(
    action="create",
    prompt="读取 ~/.hermes/data/briefs/ranked.md。撰写 3 条推文草稿（钩子 + 正文 + 话题标签）。发送到 telegram:7976161601。",
    schedule="0 8 * * *",
    context_from="<job2_id>",
    name="AI News Brief",
)
```

**工作原理：**

- 当任务 2 触发时，Hermes 会从 `~/.hermes/cron/output/{job1_id}/*.md` 读取任务 1 的最新输出
- 该输出会自动附加到任务 2 的提示词之前
- 任务 2 无需硬编码“读取此文件”——它会将内容作为上下文接收
- 链的长度可以是任意的：任务 1 → 任务 2 → 任务 3 → ...

**`context_from` 接受的格式：**

| 格式 | 示例 |
|--------|---------|
| 单个任务 ID（字符串） | `context_from="a1b2c3d4"` |
| 多个任务 ID（列表） | `context_from=["job_a", "job_b"]` |

输出会按照列出的顺序进行拼接。

**使用场景：**

- 多阶段流水线（收集 → 过滤 → 格式化 → 交付）
- 依赖任务，其中步骤 N 的工作依赖于步骤 N-1 的输出
- 扇出/扇入模式，其中一个任务聚合来自多个其他任务的结果

## 提供商恢复

定时任务继承你配置的备用提供商和凭据池轮换。如果主 API 密钥被限速或提供商返回错误，定时任务 Agent 可以：

- **回退到备用提供商**：如果你在 `config.yaml` 中配置了 `fallback_providers`（或旧版的 `fallback_model`）
- **轮换到下一个凭据**：在同一提供商的[凭据池](/docs/user-guide/configuration#credential-pool-strategies)中

这意味着高频运行或在高峰时段运行的定时任务更具弹性——单个被限速的密钥不会导致整个运行失败。

## 调度格式

Agent 的最终响应会自动发送——你**无需**在定时任务的提示词中为同一目的地包含 `send_message`。如果定时任务运行调用了 `send_message` 到调度器已经要发送的完全相同的目标，Hermes 会跳过该重复发送，并告诉模型将面向用户的内容放在最终响应中。仅在需要发送到额外或不同目标时才使用 `send_message`。

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

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性（`30m`，时间戳） | 1 | 运行一次 |
| 间隔（`every 2h`） | forever | 持续运行直到被移除 |
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

对于 `update`，传递 `skills=[]` 可以移除所有附加的技能。

## 定时任务可用的工具集

定时任务在全新的 Agent 会话中运行每个任务，没有附加聊天平台。默认情况下，定时任务 Agent 会获得**你在 `hermes tools` 中为 `cron` 平台配置的工具集**——不是 CLI 默认的，也不是所有可用的工具。

```bash
hermes tools
# → 在 curses UI 中选择 "cron" 平台
# → 像配置 Telegram/Discord 等平台一样，切换工具集的开关
```

可以通过 `cronjob.create` 上的 `enabled_toolsets` 字段（或通过 `cronjob.update` 对现有任务）进行更精细的每任务控制：

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # 仅 web + file，没有 terminal/browser 等
        prompt="总结本周的 AI 新闻：...")
```
当在任务中设置 `enabled_toolsets` 时，该设置优先；否则，`hermes tools` 的 cron-platform 配置优先；否则，Hermes 会回退到内置默认值。这对于成本控制很重要：将 `moa`、`browser`、`delegation` 带入每个微小的“获取新闻”任务，会在每次 LLM 调用时膨胀工具模式提示词。

### 完全跳过 Agent：`wakeAgent`

如果你的定时任务附加了一个预检查脚本（通过 `script=`），该脚本可以在运行时决定 Hermes 是否应该调用 Agent。输出一个最终的标准输出行，格式如下：

```text
{"wakeAgent": false}
```

...这样 cron 就会完全跳过本次执行的 Agent 运行。这对于频繁轮询（每 1-5 分钟）很有用，这些轮询只需要在实际状态发生变化时才唤醒 LLM —— 否则你会为无内容的 Agent 轮转反复付费。

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

当省略 `wakeAgent` 时，默认值为 `true`（像往常一样唤醒 Agent）。

#### 配方：廉价的预运行门控

`wakeAgent` 门控为你提供了一种零成本的方式来决定一个计划任务是否应该花费任何 LLM Token。三种模式涵盖了大多数用例。

**文件变更门控** —— 仅当被监视的文件自上次成功执行后有新内容时才运行。调度器会记录每个任务的 `last_run_at`；将其与文件的 mtime 进行比较。

```bash
#!/bin/bash
# ~/.hermes/scripts/feed-changed.sh
FEED="$HOME/data/feed.json"
STATE="$HOME/.hermes/scripts/.feed-changed.last"
test -f "$FEED" || { echo '{"wakeAgent": false}'; exit 0; }
mtime=$(stat -c %Y "$FEED")
last=$(cat "$STATE" 2>/dev/null || echo 0)
if [ "$mtime" -le "$last" ]; then
  echo '{"wakeAgent": false}'
else
  echo "$mtime" > "$STATE"
  echo '{"wakeAgent": true}'
fi
```

```text
cronjob(action="create", name="process-feed",
        schedule="every 30m",
        script="feed-changed.sh",
        prompt="A new ~/data/feed.json has landed. Summarize what changed.")
```

**外部标志门控** —— 仅当其他进程发出就绪信号时才运行（例如，部署钩子放置了一个文件，CI 作业在你的状态存储中设置了一个值）。

```bash
#!/bin/bash
# ~/.hermes/scripts/flag-ready.sh
if test -f /tmp/new-data-ready; then
  rm -f /tmp/new-data-ready
  echo '{"wakeAgent": true}'
else
  echo '{"wakeAgent": false}'
fi
```

```text
cronjob(action="create", name="nightly-analysis",
        schedule="0 9 * * *",
        script="flag-ready.sh",
        prompt="Run the nightly analysis over today's batch.")
```

**SQL 计数门控** —— 仅当你的数据库中有新行需要处理时才运行。脚本还可以通过 `context` 将计数传递给 Agent，这样 Agent 就知道它要处理多少数据，而无需重新查询。

```python
#!/usr/bin/env python
# ~/.hermes/scripts/new-rows.py
import json, sqlite3
conn = sqlite3.connect("/home/me/data/app.db")
n = conn.execute(
    "SELECT COUNT(*) FROM messages WHERE ts > strftime('%s','now','-2 hours')"
).fetchone()[0]
if n < 1:
    print(json.dumps({"wakeAgent": False}))
else:
    print(json.dumps({"wakeAgent": True, "context": {"new_rows": n}}))
```

```text
cronjob(action="create", name="summarize-new-msgs",
        schedule="every 2h",
        script="new-rows.py",
        prompt="Summarize the new messages from the last 2 hours.")
```

同样的模式适用于任何可以从脚本查询的数据源 —— Postgres、HTTP API、你自己的状态存储 —— 而无需将 SQL 求值器硬编码到 cron 子系统中。

:::tip
Hermes 自身的 `~/.hermes/state.db` 是一个内部模式，会在版本之间发生变化。不要从预运行门控中查询它 —— 请指向你自己的数据库或数据源。
:::

致谢：这套配方是由 @iankar8 在 [#2654](https://github.com/NousResearch/hermes-agent/pull/2654) 中的探索所启发的，该探索提议添加 sql/文件/命令触发器作为并行机制。`script` + `wakeAgent` 门控已经以零成本覆盖了所有三种情况，因此这项工作最终以文档形式落地。

### 链式任务：`context_from`

一个 cron 任务可以通过在 `context_from` 中列出一个或多个其他任务的名称（或 ID）来消费它们最近一次成功的输出：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

被引用任务最近一次完成的输出会作为本次运行的上下文注入到提示词上方。每个上游条目必须是有效的任务 ID 或名称（参见 `cronjob action="list"`）。注意：链式读取的是*最近一次完成的*输出 —— 它不会等待在同一时刻运行的上游任务。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

任务可能将 `model` 和 `provider` 存储为 `null`。当省略这些字段时，Hermes 会在执行时从全局配置中解析它们。它们只在设置了每个任务的覆盖时才出现在任务记录中。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 自包含的提示词仍然很重要

:::warning 重要
Cron 任务在完全新鲜的 Agent 会话中运行。提示词必须包含 Agent 所需的一切，这些内容不是由附加的技能提供的。
:::

**错误示例：** `"Check on that server issue"`

**正确示例：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

## 安全性

计划任务的提示词在创建和更新时会进行扫描，以检测提示词注入和凭据泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露载荷的提示词会被阻止。