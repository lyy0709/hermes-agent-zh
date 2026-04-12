---
title: 浏览器自动化
description: 通过多种提供商控制浏览器，包括通过 CDP 连接本地 Chrome，或使用云浏览器进行网页交互、表单填写、数据抓取等操作。
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
- **本地 Chrome 集成** — 通过 CDP 连接到您正在运行的 Chrome，进行手动浏览
- **内置隐身功能** — 随机指纹、验证码解决、住宅代理（Browserbase）
- **会话隔离** — 每个任务都有其独立的浏览器会话
- **自动清理** — 不活动的会话在超时后会自动关闭
- **视觉分析** — 截图 + AI 分析，用于视觉理解

## 设置

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

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，Browserbase 将优先使用。

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

### Camofox 本地模式

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务器，封装了 Camoufox（一个带有 C++ 指纹欺骗功能的 Firefox 分支）。它提供本地反检测浏览，无需云依赖。

```bash
# 安装并运行
git clone https://github.com/jo-inc/camofox-browser && cd camofox-browser
npm install && npm start   # 首次运行会下载 Camoufox（约 300MB）

# 或通过 Docker
docker run -d --network host -e CAMOFOX_PORT=9377 jo-inc/camofox-browser
```

然后在 `~/.hermes/.env` 中设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

或通过 `hermes tools` → Browser Automation → Camofox 进行配置。

当设置了 `CAMOFOX_URL` 时，所有浏览器工具将自动通过 Camofox 路由，而不是 Browserbase 或 agent-browser。

#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都有一个随机身份 — Cookie 和登录状态在 Agent 重启后不会保留。要启用持久化浏览器会话：

```yaml
# 在 ~/.hermes/config.yaml 中
browser:
  camofox:
    managed_persistence: true
```

启用后，Hermes 会向 Camofox 发送一个稳定的、基于配置文件的身份标识。Camofox 服务器将此身份映射到一个持久的浏览器配置文件目录，因此 Cookie、登录状态和 localStorage 在重启后得以保留。不同的 Hermes 配置文件会获得不同的浏览器配置文件（配置文件隔离）。

:::note
Camofox 服务器也必须配置 `CAMOFOX_PROFILE_DIR` 才能使持久化生效。
:::

#### VNC 实时视图

当 Camofox 在带界面的模式下运行（带有可见的浏览器窗口）时，它会在其健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现此端口，并在导航响应中包含 VNC URL，因此 Agent 可以分享一个链接供您实时观看浏览器操作。

### 通过 CDP 连接本地 Chrome (`/browser connect`)

您可以将 Hermes 浏览器工具通过 Chrome DevTools Protocol (CDP) 连接到您自己正在运行的 Chrome 实例，而不是使用云提供商。这在您想实时查看 Agent 的操作、与需要您自己的 Cookie/会话的页面交互，或避免云浏览器成本时非常有用。

在 CLI 中，使用：

```
/browser connect              # 连接到 ws://localhost:9222 的 Chrome
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status               # 检查当前连接状态
/browser disconnect            # 断开连接并返回云/本地模式
```

如果 Chrome 尚未启用远程调试运行，Hermes 将尝试使用 `--remote-debugging-port=9222` 参数自动启动它。

:::tip
手动启动启用 CDP 的 Chrome：
```bash
# Linux
google-chrome --remote-debugging-port=9222

# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```
:::

当通过 CDP 连接时，所有浏览器工具（`browser_navigate`、`browser_click` 等）都在您实时的 Chrome 实例上操作，而不是启动云会话。

### 本地浏览器模式

如果您**没有**设置任何云凭证，并且不使用 `/browser connect`，Hermes 仍然可以通过由 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。
### 可选环境变量

```bash
# 用于提升验证码破解效果的高匿代理（默认："true"）
BROWSERBASE_PROXIES=true

# 使用自定义 Chromium 的高级隐身模式 — 需要 Scale 套餐（默认："false"）
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后重新连接会话 — 需要付费套餐（默认："true"）
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时时间（毫秒）（默认：项目默认值）
# 示例：600000 (10分钟), 1800000 (30分钟)
BROWSERBASE_SESSION_TIMEOUT=600000

# 自动清理前的无活动超时时间（秒）（默认：120）
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

导航到指定 URL。必须在调用任何其他浏览器工具之前调用。用于初始化 Browserbase 会话。

```
导航到 https://github.com/NousResearch
```

:::tip
对于简单的信息检索，建议优先使用 `web_search` 或 `web_extract` — 它们更快、更便宜。当你需要**与页面交互**时（点击按钮、填写表单、处理动态内容），再使用浏览器工具。
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

在输入字段中输入文本。首先清除字段，然后输入新文本。

```
在搜索字段 @e3 中输入 "hermes agent"
```

### `browser_scroll`

向上或向下滚动页面以显示更多内容。

```
向下滚动查看更多结果
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

截取屏幕截图并使用视觉 AI 进行分析。当文本快照无法捕获重要的视觉信息时使用此工具 — 尤其适用于验证码、复杂布局或视觉验证挑战。

截图会被持久保存，文件路径会与 AI 分析结果一同返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，你可以要求 Agent 分享截图 — 它将通过 `MEDIA:` 机制作为原生照片附件发送。

```
此页面上的图表显示了什么？
```

截图存储在 `~/.hermes/cache/screenshots/` 目录下，并在 24 小时后自动清理。

### `browser_console`

获取当前页面的浏览器控制台输出（日志/警告/错误消息）和未捕获的 JavaScript 异常。对于检测无障碍树中不显示的静默 JS 错误至关重要。

```
检查浏览器控制台是否有任何 JavaScript 错误
```

使用 `clear=True` 可在读取后清除控制台，以便后续调用仅显示新消息。

## 实际示例

### 填写网页表单

```
用户：使用我的邮箱 john@example.com 在 example.com 上注册一个账户

Agent 工作流：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有引用的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击“创建账户”
6. browser_snapshot()  → 确认成功
```

### 研究动态内容

```
用户：GitHub 上当前最热门的仓库是什么？

Agent 工作流：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取热门仓库列表
3. 返回格式化的结果
```

## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认：false
```

启用后，录制会在第一次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。在本地和云端（Browserbase）模式下均可工作。超过 72 小时的录制文件会自动清理。

## 隐身功能

Browserbase 提供自动隐身功能：

| 功能 | 默认 | 说明 |
|---------|---------|-------|
| 基础隐身 | 始终开启 | 随机指纹、视口随机化、验证码破解 |
| 高匿代理 | 开启 | 通过住宅 IP 路由以获得更好的访问效果 |
| 高级隐身 | 关闭 | 自定义 Chromium 构建，需要 Scale 套餐 |
| 保持连接 | 开启 | 网络中断后重新连接会话 |

:::note
如果你的套餐不包含付费功能，Hermes 会自动回退 — 首先禁用 `keepAlive`，然后是代理 — 因此免费套餐上的浏览功能仍然可用。
:::

## 会话管理

- 每个任务通过 Browserbase 获得一个独立的浏览器会话
- 会话在无活动后自动清理（默认：2 分钟）
- 后台线程每 30 秒检查一次过期会话
- 进程退出时运行紧急清理，以防止会话残留
- 通过 Browserbase API（`REQUEST_RELEASE` 状态）释放会话

## 限制

- **基于文本的交互** — 依赖于无障碍树，而非像素坐标
- **快照大小** — 大型页面可能在 8000 字符处被截断或由 LLM 总结
- **会话超时** — 云端会话根据你的提供商套餐设置过期
- **成本** — 云端会话消耗提供商积分；会话在对话结束或一段时间无活动后自动清理。使用 `/browser connect` 进行免费的本地浏览。
- **无法下载文件** — 无法从浏览器下载文件