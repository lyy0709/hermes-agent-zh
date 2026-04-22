---
sidebar_position: 12
sidebar_label: "内置插件"
title: "内置插件"
description: "随 Hermes Agent 一同发布的插件，通过生命周期钩子自动运行——磁盘清理等"
---

# 内置插件

Hermes 随仓库捆绑发布了一小部分插件。它们位于 `<repo>/plugins/<name>/` 目录下，并与用户安装在 `~/.hermes/plugins/` 中的插件一同自动加载。它们使用与第三方插件相同的插件接口——钩子、工具、斜杠命令——只是维护在代码库内。

关于通用插件系统，请参阅[插件](/docs/user-guide/features/plugins)页面；要编写自己的插件，请参阅[构建 Hermes 插件](/docs/guides/build-a-hermes-plugin)。

## 发现机制如何工作

`PluginManager` 按顺序扫描四个来源：

1.  **捆绑插件** — `<repo>/plugins/<name>/`（本文档所描述的内容）
2.  **用户插件** — `~/.hermes/plugins/<name>/`
3.  **项目插件** — `./.hermes/plugins/<name>/`（需要设置 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4.  **Pip 入口点** — `hermes_agent.plugins`

当名称冲突时，后扫描的来源会覆盖先前的——例如，一个名为 `disk-cleanup` 的用户插件会替换掉捆绑的同名插件。

`plugins/memory/` 和 `plugins/context_engine/` 目录被特意排除在捆绑插件扫描之外。这些目录使用它们自己的发现路径，因为记忆提供商和上下文引擎是通过配置中的 `hermes memory setup` / `context.engine` 配置的单选提供商。

## 捆绑插件需手动启用

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

这与用户安装的插件使用的机制相同。捆绑插件永远不会自动启用——无论是全新安装，还是现有用户升级到更新的 Hermes 版本。你总是需要明确选择启用。

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
| `post_tool_call` | 当 `write_file` / `terminal` / `patch` 在 `HERMES_HOME` 或 `/tmp/hermes-*` 内创建匹配 `test_*`、`tmp_*` 或 `*.test.*` 的文件时，将其静默跟踪为 `test` / `temp` / `cron-output` 类别。 |
| `on_session_end` | 如果在当前轮次中有任何测试文件被自动跟踪，则运行安全的 `quick` 清理并记录一行摘要。否则保持静默。 |

**删除规则：**

| 类别 | 阈值 | 确认 |
|---|---|---|
| `test` | 每次会话结束时 | 从不 |
| `temp` | 自跟踪起 >7 天 | 从不 |
| `cron-output` | 自跟踪起 >14 天 | 从不 |
| HERMES_HOME 下的空目录 | 总是 | 从不 |
| `research` | >30 天，且超出最新的 10 个 | 总是（仅 deep 模式） |
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
| `tracked.json` | 跟踪的路径及其类别、大小和时间戳 |
| `tracked.json.bak` | 上述文件的原子写入备份 |
| `cleanup.log` | 每次跟踪/跳过/拒绝/删除的仅追加审计日志 |

**安全性** — 清理操作只处理 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径。Windows 挂载点（`/mnt/c/...`）会被拒绝。已知的顶级状态目录（`logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/`、`plugins/`、`disk-cleanup/` 自身）即使为空也永远不会被删除——这样新安装的系统不会在第一次会话结束时就被清空。

**启用：** `hermes plugins enable disk-cleanup`（或在 `hermes plugins` 中勾选复选框）。

**再次禁用：** `hermes plugins disable disk-cleanup`。

## 添加捆绑插件

捆绑插件的编写方式与任何其他 Hermes 插件完全相同——请参阅[构建 Hermes 插件](/docs/guides/build-a-hermes-plugin)。唯一的区别是：

-   目录位于 `<repo>/plugins/<name>/` 而不是 `~/.hermes/plugins/<name>/`
-   在 `hermes plugins list` 中，清单来源报告为 `bundled`
-   同名用户插件会覆盖捆绑版本

一个插件适合捆绑发布，当：

-   它没有可选的依赖项（或者其依赖项已经是 `pip install .[all]` 的依赖）
-   其行为对大多数用户有益，并且是“选择退出”而非“选择加入”
-   其逻辑与生命周期钩子紧密相关，否则 Agent 需要记住去调用这些钩子
-   它补充了核心功能，但没有扩展模型可见的工具接口

反例——应保持为用户可安装插件，而非捆绑发布：需要 API 密钥的第三方集成、小众工作流、依赖树庞大、任何会默认显著改变 Agent 行为的东西。