---
sidebar_position: 3
title: '学习路径'
description: '根据您的经验水平和目标，选择适合的 Hermes Agent 文档学习路径。'
---

# 学习路径

Hermes Agent 功能强大 —— CLI 助手、Telegram/Discord 机器人、任务自动化、RL 训练等等。本页面将根据您的经验水平和想要实现的目标，帮助您确定从哪里开始以及阅读哪些内容。

:::tip 从这里开始
如果您尚未安装 Hermes Agent，请从[安装指南](/docs/getting-started/installation)开始，然后运行[快速入门](/docs/getting-started/quickstart)。以下所有内容均假设您已成功安装。
:::

## 如何使用本页面

- **了解自己的水平？** 跳转到[按经验水平划分](#by-experience-level)的表格，并按照您所在层级的阅读顺序进行。
- **有特定目标？** 直接跳到[按使用场景划分](#by-use-case)，找到匹配的场景。
- **只是随便看看？** 查看[核心功能概览](#key-features-at-a-glance)表格，快速了解 Hermes Agent 的所有功能。

## 按经验水平划分

| 水平 | 目标 | 推荐阅读 | 时间预估 |
|---|---|---|---|
| **初学者** | 启动并运行，进行基本对话，使用内置工具 | [安装](/docs/getting-started/installation) → [快速入门](/docs/getting-started/quickstart) → [CLI 使用](/docs/user-guide/cli) → [配置](/docs/user-guide/configuration) | ~1 小时 |
| **中级** | 设置消息机器人，使用高级功能如记忆、定时任务和技能 | [会话](/docs/user-guide/sessions) → [消息](/docs/user-guide/messaging) → [工具](/docs/user-guide/features/tools) → [技能](/docs/user-guide/features/skills) → [记忆](/docs/user-guide/features/memory) → [定时任务](/docs/user-guide/features/cron) | ~2–3 小时 |
| **高级** | 构建自定义工具，创建技能，使用 RL 训练模型，为项目做贡献 | [架构](/docs/developer-guide/architecture) → [添加工具](/docs/developer-guide/adding-tools) → [创建技能](/docs/developer-guide/creating-skills) → [RL 训练](/docs/user-guide/features/rl-training) → [贡献指南](/docs/developer-guide/contributing) | ~4–6 小时 |

## 按使用场景划分

选择与您想做的事情相匹配的场景。每个场景都按您应该阅读的顺序链接到相关文档。

### "我想要一个 CLI 编码助手"

将 Hermes Agent 用作交互式终端助手，用于编写、审查和运行代码。

1. [安装](/docs/getting-started/installation)
2. [快速入门](/docs/getting-started/quickstart)
3. [CLI 使用](/docs/user-guide/cli)
4. [代码执行](/docs/user-guide/features/code-execution)
5. [上下文文件](/docs/user-guide/features/context-files)
6. [技巧与窍门](/docs/guides/tips)

:::tip
使用上下文文件直接将文件传入对话。Hermes Agent 可以读取、编辑和运行您项目中的代码。
:::

### "我想要一个 Telegram/Discord 机器人"

在您喜欢的消息平台上部署 Hermes Agent 作为机器人。

1. [安装](/docs/getting-started/installation)
2. [配置](/docs/user-guide/configuration)
3. [消息概览](/docs/user-guide/messaging)
4. [Telegram 设置](/docs/user-guide/messaging/telegram)
5. [Discord 设置](/docs/user-guide/messaging/discord)
6. [语音模式](/docs/user-guide/features/voice-mode)
7. [与 Hermes 一起使用语音模式](/docs/guides/use-voice-mode-with-hermes)
8. [安全](/docs/user-guide/security)

完整项目示例，请参见：
- [每日简报机器人](/docs/guides/daily-briefing-bot)
- [团队 Telegram 助手](/docs/guides/team-telegram-assistant)

### "我想要自动化任务"

调度重复性任务、运行批量作业或将 Agent 操作链接在一起。

1. [快速入门](/docs/getting-started/quickstart)
2. [定时任务调度](/docs/user-guide/features/cron)
3. [批量处理](/docs/user-guide/features/batch-processing)
4. [委派](/docs/user-guide/features/delegation)
5. [钩子](/docs/user-guide/features/hooks)

:::tip
定时任务让 Hermes Agent 可以按计划运行任务 —— 每日摘要、定期检查、自动报告 —— 无需您在场。
:::

### "我想要构建自定义工具/技能"

使用您自己的工具和可复用的技能包来扩展 Hermes Agent。

1. [工具概览](/docs/user-guide/features/tools)
2. [技能概览](/docs/user-guide/features/skills)
3. [MCP (模型上下文协议)](/docs/user-guide/features/mcp)
4. [架构](/docs/developer-guide/architecture)
5. [添加工具](/docs/developer-guide/adding-tools)
6. [创建技能](/docs/developer-guide/creating-skills)

:::tip
工具是 Agent 可以调用的单个函数。技能是打包在一起的工具、提示词和配置的集合。从工具开始，逐步过渡到技能。
:::

### "我想要训练模型"

使用强化学习，通过 Hermes Agent 内置的 RL 训练流水线来微调模型行为。

1. [快速入门](/docs/getting-started/quickstart)
2. [配置](/docs/user-guide/configuration)
3. [RL 训练](/docs/user-guide/features/rl-training)
4. [提供商路由](/docs/user-guide/features/provider-routing)
5. [架构](/docs/developer-guide/architecture)

:::tip
RL 训练在您已经了解 Hermes Agent 如何处理对话和工具调用的基础知识时效果最佳。如果您是新手，请先完成初学者路径。
:::

### "我想将其用作 Python 库"

以编程方式将 Hermes Agent 集成到您自己的 Python 应用程序中。

1. [安装](/docs/getting-started/installation)
2. [快速入门](/docs/getting-started/quickstart)
3. [Python 库指南](/docs/guides/python-library)
4. [架构](/docs/developer-guide/architecture)
5. [工具](/docs/user-guide/features/tools)
6. [会话](/docs/user-guide/sessions)

## 核心功能概览

不确定有哪些功能？以下是主要功能的快速目录：

| 功能 | 作用 | 链接 |
|---|---|---|
| **工具** | Agent 可以调用的内置工具（文件 I/O、搜索、Shell 等） | [工具](/docs/user-guide/features/tools) |
| **技能** | 可安装的插件包，用于添加新功能 | [技能](/docs/user-guide/features/skills) |
| **记忆** | 跨会话的持久化记忆 | [记忆](/docs/user-guide/features/memory) |
| **上下文文件** | 将文件和目录输入到对话中 | [上下文文件](/docs/user-guide/features/context-files) |
| **MCP** | 通过模型上下文协议连接到外部工具服务器 | [MCP](/docs/user-guide/features/mcp) |
| **定时任务** | 调度重复的 Agent 任务 | [定时任务](/docs/user-guide/features/cron) |
| **委派** | 生成子 Agent 进行并行工作 | [委派](/docs/user-guide/features/delegation) |
| **代码执行** | 运行以编程方式调用 Hermes 工具的 Python 脚本 | [代码执行](/docs/user-guide/features/code-execution) |
| **浏览器** | 网页浏览和抓取 | [浏览器](/docs/user-guide/features/browser) |
| **钩子** | 事件驱动的回调和中间件 | [钩子](/docs/user-guide/features/hooks) |
| **批量处理** | 批量处理多个输入 | [批量处理](/docs/user-guide/features/batch-processing) |
| **RL 训练** | 使用强化学习微调模型 | [RL 训练](/docs/user-guide/features/rl-training) |
| **提供商路由** | 跨多个 LLM 提供商路由请求 | [提供商路由](/docs/user-guide/features/provider-routing) |

## 接下来阅读什么

根据您当前所处的位置：

- **刚完成安装？** → 前往[快速入门](/docs/getting-started/quickstart)进行第一次对话。
- **完成了快速入门？** → 阅读[CLI 使用](/docs/user-guide/cli)和[配置](/docs/user-guide/configuration)以自定义您的设置。
- **对基础知识感到满意了？** → 探索[工具](/docs/user-guide/features/tools)、[技能](/docs/user-guide/features/skills)和[记忆](/docs/user-guide/features/memory)以解锁 Agent 的全部功能。
- **为团队设置？** → 阅读[安全](/docs/user-guide/security)和[会话](/docs/user-guide/sessions)以了解访问控制和对话管理。
- **准备好构建了？** → 跳转到[开发者指南](/docs/developer-guide/architecture)以了解内部原理并开始贡献。
- **想要实际例子？** → 查看[指南](/docs/guides/tips)部分，了解真实世界的项目和技巧。

:::tip
您不需要阅读所有内容。选择与您目标匹配的路径，按顺序跟随链接，您很快就能上手。您可以随时返回此页面寻找下一步。
:::