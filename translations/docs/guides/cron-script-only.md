---
sidebar_position: 13
title: "纯脚本定时任务（无需 LLM）"
description: "经典的看门狗定时任务，完全跳过 LLM —— 脚本按计划运行，其标准输出会发送到您的消息平台。内存警报、磁盘警报、CI 通知、定期健康检查。"
---

# 纯脚本定时任务

有时您已经确切地知道要发送什么消息。您不需要 Agent 来推理 —— 您只需要一个脚本定时运行，并将其输出（如果有的话）发送到 Telegram / Discord / Slack / Signal。

Hermes 将此称为 **无 Agent 模式**。这是去除了 LLM 的定时任务系统。

```
   ┌──────────────────┐          ┌──────────────────┐
   │ 调度器触发       │  每      │ 运行脚本         │
   │ （每 N 分钟）    │ ──────▶ │ （bash 或 python）│
   └──────────────────┘          └──────────────────┘
                                          │
                                          │ 标准输出
                                          ▼
                                 ┌──────────────────┐
                                 │ 投递路由器        │
                                 │ (telegram/disc…) │
                                 └──────────────────┘
```

- **无需调用 LLM。** 零 Token，零 Agent 循环，零模型开销。
- **脚本即任务。** 脚本决定是否发出警报。产生输出 → 消息被发送。无输出 → 静默触发。
- **Bash 或 Python。** `.sh` / `.bash` 文件在 `/bin/bash` 下运行；任何其他扩展名的文件在当前 Python 解释器下运行。`~/.hermes/scripts/` 目录下的任何文件都被接受。
- **相同的调度器。** 与 LLM 任务一起位于 `cronjob` 中 —— 暂停、恢复、列出、日志和投递目标都以相同的方式工作。

## 何时使用

在以下情况下使用无 Agent 模式：

- **内存 / 磁盘 / GPU 看门狗。** 每 5 分钟运行一次，仅在超过阈值时发出警报。
- **CI 钩子。** 部署完成 → 发布提交 SHA。构建失败 → 发送日志的最后 100 行。
- **定期指标。** "每日 Stripe 收入（上午 9 点）" 作为一个简单的 API 调用 + 美化输出。
- **外部事件轮询器。** 检查 API，状态变化时发出警报。
- **心跳。** 每 N 分钟向仪表板发送一次 ping，以证明主机存活。

当您需要 Agent **决定**说什么时，请使用普通（LLM 驱动）的定时任务 —— 例如总结长文档、从信息流中挑选有趣的项目、起草人性化的消息。无 Agent 路径适用于脚本的标准输出本身就是要发送的消息的情况。

## 通过聊天创建

无 Agent 模式的真正优势在于，Agent 本身可以为您设置看门狗 —— 无需编辑器，无需 shell，无需记住 CLI 标志。您描述想要什么，Hermes 编写脚本、安排计划，并告诉您何时触发。

### 示例对话

> **您：** 如果 RAM 超过 85%，每 5 分钟在 telegram 上通知我
>
> **Hermes：** *（写入 `~/.hermes/scripts/memory-watchdog.sh`，然后调用 `cronjob(...)` 并设置 `no_agent=true`）*
>
> 已设置。每 5 分钟运行一次，仅在 RAM 超过 85% 时向 Telegram 发出警报。脚本：`memory-watchdog.sh`。任务 ID：`abc123`。

在底层，Agent 进行了两次工具调用：

```python
# 1. 编写检查脚本
write_file(
    path="~/.hermes/scripts/memory-watchdog.sh",
    content='''#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  echo "RAM ${ram_pct}% on $(hostname)"
fi
# Empty stdout = silent tick; no message sent.
''',
)

# 2. 安排计划 —— no_agent=True 使得每次触发时跳过 LLM
cronjob(
    action="create",
    schedule="every 5m",
    script="memory-watchdog.sh",
    no_agent=True,
    deliver="telegram",
    name="memory-watchdog",
)
```

从那时起，每次触发都是免费的：调度器运行脚本，如果其标准输出非空则将其通过管道发送到 Telegram，并且从不接触模型。

### Agent 为您决定的内容

当您提出类似 "当 X 发生时提醒我" 或 "每 N 分钟检查 Y 并在 Z 时告诉我" 的请求时，Hermes 的 `cronjob` 工具描述会告诉它，只要消息内容完全由脚本决定，就使用 `no_agent=True`。当请求需要推理时（*"总结新问题"*、*"挑选最有趣的头条新闻"*、*"起草友好的提醒"*），它会回退到正常的 LLM 驱动路径。

您不必自己指定 `--no-agent`。只需描述行为即可。

### 通过聊天管理看门狗

Agent 可以像创建任务一样暂停、恢复、编辑和删除任务：

> **您：** 今晚停止内存看门狗
>
> **Hermes：** *（调用 `cronjob(action='pause', job_id='abc123')`）*
>
> 已暂停。使用 "重新打开它" 或通过 `hermes cron resume abc123` 恢复。

> **您：** 将其更改为每 15 分钟一次
>
> **Hermes：** *（调用 `cronjob(action='update', job_id='abc123', schedule='every 15m')`）*

完整的生命周期（创建 / 列出 / 更新 / 暂停 / 恢复 / 立即运行 / 删除）对 Agent 可用，而您无需学习任何 CLI 命令。

## 通过 CLI 创建

更喜欢使用 shell？CLI 路径通过三个命令提供相同的结果：

```bash
# 1. 编写脚本
cat > ~/.hermes/scripts/memory-watchdog.sh <<'EOF'
#!/usr/bin/env bash
# Alert when RAM usage is over 85%. Silent otherwise.
RAM_PCT=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$RAM_PCT" -ge 85 ]; then
  echo "⚠ RAM ${RAM_PCT}% on $(hostname)"
fi
# Empty stdout = silent run; no message sent.
EOF
chmod +x ~/.hermes/scripts/memory-watchdog.sh

# 2. 安排计划
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"

# 3. 验证
hermes cron list
hermes cron run <job_id>    # 触发一次进行测试
```

就这样。无需提示词，无需技能，无需模型。

## 脚本输出如何映射到投递

| 脚本行为 | 结果 |
|-----------------|--------|
| 退出码 0，标准输出非空 | 标准输出按原样投递 |
| 退出码 0，标准输出为空 | 静默触发 —— 不投递 |
| 退出码 0，标准输出最后一行包含 `{"wakeAgent": false}` | 静默触发（与 LLM 任务共享的关卡） |
| 非零退出码 | 投递错误警报（这样损坏的看门狗不会静默失败） |
| 脚本超时 | 投递错误警报 |

"空输出时静默" 的行为是经典看门狗模式的关键：脚本可以自由地每分钟运行，但频道只在确实需要注意某些事情时才会看到消息。

## 脚本规则

脚本必须位于 `~/.hermes/scripts/` 目录下。这在任务创建时和运行时都会强制执行 —— 绝对路径、`~/` 扩展和路径遍历模式（`../`）会被拒绝。该目录与 LLM 任务使用的预检查脚本关卡共享。

解释器选择基于文件扩展名：

| 扩展名 | 解释器 |
|-----------|-------------|
| `.sh`, `.bash` | `/bin/bash` |
| 其他任何扩展名 | `sys.executable`（当前 Python） |

我们特意**不**遵循 `#!/...` 的 shebang —— 保持解释器设置明确且简单，减少了调度器需要信任的范围。

## 计划语法

与所有其他定时任务相同：

```bash
hermes cron create "every 5m"        # 间隔
hermes cron create "every 2h"
hermes cron create "0 9 * * *"       # 标准 cron：每天上午 9 点
hermes cron create "30m"             # 一次性：30 分钟后运行一次
```

完整语法请参阅 [定时任务功能参考](/docs/user-guide/features/cron)。

## 投递目标

`--deliver` 接受消息网关所知道的所有目标。一些常见形式：

```bash
--deliver telegram                       # 平台主频道
--deliver telegram:-1001234567890        # 特定聊天
--deliver telegram:-1001234567890:17585  # 特定 Telegram 论坛主题
--deliver discord:#ops
--deliver slack:#engineering
--deliver signal:+15551234567
--deliver local                          # 仅保存到 ~/.hermes/cron/output/
```

对于使用机器人令牌的平台（Telegram、Discord、Slack、Signal、SMS、WhatsApp），在脚本运行时不需要运行消息网关 —— 该工具直接调用每个平台的 REST 端点，使用 `~/.hermes/.env` / `~/.hermes/config.yaml` 中已有的凭据。

## 编辑和生命周期

```bash
hermes cron list                                    # 查看所有任务
hermes cron pause <job_id>                          # 停止触发，保留定义
hermes cron resume <job_id>
hermes cron edit <job_id> --schedule "every 10m"    # 调整频率
hermes cron edit <job_id> --agent                   # 切换到 LLM 模式
hermes cron edit <job_id> --no-agent --script …     # 切换回来
hermes cron remove <job_id>                         # 删除它
```

所有适用于 LLM 任务的操作（暂停、恢复、手动触发、投递目标更改）也适用于无 Agent 任务。

## 工作示例：磁盘空间警报

```bash
cat > ~/.hermes/scripts/disk-alert.sh <<'EOF'
#!/usr/bin/env bash
# Alert when / or /home is over 90% full.
THRESHOLD=90
df -h / /home 2>/dev/null | awk -v t="$THRESHOLD" '
  NR > 1 && $5+0 >= t {
    printf "⚠ Disk %s full on %s\n", $5, $6
  }
'
EOF
chmod +x ~/.hermes/scripts/disk-alert.sh

hermes cron create "*/15 * * * *" \
  --no-agent \
  --script disk-alert.sh \
  --deliver telegram \
  --name "disk-alert"
```

当两个文件系统都低于 90% 时静默；当某个文件系统填满时，每个超过阈值的文件系统会触发恰好一行输出。

## 与其他模式的比较

| 方法 | 运行内容 | 使用时机 |
|----------|-----------|-------------|
| `hermes send`（一次性） | 任何通过管道输入它的 shell 命令 | 临时投递或作为外部调度器（systemd、launchd）的操作 |
| `cronjob --no-agent`（本页） | 您的脚本，按 Hermes 的计划运行 | 不需要推理的重复性看门狗 / 警报 / 指标 |
| `cronjob`（默认，LLM） | Agent，带有可选的预检查脚本 | 当消息内容需要对数据进行推理时 |
| 操作系统 cron + `hermes send` | 您的脚本，按操作系统的计划运行 | 当 Hermes 可能不健康时（您正在监控的对象） |

对于必须在*消息网关关闭时*也能触发的关键系统健康看门狗，请继续使用操作系统级别的 cron + 普通的 `curl` 或 `hermes send` 调用 —— 这些作为独立的操作系统进程运行，不依赖于 Hermes 是否运行。当被监控的对象是外部系统时，消息网关内的调度器是正确选择。

## 相关

- [使用定时任务自动化一切](/docs/guides/automate-with-cron) —— LLM 驱动的定时任务模式。
- [定时任务参考](/docs/user-guide/features/cron) —— 完整的计划语法、生命周期、投递路由。
- [使用 `hermes send` 管道传输脚本输出](/docs/guides/pipe-script-output) —— 用于临时脚本的一次性对应功能。
- [消息网关内部](/docs/developer-guide/gateway-internals) —— 投递路由器内部原理。