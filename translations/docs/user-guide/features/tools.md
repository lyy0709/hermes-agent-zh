---
sidebar_position: 1
title: "工具与工具集"
description: "Hermes Agent 工具概览 —— 可用工具、工具集工作原理及终端后端"
---

# 工具与工具集

工具是扩展 Agent 能力的函数。它们被组织成逻辑上的**工具集**，可按平台启用或禁用。

## 可用工具

Hermes 内置了广泛的工具注册表，涵盖网络搜索、浏览器自动化、终端执行、文件编辑、记忆、委派、RL 训练、消息传递、Home Assistant 等。

:::note
**Honcho 跨会话记忆**作为记忆提供商插件 (`plugins/memory/honcho/`) 提供，而非内置工具集。安装方法请参阅[插件](./plugins.md)。
:::

高级类别：

| 类别 | 示例 | 描述 |
|----------|----------|-------------|
| **网络** | `web_search`, `web_extract` | 搜索网络并提取页面内容。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令和操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 支持文本和视觉的交互式浏览器自动化。 |
| **媒体** | `vision_analyze`, `image_generate`, `text_to_speech` | 多模态分析与生成。 |
| **Agent 编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 规划、澄清、代码执行和子 Agent 委派。 |
| **记忆与回忆** | `memory`, `session_search` | 持久化记忆和会话搜索。 |
| **自动化与交付** | `cronjob`, `send_message` | 具有创建/列出/更新/暂停/恢复/运行/删除操作的定时任务，以及外发消息传递。 |
| **集成** | `ha_*`, MCP 服务器工具, `rl_*` | Home Assistant、MCP、RL 训练和其他集成。 |

关于权威的代码派生注册表，请参阅[内置工具参考](/docs/reference/tools-reference)和[工具集参考](/docs/reference/toolsets-reference)。

:::tip Nous 工具网关
付费的 [Nous Portal](https://portal.nousresearch.com) 订阅者可以通过 **[工具网关](tool-gateway.md)** 使用网络搜索、图像生成、TTS 和浏览器自动化 —— 无需单独的 API 密钥。运行 `hermes model` 启用它，或使用 `hermes tools` 配置单个工具。
:::

## 使用工具集

```bash
# 使用特定工具集
hermes chat --toolsets "web,terminal"

# 查看所有可用工具
hermes tools

# 按平台配置工具（交互式）
hermes tools
```

常见的工具集包括 `web`、`search`、`terminal`、`file`、`browser`、`vision`、`image_gen`、`moa`、`skills`、`tts`、`todo`、`memory`、`session_search`、`cronjob`、`code_execution`、`delegation`、`clarify`、`homeassistant`、`messaging`、`spotify`、`discord`、`discord_admin`、`debugging`、`safe` 和 `rl`。

完整列表请参阅[工具集参考](/docs/reference/toolsets-reference)，包括平台预设，如 `hermes-cli`、`hermes-telegram`，以及动态 MCP 工具集，如 `mcp-<server>`。

## 终端后端

终端工具可以在不同的执行环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在您的机器上运行（默认） | 开发、受信任的任务 |
| `docker` | 隔离的容器 | 安全性、可复现性 |
| `ssh` | 远程服务器 | 沙盒化，使 Agent 远离其自身代码 |
| `singularity` | HPC 容器 | 集群计算、无 root 权限 |
| `modal` | 云端执行 | 无服务器、可扩展 |
| `daytona` | 云端沙盒工作空间 | 持久化的远程开发环境 |
| `vercel_sandbox` | Vercel Sandbox 云端微虚拟机 | 云端执行，支持快照备份的文件系统持久化 |

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
terminal:
  backend: local    # 或：docker, ssh, singularity, modal, daytona, vercel_sandbox
  cwd: "."          # 工作目录
  timeout: 180      # 命令超时时间（秒）
```

### Docker 后端

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

### SSH 后端

推荐用于安全性 —— Agent 无法修改其自身代码：

```yaml
terminal:
  backend: ssh
```
```bash
# 在 ~/.hermes/.env 中设置凭据
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=myuser
TERMINAL_SSH_KEY=~/.ssh/id_rsa
```

### Singularity/Apptainer

```bash
# 为并行工作器预构建 SIF
apptainer build ~/python.sif docker://python:3.11-slim

# 配置
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal（无服务器云端）

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### Vercel Sandbox

```bash
pip install 'hermes-agent[vercel]'
hermes config set terminal.backend vercel_sandbox
hermes config set terminal.vercel_runtime node24
```

使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 三者进行身份验证。这种访问令牌设置是部署以及在 Render、Railway、Docker 和类似主机上运行普通长期 Hermes 进程的受支持路径。支持的运行时是 `node24`、`node22` 和 `python3.13`；Hermes 默认将 `/vercel/sandbox` 作为远程工作空间根目录。

对于一次性的本地开发，Hermes 也接受短期的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

从已链接的 Vercel 项目目录中：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

当 `container_persistent: true` 时，Hermes 使用 Vercel 快照在同一任务的不同沙盒重建之间保留文件系统状态。这可以包括沙盒内由 Hermes 同步的凭据、技能和缓存文件。快照不保留活动进程、PID 空间或相同的活动沙盒身份。

后台终端命令使用 Hermes 的通用非本地进程流程：在沙盒存活期间，通过正常的进程工具进行生成、轮询、等待、记录和终止，但 Hermes 在清理或重启后不提供原生的 Vercel 分离进程恢复功能。

保持 `container_disk` 未设置或使用共享默认值 `51200`；自定义磁盘大小不受 Vercel Sandbox 支持，将导致诊断/后端创建失败。

### 容器资源

为所有容器后端配置 CPU、内存、磁盘和持久性：

```yaml
terminal:
  backend: docker  # 或 singularity, modal, daytona, vercel_sandbox
  container_cpu: 1              # CPU 核心数（默认：1）
  container_memory: 5120        # 内存大小（MB）（默认：5GB）
  container_disk: 51200         # 磁盘大小（MB）（默认：50GB）
  container_persistent: true    # 跨会话持久化文件系统（默认：true）
```

当 `container_persistent: true` 时，安装的软件包、文件和配置在会话间保留。

### 容器安全性

所有容器后端都运行在安全加固环境中：

- 只读根文件系统（Docker）
- 所有 Linux 能力被丢弃
- 无权限提升
- PID 限制（256 个进程）
- 完整的命名空间隔离
- 通过卷实现持久化工作空间，而非可写的根层

Docker 可以选择性地通过 `terminal.docker_forward_env` 接收显式的环境变量允许列表，但转发的变量对容器内的命令可见，应视为已暴露给该会话。

## 后台进程管理

启动后台进程并管理它们：

```python
terminal(command="pytest -v tests/", background=true)
# 返回：{"session_id": "proc_abc123", "pid": 12345}

# 然后使用进程工具进行管理：
process(action="list")       # 显示所有运行中的进程
process(action="poll", session_id="proc_abc123")   # 检查状态
process(action="wait", session_id="proc_abc123")   # 阻塞直到完成
process(action="log", session_id="proc_abc123")    # 完整输出
process(action="kill", session_id="proc_abc123")   # 终止
process(action="write", session_id="proc_abc123", data="y")  # 发送输入
```

PTY 模式 (`pty=true`) 启用交互式 CLI 工具，如 Codex 和 Claude Code。

## Sudo 支持

如果命令需要 sudo，系统会提示您输入密码（在会话期间缓存）。或者在 `~/.hermes/.env` 中设置 `SUDO_PASSWORD`。

:::warning
在消息传递平台上，如果 sudo 失败，输出将包含提示，建议将 `SUDO_PASSWORD` 添加到 `~/.hermes/.env`。
:::