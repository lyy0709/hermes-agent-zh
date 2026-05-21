---
sidebar_position: 2
title: "技能系统"
description: "按需知识文档——渐进式披露、Agent 管理的技能，以及技能中心"
---

# 技能系统

技能是 Agent 在需要时可以加载的按需知识文档。它们遵循**渐进式披露**模式以最小化 Token 使用量，并且兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有技能都位于 **`~/.hermes/skills/`** —— 这是主目录和唯一可信源。在全新安装时，捆绑的技能会从代码仓库复制到此目录。从中心安装的以及由 Agent 创建的技能也会放在这里。Agent 可以修改或删除任何技能。

你也可以将 Hermes 指向**外部技能目录**——这些是除本地目录外额外扫描的文件夹。请参阅下面的[外部技能目录](#外部技能目录)。

另请参阅：

- [捆绑技能目录](/docs/reference/skills-catalog)
- [官方可选技能目录](/docs/reference/optional-skills-catalog)

## 使用技能

每个已安装的技能都会自动作为一个斜杠命令可用：

```bash
# 在 CLI 或任何消息平台中：
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# 仅输入技能名称会加载它，并让 Agent 询问你的需求：
/excalidraw
```

捆绑的 `plan` 技能是一个很好的例子。运行 `/plan [请求]` 会加载该技能的指令，告诉 Hermes 在需要时检查上下文，编写一个 Markdown 实施计划而不是执行任务，并将结果保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 下。

你也可以通过自然对话与技能交互：

```bash
hermes chat --toolsets skills -q "你有什么技能？"
hermes chat --toolsets skills -q "给我看看 axolotl 技能"
```

## 渐进式披露

技能使用一种节省 Token 的加载模式：

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → 完整内容 + 元数据       (可变)
Level 2: skill_view(name, path)  → 特定引用文件       (可变)
```

Agent 只在真正需要时才加载完整的技能内容。

## SKILL.md 格式

```markdown
---
name: my-skill
description: 此技能功能的简要描述
version: 1.0.0
platforms: [macos, linux]     # 可选——限制在特定的操作系统平台
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # 可选——条件激活（见下文）
    requires_toolsets: [terminal]   # 可选——条件激活（见下文）
    config:                          # 可选——config.yaml 设置
      - key: my.setting
        description: "此设置控制什么"
        default: "value"
        prompt: "设置提示"
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
如何确认它已成功。
```

### 平台特定技能

技能可以使用 `platforms` 字段限制自己只能在特定的操作系统上运行：

| 值 | 匹配 |
|-------|---------|
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # 仅 macOS (例如，iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS 和 Linux
```

设置后，该技能在不兼容的平台上会自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。如果省略，该技能将在所有平台上加载。

## 技能输出和媒体交付

当技能响应（或任何 Agent 响应）包含一个纯绝对路径指向媒体文件时——例如 `/home/user/screenshots/diagram.png` —— 消息网关会自动检测到它，将其从可见文本中剥离，并以原生方式将文件交付到用户的聊天中（Telegram 照片、Discord 附件等），而不是在消息中留下原始路径。

特别是对于音频，`[[audio_as_voice]]` 指令会将音频文件提升为支持该功能的平台（Telegram、WhatsApp）上的原生语音消息气泡。

### 强制文档式交付：`[[as_document]]`

有时你想要的恰恰是**相反**的内联预览：你希望文件作为可下载的附件交付，而不是重新压缩的图像气泡。典型的例子是高分辨率截图或图表——Telegram 的 `sendPhoto` 会将其重新压缩到约 200 KB 和 1280 像素，破坏了可读性。通过 `sendDocument` 发送的 1-2 MB PNG 文件可以保持原始字节不变。

如果一个响应（或其内部的任何文本——通常是最后一行）包含字面指令 `[[as_document]]`，那么从该响应中提取的每个媒体路径都将作为文档/文件附件交付，而不是图像气泡：

```
这是你渲染的图表：

/home/user/.hermes/cache/chart-q4-2025.png

[[as_document]]
```

该指令在交付前会被剥离，因此用户永远不会看到它。粒度设计上故意是每个响应全有或全无：发出一次 `[[as_document]]`，同一响应中的每个图像路径都将作为文档交付。这反映了 `[[audio_as_voice]]` 的作用范围。

在以下情况下从技能中使用它：

- 你生成的截图或图表需要用户作为文件使用（用于在其他工具中编辑、存档、完整分享）。
- 默认的有损预览会模糊细节（小文本、像素级精确的图表、对颜色敏感的渲染）。

没有单独文档路径的平台（例如 SMS）会回退到它们拥有的任何附件机制。

### 条件激活（备用技能）

技能可以根据当前会话中可用的工具自动显示或隐藏自己。这对于**备用技能**最为有用——这些是免费或本地的替代方案，应仅在高级工具不可用时才出现。

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
| `fallback_for_toolsets` | 当列出的工具集可用时，技能**隐藏**。当它们缺失时显示。 |
| `fallback_for_tools` | 同上，但检查的是单个工具而非工具集。 |
| `requires_toolsets` | 当列出的工具集不可用时，技能**隐藏**。当它们存在时显示。 |
| `requires_tools` | 同上，但检查的是单个工具。 |

**示例：** 内置的 `duckduckgo-search` 技能使用了 `fallback_for_toolsets: [web]`。当你设置了 `FIRECRAWL_API_KEY` 时，web 工具集可用，Agent 会使用 `web_search` —— DuckDuckGo 技能保持隐藏。如果 API 密钥缺失，web 工具集不可用，DuckDuckGo 技能会自动作为备选方案出现。

没有任何条件字段的技能行为与之前完全一致 —— 它们总是显示。

## 加载时的安全设置

技能可以声明所需的环境变量，而不会从发现列表中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

当遇到缺失的值时，Hermes 只会在技能实际加载到本地 CLI 时安全地询问。你可以跳过设置并继续使用该技能。消息界面永远不会在聊天中询问密钥 —— 它们会告诉你在本地使用 `hermes setup` 或 `~/.hermes/.env`。

一旦设置，声明的环境变量会**自动传递**到 `execute_code` 和 `terminal` 沙盒 —— 技能的脚本可以直接使用 `$TENOR_API_KEY`。对于非技能环境变量，请使用 `terminal.env_passthrough` 配置选项。详情请参阅[环境变量传递](/docs/user-guide/security#environment-variable-passthrough)。

### 技能配置设置

技能还可以声明存储在 `config.yaml` 中的非密钥配置设置（路径、偏好设置）：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

设置存储在 config.yaml 中的 `skills.config` 下。`hermes config migrate` 会提示未配置的设置，`hermes config show` 会显示它们。当技能加载时，其解析后的配置值会被注入到上下文中，以便 Agent 自动了解配置值。

详情请参阅[技能设置](/docs/user-guide/configuration#skill-settings)和[创建技能 — 配置设置](/docs/developer-guide/creating-skills#config-settings-configyaml)。

## 技能目录结构

```text
~/.hermes/skills/                  # 单一事实来源
├── mlops/                         # 分类目录
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
└── .bundled_manifest              # 跟踪已植入的捆绑技能
```

## 外部技能目录

如果你在 Hermes 之外维护技能 —— 例如，一个由多个 AI 工具共享的 `~/.agents/skills/` 目录 —— 你可以告诉 Hermes 也扫描这些目录。

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

- **本地创建，原地更新**：新的 Agent 创建的技能会被写入 `~/.hermes/skills/`。当 Agent 使用 `skill_manage` 操作（如 `patch`、`edit`、`write_file`、`remove_file` 或 `delete`）时，现有的技能会在其被找到的位置（包括 `external_dirs` 下的技能）进行修改。
- **外部目录不是写保护边界**：如果 Hermes 进程对某个外部技能目录具有写权限，那么由 Agent 管理的技能更新可以更改该目录中的文件。如果共享的外部技能必须保持只读，请使用文件系统权限或单独的配置文件/工具集设置。
- **本地优先**：如果同一个技能名称同时存在于本地目录和外部目录中，则本地版本优先。
- **完全集成**：外部技能会出现在系统提示词索引、`skills_list`、`skill_view` 以及 `/skill-name` 斜杠命令中 —— 与本地技能没有区别。
- **不存在的路径会被静默跳过**：如果配置的目录不存在，Hermes 会忽略它而不报错。这对于可能并非每台机器上都存在的可选共享目录很有用。

### 示例

```text
~/.hermes/skills/               # 本地（主要，读写）
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # 外部（共享，如果可写则可变）
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

所有四个技能都会出现在你的技能索引中。如果你在本地创建一个名为 `my-custom-workflow` 的新技能，它会覆盖外部版本。

## 技能包

技能包是微小的 YAML 文件，将多个技能分组到一个斜杠命令下。当你运行 `/<bundle-name>` 时，包中列出的每个技能都会同时加载 —— 当某个特定任务总是受益于同一组技能一起使用时，这非常有用。

### 快速示例

```bash
# 为后端功能工作创建一个包
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work — review, test, PR workflow"
```
然后在 CLI 或任何消息网关平台中：

```
/backend-dev 重构认证中间件
```

Agent 会收到加载了全部三个技能的一条用户消息，斜杠命令后的任何文本都会作为用户指令附加。

### YAML 模式

技能集存放在 **`~/.hermes/skill-bundles/<slug>.yaml`** 中，格式如下：

```yaml
name: backend-dev
description: 后端功能开发 — 代码审查、测试、PR 工作流。
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  始终从编写失败的测试开始，然后实现功能。
  通过标准工作流打开 PR，并包含共同作者标签。
```

字段说明：
- `name`（可选 — 默认为文件名主干） — 技能集的显示名称。会规范化为连字符 slug 用于斜杠命令（`Backend Dev` → `/backend-dev`）。
- `description`（可选） — 在 `/bundles` 和 `hermes bundles list` 中显示的简短文本。
- `skills`（必需，非空列表） — 技能名称或相对于技能目录的路径。使用与 `/<skill-name>` 相同的标识符。
- `instruction`（可选） — 附加到已加载技能内容前的额外指导。适用于固化"我们如何始终一起使用这些技能"。

### 管理技能集

```bash
# 列出所有已安装的技能集
hermes bundles list

# 查看一个技能集
hermes bundles show backend-dev

# 交互式创建技能集（省略 --skill 标志以逐行输入技能）
hermes bundles create research

# 覆盖现有技能集
hermes bundles create backend-dev --skill ... --force

# 删除技能集
hermes bundles delete backend-dev

# 重新扫描 ~/.hermes/skill-bundles/ 并报告更改
hermes bundles reload
```

在聊天会话内部，`/bundles` 会列出每个已安装的技能集及其包含的技能。

### 行为

- **当 slug 冲突时，技能集优先于单个技能**。如果你将一个技能集命名为 `research`，同时也有一个名为 `research` 的技能，那么 `/research` 会调用技能集。这是有意为之 — 你通过命名选择了使用技能集。
- **缺失的技能会被跳过，不会导致失败**。如果一个技能集列出了 `skill-foo` 但你尚未安装它，技能集仍然会加载那些能解析的技能，并且 Agent 会收到一条列出被跳过技能的通知。
- **技能集在所有界面都有效** — 交互式 CLI、TUI、仪表板聊天以及每个消息网关平台（Telegram、Discord、Slack……） — 因为调度与单个技能命令一样集中在同一位置。
- **技能集不会使提示词缓存失效**。它们在调用时生成一条新的用户消息，与 `/<skill-name>` 的方式相同 — 不会修改系统提示词。

### 何时使用技能集优于手动安装每个技能

在以下情况使用技能集：
- 你总是为重复性任务（`/backend-dev`、`/release-prep`、`/incident-response`）配对使用相同的技能。
- 你希望获得比连续输入多个 `/skill` 调用更简短的心智模型。
- 你希望通过将技能集 YAML 文件签入共享的 dotfiles 仓库并符号链接到 `~/.hermes/skill-bundles/` 来分发团队范围的"任务配置文件"。

技能集只是一个 YAML 别名 — 它不会为你安装技能。技能本身必须已经存在（在 `~/.hermes/skills/` 或外部技能目录中）。否则，技能集调用只会跳过缺失的技能。

## Agent 管理的技能（skill_manage 工具）

Agent 可以通过 `skill_manage` 工具创建、更新和删除自己的技能。这是 Agent 的**程序性记忆** — 当它发现一个非平凡的工作流时，它会将该方法保存为技能以供将来重用。

### Agent 何时创建技能

- 成功完成复杂任务（5 次以上工具调用）后
- 当它遇到错误或死胡同并找到了可行的路径时
- 当用户纠正了它的方法时
- 当它发现了一个非平凡的工作流时

### 操作

| 操作 | 用途 | 关键参数 |
|--------|---------|------------|
| `create` | 从头创建新技能 | `name`, `content`（完整的 SKILL.md），可选的 `category` |
| `patch` | 针对性修复（推荐） | `name`, `old_string`, `new_string` |
| `edit` | 主要结构重写 | `name`, `content`（完整的 SKILL.md 替换） |
| `delete` | 完全删除技能 | `name` |
| `write_file` | 添加/更新支持文件 | `name`, `file_path`, `file_content` |
| `remove_file` | 删除支持文件 | `name`, `file_path` |

:::tip
`patch` 操作是推荐的更新方式 — 它比 `edit` 更节省 Token，因为只有更改的文本会出现在工具调用中。
:::

## 技能中心

从在线注册表、`skills.sh`、直接已知技能端点以及官方可选技能中浏览、搜索、安装和管理技能。

### 常用命令

```bash
hermes skills browse                              # 浏览所有中心技能（官方优先）
hermes skills browse --source official            # 仅浏览官方可选技能
hermes skills search kubernetes                   # 在所有源中搜索
hermes skills search react --source skills-sh     # 在 skills.sh 目录中搜索
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # 安装前预览
hermes skills install openai/skills/k8s           # 安装并进行安全扫描
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install https://sharethis.chat/SKILL.md              # 直接 URL（单文件 SKILL.md）
hermes skills install https://example.com/SKILL.md --name my-skill # 当 frontmatter 中没有名称时覆盖名称
hermes skills list --source hub                   # 列出从中心安装的技能
hermes skills check                               # 检查已安装的中心技能是否有上游更新
hermes skills update                              # 在需要时重新安装有上游更改的中心技能
hermes skills audit                               # 重新扫描所有中心技能的安全性
hermes skills uninstall k8s                       # 移除一个中心技能
hermes skills reset google-workspace              # 将捆绑技能从"用户已修改"状态解除（见下文）
hermes skills reset google-workspace --restore    # 同时恢复捆绑版本，删除你的本地编辑
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # 导出技能配置
hermes skills tap add myorg/skills-repo           # 添加自定义 GitHub 源
```
### 支持的技能中心来源

| 来源 | 示例 | 备注 |
|--------|---------|-------|
| `official` | `official/security/1password` | Hermes 附带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过 `hermes skills search <query> --source skills-sh` 搜索。当 skills.sh 的 slug 与仓库文件夹名不同时，Hermes 会解析别名风格的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站上的 `/.well-known/skills/index.json` 提供的技能。使用站点或文档 URL 进行搜索。 |
| `url` | `https://sharethis.chat/SKILL.md` | 指向单个文件 `SKILL.md` 的直接 HTTP(S) URL。名称解析顺序：frontmatter → URL slug → 交互式提示 → `--name` 标志。 |
| `github` | `openai/skills/k8s` | 直接安装 GitHub 仓库/路径以及自定义 taps。 |
| `clawhub`, `lobehub`, `browse-sh`, `claude-marketplace` | 特定来源的标识符 | 社区或市场集成。 |

### 集成的技能中心和注册表

Hermes 目前集成了以下技能生态系统和发现来源：

#### 1. 官方可选技能 (`official`)

这些技能由 Hermes 仓库自身维护，安装时具有内置信任。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的源：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)

这是 Vercel 的公共技能目录。Hermes 可以直接搜索它，查看技能详情页，解析别名风格的 slug，并从底层源仓库安装。

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

这是一种基于 URL 的发现方式，来自发布 `/.well-known/skills/index.json` 的网站。它不是一个单一的集中式中心，而是一种网络发现约定。

- 实时端点示例：[Mintlify 文档技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务器实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直接 GitHub 技能 (`github`)

Hermes 可以直接从 GitHub 仓库和基于 GitHub 的 taps 安装。这在您已经知道仓库/路径或想要添加自己的自定义源仓库时非常有用。

默认 taps（无需任何设置即可浏览）：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [huggingface/skills](https://github.com/huggingface/skills)
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
- Hermes 来源 ID：`clawhub`

#### 6. Claude 市场风格仓库 (`claude-marketplace`)

Hermes 支持发布 Claude 兼容插件/市场清单的市场仓库。

已知的集成来源包括：
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes 来源 ID：`claude-marketplace`

#### 7. LobeHub (`lobehub`)

Hermes 可以搜索 LobeHub 公共目录中的 Agent 条目，并将其转换为可安装的 Hermes 技能。

- 网站：[LobeHub](https://lobehub.com/)
- 公共 Agent 索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 支持仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes 来源 ID：`lobehub`

#### 8. browse.sh (`browse-sh`)

Hermes 集成了 [browse.sh](https://browse.sh)，这是 Browserbase 的包含 200 多个特定网站浏览器自动化 SKILL.md 文件的目录（Airbnb、Amazon、arXiv、12306.cn、Etsy、Xero 等）。每个技能都描述了如何端到端地驱动一个网站，适合与 Hermes 的浏览器工具以及您已安装的任何浏览器自动化技能一起使用。

- 网站：[browse.sh](https://browse.sh/)
- 目录 API：`https://browse.sh/api/skills`
- Hermes 来源 ID：`browse-sh`
- 信任级别：`community`

```bash
hermes skills search airbnb --source browse-sh
hermes skills inspect browse-sh/airbnb.com/search-listings-ddgioa
hermes skills install browse-sh/airbnb.com/search-listings-ddgioa
```

标识符采用 `browse-sh/<hostname>/<task-id>` 的形式，并与 browse.sh 目录公开的 slug 匹配。内容通过每个技能的详情端点（`/api/skills/<slug>` → `skillMdUrl`）解析，而不是通过目录的 GitHub `sourceUrl`。

#### 9. 直接 URL (`url`)

直接从任何 HTTP(S) URL 安装单个文件 `SKILL.md` —— 当作者在自己的网站上托管技能时非常有用（没有中心列表，无需输入 GitHub 路径）。Hermes 会获取 URL，解析 YAML frontmatter，进行安全扫描，然后安装。

- Hermes 来源 ID：`url`
- 标识符：URL 本身（无需前缀）
- 范围：**仅限单个文件 `SKILL.md`**。包含 `references/` 或 `scripts/` 的多文件技能需要一个清单，应通过上述其他来源之一发布。

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```
名称解析顺序：
1. `SKILL.md` YAML frontmatter 中的 `name:` 字段（推荐方式——每个格式良好的技能都应包含此字段）。
2. URL 路径中的父目录名称（例如 `.../my-skill/SKILL.md` → `my-skill`，或 `.../my-skill.md` → `my-skill`），前提是它是一个有效的标识符（`^[a-z][a-z0-9_-]*$`）。
3. 在具有 TTY 的终端上进行交互式提示。
4. 在非交互式界面中（TUI 内的 `/skills install` 斜杠命令、消息网关平台、脚本），会返回一个指向 `--name` 覆盖选项的清晰错误。

```bash
# Frontmatter 中没有名称且 URL 段无帮助时——请提供一个名称：
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# 或者在聊天会话中：
/skills install https://example.com/SKILL.md --name sharethis-chat
```

信任级别始终为 `community`——与所有其他来源一样，会运行相同的安全扫描。URL 会存储为安装标识符，因此当你想要刷新时，`hermes skills update` 会自动从同一 URL 重新获取。

### 安全扫描与 `--force`

所有通过 hub 安装的技能都会经过一个**安全扫描器**，该扫描器会检查数据泄露、提示词注入、破坏性命令、供应链信号和其他威胁。

`hermes skills inspect ...` 现在也会在可用时显示上游元数据：
- 仓库 URL
- skills.sh 详情页 URL
- 安装命令
- 每周安装量
- 上游安全审计状态
- 已知的索引/端点 URL

当你已审查过第三方技能并希望覆盖非危险性的策略阻止时，请使用 `--force`：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为：
- `--force` 可以覆盖针对 caution/warn 类发现的策略阻止。
- `--force` **不会**覆盖 `dangerous` 扫描判定。
- 官方可选技能（`official/...`）被视为内置信任级别，不会显示第三方警告面板。

### 信任级别

| 级别 | 来源 | 策略 |
|-------|--------|--------|
| `builtin` | 随 Hermes 发布 | 始终受信任 |
| `official` | 仓库中的 `optional-skills/` | 内置信任，无第三方警告 |
| `trusted` | 受信任的注册表/仓库，例如 `openai/skills`、`anthropics/skills`、`huggingface/skills` | 比社区来源更宽松的策略 |
| `community` | 其他所有来源（`skills.sh`、已知端点、自定义 GitHub 仓库、大多数市场） | 非危险发现可通过 `--force` 覆盖；`dangerous` 判定仍会被阻止 |

### 更新生命周期

Hub 现在会跟踪足够的来源信息，以重新检查已安装技能的上游副本：

```bash
hermes skills check          # 报告哪些已安装的 hub 技能在上游发生了变化
hermes skills update         # 仅重新安装有可用更新的技能
hermes skills update react   # 更新一个特定的已安装 hub 技能
```

这使用存储的源标识符加上当前上游捆绑包内容哈希来检测变更。

:::tip GitHub 速率限制
Skills hub 操作使用 GitHub API，对于未经身份验证的用户，其速率限制为每小时 60 个请求。如果在安装或搜索时看到速率限制错误，请在 `.env` 文件中设置 `GITHUB_TOKEN`，以将限制提高到每小时 5,000 个请求。发生这种情况时，错误消息会包含一个可操作的提示。
:::

### 发布自定义技能 tap

如果你想分享一组精心策划的技能——为你的团队、组织或公开分享——你可以将它们发布为一个 **tap**：一个其他 Hermes 用户可以通过 `hermes skills tap add <owner/repo>` 添加的 GitHub 仓库。无需服务器，无需注册注册表，无需发布流水线。只需一个包含 `SKILL.md` 文件的目录。

#### 仓库布局

一个 tap 是任何布局如下的 GitHub 仓库（公开或私有——私有仓库需要 `GITHUB_TOKEN`）：

```
owner/repo
├── skills/                       # 默认路径；可按 tap 配置
│   ├── my-workflow/
│   │   ├── SKILL.md              # 必需
│   │   ├── references/           # 可选的辅助文件
│   │   ├── templates/
│   │   └── scripts/
│   ├── another-skill/
│   │   └── SKILL.md
│   └── third-skill/
│       └── SKILL.md
└── README.md                     # 可选但很有帮助
```

规则：
- 每个技能都位于 tap 根路径（默认为 `skills/`）下的独立目录中。
- 目录名称成为技能的安装段。
- 每个技能目录必须包含一个具有标准 [SKILL.md frontmatter](#skillmd-格式)（`name`、`description`，以及可选的 `metadata.hermes.tags`、`version`、`author`、`platforms`、`metadata.hermes.config`）的 `SKILL.md` 文件。
- 像 `references/`、`templates/`、`scripts/`、`assets/` 这样的子目录会在安装时随 `SKILL.md` 一起下载。
- 目录名称以 `.` 或 `_` 开头的技能会被忽略。

Hermes 通过列出 tap 路径下的每个子目录并探测每个目录中的 `SKILL.md` 来发现技能。

#### 最小 tap 示例

```
my-org/hermes-skills
└── skills/
    └── deploy-runbook/
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`：

```markdown
---
name: deploy-runbook
description: Our deployment runbook — services, rollback, Slack channels
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

# Deploy Runbook

Step 1: ...
```

将其推送到 GitHub 后，任何 Hermes 用户都可以订阅并安装：

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### 非默认路径

如果你的技能不在 `skills/` 目录下（常见于将 `skills/` 子树添加到现有项目时），请编辑 `~/.hermes/.hub/taps.json` 中的 tap 条目：

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

`hermes skills tap add` CLI 默认将新 tap 的 `path` 设置为 `"skills/"`；如果需要不同的路径，请直接编辑该文件。`hermes skills tap list` 会显示每个 tap 的有效路径。

#### 直接安装单个技能（无需添加 tap）

用户也可以从任何公共 GitHub 仓库安装单个技能，而无需将整个仓库添加为 tap：
```bash
hermes skills install owner/repo/skills/my-workflow
```

当您希望共享单个技能，而不要求用户订阅您的整个注册表时，这很有用。

#### Tap 的信任级别

新的 tap 默认被分配为 `community` 信任级别。从这些 tap 安装的技能会经过标准安全扫描，并在首次安装时显示第三方警告面板。如果您的组织或一个广受信任的来源应该获得更高的信任级别，请将其仓库添加到 `tools/skills_hub.py` 中的 `TRUSTED_REPOS` 中（需要提交 Hermes 核心 PR）。

#### Tap 管理

```bash
hermes skills tap list                                # 显示所有已配置的 tap
hermes skills tap add myorg/skills-repo               # 添加（默认路径：skills/）
hermes skills tap remove myorg/skills-repo            # 移除
```

在运行中的会话内：

```
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

Tap 存储在 `~/.hermes/.hub/taps.json` 中（按需创建）。

## 捆绑技能更新 (`hermes skills reset`)

Hermes 在仓库内的 `skills/` 目录中附带了一组捆绑技能。在安装时以及每次运行 `hermes update` 时，同步过程会将这些技能复制到 `~/.hermes/skills/` 中，并在 `~/.hermes/skills/.bundled_manifest` 处记录一个清单，将每个技能名称映射到同步时的内容哈希值（即**原始哈希**）。

每次同步时，Hermes 会重新计算您本地副本的哈希值，并将其与原始哈希值进行比较：

- **未更改** → 可以安全拉取上游更改，复制新的捆绑版本，并记录新的原始哈希值。
- **已更改** → 被视为**用户已修改**并永久跳过，因此您的编辑永远不会被覆盖。

这种保护机制很好，但有一个尖锐的边缘情况。如果您编辑了一个捆绑技能，后来又想放弃您的更改，通过从 `~/.hermes/hermes-agent/skills/` 复制粘贴来恢复到捆绑版本，清单仍然保存着最后一次成功同步时的*旧*原始哈希值。您新复制粘贴的内容（当前的捆绑哈希值）将与该过时的原始哈希值不匹配，因此同步会继续将其标记为用户已修改。

`hermes skills reset` 是逃生舱口：

```bash
# 安全：清除此技能的清单条目。您当前的副本会被保留，
# 但下一次同步会以其为基准重新基线化，以便未来的更新正常工作。
hermes skills reset google-workspace

# 完全恢复：还会删除您的本地副本，并重新复制当前的捆绑版本。
# 当您想要恢复原始的、未经修改的上游技能时，请使用此选项。
hermes skills reset google-workspace --restore

# 非交互式（例如在脚本或 TUI 模式下）—— 跳过 --restore 确认。
hermes skills reset google-workspace --restore --yes
```

相同的命令在聊天中可以作为斜杠命令使用：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note 配置文件
每个配置文件在其自己的 `HERMES_HOME` 下都有自己的 `.bundled_manifest`，因此 `hermes -p coder skills reset <name>` 只影响该配置文件。
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