---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent 以及使用 Docker 作为终端后端"
---

# Hermes Agent — Docker

Docker 与 Hermes Agent 有两种不同的交互方式：

1.  **在 Docker 中运行 Hermes** — Agent 本身在容器内运行（本页主要关注点）
2.  **Docker 作为终端后端** — Agent 在宿主机上运行，但每个命令都在一个持久化的 Docker 沙盒容器内执行，该容器在 Hermes 进程的生命周期内（跨越工具调用、`/new` 和子 Agent）持续存在（参见[配置 → Docker 后端](./configuration.md#docker-backend)）

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

在面向互联网的机器上开放任何端口都存在安全风险。除非你了解这些风险，否则不应这样做。

## 运行仪表板

内置的 Web 仪表板作为可选的辅助进程，在与网关相同的容器内运行。设置 `HERMES_DASHBOARD=1` 并同时暴露网关的 `8642` 端口和仪表板的 `9119` 端口：

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

入口点会在 `exec` 执行主命令之前，在后台启动 `hermes dashboard`（以非 root 用户 `hermes` 运行）。仪表板的输出在 `docker logs` 中带有 `[dashboard]` 前缀，因此很容易与网关日志区分开。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）以在主命令旁启动仪表板 | *(未设置 — 不启动仪表板)* |
| `HERMES_DASHBOARD_HOST` | 仪表板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 仪表板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_TUI` | 设置为 `1` 以在浏览器中暴露聊天标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`） | *(未设置)* |

默认的 `HERMES_DASHBOARD_HOST=0.0.0.0` 是宿主机通过已发布端口访问仪表板所必需的；在这种情况下，入口点会自动将 `--insecure` 传递给 `hermes dashboard`。如果你想将仪表板限制为仅容器内访问（例如，在边车容器的反向代理后面），请覆盖为 `127.0.0.1`。

:::note
仪表板辅助进程**不受监控** — 如果它崩溃，它将保持关闭状态，直到容器重启。不支持将其作为单独的容器运行：仪表板的网关存活检测要求与网关进程共享 PID 命名空间。
:::

## 以交互方式运行（CLI 聊天）

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
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

:::warning
切勿同时运行两个针对同一数据目录的 Hermes **网关**容器 — 会话文件和记忆存储并非为并发写入访问而设计。
:::

## 多配置文件支持

Hermes 支持[多个配置文件](../reference/profile-commands.md) — 独立的 `~/.hermes/` 目录，允许你从单个安装运行独立的 Agent（不同的灵魂、技能、记忆、会话、凭证）。**在 Docker 下运行时，不建议使用 Hermes 内置的多配置文件功能。**

相反，推荐的模式是**每个配置文件一个容器**，每个容器将其自己的宿主机目录绑定挂载为 `/opt/data`：

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

- **隔离性** — 每个容器都有自己的文件系统、进程表和资源限制。一个配置文件中的崩溃、依赖项更改或失控会话不会影响另一个。
- **独立生命周期** — 可以单独升级、重启、暂停或回滚每个 Agent（`docker restart hermes-work` 不会影响 `hermes-personal`）。
- **清晰的端口和网络分离** — 每个网关绑定自己的宿主机端口；聊天平台或 API 服务器之间没有串扰的风险。
- **更简单的思维模型** — 容器*就是*配置文件。备份、迁移和权限都遵循绑定挂载的目录，无需记住额外的 `--profile` 标志。
- **避免并发写入风险** — 上面关于切勿针对同一数据目录运行两个网关的警告同样适用于单个容器内的配置文件。
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

API 密钥从容器内的 `/opt/data/.env` 读取。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接的 `-e` 标志会覆盖 `.env` 中的值。这对于 CI/CD 或密钥管理器集成非常有用，因为你可能不希望密钥存储在磁盘上。

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
      # 取消注释以转发特定的环境变量，而不是使用 .env 文件：
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```

使用 `docker compose up -d` 启动，并使用 `docker compose logs -f` 查看日志。仪表盘的输出以 `[dashboard]` 为前缀，因此很容易从消息网关日志中过滤出来。

## 资源限制

Hermes 容器需要适度的资源。推荐的最低配置：

| 资源 | 最低 | 推荐 |
|----------|---------|-------------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核心 | 2 核心 |
| 磁盘（数据卷） | 500 MB | 2+ GB（随会话/技能增长） |

浏览器自动化（Playwright/Chromium）是最耗内存的功能。如果不需要浏览器工具，1 GB 就足够了。如果启用了浏览器工具，请至少分配 2 GB。

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
- ripgrep、ffmpeg、git 和 tini 作为系统工具
- **`docker-cli`** — 以便在容器内运行的 Agent 可以驱动主机的 Docker 守护进程（通过绑定挂载 `/var/run/docker.sock` 来选择启用），用于 `docker build`、`docker run`、容器检查等。
- **`openssh-client`** — 支持从容器内部使用 [SSH 终端后端](/docs/user-guide/configuration#ssh-backend)。SSH 后端会调用系统的 `ssh` 二进制文件；没有这个，它在容器化安装中会静默失败。
- WhatsApp 桥接 (`scripts/whatsapp-bridge/`)

入口点脚本 (`docker/entrypoint.sh`) 在首次运行时引导数据卷：
- 创建目录结构 (`sessions/`、`memories/`、`skills/` 等)
- 如果不存在 `.env`，则复制 `.env.example` → `.env`
- 如果缺少，则复制默认的 `config.yaml`
- 如果缺少，则复制默认的 `SOUL.md`
- 使用基于清单的方法同步捆绑的技能（保留用户编辑）
- 当 `HERMES_DASHBOARD=1` 时，可选地将 `hermes dashboard` 作为后台辅助进程启动（参见[运行仪表盘](#running-the-dashboard)）
- 然后使用你传递的任何参数运行 `hermes`

## 升级

拉取最新的镜像并重新创建容器。你的数据目录不受影响。

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

当使用 Docker 作为执行环境时（不是上述方法，而是当 Agent 在 Docker 沙盒内运行命令时 — 参见[配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用重用单个长期存在的容器，并自动将技能目录 (`~/.hermes/skills/`) 和技能声明的任何凭证文件作为只读卷绑定挂载到该容器中。技能脚本、模板和引用在沙盒内可用，无需手动配置，并且由于容器在 Hermes 进程的生命周期内持续存在，你安装的任何依赖项或写入的任何文件都会保留到下一次工具调用。

SSH 和 Modal 后端也会发生相同的同步 — 技能和凭证文件会在每个命令之前通过 rsync 或 Modal 挂载 API 上传。

## 故障排除

### 容器立即退出

检查日志：`docker logs hermes`。常见原因：
- 缺少或无效的 `.env` 文件 — 首先以交互方式运行以完成设置
- 如果运行时有暴露端口，则可能是端口冲突

### "Permission denied" 错误

容器的入口点通过 `gosu` 将权限降级为非 root 用户 `hermes` (UID 10000)。如果你的主机 `~/.hermes/` 由不同的 UID 拥有，请设置 `HERMES_UID`/`HERMES_GID` 以匹配你的主机用户，或者确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

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

`--restart unless-stopped` 标志可以处理大多数暂时性故障。如果消息网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状况

```sh
docker logs --tail 50 hermes          # 最近的日志
docker run -it --rm nousresearch/hermes-agent:latest version     # 验证版本
docker stats hermes                    # 资源使用情况
```