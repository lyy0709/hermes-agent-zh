---
title: "Windows（原生）指南 — 早期测试版"
description: "早期测试版：在 Windows 10 / 11 上原生运行 Hermes Agent — 安装、功能矩阵、UTF-8 控制台、Git Bash、将消息网关作为计划任务、编辑器处理、PATH、卸载以及常见问题"
sidebar_label: "Windows（原生）— 测试版"
sidebar_position: 3
---

# Windows（原生）指南 — 早期测试版

:::warning 早期测试版
原生 Windows 支持处于**早期测试阶段**。它可以安装、运行并通过我们的 Windows 隐患检查，但尚未像我们的 Linux/macOS/WSL2 路径那样经过大规模的实际测试。请做好遇到粗糙边缘的准备 — 尤其是在子进程处理、路径特性和非 ASCII 控制台输出方面。当你遇到问题时，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)并提供复现步骤。如果你今天想要一个经过实战考验的设置，请改用[在 WSL2 下的 Linux/macOS 安装程序](./windows-wsl-quickstart.md)。
:::

Hermes 可以在 Windows 10 和 Windows 11 上原生运行 — 无需 WSL、Cygwin 或 Docker。本页是深入探讨：哪些功能可以原生运行，哪些仅限于 WSL，安装程序实际做了什么，以及你可能需要调整的 Windows 特定选项。

如果你只想安装，[落地页](/)或[安装页面](../getting-started/installation#windows-native-powershell--early-beta)上的一行命令就是你所需要的。当你遇到意外情况时再回到这里。

:::tip 想要 WSL 吗？
如果你更喜欢真正的 POSIX 环境（用于仪表板的嵌入式终端、`fork` 语义、Linux 风格的文件监视器等），请参阅 **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)**。两者可以干净地共存：原生数据位于 `%LOCALAPPDATA%\hermes` 下，WSL 数据位于 `~/.hermes` 下。
:::

## 快速安装

打开 **PowerShell**（或 Windows 终端）并运行：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

无需管理员权限。安装程序会将文件安装到 `%LOCALAPPDATA%\hermes\` 并将 `hermes` 添加到你的**用户 PATH** — 安装完成后请打开一个新的终端。

**安装程序选项**（需要脚本块形式来传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆特定分支（用于测试 PR） |
| `-Commit` | 未设置 | 将安装固定到特定的提交 SHA（覆盖 `-Branch`） |
| `-Tag` | 未设置 | 将安装固定到特定的 git 标签（例如 `v0.14.0`） |
| `-NoVenv` | 关闭 | 跳过 venv 创建（高级 — 自行管理 Python） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码位置 |

安装程序会自动重试不稳定的 git 获取，并从任何下载的 `install.ps1` 有效负载中去除 BOM，因此在 HTTP 传输过程中获取的 UTF-8 BOM 不再破坏 `[scriptblock]::Create((irm ...))` 形式。

### 桌面安装程序（替代方案）

还提供了一个轻量级的 GUI 安装程序 — 如果你宁愿双击 `.exe` 文件而不是打开 PowerShell，这会很有用。下载 Hermes Desktop，运行安装程序，首次启动时 GUI 会在后台调用 `install.ps1` 来配置 Python（通过 `uv`）、Node、PortableGit 以及下面描述的其他依赖项引导程序。首次运行后，桌面应用程序和通过 PowerShell 安装的 `hermes` CLI 共享相同的 `%LOCALAPPDATA%\hermes\hermes-agent` 安装目录和 `%USERPROFILE%\.hermes` 数据目录 — 可以自由地在 GUI 和 CLI 之间切换。

当你想要熟悉的 Windows 安装体验或将 Hermes 交给非开发人员时，请使用桌面安装程序；当你在终端中时，请使用 PowerShell 一行命令。

### 依赖项引导程序 (`dep_ensure`)

在首次启动时（以及在检测到缺少工具时按需），Hermes 会运行一个小的 Python 引导程序 — `hermes_cli/dep_ensure.py` — 它会检查并惰性安装其所需的非 Python 依赖项。在 Windows 上，相关的依赖项是：

| 依赖项 | Hermes 需要它的原因 |
|---|---|
| **PortableGit** | 为终端工具提供 `bash.exe`，并为会话内克隆提供 `git`。在安装时配置，不由 `dep_ensure` 处理。 |
| **Node.js 22** | 浏览器工具 (`agent-browser`)、TUI 的 Web 桥接和 WhatsApp 桥接所必需。 |
| **ffmpeg** | 用于 TTS / 语音消息的音频格式转换。 |
| **ripgrep** | 快速文件搜索 — 如果不可用则回退到 `grep`。 |
| **npm 包** | `agent-browser`、Playwright Chromium 以及任何每个工具集的 Node 依赖项在首次使用浏览器工具时安装一次。 |

每个依赖项都有一个 `shutil.which(...)` 风格的检查；如果缺少二进制文件且运行是交互式的，`dep_ensure` 会提供安装选项（将实际的安装逻辑委托给 `scripts\install.ps1 -ensure <dep>`）。非交互式运行（消息网关、定时任务、无头桌面启动）会跳过提示，并显示清晰的 `此功能需要 <dep>` 错误。

## 安装程序实际做了什么

从上到下，按顺序：

1.  **引导 `uv`** — Astral 的快速 Python 管理器。安装到 `%USERPROFILE%\.local\bin`。
2.  **通过 `uv` 安装 Python 3.11**。不需要现有的 Python。
3.  **安装 Node.js 22**（如果可用则使用 winget，否则将便携式 Node tarball 解压到 `%LOCALAPPDATA%\hermes\node` 下）。用于浏览器工具和 WhatsApp 桥接。
4.  **安装便携式 Git** — 如果 `git` 已经在 PATH 上，安装程序会使用它；否则它会下载一个精简的、自包含的 **PortableGit**（约 45 MB，来自官方的 `git-for-windows` 发行版）到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限，没有 Windows 安装程序注册表，不会干扰机器上的任何其他内容。
5.  **克隆仓库**到 `%LOCALAPPDATA%\hermes\hermes-agent` 并在其中创建一个虚拟环境。
6.  **分层 `uv pip install`** — 首先尝试 `.[all]`，如果 `git+https` 依赖项在受速率限制的 GitHub 上不稳定，则回退到逐渐变小的集合（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。防止“单个不稳定依赖导致你降级到最小安装”的故障模式。
7.  **根据 `.env` 自动安装消息 SDK** — 如果存在 `TELEGRAM_BOT_TOKEN` / `DISCORD_BOT_TOKEN` / `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `WHATSAPP_ENABLED`，则运行 `python -m ensurepip --upgrade` 和有针对性的 `pip install` 调用，以便每个平台的 SDK 实际上可以导入。
8.  **设置 `HERMES_GIT_BASH_PATH`** 为解析后的 `bash.exe`，以便 Hermes 在新 shell 中确定性地找到它。
9.  **将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH** — 在你打开新终端后暴露 `hermes` 命令。
10. **运行 `hermes setup`** — 正常的首次运行向导（模型、提供商、工具集）。使用 `-SkipSetup` 跳过。
:::tip 在 Windows 上跳过提供商配置的麻烦
原生 Windows 版本仍处于早期测试阶段，为每个工具单独设置 API 密钥（Firecrawl、FAL、Browser Use、OpenAI TTS）是让 Agent 变得有用的过程中最繁琐的部分。订阅 [Nous Portal](/docs/user-guide/features/tool-gateway) 可以通过一次 OAuth 登录，覆盖模型**以及**所有这些工具。安装程序完成后，运行 `hermes setup --portal` 即可完成所有配置。
:::

## 功能支持矩阵

除了仪表板的嵌入式终端窗格外，所有功能都可在原生 Windows 上运行。

| 功能 | 原生 Windows | WSL2 |
|---|---|---|
| CLI (`hermes chat`, `hermes setup`, `hermes gateway`, …) | ✓ | ✓ |
| 交互式 TUI (`hermes --tui`) | ✓ | ✓ |
| 消息网关 (Telegram, Discord, Slack, WhatsApp, 15+ 平台) | ✓ | ✓ |
| 定时任务调度器 | ✓ | ✓ |
| 浏览器工具 (通过 Node 的 Chromium) | ✓ | ✓ |
| MCP 服务器 (stdio 和 HTTP) | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server | ✓ | ✓ (通过 WSL 网络) |
| Web 仪表板 (会话、任务、指标、配置) | ✓ | ✓ |
| 仪表板 `/chat` 嵌入式终端窗格 | ✗ (需要 POSIX PTY) | ✓ |
| 登录时自动启动 | ✓ (schtasks) | ✓ (systemd) |

仪表板的 `/chat` 标签页通过 POSIX PTY (`ptyprocess`) 嵌入了一个真实的终端。原生 Windows 没有等效的原语；Python 的 `pywinpty` / Windows ConPTY 可以工作，但需要单独实现——这留作未来的工作。**仪表板的其余部分在原生 Windows 上正常工作**——只有那个标签页会显示“请使用 WSL2”的横幅。

## Hermes 如何在 Windows 上运行 shell 命令

Hermes 的终端工具通过 **Git Bash** 运行命令，这与 Claude Code 使用的策略相同。这绕过了 POSIX 与 Windows 之间的差异，无需重写每个工具。

`bash.exe` 的查找顺序：

1. 如果设置了 `HERMES_GIT_BASH_PATH` 环境变量，则使用它。
2. `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe` (安装程序管理的 PortableGit)。
3. `%LOCALAPPDATA%\hermes\git\bin\bash.exe` (较旧的 Git-for-Windows 布局)。
4. 系统 Git-for-Windows 安装 (`%ProgramFiles%\Git\bin\bash.exe` 等)。
5. 作为最后手段，使用 PATH 上的 MSYS2、Cygwin 或任何 `bash.exe`。

安装程序会显式设置 `HERMES_GIT_BASH_PATH`，这样新的 PowerShell 会话就不需要重新查找。如果你想让 Hermes 使用特定的 bash（例如，你的系统 Git Bash 或通过符号链接的 WSL 托管的 bash），可以覆盖此变量。

**陷阱：** MinGit 的布局与完整的 Git-for-Windows 安装程序不同——bash 位于 `usr\bin\bash.exe` 下，而不是 `bin\bash.exe`。Hermes 会检查两者。如果你手动解压 MinGit zip 文件，请确保选择**非 busybox** 版本 (`MinGit-*-64-bit.zip`，而不是 `MinGit-*-busybox*.zip`)——busybox 版本提供的是 `ash` 而不是 `bash`，并且缺少大多数 coreutils。

## Windows 上的 UTF-8 控制台

Python 在 Windows 上的默认标准输入/输出使用控制台的活动代码页（通常是 cp1252 或 cp437）。Hermes 的横幅、斜杠命令列表、工具反馈、Rich 面板和技能描述都包含 Unicode。如果不进行干预，任何这些内容都会因 `UnicodeEncodeError: 'charmap' codec can't encode character…` 而崩溃。

修复方法在 `hermes_cli/stdio.py::configure_windows_stdio()` 中，该函数在每个入口点 (`cli.py::main`, `hermes_cli/main.py::main`, `gateway/run.py::main`) 的早期被调用。它：

1. 通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 将控制台代码页切换为 CP_UTF8 (65001)。
2. 使用 `errors='replace'` 将 `sys.stdout` / `sys.stderr` / `sys.stdin` 重新配置为 UTF-8。
3. 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1` (通过 `setdefault`，因此用户显式设置的值优先)，以便子 Python 进程继承 UTF-8 设置。
4. 如果 `EDITOR` 和 `VISUAL` 均未设置，则设置 `EDITOR=notepad` (参见下面的编辑器部分)。

此操作是幂等的。在非 Windows 系统上不执行任何操作。

**选择退出：** 在环境中设置 `HERMES_DISABLE_WINDOWS_UTF8=1` 将回退到旧的 cp1252 标准输入/输出路径。这对于二分查找编码错误很有用；但在正常操作中不太可能是正确的设置。

## 编辑器 (`Ctrl-X Ctrl-E`, `/edit`)

在 #21561 之前，在 Windows 上按 `Ctrl-X Ctrl-E` 或输入 `/edit` 会静默地不执行任何操作。prompt_toolkit 有一个硬编码的 POSIX 绝对路径回退列表 (`/usr/bin/nano`, `/usr/bin/pico`, `/usr/bin/vi`, …)，这在 Windows 上永远无法解析——即使安装了完整的 Git for Windows。

Hermes 的 Windows 标准输入/输出垫片现在将 `EDITOR=notepad` 设置为默认值。记事本随每个 Windows 安装附带，并且可以作为阻塞式编辑器工作——`subprocess.call(["notepad", file])` 会阻塞直到窗口关闭。

**用户覆盖设置仍然优先**（它们在 setdefault 之前被检查）：

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |

VS Code 的 `--wait` 标志至关重要——没有它，编辑器会立即返回，而 Hermes 会得到一个空缓冲区。

在你的 PowerShell 配置文件中永久设置它：

```powershell
# 在 $PROFILE 中
$env:EDITOR = "code --wait"
```

或者在系统设置中将其设置为用户环境变量，这样每个新的 shell 都会获取它。

## 在 CLI 中使用 `Ctrl+Enter` 换行

Windows Terminal 将 `Ctrl+Enter` 作为专用键序列传递。Hermes 将其绑定到“插入换行符”，这样你就可以在 CLI 中编写多行提示词，而无需回退到 `Esc` 然后 `Enter`。在 Windows Terminal、VS Code 集成终端以及任何支持 VT 转义序列的现代 Windows 控制台主机中均可使用。

在传统的 `cmd.exe` 控制台上，`Ctrl+Enter` 会退化为普通的 `Enter`——请改用 `Esc Enter`，或者升级到 Windows Terminal（它是免费的，并且在 Windows 11 上默认安装）。

## 在 Windows 登录时运行消息网关

在 Windows 上，`hermes gateway install` 使用**计划任务**并辅以启动文件夹回退——无需管理员权限。

### 安装

```powershell
hermes gateway install
```

底层发生的情况：

1. `schtasks /Create /SC ONLOGON /RL LIMITED /TN HermesGateway` —— 注册一个在你登录时运行的任务，具有标准（非提升）权限。没有 UAC 提示。
2. 如果计划任务被组策略阻止，则回退到将 `start /min cmd.exe /d /c <wrapper>` 快捷方式写入 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`。效果相同，但稍微粗糙一些。
3. 通过 `pythonw.exe`（而不是 `python.exe`）**分离**启动消息网关。`pythonw.exe` 没有附加控制台，这使其免受来自同进程组中其他进程的 `CTRL_C_EVENT` 广播的影响（这是一个实际问题，过去当你在同一进程组中对任何进程按 Ctrl+C 时，会杀死消息网关）。
启动时使用的标志：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

### 管理

```powershell
hermes gateway status      # 合并视图：计划任务 + 启动文件夹 + 运行中的 PID
hermes gateway start       # 立即启动计划任务
hermes gateway stop        # 优雅的 SIGTERM 等效操作（通过 psutil 的 TerminateProcess）
hermes gateway restart
hermes gateway uninstall   # 移除计划任务条目、启动快捷方式、pid 文件
```

`hermes gateway status` 是幂等的——连续调用一千次也绝不会意外杀死消息网关。（在 PR #21561 之前，它会通过 `os.kill(pid, 0)` 在 C 语言层面与 `CTRL_C_EVENT` 冲突而静默地杀死进程——如果你关心这个故事，请查看下面的“进程管理内部原理”。）

### 为什么不使用 Windows 服务？

服务需要管理员权限来安装，并且将消息网关的生命周期绑定到机器启动，而不是用户登录。典型的 Hermes 用户希望：登录 → 消息网关可用，注销 → 消息网关消失。计划任务正好能做到这一点，且无需提升权限。如果你真的想要一个服务，可以手动使用 `nssm` 或 `sc create`——但你可能并不需要。

## 数据布局

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git 检出 + venv。可以安全地 `Remove-Item -Recurse` 并重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | PortableGit（仅当安装程序配置了它时）。 |
| `%LOCALAPPDATA%\hermes\node\` | 便携式 Node.js（仅当安装程序配置了它时）。 |
| `%LOCALAPPDATA%\hermes\bin\` | `hermes.cmd` 包装器，已添加到用户 PATH。 |
| `%USERPROFILE%\.hermes\` | 你的配置、认证、技能、会话、日志。**重新安装后保留。** |

这种划分是故意的：`%LOCALAPPDATA%\hermes` 是一次性基础设施（你可以删除它，然后一行命令就能恢复）。`%USERPROFILE%\.hermes` 是你的数据——配置、记忆、技能、会话历史——其结构与 Linux 安装完全相同。在机器之间镜像它，你的 Hermes 就会跟着你移动。

**覆盖 `HERMES_HOME`：** 设置环境变量指向不同的数据目录。与在 Linux 上工作方式相同。

## 浏览器工具

浏览器工具使用 `agent-browser`（一个 Node 辅助程序）来驱动 Chromium。在 Windows 上：

- 安装程序通过 npm 将 `agent-browser` 添加到 PATH。
- `shutil.which("agent-browser", path=...)` 会自动获取 `.cmd` 包装器——`CreateProcessW` 无法执行无扩展名的 shebang 脚本，因此 Hermes 总是解析到 `.CMD` 包装器。不要手动调用 shebang 脚本；始终通过 `.cmd` 包装器。
- Playwright Chromium 在首次运行时自动安装（`npx playwright install chromium`）。如果安装失败，`hermes doctor` 会显示它并给出修复提示。

## 在 Windows 上运行 Hermes —— 实用说明

### 安装后的 PATH

安装程序通过 `[Environment]::SetEnvironmentVariable` 将 `%LOCALAPPDATA%\hermes\bin` 添加到你的**用户 PATH**。现有的终端不会获取这个更改——安装后请打开一个新的 PowerShell 窗口（或 Windows 终端标签页）。关闭并重新打开，不要手动执行 `$env:PATH += …`，除非你知道自己在做什么。

验证：

```powershell
Get-Command hermes        # 应打印 C:\Users\<you>\AppData\Local\hermes\bin\hermes.cmd
hermes --version
```

### 环境变量

Hermes 同时尊重 `$env:X`（进程作用域）和用户环境变量（永久的，在系统属性 → 环境变量中设置）。在 `%USERPROFILE%\.hermes\.env` 中设置 API 密钥是常规路径——与 Linux 相同：

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```

除非你特别希望每个 Windows 进程都能看到它们，否则不要将密钥放在用户环境变量中（这通常不是你想要的）。

### Windows 特定的环境变量

这些只影响原生的 Windows 安装：

| 变量 | 效果 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 的发现。指向任何 bash——完整的 Git-for-Windows、通过符号链接的 WSL bash、MSYS2、Cygwin。安装程序会自动设置此变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设置为 `1` 以禁用 UTF-8 标准输入输出垫片并回退到区域设置代码页。用于二分查找编码错误时很有用。 |
| `EDITOR` / `VISUAL` | 用于 `/edit` 和 `Ctrl-X Ctrl-E` 的编辑器。如果两者都未设置，Hermes 默认为 `notepad`。 |

## 卸载

在 PowerShell 中：

```powershell
hermes uninstall
```

这是干净的路径——移除计划任务条目、启动文件夹快捷方式、`hermes.cmd` 包装器，删除 `%LOCALAPPDATA%\hermes\hermes-agent\`，并修剪用户 PATH。它保留 `%USERPROFILE%\.hermes\`（你的配置、认证、技能、会话、日志）不动，以防你重新安装。

要彻底清除所有内容：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
```

`hermes uninstall` CLI 子命令也处理计划任务条目以不同任务名称注册的情况（旧版安装）——它通过安装路径而不是硬编码的任务名称进行搜索。

## 进程管理内部原理

这是背景材料——除非你在调试“它正在杀死自己”的奇怪问题，否则可以跳过。

在 Linux 和 macOS 上，POSIX 惯用法 `os.kill(pid, 0)` 是一个无操作权限检查：“这个 PID 是否存活并且我可以向它发送信号吗？” 在 Windows 上，Python 的 `os.kill` 将 `sig=0` 映射到 `CTRL_C_EVENT`——它们在整数值 0 处冲突——并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由，这将 Ctrl+C 广播到包含目标 PID 的**整个控制台进程组**。这是 [bpo-14484](https://bugs.python.org/issue14484)，自 2012 年以来一直开放。它不会被修复，因为改变它会破坏依赖当前行为的脚本。

后果：任何通过 `os.kill(pid, 0)` 在 Windows 上执行“检查此 PID 是否存活”的代码路径都会静默地杀死目标。Hermes 将所有此类位置（11 个文件中的 14 处）迁移到了 `gateway.status._pid_exists()`，它使用 `psutil.pid_exists()`（后者在 Windows 上使用 `OpenProcess + GetExitCodeProcess`——不涉及信号）。如果你正在编写插件或补丁，请直接使用 `psutil.pid_exists()` 或 `gateway.status._pid_exists()`——永远不要使用 `os.kill(pid, 0)`。
`scripts/check-windows-footguns.py` 在 CI 中强制执行此规则：任何新的 `os.kill(pid, 0)` 调用都会导致 `Windows footguns (blocking)` 检查失败，除非该行带有 `# windows-footgun: ok — <reason>` 标记。

## 常见问题

**安装后立即出现 `hermes: command not found`。**
打开一个新的 PowerShell 窗口。安装程序已将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH 中，但现有的 shell 需要重启才能生效。在此期间，你可以运行 `& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd"`。

**运行工具时出现 `WinError 193: %1 is not a valid Win32 application`。**
你遇到了一个绕过了 `.cmd` 包装器的 shebang 脚本调用。Hermes 通过 `shutil.which(cmd, path=local_bin)` 解析命令，因此 PATHEXT 会识别 `.CMD` —— 如果你是通过硬编码路径调用工具，请切换到 `.cmd` 变体（例如，使用 `npx.cmd`，而不是 `npx`）。

**`[scriptblock]::Create(...)` 失败并显示 `The assignment expression is not valid`。**
你下载的 `install.ps1` 包含了 UTF-8 BOM。`irm | iex` 形式会自动去除 BOM；`[scriptblock]::Create((irm ...))` 则不会。请使用简单的 `irm | iex` 形式重新运行，或者手动下载脚本并通过 `[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))` 保存为无 BOM 格式。

**重启后消息网关无法保持运行。**
检查 `hermes gateway status` —— 它合并了计划任务条目、启动文件夹快捷方式（如果使用）以及实时 PID。如果计划任务已注册但未运行，可能是组策略阻止了 `ONLOGON` 触发器。运行 `schtasks /Query /TN HermesGateway /V /FO LIST` 查看任务失败原因，或者通过卸载并使用 `HERMES_GATEWAY_FORCE_STARTUP=1` 重新安装，回退到启动文件夹路径。

**设置 `$env:EDITOR` 后，`/edit` 仍然无效。**
你只在当前进程中设置了它；请关闭并重新打开 shell，或者在系统属性 → 环境变量中为用户范围设置。在新的 PowerShell 窗口中用 `echo $env:EDITOR` 验证。

**浏览器工具启动但工具超时。**
Chromium 在首次运行时自动安装。如果安装失败（GitHub 限速、Playwright CDN 故障），请运行 `hermes doctor` —— 它会显示缺失的 Chromium 并打印确切的 `npx playwright install chromium` 命令来修复。

**`agent-browser` 因奇怪的 Node 版本错误而失败。**
安装程序在 `%LOCALAPPDATA%\hermes\node` 中提供了 Node 22，但你的 PATH 中可能首先有一个较旧的系统 Node 18。要么将 Hermes 的 node 目录移到 PATH 的前面，要么如果你不在其他地方使用 Node，可以删除系统安装。

**CLI 中的中文/日文/阿拉伯文字符显示为 `?`。**
UTF-8 标准输入输出包装器未激活。检查 `HERMES_DISABLE_WINDOWS_UTF8` 是否**未**设置（`Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8`）。如果它是空的并且你仍然看到 `?`，可能是控制台主机（非常旧的 `cmd.exe`）根本不支持 UTF-8 —— 请切换到 Windows Terminal。

**消息网关无法发送 Telegram 照片 —— "`BadRequest: payload contains invalid characters`"。**
这与 Windows 无关，但有时会首先在那里出现。通常这意味着你的文件路径在 JSON 正文中包含未转义的反斜杠。Telegram 应该接收 Hermes 规范化的路径，而不是原始的 Windows 路径 —— 如果你在自定义插件中看到此错误，请确保你传递的是 Hermes 提供的路径，而不是来自用户输入的 `str(Path(...))`。

**`git pull` 后出现 "在我的另一台机器上可以工作" 的编码异常。**
如果你在 Windows 上使用非 UTF-8 编辑器（旧版 Windows 上的记事本、某些中文输入法）编辑了 Hermes 配置或技能，文件可能已保存为带 BOM 的格式。Hermes 在大多数配置读取时容忍 `utf-8-sig`，但折叠的 YAML 标量（`description: >`）内部的 BOM 会静默地破坏 YAML 解析。请将文件重新保存为不带 BOM 的纯 UTF-8 格式。

## 下一步

-   **[安装](../getting-started/installation.md)** —— 完整的安装页面，包括 Linux/macOS/WSL2/Termux。
-   **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)** —— 如果你需要 POSIX 语义或仪表板终端窗格。
-   **[CLI 参考](../reference/cli-commands.md)** —— 每个 `hermes` 子命令。
-   **[FAQ](../reference/faq.md)** —— 常见的非 Windows 特定问题。
-   **[消息网关](./messaging/index.md)** —— 在 Windows 上运行 Telegram/Discord/Slack。