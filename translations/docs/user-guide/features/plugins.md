---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统，使用自定义工具、钩子和集成来扩展 Hermes"
---

# 插件

Hermes 拥有一个插件系统，用于添加自定义工具、钩子和集成，而无需修改核心代码。

如果你想为自己、你的团队或某个项目创建一个自定义工具，这通常是正确的途径。开发者指南中的[添加工具](/developer-guide/adding-tools)页面是针对位于 `tools/` 和 `toolsets.py` 中的 Hermes 核心内置工具。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** — 包含完整工作示例的逐步指南。

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

import json


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

    def handle_hello(params, **kwargs):
        del kwargs
        name = params.get("name", "World")
        return json.dumps({"success": True, "greeting": f"Hello, {name}!"})

    ctx.register_tool(
        name="hello_world",
        toolset="hello_world",
        schema=schema,
        handler=handle_hello,
        description="Return a friendly greeting for the given name.",
    )

    # --- Hook: log every tool call ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型就可以立即调用 `hello_world`。该钩子会在每次工具调用后打印一行日志。

位于 `./.hermes/plugins/` 下的项目本地插件默认是禁用的。只有在启动 Hermes 之前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`，才能为受信任的仓库启用它们。

## 插件能做什么

以下每个 `ctx.*` API 在插件的 `register(ctx)` 函数内部都可用。

| 功能 | 方法 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name=..., toolset=..., schema=..., handler=...)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` — 在 CLI 和消息网关会话中添加 `/name` |
| 从命令分派工具 | `ctx.dispatch_tool(name, args)` — 调用已注册的工具，并自动连接父 Agent 上下文 |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes <plugin> <subcommand>` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见[注入消息](#injecting-messages) |
| 提供数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 打包技能 | `ctx.register_skill(name, path)` — 以 `plugin:skill` 命名空间，通过 `skill_view("plugin:skill")` 加载 |
| 环境变量门控 | 在 plugin.yaml 中使用 `requires_env: [API_KEY]` — 在 `hermes plugins install` 期间提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |
| 注册消息网关平台（Discord、Telegram、IRC 等） | `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` — 参见[添加平台适配器](/developer-guide/adding-platform-adapters) |
| 注册图像生成后端 | `ctx.register_image_gen_provider(provider)` — 参见[图像生成提供商插件](/developer-guide/image-gen-provider-plugin) |
| 注册视频生成后端 | `ctx.register_video_gen_provider(provider)` — 参见[视频生成提供商插件](/developer-guide/video-gen-provider-plugin) |
| 注册上下文压缩引擎 | `ctx.register_context_engine(engine)` — 参见[上下文引擎插件](/developer-guide/context-engine-plugin) |
| 注册记忆后端 | 在 `plugins/memory/<name>/__init__.py` 中继承 `MemoryProvider` — 参见[记忆提供商插件](/developer-guide/memory-provider-plugin)（使用单独的发现系统） |
| 运行宿主拥有的 LLM 调用 | `ctx.llm.complete(...)` / `ctx.llm.complete_structured(...)` — 借用用户的活动模型和认证进行一次性补全，可选择 JSON 模式验证。参见[插件 LLM 访问](/developer-guide/plugin-llm-access) |
| 注册推理后端（LLM 提供商） | 在 `plugins/model-providers/<name>/__init__.py` 中使用 `register_provider(ProviderProfile(...))` — 参见[模型提供商插件](/developer-guide/model-provider-plugin)（使用单独的发现系统） |

## 插件发现

| 来源 | 路径 | 用例 |
|--------|------|----------|
| 捆绑 | `<repo>/plugins/` | 随 Hermes 一起发布 — 参见[内置插件](/user-guide/features/built-in-plugins) |
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |
| Nix | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装 — 参见[Nix 设置](/getting-started/nix-setup#plugins) |
当名称冲突时，后加载的源会覆盖先加载的源，因此用户插件如果与内置插件同名，则会替换它。

### 插件子类别

在每个源内部，Hermes 还识别子类别目录，这些目录将插件路由到专门的发现系统：

| 子目录 | 包含内容 | 发现系统 |
|---|---|---|
| `plugins/` (根目录) | 通用插件 — 工具、钩子、斜杠命令、CLI 命令、捆绑技能 | `PluginManager` (类型：`standalone` 或 `backend`) |
| `plugins/platforms/<name>/` | 消息网关通道适配器 (`ctx.register_platform()`) | `PluginManager` (类型：`platform`，更深一层) |
| `plugins/image_gen/<name>/` | 图像生成后端 (`ctx.register_image_gen_provider()`) | `PluginManager` (类型：`backend`，更深一层) |
| `plugins/memory/<name>/` | 记忆提供商 (继承 `MemoryProvider`) | **自有加载器**，位于 `plugins/memory/__init__.py` (类型：`exclusive` — 一次只能激活一个) |
| `plugins/context_engine/<name>/` | 上下文压缩引擎 (`ctx.register_context_engine()`) | **自有加载器**，位于 `plugins/context_engine/__init__.py` (一次只能激活一个) |
| `plugins/model-providers/<name>/` | LLM 提供商配置文件 (`register_provider(ProviderProfile(...))`) | **自有加载器**，位于 `providers/__init__.py` (在首次调用 `get_provider_profile()` 时惰性扫描) |

位于 `~/.hermes/plugins/model-providers/<name>/` 和 `~/.hermes/plugins/memory/<name>/` 的用户插件会覆盖同名的捆绑插件 — 在 `register_provider()` / `register_memory_provider()` 中遵循“后写入者胜”原则。只需放入一个目录，它就会替换内置插件，无需编辑仓库。

子类别插件会出现在 `hermes plugins list` 和交互式 `hermes plugins` UI 中，其标识是**基于路径派生的键** — 例如 `observability/langfuse`、`image_gen/openai`、`platforms/teams`。这个键（而不是清单中的 `name:`）是你传递给 `hermes plugins enable …` / `disable …` 的值，也是添加到 `config.yaml` 中 `plugins.enabled` 下的字符串。

## 插件默认需要手动启用（少数例外）

**通用插件和用户安装的后端默认是禁用的** — 发现系统会找到它们（因此它们会出现在 `hermes plugins` 和 `/plugins` 中），但在你将插件名称添加到 `~/.hermes/config.yaml` 的 `plugins.enabled` 之前，任何带有钩子或工具的插件都不会加载。这可以防止未经你明确同意的第三方代码运行。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # 可选的拒绝列表 — 如果名称同时出现在两个列表中，此列表总是优先
    - noisy-plugin
```

三种切换状态的方式：

```bash
hermes plugins                    # 交互式切换（空格键勾选/取消勾选）
hermes plugins enable <name>      # 添加到允许列表
hermes plugins disable <name>     # 从允许列表移除并添加到禁用列表
```

在 `hermes plugins install owner/repo` 之后，系统会询问 `现在启用 'name' 吗？ [y/N]` — 默认不启用。对于脚本化安装，可以使用 `--enable` 或 `--no-enable` 跳过提示。

### 允许列表不控制的内容

有几类插件会绕过 `plugins.enabled` — 它们是 Hermes 内置功能的一部分，如果默认被禁用，会破坏基本功能：

| 插件类型 | 激活方式 |
|---|---|
| **捆绑的平台插件** (IRC、Teams 等，位于 `plugins/platforms/` 下) | 自动加载，以便所有已提供的网关通道都可用。实际通道通过 `config.yaml` 中的 `gateway.platforms.<name>.enabled` 开启。 |
| **捆绑的后端** (图像生成提供商，位于 `plugins/image_gen/` 下等) | 自动加载，以便默认后端“开箱即用”。选择通过 `config.yaml` 中的 `<category>.provider` 进行（例如 `image_gen.provider: openai`）。 |
| **记忆提供商** (`plugins/memory/`) | 全部被发现；通过 `config.yaml` 中的 `memory.provider` 选择激活一个。 |
| **上下文引擎** (`plugins/context_engine/`) | 全部被发现；通过 `config.yaml` 中的 `context.engine` 选择激活一个。 |
| **模型提供商** (`plugins/model-providers/`) | `plugins/model-providers/` 下的所有捆绑提供商在首次调用 `get_provider_profile()` 时被发现并注册。用户通过 `--provider` 或 `config.yaml` 一次选择一个。 |
| **通过 pip 安装的 `backend` 插件** | 通过 `plugins.enabled` 手动启用（与通用插件相同）。 |
| **用户安装的平台** (位于 `~/.hermes/plugins/platforms/` 下) | 通过 `plugins.enabled` 手动启用 — 第三方网关适配器需要明确同意。 |

简而言之：**捆绑的“始终可用”基础设施自动加载；第三方通用插件需要手动启用。** `plugins.enabled` 允许列表是专门为放入 `~/.hermes/plugins/` 的任意代码设置的门槛。

### 现有用户的迁移

当你升级到支持手动启用插件的 Hermes 版本（配置模式 v21+）时，任何已安装在 `~/.hermes/plugins/` 下且未在 `plugins.disabled` 中的用户插件，都会**自动被保留**在 `plugins.enabled` 中。你现有的设置将继续工作。捆绑的独立插件**不会**被保留 — 即使是现有用户也需要明确选择启用。（捆绑的平台/后端插件从来不需要保留，因为它们从未被限制过。）

## 可用的钩子

插件可以为这些生命周期事件注册回调。有关完整详细信息、回调签名和示例，请参阅 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在 LLM 循环之前 — 可以返回 `{"context": "..."}` 来[将上下文注入用户消息](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在 LLM 循环之后（仅限成功的轮次） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅限第一轮） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理程序 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关销毁活动会话时 (`/new`、GC、CLI 退出) |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关交换新的会话键时 (`/new`、`/reset`、`/clear`、空闲轮换) |
| [`subagent_stop`](/user-guide/features/hooks#subagent_stop) | 每次 `delegate_task` 完成后，每个子 Agent 触发一次 |
| [`pre_gateway_dispatch`](/user-guide/features/hooks#pre_gateway_dispatch) | 网关收到用户消息后，在认证 + 分发之前。返回 `{"action": "skip" \| "rewrite" \| "allow", ...}` 来影响流程。 |
## 插件类型

Hermes 有四种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **记忆提供商** | 替换或增强内置记忆 | 单选（一个激活） | `plugins/memory/` |
| **上下文引擎** | 替换内置的上下文压缩器 | 单选（一个激活） | `plugins/context_engine/` |
| **模型提供商** | 声明推理后端（OpenRouter、Anthropic 等） | 多注册，通过 `--provider` / `config.yaml` 选择 | `plugins/model-providers/` |

记忆提供商和上下文引擎是**提供商插件**——每种类型一次只能激活一个。模型提供商也是插件，但可以同时加载多个；用户通过 `--provider` 或 `config.yaml` 一次选择一个。通用插件可以任意组合启用。

## 可插拔接口 — 每种功能的实现方式

上表展示了四种插件类别，但在“通用插件”中，`PluginContext` 暴露了几个不同的扩展点——并且 Hermes 也接受 Python 插件系统之外的扩展（配置驱动的后端、shell 钩子命令、外部服务器等）。使用下表来查找你想构建功能对应的正确文档：

| 想要添加… | 如何实现 | 编写指南 |
|---|---|---|
| LLM 可以调用的**工具** | Python 插件 — `ctx.register_tool()` | [构建 Hermes 插件](/guides/build-a-hermes-plugin) · [添加工具](/developer-guide/adding-tools) |
| **生命周期钩子**（LLM 前/后、会话开始/结束、工具过滤器） | Python 插件 — `ctx.register_hook()` | [钩子参考](/user-guide/features/hooks) · [构建 Hermes 插件](/guides/build-a-hermes-plugin) |
| CLI / 消息网关的**斜杠命令** | Python 插件 — `ctx.register_command()` | [构建 Hermes 插件](/guides/build-a-hermes-plugin) · [扩展 CLI](/developer-guide/extending-the-cli) |
| `hermes <thing>` 的**子命令** | Python 插件 — `ctx.register_cli_command()` | [扩展 CLI](/developer-guide/extending-the-cli) |
| 你的插件附带的捆绑**技能** | Python 插件 — `ctx.register_skill()` | [创建技能](/developer-guide/creating-skills) |
| **推理后端**（LLM 提供商：OpenAI 兼容、Codex、Anthropic-Messages、Bedrock） | 提供商插件 — 在 `plugins/model-providers/<name>/` 中使用 `register_provider(ProviderProfile(...))` | **[模型提供商插件](/developer-guide/model-provider-plugin)** · [添加提供商](/developer-guide/adding-providers) |
| **消息网关通道**（Discord / Telegram / IRC / Teams / 等） | 平台插件 — 在 `plugins/platforms/<name>/` 中使用 `ctx.register_platform()` | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| **记忆后端**（Honcho、Mem0、Supermemory 等） | 记忆插件 — 在 `plugins/memory/<name>/` 中继承 `MemoryProvider` | [记忆提供商插件](/developer-guide/memory-provider-plugin) |
| **上下文压缩策略** | 上下文引擎插件 — `ctx.register_context_engine()` | [上下文引擎插件](/developer-guide/context-engine-plugin) |
| **图像生成后端**（DALL·E、SDXL 等） | 后端插件 — `ctx.register_image_gen_provider()` | [图像生成提供商插件](/developer-guide/image-gen-provider-plugin) |
| **视频生成后端**（Veo、Kling、Pixverse、Grok-Imagine、Runway 等） | 后端插件 — `ctx.register_video_gen_provider()` | [视频生成提供商插件](/developer-guide/video-gen-provider-plugin) |
| **TTS 后端**（任何 CLI — Piper、VoxCPM、Kokoro、xtts、语音克隆脚本等） | 配置驱动（推荐）— 在 `config.yaml` 中的 `tts.providers.<name>` 下声明 `type: command`。或者 Python 后端插件 — 对于需要超过 shell 模板的 Python-SDK / 流式引擎，使用 `ctx.register_tts_provider()`。 | [TTS 设置](/user-guide/features/tts#custom-command-providers) · [Python 插件指南](/user-guide/features/tts#python-plugin-providers) |
| **STT 后端**（任何 CLI — whisper.cpp、自定义 whisper 二进制文件、本地 ASR CLI） | 配置驱动（推荐）— 在 `config.yaml` 中的 `stt.providers.<name>` 下声明 `type: command`，或者为遗留的单命令后门设置 `HERMES_LOCAL_STT_COMMAND`。或者 Python 后端插件 — 对于 Python-SDK 引擎（OpenRouter、SenseAudio、Gemini-STT 等），使用 `ctx.register_transcription_provider()`。 | [STT 设置](/user-guide/features/tts#stt-custom-command-providers) · [Python 插件指南](/user-guide/features/tts#python-plugin-providers-stt) |
| **通过 MCP 的外部工具**（文件系统、GitHub、Linear、Notion、任何 MCP 服务器） | 配置驱动 — 在 `config.yaml` 中声明 `mcp_servers.<name>` 并附带 `command:` / `url:`。Hermes 自动发现服务器的工具并将其与内置工具一起注册。 | [MCP](/user-guide/features/mcp) |
| **额外的技能源**（自定义 GitHub 仓库、私有技能索引） | CLI — `hermes skills tap add <repo>` | [技能中心](/user-guide/features/skills#skills-hub) · [发布自定义 tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| **消息网关事件钩子**（在 `gateway:startup`、`session:start`、`agent:end`、`command:*` 时触发） | 将 `HOOK.yaml` + `handler.py` 放入 `~/.hermes/hooks/<name>/` | [事件钩子](/user-guide/features/hooks#gateway-event-hooks) |
| **Shell 钩子**（在事件上运行 shell 命令 — 通知、审计日志、桌面提醒） | 配置驱动 — 在 `config.yaml` 中的 `hooks:` 下声明 | [Shell 钩子](/user-guide/features/hooks#shell-hooks) |

:::note
并非所有东西都是 Python 插件。一些扩展表面特意使用**配置驱动的 shell 命令**（TTS、STT、shell 钩子），这样你已有的任何 CLI 无需编写 Python 代码即可成为插件。其他是**外部服务器**（MCP），Agent 连接到它们并自动注册其工具。还有一些是**即插即用目录**（消息网关钩子），它们有自己的清单格式。根据你的用例选择合适的集成风格；上表中的编写指南都涵盖了占位符、发现和示例。
:::
## NixOS 声明式插件

在 NixOS 上，可以通过模块选项以声明式方式安装插件——无需使用 `hermes plugins install`。完整细节请参阅 **[Nix 设置指南](/getting-started/nix-setup#plugins)**。

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

声明式插件会以 `nix-managed-` 前缀进行符号链接——它们与手动安装的插件共存，并且当从 Nix 配置中移除时会自动清理。

## 管理插件

```bash
hermes plugins                                       # 统一的交互式 UI
hermes plugins list                                  # 表格：已启用 / 已禁用 / 未启用
hermes plugins install user/repo                     # 从 Git 安装，然后提示 启用？[y/N]
hermes plugins install user/repo --enable            # 安装并启用（无提示）
hermes plugins install user/repo --no-enable         # 安装但保持禁用（无提示）
hermes plugins update my-plugin                      # 拉取最新版本
hermes plugins remove my-plugin                      # 卸载
hermes plugins enable my-plugin                      # 添加到允许列表（扁平插件）
hermes plugins enable observability/langfuse         # 添加到允许列表（子类别插件）
hermes plugins disable my-plugin                     # 从允许列表中移除并添加到禁用列表
```

对于子类别目录下的插件（例如 `plugins/observability/langfuse/`、`plugins/image_gen/openai/`），请使用完整的 `<category>/<plugin>` 键——这正是 `hermes plugins list` 在 **名称** 列中显示的内容。

### 交互式 UI

不带参数运行 `hermes plugins` 会打开一个复合交互式界面：

```
插件
  ↑↓ 导航  SPACE 切换  ENTER 配置/确认  ESC 完成

  通用插件
 → [✓] my-tool-plugin — 自定义搜索工具
   [ ] webhook-notifier — 事件钩子
   [ ] disk-cleanup — 临时文件自动清理 [捆绑]
   [ ] observability/langfuse — 将轮次 / LLM 调用 / 工具追踪到 Langfuse [捆绑]

  提供商插件
     记忆提供商          ▸ honcho
     上下文引擎           ▸ compressor
```

- **通用插件部分** — 复选框，使用 SPACE 切换。勾选 = 在 `plugins.enabled` 中，未勾选 = 在 `plugins.disabled` 中（显式关闭）。
- **提供商插件部分** — 显示当前选择。按 ENTER 进入单选选择器，您可以在其中选择一个活跃的提供商。
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
| `disabled` | 显式关闭——即使在 `enabled` 中也不会加载 | （无关） | 是 |
| `not enabled` | 已发现但从未选择启用 | 否 | 否 |

新安装或捆绑插件的默认状态是 `not enabled`。`hermes plugins list` 会显示所有三种不同的状态，以便您区分哪些是显式关闭的，哪些只是等待启用。

在运行中的会话中，`/plugins` 显示当前加载了哪些插件。

## 注入消息

插件可以使用 `ctx.inject_message()` 将消息注入到活跃的对话中：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于**空闲**状态（等待用户输入），消息将作为下一个输入排队并开始新一轮对话。
- 如果 Agent 处于**对话中**（正在主动运行），消息会中断当前操作——就像用户输入新消息并按 Enter 键一样。
- 对于非 `"user"` 的角色，内容会以 `[role]` 为前缀（例如 `[system] ...`）。
- 如果消息成功排队则返回 `True`，如果没有可用的 CLI 引用（例如在消息网关模式下）则返回 `False`。

这使得远程控制查看器、消息桥接器或 Webhook 接收器等插件能够从外部源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在消息网关模式下，没有 CLI 引用，该方法返回 `False`。
:::

有关处理程序契约、模式格式、钩子行为、错误处理和常见错误的详细信息，请参阅 **[完整指南](/guides/build-a-hermes-plugin)**。