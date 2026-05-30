---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent 以及使用 Docker 作为终端后端"
---

# Hermes Agent — Docker

Docker 与 Hermes Agent 有两种不同的交互方式：

1. **在 Docker 中运行 Hermes** — Agent 本身在容器内运行（本页主要关注此方式）
2. **使用 Docker 作为终端后端** — Agent 在宿主机上运行，但每个命令都在一个持久化的 Docker 沙盒容器内执行，该容器在 Hermes 进程的生命周期内（跨越工具调用、`/new` 命令和子 Agent）持续存在（参见 [配置 → Docker 后端](./configuration.md#docker-backend)）

本页涵盖第 1 种方式。该容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在从宿主机挂载到 `/opt/data` 的单个目录中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

## 快速开始

如果你是首次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器来运行设置向导：

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将使你进入设置向导，它会提示你输入 API 密钥并将其写入 `~/.hermes/.env`。你只需要执行一次此操作。强烈建议在此步骤中为消息网关设置一个聊天系统。

:::tip
在容器内，运行一次 `hermes setup --portal` — 刷新令牌会持久保存在挂载的 `~/.hermes` 卷中。参见 [Nous Portal](/integrations/nous-portal)。
:::

## 以网关模式运行

配置完成后，以后台方式运行容器作为持久化网关（Telegram、Discord、Slack、WhatsApp 等）：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 暴露了网关的 [OpenAI 兼容 API 服务器](./features/api-server.md) 和健康检查端点。如果你只使用聊天平台（Telegram、Discord 等），它是可选的；但如果你希望仪表板或外部工具能够访问网关，则是必需的。

:::tip 网关在监督下运行
在官方 Docker 镜像中，`gateway run` **由 s6-overlay 自动监督**：如果网关进程崩溃，它会在几秒钟内重新启动，而不会丢失容器，并且仪表板（当设置了 `HERMES_DASHBOARD=1` 时）会与其一起被监督。`gateway run` CMD 进程本身是一个 `sleep infinity` 心跳，它在 s6 管理实际网关进程时保持容器存活 — 因此 `docker stop` 仍然会干净地关闭一切，但 `docker logs` 会显示被监督网关的输出。

你会在 `docker logs` 中看到一行面包屑确认升级。要选择退出 — 并恢复历史行为“网关是容器的主进程，容器退出 = 网关退出”的语义 — 请传递 `--no-supervise` 或设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。选择退出对于希望容器随网关状态码退出的 CI 冒烟测试很有用；对于生产部署，默认的监督模式严格更好。

此行为仅适用于基于 s6 的镜像。早期（基于 tini 的）镜像仍然将 `gateway run` 作为前台主进程运行。
:::

:::note 网关日志的去向
有关完整路由映射（每个配置文件的网关、仪表板、启动协调器、容器范围的 `docker logs`），请参阅下面的 [日志去向](#where-the-logs-go) 部分。
:::

注意：API 服务器的启用取决于 `API_SERVER_ENABLED=true`。要在容器内将其暴露给 `127.0.0.1` 之外，还需设置 `API_SERVER_HOST=0.0.0.0` 和一个 `API_SERVER_KEY`（最少 8 个字符 — 使用 `openssl rand -hex 32` 生成一个）。示例：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -e API_SERVER_ENABLED=true \
  -e API_SERVER_HOST=0.0.0.0 \
  -e API_SERVER_KEY="$(openssl rand -hex 32)" \
  -e API_SERVER_CORS_ORIGINS='*' \
  nousresearch/hermes-agent gateway run
```

在面向互联网的机器上开放任何端口都存在安全风险。除非你了解相关风险，否则不应这样做。

## 运行仪表板

内置的 Web 仪表板作为受监督的 s6-rc 服务，与网关在同一容器中运行。设置 `HERMES_DASHBOARD=1` 来启动它：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -p 9119:9119 \
  -e HERMES_DASHBOARD=1 \
  nousresearch/hermes-agent gateway run
```

仪表板由 s6 监督 — 如果它崩溃，`s6-supervise` 会在短暂退避后自动重启它。仪表板的 stdout/stderr 会转发到 `docker logs <container>`（无前缀；网关自身的输出现在位于每个配置文件的 s6-log 文件中 — 参见下面的 [日志去向](#where-the-logs-go) — 因此两个流不会冲突）。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）以启用受监督的仪表板服务 | *（未设置 — 服务已注册但保持停止状态）* |
| `HERMES_DASHBOARD_HOST` | 仪表板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 仪表板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_TUI` | 设置为 `1` 以暴露浏览器内的聊天标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`） | *（未设置）* |
| `HERMES_DASHBOARD_INSECURE` | 设置为 `1`（或 `true` / `yes`）以在没有 OAuth 认证门的情况下绑定。仅在受信任网络的反向代理后使用，且没有 OAuth 契约 — 仪表板会暴露 API 密钥和会话数据 | *（未设置 — 当注册了 `DashboardAuthProvider` 时强制执行认证门）* |

容器内的仪表板默认绑定到 `0.0.0.0` — 没有它，发布的 `-p 9119:9119` 端口将无法从宿主机访问。要将绑定限制在容器环回地址（用于边车 / 反向代理设置），请设置 `HERMES_DASHBOARD_HOST=127.0.0.1`。
仪表盘的 OAuth 认证门控在以下两个条件同时满足时会自动启用：

1. 绑定主机地址为非回环地址（例如容器内默认的 `0.0.0.0`），**并且**
2. 注册了 `DashboardAuthProvider` 插件。

当设置了 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 环境变量时，内置的 `dashboard_auth/nous` 提供商会自动激活（参见 [Web 仪表盘 → 认证](features/web-dashboard.md)）。门控启用后，浏览器调用者在访问任何受保护的路由之前，会被重定向到配置的门户进行 OAuth 流程。

如果没有注册任何提供者且绑定地址为非回环地址，仪表盘**将在启动时失败关闭**，并给出指向缺失环境变量的具体错误。若要明确选择退出此门控——例如在您自己的反向代理后面进行可信局域网部署，且不使用 OAuth 协议——请设置 `HERMES_DASHBOARD_INSECURE=1`。这是**唯一**禁用门控的途径；仅凭绑定主机地址本身从不意味着 `--insecure`（过去是这样，但那是在 OAuth 门控出现之前，并且会静默禁用每个容器部署的仪表盘上的门控）。

:::warning `HERMES_DASHBOARD_INSECURE=1` 会暴露 API 密钥
选择退出 OAuth 门控会将仪表盘的 API 接口（包括模型密钥和会话数据）提供给任何能访问已发布端口的人。仅当您在前面有自己的认证层，或者在您完全控制的可信局域网上时，才启用此选项。
:::

不支持将仪表盘作为单独的容器运行：其网关活跃度检测要求与网关进程共享 PID 命名空间。

## 交互式运行（CLI 聊天）

要针对正在运行的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者，如果您已经通过 Docker Desktop 等方式在正在运行的容器中打开了终端，只需运行：

```sh
/opt/hermes/.venv/bin/hermes
```

## 持久化卷

`/opt/data` 卷是所有 Hermes 状态的单一事实来源。它映射到您主机上的 `~/.hermes/` 目录，包含以下内容：

| 路径 | 内容 |
|------|----------|
| `.env` | API 密钥和密钥 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 人格/身份 |
| `sessions/` | 对话历史 |
| `memories/` | 持久化记忆存储 |
| `skills/` | 已安装的技能 |
| `home/` | 每个配置文件的 HOME 目录，用于 Hermes 工具子进程（`git`、`ssh`、`gh`、`npm` 以及技能 CLI） |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

在 `~` 下存储凭据的技能 CLI 必须针对子进程的 HOME 目录进行初始化，而不仅仅是数据卷的根目录。例如，[xurl 技能](./skills/bundled/social-media/social-media-xurl.md) 将 OAuth 状态存储在 `~/.xurl` 中；在官方的 Docker 布局中，Hermes 工具调用会将其读取为 `/opt/data/home/.xurl`，因此请使用 `HOME=/opt/data/home` 运行手动 xurl 认证，并使用 `HOME=/opt/data/home xurl auth status` 进行验证。

:::warning
切勿同时运行两个针对同一数据目录的 Hermes **网关**容器——会话文件和记忆存储并非为并发写入访问而设计。
:::

## 多配置文件支持

Hermes 支持 [多个配置文件](../reference/profile-commands.md)——独立的 `~/.hermes/` 子目录，允许您从单个安装运行独立的 Agent（不同的灵魂、技能、记忆、会话、凭据）。**在官方的 Docker 镜像中，s6 监督树将每个配置文件视为一等监督服务**，因此推荐的部署方式是**一个容器托管所有配置文件**。

使用 `hermes profile create <name>` 创建的每个配置文件都会获得：

- 在 `/run/service/gateway-<name>/` 的专用 s6 服务槽位，由运行时动态注册——无需重建容器。
- 崩溃时自动重启，由 `s6-supervise` 管理退避。
- 每个配置文件的轮转日志位于 `${HERMES_HOME}/logs/gateways/<name>/current`（10 个存档 × 每个 1 MB）。
- 跨容器重启的状态持久化：启动时协调器从每个配置文件目录读取 `gateway_state.json`，并仅为上次记录状态为 `running` 的配置文件重新启动服务槽位。已停止的配置文件保持停止状态。

您在主机上运行的生命周期命令在容器内部以相同方式工作：

```sh
# 创建配置文件——注册 gateway-<name> s6 槽位。
docker exec hermes hermes profile create coder

# 启动 / 停止 / 重启——分发 s6-svc；网关生命周期在 docker restart 后依然存在。
docker exec hermes hermes -p coder gateway start
docker exec hermes hermes -p coder gateway stop
docker exec hermes hermes -p coder gateway restart

# 状态——在容器内报告 `Manager: s6 (container supervisor)`。
docker exec hermes hermes -p coder gateway status

# 删除配置文件——同时拆除 s6 槽位。
docker exec hermes hermes profile delete coder
```

在底层，容器内的 `hermes gateway start/stop/restart` 会被拦截并路由到针对正确服务目录的 `s6-svc`；您无需直接学习 s6 命令。要查看原始监督器状态，请使用 `/command/s6-svstat /run/service/gateway-<name>`（注意 `/command/` 仅在由监督树生成的进程的 PATH 中——当通过 `docker exec` 调用时，请传递绝对路径）。

### 为什么是一个容器包含多个配置文件，而不是多个容器

在迁移到 s6 之前，“每个配置文件一个容器”是推荐模式，因为当时容器内没有监督器来管理多个网关。随着 s6 作为 PID 1，这不再是必要的，并且在几乎所有维度上，单容器布局都更简单：

| | 一个容器，多个配置文件 | 每个配置文件一个容器 |
|---|---|---|
| 磁盘开销 | 一个镜像，一个捆绑的 venv，一个 Playwright 缓存 | N 个镜像 / N 个缓存 |
| 内存开销 | 共享的 Python 解释器缓存，共享的 node_modules | 每个容器重复 |
| 配置文件创建 | `docker exec ... hermes profile create <name>`（几秒钟） | 新的 `docker run` 调用 + 端口分配 + 绑定挂载配置 |
| 每个配置文件的崩溃恢复 | `s6-supervise` 自动重启 | Docker 的 `--restart unless-stopped`（较慢，会终止同级工作） |
| 日志 | 通过 `s6-log` 实现每个配置文件的轮转文件，外加容器启动审计日志 | 每个容器使用 `docker logs <name>`——无内置轮转 |
| 备份 | 一个 `~/.hermes` 目录 | N 个需要协调的目录 |
默认配置文件（`default`）在首次启动时总是会被注册，因此全新的容器开箱即用，自带一个受监管的消息网关。额外的配置文件是纯运行时添加的。

### 何时需要单独的容器

默认情况下，配置文件在容器内运行。仅在你有特定理由时，才为每个配置文件运行单独的容器：

- **每个工作负载的资源隔离** — 例如，配置文件 A 中失控的浏览器工具会话不应导致配置文件 B 内存溢出（OOM）。容器允许你为每个配置文件设置 `--memory` / `--cpus`。
- **独立的镜像固定** — 每个工作负载使用不同的上游镜像标签。
- **网络分段** — 每个配置文件使用不同的 Docker 网络（例如，一个面向客户，一个内部使用）。
- **合规性 / 爆炸半径控制** — 不同的凭据绝不共享操作系统级别的进程树。

在这些情况下，为每个配置文件声明一个服务，使用不同的 `container_name`、`volumes` 和 `ports`：

```yaml
services:
  hermes-work:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-work
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes-work:/opt/data

  hermes-personal:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-personal
    restart: unless-stopped
    command: gateway run
    ports:
      - "8643:8642"
    volumes:
      - ~/.hermes-personal:/opt/data
```

[持久化卷](#persistent-volumes)中的警告仍然适用：切勿同时让两个容器指向同一个 `~/.hermes` 目录。每个容器内的 s6 监管器管理其自己的配置文件集；跨容器共享数据卷会损坏会话文件和记忆存储。

## 日志去向

s6 容器有四个不同的日志输出面，"为什么我的消息网关在 `docker logs` 中不显示任何内容" 是一个常见的困惑。速查表：

| 来源 | 去向 | 如何查看 |
|---|---|---|
| **每个配置文件的消息网关** (`hermes gateway run` 以及 s6 下的每个配置文件网关) | 同时输出到两个地方：`docker logs <container>`（实时，无额外前缀）**和** `${HERMES_HOME}/logs/gateways/<profile>/current`（轮转，带 ISO-8601 时间戳，10 个存档 × 每个 1 MB） | `docker logs -f hermes` 或在主机上使用 `tail -F ~/.hermes/logs/gateways/default/current` |
| **仪表盘** (当 `HERMES_DASHBOARD=1` 时) | `docker logs <container>`（无前缀） | `docker logs -f hermes` — 与网关日志行交错显示 |
| **启动协调器** (记录每次容器启动时恢复了哪些配置文件网关) | `${HERMES_HOME}/logs/container-boot.log`（仅追加的审计日志） | `tail -F ~/.hermes/logs/container-boot.log` |
| **通用 Hermes 日志** (`agent.log`, `errors.log`) | `${HERMES_HOME}/logs/`（感知配置文件） | `docker exec hermes hermes logs --follow [--level WARNING] [--session <id>]` |

有两个值得了解的实际情况：

- `logs/gateways/<profile>/current` 处的文件副本在容器重启后仍然存在。`docker logs` 仅保留当前容器生命周期内的输出（并在 `docker rm` 时被清除）；轮转的文件则持久保存在绑定挂载的卷上。
- 启动协调器的审计日志行格式为 `<iso-timestamp> profile=<name> prior_state=<state> action=<registered|started>`，因此快速执行 `grep profile=coder ~/.hermes/logs/container-boot.log` 可以揭示给定配置文件上次恢复的时间以及 s6 是否自动启动了它。

## 环境变量转发

API 密钥从容器内的 `/opt/data/.env` 文件中读取。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接的 `-e` 标志会覆盖 `.env` 文件中的值。这对于 CI/CD 或秘密管理器集成非常有用，因为你可能不希望密钥存储在磁盘上。

:::note 在寻找作为**终端后端**的 Docker 吗？
本页介绍的是在 Docker 内部运行 Hermes 本身。如果你希望 Hermes 在 Docker 沙盒容器内执行 Agent 的 `terminal` / `execute_code` 调用（一个跨 Hermes 进程共享的长生命周期容器 — 参见 issue #20561），那是一个单独的配置块 — `terminal.backend: docker` 加上 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_env`、`terminal.docker_run_as_host_user`、`terminal.docker_extra_args`、`terminal.docker_persist_across_processes` 和 `terminal.docker_orphan_reaper`。完整的配置集（包括容器生命周期规则）请参见 [配置 → Docker 后端](configuration.md#docker-backend)。
:::

## Docker Compose 示例

对于需要同时运行消息网关和仪表盘的持久化部署，使用 `docker-compose.yaml` 会很方便：

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"   # 网关 API
      - "9119:9119"   # 仪表盘（仅在 HERMES_DASHBOARD=1 时可访问）
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_DASHBOARD=1
      # 取消注释以转发特定环境变量，而不是使用 .env 文件：
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```

使用 `docker compose up -d` 启动，使用 `docker compose logs -f` 查看日志。受监管网关的标准输出也会同时输出到卷上的 `${HERMES_HOME}/logs/gateways/<profile>/current` — 完整的路由映射请参见 [日志去向](#where-the-logs-go)。

## 可选：Linux 桌面音频桥接

Docker 中的语音模式需要两件独立的事情才能工作：必须允许 Hermes 在容器内探测音频设备，并且容器必须能够访问你主机的音频服务器。以下设置涵盖了针对暴露 PulseAudio 兼容套接字的 Linux 桌面（包括许多 PipeWire 设置）的主机音频管道。

:::caution
这是一个 Linux 桌面解决方案，不是通用的 Docker Desktop 功能。当你主机音频已经正常工作，并且希望在 Hermes 容器内使用 CLI 语音模式时，这很有用。如果 Hermes 仍然报告 `Running inside Docker container -- no audio devices`，请使用包含 Docker 音频探测支持（针对 `PULSE_SERVER` / `PIPEWIRE_REMOTE`）的构建版本。
:::
首先，在你的 Compose 文件旁边创建一个 ALSA 配置：

```conf title="asound.conf"
pcm.!default {
    type pulse
    hint {
        show on
        description "Default ALSA Output (PulseAudio)"
    }
}

pcm.pulse {
    type pulse
}

ctl.!default {
    type pulse
}
```

然后构建一个安装了 ALSA PulseAudio 插件的小型派生镜像：

```dockerfile title="Dockerfile.audio"
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends libasound2-plugins \
    && rm -rf /var/lib/apt/lists/*
```

在 Compose 中使用该镜像，并透传主机的 PulseAudio socket 和 cookie：

```yaml
services:
  hermes:
    build:
      context: .
      dockerfile: Dockerfile.audio
    image: hermes-agent-audio
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    volumes:
      - ~/.hermes:/opt/data
      - /run/user/${HERMES_UID}/pulse:/run/user/${HERMES_UID}/pulse
      - ~/.config/pulse/cookie:/tmp/pulse-cookie:ro
      - ./asound.conf:/etc/asound.conf:ro
    environment:
      - HERMES_UID=${HERMES_UID}
      - HERMES_GID=${HERMES_GID}
      - XDG_RUNTIME_DIR=/run/user/${HERMES_UID}
      - PULSE_SERVER=unix:/run/user/${HERMES_UID}/pulse/native
      - PULSE_COOKIE=/tmp/pulse-cookie
```

使用你的主机 UID/GID 启动它，以便容器进程可以访问每个用户的音频 socket：

```sh
export HERMES_UID="$(id -u)"
export HERMES_GID="$(id -g)"
docker compose up -d --build
```

要验证 PortAudio 在容器内看到的内容：

```sh
docker exec hermes /opt/hermes/.venv/bin/python -c "import sounddevice as sd; print(sd.query_devices())"
```

## 资源限制

Hermes 容器需要适度的资源。推荐的最低配置：

| 资源 | 最低 | 推荐 |
|----------|---------|-------------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核心 | 2 核心 |
| 磁盘（数据卷） | 500 MB | 2+ GB（随会话/技能增长） |

浏览器自动化（Playwright/Chromium）是最耗内存的功能。如果不需要浏览器工具，1 GB 就足够了。如果使用浏览器工具，请至少分配 2 GB。

在 Docker 中设置限制：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## Dockerfile 的作用

官方镜像基于 `debian:13.4` 并包含：

- 带有所有 Hermes 依赖项的 Python 3 (`uv pip install -e ".[all]"`)
- Node.js + npm（用于浏览器自动化和 WhatsApp 桥接）
- 带有 Chromium 的 Playwright (`npx playwright install --with-deps chromium --only-shell`)
- ripgrep、ffmpeg、git 和 `xz-utils` 作为系统工具
- **`docker-cli`** — 以便在容器内运行的 Agent 可以驱动主机的 Docker 守护进程（通过绑定挂载 `/var/run/docker.sock` 来选择加入），用于 `docker build`、`docker run`、容器检查等。
- **`openssh-client`** — 启用容器内的 [SSH 终端后端](/user-guide/configuration#ssh-backend)。SSH 后端会调用系统的 `ssh` 二进制文件；没有这个，它在容器化安装中会静默失败。
- WhatsApp 桥接 (`scripts/whatsapp-bridge/`)
- **[`s6-overlay`](https://github.com/just-containers/s6-overlay) v3** 作为 PID 1（替换了旧的 `tini`）— 监督仪表板和每个配置文件的网关，在崩溃时自动重启，回收僵尸子进程，并转发信号。

容器的 `ENTRYPOINT` 是 s6-overlay 的 `/init`。启动时，它会：
1. 以 root 身份运行 `/etc/cont-init.d/01-hermes-setup`（即 `docker/stage2-hook.sh`）：可选的 UID/GID 重新映射，修复卷所有权，在首次启动时生成 `.env` / `config.yaml` / `SOUL.md`，同步捆绑的技能。
2. 运行 `/etc/cont-init.d/02-reconcile-profiles`（即 `hermes_cli.container_boot`）：遍历 `$HERMES_HOME/profiles/<name>/`，在 `/run/service/gateway-<profile>/` 下重新创建每个配置文件的网关 s6 服务槽，并仅自动启动那些最后记录状态为 `running` 的网关（参见[每个配置文件的网关监督](#per-profile-gateway-supervision)）。
3. 启动静态的 `main-hermes` 和 `dashboard` s6-rc 服务。
4. 将容器的 CMD 作为主程序执行 (`/opt/hermes/docker/main-wrapper.sh`)，该程序将用户传递给 `docker run` 的参数路由：
   - 无参数 → `hermes`（默认）
   - 第一个参数是 PATH 上的可执行文件（例如 `sleep`、`bash`）→ 直接执行它
   - 其他任何情况 → `hermes <args>`（子命令透传）
   当这个主程序退出时，容器退出，并返回其退出码。

:::warning 与 pre-s6 镜像的破坏性变更
容器 ENTRYPOINT 现在是 `/init`（s6-overlay），而不是 `/usr/bin/tini`。所有五个文档化的 `docker run` 调用模式（无参数、`chat -q "…"`、`sleep infinity`、`bash`、`--tui`）的行为都与基于 tini 的镜像相同。如果你的下游包装器依赖于 tini 特定的信号行为或硬编码的 `/usr/bin/tini --` 调用，请固定到之前的镜像标签。
:::

:::warning 权限模型
除非你在命令链中保留 `/init`（或者等效地，保留转发到 stage2 钩子的旧版 `docker/entrypoint.sh` 垫片），否则不要覆盖镜像入口点。s6-overlay 的 `/init` 以 root 身份运行，以便在首次启动时可以更改卷的所有权，然后通过 `s6-setuidgid` 为每个受监督的服务以及主程序降权到 `hermes` 用户。在官方镜像中以 root 身份启动 `hermes gateway run` 默认会被拒绝，因为它可能在 `/opt/data` 中留下 root 拥有的文件，并破坏后续的仪表板或网关启动。仅当你故意接受该风险时，才设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。
:::

### `docker exec` 自动降权到 `hermes` 用户

`docker exec hermes <cmd>` 默认在容器内以 root 身份运行，但镜像在 `/opt/hermes/bin/hermes`（PATH 中最早的位置）提供了一个薄垫片，它会检测 root 调用者并通过 `s6-setuidgid hermes` 透明地重新执行。因此，`docker exec hermes login`、`docker exec hermes profile create …`、`docker exec hermes setup` 等都会写入 UID 10000 拥有的文件——即可被受监督的网关读取——而无需额外的 `--user` 标志。非 root 调用者（受监督的进程本身、`docker exec --user hermes`、容器内的看板子代理）会命中一个短路，直接执行 venv 二进制文件，因此在热路径上没有开销。
如果你确实需要一个保留 root 权限的 `docker exec`（用于诊断会话、检查仅 root 可访问的状态、访问 `/opt/data` 之外且 root 拥有的文件），可以按次调用选择退出：

```sh
docker exec -e HERMES_DOCKER_EXEC_AS_ROOT=1 hermes <cmd>
```

垫片接受 `1` / `true` / `yes`（不区分大小写）。任何其他值——包括像 `=0` 这样的拼写错误——都会回退到降权操作，因此无法静默选择退出。如果 `s6-setuidgid` 不可用（自定义构建移除了 s6-overlay），垫片会拒绝以 root 身份运行并以退出码 126 退出，从而清晰地暴露权限模型的损坏，而不是退回到历史遗留的“陷阱”模式——即 `docker exec hermes login` 会以 `root:root` 身份写入 `auth.json`，并在每次聊天平台消息时破坏受监督的消息网关的认证。

### 按配置文件的网关监督

使用 `hermes profile create <name>` 创建的每个配置文件都会自动在 `/run/service/gateway-<name>/` 注册一个受 s6 监督的网关服务，并在容器重启时保持状态持久化的自动重启。关于面向用户的工作流和生命周期命令，请参阅上文的[多配置文件支持](#multi-profile-support)。

**相比 s6 之前的镜像，监督带来的好处：**

- 网关崩溃后，`s6-supervise` 会在约 1 秒退避后自动重启。
- 当通过 `HERMES_DASHBOARD=1` 启用仪表板时，它会在同一个监督树中受到监督，并获得相同的自动重启处理。
- `docker restart` 会保留正在运行的网关：cont-init 协调器会读取 `$HERMES_HOME/profiles/<name>/gateway_state.json`，如果最后记录的状态是 `running`，则将该槽位恢复运行。已停止的网关保持停止状态。
- 每个配置文件的网关日志持久保存在 `$HERMES_HOME/logs/gateways/<profile>/current` 下（由 `s6-log` 轮转），协调器的操作会在每次启动时追加到 `$HERMES_HOME/logs/container-boot.log`。完整的路由映射请参阅[日志去向](#where-the-logs-go)。

容器内的 `hermes status` 会报告 `Manager: s6 (container supervisor)`。使用 `/command/s6-svstat /run/service/gateway-<name>` 可以查看原始的监督器视图（注意 `/command/` 仅对监督树进程在 PATH 中；从 `docker exec` 调用时请传递绝对路径）。

## 升级

拉取最新镜像并重新创建容器。你的数据目录不受影响。

```sh
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

或者使用 Docker Compose：

```sh
docker compose pull
docker compose up -d
```

## 技能和凭证文件

当使用 Docker 作为执行环境时（不是上述方法，而是指 Agent 在 Docker 沙盒内运行命令的情况——参见[配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用复用同一个长期运行的容器，并自动将技能目录（`~/.hermes/skills/`）和技能声明的任何凭证文件以只读卷的形式绑定挂载到该容器中。技能脚本、模板和引用在沙盒内无需手动配置即可使用，并且由于该容器在 Hermes 进程的生命周期内持续存在，你安装的任何依赖项或写入的文件都会保留到下一次工具调用。

SSH 和 Modal 后端也会发生相同的同步——技能和凭证文件会在每个命令执行前通过 rsync 或 Modal 挂载 API 上传。

## 在容器中安装更多工具

官方镜像附带了一套精选的工具集（参见[Dockerfile 的作用](#what-the-dockerfile-does)），但并非 Agent 可能需要的每个工具都已预装。有五种推荐的方法，按工作量和持久性递增排序。

### npm 或 Python 工具——使用 `npx` 或 `uvx`

对于发布到 npm 或 PyPI 的任何工具，可以指示 Hermes 通过 `npx`（npm）或 `uvx`（Python）运行它，并让 Hermes 在其持久记忆中记住该命令。如果工具需要配置文件或凭证，指示它将它们放在 `/opt/data` 下（例如 `/opt/data/<tool>/config.yaml`）。

依赖项按需获取，并在容器的生命周期内缓存。写入 `/opt/data` 下的配置在容器重启后仍然存在，因为它位于绑定挂载的主机目录中。包缓存本身在 `docker rm` 后需要重建，但 `npx` 和 `uvx` 会在下次工具运行时透明地重新获取。

### 其他工具（apt 包、二进制文件）——安装并记住

对于 npm 或 PyPI 之外的任何工具——`apt` 包、预编译的二进制文件、镜像中未包含的语言运行时——指示 Hermes 如何安装它（例如 `apt-get update && apt-get install -y <package>`），并告诉它记住安装命令。该工具在容器的剩余生命周期内持续存在，当 Hermes 下次需要该工具时，会在容器重启后重新运行安装命令。

这适用于安装快速且偶尔使用的工具。对于经常使用的工具，建议采用下一种方法。

### 持久化安装——构建派生镜像

当某个工具必须在每次容器启动时立即可用，且没有重新安装的延迟时，可以构建一个继承自 `nousresearch/hermes-agent` 的新镜像，并在一个层中安装该工具：

```dockerfile
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends <your-package> \
    && rm -rf /var/lib/apt/lists/*
USER hermes
```

构建它并用它替代官方镜像：

```sh
docker build -t my-hermes:latest .
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  my-hermes:latest gateway run
```

入口点脚本和 `/opt/data` 语义保持不变地继承，因此本页其余部分仍然适用。请记住，在拉取更新的上游 `nousresearch/hermes-agent` 时，要重新构建镜像。

### 复杂工具或多服务栈——运行一个 Sidecar 容器

对于自带服务（数据库、Web 服务器、队列、无头浏览器集群）或过于庞大不适合放在 Hermes 容器内的工具，可以在共享的 Docker 网络上将它们作为单独的容器运行。Hermes 通过容器名称访问 Sidecar，就像访问本地推理服务器一样（参见[连接到本地推理服务器](#connecting-to-local-inference-servers-vllm-ollama-etc)）。
```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net

  my-tool:
    image: example/my-tool:latest
    container_name: my-tool
    restart: unless-stopped
    networks:
      - hermes-net

networks:
  hermes-net:
    driver: bridge
```

从 Hermes 容器内部，可以通过 `http://my-tool:<端口>`（或它服务的任何协议）访问 sidecar 容器。这种模式保持了每个服务的生命周期、资源限制和升级节奏的独立性，并避免了将仅被一个工具所需的依赖项塞进 Hermes 镜像中。

### 广泛有用的工具 — 请提交 issue 或 pull request

如果一个工具可能对大多数 Hermes Agent 用户有用，请考虑将其贡献到上游，而不是放在私有的派生镜像中。请在 [hermes-agent 仓库](https://github.com/NousResearch/hermes-agent) 提交 issue 或 pull request，描述该工具及其用例。捆绑到官方镜像中的工具将使每个用户受益，并避免下游分支的维护开销。

## 连接到本地推理服务器 (vLLM, Ollama 等)

当在 Docker 中运行 Hermes，而你的推理服务器（vLLM、Ollama、text-generation-inference 等）也运行在宿主机或另一个容器中时，网络配置需要特别注意。

### Docker Compose（推荐）

将两个服务放在同一个 Docker 网络中。这是最可靠的方法：

```yaml
services:
  vllm:
    image: vllm/vllm-openai:latest
    container_name: vllm
    command: >
      --model Qwen/Qwen2.5-7B-Instruct
      --served-model-name my-model
      --host 0.0.0.0
      --port 8000
    ports:
      - "8000:8000"
    networks:
      - hermes-net
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net

networks:
  hermes-net:
    driver: bridge
```

然后在你的 `~/.hermes/config.yaml` 中，使用**容器名称**作为主机名：

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::tip 关键点
- 使用**容器名称** (`vllm`) 作为主机名 — 而不是 `localhost` 或 `127.0.0.1`，它们指的是 Hermes 容器本身。
- `model` 值必须与你传递给 vLLM 的 `--served-model-name` 匹配。
- 将 `api_key` 设置为任何非空字符串（vLLM 需要该请求头，但默认不验证）。
- 在 `base_url` 中**不要**包含尾部斜杠。
:::

### 独立的 Docker run（不使用 Compose）

如果你的推理服务器直接运行在宿主机上（不在 Docker 中），在 macOS/Windows 上使用 `host.docker.internal`，在 Linux 上使用 `--network host`：

**macOS / Windows：**

```sh
docker run -d \
  --name hermes \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://host.docker.internal:8000/v1
  api_key: "none"
```

**Linux（主机网络）：**

```sh
docker run -d \
  --name hermes \
  --network host \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://127.0.0.1:8000/v1
  api_key: "none"
```

:::warning 使用 `--network host` 时，`-p` 标志会被忽略 — 所有容器端口都直接暴露在宿主机上。
:::

### 验证连接性

从 Hermes 容器内部，确认推理服务器可达：

```sh
docker exec hermes curl -s http://vllm:8000/v1/models
```

你应该能看到一个 JSON 响应，列出你提供的模型。如果失败，请检查：

1.  两个容器是否在同一个 Docker 网络上 (`docker network inspect hermes-net`)
2.  推理服务器是否监听在 `0.0.0.0`，而不是 `127.0.0.1`
3.  端口号是否匹配

### Ollama

Ollama 的工作方式相同。如果 Ollama 运行在宿主机上，使用 `host.docker.internal:11434`（macOS/Windows）或 `127.0.0.1:11434`（Linux 使用 `--network host`）。如果 Ollama 运行在同一个 Docker 网络上的自己的容器中：

```yaml
model:
  provider: custom
  model: llama3
  base_url: http://ollama:11434/v1
  api_key: "none"
```

## 故障排除

### 容器立即退出

检查日志：`docker logs hermes`。常见原因：
- 缺少或无效的 `.env` 文件 — 首先以交互模式运行以完成设置
- 如果运行时有暴露端口，可能存在端口冲突

### "Permission denied" 错误

容器的 stage2 hook 通过每个受监管服务内部的 `s6-setuidgid` 将权限降级到非 root 的 `hermes` 用户（UID 10000）。如果你的宿主机 `~/.hermes/` 目录属于不同的 UID，请设置 `HERMES_UID`/`HERMES_GID` — 或者它们的别名 `PUID`/`PGID`（为了与 LinuxServer.io 和 NAS 镜像保持一致）以匹配你的宿主机用户，或者确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

在 NAS（UGOS、Synology、unRAID）上，数据目录通常是容器无法 `chown` 的宿主机 UID 拥有的**绑定挂载**。设置 `PUID`/`PGID`（或 `HERMES_UID`/`HERMES_GID`）为该宿主机用户，以便运行时以挂载的所有者身份运行，而不是 UID 10000：

```sh
docker run -d \
  --name hermes \
  -e PUID=1000 -e PGID=10 \
  -v /volume1/docker/hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

`docker exec hermes <cmd>` 也会自动降级到 UID 10000 — 详情和每次调用的退出选项请参见 [`docker exec` 自动降级到 `hermes` 用户](#docker-exec-automatically-drops-to-the-hermes-user)。

### 浏览器工具无法工作

Playwright 需要共享内存。在你的 Docker run 命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```
### 消息网关在网络问题后未重连

`--restart unless-stopped` 标志可以处理大多数瞬时故障。如果消息网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状态

```sh
docker logs --tail 50 hermes          # 查看最近的日志
docker run -it --rm nousresearch/hermes-agent:latest version     # 验证版本
docker stats hermes                    # 资源使用情况
```