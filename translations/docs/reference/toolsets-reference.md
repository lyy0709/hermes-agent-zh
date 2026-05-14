---
sidebar_position: 4
title: "工具集参考"
description: "Hermes 核心、组合、平台和动态工具集的参考文档"
---

# 工具集参考

工具集是命名的工具捆绑包，用于控制 Agent 可以执行的操作。它们是按平台、按会话或按任务配置工具可用性的主要机制。

## 工具集工作原理

每个工具都属于且仅属于一个工具集。当您启用一个工具集时，该捆绑包中的所有工具都将对 Agent 可用。工具集分为三种类型：

- **核心** — 单个逻辑上相关的工具组（例如，`file` 捆绑了 `read_file`、`write_file`、`patch`、`search_files`）
- **组合** — 为常见场景组合多个核心工具集（例如，`debugging` 捆绑了文件、终端和网络工具）
- **平台** — 针对特定部署上下文的完整工具配置（例如，`hermes-cli` 是交互式 CLI 会话的默认配置）

## 配置工具集

### 按会话配置 (CLI)

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # 组合工具集 — 展开为 file + terminal + web
hermes chat --toolsets all              # 全部工具
```

### 按平台配置 (config.yaml)

```yaml
toolsets:
  - hermes-cli          # CLI 的默认配置
  # - hermes-telegram   # Telegram 消息网关的覆盖配置
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

| 工具集 | 工具 | 用途 |
|---------|-------|---------|
| `browser` | `browser_back`, `browser_cdp`, `browser_click`, `browser_console`, `browser_dialog`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | 核心浏览器自动化。包含 `web_search` 作为快速查找的备用方案。`browser_cdp` 和 `browser_dialog` 在运行时受控 — 仅在会话开始时 CDP 端点可达时注册（通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 或 Camofox）。`browser_dialog` 与 `browser_snapshot` 在附加了 CDP 监督器时添加的 `pending_dialogs` 和 `frame_tree` 字段协同工作。 |
| `clarify` | `clarify` | 当 Agent 需要澄清时向用户提问。 |
| `code_execution` | `execute_code` | 运行以编程方式调用 Hermes 工具的 Python 脚本。 |
| `cronjob` | `cronjob` | 调度和管理重复性任务。 |
| `debugging` | 组合 (`file` + `terminal` + `web`) | 调试捆绑包 — 文件、进程/终端、网络提取/搜索。 |
| `delegation` | `delegate_task` | 为并行工作生成隔离的子 Agent 实例。 |
| `discord` | `discord` | 核心 Discord 文本/嵌入/DM 操作（仅限消息网关）。在 `hermes-discord` 工具集上激活。 |
| `discord_admin` | `discord_admin` | Discord 管理（封禁、角色变更、频道管理）。在 `hermes-discord` 工具集上激活；要求机器人拥有相关的 Discord 权限。 |
| `feishu_doc` | `feishu_doc_read` | 读取飞书/Lark 文档内容。由飞书文档评论智能回复处理器使用。 |
| `feishu_drive` | `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies`, `feishu_drive_reply_comment` | 飞书/Lark 云盘评论操作。限定于评论 Agent；不在 `hermes-cli` 或其他消息工具集上公开。 |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | 文件读取、写入、搜索和编辑。 |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | 通过 Home Assistant 进行智能家居控制。仅在设置 `HASS_TOKEN` 时可用。 |
| `computer_use` | `computer_use` | 通过 cua-driver 进行后台 macOS 桌面控制 — 不窃取光标/焦点。适用于任何支持工具的模型。仅限 macOS；要求 `cua-driver` 在 `$PATH` 中。 |
| `image_gen` | `image_generate` | 通过 FAL.ai 进行文生图（可选择 OpenAI / xAI 后端）。 |
| `video_gen` | `video_generate` | 通过插件注册的后端进行文生视频和图生视频（xAI Grok-Imagine、FAL.ai Veo 3.1 / Pixverse v6 / Kling O3）。传递 `image_url` 以动画化图像；省略则进行文生视频。 |
| `kanban` | `kanban_block`, `kanban_comment`, `kanban_complete`, `kanban_create`, `kanban_heartbeat`, `kanban_link`, `kanban_show` | 多 Agent 协调工具 — 仅在 Agent 由看板调度器生成时注册（设置 `HERMES_KANBAN_TASK` 环境变量）。允许工作者通过结构化交接标记任务完成、为人工输入阻塞、在长时间操作期间发送心跳、评论线程，以及（对于编排器）将任务分发到子任务。 |
| `memory` | `memory` | 跨会话的持久化记忆管理。 |
| `messaging` | `send_message` | 在会话内向其他平台（Telegram、Discord 等）发送消息。 |
| `moa` | `mixture_of_agents` | 通过 Mixture of Agents 进行多模型共识。 |
| `rl` | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` | RL 训练环境管理 (Atropos)。 |
| `safe` | `image_generate`, `vision_analyze`, `web_extract`, `web_search` (通过 `includes`) | 只读研究 + 媒体生成。无文件写入、无终端、无代码执行。 |
| `search` | `web_search` | 仅网络搜索（无提取）。 |
| `session_search` | `session_search` | 搜索过去的对话会话。 |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | 技能 CRUD 和浏览。 |
| `spotify` | `spotify_albums`, `spotify_devices`, `spotify_library`, `spotify_playback`, `spotify_playlists`, `spotify_queue`, `spotify_search` | 原生 Spotify 控制（播放、队列、搜索、播放列表、专辑、资料库）。由捆绑的 `spotify` 插件注册。 |
| `terminal` | `process`, `terminal` | Shell 命令执行和后台进程管理。 |
| `todo` | `todo` | 会话内的任务列表管理。 |
| `tts` | `text_to_speech` | 文本转语音音频生成。 |
| `vision` | `vision_analyze` | 通过支持视觉的模型进行图像分析。 |
| `video` | `video_analyze` | 视频分析和理解工具（需选择加入，不在默认工具集中 — 通过 `--toolsets` 显式添加）。 |
| `web` | `web_extract`, `web_search` | 网络搜索和页面内容提取。 |
| `yuanbao` | `yb_query_group_info`, `yb_query_group_members`, `yb_search_sticker`, `yb_send_dm`, `yb_send_sticker` | 元宝 DM/群组操作和表情搜索。仅在 `hermes-yuanbao` 上注册。 |

## 平台工具集

平台工具集为部署目标定义完整的工具配置。大多数消息平台使用与 `hermes-cli` 相同的集合：

| 工具集 | 与 `hermes-cli` 的差异 |
|---------|-------------------------------|
| `hermes-cli` | 完整工具集 — 交互式 CLI 会话的默认配置。包含文件、终端、网络、浏览器、记忆、技能、视觉、图像生成、待办、TTS、委派、代码执行、定时任务、会话搜索、澄清以及 `safe`（只读）捆绑包，外加标准消息工具。 |
| `hermes-acp` | 移除 `clarify`、`cronjob`、`image_generate`、`send_message`、`text_to_speech` 以及所有四个 Home Assistant 工具。专注于 IDE 上下文中的编码任务。 |
| `hermes-api-server` | 移除 `clarify`、`send_message` 和 `text_to_speech`。保留其他所有工具 — 适用于无法进行用户交互的程序化访问。 |
| `hermes-cron` | 与 `hermes-cli` 相同。 |
| `hermes-telegram` | 与 `hermes-cli` 相同。 |
| `hermes-discord` | 在 `hermes-cli` 基础上添加 `discord` 和 `discord_admin`。 |
| `hermes-slack` | 与 `hermes-cli` 相同。 |
| `hermes-whatsapp` | 与 `hermes-cli` 相同。 |
| `hermes-signal` | 与 `hermes-cli` 相同。 |
| `hermes-matrix` | 与 `hermes-cli` 相同。 |
| `hermes-mattermost` | 与 `hermes-cli` 相同。 |
| `hermes-email` | 与 `hermes-cli` 相同。 |
| `hermes-sms` | 与 `hermes-cli` 相同。 |
| `hermes-bluebubbles` | 与 `hermes-cli` 相同。 |
| `hermes-dingtalk` | 与 `hermes-cli` 相同。 |
| `hermes-feishu` | 添加五个 `feishu_doc_*` / `feishu_drive_*` 工具（仅由文档评论处理器使用，而非常规聊天适配器）。 |
| `hermes-qqbot` | 与 `hermes-cli` 相同。 |
| `hermes-wecom` | 与 `hermes-cli` 相同。 |
| `hermes-wecom-callback` | 与 `hermes-cli` 相同。 |
| `hermes-weixin` | 与 `hermes-cli` 相同。 |
| `hermes-yuanbao` | 在 `hermes-cli` 基础上添加五个 `yb_*` 工具（DM/群组/表情）。 |
| `hermes-homeassistant` | 与 `hermes-cli` 相同（Home Assistant 工具默认已存在，并在设置 `HASS_TOKEN` 时激活）。 |
| `hermes-webhook` | 与 `hermes-cli` 相同。 |
| `hermes-gateway` | 内部消息网关编排器工具集 — 所有 `hermes-<平台>` 工具集的并集；当消息网关需要接受任何消息源时使用。 |

## 动态工具集

### MCP 服务器工具集

每个配置的 MCP 服务器在运行时都会生成一个 `mcp-<服务器>` 工具集。例如，如果您配置了一个 `github` MCP 服务器，则会创建一个包含该服务器公开的所有工具的 `mcp-github` 工具集。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这将创建一个您可以在 `--toolsets` 或平台配置中引用的 `mcp-github` 工具集。

### 插件工具集

插件可以在插件初始化期间通过 `ctx.register_tool()` 注册自己的工具集。这些工具集与内置工具集一起出现，并且可以以相同的方式启用/禁用。

### 自定义工具集

在 `config.yaml` 中定义自定义工具集以创建项目特定的捆绑包：

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

`hermes tools` 命令提供了一个基于 curses 的 UI，用于按平台切换单个工具的启用或禁用。这在工具级别（比工具集更精细）操作，并持久化到 `config.yaml`。即使其所属的工具集已启用，被禁用的工具也会被过滤掉。

另请参阅：[工具参考](./tools-reference.md) 以获取完整的单个工具及其参数列表。