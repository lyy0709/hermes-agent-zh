# 为 Hermes Agent 贡献代码

感谢您为 Hermes Agent 贡献代码！本指南涵盖了您所需的一切：设置开发环境、理解架构、决定构建什么以及如何让您的 PR 被合并。

---

## 贡献优先级

我们按以下顺序评估贡献的价值：

1.  **Bug 修复** — 崩溃、错误行为、数据丢失。始终是最高优先级。
2.  **跨平台兼容性** — macOS、不同的 Linux 发行版以及 Windows 上的 WSL2。我们希望 Hermes 能在任何地方运行。
3.  **安全加固** — shell 注入、提示词注入、路径遍历、权限提升。请参阅[安全注意事项](#security-considerations)。
4.  **性能和健壮性** — 重试逻辑、错误处理、优雅降级。
5.  **新技能** — 但仅限于广泛有用的技能。请参阅[应该是技能还是工具？](#should-it-be-a-skill-or-a-tool)
6.  **新工具** — 很少需要。大多数功能都应该是技能。见下文。
7.  **文档** — 修复、澄清、新示例。

---

## 应该是技能还是工具？

这是新贡献者最常见的问题。答案几乎总是**技能**。

### 在以下情况下，将其设为技能：

- 该功能可以表示为指令 + shell 命令 + 现有工具
- 它包装了一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用
- 它不需要自定义的 Python 集成或由 Agent 框架管理的 API 密钥
- 示例：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件

### 在以下情况下，将其设为工具：

- 它需要与 API 密钥、认证流程或由 Agent 框架管理的多组件配置进行端到端集成
- 它需要自定义的处理逻辑，并且每次都必须精确执行（不能依赖 LLM 解释的“尽力而为”）
- 它处理二进制数据、流式传输或无法通过终端的实时事件
- 示例：浏览器自动化（Browserbase 会话管理）、TTS（音频编码 + 平台交付）、视觉分析（base64 图像处理）

### 技能应该被捆绑吗？

捆绑技能（位于 `skills/` 目录下）随每个 Hermes 安装包一起发布。它们应该**对大多数用户广泛有用**：

- 文档处理、网络研究、常见的开发工作流、系统管理
- 被广泛人群定期使用

如果您的技能是官方的且有用，但并非普遍需要（例如，付费服务集成、重量级依赖项），请将其放入 **`optional-skills/`** 目录 — 它随代码仓库一起发布，但默认不激活。用户可以通过 `hermes skills browse` 发现它（标记为“official”），并使用 `hermes skills install` 安装它（没有第三方警告，内置信任）。

如果您的技能是专业化的、社区贡献的或小众的，它更适合放在 **技能中心** — 将其上传到技能注册表，并在 [Nous Research Discord](https://discord.gg/NousResearch) 上分享。用户可以使用 `hermes skills install` 安装它。

---

## 开发环境设置

### 先决条件

| 要求 | 备注 |
|-------------|-------|
| **Git** | 支持 `--recurse-submodules`，并安装 `git-lfs` 扩展 |
| **Python 3.11+** | 如果缺失，uv 会安装它 |
| **uv** | 快速的 Python 包管理器（[安装](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 可选 — 浏览器工具和 WhatsApp 桥接所需（与根目录 `package.json` 的 engines 字段匹配） |

### 克隆和安装

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建虚拟环境
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有额外功能（消息传递、定时任务、CLI 菜单、开发工具）
uv pip install -e ".[all,dev]"

# 可选：RL 训练子模块
# git submodule update --init tinker-atropos && uv pip install -e "./tinker-atropos"

# 可选：浏览器工具
npm install
```

### 配置开发环境

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# 至少添加一个 LLM 提供商的密钥：
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
# 首选 — 与 CI 匹配（封闭环境，4 个 xdist 工作进程）；参见 AGENTS.md
scripts/run_tests.sh

# 替代方案（首先激活虚拟环境）。在提交 PR 之前，仍建议使用包装脚本以确保与 GitHub Actions 一致：
pytest tests/ -v
```

---

## 项目结构

```
hermes-agent/
├── run_agent.py              # AIAgent 类 — 核心对话循环、工具调度、会话持久化
├── cli.py                    # HermesCLI 类 — 交互式 TUI、prompt_toolkit 集成
├── model_tools.py            # 工具编排（tools/registry.py 的薄层封装）
├── toolsets.py               # 工具分组和预设（hermes-cli, hermes-telegram 等）
├── hermes_state.py           # 带 FTS5 全文搜索和会话标题的 SQLite 会话数据库
├── batch_runner.py           # 用于轨迹生成的并行批量处理
│
├── agent/                    # Agent 内部模块（提取出的模块）
│   ├── prompt_builder.py         # 系统提示词组装（身份、技能、上下文文件、记忆）
│   ├── context_compressor.py     # 接近上下文窗口限制时的自动摘要
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
│   ├── registry.py               # 中央工具注册表（模式、处理器、调度）
│   ├── approval.py               # 危险命令检测 + 每会话批准
│   ├── terminal_tool.py          # 终端编排（sudo、环境生命周期、后端）
│   ├── file_operations.py        # read_file, write_file, search, patch 等
│   ├── web_tools.py              # web_search, web_extract（Parallel/Firecrawl + Gemini 摘要）
│   ├── vision_tools.py           # 通过多模态模型进行图像分析
│   ├── delegate_tool.py          # 子 Agent 生成和并行任务执行
│   ├── code_execution_tool.py    # 带 RPC 工具访问的沙盒化 Python
│   ├── session_search_tool.py    # 使用 FTS5 + 摘要搜索过去的对话
│   ├── cronjob_tools.py          # 定时任务管理
│   ├── skill_tools.py            # 技能搜索、加载、管理
│   └── environments/             # 终端执行后端
│       ├── base.py                   # BaseEnvironment ABC
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
├── environments/             # RL 训练环境（Atropos 集成）
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
  ├── 构建 API 参数 (model, messages, tools, reasoning config)
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
- **会话持久化**：所有对话都存储在 SQLite (`hermes_state.py`) 中，支持全文搜索和唯一的会话标题。JSON 日志存储在 `~/.hermes/sessions/`。
- **临时注入**：系统提示词和预填充消息在 API 调用时注入，永远不会持久化到数据库或日志中。
- **提供商抽象**：Agent 可与任何 OpenAI 兼容的 API 配合使用。提供商解析在初始化时进行（Nous Portal OAuth、OpenRouter API 密钥或自定义端点）。
- **提供商路由**：使用 OpenRouter 时，`config.yaml` 中的 `provider_routing` 控制提供商选择（按吞吐量/延迟/价格排序，允许/忽略特定提供商，数据保留策略）。这些作为 `extra_body.provider` 注入到 API 请求中。

---

## 代码风格

- **PEP 8**，但有实际例外（我们不强制执行严格的行长度限制）
- **注释**：仅在解释非显而易见的意图、权衡或 API 特性时使用。不要叙述代码做了什么——`# 递增计数器` 毫无意义
- **错误处理**：捕获特定异常。使用 `logger.warning()`/`logger.error()` 记录日志——对于意外错误使用 `exc_info=True`，以便堆栈跟踪出现在日志中
- **跨平台**：切勿假设 Unix。参见 [跨平台兼容性](#cross-platform-compatibility)

---

## 添加新工具

在编写工具之前，先问：[这应该是一个技能吗？](#should-it-be-a-skill-or-a-tool)

工具向中央注册表自注册。每个工具文件将其模式、处理程序和注册放在一起：

```python
"""my_tool — 此工具功能的简要描述。"""

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

您仍然必须将工具名称添加到 `toolsets.py` 中的相应列表（例如 `_HERMES_CORE_TOOLS` 或专用的工具集）；否则工具会注册，但永远不会暴露给 Agent。如果您引入了一个新的工具集，请在 `toolsets.py` 中添加它，并将其连接到相关的平台预设中。

有关配置文件感知路径以及插件与核心工具的指导，请参阅 `AGENTS.md`（**添加新工具**部分）。

---

## 添加技能

捆绑的技能位于按类别组织的 `skills/` 中。官方的可选技能在 `optional-skills/` 中使用相同的结构：

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
platforms: [macos, linux]          # 可选 — 限制在特定的操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则加载到所有平台（默认）
required_environment_variables:    # 可选 — 安全的加载时设置元数据
  - name: MY_API_KEY
    prompt: API 密钥
    help: 在哪里获取
    required_for: 完整功能
prerequisites:                     # 可选的旧版运行时要求
  env_vars: [MY_API_KEY]           #   required env vars 的向后兼容别名
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

如果省略该字段或字段为空，则技能在所有平台上加载（向后兼容）。有关仅限 macOS 的技能示例，请参阅 `skills/apple/`。

### 条件性技能激活

技能可以声明一些条件，这些条件基于当前会话中可用的工具和工具集来控制技能何时出现在系统提示词中。这主要用于**后备技能**——即仅当主要工具不可用时才应显示的替代方案。

在 `metadata.hermes` 下支持四个字段：

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

# 智能家居技能 —— 仅当终端可用时有用
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
- 技能依赖可能未安装的 CLI 工具（例如，`himalaya`、`openhue`、`ddgs`）
- 将命令检查视为指导，而非发现时隐藏

有关示例，请参阅 `skills/gifs/gif-search/` 和 `skills/email/himalaya/`。

### 技能指南

- **除非绝对必要，否则不要使用外部依赖。** 优先使用标准库 Python、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。
- **渐进式披露。** 将最常见的工作流放在前面。边缘情况和高级用法放在底部。
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
  banner_dim: "#HEX"        # 弱化/暗淡文本颜色
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

添加到 `hermes_cli/skin_engine.py` 中的 `_BUILTIN_SKINS` 字典。使用与上述相同的模式，但作为 Python 字典。内置皮肤随包一起提供，始终可用。

**激活方式：**
- CLI：`/skin mytheme` 或在 config.yaml 中设置 `display.skin: mytheme`
- 配置：`display: { skin: mytheme }`
完整模式和现有皮肤示例请参见 `hermes_cli/skin_engine.py`。

---

## 跨平台兼容性

Hermes 可在 Linux、macOS 和原生 Windows（以及 WSL2）上运行。编写涉及操作系统的代码时，请假设*任何*平台都可能执行你的代码路径。

> **提交 PR 前：** 运行 `scripts/check-windows-footguns.py` 以捕获你的代码差异中常见的 Windows 不安全模式。它基于 grep 且开销很小；CI 也会在每个 PR 上运行它。

### 关键规则

1.  **切勿使用 `os.kill(pid, 0)` 进行存活检查。** `os.kill(pid, 0)` 是检查“此 PID 是否存活”的标准 POSIX 惯用法——信号 0 是一个无操作权限检查。**在 Windows 上，它并非无操作。** Python 在 Windows 上的 `os.kill` 将 `sig=0` 映射到 `CTRL_C_EVENT`（它们在整数值 0 处冲突），并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由，该函数将 Ctrl+C 广播到包含目标 PID 的**整个控制台进程组**。“探测是否存活”会悄无声息地变成“杀死目标进程以及通常与其共享控制台的不相关进程”。参见 [bpo-14484](https://bugs.python.org/issue14484)（自 2012 年开放——出于兼容性原因将永远不会修复）。

    **首选方案：** 使用 `psutil`（核心依赖项——始终可用）：

    ```python
    import psutil
    if psutil.pid_exists(pid):
        # 进程存活——在所有平台上都安全
        ...
    ```

    如果你特别需要 Hermes 包装器（它在 pip install 完成前的脚手架阶段导入时有一个标准库回退），请使用 `gateway.status._pid_exists(pid)`。它首先调用 `psutil.pid_exists`，仅在 psutil 因故缺失时，在 Windows 上回退到手动编写的 `OpenProcess + WaitForSingleObject` 操作。

    审计 grep 查找新的调用点：`rg "os\.kill\([^,]+,\s*0\s*\)"`。在非测试代码中的任何匹配都假定是一个 Windows 静默杀死错误。

2.  **在调用 shell 命令前使用 `shutil.which()`——不要假设 Windows 拥有 Linux 拥有的工具。** `wmic` 在 Windows 10 21H1 及更高版本中已被移除。`ps`、`kill`、`grep`、`awk`、`fuser`、`lsof`、`pgrep` 以及大多数 POSIX CLI 工具在 Windows 上根本不存在。使用 `shutil.which("tool")` 测试可用性，并回退到 Windows 原生等效方案——通常是通过 `subprocess.run(["powershell", "-NoProfile", "-Command", ...])` 使用 PowerShell。

    对于进程枚举：PowerShell 的 `Get-CimInstance Win32_Process` 是 `wmic process` 的现代替代品。参见 `hermes_cli/gateway.py::_scan_gateway_pids` 中的模式。

3.  **`termios` 和 `fcntl` 是 Unix 独有的。** 始终捕获 `ImportError` 和 `NotImplementedError`：

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

4.  **文件编码。** Windows 可能以 `cp1252` 编码保存 `.env` 文件。始终处理编码错误：

    ```python
    try:
        load_dotenv(env_path)
    except UnicodeDecodeError:
        load_dotenv(env_path, encoding="latin-1")
    ```

    配置文件（`config.yaml`）可能被记事本等编辑器以 UTF-8 BOM 保存——在读取可能被 Windows GUI 编辑器编辑过的文件时，使用 `encoding="utf-8-sig"`。

5.  **进程管理。** `os.setsid()`、`os.killpg()`、`os.fork()`、`os.getuid()` 和 POSIX 信号处理在 Windows 上有所不同。使用 `platform.system()`、`sys.platform` 或 `hasattr(os, "setsid")` 进行防护：

    ```python
    if platform.system() != "Windows":
        kwargs["preexec_fn"] = os.setsid
    else:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    ```

    **首选方案：** 要杀死一个进程及其子进程（即 `os.killpg` 在 POSIX 上的功能），请使用 `psutil`——它在所有平台都有效：

    ```python
    import psutil
    try:
        parent = psutil.Process(pid)
        # 先杀死子进程（自底向上），然后杀死父进程。
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
    ```

6.  **Windows 上不存在的信号：`SIGALRM`、`SIGCHLD`、`SIGHUP`、`SIGUSR1`、`SIGUSR2`、`SIGPIPE`、`SIGQUIT`、`SIGKILL`。** 如果你在 Windows 上引用它们，Python 的 `signal` 模块会在导入时引发 `AttributeError`。使用 `getattr(signal, "SIGKILL", signal.SIGTERM)` 或将整个代码块置于平台检查之后。`loop.add_signal_handler` 在 Windows 上会引发 `NotImplementedError`——始终捕获它。

7.  **路径分隔符。** 使用 `pathlib.Path` 而不是用 `/` 进行字符串拼接。正斜杠在 Windows 上几乎到处都有效，但 `subprocess.run(["cmd.exe", "/c", ...])` 和其他 shell 上下文可能需要反斜杠——在子进程边界处使用 `str(path)` 进行转换，而不是在 Python 逻辑内部。

8.  **Windows 上的符号链接需要提升的权限**（除非开发者模式已开启）。创建符号链接的测试需要 `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`。

9.  **POSIX 文件模式（0o600、0o644 等）在 NTFS 上默认不强制执行。** 断言 `stat().st_mode & 0o777` 的测试必须在 Windows 上跳过——这个概念不适用。如果需要 Windows 秘密文件保护，请使用 ACL（`icacls`、`pywin32`）。

10. **Windows 上的分离后台守护进程需要 `pythonw.exe`，而不是 `python.exe`。** `python.exe` 总是分配或附加到一个控制台，这使其容易受到来自任何兄弟进程的 `CTRL_C_EVENT` 广播的影响。`pythonw.exe` 是无控制台变体。结合 `subprocess.Popen(creationflags=...)` 中的 `CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB` 使用。参考实现请参见 `hermes_cli/gateway_windows.py::_spawn_detached`。

11. **使用 `.cmd` 或 `.bat` 包装的 `subprocess.Popen` 需要 `shutil.which` 来解析。** 在 Windows 上将 `"agent-browser"` 传递给 `Popen` 会找到 `node_modules/.bin/` 中无扩展名的 POSIX shebang 包装，而 `CreateProcessW` 无法执行它——你会得到 `WinError 193 "not a valid Win32 application"`。使用 `shutil.which("agent-browser", path=local_bin)`，它会遵循 PATHEXT 并在 Windows 上选择 `.CMD` 变体。
12. **不要使用 shell shebang 来运行 Python。** `#!/usr/bin/env python` 仅在文件通过 Unix shell 执行时有效。在 Windows 上，即使文件有 shebang 行，`subprocess.run(["./myscript.py"])` 也会失败。始终显式调用 Python：`[sys.executable, "myscript.py"]`。

13. **安装程序中的 shell 命令。** 如果你修改了 `scripts/install.sh`，请在 `scripts/install.ps1` 中进行等效修改。这两个脚本是“在 Linux 上工作并不意味着在 Windows 上工作”的典型例子，并且已经多次出现差异——请保持它们同步。

14. **Windows 上已知被 OneDrive 重定向的路径：** 桌面、文档、图片、视频。启用 OneDrive 备份时，“真实”路径是 `%USERPROFILE%\OneDrive\Desktop`（等等），而不是 `%USERPROFILE%\Desktop`（它作为一个空壳存在）。通过 `ctypes` + `SHGetKnownFolderPath` 或读取 `Shell Folders` 注册表项来解析真实位置——永远不要假设 `~/Desktop`。

15. **生成脚本中的 CRLF 与 LF。** Windows 的 `cmd.exe` 和 `schtasks` 逐行解析；混合或仅 LF 的行尾可能会破坏多行的 `.cmd` / `.bat` 文件。在生成 Windows 将执行的脚本时，使用 `open(path, "w", encoding="utf-8", newline="\r\n")` —— 或 `open(path, "wb")` + 显式字节。

16. **一个命令行中的两种不同引用方案。** `subprocess.run(["schtasks", "/TR", some_cmd])` → schtasks 本身解析 `/TR`，并且当任务触发时，`some_cmd` 字符串会被 `cmd.exe` 重新解析。不同的解析器，不同的转义规则。使用两个独立的引用辅助函数，并且永远不要交叉使用它们。参考 `hermes_cli/gateway_windows.py::_quote_cmd_script_arg` 和 `_quote_schtasks_arg` 这对函数。

### 跨平台测试

使用仅限 POSIX 的系统调用的测试需要跳过标记。常见的包括：
- 符号链接 → `@pytest.mark.skipif(sys.platform == "win32", ...)`
- `0o600` 文件模式 → `@pytest.mark.skipif(sys.platform.startswith("win"), ...)`
- `signal.SIGALRM` → 仅限 Unix（参见 `tests/conftest.py::_enforce_test_timeout`）
- `os.setsid` / `os.fork` → 仅限 Unix
- 实时 Winsock / Windows 特定的回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

如果你为跨平台测试对 `sys.platform` 进行猴子补丁，也要补丁 `platform.system()` / `platform.release()` / `platform.mac_ver()` —— 每个函数都会独立地重新读取真实的操作系统，因此半补丁的测试在 Windows 运行器上仍然会走错分支。

---

## 安全注意事项

Hermes 具有终端访问权限。安全至关重要。

### 现有保护措施

| 层级 | 实现 |
|-------|---------------|
| **Sudo 密码管道** | 使用 `shlex.quote()` 防止 shell 注入 |
| **危险命令检测** | `tools/approval.py` 中的正则表达式模式，带有用户批准流程 |
| **定时任务提示词注入** | `tools/cronjob_tools.py` 中的扫描器会阻止指令覆盖模式 |
| **写入拒绝列表** | 受保护路径（`~/.ssh/authorized_keys`, `/etc/shadow`）通过 `os.path.realpath()` 解析，以防止符号链接绕过 |
| **技能防护** | 对 hub 安装的技能进行安全扫描（`tools/skills_guard.py`） |
| **代码执行沙盒** | `execute_code` 子进程运行时，环境变量中的 API 密钥已被剥离 |
| **容器加固** | Docker：所有能力被丢弃，无权限提升，PID 限制，大小受限的 tmpfs |

### 贡献安全敏感代码时

- 将用户输入插入 shell 命令时，**始终使用 `shlex.quote()`**
- 在进行基于路径的访问控制检查之前，**使用 `os.path.realpath()` 解析符号链接**
- **不要记录密钥。** API 密钥、Token 和密码不应出现在日志输出中
- 在工具执行周围**捕获宽泛的异常**，这样单个故障不会导致 Agent 循环崩溃
- 如果你的更改涉及文件路径、进程管理或 shell 命令，**在所有平台上进行测试**

如果你的 PR 影响安全性，请在描述中明确注明。

---

## 拉取请求流程

### 分支命名

```
fix/description        # 错误修复
feat/description       # 新功能
docs/description       # 文档
test/description       # 测试
refactor/description   # 代码重构
```

### 提交前

1.  **运行测试**：`scripts/run_tests.sh`（推荐；与 CI 相同）或在项目虚拟环境激活后运行 `pytest tests/ -v`
2.  **手动测试**：运行 `hermes` 并测试你更改的代码路径
3.  **检查跨平台影响**：如果你涉及文件 I/O、进程管理或终端处理，请考虑 macOS、Linux 和 WSL2
4.  **保持 PR 专注**：每个 PR 一个逻辑更改。不要将错误修复、重构和新功能混在一起。

### PR 描述

包括：
- **什么**改变了以及**为什么**
- **如何测试**它（针对错误的复现步骤，针对功能的使用示例）
- 你在**哪些平台**上进行了测试
- 引用任何相关的问题

### 提交信息

我们使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <description>
```

| 类型 | 用于 |
|------|---------|
| `fix` | 错误修复 |
| `feat` | 新功能 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 代码重构（无行为改变） |
| `chore` | 构建、CI、依赖项更新 |

范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security` 等。

示例：
```
fix(cli): 修复 save_config_value 中当模型为字符串时崩溃的问题
feat(gateway): 添加 WhatsApp 多用户会话隔离
fix(security): 防止 sudo 密码管道中的 shell 注入
test(tools): 为 file_operations 添加单元测试
```

---

## 报告问题

- 使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- 包括：操作系统、Python 版本、Hermes 版本（`hermes version`）、完整的错误回溯
- 包括复现步骤
- 创建问题前检查现有问题
- 对于安全漏洞，请私下报告

---
## 社区

- **Discord**: [discord.gg/NousResearch](https://discord.gg/NousResearch) — 用于提问、展示项目和分享技能
- **GitHub Discussions**: 用于设计提案和架构讨论
- **技能中心**: 将专业技能上传到注册表并与社区分享

---

## 许可证

通过贡献，您同意您的贡献将根据 [MIT 许可证](LICENSE) 进行许可。