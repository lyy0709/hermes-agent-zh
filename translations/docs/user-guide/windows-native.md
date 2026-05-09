---
title: "Windows（原生）指南 — 早期测试版"
description: "早期测试版：在 Windows 10 / 11 上原生运行 Hermes Agent — 安装、功能矩阵、UTF-8 控制台、Git Bash、将消息网关作为计划任务、编辑器处理、PATH、卸载以及常见问题"
sidebar_label: "Windows（原生）— 测试版"
sidebar_position: 3
---

# Windows（原生）指南 — 早期测试版

:::warning 早期测试版
原生 Windows 支持是**早期测试版**。它可以安装、运行并通过我们的 Windows 隐患检查，但尚未像我们的 Linux/macOS/WSL2 路径那样经过大规模实际测试。请预期会遇到粗糙之处 — 尤其是在子进程处理、路径特性和非 ASCII 控制台输出方面。当你遇到问题时，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)并提供复现步骤。如果你今天就需要一个经过实战考验的设置，请改用[在 WSL2 下的 Linux/macOS 安装程序](./windows-wsl-quickstart.md)。
:::

Hermes 可以在 Windows 10 和 Windows 11 上原生运行 — 无需 WSL、Cygwin 或 Docker。本页是深入探讨：哪些功能可以原生运行，哪些仅限 WSL，安装程序实际做了什么，以及你可能需要调整的 Windows 特定选项。

如果你只想安装，[落地页](/)或[安装页面](../getting-started/installation#windows-native-powershell--early-beta)上的一行命令就是你所需要的。当你遇到意外情况时，再回到这里。

:::tip 想要改用 WSL？
如果你更喜欢真正的 POSIX 环境（用于仪表板的嵌入式终端、`fork` 语义、Linux 风格的文件监视器等），请参阅 **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)**。两者可以干净地共存：原生数据位于 `%LOCALAPPDATA%\hermes` 下，WSL 数据位于 `~/.hermes` 下。
:::

## 快速安装

打开 **PowerShell**（或 Windows 终端）并运行：

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

无需管理员权限。安装程序会安装到 `%LOCALAPPDATA%\hermes\` 并将 `hermes` 添加到你的**用户 PATH** — 安装完成后请打开一个新的终端。

**安装程序选项**（需要脚本块形式来传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆特定分支（用于测试 PR） |
| `-NoVenv` | 关闭 | 跳过 venv 创建（高级 — 自行管理 Python） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码位置 |

## 安装程序实际做了什么

按顺序，从上到下：

1.  **引导 `uv`** — Astral 的快速 Python 管理器。安装到 `%USERPROFILE%\.local\bin`。
2.  **通过 `uv` 安装 Python 3.11**。无需现有 Python。
3.  **安装 Node.js 22**（如果可用则使用 winget，否则使用解压到 `%LOCALAPPDATA%\hermes\node` 下的便携式 Node 压缩包）。用于浏览器工具和 WhatsApp 桥接。
4.  **安装便携式 Git** — 如果 `git` 已在 PATH 上，安装程序会使用它；否则会下载一个精简、自包含的 **PortableGit**（约 45 MB，来自官方的 `git-for-windows` 版本）到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限，无 Windows 安装程序注册表，不干扰系统上的任何其他内容。
5.  **克隆仓库**到 `%LOCALAPPDATA%\hermes\hermes-agent` 并在其中创建虚拟环境。
6.  **分层 `uv pip install`** — 首先尝试 `.[all]`，如果某个 `git+https` 依赖因 GitHub 速率限制而失败，则回退到逐步更小的集合（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。防止“单个依赖失败导致你回退到最小安装”的故障模式。
7.  **根据 `.env` 自动安装消息 SDK** — 如果存在 `TELEGRAM_BOT_TOKEN` / `DISCORD_BOT_TOKEN` / `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `WHATSAPP_ENABLED`，则运行 `python -m ensurepip --upgrade` 和有针对性的 `pip install` 调用，以便每个平台的 SDK 实际上可以导入。
8.  **设置 `HERMES_GIT_BASH_PATH`** 为解析后的 `bash.exe`，以便 Hermes 在新的 shell 中确定性地找到它。
9.  **将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH** — 在你打开新终端后暴露 `hermes` 命令。
10. **运行 `hermes setup`** — 正常的首次运行向导（模型、提供商、工具集）。使用 `-SkipSetup` 跳过。

## 功能矩阵

除了仪表板的嵌入式终端窗格外，所有功能都可以在 Windows 上原生运行。

| 功能 | 原生 Windows | WSL2 |
|---|---|---|
| CLI (`hermes chat`, `hermes setup`, `hermes gateway`, …) | ✓ | ✓ |
| 交互式 TUI (`hermes --tui`) | ✓ | ✓ |
| 消息网关 (Telegram, Discord, Slack, WhatsApp, 15+ 平台) | ✓ | ✓ |
| 定时任务调度器 | ✓ | ✓ |
| 浏览器工具（通过 Node 的 Chromium） | ✓ | ✓ |
| MCP 服务器（stdio 和 HTTP） | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server | ✓ | ✓（通过 WSL 网络） |
| Web 仪表板（会话、作业、指标、配置） | ✓ | ✓ |
| 仪表板 `/chat` 嵌入式终端窗格 | ✗（需要 POSIX PTY） | ✓ |
| 登录时自动启动 | ✓（计划任务） | ✓（systemd） |

仪表板的 `/chat` 标签页通过 POSIX PTY (`ptyprocess`) 嵌入了一个真正的终端。原生 Windows 没有等效的原语；Python 的 `pywinpty` / Windows ConPTY 可以工作，但这是一个独立的实现 — 视为未来的工作。**仪表板的其余部分可以原生工作** — 只有那个标签页会显示“为此使用 WSL2”的横幅。

## Hermes 如何在 Windows 上运行 shell 命令

Hermes 的终端工具通过 **Git Bash** 运行命令，与 Claude Code 使用的策略相同。这避免了 POSIX 与 Windows 之间的差异，而无需重写每个工具。

`bash.exe` 的解析顺序：

1.  如果设置了 `HERMES_GIT_BASH_PATH` 环境变量，则使用它。
2.  `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe`（安装程序管理的 PortableGit）。
3.  `%LOCALAPPDATA%\hermes\git\bin\bash.exe`（较旧的 Git-for-Windows 布局）。
4.  系统 Git-for-Windows 安装（`%ProgramFiles%\Git\bin\bash.exe` 等）。
5.  MSYS2、Cygwin 或 PATH 上的任何 `bash.exe` 作为最后手段。
安装程序会显式设置 `HERMES_GIT_BASH_PATH`，这样新的 PowerShell 会话就不需要重新查找。如果你想让 Hermes 使用特定的 bash（例如，你系统上的 Git Bash 或通过符号链接的 WSL bash），可以覆盖此设置。

**陷阱：** MinGit 的布局与完整的 Git-for-Windows 安装程序不同 —— bash 位于 `usr\bin\bash.exe` 下，而不是 `bin\bash.exe`。Hermes 会检查这两个位置。如果你手动解压 MinGit zip 文件，请确保选择**非 busybox** 版本（`MinGit-*-64-bit.zip`，而不是 `MinGit-*-busybox*.zip`）—— busybox 版本提供的是 `ash` 而不是 `bash`，并且缺少大多数 coreutils。

## Windows 上的 UTF-8 控制台

Python 在 Windows 上的默认标准输入/输出使用控制台的活动代码页（通常是 cp1252 或 cp437）。Hermes 的横幅、斜杠命令列表、工具反馈、Rich 面板和技能描述都包含 Unicode。如果不进行干预，任何这些内容都会因 `UnicodeEncodeError: 'charmap' codec can't encode character…` 而崩溃。

修复方法在 `hermes_cli/stdio.py::configure_windows_stdio()` 中，该函数在每个入口点（`cli.py::main`、`hermes_cli/main.py::main`、`gateway/run.py::main`）的早期被调用。它执行以下操作：

1.  通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 将控制台代码页切换到 CP_UTF8 (65001)。
2.  使用 `errors='replace'` 将 `sys.stdout` / `sys.stderr` / `sys.stdin` 重新配置为 UTF-8。
3.  设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`（通过 `setdefault`，因此用户显式设置的值优先），以便子 Python 进程继承 UTF-8 设置。
4.  如果既未设置 `EDITOR` 也未设置 `VISUAL`，则设置 `EDITOR=notepad`（参见下面的编辑器部分）。

此操作是幂等的。在非 Windows 系统上不执行任何操作。

**选择退出：** 在环境变量中设置 `HERMES_DISABLE_WINDOWS_UTF8=1` 将回退到旧的 cp1252 标准输入/输出路径。这对于二分查找编码错误很有用；但在正常操作中不太可能是正确的设置。

## 编辑器 (`Ctrl-X Ctrl-E`, `/edit`)

在 PR #21561 之前，在 Windows 上按 `Ctrl-X Ctrl-E` 或输入 `/edit` 会静默地不执行任何操作。prompt_toolkit 有一个硬编码的 POSIX 绝对路径回退列表（`/usr/bin/nano`、`/usr/bin/pico`、`/usr/bin/vi`、……），这在 Windows 上永远无法解析 —— 即使安装了完整的 Git for Windows。

Hermes 的 Windows 标准输入/输出垫片现在将 `EDITOR=notepad` 设置为默认值。记事本随每个 Windows 安装附带，并且可以作为阻塞式编辑器工作 —— `subprocess.call(["notepad", file])` 会阻塞直到窗口关闭。

**用户覆盖仍然有效**（在 setdefault 之前会检查它们）：

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |

VS Code 上的 `--wait` 标志至关重要 —— 没有它，编辑器会立即返回，而 Hermes 会得到一个空缓冲区。

在你的 PowerShell 配置文件中永久设置它：

```powershell
# 在 $PROFILE 中
$env:EDITOR = "code --wait"
```

或者在系统设置中将其设置为用户环境变量，这样每个新的 shell 都会获取它。

## 在 CLI 中使用 `Ctrl+Enter` 换行

Windows Terminal 将 `Ctrl+Enter` 作为专用键序列传递。Hermes 将其绑定到“插入换行符”，这样你就可以在 CLI 中编写多行提示词，而无需回退到 `Esc` 然后 `Enter`。适用于 Windows Terminal、VS Code 集成终端以及任何支持 VT 转义序列的现代 Windows 控制台主机。

在传统的 `cmd.exe` 控制台上，`Ctrl+Enter` 会退化为普通的 `Enter` —— 请改用 `Esc Enter`，或者升级到 Windows Terminal（它是免费的，并且在 Windows 11 上默认安装）。

## 在 Windows 登录时运行消息网关

Windows 上的 `hermes gateway install` 使用**计划任务**，并带有启动文件夹回退 —— 不需要管理员权限。

### 安装

```powershell
hermes gateway install
```

底层操作：

1.  `schtasks /Create /SC ONLOGON /RL LIMITED /TN HermesGateway` —— 注册一个在你登录时运行的任务，具有标准（非提升）权限。没有 UAC 提示。
2.  如果计划任务被组策略阻止，则回退到将 `start /min cmd.exe /d /c <wrapper>` 快捷方式写入 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`。效果相同，只是稍微粗糙一些。
3.  通过 `pythonw.exe`（而不是 `python.exe`）**分离地**生成消息网关。`pythonw.exe` 没有附加控制台，这使其免受来自同级进程的 `CTRL_C_EVENT` 广播的影响（这是一个实际问题，过去当你在同一进程组中对任何进程按 Ctrl+C 时，会杀死消息网关）。

生成时使用的标志：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

### 管理

```powershell
hermes gateway status      # 合并视图：计划任务 + 启动文件夹 + 运行中的 PID
hermes gateway start       # 立即启动计划任务
hermes gateway stop        # 优雅的 SIGTERM 等效操作（通过 psutil 的 TerminateProcess）
hermes gateway restart
hermes gateway uninstall   # 删除计划任务条目、启动快捷方式、pid 文件
```

`hermes gateway status` 是幂等的 —— 连续调用它一千次，它也永远不会意外杀死消息网关。（在 PR #21561 之前，它会通过 `os.kill(pid, 0)` 在 C 语言级别与 `CTRL_C_EVENT` 冲突而静默地杀死网关 —— 如果你关心这个故事，请参见下面的“进程管理内部原理”。）

### 为什么不使用 Windows 服务？

服务需要管理员权限才能安装，并且将消息网关的生命周期绑定到机器启动，而不是用户登录。典型的 Hermes 用户希望：登录 → 消息网关可用，注销 → 消息网关消失。计划任务正好可以做到这一点，且不需要提升权限。如果你确实想要一个服务，请手动使用 `nssm` 或 `sc create` —— 但你可能不需要。

## 数据布局

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git 检出 + venv。可以安全地 `Remove-Item -Recurse` 并重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | PortableGit（仅当安装程序配置了它时）。 |
| `%LOCALAPPDATA%\hermes\node\` | 便携式 Node.js（仅当安装程序配置了它时）。 |
| `%LOCALAPPDATA%\hermes\bin\` | `hermes.cmd` 垫片，已添加到用户 PATH 中。 |
| `%USERPROFILE%\.hermes\` | 你的配置、认证、技能、会话、日志。**重新安装后保留。** |
这种分离是故意的：`%LOCALAPPDATA%\hermes` 是可丢弃的基础设施（你可以删除它，然后通过一行命令恢复）。`%USERPROFILE%\.hermes` 是你的数据——配置、记忆、技能、会话历史——其结构与 Linux 安装完全相同。在机器之间同步它，你的 Hermes 就会跟着你移动。

**覆盖 `HERMES_HOME`：** 设置环境变量指向不同的数据目录。其工作原理与在 Linux 上相同。

## 浏览器工具

浏览器工具使用 `agent-browser`（一个 Node 辅助程序）来驱动 Chromium。在 Windows 上：

- 安装程序通过 npm 将 `agent-browser` 添加到 PATH。
- `shutil.which("agent-browser", path=...)` 会自动获取 `.cmd` 包装器——`CreateProcessW` 无法执行没有扩展名的 shebang 脚本，因此 Hermes 总是解析到 `.CMD` 包装器。不要手动调用 shebang 脚本；始终通过 `.cmd` 包装器调用。
- Playwright Chromium 在首次运行时自动安装（`npx playwright install chromium`）。如果安装失败，`hermes doctor` 会显示问题并提供修复提示。

## 在 Windows 上运行 Hermes —— 实用说明

### 安装后的 PATH

安装程序通过 `[Environment]::SetEnvironmentVariable` 将 `%LOCALAPPDATA%\hermes\bin` 添加到你的**用户 PATH**。现有的终端不会立即生效——安装后请打开一个新的 PowerShell 窗口（或 Windows Terminal 标签页）。关闭并重新打开，不要手动执行 `$env:PATH += …`，除非你知道自己在做什么。

验证：

```powershell
Get-Command hermes        # 应打印 C:\Users\<you>\AppData\Local\hermes\bin\hermes.cmd
hermes --version
```

### 环境变量

Hermes 同时识别 `$env:X`（进程作用域）和用户环境变量（永久性，在系统属性 → 环境变量中设置）。在 `%USERPROFILE%\.hermes\.env` 中设置 API 密钥是常规路径——与 Linux 相同：

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```

除非你特别希望每个 Windows 进程都能看到它们（通常你并不希望这样），否则不要将密钥放在用户环境变量中。

### Windows 特定的环境变量

这些仅影响原生 Windows 安装：

| 变量 | 作用 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 的发现路径。指向任何 bash——完整的 Git-for-Windows、通过符号链接的 WSL bash、MSYS2、Cygwin。安装程序会自动设置此变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设置为 `1` 以禁用 UTF-8 stdio 垫片并回退到区域设置代码页。用于二分查找编码错误时很有用。 |
| `EDITOR` / `VISUAL` | 用于 `/edit` 和 `Ctrl-X Ctrl-E` 的编辑器。如果两者都未设置，Hermes 默认为 `notepad`。 |

## 卸载

在 PowerShell 中：

```powershell
hermes uninstall
```

这是干净的卸载路径——删除计划任务条目、启动文件夹快捷方式、`hermes.cmd` 包装器，删除 `%LOCALAPPDATA%\hermes\hermes-agent\`，并清理用户 PATH。它会保留 `%USERPROFILE%\.hermes\`（你的配置、认证、技能、会话、日志），以防你重新安装。

要彻底删除所有内容：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
```

`hermes uninstall` CLI 子命令也处理计划任务条目在不同任务名称下注册的情况（旧版安装）——它通过安装路径而不是硬编码的任务名称进行搜索。

## 进程管理内部原理

这是背景材料——除非你在调试“它自己杀死了自己”的奇怪问题，否则可以跳过。

在 Linux 和 macOS 上，POSIX 惯用法 `os.kill(pid, 0)` 是一个无操作权限检查：“这个 PID 是否存活并且我可以向它发送信号吗？” 在 Windows 上，Python 的 `os.kill` 将 `sig=0` 映射到 `CTRL_C_EVENT`——它们在整数值 0 处冲突——并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由，这将 Ctrl+C 广播到包含目标 PID 的**整个控制台进程组**。这是 [bpo-14484](https://bugs.python.org/issue14484)，自 2012 年以来一直开放。它不会被修复，因为改变它会破坏依赖当前行为的脚本。

后果：任何通过 `os.kill(pid, 0)` 在 Windows 上“检查此 PID 是否存活”的代码路径都在默默地杀死目标。Hermes 将所有此类位置（11 个文件中的 14 处）迁移到了 `gateway.status._pid_exists()`，它使用 `psutil.pid_exists()`（在 Windows 上，后者又使用 `OpenProcess + GetExitCodeProcess`——不涉及信号）。如果你正在编写插件或补丁，请直接使用 `psutil.pid_exists()` 或 `gateway.status._pid_exists()`——永远不要使用 `os.kill(pid, 0)`。

`scripts/check-windows-footguns.py` 在 CI 中强制执行此规则：任何新的 `os.kill(pid, 0)` 调用都会导致 `Windows footguns (blocking)` 检查失败，除非该行带有 `# windows-footgun: ok — <reason>` 标记。

## 常见问题

**安装后立即出现 `hermes: command not found`。**
打开一个新的 PowerShell 窗口。安装程序已将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH，但现有的 shell 需要重新启动才能生效。在此期间，你可以运行 `& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd"`。

**运行工具时出现 `WinError 193: %1 is not a valid Win32 application`。**
你遇到了一个绕过了 `.cmd` 包装器的 shebang 脚本调用。Hermes 通过 `shutil.which(cmd, path=local_bin)` 解析命令，因此 PATHEXT 会获取 `.CMD`——如果你通过硬编码路径调用工具，请切换到 `.cmd` 变体（例如，使用 `npx.cmd`，而不是 `npx`）。

**`[scriptblock]::Create(...)` 失败，提示 `The assignment expression is not valid`。**
你下载的 `install.ps1` 带有 UTF-8 BOM。`irm | iex` 形式会自动去除 BOM；`[scriptblock]::Create((irm ...))` 则不会。使用简单的 `irm | iex` 形式重新运行，或者手动下载脚本并通过 `[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))` 保存时不带 BOM。

**重启后消息网关无法保持运行。**
检查 `hermes gateway status`——它合并了计划任务条目、启动文件夹快捷方式（如果使用）和实时 PID。如果计划任务已注册但未运行，组策略可能阻止了 `ONLOGON` 触发器。运行 `schtasks /Query /TN HermesGateway /V /FO LIST` 查看任务的失败原因，或者通过卸载并使用 `HERMES_GATEWAY_FORCE_STARTUP=1` 重新安装来回退到启动文件夹路径。
**`/edit` 在设置 `$env:EDITOR` 后仍然无效。**
你只在当前进程中设置了它；请关闭并重新打开 shell，或者在系统属性 → 环境变量中为用户范围设置。在新的 PowerShell 窗口中用 `echo $env:EDITOR` 验证。

**浏览器工具启动但工具超时。**
Chromium 在首次运行时自动安装。如果安装失败（GitHub 限速、Playwright CDN 故障），请运行 `hermes doctor` —— 它会显示缺失的 Chromium 并打印确切的 `npx playwright install chromium` 命令来修复。

**`agent-browser` 因奇怪的 Node 版本错误而失败。**
安装程序在 `%LOCALAPPDATA%\hermes\node` 处提供了 Node 22，但你的 PATH 中可能首先有一个较旧的系统 Node 18。要么将 Hermes 的 node 目录移到 PATH 的前面，要么如果你不在其他地方使用 Node，就删除系统安装。

**CLI 中的中文/日文/阿拉伯文字符显示为 `?`。**
UTF-8 标准输入输出垫片未激活。检查 `HERMES_DISABLE_WINDOWS_UTF8` 是否**未**设置（`Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8`）。如果它是空的并且你仍然看到 `?`，则控制台主机（非常旧的 `cmd.exe`）可能根本不支持 UTF-8 —— 请切换到 Windows Terminal。

**消息网关无法发送 Telegram 照片 —— "`BadRequest: payload contains invalid characters`"。**
这与 Windows 无关，但有时首先在那里出现。通常这意味着你的文件路径在 JSON 正文中包含未转义的反斜杠。Telegram 应该接收 Hermes 规范化的路径，而不是原始的 Windows 路径 —— 如果你在自定义插件中看到此错误，请确保你传递的是 Hermes 提供的路径，而不是来自用户输入的 `str(Path(...))`。

**`git pull` 后出现 "在我的其他机器上工作正常" 的编码异常。**
如果你使用非 UTF-8 编辑器（旧版 Windows 上的记事本、某些中文输入法）在 Windows 上编辑了 Hermes 配置或技能，文件可能已保存为带 BOM 的格式。Hermes 在大多数配置读取时容忍 `utf-8-sig`，但折叠的 YAML 标量（`description: >`）内部的 BOM 会静默地破坏 YAML 解析。请将文件重新保存为不带 BOM 的纯 UTF-8 格式。

## 后续步骤

-   **[安装](../getting-started/installation.md)** —— 完整的安装页面，包括 Linux/macOS/WSL2/Termux。
-   **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)** —— 如果你需要 POSIX 语义或仪表板终端窗格。
-   **[CLI 参考](../reference/cli-commands.md)** —— 每个 `hermes` 子命令。
-   **[常见问题解答](../reference/faq.md)** —— 常见的非 Windows 特定问题。
-   **[消息网关](./messaging/index.md)** —— 在 Windows 上运行 Telegram/Discord/Slack。