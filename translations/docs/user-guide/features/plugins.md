---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统使用自定义工具、钩子和集成来扩展 Hermes"
---

# 插件

Hermes 拥有一个插件系统，可以在不修改核心代码的情况下添加自定义工具、钩子和集成。

**→ [构建 Hermes 插件](/docs/guides/build-a-hermes-plugin)** — 包含完整工作示例的逐步指南。

## 快速概览

将一个包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/`：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单
├── __init__.py      # register() — 将模式连接到处理器
├── schemas.py       # 工具模式（LLM 看到的内容）
└── tools.py         # 工具处理器（调用时运行的内容）
```

启动 Hermes — 你的工具将与内置工具一同出现。模型可以立即调用它们。

### 最小工作示例

这是一个完整的插件，它添加了一个 `hello_world` 工具，并通过钩子记录每次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: A minimal example plugin
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""Minimal Hermes plugin — registers a tool and a hook."""


def register(ctx):
    # --- Tool: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "Returns a friendly greeting for the given name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                }
            },
            "required": ["name"],
        },
    }

    def handle_hello(params):
        name = params.get("name", "World")
        return f"Hello, {name}! 👋  (from the hello-world plugin)"

    ctx.register_tool("hello_world", schema, handle_hello)

    # --- Hook: log every tool call ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型就可以立即调用 `hello_world`。该钩子会在每次工具调用后打印一行日志。

项目本地插件（位于 `./.hermes/plugins/` 下）默认是禁用的。只有在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`，才能为受信任的仓库启用它们。

## 插件能做什么

| 能力 | 方法 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` — 在 CLI 和消息网关会话中添加 `/name` |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes <plugin> <subcommand>` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见 [注入消息](#injecting-messages) |
| 提供数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 捆绑技能 | `ctx.register_skill(name, path)` — 以 `plugin:skill` 命名空间化，通过 `skill_view("plugin:skill")` 加载 |
| 环境变量门控 | 在 plugin.yaml 中使用 `requires_env: [API_KEY]` — 在 `hermes plugins install` 期间提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |

## 插件发现

| 来源 | 路径 | 用例 |
|--------|------|----------|
| 捆绑插件 | `<repo>/plugins/` | 随 Hermes 发布 — 参见 [内置插件](/docs/user-guide/features/built-in-plugins) |
| 用户插件 | `~/.hermes/plugins/` | 个人插件 |
| 项目插件 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip 插件 | `hermes_agent.plugins` entry_points | 分发包 |
| Nix 插件 | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装 — 参见 [Nix 设置](/docs/getting-started/nix-setup#plugins) |

当名称冲突时，后发现的源会覆盖先发现的源，因此与捆绑插件同名的用户插件会替换它。

## 插件采用选择加入机制

**每个插件 — 无论是用户安装的、捆绑的还是 pip 安装的 — 默认都是禁用的。** 发现机制会找到它们（因此它们会出现在 `hermes plugins` 和 `/plugins` 中），但在你将插件名称添加到 `~/.hermes/config.yaml` 中的 `plugins.enabled` 之前，不会加载任何内容。这可以防止任何带有钩子或工具的内容在你明确同意之前运行。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # 可选的拒绝列表 — 如果名称同时出现在两者中，则始终优先
    - noisy-plugin
```

三种切换状态的方式：

```bash
hermes plugins                    # 交互式切换（空格键勾选/取消勾选）
hermes plugins enable <name>      # 添加到允许列表
hermes plugins disable <name>     # 从允许列表中移除 + 添加到禁用列表
```

在 `hermes plugins install owner/repo` 之后，系统会询问 `Enable 'name' now? [y/N]` — 默认为否。对于脚本化安装，可以使用 `--enable` 或 `--no-enable` 跳过提示。

### 现有用户的迁移

当你升级到具有选择加入插件功能的 Hermes 版本（配置模式 v21+）时，任何已安装在 `~/.hermes/plugins/` 下且尚未在 `plugins.disabled` 中的用户插件，将**自动被保留**到 `plugins.enabled` 中。你现有的设置将继续工作。捆绑插件**不会**被保留 — 即使是现有用户也必须明确选择加入。

## 可用的钩子

插件可以为这些生命周期事件注册回调。有关完整详细信息、回调签名和示例，请参见 **[事件钩子页面](/docs/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/docs/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 |
| [`post_tool_call`](/docs/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 |
| [`pre_llm_call`](/docs/user-guide/features/hooks#pre_llm_call) | 每轮一次，在 LLM 循环之前 — 可以返回 `{"context": "..."}` 以 [将上下文注入到用户消息中](/docs/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/docs/user-guide/features/hooks#post_llm_call) | 每轮一次，在 LLM 循环之后（仅限成功的轮次） |
| [`on_session_start`](/docs/user-guide/features/hooks#on_session_start) | 新会话创建时（仅限第一轮） |
| [`on_session_end`](/docs/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理器 |
| [`pre_gateway_dispatch`](/docs/user-guide/features/hooks#pre_gateway_dispatch) | 消息网关收到用户消息后，在认证 + 分发之前。返回 `{"action": "skip" \| "rewrite" \| "allow", ...}` 以影响流程。 |

## 插件类型

Hermes 有三种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **记忆提供商** | 替换或增强内置记忆 | 单选（一个激活） | `plugins/memory/` |
| **上下文引擎** | 替换内置的上下文压缩器 | 单选（一个激活） | `plugins/context_engine/` |

记忆提供商和上下文引擎是**提供商插件** — 每种类型一次只能激活一个。通用插件可以以任意组合启用。

## NixOS 声明式插件

在 NixOS 上，可以通过模块选项声明式地安装插件 — 无需 `hermes plugins install`。完整详情请参见 **[Nix 设置指南](/docs/getting-started/nix-setup#plugins)**。

```nix
services.hermes-agent = {
  # 目录插件（包含 plugin.yaml 的源码树）
  extraPlugins = [ (pkgs.fetchFromGitHub { ... }) ];
  # 入口点插件（pip 包）
  extraPythonPackages = [ (pkgs.python312Packages.buildPythonPackage { ... }) ];
  # 在配置中启用
  settings.plugins.enabled = [ "my-plugin" ];
};
```

声明式插件以 `nix-managed-` 前缀符号链接 — 它们与手动安装的插件共存，并在从 Nix 配置中移除时自动清理。

## 管理插件

```bash
hermes plugins                               # 统一的交互式 UI
hermes plugins list                          # 表格：已启用 / 已禁用 / 未启用
hermes plugins install user/repo             # 从 Git 安装，然后提示 Enable? [y/N]
hermes plugins install user/repo --enable    # 安装并启用（无提示）
hermes plugins install user/repo --no-enable # 安装但保持禁用（无提示）
hermes plugins update my-plugin              # 拉取最新版本
hermes plugins remove my-plugin              # 卸载
hermes plugins enable my-plugin              # 添加到允许列表
hermes plugins disable my-plugin             # 从允许列表中移除 + 添加到禁用列表
```

### 交互式 UI

不带参数运行 `hermes plugins` 会打开一个复合交互式屏幕：

```
Plugins
  ↑↓ navigate  SPACE toggle  ENTER configure/confirm  ESC done

  General Plugins
 → [✓] my-tool-plugin — Custom search tool
   [ ] webhook-notifier — Event hooks
   [ ] disk-cleanup — Auto-cleanup of ephemeral files [bundled]

  Provider Plugins
     Memory Provider          ▸ honcho
     Context Engine           ▸ compressor
```

- **通用插件部分** — 复选框，用 SPACE 切换。勾选 = 在 `plugins.enabled` 中，未勾选 = 在 `plugins.disabled` 中（明确关闭）。
- **提供商插件部分** — 显示当前选择。按 ENTER 进入单选选择器，在那里选择一个激活的提供商。
- 捆绑插件以 `[bundled]` 标签出现在同一列表中。

提供商插件的选择会保存到 `config.yaml`：

```yaml
memory:
  provider: "honcho"      # 空字符串 = 仅内置

context:
  engine: "compressor"    # 默认内置压缩器
```

### 已启用 vs. 已禁用 vs. 未启用

插件处于以下三种状态之一：

| 状态 | 含义 | 在 `plugins.enabled` 中？ | 在 `plugins.disabled` 中？ |
|---|---|---|---|
| `enabled` | 在下一个会话中加载 | 是 | 否 |
| `disabled` | 明确关闭 — 即使也在 `enabled` 中也不会加载 | （无关） | 是 |
| `not enabled` | 已发现但从未选择加入 | 否 | 否 |

新安装或捆绑插件的默认状态是 `not enabled`。`hermes plugins list` 显示所有三种不同的状态，以便你能区分哪些是明确关闭的，哪些只是等待启用。

在运行中的会话中，`/plugins` 显示当前加载了哪些插件。

## 注入消息

插件可以使用 `ctx.inject_message()` 将消息注入到活跃的对话中：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于**空闲**状态（等待用户输入），消息将作为下一个输入排队并开始新一轮对话。
- 如果 Agent 处于**对话中**（正在主动运行），消息会中断当前操作 — 就像用户输入新消息并按 Enter 键一样。
- 对于非 `"user"` 的角色，内容会加上 `[role]` 前缀（例如 `[system] ...`）。
- 如果消息成功排队则返回 `True`，如果没有可用的 CLI 引用（例如在消息网关模式下）则返回 `False`。

这使得像远程控制查看器、消息桥接器或 Webhook 接收器这样的插件能够从外部源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在消息网关模式下，没有 CLI 引用，该方法返回 `False`。
:::

有关处理器契约、模式格式、钩子行为、错误处理和常见错误的详细信息，请参见 **[完整指南](/docs/guides/build-a-hermes-plugin)**。