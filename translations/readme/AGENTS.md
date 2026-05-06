# Hermes Agent - 开发指南

适用于在 hermes-agent 代码库上工作的 AI 编码助手和开发人员的说明。

## 开发环境

```bash
# 优先使用 .venv；如果您的检出目录使用的是 venv，则回退到 venv。
source .venv/bin/activate   # 或者：source venv/bin/activate
```

`scripts/run_tests.sh` 会首先探测 `.venv`，然后是 `venv`，接着是
`$HOME/.hermes/hermes-agent/venv`（用于与主检出目录共享虚拟环境的工作树）。

## 项目结构

文件数量不断变化——不要将下面的树状结构视为详尽无遗。
规范来源是文件系统。注释指出了您实际需要编辑的关键入口点。

```
hermes-agent/
├── run_agent.py          # AIAgent 类 — 核心对话循环（约 12k 行代码）
├── model_tools.py        # 工具编排，discover_builtin_tools()，handle_function_call()
├── toolsets.py           # 工具集定义，_HERMES_CORE_TOOLS 列表
├── cli.py                # HermesCLI 类 — 交互式 CLI 编排器（约 11k 行代码）
├── hermes_state.py       # SessionDB — SQLite 会话存储（FTS5 搜索）
├── hermes_constants.py   # get_hermes_home()，display_hermes_home() — 基于配置文件的路径
├── hermes_logging.py     # setup_logging() — agent.log / errors.log / gateway.log（基于配置文件）
├── batch_runner.py       # 并行批量处理
├── agent/                # Agent 内部组件（提供商适配器、记忆、缓存、压缩等）
├── hermes_cli/           # CLI 子命令、设置向导、插件加载器、皮肤引擎
├── tools/                # 工具实现 — 通过 tools/registry.py 自动发现
│   └── environments/     # 终端后端（本地、docker、ssh、modal、daytona、singularity）
├── gateway/              # 消息网关 — run.py + session.py + platforms/
│   ├── platforms/        # 每个平台的适配器（telegram、discord、slack、whatsapp、
│   │                     #   homeassistant、signal、matrix、mattermost、email、sms、
│   │                     #   dingtalk、wecom、weixin、feishu、qqbot、bluebubbles、
│   │                     #   yuanbao、webhook、api_server、...）。参见 ADDING_A_PLATFORM.md。
│   └── builtin_hooks/    # 始终注册的网关钩子的扩展点（默认不附带）
├── plugins/              # 插件系统（参见下面的“插件”部分）
│   ├── memory/           # 记忆提供者插件（honcho、mem0、supermemory、...）
│   ├── context_engine/   # 上下文引擎插件
│   ├── kanban/           # 多 Agent 看板调度器 + 工作器插件
│   ├── hermes-achievements/  # 游戏化成就追踪
│   ├── observability/    # 指标 / 追踪 / 日志插件
│   ├── image_gen/        # 图像生成提供商
│   └── <others>/         # disk-cleanup、example-dashboard、google_meet、platforms、
│                         #   spotify、strike-freedom-cockpit、...
├── optional-skills/      # 较重/小众的技能，随仓库附带但默认不激活
├── skills/               # 与仓库捆绑的内置技能
├── ui-tui/               # Ink (React) 终端 UI — `hermes --tui`
│   └── src/              # entry.tsx、app.tsx、gatewayClient.ts + app/components/hooks/lib
├── tui_gateway/          # TUI 的 Python JSON-RPC 后端
├── acp_adapter/          # ACP 服务器（VS Code / Zed / JetBrains 集成）
├── cron/                 # 调度器 — jobs.py、scheduler.py
├── environments/         # RL 训练环境（Atropos）
├── scripts/              # run_tests.sh、release.py、辅助脚本
├── website/              # Docusaurus 文档站点
└── tests/                # Pytest 测试套件（截至 2026 年 5 月，约 900 个文件，包含约 17k 个测试）
```

**用户配置：** `~/.hermes/config.yaml`（设置），`~/.hermes/.env`（仅 API 密钥）。
**日志：** `~/.hermes/logs/` — `agent.log`（INFO 及以上），`errors.log`（WARNING 及以上），
运行网关时生成 `gateway.log`。通过 `get_hermes_home()` 基于配置文件。
使用 `hermes logs [--follow] [--level ...] [--session ...]` 浏览。

## 文件依赖链

```
tools/registry.py  （无依赖 — 被所有工具文件导入）
       ↑
tools/*.py  （每个文件在导入时调用 registry.register()）
       ↑
model_tools.py  （导入 tools/registry + 触发工具发现）
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

---

## AIAgent 类 (run_agent.py)

真正的 `AIAgent.__init__` 接受约 60 个参数（凭证、路由、回调、
会话上下文、预算、凭证池等）。下面的签名是您通常需要处理的最小子集 —
请阅读 `run_agent.py` 以获取完整列表。

```python
class AIAgent:
    def __init__(self,
        base_url: str = None,
        api_key: str = None,
        provider: str = None,
        api_mode: str = None,              # "chat_completions" | "codex_responses" | ...
        model: str = "",                   # 空 → 稍后从配置/提供商解析
        max_iterations: int = 90,          # 工具调用迭代次数（与子 Agent 共享）
        enabled_toolsets: list = None,
        disabled_toolsets: list = None,
        quiet_mode: bool = False,
        save_trajectories: bool = False,
        platform: str = None,              # "cli", "telegram" 等
        session_id: str = None,
        skip_context_files: bool = False,
        skip_memory: bool = False,
        credential_pool=None,
        # ... 加上回调、线程/用户/聊天 ID、iteration_budget、fallback_model、
        # checkpoints 配置、prefill_messages、service_tier、reasoning_config 等。
    ): ...

    def chat(self, message: str) -> str:
        """简单接口 — 返回最终响应字符串。"""

    def run_conversation(self, user_message: str, system_message: str = None,
                         conversation_history: list = None, task_id: str = None) -> dict:
        """完整接口 — 返回包含 final_response + messages 的字典。"""
```

### Agent 循环

核心循环位于 `run_conversation()` 内部 — 完全同步，包含
中断检查、预算跟踪和一次容错调用：

```python
while (api_call_count < self.max_iterations and self.iteration_budget.remaining > 0) \
        or self._budget_grace_call:
    if self._interrupt_requested: break
    response = client.chat.completions.create(model=model, messages=messages, tools=tool_schemas)
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = handle_function_call(tool_call.name, tool_call.args, task_id)
            messages.append(tool_result_message(result))
        api_call_count += 1
    else:
        return response.content
```
消息遵循 OpenAI 格式：`{"role": "system/user/assistant/tool", ...}`。
推理内容存储在 `assistant_msg["reasoning"]` 中。

---

## CLI 架构 (cli.py)

- **Rich** 用于横幅/面板，**prompt_toolkit** 用于带自动补全的输入
- **KawaiiSpinner** (`agent/display.py`) — API 调用期间的动画表情，`┊` 活动流用于显示工具结果
- `load_cli_config()` 在 cli.py 中合并硬编码的默认值 + 用户配置 YAML
- **皮肤引擎** (`hermes_cli/skin_engine.py`) — 数据驱动的 CLI 主题；启动时从 `display.skin` 配置键初始化；皮肤可自定义横幅颜色、spinner 表情/动词/翅膀、工具前缀、响应框、品牌文本
- `process_command()` 是 `HermesCLI` 上的一个方法 — 根据通过中央注册表 `resolve_command()` 解析出的规范命令名进行分发
- 技能斜杠命令：`agent/skill_commands.py` 扫描 `~/.hermes/skills/`，将其作为**用户消息**（而非系统提示词）注入，以保留提示词缓存

### 斜杠命令注册表 (`hermes_cli/commands.py`)

所有斜杠命令都在一个中央的 `COMMAND_REGISTRY` `CommandDef` 对象列表中定义。所有下游消费者都自动从此注册表派生：

- **CLI** — `process_command()` 通过 `resolve_command()` 解析别名，根据规范名进行分发
- **消息网关** — `GATEWAY_KNOWN_COMMANDS` frozenset 用于钩子触发，`resolve_command()` 用于分发
- **消息网关帮助** — `gateway_help_lines()` 生成 `/help` 输出
- **Telegram** — `telegram_bot_commands()` 生成 BotCommand 菜单
- **Slack** — `slack_subcommand_map()` 生成 `/hermes` 子命令路由
- **自动补全** — `COMMANDS` 平面字典提供给 `SlashCommandCompleter`
- **CLI 帮助** — `COMMANDS_BY_CATEGORY` 字典提供给 `show_help()`

### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加一个 `CommandDef` 条目：
```python
CommandDef("mycommand", "Description of what it does", "Session",
           aliases=("mc",), args_hint="[arg]"),
```
2. 在 `cli.py` 的 `HermesCLI.process_command()` 中添加处理程序：
```python
elif canonical == "mycommand":
    self._handle_mycommand(cmd_original)
```
3. 如果该命令在消息网关中可用，请在 `gateway/run.py` 中添加处理程序：
```python
if canonical == "mycommand":
    return await self._handle_mycommand(event)
```
4. 对于持久化设置，使用 `cli.py` 中的 `save_config_value()`

**CommandDef 字段：**
- `name` — 不带斜杠的规范名称（例如 `"background"`）
- `description` — 人类可读的描述
- `category` — 取值为 `"Session"`、`"Configuration"`、`"Tools & Skills"`、`"Info"`、`"Exit"` 之一
- `aliases` — 替代名称的元组（例如 `("bg",)`）
- `args_hint` — 帮助中显示的参数占位符（例如 `"<prompt>"`、`"[name]"`）
- `cli_only` — 仅在交互式 CLI 中可用
- `gateway_only` — 仅在消息平台中可用
- `gateway_config_gate` — 配置点路径（例如 `"display.tool_progress_command"`）；当在 `cli_only` 命令上设置时，如果配置值为真，则该命令在消息网关中变为可用。`GATEWAY_KNOWN_COMMANDS` 始终包含配置门控命令，以便消息网关可以分发它们；帮助/菜单仅在门打开时显示它们。

**添加别名** 只需将其添加到现有 `CommandDef` 的 `aliases` 元组中。无需更改其他文件 — 分发、帮助文本、Telegram 菜单、Slack 映射和自动补全都会自动更新。

---

## TUI 架构 (ui-tui + tui_gateway)

TUI 是经典 (prompt_toolkit) CLI 的完全替代品，通过 `hermes --tui` 或 `HERMES_TUI=1` 激活。

### 进程模型

```
hermes --tui
  └─ Node (Ink)  ──stdio JSON-RPC──  Python (tui_gateway)
       │                                  └─ AIAgent + tools + sessions
       └─ 渲染转录、编辑器、提示、活动
```

TypeScript 控制屏幕。Python 控制会话、工具、模型调用和斜杠命令逻辑。

### 传输

通过 stdio 进行换行分隔的 JSON-RPC。请求来自 Ink，事件来自 Python。完整的方法/事件目录请参见 `tui_gateway/server.py`。

### 关键界面

| 界面 | Ink 组件 | 消息网关方法 |
|---------|---------------|----------------|
| 聊天流式传输 | `app.tsx` + `messageLine.tsx` | `prompt.submit` → `message.delta/complete` |
| 工具活动 | `thinking.tsx` | `tool.start/progress/complete` |
| 审批 | `prompts.tsx` | `approval.respond` ← `approval.request` |
| 澄清/sudo/秘密 | `prompts.tsx`, `maskedPrompt.tsx` | `clarify/sudo/secret.respond` |
| 会话选择器 | `sessionPicker.tsx` | `session.list/resume` |
| 斜杠命令 | 本地处理程序 + 回退 | `slash.exec` → `_SlashWorker`, `command.dispatch` |
| 补全 | `useCompletion` 钩子 | `complete.slash`, `complete.path` |
| 主题 | `theme.ts` + `branding.tsx` | `gateway.ready` 附带皮肤数据 |

### 斜杠命令流程

1. 内置客户端命令（`/help`、`/quit`、`/clear`、`/resume`、`/copy`、`/paste` 等）在 `app.tsx` 中本地处理
2. 其他所有命令 → `slash.exec`（在持久的 `_SlashWorker` 子进程中运行）→ `command.dispatch` 回退

### 开发命令

```bash
cd ui-tui
npm install       # 首次运行
npm run dev       # 监视模式（重新构建 hermes-ink + tsx --watch）
npm start         # 生产环境
npm run build     # 完整构建（hermes-ink + tsc）
npm run type-check # 仅类型检查（tsc --noEmit）
npm run lint      # eslint
npm run fmt       # prettier
npm test          # vitest
```

### 仪表板中的 TUI (`hermes dashboard` → `/chat`)

仪表板嵌入的是真实的 `hermes --tui` — **不是**重写。请参见 `hermes_cli/pty_bridge.py` + `hermes_cli/web_server.py` 中的 `@app.websocket("/api/pty")` 端点。

- 浏览器加载 `web/src/pages/ChatPage.tsx`，该文件挂载 xterm.js 的 `Terminal`，使用 WebGL 渲染器、`@xterm/addon-fit` 用于容器驱动的调整大小，以及 `@xterm/addon-unicode11` 用于现代宽字符宽度。
- `/api/pty?token=…` 升级为 WebSocket；身份验证使用与 REST 相同的临时 `_SESSION_TOKEN`，通过查询参数传递（浏览器无法在 WS 升级时设置 `Authorization`）。
- 服务器通过 `ptyprocess`（POSIX PTY — WSL 可用，原生 Windows 不可用）生成 `hermes --tui` 会生成的任何内容。
- 帧：双向原始 PTY 字节；通过 `\x1b[RESIZE:<cols>;<rows>]` 调整大小，在服务器端拦截并使用 `TIOCSWINSZ` 应用。
**不要在 React 中重新实现主要的聊天体验。** 主要的对话记录、输入/编辑器流程（包括斜杠命令行为）以及基于 PTY 的终端都属于嵌入式 `hermes --tui` —— 你在 Ink 中添加的任何新内容都会自动显示在仪表板中。如果你发现自己正在为仪表板重建对话记录或编辑器，请停止并转而扩展 Ink。

**围绕 TUI 构建结构化的 React UI 是允许的，只要它不是第二个聊天界面。** 侧边栏小部件、检查器、摘要、状态面板以及类似的辅助视图（例如 `ChatSidebar`、`ModelPickerDialog`、`ToolCall`）是可以的，只要它们是对嵌入式 TUI 的补充，而不是取代对话记录/编辑器/终端。保持它们的状态独立于 PTY 子进程的会话，并以非破坏性的方式呈现它们的故障，以便终端窗格继续正常工作。

---

## 添加新工具

对于大多数自定义或仅限本地的工具，**不要**编辑 Hermes 核心。请改用插件方式：创建 `~/.hermes/plugins/<name>/plugin.yaml` 和 `~/.hermes/plugins/<name>/__init__.py`，然后使用 `ctx.register_tool(...)` 注册工具。插件工具集会被自动发现，并且可以在不接触 `tools/` 或 `toolsets.py` 的情况下启用或禁用。

仅当用户明确贡献一个应该包含在基础系统中的新核心 Hermes 工具时，才使用下面内置的方式。

内置/核心工具需要在 **2 个文件** 中进行更改：

**1. 创建 `tools/your_tool.py`：**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. 添加到 `toolsets.py`** —— 可以是 `_HERMES_CORE_TOOLS`（所有平台）或一个新的工具集。**此步骤是必需的：** 自动发现会导入工具并注册其模式，但只有工具名称出现在某个工具集中时，它才会*暴露给 Agent*。`_HERMES_CORE_TOOLS` 不是死代码 —— 它是每个平台基础工具集默认继承的捆绑包。

自动发现：任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入 —— 无需维护手动导入列表。但将其接入一个工具集仍然是一个有意的、手动的步骤。

注册表处理模式收集、分发、可用性检查和错误包装。所有处理程序**必须**返回一个 JSON 字符串。

**工具模式中的路径引用**：如果模式描述中提到文件路径（例如默认输出目录），请使用 `display_hermes_home()` 使其感知配置文件。模式在导入时生成，这是在 `_apply_profile_override()` 设置 `HERMES_HOME` 之后。

**状态文件**：如果工具存储持久状态（缓存、日志、检查点），请使用 `get_hermes_home()` 作为基础目录 —— 永远不要使用 `Path.home() / ".hermes"`。这确保每个配置文件都有自己的状态。

**Agent 级工具**（todo, memory）：在 `handle_function_call()` 之前被 `run_agent.py` 拦截。请参阅 `tools/todo_tool.py` 了解模式。

---

## 添加配置

### config.yaml 选项：
1. 添加到 `hermes_cli/config.py` 中的 `DEFAULT_CONFIG`
2. 增加 `_config_version`（在 `DEFAULT_CONFIG` 顶部检查当前值）
   **仅当**你需要主动迁移/转换现有用户配置（重命名键、更改结构）时才需要这样做。向现有部分添加新键由深度合并自动处理，**不需要**增加版本号。

### 顶级 `config.yaml` 部分（非详尽）：

`model`, `agent`, `terminal`, `compression`, `display`, `stt`, `tts`,
`memory`, `security`, `delegation`, `smart_model_routing`, `checkpoints`,
`auxiliary`, `curator`, `skills`, `gateway`, `logging`, `cron`, `profiles`,
`plugins`, `honcho`.

`auxiliary` 包含用于辅助 LLM 工作的每任务覆盖（curator, vision,
embedding, title generation, session_search 等）—— 每个任务可以固定其自己的
provider/model/base_url/max_tokens/reasoning_effort。请参阅
`agent/auxiliary_client.py::_resolve_auto` 了解解析顺序。

`curator` 包含后台技能维护配置 ——
`enabled`, `interval_hours`, `min_idle_hours`, `stale_after_days`,
`archive_after_days`, `backup`（嵌套）。

### .env 变量（**仅限机密** —— API 密钥、Token、密码）：
1. 添加到 `hermes_cli/config.py` 中的 `OPTIONAL_ENV_VARS`，并附带元数据：
```python
"NEW_API_KEY": {
    "description": "用途说明",
    "prompt": "显示名称",
    "url": "https://...",
    "password": True,
    "category": "tool",  # provider, tool, messaging, setting
},
```

非机密设置（超时、阈值、功能标志、路径、显示偏好）属于 `config.yaml`，而不是 `.env`。如果内部代码为了向后兼容性需要一个环境变量镜像，请在代码中从 `config.yaml` 桥接到环境变量（参见 `gateway_timeout`, `terminal.cwd` → `TERMINAL_CWD`）。

### 配置加载器（三条路径 —— 了解你正在使用哪一条）：

| 加载器 | 使用者 | 位置 |
|--------|---------|----------|
| `load_cli_config()` | CLI 模式 | `cli.py` —— 合并 CLI 特定的默认值 + 用户 YAML |
| `load_config()` | `hermes tools`, `hermes setup`, 大多数 CLI 子命令 | `hermes_cli/config.py` —— 合并 `DEFAULT_CONFIG` + 用户 YAML |
| 直接 YAML 加载 | 消息网关运行时 | `gateway/run.py` + `gateway/config.py` —— 原始读取用户 YAML |

如果你添加了一个新键，CLI 能看到它但消息网关不能（反之亦然），说明你使用了错误的加载器。检查 `DEFAULT_CONFIG` 的覆盖范围。

### 工作目录：
- **CLI** —— 使用进程的当前目录 (`os.getcwd()`)。
- **消息传递** —— 使用 `config.yaml` 中的 `terminal.cwd`。消息网关将其桥接到 `TERMINAL_CWD` 环境变量供子工具使用。**`MESSAGING_CWD` 已被移除** —— 如果它在 `.env` 中设置，配置加载器会打印弃用警告。`.env` 中的 `TERMINAL_CWD` 同理；规范设置是 `config.yaml` 中的 `terminal.cwd`。
---

## 皮肤/主题系统

皮肤引擎 (`hermes_cli/skin_engine.py`) 提供了数据驱动的 CLI 视觉自定义功能。皮肤是**纯数据**——添加新皮肤无需更改代码。

### 架构

```
hermes_cli/skin_engine.py    # SkinConfig 数据类、内置皮肤、YAML 加载器
~/.hermes/skins/*.yaml       # 用户安装的自定义皮肤（即放即用）
```

- `init_skin_from_config()` — 在 CLI 启动时调用，从配置中读取 `display.skin`
- `get_active_skin()` — 返回当前皮肤的缓存 `SkinConfig`
- `set_active_skin(name)` — 在运行时切换皮肤（由 `/skin` 命令使用）
- `load_skin(name)` — 首先从用户皮肤加载，然后是内置皮肤，最后回退到默认皮肤
- 缺失的皮肤值会自动从 `default` 皮肤继承

### 皮肤可自定义的内容

| 元素 | 皮肤键 | 使用者 |
|---------|----------|---------|
| 横幅面板边框 | `colors.banner_border` | `banner.py` |
| 横幅面板标题 | `colors.banner_title` | `banner.py` |
| 横幅部分标题 | `colors.banner_accent` | `banner.py` |
| 横幅暗淡文本 | `colors.banner_dim` | `banner.py` |
| 横幅正文文本 | `colors.banner_text` | `banner.py` |
| 响应框边框 | `colors.response_border` | `cli.py` |
| 旋转器表情（等待中） | `spinner.waiting_faces` | `display.py` |
| 旋转器表情（思考中） | `spinner.thinking_faces` | `display.py` |
| 旋转器动词 | `spinner.thinking_verbs` | `display.py` |
| 旋转器翅膀（可选） | `spinner.wings` | `display.py` |
| 工具输出前缀 | `tool_prefix` | `display.py` |
| 每个工具的 Emoji | `tool_emojis` | `display.py` → `get_tool_emoji()` |
| Agent 名称 | `branding.agent_name` | `banner.py`, `cli.py` |
| 欢迎信息 | `branding.welcome` | `cli.py` |
| 响应框标签 | `branding.response_label` | `cli.py` |
| 提示符符号 | `branding.prompt_symbol` | `cli.py` |

### 内置皮肤

- `default` — 经典的 Hermes 金色/可爱风格（当前外观）
- `ares` — 深红/青铜色的战神主题，带有自定义旋转器翅膀
- `mono` — 简洁的灰度单色主题
- `slate` — 以开发者为中心的酷炫蓝色主题

### 添加内置皮肤

添加到 `hermes_cli/skin_engine.py` 中的 `_BUILTIN_SKINS` 字典：

```python
"mytheme": {
    "name": "mytheme",
    "description": "简短描述",
    "colors": { ... },
    "spinner": { ... },
    "branding": { ... },
    "tool_prefix": "┊",
},
```

### 用户皮肤 (YAML)

用户创建 `~/.hermes/skins/<name>.yaml`：

```yaml
name: cyberpunk
description: 霓虹浸染的终端主题

colors:
  banner_border: "#FF00FF"
  banner_title: "#00FFFF"
  banner_accent: "#FF1493"

spinner:
  thinking_verbs: ["jacking in", "decrypting", "uploading"]
  wings:
    - ["⟨⚡", "⚡⟩"]

branding:
  agent_name: "Cyber Agent"
  response_label: " ⚡ Cyber "

tool_prefix: "▏"
```

通过 `/skin cyberpunk` 或在 config.yaml 中设置 `display.skin: cyberpunk` 来激活。

---

## 插件

Hermes 有两个插件接口。两者都位于仓库的 `plugins/` 目录下，这样仓库自带的插件可以与用户安装在 `~/.hermes/plugins/` 下的插件以及通过 pip 安装的入口点一起被发现。

### 通用插件 (`hermes_cli/plugins.py` + `plugins/<name>/`)

`PluginManager` 从 `~/.hermes/plugins/`、`./.hermes/plugins/` 和 pip 入口点发现插件。每个插件暴露一个 `register(ctx)` 函数，该函数可以：

- 注册 Python 回调的生命周期钩子：
  `pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`,
  `on_session_start`, `on_session_end`
- 通过 `ctx.register_tool(...)` 注册新工具
- 通过 `ctx.register_cli_command(...)` 注册 CLI 子命令——插件的 argparse 树在启动时连接到 `hermes`，因此 `hermes <pluginname> <subcmd>` 无需更改 `main.py` 即可工作

钩子从 `model_tools.py`（工具调用前/后）和 `run_agent.py`（生命周期）调用。**发现时机陷阱：** `discover_plugins()` 仅在导入 `model_tools.py` 时作为副作用运行。在导入 `model_tools.py` 之前读取插件状态的代码路径必须显式调用 `discover_plugins()`（它是幂等的）。

### 记忆提供者插件 (`plugins/memory/<name>/`)

用于可插拔记忆后端的独立发现系统。当前内置的提供者包括 **honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb**。

每个提供者都实现了 `MemoryProvider` ABC（参见 `agent/memory_provider.py`），并由 `agent/memory_manager.py` 编排。生命周期钩子包括 `sync_turn(turn_messages)`, `prefetch(query)`, `shutdown()`，以及可选的 `post_setup(hermes_home, config)` 用于设置向导集成。

**通过 `plugins/memory/<name>/cli.py` 的 CLI 命令：** 如果记忆插件定义了 `register_cli(subparser)`，`discover_plugin_cli_commands()` 会在 argparse 设置时找到它，并将其连接到 `hermes <plugin>`。该框架仅暴露**当前激活的**记忆提供者的 CLI 命令（从 config.yaml 中的 `memory.provider` 读取），因此禁用的提供者不会使 `hermes --help` 变得杂乱。

**规则 (Teknium, 2026年5月)：** 插件**不得**修改核心文件（`run_agent.py`, `cli.py`, `gateway/run.py`, `hermes_cli/main.py` 等）。如果插件需要框架未暴露的功能，应扩展通用插件接口（新钩子、新的 ctx 方法）——切勿将插件特定逻辑硬编码到核心中。PR #5295 正是因此移除了 `main.py` 中 95 行硬编码的 honcho argparse 代码。

### Dashboard / context-engine / image-gen 插件目录

`plugins/context_engine/`, `plugins/image_gen/`, `plugins/example-dashboard/` 等遵循相同的模式（ABC + 编排器 + 每个插件的目录）。上下文引擎插件接入 `agent/context_engine.py`；图像生成提供者接入 `agent/image_gen_provider.py`。

---

## 技能

两个平行的接口：

- **`skills/`** — 内置技能，默认随包提供并可加载。按类别目录组织（例如 `skills/github/`, `skills/mlops/`）。
- **`optional-skills/`** — 较重或小众的技能，随仓库提供但**默认不激活**。通过 `hermes skills install official/<category>/<skill>` 显式安装。适配器位于 `tools/skills_hub.py`（`OptionalSkillSource`）。类别包括 `autonomous-ai-agents`, `blockchain`, `communication`, `creative`, `devops`, `email`, `health`, `mcp`, `migration`, `mlops`, `productivity`, `research`, `security`, `web-development`。
在审查技能 PR 时，请检查它们的目标目录——依赖重或小众的技能应放在 `optional-skills/` 目录下。

### SKILL.md 的 frontmatter

标准字段：`name`、`description`、`version`、`author`、`license`、`platforms`（操作系统限定列表：`[macos]`、`[linux, macos]`、...）、`metadata.hermes.tags`、`metadata.hermes.category`、`metadata.hermes.related_skills`、`metadata.hermes.config`（技能所需的 config.yaml 设置——存储在 `skills.config.<key>` 下，在设置期间提示，在加载时注入）。

顶层的 `tags:` 和 `category:` 也被接受，并由加载器从 `metadata.hermes.*` 镜像。

---

## 工具集

所有工具集都在 `toolsets.py` 中定义为单个 `TOOLSETS` 字典。
每个平台的适配器选择一个基础工具集（例如 Telegram 使用 `"messaging"`）；`_HERMES_CORE_TOOLS` 是大多数平台继承的默认捆绑包。

当前工具集键：`browser`、`clarify`、`code_execution`、`cronjob`、`debugging`、`delegation`、`discord`、`discord_admin`、`feishu_doc`、`feishu_drive`、`file`、`homeassistant`、`image_gen`、`kanban`、`memory`、`messaging`、`moa`、`rl`、`safe`、`search`、`session_search`、`skills`、`spotify`、`terminal`、`todo`、`tts`、`video`、`vision`、`web`、`yuanbao`。

可以通过 `hermes tools`（curses UI）或 `config.yaml` 中的 `tools.<platform>.enabled` / `tools.<platform>.disabled` 列表来按平台启用/禁用。

---

## 委派 (`delegate_task`)

`tools/delegate_tool.py` 生成一个具有隔离上下文 + 终端会话的子 Agent。同步：父 Agent 等待子 Agent 的摘要后再继续自己的循环——如果父 Agent 被中断，子 Agent 将被取消。

两种形式：

- **单任务：** 传递 `goal`（+ 可选的 `context`、`toolsets`）。
- **批量（并行）：** 传递 `tasks: [...]` —— 每个任务都有自己的子 Agent 并发运行。并发数受 `delegation.max_concurrent_children` 限制（默认 3）。

角色：

- `role="leaf"`（默认）—— 专注的工作者。不能调用 `delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`。
- `role="orchestrator"` —— 保留 `delegate_task` 以便可以生成自己的工作者。受 `delegation.orchestrator_enabled`（默认 true）限制，并受 `delegation.max_spawn_depth`（默认 2）限制。

关键配置旋钮（在 `config.yaml` 的 `delegation:` 下）：
`max_concurrent_children`、`max_spawn_depth`、`child_timeout_seconds`、`orchestrator_enabled`、`subagent_auto_approve`、`inherit_mcp_toolsets`、`max_iterations`。

同步性规则：delegate_task **不是** 持久性的。对于必须比当前轮次存活更长时间的长时间运行工作，请改用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

---

## 策展器（技能生命周期）

后台技能维护系统，用于跟踪 Agent 创建技能的使用情况，并自动归档过时的技能。用户永远不会丢失技能；归档的技能会移动到 `~/.hermes/skills/.archive/` 并可恢复。

- **核心：** `agent/curator.py`（审查循环、自动转换、LLM 审查提示词）+ `agent/curator_backup.py`（运行前 tar.gz 快照）。
- **CLI：** `hermes_cli/curator.py` 连接 `hermes curator <verb>`，其中动词有：`status`、`run`、`pause`、`resume`、`pin`、`unpin`、`archive`、`restore`、`prune`、`backup`、`rollback`。
- **遥测：** `tools/skill_usage.py` 拥有侧车 `~/.hermes/skills/.usage.json` —— 每个技能的 `use_count`、`view_count`、`patch_count`、`last_activity_at`、`state`（活跃 / 过时 / 已归档）、`pinned`。

不变式：
- 策展器只处理具有 `created_by: "agent"` 来源的技能 —— 捆绑 + 从 hub 安装的技能是禁止操作的。
- 从不删除；最大的破坏性操作是归档。
- 已固定的技能免于所有自动转换和 LLM 审查过程。
- `skill_manage(action="delete")` 拒绝已固定的技能；补丁/编辑/写入文件/删除文件操作可以通过，以便 Agent 可以继续改进已固定的技能。

配置部分（`config.yaml` 中的 `curator:`）：
`enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、`archive_after_days`、`backup.*`。

完整的面向用户的文档：`website/docs/user-guide/features/curator.md`。

---

## 定时任务（计划作业）

`cron/jobs.py`（作业存储）+ `cron/scheduler.py`（滴答循环）。Agent 通过 `cronjob` 工具安排作业；用户通过 `hermes cron <verb>`（`list`、`add`、`edit`、`pause`、`resume`、`run`、`remove`）或 `/cron` 斜杠命令。

支持的调度格式：
- 持续时间：`"30m"`、`"2h"`、`"1d"`
- "every" 短语：`"every 2h"`、`"every monday 9am"`
- 5 字段 cron 表达式：`"0 9 * * *"`
- ISO 时间戳（一次性）：`"2026-06-01T09:00:00Z"`

每个作业的字段包括 `skills`（加载特定技能）、`model` / `provider` 覆盖、`script`（运行前数据收集脚本，其标准输出被注入到提示词中；`no_agent=True` 将脚本转换为整个作业）、`context_from`（将作业 A 的最后输出链接到作业 B 的提示词中）、`workdir`（在特定目录中运行并加载其 `AGENTS.md`/`CLAUDE.md`）以及多平台交付。

强化不变式：
- 定时任务会话有 **3 分钟硬中断** —— 失控的 Agent 循环不能独占调度器。
- 追赶窗口：作业周期的一半，限制在 120 秒到 2 小时之间。
- 宽限窗口：对于错过触发时间的一次性作业，有 120 秒。
- `~/.hermes/cron/.tick.lock` 处的文件锁可防止跨进程的重复滴答。
- 定时任务会话默认传递 `skip_memory=True`；记忆提供商在定时任务期间故意不运行。

定时任务交付 **不会** 镜像到目标消息网关会话中 —— 它们会落在自己的定时任务会话中，带有页眉/页脚框架，以便主对话的消息角色交替保持完整。

---

## 看板（多 Agent 工作队列）

基于 SQLite 的持久化看板，允许多个配置文件 / 工作者在共享任务上协作。用户通过 `hermes kanban <verb>` 驱动它；由调度器生成的工作者通过专用的 `kanban_*` 工具集驱动它，这样当它们不在看板任务内时，其模式占用为零。

- **CLI：** `hermes_cli/kanban.py` 连接 `hermes kanban`，动词有 `init`、`create`、`list`（别名 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`，以及较少使用的 `watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-*`、`dispatch`、`daemon`、`gc`。
- **工作者工具集：** `tools/kanban_tools.py` 暴露 `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link` —— 受 `HERMES_KANBAN_TASK` 控制，因此该模式仅出现在实际作为工作者运行的进程中。
- **调度器：** 长期运行的循环，默认每 60 秒回收过时的认领、提升就绪任务、原子性地认领并生成分配的配置文件。默认通过 `kanban.dispatch_in_gateway: true` **在消息网关内部** 运行。
- **插件资源：** `plugins/kanban/dashboard/`（Web UI）+ `plugins/kanban/systemd/`（`hermes-kanban-dispatcher.service` 用于独立调度器部署）。
隔离模型：
- **看板**是硬边界 — 工作进程在启动时会固定设置 `HERMES_KANBAN_BOARD` 环境变量，因此它们无法看到其他看板。
- **租户**是看板*内部*的软命名空间 — 一个专家舰队可以通过工作空间路径 + 记忆键隔离为多个业务提供服务。
- 在同一任务上连续约 5 次启动失败后，调度器会自动阻止该任务，以防止循环自旋。

完整的面向用户文档：`website/docs/user-guide/features/kanban.md`。

---

## 重要策略

### 提示词缓存必须不被破坏

Hermes-Agent 确保缓存在整个会话期间保持有效。**请勿实施会导致以下情况的更改：**
- 在会话中途更改过去的上下文
- 在会话中途更改工具集
- 在会话中途重新加载记忆或重建系统提示词

破坏缓存会导致成本急剧增加。我们更改上下文的**唯一**时机是在上下文压缩期间。

会改变系统提示词状态（技能、工具、记忆等）的斜杠命令必须是**缓存感知的**：默认采用延迟失效（更改在下一次会话生效），并提供一个可选的 `--now` 标志用于立即失效。请参阅 `/skills install --now` 作为规范模式。

### 后台进程通知（消息网关）

当使用 `terminal(background=true, notify_on_complete=true)` 时，消息网关会运行一个监视器来检测进程完成情况并触发新的 Agent 轮次。通过 `config.yaml` 中的 `display.background_process_notifications`（或 `HERMES_BACKGROUND_NOTIFICATIONS` 环境变量）控制后台进程消息的详细程度：

- `all` — 运行输出更新 + 最终消息（默认）
- `result` — 仅最终完成消息
- `error` — 仅当退出代码 != 0 时的最终消息
- `off` — 完全不显示监视器消息

---

## 配置文件：多实例支持

Hermes 支持**配置文件** — 多个完全隔离的实例，每个实例都有自己的 `HERMES_HOME` 目录（配置、API 密钥、记忆、会话、技能、消息网关等）。

核心机制：`hermes_cli/main.py` 中的 `_apply_profile_override()` 在任何模块导入之前设置 `HERMES_HOME`。所有 `get_hermes_home()` 引用都会自动限定到活动配置文件的范围。

### 配置文件安全代码规则

1.  **对所有 HERMES_HOME 路径使用 `get_hermes_home()`。** 从 `hermes_constants` 导入。在读取/写入状态的代码中**绝对不要**硬编码 `~/.hermes` 或 `Path.home() / ".hermes"`。
    ```python
    # 正确
    from hermes_constants import get_hermes_home
    config_path = get_hermes_home() / "config.yaml"

    # 错误 — 破坏配置文件
    config_path = Path.home() / ".hermes" / "config.yaml"
    ```

2.  **对面向用户的消息使用 `display_hermes_home()`。** 从 `hermes_constants` 导入。对于默认配置文件，它返回 `~/.hermes`；对于其他配置文件，它返回 `~/.hermes/profiles/<name>`。
    ```python
    # 正确
    from hermes_constants import display_hermes_home
    print(f"配置已保存到 {display_hermes_home()}/config.yaml")

    # 错误 — 对配置文件显示错误的路径
    print("配置已保存到 ~/.hermes/config.yaml")
    ```

3.  **模块级常量没问题** — 它们在导入时缓存 `get_hermes_home()`，这是在 `_apply_profile_override()` 设置环境变量**之后**。只需使用 `get_hermes_home()`，而不是 `Path.home() / ".hermes"`。

4.  **模拟 `Path.home()` 的测试也必须设置 `HERMES_HOME`** — 因为代码现在使用 `get_hermes_home()`（读取环境变量），而不是 `Path.home() / ".hermes"`：
    ```python
    with patch.object(Path, "home", return_value=tmp_path), \
         patch.dict(os.environ, {"HERMES_HOME": str(tmp_path / ".hermes")}):
        ...
    ```

5.  **消息网关平台适配器应使用 Token 锁** — 如果适配器使用唯一凭据（机器人 Token、API 密钥）连接，请在 `connect()`/`start()` 方法中调用 `gateway.status` 中的 `acquire_scoped_lock()`，并在 `disconnect()`/`stop()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件使用相同的凭据。请参阅 `gateway/platforms/telegram.py` 作为规范模式。

6.  **配置文件操作是基于 HOME 锚定的，而不是基于 HERMES_HOME 锚定的** — `_get_profiles_root()` 返回 `Path.home() / ".hermes" / "profiles"`，**而不是** `get_hermes_home() / "profiles"`。这是有意为之 — 它允许 `hermes -p coder profile list` 查看所有配置文件，无论哪个配置文件处于活动状态。

## 已知陷阱

### 请勿硬编码 `~/.hermes` 路径
对于代码路径，请使用 `hermes_constants` 中的 `get_hermes_home()`。对于面向用户的打印/日志消息，请使用 `display_hermes_home()`。硬编码 `~/.hermes` 会破坏配置文件 — 每个配置文件都有自己的 `HERMES_HOME` 目录。这是在 PR #3575 中修复的 5 个错误的根源。

### 请勿引入新的 `simple_term_menu` 用法
`hermes_cli/main.py` 中现有的调用点仅作为旧版回退保留；首选的 UI 是 curses（标准库），因为 `simple_term_menu` 在 tmux/iTerm2 中使用箭头键时存在幽灵重复渲染错误。新的交互式菜单必须使用 `hermes_cli/curses_ui.py` — 请参阅 `hermes_cli/tools_config.py` 作为规范模式。

### 请勿在 spinner/display 代码中使用 `\033[K`（ANSI 清除到行尾）
在 `prompt_toolkit` 的 `patch_stdout` 下会泄漏为字面文本 `?[K`。请使用空格填充：`f"\r{line}{' ' * pad}"`。

### `_last_resolved_tool_names` 是 `model_tools.py` 中的一个进程全局变量
`delegate_tool.py` 中的 `_run_single_child()` 在子 Agent 执行期间保存和恢复此全局变量。如果您添加读取此全局变量的新代码，请注意它在子 Agent 运行期间可能暂时是过时的。

### 请勿在模式描述中硬编码跨工具引用
工具模式描述不得按名称提及来自其他工具集的工具（例如，`browser_navigate` 说“首选 web_search”）。这些工具可能不可用（缺少 API 密钥、工具集被禁用），导致模型幻觉调用不存在的工具。如果需要交叉引用，请在 `model_tools.py` 的 `get_tool_definitions()` 中动态添加 — 请参阅 `browser_navigate` / `execute_code` 后处理块的模式。

### 消息网关有**两个**消息守卫 — 两者都必须绕过审批/控制命令
当 Agent 正在运行时，消息会依次通过两个守卫：
(1) **基础适配器** (`gateway/platforms/base.py`) 在 `session_key in self._active_sessions` 时将消息排队到 `_pending_messages` 中，以及
(2) **消息网关运行器** (`gateway/run.py`) 在消息到达 `running_agent.interrupt()` 之前拦截 `/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`。
任何在 Agent 被阻塞时必须到达运行器的新命令（例如审批提示）**必须**绕过**两个**守卫，并内联分发，而不是通过 `_process_message_background()`（这会与会话生命周期产生竞争）。
### 压缩合并陈旧分支会静默回滚近期修复
在压缩合并 PR 前，确保分支已与 `main` 同步（在工作区中执行 `git fetch origin main && git reset --hard origin/main`，然后重新应用 PR 的提交）。压缩合并时，陈旧分支中不相关文件的版本会静默覆盖 `main` 分支上的近期修复。合并后使用 `git diff HEAD~1..HEAD` 验证——意外的删除是危险信号。

### 未经端到端验证，不要接入死代码
从未发布的未使用代码之所以成为死代码，是有原因的。在将未使用的模块接入活动代码路径之前，应使用临时 `HERMES_HOME` 目录，通过实际导入（而非模拟）对真实的解析链进行端到端测试。

### 测试不得写入 `~/.hermes/`
`tests/conftest.py` 中的 `_isolate_hermes_home` 自动使用夹具会将 `HERMES_HOME` 重定向到临时目录。切勿在测试中硬编码 `~/.hermes/` 路径。

**配置文件测试**：测试配置文件功能时，还需模拟 `Path.home()`，以便 `_get_profiles_root()` 和 `_get_default_hermes_home()` 在临时目录内解析。使用 `tests/hermes_cli/test_profiles.py` 中的模式：
```python
@pytest.fixture
def profile_env(tmp_path, monkeypatch):
    home = tmp_path / ".hermes"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("HERMES_HOME", str(home))
    return home
```

---

## 测试

**务必使用 `scripts/run_tests.sh`** —— 不要直接调用 `pytest`。该脚本强制执行与 CI 一致的无干扰环境（取消设置凭据变量、TZ=UTC、LANG=C.UTF-8、4 个 xdist 工作进程以匹配 GHA ubuntu-latest）。在设置了 API 密钥的 16+ 核开发机器上直接运行 `pytest`，会导致与 CI 环境产生差异，这已多次引发“本地通过，CI 失败”（反之亦然）的事件。

```bash
scripts/run_tests.sh                                  # 完整测试套件，与 CI 一致
scripts/run_tests.sh tests/gateway/                   # 单个目录
scripts/run_tests.sh tests/agent/test_foo.py::test_x  # 单个测试
scripts/run_tests.sh -v --tb=long                     # 透传 pytest 标志
```

### 为什么需要包装脚本（以及为什么旧的“直接调用 pytest”方法行不通）

该脚本消除了五个导致本地与 CI 环境差异的真实来源：

| | 不使用包装脚本 | 使用包装脚本 |
|---|---|---|
| 提供商 API 密钥 | 环境中现有的任何值（自动检测池） | 所有 `*_API_KEY`/`*_TOKEN`/等 均取消设置 |
| HOME / `~/.hermes/` | 真实的 config+auth.json | 每个测试使用临时目录 |
| 时区 | 本地时区（PDT 等） | UTC |
| 区域设置 | 已设置的任何值 | C.UTF-8 |
| xdist 工作进程 | `-n auto` = 所有核心（工作站上 20+） | `-n 4` 以匹配 CI |

`tests/conftest.py` 还通过自动使用夹具强制执行第 1-4 点，因此**任何** pytest 调用（包括 IDE 集成）都会获得无干扰行为——但包装脚本提供了双重保障。

### 不使用包装脚本运行（仅在必须时）

如果无法使用包装脚本（例如在 Windows 上或在直接调用 pytest 的 IDE 中），至少应激活虚拟环境并传递 `-n 4`：

```bash
source .venv/bin/activate   # 或：source venv/bin/activate
python -m pytest tests/ -q -n 4
```

工作进程数超过 4 会暴露出 CI 从未遇到的测试顺序不稳定性问题。

推送更改前，务必运行完整的测试套件。

### 不要编写变更检测器测试

如果测试在**预期会变更**的数据（如模型目录、配置版本号、枚举计数、硬编码的提供商模型列表）更新时就会失败，那么它就是**变更检测器**。这些测试不提供行为覆盖；它们只是保证常规的源码更新会破坏 CI，并耗费工程时间来“修复”。

**不要编写：**

```python
# 目录快照 —— 每次模型发布都会破坏
assert "gemini-2.5-pro" in _PROVIDER_MODELS["gemini"]
assert "MiniMax-M2.7" in models

# 配置版本字面量 —— 每次模式升级都会破坏
assert DEFAULT_CONFIG["_config_version"] == 21

# 枚举计数 —— 每次添加技能/提供商都会破坏
assert len(_PROVIDER_MODELS["huggingface"]) == 8
```

**应该编写：**

```python
# 行为：目录管道是否正常工作？
assert "gemini" in _PROVIDER_MODELS
assert len(_PROVIDER_MODELS["gemini"]) >= 1

# 行为：迁移是否将用户的版本提升到当前最新？
assert raw["_config_version"] == DEFAULT_CONFIG["_config_version"]

# 不变量：纯规划模型不会泄漏到旧列表中
assert not (set(moonshot_models) & coding_plan_only_models)

# 不变量：目录中的每个模型都有上下文长度条目
for m in _PROVIDER_MODELS["huggingface"]:
    assert m.lower() in DEFAULT_CONTEXT_LENGTHS_LOWER
```

规则是：如果测试读起来像是当前数据的快照，就删除它。如果读起来像是关于两段数据必须如何关联的契约，就保留它。当 PR 添加新的提供商/模型并且你想要一个测试时，让测试断言关系（例如“目录条目都有上下文长度”），而不是具体的名称。

审阅者应拒绝新的变更检测器测试；作者应在重新请求审阅前将其转换为不变量断言。