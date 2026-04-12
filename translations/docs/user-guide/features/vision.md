---
title: 视觉与图像粘贴
description: 将剪贴板中的图像粘贴到 Hermes CLI 中进行多模态视觉分析。
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

**最可靠的方法。适用于所有环境。**

```
/paste
```

输入 `/paste` 并按 Enter 键。Hermes 会检查你的剪贴板中是否有图像并附加它。这种方法适用于所有环境，因为它显式调用剪贴板后端——无需担心终端快捷键拦截问题。

### Ctrl+V / Cmd+V（括号粘贴）

当你粘贴剪贴板中与图像一起存在的文本时，Hermes 也会自动检查图像。这在以下情况下有效：
*   你的剪贴板中**同时包含文本和图像**（某些应用在你复制时会同时将两者放入剪贴板）
*   你的终端支持括号粘贴（大多数现代终端都支持）

:::warning
如果你的剪贴板**只有图像**（没有文本），在大多数终端中按 Ctrl+V 不会有任何反应。终端只能粘贴文本——没有粘贴二进制图像数据的标准机制。请改用 `/paste` 或 Alt+V。
:::

### Alt+V

Alt 键组合键在大多数终端模拟器中都能通过（它们以 ESC + 键的形式发送，而不是被拦截）。按 `Alt+V` 可以检查剪贴板中是否有图像。

:::caution
**在 VSCode 的集成终端中无效。** VSCode 会拦截许多 Alt+键 组合键用于其自身的 UI。请改用 `/paste`。
:::

### Ctrl+V（原始模式——仅限 Linux）

在 Linux 桌面终端（GNOME Terminal、Konsole、Alacritty 等）上，`Ctrl+V` **不是**粘贴快捷键——`Ctrl+Shift+V` 才是。因此 `Ctrl+V` 会向应用程序发送一个原始字节，Hermes 会捕获它来检查剪贴板。这仅在具有 X11 或 Wayland 剪贴板访问权限的 Linux 桌面终端上有效。

## 平台兼容性

| 环境 | `/paste` | Ctrl+V 文本+图像 | Alt+V | 备注 |
|---|:---:|:---:|:---:|---|
| **macOS Terminal / iTerm2** | ✅ | ✅ | ✅ | 最佳体验——`osascript` 始终可用 |
| **Linux X11 桌面** | ✅ | ✅ | ✅ | 需要 `xclip` (`apt install xclip`) |
| **Linux Wayland 桌面** | ✅ | ✅ | ✅ | 需要 `wl-paste` (`apt install wl-clipboard`) |
| **WSL2 (Windows Terminal)** | ✅ | ✅¹ | ✅ | 使用 `powershell.exe`——无需额外安装 |
| **VSCode 终端 (本地)** | ✅ | ✅¹ | ❌ | VSCode 会拦截 Alt+键 |
| **VSCode 终端 (SSH)** | ❌² | ❌² | ❌ | 远程剪贴板不可访问 |
| **SSH 终端 (任何)** | ❌² | ❌² | ❌² | 远程剪贴板不可访问 |

¹ 仅当剪贴板同时包含文本和图像时有效（仅包含图像的剪贴板 = 无反应）
² 请参阅下面的 [SSH 与远程会话](#ssh--remote-sessions)

## 平台特定设置

### macOS

**无需设置。** Hermes 使用 `osascript`（内置于 macOS）来读取剪贴板。为了获得更快的性能，可以选择安装 `pngpaste`：

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

**无需额外设置。** Hermes 会自动检测 WSL2（通过 `/proc/version`）并使用 `powershell.exe` 通过 .NET 的 `System.Windows.Forms.Clipboard` 访问 Windows 剪贴板。这是 WSL2 的 Windows 互操作功能内置的——`powershell.exe` 默认可用。

剪贴板数据以 base64 编码的 PNG 格式通过 stdout 传输，因此不需要文件路径转换或临时文件。

:::info WSLg 说明
如果你正在运行 WSLg（支持 GUI 的 WSL2），Hermes 会先尝试 PowerShell 路径，然后回退到 `wl-paste`。WSLg 的剪贴板桥接器仅支持图像的 BMP 格式——Hermes 会使用 Pillow（如果已安装）或 ImageMagick 的 `convert` 命令自动将 BMP 转换为 PNG。
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

**剪贴板粘贴在 SSH 连接中无效。** 当你通过 SSH 连接到远程机器时，Hermes CLI 在远程主机上运行。所有剪贴板工具（`xclip`、`wl-paste`、`powershell.exe`、`osascript`）读取的都是它们运行所在机器的剪贴板——即远程服务器，而不是你的本地机器。你的本地剪贴板无法从远程端访问。

### SSH 的变通方案

1.  **上传图像文件**——将图像保存在本地，通过 `scp`、VSCode 的文件资源管理器（拖放）或任何文件传输方法将其上传到远程服务器。然后通过路径引用它。*（计划在未来的版本中添加 `/attach <文件路径>` 命令。）*

2.  **使用 URL**——如果图像可以在线访问，只需在消息中粘贴 URL。Agent 可以直接使用 `vision_analyze` 查看任何图像 URL。

3.  **X11 转发**——使用 `ssh -X` 连接以转发 X11。这使得远程机器上的 `xclip` 可以访问你本地的 X11 剪贴板。需要在本地运行 X 服务器（macOS 上的 XQuartz，Linux X11 桌面内置）。对于大图像来说速度较慢。

4.  **使用消息平台**——通过 Telegram、Discord、Slack 或 WhatsApp 向 Hermes 发送图像。这些平台原生处理图像上传，不受剪贴板/终端限制的影响。

## 为什么终端无法粘贴图像

这是一个常见的困惑来源，以下是技术解释：

终端是**基于文本**的接口。当你按下 Ctrl+V（或 Cmd+V）时，终端模拟器会：

1.  从剪贴板读取**文本内容**
2.  用[括号粘贴](https://en.wikipedia.org/wiki/Bracketed-paste)转义序列包装它
3.  通过终端的文本流将其发送给应用程序

如果剪贴板只包含图像（没有文本），终端就没有内容可发送。没有标准的终端转义序列用于二进制图像数据。终端根本不会做任何事情。

这就是为什么 Hermes 使用单独的剪贴板检查——它不通过终端粘贴事件接收图像数据，而是通过子进程直接调用操作系统级工具（`osascript`、`powershell.exe`、`xclip`、`wl-paste`）来独立读取剪贴板。

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

大多数现代模型都支持这种格式，包括 GPT-4 Vision、Claude（带视觉功能）、Gemini 以及通过 OpenRouter 提供的开源多模态模型。