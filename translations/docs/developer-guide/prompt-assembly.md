---
sidebar_position: 5
title: "提示词组装"
description: "Hermes 如何构建系统提示词、保持缓存稳定性以及注入临时层"
---

# 提示词组装

Hermes 有意将以下两部分分离：

- **缓存的系统提示词状态**
- **临时的 API 调用时添加内容**

这是本项目最重要的设计选择之一，因为它影响：

- Token 使用量
- 提示词缓存效率
- 会话连续性
- 记忆正确性

主要文件：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

## 缓存的系统提示词层

缓存的系统提示词大致按以下顺序组装：

1.  Agent 身份 — 优先使用 `HERMES_HOME` 下的 `SOUL.md`，否则回退到 `prompt_builder.py` 中的 `DEFAULT_AGENT_IDENTITY`
2.  工具感知行为指导
3.  Honcho 静态块（激活时）
4.  可选的系统消息
5.  冻结的 MEMORY 快照
6.  冻结的 USER 配置文件快照
7.  技能索引
8.  上下文文件（`AGENTS.md`、`.cursorrules`、`.cursor/rules/*.mdc`）— 如果 `SOUL.md` 已在步骤 1 作为身份加载，则**不**包含在此处
9.  时间戳 / 可选的会话 ID
10. 平台提示

当设置 `skip_context_files` 时（例如，子 Agent 委派），不会加载 `SOUL.md`，而是使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

### 具体示例：组装后的系统提示词

以下是所有层都存在时最终系统提示词的简化视图（注释显示每个部分的来源）：

```
# 第 1 层：Agent 身份（来自 ~/.hermes/SOUL.md）
你是 Hermes，一个由 Nous Research 创建的 AI 助手。
你是一名专业的软件工程师和研究员。
你重视正确性、清晰度和效率。
...

# 第 2 层：工具感知行为指导
你拥有跨会话的持久记忆。使用记忆工具保存持久性事实：
用户偏好、环境细节、工具特性以及稳定的约定。记忆会注入到每一轮对话中，
因此请保持其紧凑，并专注于未来仍然重要的事实。
...
当用户引用过去对话中的内容，或者你怀疑存在相关的跨会话上下文时，
在要求用户重复之前，请使用 session_search 来回忆。

# 工具使用强制（仅适用于 GPT/Codex 模型）
你**必须**使用你的工具来采取行动 — 不要描述你将要做什么或计划做什么，
而不实际执行。
...

# 第 3 层：Honcho 静态块（激活时）
[Honcho 人格/上下文数据]

# 第 4 层：可选的系统消息（来自配置或 API）
[用户配置的系统消息覆盖]

# 第 5 层：冻结的 MEMORY 快照
## 持久记忆
- 用户偏好 Python 3.12，使用 pyproject.toml
- 默认编辑器是 nvim
- 正在处理项目 "atlas"，位于 ~/code/atlas
- 时区：US/Pacific

# 第 6 层：冻结的 USER 配置文件快照
## 用户配置文件
- 姓名：Alice
- GitHub：alice-dev

# 第 7 层：技能索引
## 技能（强制）
在回复之前，请扫描下面的技能。如果有一个技能明确匹配你的任务，
请使用 skill_view(name) 加载它并遵循其说明。
...
<available_skills>
  software-development:
    - code-review: 结构化代码审查工作流
    - test-driven-development: TDD 方法论
  research:
    - arxiv: 搜索和总结 arXiv 论文
</available_skills>

# 第 8 层：上下文文件（来自项目目录）
# 项目上下文
以下项目上下文文件已加载，应遵循：

## AGENTS.md
这是 atlas 项目。使用 pytest 进行测试。主要入口点是 src/atlas/main.py。
提交前始终运行 `make lint`。

# 第 9 层：时间戳 + 会话
当前时间：2026-03-30T14:30:00-07:00
会话：abc123

# 第 10 层：平台提示
你是一个 CLI AI Agent。尽量不要使用 Markdown，而是使用可在终端内呈现的简单文本。
```

## SOUL.md 如何出现在提示词中

`SOUL.md` 位于 `~/.hermes/SOUL.md`，作为 Agent 的身份 — 系统提示词的第一个部分。`prompt_builder.py` 中的加载逻辑如下：

```python
# 来自 agent/prompt_builder.py（简化版）
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # 安全扫描
    content = _truncate_content(content, "SOUL.md")       # 限制在 20k 字符
    return content
```

当 `load_soul_md()` 返回内容时，它会替换硬编码的 `DEFAULT_AGENT_IDENTITY`。然后调用 `build_context_files_prompt()` 函数，并设置 `skip_soul=True`，以防止 `SOUL.md` 出现两次（一次作为身份，一次作为上下文文件）。

如果 `SOUL.md` 不存在，系统将回退到：

```
你是 Hermes Agent，一个由 Nous Research 创建的智能 AI 助手。
你乐于助人、知识渊博且直接。你帮助用户处理各种任务，
包括回答问题、编写和编辑代码、分析信息、创造性工作以及通过你的工具执行操作。
你沟通清晰，在适当时承认不确定性，并优先考虑真正有用而非冗长，除非另有指示。
在探索和调查中要有针对性和效率。
```

## 上下文文件如何注入

`build_context_files_prompt()` 使用**优先级系统** — 只加载一种项目上下文类型（首次匹配获胜）：

```python
# 来自 agent/prompt_builder.py（简化版）
def build_context_files_prompt(cwd=None, skip_soul=False):
    cwd_path = Path(cwd).resolve()

    # 优先级：首次匹配获胜 — 只加载**一个**项目上下文
    project_context = (
        _load_hermes_md(cwd_path)       # 1. .hermes.md / HERMES.md（向上遍历到 git 根目录）
        or _load_agents_md(cwd_path)    # 2. AGENTS.md（仅 CWD）
        or _load_claude_md(cwd_path)    # 3. CLAUDE.md（仅 CWD）
        or _load_cursorrules(cwd_path)  # 4. .cursorrules / .cursor/rules/*.mdc
    )

    sections = []
    if project_context:
        sections.append(project_context)

    # 来自 HERMES_HOME 的 SOUL.md（独立于项目上下文）
    if not skip_soul:
        soul_content = load_soul_md()
        if soul_content:
            sections.append(soul_content)

    if not sections:
        return ""

    return (
        "# Project Context\n\n"
        "The following project context files have been loaded "
        "and should be followed:\n\n"
        + "\n".join(sections)
    )
```

### 上下文文件发现详情

| 优先级 | 文件 | 搜索范围 | 备注 |
|----------|-------|-------------|-------|
| 1 | `.hermes.md`、`HERMES.md` | 从 CWD 向上到 git 根目录 | Hermes 原生项目配置 |
| 2 | `AGENTS.md` | 仅 CWD | 常见的 Agent 指令文件 |
| 3 | `CLAUDE.md` | 仅 CWD | Claude Code 兼容性 |
| 4 | `.cursorrules`、`.cursor/rules/*.mdc` | 仅 CWD | Cursor 兼容性 |

所有上下文文件都经过：
- **安全扫描** — 检查提示词注入模式（不可见 Unicode、"忽略先前指令"、凭据窃取尝试）
- **截断** — 使用 70/20 头尾比例和截断标记，限制在 20,000 个字符
- **YAML frontmatter 剥离** — 移除 `.hermes.md` 的 frontmatter（保留用于未来配置覆盖）

## 仅 API 调用时层

这些内容有意**不**作为缓存的系统提示词的一部分持久化：

- `ephemeral_system_prompt`
- 预填充消息
- 消息网关派生的会话上下文覆盖
- 后续轮次中注入到当前轮次用户消息中的 Honcho 回忆

这种分离保持了稳定前缀的稳定性，以便缓存。

## 记忆快照

本地记忆和用户配置文件数据在会话开始时作为冻结快照注入。会话中的写入会更新磁盘状态，但不会改变已构建的系统提示词，直到新会话开始或强制重建发生。

## 上下文文件

`agent/prompt_builder.py` 使用**优先级系统**扫描和清理项目上下文文件 — 只加载一种类型（首次匹配获胜）：

1.  `.hermes.md` / `HERMES.md`（向上遍历到 git 根目录）
2.  `AGENTS.md`（启动时的 CWD；在会话期间通过 `agent/subdirectory_hints.py` 逐步发现子目录）
3.  `CLAUDE.md`（仅 CWD）
4.  `.cursorrules` / `.cursor/rules/*.mdc`（仅 CWD）

`SOUL.md` 通过 `load_soul_md()` 单独加载，用于身份槽位。当它成功加载时，`build_context_files_prompt(skip_soul=True)` 会防止它出现两次。

长文件在注入前会被截断。

## 技能索引

当技能工具可用时，技能系统会向提示词贡献一个紧凑的技能索引。

## 为什么提示词组装要这样拆分

该架构经过有意优化，以：

- 保持提供商端的提示词缓存
- 避免不必要地修改历史记录
- 保持记忆语义易于理解
- 允许消息网关/ACP/CLI 添加上下文，而不会污染持久提示词状态

## 相关文档

- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [会话存储](./session-storage.md)
- [消息网关内部原理](./gateway-internals.md)