---
sidebar_position: 12
sidebar_label: "内置插件"
title: "内置插件"
description: "随 Hermes Agent 一同发布的插件，通过生命周期钩子自动运行——磁盘清理等插件"
---

# 内置插件

Hermes 随仓库捆绑发布了一小部分插件。它们位于 `<repo>/plugins/<name>/` 目录下，并与用户安装在 `~/.hermes/plugins/` 中的插件一同自动加载。它们使用与第三方插件相同的插件接口——钩子、工具、斜杠命令——只是维护在代码树内。

关于通用插件系统，请参阅[插件](/docs/user-guide/features/plugins)页面；要编写自己的插件，请参阅[构建 Hermes 插件](/docs/guides/build-a-hermes-plugin)。

## 发现机制如何工作

`PluginManager` 按顺序扫描四个来源：

1.  **捆绑插件** — `<repo>/plugins/<name>/`（本文档所描述的内容）
2.  **用户插件** — `~/.hermes/plugins/<name>/`
3.  **项目插件** — `./.hermes/plugins/<name>/`（需要设置 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4.  **Pip 入口点** — `hermes_agent.plugins`

当名称冲突时，后扫描的来源会覆盖先前的——一个名为 `disk-cleanup` 的用户插件将替换掉捆绑的版本。

`plugins/memory/` 和 `plugins/context_engine/` 被特意排除在捆绑插件扫描之外。这些目录使用它们自己的发现路径，因为记忆提供商和上下文引擎是通过配置中的 `hermes memory setup` / `context.engine` 配置的单选提供商。

## 捆绑插件需要手动启用

捆绑插件在发布时是禁用的。发现机制能找到它们（它们会出现在 `hermes plugins list` 和交互式 `hermes plugins` UI 中），但在你明确启用之前，它们都不会加载：

```bash
hermes plugins enable disk-cleanup
```

或者通过 `~/.hermes/config.yaml`：

```yaml
plugins:
  enabled:
    - disk-cleanup
```

这与用户安装的插件使用的机制相同。捆绑插件永远不会自动启用——无论是全新安装，还是现有用户升级到新版 Hermes。你总是需要明确选择启用。

要再次关闭一个捆绑插件：

```bash
hermes plugins disable disk-cleanup
# 或者：从 config.yaml 的 plugins.enabled 中移除它
```

## 当前已发布的插件

### disk-cleanup

自动跟踪并删除会话期间创建的临时文件——测试脚本、临时输出、定时任务日志、过时的 Chrome 配置文件——无需 Agent 记住去调用工具。

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `post_tool_call` | 当 `write_file` / `terminal` / `patch` 在 `HERMES_HOME` 或 `/tmp/hermes-*` 内创建匹配 `test_*`、`tmp_*` 或 `*.test.*` 的文件时，将其静默跟踪为 `test` / `temp` / `cron-output`。 |
| `on_session_end` | 如果在当前轮次中有任何测试文件被自动跟踪，则运行安全的 `quick` 清理并记录一行摘要。否则保持静默。 |

**删除规则：**

| 类别 | 阈值 | 确认 |
|---|---|---|
| `test` | 每次会话结束时 | 从不 |
| `temp` | 自跟踪起 >7 天 | 从不 |
| `cron-output` | 自跟踪起 >14 天 | 从不 |
| HERMES_HOME 下的空目录 | 总是 | 从不 |
| `research` | >30 天，保留最新的 10 个 | 总是（仅 deep 模式） |
| `chrome-profile` | 自跟踪起 >14 天 | 总是（仅 deep 模式） |
| 文件 >500 MB | 从不自动 | 总是（仅 deep 模式） |

**斜杠命令** — `/disk-cleanup` 在 CLI 和消息网关会话中均可用：

```
/disk-cleanup status                     # 分类统计 + 前 10 个最大文件
/disk-cleanup dry-run                    # 预览而不删除
/disk-cleanup quick                      # 立即运行安全清理
/disk-cleanup deep                       # quick + 列出需要确认的项目
/disk-cleanup track <路径> <类别>        # 手动跟踪
/disk-cleanup forget <路径>              # 停止跟踪（不删除）
```

**状态** — 所有内容都位于 `$HERMES_HOME/disk-cleanup/`：

| 文件 | 内容 |
|---|---|
| `tracked.json` | 跟踪的路径，包含类别、大小和时间戳 |
| `tracked.json.bak` | 上述文件的原子写入备份 |
| `cleanup.log` | 仅追加的审计日志，记录每次跟踪/跳过/拒绝/删除 |

**安全性** — 清理操作只触及 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径。Windows 挂载点（`/mnt/c/...`）会被拒绝。众所周知的一级状态目录（`logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/`、`plugins/`、`disk-cleanup/` 自身）即使为空也永远不会被删除——全新安装不会在第一次会话结束时被清空。

**启用：** `hermes plugins enable disk-cleanup`（或在 `hermes plugins` 中勾选复选框）。

**再次禁用：** `hermes plugins disable disk-cleanup`。

### observability/langfuse

将 Hermes 轮次、LLM 调用和工具调用追踪到 [Langfuse](https://langfuse.com)——一个开源的 LLM 可观测性平台。每个轮次一个跨度，每次 API 调用一个生成记录，每次工具调用一个工具观察记录。使用总量、按类型的 Token 计数和成本估算来自 Hermes 规范的 `agent.usage_pricing` 数据，因此 Langfuse 仪表板看到的分类（输入/输出/`cache_read_input_tokens`/`cache_creation_input_tokens`/`reasoning_tokens`）与 `hermes logs` 中显示的相同。

该插件采用故障开放策略：未安装 SDK、无凭据或 Langfuse 暂时性错误——所有这些都会在钩子中转为静默的无操作。Agent 循环永远不会受到影响。

**设置（交互式——推荐）：**

```bash
hermes tools          # → Langfuse Observability → Cloud or Self-Hosted
```

向导会收集你的密钥，`pip install` 安装 `langfuse` SDK，并为你将 `observability/langfuse` 添加到 `plugins.enabled`。重启 Hermes，下一个轮次就会发送追踪记录。

**设置（手动）：**

```bash
pip install langfuse
hermes plugins enable observability/langfuse
```

然后将凭据放入 `~/.hermes/.env`：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # 或你的自托管 URL
```

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `pre_api_request` / `pre_llm_call` | 打开（或重用）一个每轮次的根跨度 "Hermes turn"。为此 API 调用启动一个 `generation` 子观察记录，并将序列化的最近消息作为输入。 |
| `post_api_request` / `post_llm_call` | 关闭生成记录，附加 `usage_details`、`cost_details`、`finish_reason`、助手输出 + 工具调用。如果没有工具调用且内容非空，则关闭轮次。 |
| `pre_tool_call` | 启动一个 `tool` 子观察记录，包含清理后的 `args`。 |
| `post_tool_call` | 关闭工具观察记录，包含清理后的 `result`。`read_file` 的负载会被摘要化（头部 + 尾部 + 省略行数），以便巨大的文件读取保持在 `HERMES_LANGFUSE_MAX_CHARS` 限制内。 |

会话分组通过 `langfuse.propagate_attributes` 使用 Hermes 会话 ID（或子 Agent 的任务 ID）作为键，因此单个 `hermes chat` 会话中的所有内容都位于一个 Langfuse 会话下。

**验证：**

```bash
hermes plugins list                 # observability/langfuse 应显示 "enabled"
hermes chat -q "hello"              # 在 Langfuse UI 中检查 "Hermes turn" 追踪记录
```

**可选调优**（在 `.env` 中）：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | 追踪记录上的环境标签（`production`、`staging`、…） |
| `HERMES_LANGFUSE_RELEASE` | — | 发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | 传递给 SDK 的采样率（0.0–1.0） |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | 消息内容/工具参数/工具结果的每字段截断长度 |
| `HERMES_LANGFUSE_DEBUG` | `false` | 详细的插件日志记录到 `agent.log` |

Hermes 前缀和标准 SDK 环境变量（`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY`、`LANGFUSE_BASE_URL`）都被接受——当两者都设置时，Hermes 前缀的变量优先。

**性能：** Langfuse 客户端在第一次钩子调用后被缓存。如果凭据或 SDK 缺失，该决定也会被缓存——后续的钩子会快速返回，而无需重新检查环境变量或重新加载配置。

**禁用：** `hermes plugins disable observability/langfuse`。插件模块仍会被发现，但在你重新启用之前，不会运行任何模块代码。

## 添加捆绑插件

捆绑插件的编写方式与任何其他 Hermes 插件完全相同——请参阅[构建 Hermes 插件](/docs/guides/build-a-hermes-plugin)。唯一的区别是：

-   目录位于 `<repo>/plugins/<name>/` 而不是 `~/.hermes/plugins/<name>/`
-   在 `hermes plugins list` 中，清单来源报告为 `bundled`
-   同名的用户插件会覆盖捆绑版本

一个插件适合捆绑的条件是：

-   它没有可选的依赖项（或者它们已经是 `pip install .[all]` 的依赖项）
-   其行为对大多数用户有益，并且是选择退出而非选择加入
-   其逻辑与生命周期钩子绑定，否则 Agent 需要记住去调用这些钩子
-   它补充了核心功能，而没有扩展模型可见的工具接口

反例——应保持为用户可安装插件，而非捆绑的：需要 API 密钥的第三方集成、小众工作流、大型依赖树、任何会默认显著改变 Agent 行为的东西。