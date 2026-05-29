---
title: Codex App-Server Runtime（可选）
sidebar_label: Codex App-Server Runtime
---

# Codex App-Server Runtime

Hermes 可以选择性地将 `openai/*` 和 `openai-codex/*` 轮次交给 [Codex CLI app-server](https://github.com/openai/codex) 处理，而不是运行其自身的工具循环。启用此功能后，终端命令、文件编辑、沙盒化和 MCP 工具调用都将在 Codex 的运行时内执行——Hermes 则成为其外围的 Shell（会话数据库、斜杠命令、消息网关、记忆和技能审查）。

这是**仅限手动选择加入**的。除非你切换标志，否则 Hermes 的默认行为保持不变。Hermes 永远不会自动将你路由到此运行时。

:::tip
不使用 OpenAI Codex？`hermes setup --portal` 可以一步配置一个非 Codex 后端，支持 Claude/Gemini 等。请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 为什么使用它

- 使用与 Codex CLI 相同的认证流程，针对你的 **ChatGPT 订阅**运行 OpenAI Agent 轮次（无需 API 密钥）。
- 使用 **Codex 自身的工具集和沙盒**——用于终端/读/写/搜索的 `shell`，用于结构化编辑的 `apply_patch`，用于规划的 `update_plan`，所有这些都在 seatbelt/landlock 沙盒中运行。
- **原生 Codex 插件**——Linear、GitHub、Gmail、Calendar、Canva 等——通过 `codex plugin` 安装的插件会自动迁移并在你的 Hermes 会话中激活。
- **Hermes 更丰富的工具随之而来**——web_search、web_extract、浏览器自动化、视觉、图像生成、技能和 TTS 通过 MCP 回调工作。Codex 会回调 Hermes 以使用其自身未内置的工具。
- **记忆和技能提示继续工作**——Codex 的事件被投影到 Hermes 的消息格式中，因此自我改进循环看到的是看起来正常的对话记录。

## 模型实际拥有的工具

这是大多数用户想提前了解的部分。当此运行时启用时，运行你轮次的模型拥有三个独立的工具来源：

### 1. Codex 的内置工具集（始终启用）

这些随 `codex app-server` 本身提供——无需 Hermes 参与，无需 MCP，无需插件。所有五个工具在运行时启动时即可用：

- **`shell`** —— 在沙盒内运行任意 shell 命令。这是模型读取文件（`cat`、`head`、`tail`）、写入文件（`echo > foo`、heredocs）、搜索文件（`find`、`rg`、`grep`）、导航目录（`ls`、`cd`）、运行构建、管理进程以及你在 bash 中执行的任何其他操作的方式。
- **`apply_patch`** —— 以 Codex 的补丁格式应用结构化的多文件差异。模型使用此工具进行重要的代码编辑（添加函数、跨文件重构）；shell heredocs 仍可用于一次性写入。
- **`update_plan`** —— Codex 内部的待办事项/计划跟踪器。相当于 Hermes 的 `todo` 工具，但完全在 Codex 的运行时内管理。
- **`view_image`** —— 将本地图像文件加载到对话中，以便模型可以查看。
- **`web_search`** —— 配置后，Codex 拥有其自身内置的网络搜索。Hermes 也通过下面的回调暴露了 `web_search`（基于 Firecrawl）；模型会选择它偏好的那个。

因此，**任何你通过终端执行的操作——读/写/搜索/查找/运行——Codex 都能原生处理**。沙盒配置文件（启用运行时默认为 `:workspace`）控制哪些内容可写。

### 2. 原生 Codex 插件（从你的 `codex plugin` 安装自动迁移）

当你启用运行时，Hermes 会查询 Codex 的 `plugin/list` RPC，并为每个已安装的插件写入一个 `[plugins."<name>@openai-curated"]` 条目。插件本身由 Codex 管理，并通过 Codex 自身的 UI 授权一次。

示例（OpenClaw 线程强调为“值得制作 YouTube 视频”的那些）：

- **Linear** —— 查找/更新问题
- **GitHub** —— 搜索代码、查看 PR、评论
- **Gmail** —— 读取/发送邮件
- **Google Calendar** —— 创建/查找事件
- **Outlook calendar/email** —— 通过 Microsoft 连接器实现相同功能
- **Canva** —— 设计生成
- ...以及你通过 `codex plugin marketplace add openai-curated` + `codex plugin install ...` 安装的任何其他插件

**不迁移的内容**：
- 你尚未安装的插件——先在 Codex 中安装它们。
- ChatGPT 应用市场条目（`app/list`）——这些已经通过你的账户认证在 Codex 内部启用。

### 3. Hermes 工具回调（MCP 服务器，在 `~/.codex/config.toml` 中注册）

Hermes 将自身注册为 MCP 服务器，以便 Codex 可以回调使用 Codex 未提供的工具。通过回调可用：

- **`web_search`** / **`web_extract`** —— 基于 Firecrawl；对于结构化内容，通常比网页抓取更清晰。
- **`browser_navigate` / `browser_click` / `browser_type` / `browser_press` / `browser_snapshot` / `browser_scroll` / `browser_back` / `browser_get_images` / `browser_console` / `browser_vision`** —— 通过 Camofox 或 Browserbase 实现完整的浏览器自动化。
- **`vision_analyze`** —— 调用单独的视觉模型来检查图像（与 Codex 的 `view_image` 不同，后者将图像加载到对话中）。
- **`image_generate`** —— 通过 Hermes 的 image_gen 插件链进行图像生成。
- **`skill_view` / `skills_list`** —— 从 Hermes 的技能库中读取。
- **`text_to_speech`** —— 通过 Hermes 配置的提供商进行 TTS。

当模型需要这些工具之一时，Codex 通过 stdio MCP 生成 `hermes_tools_mcp_server` 子进程，调用通过 `model_tools.handle_function_call()` 分发（与 Hermes 默认运行时的代码路径相同），结果像任何其他 MCP 响应一样返回给 Codex。

### 此运行时不可用的功能

这四个 Hermes 工具需要运行中的 AIAgent 上下文（循环中状态）来分发，而无状态的 MCP 回调无法驱动它们。当你需要其中任何一个时，请切换回默认运行时（`/codex-runtime auto`）：

- **`delegate_task`** —— 生成子 Agent
- **`memory`** —— Hermes 的持久化记忆存储
- **`session_search`** —— 跨会话搜索
- **`todo`** —— Hermes 的待办事项存储（Codex 的 `update_plan` 是运行时内的等效工具）

## 工作流功能（`/goal`、看板、定时任务）

### `/goal`（Ralph 循环）

**在此运行时上工作。** 目标以会话 ID 为键持久化在 `state_meta` 中，延续提示作为普通用户消息通过 `run_conversation()` 反馈，Codex 原生执行下一轮次。目标判断器通过辅助客户端运行（通过 config.yaml 中的 `auxiliary.goal_judge` 配置），与哪个运行时处于活动状态无关。如果 Codex 在审批上停滞，判断器的“受阻，需要用户输入”裁决是一个干净的退出方式。
**需要注意的一点：** 每个续写提示词都是一次全新的 Codex 轮次，这意味着 Codex 会从头重新评估命令批准策略。如果你正在执行一个包含大量写入操作的长期目标，预计会比在单个会话内任务中看到更多的批准提示。设置 `default_permissions = ":workspace"`（当你启用此运行时，Hermes 会自动执行此操作），这样简单的 workspace 写入操作就不需要提示。

### 看板（多 Agent 工作树调度）

**在此运行时上工作，有一个微妙的依赖。** 看板调度器将每个工作进程作为一个独立的 `hermes chat -q` 子进程启动，该子进程会读取用户的配置——这意味着如果全局设置了 `model.openai_runtime: codex_app_server`，工作进程也会在 Codex 运行时上启动。

在 Codex 运行时工作进程内部可用的功能：
- Codex 的完整工具集（shell、apply_patch、update_plan、view_image、web_search）——工作进程原生执行其实际任务工作。
- 已迁移的 Codex 插件——Linear、GitHub 等。
- 用于 browser_*、vision、image_gen、skills、TTS 的 Hermes 工具回调。

由于 MCP 回调暴露了它们，以下功能也可用：
- **`kanban_complete` / `kanban_block` / `kanban_comment` / `kanban_heartbeat`** —— 工作进程交接工具。这些工具从环境变量（由调度器设置）读取 `HERMES_KANBAN_TASK`，正确控制访问权限，并写入由 `HERMES_KANBAN_DB` 固定的每个看板的 SQLite 数据库。如果回调中没有这些工具，此运行时上的工作进程可以执行其任务但无法报告回来，直到调度器超时挂起。
- **`kanban_show` / `kanban_list`** —— 工作进程用于检查自身上下文的只读看板查询。
- **`kanban_create` / `kanban_unblock` / `kanban_link`** —— 仅限编排器的操作。适用于需要在 Codex 运行时上运行以分派新任务的编排器 Agent。

看板工具由调度器设置的 `HERMES_KANBAN_TASK` 环境变量控制——该变量会传播到 Codex 子进程（Codex 继承环境变量），并从那里传播到生成的 `hermes-tools` MCP 服务器子进程。因此，工具能看到正确的任务 ID 并正确控制访问。对于 Codex app-server 工作进程，当存在 `HERMES_KANBAN_TASK` 时，Hermes 还会传递狭窄的 app-server 沙盒覆盖：保持 `workspace-write` 沙盒，添加**看板数据库目录加上调度器固定的每个看板路径**作为额外的可写根目录（`HERMES_KANBAN_WORKSPACES_ROOT`、`HERMES_KANBAN_WORKSPACE`、旧的 `HERMES_KANBAN_ROOT`——去重后，数据库目录优先），并默认保持网络禁用。这避免了脆弱的 `:danger-no-sandbox` 变通方法，同时允许 `kanban_complete` / `kanban_block` 更新看板数据库**并且**允许工作进程在数据库目录外部的 workspace 挂载下写入报告/工件（例如，在单独驱动器上的 `/media/.../kanban-workspaces/...` —— [issue #27941](https://github.com/NousResearch/hermes-agent/issues/27941)）。

### 定时任务

**未专门测试。** 定时任务通过 `cronjob` → `AIAgent.run_conversation` 运行，与 CLI 的代码路径相同。如果定时任务的配置中有 `openai_runtime: codex_app_server`，它将在 Codex 上运行。相同的工具可用性规则适用——Codex 内置工具 + 插件 + MCP 回调有效，Agent 循环工具（delegate_task、memory、session_search、todo）无效。如果你的定时任务依赖这些工具，请将定时任务限定在使用默认运行时的配置文件中。

## 权衡

|  | Hermes 默认运行时 | Codex app-server（可选） |
|---|---|---|
| `delegate_task` 子 Agent | 是 | 不可用 —— 需要 Agent 循环上下文 |
| `memory`、`session_search`、`todo` | 是 | 不可用 —— 需要 Agent 循环上下文 |
| `web_search`、`web_extract` | 是 | 是（通过 MCP 回调） |
| 浏览器自动化（Camofox/Browserbase） | 是 | 是（通过 MCP 回调） |
| `vision_analyze`、`image_generate` | 是 | 是（通过 MCP 回调） |
| `skill_view`、`skills_list` | 是 | 是（通过 MCP 回调） |
| `text_to_speech` | 是 | 是（通过 MCP 回调） |
| Codex `shell`（终端/读/写/搜索/查找/运行） | — | 是（Codex 内置） |
| Codex `apply_patch`（结构化多文件编辑） | — | 是（Codex 内置） |
| Codex `update_plan`（运行时内待办事项） | — | 是（Codex 内置） |
| Codex `view_image`（将图像加载到会话中） | — | 是（Codex 内置） |
| Codex 沙盒（seatbelt/landlock，配置文件） | — | 是（Codex 内置） |
| ChatGPT 订阅认证 | — | 是（通过 `openai-codex` 提供商） |
| 原生 Codex 插件（Linear、GitHub 等） | — | 是（自动迁移） |
| 用户 MCP 服务器 | 是 | 是（自动迁移到 Codex） |
| 记忆 + 技能审查（后台） | 是 | 是（通过项目投影） |
| 多轮对话 | 是 | 是 |
| `/goal`（Ralph 循环） | 是 | 是 |
| 看板工作进程调度 | 是 | 是（通过回调） |
| 看板编排器工具 | 是 | 是（通过回调） |
| 所有消息网关平台 | 是 | 是 |
| 非 OpenAI 提供商 | 是 | 不适用 —— 仅限于 OpenAI/Codex |

## 先决条件

1. **已安装 Codex CLI：**
   ```bash
   npm i -g @openai/codex
   codex --version   # 0.130.0 或更新版本
   ```
2. **Codex OAuth 登录。** Codex 子进程读取 `~/.codex/auth.json`。有两种方式填充它：
   ```bash
   codex login                  # 将 Token 写入 ~/.codex/auth.json
   ```
   Hermes 自己的 `hermes auth login codex` 写入 `~/.hermes/auth.json` —— 那是单独的会话。**如果你还没有，请单独运行 `codex login`**。

3. **（可选）安装你想要的 Codex 插件。** 当你启用运行时，Hermes 会自动迁移你已通过 Codex CLI 安装的任何精选插件：
   ```bash
   codex plugin marketplace add openai-curated
   # 然后通过 Codex 的 TUI，安装 Linear / GitHub / Gmail / 等。
   ```
   Hermes 将发现它们并自动将 `[plugins."<name>@openai-curated"]` 条目写入 `~/.codex/config.toml`。

## 启用

在 Hermes 会话中：

```
/codex-runtime codex_app_server
```

该命令：
- 验证 `codex` CLI 是否已安装（如果未安装，会提示安装信息并阻止）。
- 将 `model.openai_runtime: codex_app_server` 持久化到你的 config.yaml。
- 将用户 MCP 服务器从 `~/.hermes/config.yaml` 迁移到 `~/.codex/config.toml`。
- **发现并迁移已安装的原生 Codex 插件**（Linear、GitHub、Gmail、Calendar、Canva 等），通过查询 Codex 的 `plugin/list` RPC。
- **将 Hermes 自身的工具注册为 MCP 服务器**，以便 Codex 子进程可以回调 Codex 未内置的工具。
- **写入 `default_permissions = ":workspace"`**，以便沙盒允许在 workspace 内写入，而无需为每个操作提示。
- 告诉你迁移了什么。在**下一个**会话生效——当前缓存的 Agent 保持先前的运行时，以便提示词缓存保持有效。
同义词：`/codex-runtime on`、`/codex-runtime off`、`/codex-runtime auto`。

在不改变任何设置的情况下检查当前状态：
```
/codex-runtime
```

你也可以在 `~/.hermes/config.yaml` 中手动设置：
```yaml
model:
  openai_runtime: codex_app_server   # 默认为 "auto" (= Hermes 运行时)
```

## 自我改进循环（记忆 + 技能提示）

Hermes 的后台自我改进会在计数器达到阈值时触发：

- 每 **10 条用户提示** → 一个分叉的审查 Agent 会查看对话，并决定是否应将任何内容保存到记忆。
- 在单个回合内每 **10 次工具迭代** → 同样的逻辑，但针对技能（`skill_manage` 写入）。

**两者都继续在 codex 运行时上工作。** codex 路径将每个已完成的 `commandExecution` / `fileChange` / `mcpToolCall` / `dynamicToolCall` 项投射为合成的 `assistant tool_call` + `tool` 结果消息，因此当审查运行时，它看到的是与默认 Hermes 运行时相同的结构。

连接保持等效的方式：

| | 默认运行时 | Codex 运行时 |
|---|---|---|
| `_turns_since_memory` 递增 | 每次用户提示，在 `run_conversation` 预循环中 | 相同的代码路径，在提前返回之前 |
| `_iters_since_skill` 递增 | 在聊天补全循环中每次工具迭代 | 在 codex 回合返回后，通过 `turn.tool_iterations` |
| 记忆触发 (`_turns_since_memory >= _memory_nudge_interval`) | 在预循环中计算，在响应后触发 | 在预循环中计算，传递给 codex 辅助函数 |
| 技能触发 (`_iters_since_skill >= _skill_nudge_interval`) | 在循环后计算 | 在 codex 回合后计算 |
| `_spawn_background_review(messages_snapshot=..., review_memory=..., review_skills=...)` | 任一触发器触发时调用 | 任一触发器触发时以相同方式调用 |

一个细节：审查分叉本身需要调用 Hermes 的 Agent 循环工具（`memory`、`skill_manage`），这需要 Hermes 自己的调度。因此，当父 Agent 在 `codex_app_server` 上时，审查分叉会被**降级到 `codex_responses`** —— 使用相同的 OAuth 凭证、相同的 `openai-codex` 提供商，但直接与 OpenAI 的 Responses API 通信，以便 Hermes 拥有循环且 Agent 循环工具可以工作。这对用户是不可见的。

最终效果：启用 codex 运行时，你的记忆和技能提示会像往常一样继续触发。

## 审批如何工作

Codex 在执行命令或应用补丁之前会请求批准。这些请求会被转换为 Hermes 标准的“危险命令”提示：

```
╭───────────────────────────────────────╮
│ 危险命令                              │
│                                       │
│ /bin/bash -lc 'echo hello > foo.txt'  │
│                                       │
│ ❯ 1. 允许一次                         │
│   2. 允许在此会话中                   │
│   3. 拒绝                             │
│                                       │
│ Codex 请求在 /your/cwd 中执行        │
╰───────────────────────────────────────╯
```

- **允许一次** → 批准此单条命令。
- **允许在此会话中** → Codex 不会为类似命令再次提示。
- **拒绝** → 命令被拒绝；Codex 继续以只读模式运行。

对于 `apply_patch`（文件编辑）审批，当 codex 通过相应的 `fileChange` 项提供数据时，Hermes 会显示更改摘要（`1 处新增，1 处更新：/tmp/new.py, /tmp/old.py`）。

## 权限配置文件

Codex 有三个内置的权限配置文件：
- `:read-only` — 禁止写入；每个 shell 命令都需要批准
- `:workspace` — 允许在当前工作空间内写入，无需提示（启用运行时后 Hermes 的默认设置）
- `:danger-no-sandbox` — 完全没有沙盒（除非你了解其含义，否则不要使用）

你可以在 Hermes 管理的块之外的 `~/.codex/config.toml` 中覆盖默认设置：

```toml
default_permissions = ":read-only"
```

（只要你的覆盖设置位于 `# managed by hermes-agent` 标记之外，Hermes 在重新迁移时会保留它。）

## 辅助任务和 ChatGPT 订阅 Token 成本

当此运行时与 `openai-codex` 提供商一起启用时，**辅助任务（标题生成、上下文压缩、视觉自动检测、后台自我改进审查分叉）默认也会通过你的 ChatGPT 订阅进行**，因为当没有为每个任务设置覆盖时，Hermes 的辅助客户端会使用主要的提供商/模型。

这并非 `codex_app_server` 特有 —— 现有的 `codex_responses` 路径也是如此 —— 但在这里更明显，因为你明确选择了订阅计费。

要将特定的辅助任务路由到更便宜/不同的模型，请在 `~/.hermes/config.yaml` 中设置显式覆盖：

```yaml
auxiliary:
  title_generation:
    provider: openrouter
    model: google/gemini-3-flash-preview
  context_compression:
    provider: openrouter
    model: google/gemini-3-flash-preview
  vision_detect:
    provider: openrouter
    model: google/gemini-3-flash-preview
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

自我改进审查分叉通过 `_current_main_runtime()` 继承主运行时，并且 Hermes 会自动将其从 `codex_app_server` 降级到 `codex_responses`（以便分叉可以实际调用 `memory` 和 `skill_manage` —— Hermes 自己的 Agent 循环工具）。除非你将辅助任务路由到其他地方，否则该分叉仍会使用你的订阅认证。

## 安全地编辑 `~/.codex/config.toml`

Hermes 将其管理的所有内容包装在两个标记注释之间：

```toml
# managed by hermes-agent — `hermes codex-runtime migrate` 重新生成此部分
default_permissions = ":workspace"
[mcp_servers.filesystem]
...
[plugins."github@openai-curated"]
...
# end hermes-agent managed section
```

**该块之外**的任何内容都属于你。重新运行迁移（通过 `/codex-runtime codex_app_server` 或每当切换运行时）会替换受管理的块，但会逐字保留其上下的用户内容。这意味着你可以：

- 添加 Hermes 不知道的自己的 MCP 服务器
- 如果你希望被提示，将 `default_permissions` 覆盖为 `:read-only`
- 配置仅限 codex 的选项（模型、提供商、otel 等）
- 在 `[permissions.<name>]` 表中添加用户定义的权限配置文件
在托管块内添加的任何内容都会在下一次迁移时被覆盖。如果你需要修改托管块，请提交 issue，我们会添加相应的配置项。

## 多配置文件/多租户设置

默认情况下，无论哪个 Hermes 配置文件处于活动状态，Hermes 都会将 codex 子进程指向 `~/.codex/`。这意味着 `hermes -p work` 和 `hermes -p personal` 共享相同的 Codex 认证、插件和配置。对于大多数用户来说，这是正确的行为——它与直接运行 `codex` CLI 的行为一致。

如果你希望每个配置文件都有独立的 Codex 隔离（独立的认证、独立的已安装插件、独立的配置），请为每个配置文件显式设置 `CODEX_HOME`。最简洁的方法是将其指向 `HERMES_HOME` 下的一个目录：

```bash
# 在工作配置文件中，你可以包装 hermes 命令：
CODEX_HOME=~/.hermes/profiles/work/codex hermes chat
```

你需要在使用该 `CODEX_HOME` 设置的情况下重新运行一次 `codex login`，以便 OAuth Token 存储在配置文件作用域的位置。之后，`hermes -p work` 将在隔离的 Codex 状态下运行。

我们没有自动设置此作用域，因为移动现有用户的 `~/.codex/` 会静默地使其 Codex CLI 认证失效——任何已经运行过 `codex login` 的用户都必须重新认证。选择加入比让用户感到意外更安全。

## HOME 环境变量透传

Hermes 在生成 codex app-server 子进程时**不会**重写 `HOME`（我们使用 `os.environ.copy()` 并且只覆盖 `CODEX_HOME` 和 `RUST_LOG`）。这意味着：

- Codex 通过其 `shell` 工具运行的命令可以看到真实的用户 `HOME`，并正确找到 `~/.gitconfig`、`~/.gh/`、`~/.aws/`、`~/.npmrc` 等。
- Codex 的内部状态通过 `CODEX_HOME` 保持隔离（默认指向 `~/.codex/`）。

这与 OpenClaw 经过早期实验后确定的边界一致：隔离 Codex 的状态，不干扰用户的主目录。（参见 openclaw/openclaw#81562。）

## MCP 服务器迁移

Hermes 的 `mcp_servers` 配置会自动转换为 Codex 期望的 TOML 格式。每次启用运行时都会运行迁移，并且是幂等的——重新运行会替换托管部分，但保留任何用户编辑的 Codex 配置。

转换的内容：

| Hermes (`config.yaml`) | Codex (`config.toml`) |
|---|---|
| `command` + `args` + `env` | stdio 传输 |
| `url` + `headers` | streamable_http 传输 |
| `timeout` | `tool_timeout_sec` |
| `connect_timeout` | `startup_timeout_sec` |
| `enabled: false` | `enabled = false` |

不迁移的内容：
- Hermes 特定的键，如 `sampling`（Codex 的 MCP 客户端没有等效项——这些会被丢弃，并针对每个服务器发出警告）。

## 原生 Codex 插件迁移

通过 `codex plugin` 安装的插件（Linear、GitHub、Gmail、Calendar、Canva 等）是通过 Codex 的 `plugin/list` RPC 发现的。对于每个 `installed: true` 的插件，Hermes 会写入一个 `[plugins."<name>@openai-curated"]` 块，在你的 Hermes 会话中启用它。

这意味着：当你的朋友说“我在我的 Codex CLI 中设置了 Calendar 和 GitHub”，并且他们启用了 Hermes 的 codex 运行时，Hermes 会自动激活这些插件。无需重新配置。

不迁移的内容：
- 你尚未安装的插件——先在 Codex 中安装它们。
- Codex 报告 `availability != AVAILABLE` 的插件（安装损坏、OAuth 过期、已从市场移除等）。这些会被跳过，以避免写入在激活时会失败的配置。
- ChatGPT 应用市场条目（每个账户的 `app/list` 结果——这些已经通过你的账户认证在 codex 内部启用）。
- 插件 OAuth——你在 Codex 本身中为每个插件授权一次；Hermes 不处理凭据。

## Hermes 工具回调（新的 MCP 服务器）

Codex 的内置工具集涵盖了 shell/文件操作/补丁，但没有网络搜索、浏览器自动化、视觉、图像生成等功能。为了在 codex 回合中保持这些功能可用，Hermes 在 `~/.codex/config.toml` 中将自己注册为一个 MCP 服务器：

```toml
[mcp_servers.hermes-tools]
command = "/path/to/python"
args = ["-m", "agent.transports.hermes_tools_mcp_server"]
env = { HERMES_HOME = "/your/.hermes", PYTHONPATH = "...", HERMES_QUIET = "1" }
startup_timeout_sec = 30.0
tool_timeout_sec = 600.0
```

当模型调用 `web_search`（或另一个暴露的 Hermes 工具）时，codex 通过 stdio 生成 `hermes_tools_mcp_server` 子进程，请求通过 `model_tools.handle_function_call()` 分发，结果像任何其他 MCP 响应一样投射回 codex。

**通过回调可用的工具：** `web_search`、`web_extract`、`browser_navigate`、`browser_click`、`browser_type`、`browser_press`、`browser_snapshot`、`browser_scroll`、`browser_back`、`browser_get_images`、`browser_console`、`browser_vision`、`vision_analyze`、`image_generate`、`skill_view`、`skills_list`、`text_to_speech`。

**不可用的工具：** `delegate_task`、`memory`、`session_search`、`todo`。这些需要运行中的 AIAgent 上下文来分发（循环中的状态），而无状态的 MCP 回调无法驱动它们。当你需要这些工具时，请使用默认的 Hermes 运行时（`/codex-runtime auto`）。

## 禁用

随时切换回来：

```
/codex-runtime auto
```

在下一个会话中生效。Codex 托管块保留在 `~/.codex/config.toml` 中，因此你以后可以重新启用而不会丢失配置——或者如果你愿意，可以手动删除它。

## 限制

此运行时是**选择加入的测试版**。在 Hermes Agent 2026.5 + Codex CLI 0.130.0 下工作正常：

- 多轮对话
- 通过 Hermes UI 进行 `commandExecution` 和 `fileChange` (apply_patch) 审批
- MCP 工具调用（已针对 `@modelcontextprotocol/server-filesystem` 和新的 `hermes-tools` 回调进行验证）
- 原生 Codex 插件迁移（已针对 Linear / GitHub / Calendar 清单进行验证）
- 拒绝/取消路径
- 切换开/关循环
- 记忆和技能提示计数器（通过集成测试实时验证）
- 通过 codex 进行 Hermes web_search（实时验证：“OpenAI Codex CLI – Getting Started” 端到端返回）

已知限制：

- **Hermes 认证和 codex 认证是独立的会话。** 为了获得最简洁的用户体验，你需要同时进行 `codex login` 和 `hermes auth login codex`（运行时使用 codex 的会话进行 LLM 调用）。这是 Hermes 的 `_import_codex_cli_tokens` 中的一个有意设计选择——Hermes 不会与 codex CLI 共享 OAuth 状态，以避免在 Token 刷新时相互覆盖。
- **`delegate_task`、`memory`、`session_search`、`todo` 在此运行时不可用。** 它们需要运行中的 AIAgent 上下文，而无状态的 MCP 回调无法提供。当你需要这些工具时，请使用 `/codex-runtime auto`。
- **当 codex 不跟踪变更集时，审批提示中没有内联补丁预览。** Codex 的 `fileChange` 审批参数并不总是携带变更集。Hermes 在可能的情况下会缓存来自相应 `item/started` 通知的数据，但如果审批在项目流式传输之前到达，提示将回退到 codex 提供的任何 `reason`。
- **无法保证亚秒级取消。** 流式传输中的中断（当 codex 正在响应时按 Ctrl+C）通过 `turn/interrupt` 发送，但如果 codex 已经刷新了最终消息，你仍然会得到响应。
如果发现 bug，请[提交 issue](https://github.com/NousResearch/hermes-agent/issues)，并附上 `hermes logs --since 5m` 的输出。在标题中提及 `codex-runtime` 以便于分类处理。

## 架构

```
                ┌─── Hermes shell (CLI / TUI / gateway) ───┐
                │  sessions DB · slash commands · memory   │
                │  & skill review · cron · session pickers │
                └──┬──────────────────────────────────────┬┘
                   │ user_message               final     │
                   ▼                            text +    │
        ┌──────────────────────────────────┐   projected  │
        │  AIAgent.run_conversation()       │   messages   │
        │   if api_mode == codex_app_server │              │
        │     → CodexAppServerSession       │              │
        │   else: chat_completions / codex_responses (default)
        └────┬─────────────────────────────┘              │
             │ JSON-RPC over stdio                        │
             ▼                                            │
        ┌──────────────────────────────────┐              │
        │  codex app-server (subprocess)    │──────────────┘
        │   thread/start, turn/start        │
        │   item/* notifications            │
        │   shell + apply_patch + update_plan│
        │   view_image + sandbox            │
        │   ┌─────────────────────────┐     │
        │   │  MCP client             │     │
        │   │  ├─ user MCP servers    │     │
        │   │  ├─ native plugins      │     │
        │   │  │   (linear, github,   │     │
        │   │  │    gmail, calendar,  │     │
        │   │  │    canva, ...)       │     │
        │   │  └─ hermes-tools ───────┼─────────────────┐
        │   │       (callback to     │     │           │
        │   │        Hermes' richer  │     │           │
        │   │        tools)          │     │           │
        │   └─────────────────────────┘     │           │
        └──────────────────────────────────┘           │
                                                        │
                                                        ▼
        ┌──────────────────────────────────────────────────────────┐
        │  hermes_tools_mcp_server.py (subprocess on demand)        │
        │   web_search, web_extract, browser_*, vision_analyze,    │
        │   image_generate, skill_view, skills_list, text_to_speech│
        └──────────────────────────────────────────────────────────┘
```

有关实现细节，请参阅 [PR #24182](https://github.com/NousResearch/hermes-agent/pull/24182) 和 [Codex app-server 协议 README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)。