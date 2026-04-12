---
title: 提供商路由
description: 配置 OpenRouter 提供商偏好，以优化成本、速度或质量。
sidebar_label: 提供商路由
sidebar_position: 7
---

# 提供商路由

当使用 [OpenRouter](https://openrouter.ai) 作为你的 LLM 提供商时，Hermes Agent 支持**提供商路由**——对哪些底层 AI 提供商处理你的请求以及它们的优先级进行细粒度控制。

OpenRouter 将请求路由到许多提供商（例如，Anthropic、Google、AWS Bedrock、Together AI）。提供商路由允许你针对成本、速度、质量进行优化，或强制执行特定的提供商要求。

## 配置

在你的 `~/.hermes/config.yaml` 中添加一个 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "price"           # 如何对提供商进行排序
  only: []                # 白名单：仅使用这些提供商
  ignore: []              # 黑名单：永不使用这些提供商
  order: []               # 明确的提供商优先级顺序
  require_parameters: false  # 仅使用支持所有参数的提供商
  data_collection: null   # 控制数据收集（"allow" 或 "deny"）
```

:::info
提供商路由仅在通过 OpenRouter 使用时生效。对于直接提供商连接（例如，直接连接到 Anthropic API）没有影响。
:::

## 选项

### `sort`

控制 OpenRouter 如何为你的请求对可用提供商进行排序。

| 值 | 描述 |
|-------|-------------|
| `"price"` | 最便宜的提供商优先 |
| `"throughput"` | 每秒 Token 数最快的优先 |
| `"latency"` | 首 Token 时间最低的优先 |

```yaml
provider_routing:
  sort: "price"
```

### `only`

提供商名称的白名单。设置后，**仅**使用这些提供商。所有其他提供商将被排除。

```yaml
provider_routing:
  only:
    - "Anthropic"
    - "Google"
```

### `ignore`

提供商名称的黑名单。这些提供商将**永不**被使用，即使它们提供最便宜或最快的选项。

```yaml
provider_routing:
  ignore:
    - "Together"
    - "DeepInfra"
```

### `order`

明确的优先级顺序。首先列出的提供商是首选。未列出的提供商将作为后备使用。

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
    - "AWS Bedrock"
```

### `require_parameters`

当为 `true` 时，OpenRouter 将仅路由到支持你请求中**所有**参数（如 `temperature`、`top_p`、`tools` 等）的提供商。这可以避免参数被静默丢弃。

```yaml
provider_routing:
  require_parameters: true
```

### `data_collection`

控制提供商是否可以使用你的提示词进行训练。选项是 `"allow"` 或 `"deny"`。

```yaml
provider_routing:
  data_collection: "deny"
```

## 实用示例

### 优化成本

路由到最便宜的可用提供商。适用于高使用量和开发场景：

```yaml
provider_routing:
  sort: "price"
```

### 优化速度

为交互式使用优先选择低延迟的提供商：

```yaml
provider_routing:
  sort: "latency"
```

### 优化吞吐量

最适合每秒 Token 数很重要的长文本生成：

```yaml
provider_routing:
  sort: "throughput"
```

### 锁定特定提供商

确保所有请求都通过特定提供商以获得一致性：

```yaml
provider_routing:
  only:
    - "Anthropic"
```

### 避免特定提供商

排除你不想使用的提供商（例如，出于数据隐私考虑）：

```yaml
provider_routing:
  ignore:
    - "Together"
    - "Lepton"
  data_collection: "deny"
```

### 首选顺序与后备

首先尝试你首选的提供商，如果不可用则回退到其他提供商：

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
  require_parameters: true
```

## 工作原理

提供商路由偏好通过每个 API 调用中的 `extra_body.provider` 字段传递给 OpenRouter API。这适用于：

- **CLI 模式** —— 在 `~/.hermes/config.yaml` 中配置，启动时加载
- **消息网关模式** —— 相同的配置文件，在网关启动时加载

路由配置从 `config.yaml` 中读取，并在创建 `AIAgent` 时作为参数传递：

```
providers_allowed  ← 来自 provider_routing.only
providers_ignored  ← 来自 provider_routing.ignore
providers_order    ← 来自 provider_routing.order
provider_sort      ← 来自 provider_routing.sort
provider_require_parameters ← 来自 provider_routing.require_parameters
provider_data_collection    ← 来自 provider_routing.data_collection
```

:::tip
你可以组合多个选项。例如，按价格排序，但排除某些提供商并要求参数支持：

```yaml
provider_routing:
  sort: "price"
  ignore: ["Together"]
  require_parameters: true
  data_collection: "deny"
```
:::

## 默认行为

当没有配置 `provider_routing` 部分时（默认情况），OpenRouter 使用其自身的默认路由逻辑，该逻辑通常会自动平衡成本和可用性。

:::tip 提供商路由 vs. 后备模型
提供商路由控制 OpenRouter 内的**子提供商**处理你的请求。关于当你的主要模型失败时自动故障转移到完全不同的提供商，请参阅[后备提供商](/docs/user-guide/features/fallback-providers)。
:::