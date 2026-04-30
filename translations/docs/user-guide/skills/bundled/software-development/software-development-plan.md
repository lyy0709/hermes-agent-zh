---
title: "Plan — 计划模式：将 Markdown 计划写入"
sidebar_label: "Plan"
description: "计划模式：将 Markdown 计划写入"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Plan

计划模式：将 Markdown 计划写入 .hermes/plans/，不执行。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/plan` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `planning`, `plan-mode`, `implementation`, `workflow` |
| 相关技能 | [`writing-plans`](/docs/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 计划模式

当用户想要一个计划而非执行时，使用此技能。

## 核心行为

本轮对话中，你仅进行计划。

- 不要实现代码。
- 除了计划 Markdown 文件外，不要编辑项目文件。
- 不要运行会修改状态的终端命令、提交、推送或执行外部操作。
- 需要时，你可以使用只读命令/工具检查仓库或其他上下文。
- 你的交付物是一个保存在活动工作空间下 `.hermes/plans/` 内的 Markdown 计划。

## 输出要求

编写一个具体且可操作的 Markdown 计划。

在相关时包含：
- 目标
- 当前上下文 / 假设
- 建议方法
- 分步计划
- 可能更改的文件
- 测试 / 验证
- 风险、权衡和开放性问题

如果任务与代码相关，请包含确切的文件路径、可能的测试目标以及验证步骤。

## 保存位置

使用 `write_file` 将计划保存在：
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

将其视为相对于活动工作目录 / 后端工作空间的路径。Hermes 文件工具是后端感知的，因此使用此相对路径可以将计划与本地、Docker、SSH、Modal 和 Daytona 后端上的工作空间保持一致。

如果运行时提供了特定的目标路径，请使用该确切路径。
如果没有，请在 `.hermes/plans/` 下创建一个合理的带时间戳的文件名。

## 交互风格

- 如果请求足够清晰，直接编写计划。
- 如果 `/plan` 没有明确的指令，请从当前对话上下文中推断任务。
- 如果确实信息不足，请提出一个简短的澄清问题，而不是猜测。
- 保存计划后，简要回复你计划了什么以及保存的路径。