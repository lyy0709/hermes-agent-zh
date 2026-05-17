---
sidebar_position: 12
title: "将脚本输出管道传输到消息平台"
description: "使用 `hermes send` 将任何 shell 脚本、cron 任务、CI 钩子或监控守护进程的文本发送到 Telegram、Discord、Slack、Signal 和其他平台。"
---

# 将脚本输出管道传输到消息平台

`hermes send` 是一个小巧、可编写脚本的 CLI，可将消息推送到 Hermes 已配置的任何消息平台。可以把它看作一个跨平台的 `curl`，用于发送通知——你不需要运行消息网关，不需要 LLM，也不需要将 bot token 重新粘贴到每个脚本中。

适用于：

- 系统监控（内存、磁盘、GPU 温度、长时间运行的任务完成）
- CI/CD 通知（部署完成、测试失败）
- 需要将结果通知你的 Cron 脚本
- 从终端发送快速的一次性消息
- 将任何工具的输出管道传输到任何地方（`make | hermes send --to slack:#builds`）

该命令复用 `hermes gateway` 已使用的相同凭据和平台适配器，因此无需维护第二个配置界面。

---

## 快速开始

```bash
# 纯文本发送到平台的默认频道
hermes send --to telegram "deploy finished"

# 从任何命令管道传输标准输出
echo "RAM 92%" | hermes send --to telegram:-1001234567890

# 发送文件
hermes send --to discord:#ops --file /tmp/report.md

# 附加主题/标题行
hermes send --to slack:#eng --subject "[CI] build.log" --file build.log

# 线程目标（Telegram 话题、Discord 线程）
hermes send --to telegram:-1001234567890:17585 "threaded reply"

# 列出每个已配置的目标
hermes send --list

# 按平台筛选
hermes send --list telegram
```

---

## 参数参考

| 标志 | 描述 |
|------|-------------|
| `-t, --to TARGET` | 目标。参见[目标格式](#目标格式)。 |
| `message` (位置参数) | 消息文本。省略则从 `--file` 或 stdin 读取。 |
| `-f, --file PATH` | 从文件读取正文。`--file -` 强制从 stdin 读取。 |
| `-s, --subject LINE` | 在正文前添加标题/主题行。 |
| `-l, --list` | 列出可用目标。可选的位置参数平台筛选器。 |
| `-q, --quiet` | 成功时不输出到 stdout（仅退出码——适合脚本）。 |
| `--json` | 输出发送的原始 JSON 结果。 |
| `-h, --help` | 显示内置帮助文本。 |

### 目标格式

| 格式 | 示例 | 含义 |
|--------|---------|---------|
| `platform` | `telegram` | 发送到平台配置的默认频道 |
| `platform:chat_id` | `telegram:-1001234567890` | 特定的数字聊天/群组/用户 |
| `platform:chat_id:thread_id` | `telegram:-1001234567890:17585` | 特定的线程或 Telegram 论坛话题 |
| `platform:#channel` | `discord:#ops` | 人类友好的频道名称（根据频道目录解析） |
| `platform:+E164` | `signal:+15551234567` | 基于电话号码的平台：Signal、SMS、WhatsApp |

Hermes 提供适配器的任何平台都可以作为目标：
`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、
`mattermost`、`feishu`、`dingtalk`、`wecom`、`weixin`、`email` 等。

### 退出码

| 代码 | 含义 |
|------|---------|
| `0` | 发送（或列出）成功 |
| `1` | 平台层面交付失败（认证、权限、网络） |
| `2` | 用法/参数/配置错误 |

退出码遵循标准的 Unix 约定，因此你的脚本可以像处理 `curl` 或 `grep` 一样根据它们进行分支。

---

## 消息正文解析

`hermes send` 按以下顺序解析消息正文：

1. **位置参数** — `hermes send --to telegram "hi"`
2. **`--file PATH`** — `hermes send --to telegram --file msg.txt`
3. **管道传输的 stdin** — `echo hi | hermes send --to telegram`

当 stdin 是 TTY（无管道）时，Hermes **不会**等待输入——你会得到一个清晰的使用错误。这可以防止脚本在意外省略正文时挂起。

---

## 实际示例

### 监控：内存/磁盘警报

用一行可移植的代码替换监控脚本中临时的 `curl https://api.telegram.org/...` 调用：

```bash
#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  hermes send --to telegram --subject "⚠ MEMORY WARNING" \
    "RAM ${ram_pct}% on $(hostname)"
fi
```

因为 `hermes send` 复用你的 Hermes 配置，所以同一个脚本可以在安装了 Hermes 的任何主机上运行——无需手动将 bot token 导出到每台机器的执行环境中。

:::tip 不要向网关报告其自身问题
对于可能在网关自身遇到困难时触发的监控脚本（内存不足警报、磁盘已满警报），请继续使用最小的 `curl` 调用，而不是 `hermes send`。如果因为系统负载过高导致 Python 解释器无法加载，你仍然希望警报能够发出。
:::

### CI / CD：构建和测试结果

```bash
# 在 .github/workflows/deploy.yml 或任何 CI 脚本中
if ./scripts/deploy.sh; then
  hermes send --to slack:#deploys "✅ ${CI_COMMIT_SHA:0:7} deployed"
else
  tail -n 100 deploy.log | hermes send \
    --to slack:#deploys --subject "❌ deploy failed"
  exit 1
fi
```

### Cron：每日报告

```bash
# Crontab 条目
0 9 * * * /usr/local/bin/generate-metrics.sh \
  | /home/me/.hermes/bin/hermes send \
      --to telegram --subject "Daily metrics $(date +%Y-%m-%d)"
```

### 长时间运行的任务：完成后通知

```bash
./train.py --epochs 200 && \
  hermes send --to telegram "training done" || \
  hermes send --to telegram "training failed (exit $?)"
```

### 使用 `--json` 和 `--quiet` 编写脚本

```bash
# 如果交付失败，脚本硬性失败；成功时不污染日志
hermes send --to telegram --quiet "keepalive" || {
  echo "Telegram delivery failed" >&2
  exit 1
}

# 捕获消息 ID 用于后续编辑/线程化
msg_id=$(hermes send --to discord:#ops --json "build started" \
  | jq -r .message_id)
```

---

## `hermes send` 需要网关运行吗？

**通常不需要。** 对于任何使用 bot token 的平台——Telegram、Discord、Slack、Signal、SMS、WhatsApp Cloud API 和大多数其他平台——`hermes send` 使用来自 `~/.hermes/.env` 和 `~/.hermes/config.yaml` 的凭据直接调用平台的 REST 端点。它是一个独立的子进程，消息交付后立即退出。

只有在**插件平台**依赖持久适配器连接时才需要运行网关（例如，保持长连接 WebSocket 的自定义插件）。在这种情况下，你会得到一个清晰的错误，指向网关；使用 `hermes gateway start` 启动它并重试。

---

## 列出和发现目标

在发送到特定频道之前，你可以检查可用的目标：

```bash
# 每个已配置平台的所有目标
hermes send --list

# 仅 Telegram 目标
hermes send --list telegram

# 机器可读格式
hermes send --list --json
```

列表是从 `~/.hermes/channel_directory.json` 构建的，网关在运行时每隔几分钟会刷新该文件。如果你看到“尚未发现任何频道”，请启动一次网关（`hermes gateway start`），以便它可以填充缓存。

人类友好的名称（`discord:#ops`、`slack:#engineering`）在发送时根据此缓存解析，因此你无需记忆数字 ID。

---

## 与其他方法的比较

| 方法 | 多平台 | 复用 Hermes 凭据 | 需要网关 | 最适合 |
|----------|----------------|---------------------|---------------|----------|
| `hermes send` | ✅ | ✅ | 否（bot-token） | 以下所有情况 |
| 原始 `curl` 到每个平台 | 每个单独编写脚本 | 手动 | 否 | 关键监控脚本 |
| 带有 `--deliver` 的 `cron` 任务 | ✅ | ✅ | 否 | 计划的 Agent 任务 |
| `send_message` Agent 工具 | ✅ | ✅ | 否 | 在 Agent 循环内部 |

`hermes send` 有意设计为最简单的接口。如果你需要 Agent 来决定说什么，请在聊天或 cron 任务中使用 `send_message` 工具。如果你需要带有 LLM 生成内容的计划运行，请使用带有 `deliver='telegram:...'` 的 `cronjob(action='create', prompt=...)`。如果你只需要管道传输原始字符串，请使用 `hermes send`。

---

## 相关

- [使用 Cron 自动化一切](/docs/guides/automate-with-cron) —— 输出自动交付到任何平台的计划任务。
- [网关内部原理](/docs/developer-guide/gateway-internals) —— `hermes send` 与 cron 交付共享的交付路由器。
- [消息平台设置](/docs/user-guide/messaging/) —— 每个平台的一次性配置。