---
sidebar_position: 3
---

# 配置模型

Hermes 使用两种模型槽位：

- **主模型** — Agent 用于思考的模型。每条用户消息、每次工具调用循环、每个流式响应都通过此模型处理。
- **辅助模型** — Agent 卸载的较小辅助任务。上下文压缩、视觉（图像分析）、网页摘要、审批评分、MCP 工具路由、会话标题生成和技能搜索。每个任务都有自己的槽位，可以独立覆盖。

本页介绍如何从仪表板配置这两种模型。如果您更喜欢配置文件或 CLI，请跳至底部的[替代方法](#alternative-methods)。

:::tip 最快路径：Nous Portal
[Nous Portal](/user-guide/features/tool-gateway) 在一个订阅下提供 300 多个模型。在新安装后，运行 `hermes setup --portal` 以登录并一键将 Nous 设置为您的提供商。使用 `hermes portal info` 检查已连接的内容。

- Portal 订阅者还可享受**按 Token 计费提供商 10% 的折扣**。
:::

:::note `model:` 模式 — 空字符串 vs. 映射
在全新安装时，捆绑的默认配置包含 `model: ""`（一个空字符串标记，表示“尚未配置”）。首次运行 `hermes setup` 或 `hermes model` 时，该键会就地升级为包含 `provider`、`default`、`base_url` 和 `api_mode` 子键的映射 — 即本页及 [`profiles.md`](./profiles.md) / [`configuration.md`](./configuration.md) 中展示的结构。如果您在 `config.yaml` 中看到空字符串，请运行 `hermes model`（或在仪表板中点击 **Change**），Hermes 将为您写入字典形式。
:::

## 模型页面

打开仪表板，点击侧边栏中的 **Models**。您将看到两个部分：

1. **Model Settings** — 顶部面板，用于为槽位分配模型。
2. **Usage analytics** — 排名卡片，显示所选时间段内运行过会话的每个模型，包含 Token 数量、成本和能力徽章。

![模型页面概览](/img/docs/dashboard-models/overview.png)

顶部卡片是 **Model Settings** 面板。主行始终显示 Agent 将为新会话启动的模型。点击 **Change** 打开选择器。

## 设置主模型

在主模型行点击 **Change**：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器有两列：

- **左侧** — 已认证的提供商。仅显示您已设置（API 密钥已设置、OAuth 授权或定义为自定义端点）的提供商。如果缺少某个提供商，请前往 **Keys** 添加其凭据。
- **右侧** — 所选提供商的精选模型列表。这些是 Hermes 为该提供商推荐的代理式模型，而非原始的 `/models` 转储（在 OpenRouter 上包含 400 多个模型，包括 TTS、图像生成器和重排器）。

在筛选框中输入内容，按提供商名称、slug 或模型 ID 进行筛选。

选择一个模型，点击 **Switch**，Hermes 会将其写入 `~/.hermes/config.yaml` 的 `model` 部分。**这仅适用于新会话** — 您已打开的任何聊天标签页将继续使用其启动时的模型。要在当前聊天中热切换，请使用其中的 `/model` 斜杠命令。

## 设置辅助模型

点击 **Show auxiliary** 以显示 11 个任务槽位：

![辅助面板展开](/img/docs/dashboard-models/auxiliary-expanded.png)

每个辅助任务默认为 `auto` — 意味着 Hermes 也使用您的主模型来处理该任务。当您希望为辅助任务使用更便宜或更快的模型时，可以覆盖特定任务。

### 常见覆盖模式

| 任务 | 何时覆盖 |
|---|---|
| **Title Gen** | 几乎总是。一个 $0.10/M 的快速模型编写会话标题的效果与 Opus 一样好。默认配置在 OpenRouter 上将其设置为 `google/gemini-3-flash-preview`。 |
| **Vision** | 当您的主模型缺乏视觉支持时。将其指向 `google/gemini-2.5-flash` 或 `gpt-4o-mini`。 |
| **Compression** | 当您使用 Opus/M2.7 等推理模型仅用于总结上下文时。一个快速的聊天模型能以 1/50 的成本完成工作。 |
| **Approval** | 对于 `approval_mode: smart` — 一个快速/便宜的模型（haiku、flash、gpt-5-mini）决定是否自动批准低风险命令。在此使用昂贵模型是浪费。 |
| **Web Extract** | 当您大量使用 `web_extract` 时。与压缩相同的逻辑 — 摘要不需要推理。 |
| **Skills Hub** | `hermes skills search` 使用此模型。通常保持 `auto` 即可。 |
| **MCP** | MCP 工具路由。通常保持 `auto` 即可。 |
| **Triage Specifier** | 路由看板分类指定器（`hermes kanban specify`），将粗略的单行描述扩展为具体规范。一个便宜且能力强的模型效果很好。 |
| **Kanban Decomposer** | 路由看板任务分解 — 将分类任务拆分为专家配置文件的子任务图。 |
| **Profile Describer** | 路由配置文件描述生成（`hermes profile describe --auto` / 仪表板自动生成按钮）。简短、廉价的调用。 |
| **Curator** | 路由策展人技能使用审查过程。在推理模型上可能运行数分钟，因此使用更便宜的辅助模型通常值得。 |

### 按任务覆盖

在任何辅助行点击 **Change**。打开相同的选择器，行为相同 — 选择提供商 + 模型，点击 Switch。该行将更新显示 `provider · model` 而不是 `auto (use main model)`。

### 全部重置为 auto

如果您过度调整并希望重新开始，请点击辅助部分顶部的 **Reset all to auto**。每个槽位将恢复使用您的主模型。

## “Use as” 快捷方式

页面上的每个模型卡片都有一个 **Use as** 下拉菜单。这是快速路径 — 选择您在分析中看到的模型，点击 **Use as**，然后一键将其分配给主槽位或任何特定的辅助任务：

![Use as 下拉菜单](/img/docs/dashboard-models/use-as-dropdown.png)

下拉菜单包含：

- **Main model** — 与在主行点击 Change 相同。
- **All auxiliary tasks** — 将此模型一次性分配给所有 11 个辅助槽位。当您希望所有辅助任务都使用便宜的快速模型时很有用。
- **Individual task options** — Vision、Web Extract、Compression 等。每个任务当前分配的模型会标记为 `current`。
当卡片当前被分配给某个任务时，会标记为 `main` 或 `aux · <任务>` —— 这样你就能一眼看出你历史记录中的哪些模型被用在了哪里。

## 哪些内容会写入 `config.yaml`

当你通过仪表板保存时，Hermes 会写入 `~/.hermes/config.yaml`：

**主模型：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4.7
  base_url: ''        # 切换提供商时清空
  api_mode: chat_completions
```

**辅助任务覆盖（示例 —— 视觉任务使用 gemini-flash）：**
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

**辅助任务设为自动（默认）：**
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
    base_url: ''
    # ... 其他字段保持不变
```

`provider: auto` 和 `model: ''` 告诉 Hermes 对该任务使用主模型。

## 何时生效？

- **CLI** (`hermes chat`)：下一次调用 `hermes chat` 时。
- **消息网关** (Telegram, Discord, Slack 等)：下一次*新*会话。现有会话保持其模型。如果你想强制所有会话都应用更改，请重启消息网关 (`hermes gateway restart`)。
- **仪表板聊天标签页** (`/chat`)：下一次新建 PTY。当前打开的聊天保持其模型 —— 使用其内部的 `/model` 命令进行热切换。

更改永远不会使运行中会话的提示词缓存失效。这是有意为之：在会话内切换主模型需要重置缓存（系统提示词包含模型特定的内容），我们将其保留给聊天中显式的 `/model` 斜杠命令。

## 故障排除

### 选择器中显示“没有已验证的提供商”

Hermes 只会在拥有有效凭据时列出提供商。检查侧边栏的 **Keys** —— 你应该看到其中之一：一个 API 密钥、一次成功的 OAuth 授权，或一个自定义端点 URL。如果你想要的提供商不在那里，请运行 `hermes setup` 来配置它，或者转到 **Keys** 并添加环境变量。

### 我运行的聊天中主模型没有改变

这是预期的。仪表板写入 `config.yaml`，新会话会读取它。当前打开的聊天是一个活跃的 Agent 进程 —— 它保持其启动时使用的模型。在聊天内部使用 `/model <名称>` 来热切换该特定会话。

### 辅助任务覆盖“没有生效”

需要检查三件事：

1.  **你是否启动了新会话？** 现有聊天不会重新读取配置。
2.  **`provider` 是否设置为 `auto` 以外的值？** 如果该字段显示 `auto`，则该任务仍在使用你的主模型。点击 **Change** 并选择一个真实的提供商。
3.  **提供商是否已验证？** 如果你将 `minimax` 分配给一个任务但没有 MiniMax API 密钥，则该任务会回退到 openrouter 默认值，并在 `agent.log` 中记录一条警告。

### 我选择了一个模型，但 Hermes 切换了提供商

在 OpenRouter（或任何聚合器）上，裸模型名称会*在*聚合器内部首先解析。因此，OpenRouter 上的 `claude-sonnet-4` 会变成 `anthropic/claude-sonnet-4.6`，并保持你的 OpenRouter 认证。但如果你在原生 Anthropic 认证下输入 `claude-sonnet-4`，它将保持为 `claude-sonnet-4-6`。如果你看到意外的提供商切换，请检查你当前的提供商是否符合预期 —— 选择器总是在对话框顶部显示当前的主模型。

## 替代方法

### CLI 斜杠命令

在任何 `hermes chat` 会话内部：

```
/model gpt-5.4 --provider openrouter             # 仅限当前会话
/model gpt-5.4 --provider openrouter --global    # 同时持久化到 config.yaml
```

`--global` 执行与仪表板 **Change** 按钮相同的操作，此外它还会就地切换正在运行的会话。

### 自定义别名

为你经常使用的模型定义你自己的短名称，然后在 CLI 或任何消息平台中使用 `/model <别名>`。有两种等效的格式 —— 选择适合你工作流程的即可。

**规范格式（顶层 `model_aliases:`）** —— 完全控制 provider + base_url：

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

**短字符串格式（`model.aliases.<name>: provider/model`）** —— 在 shell 中很方便，因为 `hermes config set` 只写入标量值，但它不能携带自定义的 `base_url`：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

两种路径都提供给同一个加载器 (`hermes_cli/model_switch.py`)。在 `model_aliases:` 中声明的条目优先于同名的 `model.aliases:` 条目。

然后在聊天中使用 `/model fav` 或 `/model grok`。用户别名会覆盖内置的短名称 (`sonnet`, `kimi`, `opus` 等)。完整参考请参阅[自定义模型别名](/reference/slash-commands#custom-model-aliases)。

### `hermes model` 子命令

```bash
hermes model            # 交互式提供商 + 模型选择器（切换默认值的规范方式）
```

`hermes model` 会引导你选择提供商、进行身份验证（OAuth 流程会打开浏览器；API 密钥提供商会提示输入密钥），然后从该提供商的精选目录中选择特定模型。选择结果会写入 `~/.hermes/config.yaml` 中的 `model.provider` 和 `model.model`。

要列出提供商/模型而不启动选择器，请使用仪表板或下面的 REST 端点。要检查 CLI 当前实际将使用什么：`hermes config show | grep '^model\.'` 和 `hermes status`。

### 直接编辑配置

编辑 `~/.hermes/config.yaml` 并重启读取它的任何组件。完整模式请参阅[配置参考](./configuration.md)。

### REST API

仪表板使用三个端点。对脚本编写很有用：

```bash
# 列出已验证的提供商 + 精选模型列表
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/options

# 读取当前主模型 + 辅助任务分配
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
会话 Token 在启动时注入到仪表盘 HTML 中，并在每次服务器重启时轮换。如果你正在针对运行中的仪表盘编写脚本，可以从浏览器开发者工具中获取它（`window.__HERMES_SESSION_TOKEN__`）。