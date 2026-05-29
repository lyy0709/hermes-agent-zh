---
title: "集成"
sidebar_label: "概览"
sidebar_position: 0
---

# 集成

Hermes Agent 连接到外部系统，用于 AI 推理、工具服务器、IDE 工作流、程序化访问等。这些集成扩展了 Hermes 的功能和运行环境。

:::tip 从这里开始
如果您只有时间设置一个集成，请设置 [Nous Portal](/integrations/nous-portal) —— 一次 OAuth 登录即可覆盖 300+ 模型以及四个工具网关工具（网络搜索、图像生成、TTS 和浏览器自动化）。
:::

## AI 提供商与路由

Hermes 开箱即用支持多个 AI 推理提供商。使用 `hermes model` 进行交互式配置，或在 `config.yaml` 中设置。

- **[AI 提供商](/user-guide/features/provider-routing)** — OpenRouter、Anthropic、OpenAI、Google 以及任何 OpenAI 兼容的端点。Hermes 会根据每个提供商自动检测视觉、流式传输和工具使用等能力。
- **[提供商路由](/user-guide/features/provider-routing)** — 对底层提供商处理您的 OpenRouter 请求进行细粒度控制。通过排序、白名单、黑名单和显式优先级排序来优化成本、速度或质量。
- **[备用提供商](/user-guide/features/fallback-providers)** — 当您的主模型遇到错误时，自动故障转移到备用 LLM 提供商。包括主模型故障转移以及用于视觉、压缩和网页提取的独立辅助任务故障转移。

## 工具服务器 (MCP)

- **[MCP 服务器](/user-guide/features/mcp)** — 通过 Model Context Protocol 将 Hermes 连接到外部工具服务器。无需编写原生 Hermes 工具即可访问来自 GitHub、数据库、文件系统、浏览器栈、内部 API 等的工具。支持 stdio 和 SSE 传输、每服务器工具过滤以及能力感知的资源/提示词注册。

## 网络搜索后端

`web_search` 和 `web_extract` 工具支持四个后端提供商，通过 `config.yaml` 或 `hermes tools` 配置：

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

快速设置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily | exa
```

如果未设置 `web.backend`，后端将根据可用的 API 密钥自动检测。自托管的 Firecrawl 也通过 `FIRECRAWL_API_URL` 支持。

## 浏览器自动化

Hermes 包含完整的浏览器自动化功能，提供多个后端选项，用于导航网站、填写表单和提取信息：

- **Browserbase** — 具有反机器人工具、验证码解决和住宅代理的托管云浏览器
- **Browser Use** — 替代的云浏览器提供商
- **本地 Chromium 系列 CDP** — 使用 `/browser connect` 连接到您正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器
- **本地 Chromium** — 通过 `agent-browser` CLI 实现的无头本地浏览器

有关设置和使用，请参阅[浏览器自动化](/user-guide/features/browser)。

## 语音与 TTS 提供商

跨所有消息平台的文本转语音和语音转文本：

| 提供商 | 质量 | 成本 | API 密钥 |
|----------|---------|------|---------|
| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
| **xAI TTS** | 良好 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需 |

语音转文本支持六个提供商：本地 faster-whisper（免费，在设备上运行）、本地命令包装器、Groq、OpenAI Whisper API、Mistral 和 xAI。语音消息转录适用于 Telegram、Discord、WhatsApp 和其他消息平台。详情请参阅[语音与 TTS](/user-guide/features/tts) 和[语音模式](/user-guide/features/voice-mode)。

## IDE 与编辑器集成

- **[IDE 集成 (ACP)](/user-guide/features/acp)** — 在 VS Code、Zed 和 JetBrains 等 ACP 兼容的编辑器中使用 Hermes Agent。Hermes 作为 ACP 服务器运行，在您的编辑器内呈现聊天消息、工具活动、文件差异和终端命令。

## 程序化访问

- **[API 服务器](/user-guide/features/api-server)** — 将 Hermes 作为 OpenAI 兼容的 HTTP 端点公开。任何支持 OpenAI 格式的前端 —— Open WebUI、LobeChat、LibreChat、NextChat、ChatBox —— 都可以连接并使用 Hermes 作为后端，并利用其完整的工具集。

## 记忆与个性化

- **[内置记忆](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化、精选的记忆。Agent 维护着跨会话持续存在的个人笔记和用户配置文件数据的有界存储。
- **[记忆提供商](/user-guide/features/memory-providers)** — 插入外部记忆后端以实现更深度的个性化。支持八个提供商：Honcho（辩证推理）、OpenViking（分层检索）、Mem0（云提取）、Hindsight（知识图谱）、Holographic（本地 SQLite）、RetainDB（混合搜索）、ByteRover（基于 CLI）和 Supermemory。

## 消息平台

Hermes 作为网关机器人运行在 27+ 个消息平台上，所有平台都通过相同的 `gateway` 子系统配置：

- **[Telegram](/user-guide/messaging/telegram)**、**[Discord](/user-guide/messaging/discord)**、**[Slack](/user-guide/messaging/slack)**、**[WhatsApp](/user-guide/messaging/whatsapp)**、**[Signal](/user-guide/messaging/signal)**、**[Matrix](/user-guide/messaging/matrix)**、**[Mattermost](/user-guide/messaging/mattermost)**、**[Email](/user-guide/messaging/email)**、**[SMS](/user-guide/messaging/sms)**、**[DingTalk](/user-guide/messaging/dingtalk)**、**[Feishu/Lark](/user-guide/messaging/feishu)**、**[WeCom](/user-guide/messaging/wecom)**、**[WeCom Callback](/user-guide/messaging/wecom-callback)**、**[Weixin](/user-guide/messaging/weixin)**、**[BlueBubbles](/user-guide/messaging/bluebubbles)**、**[QQ Bot](/user-guide/messaging/qqbot)**、**[Yuanbao](/user-guide/messaging/yuanbao)**、**[Home Assistant](/user-guide/messaging/homeassistant)**、**[Microsoft Teams](/user-guide/messaging/teams)**、**[Microsoft Teams Meetings](/user-guide/messaging/teams-meetings)**、**[Microsoft Graph Webhook](/user-guide/messaging/msgraph-webhook)**、**[Google Chat](/user-guide/messaging/google_chat)**、**[LINE](/user-guide/messaging/line)**、**[ntfy](/user-guide/messaging/ntfy)**、**[SimpleX](/user-guide/messaging/simplex)**、**[Open WebUI](/user-guide/messaging/open-webui)**、**[Webhooks](/user-guide/messaging/webhooks)**

有关平台比较表和设置指南，请参阅[消息网关概览](/user-guide/messaging)。

## 家庭自动化

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四个专用工具（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）控制智能家居设备。当配置了 `HASS_TOKEN` 时，Home Assistant 工具集会自动激活。

## 插件

- **[插件系统](/user-guide/features/plugins)** — 通过自定义工具、生命周期钩子和 CLI 命令扩展 Hermes，而无需修改核心代码。插件从 `~/.hermes/plugins/`、项目本地的 `.hermes/plugins/` 和 pip 安装的入口点发现。
- **[构建插件](/guides/build-a-hermes-plugin)** — 创建包含工具、钩子和 CLI 命令的 Hermes 插件的分步指南。

## 训练与评估

- **[批量处理](/user-guide/features/batch-processing)** — 并行运行 Agent 处理数百个提示词，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。