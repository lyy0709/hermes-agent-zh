---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的仪表盘，用于管理配置、API 密钥、会话、日志、分析、定时任务和技能"
---

# Web 仪表盘

Web 仪表盘是一个基于浏览器的用户界面，用于管理您的 Hermes Agent 安装。您可以通过简洁的 Web 界面配置设置、管理 API 密钥和监控会话，而无需编辑 YAML 文件或运行 CLI 命令。

:::tip
托管模式的身份验证使用 Nous Portal OAuth；如果您还希望仪表盘与真实的后端通信，`hermes setup --portal` 也会连接模型和工具消息网关。请参阅 [Nous Portal](/integrations/nous-portal)。
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
| `--tui` | 关闭 | 启用浏览器内的聊天标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`）。或者设置 `HERMES_DASHBOARD_TUI=1`。 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有网络接口（在共享网络上使用需谨慎）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open

# 启用浏览器内的聊天标签页
hermes dashboard --tui
```

## 前提条件

默认的 `hermes-agent` 安装包不包含 HTTP 栈或 PTY 辅助程序 —— 这些是可选的额外组件。**Web 仪表盘** 需要 FastAPI 和 Uvicorn (`web` 额外组件)。**聊天** 标签页还需要 `ptyprocess` 来在伪终端后生成嵌入的 TUI（在 POSIX 系统上是 `pty` 额外组件）。使用以下命令安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 额外组件会引入 FastAPI/Uvicorn；`pty` 会引入 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows —— 请注意，嵌入的 TUI 本身仍然需要 WSL）。`pip install hermes-agent[all]` 包含这两个额外组件，如果您还想要消息/语音等功能，这是最简单的方法。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

聊天标签页在普通的 `hermes dashboard` 启动时是默认关闭的。当您需要嵌入的浏览器聊天窗格时，请使用 `hermes dashboard --tui` 启动仪表盘，或者设置 `HERMES_DASHBOARD_TUI=1`。

## 页面

### 状态

落地页显示您安装的实时概览：

- **Agent 版本** 和发布日期
- **消息网关状态** —— 运行/停止、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### 聊天

**聊天** 标签页将完整的 Hermes TUI（与您从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。您在终端 TUI 中可以做的所有事情 —— 斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、澄清/sudo/批准提示、皮肤主题 —— 在这里都完全相同，因为仪表盘正在运行真正的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，以实现像素完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个使用仪表盘会话 Token 进行身份验证的 WebSocket
- 服务器在 POSIX 伪终端后生成 `hermes --tui`
- 按键传输到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格；鼠标跟踪（SGR 1006）、宽字符（Unicode 11）和方框绘制字形都原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 大小

**恢复现有会话：** 在 **会话** 标签页中，点击任意会话旁边的播放图标 (▶)。这将跳转到 `/chat?resume=<id>` 并使用 `--resume` 启动 TUI，加载完整的历史记录。

**前提条件：**

- Node.js（与 `hermes --tui` 的要求相同；TUI 包在首次启动时构建）
- `ptyprocess` —— 由 `pty` 额外组件安装（`pip install 'hermes-agent[web,pty]'`，或者 `[all]` 包含两者）
- POSIX 内核（Linux、macOS 或 WSL2）。`/chat` 终端窗格特别需要 POSIX PTY —— 原生 Windows Python 没有等效功能，因此在原生 Windows 安装上，仪表盘的其余部分（会话、任务、指标、配置编辑器）可以工作，但 `/chat` 标签页会显示一个横幅，告诉您对该功能使用 WSL2。

关闭浏览器标签页，服务器上的 PTY 会被干净地回收。重新打开会生成一个新的会话。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都是从 `DEFAULT_CONFIG` 自动发现的，并组织到分类标签页中：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（本地/docker/ssh/modal）、超时、Shell 偏好设置
- **display** —— 皮肤、工具进度、恢复显示、微调器设置
- **agent** —— 最大迭代次数、消息网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理工作量
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（询问/yolo/拒绝）
- 以及更多 —— config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉菜单。布尔值呈现为切换开关。其他所有内容都是文本输入框。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（在您点击保存之前不会保存）
- **导出** —— 将当前配置下载为 JSON 文件
- **导入** —— 上传 JSON 配置文件以替换当前值
:::tip
配置更改将在下一次 Agent 会话或消息网关重启时生效。Web 仪表板编辑的是与 `hermes config set` 和消息网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等。
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等。
- **消息平台** — Telegram、Discord、Slack 机器人令牌等。
- **Agent 设置** — 非机密环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（附带值的脱敏预览）
- 用途描述
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 用于删除它的按钮

高级/不常用的密钥默认隐藏在切换开关后面。

### 会话

浏览和检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、定时任务）、模型名称、消息数量、工具调用次数以及上次活动时间。活动会话带有脉动徽章标记。

- **搜索** — 使用 FTS5 在所有消息内容中进行全文搜索。结果显示高亮片段，展开时会自动滚动到第一条匹配的消息。
- **展开** — 点击会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并以 Markdown 格式渲染，支持语法高亮。
- **工具调用** — 包含工具调用的助手消息显示可折叠块，其中包含函数名称和 JSON 参数。
- **删除** — 使用垃圾桶图标删除会话及其消息历史记录。

### 日志

查看 Agent、消息网关和错误日志文件，支持过滤和实时跟踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：all、gateway、agent、tools、cli 或 cron
- **行数** — 选择显示多少行（50、100、200 或 500）
- **自动刷新** — 切换实时跟踪，每 5 秒轮询新的日志行
- **颜色编码** — 日志行按严重程度着色（错误为红色，警告为黄色，调试信息为灰色）

### 分析

根据会话历史记录计算的用量和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** — 总 Token 数（输入/输出）、缓存命中率、总估计或实际成本，以及总会话数和日均值
- **每日 Token 图表** — 堆叠条形图，显示每天的输入和输出 Token 使用量，悬停提示显示细分和成本
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
- **切换** — 使用开关启用或禁用单个技能。更改将在下一次会话时生效。
- **工具集** — 单独的部分显示内置工具集（文件操作、网页浏览等），包括其活动/非活动状态、设置要求和包含的工具列表

:::warning 安全
Web 仪表板会读取和写入您的 `.env` 文件，该文件包含 API 密钥和机密信息。它默认绑定到 `127.0.0.1` — 仅可从您的本地机器访问。如果您绑定到 `0.0.0.0`，您网络上的任何人都可以查看和修改您的凭据。仪表板本身没有身份验证机制。
:::

## `/reload` 斜杠命令

仪表板 PR 还在交互式 CLI 中添加了一个 `/reload` 斜杠命令。通过 Web 仪表板（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 即可获取更改而无需重启：

```
You → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将重新读取 `~/.hermes/.env` 到运行进程的环境中。当您通过仪表板添加了新的提供商密钥并希望立即使用时，这非常有用。

## REST API

Web 仪表板公开了一个供前端使用的 REST API。您也可以直接调用这些端点以实现自动化：

### GET /api/status

返回 Agent 版本、消息网关状态、平台状态和活动会话数。

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

返回会话的完整消息历史，包括工具调用和时间戳。

### GET /api/sessions/search

跨消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 及高亮片段。

### DELETE /api/sessions/\{session_id\}

删除会话及其消息历史。

### GET /api/logs

返回日志行。查询参数：`file` (agent/errors/gateway), `lines` (数量), `level`, `component`。

### GET /api/analytics/usage

返回 Token 使用量、成本和会话分析。查询参数：`days` (默认 30)。响应包含每日细分数据和按模型聚合的数据。

### GET /api/cron/jobs

返回所有已配置的定时任务及其状态、计划和运行历史。

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

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表和激活/配置状态。

## OAuth 身份验证（门控模式）

当仪表板绑定到公共地址（即除 `127.0.0.1` / `localhost` 之外的任何地址）时，Hermes Agent 会启用基于 OAuth 的身份验证门控。每个请求都必须携带一个经过验证的会话 Cookie，否则将通过 Nous Portal 进行完整的 OAuth 往返流程。

这适用于可通过公共互联网访问的托管部署（通常是 Fly.io）。绑定到环回地址的、由操作员拥有的仪表板不受影响。

### 门控何时启用

| 标志 | 身份验证门控 | 用例 |
|-------|-----------|----------|
| `hermes dashboard` (默认 — 绑定到 `127.0.0.1`) | 关闭 | 本地开发 |
| `hermes dashboard --host 0.0.0.0` | **开启** | 生产环境 / Fly.io 部署 |
| `hermes dashboard --host 192.168.1.10 --insecure` | 关闭 | 受信任的局域网；用户选择使用传统的会话令牌身份验证 |

当且仅当满足以下条件时，门控开启：

1. 绑定主机不是 `127.0.0.1`、`::1`、`localhost` 或 `0.0.0.0` **并且**
2. **未**设置 `--insecure` 标志。

设置 `--insecure` 会保持现有的单进程会话令牌行为 — 无需 OAuth 流程，也无需提供商插件。仅在信任所有客户端的网络中使用。

### 故障关闭语义

如果门控本应启用但**没有**注册 `DashboardAuthProvider`（没有 Nous 插件，没有自定义插件），`hermes dashboard` 会拒绝绑定并显示明确的错误消息。不存在“默认拒绝但接受一切”的回退机制 — 配置错误的门控仪表板永远不会启动。

### 默认提供商：Nous Research

捆绑的 `plugins/dashboard_auth/nous` 插件**始终安装**并自动加载。当配置了客户端 ID 时，它会自动注册一个名为 `nous` 的 `DashboardAuthProvider`。

#### 配置

该插件从两个层面读取配置，当环境变量设置为非空时，环境变量优先：

**`config.yaml`** — 规范层面：

```yaml
dashboard:
  oauth:
    client_id: agent:01HXYZ…             # 启用门控所必需
    portal_url: https://portal.nousresearch.com  # 可选；默认为生产环境
```

**环境变量** — 操作员覆盖：

| 环境变量 | 覆盖项 | 格式 | 由谁提供 |
|---------|-----------|--------|----------------|
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | `dashboard.oauth.client_id` | `agent:{instance_id}` | Nous Portal 在 Fly.io 配置时提供 |
| `HERMES_DASHBOARD_PORTAL_URL` | `dashboard.oauth.portal_url` | URL (默认: `https://portal.nousresearch.com`) | Portal — 仅用于覆盖暂存环境或自定义部署 |

根据 Hermes Agent 的约定（`~/.hermes/.env` 仅用于 API 密钥/机密），**`config.yaml` 是推荐设置这些值的地方**，适用于本地开发、本地部署以及任何您直接控制的部署。环境变量路径的存在是为了让 Fly.io 的平台密钥注入可以在不编辑镜像内 `config.yaml` 的情况下推送每个部署的 `client_id` — 这是其主要目的。

空的环境变量值被视为未设置，因此已配置但未填充的 Fly 密钥不会意外地覆盖有效的 `config.yaml` 条目。

如果两个来源都未提供 client_id，插件会报告具体原因，并且仪表板的故障关闭绑定错误会明确告知您需要修复什么：

```
拒绝将仪表板绑定到 0.0.0.0 — 在非环回地址绑定时会启用 OAuth 身份验证门控，但未注册任何身份验证提供商。

捆绑的提供商报告了以下问题：
  • nous: 未设置 HERMES_DASHBOARD_OAUTH_CLIENT_ID（并且 config.yaml 中的 dashboard.oauth.client_id 为空）。Nous Portal 在部署 Hermes Agent 实例时会提供此环境变量（格式为 'agent:{instance_id}'）— 请将其设置为您的已配置客户端 ID（作为环境变量或在 config.yaml 中的 dashboard.oauth.client_id 下设置），或者传递 --insecure 以完全跳过 OAuth 门控。

或者传递 --insecure 以跳过身份验证门控（不推荐在不受信任的网络上使用）。
```

### 公共 URL 覆盖

默认情况下，仪表板从请求中重建 OAuth 回调 URL — `X-Forwarded-Host` + `X-Forwarded-Proto` + `X-Forwarded-Prefix`（当 uvicorn 配置了 `proxy_headers=True` 时，`start_server` 在门控下会启用此配置）。这在 Fly.io 上开箱即用，因为 Fly.io 正确设置了所有三个标头。

对于位于反向代理后面且不能可靠转发这些标头的部署（手动 nginx 设置、本地入口、具有部分代理链的自定义域 Fly 部署），请将 `dashboard.public_url`（或 `HERMES_DASHBOARD_PUBLIC_URL`）设置为仪表板访问的**完整公共 URL**：
```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
```

设置后，OAuth 回调 URL 将完全按照 `<public_url>/auth/callback` 使用——在该代码路径上会忽略 `X-Forwarded-Prefix`，因为操作员已明确声明了公共 URL。这是有意为之：在常见情况下，前缀已经包含在 `public_url` 中，再叠加前缀会导致双重前缀。

优先级与其他仪表板设置相同——环境变量优先于 `config.yaml`：

| 配置方式 | 覆盖路径 | 使用场景 |
|---------|---------------|-------------|
| `config.yaml` 中的 `dashboard.public_url` | `HERMES_DASHBOARD_PUBLIC_URL` | 本地开发 / 本地部署（规范方式） |
| `HERMES_DASHBOARD_PUBLIC_URL` 环境变量 | — | Fly.io 平台密钥 / CI |
| （未设置） | — | 默认值——根据 `X-Forwarded-*` 头部重构 |

验证会拒绝不含 `http://` / `https://` 协议、不含主机名或包含引号/尖括号/空白字符/控制字符的值。格式错误的值会静默回退到头部重构，以便登录流程继续工作，而不是将用户重定向到恶意 URL。

> **注意：** `public_url` 仅覆盖 OAuth 回调 URL。`Secure` cookie 标志仍由 `request.url.scheme` 控制（在 `proxy_headers` 下遵循 `X-Forwarded-Proto`），因此在 TLS 终止的公共部署上使用 `http://` 的 `public_url` 将产生非 Secure cookie。这是操作员容易犯错的地方——请将 `public_url` 与上游正确的 TLS 终止配对使用。

### OAuth 流程

提供商实现了 [Nous Portal OAuth 合约 v1](https://github.com/NousResearch/nous-account-service/blob/main/docs/agent-dashboard-oauth-contract.md)——使用 PKCE (S256) 的授权码授权：

1. 用户访问 `/` 但没有会话 cookie → 网关重定向到 `/login`。
2. 登录页面显示“使用 Nous Research 继续”按钮 → `/auth/login?provider=nous`。
3. 服务器将 PKCE 状态存储在短期 cookie 中，将用户重定向到 `https://portal.nousresearch.com/oauth/authorize?…`。
4. 用户在 Portal 完成身份验证，跳转到 `/auth/callback?code=…&state=…`。
5. 服务器在 `POST /api/oauth/token` 处用 code 交换访问令牌，根据 Portal 的 JWKS (`/.well-known/jwks.json`) 验证 JWT 签名，并设置 `hermes_session_at` cookie。
6. 用户被重定向到 `/`（或通过 `next=` 查询参数重定向到原始深度链接路径）。

访问令牌的 TTL 为 15 分钟。**合约 v1 中没有刷新令牌**——当令牌过期时，SPA 的 fetch 包装器会检测到 401 响应信封，并全页面导航回 `/login` 以重新运行流程。

### 设置的 Cookie

| 名称 | 生命周期 | 说明 |
|------|----------|-------|
| `hermes_session_at` | 令牌 TTL (15 分钟) | HttpOnly, SameSite=Lax, 使用 HTTPS 时 Secure |
| `hermes_session_pkce` | 10 分钟 | HttpOnly；在往返过程中保存 PKCE 验证器和提供商提示 |
| `hermes_session_rt` | v1 中未使用 | 为向前兼容保留；当 `refresh_token` 为空时不写入 |

所有三个 cookie 都设置为 `Path=/` 和 `SameSite=Lax`。当通过 HTTPS 访问仪表板时（通过请求 URL 方案检测——在 `proxy_headers=True` 下遵循来自 Fly TLS 终结器的 `X-Forwarded-Proto`），会设置 `Secure` 标志。

### 登出

侧边栏小部件显示 `Logged in as <user_id…> via nous` 并带有一个登出图标。点击它会 POST 到 `/auth/logout`，这将清除所有仪表板认证 cookie 并重定向回 `/login`。

### 审计日志

每次登录开始、成功、失败和会话验证失败都会作为 JSON 行写入 `$HERMES_HOME/logs/dashboard-auth.log`。敏感字段（`access_token`、`refresh_token`、`code`、`code_verifier`、`state`、`Authorization` 头部）在记录前会被脱敏。

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

登录页面会列出所有已注册的提供商；可以堆叠多个提供商，用户在 `/login` 处选择一个。

### 验证网关已启用

```bash
# 快速环境变量路径（Fly.io 形式）。HERMES_DASHBOARD_PORTAL_URL 是
# 可选的——默认为生产环境。
HERMES_DASHBOARD_OAUTH_CLIENT_ID=agent:test \
  hermes dashboard --host 0.0.0.0

# 或通过 config.yaml 的等效方式（推荐用于本地开发 / 本地部署）：
#
#   dashboard:
#     oauth:
#       client_id: agent:test
#
# 然后只需：
hermes dashboard --host 0.0.0.0

# 访问 /api/status 查看网关状态：
curl -s http://127.0.0.1:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

仪表板的 React StatusPage 在“Web server”下显示相同的字段。登录后，侧边栏的 AuthWidget 会显示当前身份。

## CORS

Web 服务器将 CORS 限制为仅限 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）

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

位于 `http://localhost:5173` 的 Vite 开发服务器将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/`，由 FastAPI 服务器作为静态 SPA 提供。
## 更新时自动构建

运行 `hermes update` 时，如果系统已安装 `npm`，Web 前端会自动重新构建。这确保仪表盘与代码更新保持同步。如果未安装 `npm`，更新过程将跳过前端构建，`hermes dashboard` 会在首次启动时进行构建。

## 主题与插件

仪表盘内置了六个主题，并可通过用户定义的主题、插件标签页和后端 API 路由进行扩展——所有这些都是即插即用的，无需克隆仓库。

**实时切换主题**：从标题栏切换——点击语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 中的 `dashboard.theme` 配置项，并在页面加载时恢复。

内置主题：

| 主题 | 特点 |
|-------|-----------|
| **Hermes 青绿色** (`default`) | 深青绿色 + 奶油色，系统字体，舒适的间距 |
| **Hermes 青绿色 (大号)** (`default-large`) | 与默认主题相同，但使用 18px 文本和更宽松的间距 |
| **午夜** (`midnight`) | 深蓝紫色，Inter + JetBrains Mono 字体 |
| **余烬** (`ember`) | 暖深红色 + 青铜色，Spectral 衬线体 + IBM Plex Mono 字体 |
| **单色** (`mono`) | 灰度，IBM Plex 字体，紧凑 |
| **赛博朋克** (`cyberpunk`) | 黑色背景上的霓虹绿色，Share Tech Mono 字体 |
| **玫瑰** (`rose`) | 粉色 + 象牙色，Fraunces 衬线体，宽敞 |

要构建自己的主题、添加插件标签页、注入到 shell 插槽或暴露插件特定的 REST 端点，请参阅 **[扩展仪表盘](./extending-the-dashboard)** —— 完整指南涵盖：

- 主题 YAML 模式 —— 调色板、排版、布局、资源、componentStyles、colorOverrides、customCSS
- 布局变体 —— `standard`、`cockpit`、`tiled`
- 插件清单、SDK、shell 插槽、页面作用域插槽（将小部件注入到内置页面中，而无需覆盖它们）、后端 FastAPI 路由
- 一个完整的主题与插件结合演练（强袭自由驾驶舱演示）
- 发现、重新加载和故障排除