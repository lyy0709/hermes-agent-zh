---
sidebar_position: 4
title: "记忆提供商"
description: "外部记忆提供商插件 — Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory"
---

# 记忆提供商

Hermes Agent 内置了 8 个外部记忆提供商插件，为 Agent 提供超越内置 MEMORY.md 和 USER.md 的持久化、跨会话知识。一次只能激活**一个**外部提供商 —— 内置记忆始终与其同时处于活动状态。

## 快速开始

```bash
hermes memory setup      # 交互式选择器 + 配置
hermes memory status     # 检查当前激活状态
hermes memory off        # 禁用外部提供商
```

你也可以通过 `hermes plugins` → Provider Plugins → Memory Provider 来选择激活的记忆提供商。

或者在 `~/.hermes/config.yaml` 中手动设置：

```yaml
memory:
  provider: openviking   # 或 honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## 工作原理

当记忆提供商激活时，Hermes 会自动：

1.  **注入提供商上下文**到系统提示词中（提供商知道的内容）
2.  **在每次对话轮次前预取相关记忆**（后台、非阻塞）
3.  **在每次响应后将对话轮次同步**到提供商
4.  **在会话结束时提取记忆**（针对支持此功能的提供商）
5.  **将内置记忆的写入操作镜像**到外部提供商
6.  **添加提供商特定的工具**，使 Agent 能够搜索、存储和管理记忆

内置记忆（MEMORY.md / USER.md）继续像以前一样工作。外部提供商是附加功能。

## 可用提供商

### Honcho

具有辩证问答、语义搜索和持久化结论的 AI 原生跨会话用户建模。

| | |
|---|---|
| **最适合** | 需要跨会话上下文、用户-Agent 对齐的多 Agent 系统 |
| **要求** | `pip install honcho-ai` + [API 密钥](https://app.honcho.dev) 或自托管实例 |
| **数据存储** | Honcho Cloud 或自托管 |
| **成本** | Honcho 定价（云端）/ 免费（自托管） |

**工具：** `honcho_profile`（对等名片）、`honcho_search`（语义搜索）、`honcho_context`（LLM 合成）、`honcho_conclude`（存储事实）

**设置向导：**
```bash
hermes honcho setup        # （旧命令）
# 或
hermes memory setup        # 选择 "honcho"
```

**配置：** `$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。解析顺序：`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。请参阅 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

<details>
<summary>关键配置选项</summary>

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | 来自 [app.honcho.dev](https://app.honcho.dev) 的 API 密钥 |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等身份 |
| `aiPeer` | host key | AI 对等身份（每个配置文件一个） |
| `workspace` | host key | 共享工作区 ID |
| `recallMode` | `hybrid` | `hybrid`（自动注入 + 工具）、`context`（仅注入）、`tools`（仅工具） |
| `observation` | all on | 每个对等的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`、`turn`、`session` 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`、`per-repo`、`per-session`、`global` |
| `dialecticReasoningLevel` | `low` | `minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 根据查询长度自动提升推理级别 |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |

</details>

<details>
<summary>最小 honcho.json 配置（云端）</summary>

```json
{
  "apiKey": "your-key-from-app.honcho.dev",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

<details>
<summary>最小 honcho.json 配置（自托管）</summary>

```json
{
  "baseUrl": "http://localhost:8000",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

:::tip 从 `hermes honcho` 迁移
如果你之前使用过 `hermes honcho setup`，你的配置和所有服务器端数据都保持不变。只需通过设置向导重新启用，或手动设置 `memory.provider: honcho` 即可通过新系统重新激活。
:::

**多 Agent / 配置文件：**

每个 Hermes 配置文件都有自己的 Honcho AI 对等体，同时共享同一个工作区 —— 所有配置文件看到相同的用户表示，但每个 Agent 构建自己的身份和观察结果。

```bash
hermes profile create coder --clone   # 创建 Honcho 对等体 "coder"，从默认配置继承设置
```

`--clone` 的作用：在 `honcho.json` 中创建一个 `hermes.coder` 主机块，包含 `aiPeer: "coder"`、共享的 `workspace`、继承的 `peerName`、`recallMode`、`writeFrequency`、`observation` 等。该对等体会在 Honcho 中预先创建，以便在第一条消息之前就存在。

对于在设置 Honcho 之前创建的配置文件：

```bash
hermes honcho sync   # 扫描所有配置文件，为任何缺失的配置文件创建主机块
```

这会从默认的 `hermes` 主机块继承设置，并为每个配置文件创建新的 AI 对等体。幂等操作 —— 跳过已有主机块的配置文件。

<details>
<summary>完整的 honcho.json 示例（多配置文件）</summary>

```json
{
  "apiKey": "your-key",
  "workspace": "hermes",
  "peerName": "eri",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "hybrid",
      "writeFrequency": "async",
      "sessionStrategy": "per-directory",
      "observation": {
        "user": { "observeMe": true, "observeOthers": true },
        "ai": { "observeMe": true, "observeOthers": true }
      },
      "dialecticReasoningLevel": "low",
      "dialecticDynamic": true,
      "dialecticMaxChars": 600,
      "messageMaxChars": 25000,
      "saveMessages": true
    },
    "hermes.coder": {
      "enabled": true,
      "aiPeer": "coder",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "tools",
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    },
    "hermes.writer": {
      "enabled": true,
      "aiPeer": "writer",
      "workspace": "hermes",
      "peerName": "eri"
    }
  },
  "sessions": {
    "/home/user/myproject": "myproject-main"
  }
}
```
</details>

查看[配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md)和[Honcho集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

---

### OpenViking

由火山引擎（字节跳动）提供的上下文数据库，具有文件系统风格的知识层次结构、分层检索以及自动提取为6类记忆的功能。

| | |
|---|---|
| **最适合** | 需要结构化浏览的自托管知识管理 |
| **要求** | `pip install openviking` + 运行服务器 |
| **数据存储** | 自托管（本地或云端） |
| **成本** | 免费（开源，AGPL-3.0协议） |

**工具：** `viking_search`（语义搜索），`viking_read`（分层：摘要/概览/全文），`viking_browse`（文件系统导航），`viking_remember`（存储事实），`viking_add_resource`（摄取URL/文档）

**设置：**
```bash
# 首先启动 OpenViking 服务器
pip install openviking
openviking-server

# 然后配置 Hermes
hermes memory setup    # 选择 "openviking"
# 或手动配置：
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```

**主要特性：**
- 分层上下文加载：L0（约100个Token）→ L1（约2k）→ L2（全文）
- 在会话提交时自动提取记忆（个人资料、偏好、实体、事件、案例、模式）
- 用于分层知识浏览的 `viking://` URI 方案

---

### Mem0

具有语义搜索、重排序和自动去重功能的服务器端LLM事实提取。

| | |
|---|---|
| **最适合** | 无需手动干预的记忆管理 — Mem0 自动处理提取 |
| **要求** | `pip install mem0ai` + API 密钥 |
| **数据存储** | Mem0 Cloud |
| **成本** | Mem0 定价 |

**工具：** `mem0_profile`（所有存储的记忆），`mem0_search`（语义搜索 + 重排序），`mem0_conclude`（存储逐字事实）

**设置：**
```bash
hermes memory setup    # 选择 "mem0"
# 或手动配置：
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/mem0.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | Agent 标识符 |

---

### Hindsight

具有知识图谱、实体解析和多策略检索的长期记忆。`hindsight_reflect` 工具提供了其他提供商不具备的跨记忆综合能力。自动保留完整的对话轮次（包括工具调用），并跟踪会话级别的文档。

| | |
|---|---|
| **最适合** | 基于知识图谱和实体关系的记忆召回 |
| **要求** | 云端：来自 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 的 API 密钥。本地：LLM API 密钥（OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight Cloud 或本地嵌入式 PostgreSQL |
| **成本** | Hindsight 定价（云端）或免费（本地） |

**工具：** `hindsight_retain`（存储并提取实体），`hindsight_recall`（多策略搜索），`hindsight_reflect`（跨记忆综合）

**设置：**
```bash
hermes memory setup    # 选择 "hindsight"
# 或手动配置：
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

设置向导会自动安装依赖项，并且只安装所选模式所需的包（云端模式安装 `hindsight-client`，本地模式安装 `hindsight-all`）。要求 `hindsight-client >= 0.4.22`（如果版本过旧，会在会话启动时自动升级）。

**本地模式 UI：** `hindsight-embed -p hermes ui start`

**配置：** `$HERMES_HOME/hindsight/config.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` 或 `local` |
| `bank_id` | `hermes` | 记忆库标识符 |
| `recall_budget` | `mid` | 召回详尽度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid`（上下文 + 工具），`context`（仅自动注入），`tools`（仅工具） |
| `auto_retain` | `true` | 自动保留对话轮次 |
| `auto_recall` | `true` | 在每轮对话前自动召回记忆 |
| `retain_async` | `true` | 在服务器上异步处理保留操作 |
| `tags` | — | 存储记忆时应用的标签 |
| `recall_tags` | — | 召回时用于过滤的标签 |

完整配置参考请查看[插件 README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md)。

---

### Holographic

本地 SQLite 事实存储，具有 FTS5 全文搜索、信任度评分和用于组合代数查询的 HRR（全息降维表示）。

| | |
|---|---|
| **最适合** | 无需外部依赖、具有高级检索功能的纯本地记忆 |
| **要求** | 无（SQLite 始终可用）。NumPy 可选，用于 HRR 代数运算。 |
| **数据存储** | 本地 SQLite |
| **成本** | 免费 |

**工具：** `fact_store`（9个操作：添加、搜索、探查、相关、推理、矛盾、更新、删除、列表），`fact_feedback`（有用/无用评分，用于训练信任度分数）

**设置：**
```bash
hermes memory setup    # 选择 "holographic"
# 或手动配置：
hermes config set memory.provider holographic
```

**配置：** `config.yaml` 中 `plugins.hermes-memory-store` 下的部分

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 在会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任度分数（0.0–1.0） |

**独特能力：**
- `probe` — 针对特定实体的代数召回（关于一个人/事物的所有事实）
- `reason` — 跨多个实体的组合 AND 查询
- `contradict` — 自动检测冲突事实
- 具有非对称反馈的信任度评分（+0.05 有用 / -0.10 无用）

---

### RetainDB

具有混合搜索（向量 + BM25 + 重排序）、7种记忆类型和增量压缩功能的云端记忆 API。

| | |
|---|---|
| **最适合** | 已经在使用 RetainDB 基础设施的团队 |
| **要求** | RetainDB 账户 + API 密钥 |
| **数据存储** | RetainDB Cloud |
| **成本** | $20/月 |
**工具：** `retaindb_profile`（用户档案）、`retaindb_search`（语义搜索）、`retaindb_context`（任务相关上下文）、`retaindb_remember`（按类型和重要性存储）、`retaindb_forget`（删除记忆）

**设置：**
```bash
hermes memory setup    # 选择 "retaindb"
# 或手动设置：
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

---

### ByteRover

通过 `brv` CLI 实现持久化记忆 —— 具有分层检索（模糊文本 → LLM 驱动搜索）的分层知识树。本地优先，可选云同步。

| | |
|---|---|
| **最适合** | 希望拥有便携、本地优先记忆且使用 CLI 的开发者 |
| **要求** | ByteRover CLI (`npm install -g byterover-cli` 或 [安装脚本](https://byterover.dev)) |
| **数据存储** | 本地（默认）或 ByteRover Cloud（可选同步） |
| **成本** | 免费（本地）或 ByteRover 定价（云） |

**工具：** `brv_query`（搜索知识树）、`brv_curate`（存储事实/决策/模式）、`brv_status`（CLI 版本 + 树统计信息）

**设置：**
```bash
# 首先安装 CLI
curl -fsSL https://byterover.dev/install.sh | sh

# 然后配置 Hermes
hermes memory setup    # 选择 "byterover"
# 或手动设置：
hermes config set memory.provider byterover
```

**关键特性：**
- 自动预压缩提取（在上下文压缩丢弃信息前保存见解）
- 知识树存储在 `$HERMES_HOME/byterover/`（按配置文件作用域）
- SOC2 Type II 认证的云同步（可选）

---

### Supermemory

通过 Supermemory 图 API 实现具有档案召回、语义搜索、显式记忆工具以及会话结束时会话内容摄取功能的语义长期记忆。

| | |
|---|---|
| **最适合** | 具有用户画像和会话级图构建的语义召回 |
| **要求** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory Cloud |
| **成本** | Supermemory 定价 |

**工具：** `supermemory_store`（保存显式记忆）、`supermemory_search`（语义相似性搜索）、`supermemory_forget`（按 ID 或最佳匹配查询遗忘）、`supermemory_profile`（持久化档案 + 近期上下文）

**设置：**
```bash
hermes memory setup    # 选择 "supermemory"
# 或手动设置：
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/supermemory.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持 `{identity}` 模板用于按配置文件作用域的标签。 |
| `auto_recall` | `true` | 在每次轮次前注入相关记忆上下文 |
| `auto_capture` | `true` | 每次响应后存储清理后的用户-助手轮次 |
| `max_recall_results` | `10` | 格式化到上下文中的最大召回项数 |
| `profile_frequency` | `50` | 在首次轮次及之后每 N 轮次包含档案事实 |
| `capture_mode` | `all` | 默认跳过微小或琐碎的轮次 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents` |
| `api_timeout` | `5.0` | SDK 和摄取请求的超时时间 |

**环境变量：** `SUPERMEMORY_API_KEY`（必需）、`SUPERMEMORY_CONTAINER_TAG`（覆盖配置）。

**关键特性：**
- 自动上下文隔离 —— 从捕获的轮次中剥离召回的回忆，以防止递归记忆污染
- 会话结束时会话内容摄取，用于更丰富的图级知识构建
- 档案事实在首次轮次和可配置间隔时注入
- 琐碎消息过滤（跳过 "ok"、"thanks" 等）
- **按配置文件作用域的容器** —— 在 `container_tag` 中使用 `{identity}`（例如 `hermes-{identity}` → `hermes-coder`）以隔离每个 Hermes 配置文件的记忆
- **多容器模式** —— 启用 `enable_custom_container_tags` 并配置 `custom_containers` 列表，允许 Agent 跨命名容器读写。自动操作（同步、预取）保持在主容器上。

<details>
<summary>多容器示例</summary>

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "shared-knowledge"],
  "custom_container_instructions": "Use project-alpha for coding context."
}
```

</details>

**支持：** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)

---

## 提供商对比

| 提供商 | 存储 | 成本 | 工具 | 依赖项 | 独特功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云 | 付费 | 4 | `honcho-ai` | 辩证用户建模 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层次结构 + 分层加载 |
| **Mem0** | 云 | 付费 | 3 | `mem0ai` | 服务端 LLM 提取 |
| **Hindsight** | 云/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反思合成 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR 代数 + 信任评分 |
| **RetainDB** | 云 | $20/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云 | 免费/付费 | 3 | `brv` CLI | 预压缩提取 |
| **Supermemory** | 云 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图摄取 + 多容器 |

## 配置文件隔离

每个提供商的数据都按[配置文件](/docs/user-guide/profiles)隔离：

- **本地存储提供商**（Holographic、ByteRover）使用 `$HERMES_HOME/` 路径，每个配置文件不同
- **配置文件提供商**（Honcho、Mem0、Hindsight、Supermemory）将配置存储在 `$HERMES_HOME/` 中，因此每个配置文件都有自己的凭据
- **云提供商**（RetainDB）自动派生按配置文件作用域的项目名称
- **环境变量提供商**（OpenViking）通过每个配置文件的 `.env` 文件配置

## 构建记忆提供商

有关如何创建自己的记忆提供商，请参阅[开发者指南：记忆提供商插件](/docs/developer-guide/memory-provider-plugin)。