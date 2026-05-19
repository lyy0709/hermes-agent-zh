# 为 Hermes Agent 贡献代码

感谢您为 Hermes Agent 贡献代码！本指南涵盖了您需要了解的一切：设置开发环境、理解架构、决定构建什么以及如何让您的 PR 被合并。

---

## 贡献优先级

我们按以下顺序评估贡献的价值：

1.  **Bug 修复** — 崩溃、错误行为、数据丢失。始终是最高优先级。
2.  **跨平台兼容性** — macOS、不同的 Linux 发行版以及 Windows 上的 WSL2。我们希望 Hermes 能在任何地方运行。
3.  **安全加固** — Shell 注入、提示词注入、路径遍历、权限提升。请参阅[安全注意事项](#security-considerations)。
4.  **性能和健壮性** — 重试逻辑、错误处理、优雅降级。
5.  **新技能** — 但仅限于广泛有用的技能。请参阅[应该是技能还是工具？](#should-it-be-a-skill-or-a-tool)
6.  **新工具** — 很少需要。大多数功能都应该是技能。请参阅下文。
7.  **文档** — 修复、澄清、新示例。

---

## 应该是技能还是工具？

这是新贡献者最常见的问题。答案几乎总是**技能**。

### 在以下情况下，将其创建为技能：

- 该功能可以表示为指令 + shell 命令 + 现有工具
- 它包装了一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用
- 它不需要与 Agent 框架深度集成的自定义 Python 集成或 API 密钥管理
- 示例：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送电子邮件

### 在以下情况下，将其创建为工具：

- 它需要与由 Agent 框架管理的 API 密钥、身份验证流程或多组件配置进行端到端集成
- 它需要每次都必须精确执行的自定义处理逻辑（而不是 LLM 解释的“尽力而为”）
- 它处理无法通过终端传输的二进制数据、流式数据或实时事件
- 示例：浏览器自动化（Browserbase 会话管理）、TTS（音频编码 + 平台交付）、视觉分析（base64 图像处理）

### 该技能是否应该捆绑发布？

捆绑技能（位于 `skills/` 目录中）随每个 Hermes 安装包一起发布。它们应该**对大多数用户广泛有用**：

- 文档处理、网络研究、常见的开发工作流、系统管理
- 被广泛人群定期使用

如果您的技能是官方的且有用，但并非普遍需要（例如，付费服务集成、重量级依赖项），请将其放入 **`optional-skills/`** 目录 — 它随代码仓库一起发布，但默认不激活。用户可以通过 `hermes skills browse` 发现它（标记为“官方”），并使用 `hermes skills install` 安装它（无第三方警告，内置信任）。

如果您的技能是专业的、社区贡献的或小众的，它更适合放在 **技能中心** — 将其上传到技能注册表，并在 [Nous Research Discord](https://discord.gg/NousResearch) 中分享。用户可以使用 `hermes skills install` 安装它。

---

## 记忆提供商：作为独立插件发布

**我们不再接受将新的记忆提供商合并到此代码仓库中。** `plugins/memory/` 下的内置提供商集合（honcho、mem0、supermemory、byterover、hindsight、holographic、openviking、retaindb）已经关闭。如果您想添加新的记忆后端，请将其发布为**独立的插件仓库**，供用户安装到 `~/.hermes/plugins/` 目录（或通过 pip entry point）。

独立的记忆插件：

- 实现相同的 `MemoryProvider` 抽象基类（`agent/memory_provider.py`）— `sync_turn`、`prefetch`、`shutdown`，以及可选的 `post_setup(hermes_home, config)` 用于设置向导集成
- 使用相同的发现系统 — `discover_memory_providers()` 从用户/项目插件目录和 pip entry point 中拾取它们
- 通过 `post_setup()` 与 `hermes memory setup` 集成 — 无需接触核心代码
- 可以通过 `cli.py` 文件中的 `register_cli(subparser)` 注册自己的 CLI 子命令
- 获得与仓库内提供商相同的所有生命周期钩子和配置管道

在 `plugins/memory/` 下添加新目录的 PR 将被关闭，并会提示将提供商作为自己的仓库发布。现有的仓库内提供商保留；欢迎对它们进行 Bug 修复。

这不是质量门槛 — 这是一个关于耦合和维护的决策。记忆提供商是最常见的插件类型，它们不应该都放在这个代码树中。

---

## 开发环境设置

### 先决条件

| 要求 | 备注 |
|-------------|-------|
| **Git** | 支持 `--recurse-submodules`，并安装 `git-lfs` 扩展 |
| **Python 3.11+** | 如果缺失，uv 会安装它 |
| **uv** | 快速的 Python 包管理器（[安装](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 可选 — 浏览器工具和 WhatsApp 桥接所需（与根目录 `package.json` engines 匹配） |

### 克隆和安装

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建虚拟环境
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有额外功能（消息传递、定时任务、CLI 菜单、开发工具）
uv pip install -e ".[all,dev]"

# 可选：浏览器工具
npm install
```

### 为开发配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# 至少添加一个 LLM 提供商密钥：
echo "OPENROUTER_API_KEY=***" >> ~/.hermes/.env
```

### 运行

```bash
# 创建符号链接以便全局访问
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# 验证
hermes doctor
hermes chat -q "Hello"
```

### 运行测试

```bash
# 推荐 — 与 CI 匹配（隔离环境，4 个 xdist 工作进程）；参见 AGENTS.md
scripts/run_tests.sh

# 替代方案（首先激活虚拟环境）。在您打开 PR 之前，仍建议使用包装器脚本以确保与 GitHub Actions 一致：
pytest tests/ -v
```

---

## 项目结构

```
hermes-agent/
├── run_agent.py              # AIAgent 类 — 核心对话循环、工具分发、会话持久化
├── cli.py                    # HermesCLI 类 — 交互式 TUI、prompt_toolkit 集成
├── model_tools.py            # 工具编排（tools/registry.py 的薄层封装）
├── toolsets.py               # 工具分组和预设（hermes-cli、hermes-telegram 等）
├── hermes_state.py           # 带有 FTS5 全文搜索和会话标题的 SQLite 会话数据库
├── batch_runner.py           # 用于轨迹生成的并行批处理
│
├── agent/                    # Agent 内部模块（提取出的模块）
│   ├── prompt_builder.py         # 系统提示词组装（身份、技能、上下文文件、记忆）
│   ├── context_compressor.py     # 接近上下文限制时的自动摘要
│   ├── auxiliary_client.py       # 解析辅助 OpenAI 客户端（摘要、视觉）
│   ├── display.py                # KawaiiSpinner、工具进度格式化
│   ├── model_metadata.py         # 模型上下文长度、Token 估算
│   └── trajectory.py             # 轨迹保存辅助函数
│
├── hermes_cli/               # CLI 命令实现
│   ├── main.py                   # 入口点、参数解析、命令分发
│   ├── config.py                 # 配置管理、迁移、环境变量定义
│   ├── setup.py                  # 交互式设置向导
│   ├── auth.py                   # 提供商解析、OAuth、Nous Portal
│   ├── models.py                 # OpenRouter 模型选择列表
│   ├── banner.py                 # 欢迎横幅、ASCII 艺术
│   ├── commands.py               # 中央斜杠命令注册表（CommandDef）、自动补全、消息网关辅助函数
│   ├── callbacks.py              # 交互式回调（澄清、sudo、批准）
│   ├── doctor.py                 # 诊断
│   ├── skills_hub.py             # 技能中心 CLI + /skills 斜杠命令
│   └── skin_engine.py            # 皮肤/主题引擎 — 数据驱动的 CLI 视觉定制
│
├── tools/                    # 工具实现（自注册）
│   ├── registry.py               # 中央工具注册表（模式、处理器、分发）
│   ├── approval.py               # 危险命令检测 + 每会话批准
│   ├── terminal_tool.py          # 终端编排（sudo、环境生命周期、后端）
│   ├── file_operations.py        # read_file、write_file、search、patch 等
│   ├── web_tools.py              # web_search、web_extract（Parallel/Firecrawl + Gemini 摘要）
│   ├── vision_tools.py           # 通过多模态模型进行图像分析
│   ├── delegate_tool.py          # 子 Agent 生成和并行任务执行
│   ├── code_execution_tool.py    # 带有 RPC 工具访问权限的沙盒化 Python
│   ├── session_search_tool.py    # 使用 FTS5 + 锚定窗口搜索过去的对话
│   ├── cronjob_tools.py          # 定时任务管理
│   ├── skill_tools.py            # 技能搜索、加载、管理
│   └── environments/             # 终端执行后端
│       ├── base.py                   # BaseEnvironment 抽象基类
│       ├── local.py, docker.py, ssh.py, singularity.py, modal.py, daytona.py
│
├── gateway/                  # 消息网关
│   ├── run.py                    # GatewayRunner — 平台生命周期、消息路由、定时任务
│   ├── config.py                 # 平台配置解析
│   ├── session.py                # 会话存储、上下文提示词、重置策略
│   └── platforms/                # 平台适配器
│       ├── telegram.py, discord_adapter.py, slack.py, whatsapp.py
│
├── scripts/                  # 安装程序和桥接脚本
│   ├── install.sh                # Linux/macOS 安装程序
│   ├── install.ps1               # Windows PowerShell 安装程序
│   └── whatsapp-bridge/          # Node.js WhatsApp 桥接（Baileys）
│
├── skills/                   # 捆绑技能（安装时复制到 ~/.hermes/skills/）
├── optional-skills/          # 官方可选技能（可通过中心发现，默认不激活）
├── tests/                    # 测试套件
├── website/                  # 文档网站（hermes-agent.nousresearch.com）
│
├── cli-config.yaml.example   # 示例配置（复制到 ~/.hermes/config.yaml）
└── AGENTS.md                 # AI 编码助手的开发指南
```
### 用户配置（存储在 `~/.hermes/`）

| 路径 | 用途 |
|------|---------|
| `~/.hermes/config.yaml` | 设置（模型、终端、工具集、压缩等） |
| `~/.hermes/.env` | API 密钥和密钥 |
| `~/.hermes/auth.json` | OAuth 凭证（Nous Portal） |
| `~/.hermes/skills/` | 所有活跃技能（捆绑 + 从 Hub 安装 + Agent 创建） |
| `~/.hermes/memories/` | 持久化记忆（MEMORY.md, USER.md） |
| `~/.hermes/state.db` | SQLite 会话数据库 |
| `~/.hermes/sessions/` | JSON 会话日志 |
| `~/.hermes/cron/` | 定时任务数据 |
| `~/.hermes/whatsapp/session/` | WhatsApp 桥接凭证 |

---

## 架构概述

### 核心循环

```
用户消息 → AIAgent._run_agent_loop()
  ├── 构建系统提示词 (prompt_builder.py)
  ├── 构建 API 参数 (模型、消息、工具、推理配置)
  ├── 调用 LLM (OpenAI 兼容 API)
  ├── 如果响应中包含 tool_calls:
  │     ├── 通过注册表分发执行每个工具
  │     ├── 将工具结果添加到对话中
  │     └── 循环回到 LLM 调用
  ├── 如果是文本响应:
  │     ├── 将会话持久化到数据库
  │     └── 返回 final_response
  └── 如果接近 Token 限制，则进行上下文压缩
```

### 关键设计模式

- **自注册工具**：每个工具文件在导入时调用 `registry.register()`。`model_tools.py` 通过导入所有工具模块来触发发现。
- **工具集分组**：工具被分组到工具集（`web`、`terminal`、`file`、`browser` 等）中，可以按平台启用/禁用。
- **会话持久化**：所有对话都存储在 SQLite 中（`hermes_state.py`），支持全文搜索和唯一的会话标题。JSON 日志存储在 `~/.hermes/sessions/`。
- **临时注入**：系统提示词和预填充消息在 API 调用时注入，永远不会持久化到数据库或日志中。
- **提供商抽象**：Agent 可与任何 OpenAI 兼容的 API 配合使用。提供商解析在初始化时进行（Nous Portal OAuth、OpenRouter API 密钥或自定义端点）。
- **提供商路由**：使用 OpenRouter 时，`config.yaml` 中的 `provider_routing` 控制提供商选择（按吞吐量/延迟/价格排序，允许/忽略特定提供商，数据保留策略）。这些作为 `extra_body.provider` 注入到 API 请求中。

---

## 代码风格

- **遵循 PEP 8**，但有实际例外（我们不强制执行严格的行长度限制）
- **注释**：仅在解释非显而易见的意图、权衡或 API 特性时使用。不要叙述代码做了什么——`# 递增计数器` 没有添加任何信息
- **错误处理**：捕获特定异常。使用 `logger.warning()`/`logger.error()` 记录日志——对于意外错误使用 `exc_info=True`，以便堆栈跟踪出现在日志中
- **跨平台**：切勿假设是 Unix。参见 [跨平台兼容性](#cross-platform-compatibility)

---

## 添加新工具

在编写工具之前，先问：[这应该是一个技能吗？](#should-it-be-a-skill-or-a-tool)

工具向中央注册表自注册。每个工具文件将其模式、处理程序和注册放在一起：

```python
"""my_tool — 简要描述此工具的功能。"""

import json
from tools.registry import registry


def my_tool(param1: str, param2: int = 10, **kwargs) -> str:
    """处理程序。返回字符串结果（通常是 JSON）。"""
    result = do_work(param1, param2)
    return json.dumps(result)


MY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "此工具的功能以及 Agent 应在何时使用它。",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "param1 是什么"},
                "param2": {"type": "integer", "description": "param2 是什么", "default": 10},
            },
            "required": ["param1"],
        },
    },
}


def _check_requirements() -> bool:
    """如果此工具的依赖项可用，则返回 True。"""
    return True


registry.register(
    name="my_tool",
    toolset="my_toolset",
    schema=MY_TOOL_SCHEMA,
    handler=lambda args, **kw: my_tool(**args, **kw),
    check_fn=_check_requirements,
)
```

**连接到工具集（必需）**：内置工具是自动发现的：任何包含顶级 `registry.register(...)` 调用的 `tools/*.py` 文件，在 `model_tools` 加载时，都会被 `tools/registry.py` 中的 `discover_builtin_tools()` 导入。`model_tools.py` 中**没有**需要维护的手动导入列表。

您仍然必须将工具名称添加到 `toolsets.py` 中的相应列表（例如 `_HERMES_CORE_TOOLS` 或专用的工具集）；否则工具会注册但永远不会暴露给 Agent。如果您引入了一个新的工具集，请在 `toolsets.py` 中添加它，并将其连接到相关的平台预设中。

有关配置文件感知路径以及插件与核心工具的指导，请参阅 `AGENTS.md`（**添加新工具**部分）。

---

## 添加技能

捆绑的技能位于按类别组织的 `skills/` 目录中。官方的可选技能在 `optional-skills/` 中使用相同的结构：

```
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # 必需：主要说明
│       └── scripts/              # 可选：辅助脚本
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

### SKILL.md 格式

```markdown
---
name: my-skill
description: 简要描述（显示在技能搜索结果中）
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # 可选 — 限制到特定的操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则加载到所有平台（默认）
required_environment_variables:    # 可选 — 安全的加载时设置元数据
  - name: MY_API_KEY
    prompt: API 密钥
    help: 从哪里获取
    required_for: 完整功能
prerequisites:                     # 可选的旧版运行时要求
  env_vars: [MY_API_KEY]           #   required_environment_variables 的向后兼容别名
  commands: [curl, jq]             #   仅建议性；不会隐藏技能
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    fallback_for_toolsets: [web]       # 可选 — 仅在工具集不可用时显示
    requires_toolsets: [terminal]      # 可选 — 仅在工具集可用时显示
---

# 技能标题

简要介绍。

## 何时使用
触发条件 — Agent 应在何时加载此技能？

## 快速参考
常用命令或 API 调用的表格。

## 步骤
Agent 遵循的分步说明。

## 陷阱
已知的故障模式以及如何处理它们。

## 验证
Agent 如何确认其工作正常。
```
### 平台特定技能

技能可以通过 `platforms` frontmatter 字段声明其支持的操作系统平台。具有此字段的技能会在不兼容的平台上自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。

```yaml
platforms: [macos]            # 仅 macOS（例如，iMessage、Apple Reminders）
platforms: [macos, linux]     # macOS 和 Linux
platforms: [windows]          # 仅 Windows
```

如果省略该字段或字段为空，则技能在所有平台上加载（向后兼容）。有关仅限 macOS 技能的示例，请参阅 `skills/apple/`。

### 条件性技能激活

技能可以声明一些条件，这些条件基于当前会话中可用的工具和工具集来控制技能何时出现在系统提示词中。这主要用于**后备技能**——即仅当主要工具不可用时才应显示的替代方案。

`metadata.hermes` 下支持四个字段：

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # 仅当这些工具集不可用时显示
    requires_toolsets: [terminal]     # 仅当这些工具集可用时显示
    fallback_for_tools: [web_search]  # 仅当这些特定工具不可用时显示
    requires_tools: [terminal]        # 仅当这些特定工具可用时显示
```

**语义：**
- `fallback_for_*`：该技能是备用方案。当列出的工具/工具集可用时**隐藏**，当它们不可用时**显示**。用于付费工具的免费替代方案。
- `requires_*`：该技能需要某些工具才能运行。当列出的工具/工具集不可用时**隐藏**。用于依赖特定功能的技能（例如，仅在具有终端访问权限时才有意义的技能）。
- 如果同时指定了两者，则必须同时满足两个条件，技能才会出现。
- 如果两者都未指定，则技能始终显示（向后兼容）。

**示例：**

```yaml
# DuckDuckGo 搜索 —— 当 Firecrawl（web 工具集）不可用时显示
metadata:
  hermes:
    fallback_for_toolsets: [web]

# 智能家居技能 —— 仅当终端可用时才有用
metadata:
  hermes:
    requires_toolsets: [terminal]

# 本地浏览器后备方案 —— 当 Browserbase 不可用时显示
metadata:
  hermes:
    fallback_for_toolsets: [browser]
```

过滤发生在 `agent/prompt_builder.py` 中的提示词构建时。`build_skills_system_prompt()` 函数从 Agent 接收可用工具和工具集的集合，并使用 `_skill_should_show()` 来评估每个技能的条件。

### 技能设置元数据

技能可以通过 `required_environment_variables` frontmatter 字段声明安全的加载时设置元数据。缺少值不会将技能从发现中隐藏；它们会在技能实际加载时触发仅限 CLI 的安全提示。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
    required_for: 完整功能
```

用户可以跳过设置并继续加载技能。Hermes 仅向模型公开元数据（`stored_as`、`skipped`、`validated`）——绝不公开密钥值。

旧的 `prerequisites.env_vars` 仍然受支持，并已规范化为新的表示形式。

```yaml
prerequisites:
  env_vars: [TENOR_API_KEY]       # required_environment_variables 的旧别名
  commands: [curl, jq]            # 建议性 CLI 检查
```

消息网关和消息会话从不通过带内方式收集密钥；它们会指示用户运行 `hermes setup` 或在本地更新 `~/.hermes/.env`。

**何时声明必需的环境变量：**
- 技能使用应在加载时安全收集的 API 密钥或 Token
- 如果用户跳过设置，技能仍然有用，但功能可能会适度降级

**何时声明命令先决条件：**
- 技能依赖可能未安装的 CLI 工具（例如 `himalaya`、`openhue`、`ddgs`）
- 将命令检查视为指导，而非发现时隐藏

有关示例，请参阅 `skills/gifs/gif-search/` 和 `skills/email/himalaya/`。

### 技能编写标准（硬性规定）

每个新的或现代化的技能——无论是捆绑的、可选的还是贡献的——在合并前都必须满足这些标准。审阅者将拒绝违反这些标准的 PR。

1.  **`description` ≤ 60 个字符，一句话，以句号结尾。** 过长的描述会使技能列表 UI 臃肿，并且在加载许多技能时分散模型的注意力。说明功能，而非实现。不要使用营销词汇（"强大"、"全面"、"无缝"、"先进"）。不要重复技能名称。使用以下代码验证：
    ```python
    import re, pathlib
    m = re.search(r'^description: (.*)$',
                  pathlib.Path('skills/<cat>/<name>/SKILL.md').read_text(),
                  re.MULTILINE)
    assert len(m.group(1)) <= 60, len(m.group(1))
    ```

    好的示例：`按关键词、作者、类别或 ID 搜索 arXiv 论文。`
    坏的示例：`一个强大而全面的技能，允许 Agent 使用包括关键词、作者和类别在内的各种标准搜索 arXiv 以查找相关学术论文。`

2.  **SKILL.md 正文中引用的工具必须是原生 Hermes 工具或技能明确期望的 MCP 服务器。** 当技能需要某项功能时，请使用反引号指向正确的工具名称：`` `terminal` ``、`` `web_extract` ``、`` `web_search` ``、`` `read_file` ``、`` `write_file` ``、`` `patch` ``、`` `search_files` ``、`` `vision_analyze` ``、`` `browser_navigate` ``、`` `delegate_task` ``、`` `image_generate` ``、`` `text_to_speech` ``、`` `cronjob` ``、`` `memory` ``、`` `skill_view` ``、`` `todo` ``、`` `execute_code` ``。

    请**不要**命名 Agent 已封装好的 shell 实用程序：

    | 不要说 | 应该说 |
    |---|---|
    | `grep`, `rg` | `search_files` |
    | `cat`, `head`, `tail` | `read_file` |
    | `sed`, `awk` | `patch` |
    | `find`, `ls` | `search_files`（配合 `target='files'`） |
    | 用于内容提取的 `curl` | `web_extract` |
    | `echo > file`, `cat <<EOF` | `write_file` |
---
title: 技能贡献指南
description: 如何为 Hermes 贡献新技能
---

## 贡献流程

1. **Fork 仓库**并创建一个新分支。
2. **在 `skills/` 目录下创建一个新文件夹**，以技能名称命名（例如 `skills/my_skill`）。
3. **添加以下文件**：
   - `SKILL.md` — 技能的主要文档
   - `scripts/` — 辅助脚本（可选）
   - `references/` — 参考材料（可选）
   - `templates/` — 模板（可选）
   - `tests/skills/test_<skill>_skill.py` — 测试
4. **在 `.env.example` 中添加环境变量**（如果需要）。
5. **运行测试**：`scripts/run_tests.sh tests/skills/test_<skill>_skill.py -q`
6. **提交 PR**，并包含：
   - 技能用途的简短描述
   - 测试通过的截图
   - 使用 Hermes 运行该技能的示例输出

## 技能结构

### 技能元数据（Frontmatter）

每个 `SKILL.md` 必须以 YAML frontmatter 开头，包含以下字段：

```yaml
---
title: 技能名称
description: 简短描述（最多 80 个字符）
author: 贡献者姓名 (GitHub 用户名)
version: 1.0.0
platforms: [linux, macos, windows]  # 可选，默认为所有平台
---
```

**规则：**

1. **`title:` 使用动词开头。** 技能名称应描述其功能，例如 `"Deploy to Fly.io"` 或 `"Analyze Logs"`。避免使用 "How to" 或 "Guide to" 开头。

2. **`description:` 说明技能的作用，而非其实现方式。** 如果技能依赖于 MCP 服务器，请命名该 MCP 服务器并在 `## 前提条件` 中记录其设置。第三方 CLI（例如 `ffmpeg`、`gh`、特定 SDK）可以在脚本文件中调用，但文档应将其描述为“通过 `terminal` 工具调用”，而非手动 shell 会话。

3. **`platforms:` 根据实际脚本导入进行审核。** 使用仅限 POSIX 的原语（`fcntl`、`termios`、`os.setsid`、用于存活性检查的 `os.kill(pid, 0)`、`/proc`、硬编码的 `/tmp` 路径、`signal.SIGKILL`、bash heredocs、`osascript`、`apt`、`systemctl`）的技能必须通过 `platforms:` frontmatter 声明其支持的平台。默认立场是首先进行跨平台修复——使用 `tempfile.gettempdir()`、`pathlib.Path`、`psutil.pid_exists()`、Python 级别的过滤而非 `grep`。仅当依赖项真正受平台限制时才限定到较窄的平台集（例如 `osascript` 仅限 macOS，`/proc` 仅限 Linux）。

4. **`author` 首先注明人类贡献者。** 对于外部贡献，贡献者的真实姓名 + GitHub 用户名放在首位（`Jane Doe (jane-doe)`）；"Hermes Agent" 是次要协作者。如果贡献者的提交显示 "Hermes Agent" 为作者，因为他们使用 Hermes 起草了技能，请将其替换为他们的真实姓名——功劳归于人类，而非工具。

5. **`SKILL.md` 正文使用现代章节顺序。** `# <技能> 技能` 标题，2-3 句话介绍说明其作用和不作用，然后：
   - `## 何时使用` — 触发条件
   - `## 前提条件` — 环境变量、安装步骤、MCP 设置、API 密钥来源
   - `## 如何运行` — 通过 `terminal` 工具的规范调用方式
   - `## 快速参考` — 扁平的命令/API 参考
   - `## 步骤` — 带有可复制粘贴命令的编号步骤
   - `## 常见问题` — 已知限制、速率限制、看似损坏但实际正常的情况
   - `## 验证` — 证明技能有效的单个命令

   复杂技能目标约 200 行，简单技能约 100 行。删除冗余的介绍性内容、营销文案以及已在 `## 前提条件` 中记录的环境变量的重复解释。

6. **脚本放在 `scripts/` 中，参考放在 `references/` 中，模板放在 `templates/` 中。** 不要期望模型每次调用都内联编写解析器、XML 遍历器或非平凡逻辑——提供一个辅助脚本。在 SKILL.md 中通过相对于技能目录的路径引用脚本。

7. **测试位于 `tests/skills/test_<skill>_skill.py`** 并且仅使用标准库 + pytest + `unittest.mock`。不进行实时网络调用。通过 `scripts/run_tests.sh tests/skills/test_<skill>_skill.py -q` 运行。必须在密封的 CI 环境中通过（没有 API 密钥泄漏）。对任何环境变量或文件系统依赖使用 `monkeypatch` 和 `tmp_path`。

8. **`.env.example` 的添加内容被隔离到一个清晰分隔的块中。** 不要修改周围文件——贡献者提供的 `.env.example` 版本通常已过时，并且在抢救期间，技能自身块之外的编辑将被丢弃。使用 `#` 注释所有值（这是文档，而非实时配置）。

### 技能指南

- **除非绝对必要，否则不要使用外部依赖。** 优先使用标准库 Python、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。
- **渐进式披露。** 将最常见的工作流程放在前面。边缘情况和高级用法放在底部。
- **包含辅助脚本**用于 XML/JSON 解析或复杂逻辑——不要期望 LLM 每次都内联编写解析器。
- **测试它。** 运行 `hermes --toolsets skills -q "使用 X 技能执行 Y"` 并验证 Agent 是否正确遵循指令。

---

## 添加皮肤 / 主题

Hermes 使用数据驱动的皮肤系统——添加新皮肤无需更改代码。

**选项 A：用户皮肤（YAML 文件）**

创建 `~/.hermes/skins/<name>.yaml`：

```yaml
name: mytheme
description: 主题的简短描述

colors:
  banner_border: "#HEX"     # 面板边框颜色
  banner_title: "#HEX"      # 面板标题颜色
  banner_accent: "#HEX"     # 章节标题颜色
  banner_dim: "#HEX"        # 柔和/暗淡文本颜色
  banner_text: "#HEX"       # 正文文本颜色
  response_border: "#HEX"   # 响应框边框颜色

spinner:
  waiting_faces: ["(⚔)", "(⛨)"]
  thinking_faces: ["(⚔)", "(⌁)"]
  thinking_verbs: ["forging", "plotting"]
  wings:                     # 可选的左右装饰
    - ["⟪⚔", "⚔⟫"]

branding:
  agent_name: "My Agent"
  welcome: "欢迎消息"
  response_label: " ⚔ Agent "
  prompt_symbol: "⚔"

tool_prefix: "╎"             # 工具输出行前缀
```

所有字段都是可选的——缺失的值从默认皮肤继承。

**选项 B：内置皮肤**

添加到 `hermes_cli/skin_engine.py` 中的 `_BUILTIN_SKINS` 字典。使用与上述相同的模式，但作为 Python 字典。内置皮肤随包提供，始终可用。

**激活方式：**
- CLI：`/skin mytheme` 或在 config.yaml 中设置 `display.skin: mytheme`
- 配置：`display: { skin: mytheme }`

有关完整模式和现有皮肤示例，请参阅 `hermes_cli/skin_engine.py`。

---

## 跨平台兼容性

Hermes 在 Linux、macOS 和原生 Windows（以及 WSL2）上运行。编写涉及操作系统的代码时，请假设*任何*平台都可能执行你的代码路径。

> **提交 PR 前：** 运行 `scripts/check-windows-footguns.py` 以捕获你的差异中常见的 Windows 不安全模式。它基于 grep 且成本低廉；CI 也会在每个 PR 上运行它。

### 关键规则

1. **切勿调用 `os.kill(pid, 0)` 进行存活性检查。** `os.kill(pid, 0)` 是检查“此 PID 是否存活”的标准 POSIX 惯用法——信号 0 是无操作权限检查。**在 Windows 上，它并非无操作。** Python 的 Windows `os.kill` 将 `sig=0` 映射到 `CTRL_C_EVENT`（它们在整数值 0 处冲突）并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由，这将 Ctrl+C 广播到包含目标 PID 的**整个控制台进程组**。“探测是否存活”悄无声息地变成了“杀死目标以及通常与其共享控制台的不相关进程。” 参见 [bpo-14484](https://bugs.python.org/issue14484)（自 2012 年开放——由于兼容性原因永远不会修复）。
**首选：** 使用 `psutil`（核心依赖项 — 始终可用）：

```python
import psutil
if psutil.pid_exists(pid):
    # 进程存活 — 在所有平台上都安全
    ...
```

如果你特别需要使用 hermes 包装器（它在 pip install 完成前的脚手架阶段导入时有一个标准库回退方案），请使用 `gateway.status._pid_exists(pid)`。它会先调用 `psutil.pid_exists`，仅在 Windows 上且 psutil 因故缺失时，回退到手动实现的 `OpenProcess + WaitForSingleObject` 操作。

审计 grep 查找新的调用点：`rg "os\.kill\([^,]+,\s*0\s*\)"`。在非测试代码中的任何匹配都可能是 Windows 静默终止 bug。

2. **在调用 shell 命令前使用 `shutil.which()` — 不要假设 Windows 拥有 Linux 的工具。** `wmic` 已在 Windows 10 21H1 及更高版本中移除。`ps`、`kill`、`grep`、`awk`、`fuser`、`lsof`、`pgrep` 以及大多数 POSIX CLI 工具在 Windows 上根本不存在。使用 `shutil.which("tool")` 测试可用性，并回退到 Windows 原生等效方案 — 通常是通过 `subprocess.run(["powershell", "-NoProfile", "-Command", ...])` 使用 PowerShell。

对于进程枚举：PowerShell 的 `Get-CimInstance Win32_Process` 是现代版的 `wmic process` 替代品。参考 `hermes_cli/gateway.py::_scan_gateway_pids` 中的模式。

3. **`termios` 和 `fcntl` 仅适用于 Unix。** 始终捕获 `ImportError` 和 `NotImplementedError`：
   ```python
   try:
       from simple_term_menu import TerminalMenu
       menu = TerminalMenu(options)
       idx = menu.show()
   except (ImportError, NotImplementedError):
       # 回退方案：Windows 的编号菜单
       for i, opt in enumerate(options):
           print(f"  {i+1}. {opt}")
       idx = int(input("Choice: ")) - 1
   ```

4. **文件编码。** Windows 可能以 `cp1252` 编码保存 `.env` 文件。始终处理编码错误：
   ```python
   try:
       load_dotenv(env_path)
   except UnicodeDecodeError:
       load_dotenv(env_path, encoding="latin-1")
   ```
   配置文件（`config.yaml`）可能被记事本等编辑器以 UTF-8 BOM 保存 — 在读取可能被 Windows GUI 编辑器编辑过的文件时，使用 `encoding="utf-8-sig"`。

5. **进程管理。** `os.setsid()`、`os.killpg()`、`os.fork()`、`os.getuid()` 和 POSIX 信号处理在 Windows 上有所不同。使用 `platform.system()`、`sys.platform` 或 `hasattr(os, "setsid")` 进行防护：
   ```python
   if platform.system() != "Windows":
       kwargs["preexec_fn"] = os.setsid
   else:
       kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
   ```

   **首选：** 要终止一个进程及其子进程（即 POSIX 上 `os.killpg` 的功能），请使用 `psutil` — 它在所有平台上都有效：
   ```python
   import psutil
   try:
       parent = psutil.Process(pid)
       # 先终止子进程（自底向上），然后终止父进程。
       for child in parent.children(recursive=True):
           child.kill()
       parent.kill()
   except psutil.NoSuchProcess:
       pass
   ```

6. **Windows 上不存在的信号：`SIGALRM`、`SIGCHLD`、`SIGHUP`、`SIGUSR1`、`SIGUSR2`、`SIGPIPE`、`SIGQUIT`、`SIGKILL`。** 如果你在 Windows 上引用它们，Python 的 `signal` 模块会在导入时引发 `AttributeError`。使用 `getattr(signal, "SIGKILL", signal.SIGTERM)` 或将整个代码块置于平台检查之后。`loop.add_signal_handler` 在 Windows 上会引发 `NotImplementedError` — 始终捕获它。

7. **路径分隔符。** 使用 `pathlib.Path` 而不是用 `/` 进行字符串拼接。正斜杠在 Windows 上几乎到处都有效，但 `subprocess.run(["cmd.exe", "/c", ...])` 和其他 shell 上下文可能需要反斜杠 — 在子进程边界处使用 `str(path)` 进行转换，而不是在 Python 逻辑内部。

8. **Windows 上创建符号链接需要提升的权限**（除非开发者模式已开启）。创建符号链接的测试需要 `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`。

9. **POSIX 文件模式（0o600、0o644 等）在 NTFS 上默认不被强制执行。** 断言 `stat().st_mode & 0o777` 的测试必须在 Windows 上跳过 — 这个概念不适用。如果需要 Windows 秘密文件保护，请使用 ACL（`icacls`、`pywin32`）。

10. **Windows 上分离的后台守护进程需要 `pythonw.exe`，而不是 `python.exe`。** `python.exe` 总是分配或附加到一个控制台，这使得它容易受到来自任何兄弟进程的 `CTRL_C_EVENT` 广播的影响。`pythonw.exe` 是无控制台的变体。结合 `subprocess.Popen(creationflags=...)` 中的 `CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB` 使用。参考实现见 `hermes_cli/gateway_windows.py::_spawn_detached`。

11. **使用 `subprocess.Popen` 调用 `.cmd` 或 `.bat` 包装器时，需要用 `shutil.which` 来解析路径。** 在 Windows 上向 `Popen` 传递 `"agent-browser"` 会找到 `node_modules/.bin/` 中无扩展名的 POSIX shebang 包装器，而 `CreateProcessW` 无法执行它 — 你会得到 `WinError 193 "not a valid Win32 application"`。使用 `shutil.which("agent-browser", path=local_bin)`，它会遵循 PATHEXT 并在 Windows 上选择 `.CMD` 变体。

12. **不要使用 shell shebang 作为运行 Python 的方式。** `#!/usr/bin/env python` 仅在文件通过 Unix shell 执行时才有效。在 Windows 上，即使文件有 shebang 行，`subprocess.run(["./myscript.py"])` 也会失败。始终显式调用 Python：`[sys.executable, "myscript.py"]`。

13. **安装程序中的 shell 命令。** 如果你修改了 `scripts/install.sh`，请在 `scripts/install.ps1` 中进行等效修改。这两个脚本是“在 Linux 上工作并不意味着在 Windows 上工作”的典型例子，并且已经多次出现差异 — 请保持它们同步。

14. **Windows 上已知被 OneDrive 重定向的路径：** 桌面、文档、图片、视频。当启用 OneDrive 备份时，“真实”路径是 `%USERPROFILE%\OneDrive\Desktop`（等等），而不是 `%USERPROFILE%\Desktop`（后者作为一个空壳存在）。通过 `ctypes` + `SHGetKnownFolderPath` 或读取 `Shell Folders` 注册表键来解析真实位置 — 永远不要假设 `~/Desktop`。
15. **生成脚本中的 CRLF 与 LF 问题。** Windows 的 `cmd.exe` 和 `schtasks`
    会逐行解析；混合或仅使用 LF 换行符可能会破坏多行
    `.cmd` / `.bat` 文件。在生成 Windows 将要执行的脚本时，请使用 `open(path, "w", encoding="utf-8",
    newline="\r\n")` — 或者 `open(path, "wb")` + 显式字节。

16. **命令行中的两种不同引用方案。** `subprocess.run
    (["schtasks", "/TR", some_cmd])` → schtasks 本身会解析 `/TR`，并且
    当任务触发时，`some_cmd` 字符串会被 `cmd.exe` 重新解析。
    不同的解析器，不同的转义规则。使用两个独立的引用
    辅助函数，切勿混用。参考 `hermes_cli/gateway_windows.py::
    _quote_cmd_script_arg` 和 `_quote_schtasks_arg` 这一对函数。

### 跨平台测试

使用仅限 POSIX 的系统调用的测试需要跳过标记。常见的包括：
- 符号链接 → `@pytest.mark.skipif(sys.platform == "win32", ...)`
- `0o600` 文件模式 → `@pytest.mark.skipif(sys.platform.startswith("win"), ...)`
- `signal.SIGALRM` → 仅限 Unix（参见 `tests/conftest.py::_enforce_test_timeout`）
- `os.setsid` / `os.fork` → 仅限 Unix
- 实时 Winsock / Windows 特定的回归测试 →
  `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

如果为了跨平台测试而修改了 `sys.platform`，也请同时修改
`platform.system()` / `platform.release()` / `platform.mac_ver()` — 每个
函数都会独立地重新读取真实的操作系统信息，因此半修改的测试在 Windows 运行器上
仍然会走错分支。

---

## 安全考量

Hermes 拥有终端访问权限。安全至关重要。

### 现有保护措施

| 层级 | 实现 |
|-------|---------------|
| **Sudo 密码管道** | 使用 `shlex.quote()` 防止 shell 注入 |
| **危险命令检测** | `tools/approval.py` 中的正则表达式模式，配合用户审批流程 |
| **Cron 提示词注入** | `tools/cronjob_tools.py` 中的扫描器会阻止指令覆盖模式 |
| **写入拒绝列表** | 受保护路径（`~/.ssh/authorized_keys`, `/etc/shadow`）通过 `os.path.realpath()` 解析，防止符号链接绕过 |
| **技能防护** | 对 hub 安装的技能进行安全扫描（`tools/skills_guard.py`） |
| **代码执行沙盒** | `execute_code` 子进程运行时，环境变量中的 API 密钥已被剥离 |
| **容器加固** | Docker：所有能力被丢弃，无权限提升，PID 限制，大小受限的 tmpfs |

### 贡献安全敏感代码时

- **始终使用 `shlex.quote()`** 将用户输入插入到 shell 命令时
- **使用 `os.path.realpath()` 解析符号链接** 在进行基于路径的访问控制检查之前
- **不要记录密钥。** API 密钥、Token 和密码绝不应出现在日志输出中
- **捕获广泛的异常** 围绕工具执行，以便单个故障不会导致 Agent 循环崩溃
- **在所有平台上测试** 如果你的更改涉及文件路径、进程管理或 shell 命令

如果你的 PR 影响安全性，请在描述中明确注明。

### 依赖锁定策略（供应链加固）

在 2026 年 3 月的 [litellm 供应链攻击](https://github.com/BerriAI/litellm/issues/24512) 和 2026 年 5 月的 [Mini Shai-Hulud 蠕虫攻击活动](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack) 之后，所有依赖必须遵循以下规则：

| 来源类型 | 必需的处理方式 | 原理 |
|---|---|---|
| **PyPI 包** | `>=floor,<next_major` | PyPI 版本一旦发布就是不可变的，但新版本可能会被推送到你的版本范围内。`<next_major` 上限可以阻止 1.x 安装升级到恶意的 2.0.0。 |
| **Git URL** (atroposlib, tinker, yc-bench, Baileys) | 完整的提交 SHA | 分支和标签是可变的引用；SHA 是内容寻址的。 |
| **GitHub Actions** | 完整的提交 SHA + 版本注释 | Action 标签是可变的引用（例如 tj-actions/changed-files 2025 年 3 月）。固定为 `uses: owner/action@<sha>  # vX.Y.Z` |
| **仅限 CI 的 pip 安装** | `==exact` | 封闭的 CI 构建；版本变动是可接受的。 |

**PR 中每个新的 PyPI 依赖都必须有 `<next_major` 上限。** 添加无上限 `>=X.Y.Z` 规范的 PR 将被审阅者拒绝。`supply-chain-audit.yml` CI 工作流也会标记依赖清单的更改以供人工审查。

**如何确定上限：**
- 如果包的版本是 `1.x.y`，使用 `<2`。
- 如果包的版本是 `0.x.y`（1.0 之前），使用 `<0.(current_minor + 2)` — 例如，如果当前是 `0.29.x`，使用 `<0.32`。这提供了约 2 个次要版本的余量，同时保持窗口足够小，使得恶意接管版本不太可能落入其中。
- 例外：具有非常稳定 API 的包（例如 `aiohttp-socks`）可以在审阅者酌情决定下使用 `<1`。

**示例：**
```toml
# ✅ 正确 — 1.0 之后
"openai>=2.21.0,<3"
"pydantic>=2.12.5,<3"

# ✅ 正确 — 1.0 之前（严格的次要版本窗口）
"asyncpg>=0.29,<0.32"
"aiosqlite>=0.20,<0.23"
"hindsight-client>=0.4.22,<0.5"

# ❌ 被拒绝 — 无上限
"some-package>=1.2.3"

# ❌ 被拒绝 — 过于严格（阻止合法的补丁）
"some-package==1.2.3"

# ❌ 被拒绝 — 对于 1.0 之前版本过于宽松（允许 80 个次要版本）
"some-package>=0.20,<1"
```

**参考 PR：** #2796 (litellm 移除), #2810 (上限规范通过), #9801 (SHA 固定 + supply-chain-audit CI)。

---

## Pull Request 流程

### 分支命名

```
fix/description        # 错误修复
feat/description       # 新功能
docs/description       # 文档
test/description       # 测试
refactor/description   # 代码重构
```

### 提交前

1. **运行测试**：`scripts/run_tests.sh`（推荐；与 CI 相同）或在项目 venv 激活状态下运行 `pytest tests/ -v`
2. **手动测试**：运行 `hermes` 并测试你更改的代码路径
3. **检查跨平台影响**：如果你涉及文件 I/O、进程管理或终端处理，请考虑 macOS、Linux 和 WSL2
4. **保持 PR 专注**：每个 PR 一个逻辑变更。不要将错误修复、重构和新功能混在一起。
### PR 描述

包含：
- **什么** 发生了变化以及 **为什么**
- **如何测试**（针对错误的复现步骤，针对功能的使用示例）
- **在哪些平台** 上进行了测试
- 引用任何相关的问题

### 提交信息

我们使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<类型>(<范围>): <描述>
```

| 类型 | 用于 |
|------|---------|
| `fix` | 错误修复 |
| `feat` | 新功能 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 代码重构（无行为变更） |
| `chore` | 构建、CI、依赖项更新 |

范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security` 等。

示例：
```
fix(cli): 修复当 model 为字符串时 save_config_value 的崩溃问题
feat(gateway): 添加 WhatsApp 多用户会话隔离
fix(security): 防止 sudo 密码管道中的 shell 注入
test(tools): 为 file_operations 添加单元测试
```

---

## 报告问题

- 使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- 包含：操作系统、Python 版本、Hermes 版本 (`hermes version`)、完整的错误回溯
- 包含复现步骤
- 创建新问题前请检查现有问题
- 对于安全漏洞，请私下报告

---

## 社区

- **Discord**: [discord.gg/NousResearch](https://discord.gg/NousResearch) — 用于提问、展示项目和分享技能
- **GitHub Discussions**: 用于设计提案和架构讨论
- **技能中心**: 将专业技能上传到注册表并与社区分享

---

## 许可证

通过贡献，您同意您的贡献将根据 [MIT 许可证](LICENSE) 获得许可。