---
title: "Apple Reminders — 通过 remindctl 管理 Apple 提醒事项：添加、列出、完成"
sidebar_label: "Apple Reminders"
description: "通过 remindctl 管理 Apple 提醒事项：添加、列出、完成"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Apple Reminders

通过 `remindctl` 从终端直接管理 Apple 提醒事项。任务通过 iCloud 在所有 Apple 设备间同步。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/apple-reminders` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `Reminders`, `tasks`, `todo`, `macOS`, `Apple` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Apple Reminders

使用 `remindctl` 从终端直接管理 Apple 提醒事项。任务通过 iCloud 在所有 Apple 设备间同步。

## 前提条件

- **macOS** 系统并安装 Reminders.app
- 安装：`brew install steipete/tap/remindctl`
- 出现提示时授予提醒事项权限
- 检查：`remindctl status` / 请求授权：`remindctl authorize`

## 使用时机

- 用户提及“reminder”或“Reminders app”
- 创建带有截止日期并能同步到 iOS 的个人待办事项
- 管理 Apple 提醒事项列表
- 用户希望任务出现在其 iPhone/iPad 上

## 避免使用时机

- 安排 Agent 提醒 → 请改用 cronjob 工具
- 日历事件 → 请使用 Apple 日历或 Google 日历
- 项目任务管理 → 请使用 GitHub Issues、Notion 等
- 如果用户说“remind me”但指的是 Agent 提醒 → 请先确认

## 快速参考

### 查看提醒事项

```bash
remindctl                    # 今日提醒事项
remindctl today              # 今日
remindctl tomorrow           # 明日
remindctl week               # 本周
remindctl overdue            # 过期事项
remindctl all                # 全部事项
remindctl 2026-01-04         # 特定日期
```

### 管理列表

```bash
remindctl list               # 列出所有列表
remindctl list Work          # 显示特定列表
remindctl list Projects --create    # 创建列表
remindctl list Work --delete        # 删除列表
```

### 创建提醒事项

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### 截止时间 vs 闹钟 / 提前提醒

`--due` 和 `--alarm` 是不同的字段：

- `--due` 设置提醒事项的截止日期/时间。
- `--alarm` 设置 EventKit 闹钟/通知触发时间。带有时间的截止提醒可能默认在截止时间设置闹钟，但当用户要求提前提醒时，请显式传递 `--alarm`。

对于截止时间为下午 2:00 并提前 30 分钟通知的提醒：

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

要编辑现有提醒事项：

```bash
remindctl edit 87354 --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

提醒事项 UI 可能会根据闹钟时间显示或分组项目，因为那是通知触发的时间。请使用 JSON 验证，而不是假设截止时间已更改：

```bash
remindctl today --json
```

预期结构：

- `dueDate`: 实际截止时间
- `alarmDate`: 通知 / 提前提醒时间

Apple 官方的 `EKReminder` 文档仅列出了提醒事项特有的属性。闹钟支持来自继承的 `EKCalendarItem` 行为，由 remindctl 的 `--alarm` 标志公开。

### 完成 / 删除

```bash
remindctl complete 1 2 3          # 按 ID 完成
remindctl delete 4A83 --force     # 按 ID 删除
```

### 输出格式

```bash
remindctl today --json       # 用于脚本的 JSON 格式
remindctl today --plain      # TSV 格式
remindctl today --quiet      # 仅显示计数
```

## 日期格式

`--due` 和日期过滤器接受的格式：
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## 规则

1. 当用户说“remind me”时，请确认：是 Apple 提醒事项（同步到手机）还是 Agent 的 cronjob 提醒
2. 创建前始终确认提醒内容和截止日期
3. 使用 `--json` 进行程序化解析