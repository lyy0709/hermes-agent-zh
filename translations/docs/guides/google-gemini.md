---
sidebar_position: 16
title: "Google Gemini"
description: "在 Hermes Agent 中使用 Google Gemini —— 原生 AI Studio API、API 密钥设置、OAuth 选项、工具调用、流式传输和配额指南"
---

# Google Gemini

Hermes Agent 支持将 Google Gemini 作为原生提供商，使用 **Google AI Studio / Gemini API** —— 而非 OpenAI 兼容的端点。这使得 Hermes 能够将其内部 OpenAI 格式的消息和工具循环转换为 Gemini 原生的 `generateContent` API，同时保留工具调用、流式传输、多模态输入以及 Gemini 特定的响应元数据。

Hermes 还支持一个独立的 **Google Gemini (OAuth)** 提供商，该提供商使用与 Google 的 Gemini CLI 相同的 Cloud Code Assist 后端。对于风险最低的官方 API 路径，请使用 API 密钥提供商 (`gemini`)。

## 前提条件

- **Google AI Studio API 密钥** — 在 [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 创建
- **已启用计费的 Google Cloud 项目** — 推荐用于 Agent 使用。Gemini 的免费层级对于长时间运行的 Agent 会话来说太小，因为 Hermes 可能在每个用户回合中进行多次模型调用。
- **已安装 Hermes** — 原生 Gemini 提供商无需额外的 Python 包。

:::tip API 密钥路径
设置 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`。Hermes 会为 `gemini` 提供商检查这两个名称。
:::

## 快速开始

```bash
# 添加你的 Gemini API 密钥
echo "GOOGLE_API_KEY=..." >> ~/.hermes/.env

# 选择 Gemini 作为你的提供商
hermes model
# → 选择 "More providers..." → "Google AI Studio"
# → Hermes 检查你的密钥层级并显示 Gemini 模型
# → 选择一个模型

# 开始聊天
hermes chat
```

如果你更喜欢直接编辑配置，请使用原生的 Gemini API 基础 URL：

```yaml
model:
  default: gemini-3-flash-preview
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

## 配置

运行 `hermes model` 后，你的 `~/.hermes/config.yaml` 将包含：

```yaml
model:
  default: gemini-3-flash-preview
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

在 `~/.hermes/.env` 中：

```bash
GOOGLE_API_KEY=...
```

### 原生 Gemini API

推荐的端点是：

```text
https://generativelanguage.googleapis.com/v1beta
```

Hermes 检测到此端点并创建其原生 Gemini 适配器。在内部，Hermes 仍将 Agent 循环保持在 OpenAI 格式的消息中，然后将每个请求转换为 Gemini 的原生模式：

- `messages[]` → Gemini `contents[]`
- 系统提示词 → Gemini `systemInstruction`
- 工具模式 → Gemini `functionDeclarations`
- 工具结果 → Gemini `functionResponse` 部分
- 流式响应 → 为 Hermes 循环准备的 OpenAI 格式的流式数据块

:::note Gemini 3 思维签名
对于 Gemini 3 的工具使用，Hermes 会保留附加到函数调用部分的 `thoughtSignature` 值，并在下一个工具回合中回放它们。这涵盖了多步骤 Agent 工作流中验证关键路径。

Gemini 3 也可能将思维签名附加到其他响应部分。Hermes 的原生适配器目前针对 Agent 工具循环进行了优化，因此尚不能以完整的部分级保真度回放每个非工具调用的签名。
:::

### 推荐使用原生端点

Google 也提供了一个 OpenAI 兼容的端点：

```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

对于 Hermes Agent 会话，推荐使用上述原生 Gemini 端点。Hermes 包含一个原生 Gemini 适配器，因此它可以将多轮工具使用、工具调用结果、流式传输、多模态输入和 Gemini 响应元数据直接映射到 Gemini 的 `generateContent` API。当你特别需要 OpenAI API 兼容性时，OpenAI 兼容的端点仍然有用。

如果你之前将 `GEMINI_BASE_URL` 设置为 `/openai` URL，请移除或更改它：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

### OAuth 提供商

Hermes 还有一个 `google-gemini-cli` 提供商：

```bash
hermes model
# → 选择 "Google Gemini (OAuth)"
```

这使用浏览器 PKCE 登录和 Cloud Code Assist 后端。对于希望使用 Gemini CLI 风格 OAuth 的用户来说可能有用，但 Hermes 会显示明确警告，因为 Google 可能将第三方软件使用 Gemini CLI OAuth 客户端视为违反政策。对于生产或最低风险使用，推荐使用上述 API 密钥提供商。

## 可用模型

`hermes model` 选择器显示了 Hermes 提供商注册表中维护的 Gemini 模型。常见选择包括：

| 模型 | ID | 备注 |
|-------|----|-------|
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | 可用时能力最强的预览模型 |
| Gemini 3 Pro Preview | `gemini-3-pro-preview` | 强大的推理和编码模型 |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | 推荐的速度与能力平衡的默认选择 |
| Gemini 3.1 Flash Lite Preview | `gemini-3.1-flash-lite-preview` | 可用时最快/成本最低的选项 |

模型可用性会随时间变化。如果某个模型消失或未为你的密钥启用，请再次运行 `hermes model` 并从当前列表中选择一个。

:::info 模型 ID
当 `provider: gemini` 时，请使用 Gemini 的原生模型 ID，例如 `gemini-3-flash-preview`，而不是 OpenRouter 风格的 ID，如 `google/gemini-3-flash-preview`。
:::

### 最新别名

Google 为 Pro 和 Flash Gemini 系列发布了移动别名。当你希望 Google 自动推进模型而无需更改 Hermes 配置时，`gemini-pro-latest` 和 `gemini-flash-latest` 很有用。

| 别名 | 当前追踪 | 备注 |
|-------|------------------|-------|
| `gemini-pro-latest` | 最新的 Gemini Pro 模型 | 当你想要 Google 当前的 Pro 默认值时最佳 |
| `gemini-flash-latest` | 最新的 Gemini Flash 模型 | 当你想要 Google 当前的 Flash 默认值时最佳 |

```yaml
model:
  default: gemini-pro-latest
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

如果你需要严格的可复现性，请优先使用明确的模型 ID，例如 `gemini-3.1-pro-preview` 或 `gemini-3-flash-preview`。

### 通过 Gemini API 使用 Gemma

Google 也通过 Gemini API 公开了 Gemma 模型。Hermes 将这些识别为 Google 模型，但默认模型选择器中隐藏了吞吐量非常低的 Gemma 条目，以免新用户为长时间运行的 Agent 会话意外选择评估层级的模型。

有用的评估 ID 包括：

| 模型 | ID | 备注 |
|-------|----|-------|
| Gemma 4 31B IT | `gemma-4-31b-it` | 更大的 Gemma 模型；用于兼容性和质量评估 |
| Gemma 4 26B A4B IT | `gemma-4-26b-a4b-it` | 可用时较小的活动参数变体 |

这些模型最好作为 Gemini API 密钥上的评估选项。Google 的 Gemma API 定价仅为免费层级，且使用上限与生产 Gemini 模型相比很低，因此持续的 Hermes Agent 使用通常应转移到付费 Gemini 模型、自托管部署或具有适当配额的其他提供商。

要使用选择器中隐藏的 Gemma 模型，请直接设置：

```yaml
model:
  default: gemma-4-31b-it
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

## 会话中切换模型

在对话中使用 `/model` 命令：

```text
/model gemini-3-flash-preview
/model gemini-flash-latest
/model gemini-3-pro-preview
/model gemini-pro-latest
/model gemma-4-31b-it
/model gemini-3.1-flash-lite-preview
```

如果你尚未配置 Gemini，请先退出会话并运行 `hermes model`。`/model` 在已配置的提供商和模型之间切换；它不会收集新的 API 密钥。

## 诊断

```bash
hermes doctor
```

诊断程序检查：

- `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` 是否可用
- `google-gemini-cli` 的 Gemini OAuth 凭据是否存在
- 配置的提供商凭据是否可以解析

对于 OAuth 配额使用情况，请在 Hermes 会话中运行：

```text
/gquota
```

`/gquota` 适用于 `google-gemini-cli` OAuth 提供商，而非 AI Studio API 密钥提供商。

## 消息网关（消息平台）

Gemini 适用于所有 Hermes 消息网关平台（Telegram、Discord、Slack、WhatsApp、LINE、飞书等）。将 Gemini 配置为你的提供商，然后正常启动网关：

```bash
hermes gateway setup
hermes gateway start
```

网关读取 `config.yaml` 并使用相同的 Gemini 提供商配置。

## 故障排除

### "Gemini native client requires an API key"

Hermes 找不到可用的 API 密钥。将以下之一添加到 `~/.hermes/.env`：

```bash
GOOGLE_API_KEY=...
# 或
GEMINI_API_KEY=...
```

然后再次运行 `hermes model`。

### "This Google API key is on the free tier"

Hermes 在设置期间探测 Gemini API 密钥。免费层级的配额可能在几次 Agent 回合后耗尽，因为工具使用、重试、压缩和辅助任务可能需要多次模型调用。

在附加到你的密钥的 Google Cloud 项目上启用计费，如果需要则重新生成密钥，然后运行：

```bash
hermes model
```

### "404 model not found"

所选模型对你的账户、区域或密钥不可用。再次运行 `hermes model` 并从当前列表中选择另一个 Gemini 模型。

### Gemma 模型未在 `hermes model` 中显示

Hermes 可能默认从选择器中隐藏低吞吐量的 Gemma 模型。如果你有意评估某个模型，请在 `~/.hermes/config.yaml` 中直接设置模型 ID。

### Gemma 上出现 "429 quota exceeded"

通过 Gemini API 公开的 Gemma 模型对于评估很有用，但其 Gemini API 免费层级上限很低。将它们用于兼容性测试，然后切换到付费 Gemini 模型或其他提供商以进行持续的 Agent 会话。

### 配置了 OpenAI 兼容端点

检查 `~/.hermes/.env` 中是否有：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

将其更改为原生端点或移除覆盖：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

### OAuth 登录警告

`google-gemini-cli` 提供商使用 Gemini CLI / Cloud Code Assist OAuth 流程。Hermes 在启动前会发出警告，因为这不同于官方的 AI Studio API 密钥路径。对于官方 API 密钥集成，请使用带有 `GOOGLE_API_KEY` 的 `provider: gemini`。

### 工具调用因模式错误而失败

升级 Hermes 并重新运行 `hermes model`。原生 Gemini 适配器会为 Gemini 更严格的函数声明格式清理工具模式；旧版本或自定义端点可能不会。

## 相关

- [AI 提供商](/docs/integrations/providers)
- [配置](/docs/user-guide/configuration)
- [备用提供商](/docs/user-guide/features/fallback-providers)
- [AWS Bedrock](/docs/guides/aws-bedrock) — 使用 AWS 凭据的原生云提供商集成