---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的仪表盘，用于管理配置、API 密钥、会话、日志、分析、定时任务和技能"
---

# Web 仪表盘

Web 仪表盘是一个基于浏览器的用户界面，用于管理您的 Hermes Agent 安装。您可以通过简洁的 Web 界面配置设置、管理 API 密钥和监控会话，而无需编辑 YAML 文件或运行 CLI 命令。

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
| `--insecure` | off | 允许绑定到非本地主机地址（**危险** —— 会在网络上暴露 API 密钥；需配合防火墙和强身份验证使用） |
| `--tui` | off | 在浏览器中暴露 Chat 标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`）。或者设置 `HERMES_DASHBOARD_TUI=1`。 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有网络接口（在共享网络上使用需谨慎）
hermes dashboard --host 0.0.0.0

# 启动但不打开浏览器
hermes dashboard --no-open
```

## 前提条件

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 助手 —— 这些是可选的额外组件。**Web 仪表盘**需要 FastAPI 和 Uvicorn（`web` 额外依赖）。**Chat** 标签页还需要 `ptyprocess` 来在伪终端后生成嵌入式 TUI（POSIX 系统上的 `pty` 额外依赖）。使用以下命令安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 额外依赖会拉取 FastAPI/Uvicorn；`pty` 会拉取 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows —— 请注意嵌入式 TUI 本身仍需要 WSL）。`pip install hermes-agent[all]` 包含这两个额外依赖，如果您还想要消息/语音等功能，这是最简单的路径。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

## 页面

### 状态

落地页显示您安装的实时概览：

- **Agent 版本**和发布日期
- **消息网关状态** —— 运行/停止状态、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### Chat

**Chat** 标签页将完整的 Hermes TUI（与您从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。您在终端 TUI 中可以做的所有事情 —— 斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、澄清/sudo/批准提示、皮肤主题 —— 在这里都完全相同，因为仪表盘正在运行真正的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，以实现像素完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个使用仪表盘会话 Token 认证的 WebSocket
- 服务器在 POSIX 伪终端后生成 `hermes --tui`
- 按键传输到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格；鼠标跟踪（SGR 1006）、宽字符（Unicode 11）和方框绘制字形都能原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 大小

**恢复现有会话：** 在 **Sessions** 标签页中，点击任意会话旁边的播放图标（▶）。这将跳转到 `/chat?resume=<id>` 并使用 `--resume` 启动 TUI，加载完整历史记录。

**前提条件：**

- Node.js（与 `hermes --tui` 的要求相同；TUI 包在首次启动时构建）
- `ptyprocess` —— 由 `pty` 额外依赖安装（`pip install 'hermes-agent[web,pty]'`，或 `[all]` 包含两者）
- POSIX 内核（Linux、macOS 或 WSL）。不支持原生 Windows Python —— 请使用 WSL。

关闭浏览器标签页，服务器上的 PTY 会被干净地回收。重新打开会生成一个新的会话。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都从 `DEFAULT_CONFIG` 自动发现，并按标签页分类组织：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（local/docker/ssh/modal）、超时、Shell 偏好
- **display** —— 皮肤、工具进度、恢复显示、加载动画设置
- **agent** —— 最大迭代次数、消息网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理努力程度
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（ask/yolo/deny）
- 以及更多 —— config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）渲染为下拉菜单。布尔值渲染为开关。其他所有内容都是文本输入框。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（在您点击保存之前不会保存）
- **导出** —— 将当前配置下载为 JSON 文件
- **导入** —— 上传 JSON 配置文件以替换当前值

:::tip
配置更改在下一次 Agent 会话或消息网关重启时生效。Web 仪表盘编辑的是与 `hermes config set` 和消息网关读取的同一个 `config.yaml` 文件。
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
高级/不常用的配置项默认隐藏在切换按钮后。

### 会话

浏览和检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用数量以及上次活跃时间。活跃会话会有一个脉动徽章标记。

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。结果会显示高亮片段，展开时会自动滚动到第一条匹配的消息。
- **展开** — 点击一个会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并以 Markdown 格式渲染，支持语法高亮。
- **工具调用** — 包含工具调用的助手消息会显示可折叠的区块，其中包含函数名和 JSON 参数。
- **删除** — 使用垃圾桶图标删除会话及其消息历史记录。

### 日志

查看 Agent、消息网关和错误日志文件，支持过滤和实时跟踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：all、gateway、agent、tools、cli 或 cron
- **行数** — 选择显示多少行（50、100、200 或 500）
- **自动刷新** — 切换实时跟踪功能，每 5 秒轮询一次新的日志行
- **颜色编码** — 日志行按严重程度着色（红色表示错误，黄色表示警告，灰色表示调试信息）

### 分析

根据会话历史记录计算的使用情况和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** — 总 Token 数（输入/输出）、缓存命中率、总估计或实际成本，以及总会话数和日均值
- **每日 Token 图表** — 堆叠条形图，显示每天的输入和输出 Token 使用情况，悬停提示显示细分和成本
- **每日细分表** — 日期、会话数、输入 Token、输出 Token、缓存命中率和每日成本
- **按模型细分** — 显示每个使用过的模型、其会话数、Token 使用量和估计成本的表格

### 定时任务

创建和管理按计划重复运行 Agent 提示词的定时任务。

- **创建** — 填写名称（可选）、提示词、cron 表达式（例如 `0 9 * * *`）和交付目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** — 每个任务显示其名称、提示词预览、计划表达式、状态徽章（启用/暂停/错误）、交付目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活动状态和暂停状态之间切换任务
- **立即触发** — 在正常计划之外立即执行任务
- **删除** — 永久删除定时任务

### 技能

浏览、搜索和切换技能与工具集。技能从 `~/.hermes/skills/` 加载并按类别分组。

- **搜索** — 按名称、描述或类别过滤技能和工具集
- **类别过滤器** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、Red Teaming、AI）
- **切换** — 使用开关启用或禁用单个技能。更改将在下一个会话中生效。
- **工具集** — 一个单独的部分显示内置工具集（文件操作、网页浏览等），包括其活动/非活动状态、设置要求和包含的工具列表

:::warning 安全
Web 仪表板会读取和写入您的 `.env` 文件，该文件包含 API 密钥和机密信息。它默认绑定到 `127.0.0.1` — 仅可从您的本地机器访问。如果您绑定到 `0.0.0.0`，您网络上的任何人都可以查看和修改您的凭据。仪表板本身没有身份验证机制。
:::

## `/reload` 斜杠命令

仪表板 PR 还为交互式 CLI 添加了一个 `/reload` 斜杠命令。通过 Web 仪表板（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 来获取更改而无需重启：

```
You → /reload
  已重新加载 .env (更新了 3 个变量)
```

这将重新读取 `~/.hermes/.env` 到正在运行的进程环境中。当您通过仪表板添加了新的提供商密钥并希望立即使用时，这非常有用。

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

返回描述每个配置字段的模式 — 类型、描述、类别以及适用的选项。前端使用此信息为每个字段渲染正确的输入控件。

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

对消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 和高亮片段。

### DELETE /api/sessions/\{session_id\}

删除会话及其消息历史记录。

### GET /api/logs

返回日志行。查询参数：`file` (agent/errors/gateway)、`lines` (数量)、`level`、`component`。

### GET /api/analytics/usage

返回 Token 使用情况、成本和会话分析。查询参数：`days` (默认 30)。响应包括每日细分和按模型聚合的数据。

### GET /api/cron/jobs
返回所有已配置的定时任务及其状态、调度计划和运行历史。

### POST /api/cron/jobs

创建一个新的定时任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停一个定时任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复一个已暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger

立即触发一个定时任务（不按调度计划）。

### DELETE /api/cron/jobs/\{job_id\}

删除一个定时任务。

### GET /api/skills

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表和激活/配置状态。

## CORS

Web 服务器将 CORS 限制为仅限 localhost 源：

- `http://localhost:9119` / `http://127.0.0.1:9119` (生产环境)
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173` (Vite 开发服务器)

如果你在自定义端口上运行服务器，该源会自动添加。

## 开发

如果你正在为 Web 仪表板前端做贡献：

```bash
# 终端 1：启动后端 API
hermes dashboard --no-open

# 终端 2：启动带 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/`，由 FastAPI 服务器作为静态 SPA 提供服务。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这使仪表板与代码更新保持同步。如果未安装 `npm`，更新将跳过前端构建，`hermes dashboard` 将在首次启动时构建它。

## 主题与插件

仪表板内置了六个主题，并可通过用户定义的主题、插件标签和后端 API 路由进行扩展——全部即插即用，无需克隆仓库。

**实时切换主题**——从标题栏中，点击语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 中的 `dashboard.theme` 下，并在页面加载时恢复。

内置主题：

| 主题 | 特点 |
|-------|-----------|
| **Hermes 蓝绿色** (`default`) | 深蓝绿色 + 奶油色，系统字体，舒适的间距 |
| **午夜** (`midnight`) | 深蓝紫色，Inter + JetBrains Mono 字体 |
| **余烬** (`ember`) | 暖深红色 + 青铜色，Spectral 衬线体 + IBM Plex Mono 字体 |
| **单色** (`mono`) | 灰度，IBM Plex 字体，紧凑 |
| **赛博朋克** (`cyberpunk`) | 黑色背景上的霓虹绿色，Share Tech Mono 字体 |
| **玫瑰** (`rose`) | 粉色 + 象牙色，Fraunces 衬线体，宽敞 |

要构建自己的主题、添加插件标签、注入到 shell 插槽或暴露插件特定的 REST 端点，请参阅 **[扩展仪表板](./extending-the-dashboard)**——完整指南涵盖：

- 主题 YAML 模式——调色板、排版、布局、资源、componentStyles、colorOverrides、customCSS
- 布局变体——`standard`、`cockpit`、`tiled`
- 插件清单、SDK、shell 插槽、页面作用域插槽（将小部件注入到内置页面中，而无需覆盖它们）、后端 FastAPI 路由
- 完整的主题加插件组合演练（强袭自由驾驶舱演示）
- 发现、重新加载和故障排除