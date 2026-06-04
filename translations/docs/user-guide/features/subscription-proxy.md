---
sidebar_position: 15
title: "订阅代理"
description: "将您的 Nous Portal 订阅（或其他 OAuth 提供商）用作外部应用的 OpenAI 兼容端点"
---

# 订阅代理

订阅代理是一个本地 HTTP 服务器，它允许外部应用 —— OpenViking、Karakeep、Open WebUI，任何支持 OpenAI 兼容聊天补全的应用 —— 将您由 Hermes 管理的提供商订阅用作其 LLM 端点。代理会附加正确的凭据（并自动刷新），因此应用永远不需要静态 API 密钥。

这与 [API 服务器](./api-server.md) 不同：

| | API 服务器 | 订阅代理 |
|---|---|---|
| 提供内容 | 您的 Agent（完整工具集、记忆、技能） | 原始模型推理 |
| 使用场景 | "将 Hermes 用作聊天后端" | "在另一个应用中使用我的 Portal 订阅" |
| 认证 | 您的 `API_SERVER_KEY` | 任意持有者令牌（代理会附加真实的令牌） |
| 工具调用 | 是 —— Agent 会运行工具 | 否 —— 仅透传 |
| | | |

当您希望将 **Agent** 作为后端时，请使用 API 服务器。当您只想通过您的订阅使用 **模型** 时，请使用代理。

## 快速开始

### 1. 登录到您的提供商（一次性操作）

```bash
hermes portal
```

这将在浏览器中打开 Nous Portal 的 OAuth 流程。Hermes 将刷新令牌存储在 `~/.hermes/auth.json` 中 —— 所有 Hermes 提供商登录信息都存储在此处。

### 2. 启动代理

```bash
hermes proxy start
```

```
正在为 Nous Portal 启动 Hermes 代理
  监听地址： http://127.0.0.1:8645/v1
  转发至： (根据您的订阅按请求解析)
  在客户端中使用任意持有者令牌 —— 代理会附加您的真实凭据。
```

让它在前台保持运行。如果您希望它在注销后继续运行，请使用 `tmux`、`nohup` 或 systemd 单元。

### 3. 将您的应用指向它

任何 OpenAI 兼容的应用配置都采用相同的三项设置：

```
基础 URL：   http://127.0.0.1:8645/v1
API 密钥：    任意值 (例如 "sk-unused")
模型：      Hermes-4-70B    # 或 Hermes-4.3-36B, Hermes-4-405B
```

代理会忽略来自您应用的 `Authorization` 请求头，并将您真实的 Portal 凭据附加到上游请求。当持有者令牌接近过期时，会自动刷新。

## 可用的提供商

```bash
hermes proxy providers
```

当前已提供：`nous` (Nous Portal) 和 `xai` (xAI / Grok)。可以通过在 `hermes_cli/proxy/adapters/` 中实现 `UpstreamAdapter` 接口来添加更多 OAuth 提供商。

## 检查状态

```bash
hermes proxy status
```

```
Hermes 代理上游适配器

  [nous    ] Nous Portal — 就绪 (持有者令牌过期时间 2026-05-15T06:43:21Z)
```

如果您看到 `not logged in`，请运行 `hermes portal`。如果您看到 `credentials need attention`，则表示您的刷新令牌已被撤销（很少见 —— 如果您从 Portal Web UI 注销则会发生）—— 只需重新运行 `hermes portal`。

## 允许的路径

代理仅转发上游实际服务的路径。对于 Nous Portal：

| 路径 | 用途 |
|------|---------|
| `/v1/chat/completions` | 聊天补全（流式 + 非流式） |
| `/v1/completions` | 旧版文本补全 |
| `/v1/embeddings` | 嵌入 |
| `/v1/models` | 模型列表 |

其他路径 (`/v1/images/generations`, `/v1/audio/speech` 等) 将返回 404 并附带指向允许路径的明确错误信息。这可以防止杂散的客户端将奇怪的请求泄露给上游。

## 配置 OpenViking 以使用 Portal

[OpenViking](https://github.com/volcengine/OpenViking) 是一个上下文数据库，其 VLM（用于提取记忆的视觉/语言模型）和嵌入模型需要一个 LLM 提供商。通过代理，您可以将它的 `vlm.api_base` 指向您的本地代理：

编辑 `~/.openviking/ov.conf`：

```json
{
  "vlm": {
    "provider": "openai",
    "model": "Hermes-4-70B",
    "api_base": "http://127.0.0.1:8645/v1",
    "api_key": "unused-proxy-attaches-real-creds"
  }
}
```

然后在终端中与 `openviking-server` 一起启动您的代理：

```bash
# 终端 1
hermes proxy start

# 终端 2
openviking-server
```

现在，OpenViking 的 VLM 调用将通过您的 Portal 订阅进行。嵌入模型端仍然需要自己的提供商 —— Portal 确实提供 `/v1/embeddings`，但模型选择取决于您的订阅等级支持哪些模型；请查看 `portal.nousresearch.com/models`。

## 配置 Karakeep（或任何书签/摘要应用）

[Karakeep](https://karakeep.app/) 需要一个 OpenAI 兼容的 API 来进行书签摘要。在其配置中：

```bash
# Karakeep .env
OPENAI_API_BASE_URL=http://127.0.0.1:8645/v1
OPENAI_API_KEY=any-non-empty-string
INFERENCE_TEXT_MODEL=Hermes-4-70B
```

相同的模式适用于 Open WebUI、LobeChat、NextChat 或任何其他 OpenAI 兼容的客户端。

## 在局域网上暴露

默认情况下，代理绑定到 `127.0.0.1`（仅限本地主机）。要让您网络上的其他机器使用它：

```bash
hermes proxy start --host 0.0.0.0 --port 8645
```

⚠ **请注意：** 现在您网络上的任何人都可以使用您的 Portal 订阅。代理本身没有认证机制 —— 它接受任何持有者令牌。如果您将此服务暴露在受信任网络之外，请使用防火墙、VPN 或带有适当认证的反向代理。

## 速率限制

您的 Portal 订阅等级的 RPM/TPM 限制适用于整个代理。代理不会进行扇出或池化 —— 它是一个使用您完整订阅配额的单一持有者令牌。请在 [portal.nousresearch.com](https://portal.nousresearch.com) 监控使用情况。

## 架构

代理的设计是极简的。每个请求的处理流程如下：

1.  从您的应用接收 `POST /v1/chat/completions`
2.  查找适配器的当前凭据（如果即将过期则刷新）
3.  原样转发请求体，并附带 `Authorization: Bearer <minted-key>`
4.  将响应流原封不动地传回（保留 SSE）

没有转换。不记录请求体。没有 Agent 循环。代理只是一个附加凭据的透传服务。

## 未来：更多 OAuth 提供商

适配器系统是可插拔的。添加新的提供商（例如 HuggingFace、GitHub Copilot 的聊天端点、通过 OAuth 的 Anthropic）需要在 `hermes_cli/proxy/adapters/<provider>.py` 中实现 `UpstreamAdapter`，并在 `adapters/__init__.py` 中注册。在协议级别不兼容 OpenAI 的提供商（例如 Anthropic Messages API）将需要一个转换层，这超出了当前设计范围。