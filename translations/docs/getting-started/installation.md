---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2、原生 Windows 或通过 Termux 在 Android 上安装 Hermes Agent"
---

# 安装

在两分钟内启动并运行 Hermes Agent！

## 快速安装
### 在 macOS 或 Windows 上使用 Hermes Desktop 安装程序（推荐）
要轻松安装命令行和桌面应用程序，请从我们的网站[下载 Hermes Desktop 安装程序](https://hermes-agent.nousresearch.com/desktop)并运行它。

### 不使用 Hermes Desktop：
对于仅安装命令行版本（不使用 Hermes Desktop），请运行：

#### Linux / macOS / WSL2 / Android (Termux)
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows (原生)

在 powershell 中运行：
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

如果您在仅安装命令行版本后想要安装并运行 Hermes Desktop，只需运行：
```bash
hermes desktop
```

### 安装程序的作用

安装程序会自动处理所有事情——所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，您就可以开始聊天了。

#### 安装布局

安装程序将文件放置的位置取决于您是作为普通用户还是 root 用户安装：

| 安装方式 | 代码位于 | `hermes` 二进制文件 | 数据目录 |
|---|---|---|---|
| pip install | Python site-packages | `~/.local/bin/hermes` (console_scripts) | `~/.hermes/` |
| 按用户安装 (git 安装程序) | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes` (符号链接) | `~/.hermes/` |
| Root 模式 (`sudo curl … \| sudo bash`) | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/` (或 `$HERMES_HOME`) |

Root 模式的 **FHS 布局** (`/usr/local/lib/…`, `/usr/local/bin/hermes`) 与 Linux 上其他系统级开发工具的安装位置相匹配。这对于共享机器部署非常有用，一个系统安装应为所有用户服务。每个用户的配置（身份验证、技能、会话）仍然位于各自的 `~/.hermes/` 或显式设置的 `HERMES_HOME` 下。

### 安装后

重新加载您的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或者: source ~/.zshrc
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

:::tip 最快路径：Nous Portal
一个订阅涵盖 300+ 模型以及[工具网关](/user-guide/features/tool-gateway)（网络搜索、图像生成、TTS、云浏览器）。无需再为每个工具管理密钥：

```bash
hermes setup --portal
```

该命令会登录、将 Nous 设置为您的提供商，并一键启用工具网关。
:::

---

## 先决条件

**安装程序：** 在非 Windows 平台上，唯一的先决条件是 **Git**。安装程序会自动处理其他所有事情：

- **uv**（快速的 Python 包管理器）
- **Python 3.11**（通过 uv 安装，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）

:::info
您**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺少的内容并为您安装。只需确保 `git` 可用 (`git --version`)。
:::

:::tip Nix 用户
如果您使用 Nix（在 NixOS、macOS 或 Linux 上），有一个专门的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参阅 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
:::

---

## 手动 / 开发者安装

如果您想克隆仓库并从源代码安装——用于贡献、从特定分支运行或完全控制虚拟环境——请参阅贡献指南中的[开发设置](../developer-guide/contributing.md#development-setup)部分。

---

## 非 Sudo / 系统服务用户安装

支持以专用非特权用户（例如 `hermes` systemd 服务账户，或任何没有 `sudo` 权限的用户）运行 Hermes。安装路径上唯一真正需要 root 权限的是 Playwright 的 `--with-deps` 步骤，它通过 `apt` 安装 Chromium 使用的共享库（`libnss3`、`libxkbcommon` 等）。安装程序会检测 sudo 是否可用，并在不可用时优雅降级——它会将 Chromium 二进制文件安装到服务用户自己的 Playwright 缓存中，并打印管理员需要单独运行的确切命令。

**推荐的分步操作（Debian/Ubuntu）：**

1.  **一次性操作，以具有 sudo 权限的管理员用户**，安装 Chromium 所需的系统库：
    ```bash
    sudo npx playwright install-deps chromium
    ```
    （您可以在任何地方运行此命令——`npx` 会即时获取 Playwright。）

2.  **以非特权服务用户身份**，运行常规安装程序。它会检测到缺少 sudo，跳过 `--with-deps`，并将 Chromium 安装到用户的本地 Playwright 缓存中：
    ```bash
    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
    ```

    如果您想完全跳过 Playwright 步骤——例如，因为您正在无头运行且不需要浏览器自动化——请传递 `--skip-browser`：
    ```bash
    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
    ```

3.  **使 `hermes` 对服务用户的 shell 可用。** 安装程序将启动器写入 `~/.local/bin/hermes`。系统服务账户通常具有不包含 `~/.local/bin` 的最小 PATH。要么将其添加到用户的环境变量中，要么将启动器符号链接到系统位置：
    ```bash
    # 选项 A — 添加到服务用户的配置文件中
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

    # 选项 B — 系统级符号链接（以管理员身份运行）
    sudo ln -s /home/hermes/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
    ```

4.  **验证：** `hermes doctor` 现在应该能正常运行。如果您遇到 `ModuleNotFoundError: No module named 'dotenv'`，说明您正在使用系统 Python 调用仓库源代码的 `hermes` 文件 (`~/.hermes/hermes-agent/hermes`)，而不是虚拟环境启动器 (`~/.hermes/hermes-agent/venv/bin/hermes`)——请修复步骤 3。

相同的模式适用于 Arch（安装程序使用 pacman 并具有相同的 sudo 检测逻辑）、Fedora/RHEL 和 openSUSE——这些发行版根本不支持 `--with-deps`，因此管理员总是需要单独安装系统库。相关的 `dnf`/`zypper` 命令会由安装程序打印出来。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载您的 shell (`source ~/.bashrc`) 或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置您的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后缺少配置 | 运行 `hermes config check` 然后 `hermes config migrate` |

要获取更多诊断信息，请运行 `hermes doctor`——它会确切地告诉您缺少什么以及如何修复。

## 安装方法自动检测

Hermes 会自动检测它是通过 `pip`、git 安装程序、Homebrew 还是 NixOS 安装的，并且 `hermes update` 会打印出该路径对应的更新命令。无需设置环境变量——检测基于安装布局（Python site-packages、`~/.hermes/hermes-agent/`、Homebrew 前缀或 Nix 存储路径）。`hermes doctor` 也会在其环境摘要中显示检测到的方法。