---
sidebar_position: 12
title: "使用技能"
description: "查找、安装、使用和创建技能——这些按需知识文档能教会 Hermes 新的工作流程"
---

# 使用技能

技能是按需知识文档，用于教会 Hermes 如何处理特定任务——从生成 ASCII 艺术到管理 GitHub PR。本指南将引导您日常使用它们。

完整的技术参考，请参阅[技能系统](/docs/user-guide/features/skills)。

---

## 查找技能

每个 Hermes 安装都附带捆绑的技能。查看可用的技能：

```bash
# 在任何聊天会话中：
/skills

# 或从 CLI：
hermes skills list
```

这将显示一个包含名称和描述的紧凑列表：

```
ascii-art         使用 pyfiglet、cowsay、boxes 等生成 ASCII 艺术...
arxiv             从 arXiv 搜索和检索学术论文...
github-pr-workflow 完整的 PR 生命周期——创建分支、提交...
plan              计划模式——检查上下文，编写 Markdown...
excalidraw        使用 Excalidraw 创建手绘风格图表...
```

### 搜索技能

```bash
# 按关键词搜索
/skills search docker
/skills search music
```

### 技能中心

官方的可选技能（默认不激活的较重量级或小众技能）可通过中心获取：

```bash
# 浏览官方的可选技能
/skills browse

# 搜索中心
/skills search blockchain
```

---

## 使用技能

每个已安装的技能都会自动成为一个斜杠命令。只需输入其名称：

```bash
# 加载一个技能并给它一个任务
/ascii-art 制作一个写着 "HELLO WORLD" 的横幅
/plan 为待办事项应用设计一个 REST API
/github-pr-workflow 为身份验证重构创建一个 PR

# 仅输入技能名称（无任务）会加载它，并让您描述需求
/excalidraw
```

您也可以通过自然对话触发技能——要求 Hermes 使用特定技能，它将通过 `skill_view` 工具加载它。

### 渐进式披露

技能使用一种节省 Token 的加载模式。Agent 不会一次性加载所有内容：

1.  **`skills_list()`** —— 所有技能的紧凑列表（约 3k Token）。在会话开始时加载。
2.  **`skill_view(name)`** —— 单个技能的完整 SKILL.md 内容。当 Agent 确定需要该技能时加载。
3.  **`skill_view(name, file_path)`** —— 技能内的特定参考文件。仅在需要时加载。

这意味着技能在实际使用之前不会消耗 Token。

---

## 从中心安装

官方的可选技能随 Hermes 一起提供，但默认不激活。需要显式安装它们：

```bash
# 安装一个官方的可选技能
hermes skills install official/research/arxiv

# 在聊天会话中从中心安装
/skills install official/creative/songwriting-and-ai-music
```

会发生什么：
1.  技能目录被复制到 `~/.hermes/skills/`
2.  它出现在您的 `skills_list` 输出中
3.  它作为一个斜杠命令变得可用

:::tip
已安装的技能在新会话中生效。如果您希望它在当前会话中可用，请使用 `/reset` 重新开始，或者添加 `--now` 以立即使提示词缓存失效（在下一轮会消耗更多 Token）。
:::

### 验证安装

```bash
# 检查它是否存在
hermes skills list | grep arxiv

# 或在聊天中
/skills search arxiv
```

---

## 配置技能设置

一些技能在其 frontmatter 中声明它们需要的配置：

```yaml
metadata:
  hermes:
    config:
      - key: tenor.api_key
        description: "用于 GIF 搜索的 Tenor API 密钥"
        prompt: "输入您的 Tenor API 密钥"
        url: "https://developers.google.com/tenor/guides/quickstart"
```

当首次加载带有配置的技能时，Hermes 会提示您输入值。它们存储在 `config.yaml` 中的 `skills.config.*` 下。

从 CLI 管理技能配置：

```bash
# 特定技能的交互式配置
hermes skills config gif-search

# 查看所有技能配置
hermes config get skills.config
```

---

## 创建您自己的技能

技能只是带有 YAML frontmatter 的 Markdown 文件。创建一个技能不到五分钟。

### 1. 创建目录

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. 编写 SKILL.md

```markdown title="~/.hermes/skills/my-category/my-skill/SKILL.md"
---
name: my-skill
description: 此技能功能的简要描述
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# 我的技能

## 何时使用
当用户询问[特定主题]或需要[特定任务]时使用此技能。

## 步骤
1.  首先，检查[先决条件]是否可用
2.  运行 `command --with-flags`
3.  解析输出并呈现结果

## 常见问题
-   常见故障：[描述]。修复方法：[解决方案]
-   注意[边缘情况]

## 验证
运行 `check-command` 以确认结果正确。
```

### 3. 添加参考文件（可选）

技能可以包含 Agent 按需加载的支持文件：

```
my-skill/
├── SKILL.md                    # 主技能文档
├── references/
│   ├── api-docs.md             # Agent 可以查阅的 API 参考
│   └── examples.md             # 输入/输出示例
├── templates/
│   └── config.yaml             # Agent 可以使用的模板文件
└── scripts/
    └── setup.sh                # Agent 可以执行的脚本
```

在您的 SKILL.md 中引用这些文件：

```markdown
有关 API 详细信息，请加载参考：`skill_view("my-skill", "references/api-docs.md")`
```

### 4. 测试它

启动一个新会话并尝试您的技能：

```bash
hermes chat -q "/my-skill help me with the thing"
```

该技能会自动出现——无需注册。将其放入 `~/.hermes/skills/` 即可生效。

:::info
Agent 也可以使用 `skill_manage` 自行创建和更新技能。在解决复杂问题后，Hermes 可能会提议将方法保存为技能以备下次使用。
:::

---

## 按平台管理技能

控制哪些技能在哪些平台上可用：

```bash
hermes skills
```

这将打开一个交互式 TUI，您可以在其中按平台（CLI、Telegram、Discord 等）启用或禁用技能。当您希望某些技能仅在特定上下文中可用时非常有用——例如，在 Telegram 上禁用开发技能。

---

## 技能与记忆

两者都跨会话持久化，但用途不同：

| | 技能 | 记忆 |
|---|---|---|
| **是什么** | 程序性知识——如何做事情 | 事实性知识——事情是什么 |
| **何时** | 按需加载，仅在相关时 | 自动注入到每个会话中 |
| **大小** | 可以很大（数百行） | 应该紧凑（仅关键事实） |
| **成本** | 加载前零 Token | 小但持续的 Token 成本 |
| **示例** | "如何部署到 Kubernetes" | "用户偏好深色模式，住在太平洋标准时间" |
| **谁创建** | 您、Agent 或从中心安装 | Agent，基于对话 |

**经验法则：** 如果您会把它放在参考文档中，它就是技能。如果您会把它写在便利贴上，它就是记忆。

---

## 技巧

**保持技能专注。** 一个试图涵盖"所有 DevOps"的技能会太长且太模糊。一个涵盖"将 Python 应用部署到 Fly.io"的技能则足够具体，真正有用。

**让 Agent 创建技能。** 完成复杂的多步骤任务后，Hermes 通常会提议将方法保存为技能。请同意——这些由 Agent 编写的技能捕获了确切的工作流程，包括沿途发现的常见问题。

**使用分类。** 将技能组织到子目录中（`~/.hermes/skills/devops/`、`~/.hermes/skills/research/` 等）。这使列表易于管理，并帮助 Agent 更快地找到相关技能。

**当技能过时时更新它们。** 如果您使用某个技能时遇到了它未涵盖的问题，请告诉 Hermes 用您学到的知识更新该技能。未维护的技能会成为负担。

---

*有关完整的技能参考——frontmatter 字段、条件激活、外部目录等——请参阅[技能系统](/docs/user-guide/features/skills)。*