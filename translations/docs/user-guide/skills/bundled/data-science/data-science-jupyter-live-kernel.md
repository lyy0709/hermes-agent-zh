---
title: "Jupyter Live Kernel — 通过实时 Jupyter 内核进行迭代式 Python 编程 (hamelnb)"
sidebar_label: "Jupyter Live Kernel"
description: "通过实时 Jupyter 内核进行迭代式 Python 编程 (hamelnb)"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Jupyter Live Kernel

通过实时 Jupyter 内核进行迭代式 Python 编程 (hamelnb)。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/data-science/jupyter-live-kernel` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `jupyter`, `notebook`, `repl`, `data-science`, `exploration`, `iterative` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Jupyter Live Kernel (hamelnb)

通过实时 Jupyter 内核为你提供一个**有状态的 Python REPL**。变量在多次执行间保持持久。当你需要逐步构建状态、探索 API、检查 DataFrame 或迭代复杂代码时，请使用此技能代替 `execute_code`。

## 何时使用此工具 vs 其他工具

| 工具 | 使用场景 |
|------|----------|
| **此技能** | 迭代式探索、跨步骤的状态保持、数据科学、机器学习、"让我试试这个并检查一下" |
| `execute_code` | 需要访问 Hermes 工具（web_search、文件操作）的一次性脚本。无状态。 |
| `terminal` | Shell 命令、构建、安装、git、进程管理 |

**经验法则：** 如果某项任务你希望使用 Jupyter notebook，那么就使用此技能。

## 先决条件

1. 必须安装 **uv**（检查：`which uv`）
2. 必须安装 **JupyterLab**：`uv tool install jupyterlab`
3. 必须运行一个 Jupyter 服务器（见下方设置）

## 设置

hamelnb 脚本位置：
```
SCRIPT="$HOME/.agent-skills/hamelnb/skills/jupyter-live-kernel/scripts/jupyter_live_kernel.py"
```

如果尚未克隆：
```
git clone https://github.com/hamelsmu/hamelnb.git ~/.agent-skills/hamelnb
```

### 启动 JupyterLab

检查服务器是否已在运行：
```
uv run "$SCRIPT" servers
```

如果未找到服务器，则启动一个：
```
jupyter-lab --no-browser --port=8888 --notebook-dir=$HOME/notebooks \
  --IdentityProvider.token='' --ServerApp.password='' > /tmp/jupyter.log 2>&1 &
sleep 3
```

注意：为方便本地 Agent 访问，禁用了 Token/密码。服务器以无头模式运行。

### 为 REPL 使用创建 Notebook

如果你只需要一个 REPL（没有现有的 notebook），创建一个最小的 notebook 文件：
```
mkdir -p ~/notebooks
```
编写一个包含一个空代码单元的最小 .ipynb JSON 文件，然后通过 Jupyter REST API 启动一个内核会话：
```
curl -s -X POST http://127.0.0.1:8888/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"path":"scratch.ipynb","type":"notebook","name":"scratch.ipynb","kernel":{"name":"python3"}}'
```

## 核心工作流

所有命令都返回结构化的 JSON。始终使用 `--compact` 以节省 Token。

### 1. 发现服务器和 notebook

```
uv run "$SCRIPT" servers --compact
uv run "$SCRIPT" notebooks --compact
```

### 2. 执行代码（主要操作）

```
uv run "$SCRIPT" execute --path <notebook.ipynb> --code '<python code>' --compact
```

状态在多次 execute 调用间保持持久。变量、导入、对象都会保留。

多行代码使用 $'...' 引用：
```
uv run "$SCRIPT" execute --path scratch.ipynb --code $'import os\nfiles = os.listdir(".")\nprint(f"Found {len(files)} files")' --compact
```

### 3. 检查实时变量

```
uv run "$SCRIPT" variables --path <notebook.ipynb> list --compact
uv run "$SCRIPT" variables --path <notebook.ipynb> preview --name <varname> --compact
```

### 4. 编辑 notebook 单元

```
# 查看当前单元
uv run "$SCRIPT" contents --path <notebook.ipynb> --compact

# 插入新单元
uv run "$SCRIPT" edit --path <notebook.ipynb> insert \
  --at-index <N> --cell-type code --source '<code>' --compact

# 替换单元源代码（使用 contents 输出中的 cell-id）
uv run "$SCRIPT" edit --path <notebook.ipynb> replace-source \
  --cell-id <id> --source '<new code>' --compact

# 删除单元
uv run "$SCRIPT" edit --path <notebook.ipynb> delete --cell-id <id> --compact
```

### 5. 验证（重启并运行全部）

仅在用户要求进行干净的验证或你需要确认 notebook 能从头到尾运行时使用：

```
uv run "$SCRIPT" restart-run-all --path <notebook.ipynb> --save-outputs --compact
```

## 来自经验的实用技巧

1.  **服务器启动后的首次执行可能会超时** — 内核需要一点时间来初始化。如果遇到超时，只需重试。
2.  **内核的 Python 是 JupyterLab 的 Python** — 包必须安装在该环境中。如果需要额外的包，请先将其安装到 JupyterLab 工具环境中。
3.  **`--compact` 标志能显著节省 Token** — 始终使用它。没有它，JSON 输出会非常冗长。
4.  **对于纯 REPL 使用**，创建一个 scratch.ipynb 文件，无需费心编辑单元。只需重复使用 `execute`。
5.  **参数顺序很重要** — 像 `--path` 这样的子命令标志放在子子命令**之前**。例如：`variables --path nb.ipynb list` 而不是 `variables list --path nb.ipynb`。
6.  **如果会话尚不存在**，你需要通过 REST API 启动一个（见设置部分）。没有活动的内核会话，工具无法执行。
7.  **错误以 JSON 格式返回并包含回溯** — 阅读 `ename` 和 `evalue` 字段以了解出错原因。
8.  **偶尔的 websocket 超时** — 某些操作可能在第一次尝试时超时，尤其是在内核重启后。在升级问题前先重试一次。

## 超时默认值

脚本的每次执行默认超时为 30 秒。对于长时间运行的操作，传递 `--timeout 120`。对于初始设置或繁重计算，请使用更长的超时时间（60+）。