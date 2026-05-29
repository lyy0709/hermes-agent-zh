---
title: "Openhands — 将编码任务委派给 OpenHands CLI（模型无关，LiteLLM）"
sidebar_label: "Openhands"
description: "将编码任务委派给 OpenHands CLI（模型无关，LiteLLM）"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Openhands

将编码任务委派给 OpenHands CLI（模型无关，LiteLLM）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/openhands` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/openhands` |
| 版本 | `0.1.0` |
| 作者 | Tim Koepsel (xzessmedia), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `Coding-Agent`, `OpenHands`, `Model-Agnostic`, `LiteLLM` |
| 相关技能 | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 加载此技能时读取的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# OpenHands CLI

通过 `terminal` 工具将编码任务委派给 [OpenHands CLI](https://github.com/All-Hands-AI/OpenHands)。OpenHands 是模型无关的：支持任何 LiteLLM 兼容的提供商（OpenAI、Anthropic、OpenRouter、DeepSeek、Ollama、vLLM 等）。

此技能是用于批量/一次性委派的 headless 模式包装器。交互式文本 UI 不会从 Hermes 中使用。

## 使用时机

- 用户希望将编码任务专门委派给 OpenHands。
- 用户需要一个可以在非 Anthropic/非 OpenAI 提供商（DeepSeek、Qwen、Ollama、vLLM、Nous 等）上运行的编码 Agent —— 兄弟技能 `claude-code` 和 `codex` 绑定于单一供应商。
- 在工作区内进行多步骤文件编辑 + shell 命令。

对于 Claude 原生，请优先使用 `claude-code`。对于 OpenAI 原生，请优先使用 `codex`。对于 Hermes 原生子 Agent，请使用 `delegate_task`。

## 先决条件

1.  安装上游软件（需要 Python 3.12+ 和 `uv`）：

    ```
    terminal(command="uv tool install openhands --python 3.12")
    ```

    验证：`openhands --version`（撰写本文时当前版本为 `OpenHands CLI 1.16.0` / `SDK v1.21.0`）。

2.  选择一个模型并为 `--override-with-envs` 设置环境变量：

    ```
    export LLM_MODEL=openrouter/openai/gpt-4o-mini       # 或任何 LiteLLM slug
    export LLM_API_KEY=$OPENROUTER_API_KEY
    export LLM_BASE_URL=https://openrouter.ai/api/v1     # 对于原生 OpenAI 可省略
    ```

    `LLM_MODEL` 使用 LiteLLM 的完整 slug。当提供商是 OpenRouter 时，slug 是双重前缀的：`openrouter/<vendor>/<model>`（例如 `openrouter/anthropic/claude-sonnet-4.5`）。对于原生 Anthropic：`anthropic/claude-sonnet-4-5`。对于原生 OpenAI：`openai/gpt-4o-mini`。

3.  抑制启动横幅，以便 JSON 输出前没有 ASCII 艺术：

    ```
    export OPENHANDS_SUPPRESS_BANNER=1
    ```

## 如何运行

始终通过 `terminal` 工具调用。始终传递 `--headless --json --override-with-envs --exit-without-confirmation` 以实现自动化。

### 一次性任务

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openrouter/openai/gpt-4o-mini LLM_API_KEY=$OPENROUTER_API_KEY LLM_BASE_URL=https://openrouter.ai/api/v1 openhands --headless --json --override-with-envs --exit-without-confirmation -t 'Add error handling to all API calls in src/'",
  workdir="/path/to/project",
  timeout=600
)
```

### 长时间任务后台运行

```
terminal(command="<same as above>", workdir="/path/to/project", background=true, notify_on_complete=true)
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

### 恢复之前的会话

OpenHands 在每次运行结束时打印 `Conversation ID: <32-hex>` 和一行 `Hint: openhands --resume <dashed-uuid>`。使用带连字符的形式来恢复：

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=... openhands --headless --json --override-with-envs --exit-without-confirmation --resume <dashed-uuid> -t 'Now fix the bug you found'",
  workdir="/path/to/project"
)
```

## 真实标志列表

根据 `openhands --help`（CLI 1.16.0）验证。此表中未列出的任何内容都不是标志 —— 通过环境变量或设置文件传递。

| 标志 | 效果 |
|------|--------|
| `--headless` | 无 UI，需要 `-t` 或 `-f`。自动批准所有操作（此模式下没有 `--llm-approve`）。 |
| `--json` | JSONL 事件流（需要 `--headless`）。 |
| `-t TEXT` | 任务提示词。 |
| `-f PATH` | 从文件读取任务。 |
| `--resume [ID]` | 恢复会话。无 ID → 列出最近的会话。 |
| `--last` | 恢复最近的会话（与 `--resume` 一起使用）。 |
| `--override-with-envs` | 应用 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` 环境变量。没有此标志，OpenHands 使用 `~/.openhands/settings.json` 并忽略环境变量。 |
| `--exit-without-confirmation` | 不显示“您确定吗”退出对话框。 |
| `--always-approve` / `--yolo` | 自动批准每个操作（`--headless` 模式下的默认行为）。 |
| `--llm-approve` | 基于 LLM 的安全门（仅限交互模式 —— 在 headless 模式下无效）。 |
| `--version` / `-v` | 打印版本并退出。 |

**没有 `--model`、`--max-iterations`、`--workspace`、`--sandbox`、`--sandbox-type` 标志。** 模型是 `LLM_MODEL`。工作区是传递给 `terminal` 工具的 `workdir`。沙盒/运行时是 `RUNTIME` 和 `SANDBOX_VOLUMES` 环境变量。

## JSON 事件模式

使用 `--json --headless` 时，OpenHands 输出 JSONL —— 每行一个 JSON 对象，外加一些非 JSON 状态行（`Initializing agent...`、`Agent is working`、`Agent finished`、最后的摘要框、`Goodbye!`、`Conversation ID:`、`Hint:`）。过滤以 `{` 开头的行。

顶级 `kind` 字段区分事件：

- `MessageEvent` — 用户/Agent 文本回合。`source` 是 `user` 或 `agent`。
- `ActionEvent` — Agent 选择了一个工具。读取 `tool_name`（`file_editor`、`terminal`、`finish`）和 `action.kind`（`FileEditorAction`、`TerminalAction`、`FinishAction`）。
- `ObservationEvent` — 工具结果。`observation.is_error` 是成功标志。`source` 是 `environment`。
- `ActionEvent` 中的 `FinishAction` 在 `action.message` 中携带 Agent 的最终消息。

CLI 首先打印来自 LiteLLM/Authlib 的所有 stderr —— 参见陷阱。仅解析 stdout，逐行解析，忽略不以 `{` 开头的行。

## 陷阱

-   **每次调用都会出现 LiteLLM 警告。** CLI 将 `bedrock-runtime` 和 `sagemaker-runtime` 警告打印到 stderr，因为 `botocore` 未安装。还有一个 Authlib 弃用警告。这些是噪音，不是失败。将 stderr 管道传输到 `/dev/null` 或在显示给用户之前将其过滤掉。
-   **横幅垃圾信息。** 没有 `OPENHANDS_SUPPRESS_BANNER=1` 时，每次运行都以多行 `+--+` ASCII 框广告 SDK 开始。始终导出此变量。
-   **`--override-with-envs` 对于自动化是必需的。** 没有它，OpenHands 会忽略 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` 并回退到 `~/.openhands/settings.json`。在全新安装时，此文件不存在，CLI 会挂起等待首次运行设置。
-   **模型 slug 是 LiteLLM 的，而不是提供商的。** `openrouter/openai/gpt-4o-mini` 有效；指向 OpenRouter 时使用 `openai/gpt-4o-mini` 无效。`anthropic/claude-sonnet-4-5`（带连字符）是原生 Anthropic；`openrouter/anthropic/claude-sonnet-4.5`（带点）是通过 OpenRouter。弄错 → 隐晦的 LiteLLM 400 错误。
-   **`pip install openhands-ai` 是错误的包。** 那是旧的 V0 SDK。新的 CLI 是 `uv tool install openhands --python 3.12`。没有维护的 conda 包。
-   **恢复 ID 格式很棘手。** CLI 以 `Conversation ID: f46573d9cfdb45e492ca189bde40019b`（无连字符）结尾，然后是 `Hint: openhands --resume f46573d9-cfdb-45e4-92ca-189bde40019b`（带连字符）。使用带连字符的形式。
-   **Headless 模式忽略 `--llm-approve`。** 如果传递它，会出现 argparse 错误。Headless 模式硬编码为始终批准。
-   **上游不支持 Windows。** OpenHands 文档要求在 Windows 上使用 WSL。因此此技能被限制为 `[linux, macos]`。
-   **`~/.openhands/conversations/<id>/` 会累积。** 每次运行都会持久化一个轨迹。如果运行批量任务，请清理它。
-   **安装包很大（约 200 个包）。** 使用 `uv tool install`（隔离的 venv）以避免与活动项目的依赖冲突。

## 验证

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openrouter/openai/gpt-4o-mini LLM_API_KEY=$OPENROUTER_API_KEY LLM_BASE_URL=https://openrouter.ai/api/v1 openhands --headless --json --override-with-envs --exit-without-confirmation -t 'Print the string OPENHANDS_OK to stdout via the terminal tool.'",
  workdir="/tmp",
  timeout=120
)
```

如果 JSONL 流以 `FinishAction` 结尾，且其 `action.message` 提及 `OPENHANDS_OK`，则安装正常工作。

## 相关链接

-   [OpenHands GitHub](https://github.com/All-Hands-AI/OpenHands)
-   [OpenHands CLI 命令参考](https://docs.openhands.dev/openhands/usage/cli/command-reference)
-   兄弟技能：`claude-code`（仅限 Anthropic）、`codex`（仅限 OpenAI）、`opencode`（通过 OpenCode 支持多提供商）、`hermes-agent`（通过 `delegate_task` 实现的 Hermes 子 Agent）。