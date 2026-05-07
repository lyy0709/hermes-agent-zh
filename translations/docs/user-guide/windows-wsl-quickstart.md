---
title: "Windows (WSL2) 指南"
description: "通过 WSL2 在 Windows 上运行 Hermes Agent — 设置、Windows 与 Linux 之间的文件系统访问、网络以及常见问题"
sidebar_label: "Windows (WSL2)"
sidebar_position: 2
---

# Windows (WSL2) 指南

Hermes Agent 是在 **Linux** 和 **macOS** 上开发和测试的。不支持原生 Windows — 在 Windows 上，你需要在 **WSL2**（Windows Subsystem for Linux，版本 2）中运行 Hermes。这意味着实际上有两台计算机在运行：你的 Windows 主机，以及一个由 WSL 管理的 Linux 虚拟机。大多数困惑来自于不确定在任何时刻你处于哪一方。

本指南涵盖了这种分离中特别影响 Hermes 的部分：安装 WSL2、在 Windows 和 Linux 之间来回传输文件、双向网络，以及人们实际会遇到的问题。

:::info 简体中文
本页面维护了一个中文版的最小安装路径说明 — 通过右上角的 **语言** 菜单切换并选择 **简体中文**。
:::

## 为什么是 WSL2（而不是“直接用 Windows”）

Hermes 假设一个 POSIX 环境：`fork`、`/tmp`、UNIX 套接字、信号语义、基于 PTY 的终端、像 `bash`/`zsh` 这样的 shell，以及像 `rg`、`git`、`ffmpeg` 这样在 Linux 上表现一致的工具。为原生 Windows 重写这些将是一个完整的移植 — WSL2 为你提供了一个轻量级虚拟机中的真实 Linux 内核，而运行在其中的 Hermes 基本上与在 Ubuntu 上运行相同。

这个选择的实际后果：

- Hermes CLI、消息网关、会话、记忆、技能和工具运行时都存在于 Linux 虚拟机内部。
- Windows 程序（浏览器、原生应用、带有你登录配置文件的 Chrome）存在于其外部。
- 每次你希望两者通信 — 共享文件、打开 URL、控制 Chrome、访问本地模型服务器、将 Hermes 消息网关暴露给你的手机 — 你都需要跨越一个边界。这些边界正是本指南要讨论的内容。

## 安装 WSL2

在 **管理员 PowerShell** 或 Windows 终端中：

```powershell
wsl --install
```

在全新的 Windows 10 22H2+ 或 Windows 11 系统上，这将安装 WSL2 内核、虚拟机平台功能和一个默认的 Ubuntu 发行版。提示时重启。重启后，Ubuntu 将打开并要求输入 Linux 用户名 + 密码 — 这是一个 **新的 Linux 用户**，与你的 Windows 账户无关。

验证你确实在 WSL2 上（而不是旧的 WSL1）：

```powershell
wsl --list --verbose
```

你应该看到 `VERSION  2`。如果某个发行版显示 `VERSION  1`，请转换它：

```powershell
wsl --set-version Ubuntu 2
wsl --set-default-version 2
```

Hermes 在 WSL1 上无法可靠工作 — WSL1 实时翻译 Linux 系统调用，并且某些行为（procfs、信号、网络）与真实 Linux 不同。

### 发行版选择

Ubuntu (LTS) 是我们测试的版本。Debian 也可以工作。Arch 和 NixOS 适合想要它们的人，但单行安装程序假设是 Debian 衍生的 `apt` 系统 — 对于那条路径，请参阅 [Nix 设置指南](/docs/getting-started/nix-setup)。

### 启用 systemd（推荐）

使用 systemd 管理 Hermes 消息网关（以及任何其他你想保持运行的东西）更容易。在现代 WSL 上，在你的发行版内部启用它一次：

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

重新打开你的 WSL 终端。`ps -p 1 -o comm=` 应该打印出 `systemd`。

上面的 `metadata` 挂载选项很重要 — 没有它，`/mnt/c/...` 上的文件无法存储真实的 Linux 权限位，这会破坏诸如在 Windows 路径下的脚本上执行 `chmod +x` 等操作。

### 在 WSL 内部安装 Hermes

一旦你打开了一个 WSL2 shell：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes
```

安装程序将 WSL2 视为普通的 Linux — 不需要任何 WSL 特定的东西。完整布局请参阅 [安装](/docs/getting-started/installation)。

## 文件系统：跨越 Windows ↔ WSL2 边界

这是最容易让人困惑的部分。存在 **两个文件系统**，你把文件放在哪里很重要 — 关系到性能、正确性以及哪些工具可以看到。

### 两个方向

| 方向 | 内部路径 | 你使用的路径 |
|---|---|---|
| Windows 磁盘，从 WSL 中看到 | `C:\Users\you\Documents` | `/mnt/c/Users/you/Documents` |
| WSL 磁盘，从 Windows 中看到 | `/home/you/code` | `\\wsl$\Ubuntu\home\you\code`（或在较新版本上为 `\\wsl.localhost\Ubuntu\...`） |

两者都是真实的，两者都有效，但它们 **不是同一个文件系统** — 它们在底层通过 9P 网络协议桥接。这具有实际的性能和语义后果。

### 将 Hermes 和你的项目放在哪里

**经验法则：将所有 Linux 相关的东西放在 Linux 文件系统内部。**

- 你的 Hermes 安装 (`~/.hermes/`) — Linux 端。安装程序已经这样做了。
- 你从 WSL 工作的 git 仓库 — Linux 端 (`~/code/...`, `~/projects/...`)。
- 你的模型、数据集、虚拟环境 — Linux 端。

遵循此规则你将获得：

- **快速的 I/O。** 在 `/mnt/c/...` 上的操作通过 9P 进行，比原生 ext4 慢 10–100 倍。在一个 1 万个文件的仓库上执行 `git status`，在 `~/code` 下感觉是瞬间的，而在 `/mnt/c` 下可能需要 15 秒以上。
- **正确的权限。** Linux 权限位在 `/mnt/c` 上是最佳努力模拟。像 `ssh` 因“权限错误”拒绝密钥或 `chmod +x` 静默失败等情况很常见。
- **可靠的文件监视器。** 跨 9P 的 inotify 不稳定 — 文件监视器（开发服务器、测试运行器）经常会错过 `/mnt/c` 上的更改。
- **没有大小写敏感性问题。** Windows 路径默认不区分大小写；Linux 区分大小写。同时包含 `Readme.md` 和 `README.md` 的项目，根据你所在的位置，行为会有所不同。

只有当文件 **需要** 存在于 Windows 端时才将其放在 `/mnt/c` 上 — 例如，你希望从 Windows GUI 应用程序打开它，或者 Windows Chrome 的 DevTools MCP 需要当前目录是 Windows 可访问的路径。
### 文件互传

**从 Windows → 到 WSL：** 最简单的方法是打开资源管理器，在地址栏输入 `\\wsl.localhost\Ubuntu`。然后你可以拖放文件到 `\home\<你的用户名>\...`。或者从 PowerShell：

```powershell
wsl cp /mnt/c/Users/you/Downloads/file.pdf ~/incoming/
```

**从 WSL → 到 Windows：** 复制到 `/mnt/c/Users/<你的用户名>/...`，它会立即出现在 Windows 资源管理器中：

```bash
cp ~/reports/output.pdf /mnt/c/Users/you/Desktop/
```

**在 Windows 应用程序（GUI 编辑器、浏览器等）中打开 WSL 文件：** 使用 `explorer.exe` 或 `wslview`：

```bash
sudo apt install wslu     # 只需一次 — 提供 wslview、wslpath、wslopen 等命令
wslview ~/reports/output.pdf    # 使用 Windows 默认程序打开
explorer.exe .                  # 在 Windows 资源管理器中打开当前 WSL 目录
```

**在两个系统之间转换路径：**

```bash
wslpath -w ~/code/project        # → \\wsl.localhost\Ubuntu\home\you\code\project
wslpath -u 'C:\Users\you'        # → /mnt/c/Users/you
```

### 换行符、BOM 和 git

如果你在 Windows 端用 Windows 编辑器编辑文件，它们可能会获得 `CRLF` 换行符。当 Linux 端的 `bash` 或 Python 读取它们时，shell 脚本会因 `bad interpreter: /bin/bash^M` 而中断，Python 也可能在带有 BOM 的 `.env` 文件上失败。

解决方法是在 WSL 内部（而不是在 Windows 上）设置合理的 git 配置：

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

在 WSL 内部克隆。除非有特殊原因，否则总是这样做。典型的 Hermes 工作流（`hermes chat`、对仓库进行 `rg`/`ripgrep` 的工具调用、文件监视器、后台消息网关）针对 `~/code/myrepo` 将比针对 `/mnt/c/Users/you/myrepo` 快得多且可靠得多。

一个例外：**启动 Windows 二进制文件的 MCP 桥接。** 如果你通过 `cmd.exe` 使用 `chrome-devtools-mcp`（参见 [MCP 指南：WSL → Windows Chrome](/docs/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)），如果 Hermes 的当前工作目录是 `~`，Windows 可能会发出 `UNC` 警告。在这种情况下，从 `/mnt/c/` 下的某个位置启动 Hermes，以便 Windows 进程有一个带盘符的当前工作目录。

## 网络：WSL ↔ Windows

WSL2 在一个轻量级虚拟机中运行，拥有自己的网络栈。这意味着 WSL 内部的 `localhost` **与** Windows 上的 `localhost` 不同——从网络的角度看，它们是两个独立的主机。对于每个服务，你需要决定流量流向哪个方向，并选择正确的桥接方式。

有两种情况经常出现。

### 情况 1 — WSL 中的 Hermes 与 Windows 上的服务通信

最常见的情况：你在 **Windows 上运行 Ollama、LM Studio 或 llama-server**，而 Hermes（在 WSL 内部）需要访问它。

关于此问题的权威指南位于提供商指南中：**[WSL2 本地模型网络配置 →](/docs/integrations/providers#wsl2-networking-windows-users)**

简短版本：

- **Windows 11 22H2+：** 启用镜像网络模式（在 `%USERPROFILE%\.wslconfig` 中设置 `networkingMode=mirrored`，然后执行 `wsl --shutdown`）。之后 `localhost` 在两个方向上都有效。
- **Windows 10 或更旧的版本：** 使用 Windows 主机 IP（WSL 虚拟网络的默认网关），并确保 Windows 上的服务器绑定到 `0.0.0.0`，而不仅仅是 `127.0.0.1`。Windows 防火墙通常也需要为该端口添加规则。

完整的表格（Ollama / LM Studio / vLLM / SGLang 绑定地址、防火墙规则单行命令、动态 IP 助手、Hyper-V 防火墙变通方案），请点击上面的链接——此处不再赘述。

### 情况 2 — Windows（或你的局域网）上的某个程序与 WSL 中的 Hermes 通信

这是相反的方向，其他地方文档较少，但你需要它用于：

- 从 Windows 浏览器使用 Hermes **Web 仪表板**。
- 从 Windows 端工具使用 **API 服务器**（`hermes api`）。
- 测试 **消息网关**（Telegram、Discord 等），平台会向本地 webhook URL 发送请求——通常你会使用 `cloudflared`/`ngrok` 而不是原始端口转发。

#### 子情况 2a：从 Windows 主机本身访问

在 **启用了镜像模式的 Windows 11 22H2+** 上，无需任何操作。一个绑定到 `0.0.0.0:8080`（甚至 `127.0.0.1:8080`）的 WSL 进程，可以从 Windows 浏览器通过 `http://localhost:8080` 访问。WSL 会自动将绑定发布回主机。

在 **NAT 模式**（Windows 10 / 旧版 Windows 11）下，WSL2 中默认的 "localhost 转发" 通常会将 Linux 端的 `127.0.0.1` 绑定转发到 Windows 的 `localhost`，因此使用 `--host 127.0.0.1` 启动的 Hermes 服务通常可以从 Windows 通过 `http://localhost:端口` 访问。如果不行：

- 在 WSL 内部显式绑定到 `0.0.0.0`。
- 使用 `ip -4 addr show eth0 | grep inet` 找到 WSL 虚拟机的 IP，然后从 Windows 访问该 IP。

#### 子情况 2b：从局域网上的另一台设备（手机、平板、另一台 PC）访问

这才是真正的痛点。流量路径是 **局域网设备 → Windows 主机 → WSL 虚拟机**，你必须设置两个跳转：

1.  **在 WSL 内部绑定到所有接口。** 监听 `127.0.0.1` 的进程永远无法从虚拟机外部访问。请使用 `0.0.0.0`。

2.  **端口转发 Windows → WSL 虚拟机。** 在镜像模式下这是自动的。在 NAT 模式下，你必须自己为每个端口在管理员 PowerShell 中设置：

   ```powershell
   # 获取 WSL 虚拟机当前的 IP（在 NAT 模式下，每次 WSL 重启都会改变）
   $wslIp = (wsl hostname -I).Trim().Split(' ')[0]

   # 转发 Windows 端口 8080 → WSL:8080
   netsh interface portproxy add v4tov4 `
     listenaddress=0.0.0.0 listenport=8080 `
     connectaddress=$wslIp connectport=8080

   # 允许通过 Windows 防火墙
   New-NetFirewallRule -DisplayName "Hermes WSL 8080" `
     -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```

   稍后可以使用 `netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8080` 删除。

3.  **将局域网设备指向 `http://<windows-局域网-ip>:8080`。**

因为在 NAT 模式下，WSL 虚拟机的 IP 在每次重启时都会漂移，所以一次性规则只能维持到下一次 `wsl --shutdown`。对于任何需要持久化的设置，要么使用镜像模式，要么将端口代理步骤放入在 Windows 登录时运行的脚本中。
对于来自云消息提供商（Telegram `setWebhook`、Slack 事件等）的 Webhook，不要费力去配置端口转发——使用 `cloudflared` 隧道。请参阅 [Webhook 指南](/docs/user-guide/messaging/webhooks)。

## 在 Windows 上长期运行 Hermes 服务

Hermes [工具网关](/docs/user-guide/features/tool-gateway) 和 API 服务器是长期运行的进程。在 WSL2 中，你有几种保持它们运行的方法。

### 在 WSL 内使用 systemd（推荐）

如果你按照上面设置部分启用了 systemd，`hermes gateway` 和 API 服务器的运行方式与在任何 Linux 机器上相同。使用网关设置向导：

```bash
hermes gateway setup
```

它会提供安装一个 systemd 用户单元，以便在 WSL 启动时自动启动网关。

### 让 WSL 本身在 Windows 登录时启动

WSL 的虚拟机只在有东西使用它时才保持活动状态。为了在没有终端窗口打开的情况下也能访问你的网关，可以通过任务计划程序在 Windows 登录时启动一个 WSL 进程：

- **触发器：** 登录时（你的用户）。
- **操作：** 启动程序
  - 程序：`C:\Windows\System32\wsl.exe`
  - 参数：`-d Ubuntu --exec /bin/sh -c "sleep infinity"`

这可以保持虚拟机活动，从而使 systemd 管理的网关保持运行。在 Windows 11 上，较新的 `wsl --install --no-launch` + 自动启动流程也有效；`sleep infinity` 技巧是通用版本。

## GPU 透传（本地模型）

自 WSL 内核 5.10.43+ 起，WSL2 原生支持 **NVIDIA** GPU——在 Windows 上安装标准的 NVIDIA 驱动程序（**不要**在 WSL 内安装 Linux NVIDIA 驱动程序），WSL 内的 `nvidia-smi` 就能看到 GPU。然后，CUDA 工具包、`torch`、`vllm`、`sglang` 和 `llama-server` 就可以像往常一样针对真实的 GPU 进行构建。

WSL2 内的 AMD ROCm 和 Intel Arc 支持仍在发展中，并且不在 Hermes 的测试范围内——它可能适用于当前的驱动程序，但我们没有推荐的方案。

如果你运行的是 **Windows 原生** 的本地模型服务器（Windows 版 Ollama、LM Studio），它已经通过 Windows 驱动程序使用了你的 GPU，那么你完全不需要 WSL GPU 透传——只需按照上面的情况 1 操作，并从 WSL 通过网络访问它。

## 常见问题

**连接到我在 Windows 上托管的 Ollama / LM Studio 时出现 "Connection refused"。**
请参阅 [WSL2 网络](/docs/integrations/providers#wsl2-networking-windows-users)。百分之九十的情况下，服务器绑定到了 `127.0.0.1`，需要改为 `0.0.0.0`（Ollama：`OLLAMA_HOST=0.0.0.0`），或者你缺少防火墙规则。

**在仓库中执行 `git status` / `hermes chat` 时速度极慢。**
你可能在 `/mnt/c/...` 目录下工作。将仓库移动到 `~/code/...`（Linux 侧）。速度会快几个数量级。

**在脚本上出现 `bad interpreter: /bin/bash^M`。**
来自 Windows 编辑器的 CRLF 行尾。使用 `dos2unix script.sh`，并在你的 WSL git 配置中设置 `core.autocrlf input`。

**通过 MCP 启动的 Windows 二进制文件发出 "UNC paths are not supported" 警告。**
Hermes 的当前工作目录在 Linux 文件系统内，Windows `cmd.exe` 不知道如何处理它。对于该会话，从 `/mnt/c/...` 启动 Hermes，或者使用一个包装器，在调用 Windows 可执行文件之前先 `cd` 到一个 Windows 可访问的路径。

**睡眠/休眠后时钟漂移。**
WSL2 的时钟在主机从睡眠恢复后可能会延迟几分钟，这会破坏任何基于证书的操作（OAuth、HTTPS API）。按需修复：

```bash
sudo hwclock -s
```

或者安装 `ntpdate` 并在登录时运行它。

**启用镜像模式后，或连接 VPN 后，DNS 停止工作。**
镜像模式将主机的网络设置代理到 WSL 中——如果 Windows DNS 有问题（VPN 分流隧道、公司解析器），WSL 会继承这些问题。解决方法：手动覆盖 `resolv.conf`（在 `/etc/wsl.conf` 中设置 `generateResolvConf=false`，然后用自己的 `/etc/resolv.conf`，写入 `1.1.1.1` 或你的 VPN 的 DNS）。

**运行安装程序后找不到 `hermes`。**
安装程序通过 `~/.bashrc` 将 `~/.local/bin` 添加到你的 shell 的 PATH 中。你需要 `source ~/.bashrc`（或打开一个新的终端）才能在当前会话中生效。

**Windows Defender 对 WSL 文件扫描缓慢。**
当从 Windows 访问时，Defender 通过 9P 桥扫描文件，这放大了 `/mnt/c` 式跨边界访问的缓慢。如果你只在 WSL 内部接触 WSL 文件，这无关紧要。如果你经常使用 Windows 工具访问 `\\wsl$\...`，请考虑将 WSL 发行版路径从实时扫描中排除。

**磁盘空间不足。**
WSL2 将其虚拟机磁盘存储为 `%LOCALAPPDATA%\Packages\...` 下的稀疏 VHDX 文件。它会增长，但当你删除文件时不会自动收缩。要回收空间：`wsl --shutdown`，然后从管理员 PowerShell 运行 `Optimize-VHD -Path <path-to-ext4.vhdx> -Mode Full`（需要 Hyper-V 工具）——或者 WSL 文档中记录的更简单的 `diskpart` 路径。

## 下一步

- **[安装](/docs/getting-started/installation)** —— 实际的安装步骤（Linux/WSL2/Termux 都使用相同的安装程序）。
- **[集成 → 提供商 → WSL2 网络](/docs/integrations/providers#wsl2-networking-windows-users)** —— 针对本地模型服务器的权威网络深入探讨。
- **[MCP 指南 → WSL → Windows Chrome](/docs/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)** —— 从 WSL 中的 Hermes 控制你已登录的 Windows Chrome。
- **[工具网关](/docs/user-guide/features/tool-gateway)** 和 **[Web 仪表板](/docs/user-guide/features/web-dashboard)** —— 你最常希望从 WSL 暴露到网络其余部分的长期运行服务。