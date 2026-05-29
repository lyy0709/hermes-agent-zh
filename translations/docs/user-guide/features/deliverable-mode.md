---
title: 交付模式（聊天中的文件附件）
sidebar_label: 交付模式
description: Agent 如何将生成的图表、PDF、电子表格和其他文件作为原生附件发送到消息平台。
---

# 交付模式

当 Hermes Agent 在消息网关（Slack、Discord、Telegram、WhatsApp、Signal 等）内部运行时，它可以将生成的文件直接发送到聊天中——不是作为需要用户复制的路径，而是作为原生附件。

图表以内联图片形式显示。PDF 报告以文件下载形式显示。电子表格以 `.xlsx` 格式上传。Agent 无需编写 `MEDIA:` 标签或做任何特殊操作——它只需生成文件并在响应中提及文件的绝对路径。网关会从文本中提取路径，将其从可见消息中移除，并以原生方式上传文件。

## 工作原理

三个部分协同工作：

1.  **Agent 拥有能生成文件的工具。** 例如，通过 matplotlib 生成图表的 `execute_code`、用于 PDF 的 `latex-pdf-report` 技能、用于演示文稿的 `powerpoint` 技能、用于图像的 `image_generate`、用于音频的 `text_to_speech` 等等。

2.  **网关扫描 Agent 响应中的文件路径。** 任何以支持的扩展名结尾的绝对路径（`/tmp/...`）或主目录相对路径（`~/...`）都会被提取。代码块和行内代码中的路径会被忽略，因此代码示例永远不会被破坏。

3.  **网关根据文件类型进行分发。** 图像在平台支持的情况下内联嵌入；视频内联嵌入；音频路由到语音/音频附件；其他所有文件都作为文件附件上传。

## 支持的文件扩展名

| 类别 | 扩展名 | 交付方式 |
|---|---|---|
| 图像 | `.png .jpg .jpeg .gif .webp .bmp .tiff .svg` | 内联嵌入 |
| 视频 | `.mp4 .mov .avi .mkv .webm` | 内联嵌入（在支持的情况下） |
| 音频 | `.mp3 .wav .ogg .m4a .flac` | 语音 / 音频附件 |
| 文档 | `.pdf .docx .doc .odt .rtf .txt .md` | 文件上传 |
| 数据 | `.xlsx .xls .csv .tsv .json .xml .yaml .yml` | 文件上传 |
| 演示文稿 | `.pptx .ppt .odp` | 文件上传 |
| 归档文件 | `.zip .tar .gz .tgz .bz2 .7z` | 文件上传 |
| 网页 | `.html .htm` | 文件上传 |

`.py`、`.log` 和其他源文件扩展名被有意排除，这样 Agent 就不会自动发送任意源文件；如果你想向用户发送代码，请使用代码块。

## 鼓励 Agent 生成文件

默认情况下，Agent 不会主动生成文件——它需要知道要这样做。有两种方法可以引导它：

**按会话：** 明确要求（"将比较结果以图表形式发送给我"、"以 CSV 格式返回数据"）或编写你自己的自定义指令/人格条目，使其在消息平台上偏向于生成文件形式的回复。

**项目级别：** 将这种偏好添加到 Agent 工作的项目中的 `AGENTS.md` / `CLAUDE.md` / `.cursorrules` 中，添加到你在 `~/.hermes/SOUL.md` 中的全局人格中，或作为 `~/.hermes/config.yaml` 中 `agent.personalities` 下的命名预设（可通过 `/personality` 按会话切换）。

Agent 需要使用的机制很简单：将文件渲染到绝对路径（例如 `/tmp/q3-revenue.png`），并在回复中以纯文本形式提及该路径。网关会处理其余的事情。围栏代码块或反引号内的路径会被忽略，因此代码示例永远不会被破坏。

## 看板：文件随完成通知一起发送

如果你使用 Hermes 的看板多 Agent 工作流，工作 Agent 可以将交付文件附加到它们的 `kanban_complete` 调用中：

```python
kanban_complete(
    summary="rendered Q3 revenue chart and report",
    artifacts=[
        "/tmp/q3-revenue.png",
        "/tmp/q3-report.pdf",
    ],
)
```

当网关通知器将"任务完成"消息发送给在 Slack/Telegram 等平台订阅了该任务的任何人时，它还会将每个文件作为原生附件上传到该聊天中。用户可以在一个地方获得交付文件和摘要。

通知器运行时磁盘上不存在的文件会被静默跳过。

## 通过 MCP 连接更多服务

除了文件交付流水线，Agent 还可以通过 MCP（模型上下文协议）连接到其他服务。MCP 生态系统为大多数流行工具提供了社区服务器——安装你需要的任何服务：

| 服务 | 它能解锁的功能 |
|---|---|
| **Notion** | 读写 Notion 页面、数据库，查询工作区 |
| **GitHub** | 问题、PR、评论，超越 gh CLI 的仓库搜索 |
| **Linear** | 工单、项目、周期 |
| **Slack** | 工作区范围的搜索，读取其他频道 |
| **Gmail** | 收件箱分类，发送邮件，标签管理 |
| **Salesforce** | 潜在客户、商机、账户数据 |
| **Snowflake / BigQuery** | 对数据仓库执行 SQL |
| **Google Drive** | 文件搜索、内容、共享管理 |

通过 `~/.hermes/config.yaml` 中的 `mcp_servers` 部分安装 MCP 服务器。完整的设置指南请参见 [MCP 集成](./mcp.md)。

## 与 Slack 中的 Perplexity Computer 对比

Perplexity Computer 的 Slack 集成基于相同的理念：Agent 生成一个交付文件（图表、PDF、幻灯片）并将其作为原生附件发布回线程中。Hermes Agent 的交付模式在本地提供了相同的面向用户的模式：

-   生成在用户自己的 venv / 沙盒中进行（没有远程租户）。
-   文件通过相同的 Slack `files.uploadV2` API 进入聊天。
-   连接器的广度通过 MCP 实现，而不是一个包含 400 个托管集成的精选目录——只安装你实际使用的那些。

OAuth Token 保留在用户机器的 `auth.json` / `.env` 中。没有托管的 Token 存储。没有多租户微虚拟机。最终结果相同。