---
sidebar_position: 15
title: "Azure AI Foundry"
description: "将 Hermes Agent 与 Azure AI Foundry 结合使用 — 支持 OpenAI 风格和 Anthropic 风格的端点，自动检测传输协议和已部署的模型"
---

# Azure AI Foundry

Hermes Agent 将 Azure AI Foundry（以及 Azure OpenAI）作为一等提供商支持。单个 Azure 资源可以托管使用两种不同传输格式的模型：

- **OpenAI 风格** — 在类似 `https://<resource>.openai.azure.com/openai/v1` 的端点上使用 `POST /v1/chat/completions`。用于 GPT-4.x、GPT-5.x、Llama、Mistral 和大多数开源模型。
- **Anthropic 风格** — 在类似 `https://<resource>.services.ai.azure.com/anthropic` 的端点上使用 `POST /v1/messages`。当 Azure Foundry 通过 Anthropic Messages API 格式提供 Claude 模型时使用。

设置向导会探测您的端点，并自动检测其使用的传输协议、可用的部署以及每个模型的上下文长度。

## 先决条件

- 一个至少有一个部署的 Azure AI Foundry 或 Azure OpenAI 资源
- 该资源的 API 密钥（可在 Azure 门户的“密钥和终结点”下找到）
- 部署的端点 URL

## 快速开始

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入您的端点 URL
# → 输入您的 API 密钥
# Hermes 探测端点并自动检测传输协议 + 模型
# → 从列表中选择一个模型（或手动输入部署名称）
```

向导将：

1.  **嗅探 URL 路径** — 以 `/anthropic` 结尾的 URL 被识别为 Azure Foundry Claude 路由。
2.  **探测 `GET <base>/models`** — 如果端点返回一个 OpenAI 格式的模型列表，Hermes 将切换到 `chat_completions` 模式，并用返回的部署 ID 预填充选择器。
3.  **探测 Anthropic Messages 格式** — 对于不暴露 `/models` 但接受 Anthropic Messages 格式的端点的回退方案。
4.  **回退到手动输入** — 拒绝所有探测的私有/受控端点仍然有效；您需要手动选择 API 模式并输入部署名称。

所选模型的上下文长度通过 Hermes 的标准元数据链（`models.dev`、提供商元数据和硬编码的模型系列回退）解析，并存储在 `config.yaml` 中，以便模型可以正确调整其自身的上下文窗口大小。

## 配置（写入 `config.yaml`）

运行向导后，您将看到类似以下的内容：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions         # 或 "anthropic_messages"
  default: gpt-5.4-mini              # 您的部署 / 模型名称
  context_length: 400000             # 自动检测
```

在 `~/.hermes/.env` 中：

```
AZURE_FOUNDRY_API_KEY=<your-azure-key>
```

## OpenAI 风格端点（GPT、Llama 等）

Azure OpenAI 的 v1 GA 端点接受标准的 `openai` Python 客户端，只需极少的改动：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5.4
```

重要行为：

-   **GPT-5.x、codex 和 o 系列自动路由到 Responses API。** Azure Foundry 将 GPT-5 / codex / o1 / o3 / o4 模型部署为仅支持 Responses API — 对它们调用 `/chat/completions` 会返回 `400 "The requested operation is unsupported."`。Hermes 通过名称检测这些模型系列，并透明地将 `api_mode` 升级为 `codex_responses`，即使 `config.yaml` 中仍然显示 `api_mode: chat_completions`。GPT-4、GPT-4o、Llama、Mistral 和其他部署则保持在 `/chat/completions`。
-   **自动使用 `max_completion_tokens`。** Azure OpenAI（与直接使用 OpenAI 类似）要求为 gpt-4o、o 系列和 gpt-5.x 模型提供 `max_completion_tokens`。Hermes 根据端点发送正确的参数。
-   **需要 `api-version` 的 v1 之前版本端点。** 如果您有一个遗留的基础 URL，如 `https://<resource>.openai.azure.com/openai?api-version=2025-04-01-preview`，Hermes 会提取查询字符串，并通过每个请求的 `default_query` 转发它（否则 OpenAI SDK 在连接路径时会丢弃它）。

## Anthropic 风格端点（通过 Azure Foundry 的 Claude）

对于 Claude 部署，请使用 Anthropic 风格的路由：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_mode: anthropic_messages
  default: claude-sonnet-4-6
```

重要行为：

-   **从基础 URL 中移除 `/v1`。** Anthropic SDK 会将 `/v1/messages` 附加到每个请求 URL — Hermes 在将 URL 交给 SDK 之前会移除任何尾随的 `/v1`，以避免出现重复的 `/v1` 路径。
-   **`api-version` 通过 `default_query` 发送，而不是附加到 URL。** Azure Anthropic 需要一个 `api-version` 查询字符串。将其硬编码到基础 URL 中会产生格式错误的路径，如 `/anthropic?api-version=.../v1/messages` 并返回 404。Hermes 改为通过 Anthropic SDK 的 `default_query` 传递 `api-version=2025-04-15`。
-   **禁用 OAuth 令牌刷新。** Azure 部署使用静态 API 密钥。适用于 Anthropic Console 的 `~/.claude/.credentials.json` OAuth 令牌刷新循环会为 Azure 端点显式跳过，以防止 Claude Code OAuth 令牌在会话中途覆盖您的 Azure 密钥。

## 替代方案：`provider: anthropic` + Azure 基础 URL

如果您已经配置了 `provider: anthropic`，并且只想将其指向 Azure AI Foundry 以使用 Claude，您可以完全跳过 `azure-foundry` 提供商：

```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_key_env: AZURE_ANTHROPIC_KEY
  default: claude-sonnet-4-6
```

在 `~/.hermes/.env` 中设置 `AZURE_ANTHROPIC_KEY`。Hermes 检测到基础 URL 中包含 `azure.com`，并绕过 Claude Code OAuth 令牌链，从而直接使用 Azure 密钥进行 `x-api-key` 身份验证。

## 模型发现

Azure **不** 暴露一个纯 API 密钥端点来列出您*已部署*的模型部署。部署枚举需要 Azure Resource Manager 身份验证（`az cognitiveservices account deployment list`）和 Azure AD 主体，而不是推理 API 密钥。

Hermes 可以做到的是：

-   Azure OpenAI v1 端点（`<resource>.openai.azure.com/openai/v1`）通过 `GET /models` 暴露资源的**可用**模型目录。Hermes 使用此列表预填充模型选择器。
-   Azure Foundry `/anthropic` 路由：通过 URL 路径检测，手动输入模型名称。
-   私有 / 防火墙后的端点：手动输入，并显示友好的“无法探测”消息。

您始终可以直接输入部署名称 — Hermes 不会根据返回的列表进行验证。

## 环境变量

| 变量 | 用途 |
|----------|---------|
| `AZURE_FOUNDRY_API_KEY` | Azure AI Foundry / Azure OpenAI 的主要 API 密钥 |
| `AZURE_FOUNDRY_BASE_URL` | 端点 URL（通过 `hermes model` 设置；环境变量用作回退） |
| `AZURE_ANTHROPIC_KEY` | 由 `provider: anthropic` + Azure 基础 URL 使用（替代 `ANTHROPIC_API_KEY`） |

## 故障排除

**gpt-5.x 部署出现 401 未授权。**
Azure 在 `/chat/completions` 上提供 gpt-5.x，而不是 `/responses`。当 URL 包含 `openai.azure.com` 时，Hermes 会自动处理此问题，但如果您看到带有 `Invalid API key` 正文的 401 错误，请检查 `config.yaml` 中的 `api_mode` 是否为 `chat_completions`。

**在 `/v1/messages?api-version=.../v1/messages` 上出现 404。**
这是修复前 Azure Anthropic 设置中的 URL 格式错误问题。升级 Hermes — `api-version` 参数现在通过 `default_query` 传递，而不是硬编码到基础 URL 中，因此 SDK 在 URL 连接过程中无法破坏它。

**向导显示“自动检测不完整。”**
端点拒绝了 `/models` 探测和 Anthropic Messages 探测。这对于防火墙后或具有 IP 允许列表的私有端点是正常的。回退到手动选择 API 模式并输入您的部署名称 — 一切仍然有效，Hermes 只是无法预填充选择器。

**选择了错误的传输协议。**
再次运行 `hermes model`，向导将重新探测。如果探测仍然选择了错误的模式，您可以直接编辑 `config.yaml`：

```yaml
model:
  provider: azure-foundry
  api_mode: anthropic_messages   # 或 chat_completions
```

## 相关链接

-   [环境变量](/docs/reference/environment-variables)
-   [配置](/docs/user-guide/configuration)
-   [AWS Bedrock](/docs/guides/aws-bedrock) — 另一个主要的云提供商集成