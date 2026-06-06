---
sidebar_position: 3
title: "桌面应用"
description: "原生的 Hermes 桌面应用——提供与 Hermes 聊天的精致体验，包含流式工具输出、并排预览、文件浏览器、语音、定时任务、配置文件、技能和设置。支持 macOS、Windows 和 Linux。"
---

# 桌面应用

Hermes 桌面应用是一个原生应用，围绕与 CLI 和消息网关中**相同**的 Agent 构建——相同的配置、相同的 API 密钥、相同的会话、相同的技能、相同的记忆。它不是一个独立的产品或轻量级克隆；它使用相同的 Hermes Agent 核心和设置，并通过一个现代化且精心设计的 UI 来驱动它。如果你在终端中使用过 `hermes`，那么你在那里设置的一切都已经在这里了，而你在这里做的任何事情也会在那里显示。

它运行在 **macOS、Windows 和 Linux** 上。

:::tip 哪个界面是哪个？
Hermes 有几个前端，它们都与同一个 Agent 通信：

- **桌面应用**（本页）——一个具有专为聊天、配置和管理设计的 UI 的原生应用程序。
- **CLI** (`hermes`) 和 **[TUI](./tui.md)** (`hermes --tui`) —— 终端界面。
- **[Web 仪表盘](./features/web-dashboard.md)** (`hermes dashboard`) —— 一个浏览器管理面板；其可选的 **Chat** 标签页通过伪终端嵌入了 TUI。

选择适合当前场景的界面。它们共享状态，因此你可以在一个界面中开始会话，然后在另一个界面中恢复。
:::

## 安装

请遵循 [Hermes Desktop 的安装说明](../getting-started/installation.md)。

如果你已经安装了 Hermes，只需运行：

```bash
hermes desktop
```

这将使用你当前的配置、密钥、会话和技能。

## 应用包含什么

桌面应用组织成一个以聊天为主的窗口，左侧有一个用于导航的边栏。它旨在允许管理多个同时进行的 Agent 对话、配置消息提供商、创建工件、浏览项目的文件夹结构，以及同时处理多个项目。

### 聊天

应用的核心。你可以获得：

- **流式响应**，包含实时的工具活动以及 Agent 工作时的结构化工具调用摘要。
- **与其他所有 Hermes 界面相同的对话历史记录**——在这里开始的会话可以在 CLI/TUI 中恢复，反之亦然。
- **在聊天区域的任何地方拖放文件**，以将其附加到你的下一条消息。
- **右侧预览栏**——在你继续聊天时，可以并排渲染网页、文件和工具输出。

想要连接到另一台机器上的 Hermes 实例，而不是使用捆绑的本地后端？请参阅下面的 [连接到远程后端](#连接到远程后端)——关于远程托管的仪表盘连接如何工作的完整说明（身份验证网关、`/api/ws` 聊天套接字和 WebSocket 关闭代码分类），请参阅 [Web 仪表盘 → 将 Hermes Desktop 连接到远程后端](./features/web-dashboard.md#将-hermes-desktop-连接到远程后端)。

### 文件浏览器

无需离开应用即可浏览和预览工作目录——这对于跟随 Agent 读取、写入和编辑文件非常有用。使用 `hermes desktop --cwd <路径>`（或 `HERMES_DESKTOP_CWD` 环境变量）设置初始项目目录。

### 语音

与 Hermes 对话并听到它的回复，这是与其他地方相同的 [语音模式](./features/voice-mode.md)。在 macOS 上，操作系统会提示一次麦克风访问权限。

### 设置与入门引导

通过真实的 UI 管理提供商、模型、工具和凭据，而无需编辑 YAML。首次运行的入门引导让你在几秒钟内发出第一条消息。设置面板涵盖提供商/密钥、模型选择、工具集配置、MCP 服务器、消息网关和会话管理。

### 管理面板

该应用还提供了更广泛的 Hermes 管理界面，因此你无需切换到终端：

- **技能** —— 浏览、安装和管理 [技能](./features/skills.md)。
- **定时任务** —— 查看和管理 [计划任务](../reference/cli-commands.md#hermes-cron)。
- **配置文件** —— 在 [Hermes 配置文件](./profiles.md) 之间切换（隔离的配置/技能/会话）。
- **消息** —— 设置消息网关通道。
- **Agents** 和 **Command Center** —— 用于多 Agent 工作的编排界面。

## 更新

应用会在后台检查更新，并在有可用更新时提供一键更新。

[手动更新流程](https://hermes-agent.nousresearch.com/docs/getting-started/updating) 也适用于 GUI。

## CLI 参考：`hermes desktop`

要通过 CLI 启动，只需运行 `hermes desktop`。默认情况下，它会安装工作区的 Node 依赖项，构建当前操作系统的未打包 Electron 应用，然后启动该打包后的工件。

| 标志                  | 描述                                                                               |
| --------------------- | ---------------------------------------------------------------------------------- |
| `--skip-build`        | 跳过 npm install/package，并从 `apps/desktop/release` 启动现有的未打包应用         |
| `--force-build`       | 即使内容戳匹配，也强制完全重建                                                     |
| `--build-only`        | 构建桌面应用但不启动它（由 `hermes update` 使用）                                   |
| `--source`            | 针对 `apps/desktop/dist` 通过 `electron .` 启动，而不是使用打包的应用              |
| `--cwd PATH`          | 桌面聊天会话的初始项目目录（设置 `HERMES_DESKTOP_CWD`）                             |
| `--hermes-root PATH`  | 覆盖应用使用的 Hermes 源代码根目录（设置 `HERMES_DESKTOP_HERMES_ROOT`）             |
| `--ignore-existing`   | 强制应用在后端解析期间忽略 `PATH` 上已有的任何 `hermes` CLI                         |
| `--fake-boot`         | 启用确定性的启动延迟，用于验证启动 UI                                              |

## 工作原理

打包的应用仅包含 Electron 外壳。首次启动时，它会将 Hermes Agent 运行时安装到 `HERMES_HOME`（`~/.hermes`，在 Windows 上是 `%LOCALAPPDATA%\hermes`）——**与 CLI 安装使用的布局相同**，这就是两者可以互换的原因。React 渲染器通过标准的消息网关 API 与 `hermes dashboard` 后端通信，并重用 Agent 而不是重新实现它。安装、后端解析和自更新逻辑位于 Electron 主进程中。
## 连接到远程后端

默认情况下，应用启动并管理其自身的**本地**后端。你也可以将其指向运行在其他机器上的 Hermes 后端——例如 VPS、家庭服务器，或通过 Tailscale 连接的 Mini。

:::info 远程后端是一个正在运行的 `hermes dashboard` 进程
"远程后端"指的是在远程机器上运行的 **`hermes dashboard`** 服务器——这是桌面应用连接的进程。除非该仪表板实际启动并可访问，否则本节中的任何内容都无法工作。桌面应用不会为你启动它；你（或一个 `systemd` 服务）需要在远程主机上保持 `hermes dashboard` 运行，然后应用才能连接到它。如果你还使用消息通道（Telegram、Discord 等），**消息网关**是一个*独立的*长期运行进程，需要你独立启动——请参阅设置步骤后的说明。
:::

连接包含两部分：在后端，你使用**身份验证提供商**来保护仪表板；在应用中，你输入后端的 URL 并登录。将仪表板绑定到非回环地址会自动启用其身份验证门，而你配置的提供商则允许桌面应用通过。

**根据后端所在位置选择提供商：**

- **OAuth (Nous Portal) —— 适用于任何在你本机之外可访问的后端，这是首选方案。** 登录会通过你的 Nous 账户进行验证，因此此选项适用于 VPS、公共主机或任何远程后端。使用 `hermes dashboard register`（或 Portal 的 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards) 页面）注册仪表板以配置其 OAuth 客户端，然后从应用中使用**使用 Nous Research 登录**。如果你运行自己的身份提供商，自托管的 OIDC 提供商工作方式相同。
- **用户名/密码 —— 仅限本地/受信任网络使用。** 当后端位于同一受信任 LAN 或仅可通过 VPN（例如 Tailscale）访问时，这是最简单的选项。它使用单一共享凭证进行保护，无需外部身份提供商，因此**不要将其用于暴露在公共互联网上的仪表板**——在这种情况下请使用 OAuth。

本节其余部分展示用户名/密码路径，因为这是在受信任网络上建立连接最快的方式；关于 OAuth 路径，请参阅 [Web 仪表板 → 默认提供商：Nous Research](./features/web-dashboard.md#default-provider-nous-research)。

### 在后端（远程机器上）

设置用户名和密码，然后启动绑定到可访问地址的仪表板。凭证存储在 `~/.hermes/.env`（密钥文件，模式 0600）中：

```bash
# 1. 设置仪表板登录凭证。
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
# 推荐：设置一个稳定的签名密钥，以便会话在重启后得以保留。
# 如果不设置，每次启动都会生成一个随机密钥，你将在每次重启时被登出。
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. 运行仪表板，绑定到可访问的地址。绑定到非回环地址会启用身份验证门；用户名/密码提供商处理登录。
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

只要你希望桌面应用能够连接，就保持 `hermes dashboard` 进程运行——如果它停止，应用将无法再访问后端。在 `systemd`、`tmux` 或你选择的进程管理器下运行它，以便它在注销和重启后仍然存活。

另外，如果你依赖消息通道，请确保**消息网关在远程主机上运行**——仪表板后端是桌面应用与之通信的部分，但你的 Telegram/Discord/Slack 网关会话是一个不同的进程，需要你独立启动并保持运行。有关网关设置，请参阅 [消息](./messaging/index.md)。

不希望以明文形式存储密码？可以设置 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` 为一个 scrypt 哈希值——使用 `python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"` 计算。完整的配置界面（config.yaml 键、每个环境变量、速率限制器）：[Web 仪表板 → 用户名/密码提供商](./features/web-dashboard.md#usernamepassword-provider-no-oauth-idp)。

将仪表板作为 systemd 服务运行？给单元添加 `EnvironmentFile=%h/.hermes/.env`，以便在启动时将凭证加载到环境中。

:::warning
仪表板会读取和写入你的 `.env` 文件（API 密钥、密钥），并且可以运行 Agent 命令。上面展示的**用户名/密码**设置适用于受信任的网络——切勿将受密码保护的仪表板直接暴露在开放的互联网上；请将其置于 VPN 之后。[Tailscale](https://tailscale.com/) 是一个简洁的选择：绑定到机器的 tailscale IP（`--host <tailscale-ip>`），并使用 `http://<tailscale-ip>:9119` 作为远程 URL，这样只有你的 tailnet 可以访问它。要通过公共互联网访问后端，请改用 **OAuth (Nous Portal)** 提供商。
:::

### 在应用中

**设置 → 消息网关 → 远程网关：**

1.  **远程 URL** —— `http://<backend-host>:9119`（如果你使用反向代理，像 `/hermes` 这样的路径前缀也有效）
2.  **登录** —— 应用会检测后端广告的提供商并调整按钮。对于用户名/密码后端，它会显示一个**登录**按钮，打开凭证表单（输入步骤 1 中的凭证）。对于 OAuth 后端，它会显示**使用 `<provider>` 登录**（例如，*使用 Nous Research 登录*），这会运行提供商的浏览器登录流程。无论哪种方式，应用最终都会获得一个针对后端的经过身份验证的会话。
3.  **保存并重新连接** —— 将桌面 shell 切换到远程后端。会话会自动刷新；当设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 时，你可以在重启后保持登录状态。

你也可以在启动应用之前，通过 `HERMES_DESKTOP_REMOTE_URL` 环境变量设置后端 URL（这会覆盖应用内设置）；你仍然需要从消息网关设置面板登录。

### 故障排除
- **登录失败，出现 401 / "无效凭据"** — 用户名或密码与后端的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。后端对于未知用户和错误密码返回相同的通用错误（无枚举提示），因此请仔细检查两者。使用 `curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'` 确认认证已开启 — 它应报告 `true` 并在 `auth_providers` 中包含 `"basic"`。
- **没有"登录"按钮 — 而是要求提供会话 Token** — 后端的用户名/密码提供商未激活。`/api/status` 的 `auth_providers` 中不会列出 `"basic"`。请确保在 `~/.hermes/.env` 中同时设置了用户名和密码（或密码哈希），并且仪表板进程确实加载了它们。
- **每次重启后都退出登录** — 将 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置为一个固定值。如果不设置，每次启动时都会重新生成 Token 签名密钥，从而使所有会话失效。
- **连接被拒绝 / 超时** — 后端绑定到了 `127.0.0.1`（默认值）或者防火墙/VPN 阻止了端口访问。请绑定到 `0.0.0.0` 或 tailscale IP，并向受信任的网络开放端口。

关于从 Web 仪表板角度进行的相同设置，请参阅 [Web 仪表板 → 将 Hermes Desktop 连接到远程后端](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)；环境变量在 [环境变量 → Web 仪表板 & Hermes Desktop](../reference/environment-variables.md#web-dashboard--hermes-desktop) 下有详细说明。

## 故障排除

启动日志位于 `HERMES_HOME/logs/desktop.log`（包含后端输出和最近的 Python 回溯）— 如果应用报告启动失败，请首先检查此文件。你也可以从 CLI 实时查看：

```bash
hermes logs gui -f
```

常见的重置操作：

```bash
# 强制进行干净的首次启动设置 (macOS/Linux)
rm "$HOME/.hermes/hermes-agent/.hermes-bootstrap-complete"

# 重建损坏的 Python venv (macOS/Linux)
rm -rf "$HOME/.hermes/hermes-agent/venv"

# 重置卡住的 macOS 麦克风权限提示
tccutil reset Microphone com.nousresearch.hermes
```

## 从源代码构建

如果你想修改应用本身，请先在仓库根目录安装工作区依赖一次，然后在 `apps/desktop` 目录下运行开发服务器：

```bash
npm install          # 在仓库根目录执行 — 链接 apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite 渲染器 + Electron，它会启动 Python 后端
```

将应用指向特定的代码检出位置，或将其与你的真实配置隔离运行：

```bash
HERMES_DESKTOP_HERMES_ROOT=/path/to/clone npm run dev
HERMES_HOME=/tmp/throwaway npm run dev
npm run dev:fake-boot   # 使用确定性延迟来测试启动覆盖层
```

构建安装程序：

```bash
npm run dist:mac     # DMG + zip
npm run dist:win     # NSIS + MSI
npm run dist:linux   # AppImage + deb + rpm
npm run pack         # 未打包的应用，位于 release/ 目录下（无安装程序）
```

当环境中存在相关凭证时（macOS 对应 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 对应 `WIN_CSC_*`），macOS/Windows 的签名和公证会自动运行。

## 另请参阅

- [CLI 指南](./cli.md) — 终端界面
- [TUI](./tui.md) — 桌面后端复用的现代终端 UI
- [Web 仪表板](./features/web-dashboard.md) — 带有嵌入式聊天标签页的浏览器管理面板
- [配置](./configuration.md) — 桌面应用读取和写入的配置
- [Windows（原生）](./windows-native.md) — 原生 Windows 安装路径