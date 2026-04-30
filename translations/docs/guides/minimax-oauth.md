---
sidebar_position: 15
title: "MiniMax OAuth"
description: "通过浏览器 OAuth 登录 MiniMax，并在 Hermes Agent 中使用 MiniMax-M2.7 模型 — 无需 API 密钥"
---

# MiniMax OAuth

Hermes Agent 通过基于浏览器的 OAuth 登录流程支持 **MiniMax**，使用与 [MiniMax 门户](https://www.minimax.io) 相同的凭据。无需 API 密钥或信用卡 — 登录一次，Hermes 会自动刷新您的会话。

传输层复用了 `anthropic_messages` 适配器（MiniMax 在 `/anthropic` 路径下暴露了一个与 Anthropic Messages 兼容的端点），因此所有现有的工具调用、流式传输和上下文功能无需任何适配器更改即可工作。

## 概述

| 项目 | 值 |
|------|-------|
| 提供商 ID | `minimax-oauth` |
| 显示名称 | MiniMax (OAuth) |
| 认证类型 | 浏览器 OAuth (PKCE 设备码流程) |
| 传输层 | 兼容 Anthropic Messages (`anthropic_messages`) |
| 模型 | `MiniMax-M2.7`, `MiniMax-M2.7-highspeed` |
| 全球端点 | `https://api.minimax.io/anthropic` |
| 中国端点 | `https://api.minimaxi.com/anthropic` |
| 需要环境变量 | 否（此提供商**不**使用 `MINIMAX_API_KEY`） |

## 先决条件

- Python 3.9+
- 已安装 Hermes Agent
- 在 [minimax.io](https://www.minimax.io)（全球）或 [minimaxi.com](https://www.minimaxi.com)（中国）拥有 MiniMax 账户
- 本地机器上有可用的浏览器（或对于远程会话使用 `--no-browser`）

## 快速开始

```bash
# 启动提供商和模型选择器
hermes model
# → 从提供商列表中选择 "MiniMax (OAuth)"
# → Hermes 将在浏览器中打开 MiniMax 授权页面
# → 在浏览器中批准访问
# → 选择一个模型 (MiniMax-M2.7 或 MiniMax-M2.7-highspeed)
# → 开始聊天

hermes
```

首次登录后，凭据将存储在 `~/.hermes/auth.json` 下，并在每次会话开始前自动刷新。

## 手动登录

您可以在不通过模型选择器的情况下触发登录：

```bash
hermes auth add minimax-oauth
```

### 中国区域

如果您的账户在中国平台 (`minimaxi.com`) 上，请传递 `--region cn`：

```bash
hermes auth add minimax-oauth --region cn
```

### 远程 / 无头会话

在没有可用浏览器的服务器或容器上：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 将打印验证 URL 和用户代码 — 在任何设备上打开该 URL，并在提示时输入代码。

## OAuth 流程

Hermes 针对 MiniMax OAuth 端点实现了 PKCE 设备码流程：

1.  Hermes 生成一个 PKCE 验证器 / 挑战对和一个随机状态值。
2.  它向 `{base_url}/oauth/code` 发送 POST 请求，附带挑战并接收 `user_code` 和 `verification_uri`。
3.  您的浏览器打开 `verification_uri`。如果提示，请输入 `user_code`。
4.  Hermes 轮询 `{base_url}/oauth/token` 直到令牌到达（或截止时间过去）。
5.  令牌（`access_token`、`refresh_token`、过期时间）被保存到 `~/.hermes/auth.json` 中的 `minimax-oauth` 键下。

令牌刷新（标准的 OAuth `refresh_token` 授权）会在每次会话开始时，当访问令牌距离过期时间在 60 秒内时自动运行。

## 检查登录状态

```bash
hermes doctor
```

`◆ Auth Providers` 部分将显示：

```
✓ MiniMax OAuth  (已登录, region=global)
```

或者，如果未登录：

```
⚠ MiniMax OAuth  (未登录)
```

## 切换模型

```bash
hermes model
# → 选择 "MiniMax (OAuth)"
# → 从模型列表中选择
```

或者直接设置模型：

```bash
hermes config set model MiniMax-M2.7
hermes config set provider minimax-oauth
```

## 配置参考

登录后，`~/.hermes/config.yaml` 将包含类似以下的条目：

```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```

### `--region` 标志

| 值 | 门户 | 推理端点 |
|-------|--------|-------------------|
| `global` (默认) | `https://api.minimax.io` | `https://api.minimax.io/anthropic` |
| `cn` | `https://api.minimaxi.com` | `https://api.minimaxi.com/anthropic` |

### 提供商别名

以下所有内容都解析为 `minimax-oauth`：

```bash
hermes --provider minimax-oauth    # 规范形式
hermes --provider minimax-portal   # 别名
hermes --provider minimax-global   # 别名
hermes --provider minimax_oauth    # 别名（下划线形式）
```

## 环境变量

`minimax-oauth` 提供商**不**使用 `MINIMAX_API_KEY` 或 `MINIMAX_BASE_URL`。这些变量仅用于基于 API 密钥的 `minimax` 和 `minimax-cn` 提供商。

| 变量 | 作用 |
|----------|--------|
| `MINIMAX_API_KEY` | 仅由 `minimax` 提供商使用 — 对 `minimax-oauth` 忽略 |
| `MINIMAX_CN_API_KEY` | 仅由 `minimax-cn` 提供商使用 — 对 `minimax-oauth` 忽略 |

要在运行时强制使用 `minimax-oauth` 提供商：

```bash
HERMES_INFERENCE_PROVIDER=minimax-oauth hermes
```

## 模型

| 模型 | 最适合 |
|-------|----------|
| `MiniMax-M2.7` | 长上下文推理、复杂的工具调用 |
| `MiniMax-M2.7-highspeed` | 低延迟、轻量级任务、辅助调用 |

两个模型都支持高达 200,000 个 Token 的上下文。

当 `minimax-oauth` 是主要提供商时，`MiniMax-M2.7-highspeed` 也会自动用作视觉和委派任务的辅助模型。

## 故障排除

### 令牌过期 — 未自动重新登录

如果访问令牌距离过期时间在 60 秒内，Hermes 会在每次会话开始时刷新令牌。如果访问令牌已经过期（例如，在长时间离线后），刷新会在下一次请求时自动进行。如果刷新失败并出现 `refresh_token_reused` 或 `invalid_grant` 错误，Hermes 会将会话标记为需要重新登录。

**修复：** 再次运行 `hermes auth add minimax-oauth` 以开始新的登录。

### 授权超时

设备码流程有一个有限的过期窗口。如果您没有及时批准登录，Hermes 会引发超时错误。

**修复：** 重新运行 `hermes auth add minimax-oauth`（或 `hermes model`）。流程将重新开始。

### 状态不匹配（可能的 CSRF）

Hermes 检测到授权服务器返回的 `state` 值与它发送的值不匹配。

**修复：** 重新运行登录。如果问题持续存在，请检查是否有代理或重定向正在修改 OAuth 响应。

### 从远程服务器登录

如果 `hermes` 无法打开浏览器窗口，请使用 `--no-browser`：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 将打印 URL 和代码。在任何设备上打开该 URL 并在那里完成流程。

### 运行时出现 "Not logged into MiniMax OAuth" 错误

认证存储中没有 `minimax-oauth` 的凭据。您尚未登录，或者凭据文件已被删除。

**修复：** 运行 `hermes model` 并选择 MiniMax (OAuth)，或者运行 `hermes auth add minimax-oauth`。

## 注销

要删除存储的 MiniMax OAuth 凭据：

```bash
hermes auth remove minimax-oauth
```

## 另请参阅

-   [AI 提供商参考](../integrations/providers.md)
-   [环境变量](../reference/environment-variables.md)
-   [配置](../user-guide/configuration.md)
-   [hermes doctor](../reference/cli-commands.md)