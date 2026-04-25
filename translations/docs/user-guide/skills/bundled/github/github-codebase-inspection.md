---
title: "代码库检查"
sidebar_label: "代码库检查"
description: "使用 pygount 检查和分析代码库，进行代码行数统计、语言分类以及代码与注释比例分析"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 代码库检查

使用 pygount 检查和分析代码库，进行代码行数统计、语言分类以及代码与注释比例分析。当被要求检查代码行数、仓库大小、语言构成或代码库统计数据时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/codebase-inspection` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `LOC`, `代码分析`, `pygount`, `代码库`, `指标`, `仓库` |
| 相关技能 | [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 使用 pygount 进行代码库检查

使用 `pygount` 分析仓库的代码行数、语言分类、文件数量以及代码与注释比例。

## 使用时机

- 用户询问 LOC（代码行数）统计
- 用户需要仓库的语言分类报告
- 用户询问代码库大小或构成
- 用户需要代码与注释比例
- 一般的“这个仓库有多大”类问题

## 先决条件

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. 基本摘要（最常用）

获取包含文件数量、代码行数和注释行数的完整语言分类报告：

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**重要提示：** 务必使用 `--folders-to-skip` 排除依赖项/构建目录，否则 pygount 会遍历它们，耗时很长甚至卡住。

## 2. 常用文件夹排除项

根据项目类型调整：

```bash
# Python 项目
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript 项目
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# 通用排除项
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. 按特定语言过滤

```bash
# 仅统计 Python 文件
pygount --suffix=py --format=summary .

# 仅统计 Python 和 YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. 详细的逐文件输出

```bash
# 默认格式显示每个文件的分类
pygount --folders-to-skip=".git,node_modules,venv" .

# 按代码行数排序（通过 sort 管道）
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. 输出格式

```bash
# 摘要表格（默认推荐）
pygount --format=summary .

# JSON 输出，便于程序化使用
pygount --format=json .

# 管道友好格式：语言、文件数、代码、文档、空行、字符串
pygount --format=summary . 2>/dev/null
```

## 6. 结果解读

摘要表格列说明：
- **语言** — 检测到的编程语言
- **文件数** — 该语言的文件数量
- **代码** — 实际代码行数（可执行/声明性）
- **注释** — 注释或文档行数
- **%** — 占总量的百分比

特殊的伪语言：
- `__empty__` — 空文件
- `__binary__` — 二进制文件（图像、编译文件等）
- `__generated__` — 自动生成的文件（启发式检测）
- `__duplicate__` — 内容相同的文件
- `__unknown__` — 无法识别的文件类型

## 注意事项

1. **务必排除 .git、node_modules、venv** — 不使用 `--folders-to-skip`，pygount 会遍历所有内容，对于大型依赖树可能需要数分钟甚至卡住。
2. **Markdown 显示 0 代码行** — pygount 将所有 Markdown 内容归类为注释，而非代码。这是预期行为。
3. **JSON 文件显示较低的代码行数** — pygount 可能保守地统计 JSON 行数。如需准确的 JSON 行数，请直接使用 `wc -l`。
4. **大型单体仓库** — 对于非常大的仓库，考虑使用 `--suffix` 来针对特定语言进行扫描，而不是扫描所有内容。