---
title: "Honcho"
sidebar_label: "Honcho"
description: "配置和使用 Hermes 的 Honcho 记忆功能——跨会话用户建模、多配置文件对等体隔离、观察配置、辩证推理、会话摘要和上下文预算强制执行。适用于设置 Honcho、排查记忆问题、使用 Honcho 对等体管理配置文件，或调整观察、回忆和辩证设置。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Honcho

配置和使用 Hermes 的 Honcho 记忆功能——跨会话用户建模、多配置文件对等体隔离、观察配置、辩证推理、会话摘要和上下文预算强制执行。适用于设置 Honcho、排查记忆问题、使用 Honcho 对等体管理配置文件，或调整观察、回忆和辩证设置。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/honcho` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/honcho` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `Honcho`, `Memory`, `Profiles`, `Observation`, `Dialectic`, `User-Modeling`, `Session-Summary` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Hermes 的 Honcho 记忆

Honcho 提供 AI 原生的跨会话用户建模。它能在对话中学习用户是谁，并为每个 Hermes 配置文件提供其专属的对等体身份，同时共享统一的用户视图。

## 使用时机

- 设置 Honcho（云端或自托管）
- 排查记忆不工作 / 对等体不同步的问题
- 创建多配置文件设置，其中每个 Agent 都有自己的 Honcho 对等体
- 调整观察、回忆、辩证深度或写入频率设置
- 了解 5 个 Honcho 工具的作用及使用时机
- 配置上下文预算和会话摘要注入

## 设置

### 云端 (app.honcho.dev)

```bash
hermes honcho setup
# 选择 "cloud"，粘贴来自 https://app.honcho.dev 的 API 密钥
```

### 自托管

```bash
hermes honcho setup
# 选择 "local"，输入基础 URL（例如 http://localhost:8000）
```

参见：https://docs.honcho.dev/v3/guides/integrations/hermes#running-honcho-locally-with-hermes

### 验证

```bash
hermes honcho status    # 显示解析后的配置、连接测试、对等体信息
```

## 架构

### 基础上下文注入

当 Honcho 将上下文注入系统提示词（在 `hybrid` 或 `context` 回忆模式下）时，它会按以下顺序组装基础上下文块：

1.  **会话摘要** —— 当前会话至今的简短摘要（放在首位，以便模型获得即时的对话连续性）
2.  **用户表征** —— Honcho 积累的用户模型（偏好、事实、模式）
3.  **AI 对等体卡片** —— 此 Hermes 配置文件的 AI 对等体身份卡片

会话摘要在每个回合开始时由 Honcho 自动生成（当存在先前的会话时）。它让模型无需重放完整历史即可获得一个“热启动”。

### 冷启动 / 热启动提示词选择

Honcho 自动在两种提示词策略之间选择：

| 条件 | 策略 | 发生的情况 |
|-----------|----------|--------------|
| 无先前会话或表征为空 | **冷启动** | 轻量级介绍提示词；跳过摘要注入；鼓励模型了解用户 |
| 存在现有表征和/或会话历史 | **热启动** | 完整的基础上下文注入（摘要 → 表征 → 卡片）；更丰富的系统提示词 |

您无需配置此选项——它会根据会话状态自动决定。

### 对等体

Honcho 将对话建模为**对等体**之间的交互。Hermes 为每个会话创建两个对等体：

- **用户对等体** (`peerName`): 代表人类。Honcho 从观察到的消息中构建用户表征。
- **AI 对等体** (`aiPeer`): 代表此 Hermes 实例。每个配置文件都有自己的 AI 对等体，因此 Agent 会形成独立的视图。

### 观察

每个对等体有两个观察开关，控制 Honcho 从何处学习：

| 开关 | 作用 |
|--------|-------------|
| `observeMe` | 观察对等体自身的消息（构建自我表征） |
| `observeOthers` | 观察其他对等体的消息（构建跨对等体理解） |

默认值：所有四个开关**开启**（完全双向观察）。

在 `honcho.json` 中按对等体配置：

```json
{
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": true, "observeOthers": true }
  }
}
```

或使用简写预设：

| 预设 | 用户 | AI | 使用场景 |
|--------|------|----|----------|
| `"directional"` (默认) | me:on, others:on | me:on, others:on | 多 Agent，完整记忆 |
| `"unified"` | me:on, others:off | me:off, others:on | 单 Agent，仅用户建模 |

在 [Honcho 仪表板](https://app.honcho.dev) 中更改的设置会在会话初始化时同步回来——服务器端配置优先于本地默认值。

### 会话

Honcho 会话限定消息和观察的归属范围。策略选项：

| 策略 | 行为 |
|----------|----------|
| `per-directory` (默认) | 每个工作目录一个会话 |
| `per-repo` | 每个 git 仓库根目录一个会话 |
| `per-session` | 每次 Hermes 运行都创建新的 Honcho 会话 |
| `global` | 跨所有目录的单一会话 |

手动覆盖：`hermes honcho map my-project-name`

### 回忆模式

Agent 访问 Honcho 记忆的方式：

| 模式 | 自动注入上下文？ | 工具可用？ | 使用场景 |
|------|---------------------|-----------------|----------|
| `hybrid` (默认) | 是 | 是 | Agent 决定何时使用工具 vs 自动上下文 |
| `context` | 是 | 否（隐藏） | Token 成本最低，无需工具调用 |
| `tools` | 否 | 是 | Agent 显式控制所有内存访问 |

## 三个正交旋钮

Honcho 的辩证行为由三个独立的维度控制。每个维度都可以在不影响其他维度的情况下进行调整：
### 节奏（何时）

控制**对话与上下文调用的频率**。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextCadence` | `1` | 两次上下文 API 调用之间的最小对话轮数 |
| `dialecticCadence` | `2` | 两次对话 API 调用之间的最小对话轮数。建议 1–5 |
| `injectionFrequency` | `every-turn` | 基础上下文注入频率：`every-turn` 或 `first-turn` |

更高的节奏值会减少调用对话 LLM 的频率。`dialecticCadence: 2` 意味着引擎每隔一轮调用一次。设置为 `1` 则每轮都调用。

### 深度（多少轮）

控制 Honcho 每次查询执行**多少轮**对话推理。

| 键 | 默认值 | 范围 | 描述 |
|-----|---------|-------|-------------|
| `dialecticDepth` | `1` | 1-3 | 每次查询的对话推理轮数 |
| `dialecticDepthLevels` | -- | 数组 | 可选的每轮深度级别覆盖（见下文） |

`dialecticDepth: 2` 意味着 Honcho 运行两轮对话综合。第一轮产生初步答案；第二轮对其进行优化。

`dialecticDepthLevels` 允许你为每一轮独立设置推理级别：

```json
{
  "dialecticDepth": 3,
  "dialecticDepthLevels": ["low", "medium", "high"]
}
```

如果省略 `dialecticDepthLevels`，则轮次使用从 `dialecticReasoningLevel`（基础级别）派生的**比例级别**：

| 深度 | 轮次级别 |
|-------|-------------|
| 1 | [基础] |
| 2 | [最小, 基础] |
| 3 | [最小, 基础, 低] |

这确保了早期轮次成本较低，同时在最终综合时使用完整深度。

**会话开始时的深度。** 会话开始的预热会在第 1 轮对话之前，在后台运行配置的完整 `dialecticDepth`。对于冷启动的 peer，单轮预热通常返回较少的输出——多轮深度会在用户开口之前运行审计/协调周期。第 1 轮直接使用预热结果；如果预热未能及时完成，第 1 轮会回退到有超时限制的同步调用。

### 级别（强度）

控制每轮对话推理的**强度**。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以向 `honcho_reasoning` 传递 `reasoning_level` 来覆盖每次调用的默认值。`false` = 始终使用 `dialecticReasoningLevel`，忽略模型覆盖 |

更高级别会产生更丰富的综合结果，但会在 Honcho 后端消耗更多 Token。

## 多配置文件设置

每个 Hermes 配置文件都有自己的 Honcho AI peer，同时共享同一个工作空间（用户上下文）。这意味着：

- 所有配置文件看到相同的用户表示
- 每个配置文件构建自己的 AI 身份和观察结果
- 一个配置文件写入的结论可以通过共享工作空间对其他配置文件可见

### 创建带有 Honcho peer 的配置文件

```bash
hermes profile create coder --clone
# 创建主机块 hermes.coder，AI peer "coder"，从默认配置继承配置
```

`--clone` 为 Honcho 执行的操作：
1. 在 `honcho.json` 中创建一个 `hermes.coder` 主机块
2. 设置 `aiPeer: "coder"`（配置文件名称）
3. 从默认配置继承 `workspace`, `peerName`, `writeFrequency`, `recallMode` 等
4. 在 Honcho 中急切地创建 peer，使其在第一条消息之前就存在

### 回填现有配置文件

```bash
hermes honcho sync    # 为所有尚未拥有主机块的配置文件创建主机块
```

### 每个配置文件的配置

在主机块中覆盖任何设置：

```json
{
  "hosts": {
    "hermes.coder": {
      "aiPeer": "coder",
      "recallMode": "tools",
      "dialecticDepth": 2,
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    }
  }
}
```

## 工具

Agent 拥有 5 个双向的 Honcho 工具（在 `context` 召回模式下隐藏）：

| 工具 | 调用 LLM？ | 成本 | 使用场景 |
|------|-----------|------|----------|
| `honcho_profile` | 否 | 最小 | 在对话开始时快速获取事实快照，或用于快速查找姓名/角色/偏好 |
| `honcho_search` | 否 | 低 | 获取特定的过去事实供自己推理——原始摘录，无综合 |
| `honcho_context` | 否 | 低 | 完整的会话上下文快照：摘要、表示、卡片、最近消息 |
| `honcho_reasoning` | 是 | 中–高 | 由 Honcho 的对话引擎综合的自然语言问题 |
| `honcho_conclude` | 否 | 最小 | 写入或删除持久性事实；传递 `peer: "ai"` 用于 AI 自我认知 |

### `honcho_profile`
读取或更新 peer 卡片——精选的关键事实（姓名、角色、偏好、沟通风格）。传递 `card: [...]` 进行更新；省略则读取。不调用 LLM。

### `honcho_search`
对存储的上下文进行语义搜索，针对特定 peer。返回按相关性排序的原始摘录，无综合。默认 800 Token，最多 2000。适用于当你需要特定的过去事实供自己推理，而不是一个综合答案时。

### `honcho_context`
来自 Honcho 的完整会话上下文快照——会话摘要、peer 表示、peer 卡片和最近消息。不调用 LLM。当你想一次性查看 Honcho 对当前会话和 peer 的所有了解时使用。

### `honcho_reasoning`
由 Honcho 的对话推理引擎回答的自然语言问题（在 Honcho 后端调用 LLM）。成本更高，质量更高。传递 `reasoning_level` 来控制深度：`minimal`（快速/廉价）→ `low` → `medium` → `high` → `max`（彻底）。省略则使用配置的默认值（`low`）。用于对用户的模式、目标或当前状态进行综合理解。

### `honcho_conclude`
写入或删除关于 peer 的持久性结论。传递 `conclusion: "..."` 来创建。传递 `delete_id: "..."` 来删除一个结论（用于 PII 移除——Honcho 会随时间自我修复不正确的结论，因此删除仅用于 PII）。你**必须**且**只能**传递这两个参数中的一个。

### 双向 peer 目标定位

所有 5 个工具都接受一个可选的 `peer` 参数：
- `peer: "user"`（默认）——操作用户 peer
- `peer: "ai"` ——操作此配置文件的 AI peer
- `peer: "<explicit-id>"` ——工作空间中的任何 peer ID
示例：
```
honcho_profile                        # 读取用户名片
honcho_profile peer="ai"              # 读取 AI 对等体的名片
honcho_reasoning query="用户最关心什么？"
honcho_reasoning query="我的交互模式是什么？" peer="ai" reasoning_level="medium"
honcho_conclude conclusion="偏好简洁的回答"
honcho_conclude conclusion="我倾向于过度解释代码" peer="ai"
honcho_conclude delete_id="abc123"    # 删除 PII
```

## Agent 使用模式

当 Honcho 记忆激活时，Hermes 的指导原则。

### 会话开始时

```
1. honcho_profile                  → 快速预热，无 LLM 成本
2. 如果上下文看起来单薄 → honcho_context  (完整快照，仍无 LLM 调用)
3. 如果需要深度综合 → honcho_reasoning  (LLM 调用，谨慎使用)
```

**不要**在每一轮都调用 `honcho_reasoning`。自动注入已经处理了持续的上下文刷新。仅当你真正需要基础上下文未提供的综合见解时，才使用推理工具。

### 当用户分享需要记住的内容时

```
honcho_conclude conclusion="<具体的、可操作的事实>"
```

好的结论："偏好代码示例而非文字解释"、"在 2026 年 4 月之前进行 Rust 异步项目"
坏的结论："用户说了些关于 Rust 的事情"（太模糊）、"用户似乎懂技术"（已在表征中）

### 当用户询问过去上下文 / 你需要回忆具体细节时

```
honcho_search query="<主题>"       → 快速，无 LLM，适用于具体事实
honcho_context                       → 包含摘要和消息的完整快照
honcho_reasoning query="<问题>"  → 综合答案，当搜索不够用时使用
```

### 何时使用 `peer: "ai"`

使用 AI 对等体目标来构建和查询 Agent 自身的知识：
- `honcho_conclude conclusion="我解释架构时往往很啰嗦" peer="ai"` — 自我纠正
- `honcho_reasoning query="我通常如何处理模糊的请求？" peer="ai"` — 自我审计
- `honcho_profile peer="ai"` — 查看自己的身份名片

### 何时不调用工具

在 `hybrid` 和 `context` 模式下，基础上下文（用户表征 + 名片 + 会话摘要）会在每一轮之前自动注入。不要重新获取已注入的内容。仅在以下情况调用工具：
- 你需要自动注入的上下文所没有的内容
- 用户明确要求你回忆或检查记忆
- 你正在撰写关于新事物的结论

### 节奏感知

工具端的 `honcho_reasoning` 与自动注入的辩证推理共享相同的成本。在显式工具调用之后，自动注入的节奏会重置——避免在同一轮次重复计费。

## 配置参考

配置文件：`$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。

### 关键设置

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | API 密钥（[获取一个](https://app.honcho.dev)） |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等体身份 |
| `aiPeer` | 主机密钥 | AI 对等体身份 |
| `workspace` | 主机密钥 | 共享工作区 ID |
| `recallMode` | `hybrid` | `hybrid`、`context` 或 `tools` |
| `observation` | 全部开启 | 每个对等体的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`、`turn`、`session` 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`、`per-repo`、`per-session`、`global` |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |

### 辩证推理设置

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 根据查询复杂度自动提升推理级别。`false` = 固定级别 |
| `dialecticDepth` | `1` | 每次查询的辩证推理轮数 (1-3) |
| `dialecticDepthLevels` | -- | 可选的每轮级别数组，例如 `["low", "high"]` |
| `dialecticMaxInputChars` | `10000` | 辩证推理查询输入的最大字符数 |

### 上下文预算和注入

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | 无上限 | 组合基础上下文注入（摘要 + 表征 + 名片）的最大 Token 数。选择性上限 — 省略表示无上限，设置为整数以限制注入大小。 |
| `injectionFrequency` | `every-turn` | `every-turn` 或 `first-turn` |
| `contextCadence` | `1` | 上下文 API 调用之间的最小轮数间隔 |
| `dialecticCadence` | `2` | 辩证推理 LLM 调用之间的最小轮数间隔（推荐 1–5） |

`contextTokens` 预算在注入时强制执行。如果会话摘要 + 表征 + 名片超出预算，Honcho 会首先修剪摘要，然后是表征，保留名片。这可以防止长会话中上下文爆炸。

### 记忆上下文清理

Honcho 在注入前清理 `memory-context` 块，以防止提示词注入和格式错误的内容：

- 从用户撰写的结论中剥离 XML/HTML 标签
- 规范化空白字符和控制字符
- 截断超过 `messageMaxChars` 的单个结论
- 转义可能破坏系统提示词结构的分隔符序列

此修复解决了原始用户结论包含标记或特殊字符可能破坏注入上下文块的边缘情况。

## 故障排除

### "Honcho 未配置"
运行 `hermes honcho setup`。确保 `~/.hermes/config.yaml` 中包含 `memory.provider: honcho`。

### 记忆在会话间未持久化
检查 `hermes honcho status` —— 验证 `saveMessages: true` 且 `writeFrequency` 不是 `session`（仅在退出时写入）。

### 配置文件未获得自己的对等体
创建时使用 `--clone`：`hermes profile create <名称> --clone`。对于现有配置文件：`hermes honcho sync`。

### 仪表板中的观察设置更改未反映
观察配置在每次会话初始化时从服务器同步。在 Honcho UI 中更改设置后，请启动新会话。

### 消息被截断
超过 `messageMaxChars`（默认 25k）的消息会自动分块，并带有 `[continued]` 标记。如果经常遇到此情况，请检查是否是工具结果或技能内容导致消息大小膨胀。
### 上下文注入过大
如果看到关于超出上下文预算的警告，请降低 `contextTokens` 或减少 `dialecticDepth`。当预算紧张时，会话摘要会首先被修剪。

### 会话摘要缺失
会话摘要要求当前 Honcho 会话中至少有一个先前的轮次。在冷启动（新会话，无历史记录）时，摘要会被省略，Honcho 转而使用冷启动提示策略。

## CLI 命令

| 命令 | 描述 |
|---------|-------------|
| `hermes honcho setup` | 交互式设置向导（云端/本地、身份、观察、回忆、会话） |
| `hermes honcho status` | 显示活动配置文件的已解析配置、连接测试、对等方信息 |
| `hermes honcho enable` | 为活动配置文件启用 Honcho（如果需要，会创建主机块） |
| `hermes honcho disable` | 为活动配置文件禁用 Honcho |
| `hermes honcho peer` | 显示或更新对等方名称（`--user <name>`, `--ai <name>`, `--reasoning <level>`） |
| `hermes honcho peers` | 显示所有配置文件中的对等方身份 |
| `hermes honcho mode` | 显示或设置回忆模式（`hybrid`, `context`, `tools`） |
| `hermes honcho tokens` | 显示或设置 Token 预算（`--context <N>`, `--dialectic <N>`） |
| `hermes honcho sessions` | 列出已知的目录到会话名称映射 |
| `hermes honcho map <name>` | 将当前工作目录映射到 Honcho 会话名称 |
| `hermes honcho identity` | 植入 AI 对等方身份或显示两个对等方的表示 |
| `hermes honcho sync` | 为所有尚未拥有主机块的 Hermes 配置文件创建主机块 |
| `hermes honcho migrate` | 从 OpenClaw 原生记忆迁移到 Hermes + Honcho 的分步指南 |
| `hermes memory setup` | 通用记忆提供商选择器（选择 "honcho" 会运行相同的向导） |
| `hermes memory status` | 显示活动的记忆提供商和配置 |
| `hermes memory off` | 禁用外部记忆提供商 |