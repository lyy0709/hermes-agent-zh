---
sidebar_position: 99
title: "Honcho 记忆"
description: "通过 Honcho 实现 AI 原生持久化记忆 —— 辩证推理、多 Agent 用户建模和深度个性化"
---

# Honcho 记忆

[Honcho](https://github.com/plastic-labs/honcho) 是一个 AI 原生的记忆后端，它在 Hermes 内置的记忆系统之上增加了辩证推理和深度用户建模功能。与简单的键值存储不同，Honcho 通过在对话发生后进行推理，维护一个关于用户是谁的持续模型 —— 包括他们的偏好、沟通风格、目标和行为模式。

:::info Honcho 是一个记忆提供商插件
Honcho 已集成到[记忆提供商](./memory-providers.md)系统中。以下所有功能均可通过统一的记忆提供商接口使用。
:::

## Honcho 带来的增强

| 能力 | 内置记忆 | Honcho |
|-----------|----------------|--------|
| 跨会话持久化 | ✔ 基于文件的 MEMORY.md/USER.md | ✔ 服务器端，带 API |
| 用户画像 | ✔ 手动 Agent 整理 | ✔ 自动辩证推理 |
| 多 Agent 隔离 | — | ✔ 按对等方（peer）进行画像分离 |
| 观察模式 | — | ✔ 统一或定向观察 |
| 结论（推导出的洞察） | — | ✔ 服务器端对模式进行推理 |
| 跨历史记录搜索 | ✔ FTS5 会话搜索 | ✔ 对结论进行语义搜索 |

**辩证推理**：每次对话后，Honcho 会分析交流内容并推导出“结论”——关于用户偏好、习惯和目标的洞察。这些结论随时间累积，使 Agent 获得超越用户明确陈述的、不断加深的理解。

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
echo "HONCHO_API_KEY=your-key" >> ~/.hermes/.env
```

在 [honcho.dev](https://honcho.dev) 获取 API 密钥。

## 配置选项

```yaml
# ~/.hermes/config.yaml
honcho:
  observation: directional    # "unified"（新安装的默认值）或 "directional"
  peer_name: ""               # 从平台自动检测，或手动设置
```

**观察模式：**
- `unified` —— 所有观察进入一个统一的池。更简单，适用于单 Agent 设置。
- `directional` —— 观察被标记方向（用户→Agent，Agent→用户）。支持对对话动态进行更丰富的分析。

## 工具

当 Honcho 作为记忆提供商处于活动状态时，会提供四个额外的工具：

| 工具 | 用途 |
|------|---------|
| `honcho_conclude` | 对最近的对话触发服务器端辩证推理 |
| `honcho_context` | 从 Honcho 的记忆中检索与当前对话相关的上下文 |
| `honcho_profile` | 查看或更新用户的 Honcho 画像 |
| `honcho_search` | 对所有存储的结论和观察进行语义搜索 |

## CLI 命令

```bash
hermes honcho status          # 显示连接状态和配置
hermes honcho peer            # 为多 Agent 设置更新对等方名称
```

## 从 `hermes honcho` 迁移

如果您之前使用过独立的 `hermes honcho setup`：

1. 您现有的配置（`honcho.json` 或 `~/.honcho/config.json`）将被保留
2. 您的服务器端数据（记忆、结论、用户画像）保持不变
3. 在 config.yaml 中设置 `memory.provider: honcho` 以重新激活

无需重新登录或重新设置。运行 `hermes memory setup` 并选择 "honcho" —— 向导会检测到您现有的配置。

## 完整文档

完整参考请参阅[记忆提供商 —— Honcho](./memory-providers.md#honcho)。