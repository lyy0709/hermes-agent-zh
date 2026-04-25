---
title: "Fastmcp — 使用 FastMCP 在 Python 中构建、测试、检查、安装和部署 MCP 服务器"
sidebar_label: "Fastmcp"
description: "使用 FastMCP 在 Python 中构建、测试、检查、安装和部署 MCP 服务器"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Fastmcp

使用 FastMCP 在 Python 中构建、测试、检查、安装和部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库包装为 MCP 工具、暴露资源或提示词，或为 Claude Code、Cursor 或 HTTP 部署准备 FastMCP 服务器。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mcp/fastmcp` 安装 |
| 路径 | `optional-skills/mcp/fastmcp` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `MCP`, `FastMCP`, `Python`, `工具`, `资源`, `提示词`, `部署` |
| 相关技能 | [`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp), [`mcporter`](/docs/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# FastMCP

使用 FastMCP 在 Python 中构建 MCP 服务器，在本地验证它们，将它们安装到 MCP 客户端中，并将它们部署为 HTTP 端点。

## 何时使用

当任务涉及以下情况时使用此技能：

- 在 Python 中创建新的 MCP 服务器
- 将 API、数据库、CLI 或文件处理工作流包装为 MCP 工具
- 除了工具之外，还暴露资源或提示词
- 在将其连接到 Hermes 或其他客户端之前，使用 FastMCP CLI 对服务器进行冒烟测试
- 将服务器安装到 Claude Code、Claude Desktop、Cursor 或类似的 MCP 客户端中
- 为 HTTP 部署准备 FastMCP 服务器仓库

当服务器已存在且仅需要连接到 Hermes 时，使用 `native-mcp`。当目标是临时通过 CLI 访问现有 MCP 服务器而非构建一个时，使用 `mcporter`。

## 先决条件

首先在工作环境中安装 FastMCP：

```bash
pip install fastmcp
fastmcp version
```

对于 API 模板，如果尚未安装 `httpx`，请安装：

```bash
pip install httpx
```

## 包含的文件

### 模板

- `templates/api_wrapper.py` - 支持认证头的 REST API 包装器
- `templates/database_server.py` - 只读 SQLite 查询服务器
- `templates/file_processor.py` - 文本文件检查和搜索服务器

### 脚本

- `scripts/scaffold_fastmcp.py` - 复制一个启动模板并替换服务器名称占位符

### 参考资料

- `references/fastmcp-cli.md` - FastMCP CLI 工作流、安装目标和部署检查

## 工作流

### 1. 选择最小的可行服务器形态

首先选择最窄的有用范围：

- API 包装器：从 1-3 个高价值端点开始，而不是整个 API
- 数据库服务器：暴露只读内省和受约束的查询路径
- 文件处理器：暴露具有明确路径参数的确定性操作
- 提示词/资源：仅在客户端需要可重用的提示词模板或可发现的文档时添加

优先选择具有良好名称、文档字符串和模式的精简服务器，而不是具有模糊工具的大型服务器。

### 2. 从模板搭建

直接复制模板或使用脚手架助手：

```bash
python ~/.hermes/skills/mcp/fastmcp/scripts/scaffold_fastmcp.py \
  --template api_wrapper \
  --name "Acme API" \
  --output ./acme_server.py
```

可用模板：

```bash
python ~/.hermes/skills/mcp/fastmcp/scripts/scaffold_fastmcp.py --list
```

如果手动复制，请将 `__SERVER_NAME__` 替换为真实的服务器名称。

### 3. 首先实现工具

在添加资源或提示词之前，先从 `@mcp.tool` 函数开始。

工具设计规则：

- 为每个工具起一个具体的、基于动词的名称
- 将文档字符串写成面向用户的工具描述
- 保持参数明确且类型化
- 尽可能返回结构化的 JSON 安全数据
- 尽早验证不安全的输入
- 对于第一个版本，默认优先选择只读行为

好的工具示例：

- `get_customer`
- `search_tickets`
- `describe_table`
- `summarize_text_file`

弱的工具示例：

- `run`
- `process`
- `do_thing`

### 4. 仅在有助于时才添加资源和提示词

当客户端受益于获取稳定的只读内容（如模式、策略文档或生成的报告）时，添加 `@mcp.resource`。

当服务器应为已知工作流提供可重用的提示词模板时，添加 `@mcp.prompt`。

不要将每个文档都变成提示词。优先选择：

- 工具用于操作
- 资源用于数据/文档检索
- 提示词用于可重用的 LLM 指令

### 5. 在集成到任何地方之前测试服务器

使用 FastMCP CLI 进行本地验证：

```bash
fastmcp inspect acme_server.py:mcp
fastmcp list acme_server.py --json
fastmcp call acme_server.py search_resources query=router limit=5 --json
```

为了快速迭代调试，在本地运行服务器：

```bash
fastmcp run acme_server.py:mcp
```

要在本地测试 HTTP 传输：

```bash
fastmcp run acme_server.py:mcp --transport http --host 127.0.0.1 --port 8000
fastmcp list http://127.0.0.1:8000/mcp --json
fastmcp call http://127.0.0.1:8000/mcp search_resources query=router --json
```

在声称服务器工作之前，始终至少对每个新工具运行一次真实的 `fastmcp call`。

### 6. 在本地验证通过后安装到客户端

FastMCP 可以将服务器注册到支持的 MCP 客户端：

```bash
fastmcp install claude-code acme_server.py
fastmcp install claude-desktop acme_server.py
fastmcp install cursor acme_server.py -e .
```

使用 `fastmcp discover` 来检查机器上已配置的命名 MCP 服务器。

当目标是 Hermes 集成时，可以：

- 使用 `native-mcp` 技能在 `~/.hermes/config.yaml` 中配置服务器，或者
- 在开发期间继续使用 FastMCP CLI 命令，直到接口稳定

### 7. 在本地合约稳定后进行部署

对于托管部署，Prefect Horizon 是 FastMCP 文档最直接记录的路径。在部署之前：

```bash
fastmcp inspect acme_server.py:mcp
```

确保仓库包含：

- 包含 FastMCP 服务器对象的 Python 文件
- `requirements.txt` 或 `pyproject.toml`
- 部署所需的任何环境变量文档

对于通用的 HTTP 托管，首先在本地验证 HTTP 传输，然后部署在任何可以暴露服务器端口的 Python 兼容平台上。

## 常见模式

### API 包装器模式

当将 REST 或 HTTP API 暴露为 MCP 工具时使用。

推荐的第一个切片：

- 一个读取路径
- 一个列表/搜索路径
- 可选的健康检查

实现注意事项：

- 将认证信息保存在环境变量中，而不是硬编码
- 在一个辅助函数中集中请求逻辑
- 用简洁的上下文呈现 API 错误
- 在返回之前规范化不一致的上游负载

从 `templates/api_wrapper.py` 开始。

### 数据库模式

当暴露安全的查询和检查能力时使用。

推荐的第一个切片：

- `list_tables`
- `describe_table`
- 一个受约束的读取查询工具

实现注意事项：

- 默认使用只读数据库访问
- 在早期版本中拒绝非 `SELECT` SQL
- 限制行数
- 返回行和列名

从 `templates/database_server.py` 开始。

### 文件处理器模式

当服务器需要按需检查或转换文件时使用。

推荐的第一个切片：

- 总结文件内容
- 在文件内搜索
- 提取确定性元数据

实现注意事项：

- 接受明确的文件路径
- 检查缺失的文件和编码失败
- 限制预览和结果数量
- 除非需要特定的外部工具，否则避免调用 shell

从 `templates/file_processor.py` 开始。

## 质量标准

在交付 FastMCP 服务器之前，验证以下所有内容：

- 服务器可以干净地导入
- `fastmcp inspect <file.py:mcp>` 成功
- `fastmcp list <server spec> --json` 成功
- 每个新工具至少有一个真实的 `fastmcp call`
- 环境变量已记录
- 工具表面足够小，无需猜测即可理解

## 故障排除

### FastMCP 命令缺失

在活动环境中安装包：

```bash
pip install fastmcp
fastmcp version
```

### `fastmcp inspect` 失败

检查：

- 文件导入时没有导致崩溃的副作用
- FastMCP 实例在 `<file.py:object>` 中命名正确
- 模板的可选依赖项已安装

### 工具在 Python 中工作，但通过 CLI 不工作

运行：

```bash
fastmcp list server.py --json
fastmcp call server.py your_tool_name --json
```

这通常会暴露命名不匹配、缺少必需参数或不可序列化的返回值。

### Hermes 无法看到已部署的服务器

服务器构建部分可能正确，但 Hermes 配置不正确。加载 `native-mcp` 技能并在 `~/.hermes/config.yaml` 中配置服务器，然后重启 Hermes。

## 参考资料

有关 CLI 详细信息、安装目标和部署检查，请阅读 `references/fastmcp-cli.md`。