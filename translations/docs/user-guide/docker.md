---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent 以及使用 Docker 作为终端后端"
---

# Hermes Agent — Docker

Docker 与 Hermes Agent 有两种不同的交互方式：

1. **在 Docker 中运行 Hermes** — Agent 本身在容器内运行（本页主要关注点）
2. **Docker 作为终端后端** — Agent 在宿主机上运行，但在一个持久化的 Docker 沙盒容器内执行每条命令，该容器在 Hermes 进程的生命周期内（跨越工具调用、`/new` 和子 Agent）持续存在（参见[配置 → Docker 后端](./configuration.md#docker-backend)）

本页涵盖选项 1。该容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在从宿主机挂载到 `/opt/data` 的单个目录中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

## 快速开始

如果你是第一次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器来运行设置向导：

:::caution 避免在基于浏览器的 VPS 控制台中运行安装命令
一些 VPS 提供商（Hetzner Cloud 等）提供基于浏览器的控制台来管理主机。这些控制台会错误地传输特殊字符 — `:` 可能变成 `;`，`@` 可能被错误渲染，非英语键盘布局情况更糟 — 这会静默地破坏 `docker run` 参数，如 `-v ~/.hermes:/opt/data`、`-e KEY=value` 以及粘贴的 API 密钥 / Token。

**请改用 SSH 连接** (`ssh root@<host>`) 以安全地复制粘贴命令。如果必须使用浏览器控制台，请手动输入命令而不是粘贴，并在按 Enter 前仔细检查结果中的每个 `:`、`@`、`=` 和 `/`。
:::

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将使你进入设置向导，它会提示你输入 API 密钥并将其写入 `~/.hermes/.env`。你只需要执行一次此操作。强烈建议在此步骤设置一个聊天系统以供消息网关使用。

:::tip
在容器内，运行一次 `hermes setup --portal` — 刷新 Token 会持久保存在挂载的 `~/.hermes` 卷中。参见 [Nous Portal](/integrations/nous-portal)。
:::

## 在网关模式下运行

配置完成后，以后台方式运行容器作为持久化网关（Telegram、Discord、Slack、WhatsApp 等）：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 暴露了网关的 [OpenAI 兼容 API 服务器](./features/api-server.md) 和健康检查端点。如果只使用聊天平台（Telegram、Discord 等），它是可选的；但如果希望仪表板或外部工具能访问网关，则是必需的。

:::tip 网关在监督下运行
在官方 Docker 镜像中，`gateway run` **由 s6-overlay 自动监督**：如果网关进程崩溃，它会在几秒内重启，而不会丢失容器，并且仪表板（当设置了 `HERMES_DASHBOARD=1` 时）会与其一同被监督。`gateway run` CMD 进程本身是一个 `sleep infinity` 心跳，用于在 s6 管理实际网关进程时保持容器存活 — 因此 `docker stop` 仍能正常关闭一切，但 `docker logs` 显示的是被监督网关的输出。

你会在 `docker logs` 中看到一行确认升级的提示。要选择退出 — 并恢复历史行为“网关是容器的主进程，容器退出 = 网关退出”的语义 — 请传递 `--no-supervise` 或设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。选择退出对于希望容器随网关状态码退出的 CI 冒烟测试很有用；对于生产部署，默认的监督模式严格更优。

此行为仅适用于基于 s6 的镜像。早期（基于 tini 的）镜像仍将 `gateway run` 作为前台主进程运行。
:::

:::note 网关日志的去向
有关完整路由映射（每个配置文件的网关、仪表板、启动协调器、容器范围的 `docker logs`），请参阅下面的[日志去向](#where-the-logs-go)部分。
:::

注意：API 服务器的启用取决于 `API_SERVER_ENABLED=true`。要在容器内将其暴露给 `127.0.0.1` 之外，还需设置 `API_SERVER_HOST=0.0.0.0` 和一个 `API_SERVER_KEY`（最少 8 个字符 — 使用 `openssl rand -hex 32` 生成）。示例：

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

仪表板由 s6 监督 — 如果它崩溃，`s6-supervise` 会在短暂退避后自动重启它。仪表板的 stdout/stderr 会转发到 `docker logs <container>`（无前缀；网关自身的输出现在位于每个配置文件的 s6-log 文件中 — 参见下面的[日志去向](#where-the-logs-go) — 因此两个流不会冲突）。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）以启用受监督的仪表板服务 | *(未设置 — 服务已注册但保持停止状态)* |
| `HERMES_DASHBOARD_HOST` | 仪表板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 仪表板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_INSECURE` | 设置为 `1`（或 `true` / `yes`）以在没有 OAuth 认证门的情况下绑定。仅在受信任网络上的反向代理后使用，且没有 OAuth 契约 — 仪表板会暴露 API 密钥和会话数据 | *(未设置 — 当注册了 `DashboardAuthProvider` 时强制执行认证门)* |
容器内的仪表板默认绑定 `0.0.0.0` —— 如果没有这个设置，发布的 `-p 9119:9119` 端口将无法从宿主机访问。要将绑定限制在容器环回地址（用于边车/反向代理设置），请设置 `HERMES_DASHBOARD_HOST=127.0.0.1`。

当以下两个条件同时满足时，仪表板的身份验证门会自动启用：

1. 绑定主机是非环回地址（例如容器内的默认 `0.0.0.0`），**并且**
2. 注册了 `DashboardAuthProvider` 插件。

有三种内置方式来满足第二个条件：

- **用户名/密码** —— 对于可信网络或 VPN 后的自托管/本地/家庭实验室容器来说最简单：设置 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`（以及用于重启稳定会话的 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`）。不适合直接暴露在公共互联网。
- **OAuth (Nous Portal)** —— 用于托管/公共部署：当设置 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 时，`dashboard_auth/nous` 提供商会激活。
- **自托管 OIDC** —— 通过标准 OpenID Connect 对您自己的身份提供商进行身份验证：当设置 `HERMES_DASHBOARD_OIDC_ISSUER` + `HERMES_DASHBOARD_OIDC_CLIENT_ID` 时，`dashboard_auth/self_hosted` 提供商会激活。

无论您选择哪种方式，在访问任何受保护路由之前，该门都会将调用者重定向到登录页面。有关所有三种提供商的详细信息，请参阅 [Web 仪表板 → 身份验证](features/web-dashboard.md#authentication-gated-mode)。

如果未注册任何提供商且绑定是非环回地址，仪表板**将在启动时失败关闭**，并显示指向缺失环境变量的特定错误。`HERMES_DASHBOARD_INSECURE=1` 这个逃生舱口会完全禁用该门（仅绑定主机本身从不意味着 `--insecure`），但它会提供一个未经身份验证的仪表板 —— 除非您在前面有自己的身份验证层，否则请配置一个提供商。

:::warning `HERMES_DASHBOARD_INSECURE=1` 会暴露 API 密钥
选择退出 OAuth 门会将仪表板的 API 接口（包括模型密钥和会话数据）提供给任何能访问已发布端口的人。仅当您在前面有自己的身份验证层，或者在您完全控制的可信 LAN 上时，才启用它。
:::

不支持将仪表板作为单独的容器运行：其消息网关活跃度检测需要与消息网关进程共享 PID 命名空间。

## 交互式运行（CLI 聊天）

要针对正在运行的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者，如果您已经在运行的容器中打开了终端（例如通过 Docker Desktop），只需运行：

```sh
/opt/hermes/.venv/bin/hermes
```

## 持久化卷

`/opt/data` 卷是所有 Hermes 状态的单一事实来源。它映射到您宿主机上的 `~/.hermes/` 目录，包含：

| 路径 | 内容 |
|------|----------|
| `.env` | API 密钥和密钥 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 人格/身份 |
| `sessions/` | 对话历史 |
| `memories/` | 持久化记忆存储 |
| `skills/` | 已安装的技能 |
| `home/` | 用于 Hermes 工具子进程（`git`、`ssh`、`gh`、`npm` 和技能 CLI）的每个配置文件的 HOME |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

在 `~` 下存储凭据的技能 CLI 必须针对子进程 HOME 进行初始化，而不仅仅是数据卷根目录。例如，[xurl 技能](./skills/bundled/social-media/social-media-xurl.md) 将 OAuth 状态存储在 `~/.xurl` 中；在官方的 Docker 布局中，Hermes 工具调用将其读取为 `/opt/data/home/.xurl`，因此请使用 `HOME=/opt/data/home` 运行手动 xurl 身份验证，并使用 `HOME=/opt/data/home xurl auth status` 进行验证。

:::warning
切勿同时针对同一数据目录运行两个 Hermes **消息网关**容器 —— 会话文件和记忆存储并非为并发写入访问而设计。
:::

## 多配置文件支持

Hermes 支持[多个配置文件](../reference/profile-commands.md) —— 独立的 `~/.hermes/` 子目录，允许您从单个安装运行独立的 Agent（不同的灵魂、技能、记忆、会话、凭据）。**在官方 Docker 镜像内部，s6 监督树将每个配置文件视为一等监督服务**，因此推荐的部署方式是**一个容器托管所有配置文件**。

使用 `hermes profile create <name>` 创建的每个配置文件都会获得：

- 在 `/run/service/gateway-<name>/` 处的专用 s6 服务槽，由运行时动态注册 —— 无需重建容器。
- 崩溃时自动重启，由 `s6-supervise` 管理退避。
- 每个配置文件的轮换日志位于 `${HERMES_HOME}/logs/gateways/<name>/current`（10 个存档 × 每个 1 MB）。
- 跨容器重启的状态持久性：启动时协调器从每个配置文件目录读取 `gateway_state.json`，并仅将最后记录状态为 `running` 的配置文件的服务槽重新启动。已停止的配置文件保持停止状态。

您在宿主机上运行的生命周期命令在容器内部以相同方式工作：

```sh
# 创建配置文件 —— 注册 gateway-<name> s6 槽。
docker exec hermes hermes profile create coder

# 启动 / 停止 / 重启 —— 分派 s6-svc；消息网关生命周期在 docker restart 后仍然存在。
docker exec hermes hermes -p coder gateway start
docker exec hermes hermes -p coder gateway stop
docker exec hermes hermes -p coder gateway restart

# 状态 —— 在容器内部报告 `Manager: s6 (container supervisor)`。
docker exec hermes hermes -p coder gateway status

# 删除配置文件 —— 同时拆除 s6 槽。
docker exec hermes hermes profile delete coder
```

在底层，容器内的 `hermes gateway start/stop/restart` 会被拦截并路由到针对正确服务目录的 `s6-svc`；您不需要直接学习 s6 命令。要获取原始监督器状态，请使用 `/command/s6-svstat /run/service/gateway-<name>`（注意 `/command/` 仅在由监督树生成的进程的 PATH 上 —— 当从 `docker exec` 调用时，请传递绝对路径）。
### 为什么使用一个容器承载多个配置文件，而非多个容器

在迁移到 s6 之前，“每个配置文件一个容器”是推荐模式，因为当时容器内没有 supervisor 来管理多个消息网关。现在 s6 作为 PID 1，这不再是必须的，单容器布局在几乎所有维度上都更简单：

| | 一个容器，多个配置文件 | 每个配置文件一个容器 |
|---|---|---|
| 磁盘开销 | 一个镜像，一个捆绑的 venv，一个 Playwright 缓存 | N 个镜像 / N 个缓存 |
| 内存开销 | 共享的 Python 解释器缓存，共享的 node_modules | 每个容器重复 |
| 配置文件创建 | `docker exec ... hermes profile create <name>`（秒级） | 新的 `docker run` 调用 + 端口分配 + 绑定挂载配置 |
| 每个配置文件的崩溃恢复 | `s6-supervise` 自动重启 | Docker 的 `--restart unless-stopped`（较慢，会终止兄弟进程的工作） |
| 日志 | 通过 `s6-log` 为每个配置文件轮转文件，外加容器启动审计日志 | 每个容器使用 `docker logs <name>` —— 无内置轮转 |
| 备份 | 一个 `~/.hermes` 目录 | 需要协调 N 个目录 |

默认配置文件（`default`）在首次启动时总是被注册，因此一个全新的容器开箱即用就带有一个受监管的消息网关。额外的配置文件是纯运行时添加的。

### 何时确实需要单独的容器

容器内配置文件是默认模式。仅在你有特定原因时才为每个配置文件运行单独的容器：

- **每个工作负载的资源隔离** —— 例如，配置文件 A 中失控的浏览器工具会话不应导致配置文件 B 内存溢出。容器允许你为每个配置文件设置 `--memory` / `--cpus`。
- **独立的镜像固定** —— 每个工作负载使用不同的上游镜像标签。
- **网络分段** —— 每个配置文件使用不同的 Docker 网络（例如，一个面向客户，一个内部使用）。
- **合规性 / 爆炸半径** —— 不同的凭据从不共享操作系统级别的进程树。

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

[持久化卷](#persistent-volumes)中的警告仍然适用：切勿同时将两个容器指向同一个 `~/.hermes` 目录。每个容器内的 s6 supervisor 管理其自己的配置文件集；跨容器共享数据卷会损坏会话文件和记忆存储。

## 日志去向

s6 容器有四个不同的日志输出面，“为什么我的消息网关在 `docker logs` 中不显示任何内容”是一个常见的困惑。速查表：

| 来源 | 去向 | 如何读取 |
|---|---|---|
| **每个配置文件的消息网关**（`hermes gateway run` 以及 s6 下的每个配置文件网关） | 分流到两个地方：`docker logs <container>`（实时，无额外前缀）**以及** `${HERMES_HOME}/logs/gateways/<profile>/current`（轮转，ISO-8601 时间戳，10 个存档 × 每个 1 MB） | 在主机上使用 `docker logs -f hermes` 或 `tail -F ~/.hermes/logs/gateways/default/current` |
| **仪表盘**（当 `HERMES_DASHBOARD=1` 时） | `docker logs <container>`（无前缀） | `docker logs -f hermes` —— 与网关日志行交错 |
| **启动协调器**（记录每次容器启动时恢复了哪些配置文件网关） | `${HERMES_HOME}/logs/container-boot.log`（仅追加的审计日志） | `tail -F ~/.hermes/logs/container-boot.log` |
| **通用 Hermes 日志**（`agent.log`，`errors.log`） | `${HERMES_HOME}/logs/`（感知配置文件） | `docker exec hermes hermes logs --follow [--level WARNING] [--session <id>]` |

有两个值得了解的实际情况：

- `logs/gateways/<profile>/current` 处的文件副本在容器重启后仍然存在。`docker logs` 仅保留当前容器生命周期内的输出（并在 `docker rm` 时被清除）；轮转文件在绑定挂载的卷上持久化。
- 启动协调器的审计行格式为 `<iso-timestamp> profile=<name> prior_state=<state> action=<registered|started>`，因此快速执行 `grep profile=coder ~/.hermes/logs/container-boot.log` 可以显示给定配置文件上次恢复的时间以及 s6 是否自动启动了它。

## 环境变量转发

API 密钥从容器内的 `/opt/data/.env` 读取。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接的 `-e` 标志会覆盖 `.env` 中的值。这对于 CI/CD 或密钥管理器集成非常有用，因为你不想将密钥存储在磁盘上。

:::note 在寻找 Docker 作为**终端后端**吗？
本页介绍在 Docker 内部运行 Hermes 本身。如果你希望 Hermes 在 Docker 沙盒容器内执行 Agent 的 `terminal` / `execute_code` 调用（一个跨 Hermes 进程共享的长生命周期容器 —— 参见 issue #20561），那是另一个独立的配置块 —— `terminal.backend: docker` 加上 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_env`、`terminal.docker_run_as_host_user`、`terminal.docker_extra_args`、`terminal.docker_persist_across_processes` 和 `terminal.docker_orphan_reaper`。完整的配置集（包括容器生命周期规则）请参见[配置 → Docker 后端](configuration.md#docker-backend)。
:::

## Docker Compose 示例

对于同时包含消息网关和仪表盘的持久化部署，使用 `docker-compose.yaml` 很方便：

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
首先执行 `docker compose up -d`，然后使用 `docker compose logs -f` 查看日志。受监管的消息网关的 stdout 也会被 tee 到卷上的 `${HERMES_HOME}/logs/gateways/<profile>/current` 文件 —— 完整的路由映射请参见 [日志存放位置](#where-the-logs-go)。

## 可选：Linux 桌面音频桥接

Docker 中的语音模式需要两个独立的部分才能工作：必须允许 Hermes 在容器内探测音频设备，并且容器必须能够访问您主机的音频服务器。以下设置适用于暴露 PulseAudio 兼容套接字的 Linux 桌面（包括许多 PipeWire 设置），涵盖了主机音频的管道配置。

:::caution
这是一个 Linux 桌面解决方案，并非 Docker Desktop 的通用功能。当您的主机音频已经正常工作，并且希望在 Hermes 容器内使用 CLI 语音模式时，此方法很有用。如果 Hermes 仍然报告 `Running inside Docker container -- no audio devices`，请使用包含对 `PULSE_SERVER` / `PIPEWIRE_REMOTE` 的 Docker 音频探测支持的构建版本。
:::

首先，在您的 Compose 文件旁边创建一个 ALSA 配置：

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

然后构建一个安装了 ALSA PulseAudio 插件的小型衍生镜像：

```dockerfile title="Dockerfile.audio"
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends libasound2-plugins \
    && rm -rf /var/lib/apt/lists/*
```

在 Compose 中使用该镜像，并透传主机用户的 PulseAudio 套接字和 cookie：

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

使用您的主机 UID/GID 启动它，以便容器进程可以访问每个用户的音频套接字：

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

浏览器自动化（Playwright/Chromium）是最耗内存的功能。如果不需要浏览器工具，1 GB 就足够了。如果浏览器工具处于活动状态，请至少分配 2 GB。

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
- **`docker-cli`** —— 以便在容器内运行的 Agent 可以驱动主机的 Docker 守护进程（通过绑定挂载 `/var/run/docker.sock` 来选择加入），用于 `docker build`、`docker run`、容器检查等。
- **`openssh-client`** —— 启用容器内的 [SSH 终端后端](/user-guide/configuration#ssh-backend)。SSH 后端会调用系统的 `ssh` 二进制文件；没有这个，它在容器化安装中会静默失败。
- WhatsApp 桥接 (`scripts/whatsapp-bridge/`)
- **[`s6-overlay`](https://github.com/just-containers/s6-overlay) v3** 作为 PID 1（替换了旧的 `tini`）—— 监管仪表板和每个配置文件的网关，在崩溃时自动重启，回收僵尸子进程，并转发信号。

容器的 `ENTRYPOINT` 是 s6-overlay 的 `/init`。启动时它会：
1. 以 root 身份运行 `/etc/cont-init.d/01-hermes-setup` (= `docker/stage2-hook.sh`)：可选的 UID/GID 重新映射，修复卷所有权，在首次启动时生成 `.env` / `config.yaml` / `SOUL.md`，运行非交互式配置模式迁移（除非设置了 `HERMES_SKIP_CONFIG_MIGRATION=1`），同步捆绑的技能。
2. 运行 `/etc/cont-init.d/02-reconcile-profiles` (= `hermes_cli.container_boot`)：遍历 `$HERMES_HOME/profiles/<name>/`，在 `/run/service/gateway-<profile>/` 下重新创建每个配置文件的网关 s6 服务槽，并仅自动启动那些最后记录状态为 `running` 的网关（参见 [每个配置文件的网关监管](#per-profile-gateway-supervision)）。
3. 启动静态的 `main-hermes` 和 `dashboard` s6-rc 服务。
4. 将容器的 CMD 作为主程序执行 (`/opt/hermes/docker/main-wrapper.sh`)，该程序将用户传递给 `docker run` 的参数进行路由：
   - 无参数 → `hermes`（默认）
   - 第一个参数是 PATH 上的可执行文件（例如 `sleep`、`bash`）→ 直接执行它
   - 其他任何情况 → `hermes <args>`（子命令透传）
   当这个主程序退出时，容器也随之退出，并返回其退出码。

:::warning 与 pre-s6 镜像的破坏性变更
容器 ENTRYPOINT 现在是 `/init` (s6-overlay)，而不是 `/usr/bin/tini`。所有五种文档化的 `docker run` 调用模式（无参数、`chat -q "…"`、`sleep infinity`、`bash`、`--tui`）的行为都与基于 tini 的镜像相同。如果您有一个下游包装器依赖于 tini 特定的信号行为或硬编码的 `/usr/bin/tini --` 调用，请固定到之前的镜像标签。
:::
:::warning 权限模型
除非在命令链中保留 `/init`（或等效的旧版 `docker/entrypoint.sh` 垫片，它会转发到 stage2 钩子），否则不要覆盖镜像入口点。s6-overlay 的 `/init` 以 root 身份运行，以便在首次启动时更改卷的所有权，然后通过 `s6-setuidgid` 为每个受监督的服务以及主程序切换到 `hermes` 用户。在官方镜像中以 root 身份启动 `hermes gateway run` 默认会被拒绝，因为它可能在 `/opt/data` 中留下 root 拥有的文件，并破坏后续仪表板或消息网关的启动。仅当您有意接受该风险时，才设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。
:::

### `docker exec` 自动切换到 `hermes` 用户

`docker exec hermes <cmd>` 默认在容器内以 root 身份运行，但镜像在 `/opt/hermes/bin/hermes`（PATH 中最早的位置）提供了一个薄垫片，用于检测 root 调用者并通过 `s6-setuidgid hermes` 透明地重新执行。因此，`docker exec hermes login`、`docker exec hermes profile create …`、`docker exec hermes setup` 等命令都会写入 UID 10000 拥有的文件（即可被受监督的消息网关读取），无需额外的 `--user` 标志。非 root 调用者（受监督的进程本身、`docker exec --user hermes`、容器内的看板子 Agent）会触发短路，直接执行虚拟环境二进制文件，因此在热路径上没有开销。

如果您特别需要保留 root 语义的 `docker exec`（诊断会话、检查仅 root 可访问的状态、root 恰好拥有的 `/opt/data` 之外的文件），请按调用选择退出：

```sh
docker exec -e HERMES_DOCKER_EXEC_AS_ROOT=1 hermes <cmd>
```

垫片接受 `1` / `true` / `yes`（不区分大小写）。任何其他值（包括拼写错误如 `=0`）都会回退到切换用户，因此无法静默选择退出。如果 `s6-setuidgid` 不可用（自定义构建移除了 s6-overlay），垫片会拒绝以 root 身份运行并以退出码 126 退出，大声地暴露损坏的权限模型，而不是退回到历史遗留的隐患模式，即 `docker exec hermes login` 会以 `root:root` 身份写入 `auth.json`，并在每次聊天平台消息时破坏受监督消息网关的身份验证。

### 按配置文件的消息网关监督

使用 `hermes profile create <name>` 创建的每个配置文件都会自动在 `/run/service/gateway-<name>/` 注册一个 s6 监督的消息网关服务，并在容器重启时保持状态持久化并自动重启。有关面向用户的工作流和生命周期命令，请参阅上文的[多配置文件支持](#multi-profile-support)。

**相比 s6 之前的镜像，监督的优势：**

- 消息网关崩溃后，`s6-supervise` 会在约 1 秒退避后自动重启。
- 当通过 `HERMES_DASHBOARD=1` 启用仪表板时，仪表板在同一监督树上受监督，并获得相同的自动重启处理。
- `docker restart` 会保留正在运行的消息网关：cont-init 协调器读取 `$HERMES_HOME/profiles/<name>/gateway_state.json`，如果最后记录的状态是 `running`，则重新启动该槽位。已停止的消息网关保持停止状态。
- 按配置文件的消息网关日志持久保存在 `$HERMES_HOME/logs/gateways/<profile>/current` 下（由 `s6-log` 轮转），协调器的操作会在每次启动时追加到 `$HERMES_HOME/logs/container-boot.log`。有关完整路由映射，请参阅[日志去向](#where-the-logs-go)。

容器内的 `hermes status` 会报告 `Manager: s6 (container supervisor)`。使用 `/command/s6-svstat /run/service/gateway-<name>` 查看原始监督器视图（注意 `/command/` 仅对监督树进程在 PATH 中；从 `docker exec` 调用时传递绝对路径）。

## 升级

拉取最新镜像并重新创建容器。您的数据目录将被保留，容器在启动消息网关之前会对挂载的 `$HERMES_HOME/config.yaml` 运行非交互式配置模式迁移。当需要迁移时，Hermes 会先在 `config.yaml` 和 `.env` 旁边写入带时间戳的备份。

```sh
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

或使用 Docker Compose：

```sh
docker compose pull
docker compose up -d
```

仅当您需要在让新镜像重写持久化配置之前手动检查或迁移时，才设置 `HERMES_SKIP_CONFIG_MIGRATION=1`。

## 技能和凭证文件

当使用 Docker 作为执行环境时（不是上述方法，而是当 Agent 在 Docker 沙盒内运行命令时——参见[配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用重用单个长期存在的容器，并自动将技能目录（`~/.hermes/skills/`）和技能声明的任何凭证文件作为只读卷绑定挂载到该容器中。技能脚本、模板和引用在沙盒内可用，无需手动配置，并且由于容器在 Hermes 进程的生命周期内持续存在，您安装的任何依赖项或写入的任何文件都会保留到下一次工具调用。

SSH 和 Modal 后端也会发生相同的同步——技能和凭证文件会在每个命令之前通过 rsync 或 Modal 挂载 API 上传。

## 在容器中安装更多工具

官方镜像附带了一套精选的实用工具（参见[Dockerfile 的作用](#what-the-dockerfile-does)），但并非每个 Agent 可能需要的工具都已预安装。有五种推荐的方法，按工作量和持久性递增排序。

### npm 或 Python 工具——使用 `npx` 或 `uvx`

对于发布到 npm 或 PyPI 的任何工具，指示 Hermes 通过 `npx`（npm）或 `uvx`（Python）运行它，并将该命令保存在其持久记忆中。如果工具需要配置文件或凭证，指示它将这些文件放在 `/opt/data` 下（例如 `/opt/data/<tool>/config.yaml`）。

依赖项按需获取，并在容器的生命周期内缓存。写入 `/opt/data` 下的配置在容器重启后仍然存在，因为它位于绑定挂载的主机目录中。包缓存本身在 `docker rm` 后重建，但 `npx` 和 `uvx` 会在下次工具运行时透明地重新获取。
### 其他工具（apt 包、二进制文件）—— 安装并记住

对于 npm 或 PyPI 之外的任何内容 —— `apt` 包、预编译的二进制文件、镜像中未包含的语言运行时 —— 指示 Hermes 如何安装它（例如 `apt-get update && apt-get install -y <package>`）并告诉它记住安装命令。该工具在容器的剩余生命周期内持续存在，当 Hermes 下次需要该工具时，会在容器重启后重新运行安装命令。

这适用于安装快速且偶尔使用的工具。对于经常使用的工具，请优先考虑下一种方法。

### 持久化安装 —— 构建派生镜像

当某个工具必须在每次容器启动时立即可用，且无需重新安装延迟时，请构建一个继承自 `nousresearch/hermes-agent` 并安装该工具的新镜像层：

```dockerfile
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends <your-package> \
    && rm -rf /var/lib/apt/lists/*
USER hermes
```

构建它并用它代替官方镜像：

```sh
docker build -t my-hermes:latest .
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  my-hermes:latest gateway run
```

入口点脚本和 `/opt/data` 的语义保持不变地继承，因此本页其余部分仍然适用。请记住，在拉取更新的上游 `nousresearch/hermes-agent` 时，要重新构建镜像。

### 复杂工具或多服务栈 —— 运行 Sidecar 容器

对于自带服务（数据库、Web 服务器、队列、无头浏览器集群）或过于庞大而无法放在 Hermes 容器内的工具，请在共享的 Docker 网络上将它们作为单独的容器运行。Hermes 通过容器名称访问 Sidecar，就像它访问本地推理服务器一样（参见 [连接到本地推理服务器](#连接到本地推理服务器-vllm-ollama-等)）。

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

在 Hermes 容器内部，可以通过 `http://my-tool:<port>`（或其服务的任何协议）访问 Sidecar。这种模式使每个服务的生命周期、资源限制和升级节奏保持独立，并避免了 Hermes 镜像因仅被一个工具需要的依赖项而变得臃肿。

### 广泛有用的工具 —— 提交 Issue 或 Pull Request

如果一个工具可能对大多数 Hermes Agent 用户有用，请考虑将其贡献给上游，而不是在私有的派生镜像中维护。在 [hermes-agent 仓库](https://github.com/NousResearch/hermes-agent) 上提交 Issue 或 Pull Request，描述该工具及其用例。捆绑到官方镜像中的工具将使每个用户受益，并避免下游分叉的维护开销。

## 连接到本地推理服务器（vLLM、Ollama 等）

当在 Docker 中运行 Hermes，并且你的推理服务器（vLLM、Ollama、text-generation-inference 等）也在主机或另一个容器中运行时，网络连接需要特别注意。

### Docker Compose（推荐）

将两个服务放在同一个 Docker 网络上。这是最可靠的方法：

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

然后在你的 `~/.hermes/config.yaml` 中，使用 **容器名称** 作为主机名：

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::tip 关键点
- 使用 **容器名称** (`vllm`) 作为主机名 —— 而不是 `localhost` 或 `127.0.0.1`，它们指的是 Hermes 容器本身。
- `model` 值必须与你传递给 vLLM 的 `--served-model-name` 匹配。
- 将 `api_key` 设置为任何非空字符串（vLLM 需要该请求头，但默认不验证它）。
- 在 `base_url` 中 **不要** 包含尾部斜杠。
:::

### 独立的 Docker run（无 Compose）

如果你的推理服务器直接在主机上运行（不在 Docker 中），在 macOS/Windows 上使用 `host.docker.internal`，或在 Linux 上使用 `--network host`：

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

:::warning 使用 `--network host` 时，`-p` 标志会被忽略 —— 所有容器端口都直接暴露在主机上。
:::

### 验证连通性

从 Hermes 容器内部，确认推理服务器可达：

```sh
docker exec hermes curl -s http://vllm:8000/v1/models
```

你应该能看到一个 JSON 响应，列出你服务的模型。如果失败，请检查：

1.  两个容器是否在同一个 Docker 网络上 (`docker network inspect hermes-net`)
2.  推理服务器是否在监听 `0.0.0.0`，而不是 `127.0.0.1`
3.  端口号是否匹配
### Ollama

Ollama 的配置方式相同。如果 Ollama 运行在宿主机上，请使用 `host.docker.internal:11434`（macOS/Windows）或 `127.0.0.1:11434`（Linux 配合 `--network host` 参数）。如果 Ollama 运行在同一个 Docker 网络中的独立容器内：

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
- 缺少或无效的 `.env` 文件 — 请先以交互模式运行以完成设置
- 如果使用暴露端口运行，可能存在端口冲突

### "Permission denied" 错误

容器的 stage2 hook 通过每个受监管服务内的 `s6-setuidgid` 将权限降级为非 root 的 `hermes` 用户（UID 10000）。如果你的宿主机 `~/.hermes/` 目录属于不同的 UID，请设置 `HERMES_UID`/`HERMES_GID`（或其别名 `PUID`/`PGID`，以保持与 LinuxServer.io 和 NAS 镜像的兼容性）以匹配你的宿主机用户，或者确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

在 NAS（UGOS、Synology、unRAID）上，数据目录通常是**绑定挂载**，其所有者是容器无法 `chown` 的宿主机 UID。请设置 `PUID`/`PGID`（或 `HERMES_UID`/`HERMES_GID`）为该宿主机用户，这样运行时将以挂载点的所有者身份运行，而不是 UID 10000：

```sh
docker run -d \
  --name hermes \
  -e PUID=1000 -e PGID=10 \
  -v /volume1/docker/hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

`docker exec hermes <cmd>` 也会自动降级到 UID 10000 — 详情及每次调用的退出选项，请参见 [`docker exec` 自动降级到 `hermes` 用户](#docker-exec-automatically-drops-to-the-hermes-user)。

### 浏览器工具无法工作

Playwright 需要共享内存。在你的 Docker run 命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络问题后消息网关无法重连

`--restart unless-stopped` 标志可以处理大多数瞬时故障。如果消息网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状况

```sh
docker logs --tail 50 hermes          # 最近日志
docker run -it --rm nousresearch/hermes-agent:latest version     # 验证版本
docker stats hermes                    # 资源使用情况
```