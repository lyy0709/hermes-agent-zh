# Hermes Agent - 开发指南

适用于在 hermes-agent 代码库上工作的 AI 编码助手和开发人员的说明。

## 开发环境

```bash
source venv/bin/activate  # 运行 Python 前务必激活
```

## 项目结构

```
hermes-agent/
├── run_agent.py          # AIAgent 类 — 核心对话循环
├── model_tools.py        # 工具编排，discover_builtin_tools()，handle_function_call()
├── toolsets.py           # 工具集定义，_HERMES_CORE_TOOLS 列表
├── cli.py                # HermesCLI 类 — 交互式 CLI 编排器
├── hermes_state.py       # SessionDB — SQLite 会话存储（FTS5 搜索）
├── agent/                # Agent 内部组件
│   ├── prompt_builder.py     # 系统提示词组装
│   ├── context_compressor.py # 自动上下文压缩
│   ├── prompt_caching.py     # Anthropic 提示词缓存
│   ├── auxiliary_client.py   # 辅助 LLM 客户端（视觉、摘要）
│   ├── model_metadata.py     # 模型上下文长度，Token 估算
│   ├── models_dev.py         # models.dev 注册表集成（感知提供商的上下文）
│   ├── display.py            # KawaiiSpinner，工具预览格式化
│   ├── skill_commands.py     # 技能斜杠命令（共享 CLI/消息网关）
│   └── trajectory.py         # 轨迹保存助手
├── hermes_cli/           # CLI 子命令和设置
│   ├── main.py           # 入口点 — 所有 `hermes` 子命令
│   ├── config.py         # DEFAULT_CONFIG，OPTIONAL_ENV_VARS，迁移
│   ├── commands.py       # 斜杠命令定义 + SlashCommandCompleter
│   ├── callbacks.py      # 终端回调（clarify，sudo，approval）
│   ├── setup.py          # 交互式设置向导
│   ├── skin_engine.py    # 皮肤/主题引擎 — CLI 视觉定制
│   ├── skills_config.py  # `hermes skills` — 按平台启用/禁用技能
│   ├── tools_config.py   # `hermes tools` — 按平台启用/禁用工具
│   ├── skills_hub.py     # `/skills` 斜杠命令（搜索、浏览、安装）
│   ├── models.py         # 模型目录，提供商模型列表
│   ├── model_switch.py   # 共享的 /model 切换流水线（CLI + 消息网关）
│   └── auth.py           # 提供商凭据解析
├── tools/                # 工具实现（每个工具一个文件）
│   ├── registry.py       # 中央工具注册表（模式、处理器、分发）
│   ├── approval.py       # 危险命令检测
│   ├── terminal_tool.py  # 终端编排
│   ├── process_registry.py # 后台进程管理
│   ├── file_tools.py     # 文件读/写/搜索/补丁
│   ├── web_tools.py      # 网络搜索/提取（Parallel + Firecrawl）
│   ├── browser_tool.py   # Browserbase 浏览器自动化
│   ├── code_execution_tool.py # execute_code 沙盒
│   ├── delegate_tool.py  # 子 Agent 委派
│   ├── mcp_tool.py       # MCP 客户端（约 1050 行）
│   └── environments/     # 终端后端（本地、docker、ssh、modal、daytona、singularity）
├── gateway/              # 消息平台消息网关
│   ├── run.py            # 主循环，斜杠命令，消息分发
│   ├── session.py        # SessionStore — 对话持久化
│   └── platforms/        # 适配器：telegram，discord，slack，whatsapp，homeassistant，signal，qqbot
├── ui-tui/               # Ink (React) 终端 UI — `hermes --tui`
│   ├── src/entry.tsx        # TTY 网关 + render()
│   ├── src/app.tsx          # 主状态机和 UI
│   ├── src/gatewayClient.ts # 子进程 + JSON-RPC 桥接
│   ├── src/app/             # 分解的应用逻辑（事件处理器、斜杠处理器、存储、钩子）
│   ├── src/components/      # Ink 组件（品牌、markdown、提示、选择器等）
│   ├── src/hooks/           # useCompletion，useInputHistory，useQueue，useVirtualHistory
│   └── src/lib/             # 纯辅助函数（历史记录、osc52、文本、rpc、消息）
├── tui_gateway/          # TUI 的 Python JSON-RPC 后端
│   ├── entry.py             # stdio 入口点
│   ├── server.py            # RPC 处理器和会话逻辑
│   ├── render.py            # 可选的 rich/ANSI 桥接
│   └── slash_worker.py      # 用于斜杠命令的持久 HermesCLI 子进程
├── acp_adapter/          # ACP 服务器（VS Code / Zed / JetBrains 集成）
├── cron/                 # 调度器（jobs.py，scheduler.py）
├── environments/         # RL 训练环境（Atropos）
├── tests/                # Pytest 测试套件（约 3000 个测试）
└── batch_runner.py       # 并行批量处理
```

**用户配置：** `~/.hermes/config.yaml`（设置），`~/.hermes/.env`（API 密钥）

## 文件依赖链

```
tools/registry.py  （无依赖 — 被所有工具文件导入）
       ↑
tools/*.py  （每个文件在导入时调用 registry.register()）
       ↑
model_tools.py  （导入 tools/registry + 触发工具发现）
       ↑
run_agent.py，cli.py，batch_runner.py，environments/
```

---

## AIAgent 类 (run_agent.py)

```python
class AIAgent:
    def __init__(self,
        model: str = "anthropic/claude-opus-4.6",
        max_iterations: int = 90,
        enabled_toolsets: list = None,
        disabled_toolsets: list = None,
        quiet_mode: bool = False,
        save_trajectories: bool = False,
        platform: str = None,           # "cli"，"telegram" 等
        session_id: str = None,
        skip_context_files: bool = False,
        skip_memory: bool = False,
        # ... 加上 provider，api_mode，callbacks，routing 参数
    ): ...

    def chat(self, message: str) -> str:
        """简单接口 — 返回最终响应字符串。"""

    def run_conversation(self, user_message: str, system_message: str = None,
                         conversation_history: list = None, task_id: str = None) -> dict:
        """完整接口 — 返回包含 final_response + messages 的字典。"""
```

### Agent 循环

核心循环在 `run_conversation()` 内部 — 完全同步：

```python
while api_call_count < self.max_iterations and self.iteration_budget.remaining > 0:
    response = client.chat.completions.create(model=model, messages=messages, tools=tool_schemas)
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = handle_function_call(tool_call.name, tool_call.args, task_id)
            messages.append(tool_result_message(result))
        api_call_count += 1
    else:
        return response.content
```
消息遵循 OpenAI 格式：`{"role": "system/user/assistant/tool", ...}`。推理内容存储在 `assistant_msg["reasoning"]` 中。

---

## CLI 架构 (cli.py)

- **Rich** 用于横幅/面板，**prompt_toolkit** 用于带自动补全的输入
- **KawaiiSpinner** (`agent/display.py`) — API 调用期间的动画表情，`┊` 活动流用于显示工具结果
- `load_cli_config()` 在 cli.py 中合并硬编码的默认值 + 用户配置 YAML
- **皮肤引擎** (`hermes_cli/skin_engine.py`) — 数据驱动的 CLI 主题；启动时从 `display.skin` 配置键初始化；皮肤可自定义横幅颜色、旋转器表情/动词/翅膀、工具前缀、响应框、品牌文本
- `process_command()` 是 `HermesCLI` 上的一个方法 — 根据通过中央注册表的 `resolve_command()` 解析出的规范命令名进行分发
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
- `gateway_config_gate` — 配置点路径（例如 `"display.tool_progress_command"`）；当在 `cli_only` 命令上设置此值时，如果配置值为真，则该命令在消息网关中变为可用。`GATEWAY_KNOWN_COMMANDS` 始终包含配置门控命令，以便消息网关可以分发它们；帮助/菜单仅在门控打开时显示它们。

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

---

## 添加新工具

需要在 **2 个文件** 中进行更改：

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
**2. 添加到 `toolsets.py`** — 可以是 `_HERMES_CORE_TOOLS`（所有平台）或一个新的工具集。

自动发现：任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入 —— 无需维护手动导入列表。

注册表负责模式收集、分发、可用性检查和错误包装。所有处理程序**必须**返回一个 JSON 字符串。

**工具模式中的路径引用**：如果模式描述中提到文件路径（例如默认输出目录），请使用 `display_hermes_home()` 使其感知配置文件。模式在导入时生成，这是在 `_apply_profile_override()` 设置 `HERMES_HOME` 之后。

**状态文件**：如果工具存储持久状态（缓存、日志、检查点），请使用 `get_hermes_home()` 作为基础目录 —— 切勿使用 `Path.home() / ".hermes"`。这确保每个配置文件都有自己的状态。

**Agent 级工具**（待办事项、记忆）：在 `handle_function_call()` 之前被 `run_agent.py` 拦截。请参阅 `todo_tool.py` 了解模式。

---

## 添加配置

### config.yaml 选项：
1. 添加到 `hermes_cli/config.py` 中的 `DEFAULT_CONFIG`
2. 增加 `_config_version`（当前为 5）以触发现有用户的迁移

### .env 变量：
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

### 配置加载器（两个独立的系统）：

| 加载器 | 使用者 | 位置 |
|--------|---------|----------|
| `load_cli_config()` | CLI 模式 | `cli.py` |
| `load_config()` | `hermes tools`, `hermes setup` | `hermes_cli/config.py` |
| 直接 YAML 加载 | 消息网关 | `gateway/run.py` |

---

## 皮肤/主题系统

皮肤引擎 (`hermes_cli/skin_engine.py`) 提供数据驱动的 CLI 视觉自定义。皮肤是**纯数据** —— 添加新皮肤无需更改代码。

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

### 皮肤自定义的内容

| 元素 | 皮肤键 | 使用者 |
|---------|----------|---------|
| 横幅面板边框 | `colors.banner_border` | `banner.py` |
| 横幅面板标题 | `colors.banner_title` | `banner.py` |
| 横幅部分标题 | `colors.banner_accent` | `banner.py` |
| 横幅暗淡文本 | `colors.banner_dim` | `banner.py` |
| 横幅正文文本 | `colors.banner_text` | `banner.py` |
| 响应框边框 | `colors.response_border` | `cli.py` |
| 旋转器表情（等待） | `spinner.waiting_faces` | `display.py` |
| 旋转器表情（思考） | `spinner.thinking_faces` | `display.py` |
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
- `slate` — 以开发者为中心的酷蓝色主题

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
  thinking_verbs: ["接入中", "解密中", "上传中"]
  wings:
    - ["⟨⚡", "⚡⟩"]

branding:
  agent_name: "赛博 Agent"
  response_label: " ⚡ 赛博 "

tool_prefix: "▏"
```

通过 `/skin cyberpunk` 或在 config.yaml 中设置 `display.skin: cyberpunk` 来激活。

---

## 重要策略
### 提示词缓存不得破坏

Hermes-Agent 确保缓存在整个对话中保持有效。**请勿实施会导致以下情况的更改：**
- 在对话中途更改过去的上下文
- 在对话中途更改工具集
- 在对话中途重新加载记忆或重建系统提示词

破坏缓存会导致成本急剧增加。我们更改上下文的**唯一**时机是在上下文压缩期间。

### 工作目录行为
- **CLI**：使用当前目录 (`.` → `os.getcwd()`)
- **消息传递**：使用 `MESSAGING_CWD` 环境变量（默认：主目录）

### 后台进程通知（消息网关）

当使用 `terminal(background=true, notify_on_complete=true)` 时，消息网关会运行一个监视器，检测进程完成并触发新的 Agent 回合。通过 config.yaml 中的 `display.background_process_notifications`（或 `HERMES_BACKGROUND_NOTIFICATIONS` 环境变量）控制后台进程消息的详细程度：

- `all` — 运行输出更新 + 最终消息（默认）
- `result` — 仅最终完成消息
- `error` — 仅当退出码 != 0 时的最终消息
- `off` — 完全没有监视器消息

---

## 配置文件：多实例支持

Hermes 支持**配置文件** —— 多个完全隔离的实例，每个实例都有自己的 `HERMES_HOME` 目录（配置、API 密钥、记忆、会话、技能、消息网关等）。

核心机制：`hermes_cli/main.py` 中的 `_apply_profile_override()` 在任何模块导入之前设置 `HERMES_HOME`。所有 119+ 个对 `get_hermes_home()` 的引用都会自动限定到活动配置文件的范围。
### 配置文件安全的代码规则

1. **对所有 HERMES_HOME 路径使用 `get_hermes_home()`**。从 `hermes_constants` 导入。
   在读取/写入状态的代码中，**绝对不要**硬编码 `~/.hermes` 或 `Path.home() / ".hermes"`。
   ```python
   # 正确
   from hermes_constants import get_hermes_home
   config_path = get_hermes_home() / "config.yaml"

   # 错误 — 会破坏配置文件功能
   config_path = Path.home() / ".hermes" / "config.yaml"
   ```

2. **面向用户的消息使用 `display_hermes_home()`**。从 `hermes_constants` 导入。
   对于默认配置，它返回 `~/.hermes`；对于配置文件，它返回 `~/.hermes/profiles/<name>`。
   ```python
   # 正确
   from hermes_constants import display_hermes_home
   print(f"配置已保存到 {display_hermes_home()}/config.yaml")

   # 错误 — 对于配置文件会显示错误的路径
   print("配置已保存到 ~/.hermes/config.yaml")
   ```

3. **模块级常量没问题** — 它们在导入时缓存 `get_hermes_home()`，这是在 `_apply_profile_override()` 设置环境变量**之后**。只需使用 `get_hermes_home()`，而不是 `Path.home() / ".hermes"`。

4. **模拟 `Path.home()` 的测试也必须设置 `HERMES_HOME`** — 因为代码现在使用 `get_hermes_home()`（读取环境变量），而不是 `Path.home() / ".hermes"`：
   ```python
   with patch.object(Path, "home", return_value=tmp_path), \
        patch.dict(os.environ, {"HERMES_HOME": str(tmp_path / ".hermes")}):
       ...
   ```

5. **消息网关平台适配器应使用 Token 锁** — 如果适配器使用唯一凭证（机器人 Token、API 密钥）进行连接，请在 `connect()`/`start()` 方法中调用 `gateway.status` 中的 `acquire_scoped_lock()`，并在 `disconnect()`/`stop()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件使用相同的凭证。
   请参阅 `gateway/platforms/telegram.py` 中的规范模式。

6. **配置文件操作以 HOME 为锚点，而不是 HERMES_HOME** — `_get_profiles_root()` 返回 `Path.home() / ".hermes" / "profiles"`，**而不是** `get_hermes_home() / "profiles"`。
   这是有意为之的 — 它允许 `hermes -p coder profile list` 查看所有配置文件，无论哪个配置文件处于活动状态。

## 已知陷阱

### 绝对不要硬编码 `~/.hermes` 路径
对于代码路径，使用 `hermes_constants` 中的 `get_hermes_home()`。对于面向用户的打印/日志消息，使用 `display_hermes_home()`。
硬编码 `~/.hermes` 会破坏配置文件功能 — 每个配置文件都有自己的 `HERMES_HOME` 目录。这是在 PR #3575 中修复的 5 个错误的根源。

### 绝对不要使用 `simple_term_menu` 进行交互式菜单
在 tmux/iTerm2 中存在渲染错误 — 滚动时出现重影。请改用 `curses`（标准库）。请参阅 `hermes_cli/tools_config.py` 中的模式。

### 绝对不要在 spinner/display 代码中使用 `\033[K`（ANSI 清除到行尾）
在 `prompt_toolkit` 的 `patch_stdout` 下会泄漏为字面文本 `?[K`。请使用空格填充：`f"\r{line}{' ' * pad}"`。

### `_last_resolved_tool_names` 是 `model_tools.py` 中的一个进程全局变量
`delegate_tool.py` 中的 `_run_single_child()` 在子 Agent 执行期间保存和恢复此全局变量。如果你添加读取此全局变量的新代码，请注意在子 Agent 运行期间它可能暂时是过时的。

### 绝对不要在模式描述中硬编码跨工具引用
工具模式描述**不得**按名称提及来自其他工具集的工具（例如，`browser_navigate` 说“首选 web_search”）。这些工具可能不可用（缺少 API 密钥、工具集被禁用），导致模型幻觉式地调用不存在的工具。如果需要交叉引用，请在 `model_tools.py` 的 `get_tool_definitions()` 中动态添加 — 请参阅 `browser_navigate` / `execute_code` 后处理块的模式。

### 测试不得写入 `~/.hermes/`
`tests/conftest.py` 中的 `_isolate_hermes_home` 自动使用夹具将 `HERMES_HOME` 重定向到临时目录。在测试中绝对不要硬编码 `~/.hermes/` 路径。

**配置文件测试**：测试配置文件功能时，也要模拟 `Path.home()`，以便 `_get_profiles_root()` 和 `_get_default_hermes_home()` 在临时目录内解析。
使用 `tests/hermes_cli/test_profiles.py` 中的模式：
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

**始终使用 `scripts/run_tests.sh`** — 不要直接调用 `pytest`。该脚本强制执行与 CI 一致的无环境（取消设置凭证变量、TZ=UTC、LANG=C.UTF-8、4 个 xdist 工作进程匹配 GHA ubuntu-latest）。在设置了 API 密钥的 16+ 核开发机器上直接运行 `pytest` 会与 CI 产生差异，这已导致多起“本地工作，CI 失败”事件（反之亦然）。

```bash
scripts/run_tests.sh                                  # 完整套件，与 CI 一致
scripts/run_tests.sh tests/gateway/                   # 一个目录
scripts/run_tests.sh tests/agent/test_foo.py::test_x  # 一个测试
scripts/run_tests.sh -v --tb=long                     # 透传 pytest 标志
```

### 为什么需要包装器（以及为什么旧的“直接调用 pytest”行不通）

该脚本消除了五个导致本地与 CI 差异的真实来源：

| | 不使用包装器 | 使用包装器 |
|---|---|---|
| 提供商 API 密钥 | 环境中已有的任何内容（自动检测池） | 所有 `*_API_KEY`/`*_TOKEN`/等 均被取消设置 |
| HOME / `~/.hermes/` | 你的真实 config+auth.json | 每个测试一个临时目录 |
| 时区 | 本地时区（PDT 等） | UTC |
| 区域设置 | 已设置的任何内容 | C.UTF-8 |
| xdist 工作进程 | `-n auto` = 所有核心（工作站上 20+） | `-n 4` 匹配 CI |

`tests/conftest.py` 还通过一个自动使用夹具强制执行第 1-4 点，因此**任何** pytest 调用（包括 IDE 集成）都会获得无环境行为 — 但包装器是双重保险。

### 不使用包装器运行（仅在必须时）

如果无法使用包装器（例如在 Windows 上或在直接 shell 执行 pytest 的 IDE 内部），至少激活虚拟环境并传递 `-n 4`：

```bash
source venv/bin/activate
python -m pytest tests/ -q -n 4
```

工作进程数超过 4 会暴露出 CI 从未见过的测试顺序不稳定性问题。
在推送更改前始终运行完整的测试套件。

### 不要编写变更检测器测试

如果一个测试在**预期会变化**的数据更新时就会失败——例如模型目录、配置版本号、枚举计数、硬编码的提供商模型列表——那么它就是一个**变更检测器**。这些测试没有提供任何行为覆盖；它们只是保证常规的源码更新会破坏 CI，并耗费工程时间来“修复”。

**不要编写：**

```python
# 目录快照 —— 每次模型发布都会失败
assert "gemini-2.5-pro" in _PROVIDER_MODELS["gemini"]
assert "MiniMax-M2.7" in models

# 配置版本字面量 —— 每次模式升级都会失败
assert DEFAULT_CONFIG["_config_version"] == 21

# 枚举计数 —— 每次添加技能/提供商时都会失败
assert len(_PROVIDER_MODELS["huggingface"]) == 8
```

**应该编写：**

```python
# 行为：目录管道是否正常工作？
assert "gemini" in _PROVIDER_MODELS
assert len(_PROVIDER_MODELS["gemini"]) >= 1

# 行为：迁移是否将用户的版本更新到当前最新版本？
assert raw["_config_version"] == DEFAULT_CONFIG["_config_version"]

# 不变量：没有仅用于计划的模型泄漏到旧列表中
assert not (set(moonshot_models) & coding_plan_only_models)

# 不变量：目录中的每个模型都有上下文长度条目
for m in _PROVIDER_MODELS["huggingface"]:
    assert m.lower() in DEFAULT_CONTEXT_LENGTHS_LOWER
```

规则是：如果测试读起来像是当前数据的快照，就删除它。如果它读起来像是关于两段数据必须如何关联的契约，就保留它。当 PR 添加新的提供商/模型并且你想要一个测试时，让测试断言这种关系（例如“所有目录条目都有上下文长度”），而不是具体的名称。

审阅者应拒绝新的变更检测器测试；作者应在重新请求审阅前将其转换为不变量测试。