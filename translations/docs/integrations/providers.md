---
title: "AI 提供商"
sidebar_label: "AI 提供商"
sidebar_position: 1
---

# AI 提供商

本页面介绍如何为 Hermes Agent 设置推理提供商——从 OpenRouter 和 Anthropic 等云 API，到 Ollama 和 vLLM 等自托管端点，再到高级路由和回退配置。您需要至少配置一个提供商才能使用 Hermes。

## 推理提供商

您至少需要一种连接到 LLM 的方式。使用 `hermes model` 交互式地切换提供商和模型，或直接配置：

| 提供商 | 设置 |
|----------|-------|
| **Nous Portal** | `hermes model` (OAuth，基于订阅) |
| **OpenAI Codex** | `hermes model` (ChatGPT OAuth，使用 Codex 模型) |
| **GitHub Copilot** | `hermes model` (OAuth 设备代码流，`COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`) |
| **GitHub Copilot ACP** | `hermes model` (生成本地 `copilot --acp --stdio`) |
| **Anthropic** | `hermes model` (Claude Max + 通过 OAuth 获得的额外使用额度；也支持 Anthropic API 密钥或手动设置令牌——见下方说明) |
| **OpenRouter** | 在 `~/.hermes/.env` 中设置 `OPENROUTER_API_KEY` |
| **AI Gateway** | 在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY` (提供商: `ai-gateway`) |
| **z.ai / GLM** | 在 `~/.hermes/.env` 中设置 `GLM_API_KEY` (提供商: `zai`) |
| **Kimi / Moonshot** | 在 `~/.hermes/.env` 中设置 `KIMI_API_KEY` (提供商: `kimi-coding`) |
| **Kimi / Moonshot (中国)** | 在 `~/.hermes/.env` 中设置 `KIMI_CN_API_KEY` (提供商: `kimi-coding-cn`; 别名: `kimi-cn`, `moonshot-cn`) |
| **Arcee AI** | 在 `~/.hermes/.env` 中设置 `ARCEEAI_API_KEY` (提供商: `arcee`; 别名: `arcee-ai`, `arceeai`) |
| **GMI Cloud** | 在 `~/.hermes/.env` 中设置 `GMI_API_KEY` (提供商: `gmi`; 别名: `gmi-cloud`, `gmicloud`) |
| **MiniMax** | 在 `~/.hermes/.env` 中设置 `MINIMAX_API_KEY` (提供商: `minimax`) |
| **MiniMax 中国** | 在 `~/.hermes/.env` 中设置 `MINIMAX_CN_API_KEY` (提供商: `minimax-cn`) |
| **阿里云** | 在 `~/.hermes/.env` 中设置 `DASHSCOPE_API_KEY` (提供商: `alibaba`) |
| **阿里云编程计划** | `DASHSCOPE_API_KEY` (提供商: `alibaba-coding-plan`, 别名: `alibaba_coding`) — 独立的计费 SKU，不同的端点 |
| **Kilo Code** | 在 `~/.hermes/.env` 中设置 `KILOCODE_API_KEY` (提供商: `kilocode`) |
| **小米 MiMo** | 在 `~/.hermes/.env` 中设置 `XIAOMI_API_KEY` (提供商: `xiaomi`, 别名: `mimo`, `xiaomi-mimo`) |
| **腾讯 TokenHub** | 在 `~/.hermes/.env` 中设置 `TOKENHUB_API_KEY` (提供商: `tencent-tokenhub`, 别名: `tencent`, `tokenhub`, `tencentmaas`) |
| **OpenCode Zen** | 在 `~/.hermes/.env` 中设置 `OPENCODE_ZEN_API_KEY` (提供商: `opencode-zen`) |
| **OpenCode Go** | 在 `~/.hermes/.env` 中设置 `OPENCODE_GO_API_KEY` (提供商: `opencode-go`) |
| **DeepSeek** | 在 `~/.hermes/.env` 中设置 `DEEPSEEK_API_KEY` (提供商: `deepseek`) |
| **Hugging Face** | 在 `~/.hermes/.env` 中设置 `HF_TOKEN` (提供商: `huggingface`, 别名: `hf`) |
| **Google / Gemini** | 在 `~/.hermes/.env` 中设置 `GOOGLE_API_KEY` (或 `GEMINI_API_KEY`) (提供商: `gemini`) |
| **Google Gemini (OAuth)** | `hermes model` → "Google Gemini (OAuth)" (提供商: `google-gemini-cli`，支持免费套餐，浏览器 PKCE 登录) |
| **LM Studio** | `hermes model` → "LM Studio" (提供商: `lmstudio`，可选 `LM_API_KEY`) |
| **自定义端点** | `hermes model` → 选择 "Custom endpoint" (保存在 `config.yaml` 中) |

:::tip 模型键别名
在 `model:` 配置部分，您可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 效果相同。
:::


### 通过 OAuth 使用 Google Gemini (`google-gemini-cli`)

`google-gemini-cli` 提供商使用 Google 的 Cloud Code Assist 后端——与 Google 自家的 `gemini-cli` 工具使用的 API 相同。这同时支持**免费套餐**（个人账户有慷慨的每日配额）和**付费套餐**（通过 GCP 项目的标准版/企业版）。

**快速开始：**

```bash
hermes model
# → 选择 "Google Gemini (OAuth)"
# → 查看策略警告，确认
# → 浏览器打开 accounts.google.com，登录
# → 完成 — Hermes 会在首次请求时自动为您配置免费套餐
```

Hermes 默认附带 Google 的**公开** `gemini-cli` 桌面 OAuth 客户端——与 Google 在其开源 `gemini-cli` 中包含的凭据相同。桌面 OAuth 客户端不是机密的（PKCE 提供安全性）。您无需安装 `gemini-cli` 或注册自己的 GCP OAuth 客户端。

**认证工作原理：**
- 针对 `accounts.google.com` 的 PKCE 授权码流程
- 浏览器回调地址为 `http://127.0.0.1:8085/oauth2callback`（如果端口忙，则使用临时端口回退）
- 令牌存储在 `~/.hermes/auth/google_oauth.json` (chmod 0600，原子写入，跨进程 `fcntl` 锁)
- 在过期前 60 秒自动刷新
- 无头环境 (SSH, `HERMES_HEADLESS=1`) → 粘贴模式回退
- 飞行中刷新去重——两个并发请求不会重复刷新
- `invalid_grant` (刷新令牌被撤销) → 凭据文件被清除，提示用户重新登录

**推理工作原理：**
- 流量发送到 `https://cloudcode-pa.googleapis.com/v1internal:generateContent`
  (或 `:streamGenerateContent?alt=sse` 用于流式传输)，而不是付费的 `v1beta/openai` 端点
- 请求体包装为 `{project, model, user_prompt_id, request}`
- OpenAI 格式的 `messages[]`、`tools[]`、`tool_choice` 被转换为 Gemini 原生格式
  `contents[]`、`tools[].functionDeclarations`、`toolConfig`
- 响应被转换回 OpenAI 格式，以便 Hermes 的其余部分正常工作

**套餐与项目 ID：**

| 您的情况 | 操作 |
|---|---|
| 个人 Google 账户，想要免费套餐 | 无需操作 — 登录，开始聊天 |
| Workspace / 标准版 / 企业版账户 | 设置 `HERMES_GEMINI_PROJECT_ID` 或 `GOOGLE_CLOUD_PROJECT` 为您的 GCP 项目 ID |
| VPC-SC 保护的组织 | Hermes 检测到 `SECURITY_POLICY_VIOLATED` 并自动强制使用 `standard-tier` |

免费套餐在首次使用时自动配置一个 Google 托管的项目。无需 GCP 设置。

**配额监控：**

```
/gquota
```

显示每个模型的剩余 Code Assist 配额，并带有进度条：
```
Gemini Code Assist 配额（项目：123-abc）

  gemini-2.5-pro                      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░   85%
  gemini-2.5-flash [输入]            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░   92%
```

:::warning 政策风险
Google 认为在第三方软件中使用 Gemini CLI OAuth 客户端违反了其政策。一些用户报告了账户受限的情况。为了获得最低风险的体验，请通过 `gemini` 提供商使用您自己的 API 密钥。Hermes 会在 OAuth 开始前显示明确警告并要求用户明确确认。
:::

**自定义 OAuth 客户端（可选）：**

如果您更愿意注册自己的 Google OAuth 客户端——例如，为了将配额和授权范围限定在您自己的 GCP 项目中——请设置：

```bash
HERMES_GEMINI_CLIENT_ID=your-client.apps.googleusercontent.com
HERMES_GEMINI_CLIENT_SECRET=...   # 对于桌面客户端是可选的
```

在 [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) 注册一个 **桌面应用** OAuth 客户端，并确保启用了 Generative Language API。

:::info Codex 说明
OpenAI Codex 提供商通过设备码进行身份验证（打开一个 URL，输入一个代码）。Hermes 将生成的凭据存储在其自己的认证存储 `~/.hermes/auth.json` 中，并且可以导入 `~/.codex/auth.json` 中已存在的 Codex CLI 凭据（如果存在）。无需安装 Codex CLI。
:::

:::warning
即使使用 Nous Portal、Codex 或自定义端点，某些工具（视觉、网页摘要、MoA）也会使用单独的“辅助”模型。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 将这些任务路由到您的**主聊天模型**——即您在 `hermes model` 中选择的同一模型。您可以单独覆盖每个任务，将其路由到更便宜/更快的模型（例如，OpenRouter 上的 Gemini Flash）——请参阅 [辅助模型](/docs/user-guide/configuration#auxiliary-models)。
:::

:::tip Nous 工具网关
付费的 Nous Portal 订阅者还可以访问 **[工具网关](/docs/user-guide/features/tool-gateway)**——通过网络搜索、图像生成、TTS 和浏览器自动化，这些功能都通过您的订阅路由。无需额外的 API 密钥。在 `hermes model` 设置过程中会自动提供此功能，或者稍后通过 `hermes tools` 启用。
:::

### 两个用于模型管理的命令

Hermes 有**两个**模型命令，用途不同：

| 命令 | 在哪里运行 | 作用 |
|---------|-------------|--------------|
| **`hermes model`** | 您的终端（在任何会话之外） | 完整的设置向导——添加提供商、运行 OAuth、输入 API 密钥、配置端点 |
| **`/model`** | 在 Hermes 聊天会话内部 | 在**已配置的**提供商和模型之间快速切换 |

如果您尝试切换到尚未设置的提供商（例如，您只配置了 OpenRouter 但想使用 Anthropic），您需要 `hermes model`，而不是 `/model`。首先退出您的会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，完成提供商设置，然后开始一个新的会话。

### Anthropic（原生）

直接通过 Anthropic API 使用 Claude 模型——无需 OpenRouter 代理。支持三种认证方式：

:::caution 需要 Claude Max “额外用量”额度
当您通过 `hermes model` → Anthropic OAuth（或通过 `hermes auth add anthropic --type oauth`）进行身份验证时，Hermes 会以 Claude Code 的身份路由到您的 Anthropic 账户。**这仅在您拥有 Claude Max 计划并购买了额外用量额度时才有效。** 基础 Max 计划额度（Claude Code 默认包含的用量）不会被 Hermes 消耗——只有您额外添加的超额/超量额度才会被消耗。Claude Pro 订阅者无法使用此路径。

如果您没有 Max + 额外额度，请改用 `ANTHROPIC_API_KEY`——请求将按 Token 计费，费用计入该密钥所属的组织（标准 API 定价，独立于任何 Claude 订阅）。
:::

```bash
# 使用 API 密钥（按 Token 计费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 首选：通过 `hermes model` 进行身份验证
# 当可用时，Hermes 将直接使用 Claude Code 的凭据存储
hermes model

# 使用 setup-token 手动覆盖（备用 / 旧版方法）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth token
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果您已使用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```

当您通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自身的凭据存储，而不是将 Token 复制到 `~/.hermes/.env`。这确保了可刷新的 Claude 凭据保持可刷新状态。

或者永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写形式使用。
:::

### GitHub Copilot

Hermes 将 GitHub Copilot 作为一等提供商支持，提供两种模式：

**`copilot` — 直接 Copilot API**（推荐）。使用您的 GitHub Copilot 订阅，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 和其他模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**身份验证选项**（按此顺序检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果未找到 Token，`hermes model` 会提供 **OAuth 设备码登录**——与 Copilot CLI 和 opencode 使用的流程相同。

:::warning Token 类型
Copilot API **不**支持经典的个人访问令牌（`ghp_*`）。支持的 Token 类型：

| 类型 | 前缀 | 如何获取 |
|------|--------|------------|
| OAuth token | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT | `github_pat_` | GitHub 设置 → 开发者设置 → 细粒度令牌（需要 **Copilot Requests** 权限） |
| GitHub App token | `ghu_` | 通过 GitHub App 安装获取 |

如果您的 `gh auth token` 返回一个 `ghp_*` Token，请改用 `hermes model` 通过 OAuth 进行身份验证。
:::
:::info Hermes 中的 Copilot 认证行为
Hermes 将支持的 GitHub Token（`gho_*`、`github_pat_*` 或 `ghu_*`）直接发送到 `api.githubcopilot.com`，并包含 Copilot 特定的请求头（`Editor-Version`、`Copilot-Integration-Id`、`Openai-Intent`、`x-initiator`）。

当收到 HTTP 401 响应时，Hermes 现在会在回退前执行一次凭据恢复：

1. 通过正常的优先级链重新解析 Token（`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `gh auth token`）
2. 使用刷新的请求头重建共享的 OpenAI 客户端
3. 重试请求一次

一些较旧的社区代理使用 `api.github.com/copilot_internal/v2/token` 交换流程。该端点可能对某些账户类型不可用（返回 404）。因此，Hermes 将直接使用 Token 认证作为主要路径，并依赖运行时的凭据刷新和重试机制来确保鲁棒性。
:::

**API 路由**：GPT-5+ 模型（除了 `gpt-5-mini`）自动使用 Responses API。所有其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions API。模型从实时的 Copilot 目录中自动检测。

**`copilot-acp` — Copilot ACP Agent 后端**。将本地的 Copilot CLI 作为子进程启动：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 GitHub Copilot CLI 在 PATH 中，并且存在现有的 `copilot login` 会话
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 描述 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub Token（最高优先级） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制文件路径（默认：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认：`--acp --stdio`） |

### 原生 API 密钥提供商

这些提供商具有内置支持，并拥有专用的提供商 ID。设置 API 密钥并使用 `--provider` 进行选择：

```bash
# z.ai / 智谱 AI GLM
hermes chat --provider zai --model glm-5
# 需要：在 ~/.hermes/.env 中设置 GLM_API_KEY

# Kimi / 月之暗面 AI（国际版：api.moonshot.ai）
hermes chat --provider kimi-coding --model kimi-for-coding
# 需要：在 ~/.hermes/.env 中设置 KIMI_API_KEY

# Kimi / 月之暗面 AI（中国版：api.moonshot.cn）
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# 需要：在 ~/.hermes/.env 中设置 KIMI_CN_API_KEY

# MiniMax（全球端点）
hermes chat --provider minimax --model MiniMax-M2.7
# 需要：在 ~/.hermes/.env 中设置 MINIMAX_API_KEY

# MiniMax（中国端点）
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要：在 ~/.hermes/.env 中设置 MINIMAX_CN_API_KEY

# 阿里云 / 灵积（通义千问模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：在 ~/.hermes/.env 中设置 DASHSCOPE_API_KEY

# 小米 MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# 需要：在 ~/.hermes/.env 中设置 XIAOMI_API_KEY

# 腾讯 TokenHub（Hy3 预览版）
hermes chat --provider tencent-tokenhub --model hy3-preview
# 需要：在 ~/.hermes/.env 中设置 TOKENHUB_API_KEY

# Arcee AI（Trinity 模型）
hermes chat --provider arcee --model trinity-large-thinking
# 需要：在 ~/.hermes/.env 中设置 ARCEEAI_API_KEY

# GMI Cloud
# 使用 GMI 的 /v1/models 端点返回的确切模型 ID。
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# 需要：在 ~/.hermes/.env 中设置 GMI_API_KEY
```

或者在 `config.yaml` 中永久设置提供商：
```yaml
model:
  provider: "gmi"
  default: "zai-org/GLM-5.1-FP8"
```

基础 URL 可以通过环境变量 `GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL`、`XIAOMI_BASE_URL`、`GMI_BASE_URL` 或 `TOKENHUB_BASE_URL` 进行覆盖。

:::note Z.AI 端点自动检测
当使用 Z.AI / GLM 提供商时，Hermes 会自动探测多个端点（全球版、中国版、编程版变体）以找到接受您 API 密钥的端点。您无需手动设置 `GLM_BASE_URL` —— 可用的端点会被自动检测并缓存。
:::

### xAI (Grok) — Responses API + 提示词缓存

xAI 通过 Responses API（`codex_responses` 传输）连接，以在 Grok 4 模型上自动支持推理 —— 无需 `reasoning_effort` 参数，服务器默认进行推理。在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，并在 `hermes model` 中选择 xAI，或者使用快捷方式 `/model grok-4-1-fast-reasoning` 输入 `grok`。

当使用 xAI 作为提供商时（任何包含 `x.ai` 的基础 URL），Hermes 会自动启用提示词缓存，方法是在每个 API 请求中发送 `x-grok-conv-id` 请求头。这会将请求路由到同一会话内的同一台服务器，允许 xAI 的基础设施重用缓存的系统提示词和对话历史记录。

无需配置 —— 当检测到 xAI 端点且会话 ID 可用时，缓存会自动激活。这减少了多轮对话的延迟和成本。

xAI 还提供了一个专用的 TTS 端点（`/v1/tts`）。在 `hermes tools` → 语音与 TTS 中选择 **xAI TTS**，或查看 [语音与 TTS](../user-guide/features/tts.md#text-to-speech) 页面了解配置。

### Ollama Cloud — 托管的 Ollama 模型，OAuth + API 密钥

[Ollama Cloud](https://ollama.com/cloud) 托管与本地 Ollama 相同的开源权重模型目录，但无需 GPU 要求。在 `hermes model` 中将其选为 **Ollama Cloud**，从 [ollama.com/settings/keys](https://ollama.com/settings/keys) 粘贴您的 API 密钥，Hermes 会自动发现可用模型。

```bash
hermes model
# → 选择 "Ollama Cloud"
# → 粘贴您的 OLLAMA_API_KEY
# → 从发现的模型中选择（gpt-oss:120b, glm-4.6:cloud, qwen3-coder:480b-cloud 等）
```

或者直接在 `config.yaml` 中配置：
```yaml
model:
  provider: "ollama-cloud"
  default: "gpt-oss:120b"
```

模型目录从 `ollama.com/v1/models` 动态获取，并缓存一小时。`model:tag` 表示法（例如 `qwen3-coder:480b-cloud`）通过规范化得以保留 —— 不要使用连字符。

:::tip Ollama Cloud 与本地 Ollama 对比
两者都使用相同的 OpenAI 兼容 API。Cloud 是原生提供商（`--provider ollama-cloud`，`OLLAMA_API_KEY`）；本地 Ollama 通过自定义端点流程访问（基础 URL `http://localhost:11434/v1`，无需密钥）。对于无法在本地运行的大型模型，请使用 Cloud；对于隐私或离线工作，请使用本地。
:::
### AWS Bedrock

通过 AWS Bedrock 使用 Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 及其他模型。使用 AWS SDK (`boto3`) 凭证链——无需 API 密钥，只需标准的 AWS 认证。

```bash
# 最简单的方式 —— 使用 ~/.aws/credentials 中的命名配置文件
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# 或者使用明确的环境变量
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6
```

或者在 `config.yaml` 中永久配置：
```yaml
model:
  provider: "bedrock"
  default: "us.anthropic.claude-sonnet-4-6"
bedrock:
  region: "us-east-1"          # 或者设置 AWS_REGION
  # profile: "myprofile"       # 或者设置 AWS_PROFILE
  # discovery: true            # 从 IAM 自动发现区域
  # guardrail:                 # 可选的 Bedrock Guardrails
  #   id: "your-guardrail-id"
  #   version: "DRAFT"
```

认证使用标准的 boto3 链：明确的 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`、来自 `~/.aws/credentials` 的 `AWS_PROFILE`、EC2/ECS/Lambda 上的 IAM 角色、IMDS 或 SSO。如果您已经通过 AWS CLI 认证，则不需要环境变量。

Bedrock 底层使用 **Converse API**——请求被转换为 Bedrock 的模型无关格式，因此相同的配置适用于 Claude、Nova、DeepSeek 和 Llama 模型。仅当您调用非默认的区域端点时才需要设置 `BEDROCK_BASE_URL`。

有关 IAM 设置、区域选择和跨区域推理的详细指南，请参阅 [AWS Bedrock 指南](/docs/guides/aws-bedrock)。

### Qwen Portal (OAuth)

阿里巴巴的 Qwen Portal，支持基于浏览器的 OAuth 登录。在 `hermes model` 中选择 **Qwen OAuth (Portal)**，通过浏览器登录，Hermes 将持久化刷新令牌。

```bash
hermes model
# → 选择 "Qwen OAuth (Portal)"
# → 浏览器打开；使用您的阿里巴巴账户登录
# → 确认 —— 凭证保存到 ~/.hermes/auth.json

hermes chat   # 使用 portal.qwen.ai/v1 端点
```

或者在 `config.yaml` 中配置：
```yaml
model:
  provider: "qwen-oauth"
  default: "qwen3-coder-plus"
```

仅当门户端点变更时才需要设置 `HERMES_QWEN_BASE_URL`（默认：`https://portal.qwen.ai/v1`）。

:::tip Qwen OAuth 与 DashScope (Alibaba)
`qwen-oauth` 使用面向消费者的 Qwen Portal 进行 OAuth 登录——适合个人用户。`alibaba` 提供商使用 DashScope 的企业 API 和 `DASHSCOPE_API_KEY`——适合编程/生产工作负载。两者都路由到 Qwen 系列模型，但位于不同的端点。
:::

### Alibaba Coding Plan

如果您订阅了阿里巴巴的 **Coding Plan**（一个独立于标准 DashScope API 访问的定价 SKU），Hermes 将其作为一个独立的一级提供商暴露：`alibaba-coding-plan`。端点：`https://coding-intl.dashscope.aliyuncs.com/v1`。它与常规的 `alibaba` 提供商一样是 OpenAI 兼容的，但具有不同的基础 URL 和计费面。

```yaml
model:
  provider: alibaba_coding     # alibaba-coding-plan 的别名
  model: qwen3-coder-plus
```

或者从 CLI 使用：

```bash
hermes chat --provider alibaba_coding --model qwen3-coder-plus
```

`alibaba_coding` 使用与您的 `alibaba` 条目相同的 `DASHSCOPE_API_KEY`——无需单独的密钥，只需不同的路由目标。在此提供商注册之前，在 `config.yaml` 中设置 `provider: alibaba_coding` 的用户会静默地回退到 OpenRouter 路由。

### MiniMax (OAuth)

通过浏览器 OAuth 登录使用 MiniMax-M2.7——无需 API 密钥。在 `hermes model` 中选择 **MiniMax (OAuth)**，通过浏览器登录，Hermes 将持久化访问令牌和刷新令牌。底层使用 Anthropic Messages 兼容的端点 (`/anthropic`)。

```bash
hermes model
# → 选择 "MiniMax (OAuth)"
# → 浏览器打开；使用您的 MiniMax 账户登录（全球或中国区域）
# → 确认 —— 凭证保存到 ~/.hermes/auth.json

hermes chat   # 使用 api.minimax.io/anthropic 端点
```

或者在 `config.yaml` 中配置：
```yaml
model:
  provider: "minimax-oauth"
  default: "MiniMax-M2.7"
```

支持的模型：`MiniMax-M2.7`（主模型）和 `MiniMax-M2.7-highspeed`（配置为默认辅助模型）。OAuth 路径忽略 `MINIMAX_API_KEY` / `MINIMAX_BASE_URL`。

:::tip MiniMax OAuth 与 API 密钥
`minimax-oauth` 使用 MiniMax 面向消费者的门户进行 OAuth 登录——无需设置计费。`minimax` 和 `minimax-cn` 提供商使用 `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY`——用于编程访问。完整指南请参阅 [MiniMax OAuth 指南](/docs/guides/minimax-oauth)。
:::

### NVIDIA NIM

通过 [build.nvidia.com](https://build.nvidia.com)（免费 API 密钥）或本地 NIM 端点使用 Nemotron 和其他开源模型。

```bash
# 云端 (build.nvidia.com)
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# 要求：在 ~/.hermes/.env 中设置 NVIDIA_API_KEY

# 本地 NIM 端点 —— 覆盖基础 URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```

:::tip 本地 NIM
对于本地部署（DGX Spark、本地 GPU），设置 `NVIDIA_BASE_URL=http://localhost:8000/v1`。NIM 暴露与 build.nvidia.com 相同的 OpenAI 兼容的聊天补全 API，因此在云端和本地之间切换只需更改一行环境变量。
:::

### Hugging Face Inference Providers

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点 (`router.huggingface.co/v1`) 路由到 20 多个开源模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并具有自动故障转移功能。

```bash
# 使用任何可用模型
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# 要求：在 ~/.hermes/.env 中设置 HF_TOKEN

# 短别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3-235B-A22B-Thinking-2507"
```
在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的 Token — 请确保启用 "Make calls to Inference Providers" 权限。包含免费套餐（每月 $0.10 额度，提供商费率无加价）。

你可以在模型名称后附加路由后缀：`:fastest`（默认）、`:cheapest` 或 `:provider_name` 以强制使用特定后端。

可以通过 `HF_BASE_URL` 覆盖基础 URL。

## 自定义与自托管 LLM 提供商

Hermes Agent 可与**任何 OpenAI 兼容的 API 端点**配合使用。如果服务器实现了 `/v1/chat/completions`，你就可以将 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器或任何第三方 API。

### 通用设置

配置自定义端点的三种方式：

**交互式设置（推荐）：**
```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入：API 基础 URL、API 密钥、模型名称
```

**手动配置 (`config.yaml`):**
```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  provider: custom
  base_url: http://localhost:8000/v1
  api_key: your-key-or-leave-empty-for-local
```

:::warning 遗留环境变量
`.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 已**移除**。Hermes 的任何部分都不会读取它们 — `config.yaml` 是模型和端点配置的唯一真实来源。如果你的 `.env` 中有过时的条目，它们将在下一次运行 `hermes setup` 或配置迁移时自动清除。请使用 `hermes model` 或直接编辑 `config.yaml`。
:::

两种方法都会将配置持久化到 `config.yaml`，该文件是模型、提供商和基础 URL 的真实来源。

### 使用 `/model` 切换模型

:::warning hermes model 与 /model
**`hermes model`**（从终端运行，在任何聊天会话之外）是**完整的提供商设置向导**。用它来添加新提供商、运行 OAuth 流程、输入 API 密钥以及配置自定义端点。

**`/model`**（在活跃的 Hermes 聊天会话中键入）只能**在你已设置的提供商和模型之间切换**。它不能添加新提供商、运行 OAuth 或提示输入 API 密钥。如果你只配置了一个提供商（例如 OpenRouter），`/model` 将只显示该提供商的模型。

**要添加新提供商：** 退出你的会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，设置新提供商，然后开始一个新会话。
:::

一旦你配置了至少一个自定义端点，就可以在会话中途切换模型：

```
/model custom:qwen-2.5          # 切换到你的自定义端点上的一个模型
/model custom                    # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切换回云提供商
```

如果你配置了**命名的自定义提供商**（见下文），请使用三重语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供商和模型 qwen-2.5
/model custom:work:llama3       # 使用名为 "work" 的自定义提供商和模型 llama3
```

切换提供商时，Hermes 会将基础 URL 和提供商持久化到配置中，以便更改在重启后仍然有效。当从自定义端点切换到内置提供商时，过时的基础 URL 会自动清除。

:::tip
`/model custom`（裸命令，无模型名称）会查询你端点的 `/models` API，如果恰好加载了一个模型，则自动选择它。对于运行单个模型的本地服务器很有用。
:::

以下所有内容都遵循相同的模式 — 只需更改 URL、密钥和模型名称。

---

### Ollama — 本地模型，零配置

[Ollama](https://ollama.com/) 通过一个命令在本地运行开源模型。最适合：快速本地实验、隐私敏感的工作、离线使用。通过 OpenAI 兼容的 API 支持工具调用。

```bash
# 安装并运行一个模型
ollama pull qwen2.5-coder:32b
ollama serve   # 在端口 11434 启动
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:11434/v1
# 跳过 API 密钥（Ollama 不需要）
# 输入模型名称（例如 qwen2.5-coder:32b）
```

或者直接配置 `config.yaml`：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768   # 参见下面的警告
```

:::caution Ollama 默认使用非常低的上下文长度
Ollama 默认**不**使用模型的完整上下文窗口。根据你的 VRAM，默认值为：

| 可用 VRAM | 默认上下文 |
|----------------|----------------|
| 小于 24 GB | **4,096 Token** |
| 24–48 GB | 32,768 Token |
| 48+ GB | 256,000 Token |

对于使用工具的 Agent，**你至少需要 16k–32k 的上下文**。在 4k 的情况下，仅系统提示词 + 工具模式就可能填满窗口，没有空间进行对话。

**如何增加它**（选择一种）：

```bash
# 选项 1：通过环境变量设置服务器范围（推荐）
OLLAMA_CONTEXT_LENGTH=32768 ollama serve

# 选项 2：对于 systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加：Environment="OLLAMA_CONTEXT_LENGTH=32768"
# 然后：sudo systemctl daemon-reload && sudo systemctl restart ollama

# 选项 3：将其烘焙到自定义模型中（每个模型持久化）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 32768" > Modelfile
ollama create qwen2.5-coder-32k -f Modelfile
```

**你无法通过 OpenAI 兼容的 API** (`/v1/chat/completions`) 设置上下文长度。它必须在服务器端或通过 Modelfile 配置。这是将 Ollama 与 Hermes 等工具集成时最常见的困惑来源。
:::

**验证你的上下文设置是否正确：**

```bash
ollama ps
# 查看 CONTEXT 列 — 它应该显示你配置的值
```

:::tip
使用 `ollama list` 列出可用模型。使用 `ollama pull <model>` 从 [Ollama 库](https://ollama.com/library) 拉取任何模型。Ollama 自动处理 GPU 卸载 — 大多数设置无需配置。
:::

---

### vLLM — 高性能 GPU 推理

[vLLM](https://docs.vllm.ai/) 是生产级 LLM 服务的标准。最适合：GPU 硬件上的最大吞吐量、服务大型模型、连续批处理。
```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --max-model-len 65536 \
  --tensor-parallel-size 2 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:8000/v1
# 跳过 API 密钥（如果使用 --api-key 配置了 vLLM，则输入一个）
# 输入模型名称: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认读取模型的 `max_position_embeddings`。如果该值超过你的 GPU 内存，它会报错并要求你将 `--max-model-len` 设置得更低。你也可以使用 `--max-model-len auto` 来自动寻找适合的最大值。设置 `--gpu-memory-utilization 0.95`（默认为 0.9）以将更多上下文挤入 VRAM。

**工具调用需要显式标志：**

| 标志 | 用途 |
|------|---------|
| `--enable-auto-tool-choice` | 为 `tool_choice: "auto"`（Hermes 中的默认值）所必需 |
| `--tool-call-parser <name>` | 模型工具调用格式的解析器 |

支持的解析器：`hermes`（Qwen 2.5, Hermes 2/3）、`llama3_json`（Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。没有这些标志，工具调用将无法工作——模型会将工具调用作为文本输出。

:::tip
vLLM 支持人类可读的大小：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。
:::

---

### SGLang — 使用 RadixAttention 的快速服务

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，具有用于 KV 缓存重用的 RadixAttention。最适合：多轮对话（前缀缓存）、约束解码、结构化输出。

```bash
pip install "sglang[all]"
python -m sglang.launch_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 30000 \
  --context-length 65536 \
  --tp 2 \
  --tool-call-parser qwen
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:30000/v1
# 输入模型名称: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** SGLang 默认从模型的配置中读取。使用 `--context-length` 来覆盖。如果你需要超过模型声明的最大值，请设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用：** 使用 `--tool-call-parser` 并为你模型系列选择合适的解析器：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。没有这个标志，工具调用将以纯文本形式返回。

:::caution SGLang 默认最大输出 Token 数为 128
如果响应看起来被截断，请在请求中添加 `max_tokens` 或在服务器上设置 `--default-max-tokens`。如果请求中未指定，SGLang 的默认值仅为每个响应 128 个 Token。
:::

---

### llama.cpp / llama-server — CPU 和 Metal 推理

[llama.cpp](https://github.com/ggml-org/llama.cpp) 在 CPU、Apple Silicon（Metal）和消费级 GPU 上运行量化模型。最适合：在没有数据中心 GPU 的情况下运行模型、Mac 用户、边缘部署。

```bash
# 构建并启动 llama-server
cmake -B build && cmake --build build --config Release
./build/bin/llama-server \
  --jinja -fa \
  -c 32768 \
  -ngl 99 \
  -m models/qwen2.5-coder-32b-instruct-Q4_K_M.gguf \
  --port 8080 --host 0.0.0.0
```

**上下文长度（`-c`）：** 最近的构建默认值为 `0`，这会从 GGUF 元数据中读取模型的训练上下文。对于具有 128k+ 训练上下文的模型，尝试分配完整的 KV 缓存可能会导致内存不足（OOM）。将 `-c` 显式设置为你需要的值（对于 Agent 使用，32k–64k 是一个不错的范围）。如果使用并行槽位（`-np`），总上下文将在槽位之间分配——使用 `-c 32768 -np 4` 时，每个槽位仅获得 8k。

然后配置 Hermes 指向它：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:8080/v1
# 跳过 API 密钥（本地服务器不需要）
# 输入模型名称——或者留空以自动检测（如果只加载了一个模型）
```

这会将端点保存到 `config.yaml`，以便在会话之间持久化。

:::caution 工具调用需要 `--jinja`
没有 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型将尝试通过在响应文本中写入 JSON 来调用工具，但 Hermes 不会将其识别为工具调用——你会看到像 `{"name": "web_search", ...}` 这样的原始 JSON 被打印为消息，而不是实际的搜索。

原生工具调用支持（最佳性能）：Llama 3.x、Qwen 2.5（包括 Coder）、Hermes 2/3、Mistral、DeepSeek、Functionary。所有其他模型使用一个通用的处理程序，可以工作但效率可能较低。完整列表请参阅 [llama.cpp 函数调用文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

你可以通过检查 `http://localhost:8080/props` 来验证工具支持是否激活——`chat_template` 字段应该存在。
:::

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化提供了质量与内存使用之间的最佳平衡。
:::

---

### LM Studio — 带有本地模型的桌面应用程序

[LM Studio](https://lmstudio.ai/) 是一个用于通过 GUI 运行本地模型的桌面应用程序。最适合：喜欢可视化界面的用户、快速模型测试、macOS/Windows/Linux 上的开发者。

从 LM Studio 应用程序启动服务器（开发者选项卡 → 启动服务器），或使用 CLI：

```bash
lms server start                        # 在端口 1234 上启动
lms load qwen2.5-coder --context-length 32768
```

然后配置 Hermes：

```bash
hermes model
# 选择 "LM Studio"
# 按 Enter 键使用 http://localhost:1234/v1
# 选择一个已发现的模型
# 如果启用了 LM Studio 服务器身份验证，请在提示时输入 LM_API_KEY
```

Hermes 将自动加载一个具有 64K 上下文长度的 LM Studio 模型

要在 LM Studio 中更改上下文长度：

1.  单击模型选择器旁边的齿轮图标
2.  将"上下文长度"设置为至少 64000 以获得流畅的体验
3.  重新加载模型以使更改生效
4.  如果你的机器无法容纳 64000，请考虑使用具有更大上下文长度的较小模型。
或者，使用 CLI：`lms load model-name --context-length 64000`

你可以使用 CLI 来估算模型是否能容纳：`lms load model-name --context-length 64000 --estimate-only`

要设置持久的每个模型默认值：转到“我的模型”标签页 → 点击模型上的齿轮图标 → 设置上下文大小。
:::

**工具调用：** 自 LM Studio 0.3.6 版本起支持。具有原生工具调用训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会被自动检测并显示工具徽章。其他模型使用通用的后备方案，可能不太可靠。

---

### WSL2 网络（Windows 用户）

由于 Hermes Agent 需要 Unix 环境，Windows 用户在 WSL2 内运行它。如果你的模型服务器（Ollama、LM Studio 等）运行在 **Windows 主机**上，你需要桥接网络鸿沟——WSL2 使用具有自己子网的虚拟网络适配器，因此 WSL2 内的 `localhost` 指的是 Linux 虚拟机，**而不是** Windows 主机。

:::tip 两者都在 WSL2 中？没问题。
如果你的模型服务器也运行在 WSL2 内（vLLM、SGLang 和 llama-server 常见），`localhost` 会按预期工作——它们共享相同的网络命名空间。跳过本节。
:::

#### 选项 1：镜像网络模式（推荐）

在 **Windows 11 22H2+** 上可用，镜像模式使 `localhost` 在 Windows 和 WSL2 之间双向工作——最简单的修复方法。

1.  创建或编辑 `%USERPROFILE%\.wslconfig`（例如，`C:\Users\YourName\.wslconfig`）：
    ```ini
    [wsl2]
    networkingMode=mirrored
    ```

2.  从 PowerShell 重启 WSL：
    ```powershell
    wsl --shutdown
    ```

3.  重新打开你的 WSL2 终端。`localhost` 现在可以访问 Windows 服务：
    ```bash
    curl http://localhost:11434/v1/models   # Windows 上的 Ollama — 有效
    ```

:::note Hyper-V 防火墙
在某些 Windows 11 版本上，Hyper-V 防火墙默认会阻止镜像连接。如果在启用镜像模式后 `localhost` 仍然无效，请在 **管理员 PowerShell** 中运行此命令：
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```
:::

#### 选项 2：使用 Windows 主机 IP（Windows 10 / 旧版本）

如果你无法使用镜像模式，请从 WSL2 内部找到 Windows 主机 IP，并使用它代替 `localhost`：

```bash
# 获取 Windows 主机 IP（WSL2 虚拟网络的默认网关）
ip route show | grep -i default | awk '{ print $3 }'
# 示例输出：172.29.192.1
```

在你的 Hermes 配置中使用该 IP：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://172.29.192.1:11434/v1   # Windows 主机 IP，不是 localhost
```

:::tip 动态助手
主机 IP 可能在 WSL2 重启后改变。你可以在 shell 中动态获取它：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows host at: $WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # 测试 Ollama
```

或者使用你机器的 mDNS 名称（需要在 WSL2 中安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

#### 服务器绑定地址（NAT 模式必需）

如果你使用 **选项 2**（使用主机 IP 的 NAT 模式），Windows 上的模型服务器必须接受来自 `127.0.0.1` 之外的连接。默认情况下，大多数服务器只监听 localhost——NAT 模式下的 WSL2 连接来自不同的虚拟子网，将被拒绝。在镜像模式下，`localhost` 直接映射，因此默认的 `127.0.0.1` 绑定工作正常。

| 服务器 | 默认绑定 | 如何修复 |
|--------|-------------|------------|
| **Ollama** | `127.0.0.1` | 在启动 Ollama 之前设置环境变量 `OLLAMA_HOST=0.0.0.0`（Windows 系统设置 → 环境变量，或编辑 Ollama 服务） |
| **LM Studio** | `127.0.0.1` | 在开发者标签页 → 服务器设置中启用 **"Serve on Network"** |
| **llama-server** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
| **vLLM** | `0.0.0.0` | 默认已绑定到所有接口 |
| **SGLang** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |

**Windows 上的 Ollama（详细）：** Ollama 作为 Windows 服务运行。要设置 `OLLAMA_HOST`：
1.  打开 **系统属性** → **环境变量**
2.  添加一个新的 **系统变量**：`OLLAMA_HOST` = `0.0.0.0`
3.  重启 Ollama 服务（或重启电脑）

#### Windows 防火墙

Windows 防火墙将 WSL2 视为一个独立的网络（在 NAT 和镜像模式下都是如此）。如果按照上述步骤后连接仍然失败，请为你的模型服务器端口添加防火墙规则：

```powershell
# 在管理员 PowerShell 中运行 — 将 PORT 替换为你的服务器端口
New-NetFirewallRule -DisplayName "Allow WSL2 to Model Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常见端口：Ollama `11434`、vLLM `8000`、SGLang `30000`、llama-server `8080`、LM Studio `1234`。

#### 快速验证

从 WSL2 内部测试是否可以访问你的模型服务器：

```bash
# 将 URL 替换为你的服务器地址和端口
curl http://localhost:11434/v1/models          # 镜像模式
curl http://172.29.192.1:11434/v1/models       # NAT 模式（使用你实际的主机 IP）
```

如果你收到列出模型的 JSON 响应，那就没问题。在 Hermes 配置中将相同的 URL 用作 `base_url`。

---

### 本地模型故障排除

这些问题在 Hermes 使用时影响**所有**本地推理服务器。

#### 从 WSL2 到 Windows 主机上的模型服务器出现“连接被拒绝”

如果你在 WSL2 内运行 Hermes，而你的模型服务器在 Windows 主机上，在 WSL2 默认的 NAT 网络模式下，`http://localhost:<port>` 将无法工作。请参阅上面的 [WSL2 网络](#wsl2-网络windows-用户) 部分以获取修复方法。

#### 工具调用显示为文本而不是执行

模型输出类似 `{"name": "web_search", "arguments": {...}}` 的内容作为消息，而不是实际调用工具。

**原因：** 你的服务器没有启用工具调用，或者模型不支持通过服务器的工具调用实现。

| 服务器 | 修复方法 |
|--------|-----|
| **llama.cpp** | 在启动命令中添加 `--jinja` |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` |
| **SGLang** | 添加 `--tool-call-parser qwen`（或适当的解析器） |
| **Ollama** | 工具调用默认启用——确保你的模型支持它（使用 `ollama show model-name` 检查） |
| **LM Studio** | 更新到 0.3.6+ 并使用具有原生工具支持的模型 |
#### 模型似乎忘记上下文或给出不连贯的回复

**原因：** 上下文窗口太小。当对话超过上下文限制时，大多数服务器会静默丢弃较早的消息。仅 Hermes 的系统提示词 + 工具模式就可能占用 4k–8k 个 Token。

**诊断：**

```bash
# 检查 Hermes 认为的上下文是什么
# 查看启动行："Context limit: X tokens"

# 检查你服务器的实际上下文
# Ollama: ollama ps (CONTEXT 列)
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: 检查启动参数中的 --max-model-len
```

**修复：** 为 Agent 使用设置至少 **32,768 个 Token** 的上下文。请参阅上面每个服务器的部分以了解具体的标志。

#### 启动时显示 "Context limit: 2048 tokens"

Hermes 会从你服务器的 `/v1/models` 端点自动检测上下文长度。如果服务器报告的值较低（或根本没有报告），Hermes 会使用模型声明的限制，这可能是错误的。

**修复：** 在 `config.yaml` 中显式设置：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768
```

#### 回复在句子中间被截断

**可能的原因：**
1.  **服务器上的输出上限 (`max_tokens`) 过低** — SGLang 默认每个回复为 128 个 Token。在服务器上设置 `--default-max-tokens` 或在 config.yaml 中配置 Hermes 的 `model.max_tokens`。注意：`max_tokens` 仅控制回复长度 — 它与你的对话历史能有多长（即 `context_length`）无关。
2.  **上下文耗尽** — 模型填满了其上下文窗口。增加 `model.context_length` 或在 Hermes 中启用[上下文压缩](/docs/user-guide/configuration#context-compression)。

---

### LiteLLM 代理 — 多提供商消息网关

[LiteLLM](https://docs.litellm.ai/) 是一个与 OpenAI 兼容的代理，它将 100 多个 LLM 提供商统一在一个 API 后面。最适合：无需更改配置即可在提供商之间切换、负载均衡、故障转移链、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或者使用配置文件管理多个模型：
litellm --config litellm_config.yaml --port 4000
```

然后使用 `hermes model` → 自定义端点 → `http://localhost:4000/v1` 配置 Hermes。

带故障转移的 `litellm_config.yaml` 示例：
```yaml
model_list:
  - model_name: "best"
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: sk-ant-...
  - model_name: "best"
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...
router_settings:
  routing_strategy: "latency-based-routing"
```

---

### ClawRouter — 成本优化路由

BlockRunAI 出品的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一个本地路由代理，它根据查询复杂度自动选择模型。它根据 14 个维度对请求进行分类，并将其路由到能够处理任务的最便宜的模型。支付通过 USDC 加密货币进行（无需 API 密钥）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 在端口 8402 上启动
```

然后使用 `hermes model` → 自定义端点 → `http://localhost:8402/v1` → 模型名称 `blockrun/auto` 配置 Hermes。

路由配置文件：
| 配置文件 | 策略 | 节省 |
|---------|----------|---------|
| `blockrun/auto` | 平衡质量/成本 | 74-100% |
| `blockrun/eco` | 尽可能便宜 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 不定 |

:::note
ClawRouter 需要在 Base 或 Solana 上有一个 USDC 资金的钱包用于支付。所有请求都通过 BlockRun 的后端 API 路由。运行 `npx @blockrun/clawrouter doctor` 来检查钱包状态。
:::

---

### 其他兼容的提供商

任何提供与 OpenAI 兼容 API 的服务都可以使用。一些流行的选项：

| 提供商 | 基础 URL | 备注 |
|----------|----------|-------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云端托管的开源模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 超快速推理 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速开源模型托管 |
| [GMI Cloud](https://www.gmicloud.ai/) | `https://api.gmi-serving.com/v1` | 托管的 OpenAI 兼容推理服务 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 晶圆级芯片推理 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业版 OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管，多模型 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 带有本地模型的桌面应用 |

使用 `hermes model` → 自定义端点或在 `config.yaml` 中配置以上任何服务：

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

---

### 上下文长度检测

:::note 两个设置，容易混淆
**`context_length`** 是**总上下文窗口** — 输入*和*输出 Token 的合并预算（例如，Claude Opus 4.6 为 200,000）。Hermes 使用它来决定何时压缩历史记录以及验证 API 请求。

**`model.max_tokens`** 是**输出上限** — 模型在*单个回复*中可以生成的最大 Token 数。它与你的对话历史能有多长无关。行业标准名称 `max_tokens` 是常见的混淆来源；Anthropic 的原生 API 后来为了清晰起见将其重命名为 `max_output_tokens`。

当自动检测得到的窗口大小错误时，设置 `context_length`。
仅当你需要限制单个回复的长度时，才设置 `model.max_tokens`。
:::

Hermes 使用多源解析链来检测你的模型和提供商的正确上下文窗口：
1. **配置覆盖** — `config.yaml` 中的 `model.context_length`（最高优先级）
2. **自定义提供商按模型设置** — `custom_providers[].models.<id>.context_length`
3. **持久化缓存** — 先前发现的值（重启后保留）
4. **端点 `/models`** — 查询你的服务器 API（本地/自定义端点）
5. **Anthropic `/v1/models`** — 查询 Anthropic 的 API 获取 `max_input_tokens`（仅限 API 密钥用户）
6. **OpenRouter API** — 来自 OpenRouter 的实时模型元数据
7. **Nous Portal** — 将 Nous 模型 ID 后缀与 OpenRouter 元数据进行匹配
8. **[models.dev](https://models.dev)** — 社区维护的注册表，包含 100+ 提供商、3800+ 模型的提供商特定上下文长度
9. **后备默认值** — 广泛的模型系列模式（默认 128K）

对于大多数设置，这可以开箱即用。系统是提供商感知的——同一个模型根据服务提供商的不同可能有不同的上下文限制（例如，`claude-opus-4.6` 在 Anthropic 直连上是 1M，但在 GitHub Copilot 上是 128K）。

要显式设置上下文长度，请在模型配置中添加 `context_length`：

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # tokens
```

对于自定义端点，你也可以按模型设置上下文长度：

```yaml
custom_providers:
  - name: "My Local LLM"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
      deepseek-r1:70b:
        context_length: 65536
```

`hermes model` 在配置自定义端点时会提示输入上下文长度。留空则进行自动检测。

:::tip 何时手动设置
- 你使用 Ollama 并设置了低于模型最大值的自定义 `num_ctx`
- 你想将上下文限制在模型最大值以下（例如，在 128k 模型上限制为 8k 以节省 VRAM）
- 你运行在未暴露 `/v1/models` 的代理之后
:::

---

### 命名的自定义提供商

如果你使用多个自定义端点（例如，本地开发服务器和远程 GPU 服务器），你可以在 `config.yaml` 中将它们定义为命名的自定义提供商：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # 省略 api_key — Hermes 对无需密钥的本地服务器使用 "no-key-required"
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    key_env: CORP_API_KEY
    api_mode: chat_completions   # 可选，根据 URL 自动检测
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    api_mode: anthropic_messages  # 用于 Anthropic 兼容的代理
```

在会话中使用三重语法在它们之间切换：

```
/model custom:local:qwen-2.5       # 使用 "local" 端点和 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点和 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```

你也可以从交互式 `hermes model` 菜单中选择命名的自定义提供商。

---

### 选择合适的设置

| 使用场景 | 推荐 |
|----------|-------------|
| **只想让它工作** | OpenRouter（默认）或 Nous Portal |
| **本地模型，易于设置** | Ollama |
| **生产环境 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或带 `sort: "price"` 的 OpenRouter |
| **最大隐私性** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | 带自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai (GLM)、Kimi/Moonshot (`kimi-coding` 或 `kimi-coding-cn`)、MiniMax、小米 MiMo 或腾讯 TokenHub（一流提供商） |

:::tip
你可以随时使用 `hermes model` 在提供商之间切换——无需重启。无论你使用哪个提供商，你的对话历史、记忆和技能都会保留。
:::

## 可选的 API 密钥

| 功能 | 提供商 | 环境变量 |
|---------|----------|--------------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral TTS + 语音转录 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| RL 训练 | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自托管 Firecrawl

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网页搜索和抓取。如果你更喜欢在本地运行 Firecrawl，你可以将 Hermes 指向一个自托管的实例。完整的设置说明请参见 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。

**你能得到什么：** 无需 API 密钥，无速率限制，无按页计费，完全的数据主权。

**你会失去什么：** 云版本使用 Firecrawl 专有的 "Fire-engine" 进行高级反机器人绕过（Cloudflare、CAPTCHA、IP 轮换）。自托管版本使用基本的 fetch + Playwright，因此一些受保护的站点可能会失败。搜索使用 DuckDuckGo 而不是 Google。

**设置步骤：**

1. 克隆并启动 Firecrawl Docker 堆栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL — 需要约 4-8 GB RAM）：
   ```bash
   git clone https://github.com/firecrawl/firecrawl
   cd firecrawl
   # 在 .env 中设置：USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
   docker compose up -d
   ```

2. 将 Hermes 指向你的实例（无需 API 密钥）：
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```
如果启用了身份验证，你也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由

使用 OpenRouter 时，你可以控制请求如何在不同提供商之间路由。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认）、"throughput" 或 "latency"
  # only: ["anthropic"]      # 仅使用这些提供商
  # ignore: ["deepinfra"]    # 跳过这些提供商
  # order: ["anthropic", "google"]  # 按此顺序尝试提供商
  # require_parameters: true  # 仅使用支持所有请求参数的提供商
  # data_collection: "deny"   # 排除可能存储/训练数据的提供商
```

**快捷方式：** 在任何模型名称后附加 `:nitro` 以进行吞吐量排序（例如，`anthropic/claude-sonnet-4:nitro`），或附加 `:floor` 以进行价格排序。

## 备用模型

配置一个备用 提供商:模型，当你的主模型失败（速率限制、服务器错误、身份验证失败）时，Hermes 会自动切换到它：

```yaml
fallback_model:
  provider: openrouter                    # 必需
  model: anthropic/claude-sonnet-4        # 必需
  # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
  # key_env: MY_CUSTOM_KEY               # 可选，自定义端点 API 密钥的环境变量名
```

激活后，备用模型会在会话中途切换模型和提供商，而不会丢失你的对话。每个会话**最多触发一次**。

支持的提供商：`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`ollama-cloud`、`bedrock`、`ai-gateway`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`tencent-tokenhub`、`custom`。

:::tip
备用模型配置**仅**通过 `config.yaml` 进行——没有相关的环境变量。有关其触发条件、支持的提供商以及其如何与辅助任务和委派交互的完整详细信息，请参阅[备用提供商](/docs/user-guide/features/fallback-providers)。
:::

---

## 另请参阅

- [配置](/docs/user-guide/configuration) — 通用配置（目录结构、配置优先级、终端后端、记忆、压缩等）
- [环境变量](/docs/reference/environment-variables) — 所有环境变量的完整参考