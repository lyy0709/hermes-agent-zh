---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

# 配置

所有设置都存储在 `~/.hermes/` 目录中，便于访问。

## 目录结构

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和密钥
├── auth.json       # OAuth 提供商凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示词中的槽位 #1）
├── memories/       # 持久化记忆（MEMORY.md, USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 定时任务
├── sessions/       # 消息网关会话
└── logs/           # 日志（errors.log, gateway.log — 密钥自动脱敏）
```

## 管理配置

```bash
hermes config              # 查看当前配置
hermes config edit         # 在编辑器中打开 config.yaml
hermes config set KEY VAL  # 设置特定值
hermes config check        # 检查缺失的选项（更新后）
hermes config migrate      # 交互式添加缺失的选项

# 示例：
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # 保存到 .env
```

:::tip
`hermes config set` 命令会自动将值路由到正确的文件 — API 密钥保存到 `.env`，其他所有内容保存到 `config.yaml`。
:::

## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1.  **CLI 参数** — 例如，`hermes chat --model anthropic/claude-sonnet-4`（每次调用覆盖）
2.  **`~/.hermes/config.yaml`** — 所有非密钥设置的主要配置文件
3.  **`~/.hermes/.env`** — 环境变量的后备；**必需**用于密钥（API 密钥、Token、密码）
4.  **内置默认值** — 当没有设置其他内容时，硬编码的安全默认值

:::info 经验法则
密钥（API 密钥、机器人 Token、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、记忆限制、工具集）放在 `config.yaml` 中。当两者都设置时，对于非密钥设置，`config.yaml` 优先。
:::

## 环境变量替换

您可以在 `config.yaml` 中使用 `${VAR_NAME}` 语法引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中的多个引用有效：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将按字面保留（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法 — 裸 `$VAR` 不会被扩展。

关于 AI 提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、后备模型等），请参阅 [AI 提供商](/docs/integrations/providers)。

### 提供商超时

您可以设置 `providers.<id>.request_timeout_seconds` 作为提供商范围的请求超时，以及 `providers.<id>.models.<model>.timeout_seconds` 作为模型特定的覆盖。适用于每个传输上的主要轮次客户端（OpenAI-wire、原生 Anthropic、Anthropic 兼容）、后备链、凭据轮换后的重建，以及（对于 OpenAI-wire）每个请求的超时关键字参数 — 因此配置的值优先于旧的 `HERMES_API_TIMEOUT` 环境变量。

您还可以设置 `providers.<id>.stale_timeout_seconds` 用于非流式陈旧调用检测器，以及 `providers.<id>.models.<model>.stale_timeout_seconds` 作为模型特定的覆盖。这优先于旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

不设置这些将保留旧的默认值（`HERMES_API_TIMEOUT=1800`s，`HERMES_API_CALL_STALE_TIMEOUT=300`s，原生 Anthropic 900s）。目前未为 AWS Bedrock 连接（`bedrock_converse` 和 AnthropicBedrock SDK 路径都使用具有自己超时配置的 boto3）。请参阅 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 中的注释示例。

## 终端后端配置

Hermes 支持七种终端后端。每种都决定了 Agent 的 shell 命令实际在哪里执行 — 您的本地机器、Docker 容器、通过 SSH 的远程服务器、Modal 云沙盒（直接或通过 Nous 管理的网关）、Daytona 工作区、Vercel Sandbox 或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | vercel_sandbox | singularity
  cwd: "."          # 消息网关/定时任务的工作目录（CLI 始终使用启动目录）
  timeout: 180      # 每个命令的超时时间（秒）
  env_passthrough: []  # 要转发到沙盒化执行的环境变量名称（终端 + execute_code）
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于云沙盒，如 Modal、Daytona 和 Vercel Sandbox，`container_persistent: true` 意味着 Hermes 将尝试在沙盒重建过程中保留文件系统状态。它不保证同一个活动沙盒、PID 空间或后台进程稍后仍在运行。

### 后端概述

| 后端 | 命令运行位置 | 隔离性 | 最适合 |
|---------|-------------------|-----------|----------|
| **local** | 直接在您的机器上 | 无 | 开发、个人使用 |
| **docker** | 单个持久化 Docker 容器（跨会话、`/new`、子 Agent 共享） | 完全（命名空间、cap-drop） | 安全沙盒化、CI/CD |
| **ssh** | 通过 SSH 的远程服务器 | 网络边界 | 远程开发、强大硬件 |
| **modal** | Modal 云沙盒 | 完全（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全（云容器） | 托管的云开发环境 |
| **vercel_sandbox** | Vercel Sandbox | 完全（云微虚拟机） | 具有快照支持的文件系统持久化的云执行 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间（--containall） | HPC 集群、共享机器 |
### 本地后端

默认选项。命令直接在您的机器上运行，没有隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

:::warning
Agent 拥有与您的用户账户相同的文件系统访问权限。使用 `hermes tools` 来禁用您不需要的工具，或者切换到 Docker 后端以获得沙盒隔离。
:::

### Docker 后端

在 Docker 容器内运行命令，并进行了安全加固（所有能力被丢弃、无权限提升、PID 限制）。

**单个持久化容器，而非每个命令一个。** Hermes 在首次使用时启动一个长期运行的容器，并通过 `docker exec` 将每个终端、文件和 `execute_code` 调用路由到同一个容器中——跨越会话、`/new`、`/reset` 和 `delegate_task` 子代理——在 Hermes 进程的生命周期内。工作目录更改、已安装的包以及 `/workspace` 中的文件会从一个工具调用延续到下一个，就像本地 shell 一样。容器在关闭时停止并移除。详情请参阅下面的**容器生命周期**。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 将启动目录挂载到 /workspace
  docker_run_as_host_user: false   # 参见下面的“以主机用户身份运行容器”
  docker_forward_env:              # 要转发到容器中的环境变量
    - "GITHUB_TOKEN"
  docker_volumes:                  # 主机目录挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro 表示只读

  # 资源限制
  container_cpu: 1                 # CPU 核心数 (0 = 无限制)
  container_memory: 5120           # MB (0 = 无限制)
  container_disk: 51200            # MB (需要在 XFS+pquota 上启用 overlay2)
  container_persistent: true       # 在会话间持久化 /workspace 和 /root
```

**要求：** Docker Desktop 或 Docker Engine 已安装并正在运行。Hermes 会探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用程序包）。Podman 开箱即用：当两者都安装时，设置 `HERMES_DOCKER_BINARY=podman`（或完整路径）来强制使用它。

**容器生命周期：** Hermes 为每个终端和文件工具调用重用单个长期运行的容器（`docker run -d ... sleep 2h`），跨越会话、`/new`、`/reset` 和 `delegate_task` 子代理，在 Hermes 进程的生命周期内。命令通过 `docker exec` 使用登录 shell 运行，因此工作目录更改、已安装的包以及 `/workspace` 中的文件都会从一个工具调用持续到下一个。容器在 Hermes 关闭时（或在空闲清理回收它时）停止并移除。

通过 `delegate_task(tasks=[...])` 生成的并行子代理共享这一个容器——并发的 `cd`、环境变量修改和写入同一路径会发生冲突。如果子代理需要隔离的沙盒，它必须通过 `register_task_env_overrides()` 注册每个任务的镜像覆盖，RL 和基准测试环境（TerminalBench2, HermesSweEnv 等）会为其每个任务的 Docker 镜像自动执行此操作。

**安全加固：**
- `--cap-drop ALL`，仅重新添加 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 为 `/tmp` (512MB)、`/var/tmp` (256MB)、`/run` (64MB) 设置大小限制的 tmpfs

**凭证转发：** `docker_forward_env` 中列出的环境变量首先从您的 shell 环境解析，然后从 `~/.hermes/.env` 解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

### SSH 后端

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 进行连接复用（5分钟空闲保活）。默认启用持久化 shell——状态（当前工作目录、环境变量）在命令间保持。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持一个长期运行的 bash 会话 (默认: true)
```

**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选：**

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | (系统默认) | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 shell |

**工作原理：** 在初始化时使用 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 进行连接。持久化 shell 在远程主机上保持一个 `bash -l` 进程存活，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到一次性模式。

### Modal 后端

在 [Modal](https://modal.com) 云沙盒中运行命令。每个任务获得一个具有可配置 CPU、内存和磁盘的隔离 VM。文件系统可以在会话间进行快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # 快照/恢复文件系统
```

**要求：** 需要 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，或者 `~/.modal.toml` 配置文件。

**持久化：** 启用后，沙盒文件系统在清理时进行快照，并在下一个会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这保留了文件系统状态，而不是活动进程、PID 空间或后台作业。

**凭证文件：** 自动从 `~/.hermes/` 挂载（OAuth 令牌等），并在每个命令前同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 管理的工作空间中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB (最大 10 GiB)
  container_persistent: true       # 停止/恢复而非删除
```

**要求：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用后，沙盒在清理时停止（而非删除），并在下一个会话时恢复。沙盒名称遵循模式 `hermes-{task_id}`。
**磁盘限制：** Daytona 强制执行 10 GiB 的最大限制。超过此限制的请求将被截断并发出警告。

### Vercel Sandbox 后端

在 [Vercel Sandbox](https://vercel.com/docs/vercel-sandbox) 云微虚拟机中运行命令。Hermes 使用普通的终端和文件工具界面；没有面向模型的 Vercel 特定工具。

```yaml
terminal:
  backend: vercel_sandbox
  vercel_runtime: node24          # node24 | node22 | python3.13
  cwd: /vercel/sandbox            # 默认工作空间根目录
  container_persistent: true      # 快照/恢复文件系统
  container_disk: 51200           # 仅共享默认值；不支持自定义磁盘
```

**必需安装：** 安装可选的 SDK 额外包：

```bash
pip install 'hermes-agent[vercel]'
```

**必需的身份验证：** 使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 这三个环境变量配置访问令牌认证。这是在 Render、Railway、Docker 及类似主机上进行部署和正常长期运行的 Hermes 进程所支持的设置。

对于一次性的本地开发，Hermes 也接受短期的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

在已链接的 Vercel 项目目录中，可以省略项目名称：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

OIDC 令牌是短期的，不应作为文档化的部署路径使用。

**运行时：** `terminal.vercel_runtime` 支持 `node24`、`node22` 和 `python3.13`。如果未设置，Hermes 默认为 `node24`。

**持久性：** 当 `container_persistent: true` 时，Hermes 会在清理期间对沙盒文件系统进行快照，并在后续为同一任务从该快照恢复沙盒。快照内容可以包括复制到沙盒中的 Hermes 同步的凭据、技能和缓存文件。这仅保留文件系统状态；不保留活动的沙盒身份、PID 空间、shell 状态或运行的后台进程。

**后台命令：** `terminal(background=true)` 使用 Hermes 的通用非本地后台进程流程。在沙盒存活期间，您可以通过常规的进程工具生成、轮询、等待、查看日志和终止进程。Hermes 在清理或重启后不提供原生的 Vercel 分离进程恢复功能。

**磁盘大小调整：** Vercel Sandbox 目前不支持 Hermes 的 `container_disk` 资源调节旋钮。请保持 `container_disk` 未设置或使用共享默认值 `51200`；非默认值会导致诊断和创建后端失败，而不是被静默忽略。

### Singularity/Apptainer 后端

在 [Singularity/Apptainer](https://apptainer.org) 容器中运行命令。专为 Docker 不可用的 HPC 集群和共享机器设计。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB
  container_persistent: true       # 可写覆盖层在会话间持久化
```

**要求：** `$PATH` 中存在 `apptainer` 或 `singularity` 二进制文件。

**镜像处理：** Docker URL（`docker://...`）会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件直接使用。

**临时目录：** 按顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（HPC 惯例）→ `~/.hermes/sandboxes/singularity`。

**隔离：** 使用 `--containall --no-home` 实现完整的命名空间隔离，不挂载主机主目录。

### 常见终端后端问题

如果终端命令立即失败或终端工具报告为禁用：

- **Local** — 无特殊要求。入门时最安全的默认设置。
- **Docker** — 运行 `docker version` 以验证 Docker 是否正常工作。如果失败，请修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少任何一个，Hermes 会记录清晰的错误信息。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml` 文件。运行 `hermes doctor` 进行检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 处理服务器 URL 配置。
- **Singularity** — 需要 `$PATH` 中存在 `apptainer` 或 `singularity`。在 HPC 集群上常见。

如有疑问，请将 `terminal.backend` 设置回 `local`，并首先验证命令能否在那里运行。

### 销毁时的远程到主机文件同步

对于 **SSH**、**Modal** 和 **Daytona** 后端（任何 Agent 的工作树所在机器与运行 Hermes 的主机不同的情况），Hermes 会跟踪 Agent 在远程沙盒中接触过的文件，并在会话销毁/沙盒清理时，**将修改过的文件同步回主机**，位置在 `~/.hermes/cache/remote-syncs/<session-id>/` 下。

- 触发条件：会话关闭、`/new`、`/reset`、消息网关消息超时、当子 Agent 使用了远程后端时 `delegate_task` 子 Agent 完成。
- 覆盖 Agent 修改的整个树，而不仅仅是它显式打开的文件。新增、编辑和删除都会被捕获。
- 当您去查找时，远程沙盒可能已被销毁；本地的 `~/.hermes/cache/remote-syncs/…` 副本是 Agent 所做更改的权威记录。
- 大型二进制输出（模型检查点、原始数据集）受大小限制 — 同步会跳过超过 `file_sync_max_mb`（默认 `100`）的文件。如果您期望有更大的产物返回，请调高此值。

```yaml
terminal:
  file_sync_max_mb: 100     # 默认值 — 同步每个最大 100 MB 的文件
  file_sync_enabled: true   # 默认值 — 设置为 false 以完全跳过同步
```

这就是您从会话结束后被销毁的临时云沙盒中恢复结果的方式，无需告诉 Agent 显式地 `scp` 或 `modal volume put` 每个产物。

### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许您与容器共享主机目录。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/.hermes/cache/documents:/output" # 消息网关可见的导出目录
```
这适用于：
- **向 Agent 提供文件**（数据集、配置文件、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出文件）
- **共享工作区**，您和 Agent 都可以访问相同的文件

如果您使用消息网关，并希望 Agent 通过 `MEDIA:/...` 发送生成的文件，建议使用专用的、主机可见的导出挂载点，例如 `/home/user/.hermes/cache/documents:/output`。

- 在 Docker 内将文件写入 `/output/...`
- 在 `MEDIA:` 中发出**主机路径**，例如：`MEDIA:/home/user/.hermes/cache/documents/report.txt`
- **不要**发出 `/workspace/...` 或 `/output/...`，除非该确切路径也存在于主机上的网关进程中

:::warning
YAML 中的重复键会静默覆盖较早的键。如果您已经有一个 `docker_volumes:` 块，请将新的挂载合并到同一个列表中，而不是在文件后面添加另一个 `docker_volumes:` 键。
:::

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

### Docker 凭据转发

默认情况下，Docker 终端会话不会继承任意的主机凭据。如果您需要在容器内使用特定的 Token，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 首先从您当前的 shell 解析每个列出的变量，如果变量已通过 `hermes config set` 保存，则回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。只转发您愿意暴露给终端会话的凭据。
:::

### 以主机用户身份运行容器

默认情况下，Docker 容器以 `root`（UID 0）身份运行。在 `/workspace` 或其他绑定挂载点内创建的文件最终在主机上归 root 所有，因此在会话结束后，您必须使用 `sudo chown` 才能从主机编辑器编辑它们。`terminal.docker_run_as_host_user` 标志可以解决此问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # 默认值：false
```

启用后，Hermes 会将 `--user $(id -u):$(id -g)` 附加到 `docker run` 命令，这样写入绑定挂载目录（`/workspace`、`/root`、`docker_volumes` 中的任何内容）的文件将归您的主机用户所有，而不是 root。代价是：容器不能再执行 `apt install` 或写入 root 拥有的路径，如 `/root/.npm`——如果您两者都需要，请使用其 `HOME` 归非 root 用户所有的基础镜像（或在镜像构建时添加您所需的工具）。

为了保持向后兼容性，请将其保留为 `false`（默认值）。当您的工作流主要是“编辑挂载的主机文件”并且厌倦了 `sudo chown -R` 时，请打开此选项。

### 可选：将启动目录挂载到 `/workspace`

默认情况下，Docker 沙盒保持隔离。除非您明确选择加入，否则 Hermes **不会**将您当前的主机工作目录传递到容器中。

在 `config.yaml` 中启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果您从 `~/projects/my-app` 启动 Hermes，该主机目录将被绑定挂载到 `/workspace`
- Docker 后端在 `/workspace` 中启动
- 文件工具和终端命令都可以看到相同的挂载项目

禁用时，除非您通过 `docker_volumes` 显式挂载某些内容，否则 `/workspace` 仍归沙盒所有。

安全权衡：
- `false` 保留沙盒边界
- `true` 让沙盒直接访问您启动 Hermes 的目录

仅在您有意希望容器处理实时主机文件时，才使用此选择加入选项。

### 持久化 Shell

默认情况下，每个终端命令都在其自己的子进程中运行——工作目录、环境变量和 shell 变量在命令之间重置。当启用**持久化 Shell** 时，会在多个 `execute()` 调用之间保持一个长期存活的 bash 进程，以便状态在命令之间得以保留。

这对于 **SSH 后端** 最有用，因为它还消除了每个命令的连接开销。持久化 Shell **默认对 SSH 启用**，对本地后端禁用。

```yaml
terminal:
  persistent_shell: true   # 默认值 — 为 SSH 启用持久化 Shell
```

要禁用：

```bash
hermes config set terminal.persistent_shell false
```

**在命令之间持久化的内容：**
- 工作目录（`cd /tmp` 对下一个命令保持有效）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 层级 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 遵循配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

每个后端的环变量具有最高优先级。如果您也想在本地后端使用持久化 Shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 Shell 的 stdin 已被 IPC 协议占用。
:::

有关每个后端的详细信息，请参阅[代码执行](features/code-execution.md)和 README 的[终端部分](features/tools.md)。

## 技能设置

技能可以通过其 SKILL.md 的 frontmatter 声明自己的配置设置。这些是非机密值（路径、偏好设置、域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # 示例 — 每个技能定义自己的键
```

**技能设置的工作原理：**

- `hermes config migrate` 扫描所有启用的技能，查找未配置的设置，并提示您进行配置
- `hermes config show` 在“技能设置”下显示所有技能设置及其所属的技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```
关于在自定义技能中声明配置设置的详细信息，请参阅 [创建技能 — 配置设置](/docs/developer-guide/creating-skills#config-settings-configyaml)。

### 对 Agent 创建技能写入的防护

当 Agent 使用 `skill_manage` 创建、编辑、修补或删除技能时，Hermes 可以选择性地扫描新增/更新的内容，查找危险的关键词模式（凭据窃取、明显的提示词注入、数据外泄指令）。扫描器**默认关闭**——因为真实的 Agent 工作流中，合法地操作 `~/.ssh/` 或提及 `$OPENAI_API_KEY` 的情况过于频繁地触发了启发式规则。如果你希望扫描器在 Agent 的技能写入落地前提示你，可以重新开启它：

```yaml
skills:
  guard_agent_created: true   # 默认值: false
```

开启后，任何被标记的 `skill_manage` 写入操作都会显示一个包含扫描器理由的批准提示。批准的写入会落地；拒绝的写入会向 Agent 返回一个解释性错误。

## 记忆配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
```

## 文件读取安全

控制单次 `read_file` 调用可以返回多少内容。超过限制的读取会被拒绝，并返回一个错误，告知 Agent 使用 `offset` 和 `limit` 来读取更小的范围。这可以防止单次读取压缩的 JS 包或大型数据文件时淹没上下文窗口。

```yaml
file_read_max_chars: 100000  # 默认值 — ~25-35K tokens
```

如果你使用的是具有大上下文窗口的模型，并且经常读取大文件，可以提高此值。对于小上下文模型，可以降低此值以保持读取效率：

```yaml
# 大上下文模型 (200K+)
file_read_max_chars: 200000

# 小型本地模型 (16K 上下文)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重——如果同一文件区域被读取两次且文件未更改，则会返回一个轻量级的存根，而不是重新发送内容。这在上下文压缩后会重置，以便 Agent 在其内容被摘要化后可以重新读取文件。

## 工具输出截断限制

三个相关的上限控制工具在 Hermes 截断其输出前可以返回多少原始输出：

```yaml
tool_output:
  max_bytes: 50000        # 终端输出上限 (字符数)
  max_lines: 2000         # read_file 分页上限
  max_line_length: 2000   # read_file 行号视图中每行的上限
```

- **`max_bytes`** — 当 `terminal` 命令产生的 stdout/stderr 组合字符数超过此值时，Hermes 会保留前 40% 和后 60%，并在它们之间插入一个 `[OUTPUT TRUNCATED]` 通知。默认值 `50000`（≈12-15K tokens，取决于典型的 Tokenizer）。
- **`max_lines`** — 单次 `read_file` 调用 `limit` 参数的上限。超过此值的请求会被限制，以防止单次读取淹没上下文窗口。默认值 `2000`。
- **`max_line_length`** — 当 `read_file` 输出带行号的视图时应用的每行上限。超过此长度的行会被截断为此字符数，后跟 `... [truncated]`。默认值 `2000`。

对于具有大上下文窗口、能够承受每次调用更多原始输出的模型，可以提高这些限制。对于小上下文模型，可以降低它们以保持工具结果紧凑：

```yaml
# 大上下文模型 (200K+)
tool_output:
  max_bytes: 150000
  max_lines: 5000

# 小型本地模型 (16K 上下文)
tool_output:
  max_bytes: 20000
  max_lines: 500
```

## 全局工具集禁用

要在一个地方同时抑制 CLI 和所有消息网关平台上的特定工具集，请在 `agent.disabled_toolsets` 下列出它们的名称：

```yaml
agent:
  disabled_toolsets:
    - memory       # 隐藏记忆工具 + MEMORY_GUIDANCE 注入
    - web          # 在任何地方禁用 web_search / web_extract
```

这会在每个平台的工具配置（由 `hermes tools` 写入的 `platform_toolsets`）**之后**应用，因此此处列出的工具集总是会被移除——即使某个平台的保存配置中仍然列出了它。当你想要一个单一的开关来实现“在所有地方关闭 X”，而不是在 `hermes tools` UI 中编辑 15 多个平台行时，请使用此功能。

将列表留空或省略该键，则无操作。

## Git 工作树隔离

为在同一仓库上并行运行多个 Agent 启用隔离的 git 工作树：

```yaml
worktree: true    # 始终创建工作树 (与 hermes -w 相同)
# worktree: false # 默认值 — 仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个带有自己分支的新工作树。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的工作树会在退出时被移除；脏的工作树会被保留以供手动恢复。

你也可以通过在仓库根目录下的 `.worktreeinclude` 文件中列出要复制到工作树中的 git 忽略文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩

Hermes 会自动压缩长对话，以保持在模型的上下文窗口内。压缩摘要器是一个独立的 LLM 调用——你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（没有环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # 开启/关闭压缩
  threshold: 0.50                                   # 在此上下文限制百分比时触发压缩
  target_ratio: 0.20                                # 作为最近尾部保留的阈值比例
  protect_last_n: 20                                # 保持未压缩的最小最近消息数
  hygiene_hard_message_limit: 400                   # 消息网关安全阀 — 见下文

# 摘要模型/提供商在 auxiliary 下配置：
auxiliary:
  compression:
    model: ""                                       # 空 = 使用主聊天模型。覆盖示例："google/gemini-3-flash-preview" 以使用更便宜/更快的压缩。
    provider: "auto"                                # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等。
    base_url: null                                  # 自定义 OpenAI 兼容端点 (覆盖 provider)
```
:::info 旧配置迁移
旧版配置中的 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 在首次加载时（配置版本 17）会自动迁移到 `auxiliary.compression.*`。无需手动操作。
:::

`hygiene_hard_message_limit` 是仅用于消息网关的**预压缩安全阀**。当失控的会话包含数千条消息时，可能在正常的上下文百分比阈值触发前就触及模型上下文限制；当消息数量超过此上限时，无论 Token 使用情况如何，Hermes 都会强制进行压缩。默认值为 `400` —— 对于通常有超长会话的平台可提高此值，降低此值则会强制进行更激进的压缩。在运行中的网关上编辑此值会在下一条消息生效（见下文）。

:::tip 压缩和上下文长度的网关热重载
自近期版本起，在运行中的网关上编辑 `config.yaml` 中的 `model.context_length` 或任何 `compression.*` 键值，会在下一条消息生效 —— 无需重启网关、无需 `/reset`、也无需轮换会话。缓存的 Agent 签名包含这些键，因此网关在检测到更改时会透明地重建 Agent。API 密钥和工具/技能配置仍需要通常的重载路径。
:::

### 常见设置

**默认（自动检测）—— 无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用您的主提供商和主模型。如果您希望压缩使用比主聊天模型更便宜的模型，可以按任务覆盖（例如 `auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制使用特定提供商**（基于 OAuth 或 API 密钥）：
```yaml
auxiliary:
  compression:
    provider: nous
    model: gemini-3-flash
```
适用于任何提供商：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管、Ollama、zai、DeepSeek 等）：
```yaml
auxiliary:
  compression:
    model: glm-4.7
    base_url: https://api.z.ai/api/coding/paas/v4
```
指向自定义的 OpenAI 兼容端点。使用 `OPENAI_API_KEY` 进行身份验证。

### 三个旋钮如何交互

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto` （默认） | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商，使用其身份验证 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供商） |

:::warning 摘要模型上下文长度要求
摘要模型**必须**拥有至少与您的主 Agent 模型一样大的上下文窗口。压缩器将对话的完整中间部分发送给摘要模型 —— 如果该模型的上下文窗口小于主模型，摘要调用将因上下文长度错误而失败。发生这种情况时，中间轮次将被**丢弃而不进行摘要**，从而静默地丢失对话上下文。如果您覆盖了模型，请验证其上下文长度是否达到或超过您的主模型。
:::

## 上下文引擎

上下文引擎控制在接近模型 Token 限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（参见[上下文压缩](/docs/developer-guide/context-compression-and-caching)）。插件引擎可以用其他策略替换它。

```yaml
context:
  engine: "compressor"    # 默认值 —— 内置有损摘要
```

要使用插件引擎（例如，用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活** —— 您必须将 `context.engine` 显式设置为插件名称。可通过 `hermes plugins` → Provider Plugins → Context Engine 浏览和选择可用的引擎。

有关内存插件的类似单选系统，请参阅[记忆提供商](/docs/user-guide/features/memory-providers)。

## 迭代预算压力

当 Agent 处理具有许多工具调用的复杂任务时，它可能会在未意识到预算即将耗尽的情况下快速消耗其迭代预算（默认值：90 轮）。预算压力会在接近限制时自动警告模型：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息 —— 这保留了提示词缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认值：90）
  api_max_retries: 3           # 在启用备用方案前，每个提供商的重试次数（默认值：3）
```

预算压力默认启用。Agent 会自然地看到作为工具结果一部分的警告，鼓励它在迭代次数用完之前整合工作并给出响应。

当迭代预算完全耗尽时，CLI 会向用户显示通知：`⚠ Iteration budget reached (90/90) — response may be incomplete`。如果预算在活动工作中耗尽，Agent 会在停止前生成已完成工作的摘要。

`agent.api_max_retries` 控制在启用备用提供商切换**之前**，Hermes 在遇到瞬时错误（速率限制、连接中断、5xx 错误）时重试提供商 API 调用的次数。默认值为 `3` —— 总共尝试四次。如果您配置了[备用提供商](/docs/user-guide/features/fallback-providers)并希望更快地故障转移，请将此值降至 `0`，这样主提供商上的第一个瞬时错误会立即切换到备用提供商，而不是对不稳定的端点进行重复重试。

### API 超时

Hermes 为流式传输设置了单独的超时层，并为非流式调用设置了陈旧检测器。只有当您将它们保留为隐式默认值时，陈旧检测器才会仅针对本地提供商自动调整。
| 超时设置 | 默认值 | 本地提供商 | 配置 / 环境变量 |
|---------|---------|----------------|--------------|
| Socket 读取超时 | 120s | 自动提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180s | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| 陈旧非流检测 | 300s | 当未显式设置时自动禁用 | `providers.<id>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 保持不变 | `providers.<id>.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |

**Socket 读取超时** 控制 httpx 等待提供商返回下一个数据块的时间。本地 LLM 在处理大上下文进行预填充时，可能需要数分钟才能生成第一个 Token，因此当 Hermes 检测到本地端点时，会将此超时提升至 30 分钟。如果你显式设置了 `HERMES_STREAM_READ_TIMEOUT`，无论端点检测结果如何，都将始终使用该值。

**陈旧流检测** 会终止那些接收 SSE 保活 ping 但没有实际内容的连接。对于本地提供商，此功能完全禁用，因为它们在预填充期间不会发送保活 ping。

**陈旧非流检测** 会终止长时间未产生响应的非流式调用。默认情况下，Hermes 在本地端点上禁用此功能，以避免在长时间预填充期间产生误报。如果你显式设置了 `providers.<id>.stale_timeout_seconds`、`providers.<id>.models.<model>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT`，即使在本地端点上也会遵循该显式值。

## 上下文压力警告

与迭代预算压力不同，上下文压力跟踪对话距离**压缩阈值**（触发上下文压缩以总结旧消息的点）有多近。这有助于你和 Agent 了解对话何时变得过长。

| 进度 | 级别 | 发生的情况 |
|----------|-------|-------------|
| 距离阈值 **≥ 60%** | 信息 | CLI 显示青色进度条；消息网关发送信息通知 |
| 距离阈值 **≥ 85%** | 警告 | CLI 显示粗体黄色进度条；消息网关警告即将进行压缩 |

在 CLI 中，上下文压力在工具输出流中显示为进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会告知你上下文可能会被截断。

上下文压力是自动的——无需配置。它纯粹作为面向用户的通知触发，不会修改消息流或向模型的上下文中注入任何内容。

## 凭证池策略

当你为同一提供商拥有多个 API 密钥或 OAuth Token 时，可以配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀轮换密钥
  anthropic: least_used      # 总是选择使用最少的密钥
```

选项：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅[凭证池](/docs/user-guide/features/credential-pools)。

## 辅助模型

Hermes 使用"辅助"模型来处理图像分析、网页摘要、浏览器截图分析、会话标题生成和上下文压缩等辅助任务。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 将每个辅助任务路由到你的**主聊天模型**——即你在 `hermes model` 中选择的同一提供商/模型。你无需配置任何内容即可开始使用，但请注意，在昂贵的推理模型（Opus、MiniMax M2.7 等）上，辅助任务会增加显著成本。如果你希望无论主模型是什么，辅助任务都使用廉价且快速的模型，请显式设置 `auxiliary.<task>.provider` 和 `auxiliary.<task>.model`（例如，对于视觉和网页提取任务，使用 OpenRouter 上的 Gemini Flash）。

:::note 为什么 "auto" 使用你的主模型
早期版本将聚合器用户（OpenRouter、Nous Portal）分流到提供商端的廉价默认模型上。这令人困惑——付费订阅聚合器的用户会看到不同的模型处理他们的辅助流量。现在 `auto` 为所有用户使用主模型，而 `config.yaml` 中的每任务覆盖配置仍然优先（请参阅下面的[完整辅助配置参考](#full-auxiliary-config-reference)）。
:::

### 交互式配置辅助模型

无需手动编辑 YAML，运行 `hermes model` 并从菜单中选择 **"Configure auxiliary models"**。你将获得一个交互式的每任务选择器：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               当前: auto / 主模型
[ ] web_extract          当前: auto / 主模型
[ ] session_search       当前: openrouter / google/gemini-2.5-flash
[ ] title_generation     当前: openrouter / google/gemini-3-flash-preview
[ ] compression          当前: auto / 主模型
[ ] approval             当前: auto / 主模型
[ ] triage_specifier     当前: auto / 主模型
```

选择一个任务，选择一个提供商（OAuth 流程会打开浏览器；API 密钥提供商会提示输入），选择一个模型。更改将持久保存到 `config.yaml` 中的 `auxiliary.<task>.*`。与主模型选择器使用相同的机制——无需学习额外的语法。

### 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/NoF-YajElIM"
    title="Hermes Agent — 辅助模型教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

### 通用配置模式

Hermes 中的每个模型槽位——辅助任务、压缩、回退——都使用相同的三个旋钮：

| 键 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于身份验证和路由的提供商 | `"auto"` |
| `model` | 请求的模型 | 提供商的默认模型 |
| `base_url` | 自定义的 OpenAI 兼容端点（覆盖提供商） | 未设置 |
当设置了 `base_url` 时，Hermes 会忽略 provider 并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行身份验证）。当仅设置了 `provider` 时，Hermes 会使用该 provider 的内置身份验证和基础 URL。

辅助任务可用的 provider：`auto`、`main`，以及 [provider 注册表](/docs/reference/environment-variables) 中的任何 provider — `openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`ai-gateway`、`azure-foundry` — 或者你 `custom_providers` 列表中的任何命名自定义 provider（例如 `provider: "beans"`）。

:::tip MiniMax OAuth
`minimax-oauth` 通过浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **MiniMax (OAuth)** 进行身份验证。辅助任务会自动使用 `MiniMax-M2.7-highspeed`。请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::

:::warning `"main"` 仅用于辅助任务
`"main"` provider 选项意味着“使用我的主 Agent 使用的任何 provider”——它仅在 `auxiliary:`、`compression:` 和 `fallback_model:` 配置内部有效。它**不是**顶层 `model.provider` 设置的有效值。如果你使用自定义的 OpenAI 兼容端点，请在 `model:` 部分设置 `provider: custom`。所有主模型 provider 选项请参阅 [AI Providers](/docs/integrations/providers)。
:::

### 完整的辅助配置参考

```yaml
auxiliary:
  # 图像分析 (vision_analyze 工具 + 浏览器截图)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main" 等
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点 (覆盖 provider)
    api_key: ""                # base_url 的 API 密钥 (回退到 OPENAI_API_KEY)
    timeout: 120               # 秒 — LLM API 调用超时；视觉负载需要较长的超时时间
    download_timeout: 30       # 秒 — 图像 HTTP 下载超时；网络连接慢时请增加此值

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒 (6分钟) — 每次尝试的 LLM 摘要超时

  # 危险命令批准分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 上下文压缩超时 (与 compression.* 配置分开)
  compression:
    timeout: 120               # 秒 — 压缩功能会总结长对话，需要更多时间

  # 会话搜索 — 总结过去的会话匹配项
  session_search:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    max_concurrency: 3       # 限制并行摘要数量以减少请求突发导致的 429 错误
    extra_body: {}           # Provider 特定的 OpenAI 兼容请求字段

  # 技能中心 — 技能匹配和搜索
  skills_hub:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # MCP 工具调度
  mcp:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # 看板分类指定器 — `hermes kanban specify <id>` (或
  # 仪表板上 Triage 列卡片中的 ✨ Specify 按钮) 使用此
  # 槽位将一行描述扩展为具体规范，并将任务
  # 提升到 `todo` 状态。便宜快速的模型在这里效果很好；规范扩展
  # 很短，不需要推理深度。
  triage_specifier:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 120
```

:::tip
每个辅助任务都有一个可配置的 `timeout`（以秒为单位）。默认值：vision 120秒，web_extract 360秒，approval 30秒，compression 120秒。如果你为辅助任务使用慢速的本地模型，请增加这些值。Vision 还有一个单独的 `download_timeout`（默认 30秒）用于 HTTP 图像下载 — 对于慢速连接或自托管的图像服务器，请增加此值。
:::

:::info
上下文压缩有自己的 `compression:` 块用于设置阈值，以及一个 `auxiliary.compression:` 块用于模型/provider 设置 — 请参阅上文的 [Context Compression](#context-compression)。回退模型使用 `fallback_model:` 块 — 请参阅 [Fallback Model](/docs/integrations/providers#fallback-model)。这三者都遵循相同的 provider/model/base_url 模式。
:::

### 会话搜索调优

如果你为 `auxiliary.session_search` 使用推理密集型的模型，Hermes 现在为你提供了两个内置控制项：

- `auxiliary.session_search.max_concurrency`：限制 Hermes 一次总结多少个匹配的会话
- `auxiliary.session_search.extra_body`：在摘要调用中转发 provider 特定的 OpenAI 兼容请求字段

示例：

```yaml
auxiliary:
  session_search:
    provider: "main"
    model: "glm-4.5-air"
    timeout: 60
    max_concurrency: 2
    extra_body:
      enable_thinking: false
```

当你的 provider 对请求突发进行速率限制，并且你希望 `session_search` 牺牲一些并行性以换取稳定性时，请使用 `max_concurrency`。

仅当你的 provider 文档中记录了希望 Hermes 为该任务传递的 OpenAI 兼容请求体字段时，才使用 `extra_body`。Hermes 会原样转发该对象。

:::warning
`extra_body` 仅在你的 provider 实际支持你发送的字段时才有效。如果 provider 没有暴露原生的 OpenAI 兼容的推理关闭标志，Hermes 无法代表其合成一个。
:::

### 辅助任务的 OpenRouter 路由和 Pareto Code

当辅助任务解析到 OpenRouter（无论是显式设置还是通过 `provider: "main"` 而你的主 Agent 正在使用 OpenRouter 时），主 Agent 的 `provider_routing` 和 `openrouter.min_coding_score` 设置**不会传播**——根据设计，每个辅助任务都是独立的。要为特定的辅助任务设置 OpenRouter provider 偏好或使用 [Pareto Code 路由器](/docs/integrations/providers#openrouter-pareto-code-router)，请通过 `extra_body` 为每个任务单独设置：
```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openrouter/pareto-code         # 为此任务使用 Pareto Code 路由器
    extra_body:
      provider:                            # OpenRouter 提供商路由偏好
        order: [anthropic, google]         # 按顺序尝试这些提供商
        sort: throughput                   # 或 "price" | "latency"
        # only: [anthropic]                # 限制为特定提供商
        # ignore: [deepinfra]              # 排除特定提供商
      plugins:                             # OpenRouter Pareto Code 路由器旋钮
        - id: pareto-router
          min_coding_score: 0.5            # 0.0–1.0；越高 = 编码能力越强
```

此结构镜像了 OpenRouter 在聊天补全请求体中接受的内容。Hermes 会原样转发整个 `extra_body`，因此 [openrouter.ai/docs](https://openrouter.ai/docs) 上记录的任何其他 OpenRouter 请求体字段都以相同方式工作。

### 更改视觉模型

要使用 GPT-4o 而非 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`、`fallback_model:`），不适用于您的主 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 最佳可用（默认）。视觉任务尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter — 路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账户）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"minimax-oauth"` | 强制使用 MiniMax OAuth（浏览器登录，无需 API 密钥）。辅助任务使用 MiniMax-M2.7-highspeed。 | `hermes model` → MiniMax (OAuth) |
| `"main"` | 使用您活动的自定义/主端点。这可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY` 或通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容的 API。**仅限辅助任务 — 对 `model.provider` 无效。** | 自定义端点凭证 + 基础 URL |

当您希望辅助任务绕过默认路由器时，来自主提供商目录的直接 API 密钥提供商在此处也适用。配置 `GMI_API_KEY` 后，`gmi` 即有效：

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

对于 GMI 辅助路由，请使用 GMI 的 `/v1/models` 端点返回的确切模型 ID。

### 常见设置

**使用直接自定义端点**（比 `provider: "main"` 更清晰，适用于本地/自托管 API）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先于 `provider`，因此这是将辅助任务路由到特定端点的最明确方式。对于直接端点覆盖，Hermes 使用配置的 `api_key` 或回退到 `OPENAI_API_KEY`；它不会为该自定义端点重用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥进行视觉分析：**
```yaml
# 在 ~/.hermes/.env 中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或使用更便宜的 "gpt-4o-mini"
```

**使用 OpenRouter 进行视觉分析**（路由到任何模型）：
```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # 或 "google/gemini-2.5-flash" 等
```

**使用 Codex OAuth**（ChatGPT Pro/Plus 账户 — 无需 API 密钥）：
```yaml
auxiliary:
  vision:
    provider: "codex"     # 使用您的 ChatGPT OAuth Token
    # model 默认为 gpt-5.3-codex（支持视觉）
```

**使用 MiniMax OAuth**（浏览器登录，无需 API 密钥）：
```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```
运行 `hermes model` 并选择 **MiniMax (OAuth)** 以自动登录并设置此配置。对于中国区，基础 URL 将为 `https://api.minimaxi.com/anthropic`。完整步骤请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用您活动的自定义端点
    model: "my-local-model"
```

`provider: "main"` 使用 Hermes 用于正常聊天的任何提供商 — 无论是命名的自定义提供商（例如 `beans`）、内置提供商如 `openrouter`，还是遗留的 `OPENAI_BASE_URL` 端点。

:::tip
如果您使用 Codex OAuth 作为您的主模型提供商，视觉功能会自动工作 — 无需额外配置。Codex 已包含在视觉的自动检测链中。
:::

:::warning
**视觉功能需要多模态模型。** 如果您设置 `provider: "main"`，请确保您的端点支持多模态/视觉 — 否则图像分析将失败。
:::

### 环境变量（遗留方式）

辅助模型也可以通过环境变量配置。但是，`config.yaml` 是首选方法 — 它更易于管理，并且支持所有选项，包括 `base_url` 和 `api_key`。

| 设置 | 环境变量 |
|---------|---------------------|
| 视觉提供商 | `AUXILIARY_VISION_PROVIDER` |
| 视觉模型 | `AUXILIARY_VISION_MODEL` |
| 视觉端点 | `AUXILIARY_VISION_BASE_URL` |
| 视觉 API 密钥 | `AUXILIARY_VISION_API_KEY` |
| 网页提取提供商 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| 网页提取模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| 网页提取端点 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| 网页提取 API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |

压缩和回退模型设置仅支持 config.yaml。

:::tip
运行 `hermes config` 查看您当前的辅助模型设置。仅当覆盖项与默认值不同时才会显示。
:::

## 推理强度

控制模型在响应前进行多少“思考”：
```yaml
agent:
  reasoning_effort: ""   # 留空 = 中等（默认）。选项：none, minimal, low, medium, high, xhigh (max)
```

当未设置时（默认），推理力度默认为 "medium" —— 这是一个适用于大多数任务的平衡级别。设置一个值会覆盖它 —— 更高的推理力度会在复杂任务上提供更好的结果，但代价是消耗更多 Token 和增加延迟。

你也可以在运行时使用 `/reasoning` 命令更改推理力度：

```
/reasoning           # 显示当前力度级别和显示状态
/reasoning high      # 将推理力度设置为 high
/reasoning none      # 禁用推理
/reasoning show      # 在每个回复上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

## 工具使用强制

某些模型偶尔会将预期操作描述为文本，而不是进行工具调用（例如说"我会运行测试..."，而不是实际调用终端）。工具使用强制会注入系统提示词指导，引导模型回到实际调用工具的行为。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"` (默认) | 对匹配以下子串的模型启用：`gpt`, `codex`, `gemini`, `gemma`, `grok`。对所有其他模型（Claude, DeepSeek, Qwen 等）禁用。 |
| `true` | 无论模型如何，始终启用。如果你发现当前模型描述操作而不是执行操作，这很有用。 |
| `false` | 无论模型如何，始终禁用。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名称包含所列子串之一时启用（不区分大小写）。 |

### 注入的内容

启用后，可能会向系统提示词添加三层指导：

1.  **通用工具使用强制**（所有匹配的模型）—— 指示模型立即进行工具调用，而不是描述意图；持续工作直到任务完成；并且永远不要以承诺未来行动来结束一个回合。

2.  **OpenAI 执行纪律**（仅限 GPT 和 Codex 模型）—— 针对 GPT 特定失败模式的额外指导：放弃部分结果的工作、跳过先决条件查找、产生幻觉而不是使用工具、以及未经验证就声明"完成"。

3.  **Google 操作指导**（仅限 Gemini 和 Gemma 模型）—— 简洁性、绝对路径、并行工具调用以及编辑前验证模式。

这些对用户是透明的，只影响系统提示词。已经可靠使用工具的模型（如 Claude）不需要这种指导，这就是为什么 `"auto"` 排除了它们。

### 何时开启

如果你使用的模型不在默认的自动列表中，并且发现它经常描述它*将*做什么而不是实际去做，请设置 `tool_use_enforcement: true` 或将模型子串添加到列表中：

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts"
  speed: 1.0                    # 全局速度乘数（所有提供商的回退值）
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 速度乘数（转换为速率百分比，例如 1.5 → +50%）
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # 速度乘数（API 会限制在 0.25–4.0 范围内）
    base_url: "https://api.openai.com/v1"  # 用于覆盖 OpenAI 兼容的 TTS 端点
  minimax:
    speed: 1.0                  # 语音速度乘数
    # base_url: ""              # 可选：用于覆盖 OpenAI 兼容的 TTS 端点
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (默认)
  gemini:
    model: "gemini-2.5-flash-preview-tts"   # 或 gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 种预置语音：Zephyr, Puck, Kore, Enceladus 等。
  xai:
    voice_id: "eve"             # xAI TTS 语音
    language: "en"              # ISO 639-1
    sample_rate: 24000
    bit_rate: 128000            # MP3 比特率
    # base_url: "https://api.x.ai/v1"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

这同时控制着 `text_to_speech` 工具和语音模式下的语音回复（CLI 或消息网关中的 `/voice tts`）。

**速度回退层级：** 特定提供商的速度（例如 `tts.edge.speed`）→ 全局 `tts.speed` → `1.0` 默认值。设置全局 `tts.speed` 以在所有提供商间应用统一的速度，或者按提供商覆盖以进行细粒度控制。

## 显示设置

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  platforms: {}           # 按平台的显示覆盖（见下文）
  tool_progress_overrides: {}  # 已弃用 —— 请使用 display.platforms
  interim_assistant_messages: true  # 网关：将自然的回合中助手更新作为单独消息发送
  skin: default           # 内置或自定义 CLI 皮肤（见 user-guide/features/skins）
  personality: "kawaii"  # 遗留的装饰性字段，仍在某些摘要中显示
  compact: false          # 紧凑输出模式（更少的空白）
  resume_display: full    # full (恢复时显示之前的消息) | minimal (仅显示一行摘要)
  bell_on_complete: false # Agent 完成时播放终端铃声（适用于长时间任务）
  show_reasoning: false   # 在每个回复上方显示模型推理/思考过程（用 /reasoning show|hide 切换）
  streaming: false        # 将 Token 实时流式传输到终端（实时输出）
  show_cost: false        # 在 CLI 状态栏中显示估计的 $ 成本
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 无限制，显示完整路径/命令）
  runtime_footer:         # 网关：在最终回复后附加运行时上下文页脚
    enabled: false
    fields: ["model", "context_pct", "cwd"]
  language: en            # 静态消息的 UI 语言（批准提示、某些网关回复）。en | zh | ja | de | es | fr | tr | uk
```
### 静态消息的界面语言

`display.language` 设置用于翻译一小部分面向用户的静态消息——CLI 批准提示、少数消息网关斜杠命令回复（例如重启-排空通知、“批准已过期”、“目标已清除”）。它**不会**翻译 Agent 的回复、日志行、工具输出、错误回溯或斜杠命令描述——这些内容仍保持英文。如果你希望 Agent 本身用另一种语言回复，只需在你的提示词或系统消息中告诉它。

支持的值：`en`（默认）、`zh`（简体中文）、`ja`（日语）、`de`（德语）、`es`（西班牙语）、`fr`（法语）、`tr`（土耳其语）、`uk`（乌克兰语）。未知值将回退到英文。

你也可以通过 `HERMES_LANGUAGE` 环境变量按会话设置此选项，该变量会覆盖配置值。

```yaml
display:
  language: zh   # CLI 批准提示以中文显示
```

| 模式 | 你看到的内容 |
|------|-------------|
| `off` | 静默——仅显示最终响应 |
| `new` | 仅在工具变更时显示工具指示器 |
| `all` | 每次工具调用都显示简短预览（默认） |
| `verbose` | 完整的参数、结果和调试日志 |

在 CLI 中，使用 `/verbose` 在这些模式间循环切换。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上面的 `display` 部分设置 `tool_progress_command: true`。该命令将循环切换模式并保存到配置中。

### 运行时元数据页脚（仅限消息网关）

当 `display.runtime_footer.enabled: true` 时，Hermes 会在每个消息网关回合的**最终**消息后附加一个小的运行时上下文页脚——与 CLI 在状态栏中显示的信息相同（模型、上下文百分比、当前工作目录、会话持续时间、Token 数、成本）。默认关闭；如果你的团队希望每个回复都包含来源信息，可以按消息网关选择启用。

```yaml
display:
  runtime_footer:
    enabled: true
    fields: ["model", "context_pct", "cwd"]   # 可选：model, context_pct, cwd, duration, tokens, cost
```

`/footer` 斜杠命令可在任何会话的运行时切换此功能。

附加到 Telegram/Discord/Slack 回复的页脚示例：

```
— claude-opus-4.7 · 12 次工具调用 · 2分 14秒 · $0.042
```

只有回合的**最终**消息会获得页脚；中间更新保持简洁。

### 按平台的进度覆盖设置

不同平台对详细程度的需求不同。例如，Signal 无法编辑消息，因此每个进度更新都会成为一条独立的消息——很嘈杂。使用 `display.platforms` 来设置按平台的模式：

```yaml
display:
  tool_progress: all          # 全局默认
  platforms:
    signal:
      tool_progress: 'off'    # 在 Signal 上静默进度
    telegram:
      tool_progress: verbose  # 在 Telegram 上显示详细进度
    slack:
      tool_progress: 'off'    # 在共享的 Slack 工作区中保持安静
```

没有覆盖设置的平台将回退到全局的 `tool_progress` 值。有效的平台键：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`。为了向后兼容，旧的 `display.tool_progress_overrides` 键仍然会被加载，但已弃用，并在首次加载时迁移到 `display.platforms` 中。

`interim_assistant_messages` 仅适用于消息网关。启用后，Hermes 会将回合中已完成的中间助手更新作为单独的聊天消息发送。这独立于 `tool_progress`，并且不需要消息网关流式传输。

## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离 PII（仅限消息网关）
```

当 `redact_pii` 为 `true` 时，消息网关会在将系统提示词发送给 LLM 之前，从支持的平台中删除个人可识别信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希化为 `user_<12-char-sha256>` |
| 用户 ID | 哈希化为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分被哈希化，平台前缀保留（`telegram:<hash>`） |
| 主频道 ID | 数字部分被哈希化 |
| 用户姓名 / 用户名 | **不受影响**（用户选择，公开可见） |

**平台支持：** 去标识化适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除在外，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实的 ID。

哈希是确定性的——同一用户始终映射到相同的哈希值，因此模型仍然可以区分群聊中的不同用户。路由和传递在内部使用原始值。

## 语音转文本（STT）

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧的回退键仍被支持
```

提供商行为：

- `local` 使用在你机器上运行的 `faster-whisper`。请单独使用 `pip install faster-whisper` 安装它。
- `groq` 使用 Groq 的 Whisper 兼容端点并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API 并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会按以下顺序自动回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖由环境驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式（CLI）

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内的按键通话键
  max_recording_seconds: 120    # 长时间录音的硬性停止限制
  auto_tts: false               # 当 /voice on 时自动启用语音回复
  beep_enabled: true            # 在 CLI 语音模式中播放录音开始/结束提示音
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静默秒数
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。有关端到端设置和平台特定行为，请参阅[语音模式](/docs/user-guide/features/voice-mode)。
## 流式传输

将 Token 实时传输到终端或消息平台，而不是等待完整响应。

### CLI 流式传输

```yaml
display:
  streaming: true         # 将 Token 实时流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考 Token（可选）
```

启用后，响应将在流式传输框内逐个 Token 显示。工具调用仍会被静默捕获。如果提供商不支持流式传输，它会自动回退到正常显示。

### 消息网关流式传输（Telegram、Discord、Slack）

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  transport: edit         # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3      # 消息编辑之间的间隔秒数
  buffer_threshold: 40    # 强制刷新编辑前的字符数阈值
  cursor: " ▉"            # 流式传输期间显示的光标
  fresh_final_after_seconds: 60   # 当预览消息达到此秒数时发送全新的最终消息（Telegram）；0 = 始终原地编辑
```

启用后，机器人会在收到第一个 Token 时发送一条消息，然后随着更多 Token 的到来逐步编辑它。不支持消息编辑的平台（Signal、Email、Home Assistant）会在首次尝试时自动检测到——流式传输会优雅地在该会话中禁用，不会导致消息泛滥。

对于无需渐进式 Token 编辑的、独立的自然中途助手更新，请设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式传输的文本超过平台的消息长度限制（约 4096 个字符），当前消息将被最终确定，并自动开始一条新消息。

**全新最终消息（Telegram）：** Telegram 的 `editMessageText` 会保留原始消息的时间戳，因此一个长时间运行的流式回复即使在完成后也会保留第一个 Token 的时间戳。当 `fresh_final_after_seconds > 0`（默认为 `60`）时，完成的回复将作为一条全新的消息发送（并尽力删除过时的预览消息），以便 Telegram 显示的时间戳反映完成时间。简短的预览消息仍会原地最终确定。设置为 `0` 则始终原地编辑。

:::note
流式传输默认禁用。在 `~/.hermes/config.yaml` 中启用它以体验流式传输的用户体验。
:::

## 群聊会话隔离

控制共享聊天是每个房间保持一个对话，还是每个参与者保持一个对话：

```yaml
group_sessions_per_user: true  # true = 在群组/频道中按用户隔离，false = 每个聊天一个共享会话
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道和类似的共享上下文中，当平台提供用户 ID 时，每个发送者都会获得自己的会话。
- `false` 会恢复为旧的共享房间行为。如果你明确希望 Hermes 将频道视为一个协作对话，这可能很有用，但这也意味着用户共享上下文、Token 成本和中断状态。
- 私信不受影响。Hermes 仍会像往常一样按聊天/私信 ID 来区分私信。
- 无论哪种方式，线程都与其父频道保持隔离；当设置为 `true` 时，每个参与者在线程内也拥有自己的会话。

有关行为细节和示例，请参阅[会话](/docs/user-guide/sessions)和 [Discord 指南](/docs/user-guide/messaging/discord)。

## 未授权私信行为

控制当未知用户发送私信时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 拒绝访问，但会在私信中回复一个一次性配对码。
- `ignore` 会静默丢弃未授权的私信。
- 平台配置节会覆盖全局默认值，因此你可以在广泛启用配对的同时，让某个平台保持安静。

## 快捷命令

定义自定义命令，这些命令要么运行 shell 命令而不调用 LLM，要么将一个斜杠命令别名到另一个。`exec` 类型的快捷命令是零 Token 的，在消息平台（Telegram、Discord 等）上用于快速服务器检查或实用脚本非常有用。

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  disk:
    type: exec
    command: df -h /
  update:
    type: exec
    command: cd ~/.hermes/hermes-agent && git pull && pip install -e .
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update`、`/gpu` 或 `/restart`。`exec` 命令在主机上本地运行并直接返回输出——无需 LLM 调用，不消耗 Token。`alias` 命令会重写为配置的斜杠命令目标。

- **30 秒超时** — 长时间运行的命令会被终止并显示错误消息
- **优先级** — 快捷命令在技能命令之前检查，因此你可以覆盖技能名称
- **自动补全** — 快捷命令在调度时解析，不会显示在内置的斜杠命令自动补全表中
- **类型** — 支持的类型是 `exec` 和 `alias`；其他类型会显示错误
- **随处可用** — CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

纯字符串的提示词快捷方式不是有效的快捷命令。对于可重用的提示词工作流，请创建一个技能或别名到现有的斜杠命令。

## 人为延迟

在消息平台中模拟类人的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # 最小延迟（自定义模式）
  max_ms: 2500                 # 最大延迟（自定义模式）
```

## 代码执行

配置 `execute_code` 工具：

```yaml
code_execution:
  mode: project                # project（默认）| strict
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行内的最大工具调用次数
```

**`mode`** 控制脚本的工作目录和 Python 解释器：

- **`project`**（默认）— 脚本在会话的工作目录中运行，使用活动的 virtualenv/conda 环境的 python。项目依赖（`pandas`、`torch`、项目包）和相对路径（`.env`、`./data.csv`）会自然解析，与 `terminal()` 看到的内容匹配。
- **`strict`** — 脚本在临时暂存目录中运行，使用 `sys.executable`（Hermes 自身的 python）。最大程度的可复现性，但项目依赖和相对路径将无法解析。
环境清理（清除 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH`）和工具白名单在两种模式下同样适用——切换模式不会改变安全态势。

## 网络搜索后端

`web_search`、`web_extract` 和 `web_crawl` 工具支持五个后端提供商。在 `config.yaml` 中或通过 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | parallel | tavily | exa

  # 或者使用按能力划分的键来混合提供商（例如，免费搜索 + 付费提取）：
  search_backend: "searxng"
  extract_backend: "firecrawl"
```

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

**后端选择：** 如果未设置 `web.backend`，则根据可用的 API 密钥自动检测后端。如果只设置了 `SEARXNG_URL`，则使用 SearXNG。如果只设置了 `EXA_API_KEY`，则使用 Exa。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则 Firecrawl 是默认值。

**SearXNG** 是一个免费、自托管、尊重隐私的元搜索引擎，可查询 70 多个搜索引擎。无需 API 密钥——只需将 `SEARXNG_URL` 设置为你的实例（例如，`http://localhost:8080`）。SearXNG 仅支持搜索；`web_extract` 和 `web_crawl` 需要单独的提取提供商（设置 `web.extract_backend`）。有关 Docker 设置说明，请参阅[网络搜索设置指南](/docs/user-guide/features/web-search)。

**自托管 Firecrawl：** 将 `FIRECRAWL_API_URL` 设置为你自己的实例。设置自定义 URL 后，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=***` 以禁用身份验证）。

**Parallel 搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 以控制搜索行为——`fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

**Exa：** 在 `~/.hermes/.env` 中设置 `EXA_API_KEY`。支持 `category` 过滤（`company`、`research paper`、`news`、`people`、`personal site`、`pdf`）以及域名/日期过滤器。

## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 自动关闭空闲会话前的秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时时间（秒）
  record_sessions: false         # 自动将浏览器会话录制为 WebM 视频到 ~/.hermes/browser_recordings/
  # 可选的 CDP 覆盖——设置后，Hermes 直接附加到你自己的 Chrome（通过 /browser connect），而不是启动无头浏览器。
  cdp_url: ""
  # 对话框监督器——控制当附加 CDP 后端（Browserbase、通过 /browser connect 的本地 Chrome）时如何处理原生 JS 对话框（alert / confirm / prompt）。在 Camofox 和默认的本地 agent-browser 模式下忽略。
  dialog_policy: must_respond    # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300          # must_respond 策略下的安全自动关闭时间（秒）
  camofox:
    managed_persistence: false   # 为 true 时，Camofox 会话在重启后保持 cookie/登录状态
```

**对话框策略：**

- `must_respond` (默认) —— 捕获对话框，在 `browser_snapshot.pending_dialogs` 中显示，并等待 Agent 调用 `browser_dialog(action=...)`。在 `dialog_timeout_s` 秒内无响应后，对话框将自动关闭，以防止页面的 JS 线程永久阻塞。
- `auto_dismiss` —— 捕获后立即关闭。Agent 仍会在事后看到 `browser_snapshot.recent_dialogs` 中的对话框记录，其 `closed_by="auto_policy"`。
- `auto_accept` —— 捕获后立即接受。对于具有激进 `beforeunload` 提示的页面很有用。

有关完整的对话框工作流，请参阅[浏览器功能页面](./features/browser.md#browser_dialog)。

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chrome CDP 设置的详细信息，请参阅[浏览器功能页面](/docs/user-guide/features/browser)。

## 时区

使用 IANA 时区字符串覆盖服务器本地时区。影响日志中的时间戳、定时任务调度和系统提示词时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区 (默认: "" = 服务器本地时间)
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

## Discord

为消息网关配置 Discord 特定行为：

```yaml
discord:
  require_mention: true          # 在服务器频道中需要 @提及 才能响应
  free_response_channels: ""     # 逗号分隔的频道 ID 列表，在这些频道中机器人无需 @提及 即可响应每条消息
  auto_thread: true              # 在频道中 @提及 时自动创建线程
```

- `require_mention` —— 当为 `true`（默认）时，机器人仅在服务器频道中被 `@BotName` 提及时才响应。私信始终无需提及即可工作。
- `free_response_channels` —— 逗号分隔的频道 ID 列表，在这些频道中机器人无需提及即可响应每条消息。
- `auto_thread` —— 当为 `true`（默认）时，在频道中的提及会自动为对话创建一个线程，保持频道整洁（类似于 Slack 的线程功能）。

## 安全

执行前安全扫描和密钥脱敏：

```yaml
security:
  redact_secrets: false          # 在工具输出和日志中脱敏 API 密钥模式（默认关闭）
  tirith_enabled: true           # 为终端命令启用 Tirith 安全扫描
  tirith_path: "tirith"          # tirith 二进制文件路径（默认：$PATH 中的 "tirith"）
  tirith_timeout: 5              # 等待 tirith 扫描的超时时间（秒）
  tirith_fail_open: true         # 如果 tirith 不可用，允许命令执行
  website_blocklist:             # 请参阅下面的网站阻止列表部分
    enabled: false
    domains: []
    shared_files: []
```
- `redact_secrets` — 当设为 `true` 时，会在工具输出进入会话上下文和日志之前，自动检测并屏蔽看起来像 API 密钥、Token 和密码的模式。**默认关闭** — 如果你经常在工具输出中处理真实凭据并希望有一个安全网，请启用。显式设置为 `true` 以开启。
- `tirith_enabled` — 当设为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/StackGuardian/tirith) 扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 tirith 扫描的最大秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当设为 `true`（默认）时，如果 tirith 不可用或失败，则允许执行命令。设置为 `false` 以在 tirith 无法验证命令时阻止执行。

## 网站阻止列表

阻止 Agent 的网页和浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # 启用 URL 阻止（默认：false）
    domains:                     # 被阻止的域名模式列表
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # 从外部文件加载额外的规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被阻止域名模式的 URL 都会在网页或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- TLD 通配符：`*.local`

共享文件每行包含一个域名规则（空行和以 `#` 开头的注释行会被忽略）。缺失或无法读取的文件会记录警告，但不会禁用其他网页工具。

策略会缓存 30 秒，因此配置更改无需重启即可快速生效。

## 智能审批

控制 Hermes 如何处理潜在危险的命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|----------|
| `manual`（默认） | 在执行任何被标记的命令之前提示用户。在 CLI 中，显示交互式审批对话框。在消息传递中，将待处理的审批请求加入队列。 |
| `smart` | 使用辅助 LLM 来评估被标记的命令是否真的危险。低风险命令会自动批准，并具有会话级别的持久性。真正有风险的命令会升级给用户处理。 |
| `off` | 跳过所有审批检查。等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式对于减少审批疲劳特别有用 — 它允许 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用终端命令的所有安全检查。仅在受信任的沙盒环境中使用此设置。
:::

## 检查点

在破坏性文件操作之前自动创建文件系统快照。详情请参阅[检查点与回滚](/docs/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: false                 # 启用自动检查点（也可通过：hermes chat --checkpoints）。默认：false（需手动启用）。
  max_snapshots: 20              # 每个目录保留的最大检查点数（默认：20）
```

## 委派

为委派工具配置子 Agent 行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型（空 = 继承父级）
  # provider: "openrouter"                  # 覆盖提供商（空 = 继承父级）
  # base_url: "http://localhost:1234/v1"    # 直接的 OpenAI 兼容端点（优先级高于 provider）
  # api_key: "local-key"                    # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
  max_concurrent_children: 3                # 每批次并行运行的子 Agent 数（下限 1，无上限）。也可通过 DELEGATION_MAX_CONCURRENT_CHILDREN 环境变量设置。
  max_spawn_depth: 1                        # 委派树深度上限（1-3，会被限制）。1 = 扁平（默认）：父级生成不能委派的叶子节点。2 = 编排器子级可以生成叶子孙级。3 = 三级。
  orchestrator_enabled: true                # 全局开关。当为 false 时，忽略 role="orchestrator"，无论 max_spawn_depth 如何，每个子级都被强制设为叶子节点。
```

**子 Agent 提供商:模型覆盖：** 默认情况下，子 Agent 继承父级 Agent 的提供商和模型。设置 `delegation.provider` 和 `delegation.model` 可以将子 Agent 路由到不同的提供商:模型组合 — 例如，使用廉价/快速的模型处理范围狭窄的子任务，而你的主 Agent 运行昂贵的推理模型。

**直接端点覆盖：** 如果你想要明显的自定义端点路径，请设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这将直接把子 Agent 发送到该 OpenAI 兼容端点，并且优先级高于 `delegation.provider`。如果省略 `delegation.api_key`，Hermes 仅回退到 `OPENAI_API_KEY`。

委派提供商使用与 CLI/消息网关启动时相同的凭据解析机制。支持所有已配置的提供商：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。设置提供商后，系统会自动解析正确的基础 URL、API 密钥和 API 模式 — 无需手动配置凭据。

**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父级提供商（继承）。配置中的 `delegation.model` → 父级模型（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（适用于在同一提供商内切换模型，例如 OpenRouter）。

**宽度和深度：** `max_concurrent_children` 限制每批次并行运行的子 Agent 数量（默认 `3`，下限 1，无上限）。也可以通过 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量设置。当模型提交的 `tasks` 数组长度超过此限制时，`delegate_task` 会返回一个工具错误来解释该限制，而不是静默截断。`max_spawn_depth` 控制委派树的深度（限制在 1-3）。在默认值 `1` 时，委派是扁平的：子级不能生成孙级，并且传递 `role="orchestrator"` 会静默降级为 `leaf`。提高到 `2` 以便编排器子级可以生成叶子孙级；`3` 用于三级树。Agent 通过 `role="orchestrator"` 在每次调用时选择加入编排；`orchestrator_enabled: false` 会强制每个子级变回叶子节点，无论其他设置如何。成本呈乘法级增长 — 在 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 的情况下，树最多可以达到 3×3×3 = 27 个并发的叶子 Agent。有关使用模式，请参阅[子 Agent 委派 → 深度限制和嵌套编排](features/delegation.md#depth-limit-and-nested-orchestration)。
## Clarify

配置澄清提示行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清响应的秒数
```

## 上下文文件 (SOUL.md, AGENTS.md)

Hermes 使用两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|---------|-------|
| `SOUL.md` | **主要 Agent 身份** — 定义 Agent 是谁（系统提示词中的插槽 #1） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上遍历至 git 根目录 |
| `AGENTS.md` | 项目特定指令，编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则文件（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |

- **SOUL.md** 是 Agent 的主要身份。它占据系统提示词中的插槽 #1，完全替换内置的默认身份。编辑它以完全自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 将回退到内置的默认身份。
- **项目上下文文件使用优先级系统** — 只加载一种类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 是分层的：如果子目录也有 AGENTS.md，则所有文件都会被合并。
- 如果 `SOUL.md` 不存在，Hermes 会自动创建一个默认的 `SOUL.md`。
- 所有加载的上下文文件都限制在 20,000 个字符以内，并采用智能截断。

另请参阅：
- [人格 & SOUL.md](/docs/user-guide/features/personality)
- [上下文文件](/docs/user-guide/features/context-files)

## 工作目录

| 上下文 | 默认值 |
|---------|---------|
| **CLI (`hermes`)** | 运行命令的当前目录 |
| **消息网关** | 主目录 `~`（可通过 `MESSAGING_CWD` 覆盖） |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户主目录 |

覆盖工作目录：
```bash
# 在 ~/.hermes/.env 或 ~/.hermes/config.yaml 中：
MESSAGING_CWD=/home/myuser/projects    # 网关会话
TERMINAL_CWD=/workspace                # 所有终端会话
```