---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

# 功能概览

Hermes Agent 包含一套丰富的功能，其能力远超基础聊天。从持久化记忆和文件感知上下文，到浏览器自动化和语音对话，这些功能协同工作，使 Hermes 成为一个强大的自主助手。

## 核心功能

- **[工具与工具集](tools.md)** — 工具是扩展 Agent 能力的函数。它们被组织成逻辑工具集，可按平台启用或禁用，涵盖网络搜索、终端执行、文件编辑、记忆、委派等。
- **[技能系统](skills.md)** — Agent 在需要时可以加载的按需知识文档。技能遵循渐进式披露模式，以最小化 Token 使用量，并与 [agentskills.io](https://agentskills.io/specification) 开放标准兼容。
- **[持久化记忆](memory.md)** — 跨会话持久化的、有边界且经过筛选的记忆。Hermes 通过 `MEMORY.md` 和 `USER.md` 记住您的偏好、项目、环境以及它学到的东西。
- **[上下文文件](context-files.md)** — Hermes 自动发现并加载项目上下文文件（`.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `SOUL.md`, `.cursorrules`），这些文件决定了它在您项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟一个引用，即可将文件、文件夹、git diff 和 URL 直接注入到您的消息中。Hermes 会内联展开引用并自动附加内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 在进行文件更改前会自动对您的工作目录进行快照，为您提供安全网，如果出现问题，可以使用 `/rollback` 回滚。

## 自动化

- **[定时任务 (Cron)](cron.md)** — 使用自然语言或 cron 表达式安排任务自动运行。作业可以附加技能、将结果发送到任何平台，并支持暂停/恢复/编辑操作。
- **[子 Agent 委派](delegation.md)** — `delegate_task` 工具会生成具有独立上下文、受限工具集和自身终端会话的子 Agent 实例。最多可同时运行 3 个子 Agent 以实现并行工作流。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许 Agent 编写 Python 脚本以编程方式调用 Hermes 工具，通过沙盒化的 RPC 执行将多步骤工作流压缩到单个 LLM 轮次中。
- **[事件钩子](hooks.md)** — 在关键生命周期点运行自定义代码。消息网关钩子处理日志记录、警报和 Webhook；插件钩子处理工具拦截、指标和防护栏。
- **[批量处理](batch-processing.md)** — 并行运行 Hermes Agent 处理数百或数千个提示词，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。

## 媒体与网络

- **[语音模式](voice-mode.md)** — 在 CLI 和消息平台上实现完整的语音交互。使用麦克风与 Agent 交谈，听取语音回复，并在 Discord 语音频道中进行实时语音对话。
- **[浏览器自动化](browser.md)** — 具有多个后端的完整浏览器自动化：Browserbase 云、Browser Use 云、通过 CDP 的本地 Chrome 或本地 Chromium。导航网站、填写表单和提取信息。
- **[视觉与图像粘贴](vision.md)** — 多模态视觉支持。从剪贴板将图像粘贴到 CLI 中，并要求 Agent 使用任何支持视觉的模型进行分析、描述或处理。
- **[图像生成](image-generation.md)** — 使用 FAL.ai 根据文本提示词生成图像。支持八种模型（FLUX 2 Klein/Pro、GPT-Image 1.5、Nano Banana、Ideogram V3、Recraft V3、Qwen、Z-Image Turbo）；可通过 `hermes tools` 选择。
- **[语音与 TTS](tts.md)** — 在所有消息平台上实现文本转语音输出和语音消息转录，提供五种提供商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax 和 NeuTTS。

## 集成

- **[MCP 集成](mcp.md)** — 通过 stdio 或 HTTP 传输连接到任何 MCP 服务器。无需编写原生 Hermes 工具即可访问来自 GitHub、数据库、文件系统和内部 API 的外部工具。包括每服务器工具过滤和采样支持。
- **[提供商路由](provider-routing.md)** — 精细控制哪些 AI 提供商处理您的请求。通过排序、白名单、黑名单和优先级排序来优化成本、速度或质量。
- **[备用提供商](fallback-providers.md)** — 当您的主模型遇到错误时，自动故障转移到备用 LLM 提供商，包括为视觉和压缩等辅助任务提供独立的备用方案。
- **[凭证池](credential-pools.md)** — 将 API 调用分配到同一提供商的多个密钥上。在遇到速率限制或失败时自动轮换。
- **[记忆提供商](memory-providers.md)** — 插入外部记忆后端（Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover），用于跨会话用户建模和超越内置记忆系统的个性化。
- **[API 服务器](api-server.md)** — 将 Hermes 作为兼容 OpenAI 的 HTTP 端点公开。连接任何支持 OpenAI 格式的前端 — Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成 (ACP)](acp.md)** — 在兼容 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes。聊天、工具活动、文件差异和终端命令会在您的编辑器内呈现。
- **[RL 训练](rl-training.md)** — 从 Agent 会话生成轨迹数据，用于强化学习和模型微调。

## 自定义

- **[人格与 SOUL.md](personality.md)** — 完全可定制的 Agent 人格。`SOUL.md` 是主要的身份文件 — 系统提示词中的第一项 — 您可以在每次会话中切换内置或自定义的 `/personality` 预设。
- **[皮肤与主题](skins.md)** — 自定义 CLI 的视觉呈现：横幅颜色、旋转器图标和动词、响应框标签、品牌文本以及工具活动前缀。
- **[插件](plugins.md)** — 无需修改核心代码即可添加自定义工具、钩子和集成。三种插件类型：通用插件（工具/钩子）、记忆提供商（跨会话知识）和上下文引擎（替代上下文管理）。通过统一的 `hermes plugins` 交互式 UI 进行管理。