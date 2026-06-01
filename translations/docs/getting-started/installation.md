---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2、原生 Windows 或通过 Termux 在 Android 上安装 Hermes Agent"
---

# 安装

使用一行安装程序，在两分钟内启动并运行 Hermes Agent。

## 快速安装

### 桌面应用 (macOS + Windows)

更喜欢原生安装程序？

- **桌面版下载:** [GitHub Releases](https://github.com/NousResearch/hermes-agent/releases/latest)

桌面版构建提供已签名/公证的 macOS 工件和带有校验和文件的 Windows 安装程序。

### 一行 CLI 安装程序 (Linux / macOS / WSL2)

对于基于 git 的安装，它会跟踪 `main` 分支并让你立即获得最新更改：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (原生，PowerShell)

原生 Windows 无需 WSL 即可运行 Hermes — CLI、消息网关、TUI 和工具都能原生工作。（原生和 WSL2 安装可以干净地共存；关于那个仅限 WSL2 的功能，请参阅下面的功能说明。）发现错误？请[提交问题](https://github.com/NousResearch/hermes-agent/issues)。

打开 PowerShell 并运行：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

安装程序会处理**所有事情**：`uv`、Python 3.11、Node.js 22、`ripgrep`、`ffmpeg`、**以及一个便携式 Git Bash**（PortableGit — 一个自包含的 Git-for-Windows 发行版，提供 Hermes 用于 shell 命令的 `bash.exe` 和完整的 POSIX 工具链；在 32 位 Windows 上，安装程序会回退到 MinGit，它缺少 bash 并禁用终端工具 / Agent 浏览器功能）。它会在 `%LOCALAPPDATA%\hermes\hermes-agent` 下克隆仓库，创建虚拟环境，并将 `hermes` 添加到你的**用户 PATH** 中。安装后重启终端（或打开一个新的 PowerShell 窗口）以便 PATH 生效。

**Git 的处理方式：**
1. 如果 `git` 已经在你的 PATH 上，安装程序会使用你现有的安装。
2. 否则，它会下载便携式 **PortableGit**（约 50MB，来自官方的 `git-for-windows` GitHub 发布版）并将其解压到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限。完全隔离 — 它不会干扰任何系统 Git 安装，无论其是否损坏。（在 32 位 Windows 上，它会回退到 MinGit，因为 PortableGit 只提供 64 位和 ARM64 资源；依赖 bash 的 Hermes 功能在 32 位主机上将无法工作。）

**为什么不使用 winget？** 早期的设计通过 `winget install Git.Git` 自动安装 Git，但当系统 Git 安装处于部分或损坏状态时（这正是用户需要安装程序正常工作的时候），winget 会严重失败。便携式 Git 方法绕过了 winget、Windows 安装程序注册表以及任何现有的系统 Git。如果 Hermes 的 Git 安装本身损坏了，只需 `Remove-Item %LOCALAPPDATA%\hermes\git` 并重新运行安装程序 — 不影响系统，没有卸载麻烦。

安装程序还会设置 `HERMES_GIT_BASH_PATH` 指向找到的 `bash.exe`，以便 Hermes 在新的 shell 中确定性地解析它。

如果你更喜欢 WSL2，上面的 Linux 安装程序可以在其中运行；原生和 WSL 安装可以共存而不冲突（原生数据位于 `%LOCALAPPDATA%\hermes` 下，WSL 数据位于 `~/.hermes` 下）。

**桌面安装程序（替代方案）：** 还提供了一个轻量级的 GUI 安装程序 — 下载 Hermes Desktop，运行 `.exe`，首次启动时，它会在后台调用 `install.ps1` 来配置 Python（通过 `uv`）、Node、PortableGit 以及其他依赖项。桌面应用和通过 PowerShell 安装的 CLI 共享相同的安装和数据目录，因此你可以使用其中一个或两者都使用。详情请参阅 [Windows（原生）指南](../user-guide/windows-native#desktop-installer-alternative)。

### Android / Termux

Hermes 现在还提供了一个支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 并切换到经过测试的 Android 流程：
- 使用 Termux `pkg` 安装系统依赖项（`git`、`python`、`nodejs`、`ripgrep`、`ffmpeg`、构建工具）
- 使用 `python -m venv` 创建虚拟环境
- 自动导出 `ANDROID_API_LEVEL` 用于 Android wheel 构建
- 优先使用广泛的 `.[termux-all]` extra，如果第一次尝试编译失败，则回退到较小的 `.[termux]` extra（最后是基础安装）
- 默认跳过未经测试的浏览器 / WhatsApp 引导程序

如果你想要完全明确的路径，请遵循专门的 [Termux 指南](./termux.md)。

:::note Windows 功能对等性

除了基于浏览器的仪表板聊天终端外，其他所有功能都能在 Windows 上原生运行：
- **CLI (`hermes chat`, `hermes setup`, `hermes gateway`, …)** — 原生，使用你的默认终端
- **消息网关 (Telegram, Discord, Slack, …)** — 原生，作为后台 PowerShell 进程运行
- **定时任务调度器** — 原生
- **浏览器工具** — 原生（通过 Node.js 使用 Chromium）
- **MCP 服务器** — 原生（支持 stdio 和 HTTP 传输）
- **仪表板 `/chat` 终端窗格** — **仅限 WSL2**（使用 POSIX PTY；原生 Windows 没有等效功能）。仪表板的其余部分（会话、作业、指标）可以原生工作 — 只有嵌入的 PTY 终端选项卡受限。

如果你遇到编码相关的错误并希望回退到传统的 cp1252 stdio 路径（对二分查找有用），请在环境中设置 `HERMES_DISABLE_WINDOWS_UTF8=1`。
:::

### 安装程序的作用

安装程序会自动处理所有事情 — 所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，你就可以开始聊天了。

#### 安装布局

安装程序放置文件的位置取决于你是以普通用户身份安装还是以 root 身份安装：

| 安装方式 | 代码位置 | `hermes` 二进制文件 | 数据目录 |
|---|---|---|---|
| pip install | Python site-packages | `~/.local/bin/hermes` (console_scripts) | `~/.hermes/` |
| 按用户安装 (git 安装程序) | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes` (符号链接) | `~/.hermes/` |
| Root 模式 (`sudo curl … \| sudo bash`) | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/` (或 `$HERMES_HOME`) |
根模式下的 **FHS 布局** (`/usr/local/lib/…`, `/usr/local/bin/hermes`) 与 Linux 上其他系统级开发者工具的安装位置一致。这对于共享机器部署非常有用，一个系统安装即可服务所有用户。每个用户的配置（认证、技能、会话）仍位于各自的 `~/.hermes/` 目录下或显式设置的 `HERMES_HOME` 环境变量中。

### 安装后

重新加载你的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或者：source ~/.zshrc
hermes             # 开始聊天！
```

如需稍后重新配置个别设置，请使用专用命令：

```bash
hermes model          # 选择你的 LLM 提供商和模型
hermes tools          # 配置启用哪些工具
hermes gateway setup  # 设置消息平台
hermes config set     # 设置单个配置值
hermes setup          # 或者运行完整的设置向导一次性配置所有内容
```

:::tip 最快路径：Nous Portal
一个订阅覆盖 300+ 模型以及 [Tool Gateway](/user-guide/features/tool-gateway)（网络搜索、图像生成、TTS、云浏览器）。无需为每个工具单独管理密钥：

```bash
hermes setup --portal
```

该命令将登录、设置 Nous 作为你的提供商，并启用 Tool Gateway，一步到位。
:::

---

## 先决条件

**pip 安装：** 除了 Python 3.11+ 外，没有其他先决条件。其他所有内容都会自动处理。

**Git 安装程序：** 唯一的先决条件是 **Git**。安装程序会自动处理其他所有内容：

- **uv**（快速的 Python 包管理器）
- **Python 3.11**（通过 uv 安装，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）

:::info
你**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺少的内容并为你安装。只需确保 `git` 可用（`git --version`）。
:::

:::tip Nix 用户
如果你使用 Nix（在 NixOS、macOS 或 Linux 上），有一个专用的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参阅 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
:::

---

## 手动 / 开发者安装

如果你想克隆仓库并从源码安装——用于贡献、运行特定分支或完全控制虚拟环境——请参阅贡献指南中的 [开发设置](../developer-guide/contributing.md#development-setup) 部分。

---

## 非 Sudo / 系统服务用户安装

支持以专用非特权用户（例如 `hermes` systemd 服务账户，或任何没有 `sudo` 权限的用户）运行 Hermes。安装路径上唯一真正需要 root 权限的是 Playwright 的 `--with-deps` 步骤，该步骤通过 `apt` 安装 Chromium 使用的共享库（`libnss3`、`libxkbcommon` 等）。安装程序会检测 sudo 是否可用，并在不可用时优雅降级——它会将 Chromium 二进制文件安装到服务用户自己的 Playwright 缓存中，并打印管理员需要单独运行的精确命令。

**推荐的分步操作（Debian/Ubuntu）：**

1.  **一次性操作，以具有 sudo 权限的管理员用户**，安装 Chromium 需要的系统库：
    ```bash
    sudo npx playwright install-deps chromium
    ```
    （你可以在任何地方运行此命令——`npx` 会即时获取 Playwright。）

2.  **以非特权服务用户身份**，运行常规安装程序。它将检测到缺少 sudo，跳过 `--with-deps`，并将 Chromium 安装到用户的本地 Playwright 缓存中：
    ```bash
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
    ```

    如果你想完全跳过 Playwright 步骤——例如，因为你运行的是无头模式且不需要浏览器自动化——请传递 `--skip-browser`：
    ```bash
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-browser
    ```

3.  **使 `hermes` 对服务用户的 shell 可用。** 安装程序将启动器写入 `~/.local/bin/hermes`。系统服务账户通常具有最小化的 PATH，不包含 `~/.local/bin`。要么将其添加到用户的环境变量中，要么将启动器符号链接到系统位置：
    ```bash
    # 选项 A — 添加到服务用户的配置文件中
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

    # 选项 B — 系统范围的符号链接（以管理员身份运行）
    sudo ln -s /home/hermes/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
    ```

4.  **验证：** `hermes doctor` 现在应该能正常运行。如果你遇到 `ModuleNotFoundError: No module named 'dotenv'`，说明你正在使用系统 Python 调用仓库源码中的 `hermes` 文件（`~/.hermes/hermes-agent/hermes`），而不是虚拟环境启动器（`~/.hermes/hermes-agent/venv/bin/hermes`）——请修复第 3 步。

相同的模式适用于 Arch（安装程序使用 pacman 并遵循相同的 sudo 检测逻辑）、Fedora/RHEL 和 openSUSE——这些发行版根本不支持 `--with-deps`，因此管理员总是需要单独安装系统库。相关的 `dnf`/`zypper` 命令将由安装程序打印出来。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载你的 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 来配置你的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后缺少配置 | 运行 `hermes config check` 然后 `hermes config migrate` |

如需更多诊断，请运行 `hermes doctor`——它会确切地告诉你缺少什么以及如何修复。

## 安装方法自动检测

Hermes 会自动检测它是通过 `pip`、git 安装程序、Homebrew 还是 NixOS 安装的，并且 `hermes update` 会打印出该路径对应的更新命令。无需设置环境变量——检测基于安装布局（Python site-packages、`~/.hermes/hermes-agent/`、Homebrew 前缀或 Nix 存储路径）。`hermes doctor` 也会在其环境摘要中显示检测到的方法。