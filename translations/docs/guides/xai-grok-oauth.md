---
sidebar_position: 16
title: "xAI Grok OAuth (SuperGrok 订阅)"
description: "使用您的 SuperGrok 订阅登录，在 Hermes Agent 中使用 Grok 模型 — 无需 API 密钥"
---

# xAI Grok OAuth (SuperGrok 订阅)

Hermes Agent 通过基于浏览器的 OAuth 登录流程支持 xAI Grok，该流程针对 [accounts.x.ai](https://accounts.x.ai)，使用您现有的 **SuperGrok 订阅**。无需 `XAI_API_KEY` — 登录一次，Hermes 将在后台自动刷新您的会话。

传输层复用了 `codex_responses` 适配器（xAI 暴露了一个 Responses 风格的端点），因此推理、工具调用、流式传输和提示词缓存无需任何适配器更改即可工作。

同一个 OAuth 承载令牌也被 Hermes 中每个直接连接 xAI 的界面复用 — TTS、图像生成、视频生成和转录 — 因此一次登录即可覆盖所有四项功能。

## 概述

| 项目 | 值 |
|------|-------|
| 提供商 ID | `xai-oauth` |
| 显示名称 | xAI Grok OAuth (SuperGrok 订阅) |
| 认证类型 | 浏览器 OAuth 2.0 PKCE (回环回调) |
| 传输层 | xAI Responses API (`codex_responses`) |
| 默认模型 | `grok-4.3` |
| 端点 | `https://api.x.ai/v1` |
| 认证服务器 | `https://accounts.x.ai` |
| 需要环境变量 | 否（此提供商**不**使用 `XAI_API_KEY`） |
| 订阅 | [SuperGrok](https://x.ai/grok) (任何有效套餐) |

## 先决条件

- Python 3.9+
- 已安装 Hermes Agent
- 您的 xAI 账户拥有有效的 SuperGrok 订阅
- 本地机器上可用浏览器（或对远程会话使用 `--no-browser`）

## 快速开始

```bash
# 启动提供商和模型选择器
hermes model
# → 从提供商列表中选择 "xAI Grok OAuth (SuperGrok 订阅)"
# → Hermes 将在浏览器中打开 accounts.x.ai
# → 在浏览器中批准访问
# → 选择一个模型 (grok-4.3 位于顶部)
# → 开始聊天

hermes
```

首次登录后，凭据将存储在 `~/.hermes/auth.json` 下，并在过期前自动刷新。

## 手动登录

您可以在不通过模型选择器的情况下触发登录：

```bash
hermes auth add xai-oauth
```

### 远程 / 无头会话

在服务器、容器或 SSH 会话等没有可用浏览器的远程环境中，Hermes 会检测到远程环境并打印授权 URL，而不是打开浏览器。

**重要提示：** 回环监听器仍在远程机器的 `127.0.0.1:56121` 上运行。xAI 的重定向需要到达*该*监听器，因此在您的笔记本电脑上打开 URL 将会失败（`无法建立连接。我们无法访问您的应用。`），除非您转发端口：

```bash
# 在您本地机器的另一个终端中：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 然后在远程机器的 SSH 会话中：
hermes auth add xai-oauth --no-browser
# 在您的本地浏览器中打开打印的授权 URL。
```

通过跳板机 / 堡垒机：添加 `-J jump-user@jump-host`。

完整的分步指南（包括 ProxyJump 链、mosh/tmux 和 ControlMaster 注意事项），请参阅 [通过 SSH / 远程主机进行 OAuth](./oauth-over-ssh.md)。

## 登录工作原理

1.  Hermes 在您的浏览器中打开 `accounts.x.ai`。
2.  您登录（或确认现有会话）并批准访问。
3.  xAI 重定向回 Hermes，令牌保存到 `~/.hermes/auth.json`。
4.  此后，Hermes 在后台刷新访问令牌 — 您将保持登录状态，直到执行 `hermes auth remove xai-oauth` 或从您的 xAI 账户设置中撤销访问权限。

## 检查登录状态

```bash
hermes doctor
```

`◆ Auth Providers` 部分将显示每个提供商的当前状态，包括 `xai-oauth`。

## 切换模型

```bash
hermes model
# → 选择 "xAI Grok OAuth (SuperGrok 订阅)"
# → 从模型列表中选择 (grok-4.3 固定在顶部)
```

或者直接设置模型：

```bash
hermes config set model.default grok-4.3
hermes config set model.provider xai-oauth
```

## 配置参考

登录后，`~/.hermes/config.yaml` 将包含：

```yaml
model:
  default: grok-4.3
  provider: xai-oauth
  base_url: https://api.x.ai/v1
```

### 提供商别名

以下所有别名都解析为 `xai-oauth`：

```bash
hermes --provider xai-oauth        # 规范名称
hermes --provider grok-oauth       # 别名
hermes --provider x-ai-oauth       # 别名
hermes --provider xai-grok-oauth   # 别名
```

## 直接连接 xAI 的工具 (TTS / 图像 / 视频 / 转录)

一旦您通过 OAuth 登录，每个直接连接 xAI 的工具都会自动复用同一个承载令牌 — **无需单独设置**，除非您更愿意使用 API 密钥。

为每个工具选择后端：

```bash
hermes tools
# → Text-to-Speech       → "xAI TTS"
# → Image Generation     → "xAI Grok Imagine (image)"
# → Video Generation     → "xAI Grok Imagine"
```

如果 OAuth 令牌已存储，选择器会确认并跳过凭据提示。如果既未设置 OAuth 也未设置 `XAI_API_KEY`，选择器会提供一个三选一菜单：OAuth 登录、粘贴 API 密钥或跳过。

:::note 视频生成默认关闭
`video_gen` 工具集默认是禁用的。在 Agent 可以调用 `video_generate` 之前，请在 `hermes tools` → `🎬 Video Generation`（按空格键）中启用它。否则，Agent 可能会回退到捆绑的 ComfyUI 技能，该技能也标记为用于视频生成。
:::

### 模型

| 工具 | 模型 | 备注 |
|------|-------|-------|
| 聊天 | `grok-4.3` | 默认；通过 OAuth 登录时自动选择 |
| 聊天 | `grok-4.20-0309-reasoning` | 推理变体 |
| 聊天 | `grok-4.20-0309-non-reasoning` | 非推理变体 |
| 聊天 | `grok-4.20-multi-agent-0309` | 多 Agent 变体 |
| 图像 | `grok-imagine-image` | 默认；约 5–10 秒 |
| 图像 | `grok-imagine-image-quality` | 更高保真度；约 10–20 秒 |
| 视频 | `grok-imagine-video` | 文本到视频和图像到视频；最多 7 个参考图像 |
| TTS | (默认语音) | xAI `/v1/tts` 端点 |

聊天目录是从磁盘上的 `models.dev` 缓存实时派生的；一旦该缓存刷新，新的 xAI 发布版本会自动出现。`grok-4.3` 始终固定在列表顶部。

## 环境变量

| 变量 | 效果 |
|----------|--------|
| `XAI_BASE_URL` | 覆盖默认的 `https://api.x.ai/v1` 端点（很少需要）。 |
| `HERMES_INFERENCE_PROVIDER` | 在运行时强制指定活动提供商，例如 `HERMES_INFERENCE_PROVIDER=xai-oauth hermes`。 |

## 故障排除

### 令牌过期 — 未自动重新登录

Hermes 在每次会话前刷新令牌，并在收到 401 响应时再次反应性地刷新。如果刷新失败并显示 `invalid_grant`（刷新令牌已被撤销，或账户已轮换），Hermes 会显示一个类型化的重新认证消息，而不是崩溃。

**修复：** 再次运行 `hermes auth add xai-oauth` 以开始新的登录。

### 授权超时

回环监听器有一个有限的过期窗口（默认 180 秒）。如果您没有及时批准登录，Hermes 会引发超时错误。

**修复：** 重新运行 `hermes auth add xai-oauth`（或 `hermes model`）。流程将重新开始。

### 状态不匹配（可能的 CSRF）

Hermes 检测到授权服务器返回的 `state` 值与它发送的值不匹配。

**修复：** 重新运行登录。如果问题持续存在，请检查是否有代理或重定向正在修改 OAuth 响应。

### 从远程服务器登录

在 SSH 或容器会话中，Hermes 会打印授权 URL 而不是打开浏览器。回环回调监听器仍然绑定在远程主机的 `127.0.0.1:56121` 上 — 如果没有 SSH 本地转发，您的笔记本电脑浏览器无法访问它：

```bash
# 本地机器，单独的终端：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 远程机器：
hermes auth add xai-oauth --no-browser
```

完整演练（跳板机、mosh/tmux、端口冲突）：[通过 SSH / 远程主机进行 OAuth](./oauth-over-ssh.md)。

### 运行时出现 "No xAI credentials found" 错误

认证存储中没有 `xai-oauth` 条目，也没有设置 `XAI_API_KEY`。您尚未登录，或者凭据文件已被删除。

**修复：** 运行 `hermes model` 并选择 xAI Grok OAuth 提供商，或者运行 `hermes auth add xai-oauth`。

## 注销

要删除所有存储的 xAI Grok OAuth 凭据：

```bash
hermes auth logout xai-oauth
```

这将清除 `auth.json` 中的单例 OAuth 条目以及 `xai-oauth` 的任何凭据池行。如果您只想删除单个池条目（运行 `hermes auth list xai-oauth` 查看它们），请使用 `hermes auth remove xai-oauth <index|id|label>`。

## 另请参阅

- [通过 SSH / 远程主机进行 OAuth](./oauth-over-ssh.md) — 如果 Hermes 与您的浏览器不在同一台机器上，必读
- [AI 提供商参考](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置](../user-guide/configuration.md)
- [语音和 TTS](../user-guide/features/tts.md)