---
sidebar_position: 3
title: "Android / Termux"
description: "通过 Termux 在 Android 手机上直接运行 Hermes Agent"
---

# 在 Android 上通过 Termux 使用 Hermes

这是通过 [Termux](https://termux.dev/) 在 Android 手机上直接运行 Hermes Agent 的已验证路径。

它为你提供了一个在手机上可用的本地 CLI，以及目前已知能在 Android 上干净安装的核心附加功能。

## 已验证路径支持哪些功能？

已验证的 Termux 捆绑包安装了：
- Hermes CLI
- cron 支持
- PTY/后台终端支持
- MCP 支持
- Honcho 记忆支持
- ACP 支持

具体来说，它对应以下命令：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 已验证路径目前不包含哪些功能？

一些功能仍然需要桌面/服务器风格的依赖项，这些依赖项尚未为 Android 发布，或者尚未在手机上验证：

- `.[all]` 目前在 Android 上不受支持
- `voice` 附加功能被 `faster-whisper -> ctranslate2` 阻塞，而 `ctranslate2` 没有发布 Android 轮子包
- Termux 安装程序跳过了自动浏览器 / Playwright 引导
- 基于 Docker 的终端隔离在 Termux 内不可用

这并不妨碍 Hermes 作为手机原生 CLI Agent 良好运行——它只是意味着推荐的移动安装范围有意比桌面/服务器安装更窄。

---

## 选项 1：单行安装程序

Hermes 现在提供了一个支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

在 Termux 上，安装程序会自动：
- 使用 `pkg` 安装系统包
- 使用 `python -m venv` 创建虚拟环境
- 使用 `pip` 安装 `.[termux]`
- 将 `hermes` 链接到 `$PREFIX/bin`，使其保持在你的 Termux PATH 中
- 跳过未经测试的浏览器 / WhatsApp 引导

如果你想要明确的命令或需要调试失败的安装，请使用下面的手动路径。

---

## 选项 2：手动安装（完全明确）

### 1. 更新 Termux 并安装系统包

```bash
pkg update
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

为什么需要这些包？
- `python` — 运行时 + 虚拟环境支持
- `git` — 克隆/更新仓库
- `clang`, `rust`, `make`, `pkg-config`, `libffi`, `openssl` — 在 Android 上构建一些 Python 依赖项所需
- `nodejs` — 用于在已验证核心路径之外进行实验的可选 Node 运行时
- `ripgrep` — 快速文件搜索
- `ffmpeg` — 媒体 / TTS 转换

### 2. 克隆 Hermes

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

如果你已经克隆但没有包含子模块：

```bash
git submodule update --init --recursive
```

### 3. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
```

`ANDROID_API_LEVEL` 对于 Rust / 基于 maturin 的包（如 `jiter`）很重要。

### 4. 安装已验证的 Termux 捆绑包

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

如果你只想要最小的核心 Agent，这个命令也有效：

```bash
python -m pip install -e '.' -c constraints-termux.txt
```

### 5. 将 `hermes` 添加到你的 Termux PATH

```bash
ln -sf "$PWD/venv/bin/hermes" "$PREFIX/bin/hermes"
```

`$PREFIX/bin` 已经在 Termux 的 PATH 中，因此这会使 `hermes` 命令在新 shell 中持续可用，而无需每次都重新激活虚拟环境。

### 6. 验证安装

```bash
hermes version
hermes doctor
```

### 7. 启动 Hermes

```bash
hermes
```

---

## 推荐的后续设置

### 配置模型

```bash
hermes model
```

或者直接在 `~/.hermes/.env` 中设置密钥。

### 稍后重新运行完整的交互式设置向导

```bash
hermes setup
```

### 手动安装可选的 Node 依赖项

已验证的 Termux 路径有意跳过了 Node/浏览器引导。如果你稍后想要实验：

```bash
npm install
```

在另有文档说明之前，请将 Android 上的浏览器 / WhatsApp 工具视为实验性功能。

---

## 故障排除

### 安装 `.[all]` 时出现 `No solution found`

改用已验证的 Termux 捆绑包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前的阻塞点是 `voice` 附加功能：
- `voice` 拉取 `faster-whisper`
- `faster-whisper` 依赖 `ctranslate2`
- `ctranslate2` 没有发布 Android 轮子包

### `uv pip install` 在 Android 上失败

改用带有标准库 venv + `pip` 的 Termux 路径：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `jiter` / `maturin` 抱怨 `ANDROID_API_LEVEL`

在安装前显式设置 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `hermes doctor` 显示 ripgrep 或 Node 缺失

使用 Termux 包安装它们：

```bash
pkg install ripgrep nodejs
```

### 安装 Python 包时出现构建失败

确保安装了构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

---

## 手机上已知的限制

- Docker 后端不可用
- 通过 `faster-whisper` 的本地语音转录在已验证路径中不可用
- 浏览器自动化设置被安装程序有意跳过
- 一些可选的附加功能可能有效，但目前只有 `.[termux]` 被记录为已验证的 Android 捆绑包

如果你遇到新的 Android 特定问题，请提交 GitHub issue 并提供：
- 你的 Android 版本
- `termux-info`
- `python --version`
- `hermes doctor`
- 确切的安装命令和完整的错误输出