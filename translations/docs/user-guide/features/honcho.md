---
sidebar_position: 99
title: "Honcho 记忆"
description: "通过 Honcho 实现 AI 原生持久化记忆 —— 辩证推理、多 Agent 用户建模和深度个性化"
---

# Honcho 记忆

[Honcho](https://github.com/plastic-labs/honcho) 是一个 AI 原生的记忆后端，它在 Hermes 内置记忆系统之上增加了辩证推理和深度用户建模功能。与简单的键值存储不同，Honcho 通过在对话发生后进行推理，维护一个关于用户是谁的持续模型 —— 包括他们的偏好、沟通风格、目标和行为模式。

:::info Honcho 是一个记忆提供商插件
Honcho 已集成到[记忆提供商](./memory-providers.md)系统中。以下所有功能都可通过统一的记忆提供商接口使用。
:::

## Honcho 新增功能

| 能力 | 内置记忆 | Honcho |
|-----------|----------------|--------|
| 跨会话持久化 | ✔ 基于文件的 MEMORY.md/USER.md | ✔ 服务端 API |
| 用户画像 | ✔ 手动 Agent 整理 | ✔ 自动辩证推理 |
| 会话摘要 | — | ✔ 会话范围上下文注入 |
| 多 Agent 隔离 | — | ✔ 按对等方（peer）的画像分离 |
| 观察模式 | — | ✔ 统一或定向观察 |
| 结论（衍生见解） | — | ✔ 服务端对模式的推理 |
| 跨历史记录搜索 | ✔ FTS5 会话搜索 | ✔ 对结论的语义搜索 |

**辩证推理**：在每次对话轮次后（由 `dialecticCadence` 控制），Honcho 会分析对话内容，并推导出关于用户偏好、习惯和目标的见解。这些见解随时间累积，使 Agent 能够获得超越用户明确陈述的、不断加深的理解。辩证推理支持多轮深度（1-3 轮），并自动选择冷/热启动提示词 —— 冷启动查询侧重于一般用户事实，而热启动查询则优先考虑会话范围内的上下文。

**会话范围上下文**：基础上下文现在包含会话摘要，以及用户表征和对等方卡片。这使 Agent 能够了解当前会话中已经讨论过的内容，减少重复并保持连续性。

**多 Agent 画像**：当多个 Hermes 实例与同一用户对话时（例如，一个编码助手和一个个人助手），Honcho 会维护独立的“对等方”画像。每个对等方只能看到自己的观察和结论，防止上下文交叉污染。

## 设置

```bash
hermes memory setup    # 从提供商列表中选择 "honcho"
```

或手动配置：

```yaml
# ~/.hermes/config.yaml
memory:
  provider: honcho
```

```bash
echo 'HONCHO_API_KEY=***' >> ~/.hermes/.env
```

在 [honcho.dev](https://honcho.dev) 获取 API 密钥。

## 架构

### 双层上下文注入

在每次轮次中（在 `hybrid` 或 `context` 模式下），Honcho 会组装两层上下文注入到系统提示词中：

1.  **基础上下文** —— 会话摘要、用户表征、用户对等方卡片、AI 自我表征和 AI 身份卡片。在 `contextCadence` 时刷新。这是“用户是谁”的层面。
2.  **辩证补充** —— 由 LLM 合成的关于用户当前状态和需求的推理。在 `dialecticCadence` 时刷新。这是“当前什么最重要”的层面。

这两层上下文会被拼接起来，并根据 `contextTokens` 预算（如果设置了）进行截断。

### 冷/热启动提示词选择

辩证推理会自动在两种提示词策略之间选择：

-   **冷启动**（尚无基础上下文）：通用查询 —— “这个人是谁？他们的偏好、目标和工作风格是什么？”
-   **热会话**（基础上下文已存在）：会话范围查询 —— “鉴于本次会话到目前为止讨论的内容，关于该用户的哪些上下文最相关？”

这是根据基础上下文是否已填充自动决定的。

### 三个正交配置旋钮

成本和深度由三个独立的旋钮控制：

| 旋钮 | 控制内容 | 默认值 |
|------|----------|---------|
| `contextCadence` | `context()` API 调用之间的轮次间隔（基础层刷新） | `1` |
| `dialecticCadence` | `peer.chat()` LLM 调用之间的轮次间隔（辩证层刷新） | `2`（推荐 1–5） |
| `dialecticDepth` | 每次辩证调用中 `.chat()` 的轮次数（1–3） | `1` |

这些是正交的 —— 你可以设置频繁的上下文刷新但低频的辩证推理，或者低频但深度多轮的辩证推理。例如：`contextCadence: 1, dialecticCadence: 5, dialecticDepth: 2` 表示每轮刷新基础上下文，每 5 轮运行一次辩证推理，每次辩证推理运行 2 轮。

### 辩证深度（多轮）

当 `dialecticDepth` > 1 时，每次辩证调用会运行多轮 `.chat()`：

-   **第 0 轮**：冷启动或热启动提示词（见上文）
-   **第 1 轮**：自我审计 —— 识别初始评估中的差距，并从最近的会话中综合证据
-   **第 2 轮**：调和 —— 检查前几轮之间是否存在矛盾，并生成最终的综合结果

每一轮都使用成比例的推理级别（早期轮次较轻，主要轮次使用基础级别）。可以使用 `dialecticDepthLevels` 覆盖每轮的级别 —— 例如，对于深度为 3 的运行，使用 `["minimal", "medium", "high"]`。

如果前一轮返回了强信号（长且结构化的输出），则轮次会提前退出，因此深度 3 并不总是意味着 3 次 LLM 调用。

### 会话启动预热

在会话初始化时，Honcho 会在后台以配置的完整 `dialecticDepth` 发起一次辩证调用，并将结果直接提供给第 1 轮的上下文组装。对于冷启动的对等方，单轮预热通常返回较少的输出 —— 多轮深度会在用户开口之前运行审计/调和周期。如果预热在第 1 轮之前尚未完成，第 1 轮将回退到具有有限超时的同步调用。

### 查询自适应推理级别

自动注入的辩证推理会根据查询长度调整 `dialecticReasoningLevel`：≥120 字符时 +1 级，≥400 字符时 +2 级，上限为 `reasoningLevelCap`（默认 `"high"`）。可以通过 `reasoningHeuristic: false` 禁用此功能，将每次自动调用固定为 `dialecticReasoningLevel`。可用级别：`minimal`、`low`、`medium`、`high`、`max`。
## 配置选项

Honcho 的配置文件位于 `~/.honcho/config.json`（全局）或 `$HERMES_HOME/honcho.json`（配置文件本地）。安装向导会为您处理此配置。

### 完整配置参考

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | `null`（无上限） | 每轮对话自动注入上下文的 Token 预算。设置为整数（例如 1200）以设置上限。在单词边界处截断 |
| `contextCadence` | `1` | `context()` API 调用（基础层刷新）之间的最小轮数间隔 |
| `dialecticCadence` | `2` | `peer.chat()` LLM 调用（辩证层）之间的最小轮数间隔。建议 1–5。在 `tools` 模式下不相关 — 模型调用是显式的 |
| `dialecticDepth` | `1` | 每次辩证调用中 `.chat()` 传递的次数。限制在 1–3 |
| `dialecticDepthLevels` | `null` | 每次传递的可选推理级别数组，例如 `["minimal", "low", "medium"]`。覆盖按比例分配的默认值 |
| `dialecticReasoningLevel` | `'low'` | 基础推理级别：`minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以通过工具参数在每次调用时覆盖推理级别 |
| `dialecticMaxChars` | `600` | 注入系统提示词的辩证结果的最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入 + 工具）、`context`（仅注入）、`tools`（仅工具） |
| `writeFrequency` | `'async'` | 何时刷新消息：`async`（后台线程）、`turn`（同步）、`session`（结束时批量），或整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池）。使用 `observation` 对象进行细粒度控制以覆盖此设置 |
| `messageMaxChars` | `25000` | 通过 `add_messages()` 发送的每条消息的最大字符数。如果超出则分块处理 |
| `dialecticMaxInputChars` | `10000` | 传递给 `peer.chat()` 的辩证查询输入的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`、`per-repo`、`per-session` 或 `global` |

**会话策略** 控制 Honcho 会话如何映射到您的工作：
- `per-session` — 每次 `hermes` 运行都获得一个新的会话。全新开始，通过工具访问记忆。推荐新用户使用。
- `per-directory` — 每个工作目录对应一个 Honcho 会话。上下文在多次运行间累积。
- `per-repo` — 每个 git 仓库对应一个会话。
- `global` — 跨所有目录的单一会话。

**回忆模式** 控制记忆如何流入对话：
- `hybrid` — 上下文自动注入系统提示词，并且工具可用（模型决定何时查询）。
- `context` — 仅自动注入，工具隐藏。
- `tools` — 仅工具，无自动注入。Agent 必须显式调用 `honcho_reasoning`、`honcho_search` 等。

**每种回忆模式的设置：**

| 设置 | `hybrid` | `context` | `tools` |
|---------|----------|-----------|---------|
| `writeFrequency` | 刷新消息 | 刷新消息 | 刷新消息 |
| `contextCadence` | 控制基础上下文刷新 | 控制基础上下文刷新 | 不相关 — 无注入 |
| `dialecticCadence` | 控制自动 LLM 调用 | 控制自动 LLM 调用 | 不相关 — 模型显式调用 |
| `dialecticDepth` | 每次调用多轮传递 | 每次调用多轮传递 | 不相关 — 模型显式调用 |
| `contextTokens` | 限制注入量 | 限制注入量 | 不相关 — 无注入 |
| `dialecticDynamic` | 控制模型覆盖 | N/A（无工具） | 控制模型覆盖 |

在 `tools` 模式下，模型完全掌控 — 它可以在需要时调用 `honcho_reasoning`，并选择任意的 `reasoning_level`。节奏和预算设置仅适用于具有自动注入的模式（`hybrid` 和 `context`）。

## 观察（定向 vs. 统一）

Honcho 将会话建模为对等方交换消息。每个对等方有两个观察开关，与 Honcho 的 `SessionPeerConfig` 一一对应：

| 开关 | 效果 |
|--------|--------|
| `observeMe` | Honcho 根据此对等方自己的消息构建其表征 |
| `observeOthers` | 此对等方观察其他对等方的消息（为跨对等方推理提供信息） |

两个对等方 × 两个开关 = 四个标志。`observationMode` 是一个简写预设：

| 预设 | 用户标志 | AI 标志 | 语义 |
|--------|-----------|----------|-----------|
| `"directional"`（默认） | me: 开, others: 开 | me: 开, others: 开 | 完全相互观察。启用跨对等方辩证 — “AI 根据用户所说和 AI 的回复，了解用户什么。” |
| `"unified"` | me: 开, others: 关 | me: 关, others: 开 | 共享池语义 — AI 仅观察用户的消息，用户对等方仅自我建模。单一观察者池。 |

使用显式的 `observation` 块来覆盖预设，以实现每个对等方的控制：

```json
"observation": {
  "user": { "observeMe": true,  "observeOthers": true },
  "ai":   { "observeMe": true,  "observeOthers": false }
}
```

常见模式：

| 意图 | 配置 |
|--------|--------|
| 完全观察（大多数用户） | `"observationMode": "directional"` |
| AI 不应从其自己的回复中重新建模用户 | `"ai": {"observeMe": true, "observeOthers": false}` |
| AI 对等方不应从自我观察中更新的强人格 | `"ai": {"observeMe": false, "observeOthers": true}` |

通过 [Honcho 仪表板](https://app.honcho.dev) 设置的服务器端开关优先级高于本地默认值 — Hermes 在会话初始化时会同步它们。

## 工具

当 Honcho 作为记忆提供商处于活动状态时，五个工具可用：

| 工具 | 用途 |
|------|---------|
| `honcho_profile` | 读取或更新对等方卡片 — 传递 `card`（事实列表）以更新，省略以读取 |
| `honcho_search` | 对上下文进行语义搜索 — 原始摘录，无 LLM 合成 |
| `honcho_context` | 完整会话上下文 — 摘要、表征、卡片、最近消息 |
| `honcho_reasoning` | 来自 Honcho LLM 的合成答案 — 传递 `reasoning_level`（minimal/low/medium/high/max）以控制深度 |
| `honcho_conclude` | 创建或删除结论 — 传递 `conclusion` 以创建，传递 `delete_id` 以删除（仅限 PII） |
## CLI 命令

`hermes honcho` 子命令**仅在 Honcho 作为当前激活的记忆提供商时注册**（在 `config.yaml` 中设置 `memory.provider: honcho`）。首先运行 `hermes memory setup` 并选择 Honcho；该子命令将在下次调用时出现。

```bash
hermes honcho status          # 连接状态、配置和关键设置
hermes honcho setup           # 重定向到 `hermes memory setup`
hermes honcho strategy        # 显示或设置会话策略（每个会话/每个目录/每个仓库/全局）
hermes honcho peer            # 显示或更新对等体名称 + 辩证推理级别
hermes honcho mode            # 显示或设置回忆模式（混合/上下文/工具）
hermes honcho tokens          # 显示或设置上下文和辩证推理的 Token 预算
hermes honcho identity        # 初始化或显示 AI 对等体的 Honcho 身份
hermes honcho sync            # 将 Honcho 配置同步到所有现有配置文件
hermes honcho peers           # 显示所有配置文件中的对等体身份
hermes honcho sessions        # 列出已知的 Honcho 会话映射
hermes honcho map             # 将当前目录映射到 Honcho 会话名称
hermes honcho enable          # 为活动配置文件启用 Honcho
hermes honcho disable         # 为活动配置文件禁用 Honcho
hermes honcho migrate         # 从 openclaw-honcho 迁移的逐步指南
```

## 从 `hermes honcho` 迁移

如果您之前使用过独立的 `hermes honcho setup`：

1. 您现有的配置（`honcho.json` 或 `~/.honcho/config.json`）将被保留
2. 您的服务器端数据（记忆、结论、用户配置文件）保持不变
3. 在 config.yaml 中设置 `memory.provider: honcho` 以重新激活

无需重新登录或重新设置。运行 `hermes memory setup` 并选择 "honcho" — 向导会检测到您现有的配置。

## 完整文档

完整参考请参见[记忆提供商 — Honcho](./memory-providers.md#honcho)。