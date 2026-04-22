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

这将启动一个本地 Web 服务器，并在您的浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全在您的机器上运行 —— 没有任何数据离开本地主机。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | 运行 Web 服务器的端口 |
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

## 先决条件

Web 仪表盘需要 FastAPI 和 Uvicorn。使用以下命令安装：

```bash
pip install hermes-agent[web]
```

如果您使用 `pip install hermes-agent[all]` 安装，则 Web 依赖项已包含在内。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

## 页面

### 状态

落地页显示您安装的实时概览：

- **Agent 版本**和发布日期
- **消息网关状态** —— 运行/停止、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### 配置

基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都从 `DEFAULT_CONFIG` 自动发现，并按选项卡分类组织：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（local/docker/ssh/modal）、超时、Shell 偏好
- **display** —— 皮肤、工具进度、恢复显示、加载动画设置
- **agent** —— 最大迭代次数、消息网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理工作量
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（ask/yolo/deny）
- 以及更多 —— config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉菜单。布尔值呈现为开关。其他所有内容都是文本输入框。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（在您点击保存之前不会保存）
- **导出** —— 将当前配置下载为 JSON
- **导入** —— 上传 JSON 配置文件以替换当前值

:::tip
配置更改在下一个 Agent 会话或消息网关重启时生效。Web 仪表盘编辑的是与 `hermes config set` 和消息网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** —— OpenRouter、Anthropic、OpenAI、DeepSeek 等。
- **工具 API 密钥** —— Browserbase、Firecrawl、Tavily、ElevenLabs 等。
- **消息平台** —— Telegram、Discord、Slack 机器人令牌等。
- **Agent 设置** —— 非机密环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（带有值的脱敏预览）
- 其用途的描述
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 用于删除它的按钮

高级/不常用的密钥默认隐藏在切换开关后面。

### 会话

浏览和检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用数量以及上次活跃时间。实时会话标有脉动徽章。

- **搜索** —— 使用 FTS5 在所有消息内容中进行全文搜索。结果显示高亮片段，展开时自动滚动到第一条匹配的消息。
- **展开** —— 点击会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并渲染为带有语法高亮的 Markdown。
- **工具调用** —— 包含工具调用的助手消息显示可折叠块，其中包含函数名称和 JSON 参数。
- **删除** —— 使用垃圾桶图标删除会话及其消息历史记录。

### 日志

查看 Agent、消息网关和错误日志文件，支持过滤和实时跟踪。

- **文件** —— 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** —— 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** —— 按源组件过滤：all、gateway、agent、tools、cli 或 cron
- **行数** —— 选择显示多少行（50、100、200 或 500）
- **自动刷新** —— 切换实时跟踪，每 5 秒轮询新的日志行
- **颜色编码** —— 日志行按严重程度着色（错误为红色，警告为黄色，调试信息为暗淡色）

### 分析

根据会话历史记录计算的用量和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** —— 总 Token 数（输入/输出）、缓存命中率、总估计或实际成本，以及总会话数和日均值
- **每日 Token 图表** —— 堆叠条形图，显示每天的输入和输出 Token 使用量，悬停工具提示显示细分和成本
- **每日细分表** —— 日期、会话数、输入 Token、输出 Token、缓存命中率和每日成本
- **按模型细分** —— 显示每个使用模型的表格，包含其会话数、Token 使用量和估计成本
### 定时任务

创建和管理定时任务，按重复计划运行 Agent 提示词。

- **创建** — 填写名称（可选）、提示词、cron 表达式（例如 `0 9 * * *`）和投递目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** — 每个任务显示其名称、提示词预览、计划表达式、状态徽章（启用/暂停/错误）、投递目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活动状态和暂停状态之间切换任务
- **立即触发** — 在正常计划之外立即执行任务
- **删除** — 永久删除定时任务

### 技能

浏览、搜索和切换技能与工具集。技能从 `~/.hermes/skills/` 加载并按类别分组。

- **搜索** — 按名称、描述或类别筛选技能和工具集
- **类别筛选器** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、Red Teaming、AI）
- **切换** — 使用开关启用或禁用单个技能。更改将在下次会话生效。
- **工具集** — 单独的部分显示内置工具集（文件操作、网页浏览等），包括其活动/非活动状态、设置要求和包含的工具列表

:::warning 安全
Web 控制台会读取和写入你的 `.env` 文件，该文件包含 API 密钥和机密信息。默认情况下，它绑定到 `127.0.0.1` —— 仅可从本地机器访问。如果绑定到 `0.0.0.0`，则网络上的任何人都可以查看和修改你的凭据。控制台本身没有身份验证。
:::

## `/reload` 斜杠命令

此控制台 PR 还在交互式 CLI 中添加了 `/reload` 斜杠命令。通过 Web 控制台（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 来获取更改而无需重启：

```
你 → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将重新读取 `~/.hermes/.env` 到运行进程的环境中。当你通过控制台添加了新的提供商密钥并希望立即使用时非常有用。

## REST API

Web 控制台公开了一个供前端使用的 REST API。你也可以直接调用这些端点进行自动化操作：

### GET /api/status

返回 Agent 版本、消息网关状态、平台状态和活动会话计数。

### GET /api/sessions

返回最近的 20 个会话及其元数据（模型、Token 计数、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式 —— 类型、描述、类别以及适用的选项。前端使用此信息为每个字段渲染正确的输入组件。

### PUT /api/config

保存新配置。请求体：`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量及其设置/未设置状态、脱敏值、描述和类别。

### PUT /api/env

设置环境变量。请求体：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

移除环境变量。请求体：`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\}

返回单个会话的元数据。

### GET /api/sessions/\{session_id\}/messages

返回会话的完整消息历史记录，包括工具调用和时间戳。

### GET /api/sessions/search

跨消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 和高亮片段。

### DELETE /api/sessions/\{session_id\}

删除会话及其消息历史记录。

### GET /api/logs

返回日志行。查询参数：`file` (agent/errors/gateway)、`lines` (数量)、`level`、`component`。

### GET /api/analytics/usage

返回 Token 使用量、成本和会话分析。查询参数：`days` (默认 30)。响应包括每日细分和按模型聚合的数据。

### GET /api/cron/jobs

返回所有配置的定时任务及其状态、计划和运行历史。

### POST /api/cron/jobs

创建新的定时任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停定时任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复已暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger

在计划之外立即触发定时任务。

### DELETE /api/cron/jobs/\{job_id\}

删除定时任务。

### GET /api/skills

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表和活动/已配置状态。

## CORS

Web 服务器将 CORS 限制为仅限 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119` (生产环境)
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173` (Vite 开发服务器)

如果你在自定义端口上运行服务器，该来源会自动添加。

## 开发

如果你正在为 Web 控制台前端做贡献：

```bash
# 终端 1：启动后端 API
hermes dashboard --no-open

# 终端 2：启动带 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/`，FastAPI 服务器将其作为静态 SPA 提供服务。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这使控制台与代码更新保持同步。如果未安装 `npm`，更新将跳过前端构建，`hermes dashboard` 将在首次启动时构建它。

## 主题

控制台支持视觉主题，可更改颜色、叠加效果和整体感觉。从标题栏实时切换主题 —— 点击语言切换器旁边的调色板图标。
### 内置主题

| 主题 | 描述 |
|-------|-------------|
| **Hermes 青绿色** | 经典深青绿色（默认） |
| **午夜** | 深蓝紫色搭配冷色调点缀 |
| **余烬** | 暖色调深红与青铜色 |
| **单色** | 简洁的灰度，极简风格 |
| **赛博朋克** | 黑色背景上的霓虹绿 |
| **玫瑰色** | 柔和的粉色与温暖的象牙色 |

主题选择会持久化到 `config.yaml` 中的 `dashboard.theme` 字段，并在页面加载时恢复。

### 自定义主题

在 `~/.hermes/dashboard-themes/` 目录下创建 YAML 文件：

```yaml
# ~/.hermes/dashboard-themes/ocean.yaml
name: ocean
label: Ocean
description: Deep sea blues with coral accents

colors:
  background: "#0a1628"
  foreground: "#e0f0ff"
  card: "#0f1f35"
  card-foreground: "#e0f0ff"
  primary: "#ff6b6b"
  primary-foreground: "#0a1628"
  secondary: "#152540"
  secondary-foreground: "#e0f0ff"
  muted: "#1a2d4a"
  muted-foreground: "#7899bb"
  accent: "#1f3555"
  accent-foreground: "#e0f0ff"
  destructive: "#fb2c36"
  destructive-foreground: "#fff"
  success: "#4ade80"
  warning: "#fbbf24"
  border: "color-mix(in srgb, #ff6b6b 15%, transparent)"
  input: "color-mix(in srgb, #ff6b6b 15%, transparent)"
  ring: "#ff6b6b"
  popover: "#0f1f35"
  popover-foreground: "#e0f0ff"

overlay:
  noiseOpacity: 0.08
  noiseBlendMode: color-dodge
  warmGlowOpacity: 0.15
  warmGlowColor: "rgba(255,107,107,0.2)"
```

这 21 个颜色 Token 直接映射到仪表板中使用的 CSS 自定义属性。自定义主题的所有字段都是必需的。`overlay` 部分是可选的——它控制颗粒纹理和环境光晕效果。

创建文件后刷新仪表板。自定义主题将与内置主题一起出现在主题选择器中。

### 主题 API

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/themes` | GET | 列出可用主题 + 当前激活的主题名称 |
| `/api/dashboard/theme` | PUT | 设置激活的主题。请求体：`{"name": "midnight"}` |