# Hermes Agent - 开发指南

为 AI 编码助手和开发 Hermes Agent 代码库的开发者提供的说明。

## 开发环境

```bash
source venv/bin/activate  # 运行 Python 前务必激活
```

## 项目结构

```
hermes-agent/
├── run_agent.py          # AIAgent 类 — 核心对话循环
├── model_tools.py        # 工具编排，_discover_tools()，handle_function_call()
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
│   ├── callbacks.py      # 终端回调（澄清、sudo、批准）
│   ├── setup.py          # 交互式设置向导
│   ├── skin_engine.py    # 皮肤/主题引擎 — CLI 视觉定制
│   ├── skills_config.py  # `hermes skills` — 按平台启用/禁用技能
│   ├── tools_config.py   # `hermes tools` — 按平台启用/禁用工具
│   ├── skills_hub.py     # `/skills` 斜杠命令（搜索、浏览、安装）
│   ├── models.py         # 模型目录，提供商模型列表
│   ├── model_switch.py   # 共享的 /model 切换流水线（CLI + 消息网关）
│   └── auth.py           # 提供商凭证解析
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
├── gateway/              # 消息平台网关
│   ├── run.py            # 主循环，斜杠命令，消息分发
│   ├── session.py        # SessionStore — 对话持久化
│   └── platforms/        # 适配器：telegram、discord、slack、whatsapp、homeassistant、signal
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
model_tools.py  （导入 tools/registry 并触发工具发现）
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
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
        platform: str = None,           # "cli", "telegram" 等
        session_id: str = None,
        skip_context_files: bool = False,
        skip_memory: bool = False,
        # ... 加上 provider, api_mode, callbacks, routing 参数
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
- **KawaiiSpinner** (`agent/display.py`) — API 调用期间的动画表情，工具结果的 `┊` 活动流
- cli.py 中的 `load_cli_config()` 合并硬编码默认值 + 用户配置 YAML
- **皮肤引擎** (`hermes_cli/skin_engine.py`) — 数据驱动的 CLI 主题；在启动时从 `display.skin` 配置键初始化；皮肤自定义横幅颜色、spinner 表情/动词/翅膀、工具前缀、响应框、品牌文本
- `process_command()` 是 `HermesCLI` 上的一个方法 — 根据通过中央注册表的 `resolve_command()` 解析出的规范命令名进行分发
- 技能斜杠命令：`agent/skill_commands.py` 扫描 `~/.hermes/skills/`，作为**用户消息**（非系统提示词）注入以保留提示词缓存
### 斜杠命令注册表 (`hermes_cli/commands.py`)

所有斜杠命令都在一个中心的 `COMMAND_REGISTRY` 列表中定义，该列表包含 `CommandDef` 对象。所有下游消费者都自动从这个注册表派生：

- **CLI** — `process_command()` 通过 `resolve_command()` 解析别名，根据规范名称进行分发
- **消息网关** — `GATEWAY_KNOWN_COMMANDS` 冻结集用于钩子触发，`resolve_command()` 用于分发
- **消息网关帮助** — `gateway_help_lines()` 生成 `/help` 输出
- **Telegram** — `telegram_bot_commands()` 生成 BotCommand 菜单
- **Slack** — `slack_subcommand_map()` 生成 `/hermes` 子命令路由
- **自动补全** — `COMMANDS` 平面字典提供给 `SlashCommandCompleter`
- **CLI 帮助** — `COMMANDS_BY_CATEGORY` 字典提供给 `show_help()`

### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加一个 `CommandDef` 条目：
```python
CommandDef("mycommand", "描述它的功能", "Session",
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
4. 对于持久化设置，在 `cli.py` 中使用 `save_config_value()`

**CommandDef 字段：**
- `name` — 不带斜杠的规范名称（例如 `"background"`）
- `description` — 人类可读的描述
- `category` — 其中之一：`"Session"`、`"Configuration"`、`"Tools & Skills"`、`"Info"`、`"Exit"`
- `aliases` — 替代名称的元组（例如 `("bg",)`）
- `args_hint` — 在帮助中显示的参数占位符（例如 `"<prompt>"`、`"[name]"`）
- `cli_only` — 仅在交互式 CLI 中可用
- `gateway_only` — 仅在消息平台上可用
- `gateway_config_gate` — 配置点路径（例如 `"display.tool_progress_command"`）；当在 `cli_only` 命令上设置时，如果配置值为真，则该命令在消息网关中变为可用。`GATEWAY_KNOWN_COMMANDS` 始终包含配置门控命令，以便消息网关可以分发它们；帮助/菜单仅在门打开时显示它们。

**添加别名** 只需要将其添加到现有 `CommandDef` 的 `aliases` 元组中。无需其他文件更改 — 分发、帮助文本、Telegram 菜单、Slack 映射和自动补全都会自动更新。

---

## 添加新工具

需要在 **3 个文件** 中进行更改：

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

**2. 在 `model_tools.py` 的 `_discover_tools()` 列表中添加导入。**

**3. 添加到 `toolsets.py`** — 要么是 `_HERMES_CORE_TOOLS`（所有平台），要么是一个新的工具集。

注册表处理模式收集、分发、可用性检查和错误包装。所有处理程序**必须**返回一个 JSON 字符串。

**工具模式中的路径引用**：如果模式描述提到文件路径（例如默认输出目录），请使用 `display_hermes_home()` 使其感知配置文件。模式在导入时生成，这是在 `_apply_profile_override()` 设置 `HERMES_HOME` 之后。

**状态文件**：如果一个工具存储持久状态（缓存、日志、检查点），请使用 `get_hermes_home()` 作为基础目录 — 永远不要使用 `Path.home() / ".hermes"`。这确保每个配置文件都有自己的状态。

**Agent 级工具**（待办事项、记忆）：在 `handle_function_call()` 之前被 `run_agent.py` 拦截。请参阅 `todo_tool.py` 了解模式。

---

## 添加配置

### config.yaml 选项：
1. 添加到 `hermes_cli/config.py` 中的 `DEFAULT_CONFIG`
2. 增加 `_config_version`（当前为 5）以触发现有用户的迁移

### .env 变量：
1. 在 `hermes_cli/config.py` 的 `OPTIONAL_ENV_VARS` 中添加元数据：
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

皮肤引擎 (`hermes_cli/skin_engine.py`) 提供数据驱动的 CLI 视觉定制。皮肤是**纯数据** — 添加新皮肤无需更改代码。

### 架构

```
hermes_cli/skin_engine.py    # SkinConfig 数据类，内置皮肤，YAML 加载器
~/.hermes/skins/*.yaml       # 用户安装的自定义皮肤（即插即用）
```

- `init_skin_from_config()` — 在 CLI 启动时调用，从配置中读取 `display.skin`
- `get_active_skin()` — 返回当前皮肤的缓存 `SkinConfig`
- `set_active_skin(name)` — 在运行时切换皮肤（由 `/skin` 命令使用）
- `load_skin(name)` — 首先从用户皮肤加载，然后从内置皮肤加载，最后回退到默认皮肤
- 缺失的皮肤值会自动从 `default` 皮肤继承

### 皮肤定制的内容

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
| 每个工具的 emoji | `tool_emojis` | `display.py` → `get_tool_emoji()` |
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

### 用户皮肤（YAML）

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

## 重要策略
### 提示词缓存不得中断

Hermes-Agent 确保缓存在整个会话中保持有效。**请勿实施会导致以下情况的更改：**
- 在会话中途更改过去的上下文
- 在会话中途更改工具集
- 在会话中途重新加载记忆或重建系统提示词

缓存中断会导致成本急剧增加。我们更改上下文的唯一时机是在上下文压缩期间。

### 工作目录行为
- **CLI**：使用当前目录（`.` → `os.getcwd()`）
- **消息传递**：使用 `MESSAGING_CWD` 环境变量（默认：主目录）

### 后台进程通知（消息网关）

当使用 `terminal(background=true, notify_on_complete=true)` 时，消息网关会运行一个监视器来检测进程完成并触发新的 Agent 轮次。通过 config.yaml 中的 `display.background_process_notifications`（或 `HERMES_BACKGROUND_NOTIFICATIONS` 环境变量）控制后台进程消息的详细程度：

- `all` — 运行输出更新 + 最终消息（默认）
- `result` — 仅最终完成消息
- `error` — 仅当退出码 != 0 时的最终消息
- `off` — 完全没有监视器消息

---

## 配置文件：多实例支持

Hermes 支持**配置文件**——多个完全隔离的实例，每个实例都有自己的 `HERMES_HOME` 目录（配置、API 密钥、记忆、会话、技能、消息网关等）。

核心机制：`hermes_cli/main.py` 中的 `_apply_profile_override()` 在任何模块导入之前设置 `HERMES_HOME`。所有 119+ 处对 `get_hermes_home()` 的引用都会自动限定到活动配置文件的范围。

### 配置文件安全代码规则

1.  **所有 HERMES_HOME 路径都使用 `get_hermes_home()`。** 从 `hermes_constants` 导入。在读取/写入状态的代码中，切勿硬编码 `~/.hermes` 或 `Path.home() / ".hermes"`。
    ```python
    # 正确
    from hermes_constants import get_hermes_home
    config_path = get_hermes_home() / "config.yaml"

    # 错误 — 破坏配置文件
    config_path = Path.home() / ".hermes" / "config.yaml"
    ```

2.  **面向用户的消息使用 `display_hermes_home()`。** 从 `hermes_constants` 导入。对于默认配置，它返回 `~/.hermes`；对于配置文件，它返回 `~/.hermes/profiles/<name>`。
    ```python
    # 正确
    from hermes_constants import display_hermes_home
    print(f"配置已保存到 {display_hermes_home()}/config.yaml")

    # 错误 — 为配置文件显示错误的路径
    print("配置已保存到 ~/.hermes/config.yaml")
    ```

3.  **模块级常量没问题**——它们在导入时缓存 `get_hermes_home()`，这是在 `_apply_profile_override()` 设置环境变量**之后**。只需使用 `get_hermes_home()`，而不是 `Path.home() / ".hermes"`。

4.  **模拟 `Path.home()` 的测试也必须设置 `HERMES_HOME`**——因为代码现在使用 `get_hermes_home()`（读取环境变量），而不是 `Path.home() / ".hermes"`：
    ```python
    with patch.object(Path, "home", return_value=tmp_path), \
         patch.dict(os.environ, {"HERMES_HOME": str(tmp_path / ".hermes")}):
        ...
    ```

5.  **消息网关平台适配器应使用令牌锁**——如果适配器使用唯一凭据（机器人令牌、API 密钥）连接，请在 `connect()`/`start()` 方法中调用 `gateway.status` 中的 `acquire_scoped_lock()`，并在 `disconnect()`/`stop()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件使用相同的凭据。请参阅 `gateway/platforms/telegram.py` 了解规范模式。

6.  **配置文件操作以 HOME 为锚点，而不是 HERMES_HOME**——`_get_profiles_root()` 返回 `Path.home() / ".hermes" / "profiles"`，而不是 `get_hermes_home() / "profiles"`。这是有意为之——它允许 `hermes -p coder profile list` 查看所有配置文件，无论哪个配置文件处于活动状态。

## 已知陷阱

### 请勿硬编码 `~/.hermes` 路径
代码路径使用 `hermes_constants` 中的 `get_hermes_home()`。面向用户的打印/日志消息使用 `display_hermes_home()`。硬编码 `~/.hermes` 会破坏配置文件——每个配置文件都有自己的 `HERMES_HOME` 目录。这是 PR #3575 中修复的 5 个错误的根源。

### 请勿在交互式菜单中使用 `simple_term_menu`
在 tmux/iTerm2 中存在渲染错误——滚动时出现重影。请改用 `curses`（标准库）。请参阅 `hermes_cli/tools_config.py` 了解模式。

### 请勿在旋转器/显示代码中使用 `\033[K`（ANSI 清除到行尾）
在 `prompt_toolkit` 的 `patch_stdout` 下会泄漏为字面文本 `?[K`。请使用空格填充：`f"\r{line}{' ' * pad}"`。

### `_last_resolved_tool_names` 是 `model_tools.py` 中的一个进程全局变量
`delegate_tool.py` 中的 `_run_single_child()` 在子 Agent 执行期间保存和恢复此全局变量。如果你添加读取此全局变量的新代码，请注意它在子 Agent 运行期间可能暂时过时。

### 请勿在模式描述中硬编码跨工具引用
工具模式描述不得按名称提及来自其他工具集的工具（例如，`browser_navigate` 说“首选 web_search”）。这些工具可能不可用（缺少 API 密钥、工具集被禁用），导致模型产生幻觉，调用不存在的工具。如果需要交叉引用，请在 `model_tools.py` 的 `get_tool_definitions()` 中动态添加——请参阅 `browser_navigate` / `execute_code` 后处理块了解模式。
### 测试禁止写入 `~/.hermes/`
`tests/conftest.py` 中的 `_isolate_hermes_home` 自动使用夹具会将 `HERMES_HOME` 重定向到一个临时目录。测试中切勿硬编码 `~/.hermes/` 路径。

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

```bash
source venv/bin/activate
python -m pytest tests/ -q          # 完整测试套件（约 3000 个测试，约 3 分钟）
python -m pytest tests/test_model_tools.py -q   # 工具集解析
python -m pytest tests/test_cli_init.py -q       # CLI 配置加载
python -m pytest tests/gateway/ -q               # 消息网关测试
python -m pytest tests/tools/ -q                 # 工具级别测试
```

推送更改前务必运行完整测试套件。