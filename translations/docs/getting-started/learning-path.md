---
sidebar_position: 3
title: '学习路径'
description: '根据您的经验水平和目标，选择适合您的 Hermes Agent 文档学习路径。'
---

# 学习路径

Hermes Agent 功能强大 —— CLI 助手、Telegram/Discord 机器人、任务自动化、RL 训练等等。本页面将根据您的经验水平和想要实现的目标，帮助您确定从哪里开始以及阅读哪些内容。

:::tip 从这里开始
如果您尚未安装 Hermes Agent，请从[安装指南](/getting-started/installation)开始，然后运行[快速入门](/getting-started/quickstart)。以下所有内容均假设您已成功安装。
:::

## 如何使用本页面

- **了解自己的水平？** 跳转到[按经验水平划分](#by-experience-level)的表格，并按照您所在层级的阅读顺序进行。
- **有特定目标？** 直接跳到[按使用场景划分](#by-use-case)部分，找到匹配的场景。
- **只是随便看看？** 查看[核心功能概览](#key-features-at-a-glance)表格，快速了解 Hermes Agent 的所有功能。

## 按经验水平划分

| 水平 | 目标 | 推荐阅读 | 时间预估 |
|---|---|---|---|
| **初学者** | 启动并运行，进行基本对话，使用内置工具 | [安装](/getting-started/installation) → [快速入门](/getting-started/quickstart) → [CLI 使用](/user-guide/cli) → [配置](/user-guide/configuration) | ~1 小时 |
| **中级** | 设置消息机器人，使用高级功能如记忆、定时任务和技能 | [会话](/user-guide/sessions) → [消息](/user-guide/messaging) → [工具](/user-guide/features/tools) → [技能](/user-guide/features/skills) → [记忆](/user-guide/features/memory) → [定时任务](/user-guide/features/cron) | ~2–3 小时 |
| **高级** | 构建自定义工具，创建技能，使用 RL 训练模型，为项目做贡献 | [架构](/developer-guide/architecture) → [添加工具](/developer-guide/adding-tools) → [创建技能](/developer-guide/creating-skills) → [RL 训练](/user-guide/features/rl-training) → [贡献指南](/developer-guide/contributing) | ~4–6 小时 |

## 按使用场景划分

选择与您想做的事情相匹配的场景。每个场景都会按您应该阅读的顺序链接到相关文档。

### "我想要一个 CLI 编码助手"

将 Hermes Agent 用作交互式终端助手，用于编写、审查和运行代码。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [CLI 使用](/user-guide/cli)
4. [代码执行](/user-guide/features/code-execution)
5. [上下文文件](/user-guide/features/context-files)
6. [技巧与窍门](/guides/tips)

:::tip
使用上下文文件直接将文件传入对话。Hermes Agent 可以读取、编辑和运行您项目中的代码。
:::

### "我想要一个 Telegram/Discord 机器人"

在您喜欢的消息平台上部署 Hermes Agent 作为机器人。

1. [安装](/getting-started/installation)
2. [配置](/user-guide/configuration)
3. [消息概览](/user-guide/messaging)
4. [Telegram 设置](/user-guide/messaging/telegram)
5. [Discord 设置](/user-guide/messaging/discord)
6. [语音模式](/user-guide/features/voice-mode)
7. [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)
8. [安全](/user-guide/security)

完整项目示例，请参见：
- [每日简报机器人](/guides/daily-briefing-bot)
- [团队 Telegram 助手](/guides/team-telegram-assistant)

### "我想要自动化任务"

安排重复性任务、运行批量作业或将 Agent 操作串联起来。

1. [快速入门](/getting-started/quickstart)
2. [定时任务调度](/user-guide/features/cron)
3. [批量处理](/user-guide/features/batch-processing)
4. [委派](/user-guide/features/delegation)
5. [钩子](/user-guide/features/hooks)

:::tip
定时任务让 Hermes Agent 可以按计划运行任务 —— 每日摘要、定期检查、自动报告 —— 无需您在场。
:::

### "我想要构建自定义工具/技能"

使用您自己的工具和可复用的技能包来扩展 Hermes Agent。

1. [插件](/user-guide/features/plugins)
2. [构建 Hermes 插件](/guides/build-a-hermes-plugin)
3. [工具概览](/user-guide/features/tools)
4. [技能概览](/user-guide/features/skills)
5. [MCP (模型上下文协议)](/user-guide/features/mcp)
6. [架构](/developer-guide/architecture)
7. [添加工具](/developer-guide/adding-tools)
8. [创建技能](/developer-guide/creating-skills)

:::tip
对于大多数自定义工具创建，请从插件开始。[添加工具](/developer-guide/adding-tools)页面适用于 Hermes 核心内置开发，而非通常的用户/自定义工具路径。
:::

### "我想要训练模型"

使用强化学习，通过 Hermes Agent 内置的 RL 训练流水线来微调模型行为。

1. [快速入门](/getting-started/quickstart)
2. [配置](/user-guide/configuration)
3. [RL 训练](/user-guide/features/rl-training)
4. [提供商路由](/user-guide/features/provider-routing)
5. [架构](/developer-guide/architecture)

:::tip
当您已经了解 Hermes Agent 如何处理对话和工具调用的基础知识后，RL 训练效果最佳。如果您是新手，请先完成初学者路径。
:::

### "我想将其用作 Python 库"

以编程方式将 Hermes Agent 集成到您自己的 Python 应用程序中。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [Python 库指南](/guides/python-library)
4. [架构](/developer-guide/architecture)
5. [工具](/user-guide/features/tools)
6. [会话](/user-guide/sessions)

## 核心功能概览

不确定有哪些功能可用？以下是主要功能的快速目录：

| 功能 | 作用 | 链接 |
|---|---|---|
| **工具** | Agent 可以调用的内置工具（文件 I/O、搜索、Shell 等） | [工具](/user-guide/features/tools) |
| **技能** | 可安装的插件包，用于添加新功能 | [技能](/user-guide/features/skills) |
| **记忆** | 跨会话的持久化记忆 | [记忆](/user-guide/features/memory) |
| **上下文文件** | 将文件和目录输入到对话中 | [上下文文件](/user-guide/features/context-files) |
| **MCP** | 通过模型上下文协议连接到外部工具服务器 | [MCP](/user-guide/features/mcp) |
| **定时任务** | 安排重复的 Agent 任务 | [定时任务](/user-guide/features/cron) |
| **委派** | 生成子 Agent 进行并行工作 | [委派](/user-guide/features/delegation) |
| **代码执行** | 运行以编程方式调用 Hermes 工具的 Python 脚本 | [代码执行](/user-guide/features/code-execution) |
| **浏览器** | 网页浏览和抓取 | [浏览器](/user-guide/features/browser) |
| **钩子** | 事件驱动的回调和中间件 | [钩子](/user-guide/features/hooks) |
| **批量处理** | 批量处理多个输入 | [批量处理](/user-guide/features/batch-processing) |
| **RL 训练** | 使用强化学习微调模型 | [RL 训练](/user-guide/features/rl-training) |
| **提供商路由** | 跨多个 LLM 提供商路由请求 | [提供商路由](/user-guide/features/provider-routing) |

## 接下来阅读什么

根据您当前所处的位置：

- **刚完成安装？** → 前往[快速入门](/getting-started/quickstart)进行第一次对话。
- **完成了快速入门？** → 阅读[CLI 使用](/user-guide/cli)和[配置](/user-guide/configuration)以自定义您的设置。
- **对基础知识感到满意？** → 探索[工具](/user-guide/features/tools)、[技能](/user-guide/features/skills)和[记忆](/user-guide/features/memory)，以解锁 Agent 的全部能力。
- **为团队设置？** → 阅读[安全](/user-guide/security)和[会话](/user-guide/sessions)以了解访问控制和对话管理。
- **准备好构建了？** → 跳转到[开发者指南](/developer-guide/architecture)以了解内部原理并开始贡献。
- **想要实际例子？** → 查看[指南](/guides/tips)部分，了解真实世界的项目和技巧。

:::tip
您不需要阅读所有内容。选择与您目标匹配的路径，按顺序跟随链接，您很快就能上手。您可以随时返回此页面寻找下一步。
:::