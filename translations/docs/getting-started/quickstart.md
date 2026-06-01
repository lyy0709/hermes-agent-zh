---
sidebar_position: 1
title: "快速开始"
description: "与 Hermes Agent 的首次对话——从安装到聊天，5 分钟内完成"
---

# 快速开始

本指南将引导你从零开始，搭建一个能够应对实际使用的 Hermes 环境。完成安装、选择提供商、验证聊天功能，并确切知道当出现问题时该如何处理。

## 更喜欢观看视频？

**Onchain AI Garage** 制作了一个关于安装、设置和基本命令的 Masterclass 视频教程——如果你更愿意跟随视频操作，这是本页面的绝佳伴侣。更多内容，请查看完整的 [Hermes Agent 教程与用例](https://www.youtube.com/playlist?list=PLmpUb_PWAkDxewld5ZYyKifuHxgIbiq2d) 播放列表。

<div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', maxWidth: '100%', marginBottom: '1.5rem'}}>
  <iframe
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%'}}
    src="https://www.youtube-nocookie.com/embed/R3YOGfTBcQg"
    title="Hermes Agent Masterclass: Installation, Setup, Basic Commands"
    frameBorder="0"
    allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  ></iframe>
</div>

## 适用人群

- 全新用户，希望以最短路径获得可用的环境
- 切换提供商，不想因配置错误浪费时间
- 为团队、机器人或常驻工作流设置 Hermes
- 厌倦了“安装成功，但依然无法使用”的情况

## 最快路径

根据你的目标选择对应的行：

| 目标 | 首先执行 | 然后执行 |
|---|---|---|
| 我只想在我的机器上运行 Hermes | `hermes setup` | 运行一次真实聊天并验证其响应 |
| 我已经知道我的提供商 | `hermes model` | 保存配置，然后开始聊天 |
| 我想要一个机器人或常驻设置 | CLI 正常工作后执行 `hermes gateway setup` | 连接 Telegram、Discord、Slack 或其他平台 |
| 我想要本地或自托管模型 | `hermes model` → 自定义端点 | 验证端点、模型名称和上下文长度 |
| 我想要多提供商故障转移 | 首先执行 `hermes model` | 基础聊天正常工作后，再添加路由和故障转移 |

**经验法则：** 如果 Hermes 无法完成一次正常的聊天，请先不要添加更多功能。先让一次干净的对话正常工作，然后再叠加消息网关、定时任务、技能、语音或路由等功能。

---

## 1. 安装 Hermes Agent

**选项 A — pip（最简单）：**

```bash
pip install hermes-agent
hermes postinstall     # 可选：安装 Node.js、浏览器、ripgrep、ffmpeg 并运行设置
```

PyPI 发布版本跟踪的是带标签的版本（主要/次要版本），而不是 `main` 分支的每次提交。如需最新前沿版本，请使用选项 B。

**选项 B — git 安装程序（跟踪 main 分支）：**

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

更喜欢桌面版原生安装程序？

- **桌面版下载：** [GitHub Releases](https://github.com/NousResearch/hermes-agent/releases/latest)

:::tip Android / Termux
如果你在手机上安装，请参阅专门的 [Termux 指南](./termux.md)，了解经过测试的手动安装路径、支持的额外功能以及当前 Android 特定的限制。
:::

:::tip Windows 用户
请先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在你的 WSL2 终端内运行上述命令。
:::

安装完成后，重新加载你的 shell：

```bash
source ~/.bashrc   # 或者 source ~/.zshrc
```

有关详细的安装选项、先决条件和故障排除，请参阅 [安装指南](./installation.md)。

## 2. 选择提供商

这是最重要的设置步骤。使用 `hermes model` 以交互方式完成选择：

```bash
hermes model
```

:::tip 最简单路径：Nous Portal
一个订阅覆盖 300+ 模型以及 [工具网关](../user-guide/features/tool-gateway.md)（网络搜索、图像生成、TTS、云浏览器）。在全新安装后：

```bash
hermes setup --portal
```

该命令将登录、设置 Nous 为你的提供商，并一键开启工具网关。
:::

推荐的默认选项：

| 提供商 | 说明 | 如何设置 |
|----------|-----------|---------------|
| **Nous Portal** | 基于订阅，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备代码授权 |
| **Anthropic** | 直接使用 Claude 模型 — Max 计划 + 额外使用额度（OAuth），或按 Token 付费的 API 密钥 | `hermes model` → OAuth 登录（需要 Max + 额外额度），或提供 Anthropic API 密钥 |
| **OpenRouter** | 跨多个模型的多提供商路由 | 输入你的 API 密钥 |
| **Z.AI** | GLM / 智谱托管模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY`（也接受 `Z_AI_API_KEY`） |
| **Kimi / Moonshot** | Moonshot 托管的编码和聊天模型 | 设置 `KIMI_API_KEY`（或 Kimi-Coding 专用的 `KIMI_CODING_API_KEY`） |
| **Kimi / Moonshot China** | 中国区 Moonshot 端点 | 设置 `KIMI_CN_API_KEY` |
| **Arcee AI** | Trinity 模型 | 设置 `ARCEEAI_API_KEY` |
| **GMI Cloud** | 多模型直接 API | 设置 `GMI_API_KEY` |
| **MiniMax (OAuth)** | 通过浏览器 OAuth 使用 MiniMax 前沿模型 — 无需 API 密钥（`hermes_cli/models.py` 中的模型名称可能在版本间变化） | `hermes model` → MiniMax (OAuth) |
| **MiniMax** | 国际版 MiniMax 端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax China** | 中国区 MiniMax 端点 | 设置 `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | 通过 DashScope 使用 Qwen 模型 | 设置 `DASHSCOPE_API_KEY`（Qwen Coding Plan 也接受 `ALIBABA_CODING_PLAN_API_KEY`） |
| **Hugging Face** | 通过统一路由器使用 20+ 开源模型（Qwen、DeepSeek、Kimi 等） | 设置 `HF_TOKEN` |
| **AWS Bedrock** | 通过原生 Converse API 使用 Claude、Nova、Llama、DeepSeek | IAM 角色或 `aws configure`（[指南](../guides/aws-bedrock.md)） |
| **Azure Foundry** | Azure AI Foundry 托管模型 | 设置 `AZURE_FOUNDRY_API_KEY` + `AZURE_FOUNDRY_BASE_URL` |
| **Google AI Studio** | 通过直接 API 使用 Gemini 模型 | 设置 `GOOGLE_API_KEY` / `GEMINI_API_KEY` |
| **Google Gemini (OAuth)** | 通过 `google-gemini-cli` OAuth 流程使用 Gemini — 无需密钥 | `hermes model` → Google Gemini (OAuth) |
| **xAI** | 通过直接 API 使用 Grok 模型 | 设置 `XAI_API_KEY` |
| **xAI Grok OAuth** | SuperGrok / Premium+ 订阅，无需 API 密钥 | `hermes model` → xAI Grok OAuth |
| **NovitaAI** | 多模型 API 网关 | 设置 `NOVITA_API_KEY` |
| **StepFun** | Step Plan 模型 | 设置 `STEPFUN_API_KEY` |
| **Xiaomi MiMo** | 小米托管模型 | 设置 `XIAOMI_API_KEY` |
| **Tencent TokenHub** | 腾讯托管模型 | 设置 `TOKENHUB_API_KEY` |
| **Ollama Cloud** | 托管的 Ollama 托管模型 | 设置 `OLLAMA_API_KEY` |
| **LM Studio** | 本地桌面应用，暴露 OpenAI 兼容的 API | 设置 `LM_API_KEY`（如果使用非默认值，还需设置 `LM_BASE_URL`） |
| **Qwen OAuth** | Qwen Portal 浏览器 OAuth — 无需 API 密钥 | `hermes model` → Qwen OAuth |
| **Kilo Code** | KiloCode 托管模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按使用付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 每月 10 美元订阅开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接 DeepSeek API 访问 | 设置 `DEEPSEEK_API_KEY` |
| **NVIDIA NIM** | 通过 build.nvidia.com 或本地 NIM 使用 Nemotron 模型 | 设置 `NVIDIA_API_KEY`（可选：`NVIDIA_BASE_URL`） |
| **GitHub Copilot** | GitHub Copilot 订阅（GPT-5.x、Claude、Gemini 等） | 通过 `hermes model` 进行 OAuth，或设置 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP Agent 后端（生成本地 `copilot` CLI） | `hermes model`（需要 `copilot` CLI + `copilot login`） |
| **自定义端点** | VLLM、SGLang、Ollama 或任何 OpenAI 兼容的 API | 设置基础 URL + API 密钥 |
对于大多数首次用户：选择一个提供商，除非你知道为什么要更改，否则接受默认设置。完整的提供商目录（包含环境变量和设置步骤）位于[Providers](../integrations/providers.md)页面。

:::caution 最低上下文要求：64K Token
Hermes Agent 需要一个至少具有 **64,000 Token** 上下文的模型。上下文窗口较小的模型无法为多步骤工具调用工作流维持足够的工作记忆，并会在启动时被拒绝。大多数托管模型（Claude、GPT、Gemini、Qwen、DeepSeek）都能轻松满足此要求。如果你运行的是本地模型，请将其上下文大小设置为至少 64K（例如，对于 llama.cpp 使用 `--ctx-size 65536`，对于 Ollama 使用 `-c 65536`）。
:::

:::tip
你可以随时使用 `hermes model` 切换提供商——没有锁定。有关所有支持的提供商的完整列表和设置详情，请参阅[AI Providers](../integrations/providers.md)。
:::

### 设置如何存储

Hermes 将密钥与普通配置分开存储：

- **密钥和 Token** → `~/.hermes/.env`
- **非机密设置** → `~/.hermes/config.yaml`

通过 CLI 设置值是最简单的方法：

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

正确的值会自动放入正确的文件。

## 3. 运行你的第一次聊天

```bash
hermes            # 经典 CLI
hermes --tui      # 现代 TUI（推荐）
```

你将看到一个欢迎横幅，显示你的模型、可用工具和技能。使用一个具体且易于验证的提示词：

:::tip 选择你的界面
Hermes 附带两个终端界面：经典的 `prompt_toolkit` CLI 和一个较新的[TUI](../user-guide/tui.md)，后者具有模态叠加层、鼠标选择和非阻塞输入。两者共享相同的会话、斜杠命令和配置——分别使用 `hermes` 和 `hermes --tui` 尝试一下。
:::

```
用 5 个要点总结这个仓库，并告诉我主要的入口点是什么。
```

```
检查我当前的目录，告诉我哪个看起来是主要的项目文件。
```

```
帮助我为这个代码库设置一个干净的 GitHub PR 工作流。
```

**成功的样子：**

- 横幅显示你选择的模型/提供商
- Hermes 无错误回复
- 如果需要，它可以使用工具（终端、文件读取、网络搜索）
- 对话可以正常进行多个回合

如果这能正常工作，你就度过了最困难的部分。

## 4. 验证会话工作

在继续之前，确保恢复功能有效：

```bash
hermes --continue    # 恢复最近的会话
hermes -c            # 简写形式
```

这应该能让你回到刚刚的会话。如果不能，请检查你是否在同一个配置文件中，以及会话是否确实已保存。当你以后需要处理多个设置或机器时，这一点很重要。

## 5. 尝试关键功能

### 使用终端

```
❯ 我的磁盘使用情况如何？显示前 5 个最大的目录。
```

Agent 将代表你运行终端命令并显示结果。

### 斜杠命令

输入 `/` 查看所有命令的自动补全下拉列表：

| 命令 | 作用 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试一个有趣的人格 |
| `/save` | 保存对话 |

### 多行输入

按 `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` 添加新行。`Shift+Enter` 要求终端将其作为不同的序列发送（Kitty / foot / WezTerm / Ghostty 默认支持；iTerm2 / Alacritty / VS Code terminal 在启用 Kitty 键盘协议后支持）。`Alt+Enter` 和 `Ctrl+J` 在所有终端中都有效。

### 中断 Agent

如果 Agent 耗时过长，输入新消息并按 Enter——它会中断当前任务并切换到你的新指令。`Ctrl+C` 也有效。

## 6. 添加下一层

仅在基础聊天正常工作后进行。选择你需要的功能：

### 机器人或共享助手

```bash
hermes gateway setup    # 交互式平台配置
```

连接 [Telegram](/user-guide/messaging/telegram)、[Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack)、[WhatsApp](/user-guide/messaging/whatsapp)、[Signal](/user-guide/messaging/signal)、[Email](/user-guide/messaging/email)、[Home Assistant](/user-guide/messaging/homeassistant) 或 [Microsoft Teams](/user-guide/messaging/teams)。

### 自动化和工具

- `hermes tools` — 按平台调整工具访问权限
- `hermes skills` — 浏览并安装可重用的工作流
- Cron — 仅在你的机器人或 CLI 设置稳定后使用

### 沙盒化终端

为了安全，在 Docker 容器或远程服务器上运行 Agent：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

### 语音模式

```bash
# 从 Hermes 安装目录（curl 安装程序将其放在
# Linux/macOS 的 ~/.hermes/hermes-agent 或 Windows 的 %LOCALAPPDATA%\hermes\hermes-agent）：
cd ~/.hermes/hermes-agent
uv pip install -e ".[voice]"
# 包含用于免费本地语音转文本的 faster-whisper
```

然后在 CLI 中：`/voice on`。按 `Ctrl+B` 录音。参见[Voice Mode](../user-guide/features/voice-mode.md)。

### 技能

```bash
hermes skills search kubernetes
hermes skills install openai/skills/k8s
```

或者在聊天会话中使用 `/skills`。

### MCP 服务器

```yaml
# 添加到 ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

### 编辑器集成 (ACP)

ACP 支持随标准的 `[all]` 额外包一起提供，因此 curl 安装程序已经包含了它。只需运行：

```bash
hermes acp
```

（如果你安装时没有 `[all]`，请先运行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[acp]"`。）

参见[ACP Editor Integration](../user-guide/features/acp.md)。

---

## 常见故障模式

这些问题最浪费时间：

| 症状 | 可能原因 | 修复方法 |
|---|---|---|
| Hermes 打开但给出空回复或损坏的回复 | 提供商认证或模型选择错误 | 再次运行 `hermes model` 并确认提供商、模型和认证信息 |
| 自定义端点"有效"但返回垃圾信息 | 基础 URL 错误、模型名称错误或实际上不兼容 OpenAI | 先在单独的客户端验证端点 |
| 消息网关启动但无人能向其发送消息 | 机器人 Token、允许列表或平台设置不完整 | 重新运行 `hermes gateway setup` 并检查 `hermes gateway status` |
| `hermes --continue` 找不到旧会话 | 切换了配置文件或会话从未保存 | 检查 `hermes sessions list` 并确认你在正确的配置文件中 |
| 模型不可用或出现奇怪的备用行为 | 提供商路由或备用设置过于激进 | 在基础提供商稳定之前保持路由关闭 |
| `hermes doctor` 标记配置问题 | 配置值缺失或过时 | 修复配置，在添加功能之前重新测试普通聊天 |
## 故障恢复工具包

当感觉不对劲时，请按此顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

这个流程能让你从“不对劲的状态”快速回到已知的正常状态。

---

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择你的 LLM 提供商和模型 |
| `hermes tools` | 配置每个平台启用哪些工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上一个会话 |

## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义你的设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、电子邮件、Home Assistant、Teams 等
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用功能
- **[AI 提供商](../integrations/providers.md)** — 完整的提供商列表和设置详情
- **[技能系统](../user-guide/features/skills.md)** — 可复用的工作流和知识
- **[技巧与最佳实践](../guides/tips.md)** — 高级用户技巧