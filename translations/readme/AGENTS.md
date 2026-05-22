# Hermes Agent - 开发指南

适用于在 hermes-agent 代码库上工作的 AI 编码助手和开发人员的说明。

## 开发环境

```bash
# 优先使用 .venv；如果您的检出目录使用的是 venv，则回退到 venv。
source .venv/bin/activate   # 或者：source venv/bin/activate
```

`scripts/run_tests.sh` 会先探测 `.venv`，然后是 `venv`，最后是
`$HOME/.hermes/hermes-agent/venv`（用于与主检出目录共享 venv 的工作树）。

## 项目结构

文件数量不断变化——不要将下面的树状图视为详尽无遗。
规范来源是文件系统。注释指出了您实际需要编辑的关键入口点。

```
hermes-agent/
├── run_agent.py          # AIAgent 类 — 核心对话循环（约 12k 行）
├── model_tools.py        # 工具编排，discover_builtin_tools()，handle_function_call()
├── toolsets.py           # 工具集定义，_HERMES_CORE_TOOLS 列表
├── cli.py                # HermesCLI 类 — 交互式 CLI 编排器（约 11k 行）
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
│   └── builtin_hooks/    # 始终注册的网关钩子的扩展点（默认不提供）
├── plugins/              # 插件系统（参见下面的“插件”部分）
│   ├── memory/           # 记忆提供者插件（honcho、mem0、supermemory、...）
│   ├── context_engine/   # 上下文引擎插件
│   ├── model-providers/  # 推理后端插件（openrouter、anthropic、gmi、...）
│   ├── kanban/           # 多 Agent 看板调度器 + 工作器插件
│   ├── hermes-achievements/  # 游戏化成就追踪
│   ├── observability/    # 指标 / 追踪 / 日志插件
│   ├── image_gen/        # 图像生成提供商
│   └── <others>/         # disk-cleanup、example-dashboard、google_meet、platforms、
│                         #   spotify、strike-freedom-cockpit、...
├── optional-skills/      # 较重/小众的技能，随仓库提供但默认不激活
├── skills/               # 与仓库捆绑的内置技能
├── ui-tui/               # Ink (React) 终端 UI — `hermes --tui`
│   └── src/              # entry.tsx、app.tsx、gatewayClient.ts + app/components/hooks/lib
├── tui_gateway/          # TUI 的 Python JSON-RPC 后端
├── acp_adapter/          # ACP 服务器（VS Code / Zed / JetBrains 集成）
├── cron/                 # 调度器 — jobs.py、scheduler.py
├── scripts/              # run_tests.sh、release.py、辅助脚本
├── website/              # Docusaurus 文档站点
└── tests/                # Pytest 测试套件（截至 2026 年 5 月，约 900 个文件，约 17k 个测试）
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

真正的 `AIAgent.__init__` 接受约 60 个参数（凭据、路由、回调、
会话上下文、预算、凭据池等）。下面的签名是您通常需要处理的最小子集
—— 完整的列表请阅读 `run_agent.py`。

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
- **皮肤引擎** (`hermes_cli/skin_engine.py`) — 数据驱动的 CLI 主题；启动时从 `display.skin` 配置键初始化；皮肤自定义横幅颜色、spinner 表情/动词/翅膀、工具前缀、响应框、品牌文本
- `process_command()` 是 `HermesCLI` 上的一个方法 — 根据通过中央注册表 `resolve_command()` 解析出的规范命令名进行分发
- 技能斜杠命令：`agent/skill_commands.py` 扫描 `~/.hermes/skills/`，作为**用户消息**（非系统提示词）注入以保留提示词缓存

### 斜杠命令注册表 (`hermes_cli/commands.py`)

所有斜杠命令都在一个中央的 `COMMAND_REGISTRY` `CommandDef` 对象列表中定义。每个下游消费者都自动从此注册表派生：

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
3. 如果该命令在消息网关中可用，在 `gateway/run.py` 中添加处理程序：
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

**添加别名** 只需要将其添加到现有 `CommandDef` 的 `aliases` 元组中。无需更改其他文件 — 分发、帮助文本、Telegram 菜单、Slack 映射和自动补全都会自动更新。

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
npm start         # 生产模式
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
**不要在 React 中重新实现主要的聊天体验。** 主要的对话记录、输入框/输入流程（包括斜杠命令行为）以及基于 PTY 的终端都属于嵌入式 `hermes --tui` —— 你在 Ink 中添加的任何新内容都会自动显示在仪表板中。如果你发现自己正在为仪表板重建对话记录或输入框，请停止并转而扩展 Ink。

**围绕 TUI 构建结构化的 React UI 是允许的，只要它不是第二个聊天界面。** 侧边栏小部件、检查器、摘要、状态面板以及类似的辅助视图（例如 `ChatSidebar`、`ModelPickerDialog`、`ToolCall`）是可以的，只要它们是对嵌入式 TUI 的补充，而不是取代对话记录/输入框/终端。保持它们的状态独立于 PTY 子进程的会话，并以非破坏性的方式呈现它们的故障，以便终端窗格能继续正常工作。

---

## 添加新工具

对于大多数自定义或仅限本地的工具，**不要**编辑 Hermes 核心。请改用插件方式：创建 `~/.hermes/plugins/<name>/plugin.yaml` 和 `~/.hermes/plugins/<name>/__init__.py`，然后使用 `ctx.register_tool(...)` 注册工具。插件工具集会被自动发现，并且可以在不接触 `tools/` 或 `toolsets.py` 的情况下启用或禁用。

仅当用户明确要贡献一个应包含在基础系统中的新核心 Hermes 工具时，才使用下面描述的内置方式。

内置/核心工具需要在 **2 个文件** 中进行更改：

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

**2. 添加到 `toolsets.py`** —— 可以是 `_HERMES_CORE_TOOLS`（所有平台）或一个新的工具集。**此步骤是必需的：** 自动发现会导入工具并注册其模式，但只有工具名称出现在某个工具集中时，它才会*暴露给 Agent*。`_HERMES_CORE_TOOLS` 不是死代码 —— 它是每个平台的基础工具集默认继承的默认捆绑包。

自动发现：任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入 —— 无需维护手动导入列表。但将其接入一个工具集仍然是一个有意的、手动的步骤。

注册表处理模式收集、分发、可用性检查和错误包装。所有处理程序**必须**返回一个 JSON 字符串。

**工具模式中的路径引用**：如果模式描述中提到文件路径（例如默认输出目录），请使用 `display_hermes_home()` 使其感知配置文件。模式在导入时生成，此时 `_apply_profile_override()` 已经设置了 `HERMES_HOME`。

**状态文件**：如果工具存储持久状态（缓存、日志、检查点），请使用 `get_hermes_home()` 作为基础目录 —— 切勿使用 `Path.home() / ".hermes"`。这确保每个配置文件都有自己的状态。

**Agent 级工具**（todo, memory）：在 `handle_function_call()` 之前被 `run_agent.py` 拦截。请参阅 `tools/todo_tool.py` 了解模式。

---

## 依赖项锁定策略

所有依赖项都必须有上限，以限制供应链攻击面。
该策略是在 litellm 安全事件（PR #2796, #2810）之后建立的，并在 Mini Shai-Hulud 蠕虫活动（2026 年 5 月）之后得到加强。

| 源类型 | 处理方式 | 示例 |
|---|---|---|
| PyPI 包 | `>=下限版本,<下一个主版本` | `"httpx>=0.28.1,<1"` |
| Git URL | 提交 SHA | `git+https://...@<40-字符-sha>` |
| GitHub Actions | 提交 SHA + 注释 | `uses: actions/checkout@<sha>  # v4` |
| 仅 CI 使用的 pip | `==精确版本` | `pyyaml==6.0.2` |

**向 `pyproject.toml` 添加新依赖项时：**
1. 对于 1.0 之后的版本，固定为 `>=当前版本,<下一个主版本`（例如 `>=1.5.0,<2`）。
2. 对于 1.0 之前的包，使用 `<0.(当前次版本 + 2)`（例如 `>=0.29,<0.32`）。
3. 切勿提交没有上限的裸 `>=X.Y.Z` —— CI 和审查者会拒绝它。
4. 运行 `uv lock` 以重新生成带有哈希值的 `uv.lock`。

参考：#2810（版本上限检查），#9801（SHA 锁定 + 审计 CI）。

---

## 添加配置

### config.yaml 选项：
1. 添加到 `hermes_cli/config.py` 中的 `DEFAULT_CONFIG`
2. 仅当你需要主动迁移/转换现有用户配置（重命名键、更改结构）时，才增加 `_config_version`（检查 `DEFAULT_CONFIG` 顶部的当前值）。向现有部分添加新键由深度合并自动处理，**不需要**增加版本号。

### 顶级 `config.yaml` 部分（非详尽列表）：

`model`, `agent`, `terminal`, `compression`, `display`, `stt`, `tts`,
`memory`, `security`, `delegation`, `smart_model_routing`, `checkpoints`,
`auxiliary`, `curator`, `skills`, `gateway`, `logging`, `cron`, `profiles`,
`plugins`, `honcho`.

`auxiliary` 保存用于辅助 LLM 工作的每任务覆盖（curator, vision,
embedding, title generation, session_search 等）—— 每个任务可以固定其自己的 provider/model/base_url/max_tokens/reasoning_effort。请参阅 `agent/auxiliary_client.py::_resolve_auto` 了解解析顺序。

`curator` 保存后台技能维护配置 ——
`enabled`, `interval_hours`, `min_idle_hours`, `stale_after_days`,
`archive_after_days`, `backup`（嵌套的）。

### .env 变量（**仅限机密信息** —— API 密钥、Token、密码）：
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
### 配置加载器（三种路径——请明确你处于哪种情况）：

| 加载器 | 使用方 | 位置 |
|--------|---------|----------|
| `load_cli_config()` | CLI 模式 | `cli.py` — 合并 CLI 特定的默认值 + 用户 YAML |
| `load_config()` | `hermes tools`, `hermes setup`, 大多数 CLI 子命令 | `hermes_cli/config.py` — 合并 `DEFAULT_CONFIG` + 用户 YAML |
| 直接 YAML 加载 | 消息网关运行时 | `gateway/run.py` + `gateway/config.py` — 直接读取用户 YAML |

如果你添加了一个新键，CLI 能识别但消息网关不能（或反之），说明你使用了错误的加载器。请检查 `DEFAULT_CONFIG` 的覆盖范围。

### 工作目录：
- **CLI** — 使用进程的当前目录 (`os.getcwd()`)。
- **消息传递** — 使用 `config.yaml` 中的 `terminal.cwd`。消息网关会将其桥接为子工具的 `TERMINAL_CWD` 环境变量。**`MESSAGING_CWD` 已被移除** — 如果在 `.env` 中设置了此变量，配置加载器会打印弃用警告。`.env` 中的 `TERMINAL_CWD` 同理；规范设置是 `config.yaml` 中的 `terminal.cwd`。

---

## 皮肤/主题系统

皮肤引擎 (`hermes_cli/skin_engine.py`) 提供了数据驱动的 CLI 视觉自定义功能。皮肤是**纯数据** — 添加新皮肤无需更改代码。

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

| 元素 | 皮肤键 | 使用方 |
|---------|----------|---------|
| 横幅面板边框 | `colors.banner_border` | `banner.py` |
| 横幅面板标题 | `colors.banner_title` | `banner.py` |
| 横幅分区标题 | `colors.banner_accent` | `banner.py` |
| 横幅暗淡文本 | `colors.banner_dim` | `banner.py` |
| 横幅正文文本 | `colors.banner_text` | `banner.py` |
| 响应框边框 | `colors.response_border` | `cli.py` |
| 旋转器表情（等待中） | `spinner.waiting_faces` | `display.py` |
| 旋转器表情（思考中） | `spinner.thinking_faces` | `display.py` |
| 旋转器动词 | `spinner.thinking_verbs` | `display.py` |
| 旋转器翅膀（可选） | `spinner.wings` | `display.py` |
| 工具输出前缀 | `tool_prefix` | `display.py` |
| 每个工具的 emoji | `tool_emojis` | `display.py` → `get_tool_emoji()` |
| Agent 名称 | `branding.agent_name` | `banner.py`, `cli.py` |
| 欢迎消息 | `branding.welcome` | `cli.py` |
| 响应框标签 | `branding.response_label` | `cli.py` |
| 提示符符号 | `branding.prompt_symbol` | `cli.py` |

### 内置皮肤

- `default` — 经典的 Hermes 金色/可爱风格（当前外观）
- `ares` — 深红/青铜色的战神主题，带有自定义旋转器翅膀
- `mono` — 简洁的灰度单色主题
- `slate` — 以开发者为中心的酷炫蓝色主题

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

Hermes 有两个插件接口。两者都位于仓库的 `plugins/` 目录下，这样仓库自带的插件可以与用户安装在 `~/.hermes/plugins/` 的插件以及通过 pip 安装的入口点插件一起被发现。

### 通用插件 (`hermes_cli/plugins.py` + `plugins/<name>/`)

`PluginManager` 从 `~/.hermes/plugins/`、`./.hermes/plugins/` 和 pip 入口点发现插件。每个插件都暴露一个 `register(ctx)` 函数，该函数可以：

- 注册 Python 回调的生命周期钩子：
  `pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`,
  `on_session_start`, `on_session_end`
- 通过 `ctx.register_tool(...)` 注册新工具
- 通过 `ctx.register_cli_command(...)` 注册 CLI 子命令 — 插件的 argparse 树在启动时连接到 `hermes`，因此 `hermes <插件名> <子命令>` 无需更改 `main.py` 即可工作

钩子从 `model_tools.py`（工具调用前/后）和 `run_agent.py`（生命周期）调用。**发现时机陷阱：** `discover_plugins()` 仅在导入 `model_tools.py` 时作为副作用运行。在导入 `model_tools.py` 之前读取插件状态的代码路径必须显式调用 `discover_plugins()`（它是幂等的）。

### 记忆提供者插件 (`plugins/memory/<name>/`)

用于可插拔记忆后端的独立发现系统。当前内置的提供者包括 **honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb**。

每个提供者都实现 `MemoryProvider` 抽象基类（参见 `agent/memory_provider.py`），并由 `agent/memory_manager.py` 编排。生命周期钩子包括 `sync_turn(turn_messages)`, `prefetch(query)`, `shutdown()`，以及可选的 `post_setup(hermes_home, config)` 用于设置向导集成。

**通过 `plugins/memory/<name>/cli.py` 的 CLI 命令：** 如果记忆插件定义了 `register_cli(subparser)`，`discover_plugin_cli_commands()` 会在 argparse 设置时找到它，并将其连接到 `hermes <插件>`。该框架仅暴露**当前激活的**记忆提供者的 CLI 命令（从 config.yaml 中的 `memory.provider` 读取），因此禁用的提供者不会使 `hermes --help` 变得杂乱。

**规则 (Teknium, 2026年5月)：** 插件**不得**修改核心文件（`run_agent.py`, `cli.py`, `gateway/run.py`, `hermes_cli/main.py` 等）。如果插件需要框架未暴露的功能，应扩展通用插件接口（新钩子、新的 ctx 方法）— 切勿将插件特定逻辑硬编码到核心中。PR #5295 正是因此移除了 `main.py` 中 95 行硬编码的 honcho argparse 代码。
**2026年5月起，不再新增内置记忆提供商（政策）：** `plugins/memory/` 下的内置记忆提供商集合已关闭。新的记忆后端必须作为**独立的插件仓库**发布，由用户安装到 `~/.hermes/plugins/`（或通过 pip entry points）——它们实现相同的 `MemoryProvider` ABC，通过相同的发现路径注册，并通过 `hermes memory setup` / `post_setup()` 集成，而无需进入本仓库树。向 `plugins/memory/` 下添加新目录的 PR 将被关闭，并会指引发布者将提供商作为自己的仓库发布。现有的内置提供商保留；欢迎为其提供错误修复。

### 模型提供商插件 (`plugins/model-providers/<name>/`)

每个推理后端（openrouter、anthropic、gmi、deepseek、nvidia……）都作为一个插件放在这里。每个插件的 `__init__.py` 在模块加载时调用 `providers.register_provider(ProviderProfile(...))`。`providers/__init__.py._discover_providers()` 是一个**惰性的、独立的发现系统**——在首次调用 `get_provider_profile()` 或 `list_providers()` 时扫描，而非由通用的 PluginManager 扫描。

扫描顺序：
1.  捆绑插件：`<repo>/plugins/model-providers/<name>/`
2.  用户插件：`$HERMES_HOME/plugins/model-providers/<name>/`
3.  遗留插件：`<repo>/providers/<name>.py`（向后兼容）

同名用户插件会覆盖捆绑插件——`register_provider()` 遵循后写者胜原则。这使得第三方无需打仓库补丁即可替换任何内置配置。

通用 PluginManager 会记录 `kind: model-provider` 清单，但**不会**导入它们（否则会导致 `ProviderProfile` 双重实例化）。没有明确 `kind:` 的插件会通过源代码启发式方法（`__init__.py` 中存在 `register_provider` + `ProviderProfile`）自动转换。

完整创作指南：`website/docs/developer-guide/model-provider-plugin.md`。

### 仪表盘 / 上下文引擎 / 图像生成插件目录

`plugins/context_engine/`、`plugins/image_gen/` 等遵循相同的模式（ABC + 编排器 + 每个插件的目录）。上下文引擎插件接入 `agent/context_engine.py`；图像生成提供商接入 `agent/image_gen_provider.py`。参考/文档配套插件（`example-dashboard`、`strike-freedom-cockpit`、`plugin-llm-example`、`plugin-llm-async-example`）位于 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins) 配套仓库，而非本仓库树中。

---

## 技能

两个平行的层面：

-   **`skills/`** — 默认打包并加载的内置技能。按类别目录组织（例如 `skills/github/`、`skills/mlops/`）。
-   **`optional-skills/`** — 较重或小众的技能，随仓库打包但**不**默认激活。通过 `hermes skills install official/<category>/<skill>` 显式安装。适配器位于 `tools/skills_hub.py`（`OptionalSkillSource`）。类别包括 `autonomous-ai-agents`、`blockchain`、`communication`、`creative`、`devops`、`email`、`health`、`mcp`、`migration`、`mlops`、`productivity`、`research`、`security`、`web-development`。

审查技能 PR 时，请检查它们的目标目录——依赖重或小众的技能应属于 `optional-skills/`。

### SKILL.md frontmatter

标准字段：`name`、`description`、`version`、`author`、`license`、`platforms`（操作系统门控列表：`[macos]`、`[linux, macos]`、……）、`metadata.hermes.tags`、`metadata.hermes.category`、`metadata.hermes.related_skills`、`metadata.hermes.config`（技能所需的 config.yaml 设置——存储在 `skills.config.<key>` 下，在设置期间提示，在加载时注入）。

顶层的 `tags:` 和 `category:` 也被接受，并由加载器从 `metadata.hermes.*` 镜像。

### 技能创作标准（硬性规定）

每个新的或现代化的技能——无论是捆绑的、可选的还是贡献的——在合并前必须满足这些标准。审查者将拒绝违反这些标准的 PR。

1.  **`description` 不超过 60 个字符，一句话，以句号结尾。**
    过长的描述会使技能列表臃肿，并在加载许多技能时分散模型的注意力。说明功能，而非实现。不要使用营销词汇（"强大"、"全面"、"无缝"、"先进"）。不要重复技能名称。使用以下代码验证：
    ```python
    import re, pathlib
    m = re.search(r'^description: (.*)$',
                  pathlib.Path('skills/<cat>/<name>/SKILL.md').read_text(),
                  re.MULTILINE)
    assert len(m.group(1)) <= 60, len(m.group(1))
    ```

2.  **SKILL.md 正文中引用的工具必须是原生的 Hermes 工具或技能明确期望的 MCP 服务器。** 当技能需要某项能力时，用反引号指出正确的工具名称（`` `terminal` ``、`` `web_extract` ``、`` `read_file` ``、`` `patch` ``、`` `search_files` ``、`` `vision_analyze` ``、`` `browser_navigate` ``、`` `delegate_task` `` 等）。**不要**命名 Agent 已经封装好的 shell 工具——`grep` → `search_files`、`cat`/`head`/`tail` → `read_file`、`sed`/`awk` → `patch`、`find`/`ls` → `search_files target='files'`。如果技能依赖于 MCP 服务器，请命名该 MCP 服务器并在 `## 先决条件` 中记录预期的设置。其他任何内容（第三方 CLI、shell 管道等）都可以在脚本文件中使用，但不应成为正文中的主要交互界面。

3.  **`platforms:` 门控需根据实际脚本导入进行审核。** 使用仅限 POSIX 的原语（`fcntl`、`termios`、`os.setsid`、用于存活性检查的 `os.kill(pid, 0)`、`/proc`、硬编码的 `/tmp`、`signal.SIGKILL`、bash heredocs、`osascript`、`apt`、`systemctl`）的技能必须声明其支持的平台。默认立场：首先尝试跨平台修复——使用 `tempfile.gettempdir`、`pathlib.Path`、`psutil.pid_exists`、Python 级别的过滤而非 `grep`。仅当依赖项确实受平台限制时，才将门控设置为更窄的集合。

4.  **`author` 首先归功于人类贡献者。** 对于外部贡献，贡献者的真实姓名 + GitHub 用户名放在首位；"Hermes Agent" 是次要协作者。如果贡献者的提交显示作者为 "Hermes Agent"（因为他们使用 Hermes 起草了技能），请将其替换为他们的真实姓名——归功于人类，而非工具。
5. **SKILL.md 正文采用现代章节顺序。** `# <技能> 技能`
   标题，2-3 句话介绍说明其功能和限制，
   `## 何时使用`、`## 先决条件`、`## 如何运行`、
   `## 快速参考`、`## 步骤`、`## 常见问题`、
   `## 验证`。复杂技能目标约 200 行，
   简单技能约 100 行。删减冗余的介绍性内容、营销文案，
   以及已在 `## 先决条件` 中解释过的环境变量重复说明。

6. **脚本放在 `scripts/`，参考资料放在 `references/`，
   模板放在 `templates/`。** 不要期望模型每次调用都内联编写
   解析器、XML 遍历器或非平凡逻辑——提供一个辅助脚本。
   在 SKILL.md 中通过相对于技能目录的路径引用它。

7. **测试位于 `tests/skills/test_<技能>_skill.py`** 并且仅使用
   标准库 + pytest + `unittest.mock`。不进行实时网络调用。通过
   `scripts/run_tests.sh tests/skills/test_<技能>_skill.py -q` 运行。

8. **`.env.example` 的添加内容被隔离在一个清晰分隔的块中。**
   不要改动周围文件——贡献者提供的 `.env.example`
   版本通常已过时，在抢救过程中必须丢弃对技能自身块之外的编辑。

外部技能 PR 的完整抢救/现代化检查清单位于 `hermes-agent-dev` 技能的
`references/new-skill-pr-salvage.md` 文件中——在完善贡献者技能 PR 之前请加载它。

---

## 工具集

所有工具集都在 `toolsets.py` 中定义为单个 `TOOLSETS` 字典。
每个平台的适配器选择一个基础工具集（例如 Telegram 使用
`"messaging"`）；`_HERMES_CORE_TOOLS` 是大多数平台继承的默认捆绑包。

当前工具集键：`browser`、`clarify`、`code_execution`、`cronjob`、
`debugging`、`delegation`、`discord`、`discord_admin`、`feishu_doc`、
`feishu_drive`、`file`、`homeassistant`、`image_gen`、`kanban`、`memory`、
`messaging`、`moa`、`rl`、`safe`、`search`、`session_search`、`skills`、
`spotify`、`terminal`、`todo`、`tts`、`video`、`vision`、`web`、`yuanbao`。

通过 `hermes tools`（curses UI）或 `config.yaml` 中的
`tools.<platform>.enabled` / `tools.<platform>.disabled` 列表
按平台启用/禁用。

---

## 委派 (`delegate_task`)

`tools/delegate_tool.py` 生成一个具有隔离上下文 + 终端会话的子 Agent。
同步：父 Agent 等待子 Agent 的摘要后再继续其自身循环——如果父 Agent 被中断，子 Agent 将被取消。

两种形式：

- **单任务：** 传递 `goal`（+ 可选的 `context`、`toolsets`）。
- **批量（并行）：** 传递 `tasks: [...]` —— 每个任务获得其自己并发运行的子 Agent。
  并发数受 `delegation.max_concurrent_children` 限制（默认 3）。

角色：

- `role="leaf"`（默认）—— 专注的工作者。不能调用 `delegate_task`、
  `clarify`、`memory`、`send_message`、`execute_code`。
- `role="orchestrator"` —— 保留 `delegate_task` 以便它可以生成自己的工作者。
  受 `delegation.orchestrator_enabled` 控制（默认 true）并受 `delegation.max_spawn_depth` 限制（默认 2）。

关键配置选项（在 `config.yaml` 的 `delegation:` 下）：
`max_concurrent_children`、`max_spawn_depth`、`child_timeout_seconds`、
`orchestrator_enabled`、`subagent_auto_approve`、`inherit_mcp_toolsets`、
`max_iterations`。

同步性规则：delegate_task **不是** 持久性的。对于必须比当前轮次更长时间运行的
工作，请改用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

---

## 策展器（技能生命周期）

后台技能维护系统，跟踪 Agent 创建技能的
使用情况并自动归档过时的技能。用户永远不会丢失技能；归档的
技能会移动到 `~/.hermes/skills/.archive/` 并可恢复。

- **核心：** `agent/curator.py`（审查循环、自动转换、LLM 审查
  提示词） + `agent/curator_backup.py`（运行前 tar.gz 快照）。
- **CLI：** `hermes_cli/curator.py` 连接 `hermes curator <动词>`，其中
  动词有：`status`、`run`、`pause`、`resume`、`pin`、`unpin`、
  `archive`、`restore`、`prune`、`backup`、`rollback`。
- **遥测：** `tools/skill_usage.py` 管理 sidecar
  `~/.hermes/skills/.usage.json` —— 每个技能的 `use_count`、`view_count`、
  `patch_count`、`last_activity_at`、`state`（活跃 / 过时 /
  已归档）、`pinned`。

不变式：
- 策展器只处理具有 `created_by: "agent"` 来源的技能 ——
  捆绑的 + 从 hub 安装的技能是禁区。
- 从不删除；最具破坏性的操作是归档。
- 已固定的技能免于所有自动转换和 LLM 审查流程。
- `skill_manage(action="delete")` 拒绝已固定的技能；补丁/编辑/
  write_file/remove_file 可以通过，以便 Agent 可以继续改进
  已固定的技能。

配置部分（`config.yaml` 中的 `curator:`）：
`enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、
`archive_after_days`、`backup.*`。

完整的面向用户文档：`website/docs/user-guide/features/curator.md`。

---

## Cron（定时任务）

`cron/jobs.py`（任务存储） + `cron/scheduler.py`（滴答循环）。Agent
通过 `cronjob` 工具调度任务；用户通过 `hermes cron <动词>`
（`list`、`add`、`edit`、`pause`、`resume`、`run`、`remove`）或
`/cron` 斜杠命令调度。

支持的调度格式：
- 持续时间：`"30m"`、`"2h"`、`"1d"`
- "every" 短语：`"every 2h"`、`"every monday 9am"`
- 5 字段 cron 表达式：`"0 9 * * *"`
- ISO 时间戳（一次性）：`"2026-06-01T09:00:00Z"`

每个任务的字段包括 `skills`（加载特定技能）、`model` /
`provider` 覆盖、`script`（运行前数据收集脚本，其
标准输出被注入到提示词中；`no_agent=True` 将脚本
变成整个任务）、`context_from`（将任务 A 的最后输出链接到
任务 B 的提示词中）、`workdir`（在特定目录中运行，并加载其
`AGENTS.md`/`CLAUDE.md`）以及多平台交付。

强化不变式：
- **3 分钟硬中断** cron 会话 —— 失控的 Agent 循环
  不能独占调度器。
- 追赶窗口：任务周期的一半，限制在 120 秒到 2 小时之间。
- 宽限窗口：对于错过触发时间的一次性任务，有 120 秒。
- 文件锁位于 `~/.hermes/cron/.tick.lock`，防止跨进程的重复滴答。
- Cron 会话默认传递 `skip_memory=True`；记忆提供商
  在 cron 期间故意不运行。
定时任务的交付内容**不会**镜像到目标消息网关会话中——
它们会进入自己的定时任务会话，并带有页眉/页脚帧，这样主对话的消息角色交替就能保持完整。

---

## 看板（多 Agent 工作队列）

这是一个持久化的、基于 SQLite 的看板，允许多个配置文件 / 工作者在共享任务上进行协作。用户通过 `hermes kanban <动词>` 来驱动它；由调度器生成的工作者通过专用的 `kanban_*` 工具集来驱动它，这样当它们不在看板任务内时，其架构占用为零。

- **CLI：** `hermes_cli/kanban.py` 将 `hermes kanban` 与动词 `init`、`create`、`list`（别名 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`，以及较少使用的 `watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-*`、`dispatch`、`daemon`、`gc` 连接起来。
- **工作者/编排器工具集：** `tools/kanban_tools.py` 暴露 `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`；在调度器生成的任务之外明确启用 `kanban` 工具集的配置文件还会获得 `kanban_list` 和 `kanban_unblock` 用于看板路由。
- **调度器：** 一个长生命周期的循环，默认每 60 秒回收过期的认领、提升就绪任务、原子性地认领并生成已分配配置文件。默认情况下，通过 `kanban.dispatch_in_gateway: true` **在消息网关内部**运行。
- **插件资源：** `plugins/kanban/dashboard/`（Web UI）+ `plugins/kanban/systemd/`（`hermes-kanban-dispatcher.service` 用于独立调度器部署）。

隔离模型：
- **看板**是硬边界——工作者生成时，其环境变量中固定设置了 `HERMES_KANBAN_BOARD`，因此它们无法看到其他看板。
- **租户**是看板*内部*的软命名空间——一个专家团队可以通过工作空间路径 + 记忆键隔离来服务多个业务。
- 在同一任务上连续 `kanban.failure_limit` 次非成功尝试后（默认：2），调度器会自动阻塞该任务以防止循环。

完整的面向用户文档：`website/docs/user-guide/features/kanban.md`。

---

## 重要策略

### 提示词缓存不得被破坏

Hermes-Agent 确保缓存在整个对话期间保持有效。**请勿实施会导致以下情况的更改：**
- 在对话中途更改过去的上下文
- 在对话中途更改工具集
- 在对话中途重新加载记忆或重建系统提示词

破坏缓存会导致成本急剧增加。我们更改上下文的**唯一**时机是在上下文压缩期间。

改变系统提示词状态（技能、工具、记忆等）的斜杠命令必须是**缓存感知的**：默认采用延迟失效（更改在下一次会话生效），并提供一个可选的 `--now` 标志用于立即失效。请参阅 `/skills install --now` 作为规范模式。

### 后台进程通知（消息网关）

当使用 `terminal(background=true, notify_on_complete=true)` 时，消息网关会运行一个监视器来检测进程完成并触发新的 Agent 轮次。通过 `config.yaml` 中的 `display.background_process_notifications`（或 `HERMES_BACKGROUND_NOTIFICATIONS` 环境变量）控制后台进程消息的详细程度：

- `all` —— 运行输出更新 + 最终消息（默认）
- `result` —— 仅最终完成消息
- `error` —— 仅当退出代码 != 0 时的最终消息
- `off` —— 完全没有监视器消息

---

## 配置文件：多实例支持

Hermes 支持**配置文件**——多个完全隔离的实例，每个实例都有自己的 `HERMES_HOME` 目录（配置、API 密钥、记忆、会话、技能、消息网关等）。

核心机制：`hermes_cli/main.py` 中的 `_apply_profile_override()` 在任何模块导入之前设置 `HERMES_HOME`。所有 `get_hermes_home()` 引用都会自动限定在活动配置文件的范围内。

### 配置文件安全代码规则

1.  **对所有 HERMES_HOME 路径使用 `get_hermes_home()`。** 从 `hermes_constants` 导入。在读取/写入状态的代码中**切勿**硬编码 `~/.hermes` 或 `Path.home() / ".hermes"`。
    ```python
    # 正确
    from hermes_constants import get_hermes_home
    config_path = get_hermes_home() / "config.yaml"

    # 错误 —— 破坏配置文件
    config_path = Path.home() / ".hermes" / "config.yaml"
    ```

2.  **对面向用户的消息使用 `display_hermes_home()`。** 从 `hermes_constants` 导入。对于默认配置文件，它返回 `~/.hermes`；对于其他配置文件，返回 `~/.hermes/profiles/<name>`。
    ```python
    # 正确
    from hermes_constants import display_hermes_home
    print(f"配置已保存到 {display_hermes_home()}/config.yaml")

    # 错误 —— 对配置文件显示错误路径
    print("配置已保存到 ~/.hermes/config.yaml")
    ```

3.  **模块级常量没问题**——它们在导入时缓存 `get_hermes_home()`，这是在 `_apply_profile_override()` 设置环境变量**之后**。只需使用 `get_hermes_home()`，而不是 `Path.home() / ".hermes"`。

4.  **模拟 `Path.home()` 的测试也必须设置 `HERMES_HOME`**——因为代码现在使用 `get_hermes_home()`（读取环境变量），而不是 `Path.home() / ".hermes"`：
    ```python
    with patch.object(Path, "home", return_value=tmp_path), \
         patch.dict(os.environ, {"HERMES_HOME": str(tmp_path / ".hermes")}):
        ...
    ```

5.  **消息网关平台适配器应使用 Token 锁**——如果适配器使用唯一凭据（机器人 Token、API 密钥）连接，请在 `connect()`/`start()` 方法中调用 `gateway.status` 中的 `acquire_scoped_lock()`，并在 `disconnect()`/`stop()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件使用相同的凭据。请参阅 `gateway/platforms/telegram.py` 作为规范模式。

6.  **配置文件操作是基于 HOME 锚定的，而不是基于 HERMES_HOME 锚定的**——`_get_profiles_root()` 返回 `Path.home() / ".hermes" / "profiles"`，**不是** `get_hermes_home() / "profiles"`。这是有意为之——它让 `hermes -p coder profile list` 能够看到所有配置文件，无论哪个配置文件是活动的。

## 已知陷阱

### 请勿硬编码 `~/.hermes` 路径
对于代码路径，请使用 `hermes_constants` 中的 `get_hermes_home()`。对于面向用户的打印/日志消息，请使用 `display_hermes_home()`。硬编码 `~/.hermes` 会破坏配置文件——每个配置文件都有自己的 `HERMES_HOME` 目录。这是 PR #3575 中修复的 5 个错误的根源。
### 禁止引入新的 `simple_term_menu` 使用方式
`hermes_cli/main.py` 中现有的调用点仅作为遗留回退方案保留；
首选 UI 是 curses（标准库），因为 `simple_term_menu` 在 tmux/iTerm2 中使用箭头键时存在幽灵重复渲染的 bug。新的交互式菜单必须使用 `hermes_cli/curses_ui.py` — 请参考 `hermes_cli/tools_config.py` 中的规范模式。

### 禁止在 spinner/display 代码中使用 `\033[K`（ANSI 清除到行尾）
在 `prompt_toolkit` 的 `patch_stdout` 下会泄漏为字面文本 `?[K`。请使用空格填充：`f"\r{line}{' ' * pad}"`。

### `_last_resolved_tool_names` 是 `model_tools.py` 中的一个进程全局变量
`delegate_tool.py` 中的 `_run_single_child()` 在子 Agent 执行前后会保存和恢复此全局变量。如果你添加了读取此全局变量的新代码，请注意在子 Agent 运行期间它可能暂时是过时的。

### 禁止在模式描述中硬编码跨工具引用
工具模式描述中不得按名称提及来自其他工具集的工具（例如，`browser_navigate` 说“首选 web_search”）。这些工具可能不可用（缺少 API 密钥、工具集被禁用），导致模型幻觉式地调用不存在的工具。如果需要跨引用，请在 `model_tools.py` 的 `get_tool_definitions()` 中动态添加 — 请参考 `browser_navigate` / `execute_code` 后处理块的模式。

### 消息网关有两条消息守卫 — 两者都必须绕过审批/控制命令
当 Agent 运行时，消息会依次通过两个守卫：
(1) **基础适配器** (`gateway/platforms/base.py`) 在 `session_key in self._active_sessions` 时将消息排队到 `_pending_messages` 中，以及
(2) **网关运行器** (`gateway/run.py`) 在消息到达 `running_agent.interrupt()` 之前拦截 `/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`。
任何在 Agent 被阻塞时必须到达运行器的新命令（例如审批提示）**必须**绕过**两个**守卫，并以内联方式分发，而不是通过 `_process_message_background()`（这会与会话生命周期产生竞争）。

### 从过时分支进行的压缩合并会静默地回滚最近的修复
在压缩合并 PR 之前，请确保分支与 `main` 保持同步（在工作树中执行 `git fetch origin main && git reset --hard origin/main`，然后重新应用 PR 的提交）。过时分支中不相关文件的版本在压缩时会静默地覆盖 `main` 上的最新修复。合并后使用 `git diff HEAD~1..HEAD` 验证 — 意外的删除是危险信号。

### 未经端到端验证，不要接入死代码
从未发布的未使用代码之所以是死代码，是有原因的。在将未使用的模块接入活动代码路径之前，请使用实际的导入（而非模拟）针对临时的 `HERMES_HOME` 对真实的解析链进行端到端测试。

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

**始终使用 `scripts/run_tests.sh`** — 不要直接调用 `pytest`。该脚本强制执行与 CI 一致的无副作用的执行环境（取消设置凭据变量、TZ=UTC、LANG=C.UTF-8、`-n auto` xdist 工作进程、树内子进程隔离插件）。在设置了 API 密钥的 16+ 核开发机器上直接运行 `pytest`，会以多种方式与 CI 产生差异，这些差异曾导致多起“本地工作，CI 失败”的事件（反之亦然）。

```bash
scripts/run_tests.sh                                  # 完整测试套件，与 CI 一致
scripts/run_tests.sh tests/gateway/                   # 一个目录
scripts/run_tests.sh tests/agent/test_foo.py::test_x  # 一个测试
scripts/run_tests.sh -v --tb=long                     # 透传 pytest 标志
scripts/run_tests.sh --no-isolate tests/foo/          # 禁用子进程隔离（更快，用于调试）
```

### 每个测试的子进程隔离

每个测试都通过位于 `tests/_isolate_plugin.py` 的树内插件，在一个新生成的 Python 子进程中运行。这意味着一个测试中的模块级字典/集合和 ContextVars 不会泄漏到下一个测试 — 历史上使用的 `_reset_module_state` 自动使用夹具已移除。

实现说明：

- 该插件使用 `multiprocessing.get_context("spawn")`，这在 Linux、macOS 和 Windows 上同样有效（不使用 POSIX `fork`）。
- 每个测试的开销约为 0.5–1.0 秒（Python 启动 + pytest 收集）。xdist 并行性会将这些开销分摊到各个核心；在 20 核的机器上，完整套件的完成时间与之前大致相同，但无 flake。
- `isolate_timeout`（在 `pyproject.toml` 中配置）将每个测试限制在 30 秒内。挂起的测试会被终止并作为失败报告。
- 传递 `--no-isolate` 以禁用隔离 — 这在交互式调试单个测试时很有用，或者当你特别想验证状态泄漏时。
- 该插件在子进程中会自行禁用（通过哨兵环境变量 `HERMES_ISOLATE_CHILD=1`），因此不存在 fork 炸弹的风险。

### 为什么需要包装脚本（以及为什么旧的“直接调用 pytest”行不通）

该脚本消除了五个导致本地与 CI 差异的真实来源：

| | 无包装脚本 | 有包装脚本 |
|---|---|---|
| 提供商 API 密钥 | 环境中现有的任何内容（自动检测池） | 所有 `*_API_KEY`/`*_TOKEN`/等 均被取消设置 |
| HOME / `~/.hermes/` | 你的真实配置+auth.json | 每个测试使用临时目录 |
| 时区 | 本地时区（PDT 等） | UTC |
| 区域设置 | 已设置的任何内容 | C.UTF-8 |
| xdist 工作进程 | `-n auto` = 所有核心 | `-n auto`（安全 — 子进程隔离防止跨工作进程的 flake） |

`tests/conftest.py` 还通过一个自动使用夹具强制执行第 1-4 点，因此**任何** pytest 调用（包括 IDE 集成）都会获得无副作用的行为 — 但包装脚本是双重保险。
### 不使用包装器运行（仅在必须时）

如果无法使用包装器（例如在直接调用 pytest 的 IDE 中），至少需要激活虚拟环境。隔离插件会自动从 `pyproject.toml` 中的 `addopts` 加载，因此无论哪种方式，你都能获得相同的按测试进程隔离。

```bash
source .venv/bin/activate   # 或者: source venv/bin/activate
python -m pytest tests/ -q
```

如果需要在调试时绕过隔离以快速获得反馈：

```bash
python -m pytest tests/agent/test_foo.py -q --no-isolate
```

在推送更改之前，务必运行完整的测试套件。

### 不要编写变更检测器测试

如果一个测试在**预期会更改**的数据（例如模型目录、配置版本号、枚举计数、硬编码的提供商模型列表）更新时就会失败，那么它就是一个**变更检测器**。这些测试不提供任何行为覆盖；它们只是保证常规的源代码更新会破坏 CI，并耗费工程时间来“修复”。

**不要这样写：**

```python
# 目录快照 —— 每次模型发布都会中断
assert "gemini-2.5-pro" in _PROVIDER_MODELS["gemini"]
assert "MiniMax-M2.7" in models

# 配置版本字面量 —— 每次模式升级都会中断
assert DEFAULT_CONFIG["_config_version"] == 21

# 枚举计数 —— 每次添加技能/提供商时都会中断
assert len(_PROVIDER_MODELS["huggingface"]) == 8
```

**应该这样写：**

```python
# 行为：目录管道是否正常工作？
assert "gemini" in _PROVIDER_MODELS
assert len(_PROVIDER_MODELS["gemini"]) >= 1

# 行为：迁移是否将用户的版本提升到当前最新？
assert raw["_config_version"] == DEFAULT_CONFIG["_config_version"]

# 不变量：没有仅用于计划的模型泄漏到旧列表中
assert not (set(moonshot_models) & coding_plan_only_models)

# 不变量：目录中的每个模型都有上下文长度条目
for m in _PROVIDER_MODELS["huggingface"]:
    assert m.lower() in DEFAULT_CONTEXT_LENGTHS_LOWER
```

规则是：如果测试读起来像是当前数据的快照，就删除它。如果它读起来像是关于两段数据必须如何关联的契约，就保留它。当 PR 添加新的提供商/模型并且你想要一个测试时，让测试断言这种关系（例如“所有目录条目都有上下文长度”），而不是具体的名称。

审阅者应拒绝新的变更检测器测试；作者应在重新请求审阅之前将其转换为不变量测试。