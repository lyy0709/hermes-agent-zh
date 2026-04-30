---
title: "调试 Hermes TUI 命令 — 调试 Hermes TUI 斜杠命令：Python、消息网关、Ink UI"
sidebar_label: "调试 Hermes TUI 命令"
description: "调试 Hermes TUI 斜杠命令：Python、消息网关、Ink UI"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 调试 Hermes TUI 命令

调试 Hermes TUI 斜杠命令：Python、消息网关、Ink UI。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/debugging-hermes-tui-commands` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `debugging`, `hermes-agent`, `tui`, `slash-commands`, `typescript`, `python` |
| 相关技能 | [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy), [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 调试 Hermes TUI 斜杠命令

## 概述

Hermes 斜杠命令跨越三个层次 —— Python 命令注册表、tui_gateway JSON-RPC 桥接器，以及 Ink/TypeScript 前端。当命令行为异常时（自动补全中缺失、在 CLI 中工作但在 TUI 中不工作、配置持久化但 UI 不更新），问题几乎总是某一层与其他层不同步。

当你在 Hermes TUI 中遇到斜杠命令问题时，请使用此技能，特别是当命令未在自动补全中显示、在 TUI 中无法正常工作或需要添加/更新时。

## 使用时机

- 斜杠命令存在于代码库的某一部分但无法完全工作
- 需要向后端和前端同时添加命令
- 特定命令的自动补全功能失效
- CLI 和 TUI 之间的命令行为不一致
- 命令持久化了配置但未在 TUI 中实时应用

## 架构概述

<!-- ascii-guard-ignore -->
```
Python 后端 (hermes_cli/commands.py)     <- 权威的 COMMAND_REGISTRY
       │
       ▼
TUI 消息网关 (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI 前端 (ui-tui/src/app/slash/)        <- 本地处理器 + 回退处理
```
<!-- ascii-guard-ignore-end -->

命令定义必须在 Python 和 TypeScript 中一致地注册才能正常工作。Python 的 `COMMAND_REGISTRY` 是以下内容的单一事实来源：CLI 分发、消息网关帮助、Telegram BotCommand 菜单、Slack 子命令映射，以及发送给 Ink 的自动补全数据。

## 调查步骤

1. **检查命令是否存在于 TUI 前端：**
   ```bash
   search_files --pattern "/commandname" --file_glob "*.ts" --path ui-tui/
   search_files --pattern "/commandname" --file_glob "*.tsx" --path ui-tui/
   ```

2. **检查 TUI 命令定义：**
   ```bash
   read_file ui-tui/src/app/slash/commands/core.ts
   # 如果不在那里：
   search_files --pattern "commandname" --path ui-tui/src/app/slash/commands --target files
   ```

3. **检查命令是否存在于 Python 后端：**
   ```bash
   search_files --pattern "CommandDef" --file_glob "*.py" --path hermes_cli/
   search_files --pattern "commandname" --path hermes_cli/commands.py --context 3
   ```

4. **检查消息网关实现：**
   ```bash
   search_files --pattern "complete.slash|slash.exec" --path tui_gateway/
   ```

## 修复：缺失的命令自动补全

如果命令存在于 TUI 但未在自动补全中显示：

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加一个 `CommandDef` 条目：
   ```python
   CommandDef("commandname", "命令描述", "Session",
              cli_only=True, aliases=("alias",),
              args_hint="[arg1|arg2|arg3]",
              subcommands=("arg1", "arg2", "arg3")),
   ```

2. 仔细选择 `cli_only` 与消息网关可用性：
   - `cli_only=True` —— 仅在交互式 CLI/TUI 中可用
   - `gateway_only=True` —— 仅在消息平台中可用
   - 两者都不设置 —— 在所有地方都可用
   - `gateway_config_gate="display.foo"` —— 在消息网关中受配置门控的可用性

3. 确保 `subcommands` 与 TUI 显示的预期 Tab 补全选项匹配。

4. 如果命令在服务器端运行，在 `cli.py` 的 `HermesCLI.process_command()` 中添加一个处理器：
   ```python
   elif canonical == "commandname":
       self._handle_commandname(cmd_original)
   ```

5. 对于消息网关可用的命令，在 `gateway/run.py` 中添加一个处理器：
   ```python
   if canonical == "commandname":
       return await self._handle_commandname(event)
   ```

## 常见问题

1. **命令在 TUI 中显示但不在自动补全中。** 命令在 TUI 代码库中定义，但缺失于 `hermes_cli/commands.py` 中的 `COMMAND_REGISTRY`。自动补全数据从 Python 端发送。

2. **命令在自动补全中显示但不工作。** 检查 `tui_gateway/server.py` 中的命令处理器和 `ui-tui/src/app/createSlashHandler.ts` 中的前端处理器。如果命令在 Ink 中是本地唯一的，它必须在 `app.tsx` 的内置分支中处理；否则它会回退到 `slash.exec` 并且必须有一个 Python 处理器。

3. **CLI 和 TUI 之间的命令行为不同。** 命令可能有不同的实现。同时检查 `cli.py::process_command` 和 TUI 的本地处理器。本地 TUI 处理器优先于消息网关分发。

4. **命令持久化了配置但未实时应用。** 对于 TUI 本地命令，仅更新 `config.set` 是不够的。还需要立即修补相关的 nanostore 状态（通常是 `patchUiState(...)`），并将任何新状态传递给渲染组件。例如：`/details collapsed` 必须实时更新详情可见性，而不仅仅是保存 `details_mode`；会话内的全局 `/details <mode>` 可能需要一个单独的命令覆盖标志，以便实时命令可以覆盖内置部分的默认值，同时启动/配置同步保留默认展开的思考/工具行为。

5. **消息网关分发静默忽略命令。** 消息网关只分发它知道的命令。检查 `GATEWAY_KNOWN_COMMANDS`（自动从 `COMMAND_REGISTRY` 派生）是否包含规范名称。如果命令是带有 `gateway_config_gate` 的 `cli_only`，请验证门控配置值为真。

## 调试策略

当表面检查无法揭示错误时：

- **Python 端挂起或行为异常：** 使用 `python-debugpy` 技能在 `_SlashWorker.exec` 或命令处理器内部设置断点。在处理器入口处设置 `remote-pdb` 是最快的途径。
- **Ink 端无反应：** 使用 `node-inspect-debugger` 技能在 `app.tsx` 的斜杠分发或本地命令分支中设置断点。在 `npm run build` 之后使用 `sb('dist/app.js', <line>)`。
- **注册表不匹配 / 不清楚哪一侧出错：** 将规范的 `COMMAND_REGISTRY` 条目与 TUI 的本地命令列表并排比较。

## 陷阱

- 不要忘记在 `CommandDef` 中为命令设置适当的类别（例如，"Session"、"Configuration"、"Tools & Skills"、"Info"、"Exit"）
- 确保任何别名都正确注册在 `aliases` 元组中 —— 不需要其他文件更改，所有下游（Telegram 菜单、Slack 映射、自动补全、帮助）都从中派生
- 对于带有子命令的命令，确保 `CommandDef` 中的 `subcommands` 元组与 TUI 代码中的内容匹配
- `cli_only=True` 的命令在消息网关/消息平台中不起作用 —— 除非你添加一个 `gateway_config_gate` 并且门控为真
- 添加实时 UI 状态后，搜索旧属性/助手的每个消费者，并将新状态传递到所有渲染路径，而不仅仅是活动的流式路径。TUI 详情渲染至少有两个重要路径：实时的 `StreamingAssistant`/`ToolTrail` 和转录/待处理的 `MessageLine` 行。一次 `/clean` 过程应明确检查两者。
- 在测试前重新构建 TUI（`npm --prefix ui-tui run build`）—— tsx 监视模式在首次启动时可能滞后

## 验证

修复后：

1. 重新构建 TUI：
   ```bash
   cd /home/bb/hermes-agent && npm --prefix ui-tui run build
   ```

2. 运行 TUI 并测试命令：
   ```bash
   hermes --tui
   ```

3. 输入 `/` 并验证命令出现在自动补全建议中，并带有预期的描述和参数提示。

4. 执行命令并确认：
   - 触发预期行为
   - 任何持久化的配置都正确更新（`read_file ~/.hermes/config.yaml`）
   - 实时 UI 状态立即反映更改（不仅仅是重启后）

5. 如果命令在消息网关也可用，请至少从一个消息平台测试它（或运行消息网关测试：`scripts/run_tests.sh tests/gateway/`）。