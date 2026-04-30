---
title: "Hermes Agent 技能编写 — 编写仓库内技能"
sidebar_label: "Hermes Agent 技能编写"
description: "编写仓库内技能"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Hermes Agent 技能编写

编写仓库内 SKILL.md：frontmatter、验证器、结构。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/hermes-agent-skill-authoring` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `skills`, `authoring`, `hermes-agent`, `conventions`, `skill-md` |
| 相关技能 | [`writing-plans`](/docs/user-guide/skills/bundled/software-development/software-development-writing-plans), [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 编写 Hermes-Agent 技能（仓库内）

## 概述

SKILL.md 可以存在于两个位置：

1.  **用户本地：** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — 个人使用，不共享。通过 `skill_manage(action='create')` 创建。
2.  **仓库内（本技能涉及此情况）：** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — 已提交，随包分发。使用 `write_file` + `git add`。`skill_manage(action='create')` 不针对此目录树。

## 何时使用

- 用户要求你在“此分支/仓库/提交”中添加一个技能
- 你正在提交一个应随 hermes-agent 分发的可重用工作流
- 你正在编辑 `/home/bb/hermes-agent/skills/` 下的现有技能（小修改用 `patch`，重写用 `write_file`；`skill_manage` 仍可用于仓库内技能的 `patch`，但不能用于 `create`）

## 必需的 Frontmatter

权威来源：`tools/skill_manager_tool.py::_validate_frontmatter`。硬性要求：

- 以 `---` 作为起始字节（前面不能有空行）。
- 在正文前以 `\n---\n` 结束。
- 解析为 YAML 映射。
- 存在 `name` 字段。
- 存在 `description` 字段，长度 ≤ **1024 个字符**（`MAX_DESCRIPTION_LENGTH`）。
- 结束的 `---` 之后有非空正文。

`skills/software-development/` 下每个技能使用的对等匹配结构：

```yaml
---
name: my-skill-name               # 小写，连字符，≤64 个字符 (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` 不由验证器强制执行，但每个对等技能都有它们 — 省略会使你的技能显得突兀。

## 大小限制

- 描述：≤ 1024 个字符（强制执行）。
- 完整的 SKILL.md：≤ 100,000 个字符（强制执行，即 `MAX_SKILL_CONTENT_CHARS`，约 36k Token）。
- `software-development/` 中的对等技能大小在 **8-14k 字符** 之间。以此为目标范围。如果超过 20k，请拆分为 `references/*.md` 并从 SKILL.md 中引用它们。

## 对等匹配结构

每个仓库内技能大致遵循：

```
# <标题>

## 概述
一两段话：是什么以及为什么。

## 何时使用
- 项目符号形式的触发条件
- “不要用于：” 反触发条件

## <特定于技能的主题部分>
- 常见快速参考表
- 包含确切命令的代码块
- Hermes 特定配方（通过 scripts/run_tests.sh 测试，ui-tui 路径等）

## 常见陷阱
错误及其修复的编号列表。

## 验证清单
- [ ] 操作后验证的复选框列表

## 一次性配方（可选）
命名场景 → 具体命令序列。
```

并非每个部分都是必需的，但 `概述` + `何时使用` + 可操作的正文 + 陷阱是使技能感觉像对等技能的最低要求。

## 目录放置

```
skills/<category>/<skill-name>/SKILL.md
```

仓库中当前的类别（用 `ls skills/` 确认）：`autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`。

选择最接近的现有类别。不要随意创建新的顶级类别。

## 工作流程

1.  **调查目标类别中的对等技能：**
    ```
    ls skills/<category>/
    ```
    阅读 2-3 个对等技能的 SKILL.md 文件以匹配语气和结构。
2.  如果不确定，**检查验证器约束**（在 `tools/skill_manager_tool.py` 中）。
3.  **起草**：使用 `write_file` 写入 `skills/<category>/<name>/SKILL.md`。
4.  **本地验证**：
    ```python
    import yaml, re, pathlib
    content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
    assert content.startswith("---")
    m = re.search(r'\n---\s*\n', content[3:])
    fm = yaml.safe_load(content[3:m.start()+3])
    assert "name" in fm and "description" in fm
    assert len(fm["description"]) <= 1024
    assert len(content) <= 100_000
    ```
5.  在活动分支上**执行 Git add + commit**。
6.  **注意：** 当前会话的技能加载器是缓存的 — 在新会话之前，`skill_view` / `skills_list` 将看不到新技能。这是预期行为，不是错误。

## 交叉引用其他技能

`metadata.hermes.related_skills` 在加载时合并两个目录树（仓库内的 `skills/` 和 `~/.hermes/skills/`）。你可以从仓库内技能引用用户本地技能，但对于全新克隆仓库的其他用户来说，这将无法解析。最好只从仓库内技能引用仓库内技能。如果一个经常被引用的技能只存在于 `~/.hermes/skills/` 中，请考虑将其提升到仓库中。

## 编辑现有的仓库内技能

-   **小修复（拼写错误、添加陷阱、收紧触发条件）：** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` 在仓库内技能上工作正常。
-   **重大重写：** 使用 `write_file` 重写整个 SKILL.md。`skill_manage(action='edit')` 也有效，但需要提供完整的新内容。
-   **添加支持文件：** 使用 `write_file` 写入 `skills/<category>/<name>/references/<file>.md`、`templates/<file>` 或 `scripts/<file>`。`skill_manage(action='write_file')` 也有效，并强制执行 references/templates/scripts/assets 子目录白名单。
-   **始终提交**编辑 — 仓库内技能是源代码，不是运行时状态。

## 常见陷阱

1.  **使用 `skill_manage(action='create')` 创建仓库内技能。** 它会写入 `~/.hermes/skills/`，而不是仓库目录树。对于仓库内创建，请使用 `write_file`。
2.  **在 `---` 前有前导空白。** 验证器检查 `content.startswith("---")`；任何前导空行或 BOM 都会导致验证失败。
3.  **描述过于笼统。** 对等技能描述以 "Use when ..." 开头，描述*触发类别*，而不是单一任务。"Use when debugging X" 优于 "Debug X"。
4.  **忘记 author/license/metadata 块。** 验证器不强制执行，但每个对等技能都有；省略会使技能看起来半成品。
5.  **编写与对等技能重复的技能。** 在创建之前，先 `ls skills/<category>/` 并打开 2-3 个对等技能。优先扩展现有技能，而不是创建一个狭窄的兄弟技能。
6.  **期望当前会话能看到新技能。** 它不会。技能加载器在会话开始时初始化。在新会话中或通过 `skill_view` 使用确切路径进行验证。
7.  **链接到仓库中不存在的技能。** `related_skills: [some-user-local-skill]` 对你有效，但对于其他克隆仓库的用户会失效。最好只使用仓库内链接。

## 验证清单

- [ ] 文件位于 `skills/<category>/<name>/SKILL.md`（不在 `~/.hermes/skills/` 中）
- [ ] Frontmatter 从字节 0 开始，以 `---` 开头，以 `\n---\n` 结束
- [ ] `name`、`description`、`version`、`author`、`license`、`metadata.hermes.{tags, related_skills}` 全部存在
- [ ] 名称 ≤ 64 个字符，小写 + 连字符
- [ ] 描述 ≤ 1024 个字符，并以 "Use when ..." 开头
- [ ] 总文件大小 ≤ 100,000 个字符（目标 8-15k）
- [ ] 结构：`# 标题` → `## 概述` → `## 何时使用` → 正文 → `## 常见陷阱` → `## 验证清单`
- [ ] `related_skills` 引用在仓库内可解析（或明确允许为用户本地）
- [ ] 在目标分支上完成了 `git add skills/<category>/<name>/ && git commit`