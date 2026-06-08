---
sidebar_position: 3
title: "桌面应用"
description: "原生的 Hermes 桌面应用——提供与 Hermes 聊天的精致体验，包含流式工具输出、并排预览、文件浏览器、语音、定时任务、配置文件、技能和设置。支持 macOS、Windows 和 Linux。"
---

# 桌面应用

Hermes 桌面应用是一个原生应用，围绕与 CLI 和消息网关**相同**的 Agent 构建——相同的配置、相同的 API 密钥、相同的会话、相同的技能、相同的记忆。它不是一个独立的产品或轻量级克隆；它使用相同的 Hermes Agent 核心和设置，并通过一个现代化且精心设计的 UI 来驱动它。如果你在终端中使用过 `hermes`，那么你在那里设置的一切都已经在这里了，而你在这里做的任何事情也会在那里显示。

它运行在 **macOS、Windows 和 Linux** 上。

:::tip 哪个界面是哪个？
Hermes 有几个前端，它们都与同一个 Agent 通信：

- **桌面应用**（本页）——一个具有专为聊天、配置和管理设计的 UI 的原生应用程序。
- **CLI** (`hermes`) 和 **[TUI](./tui.md)** (`hermes --tui`) —— 终端界面。
- **[Web 仪表盘](./features/web-dashboard.md)** (`hermes dashboard`) —— 一个浏览器管理面板；其可选的 **Chat** 标签页通过伪终端嵌入了 TUI。

选择适合当前场景的界面。它们共享状态，因此你可以在一个界面中开始会话，然后在另一个界面中恢复它。
:::

## 安装

请遵循 [Hermes Desktop 的安装说明](../getting-started/installation.md)。

如果你已经安装了 Hermes，只需运行

```bash
hermes desktop
```

这将使用你当前的配置、密钥、会话和技能。

## 应用内包含什么

桌面应用以聊天优先的窗口进行组织，左侧边栏用于导航。它旨在允许管理多个同时进行的 Agent 对话、配置消息提供商、创建工件、浏览项目的文件夹结构，以及同时处理多个项目。

### 聊天

应用的核心。你可以获得：

- **流式响应**，包含实时的工具活动以及 Agent 工作时的结构化工具调用摘要。
- **与其他所有 Hermes 界面相同的对话历史记录**——在这里开始的会话可以在 CLI/TUI 中恢复，反之亦然。
- **拖放文件**到聊天区域的任何位置，将其附加到你的下一条消息。
- **右侧预览面板**——在你继续聊天的同时，并排渲染网页、文件和工具输出。
- **输入框历史和队列编辑**——在空的输入框中按上/下箭头键可以调出并重用之前的提示词，并在消息发送前编辑已排队的消息。

#### 状态栏

聊天窗口底部的状态栏显示实时会话状态，并提供无需打开设置的快速控制：

- **内联模型选择器**——直接从状态栏为活动会话切换模型。
- **按会话的 YOLO 切换开关**——仅为此会话打开或关闭 YOLO（与 TUI 一致）。YOLO 会绕过危险命令的确认提示，所以请了解你正在关闭什么——参见 [安全 → YOLO 模式](./security.md#yolo-mode)。

如果聊天是针对另一台机器上的 Hermes 实例，而不是捆绑的本地后端？请参阅下面的 [连接到远程后端](#连接到远程后端)——关于远程托管的仪表盘连接如何工作的完整说明（认证网关、`/api/ws` 聊天套接字和 WebSocket 关闭代码分类），请参阅 [Web 仪表盘 → 将 Hermes Desktop 连接到远程后端](./features/web-dashboard.md#将-hermes-desktop-连接到远程后端)。

### 文件浏览器

无需离开应用即可浏览和预览工作目录——对于跟随 Agent 读取、写入和编辑文件非常有用。使用 `hermes desktop --cwd <路径>`（或 `HERMES_DESKTOP_CWD` 环境变量）设置初始项目目录。

### 语音

与 Hermes 对话并听到它的回复，这是与其他地方相同的[语音模式](./features/voice-mode.md)。在 macOS 上，操作系统会提示一次麦克风访问权限。

### 设置与入门引导

通过真实的 UI 管理提供商、模型、工具和凭据，而无需编辑 YAML。首次运行的入门引导让你在几秒钟内发出第一条消息。设置面板涵盖提供商/密钥、模型选择、工具集配置、MCP 服务器、消息网关和会话管理。

- **提供商设置面板**——一个专门管理推理提供商的地方，具有用于登录和存储每个提供商凭据的账户/API 密钥用户体验。
- **菜单中的每个提供商和模型**——GUI 展示了完整的提供商列表以及 `hermes model` 所知的每个模型，因此你可以从 CLI 看到的相同目录中选择，而不是一个精选的子集。
- **xAI Grok OAuth**——Grok 是启动器中的一等 OAuth 提供商；像其他 OAuth 提供商一样通过浏览器流程登录。
- **从 GUI 安装工具后端**——直接从应用程序运行工具后端安装后的设置步骤，而无需切换到终端。
- **辅助模型警告**——如果你将主模型切换到新的提供商，而辅助任务（标题生成、摘要和类似的助手）仍然固定到另一个提供商，应用会发出警告，以免你在不知情的情况下将工作分散到两个提供商。

首次运行的入门引导已基于统一覆盖层设计系统重新设计，你可以选择**稍后选择提供商**以跳过提供商设置，先进入应用。

### 管理面板

该应用还展示了更广泛的 Hermes 管理界面，因此你无需切换到终端：

- **技能**——浏览、安装和管理[技能](./features/skills.md)。
- **定时任务**——查看和管理[计划任务](../reference/cli-commands.md#hermes-cron)。
- **配置文件**——在 [Hermes 配置文件](./profiles.md)（隔离的配置/技能/会话）之间切换。
- **消息**——设置消息网关通道。
- **Agents** 和 **Command Center**——用于多 Agent 工作的编排界面。

### 键盘与导航

- **命令面板**——按 **Cmd+K**（在 Windows/Linux 上为 Ctrl+K）跳转到操作并从键盘导航应用。
- **可重新绑定的快捷键**——设置中的快捷键面板允许你将应用的键盘快捷键重新映射到你自己的按键。
- **自定义缩放快捷键**——以半步增量缩放界面，以便更精细地控制文本大小。
- **UI 语言切换器**——在应用内更改应用的界面语言，包括简体中文 (zh-Hans)。
### 会话与配置文件

- **会话列表全面改进** — 重新设计的会话列表，支持归档和常规会话整理，以便在会话数量增长时保持列表易于管理。
- **按 ID 搜索会话** — 直接通过 ID 查找特定会话。
- **并发多配置文件会话** — 同时跨多个[配置文件](./profiles.md)运行会话，并使用跨配置文件的 `@session` 链接引用另一个配置文件中的会话。

## 更新

应用会在后台检查更新，并在有可用更新时提供一键更新功能。

[手动更新流程](https://hermes-agent.nousresearch.com/docs/getting-started/updating) 也适用于 GUI。

## 卸载

打开 **设置 → 关于 → 危险区域**，选择要移除的范围：

- **仅卸载 Chat GUI** — 移除桌面应用及其数据；Hermes Agent、您的配置和聊天记录将保留。（等同于 `hermes uninstall --gui`。）
- **卸载 GUI + Agent，保留我的数据** — 移除应用和 Agent，但保留配置、聊天记录和密钥，以便将来重新安装。（等同于 `hermes uninstall`。）
- **卸载所有内容** — 移除应用、Agent 和所有用户数据。（等同于 `hermes uninstall --full`。）

应用会关闭以完成卸载工作（清理工作在其退出后运行，以便能够移除正在运行的应用包及其自身的虚拟环境）。当未安装本地 Agent 时（例如，仅连接远程后端的 GUI 版“轻量”客户端），移除 Agent 的选项会自动隐藏。

您也可以在终端中执行相同的操作 — `hermes uninstall --gui` 仅卸载 GUI，或使用 `hermes uninstall` / `hermes uninstall --full` 同时卸载 Agent。

:::note
从**源代码检出目录**（`hermes desktop` 开发构建）运行 `hermes uninstall --gui` 也会移除工作区的 `node_modules` 和 `apps/desktop/{dist,release}` 构建输出，因为这些是 GUI 构建产物。您可以通过 `hermes desktop`（或 `npm install` + 重新构建）恢复它们 — 但如果您正在积极开发桌面应用，请预计之后需要重新安装依赖项。
:::

## CLI 参考：`hermes desktop`

要通过 CLI 启动，只需运行 `hermes desktop`。默认情况下，它会安装工作区 Node 依赖项，构建当前操作系统的未打包 Electron 应用，然后启动该打包后的产物。

| 标志                  | 描述                                                                               |
| --------------------- | ---------------------------------------------------------------------------------- |
| `--skip-build`        | 跳过 npm install/package 步骤，直接从 `apps/desktop/release` 启动现有的未打包应用 |
| `--force-build`       | 即使内容戳记匹配，也强制进行完整重建                                               |
| `--build-only`        | 构建桌面应用但不启动它（由 `hermes update` 使用）                                  |
| `--source`            | 针对 `apps/desktop/dist` 通过 `electron .` 启动，而不是使用打包的应用              |
| `--cwd PATH`          | 桌面聊天会话的初始项目目录（设置 `HERMES_DESKTOP_CWD`）                            |
| `--hermes-root PATH`  | 覆盖应用使用的 Hermes 源代码根目录（设置 `HERMES_DESKTOP_HERMES_ROOT`）            |
| `--ignore-existing`   | 强制应用在后端解析期间忽略 `PATH` 上已有的任何 `hermes` CLI                        |
| `--fake-boot`         | 启用确定性启动延迟，用于验证启动 UI                                                |

## 工作原理

打包的应用仅包含 Electron 外壳。首次启动时，它会将 Hermes Agent 运行时安装到 `HERMES_HOME`（`~/.hermes`，在 Windows 上是 `%LOCALAPPDATA%\hermes`）— **与 CLI 安装使用的布局相同**，这就是两者可以互换的原因。React 渲染器通过标准消息网关 API 与 `hermes dashboard` 后端通信，并复用 Agent 而不是重新实现它。安装、后端解析和自更新逻辑位于 Electron 主进程中。

## 连接到远程后端

默认情况下，应用启动并管理其自身的**本地**后端。您也可以将其指向运行在另一台机器上的 Hermes 后端 — 例如 VPS、家庭服务器或 Tailscale 网络后的 Mini。

:::info 远程后端是一个正在运行的 `hermes dashboard` 进程
“远程后端”指的是在远程机器上运行的 **`hermes dashboard`** 服务器 — 这是桌面应用连接的进程。除非该 dashboard 实际已启动并可访问，否则本节中的任何内容都无法工作。桌面应用不会为您启动它；您（或 `systemd` 服务）需要在远程主机上保持 `hermes dashboard` 运行，然后应用才能连接到它。如果您还使用消息通道（Telegram、Discord 等），**消息网关**是一个*独立的*长运行进程，需要您独立启动 — 请参阅设置步骤后的说明。
:::

连接包含两部分：在后端，您使用**身份验证提供商**保护 dashboard；在应用中，您输入后端的 URL 并登录。将 dashboard 绑定到非环回地址会自动启用其身份验证门，而您配置的提供商就是允许桌面应用通过的凭证。

**根据后端所在位置选择提供商：**

- **OAuth (Nous Portal) — 适用于您自己机器之外任何可访问的后端，这是首选方案。** 登录凭据通过您的 Nous 账户验证，因此此选项适用于 VPS、公共主机或任何远程后端。使用 `hermes dashboard register`（或 Portal 的 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards) 页面）注册 dashboard 以配置其 OAuth 客户端，然后从应用中使用 **Sign in with Nous Research** 登录。如果您运行自己的身份提供商，自托管的 OIDC 提供商的工作方式相同。
- **用户名/密码 — 仅限本地/受信任网络使用。** 当后端位于同一受信任 LAN 或仅可通过 VPN（例如 Tailscale）访问时，这是最简单的选项。它使用单个共享凭证进行保护，无需外部身份提供商，因此**请勿将其用于暴露在公共互联网的 dashboard** — 在这种情况下请改用 OAuth。
本节其余部分展示用户名/密码路径，因为这是在受信任网络上最快启动的方式；关于 OAuth 路径，请参阅 [Web Dashboard → 默认提供商：Nous Research](./features/web-dashboard.md#default-provider-nous-research)。

### 在后台（远程机器上）

设置用户名和密码，然后启动绑定到可访问地址的仪表板。凭证保存在 `~/.hermes/.env`（密钥文件，模式 0600）中：

```bash
# 1. 设置仪表板登录凭证。
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
# 推荐：一个稳定的签名密钥，以便会话在重启后保留。
# 如果没有设置，每次启动都会生成一个随机密钥，你将在每次重启时被登出。
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. 运行仪表板并绑定到可访问的地址。绑定到非回环地址会启用认证网关；用户名/密码提供商会处理登录。
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

只要你想让桌面应用能够连接，就保持那个 `hermes dashboard` 进程运行——如果它停止，应用将无法再访问后台。在 `systemd`、`tmux` 或你选择的进程管理器下运行它，以便它在注销和重启后仍然存活。

另外，如果你依赖消息通道，请确保**消息网关正在运行**在远程主机上——仪表板后台是桌面应用与之通信的部分，但你的 Telegram/Discord/Slack 网关会话是另一个进程，你需要单独启动并保持运行。有关网关设置，请参阅 [Messaging](./messaging/index.md)。

不想保存明文密码？将 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` 设置为一个 scrypt 哈希值——使用 `python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"` 计算。完整的配置界面（config.yaml 键、每个环境变量、速率限制器）：[Web Dashboard → 用户名/密码提供商](./features/web-dashboard.md#usernamepassword-provider-no-oauth-idp)。

将仪表板作为 systemd 服务运行？给单元添加 `EnvironmentFile=%h/.hermes/.env`，以便在启动时将凭证加载到环境中。

:::warning
仪表板读取和写入你的 `.env`（API 密钥、密钥）并可以运行 Agent 命令。上面展示的**用户名/密码**设置适用于受信任的网络——切勿将受密码保护的仪表板直接暴露在公共互联网上；将其放在 VPN 后面。[Tailscale](https://tailscale.com/) 是一个简洁的选择：绑定到机器的 tailscale IP（`--host <tailscale-ip>`）并使用 `http://<tailscale-ip>:9119` 作为远程 URL，这样只有你的 tailnet 可以访问它。要通过公共互联网访问后台，请改用 **OAuth (Nous Portal)** 提供商。
:::

### 在应用中

**设置 → 消息网关 → 远程网关：**

1.  **远程 URL** — `http://<backend-host>:9119`（如果你使用反向代理，像 `/hermes` 这样的路径前缀也有效）
2.  **登录** — 应用会检测后台广告的提供商并调整按钮。对于用户名/密码后台，它会显示一个**登录**按钮，打开凭证表单（输入步骤 1 中的凭证）。对于 OAuth 后台，它会显示**使用 `<provider>` 登录**（例如 *使用 Nous Research 登录*），这将运行提供商的浏览器登录流程。无论哪种方式，应用最终都会获得一个针对后台的认证会话。
3.  **保存并重新连接** — 将桌面 shell 切换到远程后台。会话会自动刷新；当设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 时，你可以在重启后保持登录状态。

你也可以在启动应用之前通过 `HERMES_DESKTOP_REMOTE_URL` 环境变量设置后台 URL（它会覆盖应用内设置）；你仍然需要从网关设置面板登录。

:::note 每个配置文件的远程主机
远程网关主机是按[配置文件](./profiles.md)配置的，因此每个配置文件可以指向其自己的远程后台（或保持在其本地后台）。切换配置文件会切换应用连接到的远程主机。
:::

### 故障排除

-   **登录失败，错误 401 / "无效凭证"** — 用户名或密码与后台的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。后台对于未知用户和错误密码返回相同的通用错误（没有枚举提示），所以请仔细检查两者。使用 `curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'` 确认网关已启用——它应该报告 `true` 并在 `auth_providers` 中包含 `"basic"`。
-   **没有"登录"按钮——它要求会话 Token** — 后台的用户名/密码提供商未激活。`/api/status` 不会在 `auth_providers` 中列出 `"basic"`。确保在 `~/.hermes/.env` 中同时设置了用户名和密码（或密码哈希），并且仪表板进程确实加载了它们。
-   **每次重启都被登出** — 将 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置为一个稳定的值。如果没有设置，Token 签名密钥会在每次启动时重新生成，使所有会话失效。
-   **连接被拒绝 / 超时** — 后台绑定到了 `127.0.0.1`（默认值）或者防火墙/VPN 阻止了端口。绑定到 `0.0.0.0` 或 tailscale IP，并向你的受信任网络开放该端口。

关于从 web-dashboard 角度的相同设置，请参阅 [Web Dashboard → 将 Hermes Desktop 连接到远程后台](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)；环境变量在 [Environment Variables → Web Dashboard & Hermes Desktop](../reference/environment-variables.md#web-dashboard--hermes-desktop) 下有详细说明。

## 故障排除

启动日志位于 `HERMES_HOME/logs/desktop.log`（包含后台输出和最近的 Python 回溯）——如果应用报告启动失败，请首先检查此文件。你也可以从 CLI 实时查看：

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
## 从源码构建

如果你想对应用本身进行修改，请先在仓库根目录安装工作区依赖一次，然后从 `apps/desktop` 目录运行开发服务器：

```bash
npm install          # 在仓库根目录执行 — 链接 apps/desktop、web、apps/shared
cd apps/desktop
npm run dev          # Vite 渲染器 + Electron，后者会启动 Python 后端
```

将应用指向特定的代码检出目录，或将其与你的真实配置隔离开来（沙盒化）：

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
npm run pack         # 在 release/ 目录下生成未打包的应用（无安装程序）
```

当相关凭证存在于环境变量中时（macOS 对应 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 对应 `WIN_CSC_*`），macOS/Windows 的签名和公证过程会自动运行。

## 另请参阅

- [CLI 指南](./cli.md) — 终端界面
- [TUI](./tui.md) — 桌面后端复用的现代化终端 UI
- [Web 仪表盘](./features/web-dashboard.md) — 包含嵌入式聊天标签页的浏览器管理面板
- [配置](./configuration.md) — 桌面应用读取和写入的配置
- [Windows（原生）](./windows-native.md) — 原生 Windows 安装路径