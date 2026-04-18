---
sidebar_position: 2
title: "TUI"
description: "启动 Hermes 的现代化终端用户界面——支持鼠标操作、丰富的覆盖层和非阻塞输入。"
---

# TUI

TUI 是 Hermes 的现代化前端——一个由与 [经典 CLI](cli.md) 相同的 Python 运行时支持的终端用户界面。相同的 Agent、相同的会话、相同的斜杠命令；一个更简洁、响应更迅速的交互界面。

这是交互式运行 Hermes 的推荐方式。

## 启动

```bash
# 启动 TUI
hermes --tui

# 恢复最新的 TUI 会话（如果不存在则回退到最新的经典会话）
hermes --tui -c
hermes --tui --continue

# 通过 ID 或标题恢复特定会话
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

# 直接运行源代码——跳过预构建步骤（供 TUI 贡献者使用）
hermes --tui --dev
```

你也可以通过环境变量启用它：

```bash
export HERMES_TUI=1
hermes          # 现在使用 TUI
hermes chat     # 同上
```

经典 CLI 仍作为默认选项可用。[CLI 界面](cli.md) 中记录的所有内容——斜杠命令、快速命令、技能预加载、人格、多行输入、中断——在 TUI 中同样有效。

## 为什么选择 TUI

- **即时首帧渲染**——横幅在应用完成加载前就已绘制，因此在 Hermes 启动时，终端永远不会感觉卡顿。
- **非阻塞输入**——在会话准备就绪前即可输入并排队消息。你的第一条提示词会在 Agent 上线时立即发送。
- **丰富的覆盖层**——模型选择器、会话选择器、批准和澄清提示都以模态面板而非内联流程的形式呈现。
- **实时会话面板**——工具和技能在初始化过程中逐步填充。
- **支持鼠标的文本选择**——通过拖拽以统一背景高亮文本，而非使用 SGR 反色。使用终端的常规复制手势进行复制。
- **备用屏幕渲染**——差异更新意味着流式传输时无闪烁，退出后无滚动历史残留。
- **编辑器辅助功能**——长代码片段的内联粘贴折叠、从剪贴板粘贴图片 (`Alt+V`)、括号粘贴安全保护。

相同的 [皮肤](features/skins.md) 和 [人格](features/personality.md) 同样适用。在会话中使用 `/skin ares`、`/personality pirate` 进行切换，UI 会实时重绘。在 [`example-skin.yaml`](https://github.com/NousResearch/hermes-agent/blob/main/docs/skins/example-skin.yaml) 中，皮肤键被标记为 `(both)`、`(classic)` 或 `(tui)`，以便一目了然地了解其适用范围——TUI 支持横幅调色板、UI 颜色、提示符字形/颜色、会话显示、补全菜单、选择背景色、`tool_prefix` 和 `help_header`。

## 要求

- **Node.js** ≥ 20 —— TUI 作为从 Python CLI 启动的子进程运行。`hermes doctor` 会验证此项。
- **TTY** —— 与经典 CLI 类似，在管道输入或非交互式环境中运行时，会回退到单次查询模式。

首次启动时，Hermes 会将 TUI 的 Node 依赖项安装到 `ui-tui/node_modules`（一次性操作，耗时几秒）。后续启动速度很快。如果你拉取了新的 Hermes 版本，当源代码比分发版本新时，TUI 包会自动重建。

### 外部预构建

分发预构建包的发行版（如 Nix、系统包）可以将 Hermes 指向该包：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录必须包含 `dist/entry.js` 和最新的 `node_modules`。

## 快捷键绑定

快捷键绑定与 [经典 CLI](cli.md#keybindings) 完全一致。唯一的行为差异是：

- **鼠标拖拽** 会以统一的选择背景色高亮文本。
- **`Ctrl+V`** 将剪贴板中的文本直接粘贴到编辑器中；多行粘贴内容会保持在一行，直到你展开它们。
- **斜杠命令自动补全** 会以带有描述的浮动面板形式打开，而非内联下拉列表。

## 斜杠命令

所有斜杠命令功能不变。少数几个是 TUI 特有的——它们会产生更丰富的输出或以覆盖层而非内联面板的形式呈现：

| 命令 | TUI 行为 |
|---------|--------------|
| `/help` | 带有分类命令的覆盖层，支持箭头键导航 |
| `/sessions` | 模态会话选择器——预览、标题、Token 总数、内联恢复 |
| `/model` | 按提供商分组的模态模型选择器，附带成本提示 |
| `/skin` | 实时预览——浏览时应用主题变更 |
| `/details` | 在记录中切换详细的工具调用详情 |
| `/usage` | 丰富的 Token / 成本 / 上下文面板 |

其他所有斜杠命令（包括已安装的技能、快速命令和人格切换）在经典 CLI 和 TUI 中功能相同。请参阅 [斜杠命令参考](../reference/slash-commands.md)。

## 状态栏

TUI 的状态栏实时跟踪 Agent 状态：

| 状态 | 含义 |
|--------|---------|
| `starting agent…` | 会话 ID 已激活；工具和技能仍在启动中。你可以输入——消息会排队并在准备就绪时发送。 |
| `ready` | Agent 空闲，接受输入。 |
| `thinking…` / `running…` | Agent 正在推理或运行工具。 |
| `interrupted` | 当前轮次已被取消；按 Enter 键重新发送。 |
| `forging session…` / `resuming…` | 初始连接或 `--resume` 握手。 |

每个皮肤的状态栏颜色和阈值与经典 CLI 共享——有关自定义设置，请参阅 [皮肤](features/skins.md)。

## 配置

TUI 遵循所有标准的 Hermes 配置：`~/.hermes/config.yaml`、配置文件、人格、皮肤、快速命令、凭证池、记忆提供商、工具/技能启用。不存在 TUI 特定的配置文件。

少数几个键专门用于调整 TUI 界面：

```yaml
display:
  skin: default          # 任何内置或自定义皮肤
  personality: helpful
  details_mode: compact  # 或 "verbose" —— 默认的工具调用详情级别
  mouse_tracking: true   # 如果你的终端与鼠标报告冲突，请禁用此项
```

`/details on` / `/details off` / `/details cycle` 可在运行时切换此设置。

## 会话

会话在 TUI 和经典 CLI 之间共享——两者都写入同一个 `~/.hermes/state.db`。你可以在一个界面中启动会话，在另一个界面中恢复。会话选择器会显示来自两个来源的会话，并带有来源标签。

有关生命周期、搜索、压缩和导出，请参阅 [会话](sessions.md)。

## 恢复到经典 CLI

启动 `hermes`（不带 `--tui`）会保持在经典 CLI。要使机器优先使用 TUI，请在 shell 配置文件中设置 `HERMES_TUI=1`。要恢复，请取消设置。

如果 TUI 启动失败（无 Node、缺少包、TTY 问题），Hermes 会打印诊断信息并回退——而不是让你卡住。

## 另请参阅

- [CLI 界面](cli.md) —— 完整的斜杠命令和快捷键绑定参考（共享）
- [会话](sessions.md) —— 恢复、分支和历史记录
- [皮肤与主题](features/skins.md) —— 自定义横幅、状态栏和覆盖层的主题
- [语音模式](features/voice-mode.md) —— 在两个界面中均有效
- [配置](configuration.md) —— 所有配置键