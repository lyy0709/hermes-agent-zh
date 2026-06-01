---
title: "Nous 工具网关"
description: "一次订阅，所有工具。网络搜索、图像生成、TTS 和云浏览器——全部通过 Nous Portal 路由，无需额外 API 密钥。"
sidebar_label: "工具网关"
sidebar_position: 2
---

# Nous 工具网关

**一次订阅。内置所有工具。**

工具网关包含在每个付费的 [Nous Portal](https://portal.nousresearch.com) 订阅中。它将 Hermes 的工具调用——网络搜索、图像生成、文本转语音和云浏览器自动化——路由到 Nous 已运行的基础设施中，因此您无需为了使用 Agent 而单独注册 Firecrawl、FAL、OpenAI、Browser Use 或其他任何服务。

<div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', margin: '1.5rem 0'}}>
  <a href="https://portal.nousresearch.com/manage-subscription" style={{background: 'var(--ifm-color-primary)', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold'}}>开始或管理订阅 →</a>
</div>

## 包含内容

| | 工具 | 您将获得 |
|---|---|---|
| 🔍 | **网络搜索与提取** | 通过 Firecrawl 提供 Agent 级网络搜索和整页提取。无需担心速率限制——网关负责扩展。 |
| 🎨 | **图像生成** | 一个端点下包含九个模型：**FLUX 2 Klein 9B**、**FLUX 2 Pro**、**Z-Image Turbo**、**Nano Banana Pro**（Gemini 3 Pro Image）、**GPT Image 1.5**、**GPT Image 2**、**Ideogram V3**、**Recraft V4 Pro**、**Qwen Image**。可通过标志按次选择模型，或让 Hermes 默认使用 FLUX 2 Klein。 |
| 🔊 | **文本转语音** | 集成到 `text_to_speech` 工具中的 OpenAI TTS 语音。可将语音笔记发送到 Telegram，为流水线生成音频，为任何内容配音。 |
| 🌐 | **云浏览器自动化** | 通过 Browser Use 提供无头 Chromium 会话。`browser_navigate`、`browser_click`、`browser_type`、`browser_vision`——所有驱动 Agent 的基础操作，无需 Browserbase 账户。 |

所有四项服务均按使用量计费，费用计入您的 Nous 订阅。可以任意组合使用——通过网关运行网络和图像服务，同时保留自己的 ElevenLabs 密钥用于 TTS，或者将所有内容都通过 Nous 路由。

## 为何存在

构建一个真正能*做事*的 Agent 意味着要整合 5 个以上的 API 订阅——每个都有各自的注册、速率限制、计费和特性。网关将这一切整合到一个账户中：

- **一份账单。** 向 Nous 付款；我们处理其余事宜。
- **一次注册。** 无需管理 Firecrawl、FAL、Browser Use 或 OpenAI 音频账户。
- **一个密钥。** 您的 Nous Portal OAuth 覆盖所有工具。
- **相同质量。** 与直接使用密钥的路线相同的后端——只是由我们提供前端服务。

您可以随时使用自己的密钥——针对任何工具，随时可以切换。网关不是锁定，而是捷径。

## 开始使用

有三种方式进入——选择适合您当前情况的一种：

```bash
hermes setup --portal     # 全新安装：一次性完成 Nous OAuth + 设置 Nous 为提供商 + 开启工具网关
```

```bash
hermes model              # 将您的推理提供商切换到 Nous Portal——然后 Hermes 会提示为所有工具开启网关
```

```bash
hermes tools              # 按工具启用网关——为您想要的任何工具选择 "Nous Subscription"
```

`hermes setup --portal` 和 `hermes model` 是一次性完成的路径：登录一次，可选择将所有工具切换到网关。`hermes tools` 是按需选择的路径——一次只开启您想要的工具。

**您无需先登录。** 使用 `hermes tools` 时，Nous 管理的后端（网络搜索、图像、视频、TTS、浏览器）始终会列出，即使您从未登录过 Nous Portal。选择一个后端，如果您尚未通过身份验证，Hermes 会立即运行 Portal 登录——无需事先运行 `hermes model`。如果您的 Nous OAuth 已处于活动状态，选择后端会立即启用它，无需额外提示。此路径仅登录并开启您选择的那个工具——它**不会**切换您的推理提供商，也**不会**提示您为其他所有工具启用网关。

随时检查哪些功能处于活动状态：

```bash
hermes portal status      # Portal 身份验证 + 工具网关路由摘要
hermes portal tools       # 网关目录，显示每个工具的当前路由
hermes status             # 完整系统状态（工具网关是其中一个部分）
```

`hermes portal status` 会显示类似以下的部分：

```
◆ Nous 工具网关
  Nous Portal     ✓ 托管工具可用
  网络工具       ✓ 通过 Nous 订阅激活
  图像生成       ✓ 通过 Nous 订阅激活
  TTS             ✓ 通过 Nous 订阅激活
  浏览器         ○ 通过 Browser Use 密钥激活
```

标记为 "通过 Nous 订阅激活" 的工具正在通过网关。其他任何工具都在使用您自己的密钥。

## 资格

工具网关是一项**付费订阅**功能。免费层级的 Nous 账户可以使用 Portal 进行推理，但不包含托管工具——[升级您的计划](https://portal.nousresearch.com/manage-subscription)以解锁网关。

## 混合搭配

网关是按工具配置的。只为您想要的功能开启它：

- **所有工具通过 Nous**——最简单；一次订阅，完成。
- **网关用于网络 + 图像，自带 TTS**——保留您的 ElevenLabs 语音，让 Nous 处理其余部分。
- **仅对您没有密钥的功能使用网关**——"我已经为 Browserbase 付费，但不想注册 Firecrawl 账户" 完全可行。

随时通过以下方式切换任何工具：

```bash
hermes tools          # 每个工具类别的交互式选择器
```

选择工具，选择 **Nous Subscription** 作为提供商（或您喜欢的任何直接提供商）。无需编辑配置。如果您尚未登录 Nous Portal，选择 **Nous Subscription** 会启动内联 Portal 登录——您无需先通过 `hermes model` 进行身份验证。

## 使用单个图像模型

图像生成默认使用 FLUX 2 Klein 9B 以获得速度。可以通过将模型 ID 传递给 `image_generate` 工具来按调用覆盖：

| 模型 | ID | 最适合 |
|---|---|---|
| FLUX 2 Klein 9B | `fal-ai/flux-2/klein/9b` | 快速，良好的默认选择 |
| FLUX 2 Pro | `fal-ai/flux-2/pro` | 更高保真度的 FLUX |
| Z-Image Turbo | `fal-ai/z-image/turbo` | 风格化，快速 |
| Nano Banana Pro | `fal-ai/gemini-3-pro-image` | Google Gemini 3 Pro Image |
| GPT Image 1.5 | `fal-ai/gpt-image-1/5` | OpenAI 图像生成，文本+图像 |
| GPT Image 2 | `fal-ai/gpt-image-2` | OpenAI 最新版本 |
| Ideogram V3 | `fal-ai/ideogram/v3` | 强大的提示词遵循能力 + 排版 |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro` | 矢量风格，平面设计 |
| Qwen Image | `fal-ai/qwen-image` | 阿里巴巴多模态 |

模型集会不断更新——`hermes tools` → 图像生成 显示当前实时列表。

---

## 配置参考

大多数用户永远不需要接触此部分——`hermes model` 和 `hermes tools` 以交互方式涵盖了所有工作流。本节适用于直接编写 config.yaml 或编写设置脚本。

### 每个工具的 `use_gateway` 标志

每个工具的配置块都接受一个 `use_gateway` 布尔值：

```yaml
web:
  backend: firecrawl
  use_gateway: true

image_gen:
  use_gateway: true

tts:
  provider: openai
  use_gateway: true

browser:
  cloud_provider: browser-use
  use_gateway: true
```

优先级：`use_gateway: true` 会通过 Nous 路由，无论 `.env` 中是否存在任何直接密钥。`use_gateway: false`（或不存在）会使用直接密钥（如果可用），并且仅在不存在任何密钥时才回退到网关。

### 禁用网关

```yaml
web:
  use_gateway: false   # Hermes 现在使用 .env 中的 FIRECRAWL_API_KEY
```

`hermes tools` 在您选择非网关提供商时会自动清除该标志，因此这通常会自动为您完成。

### 自托管网关（高级）

运行您自己的 Nous 兼容网关？在 `~/.hermes/.env` 中覆盖端点：

```bash
TOOL_GATEWAY_DOMAIN=your-domain.example.com
TOOL_GATEWAY_SCHEME=https
TOOL_GATEWAY_USER_TOKEN=your-token        # 通常从 Portal 登录自动填充
FIRECRAWL_GATEWAY_URL=https://...         # 专门覆盖一个端点
```

这些选项适用于自定义基础设施设置（企业部署、开发环境）。普通订阅者无需设置它们。

## 常见问题

### 它是否适用于 Telegram / Discord / 其他消息网关？

是的。工具网关在工具执行层运行，而不是在 CLI 层。每个可以调用工具的接口——CLI、Telegram、Discord、Slack、IRC、Teams、API 服务器，任何东西——都能透明地从中受益。

### 如果我的订阅过期了会怎样？

通过网关路由的工具将停止工作，直到您续订或通过 `hermes tools` 换入直接 API 密钥。Hermes 会显示一个清晰的错误，指向 portal。

### 我可以查看每个工具的使用情况或成本吗？

可以——[Nous Portal 仪表板](https://portal.nousresearch.com) 按工具细分使用情况，以便您查看账单的驱动因素。

### Modal（无服务器终端）是否包含在内？

Modal 可作为**可选附加组件**通过 Nous 订阅获得，不属于默认工具网关捆绑包。当您需要用于 shell 执行的远程沙盒时，可以通过 `hermes setup terminal` 或直接在 `config.yaml` 中配置它。

### 启用网关时，是否需要删除现有的 API 密钥？

不需要——将它们保留在 `.env` 中。当 `use_gateway: true` 时，Hermes 会跳过直接密钥并使用网关。将标志切换回 `false`，您的密钥将再次成为来源。网关不是锁定。