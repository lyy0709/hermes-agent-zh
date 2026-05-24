---
sidebar_position: 10
title: "模型提供商插件"
description: "如何为 Hermes Agent 构建模型提供商（推理后端）插件"
---

# 构建模型提供商插件

模型提供商插件声明一个推理后端 —— 一个 OpenAI 兼容的端点、一个 Anthropic Messages 服务器、一个 Codex 风格的 Responses API，或者一个原生的 Bedrock 接口 —— Hermes 可以通过它路由 `AIAgent` 调用。每个内置的提供商（OpenRouter、Anthropic、GMI、DeepSeek、Nvidia……）都作为这些插件之一提供。第三方可以通过在 `$HERMES_HOME/plugins/model-providers/` 下放置一个目录来添加自己的插件，无需对仓库进行任何更改。

:::tip
模型提供商插件是第三种**提供商插件**。其他两种是[记忆提供商插件](/docs/developer-guide/memory-provider-plugin)（跨会话知识）和[上下文引擎插件](/docs/developer-guide/context-engine-plugin)（上下文压缩策略）。这三种都遵循相同的“放置目录、声明配置文件、无需仓库编辑”的模式。
:::

## 发现机制如何工作

`providers/__init__.py._discover_providers()` 在首次有任何代码调用 `get_provider_profile()` 或 `list_providers()` 时惰性运行。发现顺序：

1.  **捆绑插件** — `<repo>/plugins/model-providers/<name>/` — 随 Hermes 一起发布
2.  **用户插件** — `$HERMES_HOME/plugins/model-providers/<name>/` — 放置在任何目录；后续会话无需重启
3.  **遗留单文件** — `<repo>/providers/<name>.py` — 用于树外可编辑安装的向后兼容

**同名用户插件会覆盖捆绑插件**，因为 `register_provider()` 遵循后写优先原则。放置一个 `$HERMES_HOME/plugins/model-providers/gmi/` 目录即可在不接触仓库的情况下替换内置的 GMI 配置文件。

## 目录结构

```
plugins/model-providers/my-provider/
├── __init__.py       # 在模块级别调用 register_provider(profile)
├── plugin.yaml       # kind: model-provider + 元数据（可选但推荐）
└── README.md         # 设置说明（可选）
```

唯一必需的文件是 `__init__.py`。`plugin.yaml` 被 `hermes plugins` 用于内省，并被通用的 PluginManager 用于将插件路由到正确的加载器；如果没有它，通用加载器会回退到源文本启发式方法。

## 最小示例 —— 一个简单的 API 密钥提供商

```python
# plugins/model-providers/acme-inference/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

acme = ProviderProfile(
    name="acme-inference",
    aliases=("acme",),
    display_name="Acme Inference",
    description="Acme — OpenAI-compatible direct API",
    signup_url="https://acme.example.com/keys",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=(
        "acme-large-v3",
        "acme-medium-v3",
        "acme-small-fast",
    ),
)

register_provider(acme)
```

```yaml
# plugins/model-providers/acme-inference/plugin.yaml
name: acme-inference
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
author: Your Name
```

就是这样。放置这两个文件后，以下内容将**自动连接**，无需其他编辑：

| 集成点 | 位置 | 获取的内容 |
|---|---|---|
| 凭据解析 | `hermes_cli/auth.py` | `PROVIDER_REGISTRY["acme-inference"]` 从配置文件填充 |
| `--provider` CLI 标志 | `hermes_cli/main.py` | 接受 `acme-inference` |
| `hermes model` 选择器 | `hermes_cli/models.py` | 出现在 `CANONICAL_PROVIDERS` 中，模型列表从 `{base_url}/models` 获取 |
| `hermes doctor` | `hermes_cli/doctor.py` | 对 `ACME_API_KEY` 的健康检查 + `{base_url}/models` 探测 |
| `hermes setup` | `hermes_cli/config.py` | `ACME_API_KEY` 出现在 `OPTIONAL_ENV_VARS` 和设置向导中 |
| URL 反向映射 | `agent/model_metadata.py` | 主机名 → 提供商名称，用于自动检测 |
| 辅助模型 | `agent/auxiliary_client.py` | 使用 `default_aux_model` 进行压缩/摘要 |
| 运行时解析 | `hermes_cli/runtime_provider.py` | 返回正确的 `base_url`、`api_key`、`api_mode` |
| 传输层 | `agent/transports/chat_completions.py` | 配置文件路径通过 `prepare_messages` / `build_extra_body` / `build_api_kwargs_extras` 生成 kwargs |

## ProviderProfile 字段

完整定义在 `providers/base.py` 中。最有用的字段：

| 字段 | 类型 | 用途 |
|---|---|---|
| `name` | str | 规范 ID —— 匹配 `config.yaml` 中的 `model.provider` 和 `--provider` 标志 |
| `aliases` | `tuple[str, ...]` | `get_provider_profile()` 解析的替代名称（例如 `grok` → `xai`） |
| `api_mode` | str | `chat_completions` \| `codex_responses` \| `anthropic_messages` \| `bedrock_converse` |
| `display_name` | str | 在 `hermes model` 选择器中显示的人类可读标签 |
| `description` | str | 选择器副标题 |
| `signup_url` | str | 首次运行设置时显示（“在此获取 API 密钥”） |
| `env_vars` | `tuple[str, ...]` | API 密钥环境变量，按优先级顺序；最后一个 `*_BASE_URL` 条目用作用户基础 URL 覆盖 |
| `base_url` | str | 默认推理端点 |
| `models_url` | str | 显式目录 URL（回退到 `{base_url}/models`） |
| `auth_type` | str | `api_key` \| `oauth_device_code` \| `oauth_external` \| `copilot` \| `aws_sdk` \| `external_process` |
| `fallback_models` | `tuple[str, ...]` | 当实时目录获取失败时显示的精选列表 |
| `default_headers` | `dict[str, str]` | 每个请求都发送（例如 Copilot 的 `Editor-Version`） |
| `fixed_temperature` | Any | `None` = 使用调用者的值；`OMIT_TEMPERATURE` 标记 = 完全不发送 temperature（Kimi） |
| `default_max_tokens` | `int \| None` | 提供商级别的 max_tokens 上限（Nvidia: 16384） |
| `default_aux_model` | str | 用于辅助任务（压缩、视觉、摘要）的廉价模型 |

## 可覆盖的钩子

对于非平凡的怪癖，可以子类化 `ProviderProfile`：

```python
from typing import Any
from providers.base import ProviderProfile

class AcmeProfile(ProviderProfile):
    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """提供商特定的消息预处理。在 codex 清理之后、开发者角色交换之前运行。默认：透传。"""
        # 示例：Qwen 将纯文本内容规范化为 parts 列表数组并注入 cache_control；Kimi 重写工具调用 JSON
        return messages

    def build_extra_body(self, *, session_id=None, **context) -> dict:
        """提供商特定的 extra_body 字段，合并到 API 调用中。
        上下文包括：session_id, provider_preferences, model, base_url,
        reasoning_config。默认：空字典。"""
        # 示例：OpenRouter 的 provider-preferences 块，
        # Gemini 的 thinking_config 转换。
        return {}

    def build_api_kwargs_extras(self, *, reasoning_config=None, **context):
        """返回 (extra_body_additions, top_level_kwargs)。当某些字段需要放在顶层（Kimi 的 reasoning_effort）而某些需要放在 extra_body 中（OpenRouter 的 reasoning 字典）时需要。默认：({}, {})."""
        return {}, {}

    def fetch_models(self, *, api_key=None, timeout=8.0) -> list[str] | None:
        """实时目录获取。默认使用 Bearer 认证访问 {models_url or base_url}/models。
        覆盖用于：自定义认证（Anthropic）、无 REST 端点（Bedrock → None）或公共/未认证目录（OpenRouter）。"""
        return super().fetch_models(api_key=api_key, timeout=timeout)
```
## 钩子参考示例

查看这些内置插件以了解惯用法：

| 插件 | 查看原因 |
|---|---|
| `plugins/model-providers/openrouter/` | 带有提供商偏好的聚合器，公共模型目录 |
| `plugins/model-providers/gemini/` | `thinking_config` 转换（原生 + OpenAI 兼容嵌套形式） |
| `plugins/model-providers/kimi-coding/` | `OMIT_TEMPERATURE`、`extra_body.thinking`、顶层 `reasoning_effort` |
| `plugins/model-providers/qwen-oauth/` | 消息规范化、`cache_control` 注入、VL 高分辨率 |
| `plugins/model-providers/nous/` | 归属标签、"禁用时省略推理" |
| `plugins/model-providers/custom/` | Ollama `num_ctx` + `think: false` 特殊处理 |
| `plugins/model-providers/bedrock/` | `api_mode="bedrock_converse"`、`fetch_models` 返回 None（无 REST 端点） |

## 用户覆盖 — 无需编辑仓库即可替换内置插件

假设你想将 `gmi` 指向你的私有测试端点进行测试。创建 `~/.hermes/plugins/model-providers/gmi/__init__.py`：

```python
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="gmi",
    aliases=("gmi-cloud", "gmicloud"),
    env_vars=("GMI_API_KEY",),
    base_url="https://gmi-staging.internal.example.com/v1",
    auth_type="api_key",
    default_aux_model="google/gemini-3.1-flash-lite-preview",
))
```

下次会话时，`get_provider_profile("gmi").base_url` 将返回测试 URL。无需仓库补丁，无需重新构建。因为用户插件在内置插件之后被发现，用户的 `register_provider()` 调用会胜出。

## api_mode 选择

识别四种值。Hermes 基于以下条件选择：

1. 用户显式覆盖（当设置时，`config.yaml` 中的 `model.api_mode`）
2. OpenCode 的按模型分发（Zen 和 Go 的 `opencode_model_api_mode`）
3. URL 自动检测 — `/anthropic` 后缀 → `anthropic_messages`、`api.openai.com` → `codex_responses`、`api.x.ai` → `codex_responses`、Kimi 域名上的 `/coding` → `chat_completions`
4. **Profile `api_mode`** 作为 URL 检测无结果时的后备方案
5. 默认 `chat_completions`

将 `profile.api_mode` 设置为匹配你的提供商默认提供的模式 — 它作为一个提示。用户 URL 覆盖仍然优先。

## 认证类型

| `auth_type` | 含义 | 使用者 |
|---|---|---|
| `api_key` | 单个环境变量携带静态 API 密钥 | 大多数提供商 |
| `oauth_device_code` | 设备码 OAuth 流程 | — |
| `oauth_external` | 用户在其他地方登录，Token 落地到 `auth.json` | Anthropic OAuth、MiniMax OAuth、Gemini Cloud Code、Qwen Portal、Nous Portal |
| `copilot` | GitHub Copilot Token 刷新周期 | 仅 `copilot` 插件 |
| `aws_sdk` | AWS SDK 凭证链（IAM 角色、配置文件、环境变量） | 仅 `bedrock` 插件 |
| `external_process` | 认证由 Agent 生成的子进程处理 | 仅 `copilot-acp` 插件 |

`auth_type` 控制哪些代码路径将你的提供商视为"简单 API 密钥提供商" — 如果不是 `api_key`，PluginManager 仍会记录清单，但 Hermes 的 CLI 级自动化（doctor 检查、`--provider` 标志、设置向导委派）可能会跳过它。

## 发现时机

提供商发现是**惰性**的 — 由进程中的第一次 `get_provider_profile()` 或 `list_providers()` 调用触发。实际上，这在启动时很早发生（`auth.py` 模块加载会急切地扩展 `PROVIDER_REGISTRY`）。如果你需要验证你的插件已加载，运行：

```bash
hermes doctor
```

— 一个成功的 `auth_type="api_key"` 配置文件将出现在 Provider Connectivity 部分，并带有 `/models` 探测。

对于编程式检查：

```python
from providers import list_providers
for p in list_providers():
    print(p.name, p.base_url, p.api_mode)
```

## 测试你的插件

将 `HERMES_HOME` 指向一个临时目录，以免污染你的真实配置：

```bash
export HERMES_HOME=/tmp/hermes-plugin-test
mkdir -p $HERMES_HOME/plugins/model-providers/my-provider
cat > $HERMES_HOME/plugins/model-providers/my-provider/__init__.py <<'EOF'
from providers import register_provider
from providers.base import ProviderProfile
register_provider(ProviderProfile(
    name="my-provider",
    env_vars=("MY_API_KEY",),
    base_url="https://api.my-provider.example.com/v1",
    auth_type="api_key",
))
EOF

export MY_API_KEY=your-test-key
hermes -z "hello" --provider my-provider -m some-model
```

## 通用 PluginManager 集成

通用的 `PluginManager`（`hermes plugins` 操作的对象）**能看到**模型提供商插件但不会导入它们 — `providers/__init__.py` 拥有它们的生命周期。管理器记录清单以供内省，并按 `kind: model-provider` 分类。当你将一个未标记的用户插件放入 `$HERMES_HOME/plugins/` 中，而它恰好使用 `ProviderProfile` 调用了 `register_provider` 时，管理器会通过源代码启发式方法自动将其强制转换为 `kind: model-provider` — 因此即使没有 `plugin.yaml`，插件仍能正确路由。

## 通过 pip 分发

与任何 Hermes 插件一样，模型提供商可以作为 pip 包分发。在你的 `pyproject.toml` 中添加一个入口点：

```toml
[project.entry-points."hermes.plugins"]
acme-inference = "acme_hermes_plugin:register"
```

…其中 `acme_hermes_plugin:register` 是一个调用 `register_provider(profile)` 的函数。通用 PluginManager 在 `discover_and_load()` 期间拾取入口点插件。对于 `kind: model-provider` 的 pip 插件，你仍然需要在清单中声明 kind（或依赖源代码启发式方法）。

完整入口点设置请参阅[构建 Hermes 插件](/docs/guides/build-a-hermes-plugin#distribute-via-pip)。

## 相关页面

- [提供商运行时](/docs/developer-guide/provider-runtime) — 解析优先级 + 每层读取配置文件的位置
- [添加提供商](/docs/developer-guide/adding-providers) — 新推理后端端到端清单（涵盖快速插件路径和完整 CLI/认证集成）
- [记忆提供商插件](/docs/developer-guide/memory-provider-plugin)
- [上下文引擎插件](/docs/developer-guide/context-engine-plugin)
- [构建 Hermes 插件](/docs/guides/build-a-hermes-plugin) — 通用插件编写