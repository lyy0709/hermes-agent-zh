---
sidebar_position: 8
title: "记忆提供商插件"
description: "如何为 Hermes Agent 构建记忆提供商插件"
---

# 构建记忆提供商插件

记忆提供商插件为 Hermes Agent 提供超越内置 MEMORY.md 和 USER.md 的持久化、跨会话知识。本指南介绍如何构建一个。

:::tip
记忆提供商是两种**提供商插件**类型之一。另一种是[上下文引擎插件](/docs/developer-guide/context-engine-plugin)，用于替换内置的上下文压缩器。两者遵循相同的模式：单选、配置驱动、通过 `hermes plugins` 管理。
:::

## 目录结构

每个记忆提供商位于 `plugins/memory/<name>/`：

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider 实现 + register() 入口点
├── plugin.yaml      # 元数据（名称、描述、钩子）
└── README.md        # 设置说明、配置参考、工具
```

## MemoryProvider 抽象基类

你的插件需要实现来自 `agent/memory_provider.py` 的 `MemoryProvider` 抽象基类：

```python
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-provider"

    def is_available(self) -> bool:
        """检查此提供商是否可以激活。不进行网络调用。"""
        return bool(os.environ.get("MY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        """在 Agent 启动时调用一次。

        kwargs 始终包含：
          hermes_home (str): 活动的 HERMES_HOME 路径。用于存储。
        """
        self._api_key = os.environ.get("MY_API_KEY", "")
        self._session_id = session_id

    # ... 实现剩余方法
```

## 必需方法

### 核心生命周期

| 方法 | 调用时机 | 必须实现？ |
|--------|-----------|-----------------|
| `name` (属性) | 始终 | **是** |
| `is_available()` | Agent 初始化，激活之前 | **是** — 不进行网络调用 |
| `initialize(session_id, **kwargs)` | Agent 启动时 | **是** |
| `get_tool_schemas()` | 初始化后，用于工具注入 | **是** |
| `handle_tool_call(name, args)` | 当 Agent 使用你的工具时 | **是**（如果你有工具） |

### 配置

| 方法 | 目的 | 必须实现？ |
|--------|---------|-----------------|
| `get_config_schema()` | 为 `hermes memory setup` 声明配置字段 | **是** |
| `save_config(values, hermes_home)` | 将非机密配置写入原生位置 | **是**（除非仅使用环境变量） |

### 可选钩子

| 方法 | 调用时机 | 使用场景 |
|--------|-----------|----------|
| `system_prompt_block()` | 系统提示词组装时 | 静态提供商信息 |
| `prefetch(query)` | 每次 API 调用前 | 返回回忆的上下文 |
| `queue_prefetch(query)` | 每次轮次后 | 为下一轮次预热 |
| `sync_turn(user, assistant)` | 每次完成的轮次后 | 持久化对话 |
| `on_session_end(messages)` | 对话结束时 | 最终提取/刷新 |
| `on_pre_compress(messages)` | 上下文压缩前 | 在丢弃前保存洞察 |
| `on_memory_write(action, target, content)` | 内置记忆写入时 | 镜像到你的后端 |
| `shutdown()` | 进程退出时 | 清理连接 |

## 配置模式

`get_config_schema()` 返回一个字段描述符列表，供 `hermes memory setup` 使用：

```python
def get_config_schema(self):
    return [
        {
            "key": "api_key",
            "description": "My Provider API 密钥",
            "secret": True,           # → 写入 .env
            "required": True,
            "env_var": "MY_API_KEY",   # 显式环境变量名
            "url": "https://my-provider.com/keys",  # 获取位置
        },
        {
            "key": "region",
            "description": "服务器区域",
            "default": "us-east",
            "choices": ["us-east", "eu-west", "ap-south"],
        },
        {
            "key": "project",
            "description": "项目标识符",
            "default": "hermes",
        },
    ]
```

带有 `secret: True` 和 `env_var` 的字段会进入 `.env`。非机密字段会传递给 `save_config()`。

:::tip 最小化与完整模式
`get_config_schema()` 中的每个字段都会在 `hermes memory setup` 期间被提示。具有许多选项的提供商应保持模式最小化 — 仅包含用户**必须**配置的字段（API 密钥、必需凭据）。在配置文件参考（例如 `$HERMES_HOME/myprovider.json`）中记录可选设置，而不是在设置期间提示所有选项。这可以保持设置向导快速，同时仍支持高级配置。请参阅 Supermemory 提供商的示例 — 它只提示 API 密钥；所有其他选项都位于 `supermemory.json` 中。
:::

## 保存配置

```python
def save_config(self, values: dict, hermes_home: str) -> None:
    """将非机密配置写入你的原生位置。"""
    import json
    from pathlib import Path
    config_path = Path(hermes_home) / "my-provider.json"
    config_path.write_text(json.dumps(values, indent=2))
```

对于仅使用环境变量的提供商，保留默认的无操作实现。

## 插件入口点

```python
def register(ctx) -> None:
    """由记忆插件发现系统调用。"""
    ctx.register_memory_provider(MyMemoryProvider())
```

## plugin.yaml

```yaml
name: my-provider
version: 1.0.0
description: "此提供商功能的简短描述。"
hooks:
  - on_session_end    # 列出你实现的钩子
```

## 线程契约

**`sync_turn()` 必须是非阻塞的。** 如果你的后端有延迟（API 调用、LLM 处理），请在守护线程中运行工作：

```python
def sync_turn(self, user_content, assistant_content):
    def _sync():
        try:
            self._api.ingest(user_content, assistant_content)
        except Exception as e:
            logger.warning("同步失败: %s", e)

    if self._sync_thread and self._sync_thread.is_alive():
        self._sync_thread.join(timeout=5.0)
    self._sync_thread = threading.Thread(target=_sync, daemon=True)
    self._sync_thread.start()
```

## 配置文件隔离

所有存储路径**必须**使用来自 `initialize()` 的 `hermes_home` kwarg，而不是硬编码的 `~/.hermes`：

```python
# 正确 — 配置文件作用域
from hermes_constants import get_hermes_home
data_dir = get_hermes_home() / "my-provider"

# 错误 — 在所有配置文件间共享
data_dir = Path("~/.hermes/my-provider").expanduser()
```

## 测试

请参阅 `tests/agent/test_memory_plugin_e2e.py` 了解使用真实 SQLite 提供商的完整端到端测试模式。

```python
from agent.memory_manager import MemoryManager

mgr = MemoryManager()
mgr.add_provider(my_provider)
mgr.initialize_all(session_id="test-1", platform="cli")

# 测试工具路由
result = mgr.handle_tool_call("my_tool", {"action": "add", "content": "test"})

# 测试生命周期
mgr.sync_all("user msg", "assistant msg")
mgr.on_session_end([])
mgr.shutdown_all()
```

## 添加 CLI 命令

记忆提供商插件可以注册自己的 CLI 子命令树（例如 `hermes my-provider status`、`hermes my-provider config`）。这使用基于约定的发现系统 — 无需更改核心文件。

### 工作原理

1. 在你的插件目录中添加一个 `cli.py` 文件
2. 定义一个 `register_cli(subparser)` 函数来构建 argparse 树
3. 记忆插件系统在启动时通过 `discover_plugin_cli_commands()` 发现它
4. 你的命令将出现在 `hermes <provider-name> <subcommand>` 下

**活动提供商门控：** 只有当你的提供商是配置中活动的 `memory.provider` 时，你的 CLI 命令才会出现。如果用户尚未配置你的提供商，你的命令将不会显示在 `hermes --help` 中。

### 示例

```python
# plugins/memory/my-provider/cli.py

def my_command(args):
    """由 argparse 分发的处理器。"""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("提供商处于活动状态并已连接。")
    elif sub == "config":
        print("显示配置...")
    else:
        print("用法: hermes my-provider <status|config>")

def register_cli(subparser) -> None:
    """构建 hermes my-provider argparse 树。

    在 argparse 设置时由 discover_plugin_cli_commands() 调用。
    """
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="显示提供商状态")
    subs.add_parser("config", help="显示提供商配置")
    subparser.set_defaults(func=my_command)
```

### 参考实现

请参阅 `plugins/memory/honcho/cli.py` 获取完整示例，包含 13 个子命令、跨配置文件管理（`--target-profile`）和配置读写。

### 包含 CLI 的目录结构

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider 实现 + register()
├── plugin.yaml      # 元数据
├── cli.py           # register_cli(subparser) — CLI 命令
└── README.md        # 设置说明
```

## 单一提供商规则

一次只能有一个外部记忆提供商处于活动状态。如果用户尝试注册第二个，MemoryManager 会拒绝并发出警告。这可以防止工具模式膨胀和后台冲突。