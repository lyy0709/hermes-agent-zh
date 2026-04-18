---
sidebar_position: 2
title: "技能系统"
description: "按需知识文档——渐进式披露、Agent管理的技能以及技能中心"
---

# 技能系统

技能是Agent在需要时可以加载的按需知识文档。它们遵循**渐进式披露**模式以最小化Token使用量，并与[agentskills.io](https://agentskills.io/specification)开放标准兼容。

所有技能都位于**`~/.hermes/skills/`**——这是主目录和唯一真实来源。在全新安装时，捆绑的技能会从代码库复制到此目录。从中心安装的以及Agent创建的技能也会放在这里。Agent可以修改或删除任何技能。

你也可以将Hermes指向**外部技能目录**——这些是除本地目录外额外扫描的文件夹。请参阅下面的[外部技能目录](#外部技能目录)。

另请参阅：

- [捆绑技能目录](/docs/reference/skills-catalog)
- [官方可选技能目录](/docs/reference/optional-skills-catalog)

## 使用技能

每个已安装的技能都会自动作为一个斜杠命令可用：

```bash
# 在CLI或任何消息平台中：
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# 仅输入技能名称会加载它，并让Agent询问你的需求：
/excalidraw
```

捆绑的`plan`技能是一个很好的例子，它是一个具有自定义行为的、由技能支持的斜杠命令。运行`/plan [request]`会指示Hermes在需要时检查上下文，编写一个Markdown实施计划而不是执行任务，并将结果保存在相对于活动工作空间/后端工作目录的`.hermes/plans/`下。

你也可以通过自然对话与技能交互：

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## 渐进式披露

技能使用一种节省Token的加载模式：

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → 完整内容 + 元数据       (可变)
Level 2: skill_view(name, path)  → 特定引用文件       (可变)
```

Agent只在真正需要时才加载完整的技能内容。

## SKILL.md 格式

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # 可选——限制到特定的操作系统平台
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # 可选——条件激活（见下文）
    requires_toolsets: [terminal]   # 可选——条件激活（见下文）
    config:                          # 可选——config.yaml 设置
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# 技能标题

## 何时使用
此技能的触发条件。

## 步骤
1. 第一步
2. 第二步

## 常见问题
- 已知的失败模式及修复方法

## 验证
如何确认它已成功运行。
```

### 平台特定技能

技能可以使用`platforms`字段限制自己只能在特定的操作系统上运行：

| 值 | 匹配 |
|-------|---------|
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # 仅限 macOS (例如，iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS 和 Linux
```

设置后，该技能在不兼容的平台上会自动从系统提示词、`skills_list()`和斜杠命令中隐藏。如果省略，则该技能在所有平台上加载。

### 条件激活（备用技能）

技能可以根据当前会话中可用的工具自动显示或隐藏自己。这对于**备用技能**最为有用——这些是免费或本地的替代方案，应仅在高级工具不可用时出现。

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # 仅当这些工具集不可用时显示
    requires_toolsets: [terminal]     # 仅当这些工具集可用时显示
    fallback_for_tools: [web_search]  # 仅当这些特定工具不可用时显示
    requires_tools: [terminal]        # 仅当这些特定工具可用时显示
```

| 字段 | 行为 |
|-------|----------|
| `fallback_for_toolsets` | 当列出的工具集可用时，技能被**隐藏**。当它们缺失时显示。 |
| `fallback_for_tools` | 相同，但检查的是单个工具而不是工具集。 |
| `requires_toolsets` | 当列出的工具集不可用时，技能被**隐藏**。当它们存在时显示。 |
| `requires_tools` | 相同，但检查的是单个工具。 |

**示例：** 内置的`duckduckgo-search`技能使用了`fallback_for_toolsets: [web]`。当你设置了`FIRECRAWL_API_KEY`时，web工具集可用，Agent会使用`web_search`——DuckDuckGo技能保持隐藏。如果API密钥缺失，web工具集不可用，DuckDuckGo技能会自动作为备用方案出现。

没有任何条件字段的技能行为与之前完全相同——它们总是显示。

## 加载时的安全设置

技能可以声明所需的环境变量，而不会从发现列表中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

当遇到缺失的值时，Hermes仅在技能实际在本地CLI中加载时才会安全地询问。你可以跳过设置并继续使用该技能。消息界面永远不会在聊天中询问密钥——它们会告诉你在本地使用`hermes setup`或`~/.hermes/.env`。

一旦设置，声明的环境变量会**自动传递**到`execute_code`和`terminal`沙盒——技能的脚本可以直接使用`$TENOR_API_KEY`。对于非技能环境变量，请使用`terminal.env_passthrough`配置选项。详情请参阅[环境变量传递](/docs/user-guide/security#环境变量传递)。
### 技能配置设置

技能还可以声明存储在 `config.yaml` 中的非机密配置设置（路径、偏好设置）：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

设置存储在您 config.yaml 中的 `skills.config` 下。`hermes config migrate` 会提示输入未配置的设置，而 `hermes config show` 会显示它们。当技能加载时，其解析后的配置值会被注入到上下文中，以便 Agent 自动了解配置值。

详情请参阅[技能设置](/docs/user-guide/configuration#skill-settings)和[创建技能 — 配置设置](/docs/developer-guide/creating-skills#config-settings-configyaml)。

## 技能目录结构

```text
~/.hermes/skills/                  # 单一事实来源
├── mlops/                         # 类别目录
│   ├── axolotl/
│   │   ├── SKILL.md               # 主要说明（必需）
│   │   ├── references/            # 附加文档
│   │   ├── templates/             # 输出格式
│   │   ├── scripts/               # 可从技能调用的辅助脚本
│   │   └── assets/                # 补充文件
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent 创建的技能
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub 状态
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # 跟踪预装的捆绑技能
```

## 外部技能目录

如果您在 Hermes 之外维护技能——例如，一个由多个 AI 工具共享的 `~/.agents/skills/` 目录——您可以告诉 Hermes 也扫描这些目录。

在 `~/.hermes/config.yaml` 的 `skills` 部分下添加 `external_dirs`：

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

路径支持 `~` 扩展和 `${VAR}` 环境变量替换。

### 工作原理

- **只读**：外部目录仅用于技能发现扫描。当 Agent 创建或编辑技能时，它总是写入 `~/.hermes/skills/`。
- **本地优先**：如果同一个技能名称同时存在于本地目录和外部目录中，则本地版本优先。
- **完全集成**：外部技能会出现在系统提示词索引、`skills_list`、`skill_view` 中，并作为 `/skill-name` 斜杠命令——与本地技能没有区别。
- **不存在的路径会被静默跳过**：如果配置的目录不存在，Hermes 会忽略它而不报错。这对于可能并非每台机器上都存在的可选共享目录很有用。

### 示例

```text
~/.hermes/skills/               # 本地（主要，读写）
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # 外部（只读，共享）
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

所有四个技能都会出现在您的技能索引中。如果您在本地创建一个名为 `my-custom-workflow` 的新技能，它会覆盖外部版本。

## Agent 管理的技能（skill_manage 工具）

Agent 可以通过 `skill_manage` 工具创建、更新和删除自己的技能。这是 Agent 的**程序性记忆**——当它找到一个非平凡的工作流时，它会将该方法保存为技能以供将来重用。

### Agent 何时创建技能

- 成功完成复杂任务（5 次以上工具调用）后
- 当它遇到错误或死胡同并找到可行路径时
- 当用户纠正其方法时
- 当它发现一个非平凡的工作流时

### 操作

| 操作 | 用途 | 关键参数 |
|--------|---------|------------|
| `create` | 从头开始创建新技能 | `name`, `content`（完整的 SKILL.md），可选的 `category` |
| `patch` | 针对性修复（推荐） | `name`, `old_string`, `new_string` |
| `edit` | 主要结构重写 | `name`, `content`（完整的 SKILL.md 替换） |
| `delete` | 完全删除技能 | `name` |
| `write_file` | 添加/更新支持文件 | `name`, `file_path`, `file_content` |
| `remove_file` | 删除支持文件 | `name`, `file_path` |

:::tip
`patch` 操作是推荐的更新方式——它比 `edit` 更节省 Token，因为只有更改的文本出现在工具调用中。
:::

## Skills Hub

浏览、搜索、安装和管理来自在线注册中心、`skills.sh`、直接已知技能端点以及官方可选技能的技能。

### 常用命令

```bash
hermes skills browse                              # 浏览所有 Hub 技能（官方优先）
hermes skills browse --source official            # 仅浏览官方可选技能
hermes skills search kubernetes                   # 搜索所有来源
hermes skills search react --source skills-sh     # 搜索 skills.sh 目录
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # 安装前预览
hermes skills install openai/skills/k8s           # 安装并进行安全扫描
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills list --source hub                   # 列出 Hub 安装的技能
hermes skills check                               # 检查已安装的 Hub 技能是否有上游更新
hermes skills update                              # 在需要时重新安装有上游更改的 Hub 技能
hermes skills audit                               # 重新扫描所有 Hub 技能的安全性
hermes skills uninstall k8s                       # 移除 Hub 技能
hermes skills reset google-workspace              # 将捆绑技能从“用户修改”状态解除（见下文）
hermes skills reset google-workspace --restore    # 同时恢复捆绑版本，删除您的本地编辑
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # 导出技能配置
hermes skills tap add myorg/skills-repo           # 添加自定义 GitHub 来源
```
### 支持的技能中心来源

| 来源 | 示例 | 备注 |
|--------|---------|-------|
| `official` | `official/security/1password` | Hermes 附带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过 `hermes skills search <query> --source skills-sh` 搜索。当 skills.sh 的别名与仓库文件夹名不同时，Hermes 会解析别名风格的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站的 `/.well-known/skills/index.json` 提供的技能。使用网站或文档 URL 进行搜索。 |
| `github` | `openai/skills/k8s` | 直接安装 GitHub 仓库/路径以及自定义的 tap。 |
| `clawhub`, `lobehub`, `claude-marketplace` | 特定来源的标识符 | 社区或市场集成。 |

### 集成的技能中心和注册表

Hermes 目前集成了以下技能生态系统和发现来源：

#### 1. 官方可选技能 (`official`)

这些技能在 Hermes 仓库本身中维护，安装时具有内置信任。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的源：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)

这是 Vercel 的公共技能目录。Hermes 可以直接搜索它，查看技能详情页面，解析别名风格的 slug，并从底层源仓库安装。

- 目录：[skills.sh](https://skills.sh/)
- CLI/工具仓库：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- 官方 Vercel 技能仓库：[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- 示例：

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. Well-known 技能端点 (`well-known`)

这是基于 URL 的发现机制，来自发布 `/.well-known/skills/index.json` 的网站。它不是一个单一的集中式中心，而是一种网络发现约定。

- 示例实时端点：[Mintlify 文档技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务器实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直接 GitHub 技能 (`github`)

Hermes 可以直接从 GitHub 仓库和基于 GitHub 的 tap 安装。这在您已经知道仓库/路径或想要添加自己的自定义源仓库时非常有用。

默认 tap（无需任何设置即可浏览）：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

#### 5. ClawHub (`clawhub`)

一个作为社区来源集成的第三方技能市场。

- 网站：[clawhub.ai](https://clawhub.ai/)
- Hermes 源 ID：`clawhub`

#### 6. Claude 市场风格仓库 (`claude-marketplace`)

Hermes 支持发布 Claude 兼容插件/市场清单的市场仓库。

已知的集成来源包括：
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes 源 ID：`claude-marketplace`

#### 7. LobeHub (`lobehub`)

Hermes 可以搜索 LobeHub 公共目录中的 Agent 条目，并将其转换为可安装的 Hermes 技能。

- 网站：[LobeHub](https://lobehub.com/)
- 公共 Agent 索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 后端仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes 源 ID：`lobehub`

### 安全扫描与 `--force`

所有从技能中心安装的技能都会经过**安全扫描器**检查，该扫描器会检查数据泄露、提示词注入、破坏性命令、供应链信号和其他威胁。

`hermes skills inspect ...` 现在也会在可用时显示上游元数据：
- 仓库 URL
- skills.sh 详情页面 URL
- 安装命令
- 每周安装量
- 上游安全审计状态
- well-known 索引/端点 URL

当您已审查过第三方技能并希望覆盖非危险策略阻止时，请使用 `--force`：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为：
- `--force` 可以覆盖针对警告/注意类发现的策略阻止。
- `--force` **不会**覆盖 `dangerous` 扫描判定。
- 官方可选技能 (`official/...`) 被视为内置信任，不会显示第三方警告面板。

### 信任级别

| 级别 | 来源 | 策略 |
|-------|--------|--------|
| `builtin` | 随 Hermes 附带 | 始终受信任 |
| `official` | 仓库中的 `optional-skills/` | 内置信任，无第三方警告 |
| `trusted` | 受信任的注册表/仓库，如 `openai/skills`、`anthropics/skills` | 比社区来源更宽松的策略 |
| `community` | 其他所有来源 (`skills.sh`、well-known 端点、自定义 GitHub 仓库、大多数市场) | 非危险发现可通过 `--force` 覆盖；`dangerous` 判定仍会被阻止 |

### 更新生命周期

技能中心现在会跟踪足够的来源信息，以重新检查已安装技能的上游副本：

```bash
hermes skills check          # 报告哪些已安装的技能中心技能在上游发生了更改
hermes skills update         # 仅重新安装有可用更新的技能
hermes skills update react   # 更新一个特定的已安装技能中心技能
```

这使用存储的源标识符加上当前上游捆绑包内容哈希来检测变更。
:::tip GitHub 速率限制
技能中心操作使用 GitHub API，未认证用户的速率限制为 60 次请求/小时。如果在安装或搜索时看到速率限制错误，请在 `.env` 文件中设置 `GITHUB_TOKEN`，将限制提高到 5,000 次请求/小时。发生此情况时，错误消息会包含可操作的提示。
:::

## 捆绑技能的更新 (`hermes skills reset`)

Hermes 在仓库的 `skills/` 目录中附带了一组捆绑技能。在安装时以及每次运行 `hermes update` 时，同步过程会将这些技能复制到 `~/.hermes/skills/` 中，并在 `~/.hermes/skills/.bundled_manifest` 处记录一个清单，将每个技能名称映射到同步时的内容哈希值（即**原始哈希值**）。

每次同步时，Hermes 会重新计算本地副本的哈希值，并与原始哈希值进行比较：

- **未更改** → 可以安全地拉取上游更改，复制新的捆绑版本，并记录新的原始哈希值。
- **已更改** → 被视为**用户已修改**并永久跳过，因此您的编辑永远不会被覆盖。

这种保护机制很好，但有一个尖锐的边缘情况。如果您编辑了一个捆绑技能，后来又想放弃更改，通过从 `~/.hermes/hermes-agent/skills/` 复制粘贴回捆绑版本，清单仍然保存着最后一次成功同步时的*旧*原始哈希值。您新复制粘贴的内容（当前捆绑哈希值）将与该过时的原始哈希值不匹配，因此同步会继续将其标记为用户已修改。

`hermes skills reset` 是逃生舱口：

```bash
# 安全：清除此技能的清单条目。您当前的副本会被保留，
# 但下一次同步会以其为基准重新基线化，以便未来的更新正常工作。
hermes skills reset google-workspace

# 完全恢复：还会删除您的本地副本，并重新复制当前的捆绑版本。
# 当您想要恢复原始的上游技能时使用此选项。
hermes skills reset google-workspace --restore

# 非交互式（例如在脚本或 TUI 模式下）——跳过 --restore 确认。
hermes skills reset google-workspace --restore --yes
```

相同的命令在聊天中可以作为斜杠命令使用：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note 配置文件
每个配置文件在其自己的 `HERMES_HOME` 下都有自己的 `.bundled_manifest`，因此 `hermes -p coder skills reset <name>` 仅影响该配置文件。
:::

### 斜杠命令（在聊天内部）

所有相同的命令都可以通过 `/skills` 使用：

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

官方的可选技能仍然使用像 `official/security/1password` 和 `official/migration/openclaw-migration` 这样的标识符。