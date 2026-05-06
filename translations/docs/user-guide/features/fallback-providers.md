---
title: 备用提供商
description: 在主模型不可用时，配置自动故障转移至备用 LLM 提供商。
sidebar_label: 备用提供商
sidebar_position: 8
---

# 备用提供商

Hermes Agent 拥有三层弹性机制，可在提供商遇到问题时保持您的会话运行：

1. **[凭证池](./credential-pools.md)** — 在*同一*提供商的多个 API 密钥间轮换（首先尝试）
2. **主模型备用** — 当您的主模型失败时，自动切换到*不同*的提供商:模型
3. **辅助任务备用** — 为视觉、压缩和网页提取等辅助任务提供独立的提供商解析

凭证池处理同一提供商内的轮换（例如，多个 OpenRouter 密钥）。本页涵盖跨提供商备用。两者都是可选的，并且独立工作。

## 主模型备用

当您的主要 LLM 提供商遇到错误时 — 速率限制、服务器过载、认证失败、连接中断 — Hermes 可以在会话中自动切换到备用提供商:模型组合，而不会丢失您的对话。

### 配置

最简单的方法是使用交互式管理器：

```bash
hermes fallback
```

`hermes fallback` 复用 `hermes model` 中的提供商选择器 — 相同的提供商列表、相同的凭证提示、相同的验证。按 `a` 添加备用，`↑`/`↓` 重新排序，`d` 删除，`q` 保存并退出。更改将持久保存在 `config.yaml` 中的 `model.fallback_providers` 下。

如果您更愿意直接编辑 YAML，请在 `~/.hermes/config.yaml` 中添加一个 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 都是**必需的**。如果缺少任何一个，备用功能将被禁用。

:::note `fallback_model` 与 `fallback_providers`
`fallback_model`（单数）是旧版单备用键 — Hermes 为了向后兼容仍然支持它。`fallback_providers`（复数，列表）支持按顺序尝试多个备用；`hermes fallback` 写入此键。当两者都设置时，Hermes 会合并它们，`fallback_providers` 优先。
:::

### 支持的提供商

| 提供商 | 值 | 要求 |
|----------|-------|-------------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes auth` (OAuth) |
| OpenAI Codex | `openai-codex` | `hermes model` (ChatGPT OAuth) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | 外部进程（编辑器集成） |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax (中国) | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` (可选: `NVIDIA_BASE_URL`) |
| GMI Cloud | `gmi` | `GMI_API_KEY` (可选: `GMI_BASE_URL`) |
| StepFun | `stepfun` | `STEPFUN_API_KEY` (可选: `STEPFUN_BASE_URL`) |
| Ollama Cloud | `ollama-cloud` | `OLLAMA_API_KEY` |
| Google Gemini (OAuth) | `google-gemini-cli` | `hermes model` (Google OAuth; 可选: `HERMES_GEMINI_PROJECT_ID`) |
| Google AI Studio | `gemini` | `GOOGLE_API_KEY` (别名: `GEMINI_API_KEY`) |
| xAI (Grok) | `xai` (别名 `grok`) | `XAI_API_KEY` (可选: `XAI_BASE_URL`) |
| AWS Bedrock | `bedrock` | 标准 boto3 认证 (`AWS_REGION` + `AWS_PROFILE` 或 `AWS_ACCESS_KEY_ID`) |
| Qwen Portal (OAuth) | `qwen-oauth` | `hermes model` (Qwen Portal OAuth; 可选: `HERMES_QWEN_BASE_URL`) |
| MiniMax (OAuth) | `minimax-oauth` | `hermes model` (MiniMax portal OAuth) |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| Xiaomi MiMo | `xiaomi` | `XIAOMI_API_KEY` |
| Arcee AI | `arcee` | `ARCEEAI_API_KEY` |
| GMI Cloud | `gmi` | `GMI_API_KEY` |
| Alibaba / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| Alibaba Coding Plan | `alibaba-coding-plan` | `ALIBABA_CODING_PLAN_API_KEY` (回退到 `DASHSCOPE_API_KEY`) |
| Kimi / Moonshot (中国) | `kimi-coding-cn` | `KIMI_CN_API_KEY` |
| StepFun | `stepfun` | `STEPFUN_API_KEY` |
| Tencent TokenHub | `tencent-tokenhub` | `TOKENHUB_API_KEY` |
| Azure AI Foundry | `azure-foundry` | `AZURE_FOUNDRY_API_KEY` + `AZURE_FOUNDRY_BASE_URL` |
| LM Studio (本地) | `lmstudio` | `LM_API_KEY` (或本地无需) + `LM_BASE_URL` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `key_env` (见下文) |

### 自定义端点备用

对于自定义的 OpenAI 兼容端点，添加 `base_url` 和可选的 `key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  key_env: MY_LOCAL_KEY              # 包含 API 密钥的环境变量名
```

### 备用触发时机

当主模型因以下原因失败时，备用会自动激活：

- **速率限制** (HTTP 429) — 在重试尝试用尽后
- **服务器错误** (HTTP 500, 502, 503) — 在重试尝试用尽后
- **认证失败** (HTTP 401, 403) — 立即（无需重试）
- **未找到** (HTTP 404) — 立即
- **无效响应** — 当 API 重复返回格式错误或空响应时

触发时，Hermes 会：

1. 解析备用提供商的凭证
2. 构建新的 API 客户端
3. 原地替换模型、提供商和客户端
4. 重置重试计数器并继续对话

切换是无缝的 — 您的对话历史、工具调用和上下文都得以保留。Agent 会从它中断的地方继续，只是使用不同的模型。

:::info 按轮次，非按会话
备用是**轮次作用域**的：每个新的用户消息开始时，主模型都会恢复。如果主模型在轮次中途失败，备用仅在该轮次激活。在下一条消息时，Hermes 会再次尝试主模型。在单个轮次内，备用最多激活一次 — 如果备用也失败，则正常的错误处理接管（重试，然后显示错误消息）。这可以防止在轮次内发生级联故障转移循环，同时给主模型每轮次一个新的机会。
:::
### 示例

**将 OpenRouter 作为 Anthropic 原生模型的备用方案：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**将 Nous Portal 作为 OpenRouter 的备用方案：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**将本地模型作为云端模型的备用方案：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  key_env: LOCAL_API_KEY
```

**将 Codex OAuth 作为备用方案：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 备用方案生效的场景

| 场景 | 是否支持备用方案 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关（Telegram、Discord 等） | ✔ |
| 子 Agent 委派 | ✘（子 Agent 不继承备用配置） |
| 定时任务 | ✘（使用固定的提供商运行） |
| 辅助任务（视觉、压缩） | ✘（使用它们自己的提供商链 — 见下文） |

:::tip
`fallback_model` 没有对应的环境变量 — 它完全通过 `config.yaml` 配置。这是有意为之：备用配置是一个深思熟虑的选择，不应被过时的 shell 导出变量覆盖。
:::

---

## 辅助任务的备用方案

Hermes 为辅助任务使用独立的轻量级模型。每个任务都有自己的提供商解析链，这充当了内置的备用系统。

### 具有独立提供商解析的任务

| 任务 | 功能 | 配置键 |
|------|-------------|-----------|
| 视觉 | 图像分析、浏览器截图 | `auxiliary.vision` |
| 网页提取 | 网页摘要 | `auxiliary.web_extract` |
| 压缩 | 上下文压缩摘要 | `auxiliary.compression` |
| 会话搜索 | 过往会话摘要 | `auxiliary.session_search` |
| 技能中心 | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| 审批 | 智能命令审批分类 | `auxiliary.approval` |
| 标题生成 | 会话标题摘要 | `auxiliary.title_generation` |

### 自动检测链

当任务的提供商设置为 `"auto"`（默认值）时，Hermes 会按顺序尝试提供商，直到有一个可用：

**对于文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → 自定义端点 → Codex OAuth →
API 密钥提供商（z.ai、Kimi、MiniMax、小米 MiMo、Hugging Face、Anthropic）→ 放弃
```

**对于视觉任务：**

```text
主提供商（如果支持视觉）→ OpenRouter → Nous Portal →
Codex OAuth → Anthropic → 自定义端点 → 放弃
```

如果解析出的提供商在调用时失败，Hermes 还有一个内部重试机制：如果提供商不是 OpenRouter 且没有设置显式的 `base_url`，它会将 OpenRouter 作为最后手段的备用方案。

### 配置辅助任务提供商

每个任务都可以在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # 例如 "openai/gpt-4o"
    base_url: ""                  # 直接端点（优先级高于 provider）
    api_key: ""                   # base_url 的 API 密钥

  web_extract:
    provider: "auto"
    model: ""

  compression:
    provider: "auto"
    model: ""

  session_search:
    provider: "auto"
    model: ""
    timeout: 30
    max_concurrency: 3
    extra_body: {}

  skills_hub:
    provider: "auto"
    model: ""

  mcp:
    provider: "auto"
    model: ""
```

以上每个任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩在 `auxiliary.compression` 下配置：

```yaml
auxiliary:
  compression:
    provider: main                                    # 与其他辅助任务相同的提供商选项
    model: google/gemini-3-flash-preview
    base_url: null                                    # 自定义 OpenAI 兼容端点
```

而备用模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选的自定义端点
```

对于 `auxiliary.session_search`，Hermes 还支持：

- `max_concurrency` 限制同时运行的会话摘要数量
- `extra_body` 在摘要调用时传递特定于提供商的 OpenAI 兼容请求字段

示例：

```yaml
auxiliary:
  session_search:
    provider: main
    model: glm-4.5-air
    max_concurrency: 2
    extra_body:
      enable_thinking: false
```

如果你的提供商不支持原生的 OpenAI 兼容的推理控制字段，`extra_body` 对此部分将没有帮助；在这种情况下，`max_concurrency` 对于减少请求突发导致的 429 错误仍然有用。

所有三者 — 辅助任务、压缩、备用模型 — 的工作方式相同：设置 `provider` 来选择处理请求的提供商，设置 `model` 来选择模型，设置 `base_url` 来指向自定义端点（覆盖 provider）。

### 辅助任务的提供商选项

这些选项仅适用于 `auxiliary:`、`compression:` 和 `fallback_model:` 配置 — `"main"` **不是** 顶层 `model.provider` 的有效值。对于自定义端点，请在 `model:` 部分使用 `provider: custom`（参见 [AI 提供商](/docs/integrations/providers)）。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 按顺序尝试提供商直到有一个可用（默认） | 至少配置了一个提供商 |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主 Agent 使用的任何提供商（仅限辅助任务） | 已配置活跃的主提供商 |
| `"anthropic"` | 强制使用 Anthropic 原生 | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |

### 直接端点覆盖

对于任何辅助任务，设置 `base_url` 会完全绕过提供商解析，并将请求直接发送到该端点：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`。Hermes 使用配置的 `api_key` 进行身份验证，如果未设置则回退到 `OPENAI_API_KEY`。它**不会**为自定义端点复用 `OPENROUTER_API_KEY`。

---

## 上下文压缩回退

上下文压缩使用 `auxiliary.compression` 配置块来控制哪个模型和提供商处理摘要生成：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

:::info 旧配置迁移
带有 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 的旧配置在首次加载时（配置版本 17）会自动迁移到 `auxiliary.compression.*`。
:::

如果没有可用的提供商进行压缩，Hermes 会丢弃中间对话轮次而不生成摘要，而不是让会话失败。

---

## 委派提供商覆盖

由 `delegate_task` 生成的子 Agent **不**使用主回退模型。但是，为了优化成本，可以将它们路由到不同的提供商:模型组合：

```yaml
delegation:
  provider: "openrouter"                      # 覆盖所有子 Agent 的提供商
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或使用直接端点
  # api_key: "local-key"
```

完整配置细节请参阅[子 Agent 委派](/docs/user-guide/features/delegation)。

---

## 定时任务提供商

定时任务使用执行时配置的任何提供商运行。它们不支持回退模型。要为定时任务使用不同的提供商，请在定时任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整配置细节请参阅[定时任务 (Cron)](/docs/user-guide/features/cron)。

---

## 总结

| 功能 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主 Agent 模型 | `config.yaml` 中的 `fallback_model` — 发生错误时每轮故障转移（每轮恢复主模型） | `fallback_model:` (顶级) |
| 视觉 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 自动检测链，如果不可用则降级为无摘要 | `auxiliary.compression` |
| 会话搜索 | 自动检测链 | `auxiliary.session_search` |
| 技能中心 | 自动检测链 | `auxiliary.skills_hub` |
| MCP 助手 | 自动检测链 | `auxiliary.mcp` |
| 审批分类 | 自动检测链 | `auxiliary.approval` |
| 标题生成 | 自动检测链 | `auxiliary.title_generation` |
| 委派 | 仅提供商覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| 定时任务 | 仅每任务提供商覆盖（无自动回退） | 每任务的 `provider` / `model` |