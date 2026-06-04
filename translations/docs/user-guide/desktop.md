---
sidebar_position: 3
title: "桌面应用"
description: "原生的 Hermes 桌面应用 —— 提供与 Hermes 聊天的精致体验，包含流式工具输出、并排预览、文件浏览器、语音、定时任务、配置文件、技能和设置。支持 macOS、Windows 和 Linux。"
---

# 桌面应用

Hermes 桌面应用是一个原生应用，围绕与 CLI 和消息网关中**相同**的 Agent 构建 —— 相同的配置、相同的 API 密钥、相同的会话、相同的技能、相同的记忆。它不是一个独立的产品或轻量级克隆；它使用相同的 Hermes Agent 核心和设置，并通过一个现代化且精心设计的 UI 来驱动它。如果你在终端中使用过 `hermes`，那么你在那里设置的一切都已经在这里了，而你在这里做的任何事情也会在那里显示。

它运行在 **macOS、Windows 和 Linux** 上。

:::tip 哪个界面是哪个？
Hermes 有几个前端，它们都与同一个 Agent 通信：

- **桌面应用**（本页）—— 一个原生应用，具有专为聊天、配置和管理构建的 UI。
- **CLI** (`hermes`) 和 **[TUI](./tui.md)** (`hermes --tui`) —— 终端界面。
- **[Web 仪表盘](./features/web-dashboard.md)** (`hermes dashboard`) —— 一个浏览器管理面板；其可选的 **Chat** 标签页通过伪终端嵌入了 TUI。

选择适合当前场景的界面。它们共享状态，因此你可以在一个界面中开始会话，然后在另一个界面中恢复。
:::

## 安装

### 在 MacOS 或 Windows 上使用 Hermes Desktop 安装程序（推荐）

从我们的网站[下载 Hermes Desktop 安装程序](https://hermes-agent.nousresearch.com/desktop)并运行它。

### 在 Linux、MacOS 或 Windows 上使用 CLI 安装程序

在常规安装脚本中添加 `--include-desktop`。

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --include-desktop
```

### 使用现有的 Hermes 安装

如果你已经安装了 Hermes，只需运行

```bash
hermes desktop
```

这将使用你当前的配置、密钥、会话和技能。

## 应用包含什么

桌面应用组织成一个以聊天为主的窗口，左侧有一个用于导航的边栏。它旨在允许管理多个同时进行的 Agent 对话、配置消息提供商、创建工件、浏览项目的文件夹结构，以及同时处理多个项目。

### 聊天

应用的核心。你可以获得：

- **流式响应**，包含实时的工具活动以及 Agent 工作时的结构化工具调用摘要。
- **与其他所有 Hermes 界面相同的对话历史记录** —— 在这里开始的会话可以在 CLI/TUI 中恢复，反之亦然。
- **在聊天区域的任何地方拖放文件**，将其附加到你的下一条消息。
- **右侧预览栏** —— 在你继续聊天时，并排渲染网页、文件和工具输出。

是与另一台机器上的 Hermes 实例聊天，而不是与捆绑的本地后端聊天？请参阅下面的[连接到远程后端](#连接到远程后端) —— 关于远程托管的仪表盘连接如何工作的完整说明（`/api/ws` 聊天套接字、`--tui` 要求、会话令牌固定和 WebSocket 关闭代码分类），请参阅 [Web 仪表盘 → 将 Hermes Desktop 连接到远程后端](./features/web-dashboard.md#将-hermes-desktop-连接到远程后端)。

### 文件浏览器

无需离开应用即可浏览和预览工作目录 —— 这对于跟随 Agent 读取、写入和编辑文件非常有用。使用 `hermes desktop --cwd <路径>`（或 `HERMES_DESKTOP_CWD` 环境变量）设置初始项目目录。

### 语音

与 Hermes 对话并听到它的回复，与其他地方可用的相同[语音模式](./features/voice-mode.md)。在 macOS 上，操作系统会提示一次麦克风访问权限。

### 设置与入门引导

通过真实的 UI 管理提供商、模型、工具和凭证，而无需编辑 YAML。首次运行的入门引导让你在几秒钟内发出第一条消息。设置面板涵盖提供商/密钥、模型选择、工具集配置、MCP 服务器、消息网关和会话管理。

### 管理面板

该应用还提供了更广泛的 Hermes 管理界面，因此你无需切换到终端：

- **技能** —— 浏览、安装和管理[技能](./features/skills.md)。
- **定时任务** —— 查看和管理[计划任务](../reference/cli-commands.md#hermes-cron)。
- **配置文件** —— 在 [Hermes 配置文件](./profiles.md) 之间切换（隔离的配置/技能/会话）。
- **消息** —— 设置消息网关通道。
- **Agents** 和 **指挥中心** —— 用于多 Agent 工作的编排界面。

## 更新

应用会在后台检查更新，并在有可用更新时提供一键更新。

[手动更新过程](https://hermes-agent.nousresearch.com/docs/getting-started/updating) 也适用于 GUI。

## CLI 参考：`hermes desktop`

要通过 CLI 启动，只需运行 `hermes desktop`。默认情况下，它会安装工作区 Node 依赖项，构建当前操作系统的未打包 Electron 应用，然后启动该打包好的工件。

| 标志                 | 描述                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------- |
| `--skip-build`       | 跳过 npm install/package，并从 `apps/desktop/release` 启动现有的未打包应用 |
| `--force-build`      | 即使内容戳记匹配，也强制完全重建                                    |
| `--build-only`       | 构建桌面应用但不启动它（由 `hermes update` 使用）                      |
| `--source`           | 针对 `apps/desktop/dist` 通过 `electron .` 启动，而不是打包好的应用           |
| `--cwd PATH`         | 桌面聊天会话的初始项目目录（设置 `HERMES_DESKTOP_CWD`）           |
| `--hermes-root PATH` | 覆盖应用使用的 Hermes 源代码根目录（设置 `HERMES_DESKTOP_HERMES_ROOT`）          |
| `--ignore-existing`  | 强制应用在后端解析期间忽略 `PATH` 上已有的任何 `hermes` CLI      |
| `--fake-boot`        | 启用确定性启动延迟，用于验证启动 UI                            |
## 工作原理

打包的应用仅包含 Electron 外壳。首次启动时，它会将 Hermes Agent 运行时安装到 `HERMES_HOME`（`~/.hermes`，或在 Windows 上是 `%LOCALAPPDATA%\hermes`）——**这与 CLI 安装使用的布局相同**，这就是两者可以互换的原因。React 渲染器通过标准消息网关 API 与 `hermes dashboard --tui` 后端通信，并复用 Agent 而不是重新实现它。安装、后端解析和自更新逻辑位于 Electron 主进程中。

## 连接到远程后端

默认情况下，应用启动并管理其自身的**本地**后端。你也可以将其指向运行在另一台机器上的 Hermes 后端——例如 VPS、家庭服务器或 Tailscale 后面的 Mini——在**设置 → 消息网关 → 远程消息网关**下进行配置。它需要两样东西：

- **远程 URL** — 后端的仪表板 URL，例如 `http://<主机>:9119`
- **会话 Token** — 后端的仪表板会话 Token

会话 Token 是容易让人困惑的部分。**Hermes 不会打印出来供你复制**——默认情况下，后端在每次启动时都会生成一个新的随机 Token，并直接注入到提供的 HTML 中，因此在 `config.yaml`、`/gateway` 或日志中都没有可获取的内容。对于远程连接，你需要在后端自行固定 Token，然后将相同的值粘贴到应用中。

后端还必须以 **`--tui`**（或 `HERMES_DASHBOARD_TUI=1`）启动。桌面端的聊天通过仪表板的 `/api/ws` + `/api/pty` WebSocket 运行，除非启用了嵌入式聊天界面，否则这些端点会被拒绝。没有 `--tui` 时，连接仍然能通过 `/api/status` 健康检查，并且应用会报告“远程 Hermes 后端已就绪”——但聊天永远无法工作，因为 WebSocket 会立即关闭。仅使用 `hermes dashboard` 或 `hermes gateway` 是不够的。

### 在后端（远程机器上）

```bash
# 1. 生成一个稳定的 Token 并将其存储在 ~/.hermes/.env 中（密钥文件，权限 0600）。
#    如果没有 HERMES_DASHBOARD_SESSION_TOKEN，Token 会在每次启动时随机生成且无法复制；
#    设置此变量将固定桌面应用将使用的值。
TOKEN=$(openssl rand -base64 32)
echo "HERMES_DASHBOARD_SESSION_TOKEN=$TOKEN" >> ~/.hermes/.env
chmod 600 ~/.hermes/.env
echo "$TOKEN"   # 将此值复制到桌面应用中

# 2. 运行仪表板，绑定到可访问的地址。
#    --tui 启用嵌入式聊天（桌面端驱动的 /api/ws + /api/pty WebSocket）——
#    没有它，应用可以连接，但聊天功能无法使用。
#    --insecure 对于任何非回环地址绑定都是必需的，并保持传统的会话 Token 认证路径
#    （非回环地址绑定 WITHOUT --insecure 会启用 OAuth 网关，这将忽略会话 Token）。
hermes dashboard --tui --no-open --insecure --host 0.0.0.0 --port 9119
```

将仪表板作为 systemd 服务运行？给单元设置 `EnvironmentFile=%h/.hermes/.env`，以便在启动时 Token 就在环境中。

:::warning
`--insecure` 会暴露一个可以读取/写入你的 `.env`（API 密钥、密钥）并可以运行 Agent 命令的端口。切勿将其暴露在开放的互联网上——将其置于 VPN 之后。[Tailscale](https://tailscale.com/) 是一个简洁的选择：绑定到机器的 tailscale IP（`--host <tailscale-ip>`）并使用 `http://<tailscale-ip>:9119` 作为远程 URL，这样只有你的 tailnet 可以访问它。
:::

### 在应用中

**设置 → 消息网关 → 远程消息网关：**

1.  **远程 URL** — `http://<后端主机>:9119`（如果你使用反向代理，像 `/hermes` 这样的路径前缀也有效）
2.  **会话 Token** — 粘贴步骤 1 中的 `$TOKEN` 值
3.  **测试远程连接** — 确认后端可访问且 Token 被接受
4.  **保存并重新连接** — 将桌面外壳切换到远程后端

Token 以加密形式存储在应用的本地配置中；后续编辑时将此字段留空以保留已保存的 Token。你也可以在启动应用之前，通过环境变量 `HERMES_DESKTOP_REMOTE_URL` + `HERMES_DESKTOP_REMOTE_TOKEN` 来设置它（两者必须一起设置；它们会覆盖应用内的设置）。

### 故障排除

-   **测试失败，返回 401** — Token 与后端的 `HERMES_DASHBOARD_SESSION_TOKEN` 不匹配，或者后端绑定在非回环地址但*没有*使用 `--insecure`（OAuth 网关已启用，忽略了 Token）。使用 `curl -s -H "X-Hermes-Session-Token: $TOKEN" http://<主机>:9119/api/status` 验证——这应该返回 JSON，而不是 401。
-   **应用显示“远程 Hermes 后端已就绪”但聊天无响应** — 后端启动时没有使用 `--tui`（或 `HERMES_DASHBOARD_TUI=1`）。状态探测通过，但聊天 WebSocket（`/api/ws` / `/api/pty`）被拒绝。使用 `--tui` 重启后端。
-   **连接被拒绝 / 超时** — 后端绑定到了 `127.0.0.1`（默认值）或者防火墙/VPN 阻止了端口。绑定到 `0.0.0.0` 或 tailscale IP，并向你的受信任网络开放端口。
-   **没有 Token 可复制** — 这是预期的。你需要自己生成；Hermes 永远不会暴露默认的临时 Token。

从 Web 仪表板角度了解相同设置，请参阅 [Web 仪表板 → 将 Hermes Desktop 连接到远程后端](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)；环境变量在 [环境变量 → Web 仪表板 & Hermes Desktop](../reference/environment-variables.md#web-dashboard--hermes-desktop) 下有详细说明。

## 故障排除

启动日志位于 `HERMES_HOME/logs/desktop.log`（它包含后端输出和最近的 Python 回溯）——如果应用报告启动失败，请首先检查此文件。你也可以从 CLI 实时查看它：

```bash
hermes logs gui -f
```

常见的重置操作：

```bash
# 强制进行干净的首次启动设置 (macOS/Linux)
rm "$HOME/.hermes/hermes-agent/.hermes-bootstrap-complete"

# 重建损坏的 Python 虚拟环境 (macOS/Linux)
rm -rf "$HOME/.hermes/hermes-agent/venv"

# 重置卡住的 macOS 麦克风权限提示
tccutil reset Microphone com.nousresearch.hermes
```

## 从源代码构建

如果你想对应用本身进行修改，请先在仓库根目录安装工作区依赖，然后在 `apps/desktop` 目录下运行开发服务器：
```bash
npm install          # 在仓库根目录执行 — 链接 apps/desktop、web、apps/shared
cd apps/desktop
npm run dev          # Vite 渲染器 + Electron，后者会启动 Python 后端
```

将应用指向特定的代码检出目录，或将其与你的真实配置隔离运行：

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

当环境中存在相关凭证时（macOS 对应 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 对应 `WIN_CSC_*`），macOS/Windows 的签名和公证过程会自动运行。

## 另请参阅

- [CLI 指南](./cli.md) — 终端界面
- [TUI](./tui.md) — 桌面后端复用的现代化终端用户界面
- [Web 仪表盘](./features/web-dashboard.md) — 包含嵌入式聊天标签页的浏览器管理面板
- [配置](./configuration.md) — 桌面应用读取和写入的配置
- [Windows（原生）](./windows-native.md) — 原生 Windows 安装路径