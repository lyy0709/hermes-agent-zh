---
title: 浏览器自动化
description: 通过多种提供商控制浏览器，包括通过 CDP 连接本地 Chrome 或使用云浏览器，实现网页交互、表单填写、数据抓取等功能。
sidebar_label: 浏览器
sidebar_position: 5
---

# 浏览器自动化

Hermes Agent 包含一套完整的浏览器自动化工具集，提供多种后端选项：

- **Browserbase 云模式**：通过 [Browserbase](https://browserbase.com) 使用托管的云浏览器和反机器人工具
- **Browser Use 云模式**：通过 [Browser Use](https://browser-use.com) 作为替代的云浏览器提供商
- **Firecrawl 云模式**：通过 [Firecrawl](https://firecrawl.dev) 使用内置抓取功能的云浏览器
- **Camofox 本地模式**：通过 [Camofox](https://github.com/jo-inc/camofox-browser) 进行本地反检测浏览（基于 Firefox 的指纹欺骗）
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 将浏览器工具连接到您自己的 Chrome 实例
- **本地浏览器模式** — 通过 `agent-browser` CLI 和本地 Chromium 安装

在所有模式下，Agent 都可以导航网站、与页面元素交互、填写表单和提取信息。

## 概述

页面被表示为**无障碍树**（基于文本的快照），这使其非常适合 LLM Agent。交互元素会获得引用 ID（如 `@e1`、`@e2`），Agent 使用这些 ID 进行点击和输入。

核心功能：

- **多提供商云执行** — Browserbase、Browser Use 或 Firecrawl — 无需本地浏览器
- **本地 Chrome 集成** — 通过 CDP 连接到您正在运行的 Chrome 进行手动浏览
- **内置隐身功能** — 随机指纹、验证码解决、住宅代理（Browserbase）
- **会话隔离** — 每个任务都有自己的浏览器会话
- **自动清理** — 非活动会话在超时后关闭
- **视觉分析** — 截图 + AI 分析以实现视觉理解

## 设置

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则可以通过 **[工具网关](tool-gateway.md)** 使用浏览器自动化功能，无需任何单独的 API 密钥。运行 `hermes model` 或 `hermes tools` 来启用它。
:::

### Browserbase 云模式

要使用 Browserbase 托管的云浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取您的凭证。

### Browser Use 云模式

要使用 Browser Use 作为您的云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，则 Browserbase 优先。

### Firecrawl 云模式

要使用 Firecrawl 作为您的云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
FIRECRAWL_API_KEY=fc-***
```

在 [firecrawl.dev](https://firecrawl.dev) 获取您的 API 密钥。然后选择 Firecrawl 作为您的浏览器提供商：

```bash
hermes setup tools
# → Browser Automation → Firecrawl
```

可选设置：

```bash
# 自托管的 Firecrawl 实例（默认：https://api.firecrawl.dev）
FIRECRAWL_API_URL=http://localhost:3002

# 会话 TTL（秒）（默认：300）
FIRECRAWL_BROWSER_TTL=600
```

### 混合路由：公共 URL 使用云，LAN/localhost 使用本地

当配置了云提供商时，Hermes 会自动为解析为私有/环回/LAN 地址的 URL（`localhost`、`127.0.0.1`、`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`、`*.local`、`*.lan`、`*.internal`、IPv6 环回 `::1`、链路本地 `169.254.x.x`）启动一个**本地 Chromium 侧车**。公共 URL 在同一会话中继续使用云提供商。

这解决了常见的“我在本地开发但使用 Browserbase”的工作流程 — Agent 可以截取 `http://localhost:3000` 的仪表板截图**并且**抓取 `https://github.com`，而您无需切换提供商或禁用 SSRF 防护。云提供商永远不会看到私有 URL。

此功能**默认开启**。要禁用它（所有 URL 都像以前一样发送到配置的云提供商）：

```yaml
# ~/.hermes/config.yaml
browser:
  cloud_provider: browserbase
  auto_local_for_private_urls: false
```

禁用自动路由后，私有 URL 将被拒绝，并显示 `"Blocked: URL targets a private or internal address"`，除非您还设置了 `browser.allow_private_urls: true`（这会让云提供商尝试访问它们 — 通常不会成功，因为 Browserbase 等无法访问您的 LAN）。

要求：本地侧车使用与纯本地模式相同的 `agent-browser` CLI，因此您需要安装它（`hermes setup tools → Browser Automation` 会自动安装它）。从公共 URL 导航后重定向到私有地址仍然会被阻止（您不能使用重定向到内部的技巧通过公共路径访问您的 LAN）。

### Camofox 本地模式

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务器，封装了 Camoufox（一个带有 C++ 指纹欺骗功能的 Firefox 分支）。它提供本地反检测浏览，无需云依赖。

```bash
# 首先克隆 Camofox 浏览器服务器
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser

# 使用 Docker 构建并启动，使用默认容器设置
# （自动检测架构：M1/M2 上为 aarch64，Intel 上为 x86_64）
make up

# 停止并移除默认容器
make down

# 强制完全重建（例如，升级 VERSION/RELEASE 后）
make reset

# 仅下载二进制文件而不构建
make fetch

# 显式覆盖架构或版本
make up ARCH=x86_64
make up VERSION=135.0.1 RELEASE=beta.24
```

`make up` 会立即启动默认容器。如果您想要自定义运行时设置，例如更大的 Node 堆、VNC 或持久化的配置文件目录，请先构建镜像，然后自行运行：

```bash
# 构建镜像而不启动默认容器
make build

# 以持久化、VNC 实时视图和更大的 Node 堆启动
mkdir -p ~/.camofox-docker
docker run -d \
  --name camofox-browser \
  --restart unless-stopped \
  -p 9377:9377 \
  -p 6080:6080 \
  -p 5901:5900 \
  -e CAMOFOX_PORT=9377 \
  -e ENABLE_VNC=1 \
  -e VNC_BIND=0.0.0.0 \
  -e VNC_RESOLUTION=1920x1080 \
  -e MAX_OLD_SPACE_SIZE=2048 \
  -v ~/.camofox-docker:/root/.camofox \
  camofox-browser:135.0.1-aarch64
```
启用 VNC 后，浏览器将以有头模式运行，并可在 `http://localhost:6080` (noVNC) 通过浏览器实时观看。你也可以将原生 VNC 客户端连接到 `localhost:5901`。

如果你已经运行了 `make up`，请在启动自定义容器之前停止并移除该默认容器：

```bash
make down
# 然后运行上面的自定义 docker run 命令
```

然后在 `~/.hermes/.env` 中设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

或者通过 `hermes tools` → Browser Automation → Camofox 进行配置。

当 `CAMOFOX_URL` 设置后，所有浏览器工具将自动通过 Camofox 路由，而不是 Browserbase 或 agent-browser。

#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都会获得一个随机身份 —— Cookie 和登录状态在 Agent 重启后不会保留。要启用持久化浏览器会话，请在 `~/.hermes/config.yaml` 中添加以下内容：

```yaml
browser:
  camofox:
    managed_persistence: true
```

然后完全重启 Hermes 以使新配置生效。

:::warning 嵌套路径很重要
Hermes 读取的是 `browser.camofox.managed_persistence`，**而不是**顶层的 `managed_persistence`。一个常见的错误是写成：

```yaml
# ❌ 错误 —— Hermes 会忽略此项
managed_persistence: true
```

如果该标志被放在错误的路径下，Hermes 会静默回退到随机的临时 `userId`，你的登录状态将在每次会话中丢失。
:::

##### Hermes 会做什么
- 向 Camofox 发送一个确定性的、作用域为配置文件的 `userId`，以便服务器可以在不同会话间复用相同的 Firefox 配置文件。
- 在清理时跳过服务器端的上下文销毁，以便 Cookie 和登录状态在 Agent 任务之间得以保留。
- 将 `userId` 的作用域限定为当前活动的 Hermes 配置文件，因此不同的 Hermes 配置文件会获得不同的浏览器配置文件（配置文件隔离）。

##### Hermes 不会做什么
- 它不会强制 Camofox 服务器进行持久化。Hermes 只发送一个稳定的 `userId`；服务器必须通过将该 `userId` 映射到持久的 Firefox 配置文件目录来遵守此约定。
- 如果你的 Camofox 服务器构建将每个请求都视为临时的（例如，总是调用 `browser.newContext()` 而不加载存储的配置文件），Hermes 将无法使这些会话持久化。请确保你运行的 Camofox 构建实现了基于 userId 的配置文件持久化。

##### 验证其是否正常工作

1.  启动 Hermes 和你的 Camofox 服务器。
2.  在浏览器任务中打开 Google（或任何登录网站）并手动登录。
3.  正常结束浏览器任务。
4.  启动一个新的浏览器任务。
5.  再次打开同一个网站 —— 你应该仍然处于登录状态。

如果第 5 步让你退出了登录，说明 Camofox 服务器没有遵守稳定的 `userId`。请仔细检查你的配置路径，确认在编辑 `config.yaml` 后完全重启了 Hermes，并验证你的 Camofox 服务器版本支持每个用户的持久化配置文件。

##### 状态存储位置

Hermes 从配置文件作用域的目录 `~/.hermes/browser_auth/camofox/`（对于非默认配置文件，则是 `$HERMES_HOME` 下的等效目录）派生出稳定的 `userId`。实际的浏览器配置文件数据存储在 Camofox 服务器端，以该 `userId` 为键。要完全重置一个持久化配置文件，请在 Camofox 服务器端清除它，并删除 Hermes 配置文件中对应的状态目录。

#### VNC 实时视图

当 Camofox 以有头模式运行（带有可见的浏览器窗口）时，它会在其健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现这一点，并在导航响应中包含 VNC URL，因此 Agent 可以分享一个链接供你实时观看浏览器。

### 通过 CDP 连接本地 Chrome (`/browser connect`)

除了云提供商，你还可以通过 Chrome DevTools Protocol (CDP) 将 Hermes 浏览器工具附加到你自己的正在运行的 Chrome 实例。这在你想实时查看 Agent 的操作、与需要你自己的 Cookie/会话的页面交互，或者避免云浏览器成本时非常有用。

:::note
`/browser connect` 是一个**交互式 CLI 斜杠命令** —— 它不由消息网关分发。如果你尝试在 WebUI、Telegram、Discord 或其他网关聊天中运行它，该消息将作为纯文本发送给 Agent，命令不会执行。请从终端（`hermes` 或 `hermes chat`）启动 Hermes，并在那里输入 `/browser connect`。
:::

在 CLI 中，使用：

```
/browser connect              # 连接到 ws://localhost:9222 的 Chrome
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status               # 检查当前连接状态
/browser disconnect            # 断开连接并返回云/本地模式
```

如果 Chrome 尚未以远程调试模式运行，Hermes 将尝试使用 `--remote-debugging-port=9222` 自动启动它。

:::tip
要手动启动启用了 CDP 的 Chrome，请使用专用的用户数据目录，这样即使 Chrome 已经以你的常规配置文件运行，调试端口也能正常启动：

```bash
# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &
```

然后启动 Hermes CLI 并运行 `/browser connect`。

**为什么需要 `--user-data-dir`？** 如果没有它，在常规 Chrome 实例已经运行时启动 Chrome，通常会在现有进程上打开一个新窗口 —— 而该现有进程启动时没有 `--remote-debugging-port`，因此端口 9222 永远不会打开。专用的用户数据目录会强制启动一个新的 Chrome 进程，调试端口才会实际监听。`--no-first-run --no-default-browser-check` 会跳过新配置文件的首次启动向导。
:::

当通过 CDP 连接时，所有浏览器工具（`browser_navigate`、`browser_click` 等）都将在你的实时 Chrome 实例上操作，而不是启动云会话。

### WSL2 + Windows Chrome：优先使用 MCP 而非 `/browser connect`

如果 Hermes 在 WSL2 内运行，但你想控制的 Chrome 窗口运行在 Windows 主机上，`/browser connect` 通常不是最佳选择。
原因：

- `/browser connect` 期望 Hermes 自身能够访问一个可用的 CDP 端点
- 现代 Chrome 实时调试会话通常暴露一个主机本地端点，无法像传统的 `9222` 端口那样直接从 WSL 访问
- 即使 Windows Chrome 可调试，最简洁的集成方式通常是让 Windows 端的浏览器 MCP 服务器连接到 Chrome，然后让 Hermes 与该 MCP 服务器通信

对于这种设置，建议通过 Hermes 的 MCP 支持使用 `chrome-devtools-mcp`。

有关实际设置，请参阅 MCP 指南：

- [在 WSL2 中将 Hermes 桥接到 Windows Chrome](../../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)

### 本地浏览器模式

如果你**没有**设置任何云凭证且不使用 `/browser connect`，Hermes 仍然可以通过 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

### 可选环境变量

```bash
# 用于更好解决验证码的住宅代理（默认："true"）
BROWSERBASE_PROXIES=true

# 使用自定义 Chromium 的高级隐身模式 —— 需要 Scale 计划（默认："false"）
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后的会话重连 —— 需要付费计划（默认："true"）
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时时间（毫秒）（默认：项目默认值）
# 示例：600000 (10分钟), 1800000 (30分钟)
BROWSERBASE_SESSION_TIMEOUT=600000

# 自动清理前的非活动超时时间（秒）（默认：120）
BROWSER_INACTIVITY_TIMEOUT=120
```

### 安装 agent-browser CLI

```bash
npm install -g agent-browser
# 或者在仓库中本地安装：
npm install
```

:::info
`browser` 工具集必须包含在你的配置文件的 `toolsets` 列表中，或者通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

## 可用工具

### `browser_navigate`

导航到 URL。必须在任何其他浏览器工具之前调用。初始化 Browserbase 会话。

```
导航到 https://github.com/NousResearch
```

:::tip
对于简单的信息检索，建议使用 `web_search` 或 `web_extract` —— 它们更快、更便宜。当你需要与页面**交互**时（点击按钮、填写表单、处理动态内容），再使用浏览器工具。
:::

### `browser_snapshot`

获取当前页面无障碍树的基于文本的快照。返回带有引用 ID（如 `@e1`、`@e2`）的交互元素，供 `browser_click` 和 `browser_type` 使用。

- **`full=false`**（默认）：紧凑视图，仅显示交互元素
- **`full=true`**：完整的页面内容

超过 8000 字符的快照会自动由 LLM 进行总结。

### `browser_click`

点击快照中通过其引用 ID 标识的元素。

```
点击 @e5 以按下“登录”按钮
```

### `browser_type`

在输入字段中输入文本。先清除字段，然后输入新文本。

```
在搜索字段 @e3 中输入 "hermes agent"
```

### `browser_scroll`

向上或向下滚动页面以显示更多内容。

```
向下滚动以查看更多结果
```

### `browser_press`

按下键盘按键。适用于提交表单或导航。

```
按 Enter 键提交表单
```

支持的按键：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

### `browser_back`

在浏览器历史记录中导航回上一页。

### `browser_get_images`

列出当前页面上的所有图片及其 URL 和替代文本。适用于查找要分析的图片。

### `browser_vision`

截取屏幕截图并使用视觉 AI 进行分析。当文本快照无法捕获重要的视觉信息时使用此工具 —— 对于验证码、复杂布局或视觉验证挑战尤其有用。

屏幕截图会被持久保存，文件路径会与 AI 分析结果一起返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，你可以要求 Agent 分享屏幕截图 —— 它将通过 `MEDIA:` 机制作为原生照片附件发送。

```
此页面上的图表显示了什么？
```

屏幕截图存储在 `~/.hermes/cache/screenshots/` 中，并在 24 小时后自动清理。

### `browser_console`

获取浏览器控制台输出（日志/警告/错误消息）以及当前页面未捕获的 JavaScript 异常。对于检测无障碍树中未显示的静默 JS 错误至关重要。

```
检查浏览器控制台是否有任何 JavaScript 错误
```

使用 `clear=True` 在读取后清除控制台，以便后续调用只显示新消息。

### `browser_cdp`

原始 Chrome DevTools 协议直通 —— 用于其他工具未涵盖的浏览器操作的逃生舱口。用于处理原生对话框、iframe 范围内的评估、Cookie/网络控制，或 Agent 需要的任何 CDP 动词。

**仅在会话开始时可以访问 CDP 端点时才可用** —— 这意味着 `/browser connect` 已附加到正在运行的 Chrome，或者在 `config.yaml` 中设置了 `browser.cdp_url`。默认的本地 agent-browser 模式、Camofox 和云提供商（Browserbase、Browser Use、Firecrawl）目前不向此工具公开 CDP —— 云提供商有每个会话的 CDP URL，但实时会话路由是后续功能。

**CDP 方法参考：** https://chromedevtools.github.io/devtools-protocol/ —— Agent 可以 `web_extract` 特定方法的页面来查找参数和返回形状。

常见模式：

```
# 列出标签页（浏览器级别，无 target_id）
browser_cdp(method="Target.getTargets")

# 处理标签页上的原生 JS 对话框
browser_cdp(method="Page.handleJavaScriptDialog",
            params={"accept": true, "promptText": ""},
            target_id="<tabId>")

# 在特定标签页中评估 JS
browser_cdp(method="Runtime.evaluate",
            params={"expression": "document.title", "returnByValue": true},
            target_id="<tabId>")

# 获取所有 Cookie
browser_cdp(method="Network.getAllCookies")
```

浏览器级别的方法（`Target.*`、`Browser.*`、`Storage.*`）省略 `target_id`。页面级别的方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）需要来自 `Target.getTargets` 的 `target_id`。每个无状态调用都是独立的 —— 会话不会在调用之间持续存在。
**跨域 iframe：** 传递 `frame_id`（来自 `browser_snapshot.frame_tree.children[]`，其中 `is_oopif=true`）以通过该 iframe 的 supervisor 实时会话路由 CDP 调用。这就是在 Browserbase 上跨域 iframe 内部的 `Runtime.evaluate` 的工作方式，因为无状态的 CDP 连接会遇到签名 URL 过期问题。示例：

```
browser_cdp(
  method="Runtime.evaluate",
  params={"expression": "document.title", "returnByValue": True},
  frame_id="<frame_id from browser_snapshot>",
)
```

同源 iframe 不需要 `frame_id` —— 请从顶级 `Runtime.evaluate` 中使用 `document.querySelector('iframe').contentDocument`。

### `browser_dialog`

响应原生 JS 对话框（`alert` / `confirm` / `prompt` / `beforeunload`）。在该工具出现之前，对话框会静默阻塞页面的 JavaScript 线程，后续的 `browser_*` 调用会挂起或抛出异常；现在 Agent 可以在 `browser_snapshot` 输出中看到待处理的对话框并进行显式响应。

**工作流程：**
1. 调用 `browser_snapshot`。如果有对话框阻塞页面，它会显示为 `pending_dialogs: [{"id": "d-1", "type": "alert", "message": "..."}]`。
2. 调用 `browser_dialog(action="accept")` 或 `browser_dialog(action="dismiss")`。对于 `prompt()` 对话框，传递 `prompt_text="..."` 来提供响应。
3. 重新快照 —— `pending_dialogs` 为空；页面的 JS 线程已恢复。

**检测自动发生**，通过一个持久的 CDP supervisor —— 每个任务一个 WebSocket，订阅 Page/Runtime/Target 事件。该 supervisor 还会在快照中填充一个 `frame_tree` 字段，以便 Agent 可以查看当前页面的 iframe 结构，包括跨域（OOPIF）iframe。

**可用性矩阵：**

| 后端 | 通过 `pending_dialogs` 检测 | 响应（`browser_dialog` 工具） |
|---|---|---|
| 通过 `/browser connect` 或 `browser.cdp_url` 连接的本地 Chrome | ✓ | ✓ 完整工作流 |
| Browserbase | ✓ | ✓ 完整工作流（通过注入的 XHR 桥接） |
| Camofox / 默认的本地 agent-browser | ✗ | ✗（无 CDP 端点） |

**在 Browserbase 上的工作原理。** Browserbase 的 CDP 代理会在服务器端自动关闭真实原生对话框（约 10 毫秒内），因此我们无法使用 `Page.handleJavaScriptDialog`。supervisor 通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个小脚本，用同步 XHR 覆盖 `window.alert`/`confirm`/`prompt`。我们通过 `Fetch.enable` 拦截这些 XHR —— 页面的 JS 线程会一直阻塞在 XHR 上，直到我们调用 `Fetch.fulfillRequest` 并传入 Agent 的响应。`prompt()` 的返回值会原封不动地返回到页面 JS 中。

**对话框策略** 在 `config.yaml` 的 `browser.dialog_policy` 下配置：

| 策略 | 行为 |
|--------|----------|
| `must_respond`（默认） | 捕获，在快照中显示，等待显式的 `browser_dialog()` 调用。在 `browser.dialog_timeout_s`（默认 300 秒）后安全地自动关闭，以防止有问题的 Agent 无限期阻塞。 |
| `auto_dismiss` | 捕获，立即关闭。Agent 仍然可以在 `browser_state` 历史记录中看到对话框，但无需采取行动。 |
| `auto_accept` | 捕获，立即接受。在导航带有激进 `beforeunload` 提示的页面时很有用。 |

`browser_snapshot.frame_tree` 内部的 **Frame tree** 限制为 30 个 frame 和 OOPIF 深度 2，以在广告繁多的页面上限制负载。当达到限制时，会显示 `truncated: true` 标志；需要完整树的 Agent 可以使用 `browser_cdp` 配合 `Page.getFrameTree`。

## 实际示例

### 填写网页表单

```
用户：用我的邮箱 john@example.com 在 example.com 上注册一个账户

Agent 工作流：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有 refs 的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击 "Create Account"
6. browser_snapshot()  → 确认成功
```

### 研究动态内容

```
用户：GitHub 上当前最热门的仓库是什么？

Agent 工作流：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取热门仓库列表
3. 返回格式化结果
```

## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认: false
```

启用后，录制会在第一次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。在本地和云端（Browserbase）模式下均可工作。超过 72 小时的录制文件会自动清理。

## 隐身功能

Browserbase 提供自动隐身功能：

| 功能 | 默认 | 备注 |
|---------|---------|-------|
| 基础隐身 | 始终开启 | 随机指纹、视口随机化、CAPTCHA 解决 |
| 住宅代理 | 开启 | 通过住宅 IP 路由以获得更好的访问效果 |
| 高级隐身 | 关闭 | 自定义 Chromium 构建，需要 Scale 计划 |
| 保持连接 | 开启 | 网络中断后会话重连 |

:::note
如果您的计划不支持付费功能，Hermes 会自动回退 —— 首先禁用 `keepAlive`，然后是代理 —— 因此免费计划上浏览仍然有效。
:::

## 会话管理

- 每个任务通过 Browserbase 获得一个隔离的浏览器会话
- 会话在无活动后自动清理（默认：2 分钟）
- 后台线程每 30 秒检查一次过期会话
- 进程退出时运行紧急清理以防止会话残留
- 通过 Browserbase API（`REQUEST_RELEASE` 状态）释放会话

## 限制

- **基于文本的交互** —— 依赖无障碍树，而非像素坐标
- **快照大小** —— 大型页面可能会被截断或在 8000 字符处由 LLM 总结
- **会话超时** —— 云端会话根据您的提供商计划设置过期
- **成本** —— 云端会话消耗提供商积分；会话在对话结束或无活动后自动清理。使用 `/browser connect` 进行免费的本地浏览。
- **无文件下载** —— 无法从浏览器下载文件