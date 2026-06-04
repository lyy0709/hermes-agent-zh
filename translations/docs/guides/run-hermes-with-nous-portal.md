---
sidebar_position: 1
title: "使用 Nous Portal 运行 Hermes Agent"
description: "完整操作指南：订阅、设置、切换模型、启用消息网关工具，并验证路由"
---

# 使用 Nous Portal 运行 Hermes Agent

本指南将引导你从头到尾在 [Nous Portal](https://portal.nousresearch.com) 订阅上运行 Hermes Agent——从注册到验证每个工具的路由是否正确。如果你只想了解 Portal 是什么以及订阅包含什么内容，请参阅 [Nous Portal 集成页面](/integrations/nous-portal)。本页是具体的操作脚本。

## 前提条件

- 已安装 Hermes Agent（[快速开始](/getting-started/quickstart)）
- 你正在设置的机器上有一个网页浏览器（或使用 SSH 端口转发——参见 [通过 SSH 进行 OAuth](/guides/oauth-over-ssh)）
- 大约 5 分钟时间

你**不需要**：OpenAI 密钥、Anthropic 密钥、Firecrawl 账户、FAL 账户、Browser Use 账户或任何其他供应商的凭证。这就是它的全部意义所在。

## 1. 获取订阅

打开 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)，注册并选择一个套餐。

已经订阅了？跳到第 2 步。

## 2. 运行一键式设置

```bash
hermes setup --portal
```

这个单一命令完成五件事：

1. 在你的浏览器中打开 portal.nousresearch.com 进行 OAuth 登录
2. 将刷新令牌存储在 `~/.hermes/auth.json`
3. 在 `~/.hermes/config.yaml` 中设置 `model.provider: nous`
4. 选择一个默认的代理式模型（`anthropic/claude-sonnet-4.6` 或类似模型）
5. 为网络搜索、图像生成、TTS 和浏览器自动化启用工具消息网关

完成后，你将回到终端，准备开始聊天。

### 如果我通过 SSH 连接到服务器怎么办？

OAuth 需要浏览器，但环回回调运行在 Hermes 所在的机器上。有两个选项：

```bash
# 选项 A：SSH 端口转发（推荐）
ssh -N -L 8642:127.0.0.1:8642 user@remote-host    # 在本地终端中
hermes setup --portal                              # 在远程机器上，在你本地的浏览器中打开打印的 URL

# 选项 B：手动粘贴（适用于 Cloud Shell、Codespaces、EC2 Instance Connect）
hermes auth add nous --type oauth --manual-paste
# 然后重新运行 `hermes setup --portal` 来连接提供商 + 消息网关
```

有关完整指南，包括 ProxyJump 链、mosh/tmux 和 ControlMaster 的注意事项，请参阅 [通过 SSH / 远程主机进行 OAuth](/guides/oauth-over-ssh)。

## 3. 验证是否成功

```bash
hermes portal info
```

你应该看到：

```
  Nous Portal
  ───────────
  Auth:    ✓ 已登录
  Portal:  https://portal.nousresearch.com
  Model:   ✓ 使用 Nous 作为推理提供商

  工具消息网关
  ────────────
  网络搜索与提取  通过 Nous Portal
  图像生成        通过 Nous Portal
  文本转语音      通过 Nous Portal
  浏览器自动化    通过 Nous Portal
```

如果有任何一行显示的不是“通过 Nous Portal”或者认证行显示“未登录”，请跳转到下面的[故障排除](#troubleshooting)部分。

## 4. 运行你的第一次对话

```bash
hermes chat
```

尝试一些同时使用模型和工具消息网关的内容：

```
嘿，搜索一下“Hermes Agent 发布说明”，并总结前 3 条结果。
```

你应该看到 Hermes 调用 `web_search`（基于 Firecrawl，通过消息网关）并回复一个摘要。如果搜索运行正常且回复合理，那么你就完成了——Portal 已从头到尾配置完毕。

## 5. 选择你真正想要的模型

`hermes setup --portal` 允许你在设置过程中选择一个模型，但订阅的全部意义在于访问完整的模型目录——你可以在会话中随时使用 `/model` 切换：

```bash
/model anthropic/claude-sonnet-4.6     # 最佳通用代理式模型
/model openai/gpt-5.4                  # 强大的推理 + 工具调用能力
/model google/gemini-2.5-pro           # 巨大的上下文窗口
/model deepseek/deepseek-v3.2          # 性价比高的编码模型
/model anthropic/claude-opus-4.6       # 用于解决难题的重型模型
```

或者弹出选择器浏览：

```bash
/model
```

永久选择不同的默认模型：

```bash
# 在你的终端中，在任何会话之外
hermes config set model.default anthropic/claude-sonnet-4.6
```

### 不要为代理工作选择 Hermes-4

Hermes-4-70B 和 Hermes-4-405B 在 Portal 上以深度折扣提供，但它们是**聊天/推理模型**，不是为工具调用调优的。它们将在多步骤代理循环中遇到困难。通过 [Nous Chat](https://chat.nousresearch.com) 将它们用于对话/研究工作，或通过[订阅代理](/user-guide/features/subscription-proxy)从非代理工具中使用。对于 Hermes Agent 本身，请坚持使用上述前沿的代理式模型。

Portal 自己的[信息页面](https://portal.nousresearch.com/info)也带有此警告——这是官方的 Nous 指导，而不仅仅是 Hermes 一方的观点。

## 6. （可选）自定义工具消息网关路由

消息网关是按工具选择加入的，不是全有或全无。如果你已经有一个 Browserbase 账户，并希望在通过 Nous 路由网络搜索和图像生成的同时继续使用它，这是支持的：

```bash
hermes tools
# → 网络搜索       → "Nous 订阅"     (推荐)
# → 图像生成       → "Nous 订阅"     (推荐)
# → 浏览器         → "Browserbase"   (你现有的密钥)
# → TTS            → "Nous 订阅"     (推荐)
```

这些行在你登录 Nous Portal 之前就会出现在 `hermes tools` 中——如果你在没有活动会话的情况下选择“Nous 订阅”，Hermes 将内联运行 Portal 登录流程（不会更改你的推理提供商或其他工具）。

使用以下命令验证你的混合配置：

```bash
hermes portal tools
```

你将看到每个工具的路由——通过订阅路由的显示 `via Nous Portal`，使用你自己密钥的显示合作伙伴名称（`browserbase`、`firecrawl` 等）。

## 7. （可选）启用语音模式

因为工具消息网关包含 OpenAI TTS，所以[语音模式](/user-guide/features/voice-mode)无需单独的 OpenAI 密钥即可工作：

```bash
hermes setup voice
# → 为 TTS 选择 "Nous 订阅"
# → 选择一个语音转文本后端（本地 faster-whisper 是免费的，无需设置）
```

然后在任何消息平台会话（Telegram、Discord、Signal 等）中，发送一条语音消息，Hermes 将转录它、回复并用合成语音回复——所有这些都使用你的 Portal 订阅。

## 8. （可选）定时任务 + 常驻工作流

Portal 订阅适用于[定时任务](/user-guide/features/cron)和[批量处理](/user-guide/features/batch-processing)，其方式与交互式聊天相同——OAuth 刷新令牌会自动重用。无需额外设置；只需安排定时任务，它们就会计入你的订阅账单。

```bash
hermes cron create "every day at 9am" \
  "搜索网络上的顶级 AI 新闻并总结 5 个最重要的故事" \
  --name "每日 AI 新闻"
```

定时任务将无人值守运行，通过你的 Portal 订阅调用模型 + 网络搜索 + 摘要生成。

## 配置文件和多用户设置

如果你使用 [Hermes 配置文件](/user-guide/profiles)（例如，每个项目一个单独的配置），Portal 刷新令牌会通过共享令牌存储自动在所有配置文件之间共享。在任何配置文件上登录一次，其余的会自动获取。

对于多个人共享一台机器的团队设置，每个人都有自己的 Portal 账户 → 每个主目录都保存自己的 `~/.hermes/auth.json` → 用户之间不共享令牌。这是正确的边界。

## 故障排除

### `hermes portal info` 在 `hermes setup --portal` 后显示“未登录”

OAuth 流程未完成。重新运行它：

```bash
hermes portal
```

如果你的浏览器没有打开或回调失败，你可能在远程/无头主机上——请参阅 [通过 SSH 进行 OAuth](/guides/oauth-over-ssh) 了解端口转发和手动粘贴的解决方法。

### “Model: currently openrouter”（或其他提供商）而不是“using Nous as inference provider”

你的本地配置发生了偏移。OAuth 成功了，但 `model.provider` 仍然指向其他提供商。修复：

```bash
hermes config set model.provider nous
```

或者交互式操作：

```bash
hermes model
# 选择 Nous Portal
```

使用 `hermes portal info` 重新验证。

### 工具消息网关工具显示合作伙伴名称而不是“via Nous Portal”

每个工具的配置覆盖了消息网关。运行：

```bash
hermes tools
# 为你想要通过消息网关路由的任何工具选择 "Nous 订阅"
```

一些用户有意混合使用——例如，网络通过 Nous 路由，但使用自己的 Browserbase 密钥进行浏览器操作。如果这是有意的，请保持原样。如果不是，此命令将修复它。

### 会话中出现“需要重新认证”

你的 Portal 刷新令牌已失效（密码更改、手动撤销、会话过期）。该令牌现在在本地被隔离，因此 Hermes 不会无限重试。只需重新登录：

```bash
hermes auth add nous
```

成功重新登录后，隔离会自动清除。

### 我想要的模型不在 `/model` 选择器中

Portal 目录镜像了 OpenRouter 的模型列表（300+）。如果缺少某个模型，请尝试直接输入 OpenRouter 风格的 slug：

```bash
/model anthropic/claude-opus-4.6
/model openai/o1-2025-12-17
```

如果某个模型确实不可用，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)——大多数缺失是我们可以更新的路由配置。

### 我的 Portal 账户上没有显示账单

`hermes portal info` 会告诉你是否真的通过 Portal 路由，还是通过其他提供商。常见原因：

- `model.provider` 设置为 `openrouter`/`anthropic`/等，而不是 `nous`
- OAuth 刷新失败，回退到其他已配置的提供商
- 多个 Hermes 配置文件，而你使用了错误的配置文件（检查 `hermes profile current`）

### 想要撤销并重新开始

```bash
hermes auth remove nous       # 清除本地刷新令牌
# 然后重新运行设置或在 Portal 网页界面中移除订阅
```

## 你能得到什么，用数字说话

| 没有 Portal | 使用 Portal |
|----------------|-------------|
| 1× OpenRouter / Anthropic / OpenAI 密钥在 `.env` 中 | 1× OAuth 刷新令牌，没有 `.env` 密钥 |
| 1× Firecrawl 密钥用于网络 | 网络通过消息网关路由 |
| 1× FAL 密钥用于图像生成 | 图像生成通过消息网关路由 |
| 1× Browser Use / Browserbase 密钥用于浏览器 | 浏览器通过消息网关路由 |
| 1× OpenAI 密钥用于 TTS / 语音模式 | TTS 通过消息网关路由 |
| 5 个独立的仪表板、充值、发票 | 1 个订阅，1 张发票 |
| 跨机器：复制所有 5 个密钥 | 跨机器：重新 OAuth 一次 |

这就是交易。如果你无论如何都在使用其中两个以上的后端，订阅就能回本。

## 另请参阅

- **[Nous Portal 集成页面](/integrations/nous-portal)** — 订阅内容概述
- **[工具消息网关](/user-guide/features/tool-gateway)** — 每个通过消息网关路由的工具的完整详细信息
- **[订阅代理](/user-guide/features/subscription-proxy)** — 从非 Hermes 工具使用你的 Portal 订阅
- **[语音模式](/user-guide/features/voice-mode)** — 在 Portal 订阅上设置语音对话
- **[通过 SSH 进行 OAuth](/guides/oauth-over-ssh)** — 远程 / 无头登录模式
- **[配置文件](/user-guide/profiles)** — 在多个 Hermes 配置之间共享一个 Portal 登录