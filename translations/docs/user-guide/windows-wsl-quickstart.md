---
title: "Windows (WSL2) 指南"
description: "通过 WSL2 在 Windows 上运行 Hermes Agent — 设置、Windows 与 Linux 之间的文件系统访问、网络以及常见问题"
sidebar_label: "Windows (WSL2)"
sidebar_position: 2
---

# Windows (WSL2) 指南

Hermes Agent 现在同时支持**原生 Windows** 和 **WSL2**。本页介绍 WSL2 路径；关于原生 PowerShell 安装，请参阅专门的 **[Windows (原生) 指南](./windows-native.md)**。

**何时选择 WSL2 而非原生：**
- 您想使用仪表板的嵌入式终端（`/chat` 标签页）— 该窗格需要 POSIX PTY，仅适用于 WSL2。
- 您正在进行大量 POSIX 开发工作，并希望您的 Hermes 会话与您的开发工具共享相同的文件系统/路径。
- 您已经拥有 WSL2 环境，并且不想维护第二个安装。

**何时原生安装即可（或更好）：**
- 交互式聊天、消息网关（Telegram/Discord 等）、定时任务调度器、浏览器工具、MCP 服务器以及大多数 Hermes 功能都可以在 Windows 上原生运行。
- 您不想每次引用文件或打开 URL 时都考虑跨越 WSL↔Windows 边界。

在 WSL2 中，实际上有两台计算机在运行：您的 Windows 主机，以及由 WSL 管理的 Linux 虚拟机。大多数困惑来自于不确定在任何时刻您处于哪一侧。

本指南涵盖了该分割中特别影响 Hermes 的部分：安装 WSL2、在 Windows 和 Linux 之间来回传输文件、双向网络以及人们实际遇到的陷阱。

:::info 简体中文
本页维护了最小安装路径的中文分步指南 — 通过右上角的**语言**菜单切换并选择**简体中文**。
:::

## 为什么选择 WSL2（对比原生 Windows）

原生 Windows 安装直接在 Windows 中运行：您的 Windows 终端（PowerShell、Windows Terminal 等）、Windows 文件系统路径（`C:\Users\…`）和 Windows 进程。Hermes 使用 Git Bash 来运行 shell 命令，这是 Claude Code 和其他 Agent 目前处理 Windows 的方式 — 它无需完全重写即可绕过 POSIX 与 Windows 的差异。

WSL2 在轻量级虚拟机中运行真正的 Linux 内核，因此其中的 Hermes 基本上与在 Ubuntu 上运行相同。当您想要一个真正的 POSIX 环境时，这很有价值：`fork`、`/tmp`、UNIX 套接字、信号语义、基于 PTY 的终端、`bash`/`zsh` 等 shell，以及像 `rg`、`git`、`ffmpeg` 这样在 Linux 上行为一致的工具。

WSL2 的实际影响：

- Hermes CLI、消息网关、会话、记忆、技能和工具运行时都位于 Linux 虚拟机内部。
- Windows 程序（浏览器、原生应用、带有您登录配置文件的 Chrome）位于其外部。
- 每次您希望两者通信时 — 共享文件、打开 URL、控制 Chrome、访问本地模型服务器、将 Hermes 消息网关暴露给您的手机 — 您都需要跨越一个边界。这些边界正是本指南要讨论的内容。

## 安装 WSL2

在 **管理员 PowerShell** 或 Windows Terminal 中：

```powershell
wsl --install
```

在全新的 Windows 10 22H2+ 或 Windows 11 系统上，这将安装 WSL2 内核、虚拟机平台功能以及默认的 Ubuntu 发行版。提示时重新启动。重启后，Ubuntu 将打开并要求输入 Linux 用户名 + 密码 — 这是一个**新的 Linux 用户**，与您的 Windows 帐户无关。

验证您确实在使用 WSL2（而不是旧的 WSL1）：

```powershell
wsl --list --verbose
```

您应该看到 `VERSION  2`。如果某个发行版显示 `VERSION  1`，请转换它：

```powershell
wsl --set-version Ubuntu 2
wsl --set-default-version 2
```

Hermes 在 WSL1 上无法可靠运行 — WSL1 实时转换 Linux 系统调用，并且某些行为（procfs、信号、网络）与真正的 Linux 不同。

### 发行版选择

Ubuntu (LTS) 是我们测试的版本。Debian 也可以工作。Arch 和 NixOS 适用于需要它们的人，但单行安装程序假设是基于 Debian 的 `apt` 系统 — 关于该路径，请参阅 [Nix 设置指南](/getting-started/nix-setup)。

### 启用 systemd（推荐）

使用 systemd 管理 Hermes 消息网关（以及您希望保持运行的其他任何东西）更容易。在现代 WSL 上，在您的发行版内部启用它一次：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[interop]
enabled=true
appendWindowsPath=true

[automount]
options = "metadata,umask=22,fmask=11"
EOF
```

然后在 PowerShell 中：

```powershell
wsl --shutdown
```

重新打开您的 WSL 终端。`ps -p 1 -o comm=` 应该打印出 `systemd`。

上面的 `metadata` 挂载选项很重要 — 没有它，`/mnt/c/...` 上的文件无法存储真正的 Linux 权限位，这会破坏在 Windows 路径下的脚本上执行 `chmod +x` 等操作。

### 在 WSL 内部安装 Hermes

一旦您打开了 WSL2 shell：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes
```

安装程序将 WSL2 视为普通的 Linux — 不需要任何 WSL 特定的东西。完整布局请参阅[安装指南](/getting-started/installation)。

## 文件系统：跨越 Windows ↔ WSL2 边界

这是最容易让人困惑的部分。存在**两个文件系统**，您存放文件的位置很重要 — 关系到性能、正确性以及哪些工具可以看到。

### 两个方向

| 方向 | 内部路径 | 您使用的路径 |
|---|---|---|
| 从 WSL 看到的 Windows 磁盘 | `C:\Users\you\Documents` | `/mnt/c/Users/you/Documents` |
| 从 Windows 看到的 WSL 磁盘 | `/home/you/code` | `\\wsl$\Ubuntu\home\you\code`（或在较新版本上为 `\\wsl.localhost\Ubuntu\...`） |

两者都是真实的，两者都有效，但它们**不是同一个文件系统** — 它们在底层通过 9P 网络协议桥接。这具有实际的性能和语义影响。

### 放置 Hermes 和您的项目的位置

**经验法则：将所有类 Linux 的东西放在 Linux 文件系统内部。**

- 您的 Hermes 安装（`~/.hermes/`）— Linux 侧。安装程序已经这样做了。
- 您从 WSL 工作的 git 仓库 — Linux 侧（`~/code/...`，`~/projects/...`）。
- 您的模型、数据集、venvs — Linux 侧。
遵循此规则你将获得：

- **快速 I/O 操作。** 对 `/mnt/c/...` 的操作需要通过 9P 协议，速度比原生 ext4 慢 10–100 倍。在一个包含 1 万个文件的仓库中，在 `~/code` 下感觉瞬间完成的 `git status` 命令，在 `/mnt/c` 下可能需要 15 秒以上。
- **正确的权限。** Linux 权限位在 `/mnt/c` 上只是尽力模拟。像 `ssh` 因“权限错误”拒绝密钥，或 `chmod +x` 静默失败等情况很常见。
- **可靠的文件监视器。** 通过 9P 协议的 inotify 不稳定——文件监视器（开发服务器、测试运行器）经常会错过 `/mnt/c` 上的更改。
- **无大小写敏感性问题。** Windows 路径默认不区分大小写；Linux 区分大小写。同时包含 `Readme.md` 和 `README.md` 的项目，其行为会因你所在的操作系统端而不同。

**仅当**你**需要**文件存在于 Windows 端时才将其放在 `/mnt/c` 上——例如，你想从 Windows GUI 应用程序打开它，或者 Windows Chrome 的 DevTools MCP 需要当前目录是一个 Windows 可访问的路径。

### 文件互传

**从 Windows → 到 WSL：** 最简单的方法是打开资源管理器，在地址栏输入 `\\wsl.localhost\Ubuntu`。然后你可以拖拽文件到 `\home\<you>\...`。或者从 PowerShell：

```powershell
wsl cp /mnt/c/Users/you/Downloads/file.pdf ~/incoming/
```

**从 WSL → 到 Windows：** 复制到 `/mnt/c/Users/<you>/...`，它会立即出现在 Windows 资源管理器中：

```bash
cp ~/reports/output.pdf /mnt/c/Users/you/Desktop/
```

**在 Windows 应用程序中打开 WSL 文件**（GUI 编辑器、浏览器等）：使用 `explorer.exe` 或 `wslview`：

```bash
sudo apt install wslu     # 一次性安装——提供 wslview、wslpath、wslopen 等工具
wslview ~/reports/output.pdf    # 使用 Windows 默认处理程序打开
explorer.exe .                  # 在 Windows 资源管理器中打开当前 WSL 目录
```

**在两个系统间转换路径：**

```bash
wslpath -w ~/code/project        # → \\wsl.localhost\Ubuntu\home\you\code\project
wslpath -u 'C:\Users\you'        # → /mnt/c/Users/you
```

### 换行符、BOM 和 git

如果你在 Windows 端使用 Windows 编辑器编辑文件，它们可能会获得 `CRLF` 换行符。当 Linux 端的 `bash` 或 Python 读取它们时，shell 脚本会因 `bad interpreter: /bin/bash^M` 而中断，Python 可能在包含 BOM 的 `.env` 文件上失败。

解决方法是在 WSL 内部（而不是在 Windows 上）进行合理的 git 配置：

```bash
git config --global core.autocrlf input
git config --global core.eol lf
```

对于已经包含 CRLF 的文件：

```bash
sudo apt install dos2unix
dos2unix path/to/script.sh
```

### “在 WSL 内部克隆还是在 `/mnt/c` 上克隆？”

在 WSL 内部克隆。除非有特定理由不这样做，否则总是如此。典型的 Hermes 工作流（`hermes chat`、对仓库进行 `rg`/`ripgrep` 的工具调用、文件监视器、后台消息网关）在 `~/code/myrepo` 上比在 `/mnt/c/Users/you/myrepo` 上要快得多且可靠得多。

一个例外：**启动 Windows 二进制文件的 MCP 桥接。** 如果你通过 `cmd.exe` 使用 `chrome-devtools-mcp`（参见 [MCP 指南：WSL → Windows Chrome](/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)），如果 Hermes 的当前工作目录是 `~`，Windows 可能会发出 `UNC` 警告。在这种情况下，从 `/mnt/c/` 下的某个位置启动 Hermes，以便 Windows 进程有一个带盘符的当前工作目录。

## 网络：WSL ↔ Windows

WSL2 在一个轻量级虚拟机中运行，拥有自己的网络栈。这意味着 WSL 内部的 `localhost` **与** Windows 上的 `localhost` **不同**——从网络的角度看，它们是两个独立的主机。对于每个服务，你需要决定流量流向哪个方向，并选择正确的桥接方式。

有两种情况经常出现。

### 情况 1 — WSL 中的 Hermes 与 Windows 上的服务通信

最常见的情况：你在 **Windows 上运行 Ollama、LM Studio 或 llama-server**，而 Hermes（在 WSL 内部）需要访问它。

关于此的权威指南位于提供商集成指南中：**[WSL2 网络用于本地模型 →](/integrations/providers#wsl2-networking-windows-users)**

简短版本：

- **Windows 11 22H2+：** 启用镜像网络模式（在 `%USERPROFILE%\.wslconfig` 中设置 `networkingMode=mirrored`，然后执行 `wsl --shutdown`）。之后 `localhost` 在两个方向上都能工作。
- **Windows 10 或更早版本：** 使用 Windows 主机 IP（WSL 虚拟网络的默认网关），并确保 Windows 上的服务器绑定到 `0.0.0.0`，而不仅仅是 `127.0.0.1`。Windows 防火墙通常也需要为该端口添加规则。

完整的表格（Ollama / LM Studio / vLLM / SGLang 绑定地址、防火墙规则单行命令、动态 IP 助手、Hyper-V 防火墙变通方案），请点击上面的链接——此处不再赘述。

### 情况 2 — Windows（或你的局域网）上的某个东西与 WSL 中的 Hermes 通信

这是相反的方向，在其他地方文档较少，但在以下情况下需要：

- 从 Windows 浏览器使用 Hermes **Web 仪表板**。
- 从 Windows 端工具使用 **OpenAI 兼容的 API 服务器**（由 `hermes gateway` 在 `API_SERVER_ENABLED=true` 时暴露）。参见 [API 服务器功能页面](/user-guide/features/api-server)。
- 测试一个 **消息网关**（Telegram、Discord 等），其中平台会 ping 一个本地 webhook URL——通常你会使用 `cloudflared`/`ngrok` 而不是原始的端口转发。

#### 子情况 2a：从 Windows 主机本身

在 **启用了镜像模式的 Windows 11 22H2+** 上，无需任何操作。在 WSL 中绑定到 `0.0.0.0:8080`（甚至 `127.0.0.1:8080`）的进程，可以从 Windows 浏览器通过 `http://localhost:8080` 访问。WSL 会自动将绑定发布回主机。

在 **NAT 模式**（Windows 10 / 较旧的 Windows 11）下，WSL2 中默认的“localhost 转发”通常会将 Linux 端的 `127.0.0.1` 绑定转发到 Windows 的 `localhost`，因此以 `--host 127.0.0.1` 启动的 Hermes 服务通常可以从 Windows 通过 `http://localhost:PORT` 访问。如果不行：

- 在 WSL 内部显式绑定到 `0.0.0.0`。
- 使用 `ip -4 addr show eth0 | grep inet` 查找 WSL 虚拟机的 IP，然后从 Windows 访问该 IP。

#### 子情况 2b：从局域网上的另一台设备（手机、平板电脑、另一台 PC）
这才是真正的痛点。流量路径是 **局域网设备 → Windows 主机 → WSL 虚拟机**，你必须同时设置这两个跳转：

1. **在 WSL 内绑定到所有接口。** 监听在 `127.0.0.1` 的进程永远无法从虚拟机外部访问。请使用 `0.0.0.0`。

2. **端口转发 Windows → WSL 虚拟机。** 在镜像模式下这是自动的。在 NAT 模式下，你必须自己为每个端口在管理员 PowerShell 中操作：

   ```powershell
   # 获取 WSL 虚拟机当前的 IP（在 NAT 模式下，每次 WSL 重启都会变化）
   $wslIp = (wsl hostname -I).Trim().Split(' ')[0]

   # 转发 Windows 端口 8080 → WSL:8080
   netsh interface portproxy add v4tov4 `
     listenaddress=0.0.0.0 listenport=8080 `
     connectaddress=$wslIp connectport=8080

   # 允许通过 Windows 防火墙
   New-NetFirewallRule -DisplayName "Hermes WSL 8080" `
     -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```

   稍后可以使用 `netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8080` 移除规则。

3. **将局域网设备指向 `http://<windows-lan-ip>:8080`。**

因为在 NAT 模式下，WSL 虚拟机的 IP 在每次重启时都会漂移，所以一次性规则只能维持到下一次 `wsl --shutdown`。对于任何需要持久化的场景，要么使用镜像模式，要么将端口代理步骤放入一个在 Windows 登录时运行的脚本中。

对于来自云消息提供商（Telegram `setWebhook`、Slack 事件等）的 Webhook，不要费力配置端口转发——使用 `cloudflared` 隧道。请参阅 [webhooks 指南](/user-guide/messaging/webhooks)。

## 在 Windows 上长期运行 Hermes 服务

Hermes 的 [工具网关](/user-guide/features/tool-gateway) 和 API 服务器是长期运行的进程。在 WSL2 中，你有几个选项来保持它们运行。

### 用于快速打开 Hermes 的桌面快捷方式

如果你只想要一个双击启动器来打开交互式 Hermes shell，可以在 Windows 端创建它，并让它为你跳转到 WSL：

1. 在 Windows 桌面上右键单击，选择 **新建 -> 快捷方式**。
2. 对于目标，使用你的发行版名称（如果需要，请替换 `Ubuntu`）：

   ```text
   wt.exe -w 0 -p "Ubuntu" wsl.exe -d Ubuntu --cd ~ -- bash -ic "hermes"
   ```

3. 将其命名为一个明显的名称，例如 `Hermes`。

这会打开 Windows 终端，启动你的 WSL 发行版，将你放入 Linux 家目录，并启动 Hermes。如果 `hermes` 尚未在 PATH 中，请手动打开一次 WSL 并运行 `source ~/.bashrc`，或者将命令替换为项目检出目录内的 `uv run hermes`。

可选优化：

- **自定义图标：** 打开 **属性 -> 更改图标**，并将其指向一个 `.ico` 文件，例如仓库中的 Hermes 网站图标。
- **固定启动器：** 一旦快捷方式生效，将其固定到“开始”菜单或任务栏，这样你就不必再次查找它。

### 在 WSL 内使用 systemd（推荐）

如果你按照上面的设置部分启用了 systemd，`hermes gateway` 和 API 服务器的工作方式与在任何 Linux 机器上相同。使用网关设置向导：

```bash
hermes gateway setup
```

它会提供安装一个 systemd 用户单元的选项，以便在 WSL 启动时自动启动网关。

### 让 WSL 本身在 Windows 登录时启动

WSL 的虚拟机只在有东西使用它时才保持活动状态。为了在没有终端窗口打开的情况下保持网关可访问，可以通过任务计划程序在 Windows 登录时启动一个 WSL 进程：

- **触发器：** 登录时（你的用户）。
- **操作：** 启动程序
  - 程序：`C:\Windows\System32\wsl.exe`
  - 参数：`-d Ubuntu --exec /bin/sh -c "sleep infinity"`

这可以保持虚拟机存活，以便 systemd 管理的网关保持运行。在 Windows 11 上，较新的 `wsl --install --no-launch` + 自动启动流程也有效；`sleep infinity` 技巧是便携版本。

## GPU 透传（本地模型）

WSL2 从 WSL 内核 5.10.43+ 开始原生支持 **NVIDIA** GPU——在 Windows 上安装标准的 NVIDIA 驱动程序（**不要**在 WSL 内安装 Linux NVIDIA 驱动程序），WSL 内的 `nvidia-smi` 就能看到 GPU。从那里开始，CUDA 工具包、`torch`、`vllm`、`sglang` 和 `llama-server` 会像往常一样针对真实的 GPU 构建。

AMD ROCm 和 Intel Arc 在 WSL2 内的支持仍在发展中，并且不在 Hermes 的测试矩阵内——它可能适用于当前的驱动程序，但我们没有推荐的方案。

如果你运行的是 **Windows 原生** 的本地模型服务器（Windows 版 Ollama、LM Studio），它已经通过 Windows 驱动程序使用你的 GPU，那么你完全不需要 WSL GPU 透传——只需按照上面的案例 1 操作，并从 WSL 通过网络访问它。

## 常见陷阱

**"Connection refused" 连接到我在 Windows 上托管的 Ollama / LM Studio。**
请参阅 [WSL2 网络](/integrations/providers#wsl2-networking-windows-users)。百分之九十的情况下，服务器绑定到了 `127.0.0.1`，需要改为 `0.0.0.0`（Ollama：`OLLAMA_HOST=0.0.0.0`），或者你缺少防火墙规则。

**在仓库中执行 `git status` / `hermes chat` 极其缓慢。**
你可能在 `/mnt/c/...` 下工作。将仓库移动到 `~/code/...`（Linux 端）。速度会快几个数量级。

**脚本出现 `bad interpreter: /bin/bash^M`。**
来自 Windows 编辑器的 CRLF 行尾。使用 `dos2unix script.sh`，并在你的 WSL git 配置中设置 `core.autocrlf input`。

**通过 MCP 启动的 Windows 二进制文件发出 "UNC paths are not supported" 警告。**
Hermes 的当前工作目录在 Linux 文件系统内，而 Windows 的 `cmd.exe` 不知道如何处理它。对于该会话，从 `/mnt/c/...` 启动 Hermes，或者使用一个包装器，在调用 Windows 可执行文件之前 `cd` 到一个 Windows 可访问的路径。

**睡眠/休眠后时钟漂移。**
WSL2 的时钟在主机从睡眠恢复后可能会滞后几分钟，这会破坏任何基于证书的操作（OAuth、HTTPS API）。按需修复：

```bash
sudo hwclock -s
```

或者安装 `ntpdate` 并在登录时运行它。

**启用镜像模式后，或连接 VPN 后，DNS 停止工作。**
镜像模式将主机的网络设置代理到 WSL 中——如果 Windows DNS 有问题（VPN 分流隧道、公司解析器），WSL 会继承这些问题。解决方法：手动覆盖 `resolv.conf`（在 `/etc/wsl.conf` 中设置 `generateResolvConf=false`，然后用 `1.1.1.1` 或你的 VPN 的 DNS 编写你自己的 `/etc/resolv.conf`）。
**运行安装程序后找不到 `hermes` 命令。**
安装程序通过 `~/.bashrc` 将 `~/.local/bin` 添加到你的 shell 的 PATH 中。你需要 `source ~/.bashrc`（或打开一个新的终端）才能使它在当前会话中生效。

**Windows Defender 对 WSL 文件访问缓慢。**
当从 Windows 访问文件时，Defender 会通过 9P 桥接进行扫描，这放大了 `/mnt/c` 这类跨边界访问的缓慢问题。如果你只在 WSL 内部操作 WSL 文件，这无关紧要。如果你经常使用 Windows 工具访问 `\\wsl$\...`，请考虑将 WSL 发行版路径从实时扫描中排除。

**磁盘空间不足。**
WSL2 将其虚拟机磁盘存储为 `%LOCALAPPDATA%\Packages\...` 下的稀疏 VHDX 文件。它会增长，但当你删除文件时不会自动收缩。要回收空间：先执行 `wsl --shutdown`，然后在管理员 PowerShell 中运行 `Optimize-VHD -Path <path-to-ext4.vhdx> -Mode Full`（需要 Hyper-V 工具）——或者使用 WSL 文档中记录的更简单的 `diskpart` 方法。

## 下一步

-   **[安装](/getting-started/installation)** — 实际的安装步骤（Linux/WSL2/Termux 都使用相同的安装程序）。
-   **[集成 → 提供商 → WSL2 网络](/integrations/providers#wsl2-networking-windows-users)** — 关于本地模型服务器网络配置的权威深入指南。
-   **[MCP 指南 → WSL → Windows Chrome](/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)** — 从 WSL 中的 Hermes 控制你已登录的 Windows Chrome。
-   **[工具网关](/user-guide/features/tool-gateway)** 和 **[Web 仪表板](/user-guide/features/web-dashboard)** — 你最常希望从 WSL 暴露给网络其他部分的长期运行服务。