---
title: "Watchers — 通过水位线去重轮询 RSS、JSON API 和 GitHub"
sidebar_label: "Watchers"
description: "通过水位线去重轮询 RSS、JSON API 和 GitHub"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Watchers

通过水位线去重轮询 RSS、JSON API 和 GitHub。

## 技能元数据

| | |
|---|---|
| 来源 | Optional — 使用 `hermes skills install official/devops/watchers` 安装 |
| 路径 | `optional-skills/devops/watchers` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `cron`, `polling`, `rss`, `github`, `http`, `automation`, `monitoring` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Watchers

按时间间隔轮询外部源，并仅对新项目做出反应。包含三个现成的脚本和一个共享的水位线辅助工具；将它们配置到定时任务中（或从终端临时运行）。

## 使用场景

- 用户希望监控 RSS/Atom 源并在有新条目时收到通知
- 用户希望监控 GitHub 仓库的 issues / pulls / releases / commits
- 用户希望轮询任意的 JSON 端点并在有新项目时收到通知
- 用户要求“为 X 设置一个监控器”或“当 X 变化时通知我”

## 心智模型

一个监控器就是一个脚本，它：

1.  从外部源获取数据
2.  与记录先前已见 ID 的水位线文件进行比较
3.  将新的水位线写回
4.  将新项目打印到 stdout（若无变化则不输出任何内容）

下面的脚本处理所有这三种情况。Agent 通过终端工具运行它们——可以来自定时任务、Webhook 或交互式聊天——并报告新内容。

## 现成脚本

技能安装后，所有三个脚本都位于 `$HERMES_HOME/skills/devops/watchers/scripts/`。每个脚本都会读取 `WATCHER_STATE_DIR`（默认为 `$HERMES_HOME/watcher-state/`）以获取其状态文件，该文件由 `--name` 参数作为键。

| 脚本 | 监控内容 | 去重键 |
|---|---|---|
| `watch_rss.py` | RSS 2.0 或 Atom 源 URL | `<guid>` / `<id>` |
| `watch_http_json.py` | 返回对象列表的任何 JSON 端点 | 可配置的 id 字段 |
| `watch_github.py` | GitHub 仓库的 issues / pulls / releases / commits | `id` / `sha` |

所有脚本都具备以下特性：

-   首次运行记录基线——从不重放现有源内容
-   水位线是有界的 ID 集合（最多 500 个），以限制内存使用
-   输出格式：每个项目为 `## <标题>\n<URL>\n\n<可选正文>`
-   无新内容时 stdout 为空——调用方将其视为静默
-   获取错误时以非零状态退出

## 用法

直接从终端工具运行监控器：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_rss.py \
  --name hn --url https://news.ycombinator.com/rss --max 5
```

监控 GitHub 仓库（在 `~/.hermes/.env` 中设置 `GITHUB_TOKEN` 以避免 60 次/小时的匿名速率限制）：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_github.py \
  --name hermes-issues --repo NousResearch/hermes-agent --scope issues
```

轮询任意 JSON API：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_http_json.py \
  --name api --url https://api.example.com/events \
  --id-field event_id --items-path data.events
```

## 配置到定时任务中

要求 Agent 使用类似以下的提示来安排定时任务：

> 每 15 分钟，运行 `watch_rss.py --name hn --url https://news.ycombinator.com/rss`。如果它打印了任何内容，请总结标题并发送。如果它什么都没打印，请保持静默。

Agent 在定时任务的 Agent 循环中通过终端工具调用脚本；无需更改 cron 内置的 `--script` 标志。

## 状态文件

每个监控器都会写入 `$HERMES_HOME/watcher-state/<名称>.json`。检查：

```bash
cat $HERMES_HOME/watcher-state/hn.json
```

强制重放（下次运行将被视为首次轮询）：

```bash
rm $HERMES_HOME/watcher-state/hn.json
```

## 编写你自己的脚本

所有三个脚本都使用相同的模板：加载水位线、获取、比较差异、保存、输出。`scripts/_watermark.py` 是共享的辅助工具；导入它即可免费获得原子写入 + 有界 ID 集合 + 首次运行基线。查看三个参考脚本中的任何一个，了解它需要多少的样板代码。

## 常见陷阱

1.  **每次运行都打印“无新项目”的标题。** 调用方依赖空 stdout = 静默。如果在空差异时打印任何内容，就会刷屏。已提供的脚本会处理此问题；自定义脚本也必须处理。
2.  **期望首次运行输出项目。** 它不会——首次运行记录基线。如果需要初始摘要，请在首次运行后删除状态文件，或在您自己的脚本中添加 `--prime-with-latest N` 标志。
3.  **水位线无限增长。** 共享辅助工具将 ID 数量上限设为 500。对于高变动率的源可以提高此值；在受限制的文件系统上可以降低此值。
4.  **将状态目录放在 Agent 沙盒无法写入的位置。** `$HERMES_HOME/watcher-state/` 始终可写。Docker/Modal 后端可能无法访问任意主机路径。