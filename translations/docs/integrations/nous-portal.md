---
sidebar_position: 1
title: "Nous Portal"
description: "一个订阅，300+ 前沿模型，工具网关，以及 Nous Chat —— 运行 Hermes Agent 的推荐方式"
---

# Nous Portal

[Nous Portal](https://portal.nousresearch.com) 是 Nous Research 的统一订阅网关，也是**运行 Hermes Agent 的推荐方式**。一次 OAuth 登录，即可替代原本需要手动配置的、分散在各个模型实验室、搜索 API、图像生成器和浏览器提供商之间的独立账户、API 密钥和账单关系。

如果你只有时间设置一样东西，那就设置这个。最快的路径：

```bash
hermes setup --portal
```

这一条命令会运行 Portal OAuth 认证，在 `config.yaml` 中将 Nous 设置为你的推理提供商，并开启工具网关。之后你就可以立即开始 `hermes chat`。

还没有订阅？访问 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) —— 注册后，回来运行上面的命令。

## 订阅包含什么

### 300+ 前沿模型，一张账单

Portal 代理了整个生态系统中精选的代理式模型目录 —— 费用计入你的 Nous 订阅，而不是每个实验室单独的信用余额。

| 系列 | 模型 |
|--------|--------|
| **Anthropic Claude** | Opus, Sonnet, Haiku (4.x 系列) |
| **OpenAI** | GPT-5.4, o 系列推理模型 |
| **Google Gemini** | 2.5 Pro, 2.5 Flash |
| **DeepSeek** | DeepSeek V3.2, DeepSeek-R1 |
| **Qwen** | Qwen3 系列, Qwen Coder |
| **Kimi / Moonshot** | Kimi-K2, Kimi-Latest |
| **GLM / Zhipu** | GLM-4.6, GLM-4-Plus |
| **MiniMax** | M2.7, M1 |
| **xAI** | Grok-4, Grok-3 |
| **Hermes** | Hermes-4-70B, Hermes-4-405B (聊天，见[下方说明](#关于-hermes-4-的说明)) |
| **+ 其他所有** | 240+ 额外模型 —— 完整的代理式前沿 |

底层路由通过 OpenRouter 实现，因此模型可用性和故障转移行为与你使用 OpenRouter 密钥时相同 —— 只是费用计入你的 Nous 订阅。你可以在会话中通过 `/model` 在 Claude Sonnet 4.6（用于代码）和 Gemini 2.5 Pro（用于长上下文）之间切换 —— 无需新凭证，无需充值，没有意外的零余额错误。

### Nous 工具网关

同一个订阅还解锁了[工具网关](/docs/user-guide/features/tool-gateway)，它将 Hermes Agent 的工具调用路由到 Nous 管理的基础设施。五个后端，一次登录：

| 工具 | 合作伙伴 | 功能 |
|------|---------|--------------|
| **网络搜索与提取** | Firecrawl | Agent 级别的搜索和整页提取。无需 Firecrawl API 密钥，无需担心速率限制。 |
| **图像生成** | FAL | 一个端点下包含九个模型：FLUX 2 Klein 9B, FLUX 2 Pro, Z-Image Turbo, Nano Banana Pro (Gemini 3 Pro Image), GPT Image 1.5, GPT Image 2, Ideogram V3, Recraft V4 Pro, Qwen Image。 |
| **文本转语音** | OpenAI TTS | 高质量的 TTS，无需单独的 OpenAI 密钥。支持跨消息平台的[语音模式](/docs/user-guide/features/voice-mode)。 |
| **云端浏览器自动化** | Browser Use | 用于 `browser_navigate`、`browser_click`、`browser_type`、`browser_vision` 的无头 Chromium 会话。无需 Browserbase 账户。 |
| **云端终端沙盒** | Modal | 用于代码执行的无服务器终端沙盒（可选附加组件）。 |

如果没有网关，连接上述每个工具意味着需要一个 Firecrawl 账户、一个 FAL 账户、一个 Browser Use 账户、一个 OpenAI 密钥和一个 Modal 账户 —— 五个独立的注册、五个独立的仪表盘、五个独立的充值流程。有了网关，所有这些都通过一个订阅进行路由。

你也可以仅启用特定的网关工具（例如，仅启用网络搜索而不启用图像生成）—— 请参阅下方的[混合使用网关与你自己的后端](#混合使用网关与你自己的后端)。

### Nous Chat

你的 Portal 账户也覆盖了 [chat.nousresearch.com](https://chat.nousresearch.com) —— Nous Research 的网页聊天界面，拥有相同的模型目录。当你远离终端时，或者进行非 Agent 对话工作时，这很有用。

### 配置文件中没有凭证

因为所有内容都通过一个经过 OAuth 认证的 Portal 会话进行路由，所以你不会有包含十几个长期有效 API 密钥的 `.env` 文件。位于 `~/.hermes/auth.json` 的刷新令牌是磁盘上唯一的凭证，Hermes 会为每个请求从中生成短期 JWT —— 请参阅下方的[令牌处理](#令牌处理)。

### 跨平台一致性

[原生 Windows](/docs/user-guide/windows-native) 仍处于早期测试阶段，按工具配置 API 密钥是其难点 —— 在 Windows 上安装 Firecrawl 账户、FAL 账户、Browser Use 账户、OpenAI 密钥是获得一个有用 Agent 过程中摩擦最大的部分。Portal 订阅解决了这个问题：一次 OAuth 认证覆盖了模型和所有网关工具，因此 Windows 用户无需手动配置四个后端，就能获得与 macOS/Linux 相同的体验。

## 关于 Hermes 4 的说明

Nous Research 自家的 **Hermes 4** 系列（Hermes-4-70B, Hermes-4-405B）可通过 Portal 以大幅折扣的价格使用。这些是**前沿的混合推理聊天模型** —— 在数学、科学、指令遵循、模式遵守、角色扮演和长篇写作方面表现出色。

然而，**不建议在 Hermes Agent 内部使用它们**。Hermes 4 是针对聊天和推理进行微调的，而不是 Agent 所依赖的快速工具调用循环。请将它们用于 [Nous Chat](https://chat.nousresearch.com)、研究工作流，或通过其他工具的[订阅代理](/docs/user-guide/features/subscription-proxy)使用 —— 但对于 Agent 工作，请从目录中选择一个前沿的代理式模型：

```bash
/model anthropic/claude-sonnet-4.6     # 最佳通用代理式模型
/model openai/gpt-5.4                  # 强大的推理 + 工具调用
/model google/gemini-2.5-pro           # 巨大的上下文窗口
/model deepseek/deepseek-v3.2          # 性价比高的编码器
```

Portal 自己的[模型信息页面](https://portal.nousresearch.com/info)也带有相同的警告，所以这不是 Hermes 单方面的观点 —— 这是来自 Nous Research 的官方指导。
## 设置

### 全新安装 — 一条命令

```bash
hermes setup --portal
```

这条命令会一次性完成完整设置：

1. 在浏览器中打开 portal.nousresearch.com 进行 OAuth 登录
2. 将刷新令牌存储在 `~/.hermes/auth.json`
3. 在 `~/.hermes/config.yaml` 中将 Nous 设置为你的推理提供商
4. 开启工具网关（网页搜索、图像生成、文本转语音、浏览器自动化路由）
5. 返回终端，准备使用 `hermes chat`

如果你还没有订阅，请先访问 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 注册。

### 现有安装 — 在其他提供商基础上添加 Portal

如果你已经配置了 Hermes 使用 OpenRouter、Anthropic 或其他任何提供商，并且想在它们的基础上添加 Portal：

```bash
hermes model
# 从提供商列表中选择 "Nous Portal"
# 浏览器打开，登录，完成
```

你现有的提供商配置保持不变。你可以在会话中使用 `/model` 切换，或在会话之间使用 `hermes model` 切换 — Portal 会成为你可用的提供商之一，而不是唯一的提供商。

### 无头模式 / SSH / 远程设置

OAuth 需要浏览器，但环回回调运行在 Hermes 所在的机器上。对于远程主机，请参阅 [OAuth over SSH / Remote Hosts](/docs/guides/oauth-over-ssh) — 适用于 Portal 的模式与任何其他基于 OAuth 的提供商相同（`ssh -L` 端口转发，对于 Cloud Shell / Codespaces 等纯浏览器环境使用 `--manual-paste`）。

### 配置文件设置

如果你使用 [Hermes 配置文件](/docs/user-guide/profiles)，Portal 刷新令牌会通过共享令牌存储自动在所有配置文件间共享。在任何配置文件中登录一次，其余配置文件会自动获取 — 无需为每个配置文件重复 OAuth 流程。

## 日常使用 Portal

### 检查已配置的内容

```bash
hermes portal status     # 登录状态、订阅信息、模型和网关路由
hermes portal tools      # 详细的工具网关目录，包含每个工具的路由
hermes portal open       # 在浏览器中打开订阅管理页面
```

`hermes portal status`（或仅 `hermes portal`）提供高级概览：

```
  Nous Portal
  ───────────
  认证：    ✓ 已登录
  Portal：  https://portal.nousresearch.com
  模型：    ✓ 使用 Nous 作为推理提供商

  工具网关
  ────────────
  网页搜索与提取  通过 Nous Portal
  图像生成       通过 Nous Portal
  文本转语音     通过 Nous Portal
  浏览器自动化   通过 Nous Portal
  云端终端       未配置
```

### 切换模型

在会话内部：

```bash
/model anthropic/claude-sonnet-4.6
/model openai/gpt-5.4
/model google/gemini-2.5-pro
```

或打开选择器：

```bash
/model
# 使用方向键，回车选择
```

在会话外部（完整的设置向导，添加新提供商时很有用）：

```bash
hermes model
```

### 将网关与你自己的后端混合使用

如果你已经拥有，例如，一个 Browserbase 账户，并希望在通过 Nous 路由网页搜索和图像生成的同时继续使用它，这是支持的。使用 `hermes tools` 为每个工具选择后端：

```bash
hermes tools
# → 网页搜索       → "Nous Subscription"
# → 图像生成       → "Nous Subscription"
# → 浏览器         → "Browserbase"  (你现有的密钥)
# → 文本转语音     → "Nous Subscription"
```

工具网关是按工具选择加入的，不是全有或全无。完整的按工具配置矩阵请参阅 [工具网关文档](/docs/user-guide/features/tool-gateway)。

### 订阅管理

随时管理你的套餐、查看使用情况或升级/取消：

- **网页：** [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)
- **CLI 快捷方式：** `hermes portal open`（在默认浏览器中打开同一页面）

## 配置参考

运行 `hermes setup --portal` 后，`~/.hermes/config.yaml` 将如下所示：

```yaml
model:
  provider: nous
  default: anthropic/claude-sonnet-4.6     # 或你选择的任何模型
  base_url: https://inference.nousresearch.com/v1
```

工具网关设置位于其各自的工具部分下：

```yaml
web:
  backend: nous       # 网页搜索/提取通过工具网关路由

image_gen:
  provider: nous

tts:
  provider: nous

browser:
  backend: nous
```

OAuth 刷新令牌单独存储在 `~/.hermes/auth.json`（不在 `config.yaml` 中 — 凭据和配置在设计上是分开的）。

## Token 处理

Hermes 在每次推理调用时，从你存储的 Portal 刷新令牌中生成一个短期的 JWT，而不是重复使用一个长期有效的 API 密钥。Token 的生命周期是完全自动的 — 刷新、生成、在临时 401 错误时重试 — 你永远看不到它。

如果 Portal 使刷新令牌失效（密码更改、手动撤销、会话过期），失效的刷新令牌会在**本地被隔离**，这样 Hermes 就不会重复使用它，你也不会看到一连串相同的 401 错误。下一次调用会显示清晰的“需要重新认证”消息。运行 `hermes auth add nous` 重新登录；隔离会在下次成功登录时自动清除。

## 故障排除

### `hermes portal status` 显示“未登录”

你尚未完成 OAuth 流程，或者你的刷新令牌已被清除。运行：

```bash
hermes auth add nous --type oauth
```

或使用 `hermes model` 并重新选择 Nous Portal。

### 在会话中收到“需要重新认证”消息

你的 Portal 刷新令牌已失效（密码更改、手动撤销或会话过期）。运行 `hermes auth add nous`，你的下一个请求将使用新的凭据。旧令牌的任何隔离都会在成功重新登录后自动清除。

### 想使用 Portal 未公开的特定提供商模型

Portal 通过 OpenRouter 代理，因此 OpenRouter 支持的任何模型通常都可用。如果特定模型没有出现在 `/model` 中，请直接尝试 OpenRouter 风格的 slug：

```bash
/model anthropic/claude-opus-4.6
```

如果某个模型确实缺失，请[提交问题](https://github.com/NousResearch/hermes-agent/issues) — 我们将 Portal 的目录提供给 Hermes，缺失通常意味着我们可以更新的路由配置。
### 我的 Portal 账户中未显示账单

首先检查 `hermes portal status` —— 如果显示您正在使用不同的提供商（显示 `Model: currently openrouter` 而不是 `using Nous as inference provider`），则您的本地配置已发生偏移。运行 `hermes model`，选择 Nous Portal，下一个请求将通过您的订阅路由。

## 另请参阅

- **[工具网关](/docs/user-guide/features/tool-gateway)** — 每个网关工具的完整详细信息、每个工具的配置和定价
- **[订阅代理](/docs/user-guide/features/subscription-proxy)** — 在非 Hermes 工具（其他 Agent、脚本、第三方客户端）中使用您的 Portal 订阅
- **[语音模式](/docs/user-guide/features/voice-mode)** — 使用 Portal 的 OpenAI TTS 进行语音对话
- **[AI 提供商](/docs/integrations/providers)** — 完整的提供商目录，如果您想比较替代方案
- **[通过 SSH 进行 OAuth](/docs/guides/oauth-over-ssh)** — 从远程主机或仅浏览器环境登录
- **[配置文件](/docs/user-guide/profiles)** — 共享一个 Portal 登录的多个 Hermes 配置