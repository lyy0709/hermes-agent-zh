---
sidebar_position: 8
title: "上下文文件"
description: "项目上下文文件 — .hermes.md、AGENTS.md、CLAUDE.md、全局 SOUL.md 和 .cursorrules — 会自动注入到每次对话中"
---

# 上下文文件

Hermes Agent 会自动发现并加载用于塑造其行为的上下文文件。有些是项目本地的，从你的工作目录中发现。`SOUL.md` 现在对 Hermes 实例是全局的，并且只从 `HERMES_HOME` 加载。

## 支持的上下文文件

| 文件 | 用途 | 发现方式 |
|------|---------|-----------|
| **.hermes.md** / **HERMES.md** | 项目指令（最高优先级） | 向上遍历到 git 根目录 |
| **AGENTS.md** | 项目指令、约定、架构 | 启动时的 CWD + 逐步遍历子目录 |
| **CLAUDE.md** | Claude Code 上下文文件（同样会被检测） | 启动时的 CWD + 逐步遍历子目录 |
| **SOUL.md** | 此 Hermes 实例的全局个性和语气自定义 | 仅从 `HERMES_HOME/SOUL.md` |
| **.cursorrules** | Cursor IDE 编码约定 | 仅 CWD |
| **.cursor/rules/*.mdc** | Cursor IDE 规则模块 | 仅 CWD |

:::info 优先级系统
每个会话只加载**一种**项目上下文类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。**SOUL.md** 总是作为 Agent 身份（槽位 #1）独立加载。
:::

## AGENTS.md

`AGENTS.md` 是主要的项目上下文文件。它告诉 Agent 你的项目是如何构建的，需要遵循哪些约定，以及任何特殊指令。

### 渐进式子目录发现

在会话开始时，Hermes 会将你工作目录中的 `AGENTS.md` 加载到系统提示词中。当 Agent 在会话期间（通过 `read_file`、`terminal`、`search_files` 等）导航到子目录时，它会**逐步发现**这些目录中的上下文文件，并在它们变得相关时立即将其注入到对话中。

```
my-project/
├── AGENTS.md              ← 启动时加载（系统提示词）
├── frontend/
│   └── AGENTS.md          ← 当 Agent 读取 frontend/ 文件时发现
├── backend/
│   └── AGENTS.md          ← 当 Agent 读取 backend/ 文件时发现
└── shared/
    └── AGENTS.md          ← 当 Agent 读取 shared/ 文件时发现
```

与在启动时加载所有内容相比，这种方法有两个优点：
- **避免系统提示词臃肿** — 子目录提示仅在需要时出现
- **保持提示词缓存** — 系统提示词在多轮对话中保持稳定

每个子目录在每个会话中最多检查一次。发现过程也会向上遍历父目录，因此读取 `backend/src/main.py` 会发现 `backend/AGENTS.md`，即使 `backend/src/` 本身没有上下文文件。

:::info
子目录上下文文件会经过与启动上下文文件相同的[安全扫描](#security-prompt-injection-protection)。恶意文件会被阻止。
:::

### AGENTS.md 示例

```markdown
# 项目上下文

这是一个带有 Python FastAPI 后端的 Next.js 14 Web 应用程序。

## 架构
- 前端：Next.js 14，使用 App Router，位于 `/frontend`
- 后端：FastAPI，位于 `/backend`，使用 SQLAlchemy ORM
- 数据库：PostgreSQL 16
- 部署：在 Hetzner VPS 上使用 Docker Compose

## 约定
- 所有前端代码使用 TypeScript 严格模式
- Python 代码遵循 PEP 8，处处使用类型提示
- 所有 API 端点返回 `{data, error, meta}` 格式的 JSON
- 测试放在 `__tests__/` 目录（前端）或 `tests/` 目录（后端）

## 重要说明
- 切勿直接修改迁移文件 — 使用 Alembic 命令
- `.env.local` 文件包含真实的 API 密钥，不要提交它
- 前端端口是 3000，后端是 8000，数据库是 5432
```

## SOUL.md

`SOUL.md` 控制 Agent 的个性、语气和沟通风格。完整详情请参阅[个性](/docs/user-guide/features/personality)页面。

**位置：**

- `~/.hermes/SOUL.md`
- 或者，如果你使用自定义主目录运行 Hermes，则为 `$HERMES_HOME/SOUL.md`

重要细节：

- 如果 `SOUL.md` 尚不存在，Hermes 会自动生成一个默认的
- Hermes 只从 `HERMES_HOME` 加载 `SOUL.md`
- Hermes 不会在工作目录中探测 `SOUL.md`
- 如果文件为空，则不会向提示词添加任何来自 `SOUL.md` 的内容
- 如果文件有内容，则在扫描和截断后逐字注入内容

## .cursorrules

Hermes 兼容 Cursor IDE 的 `.cursorrules` 文件和 `.cursor/rules/*.mdc` 规则模块。如果这些文件存在于你的项目根目录中，并且没有找到更高优先级的上下文文件（`.hermes.md`、`AGENTS.md` 或 `CLAUDE.md`），它们将作为项目上下文被加载。

这意味着你现有的 Cursor 约定在使用 Hermes 时会自动应用。

## 上下文文件的加载方式

### 启动时（系统提示词）

上下文文件由 `agent/prompt_builder.py` 中的 `build_context_files_prompt()` 加载：

1.  **扫描工作目录** — 检查 `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`（首次匹配优先）
2.  **读取内容** — 每个文件作为 UTF-8 文本读取
3.  **安全扫描** — 检查内容是否存在提示词注入模式
4.  **截断** — 超过 20,000 个字符的文件会被头尾截断（70% 头部，20% 尾部，中间有标记）
5.  **组装** — 所有部分在 `# 项目上下文` 标题下组合
6.  **注入** — 组装好的内容被添加到系统提示词中

### 会话期间（渐进式发现）

`agent/subdirectory_hints.py` 中的 `SubdirectoryHintTracker` 监视工具调用参数中的文件路径：

1.  **路径提取** — 每次工具调用后，从参数（`path`、`workdir`、shell 命令）中提取文件路径
2.  **祖先遍历** — 检查该目录及其最多 5 个父目录（在已访问的目录处停止）
3.  **提示加载** — 如果找到 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，则加载它（每个目录首次匹配）
4.  **安全扫描** — 与启动文件相同的提示词注入扫描
5.  **截断** — 每个文件限制在 8,000 个字符以内
6.  **注入** — 附加到工具结果中，因此模型可以在上下文中自然地看到它

最终的提示词部分大致如下：

```text
# 项目上下文

以下项目上下文文件已加载，应予以遵循：

## AGENTS.md

[你的 AGENTS.md 内容在这里]

## .cursorrules

[你的 .cursorrules 内容在这里]

[你的 SOUL.md 内容在这里]
```

注意，SOUL 内容是直接插入的，没有额外的包装文本。

## 安全：提示词注入防护

所有上下文文件在包含之前都会扫描潜在的提示词注入。扫描器检查：

-   **指令覆盖尝试**："ignore previous instructions"、"disregard your rules"
-   **欺骗模式**："do not tell the user"
-   **系统提示词覆盖**："system prompt override"
-   **隐藏的 HTML 注释**：`<!-- ignore instructions -->`
-   **隐藏的 div 元素**：`<div style="display:none">`
-   **凭据泄露**：`curl ... $API_KEY`
-   **秘密文件访问**：`cat .env`、`cat credentials`
-   **不可见字符**：零宽空格、双向覆盖、连接符

如果检测到任何威胁模式，文件将被阻止：

```
[已阻止：AGENTS.md 包含潜在的提示词注入 (prompt_injection)。内容未加载。]
```

:::warning
此扫描器可防范常见的注入模式，但它不能替代审查共享仓库中的上下文文件。请务必验证非你本人创建的项目中的 AGENTS.md 内容。
:::

## 大小限制

| 限制 | 值 |
|-------|-------|
| 每个文件最大字符数 | 20,000 (~7,000 Token) |
| 头部截断比例 | 70% |
| 尾部截断比例 | 20% |
| 截断标记 | 10%（显示字符数并建议使用文件工具） |

当文件超过 20,000 个字符时，截断消息显示为：

```
[...已截断 AGENTS.md：保留了 25000 个字符中的 14000+4000 个。使用文件工具读取完整文件。]
```

## 创建有效上下文文件的技巧

:::tip AGENTS.md 最佳实践
1.  **保持简洁** — 远低于 20K 字符；Agent 每轮都会读取它
2.  **使用标题结构化** — 使用 `##` 部分表示架构、约定、重要说明
3.  **包含具体示例** — 展示首选的代码模式、API 结构、命名约定
4.  **提及不应做的事情** — "切勿直接修改迁移文件"
5.  **列出关键路径和端口** — Agent 在终端命令中使用这些信息
6.  **随着项目发展而更新** — 过时的上下文比没有上下文更糟糕
:::

### 按子目录设置上下文

对于单体仓库，将特定于子目录的指令放在嵌套的 AGENTS.md 文件中：

```markdown
<!-- frontend/AGENTS.md -->
# 前端上下文

- 使用 `pnpm`，而不是 `npm` 进行包管理
- 组件放在 `src/components/`，页面放在 `src/app/`
- 使用 Tailwind CSS，切勿使用内联样式
- 使用 `pnpm test` 运行测试
```

```markdown
<!-- backend/AGENTS.md -->
# 后端上下文

- 使用 `poetry` 进行依赖管理
- 使用 `poetry run uvicorn main:app --reload` 运行开发服务器
- 所有端点都需要 OpenAPI 文档字符串
- 数据库模型在 `models/` 中，模式在 `schemas/` 中
```