---
sidebar_position: 3
---

# 配置模型

Hermes 使用两种模型槽位：

- **主模型** — Agent 用于思考的模型。每条用户消息、每次工具调用循环、每个流式响应都通过此模型处理。
- **辅助模型** — Agent 卸载的较小副任务。包括上下文压缩、视觉（图像分析）、网页摘要、会话搜索、批准评分、MCP 工具路由、会话标题生成和技能搜索。每个任务都有自己的槽位，可以独立覆盖。

本页介绍如何通过仪表板配置这两类模型。如果您更喜欢配置文件或 CLI，请直接跳到底部的[替代方法](#替代方法)。

## 模型页面

打开仪表板，点击侧边栏的 **Models**。您会看到两个部分：

1. **模型设置** — 顶部面板，用于为槽位分配模型。
2. **使用情况分析** — 显示在选定时间段内运行过会话的每个模型的排名卡片，包含 Token 数量、成本和能力徽章。

![模型页面概览](/img/docs/dashboard-models/overview.png)

顶部卡片是 **模型设置** 面板。主行始终显示 Agent 将为新会话启动的模型。点击 **Change** 打开选择器。

## 设置主模型

点击主模型行上的 **Change**：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器有两列：

- **左侧** — 已认证的提供商。只有您已设置（设置了 API 密钥、完成 OAuth 或定义为自定义端点）的提供商才会显示在此处。如果缺少某个提供商，请前往 **Keys** 添加其凭据。
- **右侧** — 所选提供商的精选模型列表。这些是 Hermes 为该提供商推荐的代理式模型，而不是原始的 `/models` 转储（在 OpenRouter 上包含 400 多个模型，包括 TTS、图像生成器和重排器）。

在筛选框中输入内容，可按提供商名称、slug 或模型 ID 进行筛选。

选择一个模型，点击 **Switch**，Hermes 会将其写入 `~/.hermes/config.yaml` 的 `model` 部分。**这仅适用于新会话** — 您已打开的任何聊天标签页将继续使用其启动时所用的模型。要热切换当前聊天，请在其内部使用 `/model` 斜杠命令。

## 设置辅助模型

点击 **Show auxiliary** 以显示八个任务槽位：

![辅助面板展开](/img/docs/dashboard-models/auxiliary-expanded.png)

每个辅助任务默认为 `auto` — 这意味着 Hermes 也使用您的主模型来处理该任务。当您希望为副任务使用更便宜或更快的模型时，可以覆盖特定任务。

### 常见的覆盖模式

| 任务 | 何时覆盖 |
|---|---|
| **标题生成** | 几乎总是。一个 $0.10/M 的快速模型可以像 Opus 一样编写会话标题。默认配置在 OpenRouter 上将其设置为 `google/gemini-3-flash-preview`。 |
| **视觉** | 当您的主模型是没有视觉功能的编码模型时（例如 Kimi、DeepSeek）。将其指向 `google/gemini-2.5-flash` 或 `gpt-4o-mini`。 |
| **压缩** | 当您为了总结上下文而在 Opus/M2.7 上消耗推理 Token 时。一个快速的聊天模型能以 1/50 的成本完成这项工作。 |
| **会话搜索** | 当召回查询扇出时 — 默认的 max_concurrency 是 3。一个便宜的模型可以保持账单可预测。 |
| **批准** | 对于 `approval_mode: smart` — 一个快速/便宜的模型（haiku、flash、gpt-5-mini）决定是否自动批准低风险命令。在此处使用昂贵的模型是浪费。 |
| **网页提取** | 当您大量使用 `web_extract` 时。与压缩相同的逻辑 — 摘要不需要推理。 |
| **技能中心** | `hermes skills search` 使用此模型。通常保持 `auto` 即可。 |
| **MCP** | MCP 工具路由。通常保持 `auto` 即可。 |

### 按任务覆盖

点击任何辅助行上的 **Change**。会打开相同的选择器，行为相同 — 选择提供商 + 模型，点击 Switch。该行将更新为显示 `provider · model` 而不是 `auto (use main model)`。

### 全部重置为自动

如果您过度调整并希望重新开始，请点击辅助部分顶部的 **Reset all to auto**。每个槽位都将恢复使用您的主模型。

## "Use as" 快捷方式

页面上的每个模型卡片都有一个 **Use as** 下拉菜单。这是快速路径 — 选择一个您在分析中看到的模型，点击 **Use as**，然后一键将其分配给主槽位或任何特定的辅助任务：

![Use as 下拉菜单](/img/docs/dashboard-models/use-as-dropdown.png)

下拉菜单包含：

- **主模型** — 与点击主行上的 Change 相同。
- **所有辅助任务** — 将此模型一次性分配给所有 8 个辅助槽位。当您只想让所有副任务都使用一个便宜的快速模型时很有用。
- **单个任务选项** — 视觉、网页提取、压缩等。每个任务当前分配的模型会标记为 `current`。

当卡片当前被分配给某个任务时，会带有 `main` 或 `aux · <task>` 徽章 — 这样您一眼就能看出您历史模型中的哪些模型被用在了哪里。

## 什么会被写入 `config.yaml`

当您通过仪表板保存时，Hermes 会写入 `~/.hermes/config.yaml`：

**主模型：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4.7
  base_url: ''        # 切换提供商时清空
  api_mode: chat_completions
```

**辅助覆盖（示例 — 视觉使用 gemini-flash）：**
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash
    base_url: ''
    api_key: ''
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

**辅助为自动（默认）：**
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
    base_url: ''
    # ... 其他字段不变
```

`provider: auto` 和 `model: ''` 告诉 Hermes 对该任务使用主模型。

## 何时生效？

- **CLI** (`hermes chat`)：下一次 `hermes chat` 调用。
- **消息网关** (Telegram、Discord、Slack 等)：下一个*新*会话。现有会话保持其模型。如果您想强制所有会话获取更改，请重启消息网关 (`hermes gateway restart`)。
- **仪表板聊天标签页** (`/chat`)：下一个新的 PTY。当前打开的聊天保持其模型 — 在其内部使用 `/model` 进行热切换。

更改永远不会使运行中会话的提示词缓存失效。这是故意的：在会话内部交换主模型需要重置缓存（系统提示词包含模型特定的内容），我们将其保留给聊天内部的显式 `/model` 斜杠命令。

## 故障排除

### 选择器中显示 "No authenticated providers"

Hermes 仅在有有效凭据时才列出提供商。检查侧边栏的 **Keys** — 您应该看到以下之一：API 密钥、成功的 OAuth 或自定义端点 URL。如果您想要的提供商不在那里，请运行 `hermes setup` 来设置它，或转到 **Keys** 并添加环境变量。

### 我运行的聊天中主模型没有改变

这是预期的。仪表板写入 `config.yaml`，新会话会读取它。当前打开的聊天是一个实时的 Agent 进程 — 它保持其启动时所用的模型。在聊天内部使用 `/model <name>` 来热切换该特定会话。

### 辅助覆盖 "没有生效"

检查三件事：

1. **您是否启动了新会话？** 现有聊天不会重新读取配置。
2. **`provider` 是否设置为 `auto` 以外的值？** 如果该字段显示 `auto`，则该任务仍在使用您的主模型。点击 **Change** 并选择一个真实的提供商。
3. **提供商是否已认证？** 如果您将 `minimax` 分配给一个任务但没有 MiniMax API 密钥，则该任务将回退到 openrouter 默认值，并在 `agent.log` 中记录警告。

### 我选择了一个模型，但 Hermes 切换了提供商

在 OpenRouter（或任何聚合器）上，裸模型名称首先在聚合器*内部*解析。因此，OpenRouter 上的 `claude-sonnet-4` 会变成 `anthropic/claude-sonnet-4.6`，保持您的 OpenRouter 认证。但如果您在原生 Anthropic 认证上输入 `claude-sonnet-4`，它将保持为 `claude-sonnet-4-6`。如果您看到意外的提供商切换，请检查您当前的提供商是否符合预期 — 选择器始终在对话框顶部显示当前的主模型。

## 替代方法

### CLI 斜杠命令

在任何 `hermes chat` 会话内部：

```
/model gpt-5.4 --provider openrouter             # 仅限会话
/model gpt-5.4 --provider openrouter --global    # 同时持久化到 config.yaml
```

`--global` 执行与仪表板 **Change** 按钮相同的操作，此外还会原地切换正在运行的会话。

### 自定义别名

为您经常使用的模型定义自己的短名称，然后在 CLI 或任何消息平台中使用 `/model <alias>`：

```yaml
# ~/.hermes/config.yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
```

或从 shell（短格式，`provider/model`）：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

然后在聊天中使用 `/model fav` 或 `/model grok`。用户别名会覆盖内置的短名称（`sonnet`、`kimi`、`opus` 等）。完整参考请参见[自定义模型别名](/docs/reference/slash-commands#custom-model-aliases)。

### `hermes model` 子命令

```bash
hermes model list                   # 列出已认证的提供商 + 模型
hermes model set anthropic/claude-opus-4.7 --provider openrouter
```

### 直接编辑配置

编辑 `~/.hermes/config.yaml` 并重启读取它的任何组件。完整模式请参见[配置参考](./configuration.md)。

### REST API

仪表板使用三个端点。对脚本编写很有用：

```bash
# 列出已认证的提供商 + 精选模型列表
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/options

# 读取当前主模型 + 辅助模型分配
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/auxiliary

# 设置主模型
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"main","provider":"openrouter","model":"anthropic/claude-opus-4.7"}' \
  http://localhost:PORT/api/model/set

# 覆盖单个辅助任务
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"vision","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# 将一个模型分配给所有辅助任务
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# 将所有辅助任务重置为自动
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"__reset__","provider":"","model":""}' \
  http://localhost:PORT/api/model/set
```

会话 Token 在启动时注入到仪表板 HTML 中，并在每次服务器重启时轮换。如果您正在针对正在运行的仪表板编写脚本，请从浏览器开发者工具 (`window.__HERMES_SESSION_TOKEN__`) 中获取它。