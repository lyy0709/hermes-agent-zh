---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的仪表盘，用于管理配置、API 密钥、会话、日志、分析、定时任务和技能"
---

# Web 仪表盘

Web 仪表盘是一个基于浏览器的用户界面，用于管理您的 Hermes Agent 安装。您无需编辑 YAML 文件或运行 CLI 命令，即可通过简洁的 Web 界面配置设置、管理 API 密钥和监控会话。

## 快速开始

```bash
hermes dashboard
```

这将启动一个本地 Web 服务器，并在您的浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全在您的机器上运行 —— 数据不会离开本地主机。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有接口（在共享网络上使用需谨慎）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open
```

## 前提条件

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 助手 —— 这些是可选的额外组件。**Web 仪表盘**需要 FastAPI 和 Uvicorn（`web` 额外组件）。**Chat** 标签页还需要 `ptyprocess` 来在伪终端后生成嵌入式 TUI（在 POSIX 系统上是 `pty` 额外组件）。使用以下命令安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 额外组件会拉取 FastAPI/Uvicorn；`pty` 会拉取 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows —— 请注意嵌入式 TUI 本身仍然需要 WSL）。`pip install hermes-agent[all]` 包含这两个额外组件，如果您还想要消息/语音等功能，这是最简单的方法。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

## 页面

### 状态

落地页显示您安装的实时概览：

- **Agent 版本**和发布日期
- **消息网关状态** —— 运行/停止、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### 聊天

**Chat** 标签页将完整的 Hermes TUI（与您从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。您在终端 TUI 中可以做的所有事情 —— 斜杠命令、模型选择器、工具调用卡片、Markdown 流式传输、澄清/sudo/批准提示、皮肤主题 —— 在这里都完全相同，因为仪表盘正在运行真正的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，以实现像素完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个使用仪表盘会话 Token 进行身份验证的 WebSocket
- 服务器在 POSIX 伪终端后生成 `hermes --tui`
- 按键传输到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格；鼠标跟踪（SGR 1006）、宽字符（Unicode 11）和方框绘制字形都原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 大小

**恢复现有会话：** 在 **Sessions** 标签页中，点击任意会话旁边的播放图标（▶）。这将跳转到 `/chat?resume=<id>` 并使用 `--resume` 启动 TUI，加载完整的历史记录。

**前提条件：**

- Node.js（与 `hermes --tui` 的要求相同；TUI 包在首次启动时构建）
- `ptyprocess` —— 由 `pty` 额外组件安装（`pip install 'hermes-agent[web,pty]'`，或 `[all]` 包含两者）
- POSIX 内核（Linux、macOS 或 WSL）。不支持原生 Windows Python —— 请使用 WSL。

关闭浏览器标签页，PTY 将在服务器上被干净地回收。重新打开会生成一个新的会话。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都是从 `DEFAULT_CONFIG` 自动发现的，并组织到分标签的类别中：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（local/docker/ssh/modal）、超时、Shell 偏好
- **display** —— 皮肤、工具进度、恢复显示、旋转器设置
- **agent** —— 最大迭代次数、消息网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理工作量
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（ask/yolo/deny）
- 以及更多 —— config.yaml 的每个部分都有相应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉菜单。布尔值呈现为切换开关。其他所有内容都是文本输入框。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（在您点击保存之前不会保存）
- **导出** —— 将当前配置下载为 JSON
- **导入** —— 上传 JSON 配置文件以替换当前值

:::tip
配置更改将在下一个 Agent 会话或消息网关重启时生效。Web 仪表盘编辑的是与 `hermes config set` 和消息网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** —— OpenRouter、Anthropic、OpenAI、DeepSeek 等
- **工具 API 密钥** —— Browserbase、Firecrawl、Tavily、ElevenLabs 等
- **消息平台** —— Telegram、Discord、Slack 机器人 Token 等
- **Agent 设置** —— 非机密环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（带有值的脱敏预览）
- 用途描述
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 用于删除它的按钮

高级/不常用的密钥默认隐藏在切换开关后面。
### 会话

浏览和检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用数量以及上次活跃时间。活跃会话会用一个脉动徽章标记。

- **搜索** — 使用 FTS5 在所有消息内容中进行全文搜索。结果会显示高亮片段，展开时会自动滚动到第一条匹配的消息。
- **展开** — 点击一个会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并以 Markdown 格式渲染，支持语法高亮。
- **工具调用** — 包含工具调用的助手消息会显示可折叠的块，其中包含函数名称和 JSON 参数。
- **删除** — 使用垃圾桶图标删除会话及其消息历史记录。

### 日志

查看 Agent、消息网关和错误日志文件，支持过滤和实时跟踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：all、gateway、agent、tools、cli 或 cron
- **行数** — 选择要显示的行数（50、100、200 或 500）
- **自动刷新** — 切换实时跟踪功能，每 5 秒轮询一次新的日志行
- **颜色编码** — 日志行按严重程度着色（红色表示错误，黄色表示警告，灰色表示调试信息）

### 分析

根据会话历史记录计算的用量和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** — 总 Token 数（输入/输出）、缓存命中率、总估计或实际成本，以及总会话数和日均值
- **每日 Token 图表** — 堆叠条形图，显示每天的输入和输出 Token 使用量，悬停提示显示细分和成本
- **每日细分表** — 日期、会话数、输入 Token、输出 Token、缓存命中率和每日成本
- **按模型细分** — 显示每个使用过的模型、其会话数、Token 使用量和估计成本的表格

### 定时任务

创建和管理定时任务，按重复计划运行 Agent 提示词。

- **创建** — 填写名称（可选）、提示词、cron 表达式（例如 `0 9 * * *`）和交付目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** — 每个任务显示其名称、提示词预览、计划表达式、状态徽章（启用/暂停/错误）、交付目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活动状态和暂停状态之间切换任务
- **立即触发** — 在正常计划之外立即执行任务
- **删除** — 永久删除定时任务

### 技能

浏览、搜索和切换技能与工具集。技能从 `~/.hermes/skills/` 加载，并按类别分组。

- **搜索** — 按名称、描述或类别过滤技能和工具集
- **类别过滤器** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、Red Teaming、AI）
- **切换** — 使用开关启用或禁用单个技能。更改将在下一个会话中生效。
- **工具集** — 一个单独的部分显示内置工具集（文件操作、网页浏览等），包括其活动/非活动状态、设置要求和包含的工具列表

:::warning 安全
Web 仪表板会读取和写入您的 `.env` 文件，该文件包含 API 密钥和机密信息。默认情况下，它绑定到 `127.0.0.1` — 仅可从您的本地机器访问。如果您绑定到 `0.0.0.0`，您网络上的任何人都可以查看和修改您的凭据。仪表板本身没有身份验证机制。
:::

## `/reload` 斜杠命令

仪表板的 PR 还为交互式 CLI 添加了一个 `/reload` 斜杠命令。通过 Web 仪表板（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 来获取更改，而无需重启：

```
You → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将把 `~/.hermes/.env` 重新读入正在运行的进程的环境中。当您通过仪表板添加了新的提供商密钥并希望立即使用时，这非常有用。

## REST API

Web 仪表板公开了一个供前端使用的 REST API。您也可以直接调用这些端点以实现自动化：

### GET /api/status

返回 Agent 版本、消息网关状态、平台状态和活跃会话数。

### GET /api/sessions

返回最近 20 个会话及其元数据（模型、Token 计数、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式 — 类型、描述、类别以及适用的选择选项。前端使用此信息为每个字段渲染正确的输入控件。

### PUT /api/config

保存新配置。请求体：`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量及其设置/未设置状态、脱敏值、描述和类别。

### PUT /api/env

设置环境变量。请求体：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

删除环境变量。请求体：`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\}

返回单个会话的元数据。

### GET /api/sessions/\{session_id\}/messages

返回会话的完整消息历史记录，包括工具调用和时间戳。

### GET /api/sessions/search

跨消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 和高亮片段。

### DELETE /api/sessions/\{session_id\}

删除会话及其消息历史记录。

### GET /api/logs

返回日志行。查询参数：`file`（agent/errors/gateway）、`lines`（数量）、`level`、`component`。

### GET /api/analytics/usage

返回 Token 使用量、成本和会话分析。查询参数：`days`（默认 30）。响应包括每日细分和按模型汇总的数据。

### GET /api/cron/jobs

返回所有配置的定时任务及其状态、计划和运行历史记录。
### POST /api/cron/jobs

创建一个新的定时任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停一个定时任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复一个已暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger

立即触发一个定时任务（不按计划时间）。

### DELETE /api/cron/jobs/\{job_id\}

删除一个定时任务。

### GET /api/skills

返回所有技能，包含其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集，包含其标签、描述、工具列表以及激活/配置状态。

## CORS

Web 服务器将 CORS 限制为仅允许 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119` (生产环境)
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173` (Vite 开发服务器)

如果你在自定义端口上运行服务器，该来源会自动添加。

## 开发

如果你正在为 Web 仪表盘前端做贡献：

```bash
# 终端 1：启动后端 API
hermes dashboard --no-open

# 终端 2：启动带有 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/` 目录，由 FastAPI 服务器作为静态 SPA 提供。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这确保了仪表盘与代码更新保持同步。如果未安装 `npm`，更新将跳过前端构建，`hermes dashboard` 会在首次启动时构建它。

## 主题

主题控制仪表盘在三个层面的视觉呈现：

- **调色板** — 颜色（背景、文本、强调色、暖光、噪点）
- **排版** — 字体族、基础大小、行高、字间距
- **布局** — 圆角半径和密度（间距乘数）

从标题栏实时切换主题 — 点击语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 中的 `dashboard.theme` 下，并在页面加载时恢复。

### 内置主题

每个内置主题都自带其调色板、排版和布局 — 切换会产生超越颜色之外的可见变化。

| 主题 | 调色板 | 排版 | 布局 |
|-------|---------|------------|--------|
| **Hermes 蓝绿色** (`default`) | 深蓝绿色 + 奶油色 | 系统堆栈，15px | 0.5rem 半径，舒适 |
| **午夜** (`midnight`) | 深蓝紫色 | Inter + JetBrains Mono, 14px | 0.75rem 半径，舒适 |
| **余烬** (`ember`) | 暖绯红 / 青铜色 | Spectral (衬线体) + IBM Plex Mono, 15px | 0.25rem 半径，舒适 |
| **单色** (`mono`) | 灰度 | IBM Plex Sans + IBM Plex Mono, 13px | 0 半径，紧凑 |
| **赛博朋克** (`cyberpunk`) | 黑色背景上的霓虹绿 | 全部使用 Share Tech Mono, 14px | 0 半径，紧凑 |
| **玫瑰** (`rose`) | 粉色和象牙色 | Fraunces (衬线体) + DM Mono, 16px | 1rem 半径，宽敞 |

引用 Google Fonts 的主题（除 Hermes 蓝绿色外的所有主题）会按需加载样式表 — 首次切换到它们时，会向 `<head>` 注入一个 `<link>` 标签。

### 自定义主题

将 YAML 文件放入 `~/.hermes/dashboard-themes/` 目录，它会自动出现在选择器中。文件可以非常简单，只需一个名称加上你想要覆盖的字段 — 每个缺失的字段都会继承一个合理的默认值。

最小示例（仅颜色，使用简写十六进制）：

```yaml
# ~/.hermes/dashboard-themes/neon.yaml
name: neon
label: Neon
description: 纯洋红色配黑色
colors:
  background: "#000000"
  midground: "#ff00ff"
```

完整示例（包含所有可调参数）：

```yaml
# ~/.hermes/dashboard-themes/ocean.yaml
name: ocean
label: Ocean Deep
description: 深海蓝配珊瑚色点缀

palette:
  background:
    hex: "#0a1628"
    alpha: 1.0
  midground:
    hex: "#a8d0ff"
    alpha: 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0.0
  warmGlow: "rgba(255, 107, 107, 0.35)"
  noiseOpacity: 0.7

typography:
  fontSans: "Poppins, system-ui, sans-serif"
  fontMono: "Fira Code, ui-monospace, monospace"
  fontDisplay: "Poppins, system-ui, sans-serif"   # 可选，回退到 fontSans
  fontUrl: "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap"
  baseSize: "15px"
  lineHeight: "1.6"
  letterSpacing: "-0.003em"

layout:
  radius: "0.75rem"      # 0 | 0.25rem | 0.5rem | 0.75rem | 1rem | 任意长度
  density: comfortable   # compact | comfortable | spacious

# 可选 — 固定本应从调色板派生的单个 shadcn token。
# 此处列出的任何键都会覆盖调色板级联。
colorOverrides:
  destructive: "#ff6b6b"
  ring: "#ff6b6b"
```

创建文件后刷新仪表盘。

### 调色板模型

调色板是一个 3 层三元组 — **背景色**、**中间色**、**前景色** — 加上一个暖光 rgba() 字符串和一个噪点不透明度乘数。仪表盘样式表中的每个 shadcn token（card、muted、border、primary、popover 等）都通过 CSS `color-mix()` 从这个三元组派生而来，因此覆盖三种颜色会级联影响整个 UI。

- `background` — 最深的画布颜色（通常接近黑色）。页面背景和卡片填充色来源于此。
- `midground` — 主要文本和强调色。大多数 UI 元素使用此颜色。
- `foreground` — 顶层高亮色。在默认主题中，这是 alpha 为 0 的白色（不可见）；想要在顶部有明亮强调色的主题可以提高其 alpha 值。
- `warmGlow` — 环境背景使用的 rgba() 晕影颜色。
- `noiseOpacity` — 0–1.2 的噪点叠加层乘数。越低 = 越柔和，越高 = 颗粒感越强。

每一层接受 `{hex, alpha}` 或一个纯十六进制字符串（alpha 默认为 1.0）。

### 排版模型
| 键名 | 类型 | 描述 |
|-----|------|-------------|
| `fontSans` | 字符串 | 用于正文的 CSS font-family 堆栈（应用于 `html`、`body`） |
| `fontMono` | 字符串 | 用于代码块、`<code>`、`.font-mono` 工具类、密集读数显示的 CSS font-family 堆栈 |
| `fontDisplay` | 字符串 | 可选的标题/展示字体堆栈。回退到 `fontSans` |
| `fontUrl` | 字符串 | 可选的外部样式表 URL。在主题切换时作为 `<link rel="stylesheet">` 注入到 `<head>` 中。相同的 URL 不会被重复注入。适用于 Google Fonts、Bunny Fonts、自托管的 `@font-face` 样式表，任何可以链接的内容 |
| `baseSize` | 字符串 | 根字体大小 — 控制整个仪表板的 rem 比例。例如：`"14px"`、`"16px"` |
| `lineHeight` | 字符串 | 默认行高，例如 `"1.5"`、`"1.65"` |
| `letterSpacing` | 字符串 | 默认字母间距，例如 `"0"`、`"0.01em"`、`"-0.01em"` |

### 布局模型

| 键名 | 值 | 描述 |
|-----|--------|-------------|
| `radius` | 任意 CSS 长度 | 圆角半径 Token。级联到 `--radius-sm/md/lg/xl`，因此每个圆角元素会一起变化。 |
| `density` | `compact` \| `comfortable` \| `spacious` | 间距乘数。紧凑 = 0.85×，舒适 = 1.0×（默认），宽松 = 1.2×。缩放 Tailwind 的基础间距，因此内边距、间隙和 space-between 工具类都会按比例变化。 |

### 颜色覆盖（可选）

大多数主题不需要这个 — 三层调色板会派生出所有 shadcn Token。但如果你想要一个派生无法产生的特定强调色（例如柔和主题中更柔和的破坏性红色，或品牌特定的成功绿色），可以在这里固定单个 Token。

支持的键名：`card`、`cardForeground`、`popover`、`popoverForeground`、`primary`、`primaryForeground`、`secondary`、`secondaryForeground`、`muted`、`mutedForeground`、`accent`、`accentForeground`、`destructive`、`destructiveForeground`、`success`、`warning`、`border`、`input`、`ring`。

此处设置的任何键名都会覆盖活动主题的派生值 — 切换到另一个主题会清除覆盖。

### 布局变体

`layoutVariant` 选择整体外壳布局。默认为 `standard`。

| 变体 | 行为 |
|---------|-----------|
| `standard` | 单列，最大宽度 1600px（默认） |
| `cockpit` | 左侧边栏轨道（260px）+ 主要内容。由插件通过 `sidebar` 插槽填充 |
| `tiled` | 取消最大宽度限制，使页面可以使用完整的视口 |

```yaml
layoutVariant: cockpit
```

当前变体通过 `document.documentElement.dataset.layoutVariant` 暴露，因此自定义 CSS 可以通过 `:root[data-layout-variant="cockpit"]` 来定位它。

### 主题资源

为主题提供艺术资源 URL。每个命名的插槽都会变成一个 CSS 变量（`--theme-asset-<name>`），供插件和内置外壳读取；`bg` 插槽会自动连接到背景。

```yaml
assets:
  bg: "https://example.com/hero-bg.jpg"       # 全视口背景
  hero: "/my-images/strike-freedom.png"       # 用于插件侧边栏
  crest: "/my-images/crest.svg"               # 用于页眉插槽插件
  logo: "/my-images/logo.png"
  sidebar: "/my-images/rail.png"
  header: "/my-images/header-art.png"
  custom:
    scanLines: "/my-images/scanlines.png"     # → --theme-asset-custom-scanLines
```

值接受裸 URL（自动包装在 `url(...)` 中）、预包装的 `url(...)`/`linear-gradient(...)`/`radial-gradient(...)` 表达式，以及 `none`。

### 组件外观覆盖

主题可以通过 `componentStyles` 块重新设计单个外壳组件的样式，而无需编写 CSS 选择器。每个桶的条目都会变成 CSS 变量（`--component-<bucket>-<kebab-property>`），由外壳的共享组件读取 — 因此 `card:` 覆盖应用于每个 `<Card>`，`header:` 应用于应用栏，等等。

```yaml
componentStyles:
  card:
    clipPath: "polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px)"
    background: "linear-gradient(180deg, rgba(10, 22, 52, 0.85), rgba(5, 9, 26, 0.92))"
    boxShadow: "inset 0 0 0 1px rgba(64, 200, 255, 0.28)"
  header:
    background: "linear-gradient(180deg, rgba(16, 32, 72, 0.95), rgba(5, 9, 26, 0.9))"
  tab:
    clipPath: "polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)"
  sidebar: {...}
  backdrop: {...}
  footer: {...}
  progress: {...}
  badge: {...}
  page: {...}
```

支持的桶：`card`、`header`、`footer`、`sidebar`、`tab`、`progress`、`badge`、`backdrop`、`page`。属性名使用驼峰式（`clipPath`）并以短横线分隔（`clip-path`）形式发出。值是纯 CSS 字符串 — CSS 接受的任何内容（`clip-path`、`border-image`、`background`、`box-shadow`、动画等）。

### 自定义 CSS

对于不适合 `componentStyles` 的选择器级外观 — 伪元素、动画、媒体查询、主题范围的覆盖 — 将原始 CSS 放入 `customCSS` 字段：

```yaml
customCSS: |
  :root[data-layout-variant="cockpit"] body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 100;
    background: repeating-linear-gradient(to bottom,
      transparent 0px, transparent 2px,
      rgba(64, 200, 255, 0.035) 3px, rgba(64, 200, 255, 0.035) 4px);
    mix-blend-mode: screen;
  }
```

CSS 在应用主题时作为单个作用域的 `<style data-hermes-theme-css>` 标签注入，并在主题切换时清理。每个主题限制为 32 KiB。

## 仪表板插件

插件位于 `~/.hermes/plugins/<name>/dashboard/`（用户）或仓库 `plugins/<name>/dashboard/`（捆绑）。每个插件都包含一个 `manifest.json` 和一个使用 `window.__HERMES_PLUGIN_SDK__` 上暴露的插件 SDK 的纯 JS 包。

### 清单

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills",
    "override": "/",
    "hidden": false
  },
  "slots": ["sidebar", "header-left"],
  "entry": "dist/index.js",
  "css": "dist/index.css",
  "api": "api.py"
}
```

| 字段 | 描述 |
|-------|-------------|
| `tab.path` | 插件组件渲染的路由路径 |
| `tab.position` | `end`、`after:<tab>` 或 `before:<tab>` |
| `tab.override` | 当设置为内置路径（`/`、`/sessions` 等）时，此插件将替换该页面，而不是添加新标签页 |
| `tab.hidden` | 为 true 时，注册组件 + 插槽但跳过导航条目。用于仅插槽插件 |
| `slots` | 此插件填充的外壳插槽（文档辅助；实际注册从 JS 包中进行） |
### Shell 插槽

插件通过调用 `window.__HERMES_PLUGINS__.registerSlot(pluginName, slotName, Component)` 将组件注入到命名的 Shell 位置。多个插件可以填充同一个插槽——它们会按照注册顺序堆叠渲染。

| 插槽 | 位置 |
|------|----------|
| `backdrop` | 背景层堆叠内部 |
| `header-left` | 顶部栏中 Hermes 品牌标识之前 |
| `header-right` | 主题/语言切换器之前 |
| `header-banner` | 导航栏下方的全宽条带 |
| `sidebar` | 驾驶舱侧边栏轨道（仅在 `layoutVariant === "cockpit"` 时渲染） |
| `pre-main` | 路由出口上方 |
| `post-main` | 路由出口下方 |
| `footer-left` / `footer-right` | 页脚单元格内容（替换默认内容） |
| `overlay` | 位于所有内容之上的固定定位层 |

### 插件 SDK

在 `window.__HERMES_PLUGIN_SDK__` 上暴露：

- `React` + `hooks` (useState, useEffect, useCallback, useMemo, useRef, useContext, createContext)
- `components` — Card, Badge, Button, Input, Label, Select, Separator, Tabs, **PluginSlot**
- `api` — Hermes API 客户端，以及原始的 `fetchJSON`
- `utils` — `cn()`, `timeAgo()`, `isoTimeAgo()`
- `useI18n` — 用于多语言插件的 i18n 钩子

### 演示：强袭自由驾驶舱

`plugins/strike-freedom-cockpit/` 附带了一个完整的皮肤演示，展示了所有扩展点——驾驶舱布局变体、主题提供的英雄/徽章资源、通过 `componentStyles` 实现的凹槽卡片角、通过 `customCSS` 实现的扫描线，以及一个仅包含插槽的插件，用于填充侧边栏、页眉和页脚。将主题 YAML 复制到 `~/.hermes/dashboard-themes/` 并将插件目录复制到 `~/.hermes/plugins/` 即可试用。

### 主题 API

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/themes` | GET | 列出可用主题 + 活动主题名称。内置主题返回 `{name, label, description}`；用户主题还包含一个 `definition` 字段，其中包含完整的规范化主题对象。 |
| `/api/dashboard/theme` | PUT | 设置活动主题。请求体：`{"name": "midnight"}` |