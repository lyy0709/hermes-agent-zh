---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

# 配置

所有设置都存储在 `~/.hermes/` 目录中，便于访问。

:::tip 获取可用 `config.yaml` 的最简单途径
运行 `hermes setup --portal` — 一次 OAuth 即可获得模型提供商和所有四个工具网关工具，无需手动编辑 YAML。Portal 订阅者还可享受按 Token 计费提供商 10% 的折扣。请参阅 [Nous Portal](/integrations/nous-portal)。
:::

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

1.  **CLI 参数** — 例如：`hermes chat --model anthropic/claude-sonnet-4`（每次调用覆盖）
2.  **`~/.hermes/config.yaml`** — 所有非密钥设置的主要配置文件
3.  **`~/.hermes/.env`** — 环境变量的后备；**必需**用于密钥（API 密钥、Token、密码）
4.  **内置默认值** — 当没有设置其他值时，使用硬编码的安全默认值

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

单个值中的多个引用有效：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将按字面保留（`${UNDEFINED_VAR}` 保持原样）。仅支持 `${VAR}` 语法 — 裸 `$VAR` 不会被扩展。

有关 AI 提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、后备模型等），请参阅 [AI 提供商](/integrations/providers)。

### 提供商超时设置

您可以设置 `providers.<id>.request_timeout_seconds` 来配置提供商范围的请求超时，还可以设置 `providers.<id>.models.<model>.timeout_seconds` 来配置模型特定的覆盖。这适用于每个传输上的主要轮次客户端（OpenAI-wire、原生 Anthropic、Anthropic 兼容）、后备链、凭据轮换后的重建，以及（对于 OpenAI-wire）每个请求的超时关键字参数 — 因此配置的值优先于旧的 `HERMES_API_TIMEOUT` 环境变量。

您还可以设置 `providers.<id>.stale_timeout_seconds` 来配置非流式陈旧调用检测器，以及 `providers.<id>.models.<model>.stale_timeout_seconds` 来配置模型特定的覆盖。这优先于旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

不设置这些值将保留旧的默认值（`HERMES_API_TIMEOUT=1800` 秒，`HERMES_API_CALL_STALE_TIMEOUT=300` 秒，原生 Anthropic 900 秒）。目前未为 AWS Bedrock 配置（`bedrock_converse` 和 AnthropicBedrock SDK 路径都使用 boto3，其自身有超时配置）。请参阅 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 中的注释示例。

## 终端后端配置

Hermes 支持六种终端后端。每种都决定了 Agent 的 shell 命令实际执行的位置 — 您的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙盒（直接或通过 Nous 管理的网关）、Daytona 工作空间，或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | singularity
  cwd: "."          # 消息网关/定时任务的工作目录（CLI 始终使用启动目录）
  timeout: 180      # 每个命令的超时时间（秒）
  env_passthrough: []  # 要转发到沙盒化执行的环境变量名称（终端 + execute_code）
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于 Modal 和 Daytona 等云沙盒，`container_persistent: true` 意味着 Hermes 将尝试在沙盒重建过程中保留文件系统状态。它不保证同一个活动沙盒、PID 空间或后台进程稍后仍在运行。

### 后端概述

| 后端 | 命令运行位置 | 隔离性 | 最适合 |
|---------|-------------------|-----------|----------|
| **local** | 直接在您的机器上 | 无 | 开发、个人使用 |
| **docker** | 单个持久化 Docker 容器（在会话、`/new`、子 Agent 之间共享） | 完全（命名空间、cap-drop） | 安全沙盒化、CI/CD |
| **ssh** | 通过 SSH 连接的远程服务器 | 网络边界 | 远程开发、强大硬件 |
| **modal** | Modal 云沙盒 | 完全（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作空间 | 完全（云容器） | 托管的云开发环境 |
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

**单个持久化容器，在多个 Hermes 进程间共享。** Hermes 在首次使用时启动一个长期运行的容器，并通过 `docker exec` 将每个终端、文件和 `execute_code` 调用路由到同一个容器中——跨会话、`/new`、`/reset` 和 `delegate_task` 子 Agent 都是如此。工作目录更改、已安装的包、`/workspace` 中的文件以及**后台进程**都会从一个工具调用延续到下一个，从一个 Hermes 进程延续到下一个。当您关闭 TUI 会话、运行 `/quit` 或启动新的 `hermes` 调用时，容器会继续运行，下一个 Hermes 进程通过标签查找来复用该容器。确切的销毁规则请参见下面的**容器生命周期**。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 将启动目录挂载到 /workspace
  docker_run_as_host_user: false   # 参见下面的“以主机用户身份运行容器”
  docker_forward_env:              # 要转发到容器内的主机环境变量
    - "GITHUB_TOKEN"
  docker_env:                      # 要注入的字面量环境变量 (KEY=value)
    DEBUG: "1"
    PYTHONUNBUFFERED: "1"
  docker_volumes:                  # 主机目录挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro 表示只读
  docker_extra_args:               # 原样附加到 `docker run` 的额外标志
    - "--gpus=all"
    - "--network=host"

  # 资源限制
  container_cpu: 1                 # CPU 核心数 (0 = 无限制)
  container_memory: 5120           # MB (0 = 无限制)
  container_disk: 51200            # MB (需要在 XFS+pquota 上使用 overlay2)
  container_persistent: true       # 持久化 /workspace 和 /root 绑定挂载目录

  # 跨进程容器复用（默认值符合“跨会话共享一个长期运行容器”的约定——参见容器生命周期）。
  docker_persist_across_processes: true   # 在 Hermes 重启时复用容器
  docker_orphan_reaper: true              # 在启动时清理被遗弃的 Exited 容器

  # 跨后端生命周期设置（也适用于 docker）
  timeout: 180                     # 每个命令的超时时间（秒）
  lifetime_seconds: 300            # 空闲清理窗口；也作为 2 倍孤儿清理器的阈值
```

**`docker_env`** 与 **`docker_forward_env`**：前者注入您在配置中指定的字面量 `KEY=value` 对（值存储在您的 `config.yaml` 中，或通过 `TERMINAL_DOCKER_ENV='{"DEBUG":"1"}'` 作为 JSON 字典传递）。后者从您的 shell 或 `~/.hermes/.env` 转发值，因此实际的密钥永远不会出现在配置文件中。对 Token 使用 `docker_forward_env`，对容器需要的静态开关使用 `docker_env`。

**`terminal.docker_extra_args`**（也可以通过 `TERMINAL_DOCKER_EXTRA_ARGS='["--gpus=all"]'` 覆盖）允许您传递 Hermes 未作为一等键公开的任意 `docker run` 标志——`--gpus`、`--network`、`--add-host`、替代的 `--security-opt` 覆盖等。每个条目必须是字符串；该列表最后附加到组装好的 `docker run` 调用中，以便在需要时可以覆盖 Hermes 的默认值。请谨慎使用——与沙盒加固（能力丢弃、`--user`、工作区绑定挂载）冲突的标志会静默地削弱隔离性。

**要求：** Docker Desktop 或 Docker Engine 已安装并正在运行。Hermes 会探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用程序包）。Podman 开箱即用：当两者都安装时，设置 `HERMES_DOCKER_BINARY=podman`（或完整路径）来强制使用它。

#### 容器生命周期

每个由 Hermes 管理的容器都标有三个标签，以便后续进程（以及孤儿清理器）能够识别它：

- `hermes-agent=1` — 标记为 Hermes 管理
- `hermes-task-id=<经过清理的 task_id>` — 用于按任务复用的探测键
- `hermes-profile=<经过清理的配置文件名称>` — 将复用和清理范围限定到活动的 Hermes 配置文件

启动时，Hermes 运行 `docker ps --filter label=hermes-task-id=<id> --filter label=hermes-profile=<profile>`，并在找到现有容器时**附加到该容器**。如果容器处于 `exited` 状态（例如，在 Docker 守护进程重启后），则会 `docker start` 并复用——文件系统状态和任何已安装的包会保留，但容器内的后台进程不会保留。

当 Hermes 进程退出时——无论是 `/quit`、关闭 TUI 会话、消息网关关闭，甚至是 SIGKILL——在默认模式下，容器的清理路径是**无操作的**。容器继续运行。下一个 Hermes 进程通过标签探测在几毫秒内附加到它。这是“跨会话共享一个长期运行容器”约定所需的行为：这是确保后台进程（npm 监视器、开发服务器、长时间运行的 pytest）在会话间存活的唯一方式。

**容器仅在以下情况下被销毁（停止并 `docker rm -f`）：**

| 触发条件 | 触发时机 |
|---|---|
| `docker_persist_across_processes: false` | 显式的每进程隔离。每次 `cleanup()` 都会执行 `stop` + `rm -f`。符合 issue-#20561 之前的行为。 |
| 空闲清理器 (`lifetime_seconds`, 默认 300s) | 仅当环境设置为 `persist_across_processes=false` 时。持久化模式的环境无操作；容器在空闲清理中存活。 |
| 下次启动时的孤儿清理器 | 清理早于 `2 × lifetime_seconds`（默认 600s = 10 分钟）的、标记为 hermes 的 **Exited** 容器，范围限定在当前配置文件。**Running 状态的容器永远不会被触及**——确保兄弟进程安全。设置 `docker_orphan_reaper: false` 来禁用。 |
| 用户直接操作 | `docker rm -f`、`docker system prune`、Docker Desktop 重启。我们不设置 `--restart=always`，因此主机重启会使容器处于 `Exited` 状态（其 CoW 层会保留并在下次启动时被复用，但后台进程会丢失）。 |
值得了解的边缘情况：

- **容器内 PID 1 进程因 OOM 被终止** 会导致容器状态变为 `Exited`。下次重用时会 `docker start` 它；文件系统状态会保留，但后台进程不会。
- **切换配置文件** 会使容器彼此隔离 —— 标记为 `hermes-profile=work` 的容器对于在 `hermes-profile=research` 下运行的 Hermes 进程是不可见的。孤儿容器回收器也是按配置文件作用域划分的，因此跨配置文件的容器不会被意外回收，但它们也不会自动清理，直到你在其原始配置文件下再次启动 Hermes。

通过 `delegate_task(tasks=[...])` 生成的并行子 Agent 共享同一个容器 —— 并发的 `cd`、环境变量修改以及写入同一路径会发生冲突。如果子 Agent 需要一个隔离的沙盒，它必须通过 `register_task_env_overrides()` 注册每个任务的镜像覆盖，RL 和基准环境（TerminalBench2、HermesSweEnv 等）会为其每个任务的 Docker 镜像自动执行此操作。

**安全加固：**
- `--cap-drop ALL`，仅重新添加 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 为 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）设置大小限制的 tmpfs

**凭证转发：** 列在 `docker_forward_env` 中的环境变量首先从你的 shell 环境解析，然后从 `~/.hermes/.env` 解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

#### 环境变量覆盖

`terminal:` 下的每个键都有一个形式为 `TERMINAL_<KEY_UPPERCASE>` 的环境变量覆盖。对于 Docker 后端最有用的几个：

| 环境变量 | 映射到 | 备注 |
|---|---|---|
| `TERMINAL_DOCKER_IMAGE` | `docker_image` | 基础镜像 |
| `TERMINAL_DOCKER_FORWARD_ENV` | `docker_forward_env` | JSON 数组：`'["GITHUB_TOKEN","OPENAI_API_KEY"]'` |
| `TERMINAL_DOCKER_ENV` | `docker_env` | JSON 字典：`'{"DEBUG":"1"}'` |
| `TERMINAL_DOCKER_VOLUMES` | `docker_volumes` | `"host:container[:ro]"` 字符串的 JSON 数组 |
| `TERMINAL_DOCKER_EXTRA_ARGS` | `docker_extra_args` | JSON 数组 |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | `docker_mount_cwd_to_workspace` | `true` / `false` |
| `TERMINAL_DOCKER_RUN_AS_HOST_USER` | `docker_run_as_host_user` | `true` / `false` |
| `TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES` | `docker_persist_across_processes` | `true` / `false` — 默认 `true` |
| `TERMINAL_DOCKER_ORPHAN_REAPER` | `docker_orphan_reaper` | `true` / `false` — 默认 `true` |
| `TERMINAL_CONTAINER_CPU` | `container_cpu` | CPU 核心数 |
| `TERMINAL_CONTAINER_MEMORY` | `container_memory` | MB |
| `TERMINAL_CONTAINER_DISK` | `container_disk` | MB |
| `TERMINAL_CONTAINER_PERSISTENT` | `container_persistent` | `true` / `false` — 控制绑定挂载的工作区目录，与 `docker_persist_across_processes` 不同 |
| `TERMINAL_LIFETIME_SECONDS` | `lifetime_seconds` | 空闲回收器窗口 |
| `TERMINAL_TIMEOUT` | `timeout` | 每条命令的超时时间 |
| `HERMES_DOCKER_BINARY` | _无_ | 强制指定 docker/podman 二进制文件路径 |

### SSH 后端

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 进行连接复用（5 分钟空闲保活）。默认启用持久化 shell —— 状态（当前工作目录、环境变量）在命令之间保留。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持一个长期存在的 bash 会话（默认：true）
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
| `TERMINAL_SSH_KEY` | （系统默认） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 shell |

**工作原理：** 在初始化时使用 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 进行连接。持久化 shell 在远程主机上保持一个 `bash -l` 进程存活，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到一次性模式。

### Modal 后端

在 [Modal](https://modal.com) 云沙盒中运行命令。每个任务获得一个具有可配置 CPU、内存和磁盘的隔离 VM。文件系统可以在会话之间快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB（5GB）
  container_disk: 51200            # MB（50GB）
  container_persistent: true       # 快照/恢复文件系统
```

**必需：** 环境变量 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`，或 `~/.modal.toml` 配置文件。

**持久化：** 启用后，沙盒文件系统在清理时被快照，并在下次会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这保留了文件系统状态，而不是活动进程、PID 空间或后台作业。

**凭证文件：** 自动从 `~/.hermes/` 挂载（OAuth 令牌等），并在每条命令前同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 托管的工作区中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB（最大 10 GiB）
  container_persistent: true       # 停止/恢复而不是删除
```

**必需：** 环境变量 `DAYTONA_API_KEY`。

**持久化：** 启用后，沙盒在清理时被停止（而非删除），并在下次会话时恢复。沙盒名称遵循模式 `hermes-{task_id}`。

**磁盘限制：** Daytona 强制执行 10 GiB 的最大限制。超过此限制的请求会被警告并限制。

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
**要求：** `$PATH` 中需有 `apptainer` 或 `singularity` 二进制文件。

**镜像处理：** Docker URL（`docker://...`）会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件直接使用。

**临时目录：** 按以下顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（HPC 惯例）→ `~/.hermes/sandboxes/singularity`。

**隔离：** 使用 `--containall --no-home` 实现完全的命名空间隔离，不挂载宿主机 home 目录。

### 常见终端后端问题

如果终端命令立即失败或终端工具报告为禁用：

- **本地** — 无特殊要求。入门时最安全的默认选项。
- **Docker** — 运行 `docker version` 验证 Docker 是否正常工作。如果失败，请修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少任一，Hermes 会记录清晰的错误信息。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 进行检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 处理服务器 URL 配置。
- **Singularity** — `$PATH` 中需要 `apptainer` 或 `singularity`。常见于 HPC 集群。

如有疑问，请将 `terminal.backend` 设置回 `local`，并首先验证命令能否在那里运行。

### 会话结束时从远程到主机的文件同步

对于 **SSH**、**Modal** 和 **Daytona** 后端（任何 Agent 的工作树与运行 Hermes 的主机不在同一台机器上的情况），Hermes 会跟踪 Agent 在远程沙盒内接触过的文件，并在会话结束/沙盒清理时，**将修改过的文件同步回主机**，位置在 `~/.hermes/cache/remote-syncs/<session-id>/` 下。

- 触发时机：会话关闭、`/new`、`/reset`、消息网关消息超时、当子 Agent 使用了远程后端时 `delegate_task` 子 Agent 完成。
- 涵盖 Agent 修改的整个工作树，而不仅仅是它显式打开的文件。新增、编辑和删除都会被捕获。
- 当你去查看时，远程沙盒可能已被销毁；本地的 `~/.hermes/cache/remote-syncs/…` 副本是 Agent 所做更改的权威记录。
- 大型二进制输出（模型检查点、原始数据集）受大小限制 — 同步会跳过超过 `file_sync_max_mb`（默认 `100`）的文件。如果你期望有更大的产物返回，请调高此值。

```yaml
terminal:
  file_sync_max_mb: 100     # 默认值 — 同步每个最大 100 MB 的文件
  file_sync_enabled: true   # 默认值 — 设为 false 以完全跳过同步
```

这就是你如何从会话结束后即被销毁的临时云沙盒中恢复结果，而无需告诉 Agent 显式地 `scp` 或 `modal volume put` 每个产物。

### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你与容器共享主机目录。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/.hermes/cache/documents:/output" # 消息网关可见的导出目录
```

这适用于：
- **向 Agent 提供文件**（数据集、配置、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出物）
- **共享工作区**，你与 Agent 都可以访问相同的文件

如果你使用消息网关，并希望 Agent 通过 `MEDIA:/...` 发送生成的文件，建议使用一个专用的、主机可见的导出挂载点，例如 `/home/user/.hermes/cache/documents:/output`。

- 在 Docker 内将文件写入 `/output/...`
- 在 `MEDIA:` 中发出**主机路径**，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`
- **不要**发出 `/workspace/...` 或 `/output/...`，除非该确切路径也存在于主机上的网关进程中

:::warning
YAML 中的重复键会静默覆盖较早的键。如果你已经有一个 `docker_volumes:` 块，请将新的挂载合并到同一个列表中，而不是在文件后面添加另一个 `docker_volumes:` 键。
:::

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

### Docker 凭据转发

默认情况下，Docker 终端会话不会继承任意的宿主机凭据。如果你需要在容器内使用特定的 Token，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 首先从你当前的 shell 解析每个列出的变量，如果变量已通过 `hermes config set` 保存，则回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。只转发你愿意暴露给终端会话的凭据。
:::

### 以宿主机用户身份运行容器

默认情况下，Docker 容器以 `root`（UID 0）身份运行。在 `/workspace` 或其他绑定挂载中创建的文件在宿主机上最终归 root 所有，因此在会话结束后，你必须先 `sudo chown` 它们，才能从宿主机编辑器进行编辑。`terminal.docker_run_as_host_user` 标志可以解决此问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # 默认值: false
```

启用后，Hermes 会将 `--user $(id -u):$(id -g)` 附加到 `docker run` 命令，这样写入绑定挂载目录（`/workspace`、`/root`、`docker_volumes` 中的任何内容）的文件将由你的宿主机用户拥有，而不是 root。代价是：容器不能再执行 `apt install` 或写入 root 拥有的路径，如 `/root/.npm` — 如果你两者都需要，请使用其 `HOME` 归非 root 用户拥有的基础镜像（或在镜像构建时添加你所需的工具）。

为了保持向后兼容的行为，请将其保留为 `false`（默认值）。当你的工作流主要是“编辑已挂载的宿主机文件”并且你厌倦了 `sudo chown -R` 时，请打开它。

### 可选：将启动目录挂载到 `/workspace`
Docker 沙盒默认保持隔离状态。除非你明确选择启用，否则 Hermes **不会**将当前主机工作目录传递到容器中。

在 `config.yaml` 中启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该主机目录将被绑定挂载到 `/workspace`
- Docker 后端将在 `/workspace` 中启动
- 文件工具和终端命令都将看到相同的已挂载项目

禁用时，除非你通过 `docker_volumes` 显式挂载某些内容，否则 `/workspace` 将保持为沙盒所有。

安全权衡：
- `false` 保留沙盒边界
- `true` 使沙盒能够直接访问你启动 Hermes 的目录

仅当你明确希望容器处理主机上的实时文件时，才选择启用此选项。

### 持久化 Shell

默认情况下，每个终端命令都在其自己的子进程中运行——工作目录、环境变量和 shell 变量在命令之间会重置。当启用**持久化 shell**时，会在多个 `execute()` 调用之间保持一个长期存活的 bash 进程，以便状态在命令之间得以保留。

这对于 **SSH 后端**最为有用，因为它还能消除每个命令的连接开销。持久化 shell **默认对 SSH 启用**，对本地后端禁用。

```yaml
terminal:
  persistent_shell: true   # 默认值 — 为 SSH 启用持久化 shell
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

每个后端的特定环境变量具有最高优先级。如果你也想在本地后端启用持久化 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 shell 的 stdin 已被 IPC 协议占用。
:::

有关每个后端的详细信息，请参阅[代码执行](features/code-execution.md)和 README 的[终端部分](features/tools.md)。

## 技能设置

技能可以通过其 SKILL.md 的 frontmatter 声明自己的配置设置。这些是非机密值（路径、偏好、域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # 示例 — 每个技能定义自己的键
```

**技能设置的工作原理：**

- `hermes config migrate` 扫描所有已启用的技能，查找未配置的设置，并提供提示
- `hermes config show` 在"技能设置"下显示所有技能设置及其所属的技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

有关在自定义技能中声明配置设置的详细信息，请参阅[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

### 对 Agent 创建的技能写入的防护

当 Agent 使用 `skill_manage` 创建、编辑、修补或删除技能时，Hermes 可以选择性地扫描新/更新的内容，查找危险的关键字模式（凭据收集、明显的提示词注入、数据外泄指令）。扫描器**默认关闭**——因为合法的 Agent 工作流（确实会操作 `~/.ssh/` 或提及 `$OPENAI_API_KEY`）触发启发式规则的频率太高。如果你希望扫描器在 Agent 的技能写入生效前提示你，请重新启用它：

```yaml
skills:
  guard_agent_created: true   # 默认值: false
```

启用后，任何被标记的 `skill_manage` 写入操作都会显示一个带有扫描器理由的批准提示。接受的写入会生效；拒绝的写入会向 Agent 返回解释性错误。

## 记忆配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 个 Token
  user_char_limit: 1375     # ~500 个 Token
```

## 文件读取安全

控制单个 `read_file` 调用可以返回多少内容。超过限制的读取会被拒绝，并返回错误，告知 Agent 使用 `offset` 和 `limit` 来读取更小的范围。这可以防止单次读取压缩的 JS 包或大型数据文件淹没上下文窗口。

```yaml
file_read_max_chars: 100000  # 默认值 — ~25-35K 个 Token
```

如果你使用的是具有大上下文窗口的模型，并且经常读取大文件，请提高此值。对于小上下文模型，降低此值以保持读取效率：

```yaml
# 大上下文模型 (200K+)
file_read_max_chars: 200000

# 小型本地模型 (16K 上下文)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重——如果同一文件区域被读取两次且文件未更改，则返回轻量级存根而不是重新发送内容。这会在上下文压缩时重置，以便 Agent 可以在其内容被摘要化后重新读取文件。

## 工具输出截断限制

三个相关的上限控制工具在 Hermes 截断其输出前可以返回多少原始输出：

```yaml
tool_output:
  max_bytes: 50000        # 终端输出上限（字符数）
  max_lines: 2000         # read_file 分页上限
  max_line_length: 2000   # read_file 行号视图中的每行上限
```

- **`max_bytes`** — 当 `terminal` 命令产生的组合 stdout/stderr 超过此字符数时，Hermes 保留前 40% 和后 60%，并在它们之间插入 `[OUTPUT TRUNCATED]` 通知。默认值 `50000`（≈12-15K 个 Token，取决于典型的 Token 化器）。
- **`max_lines`** — 单个 `read_file` 调用的 `limit` 参数的上限。超过此值的请求会被限制，以防止单次读取淹没上下文窗口。默认值 `2000`。
- **`max_line_length`** — 当 `read_file` 输出带行号的视图时应用的每行上限。超过此长度的行将被截断为此字符数，后跟 `... [truncated]`。默认值 `2000`。
提升支持大上下文窗口模型的限制，这些模型每次调用可以处理更多原始输出。降低小上下文模型的限制，以保持工具结果紧凑：

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

要在一个地方禁止 CLI 和所有消息网关平台上的特定工具集，请在 `agent.disabled_toolsets` 下列出它们的名称：

```yaml
agent:
  disabled_toolsets:
    - memory       # 隐藏记忆工具和 MEMORY_GUIDANCE 注入
    - web          # 在任何地方禁用 web_search / web_extract
```

此设置在**每个平台的工具配置之后**应用（由 `hermes tools` 写入的 `platform_toolsets`），因此此处列出的工具集总是会被移除——即使某个平台的保存配置仍然列出了它。当您想要一个“在所有地方关闭 X”的单一开关，而不是在 `hermes tools` UI 中编辑 15 个以上的平台行时，请使用此功能。

将列表留空或省略该键，则无任何操作。

## Git Worktree 隔离

为在同一仓库上并行运行多个 Agent 启用隔离的 git worktree：

```yaml
worktree: true    # 始终创建一个 worktree（与 hermes -w 相同）
# worktree: false # 默认值 — 仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个带有自己分支的新 worktree。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的 worktree 会在退出时被移除；脏的 worktree 会被保留以供手动恢复。

您还可以通过在仓库根目录下的 `.worktreeinclude` 文件中列出要复制到 worktree 中的 git 忽略文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩

Hermes 会自动压缩长对话，以保持在模型的上下文窗口内。压缩摘要器是一个独立的 LLM 调用——您可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（没有环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # 开启/关闭压缩
  threshold: 0.50                                   # 在此上下文限制百分比时触发压缩
  target_ratio: 0.20                                # 作为最近尾部保留的阈值分数
  protect_last_n: 20                                # 保持未压缩的最小最近消息数
  protect_first_n: 3                                # 在每次压缩中固定的非系统头部消息数（0 = 不固定任何内容）
  hygiene_hard_message_limit: 400                   # 消息网关安全阀 — 见下文

# 摘要模型/提供商的配置位于 auxiliary 下：
auxiliary:
  compression:
    model: ""                                       # 空 = 使用主聊天模型。覆盖为例如 "google/gemini-3-flash-preview" 以使用更便宜/更快的压缩模型。
    provider: "auto"                                # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等。
    base_url: null                                  # 自定义 OpenAI 兼容端点（覆盖 provider）
```

:::info 旧配置迁移
带有 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 的旧配置在首次加载时（配置版本 17）会自动迁移到 `auxiliary.compression.*`。无需手动操作。
:::

`hygiene_hard_message_limit` 是一个仅用于消息网关的**压缩前安全阀**。拥有数千条消息的失控会话可能在正常的上下文百分比阈值触发之前就达到了模型上下文限制；当消息数量超过此上限时，无论 Token 使用情况如何，Hermes 都会强制进行压缩。默认值为 `400`——对于非常长会话是常态的平台，可以提高此值；降低此值以强制进行更积极的压缩。在运行中的消息网关上编辑此值会在下一条消息时生效（见下文）。

`protect_first_n` 控制有多少**非系统**头部消息在每次压缩中被固定。默认值为 `3`——初始的用户/助手交换会在每次摘要器处理中保留，以便原始目标保持可见。在长时间运行的滚动压缩会话中，如果初始回合已不再相关，请设置 `protect_first_n: 0` 以仅固定系统提示词 + 摘要 + 尾部，而不固定其他内容。无论此设置如何，系统提示词本身总是会被保留。

:::tip 消息网关对压缩和上下文长度的热重载
自近期版本起，在运行中的消息网关上编辑 `config.yaml` 中的 `model.context_length` 或任何 `compression.*` 键，会在下一条消息时生效——无需重启消息网关、无需 `/reset`、无需会话轮换。缓存的 Agent 签名包含这些键，因此当消息网关检测到更改时，会透明地重建 Agent。API 密钥和工具/技能配置仍然需要通常的重载路径。
:::

### 常见设置

**默认（自动检测） — 无需配置：**
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
| `auto` (默认) | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商，使用其身份验证 |
| 任意 | 已设置 | 直接使用自定义端点（忽略 provider） |
:::warning 摘要模型上下文长度要求
摘要模型**必须**拥有至少与主 Agent 模型一样大的上下文窗口。压缩器会将对话的完整中间部分发送给摘要模型——如果该模型的上下文窗口小于主模型，摘要调用将因上下文长度错误而失败。发生这种情况时，中间轮次的对话会被**直接丢弃而不进行摘要**，从而静默地丢失对话上下文。如果您覆盖了模型，请验证其上下文长度是否达到或超过主模型。
:::

## 上下文引擎

上下文引擎控制在接近模型 Token 限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（参见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎可以用其他策略替换它。

```yaml
context:
  engine: "compressor"    # 默认值 — 内置有损摘要
```

要使用插件引擎（例如，用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活**——您必须将 `context.engine` 显式设置为插件名称。可用的引擎可以通过 `hermes plugins` → Provider Plugins → Context Engine 浏览和选择。

有关内存插件的类似单选系统，请参阅[记忆提供商](/user-guide/features/memory-providers)。

## 迭代预算压力

当 Agent 处理具有许多工具调用的复杂任务时，它可能会在未意识到预算即将耗尽的情况下快速消耗其迭代预算（默认值：90 轮）。预算压力会在接近限制时自动警告模型：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息——这可以保留提示词缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认值：90）
  api_max_retries: 3           # 触发回退机制前每个提供商的重试次数（默认值：3）
```

预算压力默认启用。Agent 会自然地看到作为工具结果一部分的警告，鼓励它在迭代次数用完之前整合工作并给出响应。

当迭代预算完全耗尽时，CLI 会向用户显示通知：`⚠ Iteration budget reached (90/90) — response may be incomplete`。如果预算在活动工作中耗尽，Agent 会在停止前生成已完成工作的摘要。

`agent.api_max_retries` 控制 Hermes 在触发回退提供商切换**之前**，对瞬时错误（速率限制、连接中断、5xx 错误）重试提供商 API 调用的次数。默认值为 `3`——总共尝试四次。如果您配置了[回退提供商](/user-guide/features/fallback-providers)并希望更快地故障转移，请将其降至 `0`，这样主提供商上的第一个瞬时错误会立即切换到回退提供商，而不是对不稳定的端点进行重试。

### API 超时

Hermes 为流式传输设置了独立的超时层，并为非流式调用设置了陈旧检测器。只有当您将它们保留为隐式默认值时，陈旧检测器才会仅针对本地提供商自动调整。

| 超时 | 默认值 | 本地提供商 | 配置 / 环境变量 |
|---------|---------|----------------|--------------|
| Socket 读取超时 | 120s | 自动提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180s | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| 陈旧非流检测 | 300s | 保留隐式值时自动禁用 | `providers.<id>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 不变 | `providers.<id>.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |

**Socket 读取超时**控制 httpx 等待提供商下一个数据块的时间。本地 LLM 在大型上下文上进行预填充可能需要几分钟才能产生第一个 Token，因此当 Hermes 检测到本地端点时，会将其提升至 30 分钟。如果您显式设置了 `HERMES_STREAM_READ_TIMEOUT`，则无论端点检测结果如何，都将始终使用该值。

**陈旧流检测**会终止那些接收 SSE 保持活动 ping 但没有实际内容的连接。这对于本地提供商是完全禁用的，因为它们在预填充期间不发送保持活动 ping。

**陈旧非流检测**会终止那些长时间没有响应的非流式调用。默认情况下，Hermes 在本地端点上禁用此功能，以避免在长时间预填充期间出现误报。如果您显式设置了 `providers.<id>.stale_timeout_seconds`、`providers.<id>.models.<model>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT`，那么即使在本地端点上也会遵循该显式值。

## 上下文压力警告

与迭代预算压力不同，上下文压力跟踪对话距离**压缩阈值**有多近——即触发上下文压缩以摘要旧消息的点。这有助于您和 Agent 了解对话何时变得过长。

| 进度 | 级别 | 发生的情况 |
|----------|-------|-------------|
| 距离阈值 **≥ 60%** | 信息 | CLI 显示青色进度条；消息网关发送信息性通知 |
| 距离阈值 **≥ 85%** | 警告 | CLI 显示粗体黄色进度条；消息网关警告压缩即将发生 |

在 CLI 中，上下文压力显示为工具输出反馈中的进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```
如果自动压缩被禁用，警告会提示你上下文可能会被截断。

上下文压力是自动的——无需配置。它纯粹作为面向用户的通知触发，不会修改消息流或向模型的上下文中注入任何内容。

## 凭证池策略

当你为同一提供商拥有多个 API 密钥或 OAuth 令牌时，可以配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀轮换密钥
  anthropic: least_used      # 总是选择使用最少的密钥
```

选项：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅[凭证池](/user-guide/features/credential-pools)。

## 提示词缓存

当活跃的提供商支持时，Hermes 会自动开启跨会话提示词缓存——无需用户配置。

对于 **原生 Anthropic**、**OpenRouter** 和 **Nous Portal** 上的 Claude，Hermes 会在系统提示词和技能块上附加带有 1 小时 TTL（`ttl: "1h"`）的 `cache_control` 断点。在新的一小时内首次发送需支付完整的输入费用；同一小时内跨任何会话的后续发送将从缓存中提取，享受折扣的缓存读取费率。这意味着系统提示词、加载的技能内容以及任何长上下文包含的早期部分，在第一个小时内可以在 `hermes` 会话之间以及分叉的子 Agent 之间重复使用。

Qwen Cloud（阿里云 DashScope）上游将缓存 TTL 限制在 5 分钟，因此 Hermes 在那里使用 5 分钟的断点 TTL。其他通过第三方路径的 Claude（AWS Bedrock、Azure Foundry）则回退到提供商自己的默认缓存设置。xAI Grok 使用独立的会话固定对话 ID 机制——请参阅 [xAI 提示词缓存](/integrations/providers#xai-grok--responses-api--prompt-caching)。

没有开关可以禁用此功能——缓存始终开启，即使在单轮对话中也能节省费用，因为仅系统提示词就占了输入 Token 数量的相当一部分。

## 辅助模型

Hermes 使用“辅助”模型来处理图像分析、网页摘要、浏览器截图分析、会话标题生成和上下文压缩等辅助任务。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将每个辅助任务路由到你的**主聊天模型**——即你在 `hermes model` 中选择的同一提供商/模型。你无需配置任何东西即可开始使用，但请注意，在昂贵的推理模型（Opus、MiniMax M2.7 等）上，辅助任务会增加可观的成本。如果你希望无论主模型是什么，辅助任务都使用廉价且快速的模型，请显式设置 `auxiliary.<task>.provider` 和 `auxiliary.<task>.model`（例如，使用 OpenRouter 上的 Gemini Flash 进行视觉和网页提取）。

:::note 为什么 "auto" 使用你的主模型
早期版本将聚合器用户（OpenRouter、Nous Portal）分流到提供商端的廉价默认模型上。这令人困惑——付费订阅聚合器的用户会看到不同的模型处理他们的辅助流量。现在 `auto` 对所有人都使用主模型，而 `config.yaml` 中的每任务覆盖设置仍然优先（见下文[完整的辅助配置参考](#full-auxiliary-config-reference)）。
:::

### 交互式配置辅助模型

无需手动编辑 YAML，运行 `hermes model` 并从菜单中选择 **"Configure auxiliary models"**。你将获得一个交互式的每任务选择器：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               当前: auto / 主模型
[ ] web_extract          当前: auto / 主模型
[ ] title_generation     当前: openrouter / google/gemini-3-flash-preview
[ ] compression          当前: auto / 主模型
[ ] approval             当前: auto / 主模型
[ ] triage_specifier     当前: auto / 主模型
[ ] kanban_decomposer    当前: auto / 主模型
[ ] profile_describer    当前: auto / 主模型
```

选择一个任务，选择一个提供商（OAuth 流程会打开浏览器；API 密钥提供商会提示），选择一个模型。更改将持久保存到 `config.yaml` 中的 `auxiliary.<task>.*`。与主模型选择器使用相同的机制——无需学习额外的语法。

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
| `provider` | 用于认证和路由的提供商 | `"auto"` |
| `model` | 请求的模型 | 提供商的默认值 |
| `base_url` | 自定义的 OpenAI 兼容端点（覆盖提供商） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略提供商并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当只设置了 `provider` 时，Hermes 使用该提供商内置的认证和基础 URL。

辅助任务可用的提供商：`auto`、`main`，以及[提供商注册表](/reference/environment-variables)中的任何提供商——`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`azure-foundry`——或者你 `custom_providers` 列表中的任何命名自定义提供商（例如 `provider: "beans"`）。

:::tip MiniMax OAuth
`minimax-oauth` 通过浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **MiniMax (OAuth)** 进行认证。辅助任务自动使用 `MiniMax-M2.7-highspeed`。请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::
:::tip xAI Grok OAuth
`xai-oauth` 通过浏览器 OAuth 登录，适用于 SuperGrok 和 X Premium+ 订阅用户（无需 API 密钥）。运行 `hermes model` 并选择 **xAI Grok OAuth (SuperGrok / Premium+)** 进行身份验证。同一个 OAuth Token 会复用于所有直接对接 xAI 的功能（聊天、辅助任务、TTS、图像生成、视频生成、转录）。请参阅 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)，如果 Hermes 在远程主机上，请参阅 [通过 SSH / 远程主机进行 OAuth](../guides/oauth-over-ssh.md)。
:::

:::warning `"main"` 仅用于辅助任务
`"main"` 这个提供商选项意味着“使用我的主 Agent 所用的任何提供商”——它仅在 `auxiliary:`、`compression:` 和主备选条目（`fallback_providers:` 或旧的 `fallback_model:`）内部有效。它**不是**顶层 `model.provider` 设置的有效值。如果你使用自定义的 OpenAI 兼容端点，请在 `model:` 部分设置 `provider: custom`。所有主模型提供商选项请参阅 [AI 提供商](/integrations/providers)。
:::

### 完整的辅助配置参考

```yaml
auxiliary:
  # 图像分析 (vision_analyze 工具 + 浏览器截图)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main" 等。
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点（覆盖 provider）
    api_key: ""                # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
    timeout: 120               # 秒 — LLM API 调用超时；视觉负载需要较长的超时时间
    download_timeout: 30       # 秒 — 图像 HTTP 下载超时；对于慢速连接请增加此值

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

  # 上下文压缩超时（与 compression.* 配置分开）
  compression:
    timeout: 120               # 秒 — 压缩功能用于总结长对话，需要更多时间

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

  # 看板分类指定器 — `hermes kanban specify <id>`（或仪表板上 Triage 列卡片上的 ✨ Specify 按钮）使用此槽位将一行描述扩展为具体规格，并将任务提升到 `todo` 状态。便宜快速的模型在这里效果很好；规格扩展很短，不需要推理深度。
  triage_specifier:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 120
```

:::tip
每个辅助任务都有一个可配置的 `timeout`（以秒为单位）。默认值：vision 120秒，web_extract 360秒，approval 30秒，compression 120秒。如果你为辅助任务使用慢速的本地模型，请增加这些值。Vision 还有一个单独的 `download_timeout`（默认 30秒）用于 HTTP 图像下载——对于慢速连接或自托管的图像服务器，请增加此值。
:::

:::info
上下文压缩有自己的 `compression:` 块用于设置阈值，以及一个 `auxiliary.compression:` 块用于模型/提供商设置——请参阅上文的 [上下文压缩](#context-compression)。主备选链使用顶层的 `fallback_providers:` 列表——请参阅 [备选提供商](/integrations/providers#fallback-providers)。这三者都遵循相同的 provider/model/base_url 模式。
:::

### 辅助任务的 OpenRouter 路由和 Pareto Code

当辅助任务解析到 OpenRouter（无论是显式指定还是通过 `provider: "main"` 而你的主 Agent 正在使用 OpenRouter 时），主 Agent 的 `provider_routing` 和 `openrouter.min_coding_score` 设置**不会传播**——根据设计，每个辅助任务是独立的。要为特定的辅助任务设置 OpenRouter 提供商偏好或使用 [Pareto Code 路由器](/integrations/providers#openrouter-pareto-code-router)，请通过 `extra_body` 为每个任务单独设置：

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

其结构镜像了 OpenRouter 在聊天补全请求体中接受的内容。Hermes 会原样转发整个 `extra_body`，因此 [openrouter.ai/docs](https://openrouter.ai/docs) 上记录的任何其他 OpenRouter 请求体字段都以相同的方式工作。

### 更改视觉模型

要使用 GPT-4o 而不是 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或者通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`）和主备选条目（`fallback_providers:` 或旧的 `fallback_model:`），不适用于你的主 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 最佳可用（默认）。Vision 尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter — 路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账户）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"minimax-oauth"` | 强制使用 MiniMax OAuth（浏览器登录，无需 API 密钥）。辅助任务使用 MiniMax-M2.7-highspeed。 | `hermes model` → MiniMax (OAuth) |
| `"xai-oauth"` | 强制使用 xAI Grok OAuth（SuperGrok 或 X Premium+ 订阅用户的浏览器登录，无需 API 密钥）。同一个 OAuth Token 覆盖聊天、TTS、图像、视频和转录。 | `hermes model` → xAI Grok OAuth (SuperGrok / Premium+) |
| `"main"` | 使用你活动的自定义/主端点。这可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，或者来自通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容的 API。**仅限辅助任务 — 对 `model.provider` 无效。** | 自定义端点凭据 + base URL |
当您希望辅助任务绕过默认路由时，来自主提供商目录的直接 API 密钥提供商在此处也适用。配置 `GMI_API_KEY` 后，`gmi` 即生效：

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

对于 GMI 辅助路由，请使用 GMI 的 `/v1/models` 端点返回的确切模型 ID。

### 常见设置

**使用直接自定义端点**（对于本地/自托管 API，比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由到特定端点的最明确方式。对于直接端点覆盖，Hermes 使用配置的 `api_key` 或回退到 `OPENAI_API_KEY`；它不会为该自定义端点重用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥处理视觉任务：**
```yaml
# 在 ~/.hermes/.env 中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或更便宜的 "gpt-4o-mini"
```

**使用 OpenRouter 处理视觉任务**（路由到任何模型）：
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
运行 `hermes model` 并选择 **MiniMax (OAuth)** 以自动登录并设置此配置。对于中国区，基础 URL 将是 `https://api.minimaxi.com/anthropic`。完整步骤请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用您用于正常聊天的活动提供商
    model: "my-local-model"
```

`provider: "main"` 使用 Hermes 用于正常聊天的任何提供商 — 无论是命名的自定义提供商（例如 `beans`）、内置提供商如 `openrouter`，还是遗留的 `OPENAI_BASE_URL` 端点。

:::tip
如果您使用 Codex OAuth 作为您的主模型提供商，视觉功能会自动生效 — 无需额外配置。Codex 已包含在视觉任务的自动检测链中。
:::

:::warning
**视觉任务需要多模态模型。** 如果您设置 `provider: "main"`，请确保您的端点支持多模态/视觉 — 否则图像分析将失败。
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

压缩和回退模型设置仅支持 config.yaml 配置。

:::tip
运行 `hermes config` 查看您当前的辅助模型设置。仅当覆盖项与默认值不同时才会显示。
:::

## 推理强度

控制模型在响应前进行多少“思考”：

```yaml
agent:
  reasoning_effort: ""   # 空 = 中等（默认）。选项：none, minimal, low, medium, high, xhigh (max)
```

当未设置时（默认），推理强度默认为“medium” — 这是一个适用于大多数任务的平衡级别。设置一个值会覆盖它 — 更高的推理强度在复杂任务上能提供更好的结果，但代价是消耗更多 Token 和增加延迟。

您也可以在运行时使用 `/reasoning` 命令更改推理强度：

```
/reasoning           # 显示当前强度级别和显示状态
/reasoning high      # 将推理强度设置为 high
/reasoning none      # 禁用推理
/reasoning show      # 在每个响应上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

## 工具使用强制

某些模型偶尔会将预期操作描述为文本，而不是进行工具调用（例如“我会运行测试...”而不是实际调用终端）。工具使用强制会注入系统提示词指导，引导模型回到实际调用工具的行为。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认） | 对匹配以下模型的启用：`gpt`, `codex`, `gemini`, `gemma`, `grok`。对所有其他模型（Claude, DeepSeek, Qwen 等）禁用。 |
| `true` | 无论模型如何，始终启用。如果您发现当前模型描述操作而不是执行操作，这很有用。 |
| `false` | 无论模型如何，始终禁用。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名称包含列出的子字符串之一（不区分大小写）时启用。 |

### 注入的内容

启用后，可能会向系统提示词添加三层指导：

1.  **通用工具使用强制**（所有匹配的模型） — 指示模型立即进行工具调用，而不是描述意图；持续工作直到任务完成；并且永远不要以承诺未来行动来结束一个回合。

2.  **OpenAI 执行纪律**（仅限 GPT 和 Codex 模型） — 额外的指导，解决 GPT 特有的失败模式：在部分结果上放弃工作、跳过先决条件查找、产生幻觉而不是使用工具，以及在未经验证的情况下声明“完成”。

3.  **Google 操作指导**（仅限 Gemini 和 Gemma 模型） — 简洁性、绝对路径、并行工具调用以及编辑前验证模式。
这些对用户是透明的，只影响系统提示词。已经能可靠使用工具的模型（如 Claude）不需要这种引导，这就是为什么 `"auto"` 会排除它们。

### 何时开启

如果你使用的模型不在默认的自动列表中，并且注意到它经常描述它*将*做什么而不是实际去做，请设置 `tool_use_enforcement: true` 或将模型子字符串添加到列表中：

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts"
  speed: 1.0                    # 全局语速乘数（所有提供商的回退值）
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 语速乘数（转换为速率百分比，例如 1.5 → +50%）
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # 语速乘数（API 限制在 0.25–4.0 之间）
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

**语速回退层级：** 提供商特定语速（例如 `tts.edge.speed`）→ 全局 `tts.speed` → 默认值 `1.0`。设置全局 `tts.speed` 以对所有提供商应用统一的语速，或者按提供商覆盖以进行细粒度控制。

## 显示设置

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  platforms: {}           # 按平台的显示覆盖（见下文）
  tool_progress_overrides: {}  # 已弃用 — 请使用 display.platforms 代替
  interim_assistant_messages: true  # 网关：将自然的回合中助手更新作为单独消息发送
  skin: default           # 内置或自定义 CLI 皮肤（参见 user-guide/features/skins）
  personality: "kawaii"  # 遗留的装饰性字段，仍在某些摘要中显示
  compact: false          # 紧凑输出模式（更少的空白）
  resume_display: full    # full (恢复时显示之前的消息) | minimal (仅显示一行摘要)
  bell_on_complete: false # 当 Agent 完成任务时播放终端提示音（适用于长时间任务）
  show_reasoning: false   # 在每个响应上方显示模型推理/思考过程（使用 /reasoning show|hide 切换）
  streaming: false        # 将 Token 实时流式传输到终端（实时输出）
  show_cost: false        # 在 CLI 状态栏中显示估算的 $ 成本
  timestamps: false       # 为 true 时，在 CLI / TUI 记录中为用户和助手标签前缀 [HH:MM] 时间戳
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 无限制，显示完整路径/命令）
  runtime_footer:         # 网关：在最终回复后附加运行时上下文页脚
    enabled: false
    fields: ["model", "context_pct", "cwd"]
  file_mutation_verifier: true    # 当 write_file/patch 调用在本回合失败时，附加一个提示性页脚
  language: en            # 静态消息的 UI 语言（批准提示、部分网关回复）。en | zh | zh-hant | ja | de | es | fr | tr | uk | af | ko | it | ga | pt | ru | hu
```

### 文件修改验证器

当 `display.file_mutation_verifier` 为 `true`（默认）时，只要一个 `write_file` 或 `patch` 调用在本回合期间失败，并且从未被对同一路径的成功写入所取代，Hermes 就会在助手的最终响应后附加一行提示。这可以捕捉到"一批并行补丁，一半静默失败，模型总结成功"这类过度声称的情况，而无需你在每次编辑后手动运行 `git status`。

示例页脚：

```
⚠️ 文件修改验证器：尽管上述措辞可能暗示成功，但本回合有 3 个文件未被修改。请运行 `git status` 或 `read_file` 来确认。
  • concepts/automatic-organization.md — [patch] 无法找到 old_string 的匹配项
  • concepts/lora.md — [patch] 无法找到 old_string 的匹配项
  • concepts/rag-pipeline.md — [patch] 无法找到 old_string 的匹配项
```

设置 `file_mutation_verifier: false`（或 `HERMES_FILE_MUTATION_VERIFIER=0`）以抑制该页脚。验证器仅在回合结束时仍有实际失败未解决时触发——如果模型在同一回合内重试失败的补丁并成功，则不会为该文件触发验证器。

### 静态消息的 UI 语言

`display.language` 设置翻译一小部分面向用户的静态消息——CLI 批准提示、少数网关斜杠命令回复（例如重启-清空通知、"批准已过期"、"目标已清除"）。它**不**翻译 Agent 响应、日志行、工具输出、错误回溯或斜杠命令描述——这些保持英文。如果你希望 Agent 本身用另一种语言回复，只需在你的提示词或系统消息中告诉它。

支持的值：`en`（默认）、`zh`（简体中文）、`ja`（日语）、`de`（德语）、`es`（西班牙语）、`fr`（法语）、`tr`（土耳其语）、`uk`（乌克兰语）。未知值将回退到英文。
你也可以通过 `HERMES_LANGUAGE` 环境变量按会话设置此选项，它会覆盖配置文件中的值。

```yaml
display:
  language: zh   # CLI 确认提示将以中文显示
```

| 模式 | 你将看到的内容 |
|------|-------------|
| `off` | 静默模式 — 仅显示最终响应 |
| `new` | 仅当工具变更时显示工具指示器 |
| `all` | 显示每个工具调用及其简短预览（默认） |
| `verbose` | 显示完整的参数、结果和调试日志 |

在 CLI 中，可以使用 `/verbose` 命令在这些模式间循环切换。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上方的 `display` 部分设置 `tool_progress_command: true`。该命令将循环切换模式并保存到配置中。

### 运行时元数据页脚（仅消息网关）

当 `display.runtime_footer.enabled: true` 时，Hermes 会在消息网关**每轮对话的最终**消息后附加一个小的运行时上下文页脚 — 包含与 CLI 状态栏显示的相同信息（模型、上下文百分比、当前工作目录、会话时长、Token 数、成本）。默认关闭；如果你的团队希望每条回复都包含来源信息，可以按消息网关选择启用。

```yaml
display:
  runtime_footer:
    enabled: true
    fields: ["model", "context_pct", "cwd"]   # 可选字段：model, context_pct, cwd, duration, tokens, cost
```

在任何会话中，都可以使用 `/footer` 斜杠命令在运行时切换此功能。

附加到 Telegram/Discord/Slack 回复的页脚示例：

```
— claude-opus-4.7 · 12 次工具调用 · 2分 14秒 · $0.042
```

只有每轮对话的**最终**消息会附加页脚；中间更新信息保持简洁。

### 按平台覆盖进度显示

不同平台对详细程度的需求不同。例如，Signal 无法编辑消息，因此每次进度更新都会成为一条独立的消息 — 这会造成干扰。使用 `display.platforms` 来设置每个平台的模式：

```yaml
display:
  tool_progress: all          # 全局默认值
  platforms:
    signal:
      tool_progress: 'off'    # 在 Signal 上静默显示进度
    telegram:
      tool_progress: verbose  # 在 Telegram 上显示详细进度
    slack:
      tool_progress: 'off'    # 在共享的 Slack 工作区中保持安静
```

没有覆盖设置的平台将回退到全局的 `tool_progress` 值。有效的平台键：`telegram`, `discord`, `slack`, `signal`, `whatsapp`, `matrix`, `mattermost`, `email`, `sms`, `homeassistant`, `dingtalk`, `feishu`, `wecom`, `weixin`, `bluebubbles`, `qqbot`。为了向后兼容，旧的 `display.tool_progress_overrides` 键仍然会被加载，但已弃用，并在首次加载时迁移到 `display.platforms`。

`interim_assistant_messages` 仅适用于消息网关。启用后，Hermes 会将完成的中途助手更新作为单独的聊天消息发送。这独立于 `tool_progress`，并且不需要消息网关流式传输。

## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离个人身份信息（仅消息网关）
```

当 `redact_pii` 为 `true` 时，消息网关会在将系统提示词发送给 LLM 之前，从支持的平台中删除个人身份信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希化为 `user_<12-char-sha256>` |
| 用户 ID | 哈希化为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分被哈希化，平台前缀保留（`telegram:<hash>`） |
| 主频道 ID | 数字部分被哈希化 |
| 用户姓名 / 用户名 | **不受影响**（用户选择，公开可见） |

**平台支持：** 去标识化适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除在外，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实的 ID。

哈希值是确定性的 — 同一用户始终映射到相同的哈希值，因此模型仍然可以区分群聊中的不同用户。路由和投递在内部使用原始值。

## 语音转文本（STT）

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧的回退键仍然有效
```

提供商行为：

- `local` 使用在你机器上运行的 `faster-whisper`。请使用 `pip install faster-whisper` 单独安装。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会按以下顺序自动回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式（CLI）

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内部的按键通话键
  max_recording_seconds: 120    # 长时间录音的硬性停止限制
  auto_tts: false               # 当 /voice on 时自动启用语音回复
  beep_enabled: true            # 在 CLI 语音模式中播放录音开始/结束提示音
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静默秒数
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。有关端到端设置和平台特定行为，请参阅[语音模式](/user-guide/features/voice-mode)。

## 流式传输

将 Token 实时流式传输到终端或消息平台，而不是等待完整响应。

### CLI 流式传输

```yaml
display:
  streaming: true         # 将 Token 实时流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考 Token（可选）
```

启用后，响应将在流式传输框内逐个 Token 显示。工具调用仍会被静默捕获。如果提供商不支持流式传输，它会自动回退到正常显示模式。

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

启用后，机器人会在收到第一个 Token 时发送一条消息，然后随着更多 Token 到达而渐进式地编辑它。不支持消息编辑的平台（Signal、Email、Home Assistant）会在首次尝试时自动检测到——流式传输会优雅地在该会话中禁用，而不会导致消息泛滥。

对于无需渐进式 Token 编辑的、独立的自然中途助手更新，请设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式文本超过平台的消息长度限制（约 4096 个字符），当前消息将被最终确定，并自动开始一条新消息。

**全新的最终消息（Telegram）：** Telegram 的 `editMessageText` 会保留原始消息的时间戳，因此一个长时间运行的流式回复即使在完成后也会保持第一个 Token 的时间戳。当 `fresh_final_after_seconds > 0`（默认为 `60`）时，已完成的回复将作为一条全新的消息发送（并尽力删除过时的预览消息），以便 Telegram 显示的时间戳反映完成时间。简短的预览消息仍会原地最终确定。设置为 `0` 可始终原地编辑。

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
- 无论哪种方式，线程都与其父频道保持隔离；当设置为 `true` 时，每个参与者在线程内部也拥有自己的会话。

有关行为细节和示例，请参阅[会话](/user-guide/sessions)和 [Discord 指南](/user-guide/messaging/discord)。

## 未经授权的私信行为

控制当未知用户发送私信时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 拒绝访问，但会在私信中回复一个一次性配对码。
- `ignore` 会静默丢弃未经授权的私信。
- 平台特定配置会覆盖全局默认值，因此你可以在广泛启用配对的同时，让某个平台保持安静。

## 快捷命令

定义自定义命令，这些命令要么无需调用 LLM 即可运行 shell 命令，要么将一个斜杠命令别名化为另一个。`exec` 类型的快捷命令不消耗 Token，在消息平台（Telegram、Discord 等）上用于快速服务器检查或实用脚本非常有用。

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

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update`、`/gpu` 或 `/restart`。`exec` 命令在主机本地运行并直接返回输出——无需 LLM 调用，不消耗 Token。`alias` 命令会重写为配置的斜杠命令目标。

- **30 秒超时** —— 长时间运行的命令会被终止并显示错误消息
- **优先级** —— 快捷命令在技能命令之前检查，因此你可以覆盖技能名称
- **自动补全** —— 快捷命令在调度时解析，不会显示在内置的斜杠命令自动补全表中
- **类型** —— 支持的类型是 `exec` 和 `alias`；其他类型会显示错误
- **随处可用** —— CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

仅包含字符串的提示词快捷方式不是有效的快捷命令。对于可重用的提示词工作流，请创建一个技能或别名到现有的斜杠命令。

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

- **`project`**（默认）—— 脚本在会话的工作目录中运行，使用活动的 virtualenv/conda 环境的 python。项目依赖项（`pandas`、`torch`、项目包）和相对路径（`.env`、`./data.csv`）会自然解析，与 `terminal()` 看到的内容匹配。
- **`strict`** —— 脚本在临时暂存目录中运行，使用 `sys.executable`（Hermes 自身的 python）。最大程度的可复现性，但项目依赖项和相对路径将无法解析。

环境变量清理（去除 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH`）和工具白名单在两种模式下同样适用——切换模式不会改变安全态势。
## Web 搜索后端

`web_search` 和 `web_extract` 工具支持五个后端提供商。在 `config.yaml` 中或通过 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | parallel | tavily | exa

  # 或者使用按能力划分的键来混合提供商（例如，免费搜索 + 付费提取）：
  search_backend: "searxng"
  extract_backend: "firecrawl"
```

| 后端 | 环境变量 | 搜索 | 提取 |
|---------|---------|--------|---------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ |

**后端选择：** 如果未设置 `web.backend`，则根据可用的 API 密钥自动检测后端。如果只设置了 `SEARXNG_URL`，则使用 SearXNG。如果只设置了 `EXA_API_KEY`，则使用 Exa。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则 Firecrawl 为默认值。

**SearXNG** 是一个免费、自托管、尊重隐私的元搜索引擎，可查询 70 多个搜索引擎。无需 API 密钥——只需将 `SEARXNG_URL` 设置为你的实例（例如，`http://localhost:8080`）。SearXNG 仅支持搜索；`web_extract` 需要一个单独的提取提供商（设置 `web.extract_backend`）。有关 Docker 设置说明，请参阅 [Web 搜索设置指南](/user-guide/features/web-search)。

**自托管 Firecrawl：** 将 `FIRECRAWL_API_URL` 设置为你自己的实例。设置自定义 URL 后，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=***` 以禁用身份验证）。

**Parallel 搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 以控制搜索行为——`fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

**Exa：** 在 `~/.hermes/.env` 中设置 `EXA_API_KEY`。支持 `category` 过滤（`company`、`research paper`、`news`、`people`、`personal site`、`pdf`）以及域名/日期过滤器。

## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 自动关闭空闲会话前的秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时时间（秒）
  record_sessions: false         # 将会话自动录制为 WebM 视频到 ~/.hermes/browser_recordings/
  # 可选的 CDP 覆盖——设置后，Hermes 直接附加到你自己的 Chromium 系列浏览器（通过 /browser connect），而不是启动无头浏览器。
  cdp_url: ""
  # 对话框监督器——控制当附加 CDP 后端（Browserbase、通过 /browser connect 连接的本地 Chromium 系列浏览器）时如何处理原生 JS 对话框（alert / confirm / prompt）。在 Camofox 和默认的本地 agent-browser 模式下忽略。
  dialog_policy: must_respond    # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300          # must_respond 策略下的安全自动关闭时间（秒）
  camofox:
    managed_persistence: false   # 为 true 时，Camofox 会话在重启间持久化 cookies/登录状态
    user_id: ""                  # 可选的外部管理的 Camofox userId
    session_key: ""              # Hermes 创建标签页时发送的可选会话密钥
    adopt_existing_tab: false    # 在创建新标签页前，为这个身份重用现有标签页
```

**对话框策略：**

- `must_respond` (默认) —— 捕获对话框，在 `browser_snapshot.pending_dialogs` 中显示，并等待 Agent 调用 `browser_dialog(action=...)`。在 `dialog_timeout_s` 秒内无响应后，对话框将自动关闭，以防止页面的 JS 线程永久阻塞。
- `auto_dismiss` —— 捕获后立即关闭。Agent 仍会在事后看到 `browser_snapshot.recent_dialogs` 中的对话框记录，其 `closed_by="auto_policy"`。
- `auto_accept` —— 捕获后立即接受。对于具有激进 `beforeunload` 提示的页面很有用。

有关完整的对话框工作流，请参阅 [浏览器功能页面](./features/browser.md#browser_dialog)。

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chromium 系列 CDP 设置的详细信息，请参阅 [浏览器功能页面](/user-guide/features/browser)。

## 时区

使用 IANA 时区字符串覆盖服务器本地时区。影响日志中的时间戳、定时任务调度和系统提示词中的时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区 (默认: "" = 服务器本地时间)
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

## Discord

为消息网关配置 Discord 特定行为：

```yaml
discord:
  require_mention: true          # 在服务器频道中需要 @提及 才能响应
  free_response_channels: ""     # 逗号分隔的频道 ID 列表，在这些频道中机器人无需 @提及 即可响应
  auto_thread: true              # 在频道中被 @提及 时自动创建线程
```

- `require_mention` —— 当为 `true`（默认）时，机器人仅在服务器频道中被 `@BotName` 提及时才响应。私信始终无需提及即可工作。
- `free_response_channels` —— 逗号分隔的频道 ID 列表，在这些频道中机器人响应每条消息，无需提及。
- `auto_thread` —— 当为 `true`（默认）时，频道中的提及会自动为对话创建一个线程，保持频道整洁（类似于 Slack 的线程功能）。

## 安全

执行前的安全扫描和密钥脱敏：

```yaml
security:
  redact_secrets: true           # 在工具输出和日志中对 API 密钥模式进行脱敏（默认开启）
  tirith_enabled: true           # 为终端命令启用 Tirith 安全扫描
  tirith_path: "tirith"          # tirith 二进制文件的路径（默认：`$PATH` 中的 "tirith"）
  tirith_timeout: 5              # 等待 tirith 扫描的超时时间（秒）
  tirith_fail_open: true         # 如果 tirith 不可用，允许命令执行
  website_blocklist:             # 参见下面的网站阻止列表部分
    enabled: false
    domains: []
    shared_files: []
```
- `redact_secrets` — 当设为 `true` 时，在工具输出进入会话上下文和日志之前，自动检测并隐藏看起来像 API 密钥、Token 和密码的模式。**默认开启**。仅在需要原始凭据类字符串进行调试或隐藏器开发时，才显式设置为 `false`。
- `tirith_enabled` — 当设为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/sheeki03/tirith) 扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 tirith 扫描的最大秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当设为 `true`（默认）时，如果 tirith 不可用或失败，则允许执行命令。设置为 `false` 可在 tirith 无法验证命令时阻止执行。

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
    shared_files:                # 从外部文件加载额外规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被阻止域名模式的 URL 都会在网页或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- TLD 通配符：`*.local`

共享文件每行包含一条域名规则（空行和以 `#` 开头的注释行会被忽略）。缺失或不可读的文件会记录警告，但不会禁用其他网页工具。

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
| `smart` | 使用辅助 LLM 来评估被标记的命令是否真正危险。低风险命令会自动批准，并具有会话级别的持久性。真正有风险的命令会升级给用户处理。 |
| `off` | 跳过所有审批检查。等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式对于减少审批疲劳特别有用——它允许 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用所有针对终端命令的安全检查。仅在受信任的沙盒环境中使用此设置。
:::

## 检查点

在破坏性文件操作之前自动创建文件系统快照。详情请参阅[检查点与回滚](/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: false                 # 启用自动检查点（也可通过 hermes chat --checkpoints 启用）。默认：false（需手动启用）。
  max_snapshots: 20              # 每个目录保留的最大检查点数量（默认：20）
```

## 委派

为委派工具配置子 Agent 行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型（空 = 继承父级）
  # provider: "openrouter"                  # 覆盖提供商（空 = 继承父级）
  # base_url: "http://localhost:1234/v1"    # 直接的 OpenAI 兼容端点（优先级高于 provider）
  # api_key: "local-key"                    # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
  # api_mode: ""                            # base_url 的通信协议："chat_completions"、"codex_responses" 或 "anthropic_messages"。空 = 根据 URL 自动检测（例如，以 /anthropic 结尾 → anthropic_messages）。对于启发式方法无法检测的非标准端点，请显式设置。
  max_concurrent_children: 3                # 每批次的并行子任务数（下限 1，无上限）。也可通过 DELEGATION_MAX_CONCURRENT_CHILDREN 环境变量设置。
  max_spawn_depth: 1                        # 委派树深度上限（1-3，会被限制）。1 = 扁平结构（默认）：父级生成不能委派的叶子节点。2 = 编排器子级可以生成叶子孙级。3 = 三层结构。
  orchestrator_enabled: true                # 全局开关。当为 false 时，role="orchestrator" 被忽略，无论 max_spawn_depth 如何，每个子级都被强制设为叶子节点。
```

**子 Agent 提供商:模型覆盖：** 默认情况下，子 Agent 继承父级 Agent 的提供商和模型。设置 `delegation.provider` 和 `delegation.model` 可以将子 Agent 路由到不同的提供商:模型组合——例如，使用廉价/快速的模型处理范围狭窄的子任务，而您的主 Agent 运行昂贵的推理模型。

**直接端点覆盖：** 如果您想要明显的自定义端点路径，请设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这将直接把子 Agent 发送到该 OpenAI 兼容端点，并且优先级高于 `delegation.provider`。如果省略 `delegation.api_key`，Hermes 仅回退到 `OPENAI_API_KEY`。

**通信协议（`api_mode`）：** Hermes 会根据 `delegation.base_url` 自动检测通信协议（例如，以 `/anthropic` 结尾的路径 → `anthropic_messages`；Codex / 原生 Anthropic / Kimi-coding 主机名保持其现有的检测逻辑）。对于启发式方法无法分类的端点——例如 Azure AI Foundry、MiniMax、Zhipu GLM 或代理 Anthropic 后端样式的 LiteLLM 代理——请将 `delegation.api_mode` 显式设置为 `chat_completions`、`codex_responses` 或 `anthropic_messages` 之一。保持为空（默认）以继续使用自动检测。

委派提供商使用与 CLI/消息网关启动时相同的凭据解析机制。支持所有已配置的提供商：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。设置提供商后，系统会自动解析正确的基础 URL、API 密钥和 API 模式——无需手动配置凭据。
**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父级提供商（继承）。配置中的 `delegation.model` → 父级模型（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（适用于在同一提供商内切换模型，例如 OpenRouter）。

**宽度和深度：** `max_concurrent_children` 限制每个批次中并行运行的子 Agent 数量（默认 `3`，下限为 1，无上限）。也可以通过 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量设置。当模型提交的 `tasks` 数组长度超过此限制时，`delegate_task` 会返回一个工具错误来解释该限制，而不是静默截断。`max_spawn_depth` 控制委派树的深度（限制在 1-3）。在默认值 `1` 时，委派是扁平的：子 Agent 不能生成孙 Agent，并且传递 `role="orchestrator"` 会静默降级为 `leaf`。提高到 `2` 可以使 orchestrator 子 Agent 生成 leaf 孙 Agent；`3` 用于三层树。Agent 通过 `role="orchestrator"` 在每次调用时选择启用编排；`orchestrator_enabled: false` 会强制每个子 Agent 恢复为 leaf，无论其他设置如何。成本呈乘法级增长——在 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，树最多可达到 3×3×3 = 27 个并发的 leaf Agent。有关使用模式，请参阅 [子 Agent 委派 → 深度限制和嵌套编排](features/delegation.md#depth-limit-and-nested-orchestration)。

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
| `SOUL.md` | **Agent 主要身份** — 定义 Agent 是谁（系统提示词中的槽位 #1） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上遍历至 git 根目录 |
| `AGENTS.md` | 项目特定指令，编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则文件（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |

- **SOUL.md** 是 Agent 的主要身份。它占据系统提示词中的槽位 #1，完全替换内置的默认身份。编辑它以完全自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 将回退到内置的默认身份。
- **项目上下文文件使用优先级系统** — 只加载一种类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 总是独立加载。
- **AGENTS.md** 是分层的：如果子目录也有 AGENTS.md，所有文件都会被合并。
- 如果 `SOUL.md` 不存在，Hermes 会自动创建一个默认的。
- 所有加载的上下文文件都限制在 20,000 个字符以内，并采用智能截断。

另请参阅：
- [人格 & SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

## 工作目录

| 上下文 | 默认值 |
|---------|---------|
| **CLI (`hermes`)** | 运行命令时的当前目录 |
| **消息网关** | `~/.hermes/config.yaml` 中的 `terminal.cwd`；如果未设置，则为家目录 `~` |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户家目录 |

覆盖工作目录：
```yaml
# 在 ~/.hermes/config.yaml 中：
terminal:
  cwd: /home/myuser/projects
```

`~/.hermes/.env` 中的 `MESSAGING_CWD` 和直接 `TERMINAL_CWD` 条目是旧版兼容性回退。新配置应使用 `terminal.cwd`。