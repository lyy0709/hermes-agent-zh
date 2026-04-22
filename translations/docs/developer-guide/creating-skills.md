---
sidebar_position: 3
title: "创建技能"
description: "如何为 Hermes Agent 创建技能 — SKILL.md 格式、指南和发布"
---

# 创建技能

技能是为 Hermes Agent 添加新功能的首选方式。它们比工具更容易创建，无需修改 Agent 的代码，并且可以与社区共享。

## 应该创建技能还是工具？

在以下情况下创建**技能**：
- 该功能可以表示为指令 + shell 命令 + 现有工具的组合
- 它封装了一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用
- 它不需要内置到 Agent 中的自定义 Python 集成或 API 密钥管理
- 例如：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件

在以下情况下创建**工具**：
- 它需要与 API 密钥、认证流程或多组件配置进行端到端集成
- 它需要每次都必须精确执行的自定义处理逻辑
- 它处理二进制数据、流式传输或实时事件
- 例如：浏览器自动化、TTS、视觉分析

## 技能目录结构

捆绑的技能位于按类别组织的 `skills/` 目录中。官方的可选技能在 `optional-skills/` 中使用相同的结构：

```text
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # 必需：主要指令
│       └── scripts/              # 可选：辅助脚本
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

## SKILL.md 格式

```markdown
---
name: my-skill
description: 简要描述（显示在技能搜索结果中）
version: 1.0.0
author: 你的名字
license: MIT
platforms: [macos, linux]          # 可选 — 限制在特定的操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则加载到所有平台（默认）
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # 可选 — 仅当这些工具集处于活动状态时显示
    requires_tools: [web_search]        # 可选 — 仅当这些工具可用时显示
    fallback_for_toolsets: [browser]    # 可选 — 当这些工具集处于活动状态时隐藏
    fallback_for_tools: [browser_navigate]  # 可选 — 当这些工具存在时隐藏
    config:                              # 可选 — 技能需要的 config.yaml 设置
      - key: my.setting
        description: "此设置控制的内容"
        default: "sensible-default"
        prompt: "设置时显示的提示"
required_environment_variables:          # 可选 — 技能需要的环境变量
  - name: MY_API_KEY
    prompt: "输入你的 API 密钥"
    help: "在 https://example.com 获取"
    required_for: "API 访问"
---

# 技能标题

简要介绍。

## 何时使用
触发条件 — Agent 应该在何时加载此技能？

## 快速参考
常用命令或 API 调用的表格。

## 步骤
Agent 遵循的分步指令。

## 常见问题
已知的失败模式及处理方法。

## 验证
Agent 如何确认操作成功。
```

### 平台特定技能

技能可以使用 `platforms` 字段限制自己只在特定的操作系统上运行：

```yaml
platforms: [macos]            # 仅 macOS（例如，iMessage、Apple Reminders）
platforms: [macos, linux]     # macOS 和 Linux
platforms: [windows]          # 仅 Windows
```

设置后，该技能在不兼容的平台上会自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。如果省略或为空，则技能在所有平台上加载（向后兼容）。

### 条件性技能激活

技能可以声明对特定工具或工具集的依赖。这控制了该技能是否出现在给定会话的系统提示词中。

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # 如果 web 工具集处于**非**活动状态，则隐藏
    requires_tools: [web_search]       # 如果 web_search 工具**不**可用，则隐藏
    fallback_for_toolsets: [browser]   # 如果 browser 工具集**处于**活动状态，则隐藏
    fallback_for_tools: [browser_navigate]  # 如果 browser_navigate **可用**，则隐藏
```

| 字段 | 行为 |
|-------|----------|
| `requires_toolsets` | 当**任何**列出的工具集**不**可用时，技能被**隐藏** |
| `requires_tools` | 当**任何**列出的工具**不**可用时，技能被**隐藏** |
| `fallback_for_toolsets` | 当**任何**列出的工具集**处于**可用状态时，技能被**隐藏** |
| `fallback_for_tools` | 当**任何**列出的工具**处于**可用状态时，技能被**隐藏** |

**`fallback_for_*` 的使用场景：** 创建一个在主工具不可用时的备用技能。例如，一个带有 `fallback_for_tools: [web_search]` 的 `duckduckgo-search` 技能，仅当 web 搜索工具（需要 API 密钥）未配置时显示。

**`requires_*` 的使用场景：** 创建一个仅在特定工具存在时才有意义的技能。例如，一个带有 `requires_toolsets: [web]` 的网页抓取工作流技能，在 web 工具被禁用时不会使提示词变得杂乱。

### 环境变量要求

技能可以声明它们需要的环境变量。当通过 `skill_view` 加载技能时，其所需的变量会自动注册，以便传递到沙盒化的执行环境（terminal, execute_code）中。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API 密钥"               # 提示用户时显示
    help: "在 https://tenor.com 获取你的密钥"  # 帮助文本或 URL
    required_for: "GIF 搜索功能"   # 哪个功能需要此变量
```

每个条目支持：
- `name`（必需）— 环境变量名称
- `prompt`（可选）— 向用户询问值时显示的提示文本
- `help`（可选）— 获取该值的帮助文本或 URL
- `required_for`（可选）— 描述哪个功能需要此变量

用户也可以在 `config.yaml` 中手动配置传递变量：
```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

查看 `skills/apple/` 目录获取仅限 macOS 的技能示例。

## 加载时的安全设置

当技能需要 API 密钥或 Token 时，使用 `required_environment_variables`。缺失的值**不会**在发现时隐藏该技能。相反，Hermes 会在本地 CLI 中加载该技能时安全地提示用户输入。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
    required_for: 完整功能
```

用户可以跳过设置并继续加载该技能。Hermes 永远不会向模型暴露原始的秘密值。消息网关和消息会话会显示本地设置指南，而不是在会话内收集秘密。

:::tip 沙盒透传
当你的技能加载时，任何已设置的已声明的 `required_environment_variables` 都会**自动透传**到 `execute_code` 和 `terminal` 沙盒——包括像 Docker 和 Modal 这样的远程后端。你的技能脚本可以访问 `$TENOR_API_KEY`（或在 Python 中访问 `os.environ["TENOR_API_KEY"]`），而无需用户进行任何额外配置。详情请参阅[环境变量透传](/docs/user-guide/security#environment-variable-passthrough)。
:::

为了向后兼容，仍支持旧版的 `prerequisites.env_vars` 作为别名。

### 配置设置 (config.yaml)

技能可以声明存储在 `config.yaml` 中 `skills.config` 命名空间下的非秘密设置。与环境变量（存储在 `.env` 中的秘密）不同，配置设置用于路径、偏好设置和其他非敏感值。

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: 插件数据目录的路径
        default: "~/myplugin-data"
        prompt: 插件数据目录路径
      - key: myplugin.domain
        description: 插件操作的领域
        default: ""
        prompt: 插件领域（例如，AI/ML 研究）
```

每个条目支持：
- `key`（必需）— 设置的路径（例如，`myplugin.path`）
- `description`（必需）— 解释该设置控制什么
- `default`（可选）— 如果用户未配置，则使用默认值
- `prompt`（可选）— 在 `hermes config migrate` 期间显示的提示文本；回退到 `description`

**工作原理：**

1.  **存储：** 值被写入 `config.yaml` 中的 `skills.config.<key>` 下：
    ```yaml
    skills:
      config:
        myplugin:
          path: ~/my-data
    ```

2.  **发现：** `hermes config migrate` 扫描所有启用的技能，查找未配置的设置，并提示用户。设置也会出现在 `hermes config show` 的 "技能设置" 下。

3.  **运行时注入：** 当技能加载时，其配置值会被解析并附加到技能消息中：
    ```
    [技能配置（来自 ~/.hermes/config.yaml）：
      myplugin.path = /home/user/my-data
    ]
    ```
    Agent 可以看到配置好的值，而无需自己读取 `config.yaml`。

4.  **手动设置：** 用户也可以直接设置值：
    ```bash
    hermes config set skills.config.myplugin.path ~/my-data
    ```

:::tip 何时使用哪个
使用 `required_environment_variables` 处理 API 密钥、Token 和其他**秘密**（存储在 `~/.hermes/.env` 中，从不向模型显示）。使用 `config` 处理**路径、偏好设置和非敏感设置**（存储在 `config.yaml` 中，在 config show 中可见）。
:::

### 凭证文件要求（OAuth Token 等）

使用 OAuth 或基于文件的凭证的技能可以声明需要挂载到远程沙盒中的文件。这适用于存储为**文件**的凭证（不是环境变量）——通常是由设置脚本生成的 OAuth Token 文件。

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 Token（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭证
```

每个条目支持：
- `path`（必需）— 相对于 `~/.hermes/` 的文件路径
- `description`（可选）— 解释文件是什么以及如何创建

加载时，Hermes 会检查这些文件是否存在。缺失的文件会触发 `setup_needed`。存在的文件会自动：
- **挂载到 Docker** 容器中作为只读绑定挂载
- **同步到 Modal** 沙盒中（在创建时 + 每个命令执行前，因此会话中的 OAuth 可以工作）
- 在**本地**后端上可用，无需任何特殊处理

:::tip 何时使用哪个
使用 `required_environment_variables` 处理简单的 API 密钥和 Token（存储在 `~/.hermes/.env` 中的字符串）。使用 `required_credential_files` 处理 OAuth Token 文件、客户端秘密、服务账户 JSON、证书或任何存储在磁盘上的凭证文件。
:::

查看 `skills/productivity/google-workspace/SKILL.md` 获取同时使用两者的完整示例。

## 技能指南

### 无外部依赖

优先使用标准库 Python、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。如果需要依赖项，请在技能中记录安装步骤。

### 渐进式披露

将最常见的工作流程放在前面。边缘情况和高级用法放在底部。这可以降低常见任务的 Token 使用量。

### 包含辅助脚本

对于 XML/JSON 解析或复杂逻辑，请在 `scripts/` 中包含辅助脚本——不要期望 LLM 每次都内联编写解析器。

#### 从 SKILL.md 引用捆绑的脚本

当技能加载时，激活消息会将绝对技能目录暴露为 `[技能目录：/abs/path]`，并且还会在 SKILL.md 正文的任何地方替换两个模板 Token：

| Token | 替换为 |
|---|---|
| `${HERMES_SKILL_DIR}` | 技能目录的绝对路径 |
| `${HERMES_SESSION_ID}` | 活动会话 ID（如果没有会话，则保留原样） |

因此，SKILL.md 可以告诉 Agent 直接运行捆绑的脚本：

```markdown
要分析输入，请运行：

    node ${HERMES_SKILL_DIR}/scripts/analyse.js <input>
```

Agent 会看到替换后的绝对路径，并使用一个可立即运行的命令调用 `terminal` 工具——无需路径计算，无需额外的 `skill_view` 往返。可以在 `config.yaml` 中通过设置 `skills.template_vars: false` 全局禁用替换。
#### 内联 Shell 代码片段（需手动启用）

技能也可以在 SKILL.md 正文中嵌入以内联 Shell 代码片段形式编写的 `` !`cmd` ``。启用后，每个代码片段的 stdout 会在 Agent 读取消息之前被内联到消息中，这样技能就可以注入动态上下文：

```markdown
当前日期: !`date -u +%Y-%m-%d`
Git 分支: !`git -C ${HERMES_SKILL_DIR} rev-parse --abbrev-ref HEAD`
```

此功能**默认关闭**——SKILL.md 中的任何代码片段都会在主机上未经批准运行，因此请仅对您信任的技能源启用它：

```yaml
# config.yaml
skills:
  inline_shell: true
  inline_shell_timeout: 10   # 每个代码片段的超时时间（秒）
```

代码片段以技能目录作为其工作目录运行，输出限制在 4000 个字符以内。失败（超时、非零退出）会显示为简短的 `[inline-shell error: ...]` 标记，而不会破坏整个技能。

### 测试它

运行该技能并验证 Agent 是否正确遵循指令：

```bash
hermes chat --toolsets skills -q "使用 X 技能来做 Y"
```

## 技能应该存放在哪里？

捆绑技能（位于 `skills/` 目录下）随每个 Hermes 安装包一起发布。它们应该**对大多数用户普遍有用**：

- 文档处理、网络研究、常见的开发工作流、系统管理
- 被广泛人群定期使用

如果你的技能是官方的且有用，但并非普遍需要（例如，付费服务集成、重量级依赖项），请将其放入 **`optional-skills/`** 目录——它随代码仓库一起发布，可通过 `hermes skills browse` 发现（标记为 "official"），并以内置信任级别安装。

如果你的技能是专业化的、社区贡献的或小众的，它更适合放在 **技能中心**——将其上传到注册表并通过 `hermes skills install` 分享。

## 发布技能

### 发布到技能中心

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### 发布到自定义仓库

将你的仓库添加为一个 tap：

```bash
hermes skills tap add owner/repo
```

然后用户就可以从你的仓库中搜索和安装技能。

## 安全扫描

所有从中心安装的技能都会经过安全扫描器检查，检查内容包括：

- 数据外泄模式
- 提示词注入尝试
- 破坏性命令
- Shell 注入

信任级别：
- `builtin` —— 随 Hermes 一起发布（始终受信任）
- `official` —— 来自代码仓库中的 `optional-skills/` 目录（内置信任，无第三方警告）
- `trusted` —— 来自 openai/skills, anthropics/skills
- `community` —— 非危险发现可以通过 `--force` 覆盖；`dangerous` 判定结果仍会被阻止

Hermes 现在可以从多个外部发现模型消费第三方技能：
- 直接的 GitHub 标识符（例如 `openai/skills/k8s`）
- `skills.sh` 标识符（例如 `skills-sh/vercel-labs/json-render/json-render-react`）
- 从 `/.well-known/skills/index.json` 提供的知名端点

如果你希望你的技能无需特定于 GitHub 的安装程序即可被发现，除了在仓库或市场中发布之外，还可以考虑从一个知名端点提供服务。