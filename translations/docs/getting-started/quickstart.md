---
sidebar_position: 1
title: "快速开始"
description: "与 Hermes Agent 的初次对话 —— 从安装到聊天只需 2 分钟"
---

# 快速开始

本指南将引导您完成安装 Hermes Agent、设置提供商并进行首次对话。结束时，您将了解其主要功能以及如何进一步探索。

## 1. 安装 Hermes Agent

运行单行安装程序：

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Android / Termux
如果您在手机上安装，请参阅专门的 [Termux 指南](./termux.md)，了解经过测试的手动路径、支持的额外功能以及当前 Android 特定的限制。
:::

:::tip Windows 用户
请先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在 WSL2 终端内运行上述命令。
:::

安装完成后，重新加载您的 shell：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

## 2. 设置提供商

安装程序会自动配置您的 LLM 提供商。如需稍后更改，请使用以下命令之一：

```bash
hermes model       # 选择您的 LLM 提供商和模型
hermes tools       # 配置启用哪些工具
hermes setup       # 或一次性配置所有内容
```

`hermes model` 将引导您选择推理提供商：

| 提供商 | 说明 | 如何设置 |
|----------|-----------|---------------|
| **Nous Portal** | 基于订阅，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备代码授权 |
| **Anthropic** | 直接使用 Claude 模型（Pro/Max 或 API 密钥） | 通过 `hermes model` 使用 Claude Code 授权，或使用 Anthropic API 密钥 |
| **OpenRouter** | 跨多种模型的多提供商路由 | 输入您的 API 密钥 |
| **Z.AI** | GLM / 智谱托管模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY` |
| **Kimi / Moonshot** | Moonshot 托管的编码和聊天模型 | 设置 `KIMI_API_KEY` |
| **Kimi / Moonshot China** | 中国区 Moonshot 端点 | 设置 `KIMI_CN_API_KEY` |
| **Arcee AI** | Trinity 模型 | 设置 `ARCEEAI_API_KEY` |
| **MiniMax** | 国际版 MiniMax 端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax China** | 中国区 MiniMax 端点 | 设置 `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | 通过 DashScope 使用 Qwen 模型 | 设置 `DASHSCOPE_API_KEY` |
| **Hugging Face** | 通过统一路由器使用 20+ 开源模型（Qwen、DeepSeek、Kimi 等） | 设置 `HF_TOKEN` |
| **Kilo Code** | KiloCode 托管模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按需付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 每月 10 美元订阅开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接访问 DeepSeek API | 设置 `DEEPSEEK_API_KEY` |
| **NVIDIA NIM** | 通过 build.nvidia.com 或本地 NIM 使用 Nemotron 模型 | 设置 `NVIDIA_API_KEY`（可选：`NVIDIA_BASE_URL`） |
| **Ollama Cloud** | 托管的 Ollama 目录，无需本地 GPU | 设置 `OLLAMA_API_KEY`（或在 `hermes model` 中选择 **Ollama Cloud**） |
| **Google Gemini (OAuth)** | 通过 Cloud Code Assist 使用 Gemini —— 免费和付费层级 | 通过 `hermes model` 进行 OAuth（付费层级可选：`HERMES_GEMINI_PROJECT_ID`） |
| **xAI (Grok)** | 通过 Responses API + 提示词缓存使用 Grok 4 模型 | 设置 `XAI_API_KEY`（别名：`grok`） |
| **GitHub Copilot** | GitHub Copilot 订阅（GPT-5.x、Claude、Gemini 等） | 通过 `hermes model` 进行 OAuth，或使用 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP Agent 后端（生成本地 `copilot` CLI） | `hermes model`（需要 `copilot` CLI + `copilot login`） |
| **Vercel AI Gateway** | Vercel AI Gateway 路由 | 设置 `AI_GATEWAY_API_KEY` |
| **自定义端点** | VLLM、SGLang、Ollama 或任何 OpenAI 兼容的 API | 设置基础 URL + API 密钥 |

:::caution 最低上下文：64K Token
Hermes Agent 需要一个至少具有 **64,000 Token** 上下文的模型。上下文窗口较小的模型无法为多步骤工具调用工作流维持足够的工作记忆，将在启动时被拒绝。大多数托管模型（Claude、GPT、Gemini、Qwen、DeepSeek）都轻松满足此要求。如果您运行本地模型，请将其上下文大小设置为至少 64K（例如，对于 llama.cpp 使用 `--ctx-size 65536`，对于 Ollama 使用 `-c 65536`）。
:::

:::tip
您可以随时使用 `hermes model` 切换提供商 —— 无需更改代码，没有锁定。配置自定义端点时，Hermes 会提示输入上下文窗口大小，并在可能时自动检测。详情请参阅[上下文长度检测](../integrations/providers.md#context-length-detection)。
:::

## 3. 开始聊天

```bash
hermes            # 经典 CLI
hermes --tui      # 现代 TUI（推荐）
```

就是这样！您将看到一个欢迎横幅，显示您的模型、可用工具和技能。输入消息并按 Enter 键。

:::tip 选择您的界面
Hermes 附带两个终端界面：经典的 `prompt_toolkit` CLI 和带有模态叠加层、鼠标选择和非阻塞输入的新版 [TUI](../user-guide/tui.md)。两者共享相同的会话、斜杠命令和配置 —— 分别使用 `hermes` 和 `hermes --tui` 尝试一下。
:::

```
❯ 你能帮我做什么？
```

Agent 可以访问用于网络搜索、文件操作、终端命令等工具 —— 所有这些都开箱即用。

## 4. 尝试关键功能

### 要求它使用终端

```
❯ 我的磁盘使用情况如何？显示前 5 个最大的目录。
```

Agent 将代表您运行终端命令并向您显示结果。

### 使用斜杠命令

输入 `/` 可查看所有命令的自动完成下拉列表：

| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试一个有趣的人格 |
| `/save` | 保存对话 |

### 多行输入

按 `Alt+Enter` 或 `Ctrl+J` 添加新行。非常适合粘贴代码或编写详细的提示词。

### 中断 Agent

如果 Agent 耗时过长，只需输入新消息并按 Enter 键 —— 它会中断当前任务并切换到您的新指令。`Ctrl+C` 也有效。

### 恢复会话

退出时，hermes 会打印一个恢复命令：

```bash
hermes --continue    # 恢复最近的会话
hermes -c            # 简写形式
```

## 5. 进一步探索

以下是一些接下来可以尝试的事情：

### 设置沙盒化终端

为了安全起见，在 Docker 容器或远程服务器上运行 Agent：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

### 连接消息平台

通过 Telegram、Discord、Slack、WhatsApp、Signal、Email 或 Home Assistant 从您的手机或其他平台与 Hermes 聊天：

```bash
hermes gateway setup    # 交互式平台配置
```

### 添加语音模式

想在 CLI 中使用麦克风输入或在消息中使用语音回复吗？

```bash
pip install "hermes-agent[voice]"
# 包含用于免费本地语音转文本的 faster-whisper
```

然后在 Hermes 中启动并启用它：

```text
/voice on
```

按 `Ctrl+B` 进行录音，或使用 `/voice tts` 让 Hermes 说出其回复。有关 CLI、Telegram、Discord 和 Discord 语音频道的完整设置，请参阅[语音模式](../user-guide/features/voice-mode.md)。

### 安排自动化任务

```
❯ 每天早上 9 点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 向我发送摘要。
```

Agent 将通过消息网关设置一个自动运行的定时任务。

### 浏览和安装技能

```bash
hermes skills search kubernetes
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills install openai/skills/k8s
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

提示：
- 使用 `--source skills-sh` 搜索公共 `skills.sh` 目录。
- 使用 `--source well-known` 配合文档/站点 URL 从 `/.well-known/skills/index.json` 发现技能。
- 仅在审查第三方技能后使用 `--force`。它可以覆盖非危险策略阻止，但不能覆盖 `dangerous` 扫描判定。

或者在聊天中使用 `/skills` 斜杠命令。

### 通过 ACP 在编辑器内使用 Hermes

Hermes 也可以作为 ACP 服务器运行，用于 VS Code、Zed 和 JetBrains 等 ACP 兼容编辑器：

```bash
pip install -e '.[acp]'
hermes acp
```

有关设置详情，请参阅 [ACP 编辑器集成](../user-guide/features/acp.md)。

### 尝试 MCP 服务器

通过模型上下文协议连接到外部工具：

```yaml
# 添加到 ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

---

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择您的 LLM 提供商和模型 |
| `hermes tools` | 按平台配置启用哪些工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上次会话 |

## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义您的设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、Email 或 Home Assistant
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用功能