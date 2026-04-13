---
sidebar_position: 8
title: "代码执行"
description: "支持 RPC 工具访问的沙盒化 Python 执行 —— 将多步骤工作流压缩为单轮交互"
---

# 代码执行（编程式工具调用）

`execute_code` 工具允许 Agent 编写能够以编程方式调用 Hermes 工具的 Python 脚本，从而将多步骤工作流压缩为单轮 LLM 交互。脚本在 Agent 主机上的沙盒子进程中运行，通过 Unix 域套接字 RPC 进行通信。

## 工作原理

1.  Agent 使用 `from hermes_tools import ...` 编写 Python 脚本
2.  Hermes 生成一个包含 RPC 函数的 `hermes_tools.py` 存根模块
3.  Hermes 打开一个 Unix 域套接字并启动一个 RPC 监听线程
4.  脚本在子进程中运行 —— 工具调用通过套接字传回 Hermes
5.  只有脚本的 `print()` 输出会返回给 LLM；中间工具结果永远不会进入上下文窗口

```python
# Agent 可以编写如下脚本：
from hermes_tools import web_search, web_extract

results = web_search("Python 3.13 features", limit=5)
for r in results["data"]["web"]:
    content = web_extract([r["url"]])
    # ... 过滤和处理 ...
print(summary)
```

**沙盒中可用的工具：** `web_search`, `web_extract`, `read_file`, `write_file`, `search_files`, `patch`, `terminal`（仅限前台）。

## Agent 的使用时机

当出现以下情况时，Agent 会使用 `execute_code`：

- **3 次以上的工具调用**，且调用之间存在处理逻辑
- 批量数据过滤或条件分支
- 对结果进行循环处理

关键优势：中间工具结果永远不会进入上下文窗口 —— 只有最终的 `print()` 输出会返回，从而显著减少 Token 使用量。

## 实际示例

### 数据处理流水线

```python
from hermes_tools import search_files, read_file
import json

# 查找所有配置文件并提取数据库设置
matches = search_files("database", path=".", file_glob="*.yaml", limit=20)
configs = []
for match in matches.get("matches", []):
    content = read_file(match["path"])
    configs.append({"file": match["path"], "preview": content["content"][:200]})

print(json.dumps(configs, indent=2))
```

### 多步骤网络研究

```python
from hermes_tools import web_search, web_extract
import json

# 单轮内完成搜索、提取和总结
results = web_search("Rust async runtime comparison 2025", limit=5)
summaries = []
for r in results["data"]["web"]:
    page = web_extract([r["url"]])
    for p in page.get("results", []):
        if p.get("content"):
            summaries.append({
                "title": r["title"],
                "url": r["url"],
                "excerpt": p["content"][:500]
            })

print(json.dumps(summaries, indent=2))
```

### 批量文件重构

```python
from hermes_tools import search_files, read_file, patch

# 查找所有使用已弃用 API 的 Python 文件并修复它们
matches = search_files("old_api_call", path="src/", file_glob="*.py")
fixed = 0
for match in matches.get("matches", []):
    result = patch(
        path=match["path"],
        old_string="old_api_call(",
        new_string="new_api_call(",
        replace_all=True
    )
    if "error" not in str(result):
        fixed += 1

print(f"Fixed {fixed} files out of {len(matches.get('matches', []))} matches")
```

### 构建和测试流水线

```python
from hermes_tools import terminal, read_file
import json

# 运行测试，解析结果并报告
result = terminal("cd /project && python -m pytest --tb=short -q 2>&1", timeout=120)
output = result.get("output", "")

# 解析测试输出
passed = output.count(" passed")
failed = output.count(" failed")
errors = output.count(" error")

report = {
    "passed": passed,
    "failed": failed,
    "errors": errors,
    "exit_code": result.get("exit_code", -1),
    "summary": output[-500:] if len(output) > 500 else output
}

print(json.dumps(report, indent=2))
```

## 资源限制

| 资源 | 限制 | 说明 |
|----------|-------|-------|
| **超时** | 5 分钟 (300s) | 脚本会被 SIGTERM 终止，5 秒宽限期后发送 SIGKILL |
| **标准输出** | 50 KB | 输出会被截断，并附加 `[output truncated at 50KB]` 提示 |
| **标准错误** | 10 KB | 在非零退出时包含在输出中，用于调试 |
| **工具调用** | 每次执行 50 次 | 达到限制时返回错误 |

所有限制均可通过 `config.yaml` 配置：

```yaml
# 在 ~/.hermes/config.yaml 中
code_execution:
  timeout: 300       # 每个脚本的最大秒数（默认：300）
  max_tool_calls: 50 # 每次执行的最大工具调用次数（默认：50）
```

## 脚本内部工具调用的工作原理

当你的脚本调用类似 `web_search("query")` 的函数时：

1.  调用被序列化为 JSON，并通过 Unix 域套接字发送到父进程
2.  父进程通过标准的 `handle_function_call` 处理程序进行分派
3.  结果通过套接字发送回来
4.  函数返回解析后的结果

这意味着脚本内部的工具调用行为与普通工具调用完全相同 —— 相同的速率限制、相同的错误处理、相同的能力。唯一的限制是 `terminal()` 仅限前台使用（没有 `background` 或 `pty` 参数）。

## 错误处理

当脚本失败时，Agent 会收到结构化的错误信息：

-   **非零退出码**：标准错误包含在输出中，因此 Agent 可以看到完整的回溯信息
-   **超时**：脚本被终止，Agent 会看到 `"Script timed out after 300s and was killed."`
-   **中断**：如果用户在执行期间发送了新消息，脚本会被终止，Agent 会看到 `[execution interrupted — user sent a new message]`
-   **工具调用限制**：当达到 50 次调用限制时，后续的工具调用会返回错误消息

响应始终包含 `status`（success/error/timeout/interrupted）、`output`、`tool_calls_made` 和 `duration_seconds`。

## 安全性

:::danger 安全模型
子进程在**最小化环境**中运行。默认情况下，API 密钥、Token 和凭据会被剥离。脚本只能通过 RPC 通道访问工具 —— 除非明确允许，否则它无法从环境变量中读取密钥。
:::

名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD` 或 `AUTH` 的环境变量会被排除。只有安全的系统变量（`PATH`、`HOME`、`LANG`、`SHELL`、`PYTHONPATH`、`VIRTUAL_ENV` 等）会被传递。

### 技能环境变量透传

当技能在其 frontmatter 中声明 `required_environment_variables` 时，这些变量在技能加载后**会自动透传**到 `execute_code` 和 `terminal` 沙盒中。这使得技能可以使用其声明的 API 密钥，而不会削弱任意代码执行的安全性。

对于非技能用例，你可以在 `config.yaml` 中明确设置允许列表：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

完整详情请参阅[安全指南](/docs/user-guide/security#environment-variable-passthrough)。

脚本在临时目录中运行，执行后会被清理。子进程在其自己的进程组中运行，以便在超时或中断时能够被干净地终止。

## execute_code 与 terminal 对比

| 用例 | execute_code | terminal |
|----------|-------------|----------|
| 在工具调用之间进行多步骤工作流 | ✅ | ❌ |
| 简单的 shell 命令 | ❌ | ✅ |
| 过滤/处理大量工具输出 | ✅ | ❌ |
| 运行构建或测试套件 | ❌ | ✅ |
| 循环处理搜索结果 | ✅ | ❌ |
| 交互式/后台进程 | ❌ | ✅ |
| 需要在环境中使用 API 密钥 | ⚠️ 仅通过[透传](/docs/user-guide/security#environment-variable-passthrough) | ✅（大多数会透传） |

**经验法则：** 当你需要以编程方式调用 Hermes 工具，并在调用之间加入逻辑时，使用 `execute_code`。对于运行 shell 命令、构建和进程，使用 `terminal`。

## 平台支持

代码执行需要 Unix 域套接字，仅在 **Linux 和 macOS** 上可用。在 Windows 上会自动禁用 —— Agent 会回退到常规的顺序工具调用。