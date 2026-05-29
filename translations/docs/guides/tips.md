---
sidebar_position: 1
title: "技巧与最佳实践"
description: "实用建议，助你充分利用 Hermes Agent — 提示词技巧、CLI 快捷键、上下文文件、记忆、成本优化和安全"
---

# 技巧与最佳实践

一系列立竿见影的实用技巧合集，让你能立即更高效地使用 Hermes Agent。每个部分针对不同方面 — 浏览标题并跳转到相关部分。

:::tip 不知道选哪个模型？
运行 `hermes setup --portal` — 一个订阅即可获得 300 多个模型，包括 Claude、GPT-5 和 Gemini。参见 [Nous Portal](/integrations/nous-portal)。
:::

---

## 获得最佳结果

### 明确表达你的需求

模糊的提示词会产生模糊的结果。不要说“修复代码”，而应该说“修复 `api/handlers.py` 第 47 行的 TypeError — `process_request()` 函数从 `parse_body()` 收到了 `None`。” 你提供的上下文越多，需要的迭代次数就越少。

### 预先提供上下文

在请求的开头就提供相关细节：文件路径、错误信息、预期行为。一条精心设计的消息胜过三轮澄清。直接粘贴错误堆栈跟踪 — Agent 可以解析它们。

### 使用上下文文件处理重复指令

如果你发现自己重复相同的指令（“使用制表符而非空格”、“我们使用 pytest”、“API 在 `/api/v2`”），请将它们放入 `AGENTS.md` 文件中。Agent 会在每次会话中自动读取它 — 设置后无需额外操作。

### 让 Agent 使用其工具

不要试图手把手指导每一步。说“查找并修复失败的测试”，而不是“打开 `tests/test_foo.py`，查看第 42 行，然后...”。Agent 拥有文件搜索、终端访问和代码执行能力 — 让它去探索和迭代。

### 使用技能处理复杂工作流

在编写冗长的提示词来解释如何做某事之前，先检查是否已有相应的技能。输入 `/skills` 浏览可用技能，或直接调用一个，如 `/axolotl` 或 `/github-pr-workflow`。

## CLI 高级用户技巧

### 多行输入

按 **Alt+Enter**、**Ctrl+J** 或 **Shift+Enter** 插入换行符而不发送。`Shift+Enter` 仅在终端将其作为独立按键发送时才有效（Kitty / foot / WezTerm / Ghostty 默认支持；iTerm2 / Alacritty / VS Code 终端在启用 Kitty 键盘协议后支持）。其他两个组合键在所有终端中都有效。

### 粘贴检测

CLI 会自动检测多行粘贴。直接粘贴代码块或错误堆栈跟踪 — 它不会将每一行作为单独的消息发送。粘贴的内容会被缓冲并作为一条消息发送。

### 中断和重定向

按一次 **Ctrl+C** 可在 Agent 响应过程中中断它。然后你可以输入新消息来重定向它。在 2 秒内按两次 Ctrl+C 可强制退出。当 Agent 开始走错方向时，这非常有用。

### 使用 `-c` 恢复会话

忘记了上次会话的内容？运行 `hermes -c` 即可从上次中断的地方恢复，并恢复完整的对话历史记录。你也可以通过标题恢复：`hermes -r "我的研究项目"`。

### 剪贴板图片粘贴

按 **Ctrl+V** 将剪贴板中的图片直接粘贴到聊天中。Agent 使用视觉功能分析屏幕截图、图表、错误弹窗或 UI 模型 — 无需先保存到文件。

### 斜杠命令自动补全

输入 `/` 并按 **Tab** 查看所有可用命令。这包括内置命令（`/compress`、`/model`、`/title`）和每个已安装的技能。你无需记忆任何内容 — Tab 补全已为你准备好。

:::tip
使用 `/verbose` 循环切换工具输出显示模式：**关闭 → 新建 → 全部 → 详细**。“全部”模式非常适合观察 Agent 的操作；“关闭”模式对于简单的问答最简洁。
:::

## 上下文文件

### AGENTS.md：你项目的“大脑”

在项目根目录创建一个 `AGENTS.md` 文件，包含架构决策、编码规范和项目特定指令。这会自动注入到每个会话中，因此 Agent 始终知道你项目的规则。

```markdown
# 项目上下文
- 这是一个使用 SQLAlchemy ORM 的 FastAPI 后端
- 数据库操作始终使用 async/await
- 测试放在 tests/ 目录下并使用 pytest-asyncio
- 切勿提交 .env 文件
```

### SOUL.md：自定义人格

希望 Hermes 拥有稳定的默认风格？编辑 `~/.hermes/SOUL.md`（如果使用自定义的 Hermes 主目录，则是 `$HERMES_HOME/SOUL.md`）。Hermes 现在会自动生成一个初始的 SOUL，并将该全局文件用作实例范围的人格来源。

完整指南请参阅 [在 Hermes 中使用 SOUL.md](/guides/use-soul-with-hermes)。

```markdown
# 灵魂（人格）
你是一名资深后端工程师。言简意赅，直截了当。
除非被要求，否则跳过解释。倾向于简洁的解决方案而非冗长的方案。
始终考虑错误处理和边界情况。
```

使用 `SOUL.md` 来定义持久的人格。使用 `AGENTS.md` 来定义项目特定的指令。

### .cursorrules 兼容性

已经有 `.cursorrules` 或 `.cursor/rules/*.mdc` 文件？Hermes 也会读取它们。无需重复你的编码规范 — 它们会自动从工作目录加载。

### 发现机制

Hermes 在会话开始时从当前工作目录加载顶层的 `AGENTS.md`。子目录中的 `AGENTS.md` 文件在工具调用期间通过 `subdirectory_hints.py` 延迟发现，并注入到工具结果中 — 它们不会预先加载到系统提示词中。

:::tip
保持上下文文件重点突出且简洁。因为每个字符都会计入你的 Token 预算，它们会被注入到每条消息中。
:::

## 记忆与技能

### 记忆与技能：各自用途

**记忆** 用于存储事实：你的环境、偏好、项目位置以及 Agent 了解到的关于你的信息。**技能** 用于存储流程：多步骤工作流、特定工具的指令和可复用的操作指南。用记忆存储“是什么”，用技能存储“怎么做”。

### 何时创建技能

如果你发现一个任务需要 5 个以上的步骤，并且你将来还会再做，请让 Agent 为其创建一个技能。说“把你刚才做的保存为一个名为 `deploy-staging` 的技能。” 下次，只需输入 `/deploy-staging`，Agent 就会加载完整的流程。
### 管理记忆容量

记忆容量是刻意限制的（MEMORY.md 约 2,200 字符，USER.md 约 1,375 字符）。当记忆填满时，Agent 会合并条目。你可以通过说“清理你的记忆”或“替换旧的 Python 3.9 笔记——我们现在用 3.12 了”来帮助它。

### 让 Agent 记住

在富有成效的会话结束后，说“记住这个，下次用”，Agent 就会保存关键要点。你也可以更具体：“保存到记忆中，我们的 CI 使用 GitHub Actions 和 `deploy.yml` 工作流。”

:::warning
记忆是冻结的快照——在会话期间所做的更改，直到下一次会话开始时才会出现在系统提示词中。Agent 会立即写入磁盘，但提示词缓存在会话期间不会失效。
:::

## 性能与成本

### 不要破坏提示词缓存

大多数 LLM 提供商会缓存系统提示词前缀。如果你保持系统提示词稳定（相同的上下文文件，相同的记忆），会话中的后续消息会获得**缓存命中**，成本显著降低。避免在会话中途更改模型或系统提示词。

### 在达到限制前使用 /compress

长时间的会话会累积 Token。当你注意到响应变慢或被截断时，运行 `/compress`。这会总结对话历史，保留关键上下文，同时大幅减少 Token 数量。使用 `/usage` 来检查当前状态。

### 委派以实现并行工作

需要同时研究三个主题吗？要求 Agent 使用 `delegate_task` 并分配并行子任务。每个子 Agent 都在自己的上下文中独立运行，只有最终摘要会返回——这极大地减少了主对话的 Token 使用量。

### 使用 execute_code 进行批量操作

与其逐个运行终端命令，不如让 Agent 编写一个一次性完成所有操作的脚本。“写一个 Python 脚本来将所有 `.jpeg` 文件重命名为 `.jpg` 并运行它”比逐个重命名文件更便宜、更快。

### 选择合适的模型

使用 `/model` 在会话中途切换模型。对于复杂的推理和架构决策，使用前沿模型（Claude Sonnet/Opus, GPT-4o）。对于格式化、重命名或样板代码生成等简单任务，切换到更快的模型。

:::tip
定期运行 `/usage` 查看你的 Token 消耗情况。运行 `/insights` 可以查看过去 30 天使用模式的更广泛视图。
:::

## 消息传递技巧

### 设置主频道

在你偏好的 Telegram 或 Discord 聊天中使用 `/sethome` 将其指定为主频道。定时任务结果和计划任务输出会发送到这里。如果没有设置，Agent 将无处发送主动消息。

### 使用 /title 组织会话

使用 `/title auth-refactor` 或 `/title research-llm-quantization` 为会话命名。命名的会话易于通过 `hermes sessions list` 查找，并通过 `hermes -r "auth-refactor"` 恢复。未命名的会话会堆积起来，变得难以区分。

### 使用 DM 配对实现团队访问

与其手动收集用户 ID 用于允许列表，不如启用 DM 配对。当队友向机器人发送私信时，他们会获得一个一次性配对码。你可以通过 `hermes pairing approve telegram XKGH5N7P` 来批准——简单又安全。

### 工具进度显示模式

使用 `/verbose` 来控制你看到多少工具活动。在消息传递平台上，通常少即是多——将其保持在“new”模式，只查看新的工具调用。在 CLI 中，“all”模式可以让你满意地实时查看 Agent 所做的一切。

:::tip
在消息传递平台上，会话在空闲时间后（默认：24 小时）或每天凌晨 4 点自动重置。如果你需要更长的会话，可以在 `~/.hermes/config.yaml` 中按平台进行调整。
:::

## 安全

### 对不受信任的代码使用 Docker

在处理不受信任的仓库或运行不熟悉的代码时，使用 Docker 或 Daytona 作为你的终端后端。在你的 `.env` 中设置 `TERMINAL_BACKEND=docker`。容器内的破坏性命令不会损害你的主机系统。

```bash
# 在你的 .env 中：
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=hermes-sandbox:latest
```

### 避免 Windows 编码陷阱

在 Windows 上，某些默认编码（如 `cp125x`）无法表示所有 Unicode 字符，这可能导致在测试或脚本中写入文件时出现 `UnicodeEncodeError`。

- 优先使用显式的 UTF-8 编码打开文件：

```python
with open("results.txt", "w", encoding="utf-8") as f:
    f.write("✓ All good\n")
```

- 在 PowerShell 中，你也可以将当前会话切换到 UTF-8，用于控制台和原生命令输出：

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
```

这使 PowerShell 和子进程保持使用 UTF-8，有助于避免仅在 Windows 上出现的故障。

### 在选择“始终”之前仔细审查

当 Agent 触发危险命令批准（`rm -rf`、`DROP TABLE` 等）时，你会看到四个选项：**一次**、**会话**、**始终**、**拒绝**。在选择“始终”之前请仔细考虑——它会永久地将该模式加入允许列表。先从“会话”开始，直到你感到放心。

### 命令批准是你的安全网

Hermes 在执行前会对照精心策划的危险模式列表检查每个命令。这包括递归删除、SQL 删除、将 curl 管道传输到 shell 等。在生产环境中不要禁用此功能——它的存在有充分的理由。

:::warning
当在容器后端（Docker、Singularity、Modal、Daytona）中运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。请确保你的容器镜像已正确锁定。
:::

### 为消息传递机器人使用允许列表

切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`。始终使用特定平台的允许列表（`TELEGRAM_ALLOWED_USERS`、`DISCORD_ALLOWED_USERS`）或 DM 配对来控制谁可以与你的 Agent 交互。

```bash
# 推荐：每个平台使用显式的允许列表
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678

# 或者使用跨平台允许列表
GATEWAY_ALLOWED_USERS=123456789,987654321
```

---

*有应该出现在本页的技巧吗？请提交 Issue 或 PR——欢迎社区贡献。*