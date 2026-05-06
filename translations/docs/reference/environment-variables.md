---
sidebar_position: 2
title: "环境变量"
description: "Hermes Agent 使用的所有环境变量的完整参考"
---

# 环境变量参考

所有变量都应设置在 `~/.hermes/.env` 文件中。你也可以使用 `hermes config set VAR value` 来设置它们。

## LLM 提供商

| 变量 | 描述 |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥（推荐使用，灵活性高） |
| `OPENROUTER_BASE_URL` | 覆盖 OpenRouter 兼容的基础 URL |
| `HERMES_OPENROUTER_CACHE` | 启用 OpenRouter 响应缓存 (`1`/`true`/`yes`/`on`)。覆盖 config.yaml 中的 `openrouter.response_cache`。参见 [响应缓存](https://openrouter.ai/docs/guides/features/response-caching)。 |
| `HERMES_OPENROUTER_CACHE_TTL` | 缓存 TTL（生存时间），单位秒 (1-86400)。覆盖 config.yaml 中的 `openrouter.response_cache_ttl`。 |
| `NOUS_BASE_URL` | 覆盖 Nous Portal 基础 URL（很少需要；仅用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 直接覆盖 Nous 推理端点 |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway API 密钥 ([ai-gateway.vercel.sh](https://ai-gateway.vercel.sh)) |
| `AI_GATEWAY_BASE_URL` | 覆盖 AI Gateway 基础 URL（默认：`https://ai-gateway.vercel.sh/v1`) |
| `OPENAI_API_KEY` | 用于自定义 OpenAI 兼容端点的 API 密钥（与 `OPENAI_BASE_URL` 一起使用） |
| `OPENAI_BASE_URL` | 自定义端点的基础 URL（VLLM、SGLang 等） |
| `COPILOT_GITHUB_TOKEN` | Copilot API 的 GitHub Token — 第一优先级（OAuth `gho_*` 或细粒度 PAT `github_pat_*`；经典 PAT `ghp_*` **不支持**） |
| `GH_TOKEN` | GitHub Token — Copilot 的第二优先级（也用于 `gh` CLI） |
| `GITHUB_TOKEN` | GitHub Token — Copilot 的第三优先级 |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot ACP CLI 二进制文件路径（默认：`copilot`) |
| `COPILOT_CLI_PATH` | `HERMES_COPILOT_ACP_COMMAND` 的别名 |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 Copilot ACP 参数（默认：`--acp --stdio`) |
| `COPILOT_ACP_BASE_URL` | 覆盖 Copilot ACP 基础 URL |
| `GLM_API_KEY` | z.ai / 智谱AI GLM API 密钥 ([z.ai](https://z.ai)) |
| `ZAI_API_KEY` | `GLM_API_KEY` 的别名 |
| `Z_AI_API_KEY` | `GLM_API_KEY` 的别名 |
| `GLM_BASE_URL` | 覆盖 z.ai 基础 URL（默认：`https://api.z.ai/api/paas/v4`) |
| `KIMI_API_KEY` | Kimi / 月之暗面 AI API 密钥 ([moonshot.ai](https://platform.moonshot.ai)) |
| `KIMI_BASE_URL` | 覆盖 Kimi 基础 URL（默认：`https://api.moonshot.ai/v1`) |
| `KIMI_CN_API_KEY` | Kimi / 月之暗面中国区 API 密钥 ([moonshot.cn](https://platform.moonshot.cn)) |
| `ARCEEAI_API_KEY` | Arcee AI API 密钥 ([chat.arcee.ai](https://chat.arcee.ai/)) |
| `ARCEE_BASE_URL` | 覆盖 Arcee 基础 URL（默认：`https://api.arcee.ai/api/v1`) |
| `GMI_API_KEY` | GMI Cloud API 密钥 ([gmicloud.ai](https://www.gmicloud.ai/)) |
| `GMI_BASE_URL` | 覆盖 GMI Cloud 基础 URL（默认：`https://api.gmi-serving.com/v1`) |
| `MINIMAX_API_KEY` | MiniMax API 密钥 — 全球端点 ([minimax.io](https://www.minimax.io))。**不被 `minimax-oauth` 使用**（OAuth 路径使用浏览器登录）。 |
| `MINIMAX_BASE_URL` | 覆盖 MiniMax 基础 URL（默认：`https://api.minimax.io/anthropic` — Hermes 使用 MiniMax 的 Anthropic Messages 兼容端点）。**不被 `minimax-oauth` 使用**。 |
| `MINIMAX_CN_API_KEY` | MiniMax API 密钥 — 中国区端点 ([minimaxi.com](https://www.minimaxi.com))。**不被 `minimax-oauth` 使用**（OAuth 路径使用浏览器登录）。 |
| `MINIMAX_CN_BASE_URL` | 覆盖 MiniMax 中国区基础 URL（默认：`https://api.minimaxi.com/anthropic`）。**不被 `minimax-oauth` 使用**。 |
| `KILOCODE_API_KEY` | Kilo Code API 密钥 ([kilo.ai](https://kilo.ai)) |
| `KILOCODE_BASE_URL` | 覆盖 Kilo Code 基础 URL（默认：`https://api.kilo.ai/api/gateway`) |
| `XIAOMI_API_KEY` | 小米 MiMo API 密钥 ([platform.xiaomimimo.com](https://platform.xiaomimimo.com)) |
| `XIAOMI_BASE_URL` | 覆盖小米 MiMo 基础 URL（默认：`https://api.xiaomimimo.com/v1`) |
| `TOKENHUB_API_KEY` | 腾讯 TokenHub API 密钥 ([tokenhub.tencentmaas.com](https://tokenhub.tencentmaas.com)) |
| `TOKENHUB_BASE_URL` | 覆盖腾讯 TokenHub 基础 URL（默认：`https://tokenhub.tencentmaas.com/v1`) |
| `AZURE_FOUNDRY_API_KEY` | Azure AI Foundry / Azure OpenAI API 密钥 ([ai.azure.com](https://ai.azure.com/)) |
| `AZURE_FOUNDRY_BASE_URL` | Azure AI Foundry 端点 URL（例如，OpenAI 风格：`https://<resource>.openai.azure.com/openai/v1`，或 Anthropic 风格：`https://<resource>.services.ai.azure.com/anthropic`) |
| `AZURE_ANTHROPIC_KEY` | 用于 `provider: anthropic` + `base_url` 指向 Azure Foundry Claude 部署的 Azure Anthropic API 密钥（当同时配置了 Anthropic 和 Azure Anthropic 时，作为 `ANTHROPIC_API_KEY` 的替代方案） |
| `HF_TOKEN` | Hugging Face Token，用于推理提供商 ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)) |
| `HF_BASE_URL` | 覆盖 Hugging Face 基础 URL（默认：`https://router.huggingface.co/v1`) |
| `GOOGLE_API_KEY` | Google AI Studio API 密钥 ([aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)) |
| `GEMINI_API_KEY` | `GOOGLE_API_KEY` 的别名 |
| `GEMINI_BASE_URL` | 覆盖 Google AI Studio 基础 URL |
| `HERMES_GEMINI_CLIENT_ID` | `google-gemini-cli` PKCE 登录的 OAuth 客户端 ID（可选；默认为 Google 的公共 gemini-cli 客户端） |
| `HERMES_GEMINI_CLIENT_SECRET` | `google-gemini-cli` 的 OAuth 客户端密钥（可选） |
| `HERMES_GEMINI_PROJECT_ID` | 付费 Gemini 层级的 GCP 项目 ID（免费层级自动配置） |
| `ANTHROPIC_API_KEY` | Anthropic Console API 密钥 ([console.anthropic.com](https://console.anthropic.com/)) |
| `ANTHROPIC_TOKEN` | 手动或旧版 Anthropic OAuth/setup-token 覆盖 |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API 密钥，用于通义千问模型 ([modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)) |
| `DASHSCOPE_BASE_URL` | 自定义 DashScope 基础 URL（默认：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`；中国大陆地区使用 `https://dashscope.aliyuncs.com/compatible-mode/v1`) |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥，用于直接访问 DeepSeek ([platform.deepseek.com](https://platform.deepseek.com/api_keys)) |
| `DEEPSEEK_BASE_URL` | 自定义 DeepSeek API 基础 URL |
| `NVIDIA_API_KEY` | NVIDIA NIM API 密钥 — Nemotron 和开源模型 ([build.nvidia.com](https://build.nvidia.com)) |
| `NVIDIA_BASE_URL` | 覆盖 NVIDIA 基础 URL（默认：`https://integrate.api.nvidia.com/v1`；本地 NIM 端点设置为 `http://localhost:8000/v1`) |
| `GMI_API_KEY` | GMI Cloud API 密钥 — 开源和推理模型 ([inference.gmi.ai](https://inference.gmi.ai)) |
| `GMI_BASE_URL` | 覆盖 GMI Cloud 基础 URL（默认：`https://api.gmi.ai/v1`) |
| `STEPFUN_API_KEY` | StepFun API 密钥 — Step 系列模型 ([platform.stepfun.com](https://platform.stepfun.com)) |
| `STEPFUN_BASE_URL` | 覆盖 StepFun 基础 URL（默认：`https://api.stepfun.com/v1`) |
| `OLLAMA_API_KEY` | Ollama Cloud API 密钥 — 托管的 Ollama 目录，无需本地 GPU ([ollama.com/settings/keys](https://ollama.com/settings/keys)) |
| `OLLAMA_BASE_URL` | 覆盖 Ollama Cloud 基础 URL（默认：`https://ollama.com/v1`) |
| `XAI_API_KEY` | xAI (Grok) API 密钥，用于聊天 + TTS ([console.x.ai](https://console.x.ai/)) |
| `XAI_BASE_URL` | 覆盖 xAI 基础 URL（默认：`https://api.x.ai/v1`) |
| `MISTRAL_API_KEY` | Mistral API 密钥，用于 Voxtral TTS 和 Voxtral STT ([console.mistral.ai](https://console.mistral.ai)) |
| `AWS_REGION` | 用于 Bedrock 推理的 AWS 区域（例如 `us-east-1`、`eu-central-1`）。由 boto3 读取。 |
| `AWS_PROFILE` | 用于 Bedrock 身份验证的 AWS 命名配置文件（读取 `~/.aws/credentials`）。留空则使用默认的 boto3 凭据链。 |
| `BEDROCK_BASE_URL` | 覆盖 Bedrock 运行时基础 URL（默认：`https://bedrock-runtime.us-east-1.amazonaws.com`；通常留空，改用 `AWS_REGION`) |
| `HERMES_QWEN_BASE_URL` | Qwen Portal 基础 URL 覆盖（默认：`https://portal.qwen.ai/v1`) |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API 密钥 — 按需付费访问精选模型 ([opencode.ai](https://opencode.ai/auth)) |
| `OPENCODE_ZEN_BASE_URL` | 覆盖 OpenCode Zen 基础 URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API 密钥 — 每月 10 美元订阅，用于开源模型 ([opencode.ai](https://opencode.ai/auth)) |
| `OPENCODE_GO_BASE_URL` | 覆盖 OpenCode Go 基础 URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | 如果你手动导出了一个，则显式覆盖 Claude Code Token |
| `HERMES_MODEL` | 在进程级别覆盖模型名称（由 cron 调度器使用；正常使用建议用 `config.yaml`) |
| `VOICE_TOOLS_OPENAI_KEY` | 用于 OpenAI 语音转文本和文本转语音提供商的首选 OpenAI 密钥 |
| `HERMES_LOCAL_STT_COMMAND` | 可选的本地语音转文本命令模板。支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符 |
| `HERMES_LOCAL_STT_LANGUAGE` | 传递给 `HERMES_LOCAL_STT_COMMAND` 或自动检测的本地 `whisper` CLI 回退的默认语言（默认：`en`) |
| `HERMES_HOME` | 覆盖 Hermes 配置目录（默认：`~/.hermes`）。同时限定消息网关 PID 文件和 systemd 服务名称的范围，以便多个安装可以同时运行 |
| `HERMES_KANBAN_HOME` | 覆盖共享的 Hermes 根目录，该目录锚定看板（数据库 + 工作空间 + 工作日志）。回退到 `get_default_hermes_root()`（任何活动配置文件的父目录）。对测试和不寻常的部署有用 |
| `HERMES_KANBAN_BOARD` | 为此进程固定活动看板。优先级高于 `~/.hermes/kanban/current`；调度器将其注入工作子进程环境，因此工作进程物理上无法看到其他看板上的任务。默认为 `default`。Slug 验证：小写字母数字 + 连字符 + 下划线，1-64 个字符 |
| `HERMES_KANBAN_DB` | 直接固定看板数据库文件路径（最高优先级；高于 `HERMES_KANBAN_BOARD` 和 `HERMES_KANBAN_HOME`）。调度器将其注入工作子进程环境，以便配置文件工作进程汇聚到调度器的看板上 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 直接固定看板工作空间根目录（工作空间的最高优先级；高于 `HERMES_KANBAN_HOME`）。调度器将其注入工作子进程环境 |
## 提供商认证（OAuth）

对于原生的 Anthropic 认证，当 Claude Code 自身的凭证文件存在时，Hermes 优先使用它们，因为这些凭证可以自动刷新。**针对 Anthropic 的 OAuth 需要一个 Claude Max 计划并购买额外的使用额度** —— Hermes 会以 Claude Code 的身份路由请求，这只会从 Max 计划的额外/超额额度中扣除，而不是基础 Max 额度，并且在 Claude Pro 上无效。如果没有 Max 计划 + 额外额度，请改用 API 密钥。环境变量如 `ANTHROPIC_TOKEN` 作为手动覆盖仍然有用，但它们不再是 Claude Max 登录的首选方式。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_INFERENCE_PROVIDER` | 覆盖提供商选择：`auto`、`custom`、`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`huggingface`、`gemini`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`（浏览器 OAuth 登录 —— 无需 API 密钥；参见 [MiniMax OAuth 指南](../guides/minimax-oauth.md)）、`kilocode`、`xiaomi`、`arcee`、`gmi`、`stepfun`、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`google-gemini-cli`、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`ai-gateway`、`tencent-tokenhub`（默认：`auto`） |
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 重新签发 Agent 密钥前的最小 TTL（默认：1800 = 30分钟） |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭证/令牌流程的 HTTP 超时时间 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载转储到日志文件（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | 指向一个 JSON 文件的路径，该文件包含在 API 调用时注入的临时预填充消息 |
| `HERMES_TIMEZONE` | IANA 时区覆盖（例如 `America/New_York`） |

## 工具 API

| 变量 | 描述 |
|----------|-------------|
| `PARALLEL_API_KEY` | AI 原生网络搜索 ([parallel.ai](https://parallel.ai/)) |
| `FIRECRAWL_API_KEY` | 网络爬取和云浏览器 ([firecrawl.dev](https://firecrawl.dev/)) |
| `FIRECRAWL_API_URL` | 自定义 Firecrawl API 端点，用于自托管实例（可选） |
| `TAVILY_API_KEY` | Tavily API 密钥，用于 AI 原生网络搜索、提取和爬取 ([app.tavily.com](https://app.tavily.com/home)) |
| `TAVILY_BASE_URL` | 覆盖 Tavily API 端点。适用于企业代理和自托管的 Tavily 兼容搜索后端。模式与 `GROQ_BASE_URL` 相同。 |
| `EXA_API_KEY` | Exa API 密钥，用于 AI 原生网络搜索和内容 ([exa.ai](https://exa.ai/)) |
| `BROWSERBASE_API_KEY` | 浏览器自动化 ([browserbase.com](https://browserbase.com/)) |
| `BROWSERBASE_PROJECT_ID` | Browserbase 项目 ID |
| `BROWSER_USE_API_KEY` | Browser Use 云浏览器 API 密钥 ([browser-use.com](https://browser-use.com/)) |
| `FIRECRAWL_BROWSER_TTL` | Firecrawl 浏览器会话 TTL（秒）（默认：300） |
| `BROWSER_CDP_URL` | 本地浏览器的 Chrome DevTools Protocol URL（通过 `/browser connect` 设置，例如 `ws://localhost:9222`） |
| `CAMOFOX_URL` | Camofox 本地反检测浏览器 URL（默认：`http://localhost:9377`） |
| `BROWSER_INACTIVITY_TIMEOUT` | 浏览器会话不活动超时时间（秒） |
| `FAL_KEY` | 图像生成 ([fal.ai](https://fal.ai/)) |
| `GROQ_API_KEY` | Groq Whisper STT API 密钥 ([groq.com](https://groq.com/)) |
| `ELEVENLABS_API_KEY` | ElevenLabs 高级 TTS 语音 ([elevenlabs.io](https://elevenlabs.io/)) |
| `STT_GROQ_MODEL` | 覆盖 Groq STT 模型（默认：`whisper-large-v3-turbo`） |
| `GROQ_BASE_URL` | 覆盖 Groq OpenAI 兼容的 STT 端点 |
| `STT_OPENAI_MODEL` | 覆盖 OpenAI STT 模型（默认：`whisper-1`） |
| `STT_OPENAI_BASE_URL` | 覆盖 OpenAI 兼容的 STT 端点 |
| `GITHUB_TOKEN` | 用于技能中心的 GitHub 令牌（更高的 API 速率限制，技能发布） |
| `HONCHO_API_KEY` | 跨会话用户建模 ([honcho.dev](https://honcho.dev/)) |
| `HONCHO_BASE_URL` | 自托管 Honcho 实例的基础 URL（默认：Honcho 云）。本地实例不需要 API 密钥 |
| `HINDSIGHT_TIMEOUT` | Hindsight 记忆提供者 API 调用的超时时间（秒）（默认：`60`）。如果你的 Hindsight 实例在 `/sync` 或 `on_session_switch` 期间响应缓慢，并且在 `errors.log` 中看到超时，请增加此值。 |
| `SUPERMEMORY_API_KEY` | 具有个人资料回忆和会话摄取功能的语义长期记忆 ([supermemory.ai](https://supermemory.ai)) |
| `TINKER_API_KEY` | RL 训练 ([tinker-console.thinkingmachines.ai](https://tinker-console.thinkingmachines.ai/)) |
| `WANDB_API_KEY` | RL 训练指标 ([wandb.ai](https://wandb.ai/)) |
| `DAYTONA_API_KEY` | Daytona 云沙盒 ([daytona.io](https://daytona.io/)) |
| `VERCEL_TOKEN` | Vercel 沙盒访问令牌 ([vercel.com](https://vercel.com/)) |
| `VERCEL_PROJECT_ID` | Vercel 项目 ID（与 `VERCEL_TOKEN` 一起使用） |
| `VERCEL_TEAM_ID` | Vercel 团队 ID（与 `VERCEL_TOKEN` 一起使用） |
| `VERCEL_OIDC_TOKEN` | Vercel 短期 OIDC 令牌（仅限开发的替代方案） |

### Langfuse 可观测性

用于捆绑的 [`observability/langfuse`](/docs/user-guide/features/built-in-plugins#observabilitylangfuse) 插件的环境变量。通过 `hermes tools → Langfuse Observability` 或在 `~/.hermes/.env` 中手动设置这些变量。在它们生效之前，还必须启用该插件（`hermes plugins enable observability/langfuse`）。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_LANGFUSE_PUBLIC_KEY` | Langfuse 项目公钥 (`pk-lf-...`)。必需。 |
| `HERMES_LANGFUSE_SECRET_KEY` | Langfuse 项目密钥 (`sk-lf-...`)。必需。 |
| `HERMES_LANGFUSE_BASE_URL` | Langfuse 服务器 URL（默认：`https://cloud.langfuse.com`）。为自托管设置。 |
| `HERMES_LANGFUSE_ENV` | 跟踪记录上的环境标签（`production`、`staging`、…） |
| `HERMES_LANGFUSE_RELEASE` | 跟踪记录上的发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | SDK 采样率 0.0–1.0（默认：`1.0`） |
| `HERMES_LANGFUSE_MAX_CHARS` | 序列化负载的每字段截断长度（默认：`12000`） |
| `HERMES_LANGFUSE_DEBUG` | `true` 启用详细的插件日志记录到 `agent.log` |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | 标准 Langfuse SDK 名称。当等效的 `HERMES_LANGFUSE_*` 变量未设置时，作为后备方案接受。 |
### Nous 工具网关

这些变量为付费 Nous 订阅者或自托管网关部署配置[工具网关](/docs/user-guide/features/tool-gateway)。大多数用户无需设置这些——网关通过 `hermes model` 或 `hermes tools` 自动配置。

| 变量 | 描述 |
|----------|-------------|
| `TOOL_GATEWAY_DOMAIN` | 工具网关路由的基础域名（默认：`nousresearch.com`） |
| `TOOL_GATEWAY_SCHEME` | 网关 URL 的 HTTP 或 HTTPS 方案（默认：`https`） |
| `TOOL_GATEWAY_USER_TOKEN` | 工具网关的认证 Token（通常从 Nous 认证自动填充） |
| `FIRECRAWL_GATEWAY_URL` | 专门用于 Firecrawl 网关端点的覆盖 URL |

## 终端后端

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_ENV` | 后端：`local`、`docker`、`ssh`、`singularity`、`modal`、`daytona`、`vercel_sandbox` |
| `HERMES_DOCKER_BINARY` | 覆盖 Hermes 调用的容器二进制文件（例如 `podman`、`/usr/local/bin/docker`）。未设置时，Hermes 自动在 `PATH` 上发现 `docker` 或 `podman`。当两者都安装且你希望使用非默认项，或二进制文件位于 `PATH` 之外时需要。 |
| `TERMINAL_DOCKER_IMAGE` | Docker 镜像（默认：`nikolaik/python-nodejs:python3.11-nodejs20`） |
| `TERMINAL_DOCKER_FORWARD_ENV` | 要显式转发到 Docker 终端会话的环境变量名称的 JSON 数组。注意：技能声明的 `required_environment_variables` 会自动转发——你只需要为任何技能未声明的变量设置此项。 |
| `TERMINAL_DOCKER_VOLUMES` | 额外的 Docker 卷挂载（逗号分隔的 `host:container` 对） |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | 高级选择加入：将启动时的当前工作目录挂载到 Docker 的 `/workspace`（`true`/`false`，默认：`false`） |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity 镜像或 `.sif` 路径 |
| `TERMINAL_MODAL_IMAGE` | Modal 容器镜像 |
| `TERMINAL_DAYTONA_IMAGE` | Daytona 沙盒镜像 |
| `TERMINAL_VERCEL_RUNTIME` | Vercel 沙盒运行时（`node24`、`node22`、`python3.13`） |
| `TERMINAL_TIMEOUT` | 命令超时时间（秒） |
| `TERMINAL_LIFETIME_SECONDS` | 终端会话的最大生命周期（秒） |
| `TERMINAL_CWD` | 终端会话的工作目录（仅限网关/cron；CLI 使用启动目录） |
| `SUDO_PASSWORD` | 启用 sudo 而不需要交互式提示 |

对于云沙盒后端，持久性是面向文件系统的。`TERMINAL_LIFETIME_SECONDS` 控制 Hermes 何时清理空闲的终端会话，后续恢复可能会重新创建沙盒，而不是保持相同的活动进程运行。

## SSH 后端

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_SSH_HOST` | 远程服务器主机名 |
| `TERMINAL_SSH_USER` | SSH 用户名 |
| `TERMINAL_SSH_PORT` | SSH 端口（默认：22） |
| `TERMINAL_SSH_KEY` | 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 的持久化 shell（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

## 容器资源（Docker、Singularity、Modal、Daytona）

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_CONTAINER_CPU` | CPU 核心数（默认：1） |
| `TERMINAL_CONTAINER_MEMORY` | 内存大小（MB）（默认：5120） |
| `TERMINAL_CONTAINER_DISK` | 磁盘大小（MB）（默认：51200） |
| `TERMINAL_CONTAINER_PERSISTENT` | 跨会话持久化容器文件系统（默认：`true`） |
| `TERMINAL_SANDBOX_DIR` | 用于工作区和覆盖层的主机目录（默认：`~/.hermes/sandboxes/`） |

## 持久化 Shell

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_PERSISTENT_SHELL` | 为非本地后端启用持久化 shell（默认：`true`）。也可通过 config.yaml 中的 `terminal.persistent_shell` 设置 |
| `TERMINAL_LOCAL_PERSISTENT` | 为本地后端启用持久化 shell（默认：`false`） |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久化 shell（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

## 消息传递

| 变量 | 描述 |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人 Token（来自 @BotFather） |
| `TELEGRAM_ALLOWED_USERS` | 允许使用机器人的逗号分隔的用户 ID（适用于私聊、群组和论坛） |
| `TELEGRAM_GROUP_ALLOWED_USERS` | 仅在群组/论坛中授权的逗号分隔的发送者用户 ID（**不**授予私聊访问权限）。为向后兼容 #17686 之前的配置，仍接受以 `-` 开头的聊天 ID 形状的值作为聊天 ID，但会显示弃用警告。 |
| `TELEGRAM_GROUP_ALLOWED_CHATS` | 逗号分隔的群组/论坛聊天 ID；任何成员均被授权 |
| `TELEGRAM_HOME_CHANNEL` | 用于 cron 交付的默认 Telegram 聊天/频道 |
| `TELEGRAM_HOME_CHANNEL_NAME` | Telegram 主页频道的显示名称 |
| `TELEGRAM_WEBHOOK_URL` | Webhook 模式的公共 HTTPS URL（启用 webhook 而非轮询） |
| `TELEGRAM_WEBHOOK_PORT` | Webhook 服务器的本地监听端口（默认：`8443`） |
| `TELEGRAM_WEBHOOK_SECRET` | Telegram 在每个更新中回显用于验证的密钥 Token。**只要设置了 `TELEGRAM_WEBHOOK_URL` 就必需**——没有它网关将拒绝启动（GHSA-3vpc-7q5r-276h）。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_REACTIONS` | 在处理消息时启用表情符号反应（默认：`false`） |
| `TELEGRAM_REPLY_TO_MODE` | 回复引用行为：`off`、`first`（默认）或 `all`。匹配 Discord 模式。 |
| `TELEGRAM_IGNORED_THREADS` | 机器人永不响应的逗号分隔的 Telegram 论坛主题/线程 ID |
| `TELEGRAM_PROXY` | Telegram 连接的代理 URL——覆盖 `HTTPS_PROXY`。支持 `http://`、`https://`、`socks5://` |
| `DISCORD_BOT_TOKEN` | Discord 机器人 Token |
| `DISCORD_ALLOWED_USERS` | 允许使用机器人的逗号分隔的 Discord 用户 ID |
| `DISCORD_ALLOWED_ROLES` | 允许使用机器人的逗号分隔的 Discord 角色 ID（与 `DISCORD_ALLOWED_USERS` 为 OR 关系）。自动启用 Members 意图。在审核团队变动时很有用——角色授权会自动传播。 |
| `DISCORD_ALLOWED_CHANNELS` | 逗号分隔的 Discord 频道 ID。设置后，机器人仅在这些频道中响应（如果允许，还包括私聊）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。 |
| `DISCORD_PROXY` | Discord 连接的代理 URL——覆盖 `HTTPS_PROXY`。支持 `http://`、`https://`、`socks5://` |
| `DISCORD_HOME_CHANNEL` | 用于 cron 交付的默认 Discord 频道 |
| `DISCORD_HOME_CHANNEL_NAME` | Discord 主页频道的显示名称 |
| `DISCORD_COMMAND_SYNC_POLICY` | Discord 斜杠命令启动同步策略：`safe`（差异化和协调）、`bulk`（旧版 `tree.sync()`）或 `off` |
| `DISCORD_REQUIRE_MENTION` | 在服务器频道中响应前需要 @提及 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 不需要提及的逗号分隔的频道 ID |
| `DISCORD_AUTO_THREAD` | 在支持时自动线程化长回复 |
| `DISCORD_REACTIONS` | 在处理消息时启用表情符号反应（默认：`true`） |
| `DISCORD_IGNORED_CHANNELS` | 机器人永不响应的逗号分隔的频道 ID |
| `DISCORD_NO_THREAD_CHANNELS` | 机器人响应时不自动线程化的逗号分隔的频道 ID |
| `DISCORD_REPLY_TO_MODE` | 回复引用行为：`off`、`first`（默认）或 `all` |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 允许机器人 ping `@everyone`/`@here`（默认：`false`）。参见[提及控制](../user-guide/messaging/discord.md#mention-control)。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 允许机器人 ping `@role` 提及（默认：`false`）。 |
| `DISCORD_ALLOW_MENTION_USERS` | 允许机器人 ping 单个 `@user` 提及（默认：`true`）。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 回复消息时 ping 作者（默认：`true`）。 |
| `SLACK_BOT_TOKEN` | Slack 机器人 Token（`xoxb-...`） |
| `SLACK_APP_TOKEN` | Slack 应用级 Token（`xapp-...`，Socket 模式必需） |
| `SLACK_ALLOWED_USERS` | 逗号分隔的 Slack 用户 ID |
| `SLACK_HOME_CHANNEL` | 用于 cron 交付的默认 Slack 频道 |
| `SLACK_HOME_CHANNEL_NAME` | Slack 主页频道的显示名称 |
| `WHATSAPP_ENABLED` | 启用 WhatsApp 桥接（`true`/`false`） |
| `WHATSAPP_MODE` | `bot`（独立号码）或 `self-chat`（给自己发消息） |
| `WHATSAPP_ALLOWED_USERS` | 逗号分隔的电话号码（带国家代码，无 `+`），或 `*` 允许所有发送者 |
| `WHATSAPP_ALLOW_ALL_USERS` | 允许所有 WhatsApp 发送者，无需允许列表（`true`/`false`） |
| `WHATSAPP_DEBUG` | 在桥接中记录原始消息事件以进行故障排除（`true`/`false`） |
| `SIGNAL_HTTP_URL` | signal-cli 守护进程 HTTP 端点（例如 `http://127.0.0.1:8080`） |
| `SIGNAL_ACCOUNT` | 机器人电话号码（E.164 格式） |
| `SIGNAL_ALLOWED_USERS` | 逗号分隔的 E.164 电话号码或 UUID |
| `SIGNAL_GROUP_ALLOWED_USERS` | 逗号分隔的群组 ID，或 `*` 表示所有群组 |
| `SIGNAL_HOME_CHANNEL_NAME` | Signal 主页频道的显示名称 |
| `SIGNAL_IGNORE_STORIES` | 忽略 Signal 故事/状态更新 |
| `SIGNAL_ALLOW_ALL_USERS` | 允许所有 Signal 用户，无需允许列表 |
| `TWILIO_ACCOUNT_SID` | Twilio 账户 SID（与电话技能共享） |
| `TWILIO_AUTH_TOKEN` | Twilio 认证 Token（与电话技能共享；也用于 webhook 签名验证） |
| `TWILIO_PHONE_NUMBER` | Twilio 电话号码（E.164 格式）（与电话技能共享） |
| `SMS_WEBHOOK_URL` | 用于 Twilio 签名验证的公共 URL——必须与 Twilio 控制台中的 webhook URL 匹配（必需） |
| `SMS_WEBHOOK_PORT` | 入站 SMS 的 Webhook 监听端口（默认：`8080`） |
| `SMS_WEBHOOK_HOST` | Webhook 绑定地址（默认：`0.0.0.0`） |
| `SMS_INSECURE_NO_SIGNATURE` | 设置为 `true` 以禁用 Twilio 签名验证（仅限本地开发——不用于生产） |
| `SMS_ALLOWED_USERS` | 允许聊天的逗号分隔的 E.164 电话号码 |
| `SMS_ALLOW_ALL_USERS` | 允许所有 SMS 发送者，无需允许列表 |
| `SMS_HOME_CHANNEL` | 用于 cron 作业/通知交付的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | SMS 主页频道的显示名称 |
| `EMAIL_ADDRESS` | 电子邮件网关适配器的电子邮件地址 |
| `EMAIL_PASSWORD` | 电子邮件账户的密码或应用密码 |
| `EMAIL_IMAP_HOST` | 电子邮件适配器的 IMAP 主机名 |
| `EMAIL_IMAP_PORT` | IMAP 端口 |
| `EMAIL_SMTP_HOST` | 电子邮件适配器的 SMTP 主机名 |
| `EMAIL_SMTP_PORT` | SMTP 端口 |
| `EMAIL_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的电子邮件地址 |
| `EMAIL_HOME_ADDRESS` | 主动电子邮件交付的默认收件人 |
| `EMAIL_HOME_ADDRESS_NAME` | 电子邮件主页目标的显示名称 |
| `EMAIL_POLL_INTERVAL` | 电子邮件轮询间隔（秒） |
| `EMAIL_ALLOW_ALL_USERS` | 允许所有入站电子邮件发送者 |
| `DINGTALK_CLIENT_ID` | 钉钉机器人 AppKey，来自开发者门户（[open.dingtalk.com](https://open.dingtalk.com)） |
| `DINGTALK_CLIENT_SECRET` | 钉钉机器人 AppSecret，来自开发者门户 |
| `DINGTALK_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的钉钉用户 ID |
| `FEISHU_APP_ID` | 飞书/Lark 机器人 App ID，来自 [open.feishu.cn](https://open.feishu.cn/) |
| `FEISHU_APP_SECRET` | 飞书/Lark 机器人 App Secret |
| `FEISHU_DOMAIN` | `feishu`（中国）或 `lark`（国际）。默认：`feishu` |
| `FEISHU_CONNECTION_MODE` | `websocket`（推荐）或 `webhook`。默认：`websocket` |
| `FEISHU_ENCRYPT_KEY` | Webhook 模式的可选加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | Webhook 模式的可选验证 Token |
| `FEISHU_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的飞书用户 ID |
| `FEISHU_ALLOW_BOTS` | `none`（默认）/ `mentions` / `all`——接受来自其他机器人的入站消息。参见[机器人间消息传递](../user-guide/messaging/feishu.md#bot-to-bot-messaging) |
| `FEISHU_REQUIRE_MENTION` | `true`（默认）/ `false`——群组消息是否必须 @提及机器人。可通过 `group_rules.<chat_id>.require_mention` 按聊天覆盖。 |
| `FEISHU_HOME_CHANNEL` | 用于 cron 交付和通知的飞书聊天 ID |
| `WECOM_BOT_ID` | 企业微信 AI 机器人 ID，来自管理控制台 |
| `WECOM_SECRET` | 企业微信 AI 机器人密钥 |
| `WECOM_WEBSOCKET_URL` | 自定义 WebSocket URL（默认：`wss://openws.work.weixin.qq.com`） |
| `WECOM_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的企业微信用户 ID |
| `WECOM_HOME_CHANNEL` | 用于 cron 交付和通知的企业微信聊天 ID |
| `WECOM_CALLBACK_CORP_ID` | 用于回调自建应用的企业微信企业 Corp ID |
| `WECOM_CALLBACK_CORP_SECRET` | 自建应用的 Corp 密钥 |
| `WECOM_CALLBACK_AGENT_ID` | 自建应用的 Agent ID |
| `WECOM_CALLBACK_TOKEN` | 回调验证 Token |
| `WECOM_CALLBACK_ENCODING_AES_KEY` | 回调加密的 AES 密钥 |
| `WECOM_CALLBACK_HOST` | 回调服务器绑定地址（默认：`0.0.0.0`） |
| `WECOM_CALLBACK_PORT` | 回调服务器端口（默认：`8645`） |
| `WECOM_CALLBACK_ALLOWED_USERS` | 允许列表的逗号分隔的用户 ID |
| `WECOM_CALLBACK_ALLOW_ALL_USERS` | 设置为 `true` 以允许所有用户，无需允许列表 |
| `WEIXIN_ACCOUNT_ID` | 通过 iLink Bot API 二维码登录获取的微信账户 ID |
| `WEIXIN_TOKEN` | 通过 iLink Bot API 二维码登录获取的微信认证 Token |
| `WEIXIN_BASE_URL` | 覆盖微信 iLink Bot API 基础 URL（默认：`https://ilinkai.weixin.qq.com`） |
| `WEIXIN_CDN_BASE_URL` | 覆盖用于媒体的微信 CDN 基础 URL（默认：`https://novac2c.cdn.weixin.qq.com/c2c`） |
| `WEIXIN_DM_POLICY` | 私聊策略：`open`、`allowlist`、`pairing`、`disabled`（默认：`open`） |
| `WEIXIN_GROUP_POLICY` | 群组消息策略：`open`、`allowlist`、`disabled`（默认：`disabled`） |
| `WEIXIN_ALLOWED_USERS` | 允许与机器人私聊的逗号分隔的微信用户 ID |
| `WEIXIN_GROUP_ALLOWED_USERS` | 允许与机器人交互的逗号分隔的微信**群聊 ID**（非成员用户 ID）。变量名是遗留的——它期望群组 ID。仅当 iLink 实际传递群组事件时生效；二维码登录的 iLink 机器人身份（`...@im.bot`）通常不会接收普通微信群消息。 |
| `WEIXIN_HOME_CHANNEL` | 用于 cron 交付和通知的微信聊天 ID |
| `WEIXIN_HOME_CHANNEL_NAME` | 微信主页频道的显示名称 |
| `WEIXIN_ALLOW_ALL_USERS` | 允许所有微信用户，无需允许列表（`true`/`false`） |
| `BLUEBUBBLES_SERVER_URL` | BlueBubbles 服务器 URL（例如 `http://192.168.1.10:1234`） |
| `BLUEBUBBLES_PASSWORD` | BlueBubbles 服务器密码 |
| `BLUEBUBBLES_WEBHOOK_HOST` | Webhook 监听器绑定地址（默认：`127.0.0.1`） |
| `BLUEBUBBLES_WEBHOOK_PORT` | Webhook 监听器端口（默认：`8645`） |
| `BLUEBUBBLES_HOME_CHANNEL` | 用于 cron/通知交付的电话/电子邮件 |
| `BLUEBUBBLES_ALLOWED_USERS` | 逗号分隔的授权用户 |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | 允许所有用户（`true`/`false`） |
| `QQ_APP_ID` | QQ 机器人 App ID，来自 [q.qq.com](https://q.qq.com) |
| `QQ_CLIENT_SECRET` | QQ 机器人 App Secret，来自 [q.qq.com](https://q.qq.com) |
| `QQ_STT_API_KEY` | 外部 STT 备用提供商的 API 密钥（可选，当 QQ 内置 ASR 未返回文本时使用） |
| `QQ_STT_BASE_URL` | 外部 STT 提供商的基础 URL（可选） |
| `QQ_STT_MODEL` | 外部 STT 提供商的模型名称（可选） |
| `QQ_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的 QQ 用户 openID |
| `QQ_GROUP_ALLOWED_USERS` | 用于群组 @-消息访问的逗号分隔的 QQ 群组 ID |
| `QQ_ALLOW_ALL_USERS` | 允许所有用户（`true`/`false`，覆盖 `QQ_ALLOWED_USERS`） |
| `QQBOT_HOME_CHANNEL` | 用于 cron 交付和通知的 QQ 用户/群组 openID |
| `QQBOT_HOME_CHANNEL_NAME` | QQ 主页频道的显示名称 |
| `QQ_PORTAL_HOST` | 覆盖 QQ 门户主机（设置为 `sandbox.q.qq.com` 以通过沙盒网关路由；默认：`q.qq.com`）。 |
| `MATTERMOST_URL` | Mattermost 服务器 URL（例如 `https://mm.example.com`） |
| `MATTERMOST_TOKEN` | Mattermost 的机器人 Token 或个人访问 Token |
| `MATTERMOST_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的 Mattermost 用户 ID |
| `MATTERMOST_HOME_CHANNEL` | 用于主动消息传递（cron、通知）的频道 ID |
| `MATTERMOST_REQUIRE_MENTION` | 在频道中需要 `@提及`（默认：`true`）。设置为 `false` 以响应所有消息。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | 机器人响应时不需要 `@提及` 的逗号分隔的频道 ID |
| `MATTERMOST_REPLY_MODE` | 回复样式：`thread`（线程化回复）或 `off`（扁平消息，默认） |
| `MATRIX_HOMESERVER` | Matrix 家庭服务器 URL（例如 `https://matrix.org`） |
| `MATRIX_ACCESS_TOKEN` | 用于机器人认证的 Matrix 访问 Token |
| `MATRIX_USER_ID` | Matrix 用户 ID（例如 `@hermes:matrix.org`）——密码登录时必需，使用访问 Token 时可选 |
| `MATRIX_PASSWORD` | Matrix 密码（访问 Token 的替代方案） |
| `MATRIX_ALLOWED_USERS` | 允许向机器人发送消息的逗号分隔的 Matrix 用户 ID（例如 `@alice:matrix.org`） |
| `MATRIX_HOME_ROOM` | 用于主动消息传递的房间 ID（例如 `!abc123:matrix.org`） |
| `MATRIX_ENCRYPTION` | 启用端到端加密（`true`/`false`，默认：`false`） |
| `MATRIX_DEVICE_ID` | 稳定的 Matrix 设备 ID，用于跨重启的 E2EE 持久化（例如 `HERMES_BOT`）。没有此设置，E2EE 密钥会在每次启动时轮换，历史房间解密会中断。 |
| `MATRIX_REACTIONS` | 在入站消息上启用处理生命周期的表情符号反应（默认：`true`）。设置为 `false` 以禁用。 |
| `MATRIX_REQUIRE_MENTION` | 在房间中需要 `@提及`（默认：`true`）。设置为 `false` 以响应所有消息。 |
| `MATRIX_FREE_RESPONSE_ROOMS` | 机器人响应时不需要 `@提及` 的逗号分隔的房间 ID |
| `MATRIX_AUTO_THREAD` | 为房间消息自动创建线程（默认：`true`） |
| `MATRIX_DM_MENTION_THREADS` | 当机器人在私聊中被 `@提及` 时创建线程（默认：`false`） |
| `MATRIX_RECOVERY_KEY` | 设备密钥轮换后用于跨签名验证的恢复密钥。推荐用于启用跨签名的 E2EE 设置。 |
| `HASS_TOKEN` | Home Assistant 长期访问 Token（启用 HA 平台 + 工具） |
| `HASS_URL` | Home Assistant URL（默认：`http://homeassistant.local:8123`） |
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器（`true`/`false`） |
| `WEBHOOK_PORT` | 接收 webhook 的 HTTP 服务器端口（默认：`8644`） |
| `WEBHOOK_SECRET` | 用于 webhook 签名验证的全局 HMAC 密钥（当路由未指定自己的密钥时用作后备） |
| `API_SERVER_ENABLED` | 启用 OpenAI 兼容的 API 服务器（`true`/`false`）。与其他平台一起运行。 |
| `API_SERVER_KEY` | API 服务器认证的 Bearer Token。对于非环回绑定强制执行。 |
| `API_SERVER_CORS_ORIGINS` | 允许直接调用 API 服务器的逗号分隔的浏览器来源（例如 `http://localhost:3000,http://127.0.0.1:3000`）。默认：禁用。 |
| `API_SERVER_PORT` | API 服务器的端口（默认：`8642`） |
| `API_SERVER_HOST` | API 服务器的主机/绑定地址（默认：`127.0.0.1`）。使用 `0.0.0.0` 进行网络访问——需要 `API_SERVER_KEY` 和狭窄的 `API_SERVER_CORS_ORIGINS` 允许列表。 |
| `API_SERVER_MODEL_NAME` | 在 `/v1/models` 上公布的模型名称。默认为配置文件名称（或默认配置文件的 `hermes-agent`）。对于像 Open WebUI 这样的前端需要每个连接不同模型名称的多用户设置很有用。 |
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL，用于转发消息到（[代理模式](/docs/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)）。设置后，网关仅处理平台 I/O——所有 Agent 工作都委派给远程服务器。也可通过 `config.yaml` 中的 `gateway.proxy_url` 配置。 |
| `GATEWAY_PROXY_KEY` | 在代理模式下用于远程 API 服务器认证的 Bearer Token。必须与远程主机上的 `API_SERVER_KEY` 匹配。 |
| `MESSAGING_CWD` | 消息传递模式下终端命令的工作目录（默认：`~`） |
| `GATEWAY_ALLOWED_USERS` | 跨所有平台允许的逗号分隔的用户 ID |
| `GATEWAY_ALLOW_ALL_USERS` | 允许所有用户，无需允许列表（`true`/`false`，默认：`false`） |
### 高级消息调优

针对各平台的高级调节旋钮，用于节流出站消息批处理器。大多数用户永远不需要调整这些设置；默认值已设置为尊重各平台的速率限制，同时不会感觉迟钝。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_TELEGRAM_TEXT_BATCH_DELAY_SECONDS` | 刷新已排队的 Telegram 文本块前的宽限窗口（默认：`0.6`）。 |
| `HERMES_TELEGRAM_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 当单个 Telegram 消息超过长度限制时，拆分块之间的延迟（默认：`2.0`）。 |
| `HERMES_TELEGRAM_MEDIA_BATCH_DELAY_SECONDS` | 刷新已排队的 Telegram 媒体前的宽限窗口（默认：`0.6`）。 |
| `HERMES_TELEGRAM_FOLLOWUP_GRACE_SECONDS` | Agent 完成后发送跟进消息前的延迟，以避免与最后一个流式块竞争。 |
| `HERMES_TELEGRAM_HTTP_CONNECT_TIMEOUT` / `_READ_TIMEOUT` / `_WRITE_TIMEOUT` / `_POOL_TIMEOUT` | 覆盖底层的 `python-telegram-bot` HTTP 超时设置（秒）。 |
| `HERMES_TELEGRAM_HTTP_POOL_SIZE` | 到 Telegram API 的最大并发 HTTP 连接数。 |
| `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS` | 禁用 DNS 失败时使用的硬编码 Cloudflare 备用 IP（`true`/`false`）。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 刷新已排队的 Discord 文本块前的宽限窗口（默认：`0.6`）。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 当 Discord 消息超过长度限制时，拆分块之间的延迟（默认：`2.0`）。 |
| `HERMES_MATRIX_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | Matrix 平台对应的批处理旋钮。 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` / `_MAX_CHARS` / `_MAX_MESSAGES` | 飞书批处理器调优 — 延迟、拆分延迟、每条消息最大字符数、每批最大消息数。 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 飞书媒体刷新延迟。 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 飞书 Webhook 去重缓存的大小（默认：`1024`）。 |
| `HERMES_WECOM_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | 企业微信批处理器调优。 |
| `HERMES_VISION_DOWNLOAD_TIMEOUT` | 将图像交给视觉模型前下载的超时时间（秒）（默认：`30`）。 |
| `HERMES_RESTART_DRAIN_TIMEOUT` | 消息网关：在 `/restart` 时等待活动运行任务排空的时间（秒），之后强制重启（默认：`900`）。 |
| `HERMES_GATEWAY_PLATFORM_CONNECT_TIMEOUT` | 消息网关启动期间每个平台的连接超时时间（秒）。 |
| `HERMES_GATEWAY_BUSY_INPUT_MODE` | 默认的消息网关忙碌输入行为：`queue`、`steer` 或 `interrupt`。可通过每个聊天中的 `/busy` 命令覆盖。 |
| `HERMES_GATEWAY_BUSY_ACK_ENABLED` | 当用户在 Agent 忙碌时发送输入时，消息网关是否发送确认消息（⚡/⏳/⏩）（默认：`true`）。设置为 `false` 以完全抑制这些消息 — 输入仍会正常排队/转向/中断，只是聊天回复被静音。从 `config.yaml` 中的 `display.busy_ack_enabled` 桥接而来。 |
| `HERMES_CRON_TIMEOUT` | 定时任务 Agent 运行的不活动超时时间（秒）（默认：`600`）。Agent 在主动调用工具或接收流式 Token 时可以无限期运行 — 此设置仅在空闲时触发。设置为 `0` 表示无限制。 |
| `HERMES_CRON_SCRIPT_TIMEOUT` | 附加到定时任务的预运行脚本的超时时间（秒）（默认：`120`）。覆盖需要更长时间执行的脚本（例如，用于反机器人定时的随机延迟）。也可通过 `config.yaml` 中的 `cron.script_timeout_seconds` 配置。 |
| `HERMES_CRON_MAX_PARALLEL` | 每个时间点并行运行的最大定时任务数（默认：`4`）。 |

## Agent 行为

| 变量 | 描述 |
|----------|-------------|
| `HERMES_MAX_ITERATIONS` | 每次对话的最大工具调用迭代次数（默认：90） |
| `HERMES_INFERENCE_MODEL` | 在进程级别覆盖模型名称（对于会话，优先级高于 `config.yaml`）。也可通过 `-m`/`--model` 标志设置。 |
| `HERMES_YOLO_MODE` | 设置为 `1` 以绕过危险命令批准提示。等同于 `--yolo`。 |
| `HERMES_ACCEPT_HOOKS` | 自动批准 `config.yaml` 中声明的任何未见过的 shell 钩子，无需 TTY 提示。等同于 `--accept-hooks` 或 `hooks_auto_accept: true`。 |
| `HERMES_IGNORE_USER_CONFIG` | 跳过 `~/.hermes/config.yaml` 并使用内置默认值（`.env` 中的凭据仍会加载）。等同于 `--ignore-user-config`。 |
| `HERMES_IGNORE_RULES` | 跳过自动注入 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能。等同于 `--ignore-rules`。 |
| `HERMES_MD_NAMES` | 要自动注入的规则文件名的逗号分隔列表（默认：`AGENTS.md,CLAUDE.md,.cursorrules,SOUL.md`）。 |
| `HERMES_TOOL_PROGRESS` | 用于工具进度显示的已弃用兼容性变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_TOOL_PROGRESS_MODE` | 用于工具进度模式的已弃用兼容性变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_HUMAN_DELAY_MODE` | 响应节奏：`off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | 自定义延迟范围最小值（毫秒） |
| `HERMES_HUMAN_DELAY_MAX_MS` | 自定义延迟范围最大值（毫秒） |
| `HERMES_QUIET` | 抑制非必要输出（`true`/`false`） |
| `HERMES_API_TIMEOUT` | LLM API 调用超时时间（秒）（默认：`1800`） |
| `HERMES_API_CALL_STALE_TIMEOUT` | 非流式陈旧调用超时时间（秒）（默认：`300`）。如果未设置，对于本地提供商会自动禁用。也可通过 `config.yaml` 中的 `providers.<id>.stale_timeout_seconds` 或 `providers.<id>.models.<model>.stale_timeout_seconds` 配置。 |
| `HERMES_STREAM_READ_TIMEOUT` | 流式套接字读取超时时间（秒）（默认：`120`）。对于本地提供商自动增加到 `HERMES_API_TIMEOUT`。如果本地 LLM 在长代码生成期间超时，请增加此值。 |
| `HERMES_STREAM_STALE_TIMEOUT` | 陈旧流检测超时时间（秒）（默认：`180`）。对于本地提供商自动禁用。如果在此窗口内没有块到达，则触发连接终止。 |
| `HERMES_STREAM_RETRIES` | 在瞬态网络错误时，流中重新连接尝试的次数（默认：`3`）。 |
| `HERMES_AGENT_TIMEOUT` | 消息网关中运行 Agent 的不活动超时时间（秒）（默认：`900`）。每次工具调用和流式 Token 都会重置。设置为 `0` 以禁用。 |
| `HERMES_AGENT_TIMEOUT_WARNING` | 消息网关：在不活动这么多秒后发送警告消息（默认：`HERMES_AGENT_TIMEOUT` 的 75%）。 |
| `HERMES_AGENT_NOTIFY_INTERVAL` | 消息网关：长时间运行的 Agent 轮次之间进度通知的间隔时间（秒）。 |
| `HERMES_CHECKPOINT_TIMEOUT` | 文件系统检查点创建的超时时间（秒）（默认：`30`）。 |
| `HERMES_EXEC_ASK` | 在消息网关模式下启用执行批准提示（`true`/`false`） |
| `HERMES_ENABLE_PROJECT_PLUGINS` | 启用从 `./.hermes/plugins/` 自动发现仓库本地插件（`true`/`false`，默认：`false`） |
| `HERMES_BACKGROUND_NOTIFICATIONS` | 消息网关中后台进程通知模式：`all`（默认）、`result`、`error`、`off` |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | 在 API 调用时注入的临时系统提示词（永远不会持久化到会话中） |
| `HERMES_PREFILL_MESSAGES_FILE` | 指向一个 JSON 文件的路径，该文件包含在 API 调用时注入的临时预填充消息。 |
| `HERMES_ALLOW_PRIVATE_URLS` | `true`/`false` — 允许工具获取 localhost/私有网络 URL。在消息网关模式下默认关闭。 |
| `HERMES_REDACT_SECRETS` | `true`/`false` — 控制日志和可共享输出中的秘密信息脱敏（默认：`true`）。 |
| `HERMES_WRITE_SAFE_ROOT` | 可选的目录前缀，用于限制 `write_file`/`patch` 的写入；此路径之外的写入需要批准。 |
| `HERMES_DISABLE_FILE_STATE_GUARD` | 设置为 `1` 以关闭 `patch`/`write_file` 上的“自您读取后文件已更改”防护。 |
| `HERMES_CORE_TOOLS` | 用于规范核心工具列表的逗号分隔覆盖（高级；很少需要）。 |
| `HERMES_BUNDLED_SKILLS` | 用于启动时加载的捆绑技能列表的逗号分隔覆盖。 |
| `HERMES_OPTIONAL_SKILLS` | 可选技能名称的逗号分隔列表，在首次运行时自动安装。 |
| `HERMES_DEBUG_INTERRUPT` | 设置为 `1` 以将详细的中断/取消跟踪记录到 `agent.log`。 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载转储到日志文件（`true`/`false`） |
| `HERMES_DUMP_REQUEST_STDOUT` | 将 API 请求负载转储到 stdout 而不是日志文件。 |
| `HERMES_OAUTH_TRACE` | 设置为 `1` 以记录 OAuth Token 交换和刷新尝试。包括脱敏的计时信息。 |
| `HERMES_OAUTH_FILE` | 覆盖用于 OAuth 凭据存储的路径（默认：`~/.hermes/auth.json`）。 |
| `HERMES_AGENT_HELP_GUIDANCE` | 为自定义部署向系统提示词附加额外的指导文本。 |
| `HERMES_AGENT_LOGO` | 覆盖 CLI 启动时的 ASCII 横幅徽标。 |
| `DELEGATION_MAX_CONCURRENT_CHILDREN` | 每个 `delegate_task` 批次的最大并行子 Agent 数（默认：`3`，下限为 1，无上限）。也可通过 `config.yaml` 中的 `delegation.max_concurrent_children` 配置 — 配置值具有优先级。 |
## 界面

| 变量 | 描述 |
|----------|-------------|
| `HERMES_TUI` | 当设置为 `1` 时，启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等同于传递 `--tui` 参数。 |
| `HERMES_TUI_DIR` | 预构建的 `ui-tui/` 目录路径（必须包含 `dist/entry.js` 和已填充的 `node_modules`）。供发行版和 Nix 使用，以跳过首次启动时的 `npm install`。 |
| `HERMES_TUI_RESUME` | 启动时通过 ID 恢复特定的 TUI 会话。设置后，`hermes --tui` 会跳过创建新会话，转而拾取指定会话 —— 这在断开连接或终端崩溃后重新连接时很有用。 |
| `HERMES_TUI_THEME` | 强制设置 TUI 颜色主题：`light`、`dark` 或原始的 6 字符背景十六进制值（例如 `ffffff` 或 `1a1a2e`）。未设置时，Hermes 使用 `COLORFGBG` 和终端背景查询自动检测；此变量会覆盖那些未设置 `COLORFGBG` 的终端（Ghostty、Warp、iTerm2 等）的检测。 |
| `HERMES_INFERENCE_MODEL` | 强制设置 `hermes -z` / `hermes chat` 的模型，而不修改 `config.yaml`。与 `HERMES_INFERENCE_PROVIDER` 配对使用。对于需要每次运行覆盖默认模型的脚本化调用者（sweeper、CI、批量运行器）很有用。 |

## 会话设置

| 变量 | 描述 |
|----------|-------------|
| `SESSION_IDLE_MINUTES` | 在 N 分钟不活动后重置会话（默认：1440） |
| `SESSION_RESET_HOUR` | 每日重置时间，24 小时制（默认：4 = 凌晨 4 点） |

## 上下文压缩（仅限 config.yaml）

上下文压缩仅通过 `config.yaml` 配置 —— 没有对应的环境变量。阈值设置位于 `compression:` 块中，而摘要模型/提供商位于 `auxiliary.compression:` 下。

```yaml
compression:
  enabled: true
  threshold: 0.50
  target_ratio: 0.20         # 作为最近尾部保留的阈值比例
  protect_last_n: 20         # 保持未压缩的最小最近消息数
```

:::info 旧版迁移
包含 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 的旧配置会在首次加载时自动迁移到 `auxiliary.compression.*`。
:::

## 辅助任务覆盖

| 变量 | 描述 |
|----------|-------------|
| `AUXILIARY_VISION_PROVIDER` | 覆盖视觉任务的提供商 |
| `AUXILIARY_VISION_MODEL` | 覆盖视觉任务的模型 |
| `AUXILIARY_VISION_BASE_URL` | 视觉任务的直接 OpenAI 兼容端点 |
| `AUXILIARY_VISION_API_KEY` | 与 `AUXILIARY_VISION_BASE_URL` 配对的 API 密钥 |
| `AUXILIARY_WEB_EXTRACT_PROVIDER` | 覆盖网页提取/摘要的提供商 |
| `AUXILIARY_WEB_EXTRACT_MODEL` | 覆盖网页提取/摘要的模型 |
| `AUXILIARY_WEB_EXTRACT_BASE_URL` | 网页提取/摘要的直接 OpenAI 兼容端点 |
| `AUXILIARY_WEB_EXTRACT_API_KEY` | 与 `AUXILIARY_WEB_EXTRACT_BASE_URL` 配对的 API 密钥 |

对于特定任务的直接端点，Hermes 使用任务配置的 API 密钥或 `OPENAI_API_KEY`。它不会为这些自定义端点重用 `OPENROUTER_API_KEY`。

## 备用提供商（仅限 config.yaml）

主模型备用链仅通过 `config.yaml` 配置 —— 没有对应的环境变量。在顶层添加一个包含 `provider` 和 `model` 键的 `fallback_providers` 列表，以在主模型遇到错误时启用自动故障转移。

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

为了向后兼容，旧的顶层 `fallback_model` 单提供商格式仍会被读取，但新配置应使用 `fallback_providers`。

完整详情请参阅 [备用提供商](/docs/user-guide/features/fallback-providers)。

## 提供商路由（仅限 config.yaml）

这些配置项放在 `~/.hermes/config.yaml` 的 `provider_routing` 部分下：

| 键 | 描述 |
|-----|-------------|
| `sort` | 提供商排序方式：`"price"`（默认）、`"throughput"` 或 `"latency"` |
| `only` | 允许的提供商 slug 列表（例如 `["anthropic", "google"]`） |
| `ignore` | 要跳过的提供商 slug 列表 |
| `order` | 按顺序尝试的提供商 slug 列表 |
| `require_parameters` | 仅使用支持所有请求参数的提供商（`true`/`false`） |
| `data_collection` | `"allow"`（默认）或 `"deny"` 以排除存储数据的提供商 |

:::tip
使用 `hermes config set` 来设置环境变量 —— 它会自动将它们保存到正确的文件（`.env` 用于密钥，`config.yaml` 用于其他所有内容）。
:::