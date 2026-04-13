# 上下文压缩与缓存

Hermes Agent 采用双压缩系统和 Anthropic 提示词缓存，以在长对话中高效管理上下文窗口使用。

源文件：`agent/context_engine.py` (ABC), `agent/context_compressor.py` (默认引擎), `agent/prompt_caching.py`, `gateway/run.py` (会话清理), `run_agent.py` (搜索 `_compress_context`)

## 可插拔的上下文引擎

上下文管理基于 `ContextEngine` 抽象基类 (`agent/context_engine.py`)。内置的 `ContextCompressor` 是默认实现，但插件可以用其他引擎替换它（例如，无损上下文管理）。

```yaml
context:
  engine: "compressor"    # 默认值 — 内置有损摘要
  engine: "lcm"           # 示例 — 提供无损上下文的插件
```

引擎负责：
- 决定何时应触发压缩 (`should_compress()`)
- 执行压缩 (`compress()`)
- 可选地暴露 Agent 可以调用的工具（例如，`lcm_grep`）
- 跟踪来自 API 响应的 Token 使用情况

选择是通过 `config.yaml` 中的 `context.engine` 配置驱动的。解析顺序为：
1. 检查 `plugins/context_engine/<name>/` 目录
2. 检查通用插件系统 (`register_context_engine()`)
3. 回退到内置的 `ContextCompressor`

插件引擎**永远不会自动激活** — 用户必须显式地将 `context.engine` 设置为插件的名称。默认的 `"compressor"` 始终使用内置引擎。

通过 `hermes plugins` → Provider Plugins → Context Engine 配置，或直接编辑 `config.yaml`。

关于构建上下文引擎插件，请参阅[上下文引擎插件](/docs/developer-guide/context-engine-plugin)。

## 双压缩系统

Hermes 有两个独立的压缩层，它们独立运行：

```
                     ┌──────────────────────────┐
  传入消息           │   消息网关会话清理        │  在上下文达到 85% 时触发
  ─────────────────► │   (Agent 处理前，粗略估计) │  大型会话的安全网
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │   Agent ContextCompressor │  在上下文达到 50% 时触发 (默认)
                     │   (循环内，真实 Token 数)  │  常规上下文管理
                     └──────────────────────────┘
```

### 1. 消息网关会话清理 (85% 阈值)

位于 `gateway/run.py` (搜索 `_maybe_compress_session`)。这是一个**安全网**，在 Agent 处理消息之前运行。它防止会话在轮次之间变得过大时（例如，Telegram/Discord 中过夜累积）导致 API 失败。

- **阈值**：固定为模型上下文长度的 85%
- **Token 来源**：优先使用上一轮 API 报告的实际 Token 数；回退到基于字符的粗略估计 (`estimate_messages_tokens_rough`)
- **触发条件**：仅当 `len(history) >= 4` 且压缩启用时
- **目的**：捕获那些逃脱了 Agent 自身压缩器的会话

消息网关清理阈值有意设置得比 Agent 的压缩器更高。将其设置为 50%（与 Agent 相同）会导致在长网关会话中每一轮都过早压缩。

### 2. Agent ContextCompressor (50% 阈值，可配置)

位于 `agent/context_compressor.py`。这是**主要的压缩系统**，在 Agent 的工具循环内运行，可以访问准确的、API 报告的 Token 计数。

## 配置

所有压缩设置都从 `config.yaml` 中的 `compression` 键下读取：

```yaml
compression:
  enabled: true              # 启用/禁用压缩 (默认: true)
  threshold: 0.50            # 上下文窗口的分数 (默认: 0.50 = 50%)
  target_ratio: 0.20         # 将多少阈值部分保留为尾部 (默认: 0.20)
  protect_last_n: 20         # 最小受保护的尾部消息数 (默认: 20)
  summary_model: null        # 覆盖用于摘要的模型 (默认: 使用辅助模型)
```

### 参数详情

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `threshold` | `0.50` | 0.0-1.0 | 当提示词 Token 数 ≥ `threshold × context_length` 时触发压缩 |
| `target_ratio` | `0.20` | 0.10-0.80 | 控制尾部保护的 Token 预算：`threshold_tokens × target_ratio` |
| `protect_last_n` | `20` | ≥1 | 始终保留的最少最近消息数 |
| `protect_first_n` | `3` | (硬编码) | 系统提示词 + 首次交换始终保留 |

### 计算值（针对默认设置下的 200K 上下文模型）

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```

## 压缩算法

`ContextCompressor.compress()` 方法遵循 4 阶段算法：

### 阶段 1：修剪旧的工具结果（廉价，无需 LLM 调用）

受保护尾部之外的旧工具结果（>200 字符）被替换为：
```
[旧工具输出已清除以节省上下文空间]
```

这是一个廉价的预处理，可以从冗长的工具输出（文件内容、终端输出、搜索结果）中节省大量 Token。

### 阶段 2：确定边界

```
┌─────────────────────────────────────────────────────────────┐
│  消息列表                                                   │
│                                                             │
│  [0..2]  ← protect_first_n (系统提示词 + 首次交换)          │
│  [3..N]  ← 中间轮次 → 被摘要化                              │
│  [N..end] ← 尾部 (基于 Token 预算 或 protect_last_n)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

尾部保护是**基于 Token 预算的**：从末尾向前遍历，累积 Token 直到预算耗尽。如果预算保护的消息更少，则回退到固定的 `protect_last_n` 计数。

边界会进行对齐，以避免分割 tool_call/tool_result 组。`_align_boundary_backward()` 方法会遍历连续的工具结果以找到父助理消息，保持组完整。
### 阶段 3：生成结构化摘要

:::warning 摘要模型的上下文长度
摘要模型的上下文窗口**必须至少与**主 Agent 模型的一样大。整个中间部分会在一次 `call_llm(task="compression")` 调用中发送给摘要模型。如果摘要模型的上下文更小，API 会返回一个上下文长度错误 —— `_generate_summary()` 会捕获它，记录一个警告，并返回 `None`。然后压缩器会**在没有摘要的情况下**丢弃中间轮次，悄无声息地丢失会话上下文。这是导致压缩质量下降的最常见原因。
:::

中间轮次使用辅助 LLM 和结构化模板进行摘要：

```
## 目标
[用户试图完成什么]

## 约束与偏好
[用户偏好、编码风格、约束条件、重要决策]

## 进展
### 已完成
[已完成的工作 —— 具体的文件路径、运行的命令、结果]
### 进行中
[当前正在进行的工作]
### 受阻
[遇到的任何阻碍或问题]

## 关键决策
[重要的技术决策及其原因]

## 相关文件
[读取、修改或创建的文件 —— 每个文件附简要说明]

## 后续步骤
[接下来需要做什么]

## 关键上下文
[具体的值、错误信息、配置详情]
```

摘要的预算根据要压缩的内容量进行缩放：
- 公式：`content_tokens × 0.20`（`_SUMMARY_RATIO` 常量）
- 最小值：2,000 个 Token
- 最大值：`min(context_length × 0.05, 12,000)` 个 Token

### 阶段 4：组装压缩后的消息

压缩后的消息列表是：
1. 头部消息（首次压缩时会在系统提示词后附加一个说明）
2. 摘要消息（选择角色以避免连续出现相同角色的违规情况）
3. 尾部消息（未修改）

孤立的 tool_call/tool_result 对由 `_sanitize_tool_pairs()` 清理：
- 引用已移除调用的工具结果 → 被移除
- 其结果已被移除的工具调用 → 注入存根结果

### 迭代式重新压缩

在后续的压缩中，之前的摘要会连同**更新**它的指令一起传递给 LLM，而不是从头开始摘要。这可以在多次压缩中保留信息 —— 项目从“进行中”移动到“已完成”，添加新的进展，并移除过时的信息。

压缩器实例上的 `_previous_summary` 字段用于存储上一次的摘要文本。

## 压缩前后示例

### 压缩前（45 条消息，约 95K Token）

```
[0] system:    "You are a helpful assistant..." (系统提示词)
[1] user:      "Help me set up a FastAPI project"
[2] assistant: <tool_call> terminal: mkdir project </tool_call>
[3] tool:      "directory created"
[4] assistant: <tool_call> write_file: main.py </tool_call>
[5] tool:      "file written (2.3KB)"
    ... 30 多轮文件编辑、测试、调试 ...
[38] assistant: <tool_call> terminal: pytest </tool_call>
[39] tool:      "8 passed, 2 failed\n..."  (5KB 输出)
[40] user:      "Fix the failing tests"
[41] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[42] tool:      "import pytest\n..."  (3KB)
[43] assistant: "I see the issue with the test fixtures..."
[44] user:      "Great, also add error handling"
```

### 压缩后（25 条消息，约 45K Token）

```
[0] system:    "You are a helpful assistant...
               [Note: Some earlier conversation turns have been compacted...]"
[1] user:      "Help me set up a FastAPI project"
[2] assistant: "[CONTEXT COMPACTION] Earlier turns were compacted...

               ## 目标
               设置一个带有测试和错误处理的 FastAPI 项目

               ## 进展
               ### 已完成
               - 创建了项目结构：main.py, tests/, requirements.txt
               - 在 main.py 中实现了 5 个 API 端点
               - 在 tests/test_api.py 中编写了 10 个测试用例
               - 10 个测试中有 8 个通过

               ### 进行中
               - 修复 2 个失败的测试 (test_create_user, test_delete_user)

               ## 相关文件
               - main.py — 包含 5 个端点的 FastAPI 应用
               - tests/test_api.py — 10 个测试用例
               - requirements.txt — fastapi, pytest, httpx

               ## 后续步骤
               - 修复失败的测试夹具
               - 添加错误处理"
[3] user:      "Fix the failing tests"
[4] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[5] tool:      "import pytest\n..."
[6] assistant: "I see the issue with the test fixtures..."
[7] user:      "Great, also add error handling"
```


## 提示词缓存（Anthropic）

来源：`agent/prompt_caching.py`

通过缓存对话前缀，在多轮对话中减少约 75% 的输入 Token 成本。使用 Anthropic 的 `cache_control` 断点。

### 策略：system_and_3

Anthropic 允许每个请求最多有 4 个 `cache_control` 断点。Hermes 使用 "system_and_3" 策略：

```
断点 1: 系统提示词           (在所有轮次中稳定)
断点 2: 倒数第 3 条非系统消息  ─┐
断点 3: 倒数第 2 条非系统消息   ├─ 滚动窗口
断点 4: 最后一条非系统消息      ─┘
```

### 工作原理

`apply_anthropic_cache_control()` 深度复制消息并注入 `cache_control` 标记：

```python
# 缓存标记格式
marker = {"type": "ephemeral"}
# 或者对于 1 小时 TTL：
marker = {"type": "ephemeral", "ttl": "1h"}
```

标记根据内容类型以不同方式应用：

| 内容类型 | 标记放置位置 |
|-------------|-------------------|
| 字符串内容 | 转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` |
| 列表内容 | 添加到最后一个元素的字典中 |
| 无/空 | 添加为 `msg["cache_control"]` |
| 工具消息 | 添加为 `msg["cache_control"]`（仅限原生 Anthropic） |

### 缓存感知的设计模式

1.  **稳定的系统提示词**：系统提示词是断点 1，并在所有轮次中被缓存。避免在对话中途修改它（压缩仅在第一次压缩时附加说明）。
2. **消息顺序很重要**：缓存命中需要前缀匹配。在中间添加或删除消息会使之后的所有内容缓存失效。

3. **压缩缓存交互**：压缩后，压缩区域的缓存会失效，但系统提示词缓存会保留。滚动的 3 条消息窗口会在 1-2 轮对话内重新建立缓存。

4. **TTL 选择**：默认是 `5m`（5 分钟）。对于用户在两轮对话之间有长时间休息的长时间运行会话，请使用 `1h`。

### 启用提示词缓存

提示词缓存在以下情况下会自动启用：
- 模型是 Anthropic Claude 模型（通过模型名称检测）
- 提供商支持 `cache_control`（原生的 Anthropic API 或 OpenRouter）

```yaml
# config.yaml — TTL 是可配置的
model:
  cache_ttl: "5m"   # "5m" 或 "1h"
```

CLI 在启动时会显示缓存状态：
```
💾 提示词缓存：已启用（通过 OpenRouter 的 Claude，5m TTL）
```

## 上下文压力警告

Agent 在压缩阈值的 85% 时（不是上下文的 85% — 是阈值本身的 85%，而阈值是上下文的 50%）会发出上下文压力警告：

```
⚠️  上下文已达到压缩阈值的 85%（42,500/50,000 个 Token）
```

压缩后，如果使用率降至阈值 85% 以下，警告状态会被清除。如果压缩未能将使用率降低到警告水平以下（对话内容过于密集），警告会持续存在，但压缩不会再次触发，直到再次超过阈值。