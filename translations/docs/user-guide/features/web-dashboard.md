---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的管理面板，用于管理配置、API 密钥、MCP 服务器、消息配对、Webhook、消息网关、记忆、凭证、会话、日志、分析、定时任务和技能"
---

# Web 仪表盘

Web 仪表盘是一个基于浏览器的用户界面，用于管理您的 Hermes Agent 安装。您可以通过简洁的 Web 界面配置设置、管理 API 密钥和监控会话，而无需编辑 YAML 文件或运行 CLI 命令。

:::tip
托管模式的身份验证使用 Nous Portal OAuth；如果您还希望仪表盘与真实的后端通信，`hermes setup --portal` 也会连接模型和工具网关。请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 快速开始

```bash
hermes dashboard
```

这将启动一个本地 Web 服务器，并在您的浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全在您的机器上运行 —— 数据不会离开本地主机。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | 运行 Web 服务器的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | 关闭 | 允许绑定到非本地主机地址 (**危险** —— 会在网络上暴露 API 密钥；请配合防火墙和强身份验证使用) |
| `--tui` | 关闭 | 在浏览器中启用 Chat 标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`）。或者设置 `HERMES_DASHBOARD_TUI=1`。 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有网络接口（在共享网络上使用需谨慎）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open

# 启用浏览器内的 Chat 标签页
hermes dashboard --tui
```

## 前提条件

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 辅助程序 —— 这些是可选的额外组件。**Web 仪表盘** 需要 FastAPI 和 Uvicorn (`web` 额外组件)。**Chat** 标签页还需要 `ptyprocess` 来在伪终端后生成嵌入的 TUI（在 POSIX 系统上是 `pty` 额外组件）。使用以下命令安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 额外组件会拉取 FastAPI/Uvicorn；`pty` 会拉取 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows —— 请注意，嵌入的 TUI 本身仍然需要 WSL）。`pip install hermes-agent[all]` 包含这两个额外组件，如果您还想要消息/语音等功能，这是最简单的路径。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

Chat 标签页在普通的 `hermes dashboard` 启动时是默认关闭的。当您需要嵌入式的浏览器聊天窗格时，请使用 `hermes dashboard --tui` 启动仪表盘，或设置 `HERMES_DASHBOARD_TUI=1`。

## 页面

### 状态

落地页显示您安装的实时概览：

- **Agent 版本** 和发布日期
- **消息网关状态** —— 运行/停止、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### Chat

**Chat** 标签页将完整的 Hermes TUI（与您从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。您在终端 TUI 中可以做的所有事情 —— 斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、澄清/sudo/批准提示、皮肤主题 —— 在这里都完全相同，因为仪表盘正在运行真实的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，以实现像素完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个使用仪表盘会话 Token 进行身份验证的 WebSocket
- 服务器在 POSIX 伪终端后生成 `hermes --tui`
- 按键传输到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格；鼠标跟踪（SGR 1006）、宽字符（Unicode 11）和方框绘制字形都能原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 大小

**恢复现有会话：** 在 **Sessions** 标签页中，点击任意会话旁边的播放图标 (▶)。这将跳转到 `/chat?resume=<id>` 并使用 `--resume` 启动 TUI，加载完整的历史记录。

**前提条件：**

- Node.js（与 `hermes --tui` 的要求相同；TUI 包在首次启动时构建）
- `ptyprocess` —— 由 `pty` 额外组件安装（`pip install 'hermes-agent[web,pty]'`，或 `[all]` 包含两者）
- POSIX 内核（Linux、macOS 或 WSL2）。`/chat` 终端窗格特别需要 POSIX PTY —— 原生 Windows Python 没有等效功能，因此在原生 Windows 安装上，仪表盘的其余部分（会话、任务、指标、配置编辑器）可以工作，但 `/chat` 标签页会显示一个横幅，告诉您使用 WSL2 来获得该功能。

关闭浏览器标签页，服务器上的 PTY 会被干净地回收。重新打开会生成一个新的会话。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都从 `DEFAULT_CONFIG` 自动发现，并组织到分类标签页中：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（本地/docker/ssh/modal）、超时、Shell 偏好
- **display** —— 皮肤、工具进度、恢复显示、加载动画设置
- **agent** —— 最大迭代次数、网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理工作量
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（询问/随意/拒绝）
- 以及更多 —— config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉菜单。布尔值呈现为切换开关。其他所有内容都是文本输入框。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（在您点击保存之前不会保存）
- **导出** —— 将当前配置下载为 JSON 文件
- **导入** —— 上传 JSON 配置文件以替换当前值
:::提示
配置更改将在下一次 Agent 会话或消息网关重启时生效。Web 仪表板编辑的是与 `hermes config set` 和消息网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等。
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等。
- **消息平台** — Telegram、Discord、Slack 机器人令牌等。
- **Agent 设置** — 非机密的环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（附带值的脱敏预览）
- 其用途描述
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 用于删除它的按钮

高级/不常用的密钥默认隐藏在切换开关后面。

### 会话

浏览和检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、定时任务）、模型名称、消息数量、工具调用数量以及上次活动时间。活动会话标有脉动徽章。

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。结果显示高亮片段，展开时自动滚动到第一条匹配的消息。
- **统计** — 摘要栏显示会话总数、存储中活跃数量、已归档数量、消息总数以及按来源的细分。
- **展开** — 点击会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并以 Markdown 格式渲染，支持语法高亮。
- **工具调用** — 包含工具调用的助手消息显示可折叠块，其中包含函数名称和 JSON 参数。
- **重命名** — 内联设置或清除会话标题（铅笔图标）。
- **导出** — 将会话（元数据 + 完整消息历史记录）下载为 JSON（下载图标）。
- **清理** — 标题栏的“清理旧会话”按钮会删除早于 N 天且已结束的会话。
- **删除** — 使用垃圾桶图标删除会话及其消息历史记录。

![会话管理页面 — 统计栏、清理以及每行的重命名/导出/删除](/img/dashboard/admin-sessions.png)

### 日志

查看 Agent、消息网关和错误日志文件，支持过滤和实时跟踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：全部、gateway、agent、tools、cli 或 cron
- **行数** — 选择显示多少行（50、100、200 或 500）
- **自动刷新** — 切换实时跟踪，每 5 秒轮询一次新日志行
- **颜色编码** — 日志行按严重程度着色（错误为红色，警告为黄色，调试信息为灰色）

### 分析

根据会话历史记录计算的用量和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** — 总 Token 数（输入/输出）、缓存命中率、总估计或实际成本、会话总数及日均值
- **每日 Token 图表** — 堆叠条形图，显示每天的输入和输出 Token 使用量，悬停提示显示细分和成本
- **每日细分表** — 日期、会话数、输入 Token、输出 Token、缓存命中率和每日成本
- **按模型细分** — 表格显示使用的每个模型、其会话数、Token 使用量和估计成本

### 定时任务

创建和管理计划任务，按重复计划运行 Agent 提示词。

- **创建** — 填写名称（可选）、提示词、cron 表达式（例如 `0 9 * * *`）和交付目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** — 每个任务显示其名称、提示词预览、计划表达式、状态徽章（启用/暂停/错误）、交付目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活动状态和暂停状态之间切换任务
- **编辑** — 打开预填充的模态框以更改任务的提示词、计划、名称或交付目标
- **立即触发** — 在正常计划之外立即执行任务
- **删除** — 永久删除定时任务

### 技能

浏览、搜索和切换已安装的技能和工具集，并从中心安装新的。技能从 `~/.hermes/skills/` 加载并按类别分组。

- **搜索** — 按名称、描述或类别过滤已安装的技能和工具集
- **类别过滤器** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、Red Teaming、AI）
- **切换** — 使用开关启用或禁用单个技能。更改在下一次会话时生效。
- **工具集** — 一个单独的视图显示内置工具集（文件操作、网页浏览等），包括其活动/非活动状态、设置要求和包含的工具列表
- **浏览中心** — 第三个视图在所有来源中搜索技能中心（与 `hermes skills search` 相同），通过标识符安装任何结果并显示实时安装日志，并提供“全部更新”按钮来刷新已安装的技能。

![技能管理页面 — 浏览中心视图：搜索、安装和更新](/img/dashboard/admin-skills-hub.png)

### MCP

无需 CLI 即可管理 [MCP](/integrations/mcp) 服务器。与 `hermes mcp` 读取的 `config.yaml` 中的 `mcp_servers` 块相同。

**您的 MCP 服务器：**

- **添加** — 注册 HTTP/SSE 服务器（URL）或 stdio 服务器（命令 + 参数），对于 stdio 服务器可选的 `KEY=VALUE` 环境变量
- **启用 / 禁用** — 切换服务器的开启或关闭状态而不删除它。禁用的服务器保留在配置中，以便稍后重新启用。在下一次消息网关重启时生效。
- **测试** — 连接到服务器，列出其工具，然后断开连接 — 在 Agent 依赖它之前验证连接
- **移除** — 从配置中删除服务器
- 类似密钥的环境变量值在列表视图中会被脱敏

**目录：** 浏览 Nous 批准的 MCP 服务器（捆绑的 `optional-mcps/` 目录）并一键安装其中任何一个。需要 API 密钥的条目会内联提示输入；值会存入 `.env`。这与 `hermes mcp catalog` / `hermes mcp install` 使用的目录相同。
![MCP 管理页面 — 您的服务器及启用/禁用开关，以及安装目录](/img/dashboard/admin-mcp.png)

### Webhooks

管理动态的 [webhook 订阅](/user-guide/messaging/webhooks)。必须先在消息设置中启用 webhook 平台；如果未启用，页面会显示提示。

- **创建** — 名称、描述、事件过滤器、投递目标、可选的直接投递模式，以及一个 Agent 提示词。创建时，页面会显示路由 URL 和一次性 HMAC 密钥以供复制。
- **启用 / 禁用** — 切换订阅的开关状态。禁用的路由会保留在订阅文件中，但消息网关会拒绝其传入的事件（403）。网关会热重载该文件，因此更改会在下一个事件时生效 — 无需重启。
- **列表** — 每个订阅显示其 URL、事件和投递目标
- **删除** — 移除订阅

![Webhooks 管理页面 — 带有启用/禁用开关的订阅](/img/dashboard/admin-webhooks.png)

### 配对

无需 CLI 即可批准和撤销消息用户 — 远程管理员如何将 Telegram/Discord 等用户加入已配对的消息网关。与 `hermes pairing` 完全一致。

- **待处理请求** — 每个请求显示平台、代码、用户和时长，并带有批准按钮
- **已批准用户** — 每个用户显示平台和用户，并带有撤销按钮
- **清空待处理** — 删除所有未处理的配对代码

![配对管理页面](/img/dashboard/admin-pairing.png)

### 系统

一个整合的管理面板，用于执行安装范围内的操作：

- **主机** — 实时系统状态：操作系统 / 内核、架构、主机名、Python 和 Hermes 版本、CPU 核心数 + 使用率、内存、Hermes 主目录的磁盘使用情况、运行时间以及平均负载。（如果安装了 `psutil`，CPU/内存/磁盘信息来自它；身份字段始终显示。）
- **Nous Portal** — 登录状态、活动的推理提供商，以及工具网关路由表（哪些工具通过 Portal 运行 vs. 本地运行），并附有管理订阅的链接。`hermes portal` 的只读镜像。
- **技能策展器** — 后台技能维护状态（活动 / 暂停、间隔、上次运行），带有暂停/恢复和立即运行按钮。`hermes curator` 的镜像。
- **消息网关** — 启动、停止和重启消息网关，并显示实时状态（运行/停止、PID、状态）
- **记忆** — 选择外部记忆提供商（或仅使用内置的），并重置内置的 `MEMORY.md` / `USER.md` 存储
- **凭证池** — 添加和移除 Agent 轮询使用的轮换 API 密钥（按提供商）。列表中的密钥会被脱敏；原始值仅会到达 Agent。
- **操作** — 运行 `doctor`、安全审计、创建备份、从备份存档恢复、更新技能、显示系统提示词大小细分、生成支持转储，或为已弃用的设置迁移配置。每个操作都会生成一个后台任务，其实时日志会流式传输到页面。
- **检查点** — 查看 `/rollback` 影子存储大小并进行清理
- **Shell 钩子** — 列出已配置的钩子及其同意状态 + 可执行状态，**创建**一个钩子（事件、命令、匹配器、超时，带有选择加入的同意授权），以及移除一个钩子。钩子运行任意命令，因此创建表单带有安全警告，并且只有在同意授予后钩子才会触发。

![系统管理页面 — 主机状态和 Nous Portal 状态](/img/dashboard/admin-system-top.png)

![系统管理页面 — 技能策展器、消息网关、记忆和凭证池](/img/dashboard/admin-system-curator.png)

![系统管理页面 — 操作、检查点和 Shell 钩子](/img/dashboard/admin-system-ops.png)

创建 Shell 钩子（注意同意复选框和运行任意命令的警告）：

![新建 Shell 钩子模态框](/img/dashboard/admin-hook-create.png)

:::warning 安全
Web 仪表板会读取和写入您的 `.env` 文件，该文件包含 API 密钥和机密信息。默认情况下，它绑定到 `127.0.0.1` — 仅可从您的本地机器访问。如果您绑定到 `0.0.0.0`，您网络上的任何人都可以查看和修改您的凭据。仪表板本身没有身份验证功能。
:::

## `/reload` 斜杠命令

仪表板的 PR 还在交互式 CLI 中添加了一个 `/reload` 斜杠命令。通过 Web 仪表板（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 来获取更改而无需重启：

```
您 → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将把 `~/.hermes/.env` 重新读入运行进程的环境变量中。当您通过仪表板添加了新的提供商密钥并希望立即使用时，这非常有用。

## REST API

Web 仪表板公开了一个供前端使用的 REST API。您也可以直接调用这些端点以实现自动化：

### GET /api/status

返回 Agent 版本、消息网关状态、平台状态和活动会话数。

### GET /api/sessions

返回最近的 20 个会话及其元数据（模型、Token 计数、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式 — 类型、描述、类别，以及适用的选择选项。前端使用此信息为每个字段渲染正确的输入控件。

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

跨消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 及高亮片段。
### DELETE /api/sessions/{session_id}

删除一个会话及其消息历史。

### GET /api/logs

返回日志行。查询参数：`file` (agent/errors/gateway), `lines` (数量), `level`, `component`。

### GET /api/analytics/usage

返回 Token 使用量、成本和会话分析。查询参数：`days` (默认 30)。响应包括每日细分数据和按模型聚合的数据。

### GET /api/cron/jobs

返回所有已配置的定时任务及其状态、计划和运行历史。

### POST /api/cron/jobs

创建一个新的定时任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/{job_id}/pause

暂停一个定时任务。

### POST /api/cron/jobs/{job_id}/resume

恢复一个已暂停的定时任务。

### POST /api/cron/jobs/{job_id}/trigger

立即触发一个定时任务，不受其计划限制。

### DELETE /api/cron/jobs/{job_id}

删除一个定时任务。

### GET /api/skills

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表和激活/配置状态。

### 管理端点

这些端点支撑着 MCP、Webhooks、配对和系统页面。所有端点都与 `/api/` 下的其他端点位于相同的认证网关之后。

| 方法 & 路径 | 用途 |
|---------------|---------|
| `GET /api/mcp/servers` | 列出已配置的 MCP 服务器（环境值已脱敏） |
| `POST /api/mcp/servers` | 添加一个服务器。请求体：`{name, url?, command?, args?, env?, auth?}` |
| `POST /api/mcp/servers/{name}/test` | 连接、列出工具、断开连接 |
| `PUT /api/mcp/servers/{name}/enabled` | 启用 / 禁用一个服务器 |
| `DELETE /api/mcp/servers/{name}` | 移除一个服务器 |
| `GET /api/mcp/catalog` | 浏览 Nous 批准的 MCP 目录 |
| `POST /api/mcp/catalog/install` | 安装一个目录条目（需要环境变量） |
| `GET /api/pairing` | 列出待处理 + 已批准的消息用户 |
| `POST /api/pairing/approve` | 批准一个代码。请求体：`{platform, code}` |
| `POST /api/pairing/revoke` | 撤销一个用户。请求体：`{platform, user_id}` |
| `POST /api/pairing/clear-pending` | 删除所有待处理的代码 |
| `GET /api/webhooks` | 列出订阅 + 平台启用状态 |
| `POST /api/webhooks` | 创建一个订阅（返回一次性密钥） |
| `DELETE /api/webhooks/{name}` | 移除一个订阅 |
| `GET /api/credentials/pool` | 列出池化的轮换密钥（已脱敏） |
| `POST /api/credentials/pool` | 添加一个密钥。请求体：`{provider, api_key, label?}` |
| `DELETE /api/credentials/pool/{provider}/{index}` | 移除一个密钥（基于 1 的索引） |
| `GET /api/memory` | 活跃提供商 + 可用提供商 + 内置文件大小 |
| `PUT /api/memory/provider` | 选择一个提供商（空 = 仅内置） |
| `POST /api/memory/reset` | 重置内置记忆。请求体：`{target: all\|memory\|user}` |
| `POST /api/gateway/start` · `/stop` · `/restart` | 消息网关生命周期（后台运行） |
| `POST /api/ops/doctor` · `/security-audit` · `/backup` · `/import` | 诊断与维护（后台运行；通过 `/api/actions/{name}/status` 跟踪） |
| `GET /api/ops/hooks` | 已配置的 shell 钩子 + 允许列表状态 |
| `GET /api/ops/checkpoints` · `POST .../prune` | 检查 / 清理 `/rollback` 存储 |
| `POST /api/ops/hooks` · `DELETE /api/ops/hooks` | 创建 / 移除一个 shell 钩子（需同意） |
| `GET /api/system/stats` | 主机统计信息 — 操作系统、CPU、内存、磁盘、运行时间 |
| `GET /api/curator` · `PUT .../paused` · `POST .../run` | 技能策展器状态 + 暂停/恢复 + 运行 |
| `GET /api/portal` | Nous Portal 认证 + 工具网关路由（只读） |
| `POST /api/ops/prompt-size` · `/dump` · `/config-migrate` | 诊断（后台运行） |
| `PUT /api/webhooks/{name}/enabled` | 启用 / 禁用一个 webhook 路由 |
| `POST /api/skills/hub/install` · `/uninstall` · `/update` | 技能中心操作（后台运行） |
| `GET /api/skills/hub/search` | 在所有源中搜索技能中心 |
| `GET /api/sessions/stats` | 会话存储统计信息 |
| `PATCH /api/sessions/{id}` | 重命名 / 归档一个会话 |
| `GET /api/sessions/{id}/export` | 将会话（元数据 + 消息）导出为 JSON |
| `POST /api/sessions/prune` | 删除早于 N 天的已结束会话 |
| `PUT /api/cron/jobs/{id}` | 编辑定时任务的提示词 / 计划 / 名称 / 交付方式 |

## OAuth 认证（门控模式）

当仪表板绑定到公共地址时 — 即除 `127.0.0.1` / `localhost` 之外的任何地址 — Hermes Agent 会启用基于 OAuth 的认证门控。每个请求都必须携带一个已验证的会话 Cookie，否则将通过 Nous Portal 进行完整的 OAuth 往返流程。

这适用于可通过公共互联网访问仪表板的托管部署（通常是 Fly.io）。绑定到环回地址的操作员自有仪表板不受影响。

### 门控何时启用

| 标志 | 认证门控 | 使用场景 |
|-------|-----------|----------|
| `hermes dashboard` (默认 — 绑定到 `127.0.0.1`) | 关闭 | 本地开发 |
| `hermes dashboard --host 0.0.0.0` | **开启** | 生产 / Fly.io 部署 |
| `hermes dashboard --host 192.168.1.10 --insecure` | 关闭 | 受信任的局域网；用户选择使用传统的会话令牌认证 |

当且仅当满足以下条件时，门控开启：

1. 绑定主机不是 `127.0.0.1`、`::1`、`localhost` 或 `0.0.0.0` **并且**
2. **未**设置 `--insecure` 标志。

设置 `--insecure` 会保持现有的单进程会话令牌行为 — 无需 OAuth 流程，无需提供商插件。仅在信任每个客户端的网络上使用。

### 故障关闭语义

如果门控本应启用但**没有**注册任何 `DashboardAuthProvider`（没有 Nous 插件，没有自定义插件），`hermes dashboard` 将拒绝绑定并显示明确的错误消息。没有“默认拒绝但接受一切”的回退方案 — 配置错误的门控仪表板永远不会启动。

### 默认提供商：Nous Research

捆绑的 `plugins/dashboard_auth/nous` 插件**始终安装**并自动加载。当配置了客户端 ID 时，它会自动注册一个名为 `nous` 的 `DashboardAuthProvider`。
#### 配置

该插件从两个层面读取配置，当环境变量设置为非空值时，环境变量优先：

**`config.yaml`** — 规范配置层面：

```yaml
dashboard:
  oauth:
    client_id: agent:01HXYZ…             # 启用认证网关所必需
    portal_url: https://portal.nousresearch.com  # 可选；默认为生产环境
```

**环境变量** — 操作员覆盖：

| 环境变量 | 覆盖项 | 格式 | 提供方 |
|---------|-----------|--------|----------------|
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | `dashboard.oauth.client_id` | `agent:{instance_id}` | Nous Portal 在 Fly.io 部署时提供 |
| `HERMES_DASHBOARD_PORTAL_URL` | `dashboard.oauth.portal_url` | URL (默认: `https://portal.nousresearch.com`) | Portal — 仅在暂存环境或自定义部署时覆盖 |

根据 Hermes Agent 的约定（`~/.hermes/.env` 仅用于 API 密钥/密钥），**`config.yaml` 是推荐设置这些值的地方**，适用于本地开发、本地部署以及任何你直接控制的部署。环境变量路径的存在是为了让 Fly.io 的平台密钥注入可以在无需任何人编辑镜像内 `config.yaml` 的情况下推送每次部署的 `client_id` — 这是其主要目的。

空的环境变量值被视为未设置，因此一个已配置但未填充的 Fly 密钥不会意外地覆盖有效的 `config.yaml` 条目。

如果两个来源都未提供 client_id，插件会报告具体原因，并且仪表板的故障关闭绑定错误会明确告知你需要修复什么：

```
拒绝将仪表板绑定到 0.0.0.0 — OAuth 认证网关在非回环绑定时启用，但未注册任何认证提供商。

捆绑的提供商报告了以下问题：
  • nous: 未设置 HERMES_DASHBOARD_OAUTH_CLIENT_ID（并且
    config.yaml 中的 dashboard.oauth.client_id 为空）。Nous Portal
    在部署 Hermes Agent 实例时会提供此环境变量（格式为 'agent:{instance_id}'）—
    请将其设置为你已配置的客户端 ID（作为环境变量或在 config.yaml 中的
    dashboard.oauth.client_id 下），或者传递 --insecure 以完全跳过 OAuth 网关。

或者传递 --insecure 以跳过认证网关（在不信任的网络中不推荐）。
```

### 公共 URL 覆盖

默认情况下，仪表板从请求中重构 OAuth 回调 URL — `X-Forwarded-Host` + `X-Forwarded-Proto` + `X-Forwarded-Prefix`（当 uvicorn 配置了 `proxy_headers=True` 时，`start_server` 在网关下会启用此配置）。这在 Fly.io 上开箱即用，因为 Fly.io 正确设置了所有三个头部。

对于部署在不能可靠转发这些头部的反向代理之后的情况（手动 nginx 设置、本地入口、带有部分代理链的自定义域名 Fly 部署），请将 `dashboard.public_url`（或 `HERMES_DASHBOARD_PUBLIC_URL`）设置为访问仪表板的**完整公共 URL**：

```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
```

设置后，OAuth 回调 URL 将直接变为 `<public_url>/auth/callback` — 在该代码路径上会忽略 `X-Forwarded-Prefix`，因为操作员已明确声明了公共 URL。这是有意为之：在常见情况下，前缀已经包含在 `public_url` 中，叠加前缀会导致重复。

优先级与其他仪表板设置相同 — 环境变量优先于 `config.yaml`：

| 配置层面 | 覆盖路径 | 何时使用 |
|---------|---------------|-------------|
| `config.yaml` 中的 `dashboard.public_url` | `HERMES_DASHBOARD_PUBLIC_URL` | 本地开发 / 本地部署（规范） |
| `HERMES_DASHBOARD_PUBLIC_URL` 环境变量 | — | Fly.io 平台密钥 / CI |
| （未设置） | — | 默认 — 从 `X-Forwarded-*` 头部重构 |

验证会拒绝没有 `http://` / `https://` 协议、没有主机名或包含引号/尖括号/空白字符/控制字符的值。格式错误的值会静默回退到头部重构，以便登录流程继续工作，而不是将用户重定向到恶意 URL。

> **注意：** `public_url` 仅覆盖 OAuth 回调 URL。`Secure` cookie 标志仍由 `request.url.scheme` 控制（在 `proxy_headers=True` 下，会遵循来自 Fly TLS 终结器的 `X-Forwarded-Proto`），因此在 TLS 终结的公共部署上使用 `http://` 的 `public_url` 将产生非 Secure cookie。这是操作员的一个隐患 — 请将 `public_url` 与上游正确的 TLS 终结配对使用。

### OAuth 流程

该提供商实现了 [Nous Portal OAuth 合约 v1](https://github.com/NousResearch/nous-account-service/blob/main/docs/agent-dashboard-oauth-contract.md) — 带有 PKCE (S256) 的授权码授权：

1. 用户在没有会话 cookie 的情况下访问 `/` → 网关重定向到 `/login`。
2. 登录页面显示“使用 Nous Research 继续”按钮 → `/auth/login?provider=nous`。
3. 服务器将 PKCE 状态存储在短期 cookie 中，将用户重定向到 `https://portal.nousresearch.com/oauth/authorize?…`。
4. 用户通过 Portal 认证，到达 `/auth/callback?code=…&state=…`。
5. 服务器在 `POST /api/oauth/token` 处将 code 交换为访问令牌，根据 Portal 的 JWKS (`/.well-known/jwks.json`) 验证 JWT 签名，并设置 `hermes_session_at` cookie。
6. 用户被重定向到 `/`（或通过 `next=` 查询参数重定向到原始的深度链接路径）。

访问令牌的 TTL 为 15 分钟。**合约 v1 中没有刷新令牌** — 当令牌过期时，SPA 的 fetch 包装器会检测到 401 响应信封，并全页面导航回 `/login` 以重新运行流程。

### 设置的 Cookie

| 名称 | 生命周期 | 备注 |
|------|----------|-------|
| `hermes_session_at` | 令牌 TTL (15 分钟) | HttpOnly, SameSite=Lax, 在 HTTPS 时启用 Secure |
| `hermes_session_pkce` | 10 分钟 | HttpOnly；在往返期间保存 PKCE 验证器和提供商提示 |
| `hermes_session_rt` | v1 中未使用 | 为向前兼容保留；当 `refresh_token` 为空时不写入 |

所有三个 cookie 都设置为 `Path=/` 和 `SameSite=Lax`。当通过 HTTPS 访问仪表板时（通过请求 URL 方案检测 — 在 `proxy_headers=True` 下，会遵循来自 Fly TLS 终结器的 `X-Forwarded-Proto`），会设置 `Secure` 标志。
### 登出

侧边栏小部件显示 `Logged in as <user_id…> via nous` 并带有一个登出图标。点击它会向 `/auth/logout` 发送 POST 请求，这将清除所有 dashboard-auth 相关的 cookie 并重定向回 `/login`。

### 审计日志

每次登录开始、成功、失败以及会话验证失败都会以 JSON 行格式写入 `$HERMES_HOME/logs/dashboard-auth.log`。敏感字段（`access_token`、`refresh_token`、`code`、`code_verifier`、`state`、`Authorization` 请求头）在记录前会被脱敏。

### 自定义提供商

要接入非 Nous 的 OAuth 提供商（例如 Google、GitHub、自定义 OIDC），请创建一个注册 `DashboardAuthProvider` 的插件：

```python
# ~/.hermes/plugins/dashboard-auth-myidp/__init__.py
from hermes_cli.dashboard_auth import DashboardAuthProvider, Session, LoginStart

class MyIdPProvider(DashboardAuthProvider):
    name = "myidp"
    display_name = "My Identity Provider"

    def start_login(self, *, redirect_uri): ...
    def complete_login(self, *, code, state, code_verifier, redirect_uri): ...
    def verify_session(self, *, access_token): ...
    def refresh_session(self, *, refresh_token): ...
    def revoke_session(self, *, refresh_token): ...

def register(ctx):
    ctx.register_dashboard_auth_provider(MyIdPProvider())
```

登录页面会列出所有已注册的提供商；可以叠加多个提供商，用户在 `/login` 页面选择其中一个。

### 验证网关已启用

```bash
# 快速环境变量路径（Fly.io 形态）。HERMES_DASHBOARD_PORTAL_URL 是
# 可选的 —— 默认为生产环境。
HERMES_DASHBOARD_OAUTH_CLIENT_ID=agent:test \
  hermes dashboard --host 0.0.0.0

# 或者通过 config.yaml 的等效配置（推荐用于本地开发/本地部署）：
#
#   dashboard:
#     oauth:
#       client_id: agent:test
#
# 然后直接运行：
hermes dashboard --host 0.0.0.0

# 访问 /api/status 查看网关状态：
curl -s http://127.0.0.1:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

仪表板的 React StatusPage 在 "Web server" 下显示相同的字段。登录后，侧边栏的 AuthWidget 会显示当前身份。

## CORS

Web 服务器将 CORS 限制为仅限 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119` (生产环境)
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173` (Vite 开发服务器)

如果在自定义端口上运行服务器，该来源会自动添加。

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

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/`，由 FastAPI 服务器作为静态 SPA 提供服务。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这使仪表板与代码更新保持同步。如果未安装 `npm`，更新将跳过前端构建，`hermes dashboard` 会在首次启动时构建它。

## 主题与插件

仪表板内置了六个主题，并可以通过用户定义的主题、插件标签页和后端 API 路由进行扩展 —— 所有这些都可以直接放入，无需克隆仓库。

**实时切换主题** —— 从标题栏，点击语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 中的 `dashboard.theme` 下，并在页面加载时恢复。

内置主题：

| 主题 | 特点 |
|-------|-----------|
| **Hermes Teal** (`default`) | 深青色 + 奶油色，系统字体，舒适的间距 |
| **Hermes Teal (Large)** (`default-large`) | 与默认主题相同，但使用 18px 文本和更宽松的间距 |
| **Midnight** (`midnight`) | 深蓝紫色，Inter + JetBrains Mono 字体 |
| **Ember** (`ember`) | 暖色调深红 + 青铜色，Spectral 衬线字体 + IBM Plex Mono 字体 |
| **Mono** (`mono`) | 灰度，IBM Plex 字体，紧凑 |
| **Cyberpunk** (`cyberpunk`) | 黑色背景上的霓虹绿，Share Tech Mono 字体 |
| **Rosé** (`rose`) | 粉色 + 象牙色，Fraunces 衬线字体，宽敞 |

要构建自己的主题、添加插件标签页、注入到 shell 插槽或暴露插件特定的 REST 端点，请参阅 **[扩展仪表板](./extending-the-dashboard)** —— 完整指南涵盖：

- 主题 YAML 模式 —— 调色板、排版、布局、资源、componentStyles、colorOverrides、customCSS
- 布局变体 —— `standard`、`cockpit`、`tiled`
- 插件清单、SDK、shell 插槽、页面作用域插槽（将小部件注入到内置页面中而无需覆盖它们）、后端 FastAPI 路由
- 一个完整的主题加插件组合演练（强袭自由驾驶舱演示）
- 发现、重新加载和故障排除