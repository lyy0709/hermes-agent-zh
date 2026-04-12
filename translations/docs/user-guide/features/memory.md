---
sidebar_position: 3
title: "持久化记忆"
description: "Hermes Agent 如何在会话间保持记忆 — MEMORY.md、USER.md 和会话搜索"
---

# 持久化记忆

Hermes Agent 拥有有限的、经过筛选的记忆，这些记忆在会话间持久存在。这使得它能够记住您的偏好、项目、执行环境以及它学到的东西。

## 工作原理

Agent 的记忆由两个文件构成：

| 文件 | 用途 | 字符限制 |
|------|---------|------------|
| **MEMORY.md** | Agent 的个人笔记 — 环境事实、约定、学到的东西 | 2,200 字符 (~800 Token) |
| **USER.md** | 用户档案 — 您的偏好、沟通风格、期望 | 1,375 字符 (~500 Token) |

两者都存储在 `~/.hermes/memories/` 目录下，并在会话开始时作为冻结的快照注入到系统提示词中。Agent 通过 `memory` 工具管理自己的记忆 — 它可以添加、替换或删除条目。

:::info
字符限制使记忆保持聚焦。当记忆已满时，Agent 会合并或替换条目，为新信息腾出空间。
:::

## 记忆在系统提示词中的呈现方式

在每个会话开始时，记忆条目会从磁盘加载，并以冻结块的形式渲染到系统提示词中：

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

格式包括：
- 显示存储类型（MEMORY 或 USER PROFILE）的标题
- 使用百分比和字符计数，以便 Agent 了解容量
- 由 `§`（节号）分隔符分隔的各个条目
- 条目可以是多行的

**冻结快照模式：** 系统提示词注入在会话开始时捕获一次，在会话中永不更改。这是有意为之 — 它保留了 LLM 的前缀缓存以提高性能。当 Agent 在会话期间添加/删除记忆条目时，更改会立即持久化到磁盘，但直到下一个会话开始时才会出现在系统提示词中。工具响应始终显示实时状态。

## 记忆工具操作

Agent 使用 `memory` 工具执行以下操作：

- **add** — 添加新的记忆条目
- **replace** — 用更新后的内容替换现有条目（通过 `old_text` 使用子字符串匹配）
- **remove** — 删除不再相关的条目（通过 `old_text` 使用子字符串匹配）

没有 `read` 操作 — 记忆内容会在会话开始时自动注入到系统提示词中。Agent 将其记忆视为其对话上下文的一部分。

### 子字符串匹配

`replace` 和 `remove` 操作使用简短、唯一的子字符串匹配 — 您不需要完整的条目文本。`old_text` 参数只需要是一个能唯一标识一个条目的子字符串：

```python
# 如果记忆包含 "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

如果子字符串匹配多个条目，则会返回错误，要求提供更具体的匹配项。

## 两个目标详解

### `memory` — Agent 的个人笔记

用于 Agent 需要记住的关于环境、工作流程和所学经验的信息：

- 环境事实（操作系统、工具、项目结构）
- 项目约定和配置
- 发现的工具怪癖和解决方法
- 已完成任务的日记条目
- 有效的技能和技术

### `user` — 用户档案

用于关于用户身份、偏好和沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁 vs 详细、格式偏好）
- 讨厌的事物和需要避免的事情
- 工作流程习惯
- 技术水平

## 保存什么 vs 跳过什么

### 保存这些（主动）

Agent 会自动保存 — 您无需要求。它在学到以下内容时保存：

- **用户偏好：** "我更喜欢 TypeScript 而不是 JavaScript" → 保存到 `user`
- **环境事实：** "此服务器运行 Debian 12 和 PostgreSQL 16" → 保存到 `memory`
- **更正：** "不要对 Docker 命令使用 `sudo`，用户属于 docker 组" → 保存到 `memory`
- **约定：** "项目使用制表符、120 字符行宽、Google 风格的文档字符串" → 保存到 `memory`
- **已完成的工作：** "于 2026-01-15 将数据库从 MySQL 迁移到 PostgreSQL" → 保存到 `memory`
- **明确请求：** "记住我的 API 密钥每月轮换一次" → 保存到 `memory`

### 跳过这些

- **琐碎/明显的信息：** "用户询问了 Python" — 太模糊，没有用处
- **容易重新发现的事实：** "Python 3.12 支持 f-string 嵌套" — 可以网络搜索这个
- **原始数据转储：** 大型代码块、日志文件、数据表 — 对于记忆来说太大
- **特定于会话的临时信息：** 临时文件路径、一次性调试上下文
- **已在上下文文件中的信息：** SOUL.md 和 AGENTS.md 的内容

## 容量管理

记忆有严格的字符限制，以保持系统提示词的有界性：

| 存储 | 限制 | 典型条目数 |
|-------|-------|----------------|
| memory | 2,200 字符 | 8-15 个条目 |
| user | 1,375 字符 | 5-10 个条目 |

### 当记忆已满时会发生什么

当您尝试添加一个会超出限制的条目时，工具会返回错误：

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Replace or remove existing entries first.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

然后 Agent 应该：
1.  读取当前条目（在错误响应中显示）
2.  识别可以删除或合并的条目
3.  使用 `replace` 将相关条目合并为更短的版本
4.  然后 `add` 新条目

**最佳实践：** 当记忆容量超过 80%（在系统提示词标题中可见）时，在添加新条目之前先合并条目。例如，将三个独立的 "项目使用 X" 条目合并为一个全面的项目描述条目。

### 良好记忆条目的实际示例

**紧凑、信息密集的条目效果最佳：**

```
# 好：打包多个相关事实
用户运行 macOS 14 Sonoma，使用 Homebrew，安装了 Docker Desktop 和 Podman。Shell：zsh 配合 oh-my-zsh。编辑器：VS Code 配合 Vim 键绑定。

# 好：具体、可操作的约定
项目 ~/code/api 使用 Go 1.22、sqlc 处理数据库查询、chi 路由器。用 'make test' 运行测试。CI 通过 GitHub Actions。

# 好：附带上下文的经验教训
暂存服务器 (10.0.1.50) 需要 SSH 端口 2222，而不是 22。密钥位于 ~/.ssh/staging_ed25519。

# 差：太模糊
用户有一个项目。

# 差：太冗长
在 2026 年 1 月 5 日，用户让我查看他们的项目，该项目位于 ~/code/api。我发现它使用 Go 版本 1.22 并且...
```

## 重复项预防

记忆系统会自动拒绝完全重复的条目。如果您尝试添加已存在的内容，它会返回成功并附带 "no duplicate added" 消息。

## 安全扫描

记忆条目在被接受之前会进行注入和泄露模式扫描，因为它们会被注入到系统提示词中。匹配威胁模式（提示词注入、凭据泄露、SSH 后门）或包含不可见 Unicode 字符的内容会被阻止。

## 会话搜索

除了 MEMORY.md 和 USER.md，Agent 还可以使用 `session_search` 工具搜索其过去的对话：

- 所有 CLI 和消息会话都存储在 SQLite (`~/.hermes/state.db`) 中，支持 FTS5 全文搜索
- 搜索查询返回相关的过去对话，并附带 Gemini Flash 摘要
- Agent 可以找到几周前讨论过的事情，即使它们不在其活动记忆中

```bash
hermes sessions list    # 浏览过去的会话
```

### session_search 与 memory 对比

| 特性 | 持久化记忆 | 会话搜索 |
|---------|------------------|----------------|
| **容量** | 总计约 1,300 Token | 无限制（所有会话） |
| **速度** | 即时（在系统提示词中） | 需要搜索 + LLM 摘要 |
| **使用场景** | 始终可用的关键事实 | 查找特定的过去对话 |
| **管理** | 由 Agent 手动筛选 | 自动 — 存储所有会话 |
| **Token 成本** | 每个会话固定（约 1,300 Token） | 按需（需要时搜索） |

**记忆** 用于应始终在上下文中的关键事实。**会话搜索** 用于 "我们上周讨论过 X 吗？" 这类查询，其中 Agent 需要回忆过去对话的具体内容。

## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 Token
  user_char_limit: 1375     # ~500 Token
```

## 外部记忆提供商

对于超越 MEMORY.md 和 USER.md 的更深入、持久的记忆，Hermes 附带了 8 个外部记忆提供商插件 — 包括 Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 和 Supermemory。

外部提供商与内置记忆**并行**运行（从不替换它），并增加了知识图谱、语义搜索、自动事实提取和跨会话用户建模等功能。

```bash
hermes memory setup      # 选择并配置一个提供商
hermes memory status     # 检查当前激活的提供商
```

有关每个提供商的完整详细信息、设置说明和比较，请参阅[记忆提供商](./memory-providers.md)指南。