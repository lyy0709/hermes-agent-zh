---
sidebar_position: 5
title: "添加提供商"
description: "如何向 Hermes Agent 添加新的推理提供商 — 认证、运行时解析、CLI 流程、适配器、测试和文档"
---

# 添加提供商

Hermes 已经可以通过自定义提供商路径与任何 OpenAI 兼容的端点通信。除非你希望为该服务提供一流的用户体验，否则不要添加内置提供商：

- 提供商特定的认证或 Token 刷新
- 精选的模型目录
- 设置向导 / `hermes model` 菜单条目
- 用于 `provider:model` 语法的提供商别名
- 需要适配器的非 OpenAI API 格式

如果该提供商只是“另一个 OpenAI 兼容的基础 URL 和 API 密钥”，那么一个命名的自定义提供商可能就足够了。

## 心智模型

一个内置提供商需要在多个层级上保持一致：

1. `hermes_cli/auth.py` 决定如何查找凭据。
2. `hermes_cli/runtime_provider.py` 将其转换为运行时数据：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 使用 `api_mode` 来决定如何构建和发送请求。
4. `hermes_cli/models.py` 和 `hermes_cli/main.py` 使提供商出现在 CLI 中。（`hermes_cli/setup.py` 会自动委托给 `main.py` — 那里不需要更改。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 确保辅助任务和 Token 预算正常工作。

重要的抽象是 `api_mode`。

- 大多数提供商使用 `chat_completions`。
- Codex 使用 `codex_responses`。
- Anthropic 使用 `anthropic_messages`。
- 一个新的非 OpenAI 协议通常意味着添加一个新的适配器和一个新的 `api_mode` 分支。

## 首先选择实现路径

### 路径 A — OpenAI 兼容的提供商

当提供商接受标准聊天补全风格请求时使用此路径。

典型工作：

- 添加认证元数据
- 添加模型目录 / 别名
- 添加运行时解析
- 添加 CLI 菜单连接
- 添加辅助模型默认值
- 添加测试和用户文档

通常不需要新的适配器或新的 `api_mode`。

### 路径 B — 原生提供商

当提供商的行为不像 OpenAI 聊天补全时使用此路径。

当前代码库中的示例：

- `codex_responses`
- `anthropic_messages`

此路径包括路径 A 的所有内容，外加：

- `agent/` 中的提供商适配器
- `run_agent.py` 中用于请求构建、分发、用量提取、中断处理和响应规范化的分支
- 适配器测试

## 文件清单

### 每个内置提供商都需要

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试
8. `website/docs/` 下的面向用户的文档

:::tip
`hermes_cli/setup.py` **不需要**更改。设置向导将提供商/模型选择委托给 `main.py` 中的 `select_provider_and_model()` — 任何在那里添加的提供商都会自动在 `hermes setup` 中可用。
:::

### 原生 / 非 OpenAI 提供商额外需要

10. `agent/<provider>_adapter.py`
11. `run_agent.py`
12. `pyproject.toml`（如果需要提供商 SDK）

## 步骤 1：选择一个规范的提供商 ID

选择一个单一的提供商 ID 并在各处使用。

代码库中的示例：

- `openai-codex`
- `kimi-coding`
- `minimax-cn`

相同的 ID 应出现在：

- `hermes_cli/auth.py` 中的 `PROVIDER_REGISTRY`
- `hermes_cli/models.py` 中的 `_PROVIDER_LABELS`
- `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中的 `_PROVIDER_ALIASES`
- `hermes_cli/main.py` 中的 CLI `--provider` 选项
- 设置向导 / 模型选择分支
- 辅助模型默认值
- 测试

如果这些文件中的 ID 不一致，提供商将感觉像是半连接的：认证可能工作，但 `/model`、设置向导或运行时解析会静默地忽略它。

## 步骤 2：在 `hermes_cli/auth.py` 中添加认证元数据

对于 API 密钥提供商，向 `PROVIDER_REGISTRY` 添加一个 `ProviderConfig` 条目，包含：

- `id`
- `name`
- `auth_type="api_key"`
- `inference_base_url`
- `api_key_env_vars`
- 可选的 `base_url_env_var`

同时向 `_PROVIDER_ALIASES` 添加别名。

使用现有的提供商作为模板：

- 简单的 API 密钥路径：Z.AI, MiniMax
- 带端点检测的 API 密钥路径：Kimi, Z.AI
- 原生 Token 解析：Anthropic
- OAuth / 认证存储路径：Nous, OpenAI Codex

这里需要回答的问题：

- Hermes 应该检查哪些环境变量，优先级顺序是什么？
- 提供商是否需要基础 URL 覆盖？
- 它需要端点探测或 Token 刷新吗？
- 当凭据缺失时，认证错误应该显示什么？

如果提供商需要的不仅仅是“查找一个 API 密钥”，请添加一个专用的凭据解析器，而不是将逻辑塞进不相关的分支。

## 步骤 3：在 `hermes_cli/models.py` 中添加模型目录和别名

更新提供商目录，使提供商在菜单和 `provider:model` 语法中工作。

典型的编辑：

- `_PROVIDER_MODELS`
- `_PROVIDER_LABELS`
- `_PROVIDER_ALIASES`
- `list_available_providers()` 内的提供商显示顺序
- `provider_model_ids()`（如果提供商支持实时 `/models` 获取）

如果提供商暴露实时模型列表，优先使用该列表，并将 `_PROVIDER_MODELS` 作为静态回退。

这个文件也使得以下输入能够工作：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果这里缺少别名，提供商可能认证正确，但在 `/model` 解析中仍然失败。

## 步骤 4：在 `hermes_cli/runtime_provider.py` 中解析运行时数据

`resolve_runtime_provider()` 是 CLI、消息网关、定时任务、ACP 和辅助客户端使用的共享路径。

添加一个分支，返回至少包含以下内容的字典：

```python
{
    "provider": "your-provider",
    "api_mode": "chat_completions",  # 或你的原生模式
    "base_url": "https://...",
    "api_key": "...",
    "source": "env|portal|auth-store|explicit",
    "requested_provider": requested_provider,
}
```

如果提供商是 OpenAI 兼容的，`api_mode` 通常应保持为 `chat_completions`。

注意 API 密钥的优先级。Hermes 已经包含逻辑来避免将 OpenRouter 密钥泄露给不相关的端点。新的提供商应该同样明确地说明哪个密钥用于哪个基础 URL。
## 步骤 5：在 `hermes_cli/main.py` 中连接 CLI

一个提供商在交互式 `hermes model` 流程中出现之前是不可发现的。

在 `hermes_cli/main.py` 中更新以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 中的 `providers` 列表
- 提供商分发逻辑（`if selected_provider == ...`）
- `--provider` 参数的可选值
- 如果提供商支持登录/登出流程，则更新相应的选项
- 一个 `_model_flow_<provider>()` 函数，如果适用也可以复用 `_model_flow_api_key_provider()`

:::tip
`hermes_cli/setup.py` 不需要更改 — 它调用 `main.py` 中的 `select_provider_and_model()`，因此你的新提供商会自动出现在 `hermes model` 和 `hermes setup` 中。
:::

## 步骤 6：确保辅助调用正常工作

这里有两个文件很重要：

### `agent/auxiliary_client.py`

如果这是一个直接的 API 密钥提供商，请将一个廉价/快速的默认辅助模型添加到 `_API_KEY_PROVIDER_AUX_MODELS` 中。

辅助任务包括：

- 视觉摘要
- 网页提取摘要
- 上下文压缩摘要
- 会话搜索摘要
- 记忆刷新

如果提供商没有合适的辅助默认模型，辅助任务可能会回退失败，或者意外地使用昂贵的主模型。

### `agent/model_metadata.py`

添加提供商模型的上下文长度，以便 Token 预算、压缩阈值和限制保持合理。

## 步骤 7：如果提供商是原生提供商，添加适配器和 `run_agent.py` 支持

如果提供商不是普通的聊天补全服务，请将提供商特定的逻辑隔离在 `agent/<provider>_adapter.py` 中。

保持 `run_agent.py` 专注于编排。它应该调用适配器辅助函数，而不是在整个文件中内联手动构建提供商负载。

原生提供商通常需要在以下位置进行工作：

### 新的适配器文件

典型职责：

- 构建 SDK / HTTP 客户端
- 解析 Token
- 将 OpenAI 风格的对话消息转换为提供商的请求格式
- 如果需要，转换工具模式
- 将提供商响应规范化回 `run_agent.py` 期望的格式
- 提取使用情况和完成原因数据

### `run_agent.py`

搜索 `api_mode` 并审核每个切换点。至少验证：

- `__init__` 选择了新的 `api_mode`
- 客户端构建适用于该提供商
- `_build_api_kwargs()` 知道如何格式化请求
- `_api_call_with_interrupt()` 分发到正确的客户端调用
- 中断 / 客户端重建路径正常工作
- 响应验证接受提供商的格式
- 完成原因提取正确
- Token 使用情况提取正确
- 回退模型激活可以干净地切换到新提供商
- 摘要生成和记忆刷新路径仍然有效

同时搜索 `run_agent.py` 中的 `self.client.`。任何假设标准 OpenAI 客户端存在的代码路径，在原生提供商使用不同的客户端对象或 `self.client = None` 时都可能中断。

### 提示词缓存和提供商特定的请求字段

提示词缓存和提供商特定的配置项很容易出现回归。

代码库中已有的示例：

- Anthropic 有一个原生的提示词缓存路径
- OpenRouter 获取提供商路由字段
- 并非每个提供商都应该接收每个请求端选项

当你添加原生提供商时，请仔细检查 Hermes 是否只发送该提供商实际理解的字段。

## 步骤 8：测试

至少，要修改保护提供商连接的测试。

常见位置：

- `tests/test_runtime_provider_resolution.py`
- `tests/test_cli_provider_resolution.py`
- `tests/test_cli_model_command.py`
- `tests/test_setup_model_selection.py`
- `tests/test_provider_parity.py`
- `tests/test_run_agent.py`
- 对于原生提供商，还有 `tests/test_<provider>_adapter.py`

对于仅文档的示例，确切的文件集可能有所不同。重点是覆盖：

- 身份验证解析
- CLI 菜单 / 提供商选择
- 运行时提供商解析
- Agent 执行路径
- 提供商:模型解析
- 任何适配器特定的消息转换

运行测试时禁用 xdist：

```bash
source venv/bin/activate
python -m pytest tests/test_runtime_provider_resolution.py tests/test_cli_provider_resolution.py tests/test_cli_model_command.py tests/test_setup_model_selection.py -n0 -q
```

对于更深入的更改，在推送前运行完整的测试套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

## 步骤 9：实时验证

测试之后，运行一个真实的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果你更改了菜单，也测试交互式流程：

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生提供商，至少验证一个工具调用，而不仅仅是纯文本响应。

## 步骤 10：更新面向用户的文档

如果提供商打算作为一等选项发布，也请更新用户文档：

- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

开发者可以完美地连接提供商，但仍然可能让用户无法发现所需的环境变量或设置流程。

## OpenAI 兼容提供商清单

如果提供商是标准的聊天补全服务，请使用此清单。

- [ ] 在 `hermes_cli/auth.py` 中添加了 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加了别名
- [ ] 在 `hermes_cli/models.py` 中添加了模型目录
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加了运行时分支
- [ ] 在 `hermes_cli/main.py` 中添加了 CLI 连接（setup.py 自动继承）
- [ ] 在 `agent/auxiliary_client.py` 中添加了辅助模型
- [ ] 在 `agent/model_metadata.py` 中添加了上下文长度
- [ ] 更新了运行时 / CLI 测试
- [ ] 更新了用户文档

## 原生提供商清单

当提供商需要新的协议路径时使用此清单。

- [ ] OpenAI 兼容清单中的所有内容
- [ ] 在 `agent/<provider>_adapter.py` 中添加了适配器
- [ ] 在 `run_agent.py` 中支持新的 `api_mode`
- [ ] 中断 / 重建路径正常工作
- [ ] 使用情况和完成原因提取正常工作
- [ ] 回退路径正常工作
- [ ] 添加了适配器测试
- [ ] 实时冒烟测试通过
## 常见陷阱

### 1. 将提供商添加到认证但未添加到模型解析

这会导致凭据解析正确，但 `/model` 和 `provider:model` 输入失败。

### 2. 忘记 `config["model"]` 可以是字符串或字典

许多提供商选择代码必须对这两种形式进行规范化处理。

### 3. 假设必须使用内置提供商

如果服务只是 OpenAI 兼容的，自定义提供商可能已经以更少的维护成本解决了用户的问题。

### 4. 忘记辅助路径

主聊天路径可能正常工作，而摘要、记忆刷新或视觉助手失败，因为辅助路由从未更新。

### 5. 隐藏在 `run_agent.py` 中的原生提供商分支

搜索 `api_mode` 和 `self.client.`。不要假设显而易见的请求路径是唯一的。

### 6. 将仅适用于 OpenRouter 的配置项发送给其他提供商

像提供商路由这样的字段只属于支持它们的提供商。

### 7. 更新了 `hermes model` 但没有更新 `hermes setup`

两个流程都需要了解该提供商。

## 实现时的良好搜索目标

如果你在寻找提供商涉及的所有地方，请搜索这些符号：

- `PROVIDER_REGISTRY`
- `_PROVIDER_ALIASES`
- `_PROVIDER_MODELS`
- `resolve_runtime_provider`
- `_model_flow_`
- `select_provider_and_model`
- `api_mode`
- `_API_KEY_PROVIDER_AUX_MODELS`
- `self.client.`

## 相关文档

- [提供商运行时解析](./provider-runtime.md)
- [架构](./architecture.md)
- [贡献指南](./contributing.md)