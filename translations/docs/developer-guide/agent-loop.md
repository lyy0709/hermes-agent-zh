---
sidebar_position: 3
title: "Agent 循环内部机制"
description: "详细解析 AIAgent 的执行流程、API 模式、工具、回调以及回退行为"
---

# Agent 循环内部机制

核心编排引擎是 `run_agent.py` 中的 `AIAgent` 类 —— 大约 10,700 行代码，负责处理从提示词组装到工具调度再到提供商故障转移的一切事务。

## 核心职责

`AIAgent` 负责：

- 通过 `prompt_builder.py` 组装有效的系统提示词和工具模式
- 选择正确的提供商/API 模式（chat_completions、codex_responses、anthropic_messages）
- 发起支持取消操作的可中断模型调用
- 执行工具调用（通过线程池顺序或并发执行）
- 以 OpenAI 消息格式维护对话历史
- 处理压缩、重试和回退模型切换
- 跟踪父 Agent 和子 Agent 的迭代预算
- 在上下文丢失前刷新持久化记忆

## 两个入口点

```python
# 简单接口 —— 返回最终响应字符串
response = agent.chat("修复 main.py 中的 bug")

# 完整接口 —— 返回包含消息、元数据、使用统计信息的字典
result = agent.run_conversation(
    user_message="修复 main.py 中的 bug",
    system_message=None,           # 如果省略则自动构建
    conversation_history=None,      # 如果省略则从会话自动加载
    task_id="task_abc123"
)
```

`chat()` 是 `run_conversation()` 的一个薄包装层，从结果字典中提取 `final_response` 字段。

## API 模式

Hermes 支持三种 API 执行模式，根据提供商选择、显式参数和基础 URL 启发式规则解析得出：

| API 模式 | 用于 | 客户端类型 |
|----------|----------|-------------|
| `chat_completions` | OpenAI 兼容端点（OpenRouter、自定义、大多数提供商） | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | `openai.OpenAI` 配合 Responses 格式 |
| `anthropic_messages` | 原生 Anthropic Messages API | 通过适配器使用 `anthropic.Anthropic` |

模式决定了消息的格式化方式、工具调用的结构、响应的解析方式以及缓存/流式传输的工作方式。在 API 调用前后，所有三种模式都会收敛到相同的内部消息格式（OpenAI 风格的 `role`/`content`/`tool_calls` 字典）。

**模式解析顺序：**
1. 显式的 `api_mode` 构造函数参数（最高优先级）
2. 提供商特定检测（例如，`anthropic` 提供商 → `anthropic_messages`）
3. 基础 URL 启发式规则（例如，`api.anthropic.com` → `anthropic_messages`）
4. 默认：`chat_completions`

## 轮次生命周期

Agent 循环的每次迭代都遵循以下顺序：

```text
run_conversation()
  1. 如果未提供则生成 task_id
  2. 将用户消息追加到对话历史
  3. 构建或重用缓存的系统提示词（prompt_builder.py）
  4. 检查是否需要预检压缩（>50% 上下文）
  5. 根据对话历史构建 API 消息
     - chat_completions：原样使用 OpenAI 格式
     - codex_responses：转换为 Responses API 输入项
     - anthropic_messages：通过 anthropic_adapter.py 转换
  6. 注入临时提示词层（预算警告、上下文压力）
  7. 如果使用 Anthropic 则应用提示词缓存标记
  8. 发起可中断的 API 调用（_api_call_with_interrupt）
  9. 解析响应：
     - 如果包含 tool_calls：执行它们，追加结果，循环回到步骤 5
     - 如果是文本响应：持久化会话，如果需要则刷新记忆，返回
```

### 消息格式

所有消息在内部都使用 OpenAI 兼容格式：

```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

推理内容（来自支持扩展思考的模型）存储在 `assistant_msg["reasoning"]` 中，并可通过 `reasoning_callback` 选择性地显示。

### 消息交替规则

Agent 循环强制执行严格的消息角色交替：

- 系统消息之后：`用户 → 助手 → 用户 → 助手 → ...`
- 工具调用期间：`助手（带 tool_calls）→ 工具 → 工具 → ... → 助手`
- **绝不**连续出现两个助手消息
- **绝不**连续出现两个用户消息
- **只有** `tool` 角色可以连续出现（并行工具结果）

提供商会验证这些序列，并拒绝格式错误的历史记录。

## 可中断的 API 调用

API 请求被包装在 `_api_call_with_interrupt()` 中，该函数在后台线程中运行实际的 HTTP 调用，同时监控一个中断事件：

```text
┌──────────────────────┐     ┌──────────────┐
│  主线程              │     │  API 线程    │
│  等待：              │────▶│  HTTP POST   │
│  - 响应就绪          │     │  到提供商    │
│  - 中断事件          │     └──────────────┘
│  - 超时              │
└──────────────────────┘
```

当被中断时（用户发送新消息、`/stop` 命令或信号）：
- API 线程被放弃（响应被丢弃）
- Agent 可以处理新的输入或干净地关闭
- 没有部分响应被注入到对话历史中

## 工具执行

### 顺序执行 vs 并发执行

当模型返回工具调用时：

- **单个工具调用** → 在主线程中直接执行
- **多个工具调用** → 通过 `ThreadPoolExecutor` 并发执行
  - 例外：标记为交互式的工具（例如 `clarify`）强制顺序执行
  - 无论完成顺序如何，结果都按原始工具调用顺序重新插入

### 执行流程

```text
对于 response.tool_calls 中的每个 tool_call：
    1. 从 tools/registry.py 解析处理器
    2. 触发 pre_tool_call 插件钩子
    3. 检查是否为危险命令（tools/approval.py）
       - 如果是危险的：调用 approval_callback，等待用户
    4. 使用 args + task_id 执行处理器
    5. 触发 post_tool_call 插件钩子
    6. 将 {"role": "tool", "content": result} 追加到历史记录
```

### Agent 级别工具

有些工具在到达 `handle_function_call()` *之前* 被 `run_agent.py` 拦截：

| 工具 | 为何被拦截 |
|------|--------------------|
| `todo` | 读取/写入 Agent 本地的任务状态 |
| `memory` | 写入具有字符限制的持久化记忆文件 |
| `session_search` | 通过 Agent 的会话数据库查询会话历史 |
| `delegate_task` | 生成具有隔离上下文的子 Agent |

这些工具直接修改 Agent 状态，并返回合成的工具结果，而无需经过注册表。

## 回调接口

`AIAgent` 支持特定于平台的回调，这些回调能够在 CLI、消息网关和 ACP 集成中实现实时进度显示：

| 回调 | 触发时机 | 使用者 |
|----------|-----------|---------|
| `tool_progress_callback` | 每次工具执行前/后 | CLI 旋转器、消息网关进度消息 |
| `thinking_callback` | 模型开始/停止思考时 | CLI "thinking..." 指示器 |
| `reasoning_callback` | 模型返回推理内容时 | CLI 推理显示、消息网关推理块 |
| `clarify_callback` | 调用 `clarify` 工具时 | CLI 输入提示、消息网关交互式消息 |
| `step_callback` | 每次完整的 Agent 轮次之后 | 消息网关步骤跟踪、ACP 进度 |
| `stream_delta_callback` | 每个流式 Token（启用时） | CLI 流式显示 |
| `tool_gen_callback` | 从流中解析出工具调用时 | CLI 旋转器中的工具预览 |
| `status_callback` | 状态变更时（思考、执行等） | ACP 状态更新 |

## 预算和回退行为

### 迭代预算

Agent 通过 `IterationBudget` 跟踪迭代次数：

- 默认：90 次迭代（可通过 `agent.max_turns` 配置）
- 每个 Agent 都有自己的预算。子 Agent 获得独立的预算，上限为 `delegation.max_iterations`（默认 50）—— 父 Agent 和子 Agent 的总迭代次数可以超过父 Agent 的上限
- 达到 100% 时，Agent 停止并返回已完成工作的摘要

### 回退模型

当主模型失败时（429 速率限制、5xx 服务器错误、401/403 认证错误）：

1. 检查配置中的 `fallback_providers` 列表
2. 按顺序尝试每个回退模型
3. 成功后，使用新的提供商继续对话
4. 遇到 401/403 时，在故障转移前尝试刷新凭据

回退系统也独立覆盖辅助任务 —— 视觉、压缩、网页提取和会话搜索各自都有可通过 `auxiliary.*` 配置部分配置的回退链。

## 压缩和持久化

### 压缩触发时机

- **预检**（API 调用前）：如果对话超过模型上下文窗口的 50%
- **消息网关自动压缩**：如果对话超过 85%（更激进，在轮次之间运行）

### 压缩期间发生什么

1. 首先将记忆刷新到磁盘（防止数据丢失）
2. 中间的对话轮次被总结成一个紧凑的摘要
3. 最后 N 条消息被完整保留（`compression.protect_last_n`，默认：20）
4. 工具调用/结果消息对被保持在一起（永不拆分）
5. 生成一个新的会话谱系 ID（压缩会创建一个“子”会话）

### 会话持久化

每次轮次之后：
- 消息被保存到会话存储（通过 `hermes_state.py` 使用 SQLite）
- 记忆变更被刷新到 `MEMORY.md` / `USER.md`
- 稍后可以通过 `/resume` 或 `hermes chat --resume` 恢复会话

## 关键源文件

| 文件 | 用途 |
|------|---------|
| `run_agent.py` | AIAgent 类 —— 完整的 Agent 循环（约 10,700 行） |
| `agent/prompt_builder.py` | 从记忆、技能、上下文文件、人格组装系统提示词 |
| `agent/context_engine.py` | ContextEngine ABC —— 可插拔的上下文管理 |
| `agent/context_compressor.py` | 默认引擎 —— 有损摘要算法 |
| `agent/prompt_caching.py` | Anthropic 提示词缓存标记和缓存指标 |
| `agent/auxiliary_client.py` | 用于辅助任务的辅助 LLM 客户端（视觉、摘要） |
| `model_tools.py` | 工具模式收集、`handle_function_call()` 调度 |

## 相关文档

- [提供商运行时解析](./provider-runtime.md)
- [提示词组装](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [工具运行时](./tools-runtime.md)
- [架构概述](./architecture.md)