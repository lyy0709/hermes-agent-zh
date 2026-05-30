---
sidebar_position: 4
---

# 同时运行多个消息网关

在一台机器上以托管服务的形式运行多个[配置文件](./profiles.md)——每个配置文件都有自己的机器人令牌、会话和记忆。本页涵盖运维相关事项：同时启动所有配置文件、跨配置文件查看日志、防止主机休眠以及处理常见的 launchd/systemd 异常。

如果你只运行一个 Hermes Agent，则不需要此页面——请参阅[配置文件](./profiles.md)了解基础知识。

## 何时使用此功能

当你需要两个或更多 Hermes Agent 同时在线时，就需要此设置。常见原因包括：

- 一个 Telegram 机器人上运行个人助理，另一个上运行编程 Agent
- 每个家庭成员一个 Agent，或每个 Slack 工作区一个 Agent
- 同一配置的沙盒 + 生产实例
- 研究 Agent + 写作 Agent + 定时任务驱动的机器人——每个都有独立的记忆和技能

每个配置文件已经拥有自己的平台特定 LaunchAgent（`ai.hermes.gateway-<name>.plist`）或 systemd 用户服务（`hermes-gateway-<name>.service`）。本指南增加了集中管理它们的模式。

## 快速开始

```bash
# 创建配置文件（一次性操作）
hermes profile create coder
hermes profile create personal-bot
hermes profile create research

# 配置每个配置文件
coder setup
personal-bot setup
research setup

# 将每个消息网关安装为托管服务
coder gateway install
personal-bot gateway install
research gateway install

# 启动所有消息网关
coder gateway start
personal-bot gateway start
research gateway start
```

就这样——三个独立的 Agent，每个都在自己的进程中运行，崩溃时和用户登录时会自动重启。

## 同时启动、停止或重启所有消息网关

CLI 提供了单配置文件的生命周期命令。要对每个配置文件执行操作，请将它们包装在 shell 循环中。将下面的代码片段放入 `~/.local/bin/hermes-gateways` 并执行 `chmod +x`：

```sh
#!/bin/sh
set -eu

# 在此处添加或删除配置文件名称，以匹配你创建/删除的配置文件。
profiles="default coder personal-bot research"

usage() {
  echo "Usage: hermes-gateways {start|stop|restart|status|list}"
}

run_for_profile() {
  profile="$1"
  action="$2"
  if [ "$profile" = "default" ]; then
    hermes gateway "$action"
  else
    hermes -p "$profile" gateway "$action"
  fi
}

action="${1:-}"
case "$action" in
  start|stop|restart|status)
    for profile in $profiles; do
      echo "==> $action $profile"
      run_for_profile "$profile" "$action"
    done
    ;;
  list)
    hermes gateway list
    ;;
  *)
    usage
    exit 2
    ;;
esac
```

然后：

```bash
hermes-gateways start      # 启动每个已配置的配置文件
hermes-gateways stop       # 停止每个已配置的配置文件
hermes-gateways restart    # 重启所有配置文件
hermes-gateways status     # 查看所有配置文件的状态
hermes-gateways list       # 委托给 `hermes gateway list`
```

:::tip
`default` 配置文件使用 `hermes gateway <action>`（不带 `-p`）来操作，而不是 `hermes -p default gateway <action>`。上面的包装器处理了这两种形式。
:::

## 管理单个配置文件

每个配置文件安装的快捷命令：

```bash
coder gateway run        # 前台运行（Ctrl-C 停止）
coder gateway start      # 启动托管服务
coder gateway stop       # 停止托管服务
coder gateway restart    # 重启
coder gateway status     # 状态
coder gateway install    # 创建 LaunchAgent / systemd 单元
coder gateway uninstall  # 删除服务文件
```

这些命令等同于 `hermes -p coder gateway <action>`——如果配置文件别名不在 `PATH` 中，或者你从脚本中动态定位配置文件，这会很有用。

## 服务文件

每个配置文件都以其唯一名称安装自己的服务，因此安装永远不会冲突：

| 平台 | 路径                                                              |
| -------- | ----------------------------------------------------------------- |
| macOS    | `~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist`        |
| Linux    | `~/.config/systemd/user/hermes-gateway-<profile>.service`         |

默认配置文件保留历史名称：`ai.hermes.gateway.plist` / `hermes-gateway.service`。

## 查看日志

每个配置文件写入自己的日志文件：

```bash
# 默认配置文件
tail -f ~/.hermes/logs/gateway.log
tail -f ~/.hermes/logs/gateway.error.log

# 命名配置文件
tail -f ~/.hermes/profiles/<name>/logs/gateway.log
tail -f ~/.hermes/profiles/<name>/logs/gateway.error.log
```

同时流式传输每个配置文件的日志：

```bash
tail -f ~/.hermes/logs/gateway.log ~/.hermes/profiles/*/logs/gateway.log
```

CLI 还有一个结构化的日志查看器：

```bash
hermes logs --tail              # 跟踪默认配置文件
hermes -p coder logs --tail     # 跟踪一个配置文件
hermes logs --help              # 过滤器、级别、JSON 输出
```

## 识别实际运行的内容

```bash
hermes profile list             # 配置文件 + 模型 + 消息网关状态
hermes-gateways status          # 每个配置文件的完整状态
launchctl list | grep hermes    # macOS —— PID 和标签
systemctl --user list-units 'hermes-gateway-*'   # Linux —— 单元
```

## 编辑配置

每个配置文件在其自己的目录中保存其配置：

```
~/.hermes/profiles/<name>/
├── .env              # API 密钥、机器人令牌 (chmod 600)
├── config.yaml       # 模型、提供商、工具集、消息网关设置
└── SOUL.md           # 灵魂（人格）/ 系统提示词
```

默认配置文件直接使用 `~/.hermes/` 目录下的相同三个文件。

使用任何编辑器或通过 CLI 编辑它们：

```bash
hermes config set model.model anthropic/claude-sonnet-4    # 默认配置文件
coder config set model.model openai/gpt-5                  # 命名配置文件
```

编辑 `.env` 或 `config.yaml` 后，重启受影响的消息网关：

```bash
coder gateway restart
# 或者，对于所有配置文件：
hermes-gateways restart
```

## 保持主机唤醒

消息网关进程可以全天运行，但操作系统在空闲时仍会尝试休眠。两种模式：

### macOS —— `caffeinate`

`caffeinate` 内置于 macOS 中，运行时可以防止休眠。无需安装。

```bash
caffeinate -dis                    # 阻止显示器、空闲和系统休眠
caffeinate -dis -t 28800           # 同上，8 小时后自动退出
caffeinate -i -w $(cat ~/.hermes/gateway.pid) &   # 默认消息网关运行时保持唤醒

# 持久化：在后台运行并忘记
nohup caffeinate -dis >/dev/null 2>&1 &
disown

# 检查 / 停止
pmset -g assertions | grep -iE 'caffeinate|prevent|user is active'
pkill caffeinate
```

| 标志   | 效果                                            |
| ------ | ------------------------------------------------- |
| `-d`   | 阻止显示器休眠                               |
| `-i`   | 阻止空闲系统休眠（默认）                 |
| `-m`   | 阻止磁盘休眠                                  |
| `-s`   | 阻止系统休眠（仅限交流电源供电的 Mac）         |
| `-u`   | 模拟用户活动（防止屏幕锁定）     |
| `-t N` | `N` 秒后自动退出                       |
| `-w P` | 当 PID `P` 退出时退出                           |

:::warning 合盖仍会使 Mac 休眠
`caffeinate` 无法覆盖 MacBook 上由硬件驱动的合盖休眠。
对于合盖操作，请更改你的“节能”/“电池”偏好设置或使用第三方工具。
:::

### Linux —— `systemd-inhibit` 或 `loginctl`

```bash
# 在命令运行时禁止挂起
systemd-inhibit --what=idle:sleep --who=hermes --why="gateways running" \
  sleep infinity &

# 允许用户服务在注销后继续运行（推荐）
sudo loginctl enable-linger "$USER"
```

启用 lingering 后，你的 systemd 用户单元（包括 `hermes-gateway-<profile>.service`）将在 SSH 断开连接和重启后继续运行。

## 令牌冲突安全

每个配置文件必须为每个平台使用唯一的机器人令牌。如果两个配置文件共享 Telegram、Discord、Slack、WhatsApp 或 Signal 令牌，第二个消息网关将拒绝启动，并显示错误信息指出冲突的配置文件。

进行审计：

```bash
grep -H 'TELEGRAM_BOT_TOKEN\|DISCORD_BOT_TOKEN' \
     ~/.hermes/.env ~/.hermes/profiles/*/.env
```

## 更新代码

`hermes update` 拉取最新代码一次，并将新的捆绑技能同步到每个配置文件中：

```bash
hermes update
hermes-gateways restart
```

用户修改过的技能永远不会被覆盖。

## 故障排除

### "Could not find service in domain for user gui: 501"

你在之前的 `hermes gateway stop` 之后运行了 `hermes gateway start`。CLI 的 `stop` 会执行完整的 `launchctl unload`，这会从 launchd 的注册表中移除服务。CLI 在 `start` 时捕获此特定错误，并自动重新加载 plist（`↻ launchd job was unloaded; reloading service definition`）。服务正常启动。无需修复。

### 崩溃后残留的 PID

如果一个配置文件的消息网关显示 `not running` 但进程仍然存活：

```bash
ps -ef | grep "hermes_cli.*-p <profile>"
cat ~/.hermes/profiles/<profile>/gateway.pid
kill -TERM <pid>          # 优雅终止
kill -KILL <pid>          # 如果几秒后失败
<profile> gateway start
```

### 强制硬重置一个服务

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist
launchctl load   ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist

# Linux
systemctl --user restart hermes-gateway-<profile>.service
```

### 健康检查

```bash
hermes doctor                  # 默认配置文件
hermes -p <profile> doctor     # 一个配置文件
```