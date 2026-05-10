---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2、原生 Windows（早期测试版）或通过 Termux 在 Android 上安装 Hermes Agent"
---

# 安装

使用一行安装程序，在不到两分钟内启动并运行 Hermes Agent。

## 快速安装

### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows（原生，PowerShell）— 早期测试版

:::warning 早期测试版
原生 Windows 支持处于**早期测试阶段**。它可以在常见路径下安装并运行，但尚未像我们的 POSIX 安装程序那样经过广泛的道路测试。遇到问题时请[提交问题](https://github.com/NousResearch/hermes-agent/issues)。对于目前 Windows 上最经得起考验的设置，请改用上述在 **WSL2** 内部的 Linux/macOS 一行安装程序。
:::

打开 PowerShell 并运行：

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

安装程序会处理**所有事情**：`uv`、Python 3.11、Node.js 22、`ripgrep`、`ffmpeg`、**以及一个便携式 Git Bash**（PortableGit — 一个自包含的 Git-for-Windows 发行版，提供 Hermes 用于 shell 命令的 `bash.exe` 和完整的 POSIX 工具链；在 32 位 Windows 上，安装程序会回退到 MinGit，它缺少 bash 并禁用终端工具 / Agent 浏览器功能）。它会在 `%LOCALAPPDATA%\hermes\hermes-agent` 下克隆仓库，创建虚拟环境，并将 `hermes` 添加到您的**用户 PATH** 中。安装后请重启终端（或打开一个新的 PowerShell 窗口），以便 PATH 生效。

**Git 的处理方式：**
1. 如果 `git` 已经在您的 PATH 上，安装程序会使用您现有的安装。
2. 否则，它会下载便携式 **PortableGit**（约 50MB，来自官方的 `git-for-windows` GitHub 发布版）并将其解压到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限。完全隔离 — 它不会干扰任何系统 Git 安装，无论其是否损坏。（在 32 位 Windows 上，它会回退到 MinGit，因为 PortableGit 只提供 64 位和 ARM64 资源；依赖 bash 的 Hermes 功能在 32 位主机上将无法工作。）

**为什么不使用 winget？** 早期的设计通过 `winget install Git.Git` 自动安装 Git，但当系统 Git 安装处于部分或损坏状态时（这正是用户需要安装程序正常工作的时候），winget 会严重失败。便携式 Git 方法绕过了 winget、Windows 安装程序注册表以及任何现有的系统 Git。如果 Hermes 的 Git 安装本身损坏，只需 `Remove-Item %LOCALAPPDATA%\hermes\git` 并重新运行安装程序 — 不影响系统，没有卸载麻烦。

安装程序还会将 `HERMES_GIT_BASH_PATH` 设置为找到的 `bash.exe`，以便 Hermes 在新的 shell 中确定性地解析它。

如果您更喜欢 WSL2，上面的 Linux 安装程序可以在其中运行；原生和 WSL 安装可以共存而不冲突（原生数据位于 `%LOCALAPPDATA%\hermes`，WSL 数据位于 `~/.hermes`）。

### Android / Termux

Hermes 现在还提供了一个支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 并切换到经过测试的 Android 流程：
- 使用 Termux `pkg` 安装系统依赖项（`git`、`python`、`nodejs`、`ripgrep`、`ffmpeg`、构建工具）
- 使用 `python -m venv` 创建虚拟环境
- 自动导出 `ANDROID_API_LEVEL` 用于 Android wheel 构建
- 优先使用广泛的 `.[termux-all]` 额外依赖项，如果第一次尝试编译失败，则回退到较小的 `.[termux]` 额外依赖项（最后是基础安装）
- 默认跳过未经测试的浏览器 / WhatsApp 引导程序

如果您想要完全明确的路径，请遵循专门的 [Termux 指南](./termux.md)。

:::note Windows 功能对等性（早期测试版）

原生 Windows 处于**早期测试阶段**。除了基于浏览器的仪表板聊天终端外，所有功能都在 Windows 上原生运行：
- **CLI（`hermes chat`、`hermes setup`、`hermes gateway`、…）** — 原生，使用您的默认终端
- **消息网关（Telegram、Discord、Slack、…）** — 原生，作为后台 PowerShell 进程运行
- **定时任务调度器** — 原生
- **浏览器工具** — 原生（通过 Node.js 使用 Chromium）
- **MCP 服务器** — 原生（支持 stdio 和 HTTP 传输）
- **仪表板 `/chat` 终端窗格** — **仅限 WSL2**（使用 POSIX PTY；原生 Windows 没有等效物）。仪表板的其余部分（会话、作业、指标）可以原生工作 — 只有嵌入的 PTY 终端标签页受限。

如果在环境中遇到与编码相关的错误并希望回退到传统的 cp1252 stdio 路径，请设置 `HERMES_DISABLE_WINDOWS_UTF8=1`（对二分查找很有用）。
:::

### 安装程序的作用

安装程序会自动处理所有事情 — 所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，您就可以开始聊天了。

#### 安装布局

安装程序放置文件的位置取决于您是作为普通用户还是 root 用户安装：

| 安装程序 | 代码位于 | `hermes` 二进制文件 | 数据目录 |
|---|---|---|---|
| 按用户（普通） | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes`（符号链接） | `~/.hermes/` |
| Root 模式（`sudo curl … \| sudo bash`） | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/`（或 `$HERMES_HOME`） |

Root 模式的 **FHS 布局**（`/usr/local/lib/…`、`/usr/local/bin/hermes`）与 Linux 上其他系统范围的开发工具的安装位置相匹配。这对于共享机器部署很有用，其中一个系统安装应为每个用户服务。按用户配置（身份验证、技能、会话）仍然位于每个用户的 `~/.hermes/` 或显式的 `HERMES_HOME` 下。

### 安装后

重新加载您的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或：source ~/.zshrc
hermes             # 开始聊天！
```

以后要重新配置单个设置，请使用专用命令：

```bash
hermes model          # 选择您的 LLM 提供商和模型
hermes tools          # 配置启用哪些工具
hermes gateway setup  # 设置消息平台
hermes config set     # 设置单个配置值
hermes setup          # 或者运行完整的设置向导一次性配置所有内容
```

---

## 先决条件

唯一的先决条件是 **Git**。安装程序会自动处理其他所有事情：

- **uv**（快速的 Python 包管理器）
- **Python 3.11**（通过 uv，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）

:::info
您**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺少的内容并为您安装。只需确保 `git` 可用（`git --version`）。
:::

:::tip Nix 用户
如果您使用 Nix（在 NixOS、macOS 或 Linux 上），有一个专门的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参阅 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
:::

---

## 手动 / 开发者安装

如果您想克隆仓库并从源代码安装 — 用于贡献、从特定分支运行或完全控制虚拟环境 — 请参阅贡献指南中的 [开发设置](../developer-guide/contributing.md#development-setup) 部分。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载您的 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置您的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后缺少配置 | 运行 `hermes config check` 然后 `hermes config migrate` |

要获取更多诊断信息，请运行 `hermes doctor` — 它会准确告诉您缺少什么以及如何修复。