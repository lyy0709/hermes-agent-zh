---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、调度、编辑、暂停、加载技能以及交付定时任务"
---

# Cron 内部机制

cron 子系统提供定时任务执行功能——从简单的一次性延迟任务，到具有技能注入和跨平台交付功能的、基于 cron 表达式的周期性任务。

## 关键文件

| 文件 | 用途 |
|------|---------|
| `cron/jobs.py` | 任务模型、存储、对 `jobs.json` 的原子读写 |
| `cron/scheduler.py` | 调度器循环——检测到期任务、执行、跟踪重复 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册和处理程序 |
| `gateway/run.py` | 消息网关集成——在长运行循环中进行 cron 滴答 |
| `hermes_cli/cron.py` | CLI `hermes cron` 子命令 |

## 调度模型

支持四种调度格式：

| 格式 | 示例 | 行为 |
|--------|---------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 一次性，在指定持续时间后触发 |
| **时间间隔** | `every 2h`, `every 30m` | 周期性，以固定时间间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准的 5 字段 cron 语法（分钟、小时、日、月、星期几） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 一次性，在精确时间触发 |

面向模型的接口是一个单一的 `cronjob` 工具，具有操作风格的动作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中，具有原子写入语义（写入临时文件，然后重命名）。每个任务记录包含：

```json
{
  "id": "job_abc123",
  "name": "每日简报",
  "prompt": "总结今天的 AI 新闻和融资轮次",
  "schedule": "0 9 * * *",
  "skills": ["ai-funding-daily-report"],
  "deliver": "telegram:-1001234567890",
  "repeat": null,
  "state": "scheduled",
  "next_run": "2025-01-16T09:00:00Z",
  "run_count": 42,
  "created_at": "2025-01-01T00:00:00Z",
  "model": null,
  "provider": null,
  "script": null
}
```

### 任务生命周期状态

| 状态 | 含义 |
|-------|---------|
| `scheduled` | 活跃状态，将在下一个预定时间触发 |
| `paused` | 已暂停——在恢复前不会触发 |
| `completed` | 重复次数耗尽或已触发的一次性任务 |
| `running` | 当前正在执行（临时状态） |

### 向后兼容性

较旧的任务可能只有一个 `skill` 字段，而不是 `skills` 数组。调度器在加载时会将其规范化——单个 `skill` 会被提升为 `skills: [skill]`。

## 调度器运行时

### 滴答周期

调度器按周期性的滴答运行（默认：每 60 秒）：

```text
tick()
  1. 获取调度器锁（防止滴答重叠）
  2. 从 jobs.json 加载所有任务
  3. 筛选出到期任务 (next_run <= now AND state == "scheduled")
  4. 对于每个到期任务：
     a. 将状态设置为 "running"
     b. 创建全新的 AIAgent 会话（无对话历史）
     c. 按顺序加载附加的技能（作为用户消息注入）
     d. 通过 Agent 运行任务提示词
     e. 将响应交付到配置的目标
     f. 更新 run_count，计算 next_run
     g. 如果重复次数耗尽 → state = "completed"
     h. 否则 → state = "scheduled"
  5. 将更新后的任务写回 jobs.json
  6. 释放调度器锁
```

### 消息网关集成

在消息网关模式下，调度器滴答被集成到消息网关的主事件循环中。消息网关在其周期性维护循环中调用 `scheduler.tick()`，该循环与消息处理并行运行。

在 CLI 模式下，定时任务仅在运行 `hermes cron` 命令时或在活跃的 CLI 会话期间触发。

### 全新会话隔离

每个定时任务都在一个全新的 Agent 会话中运行：

- 没有之前运行的对话历史
- 不记得之前的定时任务执行（除非持久化到记忆/文件中）
- 提示词必须是自包含的——定时任务不能询问澄清性问题
- `cronjob` 工具集被禁用（递归防护）

## 基于技能的任务

定时任务可以通过 `skills` 字段附加一个或多个技能。在执行时：

1. 技能按指定顺序加载
2. 每个技能的 SKILL.md 内容作为上下文注入
3. 任务的提示词作为任务指令追加
4. Agent 处理组合后的技能上下文 + 提示词

这使得无需将完整指令粘贴到定时任务提示词中，即可实现可重用、经过测试的工作流。例如：

```
创建每日融资报告 → 附加 "ai-funding-daily-report" 技能
```

### 基于脚本的任务

任务也可以通过 `script` 字段附加一个 Python 脚本。该脚本在每次 Agent 轮次*之前*运行，其标准输出作为上下文注入到提示词中。这使得数据收集和变更检测模式成为可能：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# 获取竞争对手的发布说明，与上次运行进行差异比较
# 将摘要打印到标准输出 —— Agent 分析并报告
```

脚本超时时间默认为 120 秒。`_get_script_timeout()` 通过三层链解析超时限制：

1.  **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试/猴子补丁）。仅在与默认值不同时使用。
2.  **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3.  **配置** — `config.yaml` 中的 `cron.script_timeout_seconds`（通过 `load_config()` 读取）
4.  **默认值** — 120 秒

### 提供商恢复

`run_job()` 将用户配置的备用提供商和凭据池传递给 `AIAgent` 实例：

-   **备用提供商** — 从 `config.yaml` 读取 `fallback_providers`（列表）或 `fallback_model`（旧版字典），与消息网关的 `_load_fallback_model()` 模式匹配。作为 `fallback_model=` 传递给 `AIAgent.__init__`，后者将两种格式都规范化为备用链。
-   **凭据池** — 使用解析出的运行时提供商名称，通过 `agent.credential_pool` 中的 `load_pool(provider)` 加载。仅在池中有凭据时传递（`pool.has_credentials()`）。这使得在 429/速率限制错误时能够进行同提供商密钥轮换。

这镜像了消息网关的行为——没有它，定时任务 Agent 在遇到速率限制时将无法尝试恢复。

## 交付模型

定时任务结果可以交付到任何支持的平台：

| 目标 | 语法 | 示例 |
|--------|--------|---------|
| 原始聊天 | `origin` | 交付到创建任务的聊天 |
| 本地文件 | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram` 或 `telegram:<chat_id>` | `telegram:-1001234567890` |
| Discord | `discord` 或 `discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 交付到 Slack 主频道 |
| WhatsApp | `whatsapp` | 交付到 WhatsApp 主聊天 |
| Signal | `signal` | 交付到 Signal |
| Matrix | `matrix` | 交付到 Matrix 主房间 |
| Mattermost | `mattermost` | 交付到 Mattermost 主频道 |
| Email | `email` | 通过电子邮件交付 |
| SMS | `sms` | 通过短信交付 |
| Home Assistant | `homeassistant` | 交付到 HA 对话 |
| 钉钉 | `dingtalk` | 交付到钉钉 |
| 飞书 | `feishu` | 交付到飞书 |
| 企业微信 | `wecom` | 交付到企业微信 |
| 微信 | `weixin` | 交付到微信 |
| BlueBubbles | `bluebubbles` | 通过 BlueBubbles 交付到 iMessage |

对于 Telegram 话题，使用格式 `telegram:<chat_id>:<thread_id>`（例如，`telegram:-1001234567890:17585`）。

### 响应包装

默认情况下（`cron.wrap_response: true`），定时任务交付会包装以下内容：
- 标识定时任务名称和任务的标题
- 注明 Agent 在对话中看不到已交付消息的页脚

定时任务响应中的 `[SILENT]` 前缀会完全抑制交付——适用于只需要写入文件或执行副作用的任务。

### 会话隔离

定时任务交付**不会**镜像到消息网关会话的对话历史中。它们只存在于定时任务自身的会话中。这防止了目标聊天对话中出现消息交替违规。

## 递归防护

定时任务运行的会话禁用了 `cronjob` 工具集。这防止了：
- 预定任务创建新的定时任务
- 可能导致 Token 使用量激增的递归调度
- 在任务内部意外修改任务计划

## 锁定

调度器使用基于文件的锁定，以防止重叠的滴答两次执行同一批到期任务。这在消息网关模式下很重要，因为如果前一个滴答花费的时间超过滴答间隔，多个维护周期可能会重叠。

## CLI 接口

`hermes cron` CLI 提供直接的任务管理：

```bash
hermes cron list                    # 显示所有任务
hermes cron create                  # 交互式任务创建（别名：add）
hermes cron edit <job_id>           # 编辑任务配置
hermes cron pause <job_id>          # 暂停正在运行的任务
hermes cron resume <job_id>         # 恢复已暂停的任务
hermes cron run <job_id>            # 触发立即执行
hermes cron remove <job_id>         # 删除任务
```

## 相关文档

-   [Cron 功能指南](/docs/user-guide/features/cron)
-   [消息网关内部机制](./gateway-internals.md)
-   [Agent 循环内部机制](./agent-loop.md)