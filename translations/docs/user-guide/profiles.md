---
sidebar_position: 2
---

# 配置文件：运行多个 Agent

在同一台机器上运行多个独立的 Hermes Agent —— 每个 Agent 都拥有自己的配置、API 密钥、记忆、会话、技能和消息网关。

## 什么是配置文件？

配置文件是一个完全隔离的 Hermes 执行环境。每个配置文件都有自己的目录，包含其专属的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务和状态数据库。配置文件让你可以为不同目的运行独立的 Agent —— 例如一个编码助手、一个个人机器人、一个研究 Agent —— 而不会产生任何交叉污染。

当你创建一个配置文件时，它会自动成为一个独立的命令。创建一个名为 `coder` 的配置文件，你立即就拥有了 `coder chat`、`coder setup`、`coder gateway start` 等命令。

## 快速开始

```bash
hermes profile create coder       # 创建配置文件 + "coder" 命令别名
coder setup                       # 配置 API 密钥和模型
coder chat                        # 开始聊天
```

就是这样。`coder` 现在是一个完全独立的 Agent。它有自己的配置、自己的记忆、自己的一切。

## 创建配置文件

### 空白配置文件

```bash
hermes profile create mybot
```

创建一个全新的配置文件，并预置了捆绑的技能。运行 `mybot setup` 来配置 API 密钥、模型和消息网关令牌。

### 仅克隆配置 (`--clone`)

```bash
hermes profile create work --clone
```

将你当前配置文件的 `config.yaml`、`.env` 和 `SOUL.md` 复制到新的配置文件中。使用相同的 API 密钥和模型，但会话和记忆是全新的。编辑 `~/.hermes/profiles/work/.env` 以使用不同的 API 密钥，或编辑 `~/.hermes/profiles/work/SOUL.md` 以获得不同的人格。

### 克隆所有内容 (`--clone-all`)

```bash
hermes profile create backup --clone-all
```

复制**所有内容** —— 配置、API 密钥、人格、所有记忆、完整的会话历史、技能、定时任务、插件。一个完整的快照。适用于备份或分叉一个已有上下文的 Agent。

### 从特定配置文件克隆

```bash
hermes profile create work --clone --clone-from coder
```

:::tip Honcho 记忆 + 配置文件
启用 Honcho 时，`--clone` 会自动为新配置文件创建一个专用的 AI 对等体，同时共享相同的用户工作空间。每个配置文件都会构建自己的观察和身份。详情请参阅 [Honcho -- 多 Agent / 配置文件](./features/memory-providers.md#honcho)。
:::

## 使用配置文件

### 命令别名

每个配置文件都会自动在 `~/.local/bin/<name>` 处获得一个命令别名：

```bash
coder chat                    # 与 coder Agent 聊天
coder setup                   # 配置 coder 的设置
coder gateway start           # 启动 coder 的消息网关
coder doctor                  # 检查 coder 的健康状况
coder skills list             # 列出 coder 的技能
coder config set model.model anthropic/claude-sonnet-4
```

该别名适用于所有 hermes 子命令 —— 它本质上就是 `hermes -p <name>`。

### `-p` 标志

你也可以在任何命令中显式指定目标配置文件：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 在任何位置都有效
```

### 粘性默认值 (`hermes profile use`)

```bash
hermes profile use coder
hermes chat                   # 现在以 coder 为目标
hermes tools                  # 配置 coder 的工具
hermes profile use default    # 切换回默认
```

设置一个默认配置文件，这样普通的 `hermes` 命令就会以该配置文件为目标。类似于 `kubectl config use-context`。

### 了解当前状态

CLI 始终显示哪个配置文件处于活动状态：

- **提示符**：显示 `coder ❯` 而不是 `❯`
- **横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前配置文件的名称、路径、模型、消息网关状态

## 运行消息网关

每个配置文件都将其自己的消息网关作为独立的进程运行，并拥有自己的机器人令牌：

```bash
coder gateway start           # 启动 coder 的消息网关
assistant gateway start       # 启动 assistant 的消息网关（独立进程）
```

### 不同的机器人令牌

每个配置文件都有自己的 `.env` 文件。在每个文件中配置不同的 Telegram/Discord/Slack 机器人令牌：

```bash
# 编辑 coder 的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑 assistant 的令牌
nano ~/.hermes/profiles/assistant/.env
```

### 安全性：令牌锁

如果两个配置文件意外使用了相同的机器人令牌，第二个消息网关将被阻止，并显示一个清晰的错误信息，指出冲突的配置文件名称。支持 Telegram、Discord、Slack、WhatsApp 和 Signal。

### 持久化服务

```bash
coder gateway install         # 创建 hermes-gateway-coder systemd/launchd 服务
assistant gateway install     # 创建 hermes-gateway-assistant 服务
```

每个配置文件都有自己的服务名称。它们独立运行。

## 配置配置文件

每个配置文件都有自己的：

- **`config.yaml`** —— 模型、提供商、工具集、所有设置
- **`.env`** —— API 密钥、机器人令牌
- **`SOUL.md`** —— 人格和指令

```bash
coder config set model.model anthropic/claude-sonnet-4
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

## 更新

`hermes update` 会拉取一次代码（共享）并自动将新的捆绑技能同步到**所有**配置文件：

```bash
hermes update
# → 代码已更新 (12 次提交)
# → 技能已同步：default (已是最新), coder (+2 个新技能), assistant (+2 个新技能)
```

用户修改过的技能永远不会被覆盖。

## 管理配置文件

```bash
hermes profile list           # 显示所有配置文件及其状态
hermes profile show coder     # 显示一个配置文件的详细信息
hermes profile rename coder dev-bot   # 重命名（更新别名 + 服务）
hermes profile export coder   # 导出到 coder.tar.gz
hermes profile import coder.tar.gz   # 从存档导入
```

## 删除配置文件

```bash
hermes profile delete coder
```

这会停止消息网关，移除 systemd/launchd 服务，移除命令别名，并删除所有配置文件数据。系统会要求你输入配置文件名称以进行确认。

使用 `--yes` 跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认配置文件 (`~/.hermes`)。要删除所有内容，请使用 `hermes uninstall`。
:::

## Tab 补全

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将该行添加到你的 `~/.bashrc` 或 `~/.zshrc` 中以获得持久的补全功能。在 `-p` 之后补全配置文件名称、配置文件子命令和顶级命令。

## 工作原理

配置文件使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本会在启动 hermes 之前设置 `HERMES_HOME=~/.hermes/profiles/coder`。由于代码库中有 119+ 个文件通过 `get_hermes_home()` 解析路径，所有内容都会自动限定在配置文件的目录范围内 —— 配置、会话、记忆、技能、状态数据库、消息网关 PID、日志和定时任务。

默认配置文件就是 `~/.hermes` 本身。无需迁移 —— 现有安装的工作方式完全相同。