# Hermes Agent - 开发指南

面向 AI 编码助手和参与 hermes-agent 代码库开发的开发者的说明。

## 开发环境

```bash
# 优先使用 .venv；如果您的检出使用的是 venv，则回退到 venv。
source .venv/bin/activate   # 或者：source venv/bin/activate
```

`scripts/run_tests.sh` 会先探测 `.venv`，然后是 `venv`，接着是
`$HOME/.hermes/hermes-agent/venv`（用于与主检出共享 venv 的工作树）。

## 项目结构

文件数量经常变动——不要将下面的树状图视为详尽无遗。
规范来源是文件系统。注释指出了您实际会编辑的关键入口点。

```
hermes-agent/
├── run_agent.py          # AIAgent 类 — 核心对话循环 (~12k 行代码)
├── model_tools.py        # 工具编排，discover_builtin_tools()，handle_function_call()
├── toolsets.py           # 工具集定义，_HERMES_CORE_TOOLS 列表
├── cli.py                # HermesCLI 类 — 交互式 CLI 编排器 (~11k 行代码)
├── hermes_state.py       # SessionDB — SQLite 会话存储（FTS5 搜索）
├── hermes_constants.py   # get_hermes_home()，display_hermes_home() — 基于配置文件的路径
├── hermes_logging.py     # setup_logging() — agent.log / errors.log / gateway.log（基于配置文件）
├── batch_runner.py       # 并行批量处理
├── agent/                # Agent 内部组件（提供商适配器、记忆、缓存、压缩等）
├── hermes_cli/           # CLI 子命令、设置向导、插件加载器、皮肤引擎
├── tools/                # 工具实现 — 通过 tools/registry.py 自动发现
│   └── environments/     # 终端后端（本地、docker、ssh、modal、daytona、singularity）
├── gateway/              # 消息网关 — run.py + session.py + platforms/
│   ├── platforms/        # 各平台适配器（telegram、discord、slack、whatsapp、
│   │                     #   homeassistant、signal、matrix、mattermost、email、sms、
│   │                     #   dingtalk、wecom、weixin、feishu、qqbot、bluebubbles、
│   │                     #   webhook、api_server、...）。参见 ADDING_A_PLATFORM.md。
│   └── builtin_hooks/    # 始终注册的网关钩子的扩展点（未随附）
├── plugins/              # 插件系统（参见下面的“插件”部分）
│   ├── memory/           # 记忆提供者插件（honcho、mem0、supermemory、...）
│   ├── context_engine/   # 上下文引擎插件
│   └── <others>/         # 仪表板、图像生成、磁盘清理、示例、...
├── optional-skills/      # 较重/小众的技能，随附但默认不激活
├── skills/               # 与仓库捆绑的内置技能
├── ui-tui/               # Ink (React) 终端 UI — `hermes --tui`
│   └── src/              # entry.tsx, app.tsx, gatewayClient.ts + app/components/hooks/lib
├── tui_gateway/          # TUI 的 Python JSON-RPC 后端
├── acp_adapter/          # ACP 服务器（VS Code / Zed / JetBrains 集成）
├── cron/                 # 调度器 — jobs.py, scheduler.py
├── environments/         # RL 训练环境（Atropos）
├── scripts/              # run_tests.sh, release.py, 辅助脚本
├── website/              # Docusaurus 文档站点
└── tests/                # Pytest 测试套件（截至 2026 年 4 月，约 700 个文件，~15k 个测试）
```

**用户配置：** `~/.hermes/config.yaml`（设置），`~/.hermes/.env`（仅 API 密钥）。
**日志：** `~/.hermes/logs/` — `agent.log`（INFO+），`errors.log`（WARNING+），
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
会话上下文、预算、凭证池等）。下面的签名是您通常会接触到的最小子集 —
请阅读 `run_agent.py` 获取完整列表。

```python
class AIAgent:
    def __init__(self,
        base_url: str = None,
        api_key: str = None,
        provider: str = None,
        api_mode: str = None,              # "chat_completions" | "codex_responses" | ...
        model: str = "",                   # 空 → 稍后从配置/提供商解析
        max_iterations: int = 90,          # 工具调用迭代次数（与子代理共享）
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

核心循环在 `run_conversation()` 内部 — 完全同步，包含
中断检查、预算跟踪和一次宽容调用：

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
- 技能斜杠命令：`agent/skill_commands.py` 扫描 `~/.hermes/skills/`，作为**用户消息**（而非系统提示词）注入，以保留提示词缓存

### 斜杠命令注册表 (`hermes_cli/commands.py`)

所有斜杠命令都在一个中央的 `COMMAND_REGISTRY` 列表中定义，该列表包含 `CommandDef` 对象。所有下游消费者都自动从此注册表派生：

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
- `category` — 其中之一：`"Session"`、`"Configuration"`、`"Tools & Skills"`、`"Info"`、`"Exit"`
- `aliases` — 替代名称的元组（例如 `("bg",)`）
- `args_hint` — 帮助中显示的参数占位符（例如 `"<prompt>"`、`"[name]"`）
- `cli_only` — 仅在交互式 CLI 中可用
- `gateway_only` — 仅在消息平台上可用
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
npm run dev       # 监视模式（重建 hermes-ink + tsx --watch）
npm start         # 生产环境
npm run build     # 完整构建（hermes-ink + tsc）
npm run type-check # 仅类型检查（tsc --noEmit）
npm run lint      # eslint
npm run fmt       # prettier
npm test          # vitest
```

### 仪表板中的 TUI (`hermes dashboard` → `/chat`)

仪表板嵌入的是真正的 `hermes --tui` — **不是**重写。请参见 `hermes_cli/pty_bridge.py` + `hermes_cli/web_server.py` 中的 `@app.websocket("/api/pty")` 端点。

- 浏览器加载 `web/src/pages/ChatPage.tsx`，该文件挂载 xterm.js 的 `Terminal`，使用 WebGL 渲染器、`@xterm/addon-fit` 用于容器驱动的调整大小，以及 `@xterm/addon-unicode11` 用于现代宽字符宽度。
- `/api/pty?token=…` 升级为 WebSocket；身份验证使用与 REST 相同的临时 `_SESSION_TOKEN`，通过查询参数传递（浏览器无法在 WS 升级时设置 `Authorization`）。
- 服务器通过 `ptyprocess`（POSIX PTY — WSL 可用，原生 Windows 不可用）生成 `hermes --tui` 会生成的任何内容。
- 帧：双向原始 PTY 字节；通过 `\x1b[RESIZE:<cols>;<rows>]` 调整大小，在服务器端拦截并使用 `TIOCSWINSZ` 应用。
**不要在 React 中重新实现主要的聊天体验。** 主要的对话记录、输入框/输入流（包括斜杠命令行为）以及基于 PTY 的终端都属于嵌入式 `hermes --tui` —— 你在 Ink 中添加的任何新内容都会自动显示在仪表板中。如果你发现自己正在为仪表板重建对话记录或输入框，请停止并转而扩展 Ink。

**围绕 TUI 构建结构化的 React UI 是允许的，只要它不是第二个聊天界面。** 侧边栏小部件、检查器、摘要、状态面板和类似的辅助视图（例如 `ChatSidebar`、`ModelPickerDialog`、`ToolCall`）是可以的，只要它们补充嵌入式 TUI 而不是替换对话记录/输入框/终端。保持它们的状态独立于 PTY 子进程的会话，并以非破坏性的方式呈现它们的故障，以便终端窗格保持正常工作不受影响。

---

## 添加新工具

需要在 **2 个文件** 中进行更改：

**1. 创建 `tools/your_tool.py`:**
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

**2. 添加到 `toolsets.py`** —— 可以是 `_HERMES_CORE_TOOLS`（所有平台）或一个新的工具集。

自动发现：任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入 —— 无需维护手动导入列表。

注册表处理模式收集、分发、可用性检查和错误包装。所有处理程序**必须**返回一个 JSON 字符串。

**工具模式中的路径引用**：如果模式描述中提到文件路径（例如默认输出目录），请使用 `display_hermes_home()` 使其感知配置文件。模式在导入时生成，这是在 `_apply_profile_override()` 设置 `HERMES_HOME` 之后。

**状态文件**：如果一个工具存储持久状态（缓存、日志、检查点），请使用 `get_hermes_home()` 作为基础目录 —— 永远不要用 `Path.home() / ".hermes"`。这确保每个配置文件都有自己的状态。

**Agent 级工具**（待办事项、记忆）：在 `handle_function_call()` 之前被 `run_agent.py` 拦截。请参阅 `tools/todo_tool.py` 了解模式。

---

## 添加配置

### config.yaml 选项：
1. 添加到 `hermes_cli/config.py` 中的 `DEFAULT_CONFIG`
2. 增加 `_config_version`（检查 `DEFAULT_CONFIG` 顶部的当前值）
   **仅当**你需要主动迁移/转换现有用户配置时（重命名键、更改结构）。向现有部分添加新键由深度合并自动处理，**不需要**增加版本号。

### .env 变量（**仅限机密** —— API 密钥、Token、密码）：
1. 添加到 `hermes_cli/config.py` 中的 `OPTIONAL_ENV_VARS` 并附带元数据：
```python
"NEW_API_KEY": {
    "description": "用途说明",
    "prompt": "显示名称",
    "url": "https://...",
    "password": True,
    "category": "tool",  # provider, tool, messaging, setting
},
```

非机密设置（超时、阈值、功能标志、路径、显示偏好）属于 `config.yaml`，而不是 `.env`。如果内部代码为了向后兼容需要一个环境变量镜像，请在代码中从 `config.yaml` 桥接到环境变量（参见 `gateway_timeout`、`terminal.cwd` → `TERMINAL_CWD`）。

### 配置加载器（三条路径 —— 了解你正在使用哪一条）：

| 加载器 | 使用者 | 位置 |
|--------|---------|----------|
| `load_cli_config()` | CLI 模式 | `cli.py` —— 合并 CLI 特定的默认值 + 用户 YAML |
| `load_config()` | `hermes tools`、`hermes setup`、大多数 CLI 子命令 | `hermes_cli/config.py` —— 合并 `DEFAULT_CONFIG` + 用户 YAML |
| 直接 YAML 加载 | 消息网关运行时 | `gateway/run.py` + `gateway/config.py` —— 原始读取用户 YAML |

如果你添加了一个新键，CLI 能看到但消息网关看不到（或反之），说明你使用了错误的加载器。检查 `DEFAULT_CONFIG` 的覆盖范围。

### 工作目录：
- **CLI** —— 使用进程的当前目录 (`os.getcwd()`)。
- **消息传递** —— 使用 `config.yaml` 中的 `terminal.cwd`。消息网关将其桥接到 `TERMINAL_CWD` 环境变量供子工具使用。**`MESSAGING_CWD` 已被移除** —— 如果它在 `.env` 中设置，配置加载器会打印弃用警告。`.env` 中的 `TERMINAL_CWD` 同理；规范设置是 `config.yaml` 中的 `terminal.cwd`。

---

## 皮肤/主题系统

皮肤引擎 (`hermes_cli/skin_engine.py`) 提供数据驱动的 CLI 视觉自定义。皮肤是**纯数据** —— 添加新皮肤无需更改代码。

### 架构

```
hermes_cli/skin_engine.py    # SkinConfig 数据类、内置皮肤、YAML 加载器
~/.hermes/skins/*.yaml       # 用户安装的自定义皮肤（即插即用）
```

- `init_skin_from_config()` —— 在 CLI 启动时调用，从配置中读取 `display.skin`
- `get_active_skin()` —— 返回当前皮肤的缓存 `SkinConfig`
- `set_active_skin(name)` —— 在运行时切换皮肤（由 `/skin` 命令使用）
- `load_skin(name)` —— 首先从用户皮肤加载，然后是内置皮肤，最后回退到默认皮肤
- 缺失的皮肤值会自动从 `default` 皮肤继承

### 皮肤自定义的内容

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
| 欢迎消息 | `branding.welcome` | `cli.py` |
| 响应框标签 | `branding.response_label` | `cli.py` |
| 提示符符号 | `branding.prompt_symbol` | `cli.py` |
### 内置皮肤

- `default` — 经典 Hermes 金色/可爱风格（当前外观）
- `ares` — 深红/青铜战神主题，带有自定义旋转器翅膀
- `mono` — 简洁的灰度单色主题
- `slate` — 酷炫的蓝色开发者主题

### 添加内置皮肤

在 `hermes_cli/skin_engine.py` 的 `_BUILTIN_SKINS` 字典中添加：

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

### 用户自定义皮肤（YAML）

用户创建 `~/.hermes/skins/<name>.yaml`：

```yaml
name: cyberpunk
description: 霓虹灯风格的终端主题

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

Hermes 有两个插件接口。两者都位于代码库的 `plugins/` 目录下，这样仓库自带的插件可以与用户安装在 `~/.hermes/plugins/` 目录下以及通过 pip 安装的插件一起被发现。

### 通用插件 (`hermes_cli/plugins.py` + `plugins/<name>/`)

`PluginManager` 从 `~/.hermes/plugins/`、`./.hermes/plugins/` 和 pip 入口点发现插件。每个插件暴露一个 `register(ctx)` 函数，该函数可以：

- 注册 Python 回调的生命周期钩子：
  `pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`,
  `on_session_start`, `on_session_end`
- 通过 `ctx.register_tool(...)` 注册新工具
- 通过 `ctx.register_cli_command(...)` 注册 CLI 子命令 — 插件的 argparse 树在启动时连接到 `hermes`，因此 `hermes <pluginname> <subcmd>` 无需修改 `main.py` 即可工作

钩子从 `model_tools.py`（工具调用前/后）和 `run_agent.py`（生命周期）调用。**发现时机陷阱：** `discover_plugins()` 仅在导入 `model_tools.py` 时作为副作用运行。在导入 `model_tools.py` 之前读取插件状态的代码路径必须显式调用 `discover_plugins()`（它是幂等的）。

### 记忆提供商插件 (`plugins/memory/<name>/`)

用于可插拔记忆后端的独立发现系统。当前内置的提供商包括 **honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb**。

每个提供商实现 `MemoryProvider` 抽象基类（参见 `agent/memory_provider.py`），并由 `agent/memory_manager.py` 编排。生命周期钩子包括 `sync_turn(turn_messages)`, `prefetch(query)`, `shutdown()`，以及可选的 `post_setup(hermes_home, config)` 用于设置向导集成。

**通过 `plugins/memory/<name>/cli.py` 的 CLI 命令：** 如果记忆插件定义了 `register_cli(subparser)`，`discover_plugin_cli_commands()` 会在 argparse 设置时找到它并将其连接到 `hermes <plugin>`。该框架仅暴露**当前激活的**记忆提供商（从 config.yaml 中的 `memory.provider` 读取）的 CLI 命令，因此禁用的提供商不会使 `hermes --help` 变得杂乱。

**规则（Teknium，2026年5月）：** 插件**不得**修改核心文件（`run_agent.py`, `cli.py`, `gateway/run.py`, `hermes_cli/main.py` 等）。如果插件需要框架未暴露的功能，应扩展通用插件接口（新钩子、新的 ctx 方法）— 切勿将插件特定逻辑硬编码到核心中。PR #5295 正是因此移除了 `main.py` 中 95 行硬编码的 honcho argparse 代码。

### 仪表板 / 上下文引擎 / 图像生成插件目录

`plugins/context_engine/`、`plugins/image_gen/`、`plugins/example-dashboard/` 等遵循相同的模式（抽象基类 + 编排器 + 每个插件的目录）。上下文引擎插件连接到 `agent/context_engine.py`；图像生成提供商连接到 `agent/image_gen_provider.py`。

---

## 技能

两个平行的接口：

- **`skills/`** — 内置技能，默认随附并加载。按类别目录组织（例如 `skills/github/`、`skills/mlops/`）。
- **`optional-skills/`** — 较重或小众的技能，随仓库提供但**默认不激活**。通过 `hermes skills install official/<category>/<skill>` 显式安装。适配器位于 `tools/skills_hub.py`（`OptionalSkillSource`）。类别包括 `autonomous-ai-agents`、`blockchain`、`communication`、`creative`、`devops`、`email`、`health`、`mcp`、`migration`、`mlops`、`productivity`、`research`、`security`、`web-development`。

审查技能 PR 时，请检查它们的目标目录 — 依赖重或小众的技能应属于 `optional-skills/`。

### SKILL.md 前置元数据

标准字段：`name`、`description`、`version`、`platforms`（操作系统门控列表：`[macos]`、`[linux, macos]`、...）、`metadata.hermes.tags`、`metadata.hermes.category`、`metadata.hermes.config`（技能所需的 config.yaml 设置 — 存储在 `skills.config.<key>` 下，在设置期间提示，在加载时注入）。

---

## 重要策略

### 提示词缓存不得被破坏

Hermes-Agent 确保缓存在整个会话中保持有效。**请勿实施会破坏缓存的更改：**
- 在会话中途更改过去的上下文
- 在会话中途更改工具集
- 在会话中途重新加载记忆或重建系统提示词

破坏缓存会导致成本急剧增加。我们更改上下文的**唯一**时机是在上下文压缩期间。

改变系统提示词状态（技能、工具、记忆等）的斜杠命令必须是**缓存感知的**：默认采用延迟失效（更改在下一次会话生效），并提供一个可选的 `--now` 标志用于立即失效。请参阅 `/skills install --now` 作为规范模式。

### 后台进程通知（消息网关）

当使用 `terminal(background=true, notify_on_complete=true)` 时，消息网关会运行一个监视器来检测进程完成并触发新的 Agent 轮次。通过 config.yaml 中的 `display.background_process_notifications`（或环境变量 `HERMES_BACKGROUND_NOTIFICATIONS`）控制后台进程消息的详细程度：
- `all` — 运行输出更新 + 最终消息（默认）
- `result` — 仅最终完成消息
- `error` — 仅当退出码 != 0 时的最终消息
- `off` — 完全不显示监视器消息

---

## 配置文件：多实例支持

Hermes 支持**配置文件**——多个完全隔离的实例，每个实例都有自己的 `HERMES_HOME` 目录（配置、API 密钥、记忆、会话、技能、消息网关等）。

核心机制：`hermes_cli/main.py` 中的 `_apply_profile_override()` 在任何模块导入之前设置 `HERMES_HOME`。所有 `get_hermes_home()` 引用都会自动限定在活动配置文件的范围内。

### 配置文件安全代码规则

1.  **所有 HERMES_HOME 路径都使用 `get_hermes_home()`。** 从 `hermes_constants` 导入。在读取/写入状态的代码中，**绝对不要**硬编码 `~/.hermes` 或 `Path.home() / ".hermes"`。
    ```python
    # 正确
    from hermes_constants import get_hermes_home
    config_path = get_hermes_home() / "config.yaml"

    # 错误 — 会破坏配置文件功能
    config_path = Path.home() / ".hermes" / "config.yaml"
    ```

2.  **面向用户的消息使用 `display_hermes_home()`。** 从 `hermes_constants` 导入。对于默认配置文件，它返回 `~/.hermes`；对于其他配置文件，返回 `~/.hermes/profiles/<name>`。
    ```python
    # 正确
    from hermes_constants import display_hermes_home
    print(f"配置已保存到 {display_hermes_home()}/config.yaml")

    # 错误 — 对于配置文件会显示错误的路径
    print("配置已保存到 ~/.hermes/config.yaml")
    ```

3.  **模块级常量没问题** — 它们在导入时缓存 `get_hermes_home()`，这是在 `_apply_profile_override()` 设置环境变量**之后**。只需使用 `get_hermes_home()`，而不是 `Path.home() / ".hermes"`。

4.  **模拟 `Path.home()` 的测试也必须设置 `HERMES_HOME`** — 因为代码现在使用 `get_hermes_home()`（读取环境变量），而不是 `Path.home() / ".hermes"`：
    ```python
    with patch.object(Path, "home", return_value=tmp_path), \
         patch.dict(os.environ, {"HERMES_HOME": str(tmp_path / ".hermes")}):
        ...
    ```

5.  **消息网关平台适配器应使用令牌锁** — 如果适配器使用唯一凭据（机器人令牌、API 密钥）连接，请在 `connect()`/`start()` 方法中调用 `gateway.status` 中的 `acquire_scoped_lock()`，并在 `disconnect()`/`stop()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件使用相同的凭据。请参阅 `gateway/platforms/telegram.py` 了解规范模式。

6.  **配置文件操作基于 HOME，而不是 HERMES_HOME** — `_get_profiles_root()` 返回 `Path.home() / ".hermes" / "profiles"`，**而不是** `get_hermes_home() / "profiles"`。这是有意为之的——它允许 `hermes -p coder profile list` 查看所有配置文件，无论哪个是活动的。

## 已知陷阱

### 不要硬编码 `~/.hermes` 路径
代码路径使用 `hermes_constants` 中的 `get_hermes_home()`。面向用户的打印/日志消息使用 `display_hermes_home()`。硬编码 `~/.hermes` 会破坏配置文件功能——每个配置文件都有自己的 `HERMES_HOME` 目录。这是 PR #3575 中修复的 5 个错误的根源。

### 不要引入新的 `simple_term_menu` 用法
`hermes_cli/main.py` 中现有的调用点仅作为遗留回退保留；首选的 UI 是 curses（标准库），因为 `simple_term_menu` 在 tmux/iTerm2 中使用箭头键时存在幽灵重复渲染错误。新的交互式菜单必须使用 `hermes_cli/curses_ui.py`——请参阅 `hermes_cli/tools_config.py` 了解规范模式。

### 不要在 spinner/display 代码中使用 `\033[K`（ANSI 清除到行尾）
在 `prompt_toolkit` 的 `patch_stdout` 下会泄漏为字面文本 `?[K`。使用空格填充：`f"\r{line}{' ' * pad}"`。

### `_last_resolved_tool_names` 是 `model_tools.py` 中的一个进程全局变量
`delegate_tool.py` 中的 `_run_single_child()` 在子 Agent 执行期间保存和恢复此全局变量。如果你添加读取此全局变量的新代码，请注意它在子 Agent 运行期间可能暂时是过时的。

### 不要在模式描述中硬编码跨工具引用
工具模式描述不得按名称提及来自其他工具集的工具（例如，`browser_navigate` 说“首选 web_search”）。这些工具可能不可用（缺少 API 密钥、工具集被禁用），导致模型幻觉式地调用不存在的工具。如果需要交叉引用，请在 `model_tools.py` 的 `get_tool_definitions()` 中动态添加——请参阅 `browser_navigate` / `execute_code` 后处理块了解模式。

### 消息网关有**两个**消息守卫——两者都必须绕过审批/控制命令
当 Agent 运行时，消息会依次通过两个守卫：
(1) **基础适配器** (`gateway/platforms/base.py`) 在 `session_key in self._active_sessions` 时将消息排队到 `_pending_messages` 中，以及
(2) **消息网关运行器** (`gateway/run.py`) 在消息到达 `running_agent.interrupt()` 之前拦截 `/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`。
任何在 Agent 被阻塞时必须到达运行器的新命令（例如审批提示）**必须**绕过**两个**守卫，并内联分发，而不是通过 `_process_message_background()`（这会与会话生命周期产生竞争）。

### 来自陈旧分支的压缩合并会静默恢复最近的修复
在压缩合并 PR 之前，请确保分支与 `main` 保持同步（在工作树中执行 `git fetch origin main && git reset --hard origin/main`，然后重新应用 PR 的提交）。一个陈旧分支中不相关文件的版本在压缩时会静默覆盖 `main` 上的最新修复。合并后使用 `git diff HEAD~1..HEAD` 验证——意外的删除是危险信号。

### 不要在没有端到端验证的情况下接入死代码
从未发布过的未使用代码之所以是死代码，是有原因的。在将未使用的模块接入实时代码路径之前，请使用实际的导入（而非模拟）针对临时的 `HERMES_HOME` 对真实的解析链进行端到端测试。

### 测试不能写入 `~/.hermes/`
`tests/conftest.py` 中的 `_isolate_hermes_home` 自动使用夹具将 `HERMES_HOME` 重定向到临时目录。在测试中永远不要硬编码 `~/.hermes/` 路径。

**配置文件测试**：测试配置文件功能时，也要模拟 `Path.home()`，以便 `_get_profiles_root()` 和 `_get_default_hermes_home()` 在临时目录内解析。使用 `tests/hermes_cli/test_profiles.py` 中的模式：
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

**务必使用 `scripts/run_tests.sh`** — 不要直接调用 `pytest`。该脚本强制执行与 CI 环境一致的无依赖环境（取消设置凭证变量、TZ=UTC、LANG=C.UTF-8、4 个 xdist 工作进程以匹配 GHA ubuntu-latest）。在设置了 API 密钥的 16+ 核开发机器上直接运行 `pytest`，会以多种方式偏离 CI 环境，这已导致多次“本地通过，CI 失败”的事件（反之亦然）。

```bash
scripts/run_tests.sh                                  # 完整测试套件，与 CI 一致
scripts/run_tests.sh tests/gateway/                   # 一个目录
scripts/run_tests.sh tests/agent/test_foo.py::test_x  # 一个测试
scripts/run_tests.sh -v --tb=long                     # 传递 pytest 标志
```

### 为什么需要包装脚本（以及为什么旧的“直接调用 pytest”行不通）

该脚本消除了五个导致本地与 CI 环境差异的真实来源：

| | 不使用包装脚本 | 使用包装脚本 |
|---|---|---|
| 提供商 API 密钥 | 环境中已有的任何内容（自动检测池） | 所有 `*_API_KEY`/`*_TOKEN`/等 均被取消设置 |
| HOME / `~/.hermes/` | 您真实的 config+auth.json | 每个测试使用临时目录 |
| 时区 | 本地时区（PDT 等） | UTC |
| 区域设置 | 已设置的任何内容 | C.UTF-8 |
| xdist 工作进程 | `-n auto` = 所有核心（工作站上 20+） | `-n 4` 以匹配 CI |

`tests/conftest.py` 还通过一个自动使用的 fixture 强制执行第 1-4 点，因此**任何** pytest 调用（包括 IDE 集成）都会获得无依赖行为 — 但包装脚本是双重保险。

### 不使用包装脚本运行（仅在必须时）

如果无法使用包装脚本（例如在 Windows 上或在直接调用 pytest 的 IDE 内部），至少激活虚拟环境并传递 `-n 4`：

```bash
source .venv/bin/activate   # 或: source venv/bin/activate
python -m pytest tests/ -q -n 4
```

工作进程数超过 4 会暴露 CI 从未遇到的测试顺序不稳定问题。

推送更改前务必运行完整测试套件。

### 不要编写变更检测器测试

如果一个测试在**预期会变化**的数据更新时失败，那么它就是**变更检测器** — 例如模型目录、配置版本号、枚举计数、硬编码的提供商模型列表。这些测试不提供任何行为覆盖；它们只是保证常规的源码更新会破坏 CI，并耗费工程时间来“修复”。

**不要编写：**

```python
# 目录快照 — 每次模型发布都会中断
assert "gemini-2.5-pro" in _PROVIDER_MODELS["gemini"]
assert "MiniMax-M2.7" in models

# 配置版本字面量 — 每次模式升级都会中断
assert DEFAULT_CONFIG["_config_version"] == 21

# 枚举计数 — 每次添加技能/提供商都会中断
assert len(_PROVIDER_MODELS["huggingface"]) == 8
```

**应该编写：**

```python
# 行为：目录管道是否正常工作？
assert "gemini" in _PROVIDER_MODELS
assert len(_PROVIDER_MODELS["gemini"]) >= 1

# 行为：迁移是否将用户的版本提升到当前最新？
assert raw["_config_version"] == DEFAULT_CONFIG["_config_version"]

# 不变量：没有仅计划模型泄漏到旧列表中
assert not (set(moonshot_models) & coding_plan_only_models)

# 不变量：目录中的每个模型都有上下文长度条目
for m in _PROVIDER_MODELS["huggingface"]:
    assert m.lower() in DEFAULT_CONTEXT_LENGTHS_LOWER
```

规则是：如果测试读起来像是当前数据的快照，就删除它。如果它读起来像是关于两段数据必须如何关联的契约，就保留它。当 PR 添加新的提供商/模型并且您想要一个测试时，让测试断言这种关系（例如“所有目录条目都有上下文长度”），而不是具体的名称。

审阅者应拒绝新的变更检测器测试；作者应在重新请求审阅前将其转换为不变量断言。