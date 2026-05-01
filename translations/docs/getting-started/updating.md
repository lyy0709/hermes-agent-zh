---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本或卸载它"
---

# 更新与卸载

## 更新

使用一条命令即可更新到最新版本：

```bash
hermes update
```

此命令会拉取最新代码、更新依赖项，并提示你配置自上次更新以来添加的任何新选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了该提示，可以手动运行 `hermes config check` 来查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 更新期间会发生什么

当你运行 `hermes update` 时，会发生以下步骤：

1.  **配对数据快照** — 保存一个轻量级的更新前状态快照（涵盖 `~/.hermes/pairing/`、飞书评论规则和其他在运行时被修改的状态文件）。可通过 `hermes backup restore --state pre-update` 回滚。
2.  **Git 拉取** — 从 `main` 分支拉取最新代码并更新子模块
3.  **依赖项安装** — 运行 `uv pip install -e ".[all]"` 以获取新的或更改的依赖项
4.  **配置迁移** — 检测自你当前版本以来添加的新配置选项并提示你设置它们
5.  **消息网关自动重启** — 更新完成后，正在运行的消息网关会被刷新，以便新代码立即生效。由服务管理的消息网关（Linux 上的 systemd，macOS 上的 launchd）通过服务管理器重启。当 Hermes 可以将正在运行的 PID 映射回配置文件时，手动启动的消息网关会自动重新启动。

### 仅预览：`hermes update --check`

想在实际拉取之前知道你落后于 `origin/main` 吗？运行 `hermes update --check` — 它会获取、并排打印你的本地提交和最新的远程提交，如果同步则退出码为 `0`，如果落后则退出码为 `1`。不会修改任何文件，也不会重启任何消息网关。在需要判断“是否有更新”的脚本和定时任务中很有用。

### 完整的更新前备份：`--backup`

对于高价值的配置文件（生产环境消息网关、共享团队安装），你可以选择对 `HERMES_HOME`（配置、认证、会话、技能、配对）进行完整的拉取前备份：

```bash
hermes update --backup
```

或者将其设置为每次运行的默认行为：

```yaml
# ~/.hermes/config.yaml
update:
  backup: true
```

`--backup` 在早期版本中是始终开启的行为，但在大型主目录上每次更新都会增加几分钟时间，所以现在改为可选。上面提到的轻量级配对数据快照仍然无条件运行。

预期输出如下所示：

```
$ hermes update
正在更新 Hermes Agent...
📥 正在拉取最新代码...
已经是最新的。 (或：正在更新 abc1234..def5678)
📦 正在更新依赖项...
✅ 依赖项已更新
🔍 正在检查新的配置选项...
✅ 配置是最新的 (或：发现 2 个新选项 — 正在运行迁移...)
🔄 正在重启消息网关...
✅ 消息网关已重启
✅ Hermes Agent 更新成功！
```

### 推荐的更新后验证

`hermes update` 处理主要的更新路径，但快速验证可以确认一切顺利落地：

1.  `git status --short` — 如果工作树意外地变脏，请在继续之前检查
2.  `hermes doctor` — 检查配置、依赖项和服务健康状况
3.  `hermes --version` — 确认版本号按预期更新
4.  如果你使用消息网关：`hermes gateway status`
5.  如果 `doctor` 报告 npm audit 问题：在标记的目录中运行 `npm audit fix`

:::warning 更新后工作树变脏
如果 `git status --short` 在 `hermes update` 后显示意外的更改，请停止并在继续之前检查它们。这通常意味着本地修改被重新应用到更新后的代码之上，或者依赖项步骤刷新了锁文件。
:::

### 如果你的终端在更新过程中断开连接

`hermes update` 会保护自己免受意外终端丢失的影响：

*   更新会忽略 `SIGHUP`，因此关闭 SSH 会话或终端窗口不再会在安装过程中终止它。`pip` 和 `git` 子进程继承了这种保护，因此 Python 环境不会因连接断开而处于半安装状态。
*   所有输出在更新运行时都会镜像到 `~/.hermes/logs/update.log`。如果你的终端消失，请重新连接并检查日志，查看更新是否完成以及消息网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

*   `Ctrl-C` (SIGINT) 和系统关机 (SIGTERM) 仍然会被响应 — 这些是故意的取消操作，而不是意外。

你不再需要将 `hermes update` 包装在 `screen` 或 `tmux` 中以在终端断开连接时存活。

### 检查当前版本

```bash
hermes version
```

与 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases) 上的最新版本进行比较。

### 从消息平台更新

你也可以直接从 Telegram、Discord、Slack 或 WhatsApp 发送以下命令进行更新：

```
/update
```

这会拉取最新代码、更新依赖项并重启正在运行的消息网关。机器人将在重启期间短暂离线（通常 5-15 秒），然后恢复。

### 手动更新

如果你是手动安装的（不是通过快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码和子模块
git pull origin main
git submodule update --init --recursive

# 重新安装（获取新的依赖项）
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"

# 检查新的配置选项
hermes config check
hermes config migrate   # 以交互方式添加任何缺失的选项
```

### 回滚说明

如果更新引入了问题，你可以回滚到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回滚到特定的提交
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# 如果正在运行，重启消息网关
hermes gateway restart
```

要回滚到特定的发布标签：

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning
如果添加了新选项，回滚可能会导致配置不兼容。回滚后运行 `hermes config check`，如果遇到错误，请从 `config.yaml` 中删除任何无法识别的选项。
:::

### 给 Nix 用户的说明

如果你通过 Nix flake 安装，更新是通过 Nix 包管理器管理的：

```bash
# 更新 flake 输入
nix flake update hermes-agent

# 或者用最新版本重新构建
nix profile upgrade hermes-agent
```

Nix 安装是不可变的 — 回滚由 Nix 的生成系统处理：

```bash
nix profile rollback
```

更多详情请参阅 [Nix 设置](./nix-setup.md)。

---

## 卸载

```bash
hermes uninstall
```

卸载程序会给你保留配置文件（`~/.hermes/`）以便将来重新安装的选项。

### 手动卸载

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选 — 如果你计划重新安装，请保留
```

:::info
如果你将消息网关安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::