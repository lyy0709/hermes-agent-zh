---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent 以及使用 Docker 作为终端后端"
---

# Hermes Agent — Docker

Docker 与 Hermes Agent 有两种不同的交互方式：

1. **在 Docker 中运行 Hermes** — Agent 本身在容器内运行（本页主要关注此方式）
2. **Docker 作为终端后端** — Agent 在宿主机上运行，但每个命令都在一个持久化的 Docker 沙盒容器内执行，该容器在 Hermes 进程的生命周期内（跨越工具调用、`/new` 和子 Agent）持续存在（参见 [配置 → Docker 后端](./configuration.md#docker-backend)）

本页涵盖选项 1。该容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在从宿主机挂载到 `/opt/data` 的单个目录中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

## 快速开始

如果你是第一次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器来运行设置向导：

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将使你进入设置向导，它会提示你输入 API 密钥并将其写入 `~/.hermes/.env`。你只需要执行一次此操作。强烈建议在此步骤中为消息网关设置一个聊天系统。

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

注意：API 服务器的启用取决于 `API_SERVER_ENABLED=true`。要在容器内部将其暴露给 `127.0.0.1` 之外，还需设置 `API_SERVER_HOST=0.0.0.0` 和一个 `API_SERVER_KEY`（至少 8 个字符 — 使用 `openssl rand -hex 32` 生成一个）。示例：

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

内置的 Web 仪表板作为可选的辅助进程，在与网关相同的容器内运行。设置 `HERMES_DASHBOARD=1` 以默认在容器环回地址 (`127.0.0.1`) 上运行仪表板：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -e HERMES_DASHBOARD=1 \
  nousresearch/hermes-agent gateway run
```

入口点在 `exec` 执行主命令之前，会在后台启动 `hermes dashboard`（以非 root 用户 `hermes` 运行）。仪表板的输出在 `docker logs` 中带有 `[dashboard]` 前缀，便于与网关日志区分。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）以在主命令旁启动仪表板 | *(未设置 — 仪表板不启动)* |
| `HERMES_DASHBOARD_HOST` | 仪表板 HTTP 服务器的绑定地址 | `127.0.0.1` |
| `HERMES_DASHBOARD_PORT` | 仪表板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_TUI` | 设置为 `1` 以暴露浏览器内的聊天标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`） | *(未设置)* |

默认情况下，仪表板保持在环回地址上，以避免将未经身份验证的 Web 界面暴露在网络上。若要故意发布它，请设置 `HERMES_DASHBOARD_HOST=0.0.0.0` 并配置你自己的可信网络边界/反向代理。在这种情况下，你必须通过在命令路径中传递主机/标志来显式添加 `--insecure` 行为（入口点不再自动启用不安全模式）。

:::note
仪表板在容器内作为受监督的 s6 服务运行。如果仪表板进程崩溃，s6-overlay 会在短暂退避后自动重启它 — 你将看到新的 PID，而无需重启容器。日志和崩溃输出可通过 `docker logs <容器>` 查看（s6 将服务的 stdout/stderr 转发到那里）。

不支持将仪表板作为单独的容器运行：其网关存活检测要求与网关进程共享 PID 命名空间。
:::

## 交互式运行（CLI 聊天）

要针对正在运行的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者，如果你已经在运行的容器中打开了终端（例如通过 Docker Desktop），只需运行：

```sh
/opt/hermes/.venv/bin/hermes
```

## 持久化卷

`/opt/data` 卷是所有 Hermes 状态的单一事实来源。它映射到宿主机的 `~/.hermes/` 目录，包含：

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

在 `~` 下存储凭据的技能 CLI 必须针对子进程 HOME 进行初始化，而不仅仅是数据卷根目录。例如，[xurl 技能](./skills/bundled/social-media/social-media-xurl.md) 将 OAuth 状态存储在 `~/.xurl` 中；在官方的 Docker 布局中，Hermes 工具调用将其读取为 `/opt/data/home/.xurl`，因此请使用 `HOME=/opt/data/home` 运行手动 xurl 认证，并使用 `HOME=/opt/data/home xurl auth status` 进行验证。
:::warning
切勿同时运行两个 Hermes **消息网关**容器访问同一数据目录——会话文件和记忆存储不支持并发写入访问。
:::

## 多配置文件支持

Hermes 支持[多配置文件](../reference/profile-commands.md)——独立的 `~/.hermes/` 目录，允许您从单一安装运行独立的 Agent（不同的灵魂、技能、记忆、会话、凭证）。**在 Docker 下运行时，不建议使用 Hermes 内置的多配置文件功能。**

相反，推荐的模式是**每个配置文件对应一个容器**，每个容器将其自己的主机目录绑定挂载为 `/opt/data`：

```sh
# 工作配置文件
docker run -d \
  --name hermes-work \
  --restart unless-stopped \
  -v ~/.hermes-work:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run

# 个人配置文件
docker run -d \
  --name hermes-personal \
  --restart unless-stopped \
  -v ~/.hermes-personal:/opt/data \
  -p 8643:8642 \
  nousresearch/hermes-agent gateway run
```

为什么在 Docker 中推荐使用独立容器而非配置文件：

- **隔离性**——每个容器拥有自己的文件系统、进程表和资源限制。一个配置文件中的崩溃、依赖项更改或失控会话不会影响另一个。
- **独立生命周期**——可以单独升级、重启、暂停或回滚每个 Agent（`docker restart hermes-work` 不会影响 `hermes-personal`）。
- **清晰的端口和网络分离**——每个消息网关绑定自己的主机端口；聊天平台或 API 服务器之间不存在串扰风险。
- **更简单的思维模型**——容器*即*配置文件。备份、迁移和权限都遵循绑定挂载的目录，无需记忆额外的 `--profile` 标志。
- **避免并发写入风险**——上述关于切勿运行两个消息网关访问同一数据目录的警告，同样适用于单个容器内的配置文件。

在 Docker Compose 中，这仅意味着为每个配置文件声明一个服务，并指定不同的 `container_name`、`volumes` 和 `ports`：

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

## 环境变量转发

API 密钥从容器内的 `/opt/data/.env` 文件中读取。您也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接的 `-e` 标志会覆盖 `.env` 文件中的值。这对于 CI/CD 或密钥管理器集成非常有用，因为您不希望密钥存储在磁盘上。

:::note 正在寻找作为**终端后端**的 Docker？
本页介绍在 Docker 内部运行 Hermes 本身。如果您希望 Hermes 在 Docker 沙盒容器（每个 Hermes 进程一个持久容器）内执行 Agent 的 `terminal` / `execute_code` 调用，那是另一个独立的配置块——`terminal.backend: docker` 加上 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_run_as_host_user` 和 `terminal.docker_extra_args`。完整配置请参见[配置 → Docker 后端](configuration.md#docker-backend)。
:::

## Docker Compose 示例

对于需要同时运行消息网关和仪表盘的持久化部署，使用 `docker-compose.yaml` 非常方便：

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"   # 消息网关 API
      - "9119:9119"   # 仪表盘（仅在 HERMES_DASHBOARD=1 时可达）
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_DASHBOARD=1
      # 取消注释以转发特定环境变量，而非使用 .env 文件：
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```

使用 `docker compose up -d` 启动，使用 `docker compose logs -f` 查看日志。仪表盘输出以 `[dashboard]` 为前缀，因此很容易从消息网关日志中过滤出来。

## 可选：Linux 桌面音频桥接

Docker 中的语音模式需要两个独立的部分才能工作：必须允许 Hermes 探测容器内的音频设备，并且容器必须能够访问您的主机音频服务器。以下设置适用于暴露 PulseAudio 兼容套接字的 Linux 桌面（包括许多 PipeWire 设置）的主机音频管道。

:::caution
这是一个 Linux 桌面解决方案，并非通用的 Docker Desktop 功能。当您的主机音频已经正常工作，并且希望在 Hermes 容器内使用 CLI 语音模式时，此方法非常有用。如果 Hermes 仍然报告 `Running inside Docker container -- no audio devices`，请使用包含 Docker 音频探测支持（针对 `PULSE_SERVER` / `PIPEWIRE_REMOTE`）的构建版本。
:::

首先，在 Compose 文件旁边创建一个 ALSA 配置：

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
使用您的主机 UID/GID 启动，以便容器进程可以访问每用户的音频套接字：

```sh
export HERMES_UID="$(id -u)"
export HERMES_GID="$(id -g)"
docker compose up -d --build
```

要验证容器内 PortAudio 看到的内容：

```sh
docker exec hermes /opt/hermes/.venv/bin/python -c "import sounddevice as sd; print(sd.query_devices())"
```

## 资源限制

Hermes 容器需要中等资源。推荐的最低配置：

| 资源 | 最低 | 推荐 |
|----------|---------|-------------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核心 | 2 核心 |
| 磁盘（数据卷） | 500 MB | 2+ GB（随会话/技能增长） |

浏览器自动化（Playwright/Chromium）是最耗内存的功能。如果不需要浏览器工具，1 GB 足够。如果浏览器工具处于活动状态，请分配至少 2 GB。

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

- Python 3 及所有 Hermes 依赖项 (`uv pip install -e ".[all]"`)
- Node.js + npm（用于浏览器自动化和 WhatsApp 桥接）
- Playwright 与 Chromium (`npx playwright install --with-deps chromium --only-shell`)
- ripgrep、ffmpeg、git 和 `xz-utils` 作为系统工具
- **`docker-cli`** — 以便在容器内运行的 Agent 可以驱动主机的 Docker 守护进程（通过绑定挂载 `/var/run/docker.sock` 来选择启用），用于 `docker build`、`docker run`、容器检查等。
- **`openssh-client`** — 启用容器内的 [SSH 终端后端](/user-guide/configuration#ssh-backend)。SSH 后端会调用系统的 `ssh` 二进制文件；没有这个，它在容器化安装中会静默失败。
- WhatsApp 桥接 (`scripts/whatsapp-bridge/`)
- **[`s6-overlay`](https://github.com/just-containers/s6-overlay) v3** 作为 PID 1（取代了旧的 `tini`）— 监督仪表板和每个配置文件的网关，在崩溃时自动重启，回收僵尸子进程，并转发信号。

容器的 `ENTRYPOINT` 是 s6-overlay 的 `/init`。启动时它会：
1. 以 root 身份运行 `/etc/cont-init.d/01-hermes-setup`（即 `docker/stage2-hook.sh`）：可选的 UID/GID 重新映射，修复卷所有权，在首次启动时生成 `.env` / `config.yaml` / `SOUL.md`，同步捆绑的技能。
2. 运行 `/etc/cont-init.d/02-reconcile-profiles`（即 `hermes_cli.container_boot`）：遍历 `$HERMES_HOME/profiles/<name>/`，在 `/run/service/gateway-<profile>/` 下重新创建每个配置文件的网关 s6 服务槽，并仅自动启动那些最后记录状态为 `running` 的网关（参见[每个配置文件的网关监督](#per-profile-gateway-supervision)）。
3. 启动静态的 `main-hermes` 和 `dashboard` s6-rc 服务。
4. 将容器的 CMD 作为主程序执行 (`/opt/hermes/docker/main-wrapper.sh`)，该程序将用户传递给 `docker run` 的参数路由：
   - 无参数 → `hermes`（默认）
   - 第一个参数是 PATH 上的可执行文件（例如 `sleep`、`bash`）→ 直接执行它
   - 其他任何情况 → `hermes <args>`（子命令透传）
   当这个主程序退出时，容器退出，并返回其退出代码。

:::warning 与 pre-s6 镜像的破坏性变更
容器 ENTRYPOINT 现在是 `/init`（s6-overlay），而不是 `/usr/bin/tini`。所有五种文档化的 `docker run` 调用模式（无参数、`chat -q "…"`、`sleep infinity`、`bash`、`--tui`）的行为都与基于 tini 的镜像相同。如果您有一个依赖于 tini 特定信号行为或硬编码 `/usr/bin/tini --` 调用的下游包装器，请固定到之前的镜像标签。
:::

:::warning 权限模型
除非您在命令链中保留 `/init`（或者等效地，保留将请求转发到 stage2 钩子的旧版 `docker/entrypoint.sh` 垫片），否则不要覆盖镜像入口点。s6-overlay 的 `/init` 以 root 身份运行，以便在首次启动时可以更改卷的所有权，然后通过 `s6-setuidgid` 为每个受监督的服务以及主程序切换到 `hermes` 用户。在官方镜像内以 root 身份启动 `hermes gateway run` 默认会被拒绝，因为它可能会在 `/opt/data` 中留下 root 拥有的文件，并破坏后续的仪表板或网关启动。仅在您有意接受该风险时设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。
:::

### 每个配置文件的网关监督

在容器内部，使用 `hermes profile create <name>` 创建的每个配置文件会自动在 `/run/service/gateway-<name>/` 下注册一个 s6 监督的网关服务。您在主机上运行的生命周期命令以相同的方式工作：

```sh
hermes profile create coder            # 注册 gateway-coder s6 槽位
hermes -p coder gateway start          # s6-svc -u  → 受监督的网关
hermes -p coder gateway stop           # s6-svc -d  → 服务停止
hermes -p coder gateway restart        # s6-svc -t  → 向监督进程发送 SIGTERM
hermes profile delete coder            # 拆除 s6 槽位
```

**相较于 pre-s6 镜像的监督优势：**

- 网关崩溃后，`s6-supervise` 会在约 1 秒退避后自动重启。
- 仪表板崩溃后自动重启（设置 `HERMES_DASHBOARD=1` 以启动它）。
- `docker restart` 会保留正在运行的网关：cont-init 协调器读取 `$HERMES_HOME/profiles/<name>/gateway_state.json`，如果最后记录的状态是 `running`，则重新启动该槽位。已停止的网关保持停止状态。
- 每个配置文件的网关日志持久保存在 `$HERMES_HOME/logs/gateways/<profile>/current` 下（由 `s6-log` 轮换），并且协调器的操作在每次启动时追加到 `$HERMES_HOME/logs/container-boot.log`。

容器内的 `hermes status` 报告 `Manager: s6 (container supervisor)`。使用 `/command/s6-svstat /run/service/gateway-<name>` 查看原始监督器视图（注意 `/command/` 仅在监督树进程的 PATH 上；从 `docker exec` 调用时传递绝对路径）。

## 升级

拉取最新镜像并重新创建容器。您的数据目录保持不变。

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

当使用 Docker 作为执行环境时（不是上述方法，而是当 Agent 在 Docker 沙盒内运行命令时——参见[配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用重用单个长期运行的容器，并自动将技能目录（`~/.hermes/skills/`）和技能声明的任何凭证文件作为只读卷绑定挂载到该容器中。技能脚本、模板和引用在沙盒内可用，无需手动配置，并且由于容器在 Hermes 进程的生命周期内持续存在，您安装的任何依赖项或写入的任何文件都会保留到下一次工具调用。

SSH 和 Modal 后端也会发生相同的同步——技能和凭证文件会在每个命令执行前通过 rsync 或 Modal 挂载 API 上传。

## 在容器中安装更多工具

官方镜像附带了一套精选的实用工具（参见[Dockerfile 的作用](#what-the-dockerfile-does)），但并非 Agent 可能需要的每个工具都已预装。有五种推荐的方法，按工作量和持久性递增排序。

### npm 或 Python 工具——使用 `npx` 或 `uvx`

对于发布到 npm 或 PyPI 的任何工具，指示 Hermes 通过 `npx`（npm）或 `uvx`（Python）运行它，并将该命令存储在其持久记忆中。如果工具需要配置文件或凭证，指示它将这些文件放在 `/opt/data` 下（例如 `/opt/data/<tool>/config.yaml`）。

依赖项按需获取，并在容器的生命周期内缓存。写入 `/opt/data` 下的配置在容器重启后仍然存在，因为它位于绑定挂载的主机目录上。包缓存本身在 `docker rm` 后重建，但 `npx` 和 `uvx` 会在下次运行工具时透明地重新获取。

### 其他工具（apt 包、二进制文件）——安装并记住

对于 npm 或 PyPI 之外的任何工具——`apt` 包、预构建的二进制文件、镜像中未包含的语言运行时——指示 Hermes 如何安装它（例如 `apt-get update && apt-get install -y <package>`），并告诉它记住安装命令。该工具在容器的剩余生命周期内持续存在，当 Hermes 下次需要该工具时，会在容器重启后重新运行安装命令。

这适用于安装快速且偶尔使用的工具。对于经常使用的工具，请优先考虑下一种方法。

### 持久化安装——构建派生镜像

当某个工具必须在每次容器启动时立即可用，且无需重新安装延迟时，构建一个继承自 `nousresearch/hermes-agent` 并在层中安装该工具的新镜像：

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

入口点脚本和 `/opt/data` 语义保持不变地继承，因此本页其余部分仍然适用。请记住，在拉取更新的上游 `nousresearch/hermes-agent` 时，要重新构建镜像。

### 复杂工具或多服务栈——运行 Sidecar 容器

对于自带服务（数据库、Web 服务器、队列、无头浏览器集群）或太重而无法放在 Hermes 容器内的工具，请在共享的 Docker 网络上将它们作为单独的容器运行。Hermes 通过容器名称访问 Sidecar，就像它访问本地推理服务器一样（参见[连接到本地推理服务器](#connecting-to-local-inference-servers-vllm-ollama-etc)）。

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

在 Hermes 容器内部，Sidecar 可以通过 `http://my-tool:<port>`（或它服务的任何协议）访问。这种模式使每个服务的生命周期、资源限制和升级节奏保持独立，并避免 Hermes 镜像因仅被一个工具需要的依赖项而臃肿。

### 广泛有用的工具——提交 Issue 或 Pull Request

如果一个工具可能对大多数 Hermes Agent 用户有用，请考虑将其贡献给上游，而不是在私有派生镜像中携带。在 [hermes-agent 仓库](https://github.com/NousResearch/hermes-agent) 上提交 Issue 或 Pull Request，描述该工具及其用例。捆绑到官方镜像中的工具将使每个用户受益，并避免下游分叉的维护开销。

## 连接到本地推理服务器（vLLM、Ollama 等）

当在 Docker 中运行 Hermes，并且您的推理服务器（vLLM、Ollama、text-generation-inference 等）也在主机或另一个容器中运行时，网络需要特别注意。

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
然后在你的 `~/.hermes/config.yaml` 中，使用**容器名称**作为主机名：

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::tip 关键点
- 使用**容器名称** (`vllm`) 作为主机名 —— 而不是 `localhost` 或 `127.0.0.1`，它们指的是 Hermes 容器本身。
- `model` 值必须与你传递给 vLLM 的 `--served-model-name` 匹配。
- 将 `api_key` 设置为任何非空字符串（vLLM 需要该请求头，但默认不验证它）。
- 不要在 `base_url` 中包含尾部斜杠。
:::

### 独立的 Docker 运行（无 Compose）

如果你的推理服务器直接运行在宿主机上（不在 Docker 中），在 macOS/Windows 上使用 `host.docker.internal`，或在 Linux 上使用 `--network host`：

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

:::warning 使用 `--network host` 时，`-p` 标志会被忽略 —— 所有容器端口都直接暴露在宿主机上。
:::

### 验证连接性

从 Hermes 容器内部，确认推理服务器可达：

```sh
docker exec hermes curl -s http://vllm:8000/v1/models
```

你应该能看到一个 JSON 响应，列出你提供的模型。如果失败，请检查：

1. 两个容器是否在同一个 Docker 网络上 (`docker network inspect hermes-net`)
2. 推理服务器是否在监听 `0.0.0.0`，而不是 `127.0.0.1`
3. 端口号是否匹配

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
- 缺少或无效的 `.env` 文件 —— 首先以交互方式运行以完成设置
- 如果运行时有暴露端口，可能存在端口冲突

### "Permission denied" 错误

容器的 stage2 hook 通过每个受监督服务内部的 `s6-setuidgid` 将权限降级为非 root 用户 `hermes`（UID 10000）。如果你的宿主机 `~/.hermes/` 属于不同的 UID，请设置 `HERMES_UID`/`HERMES_GID` 以匹配你的宿主机用户，或者确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

### 浏览器工具不工作

Playwright 需要共享内存。在你的 Docker run 命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络问题后消息网关未重新连接

`--restart unless-stopped` 标志处理大多数瞬时故障。如果消息网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状况

```sh
docker logs --tail 50 hermes          # 最近日志
docker run -it --rm nousresearch/hermes-agent:latest version     # 验证版本
docker stats hermes                    # 资源使用情况
```