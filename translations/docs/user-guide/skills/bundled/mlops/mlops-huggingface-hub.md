---
title: "Huggingface Hub — HuggingFace hf CLI：搜索/下载/上传模型、数据集"
sidebar_label: "Huggingface Hub"
description: "HuggingFace hf CLI：搜索/下载/上传模型、数据集"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Huggingface Hub

HuggingFace hf CLI：搜索/下载/上传模型、数据集。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/huggingface-hub` |
| 版本 | `1.0.0` |
| 作者 | Hugging Face |
| 许可证 | MIT |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Hugging Face CLI (`hf`) 参考指南

`hf` 命令是与 Hugging Face Hub 交互的现代命令行界面，提供管理仓库、模型、数据集和 Spaces 的工具。

> **重要提示：** `hf` 命令现已取代已弃用的 `huggingface-cli` 命令。

## 快速开始
*   **安装：** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **帮助：** 使用 `hf --help` 查看所有可用功能和实际示例。
*   **认证：** 建议通过 `HF_TOKEN` 环境变量或 `--token` 标志进行。

---

## 核心命令

### 通用操作
*   `hf download REPO_ID`：从 Hub 下载文件。
*   `hf upload REPO_ID`：上传文件/文件夹（推荐用于单次提交）。
*   `hf upload-large-folder REPO_ID LOCAL_PATH`：推荐用于可恢复的大目录上传。
*   `hf sync`：在本地目录和存储桶之间同步文件。
*   `hf env` / `hf version`：查看环境和版本详情。

### 认证 (`hf auth`)
*   `login` / `logout`：使用来自 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 的 Token 管理会话。
*   `list` / `switch`：管理并在多个存储的访问 Token 之间切换。
*   `whoami`：识别当前登录的账户。

### 仓库管理 (`hf repos`)
*   `create` / `delete`：创建或永久删除仓库。
*   `duplicate`：将模型、数据集或 Space 克隆到新的 ID。
*   `move`：在命名空间之间转移仓库。
*   `branch` / `tag`：管理类 Git 的引用。
*   `delete-files`：使用模式删除特定文件。

---

## 专门的 Hub 交互

### 数据集与模型
*   **数据集：** `hf datasets list`、`info` 和 `parquet`（列出 parquet URL）。
*   **SQL 查询：** `hf datasets sql SQL` — 通过 DuckDB 对数据集 parquet URL 执行原始 SQL。
*   **模型：** `hf models list` 和 `info`。
*   **论文：** `hf papers list` — 查看每日论文。

### 讨论与拉取请求 (`hf discussions`)
*   管理 Hub 贡献的生命周期：`list`、`create`、`info`、`comment`、`close`、`reopen` 和 `rename`。
*   `diff`：查看 PR 中的更改。
*   `merge`：完成拉取请求。

### 基础设施与计算
*   **端点：** 部署和管理推理端点 (`deploy`、`pause`、`resume`、`scale-to-zero`、`catalog`)。
*   **作业：** 在 HF 基础设施上运行计算任务。包括 `hf jobs uv`（用于运行带有内联依赖项的 Python 脚本）和 `stats`（用于资源监控）。
*   **Spaces：** 管理交互式应用。包括 `dev-mode` 和 `hot-reload`，用于无需完全重启即可热重载 Python 文件。

### 存储与自动化
*   **存储桶：** 完整的类 S3 存储桶管理 (`create`、`cp`、`mv`、`rm`、`sync`)。
*   **缓存：** 使用 `list`、`prune`（移除分离的修订版本）和 `verify`（校验和检查）管理本地存储。
*   **Webhook：** 通过管理 Hub Webhook (`create`、`watch`、`enable`/`disable`) 自动化工作流。
*   **收藏集：** 将 Hub 项目组织到收藏集中 (`add-item`、`update`、`list`)。

---

## 高级用法与技巧

### 全局标志
*   `--format json`：生成机器可读的输出以用于自动化。
*   `-q` / `--quiet`：将输出限制为仅 ID。

### 扩展与技能
*   **扩展：** 使用 `hf extensions install REPO_ID` 通过 GitHub 仓库扩展 CLI 功能。
*   **技能：** 使用 `hf skills add` 管理 AI 助手技能。