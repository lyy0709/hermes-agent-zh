---
sidebar_position: 3
title: "桌面应用"
description: "原生的 Hermes 桌面应用 —— 提供与 Hermes 聊天的精致体验，包含流式工具输出、并排预览、文件浏览器、语音、定时任务、配置文件、技能和设置。支持 macOS、Windows 和 Linux。"
---

# 桌面应用

Hermes 桌面应用是一个围绕**相同** Agent 构建的原生应用 —— 与 CLI 和消息网关中的 Agent 相同：相同的配置、相同的 API 密钥、相同的会话、相同的技能、相同的记忆。它不是一个独立的产品或轻量级克隆；它使用相同的 Hermes Agent 核心和设置，并通过一个现代化且精心设计的 UI 来驱动它。如果你在终端中使用过 `hermes`，那么你在那里设置的一切都已经在这里了，而你在这里做的任何事情也会在那里显示。

它运行在 **macOS、Windows 和 Linux** 上。

:::tip 哪个界面是哪个？
Hermes 有几个前端，它们都与同一个 Agent 通信：

- **桌面应用**（本页）—— 一个具有专为聊天、配置和管理构建的 UI 的原生应用程序。
- **CLI** (`hermes`) 和 **[TUI](./tui.md)** (`hermes --tui`) —— 终端界面。
- **[Web 仪表盘](./features/web-dashboard.md)** (`hermes dashboard`) —— 一个浏览器管理面板；其可选的 **Chat** 标签页通过伪终端嵌入了 TUI。

根据情况选择适合的界面。它们共享状态，因此你可以在一个界面中开始会话，然后在另一个界面中恢复它。
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

## 应用内包含什么

桌面应用组织成一个以聊天为主的窗口，左侧有一个用于导航的侧边栏。它旨在允许管理多个同时进行的 Agent 对话、配置消息提供商、创建工件、浏览项目的文件夹结构，以及同时处理多个项目。

### 聊天

应用的核心。你可以获得：

- **流式响应**，包含实时的工具活动以及 Agent 工作时的结构化工具调用摘要。
- **与其他所有 Hermes 界面相同的对话历史记录** —— 在这里开始的会话可以在 CLI/TUI 中恢复，反之亦然。
- **拖放文件**到聊天区域的任何位置，将其附加到你的下一条消息。
- **右侧预览栏** —— 在你继续聊天时，并排渲染网页、文件和工具输出。

### 文件浏览器

无需离开应用即可浏览和预览工作目录 —— 这对于跟随 Agent 读取、写入和编辑文件非常有用。使用 `hermes desktop --cwd <路径>`（或 `HERMES_DESKTOP_CWD` 环境变量）设置初始项目目录。

### 语音

与 Hermes 交谈并听到它的回复，这是与其他地方相同的[语音模式](./features/voice-mode.md)。在 macOS 上，操作系统会提示一次麦克风访问权限。

### 设置与入门引导

通过真实的 UI 管理提供商、模型、工具和凭据，而不是编辑 YAML。首次运行的入门引导让你在几秒钟内发出第一条消息。设置面板涵盖提供商/密钥、模型选择、工具集配置、MCP 服务器、消息网关和会话管理。

### 管理面板

该应用还提供了更广泛的 Hermes 管理界面，因此你无需切换到终端：

- **技能** —— 浏览、安装和管理[技能](./features/skills.md)。
- **定时任务** —— 查看和管理[计划任务](../reference/cli-commands.md#hermes-cron)。
- **配置文件** —— 在 [Hermes 配置文件](./profiles.md)之间切换（隔离的配置/技能/会话）。
- **消息** —— 设置消息网关通道。
- **Agents** 和 **Command Center** —— 用于多 Agent 工作的编排界面。

## 更新

应用会在后台检查更新，并在有可用更新时提供一键更新。

[手动更新过程](https://hermes-agent.nousresearch.com/docs/getting-started/updating)也适用于 GUI。

## CLI 参考：`hermes desktop`

要通过 CLI 启动，只需运行 `hermes desktop`。默认情况下，它会安装工作区 Node 依赖项，构建当前操作系统的未打包 Electron 应用，然后启动该打包后的工件。

| 标志                 | 描述                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------- |
| `--skip-build`       | 跳过 npm install/package，并从 `apps/desktop/release` 启动现有的未打包应用 |
| `--force-build`      | 即使内容戳匹配，也强制完全重建                                    |
| `--build-only`       | 构建桌面应用但不启动它（由 `hermes update` 使用）                      |
| `--source`           | 通过 `electron .` 针对 `apps/desktop/dist` 启动，而不是打包的应用           |
| `--cwd PATH`         | 桌面聊天会话的初始项目目录（设置 `HERMES_DESKTOP_CWD`）           |
| `--hermes-root PATH` | 覆盖应用使用的 Hermes 源代码根目录（设置 `HERMES_DESKTOP_HERMES_ROOT`）          |
| `--ignore-existing`  | 强制应用在后端解析期间忽略 `PATH` 上已有的任何 `hermes` CLI      |
| `--fake-boot`        | 启用确定性启动延迟以验证启动 UI                            |

## 工作原理

打包的应用仅包含 Electron 外壳。首次启动时，它会将 Hermes Agent 运行时安装到 `HERMES_HOME`（`~/.hermes`，在 Windows 上是 `%LOCALAPPDATA%\hermes`）—— **与 CLI 安装使用的布局相同**，这就是两者可以互换的原因。React 渲染器通过标准消息网关 API 与 `hermes dashboard --tui` 后端通信，并重用 Agent 而不是重新实现它。安装、后端解析和自更新逻辑位于 Electron 主进程中。

## 故障排除

启动日志位于 `HERMES_HOME/logs/desktop.log`（包含后端输出和最近的 Python 回溯）—— 如果应用报告启动失败，请首先检查此文件。你也可以从 CLI 跟踪它：

```bash
hermes logs gui -f
```

常见的重置操作：

```bash
# 强制进行干净的首次启动设置 (macOS/Linux)
rm "$HOME/.hermes/hermes-agent/.hermes-bootstrap-complete"

# 重建损坏的 Python venv (macOS/Linux)
rm -rf "$HOME/.hermes/hermes-agent/venv"

# 重置卡住的 macOS 麦克风提示
tccutil reset Microphone com.nousresearch.hermes
```

## 从源代码构建

如果你想对应用本身进行修改，请先从仓库根目录安装工作区依赖一次，然后从 `apps/desktop` 运行开发服务器：

```bash
npm install          # 从仓库根目录运行 —— 链接 apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite 渲染器 + Electron，启动 Python 后端
```

将应用指向特定的代码检出，或将其与你的真实配置隔离：

```bash
HERMES_DESKTOP_HERMES_ROOT=/path/to/clone npm run dev
HERMES_HOME=/tmp/throwaway npm run dev
npm run dev:fake-boot   # 使用确定性延迟练习启动覆盖层
```

构建安装程序：

```bash
npm run dist:mac     # DMG + zip
npm run dist:win     # NSIS + MSI
npm run dist:linux   # AppImage + deb + rpm
npm run pack         # release/ 下的未打包应用（无安装程序）
```

当环境中存在相关凭据时（macOS 为 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 为 `WIN_CSC_*`），macOS/Windows 签名和公证会自动运行。

## 另请参阅

- [CLI 指南](./cli.md) —— 终端界面
- [TUI](./tui.md) —— 桌面后端重用的现代化终端 UI
- [Web 仪表盘](./features/web-dashboard.md) —— 带有嵌入式聊天标签页的浏览器管理面板
- [配置](./configuration.md) —— 桌面应用读取和写入的配置
- [Windows (原生)](./windows-native.md) —— 原生 Windows 安装路径