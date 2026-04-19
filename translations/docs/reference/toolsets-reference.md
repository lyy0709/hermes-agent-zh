---
sidebar_position: 4
title: "工具集参考"
description: "Hermes 核心、复合、平台和动态工具集的参考文档"
---

# 工具集参考

工具集是命名的工具捆绑包，用于控制 Agent 可以执行的操作。它们是按平台、按会话或按任务配置工具可用性的主要机制。

## 工具集工作原理

每个工具都属于且仅属于一个工具集。启用一个工具集时，该捆绑包中的所有工具都将对 Agent 可用。工具集分为三种类型：

- **核心** — 单个逻辑上相关的工具组（例如，`file` 捆绑了 `read_file`、`write_file`、`patch`、`search_files`）
- **复合** — 为常见场景组合多个核心工具集（例如，`debugging` 捆绑了文件、终端和网络工具）
- **平台** — 针对特定部署上下文的完整工具配置（例如，`hermes-cli` 是交互式 CLI 会话的默认配置）

## 配置工具集

### 按会话配置 (CLI)

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # 复合工具集 — 展开为 file + terminal + web
hermes chat --toolsets all              # 全部工具
```

### 按平台配置 (config.yaml)

```yaml
toolsets:
  - hermes-cli          # CLI 的默认配置
  # - hermes-telegram   # 为 Telegram 消息网关覆盖
```

### 交互式管理

```bash
hermes tools                            # 用于按平台启用/禁用工具的 curses UI
```

或在会话内：

```
/tools list
/tools disable browser
/tools enable rl
```

## 核心工具集

| 工具集 | 包含工具 | 用途 |
|---------|-------|---------|
| `browser` | `browser_back`, `browser_click`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | 完整的浏览器自动化。包含 `web_search` 作为快速查找的备用方案。 |
| `clarify` | `clarify` | 当 Agent 需要澄清时向用户提问。 |
| `code_execution` | `execute_code` | 运行以编程方式调用 Hermes 工具的 Python 脚本。 |
| `cronjob` | `cronjob` | 调度和管理重复性任务。 |
| `delegation` | `delegate_task` | 生成隔离的子 Agent 实例以进行并行工作。 |
| `feishu_doc` | `feishu_doc_read` | 读取飞书/Lark 文档内容。由飞书文档评论智能回复处理器使用。 |
| `feishu_drive` | `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies`, `feishu_drive_reply_comment` | 飞书/Lark 云盘评论操作。作用域限定于评论 Agent；不在 `hermes-cli` 或其他消息工具集上公开。 |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | 文件读取、写入、搜索和编辑。 |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | 通过 Home Assistant 进行智能家居控制。仅在设置 `HASS_TOKEN` 时可用。 |
| `image_gen` | `image_generate` | 通过 FAL.ai 进行文生图。 |
| `memory` | `memory` | 跨会话的持久化记忆管理。 |
| `messaging` | `send_message` | 在会话内向其他平台（Telegram、Discord 等）发送消息。 |
| `moa` | `mixture_of_agents` | 通过 Mixture of Agents 实现多模型共识。 |
| `rl` | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` | RL 训练执行环境管理 (Atropos)。 |
| `search` | `web_search` | 仅限网络搜索（不包含提取）。 |
| `session_search` | `session_search` | 搜索过去的对话会话。 |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | 技能的增删改查和浏览。 |
| `terminal` | `process`, `terminal` | Shell 命令执行和后台进程管理。 |
| `todo` | `todo` | 会话内的任务列表管理。 |
| `tts` | `text_to_speech` | 文本转语音音频生成。 |
| `vision` | `vision_analyze` | 通过支持视觉的模型进行图像分析。 |
| `web` | `web_extract`, `web_search` | 网络搜索和页面内容提取。 |

## 复合工具集

这些工具集会展开为多个核心工具集，为常见场景提供便捷的简写：

| 工具集 | 展开为 | 使用场景 |
|---------|-----------|----------|
| `debugging` | `web` + `file` + `process`, `terminal` (通过 `includes`) — 实际上是 `patch`, `process`, `read_file`, `search_files`, `terminal`, `web_extract`, `web_search`, `write_file` | 调试会话 — 文件访问、终端和网络研究，无需浏览器或委派开销。 |
| `safe` | `image_generate`, `vision_analyze`, `web_extract`, `web_search` | 只读研究和媒体生成。无文件写入、无终端访问、无代码执行。适用于不受信任或受限的执行环境。 |

## 平台工具集

平台工具集定义了部署目标的完整工具配置。大多数消息平台使用与 `hermes-cli` 相同的集合：

| 工具集 | 与 `hermes-cli` 的差异 |
|---------|-------------------------------|
| `hermes-cli` | 完整工具集 — 所有 36 个核心工具，包括 `clarify`。交互式 CLI 会话的默认配置。 |
| `hermes-acp` | 移除 `clarify`, `cronjob`, `image_generate`, `send_message`, `text_to_speech`, homeassistant 工具。专注于 IDE 上下文中的编码任务。 |
| `hermes-api-server` | 移除 `clarify`, `send_message` 和 `text_to_speech`。添加其他所有工具 — 适用于无法进行用户交互的程序化访问。 |
| `hermes-telegram` | 与 `hermes-cli` 相同。 |
| `hermes-discord` | 与 `hermes-cli` 相同。 |
| `hermes-slack` | 与 `hermes-cli` 相同。 |
| `hermes-whatsapp` | 与 `hermes-cli` 相同。 |
| `hermes-signal` | 与 `hermes-cli` 相同。 |
| `hermes-matrix` | 与 `hermes-cli` 相同。 |
| `hermes-mattermost` | 与 `hermes-cli` 相同。 |
| `hermes-email` | 与 `hermes-cli` 相同。 |
| `hermes-sms` | 与 `hermes-cli` 相同。 |
| `hermes-bluebubbles` | 与 `hermes-cli` 相同。 |
| `hermes-dingtalk` | 与 `hermes-cli` 相同。 |
| `hermes-feishu` | 与 `hermes-cli` 相同。注意：`feishu_doc` / `feishu_drive` 工具集仅由文档评论处理器使用，而非常规的飞书聊天适配器。 |
| `hermes-qqbot` | 与 `hermes-cli` 相同。 |
| `hermes-wecom` | 与 `hermes-cli` 相同。 |
| `hermes-wecom-callback` | 与 `hermes-cli` 相同。 |
| `hermes-weixin` | 与 `hermes-cli` 相同。 |
| `hermes-homeassistant` | 与 `hermes-cli` 相同，并且始终启用 `homeassistant` 工具集。 |
| `hermes-webhook` | 与 `hermes-cli` 相同。 |
| `hermes-gateway` | 内部消息网关编排器工具集 — 当消息网关需要接受任何消息源时，使用最广泛可能的工具集的并集。 |

## 动态工具集

### MCP 服务器工具集

每个已配置的 MCP 服务器在运行时都会生成一个 `mcp-<server>` 工具集。例如，如果配置了一个 `github` MCP 服务器，则会创建一个包含该服务器公开的所有工具的 `mcp-github` 工具集。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这将创建一个可以在 `--toolsets` 或平台配置中引用的 `mcp-github` 工具集。

### 插件工具集

插件可以在初始化期间通过 `ctx.register_tool()` 注册自己的工具集。这些工具集会与内置工具集一起出现，并且可以以相同的方式启用/禁用。

### 自定义工具集

在 `config.yaml` 中定义自定义工具集，以创建特定于项目的捆绑包：

```yaml
toolsets:
  - hermes-cli
custom_toolsets:
  data-science:
    - file
    - terminal
    - code_execution
    - web
    - vision
```

### 通配符

- `all` 或 `*` — 展开为每个已注册的工具集（内置 + 动态 + 插件）

## 与 `hermes tools` 的关系

`hermes tools` 命令提供了一个基于 curses 的 UI，用于按平台逐个启用或禁用工具。这是在工具级别（比工具集更精细）进行操作，并将持久化到 `config.yaml`。即使其所属的工具集已启用，被禁用的工具也会被过滤掉。

另请参阅：[工具参考](./tools-reference.md) 以获取完整工具列表及其参数。