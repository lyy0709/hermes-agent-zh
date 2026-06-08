---
title: "简化代码 — 对近期代码变更进行并行三 Agent 清理"
sidebar_label: "简化代码"
description: "对近期代码变更进行并行三 Agent 清理"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 简化代码

对近期代码变更进行并行三 Agent 清理。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/simplify-code` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（灵感来源于 Claude Code /simplify） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `code-review`, `cleanup`, `refactor`, `delegation`, `subagent`, `parallel`, `simplify` |
| 相关技能 | [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review), [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development), [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 简化代码 — 并行审查与清理

使用三个专注的审查者并行审查您近期的代码变更，汇总他们的发现，并应用值得应用的修复。

**核心原则：** 三个专注的审查者胜过一个宽泛的审查者。每个审查者都深入代码库，专门寻找一类问题——复用性、质量、效率——而不会将其注意力分散到所有三类问题上。它们并发运行，因此您只需支付一次审查的延迟，而非三次。

## 使用时机

当用户说出以下任何内容时触发此技能：

- "simplify" / "simplify my changes" / "simplify these changes"
- "review my code" / "review my recent changes" / "clean up my changes"
- "/simplify"（如果他们延续了 Claude Code 的习惯）

用户可能添加的可选修饰符——请遵循它们：

- **聚焦：** "simplify focus on efficiency" → 仅运行效率审查者（或在汇总时向其倾斜权重）。可识别的聚焦点：`reuse`、`quality`、`efficiency`。
- **试运行：** "simplify but don't change anything" / "just report" → 运行三个审查者，呈现发现，**不应用**任何更改。在应用前询问。
- **范围：** "simplify the last commit" / "simplify staged" / "simplify src/foo.py" → 相应地缩小差异来源（参见阶段 1）。

**不要**在每次编辑后自动运行此技能。它需要消耗三个子 Agent 的 Token——仅在用户明确要求时调用。

## 流程

### 阶段 1 — 识别变更

捕获要审查的差异。根据用户要求选择来源，按以下默认顺序：

```bash
# 1. 默认：未提交的工作树变更（已跟踪文件）
git diff

# 2. 如果为空，则包含暂存变更
git diff HEAD

# 3. 用户可能请求的范围变体：
git diff --staged                 # "staged changes"
git diff HEAD~1                    # "the last commit"
git diff main...HEAD              # "this branch" / "my PR"
git diff -- src/foo.py            # specific file(s)
```

如果 `git diff` 和 `git diff HEAD` 都为空，并且没有 git 仓库或没有变更，则回退到用户明确命名的文件或在此会话中最近创建/编辑的文件。如果确实找不到任何更改的代码，请说明并停止——没有可简化的内容。

捕获完整的差异文本。注意其大小：如果非常大（例如 >2000 行更改），警告用户三个子 Agent 各自携带完整差异将消耗大量 Token，并提供在继续之前缩小范围（按目录、按提交）的选项。

### 阶段 2 — 并行启动三个审查者

使用 `delegate_task` 的**批处理模式**——在一个 `tasks` 数组中传递所有三个任务，以便它们并发运行。对于此模式，三个是合适的扇出度；它在任何默认安装的 `delegation.max_concurrent_children` 预算范围内。

给**每个**审查者**完整的差异**（不是片段——跨文件问题隐藏在间隙中）以及绝对仓库路径，以便他们可以搜索更广泛的代码库。每个审查者都获得 `terminal`、`file` 和 `search` 工具集（以便他们可以使用 `git`、`read_file` 和 `search_files`/grep）。

告诉每个审查者：
- 搜索现有代码库以获取证据（不要仅从差异中推理）。
- 将发现报告为具体列表：`file:line → problem → suggested fix`。
- 将每个发现的置信度评级为 `high` / `medium` / `low`。
- 跳过琐碎问题和仅样式更改。仅标记能实质性改进代码的内容。

传递以下三个目标（排除用户聚焦点指定的任何目标）：

**审查者 1 — 代码复用**
> 审查此差异，查找重复代码库中已有功能的代码。搜索工具模块、共享助手和相邻文件（使用 search_files / grep），查找新代码可以调用而非重新实现的现有函数、常量或模式。标记：重复现有函数的新函数；现有工具已实现但手动重写的逻辑（手动字符串/路径操作、自定义环境检查、临时类型守卫、重新实现的解析）。对于每个问题，指明要使用的现有内容及其位置。

**审查者 2 — 代码质量**
> 审查此差异，查找质量问题。寻找：冗余状态（重复或可从现有状态派生的值；不需要存在的缓存）；参数蔓延（在应重构函数的地方添加新参数）；带变体的复制粘贴（应共享抽象的近重复代码块）；泄漏的抽象（暴露内部实现，破坏现有封装边界）；字符串类型代码（在已有常量/枚举/注册表的地方使用原始字符串——在标记前检查规范注册表）。对于每个问题，给出具体的重构方案。

**审查者 3 — 效率**
> 审查此差异，查找效率问题。寻找：不必要的工作（冗余计算、重复文件读取、重复 API 调用、N+1 访问模式）；错过的并发（独立操作顺序运行）；热路径臃肿（在启动或每个请求路径上的繁重/阻塞工作）；TOCTOU 反模式（在操作前进行存在性预检查，而不是执行操作并处理错误）；内存问题（无限制增长、缺少清理、监听器/句柄泄漏）；过于宽泛的读取（加载整个文件，而切片即可）。对于每个问题，给出具体的修复方案及其为何更快或更轻量。

### 阶段 3 — 汇总与应用

等待所有三个审查者返回（批处理模式将它们一起返回）。

1.  **合并**发现到一个列表中，在审查者重叠的地方去重。
2.  **丢弃误报**——您拥有最多的上下文；您不必与审查者争论，只需静默删除薄弱或错误的建议。
3.  **解决冲突。** 审查者可能意见不一（审查者 1："使用现有工具 X"；审查者 3："X 很慢，内联它"）。默认解决顺序：**正确性 > 用户声明的聚焦点 > 可读性/复用性 > 微观性能。** 除非路径确实是热点，否则不要应用损害清晰度的性能"修复"。当两个建议相互排斥且都有道理时，选择涉及代码更少的那个，并注明替代方案。
4.  **应用**存活的修复，直接使用 `patch` / `write_file`——除非用户要求试运行，在这种情况下呈现列表并首先询问。
5.  **验证**您没有破坏任何东西：运行项目针对已修改文件的定向测试（不是完整套件），并重新运行仓库使用的任何 linter/类型检查。如果某个修复破坏了测试，则还原该修复并报告。
6.  **总结**您所做的更改：按审查者类别分组的已应用修复的简短列表，以及您故意跳过的任何发现及其原因。

## 陷阱

- **不要扇出超过约 3 个。** 更多的审查者意味着更高的成本和更多需要协调的冲突建议，而不是更好的覆盖率。三个类别覆盖了空间。
- **给每个审查者**完整的**差异。** 将差异拆分给审查者会破坏设计——跨文件重复和 N+1 问题只有在完整视图下才会显现。
- **审查者搜索，而非猜测。** 没有指向现有工具的复用发现（"可能有一个助手函数"）是噪音。要求提供 `file:line` 证据；删除缺少证据的发现。
- **应用 ≠ 重写。** 这是对用户近期更改的清理，而不是重构整个模块的许可证。将编辑范围限制在差异触及的内容以及修复所需的最小周边更改。
- **尊重项目约定。** 如果仓库有 AGENTS.md / CLAUDE.md / HERMES.md 或 linter 配置，请将这些规则纳入审查者提示词中，以便建议符合内部风格，而不是与之冲突。
- **大差异会撑爆上下文。** 如果差异很大，请在委派前缩小范围——三个子 Agent 各自携带 5000 行差异是昂贵的，并且可能被截断。

## 相关

如果您的安装包含 `subagent-driven-development` 技能（可选），它涵盖了互补的情况：在实现过程中进行并行审查，按任务进行。此技能是独立的*事后*清理过程。使用 `requesting-code-review` 进行提交前的安全/质量门控。