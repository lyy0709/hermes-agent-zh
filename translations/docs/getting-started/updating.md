---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本或卸载它"
---

# 更新与卸载

## 更新

### Git 安装

使用单个命令更新到最新版本：

```bash
hermes update
```

此命令会从 `main` 分支拉取最新代码，更新依赖项，并提示你配置自上次更新以来添加的任何新选项。

### pip 安装

PyPI 发布跟踪的是**带标签的版本**（主要和次要版本），而不是 `main` 分支上的每次提交。使用以下命令检查更新并升级：

```bash
hermes update --check    # 查看 PyPI 上是否有新版本
hermes update            # 运行 pip install --upgrade hermes-agent
```

或手动操作：

```bash
pip install --upgrade hermes-agent    # 或：uv pip install --upgrade hermes-agent
```

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加它们。如果你跳过了该提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 更新期间会发生什么（Git 安装）

当你运行 `hermes update` 时，会发生以下步骤：

1.  **配对数据快照** — 保存一个轻量级的更新前状态快照（涵盖 `~/.hermes/pairing/`、飞书评论规则和其他在运行时被修改的状态文件）。可通过[快照和回滚](../user-guide/checkpoints-and-rollback.md)中描述的快照恢复流程恢复，或通过提取 Hermes 在你 `~/.hermes/` 目录旁边写入的最新快速快照 zip 文件恢复。
2.  **Git pull** — 从 `main` 分支拉取最新代码并更新子模块
3.  **拉取后语法验证 + 自动回滚** — 拉取后，Hermes 会编译每个 `hermes` 调用在启动时导入的八个关键文件。如果任何文件解析失败（例如，存在孤立的合并冲突标记、意外截断的文件），Hermes 会运行 `git reset --hard <pre-pull-sha>` 来回滚安装，以便你的 shell 保持可启动状态。一旦上游修复完成，请重新运行 `hermes update`。
4.  **依赖项安装** — 运行 `uv pip install -e ".[all]"` 以获取新的或更改的依赖项
5.  **配置迁移** — 检测自你当前版本以来添加的新配置选项，并提示你设置它们
6.  **消息网关自动重启** — 更新完成后，正在运行的消息网关会被刷新，以便新代码立即生效。由服务管理的消息网关（Linux 上的 systemd，macOS 上的 launchd）通过服务管理器重启。当 Hermes 可以将正在运行的 PID 映射回配置文件时，手动启动的消息网关会自动重新启动。

### 针对非默认分支进行更新：`--branch`

默认情况下，`hermes update` 跟踪 `origin/main`。传递 `--branch <name>` 可以针对不同的分支进行更新 — 这对于 QA 渠道、功能分支或候选发布版本测试很有用：

```bash
hermes update --branch release-candidate
hermes update --check --branch experimental   # 仅预览落后情况
```

如果你的本地检出位于不同的分支，Hermes 会自动暂存任何未提交的工作，将 HEAD 切换到目标分支，然后拉取。本地不存在的分支会自动从 `origin/<name>` 跟踪（`git checkout -B <name> origin/<name>`）。任何地方都不存在的分支会干净地失败 — 你的暂存更改会在退出前恢复，因此你永远不会陷入奇怪的状态。仅在非 `main` 分支上，`main` 独有的 fork-upstream 同步逻辑会自动跳过。

### 仅预览：`hermes update --check`

想在拉取之前知道是否有更新可用吗？运行 `hermes update --check` — 对于 Git 安装，它会获取并与 `origin/main` 比较提交；对于 pip 安装，它会查询 PyPI 获取最新版本。不会修改任何文件，也不会重启任何消息网关。在需要判断“是否有更新”的脚本和定时任务中很有用。

### 完整的更新前备份：`--backup`

对于高价值的配置文件（生产环境消息网关、共享团队安装），你可以选择在拉取前对 `HERMES_HOME`（配置、认证、会话、技能、配对）进行完整备份：

```bash
hermes update --backup
```

或者将其设置为每次运行的默认行为：

```yaml
# ~/.hermes/config.yaml
updates:
  pre_update_backup: true
```

`--backup` 在早期版本中是始终开启的行为，但在大型主目录上每次更新都会增加几分钟时间，所以现在改为可选。上面提到的轻量级配对数据快照仍然无条件运行。

### Windows：另一个 `hermes.exe` 正在运行

在 Windows 上，如果 `hermes update` 检测到另一个 `hermes.exe` 进程正在占用虚拟环境的入口点可执行文件 — 最常见的是 Hermes Desktop 应用程序生成的后端、另一个终端中打开的 `hermes` REPL 或正在运行的消息网关 — 它将拒绝运行：

```
$ hermes update
✗ Another hermes.exe is running:
    PID 12345  hermes.exe

  Updating now would fail to overwrite ...\venv\Scripts\hermes.exe because
  Windows blocks REPLACE on a running executable.

  Close Hermes Desktop, exit any open `hermes` REPLs, and
  stop the gateway (`hermes gateway stop`) before retrying.
  Override with `hermes update --force` if you've already
  confirmed those processes will not write to the venv.
```

关闭列出的进程并重新运行。如果你确定并发进程不会干扰（这种情况很少见 — 通常仅在防病毒软件垫片错误归属时有用），请传递 `--force` 以跳过检查。在这种情况下，更新程序仍将使用指数退避重试 `.exe` 重命名，并且在遇到顽固锁定时，通过 `MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT)` 将替换安排到下次重启，以便更新可以完成。

预期输出如下所示：

```
$ hermes update
Updating Hermes Agent...
📥 Pulling latest code...
Already up to date.  (或: Updating abc1234..def5678)
📦 Updating dependencies...
✅ Dependencies updated
🔍 Checking for new config options...
✅ Config is up to date  (或: Found 2 new options — running migration...)
🔄 Restarting gateways...
✅ Gateway restarted
✅ Hermes Agent updated successfully!
```

### 推荐的更新后验证

`hermes update` 处理主要的更新路径，但快速验证可以确认一切顺利落地：

1.  `git status --short` — 如果工作树意外变脏，请在继续之前检查
2.  `hermes doctor` — 检查配置、依赖项和服务健康状况
3.  `hermes --version` — 确认版本按预期更新
4.  如果你使用消息网关：`hermes gateway status`
5.  如果 `doctor` 报告 npm 审计问题：在标记的目录中运行 `npm audit fix`

:::warning 更新后工作树变脏
如果 `git status --short` 在 `hermes update` 后显示意外更改，请在继续之前停止并检查它们。这通常意味着本地修改被重新应用到更新后的代码之上，或者依赖项步骤刷新了锁文件。
:::

### 如果你的终端在更新过程中断开连接

`hermes update` 会保护自己免受意外终端丢失的影响：

-   更新忽略 `SIGHUP`，因此关闭 SSH 会话或终端窗口不再会在安装过程中终止它。`pip` 和 `git` 子进程继承此保护，因此 Python 环境不会因连接断开而处于半安装状态。
-   所有输出在更新运行时都会镜像到 `~/.hermes/logs/update.log`。如果你的终端消失，请重新连接并检查日志，查看更新是否完成以及消息网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

-   `Ctrl-C` (SIGINT) 和系统关机 (SIGTERM) 仍然会被响应 — 这些是故意的取消操作，而不是意外。

你不再需要将 `hermes update` 包装在 `screen` 或 `tmux` 中以在终端断开连接后存活。

### 检查当前版本

```bash
hermes version
```

与 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases)上的最新版本进行比较。

### 从消息平台更新

你也可以直接从 Telegram、Discord、Slack、WhatsApp 或 Teams 发送以下命令进行更新：

```
/update
```

这会拉取最新代码，更新依赖项，并重启正在运行的消息网关。机器人将在重启期间短暂离线（通常 5-15 秒），然后恢复。

### 手动更新

如果你手动安装（不是通过快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码
git pull origin main

# 重新安装（获取新的依赖项）
uv pip install -e ".[all]"

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

要回滚到特定的发布标签（替换你之前的标签 — 例如，最近的发布如 `v2026.5.16`，或来自 `git tag --sort=-version:refname` 的任何更早的标签）：

```bash
git checkout vX.Y.Z
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

# 或者用最新版本重建
nix profile upgrade hermes-agent
```

Nix 安装是不可变的 — 回滚由 Nix 的生成系统处理：

```bash
nix profile rollback
```

更多详情请参阅 [Nix 设置](./nix-setup.md)。

---

## 卸载

### Git 安装

```bash
hermes uninstall
```

卸载程序会给你选择保留配置文件（`~/.hermes/`）以备将来重新安装。

### pip 安装

```bash
pip uninstall hermes-agent
rm -rf ~/.hermes            # 可选 — 如果你计划重新安装，请保留
```

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