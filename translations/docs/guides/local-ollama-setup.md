---
sidebar_position: 9
title: "使用 Ollama 本地运行 Hermes — 零 API 成本"
description: "使用 Ollama 和 Gemma 4 等开源模型，在您自己的机器上完全本地运行 Hermes Agent 的分步指南，无需云 API 密钥或付费订阅"
---

# 使用 Ollama 本地运行 Hermes — 零 API 成本

## 问题所在

云 LLM API 按 Token 收费。一次重度编码会话可能花费 5-20 美元。对于个人项目、学习或隐私敏感的工作，这会累积起来 — 而且您将每次对话都发送给了第三方。

## 本指南解决的问题

您将设置完全在您自己的硬件上运行的 Hermes Agent，使用 [Ollama](https://ollama.com) 作为模型后端。无需 API 密钥，无需订阅，数据不会离开您的机器。配置完成后，Hermes 的工作方式与使用 OpenRouter 或 Anthropic 时完全相同 — 终端命令、文件编辑、网页浏览、委派 — 但模型在本地运行。

完成后，您将拥有：

- 提供一种或多种开源模型的 Ollama
- 将 Hermes 连接到 Ollama 作为自定义端点
- 一个可以编辑文件、运行命令和浏览网页的本地工作 Agent
- 可选：一个完全由您自己的硬件驱动的 Telegram/Discord 机器人

## 所需条件

| 组件 | 最低要求 | 推荐配置 |
|-----------|---------|-------------|
| **内存** | 8 GB (适用于 3B 模型) | 32+ GB (适用于 27B+ 模型) |
| **存储空间** | 5 GB 可用空间 | 30+ GB (适用于多个模型) |
| **CPU** | 4 核 | 8+ 核 (AMD EPYC, Ryzen, Intel Xeon) |
| **GPU** | 非必需 | 具有 8+ GB 显存的 NVIDIA GPU 可显著提升速度 |

:::tip 仅 CPU 也可运行，但响应会较慢
Ollama 可在仅 CPU 的服务器上运行。现代 8 核 CPU 上的 9B 模型提供约 10 tokens/秒。CPU 上的 31B 模型更慢（约 2–5 tokens/秒）— 每次响应需要 30–120 秒，但可以工作。GPU 能显著改善此情况。对于仅 CPU 的设置，请在配置中增加 API 超时时间：

```yaml
agent:
  api_timeout: 1800   # 30 分钟 — 为慢速本地模型留出充裕时间
```
:::

## 步骤 1：安装 Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

验证其是否正在运行：

```bash
ollama --version
curl http://localhost:11434/api/tags   # 应返回 {"models":[]}
```

## 步骤 2：拉取模型

根据您的硬件选择：

| 模型 | 磁盘占用 | 所需内存 | 工具调用 | 最佳用途 |
|-------|-------------|------------|:------------:|----------|
| `gemma4:31b` | ~20 GB | 24+ GB | 是 | 最佳质量 — 强大的工具使用和推理能力 |
| `gemma2:27b` | ~16 GB | 20+ GB | 否 | 对话任务，无工具使用 |
| `gemma2:9b` | ~5 GB | 8+ GB | 否 | 快速聊天、问答 — 无法调用工具 |
| `llama3.2:3b` | ~2 GB | 4+ GB | 否 | 仅限轻量级快速回答 |

:::warning 工具调用很重要
Hermes 是一个**代理式**助手 — 它通过工具调用来编辑文件、运行命令和浏览网页。不支持工具调用的模型只能聊天；它们无法执行操作。要获得完整的 Hermes 体验，请使用支持工具的模型（如 `gemma4:31b`）。
:::

拉取您选择的模型：

```bash
ollama pull gemma4:31b
```

:::info 多个模型
您可以拉取多个模型，并在 Hermes 内部使用 `/model` 命令在它们之间切换。Ollama 会根据需求将活动模型加载到内存中，并自动卸载空闲模型。
:::

验证模型是否工作：

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:31b",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

您应该能看到一个包含模型回复的 JSON 响应。

## 步骤 3：配置 Hermes

运行 Hermes 设置向导：

```bash
hermes setup
```

当提示选择提供商时，选择 **自定义端点** 并输入：

- **基础 URL:** `http://localhost:11434/v1`
- **API 密钥:** 留空或输入 `no-key` (Ollama 不需要)
- **模型:** `gemma4:31b` (或您拉取的其他模型)

或者，直接编辑 `~/.hermes/config.yaml`：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"
```

## 步骤 4：开始使用 Hermes

```bash
hermes
```

就是这样。您现在正在运行一个完全本地的 Agent。试试看：

```
您：列出此目录中的所有 Python 文件并统计每个文件的行数

您：读取 README.md 并总结这个项目是做什么的

您：创建一个获取胡志明市天气的 Python 脚本
```

Hermes 将使用终端工具、文件操作和您的本地模型 — 无需云调用。

## 步骤 5：为您的任务选择合适的模型

并非每个任务都需要最大的模型。以下是一个实用指南：

| 任务 | 推荐模型 | 原因 |
|------|-------------------|-----|
| 文件编辑、代码、终端命令 | `gemma4:31b` | 唯一具有可靠工具调用能力的模型 |
| 快速问答（无需工具使用） | `gemma2:9b` | 对话任务响应快 |
| 轻量级聊天 | `llama3.2:3b` | 最快，但能力非常有限 |

:::note
对于完整的代理式工作（编辑文件、运行命令、浏览网页），`gemma4:31b` 是目前支持工具调用的最佳本地选项。请查看 [Ollama 的模型库](https://ollama.com/library) 以获取更新的模型 — 工具调用支持正在迅速扩展。
:::

在会话中动态切换模型：

```
/model gemma2:9b
```

## 步骤 6：优化速度

### 增加 Ollama 的上下文窗口

默认情况下，Ollama 使用 2048 个 Token 的上下文。对于代理式工作（工具调用、长对话），您需要更多：

```bash
# 创建一个扩展上下文的 Modelfile
cat > /tmp/Modelfile << 'EOF'
FROM gemma4:31b
PARAMETER num_ctx 16384
EOF

ollama create gemma4-16k -f /tmp/Modelfile
```

然后将您的 Hermes 配置更新为使用 `gemma4-16k` 作为模型名称。

### 保持模型加载状态

默认情况下，Ollama 在 5 分钟不活动后卸载模型。对于持久化的消息网关机器人，请保持其加载状态：

```bash
# 将 keep-alive 设置为 24 小时
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma4:31b", "keep_alive": "24h"}'
```

或者在 Ollama 的环境变量中全局设置：

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_KEEP_ALIVE=24h"
```

### 使用 GPU 卸载（如果可用）

如果您有 NVIDIA GPU，Ollama 会自动将层卸载到 GPU。使用以下命令检查：

```bash
ollama ps   # 显示哪个模型已加载以及卸载到 GPU 的层数
```

对于 12 GB GPU 上的 31B 模型，您将获得部分卸载（约 40 层在 GPU 上，其余在 CPU 上），这仍然能显著提升速度。

## 步骤 7：作为消息网关机器人运行（可选）

一旦 Hermes 在 CLI 中本地工作，您可以将其作为 Telegram 或 Discord 机器人公开 — 仍然完全在您的硬件上运行。

### Telegram

1. 通过 [@BotFather](https://t.me/BotFather) 创建一个机器人并获取 Token
2. 添加到您的 `~/.hermes/config.yaml`：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

platforms:
  telegram:
    enabled: true
    token: "YOUR_TELEGRAM_BOT_TOKEN"
```

3. 启动消息网关：

```bash
hermes gateway
```

现在在 Telegram 上给您的机器人发消息 — 它将使用您的本地模型进行响应。

### Discord

1. 在 [discord.com/developers](https://discord.com/developers/applications) 创建一个 Discord 应用程序
2. 添加到配置中：

```yaml
platforms:
  discord:
    enabled: true
    token: "YOUR_DISCORD_BOT_TOKEN"
```

3. 启动：`hermes gateway`

## 步骤 8：设置备用方案（可选）

本地模型可能难以处理复杂任务。设置一个云备用方案，仅在本地模型失败时激活：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

这样，您 90% 的使用是免费的（本地），只有困难的任务才会使用付费 API。

## 故障排除

### 启动时出现 "Connection refused"

Ollama 没有运行。启动它：

```bash
sudo systemctl start ollama
# 或
ollama serve
```

### 响应缓慢

- **检查模型大小与内存：** 如果您的模型所需内存超过可用内存，它会交换到磁盘。使用更小的模型或增加内存。
- **检查 `ollama ps`：** 如果没有 GPU 层被卸载，响应受 CPU 限制。这对于仅 CPU 的服务器是正常的。
- **减少上下文：** 大型对话会减慢推理速度。定期使用 `/compress`，或在配置中设置较低的压缩阈值。

### 模型不遵循工具调用

较小的模型（3B, 7B）有时会忽略工具调用指令，并生成纯文本而不是结构化函数调用。解决方案：

- **使用更大的模型** — `gemma4:31b` 或 `gemma2:27b` 处理工具调用的能力比 3B/7B 模型好得多。
- **Hermes 具有自动修复功能** — 它会检测格式错误的工具调用并尝试自动修复它们。
- **设置备用方案** — 如果本地模型失败 3 次，Hermes 会回退到云提供商。

### 上下文窗口错误

默认的 Ollama 上下文（2048 个 Token）对于代理式工作来说太小了。请参阅 [步骤 6](#step-6-optimize-for-speed) 来增加它。

## 成本对比

以下是在典型编码会话（约 100K 输入 Token，约 20K 输出 Token）中，本地运行与云 API 相比节省的成本：

| 提供商 | 每次会话成本 | 每月成本（每日使用） |
|----------|-----------------|---------------------|
| Anthropic Claude Sonnet | ~$0.80 | ~$24 |
| OpenRouter (GPT-4o) | ~$0.60 | ~$18 |
| **Ollama (本地)** | **$0.00** | **$0.00** |

您唯一的成本是电费 — 根据硬件不同，每次会话大约 $0.01–0.05。

## 本地运行效果良好的方面

- **文件编辑和代码生成** — 9B+ 模型处理得很好
- **终端命令** — Hermes 包装命令、运行命令、读取输出，与模型无关
- **网页浏览** — 浏览器工具负责获取；模型只解释结果
- **定时任务和计划任务** — 与云设置工作方式相同
- **多平台消息网关** — Telegram、Discord、Slack 都能与本地模型配合工作

## 云模型表现更好的方面

- **非常复杂的多步推理** — 70B+ 或 Claude Opus 等云模型明显更好
- **长上下文窗口** — 云模型提供 100K–1M Token；本地模型通常为 8K–32K
- **大型响应的速度** — 对于长文本生成，云推理比仅 CPU 的本地推理更快

最佳方案：日常任务使用本地模型，困难任务设置云备用方案。