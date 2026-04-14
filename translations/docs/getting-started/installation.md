---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2 或通过 Termux 在 Android 上安装 Hermes Agent"
---

# 安装

使用一行命令安装程序在两分钟内启动并运行 Hermes Agent，或者按照手动步骤以获得完全控制。

## 快速安装

### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Android / Termux

Hermes 现在也提供了一个支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 并切换到经过测试的 Android 流程：
- 使用 Termux `pkg` 安装系统依赖项 (`git`, `python`, `nodejs`, `ripgrep`, `ffmpeg`, 构建工具)
- 使用 `python -m venv` 创建虚拟环境
- 自动导出 `ANDROID_API_LEVEL` 用于 Android wheel 构建
- 使用 `pip` 安装精选的 `.[termux]` 额外包
- 默认跳过未经测试的浏览器 / WhatsApp 引导程序

如果你想要完全明确的路径，请遵循专门的 [Termux 指南](./termux.md)。

:::warning Windows
原生 Windows **不受支持**。请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes Agent。上面的安装命令在 WSL2 内有效。
:::

### 安装程序的作用

安装程序会自动处理所有事情 —— 所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，你就可以开始聊天了。

### 安装后

重新加载你的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或者: source ~/.zshrc
hermes             # 开始聊天！
```

以后要重新配置单个设置，请使用专用命令：

```bash
hermes model          # 选择你的 LLM 提供商和模型
hermes tools          # 配置启用哪些工具
hermes gateway setup  # 设置消息平台
hermes config set     # 设置单个配置值
hermes setup          # 或者运行完整的设置向导一次性配置所有内容
```

---

## 先决条件

唯一的先决条件是 **Git**。安装程序会自动处理其他所有事情：

- **uv** (快速的 Python 包管理器)
- **Python 3.11** (通过 uv，无需 sudo)
- **Node.js v22** (用于浏览器自动化和 WhatsApp 桥接)
- **ripgrep** (快速文件搜索)
- **ffmpeg** (用于 TTS 的音频格式转换)

:::info
你**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺少的内容并为你安装。只需确保 `git` 可用 (`git --version`)。
:::

:::tip Nix 用户
如果你使用 Nix (在 NixOS、macOS 或 Linux 上)，有一个专门的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参阅 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
:::

---

## 手动安装

如果你希望对安装过程有完全的控制权，请按照以下步骤操作。

### 步骤 1：克隆仓库

使用 `--recurse-submodules` 克隆以拉取所需的子模块：

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

如果你已经克隆但没有使用 `--recurse-submodules`：
```bash
git submodule update --init --recursive
```

### 步骤 2：安装 uv 并创建虚拟环境

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用 Python 3.11 创建 venv (uv 会下载它，如果不存在的话 —— 无需 sudo)
uv venv venv --python 3.11
```

:::tip
你**不需要**激活 venv 来使用 `hermes`。入口点有一个硬编码的 shebang 指向 venv 的 Python，所以一旦符号链接创建好，它就可以全局工作。
:::

### 步骤 3：安装 Python 依赖项

```bash
# 告诉 uv 要安装到哪个 venv
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有额外包
uv pip install -e ".[all]"
```

如果你只想要核心 Agent (没有 Telegram/Discord/cron 支持)：
```bash
uv pip install -e "."
```

<details>
<summary><strong>可选额外包明细</strong></summary>

| 额外包 | 添加的内容 | 安装命令 |
|-------|-------------|-----------------|
| `all` | 以下所有内容 | `uv pip install -e ".[all]"` |
| `messaging` | Telegram、Discord 和 Slack 消息网关 | `uv pip install -e ".[messaging]"` |
| `cron` | 用于定时任务的 Cron 表达式解析 | `uv pip install -e ".[cron]"` |
| `cli` | 用于设置向导的终端菜单 UI | `uv pip install -e ".[cli]"` |
| `modal` | Modal 云执行后端 | `uv pip install -e ".[modal]"` |
| `tts-premium` | ElevenLabs 高级语音 | `uv pip install -e ".[tts-premium]"` |
| `voice` | CLI 麦克风输入 + 音频播放 | `uv pip install -e ".[voice]"` |
| `pty` | PTY 终端支持 | `uv pip install -e ".[pty]"` |
| `termux` | 经过测试的 Android / Termux 捆绑包 (`cron`, `cli`, `pty`, `mcp`, `honcho`, `acp`) | `python -m pip install -e ".[termux]" -c constraints-termux.txt` |
| `honcho` | AI 原生记忆 (Honcho 集成) | `uv pip install -e ".[honcho]"` |
| `mcp` | Model Context Protocol 支持 | `uv pip install -e ".[mcp]"` |
| `homeassistant` | Home Assistant 集成 | `uv pip install -e ".[homeassistant]"` |
| `acp` | ACP 编辑器集成支持 | `uv pip install -e ".[acp]"` |
| `slack` | Slack 消息 | `uv pip install -e ".[slack]"` |
| `dev` | pytest 和测试工具 | `uv pip install -e ".[dev]"` |

你可以组合额外包：`uv pip install -e ".[messaging,cron]"`

:::tip Termux 用户
`.[all]` 目前在 Android 上不可用，因为 `voice` 额外包会拉取 `faster-whisper`，而它依赖于 `ctranslate2` wheels，这些 wheels 没有为 Android 发布。请使用 `.[termux]` 作为经过测试的移动安装路径，然后根据需要仅添加单个额外包。
:::

</details>

### 步骤 4：安装可选的子模块 (如果需要)

```bash
# RL 训练后端 (可选)
uv pip install -e "./tinker-atropos"
```

两者都是可选的 —— 如果你跳过它们，相应的工具集将不可用。

### 步骤 5：安装 Node.js 依赖项 (可选)

仅用于**浏览器自动化** (基于 Browserbase) 和 **WhatsApp 桥接**：

```bash
npm install
```

### 步骤 6：创建配置目录

```bash
# 创建目录结构
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}

# 复制示例配置文件
cp cli-config.yaml.example ~/.hermes/config.yaml

# 为 API 密钥创建一个空的 .env 文件
touch ~/.hermes/.env
```

### 步骤 7：添加你的 API 密钥

打开 `~/.hermes/.env` 并至少添加一个 LLM 提供商密钥：

```bash
# 必需 —— 至少一个 LLM 提供商：
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 可选 —— 启用额外工具：
FIRECRAWL_API_KEY=fc-your-key          # 网络搜索和抓取 (或自托管，见文档)
FAL_KEY=your-fal-key                   # 图像生成 (FLUX)
```

或者通过 CLI 设置它们：
```bash
hermes config set OPENROUTER_API_KEY sk-or-v1-your-key-here
```

### 步骤 8：将 `hermes` 添加到你的 PATH

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

如果 `~/.local/bin` 不在你的 PATH 中，请将其添加到你的 shell 配置中：

```bash
# Bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc

# Zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# Fish
fish_add_path $HOME/.local/bin
```

### 步骤 9：配置你的提供商

```bash
hermes model       # 选择你的 LLM 提供商和模型
```

### 步骤 10：验证安装

```bash
hermes version    # 检查命令是否可用
hermes doctor     # 运行诊断以验证一切正常
hermes status     # 检查你的配置
hermes chat -q "Hello! What tools do you have available?"
```

---

## 快速参考：手动安装 (精简版)

适用于只想看命令的用户：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆并进入
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建 venv
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有内容
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"
npm install  # 可选，用于浏览器工具和 WhatsApp

# 配置
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env

# 使 hermes 全局可用
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# 验证
hermes doctor
hermes
```

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载你的 shell (`source ~/.bashrc`) 或检查 PATH |
| `API key not set` | 运行 `hermes model` 来配置你的提供商，或者 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后缺少配置 | 运行 `hermes config check` 然后 `hermes config migrate` |

要获取更多诊断信息，请运行 `hermes doctor` —— 它会准确地告诉你缺少什么以及如何修复。