---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的仪表盘，用于管理配置、API 密钥和监控会话"

# Web 仪表盘

Web 仪表盘是一个基于浏览器的用户界面，用于管理你的 Hermes Agent 安装。无需编辑 YAML 文件或运行 CLI 命令，你就可以通过简洁的 Web 界面配置设置、管理 API 密钥和监控会话。

## 快速开始

```bash
hermes web
```

这将启动一个本地 Web 服务器，并在你的浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全在你的机器上运行 —— 数据不会离开本地主机。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |

```bash
# 自定义端口
hermes web --port 8080

# 绑定到所有接口（在共享网络上使用需谨慎）
hermes web --host 0.0.0.0

# 启动时不打开浏览器
hermes web --no-open
```

## 前提条件

Web 仪表盘需要 FastAPI 和 Uvicorn。通过以下命令安装：

```bash
pip install hermes-agent[web]
```

如果你使用 `pip install hermes-agent[all]` 安装，则 Web 依赖项已包含在内。

当你未安装依赖项而运行 `hermes web` 时，它会告诉你需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

## 页面

### 状态

落地页显示你安装的实时概览：

- **Agent 版本** 和发布日期
- **消息网关状态** —— 运行/停止、PID、已连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 使用量以及对话预览

状态页面每 5 秒自动刷新一次。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都是从 `DEFAULT_CONFIG` 自动发现的，并按选项卡分类组织：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（本地/docker/ssh/modal）、超时、Shell 偏好
- **display** —— 皮肤、工具进度、恢复显示、加载动画设置
- **agent** —— 最大迭代次数、消息网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理工作量
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（ask/yolo/deny）
- 以及更多 —— config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉菜单。布尔值呈现为开关。其他所有内容都是文本输入。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（点击保存前不会保存）
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

:::warning 安全
Web 仪表盘读取和写入你的 `.env` 文件，该文件包含 API 密钥和机密信息。它默认绑定到 `127.0.0.1` —— 仅可从你的本地机器访问。如果你绑定到 `0.0.0.0`，你网络上的任何人都可以查看和修改你的凭据。仪表盘本身没有身份验证。
:::

## `/reload` 斜杠命令

该仪表盘 PR 还在交互式 CLI 中添加了一个 `/reload` 斜杠命令。通过 Web 仪表盘（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 来获取更改，而无需重启：

```
你 → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将把 `~/.hermes/.env` 重新读入正在运行的进程环境中。当你通过仪表盘添加了新的提供商密钥并希望立即使用时，这很有用。

## REST API

Web 仪表盘公开了一个供前端使用的 REST API。你也可以直接调用这些端点以实现自动化：

### GET /api/status

返回 Agent 版本、消息网关状态、平台状态和活跃会话数。

### GET /api/sessions

返回最近 20 个会话及其元数据（模型、Token 计数、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式 —— 类型、描述、类别以及适用的选择选项。前端使用此信息为每个字段渲染正确的输入组件。

### PUT /api/config

保存新配置。请求体：`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量及其设置/未设置状态、脱敏值、描述和类别。

### PUT /api/env

设置环境变量。请求体：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

删除环境变量。请求体：`{"key": "VAR_NAME"}`。

## CORS

Web 服务器将 CORS 限制为仅限 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）

如果你在自定义端口上运行服务器，该来源会自动添加。

## 开发

如果你正在为 Web 仪表盘前端做贡献：

```bash
# 终端 1：启动后端 API
hermes web --no-open

# 终端 2：启动带 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/`，由 FastAPI 服务器作为静态 SPA 提供服务。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这使仪表盘与代码更新保持同步。如果未安装 `npm`，更新将跳过前端构建，`hermes web` 将在首次启动时构建它。