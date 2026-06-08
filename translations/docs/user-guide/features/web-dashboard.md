---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的管理面板，用于管理配置、API 密钥、MCP 服务器、消息配对、Webhook、消息网关、记忆、凭证、会话、日志、分析、定时任务和技能"
---

# Web 仪表盘

Web 仪表盘是一个基于浏览器的用户界面，用于管理您的 Hermes Agent 安装。您无需编辑 YAML 文件或运行 CLI 命令，即可通过简洁的 Web 界面配置设置、管理 API 密钥和监控会话。

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
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | 关闭 | 允许绑定到非本地主机地址 (**危险** —— 会在网络上暴露 API 密钥；请配合防火墙和强身份验证使用) |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有网络接口（在共享网络上使用需谨慎）
hermes dashboard --host 0.0.0.0

# 启动但不打开浏览器
hermes dashboard --no-open
```

## 前提条件

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 辅助程序 —— 这些是可选的额外组件。**Web 仪表盘** 需要 FastAPI 和 Uvicorn (`web` 额外组件)。**Chat** 标签页还需要 `ptyprocess` 来在伪终端后生成嵌入式 TUI (在 POSIX 系统上为 `pty` 额外组件)。使用以下命令安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 额外组件会引入 FastAPI/Uvicorn；`pty` 会引入 `ptyprocess` (POSIX) 或 `pywinpty` (原生 Windows —— 请注意嵌入式 TUI 本身仍需要 WSL)。`pip install hermes-agent[all]` 包含这两个额外组件，如果您还想要消息/语音等功能，这是最简单的途径。

当您在没有依赖项的情况下运行 `hermes dashboard` 时，它会告诉您需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

Chat 标签页是每次 `hermes dashboard` 启动的一部分 —— 嵌入式浏览器聊天窗格（通过 PTY/WebSocket 运行 TUI）始终可用，无需额外标志。

## 页面

### 状态

落地页显示您安装的实时概览：

- **Agent 版本** 和发布日期
- **消息网关状态** —— 运行/停止、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### 聊天

**Chat** 标签页将完整的 Hermes TUI（与您从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。您在终端 TUI 中可以做的所有事情 —— 斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、澄清/sudo/批准提示、皮肤主题 —— 在这里都完全相同，因为仪表盘正在运行真实的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，以实现像素完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个使用仪表盘会话 Token 进行身份验证的 WebSocket
- 服务器在 POSIX 伪终端后生成 `hermes --tui`
- 按键传输到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格；鼠标跟踪 (SGR 1006)、宽字符 (Unicode 11) 和方框绘制字形都原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 大小

**恢复现有会话：** 在 **Sessions** 标签页中，点击任意会话旁边的播放图标 (▶)。这将跳转到 `/chat?resume=<id>` 并使用 `--resume` 启动 TUI，加载完整的历史记录。

**前提条件：**

- Node.js（与 `hermes --tui` 的要求相同；TUI 包在首次启动时构建）
- `ptyprocess` —— 由 `pty` 额外组件安装 (`pip install 'hermes-agent[web,pty]'`，或 `[all]` 包含两者)
- POSIX 内核 (Linux、macOS 或 WSL2)。`/chat` 终端窗格特别需要 POSIX PTY —— 原生 Windows Python 没有等效功能，因此在原生 Windows 安装上，仪表盘的其他部分（会话、任务、指标、配置编辑器）可以工作，但 `/chat` 标签页将显示一个横幅，告诉您使用 WSL2 来获得该功能。

关闭浏览器标签页，服务器上的 PTY 会被干净地回收。重新打开会生成一个新的会话。

要将 [Hermes Desktop](#connecting-hermes-desktop-to-a-remote-backend) 指向运行在另一台机器上的仪表盘，而不是其自身捆绑的后端，请参阅下面的远程后端部分。

### 将 Hermes Desktop 连接到远程后端

Hermes Desktop 通常启动其自己的本地后端，但它也可以通过 **Settings → Gateway → Remote gateway** 连接到运行在远程机器（虚拟机、家庭实验室服务器等）上的仪表盘。这是“Desktop 显示后端已就绪但聊天从未工作”报告的最常见原因，因为 Desktop 的就绪检查验证的内容少于实时聊天连接实际需要的内容。

:::info 前提条件：远程主机上必须运行着一个 `hermes dashboard`
Desktop 连接的“远程后端”**就是**运行在远程机器上的 `hermes dashboard` 进程 —— 即本文档记录的同一个服务器。在以下任何步骤生效之前，它必须已启动并可访问；Desktop 是连接到它，而不是为您启动它。请确保它在 `systemd`/`tmux`/等 下持续运行，以便在注销和重启后仍然存活。**消息网关** (Telegram/Discord/Slack/等) 是一个*独立的*长时间运行进程 —— 如果您依赖消息渠道，请独立启动它；它不是桌面应用程序连接的对象。
:::
Desktop 的“远程后端就绪”探针仅访问 `GET /api/status`，这是一个公共端点——只要*任何*仪表板在主机上运行，它就会响应。实时聊天连接是一个**独立**的 WebSocket，连接到 `/api/ws`（以及 `/api/pty`），而该套接字还受另外两个状态探针从未触及的检查所限制：

1.  **必须经过身份验证。** 当仪表板绑定到非环回地址时，它会启用其身份验证门。使用用户名和密码（捆绑的[用户名/密码提供商](#usernamepassword-provider-no-oauth-idp)）来保护它；Desktop 登录一次，并通过一次性票据为 WebSocket 重用生成的会话。如果没有配置提供商，非环回仪表板**会在启动时失败关闭**。
2.  **绑定主机必须允许客户端连接，并且 Host 头必须匹配。** 环回绑定（`127.0.0.1`）仅接受环回客户端，因此无论凭据如何，远程机器都会在套接字层被拒绝。绑定到非环回地址（`--host 0.0.0.0`），以便对等 IP 守卫允许远程客户端通过。您在 Desktop 中输入的远程 URL 必须能够通过仪表板绑定的相同主机访问仪表板——DNS 重绑定守卫要求 Host 头匹配。

#### 远程仪表板设置

设置用户名和密码，然后运行绑定到可访问地址的仪表板。对于 `systemd` 服务：

```ini
[Service]
EnvironmentFile=%h/.hermes/.env
ExecStart=/path/to/venv/bin/python -m hermes_cli.main dashboard \
    --host 0.0.0.0 --port 9119 --no-open
```

其中 `~/.hermes/.env` 包含：

```bash
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<32+ random bytes; openssl rand -base64 32>
```

然后在 Desktop 中输入**远程 URL**（例如 `http://VM_IP:9119`）并使用该用户名和密码**登录**。完整配置界面请参阅[用户名/密码提供商](#usernamepassword-provider-no-oauth-idp)部分。

:::tip 在重试 Desktop 之前，请验证门已启用
从任何机器上，检查仪表板是否通告了用户名/密码提供商：

```bash
curl -s http://VM_IP:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

- `auth_required: true` 且 providers 列表中有 `"basic"` → Desktop 的**登录**流程将正常工作。
- `auth_required: false` → 绑定是环回的，或者门未启用。请绑定到非环回地址。
- `auth_required: true` 但没有 `"basic"` 提供商 → 用户名/密码环境变量未加载。请先修复这些问题。
:::

如果 `/api/status` 显示门已启用且带有 `"basic"` 提供商，但 Desktop 登录后*仍然*无法连接，则问题超出了基本设置范围——请获取新的 `desktop.log`（设置 → 消息网关 → 打开日志）以及同一重试窗口内的仪表板日志，并查找 `/api/ws` 的关闭代码（4403 = 聊天 WebSocket 被请求守卫拒绝，例如 Host/对等 IP 不匹配；4401 = WebSocket 票据未通过身份验证）。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都是从 `DEFAULT_CONFIG` 自动发现的，并按选项卡分类组织：

![配置管理页面——左侧是部分筛选器，右侧是自动发现的字段](/img/dashboard/admin-config.png)

- **model** — 默认模型、提供商、基础 URL、推理设置
- **terminal** — 后端（本地/docker/ssh/modal）、超时、Shell 偏好设置
- **display** — 皮肤、工具进度、恢复显示、旋转器设置
- **agent** — 最大迭代次数、消息网关超时、服务层级
- **delegation** — 子 Agent 限制、推理工作量
- **memory** — 提供商选择、上下文注入设置
- **approvals** — 危险命令批准模式（询问/勇往直前/拒绝）
- 以及更多 — config.yaml 的每个部分都有相应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉菜单。布尔值呈现为切换开关。其他所有内容都是文本输入。

**操作：**

- **保存** — 立即将更改写入 `config.yaml`
- **重置为默认值** — 将所有字段恢复为其默认值（点击保存前不会保存）
- **导出** — 将当前配置下载为 JSON
- **导入** — 上传 JSON 配置文件以替换当前值

:::tip
配置更改在下一次 Agent 会话或消息网关重启时生效。Web 仪表板编辑的是与 `hermes config set` 和消息网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等
- **消息平台** — Telegram、Discord、Slack 机器人令牌等
- **Agent 设置** — 非机密环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（带有值的脱敏预览）
- 用途描述
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 用于删除它的按钮

高级/不常用的密钥默认隐藏在切换开关后面。

### 会话

浏览和检查所有 Agent 会话。每行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、定时任务）、模型名称、消息数量、工具调用数量以及上次活动时间。活动会话标有脉动徽章。

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。结果显示高亮片段，展开时会自动滚动到第一条匹配的消息。
- **统计** — 摘要栏显示会话总数、存储中活动会话数、已归档数量、总消息数以及按来源的细分。
- **展开** — 点击会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并渲染为带有语法高亮的 Markdown。
- **工具调用** — 带有工具调用的助手消息显示可折叠块，其中包含函数名称和 JSON 参数。
- **重命名** — 内联设置或清除会话标题（铅笔图标）。
- **导出** — 将会话（元数据 + 完整消息历史记录）下载为 JSON（下载图标）。
- **清理** — 标题中的“清理旧会话”按钮会删除早于 N 天的已结束会话。
- **删除** — 使用垃圾桶图标删除会话及其消息历史记录。
![会话管理页面 — 统计栏、清理功能，以及每行的重命名/导出/删除操作](/img/dashboard/admin-sessions.png)

### 日志

查看 Agent、消息网关和错误日志文件，支持过滤和实时追踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：all、gateway、agent、tools、cli 或 cron
- **行数** — 选择显示多少行日志（50、100、200 或 500）
- **自动刷新** — 切换实时追踪，每 5 秒轮询一次新日志行
- **颜色编码** — 日志行按严重程度着色（红色表示错误，黄色表示警告，调试信息颜色较浅）

### 分析

根据会话历史计算的用量和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** — 总 Token 数（输入/输出）、缓存命中率、总估算或实际成本，以及总会话数和日均会话数
- **每日 Token 图表** — 堆叠条形图，显示每天的输入和输出 Token 使用量，悬停提示框显示细分数据和成本
- **每日细分表** — 日期、会话数、输入 Token、输出 Token、缓存命中率和每日成本
- **按模型细分** — 表格显示使用的每个模型、其会话数、Token 使用量和估算成本

### 定时任务

创建和管理定时任务，按重复计划运行 Agent 提示词。

- **创建** — 填写名称（可选）、提示词、cron 表达式（例如 `0 9 * * *`）和交付目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** — 每个任务显示其名称、提示词预览、计划表达式、状态徽章（启用/暂停/错误）、交付目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活动状态和暂停状态之间切换任务
- **编辑** — 打开预填充的模态框，更改任务的提示词、计划、名称或交付目标
- **立即触发** — 在正常计划之外立即执行任务
- **删除** — 永久删除定时任务

### 技能

浏览、搜索和切换已安装的技能和工具集，并从中心安装新的技能。技能从 `~/.hermes/skills/` 加载并按类别分组。

- **搜索** — 按名称、描述或类别过滤已安装的技能和工具集
- **类别过滤器** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、Red Teaming、AI）
- **切换** — 使用开关启用或禁用单个技能。更改将在下一次会话生效。
- **工具集** — 一个单独的视图显示内置工具集（文件操作、网页浏览等），包括其活动/非活动状态、设置要求和包含的工具列表
- **浏览中心** — 第三个视图在所有来源中搜索技能中心（与 `hermes skills search` 相同），通过标识符安装任何结果并显示实时安装日志，并提供“全部更新”按钮以刷新已安装的技能。

![技能管理页面 — 浏览中心视图：搜索、安装和更新](/img/dashboard/admin-skills-hub.png)

### MCP

无需 CLI 即可管理 [MCP](/integrations/mcp) 服务器。与 `hermes mcp` 读取的 `config.yaml` 中的 `mcp_servers` 块相同。

**您的 MCP 服务器：**

- **添加** — 注册 HTTP/SSE 服务器（URL）或 stdio 服务器（命令 + 参数），对于 stdio 服务器可选的 `KEY=VALUE` 环境变量
- **启用 / 禁用** — 在不删除服务器的情况下启用或禁用它。禁用的服务器保留在配置中，以便稍后重新启用。更改在下次网关重启后生效。
- **测试** — 连接到服务器，列出其工具，然后断开连接 — 在 Agent 依赖它之前验证连接
- **移除** — 从配置中删除服务器
- 列表视图中，类似 Secret 的环境变量值会被隐藏

**目录：** 浏览 Nous 批准的 MCP 服务器（捆绑的 `optional-mcps/` 目录）并一键安装其中任何一个。需要 API 密钥的条目会内联提示输入；值将保存到 `.env`。这与 `hermes mcp catalog` / `hermes mcp install` 使用的目录相同。

![MCP 管理页面 — 您的服务器带有启用/禁用开关，以及安装目录](/img/dashboard/admin-mcp.png)

### Webhooks

管理动态的 [Webhook 订阅](/user-guide/messaging/webhooks)。必须在消息设置中先启用 Webhook 平台；如果未启用，页面会显示提示。

- **创建** — 名称、描述、事件过滤器、交付目标、可选的直接交付模式以及一个 Agent 提示词。创建时，页面会显示路由 URL 和一次性 HMAC 密钥以供复制。
- **启用 / 禁用** — 启用或禁用订阅。禁用的路由保留在订阅文件中，但网关会拒绝其传入事件（403）。网关会热重载该文件，因此更改在下一次事件时生效 — 无需重启。
- **列表** — 每个订阅显示其 URL、事件和交付目标
- **删除** — 移除订阅

![Webhooks 管理页面 — 带有启用/禁用开关的订阅](/img/dashboard/admin-webhooks.png)

### 配对

无需 CLI 即可批准和撤销消息用户 — 远程管理员如何将 Telegram/Discord 等用户加入已配对的网关。与 `hermes pairing` 功能完全一致。

- **待处理请求** — 每个请求显示平台、代码、用户和时长，并带有批准按钮
- **已批准用户** — 每个用户显示平台和用户，并带有撤销按钮
- **清空待处理** — 删除所有未处理的配对代码

![配对管理页面](/img/dashboard/admin-pairing.png)

### 频道

从浏览器将 Hermes 连接到任何消息平台 — 与 `hermes setup gateway` 功能完全一致。页面列出每个支持的频道（Telegram、Discord、Slack、Matrix、Mattermost、WhatsApp、Signal、BlueBubbles/iMessage、Email、SMS/Twilio、钉钉、飞书/Lark、企业微信、微信、QQ 机器人、元宝，以及 API 服务器和 Webhook 端点）及其实时连接状态。

- **配置** — 打开每个平台的表单，包含该频道所需的确切字段（机器人令牌、应用令牌、服务器 URL、允许列表等）。Secret 字段渲染为密码输入框并存储为隐藏值；留空字段将保留现有值。必填字段已标记并经过验证。“设置指南”链接指向该平台的凭证文档。
- **启用 / 禁用** — 启用或禁用一个频道。凭证保留在磁盘上；仅活动状态发生变化。
- **测试** — 检查频道是否已配置、启用，并从网关报告实时连接。
- **重启网关** — 凭证写入 `~/.hermes/.env`，启用标志写入 `config.yaml`；网关在下次重启时连接每个启用的频道，您可以直接从页面触发重启。
![Channels 管理页面 — 每个消息平台的状态、启用开关和平台专属设置表单](/img/dashboard/admin-channels.png)

### 系统

一个用于安装范围操作的统一管理面板：

- **主机** — 实时系统状态：操作系统/内核、架构、主机名、Python 和 Hermes 版本、CPU 核心数 + 利用率、内存、Hermes 主目录的磁盘使用情况、运行时间和平均负载。（CPU/内存/磁盘信息在安装了 `psutil` 时提供；身份字段始终显示。）Hermes 版本显示一个**更新状态徽章**（最新 / 落后 N 个提交）和一个**检查更新**按钮。当 git 或 pip 安装有可用更新时，一个**立即更新**按钮会打开一个确认对话框 — 显示你将拉取多少个提交 — 然后在后台运行 `hermes update`。在 Docker/Nix/Homebrew 安装中，仪表板无法就地应用更新，因此会显示正确的带外更新命令。
- **Nous Portal** — 登录状态、活动的推理提供商，以及工具网关路由表（哪些工具通过 Portal 运行 vs. 本地运行），并附有管理订阅的链接。是 `hermes portal` 的只读镜像。
- **技能策展器** — 后台技能维护状态（活动/暂停、间隔、上次运行），带有暂停/恢复和立即运行按钮。镜像 `hermes curator`。
- **消息网关** — 启动、停止和重启消息网关，并显示实时状态（运行/停止、PID、状态）
- **记忆** — 选择外部记忆提供商（或仅使用内置的），并重置内置的 `MEMORY.md` / `USER.md` 存储
- **凭证池** — 添加和移除 Agent 轮询使用的轮换 API 密钥（按提供商）。列表中的密钥会被脱敏；原始值仅对 Agent 可见。
- **运维** — 运行 `doctor`、安全审计、创建备份、从备份存档恢复、更新技能、显示系统提示词大小细分、生成支持转储，或为已弃用的设置迁移配置。每个操作都会生成一个后台任务，其实时日志会流式传输到页面。
- **检查点** — 查看 `/rollback` 影子存储大小并进行清理
- **Shell 钩子** — 列出已配置的钩子及其同意状态 + 可执行状态，**创建**一个钩子（事件、命令、匹配器、超时，附带可选同意的授权），以及移除一个钩子。钩子运行任意命令，因此创建表单带有安全警告，并且钩子仅在授予同意后才会触发。

![系统管理页面 — 主机状态和 Nous Portal 状态](/img/dashboard/admin-system-top.png)

![系统管理页面 — 技能策展器、消息网关、记忆和凭证池](/img/dashboard/admin-system-curator.png)

![系统管理页面 — 运维、检查点和 Shell 钩子](/img/dashboard/admin-system-ops.png)

创建 Shell 钩子（注意同意复选框和运行任意命令的警告）：

![新建 Shell 钩子模态框](/img/dashboard/admin-hook-create.png)

:::warning 安全
Web 仪表板会读取和写入你的 `.env` 文件，该文件包含 API 密钥和机密信息。默认情况下，它绑定到 `127.0.0.1` — 仅可从你的本地机器访问。如果你绑定到 `0.0.0.0`，你网络上的任何人都可以查看和修改你的凭证。仪表板本身没有身份验证功能。
:::

## `/reload` 斜杠命令

仪表板的 PR 还在交互式 CLI 中添加了一个 `/reload` 斜杠命令。通过 Web 仪表板（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 来获取更改而无需重启：

```
你 → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将把 `~/.hermes/.env` 重新读入运行进程的环境变量中。当你通过仪表板添加了新的提供商密钥并希望立即使用时非常有用。

## REST API

Web 仪表板公开了一个前端使用的 REST API。你也可以直接调用这些端点进行自动化操作：

### GET /api/status

返回 Agent 版本、消息网关状态、平台状态和活动会话数。

### GET /api/sessions

返回最近 20 个会话及其元数据（模型、Token 计数、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式 — 类型、描述、类别，以及适用的选择选项。前端使用此信息为每个字段渲染正确的输入组件。

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

返回所有已配置的定时任务及其状态、计划和运行历史。

### POST /api/cron/jobs

创建新的定时任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停定时任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复已暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger

触发定时任务。
立即触发一个定时任务，无论其计划如何。

### DELETE /api/cron/jobs/\{job_id\}

删除一个定时任务。

### GET /api/skills

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表和激活/配置状态。

### 管理端点

这些端点支撑着 MCP、Channels、Webhooks、Pairing 和 System 页面。它们与 `/api/` 下的其他端点位于相同的认证门控之后。

| 方法 & 路径 | 用途 |
|---------------|---------|
| `GET /api/mcp/servers` | 列出已配置的 MCP 服务器（环境变量值已脱敏） |
| `POST /api/mcp/servers` | 添加一个服务器。请求体：`{name, url?, command?, args?, env?, auth?}` |
| `POST /api/mcp/servers/{name}/test` | 连接、列出工具、断开连接 |
| `PUT /api/mcp/servers/{name}/enabled` | 启用 / 禁用一个服务器 |
| `DELETE /api/mcp/servers/{name}` | 移除一个服务器 |
| `GET /api/mcp/catalog` | 浏览 Nous 批准的 MCP 目录 |
| `POST /api/mcp/catalog/install` | 安装一个目录条目（需要环境变量） |
| `GET /api/messaging/platforms` | 列出每个消息通道及其状态 + 每个平台的设置字段 |
| `PUT /api/messaging/platforms/{id}` | 配置一个通道。请求体：`{enabled?, env?, clear_env?}`（env 写入 `.env`，enabled 写入 `config.yaml`） |
| `POST /api/messaging/platforms/{id}/test` | 报告通道是否已配置、启用并连接 |
| `GET /api/pairing` | 列出待处理 + 已批准的消息用户 |
| `POST /api/pairing/approve` | 批准一个代码。请求体：`{platform, code}` |
| `POST /api/pairing/revoke` | 撤销一个用户。请求体：`{platform, user_id}` |
| `POST /api/pairing/clear-pending` | 丢弃所有待处理的代码 |
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
| `POST /api/ops/hooks` · `DELETE /api/ops/hooks` | 创建 / 移除一个 shell 钩子（需同意门控） |
| `GET /api/system/stats` | 主机统计信息 — 操作系统、CPU、内存、磁盘、运行时间 |
| `GET /api/hermes/update/check` | 报告更新可用性（落后提交数、安装方法）但不应用。`?force=1` 可清除 6 小时缓存 |
| `GET /api/curator` · `PUT .../paused` · `POST .../run` | 技能策展器状态 + 暂停/恢复 + 运行 |
| `GET /api/portal` | Nous Portal 认证 + Tool Gateway 路由（只读） |
| `POST /api/ops/prompt-size` · `/dump` · `/config-migrate` | 诊断（后台运行） |
| `PUT /api/webhooks/{name}/enabled` | 启用 / 禁用一个 webhook 路由 |
| `POST /api/skills/hub/install` · `/uninstall` · `/update` | Skills hub 操作（后台运行） |
| `GET /api/skills/hub/search` | 在所有源中搜索技能中心 |
| `GET /api/sessions/stats` | 会话存储统计信息 |
| `PATCH /api/sessions/{id}` | 重命名 / 归档一个会话 |
| `GET /api/sessions/{id}/export` | 将会话（元数据 + 消息）导出为 JSON |
| `POST /api/sessions/prune` | 删除早于 N 天的已结束会话 |
| `PUT /api/cron/jobs/{id}` | 编辑定时任务的提示词 / 计划 / 名称 / 交付方式 |

## 认证（门控模式）

当仪表板绑定到公共或非环回地址时 — 即除 `127.0.0.1` / `localhost` 之外的任何地址 — Hermes Agent 会启用认证门控。每个请求都必须携带一个已验证的会话 cookie，否则将被重定向到登录页面。系统内置了三种提供商：

- **[用户名/密码](#usernamepassword-provider-no-oauth-idp)** — 为自托管/本地部署/家庭实验室仪表板添加认证的最简单方式。无需外部身份提供商。**仅限在受信任的网络或 VPN 后使用 — 不适用于公开互联网暴露。**
- **[OAuth (Nous Portal)](#default-provider-nous-research)** — 适用于托管部署和任何可通过公共互联网访问的仪表板，也是[远程连接 Hermes Desktop](#connecting-hermes-desktop-to-a-remote-backend) 的推荐方式。每次登录都会根据您的 Nous 账户进行验证，因此此提供商适用于面向互联网的使用场景。
- **[自托管 OIDC](#self-hosted-oidc-provider)** — 用于通过标准 OpenID Connect 引入您自己的身份提供商（Keycloak、Auth0、Okta、通过 OIDC 桥接的 Google、GitHub 等）。不涉及 Nous Portal；适用于前置符合标准的 OIDC 服务器时的公开互联网暴露。

绑定到环回地址的操作员自有仪表板不受影响 — 无需认证，无登录页面。

### 门控启用时机

| 标志 | 认证门控 | 使用场景 |
|-------|-----------|----------|
| `hermes dashboard`（默认 — 绑定到 `127.0.0.1`） | 关闭 | 本地开发 |
| `hermes dashboard --host 0.0.0.0` | **开启** | 远程 / 生产环境 — 使用用户名/密码提供商或 OAuth 进行保护 |

当且仅当满足以下条件时，门控才会开启：

1. 绑定主机不是 `127.0.0.1`、`::1`、`localhost` 或 `0.0.0.0`，**并且**
2. **未**设置 `--insecure` 标志。

:::danger `--insecure` 完全禁用认证
`--insecure` 会跳过门控，并提供一个未经认证的仪表板，该仪表板可以读取/写入您的 `.env`（API 密钥、密钥）并可以运行 Agent 命令。**请勿将其用于远程连接。** 要将仪表板暴露给另一台机器，请配置[用户名/密码提供商](#usernamepassword-provider-no-oauth-idp)（或 OAuth）并保持 `--insecure` 关闭。该标志仅作为在完全受信任、有防火墙的单主机网络上的最后逃生手段。
:::
### 故障关闭语义

如果消息网关会启用但**没有**注册任何 `DashboardAuthProvider`（没有 Nous 插件，没有自定义插件），`hermes dashboard` 会拒绝绑定并显示明确的错误信息。不存在“默认拒绝但接受一切”的回退机制 —— 配置错误的受保护仪表盘永远不会启动。

### 默认提供商：Nous Research

捆绑的 `plugins/dashboard_auth/nous` 插件**始终安装**并自动加载。当配置了客户端 ID 时，它会自动注册一个名为 `nous` 的 `DashboardAuthProvider`。

因为每次登录都会通过 Nous Portal 验证并受您的 Nous 账户保护，**所以 Nous 提供商适合将仪表盘暴露在公共互联网上。**

#### 注册仪表盘

要使用 Nous 提供商，您需要一个 OAuth 客户端 ID（格式为 `agent:{id}`）。有两种获取方式：

- **CLI — `hermes dashboard register`。** 在仪表盘所在的主机上运行它。它会解析您现有的 Nous 登录（如果尚未登录，请先运行 `hermes setup`），向 Portal 注册一个自托管的 OAuth 客户端，并将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env` 文件。可选标志：`--name`（一个人类可读的标签，否则自动生成）和 `--redirect-uri`（面向互联网主机的公共 HTTPS 回调 URL）。

  ```bash
  hermes dashboard register
  # ✓ 已注册仪表盘 "swift_falcon"
  # …将 HERMES_DASHBOARD_OAUTH_CLIENT_ID 写入 ~/.hermes/.env
  ```

- **GUI — 本地仪表盘页面。** 在 Nous Portal 中打开 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards)，从浏览器注册、命名、管理和撤销自托管仪表盘。将生成的 `agent:{id}` 客户端 ID 复制到 `HERMES_DASHBOARD_OAUTH_CLIENT_ID`（环境变量）或 `dashboard.oauth.client_id`（config.yaml）中。这也是您撤销通过 CLI 注册的仪表盘的地方。

#### 配置

该插件从两个层面读取配置，当环境变量设置为非空值时，环境变量优先：

**`config.yaml`** — 规范层面：

```yaml
dashboard:
  oauth:
    client_id: agent:01HXYZ…             # 启用消息网关所必需
```

**环境变量** — 操作员覆盖：

| 环境变量 | 覆盖项 | 格式 | 由谁提供 |
|---------|-----------|--------|----------------|
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | `dashboard.oauth.client_id` | `agent:{instance_id}` | `hermes dashboard register` |

根据 Hermes Agent 的约定（`~/.hermes/.env` 仅用于 API 密钥/机密），**对于本地开发、内部部署以及任何您直接控制的部署，建议在 `config.yaml` 中设置这些值**。环境变量路径的存在是为了让托管平台的密钥注入能够推送每次部署的 `client_id`，而无需任何人在镜像内编辑 `config.yaml` —— 这是其主要目的。

空的环境变量值被视为未设置，因此已配置但未填充的平台密钥不会意外地遮蔽有效的 `config.yaml` 条目。

如果两个来源都没有提供 client_id，插件会报告具体原因，并且仪表盘的故障关闭绑定错误会明确告诉您需要修复什么：

```
拒绝将仪表盘绑定到 0.0.0.0 — 在非环回绑定上启用了 OAuth 身份验证网关，但未注册任何身份验证提供商。

捆绑的提供商报告了以下问题：
  • nous: 未设置 HERMES_DASHBOARD_OAUTH_CLIENT_ID（并且
    config.yaml 中的 dashboard.oauth.client_id 为空）。Nous Portal
    在部署 Hermes Agent 实例时会提供此环境变量（格式为 'agent:{instance_id}'）—
    请将其设置为您提供的客户端 ID（作为环境变量或在 config.yaml 的 dashboard.oauth.client_id 下），
    或者传递 --insecure 以完全跳过 OAuth 网关。

或者传递 --insecure 以跳过身份验证网关（在不信任的网络上不推荐）。
```

#### 工作示例：Nous Research

从已登录的 Hermes 安装到受 Nous 保护的仪表盘，只需三步。

**1. 登录并注册仪表盘。** `hermes dashboard register` 使用您现有的 Nous 登录来配置 OAuth 客户端，并将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env`：

```bash
hermes setup            # 如果您尚未登录 Nous Portal
hermes dashboard register
# ✓ 已注册仪表盘 "swift_falcon"
# …将 HERMES_DASHBOARD_OAUTH_CLIENT_ID 写入 ~/.hermes/.env
```

**2. 在可访问的地址上运行仪表盘。** 非环回绑定且不带 `--insecure` 会启用 OAuth 网关，刚刚写入的 `client_id` 会激活 `nous` 提供商：

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<主机>:9119/`，您将被重定向到 `/login`。点击**使用 Nous Research 登录** → 在 Portal 进行身份验证 → 返回已通过身份验证的仪表盘。从任何机器验证网关：

```bash
curl -s http://<主机>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

然后 `GET /api/auth/me` 会返回已验证的会话（`provider: nous`）。对于面向互联网的主机，请使用 `--redirect-uri https://hermes.example.com/auth/callback` 进行注册，并设置 `HERMES_DASHBOARD_PUBLIC_URL`，以便 OAuth 回调解析到您的公共 URL（参见[公共 URL 覆盖](#public-url-override)）。

### 用户名/密码提供商（无需 OAuth IDP）

如果您不想连接 OAuth 身份提供商 —— 一个自托管的“只需为我的仪表盘设置密码”的部署 —— 捆绑的 `plugins/dashboard_auth/basic` 插件会注册一个名为 `basic` 的 `DashboardAuthProvider`，它使用**用户名和密码**进行身份验证，而不是 OAuth 重定向。

它连接到与 OAuth 提供商相同的网关：在非环回绑定且不带 `--insecure` 时启用网关，登录页面为此提供商呈现凭据表单（而不是“使用 X 登录”按钮），并且登录之后的一切 —— 会话 Cookie、透明刷新、WS 票据、注销、审计日志 —— 都与 OAuth 路径相同。会话是由提供商自行生成的无状态 HMAC 签名 Token，因此**没有数据库，也没有外部 IDP**。密码哈希使用标准库 `scrypt`（无第三方依赖）。
:::warning 仅限在受信任的网络中使用 —— 不要暴露在公共互联网上
用户名/密码提供商适用于在**受信任网络**上自托管/本地部署/家庭实验室的仪表板，或仅能通过**VPN**访问的场景。它保护的是单个共享凭据，背后没有外部身份提供商、MFA 或多用户账户，因此**不适合将仪表板直接暴露在公共互联网上**。对于面向互联网的仪表板，请使用 [Nous Research 提供商](#default-provider-nous-research)（或您自己的[自托管 OIDC](#self-hosted-oidc-provider) / [自定义 OAuth](#custom-providers) 提供商）。

#### 配置

与 Nous 提供商类似，它从 `config.yaml`（规范配置）读取配置，当环境变量设置为非空时，环境变量优先。仅当配置了 `username` 加上 `password_hash`（首选）或 `password` 时才会激活 —— 否则它不执行任何操作，因此 OAuth 用户和环回/`--insecure` 操作者不受影响。

**`config.yaml`:**

```yaml
dashboard:
  basic_auth:
    username: admin
    # 首选 —— 静态存储时无明文。使用以下命令计算：
    #   python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"
    password_hash: "scrypt$16384$8$1$…$…"
    # ...或者使用明文密码（加载时在内存中哈希化；静态存储安全性较低）：
    # password: "s3cret"
    secret: "<32+ random bytes, base64 or hex>"  # token-signing key
    session_ttl_seconds: 43200                    # optional; access-token lifetime (default 12h)
```

**环境变量覆盖：**

| 环境变量 | 覆盖项 | 备注 |
|---------|-----------|-------|
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | `dashboard.basic_auth.username` | 激活所必需 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` | `dashboard.basic_auth.password_hash` | 首选（静态存储时无明文） |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | `dashboard.basic_auth.password` | 明文；**优先于配置文件中的 `password_hash`**，因此您可以通过环境变量轮换密码 |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | `dashboard.basic_auth.secret` | token 签名密钥 |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | `dashboard.basic_auth.session_ttl_seconds` | 访问令牌生命周期 |

:::caution 设置明确的 `secret` 以保持会话稳定
当 `secret` 为空时，会生成一个随机的进程内签名密钥。这对于单个进程来说没问题，但意味着**每次重启都会使所有会话失效**，并且会话**无法跨多个工作进程**。对于需要重启后保持会话/多工作进程部署的场景，请设置一个明确的 `secret`。
:::

`/auth/password-login` 端点按客户端 IP 进行速率限制（默认 10 次尝试/分钟 → HTTP 429），并且对于未知用户和错误密码都返回一个通用的 `401 Invalid credentials` 响应，因此它不能被用作用户名枚举的查询接口。

#### 操作示例：用户名/密码

只需三步，即可从零开始在受信任网络上搭建一个需要密码访问的仪表板。

**1. 在 `~/.hermes/.env` 中设置凭据。** 对密码进行哈希处理，这样静态存储时就没有明文，并设置一个稳定的签名密钥，以便会话在重启后得以保持：

```bash
# 计算您所选密码的 scrypt 哈希值：
HASH=$(python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('choose-a-strong-password'))")

cat >> ~/.hermes/.env <<EOF
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH=$HASH
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env
```

**2. 在可访问的地址上运行仪表板。** 非环回地址绑定且不使用 `--insecure` 选项会启用身份验证门，而用户名和哈希值会激活 `basic` 提供商：

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，您将被重定向到 `/login` —— 这是一个**凭据表单**（而不是“使用 X 登录”按钮）。输入 `admin` / 您的密码 → 进入已通过身份验证的仪表板。从任何机器验证身份验证门：

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

`GET /api/auth/me` 随后会返回已验证的会话（`provider: basic`）。请将其置于 VPN 之后 —— 请参阅上面的警告；对于公共主机，请使用 [Nous Research](#default-provider-nous-research) 或[自托管 OIDC](#self-hosted-oidc-provider) 提供商。

#### 编写您自己的密码提供商

`basic` 只是一个扩展点的实现。任何插件都可以注册一个密码提供商：在您的 `DashboardAuthProvider` 子类上设置 `supports_password = True`，并实现 `complete_password_login(*, username, password) -> Session`（拒绝时抛出 `InvalidCredentialsError`，如果您的后端存储宕机则抛出 `ProviderError`）。对于纯密码提供商，OAuth 的 `start_login` / `complete_login` 方法可以留作 `NotImplementedError` 存根。这是实现 LDAP 绑定、凭据数据库或任何其他非重定向身份验证方案的途径 —— 框架会为您处理表单、路由、Cookie 和刷新。

### 自托管 OIDC 提供商

如果您运行自己的身份提供商，捆绑的 `plugins/dashboard_auth/self_hosted` 插件会使用**标准 OpenID Connect** 对仪表板进行身份验证 —— 无需针对每个 IDP 编写代码，也不涉及 Nous Portal。它经过验证，可与任何符合规范的 OIDC 服务器配合使用：

> **Authentik · Keycloak · Zitadel · Authelia · Auth0 · Okta · Google · …**

与 Nous 提供商类似，它会自动加载，并且仅在配置完成后才注册自身，因此对于环回/`--insecure` 仪表板，它不执行任何操作。

#### 配置

配置一个 **issuer** 和一个 **client_id**（一个公共的 PKCE 客户端 —— 无需客户端密钥）。插件会从 `{issuer}/.well-known/openid-configuration` 获取 IDP 的 `authorization_endpoint`、`token_endpoint` 和 `jwks_uri`，因此您永远不需要硬编码端点 URL。

**`config.yaml`** —— 规范配置表面：

```yaml
dashboard:
  oauth:
    provider: self-hosted
    self_hosted:
      issuer: https://auth.example.com/application/o/hermes/   # required
      client_id: hermes-dashboard                              # required
      scopes: "openid profile email"                           # optional (this is the default)
```
**环境变量** — 操作员覆盖（当设置为非空时，环境变量优先级高于 `config.yaml`；空值被视为未设置）：

| 环境变量 | 覆盖项 | 备注 |
|---------|-----------|-------|
| `HERMES_DASHBOARD_OIDC_ISSUER` | `dashboard.oauth.self_hosted.issuer` | OIDC 颁发者 URL — 必需 |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | `dashboard.oauth.self_hosted.client_id` | 公共客户端 ID — 必需 |
| `HERMES_DASHBOARD_OIDC_SCOPES` | `dashboard.oauth.self_hosted.scopes` | 默认为 `openid profile email` |

在你的 IDP 中，注册一个使用授权码 + PKCE (S256) 授权的**公共**应用程序/客户端，并将仪表板的回调 URL 添加为允许的重定向 URI。回调 URL 是 `<dashboard public URL>/auth/callback`（关于仪表板在代理后如何推导其公共 URL，请参阅 [公共 URL 覆盖](#public-url-override)）。

#### 验证内容

该提供商根据发现的 `jwks_uri` 验证 OpenID Connect **ID Token** (RS256/ES256)，并将 `iss` 和 `aud` 声明固定为你配置的 `issuer` 和 `client_id`。标准的 OIDC 声明映射到仪表板会话：

| 会话字段 | 声明 |
|---------------|----------|
| `user_id` | `sub` (必需) |
| `email` | `email` |
| `display_name` | `name` → `preferred_username` → `nickname` → `email` |
| `org_id` | `org_id` / `organization`，否则为拼接的 `groups` |

ID Token 是建立身份的依据 — 访问令牌被视为不透明的（OIDC 规范不要求它必须是 JWT）。端点 URL 必须使用 HTTPS（本地开发 IDP 允许使用环回地址 `http://`），并且发现文档中公布的 `issuer` 必须与你配置的匹配（允许尾部斜杠的差异）。当 IDP 颁发刷新令牌时，将通过标准的 `refresh_token` 授权用于静默重新认证；登出时，如果 IDP 公布了 RFC 7009 的 `revocation_endpoint`，则会调用它。

> **机密客户端**（那些带有 `client_secret` 的）目前不受支持 — 请配置一个公共 + PKCE 客户端，这是面向浏览器的仪表板的典型选择。

#### 操作示例：Keycloak

[Keycloak](https://www.keycloak.org/) 是最容易搭建用于本地测试的自托管 OIDC 服务器之一 — 它在开发模式下（内存数据库）作为单个容器运行，并暴露标准的 OIDC 发现。本指南将帮助你在几分钟内从零开始实现一个可用的仪表板登录。

**1. 使用预配置的领域运行 Keycloak。** 将此领域导出保存为 `realm-hermes.json` — 它定义了一个 `hermes` 领域、一个**公共 PKCE 客户端** (`hermes-dashboard`) 和一个测试用户，所有这些都在启动时导入，因此无需在管理界面中点击任何内容：

```json
{
  "realm": "hermes",
  "enabled": true,
  "clients": [
    {
      "clientId": "hermes-dashboard",
      "name": "Hermes Agent Dashboard",
      "enabled": true,
      "publicClient": true,
      "standardFlowEnabled": true,
      "protocol": "openid-connect",
      "redirectUris": ["http://localhost:9119/auth/callback"],
      "webOrigins": ["http://localhost:9119"],
      "attributes": { "pkce.code.challenge.method": "S256" }
    }
  ],
  "users": [
    {
      "username": "testuser",
      "enabled": true,
      "emailVerified": true,
      "email": "testuser@example.com",
      "firstName": "Test",
      "lastName": "User",
      "credentials": [
        { "type": "password", "value": "testpassword", "temporary": false }
      ]
    }
  ]
}
```

启动它（Keycloak 26+），将该文件挂载到导入目录：

```bash
docker run --rm -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -v "$PWD/realm-hermes.json:/opt/keycloak/data/import/realm-hermes.json:ro" \
  quay.io/keycloak/keycloak:26.0 \
  start-dev --import-realm
```

启动后，该领域将在 `http://localhost:8080/realms/hermes/.well-known/openid-configuration`（颁发者 `http://localhost:8080/realms/hermes`）公布标准的 OIDC 发现。管理控制台位于 `http://localhost:8080/` (`admin` / `admin`)。

**2. 将仪表板指向它。** 自托管插件允许使用环回地址 `http://` 作为颁发者（任何非环回颁发者都需要 HTTPS），因此本地的 Keycloak 可以直接使用：

```bash
export HERMES_DASHBOARD_OIDC_ISSUER="http://localhost:8080/realms/hermes"
export HERMES_DASHBOARD_OIDC_CLIENT_ID="hermes-dashboard"
export HERMES_DASHBOARD_PUBLIC_URL="http://localhost:9119"
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

`HERMES_DASHBOARD_PUBLIC_URL` 告诉仪表板其 OAuth 回调地址是 `http://localhost:9119/auth/callback` — 这是上面领域注册的重定向 URI。绑定到 `0.0.0.0`（非环回绑定）且不使用 `--insecure` 将启用 OAuth 网关。

**3. 登录。** 打开 `http://localhost:9119/`，你将被重定向到 `/login`。点击 **使用自托管 OIDC 登录** → 在 Keycloak 使用 `testuser` / `testpassword` 认证 → 返回已认证的仪表板。侧边栏显示 `Logged in as Test User via self-hosted`，并且 `GET /api/auth/me` 返回已验证的会话 (`provider: self-hosted`, `email: testuser@example.com`)。

> 如果你在不同的主机/端口上绑定或浏览，请将该来源的 `…/auth/callback` 添加到 Keycloak 管理控制台（Clients → hermes-dashboard → Settings）中客户端的**有效重定向 URI**。同样的模式适用于 Authentik、Zitadel、Authelia 和其他 OIDC 服务器 — 只有颁发者 URL 和客户端注册界面不同。

### 公共 URL 覆盖

默认情况下，仪表板从请求中重构 OAuth 回调 URL — `X-Forwarded-Host` + `X-Forwarded-Proto` + `X-Forwarded-Prefix`（当 uvicorn 配置了 `proxy_headers=True` 时，`start_server` 在网关下启用此配置）。这可以在正确设置了所有三个头的反向代理后面开箱即用。

对于不能可靠转发这些头的反向代理部署（手动 nginx 设置、本地入口、具有部分代理链的自定义域名部署），请将 `dashboard.public_url`（或 `HERMES_DASHBOARD_PUBLIC_URL`）设置为仪表板被访问的**完整公共 URL**：
```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
```

设置后，OAuth 回调 URL 将直接变为 `<public_url>/auth/callback` —— 在该代码路径上会忽略 `X-Forwarded-Prefix`，因为操作员已明确声明了公共 URL。这是有意为之：在常见情况下，前缀已经包含在 `public_url` 中，如果再加上前缀会导致双重前缀。

优先级与其他仪表板设置相同 —— 环境变量优先于 `config.yaml`：

| 配置方式 | 覆盖路径 | 使用场景 |
|---------|---------------|-------------|
| `config.yaml` 中的 `dashboard.public_url` | `HERMES_DASHBOARD_PUBLIC_URL` | 本地开发 / 本地部署（规范方式） |
| `HERMES_DASHBOARD_PUBLIC_URL` 环境变量 | — | 托管平台密钥 / CI |
| （未设置） | — | 默认 —— 从 `X-Forwarded-*` 头部重构 |

验证会拒绝不含 `http://` / `https://` 协议、不含主机名或包含引号/尖括号/空白字符/控制字符的值。格式错误的值会静默回退到头部重构，以便登录流程继续工作，而不是将用户导向恶意 URL。

> **注意：** `public_url` 仅覆盖 OAuth 回调 URL。`Secure` cookie 标志仍由 `request.url.scheme` 控制（在 `proxy_headers` 下遵循 `X-Forwarded-Proto`），因此在 TLS 终止的公共部署上使用 `http://` 的 `public_url` 会产生非 Secure cookie。这是操作员容易犯错的地方 —— 请将 `public_url` 与上游正确的 TLS 终止配对使用。

### OAuth 流程

提供商实现了 [Nous Portal OAuth 合约 v1](https://github.com/NousResearch/nous-account-service/blob/main/docs/agent-dashboard-oauth-contract.md) —— 使用 PKCE (S256) 的授权码授权模式：

1. 用户访问 `/` 但没有会话 cookie → 网关重定向到 `/login`。
2. 登录页面显示“使用 Nous Research 继续”按钮 → `/auth/login?provider=nous`。
3. 服务器将 PKCE 状态存储在短期 cookie 中，将用户重定向到 `https://portal.nousresearch.com/oauth/authorize?…`。
4. 用户在 Portal 完成身份验证，跳转到 `/auth/callback?code=…&state=…`。
5. 服务器在 `POST /api/oauth/token` 处用 code 交换访问令牌，根据 Portal 的 JWKS (`/.well-known/jwks.json`) 验证 JWT 签名，并设置 `hermes_session_at` cookie。
6. 用户被重定向到 `/`（或通过 `next=` 查询参数重定向到原始的深度链接路径）。

访问令牌的有效期为 15 分钟。**合约 v1 中没有刷新令牌** —— 当令牌过期时，SPA 的 fetch 包装器会检测到 401 响应信封，并全页面导航回 `/login` 以重新运行流程。

### 设置的 Cookie

| 名称 | 生命周期 | 备注 |
|------|----------|-------|
| `hermes_session_at` | 令牌 TTL (15 分钟) | HttpOnly, SameSite=Lax, 使用 HTTPS 时 Secure |
| `hermes_session_pkce` | 10 分钟 | HttpOnly；在往返过程中保存 PKCE 验证器和提供商提示 |
| `hermes_session_rt` | v1 中未使用 | 为向前兼容保留；当 `refresh_token` 为空时不写入 |

这三个 cookie 都设置了 `Path=/` 和 `SameSite=Lax`。`Secure` 标志在通过 HTTPS 访问仪表板时设置（通过请求 URL 方案检测 —— 在 `proxy_headers=True` 时遵循来自上游 TLS 终结器的 `X-Forwarded-Proto`）。

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
# 快速环境变量路径。
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

仪表板的 React StatusPage 在“Web 服务器”下显示相同的字段。登录后，侧边栏的 AuthWidget 会显示当前身份。

## 将 Hermes Desktop 连接到远程后端

Hermes Desktop 可以驱动运行在另一台机器上的 Hermes 后端（VPS、家庭服务器、Tailscale 后面的 Mini）。在应用中，这位于 **设置 → 消息网关 → 远程网关** 下，需要提供 **远程 URL** 和一种 **登录** 方式。（关于桌面应用本身 —— 安装、设置、聊天 —— 请参阅 [Hermes Desktop](/user-guide/desktop) 页面。）

您可以使用捆绑的认证提供商之一来保护远程仪表板，桌面应用会根据后端通告的提供商进行登录。对于您自己机器之外可访问的后端 —— VPS、公共主机、任何面向互联网的服务 —— 推荐的提供商是 **OAuth (Nous Portal)**（使用 [`hermes dashboard register`](#registering-a-dashboard) 注册，并使用 *使用 Nous Research 登录* 登录）。捆绑的 [用户名/密码提供商](#usernamepassword-provider-no-oauth-idp) 是当后端位于受信任的 LAN 或仅通过 VPN 可访问时的最快选项，但**不适合直接暴露在公共互联网上**。将仪表板绑定到非环回地址会启用其认证网关；登录后，Desktop 会自动为聊天 WebSocket 重用会话 —— 无需复制或粘贴令牌。
以下配方使用用户名/密码路径，因为这是在受信任网络上最快搭建的方式；如需 OAuth 路径，请参阅[默认提供商：Nous Research](#default-provider-nous-research)。

### 在后端（远程机器上）

```bash
# 1. 在 ~/.hermes/.env 中设置仪表板登录凭据（密钥文件，0600）。
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
# 推荐：设置一个稳定的签名密钥，以便会话在重启后得以保留。
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. 运行仪表板，绑定到可访问的地址。非回环地址绑定
#    会启用认证网关；用户名/密码提供商会处理登录。
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

不希望明文存储密码？请使用 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` 配合 scrypt 哈希值替代——完整配置请参阅[用户名/密码提供商（无 OAuth IdP）](#usernamepassword-provider-no-oauth-idp)。

如果将仪表板作为 systemd 服务运行，当单元文件包含 `EnvironmentFile=%h/.hermes/.env` 时，`~/.hermes/.env` 会被自动加载，因此凭据会在启动时进入环境变量。

:::warning
仪表板会读取和写入你的 `.env` 文件（API 密钥、密钥），并且可以运行 Agent 命令。此处展示的**用户名/密码**设置适用于受信任的网络——切勿将受密码保护的仪表板直接暴露在开放的互联网上。请将其置于 VPN 之后。[Tailscale](https://tailscale.com/) 是一个简洁的选择：绑定到机器的 tailscale IP（`--host <tailscale-ip>`）并使用 `http://<tailscale-ip>:9119` 作为远程 URL。只有你 tailnet 上的设备可以访问它。要通过公共互联网访问后端，请改用 **OAuth (Nous Portal)** 提供商。
:::

### 在 Hermes Desktop 中

**设置 → 消息网关 → 远程网关：**

- **远程 URL** — `http://<backend-host>:9119`（如果使用反向代理，支持像 `/hermes` 这样的路径前缀）
- **登录** — 应用会检测到用户名/密码网关并显示**登录**按钮；点击它并输入步骤 1 中的凭据
- **保存并重新连接** — 将桌面 shell 切换到远程后端

当后端设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 时，会话会自动刷新并在重启后得以保留。

### 环境变量覆盖

除了应用内设置，你还可以在启动桌面应用前通过环境变量将其指向后端。当设置了 `HERMES_DESKTOP_REMOTE_URL` 时，它会覆盖应用内保存的 URL（消息网关设置面板会显示“env override”徽章并禁用编辑）；你仍然需要从面板使用你的用户名和密码**登录**。

| 环境变量 | 值 |
|---------|-------|
| `HERMES_DESKTOP_REMOTE_URL` | `http://<backend-host>:9119` |

### 故障排除

- **“远程网关不完整”** — 你尚未输入远程 URL。
- **登录失败，出现 401 / “无效凭据”** — 用户名或密码与后端的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。后端对于未知用户和错误密码返回相同的通用错误，因此请检查两者。使用 `curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'` 确认网关状态——它应该报告 `true` 并包含 `"basic"`。
- **没有“登录”按钮——它要求会话 Token 替代** — 用户名/密码提供商未激活（`/api/status` 不会列出 `"basic"`）。请确保用户名和密码（或密码哈希）已设置，并且仪表板进程已加载它们。
- **每次重启后都退出登录** — 将 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置为一个稳定的值；否则签名密钥会在每次启动时重新生成。
- **连接被拒绝 / 超时** — 后端绑定到了 `127.0.0.1`（默认值）而非可访问的地址，或者防火墙/VPN 阻塞了端口。请绑定到 `0.0.0.0` 或 tailscale IP，并向你的受信任网络开放该端口。

## CORS

Web 服务器将 CORS 限制为仅限 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）

如果你在自定义端口上运行服务器，该来源会自动添加。

## 开发

如果你正在为 Web 仪表板前端做贡献：

```bash
# 终端 1：启动后端 API
hermes dashboard --no-open

# 终端 2：启动带有 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/`，由 FastAPI 服务器作为静态 SPA 提供服务。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这使仪表板与代码更新保持同步。如果未安装 `npm`，更新将跳过前端构建，`hermes dashboard` 将在首次启动时构建它。

## 主题和插件

仪表板内置了六个主题，并可以通过用户定义的主题、插件标签页和后端 API 路由进行扩展——全部即插即用，无需克隆仓库。

**实时切换主题**：从标题栏——点击语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 中的 `dashboard.theme` 下，并在页面加载时恢复。

**独立更改字体**：在同一选择器中——主题列表下方的**字体**部分会覆盖当前活动主题的 UI 字体。该选择在主题切换时保持不变（`config.yaml` → `dashboard.font`）；选择**主题默认**以清除它并返回活动主题自身的字体。

内置主题：

| 主题 | 特点 |
|-------|-----------|
| **Hermes Teal** (`default`) | 深青色 + 奶油色，系统字体，舒适的间距 |
| **Hermes Teal (Large)** (`default-large`) | 与默认主题相同，但文本为 18px，间距更宽松 |
| **Midnight** (`midnight`) | 深蓝紫色，Inter + JetBrains Mono 字体 |
| **Ember** (`ember`) | 暖深红色 + 青铜色，Spectral 衬线字体 + IBM Plex Mono 字体 |
| **Mono** (`mono`) | 灰度，IBM Plex 字体，紧凑 |
| **Cyberpunk** (`cyberpunk`) | 黑色背景上的霓虹绿色，Share Tech Mono 字体 |
| **Rosé** (`rose`) | 粉色 + 象牙色，Fraunces 衬线字体，宽敞 |
要构建自己的主题、添加插件选项卡、注入到 Shell 插槽或暴露插件特定的 REST 端点，请参阅 **[扩展仪表盘](./extending-the-dashboard)** — 完整指南涵盖：

- 主题 YAML 模式 — 调色板、排版、布局、资源、组件样式、颜色覆盖、自定义 CSS
- 布局变体 — `standard`、`cockpit`、`tiled`
- 插件清单、SDK、Shell 插槽、页面作用域插槽（将小部件注入到内置页面中，而无需覆盖它们）、后端 FastAPI 路由
- 完整的主题与插件结合演练（Strike Freedom cockpit 演示）
- 发现、重新加载和故障排除