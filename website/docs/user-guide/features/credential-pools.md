---
title: 凭证池
description: 为每个提供商池化多个 API 密钥或 OAuth 令牌，以实现自动轮换和速率限制恢复。
sidebar_label: 凭证池
sidebar_position: 9
---

# 凭证池

凭证池允许您为同一提供商注册多个 API 密钥或 OAuth 令牌。当一个密钥达到速率限制或计费配额时，Hermes 会自动轮换到下一个健康的密钥——无需切换提供商即可保持会话活动。

这与[备用提供商](./fallback-providers.md)不同，后者会完全切换到*不同的*提供商。凭证池是同一提供商内的轮换；备用提供商是跨提供商的故障转移。系统会首先尝试凭证池——如果池中所有密钥都已耗尽，*然后*才会激活备用提供商。

## 工作原理

```
您的请求
  → 从池中选取密钥 (round_robin / least_used / fill_first / random)
  → 发送给提供商
  → 429 速率限制？
      → 重试同一密钥一次（瞬时故障）
      → 第二次 429 → 轮换到池中下一个密钥
      → 所有密钥耗尽 → fallback_model（不同提供商）
  → 402 计费错误？
      → 立即轮换到池中下一个密钥（24 小时冷却）
  → 401 认证过期？
      → 尝试刷新令牌 (OAuth)
      → 刷新失败 → 轮换到池中下一个密钥
  → 成功 → 正常继续
```

## 快速开始

如果您已在 `.env` 中设置了 API 密钥，Hermes 会自动将其发现为单密钥池。要利用池化优势，请添加更多密钥：

```bash
# 添加第二个 OpenRouter 密钥
hermes auth add openrouter --api-key sk-or-v1-your-second-key

# 添加第二个 Anthropic 密钥
hermes auth add anthropic --type api-key --api-key sk-ant-api03-your-second-key

# 添加一个 Anthropic OAuth 凭证 (Claude Code 订阅)
hermes auth add anthropic --type oauth
# 打开浏览器进行 OAuth 登录
```

检查您的凭证池：

```bash
hermes auth list
```

输出：
```
openrouter (2 credentials):
  #1  OPENROUTER_API_KEY   api_key env:OPENROUTER_API_KEY ←
  #2  backup-key           api_key manual

anthropic (3 credentials):
  #1  hermes_pkce          oauth   hermes_pkce ←
  #2  claude_code          oauth   claude_code
  #3  ANTHROPIC_API_KEY    api_key env:ANTHROPIC_API_KEY
```

`←` 标记当前选定的凭证。

## 交互式管理

不带子命令运行 `hermes auth` 以启动交互式向导：

```bash
hermes auth
```

这将显示您的完整凭证池状态并提供菜单：

```
您想做什么？
  1. 添加凭证
  2. 移除凭证
  3. 重置提供商的冷却时间
  4. 设置提供商的轮换策略
  5. 退出
```

对于同时支持 API 密钥和 OAuth 的提供商（Anthropic、Nous、Codex），添加流程会询问类型：

```
anthropic 同时支持 API 密钥和 OAuth 登录。
  1. API 密钥（从提供商仪表板粘贴密钥）
  2. OAuth 登录（通过浏览器认证）
类型 [1/2]：
```

## CLI 命令

| 命令 | 描述 |
|---------|-------------|
| `hermes auth` | 交互式凭证池管理向导 |
| `hermes auth list` | 显示所有凭证池和凭证 |
| `hermes auth list <provider>` | 显示特定提供商的凭证池 |
| `hermes auth add <provider>` | 添加凭证（提示输入类型和密钥） |
| `hermes auth add <provider> --type api-key --api-key <key>` | 非交互式添加 API 密钥 |
| `hermes auth add <provider> --type oauth` | 通过浏览器登录添加 OAuth 凭证 |
| `hermes auth remove <provider> <index>` | 按 1 起始索引移除凭证 |
| `hermes auth reset <provider>` | 清除所有冷却/耗尽状态 |

## 轮换策略

通过 `hermes auth` → "设置轮换策略" 或在 `config.yaml` 中配置：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```

| 策略 | 行为 |
|----------|----------|
| `fill_first` (默认) | 使用第一个健康密钥直到耗尽，然后移动到下一个 |
| `round_robin` | 均匀循环使用密钥，每次选择后轮换 |
| `least_used` | 始终选择请求计数最低的密钥 |
| `random` | 在健康密钥中随机选择 |

## 错误恢复

凭证池以不同方式处理不同的错误：

| 错误 | 行为 | 冷却时间 |
|-------|----------|----------|
| **429 速率限制** | 重试同一密钥一次（瞬时）。连续第二次 429 则轮换到下一个密钥 | 1 小时 |
| **402 计费/配额** | 立即轮换到下一个密钥 | 24 小时 |
| **401 认证过期** | 首先尝试刷新 OAuth 令牌。仅当刷新失败时才轮换 | — |
| **所有密钥耗尽** | 如果配置了 `fallback_model`，则回退到该模型 | — |

`has_retried_429` 标志在每次成功的 API 调用后重置，因此单个瞬时 429 不会触发轮换。

## 自定义端点凭证池

自定义 OpenAI 兼容端点（Together.ai、RunPod、本地服务器）拥有自己的凭证池，以 `config.yaml` 中 `custom_providers` 的端点名称作为键。

当您通过 `hermes model` 设置自定义端点时，它会自动生成一个名称，如 "Together.ai" 或 "Local (localhost:8080)"。此名称成为凭证池的键。

```bash
# 通过 hermes model 设置自定义端点后：
hermes auth list
# 显示：
#   Together.ai (1 credential):
#     #1  config key    api_key config:Together.ai ←

# 为同一端点添加第二个密钥：
hermes auth add Together.ai --api-key sk-together-second-key
```

自定义端点凭证池存储在 `auth.json` 的 `credential_pool` 下，带有 `custom:` 前缀：

```json
{
  "credential_pool": {
    "openrouter": [...],
    "custom:together.ai": [...]
  }
}
```

## 自动发现

Hermes 自动从多个来源发现凭证，并在启动时填充凭证池：

| 来源 | 示例 | 自动填充？ |
|--------|---------|-------------|
| 环境变量 | `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` | 是 |
| OAuth 令牌 (auth.json) | Codex 设备代码, Nous 设备代码 | 是 |
| Claude Code 凭证 | `~/.claude/.credentials.json` | 是 (Anthropic) |
| Hermes PKCE OAuth | `~/.hermes/auth.json` | 是 (Anthropic) |
| 自定义端点配置 | `config.yaml` 中的 `model.api_key` | 是 (自定义端点) |
| 手动条目 | 通过 `hermes auth add` 添加 | 持久化在 auth.json 中 |

自动填充的条目在每次加载凭证池时更新——如果您移除了环境变量，其对应的池条目会自动被修剪。手动条目（通过 `hermes auth add` 添加）永远不会被自动修剪。

## 委派与子 Agent 共享

当 Agent 通过 `delegate_task` 生成子 Agent 时，父 Agent 的凭证池会自动与子 Agent 共享：

- **同一提供商** — 子 Agent 接收父 Agent 的完整凭证池，支持在速率限制时进行密钥轮换
- **不同提供商** — 子 Agent 加载该提供商自己的凭证池（如果已配置）
- **未配置凭证池** — 子 Agent 回退到继承的单个 API 密钥

这意味着子 Agent 无需额外配置即可享受与父 Agent 相同的速率限制恢复能力。按任务凭证租赁确保子 Agent 在并发轮换密钥时不会相互冲突。

## 线程安全

凭证池对所有状态变更（`select()`、`mark_exhausted_and_rotate()`、`try_refresh_current()`、`mark_used()`）使用线程锁。这确保了当消息网关同时处理多个聊天会话时，并发访问是安全的。

## 架构

有关完整的数据流图，请参阅仓库中的 [`docs/credential-pool-flow.excalidraw`](https://excalidraw.com/#json=2Ycqhqpi6f12E_3ITyiwh,c7u9jSt5BwrmiVzHGbm87g)。

凭证池集成在提供商解析层：

1. **`agent/credential_pool.py`** — 凭证池管理器：存储、选择、轮换、冷却
2. **`hermes_cli/auth_commands.py`** — CLI 命令和交互式向导
3. **`hermes_cli/runtime_provider.py`** — 支持凭证池的凭证解析
4. **`run_agent.py`** — 错误恢复：429/402/401 → 凭证池轮换 → 回退

## 存储

凭证池状态存储在 `~/.hermes/auth.json` 的 `credential_pool` 键下：

```json
{
  "version": 1,
  "credential_pool": {
    "openrouter": [
      {
        "id": "abc123",
        "label": "OPENROUTER_API_KEY",
        "auth_type": "api_key",
        "priority": 0,
        "source": "env:OPENROUTER_API_KEY",
        "access_token": "sk-or-v1-...",
        "last_status": "ok",
        "request_count": 142
      }
    ]
  },
}
```

策略存储在 `config.yaml` 中（而非 `auth.json`）：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```