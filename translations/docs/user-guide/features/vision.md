---
title: 视觉与图像粘贴
description: 将剪贴板中的图像粘贴到 Hermes CLI 中，进行多模态视觉分析。
sidebar_label: 视觉与图像粘贴
sidebar_position: 7
---

# 视觉与图像粘贴

Hermes Agent 支持**多模态视觉**功能——你可以将剪贴板中的图像直接粘贴到 CLI 中，并要求 Agent 对其进行分析、描述或处理。图像会以 base64 编码的内容块形式发送给模型，因此任何具备视觉能力的模型都可以处理它们。

## 工作原理

1.  将图像复制到剪贴板（截图、浏览器图片等）
2.  使用以下方法之一附加图像
3.  输入你的问题并按 Enter 键
4.  图像会以 `[📎 Image #1]` 徽章的形式显示在输入框上方
5.  提交时，图像会作为视觉内容块发送给模型

你可以在发送前附加多张图像——每张图像都有自己的徽章。按 `Ctrl+C` 可清除所有已附加的图像。

图像会以带时间戳的文件名保存为 PNG 文件，存储在 `~/.hermes/images/` 目录下。

## 粘贴方法

附加图像的方式取决于你的终端环境。并非所有方法都适用于所有环境——以下是完整的分类说明：

### `/paste` 命令

**最可靠、明确的图像附加备用方案。**

```
/paste
```

输入 `/paste` 并按 Enter 键。Hermes 会检查你的剪贴板中是否有图像并附加它。当你的终端重写了 `Cmd+V`/`Ctrl+V`，或者当你只复制了图像而没有可供检查的括号粘贴文本负载时，这是最安全的选择。

### Ctrl+V / Cmd+V

Hermes 现在将粘贴视为一个分层流程：
- 首先是普通文本粘贴
- 如果终端未能干净地传递文本，则回退到原生剪贴板 / OSC52 文本
- 当剪贴板或粘贴的负载解析为图像或图像路径时，附加图像

这意味着粘贴的 macOS 截图临时路径和 `file://...` 图像 URI 可以立即附加，而不是作为原始文本停留在输入框中。

:::warning
如果你的剪贴板中**只有图像**（没有文本），终端仍然无法直接发送二进制图像数据。请使用 `/paste` 作为明确的图像附加备用方案。
:::

### `/terminal-setup` 用于 VS Code / Cursor / Windsurf

如果你在 macOS 上的本地 VS Code 系列集成终端内运行 TUI，Hermes 可以安装推荐的 `workbench.action.terminal.sendSequence` 绑定，以获得更好的多行和撤销/重做对等性：

```text
/terminal-setup
```

当 `Cmd+Enter`、`Cmd+Z` 或 `Shift+Cmd+Z` 被 IDE 拦截时，这尤其有用。仅在本地机器上运行此命令——不要在 SSH 会话中运行。

## 平台兼容性

| 环境 | `/paste` | Cmd/Ctrl+V | `/terminal-setup` | 备注 |
|---|:---:|:---:|:---:|---|
| **macOS Terminal / iTerm2** | ✅ | ✅ | n/a | 最佳体验——原生剪贴板 + 截图路径恢复 |
| **Apple Terminal** | ✅ | ✅ | n/a | 如果 Cmd+←/→/⌫ 被重写，请使用 Ctrl+A / Ctrl+E / Ctrl+U 备用方案 |
| **Linux X11 桌面** | ✅ | ✅ | n/a | 需要 `xclip` (`apt install xclip`) |
| **Linux Wayland 桌面** | ✅ | ✅ | n/a | 需要 `wl-paste` (`apt install wl-clipboard`) |
| **WSL2 (Windows Terminal)** | ✅ | ✅ | n/a | 使用 `powershell.exe`——无需额外安装 |
| **VS Code / Cursor / Windsurf (本地)** | ✅ | ✅ | ✅ | 推荐用于更好的 Cmd+Enter / 撤销 / 重做对等性 |
| **VS Code / Cursor / Windsurf (SSH)** | ❌² | ❌² | ❌³ | 请在本地机器上运行 `/terminal-setup` |
| **SSH 终端 (任何)** | ❌² | ❌² | n/a | 远程剪贴板不可访问 |

² 请参阅下面的 [SSH 与远程会话](#ssh--remote-sessions)
³ 该命令写入本地 IDE 键绑定，不应从远程主机运行

## 平台特定设置

### macOS

**无需设置。** Hermes 使用 `osascript`（macOS 内置）来读取剪贴板。为了获得更快的性能，可以选择安装 `pngpaste`：

```bash
brew install pngpaste
```

### Linux (X11)

安装 `xclip`：

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Linux (Wayland)

现代 Linux 桌面（Ubuntu 22.04+、Fedora 34+）通常默认使用 Wayland。安装 `wl-clipboard`：

```bash
# Ubuntu/Debian
sudo apt install wl-clipboard

# Fedora
sudo dnf install wl-clipboard

# Arch
sudo pacman -S wl-clipboard
```

:::tip 如何检查是否在使用 Wayland
```bash
echo $XDG_SESSION_TYPE
# "wayland" = Wayland, "x11" = X11, "tty" = 无显示服务器
```
:::

### WSL2

**无需额外设置。** Hermes 会自动检测 WSL2（通过 `/proc/version`），并使用 `powershell.exe` 通过 .NET 的 `System.Windows.Forms.Clipboard` 访问 Windows 剪贴板。这是 WSL2 Windows 互操作内置的功能——`powershell.exe` 默认可用。

剪贴板数据通过 stdout 以 base64 编码的 PNG 格式传输，因此不需要文件路径转换或临时文件。

:::info WSLg 说明
如果你正在运行 WSLg（支持 GUI 的 WSL2），Hermes 会先尝试 PowerShell 路径，然后回退到 `wl-paste`。WSLg 的剪贴板桥接仅支持图像的 BMP 格式——Hermes 会使用 Pillow（如果已安装）或 ImageMagick 的 `convert` 命令自动将 BMP 转换为 PNG。
:::

#### 验证 WSL2 剪贴板访问

```bash
# 1. 检查 WSL 检测
grep -i microsoft /proc/version

# 2. 检查 PowerShell 是否可访问
which powershell.exe

# 3. 复制一张图片，然后检查
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::ContainsImage()"
# 应该打印 "True"
```

## SSH 与远程会话

**通过 SSH 进行剪贴板图像粘贴无法完全正常工作。** 当你 SSH 到远程机器时，Hermes CLI 在远程主机上运行。剪贴板工具（`xclip`、`wl-paste`、`powershell.exe`、`osascript`）读取的是它们运行所在机器的剪贴板——即远程服务器，而不是你的本地机器。因此，你的本地剪贴板图像无法从远程端访问。

文本有时仍然可以通过终端粘贴或 OSC52 桥接，但图像剪贴板访问和本地截图临时路径仍然与运行 Hermes 的机器绑定。

### SSH 的变通方案

1.  **上传图像文件**——将图像保存在本地，通过 `scp`、VSCode 的文件资源管理器（拖放）或任何文件传输方法将其上传到远程服务器。然后通过路径引用它。*(计划在未来的版本中添加 `/attach <filepath>` 命令。)*

2.  **使用 URL**——如果图像可以在线访问，只需将 URL 粘贴到你的消息中。Agent 可以直接使用 `vision_analyze` 查看任何图像 URL。

3.  **X11 转发**——使用 `ssh -X` 连接以转发 X11。这使得远程机器上的 `xclip` 可以访问你的本地 X11 剪贴板。需要在本地运行 X 服务器（macOS 上的 XQuartz，Linux X11 桌面内置）。对于大图像来说速度较慢。

4.  **使用消息平台**——通过 Telegram、Discord、Slack 或 WhatsApp 向 Hermes 发送图像。这些平台原生处理图像上传，不受剪贴板/终端限制的影响。

## 为什么终端无法粘贴图像

这是一个常见的困惑来源，以下是技术解释：

终端是**基于文本**的接口。当你按下 Ctrl+V（或 Cmd+V）时，终端模拟器会：

1.  读取剪贴板中的**文本内容**
2.  将其包装在[括号粘贴](https://en.wikipedia.org/wiki/Bracketed-paste)转义序列中
3.  通过终端的文本流将其发送到应用程序

如果剪贴板只包含图像（没有文本），终端就没有内容可发送。没有标准的终端转义序列用于二进制图像数据。终端什么也不做。

这就是为什么 Hermes 使用单独的剪贴板检查——它通过子进程直接调用操作系统级工具（`osascript`、`powershell.exe`、`xclip`、`wl-paste`）来独立读取剪贴板，而不是通过终端粘贴事件接收图像数据。

## 支持的模型

图像粘贴适用于任何具备视觉能力的模型。图像以 OpenAI 视觉内容格式的 base64 编码数据 URL 形式发送：

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,..."
  }
}
```

大多数现代模型都支持这种格式，包括 GPT-4 Vision、Claude（带视觉）、Gemini 以及通过 OpenRouter 提供的开源多模态模型。