---
sidebar_position: 3
title: "常见问题与故障排除"
description: "关于 Hermes Agent 的常见问题及其解决方案"
---

# 常见问题与故障排除

针对最常见问题和故障的快速解答与修复方法。

---

## 常见问题

### Hermes 支持哪些 LLM 提供商？

Hermes Agent 可与任何兼容 OpenAI API 的接口协同工作。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API 密钥访问数百个模型（推荐，灵活性高）
- **Nous Portal** — Nous Research 自家的推理端点
- **OpenAI** — GPT-4o, o1, o3 等
- **Anthropic** — Claude 模型（通过 OpenRouter 或兼容代理）
- **Google** — Gemini 模型（通过 OpenRouter 或兼容代理）
- **z.ai / ZhipuAI** — GLM 模型
- **Kimi / Moonshot AI** — Kimi 模型
- **MiniMax** — 全球和中国区端点
- **本地模型** — 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 的服务器

使用 `hermes model` 命令或编辑 `~/.hermes/.env` 文件来设置您的提供商。所有提供商的配置键请参阅[环境变量](./environment-variables.md)参考。

### 它能在 Windows 上运行吗？

**不能原生运行。** Hermes Agent 需要一个类 Unix 环境。在 Windows 上，请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes。标准安装命令在 WSL2 中完美运行：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 它能在 Android / Termux 上运行吗？

可以 — Hermes 现在为 Android 手机提供了经过测试的 Termux 安装路径。

快速安装：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

关于完整明确的手动步骤、支持的额外功能以及当前限制，请参阅 [Termux 指南](../getting-started/termux.md)。

重要注意事项：完整的 `.[all]` 额外功能目前在 Android 上不可用，因为 `voice` 额外功能依赖于 `faster-whisper` → `ctranslate2`，而 `ctranslate2` 没有发布适用于 Android 的 wheel 包。请改用经过测试的 `.[termux]` 额外功能。

### 我的数据会被发送到别处吗？

API 调用**仅发送到您配置的 LLM 提供商**（例如 OpenRouter、您的本地 Ollama 实例）。Hermes Agent 不收集遥测数据、使用数据或分析数据。您的对话、记忆和技能都本地存储在 `~/.hermes/` 目录中。

### 我可以离线使用吗 / 可以使用本地模型吗？

可以。运行 `hermes model`，选择 **Custom endpoint**，并输入您服务器的 URL：

```bash
hermes model
# 选择：Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 将此值设置为与您服务器的实际上下文窗口匹配
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将端点、提供商和基础 URL 持久化保存在 `config.yaml` 中，因此重启后配置依然有效。如果您的本地服务器只加载了一个模型，`/model custom` 会自动检测它。您也可以在 config.yaml 中设置 `provider: custom` — 它是一个一等提供商，而不是其他任何东西的别名。

这适用于 Ollama、vLLM、llama.cpp 服务器、SGLang、LocalAI 等。详情请参阅[配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户
如果您在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 — Ollama 的 `/api/show` 报告的是模型的*最大*上下文长度，而不是您配置的有效 `num_ctx`。
:::

:::tip 本地模型超时
Hermes 会自动检测本地端点并放宽流式传输超时设置（读取超时从 120 秒提高到 1800 秒，禁用陈旧流检测）。如果您在非常大的上下文上仍然遇到超时，请在您的 `.env` 文件中设置 `HERMES_STREAM_READ_TIMEOUT=1800`。详情请参阅[本地 LLM 指南](../guides/local-llm-on-mac.md#timeouts)。
:::

### 费用是多少？

Hermes Agent 本身是**免费且开源的**（MIT 许可证）。您只需为您选择的 LLM 提供商的 API 使用付费。本地模型完全免费运行。

### 多人可以使用同一个实例吗？

可以。[消息网关](../user-guide/messaging/index.md)允许多个用户通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例交互。访问权限通过允许列表（特定用户 ID）和私信配对（第一个发送消息的用户获得访问权）进行控制。

### 记忆和技能有什么区别？

- **记忆**存储**事实** — Agent 了解的关于您、您的项目和偏好的信息。记忆会根据相关性自动检索。
- **技能**存储**流程** — 如何做某事的逐步说明。当 Agent 遇到类似任务时，会回忆起技能。

两者都会在会话之间持久化。详情请参阅[记忆](../user-guide/features/memory.md)和[技能](../user-guide/features/skills.md)。

### 我可以在自己的 Python 项目中使用它吗？

可以。导入 `AIAgent` 类并以编程方式使用 Hermes：

```python
from run_agent import AIAgent

agent = AIAgent(model="anthropic/claude-opus-4.7")
response = agent.chat("简要解释一下量子计算")
```

完整的 API 用法请参阅 [Python 库指南](../user-guide/features/code-execution.md)。

---

## 故障排除

### 安装问题

#### 安装后出现 `hermes: command not found`

**原因：** 您的 shell 尚未重新加载更新后的 PATH。

**解决方案：**
```bash
# 重新加载您的 shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者启动一个新的终端会话
```

如果仍然不行，请验证安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会将 `~/.local/bin` 添加到您的 PATH 中。如果您使用非标准的 shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::
#### Python 版本过旧

**原因：** Hermes 需要 Python 3.11 或更高版本。

**解决方案：**
```bash
python3 --version   # 检查当前版本

# 安装更新的 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理此问题 — 如果你在手动安装过程中看到此错误，请先升级 Python。

#### 终端命令显示 `node: command not found`（或 `nvm`、`pyenv`、`asdf` 等）

**原因：** Hermes 通过在启动时运行一次 `bash -l` 来构建每个会话的环境快照。Bash 登录 shell 会读取 `/etc/profile`、`~/.bash_profile` 和 `~/.profile`，但**不会 source `~/.bashrc`** — 因此安装在那里的工具（`nvm`、`asdf`、`pyenv`、`cargo`、自定义 `PATH` 导出）对快照不可见。这最常发生在 Hermes 在 systemd 下运行或在没有任何东西预加载交互式 shell 配置文件的极简 shell 中时。

**解决方案：** Hermes 默认会自动 source `~/.bashrc`。如果这还不够 — 例如，你是 zsh 用户，PATH 设置在 `~/.zshrc` 中，或者你从独立文件初始化 `nvm` — 请在 `~/.hermes/config.yaml` 中列出要 source 的额外文件：

```yaml
terminal:
  shell_init_files:
    - ~/.zshrc                     # zsh 用户：将 zsh 管理的 PATH 拉入 bash 快照
    - ~/.nvm/nvm.sh                # 直接初始化 nvm（无论使用何种 shell 都有效）
    - /etc/profile.d/cargo.sh      # 系统范围的 rc 文件
  # 设置此列表时，默认的 ~/.bashrc 自动 source 功能**不会**被添加 —
  # 如果你想要两者，请显式包含它：
  #   - ~/.bashrc
  #   - ~/.zshrc
```

缺失的文件会被静默跳过。Sourcing 在 bash 中执行，因此依赖 zsh 特有语法的文件可能会出错 — 如果担心这一点，请只 source 设置 PATH 的部分（例如直接 source nvm 的 `nvm.sh`），而不是整个 rc 文件。

要禁用自动 source 行为（仅使用严格的登录 shell 语义）：

```yaml
terminal:
  auto_source_bashrc: false
```

#### `uv: command not found`

**原因：** `uv` 包管理器未安装或不在 PATH 中。

**解决方案：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装期间出现权限被拒绝错误

**原因：** 对安装目录的写入权限不足。

**解决方案：**
```bash
# 不要对安装程序使用 sudo — 它会安装到 ~/.local/bin
# 如果你之前用 sudo 安装过，请清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 提供商和模型问题

#### `/model` 只显示一个提供商 / 无法切换提供商

**原因：** `/model`（在聊天会话内部）只能在你**已经配置好**的提供商之间切换。如果你只设置了 OpenRouter，那么 `/model` 就只会显示它。

**解决方案：** 退出你的会话，在终端中使用 `hermes model` 来添加新的提供商：

```bash
# 先退出 Hermes 聊天会话（Ctrl+C 或 /quit）

# 运行完整的提供商设置向导
hermes model

# 这允许你：添加提供商、运行 OAuth、输入 API 密钥、配置端点
```

通过 `hermes model` 添加新提供商后，启动一个新的聊天会话 — `/model` 现在将显示你所有已配置的提供商。

:::tip 快速参考
| 想要... | 使用 |
|-----------|-----|
| 添加新提供商 | `hermes model`（在终端中） |
| 输入/更改 API 密钥 | `hermes model`（在终端中） |
| 在会话中途切换模型 | `/model <名称>`（在会话内部） |
| 切换到不同的已配置提供商 | `/model provider:model`（在会话内部） |
:::

#### API 密钥无效

**原因：** 密钥缺失、已过期、设置不正确或属于错误的提供商。

**解决方案：**
```bash
# 检查你的配置
hermes config show

# 重新配置你的提供商
hermes model

# 或直接设置
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxxxxxxxxx
```

:::warning
确保密钥与提供商匹配。OpenAI 密钥不适用于 OpenRouter，反之亦然。检查 `~/.hermes/.env` 中是否有冲突的条目。
:::

#### 模型不可用 / 找不到模型

**原因：** 模型标识符不正确或你的提供商不提供该模型。

**解决方案：**
```bash
# 列出你的提供商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL anthropic/claude-opus-4.7

# 或按会话指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 速率限制（429 错误）

**原因：** 你已超出提供商的速率限制。

**解决方案：** 稍等片刻再重试。对于持续使用，请考虑：
- 升级你的提供商套餐
- 切换到不同的模型或提供商
- 使用 `hermes chat --provider <替代方案>` 路由到不同的后端

#### 上下文长度超出

**原因：** 对话内容过长，超出了模型的上下文窗口，或者 Hermes 检测到的模型上下文长度有误。

**解决方案：**
```bash
# 压缩当前会话
/compress

# 或启动一个新会话
hermes chat

# 使用具有更大上下文窗口的模型
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果这种情况发生在第一次长对话时，Hermes 可能对你的模型上下文长度检测有误。检查它检测到了什么：

查看 CLI 启动行 — 它会显示检测到的上下文长度（例如，`📊 Context limit: 128000 tokens`）。你也可以在会话中使用 `/usage` 进行检查。

要修复上下文检测，请显式设置它：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 你的模型实际上下文窗口
```

或者对于自定义端点，按模型添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```

有关自动检测如何工作以及所有覆盖选项，请参阅[上下文长度检测](../integrations/providers.md#context-length-detection)。

---

### 终端问题
#### 命令因危险被阻止

**原因：** Hermes 检测到一个可能具有破坏性的命令（例如 `rm -rf`、`DROP TABLE`）。这是一项安全功能。

**解决方案：** 当出现提示时，请检查该命令并输入 `y` 来批准执行。您也可以：
- 要求 Agent 使用更安全的替代方案
- 在[安全文档](../user-guide/security.md)中查看完整的危险模式列表

:::tip
这是预期行为 — Hermes 绝不会静默执行破坏性命令。批准提示会明确显示将要执行的内容。
:::

#### 通过消息网关执行 `sudo` 无效

**原因：** 消息网关运行时没有交互式终端，因此 `sudo` 无法提示输入密码。

**解决方案：**
- 在消息交互中避免使用 `sudo` — 要求 Agent 寻找替代方案
- 如果必须使用 `sudo`，请在 `/etc/sudoers` 中为特定命令配置免密码 sudo
- 或者切换到终端界面执行管理任务：`hermes chat`

#### Docker 后端连接失败

**原因：** Docker 守护进程未运行，或者用户缺少权限。

**解决方案：**
```bash
# 检查 Docker 是否在运行
docker info

# 将您的用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker run hello-world
```

---

### 消息问题

#### Bot 不响应消息

**原因：** Bot 未运行、未授权，或者您的用户不在允许列表中。

**解决方案：**
```bash
# 检查消息网关是否在运行
hermes gateway status

# 启动消息网关
hermes gateway start

# 检查日志中的错误
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息无法送达

**原因：** 网络问题、Bot Token 过期，或平台 Webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 验证您的 Bot Token 是否有效
- 检查消息网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 Webhook 的平台（Slack、WhatsApp），请确保您的服务器可公开访问

#### 允许列表困惑 — 谁可以和 Bot 对话？

**原因：** 授权模式决定了谁可以访问。

**解决方案：**

| 模式 | 工作原理 |
|------|-------------|
| **允许列表** | 只有配置中列出的用户 ID 可以交互 |
| **私信配对** | 第一个在私信中发送消息的用户获得独占访问权 |
| **开放** | 任何人都可以交互（生产环境不推荐） |

在 `~/.hermes/config.yaml` 中您的消息网关设置下进行配置。请参阅[消息文档](../user-guide/messaging/index.md)。

#### 消息网关无法启动

**原因：** 缺少依赖项、端口冲突，或 Token 配置错误。

**解决方案：**
```bash
# 安装消息依赖项
pip install "hermes-agent[telegram]"   # 或 [discord], [slack], [whatsapp]

# 检查端口冲突
lsof -i :8080

# 验证配置
hermes config show
```

#### WSL：消息网关持续断开连接或 `hermes gateway start` 失败

**原因：** WSL 的 systemd 支持不可靠。许多 WSL2 安装没有启用 systemd，即使启用了，服务也可能无法在 WSL 重启或 Windows 空闲关机后存活。

**解决方案：** 使用前台模式代替 systemd 服务：

```bash
# 选项 1：直接前台运行（最简单）
hermes gateway run

# 选项 2：通过 tmux 持久化（终端关闭后仍存活）
tmux new -s hermes 'hermes gateway run'
# 稍后重新连接：tmux attach -t hermes

# 选项 3：通过 nohup 后台运行
nohup hermes gateway run > ~/.hermes/logs/gateway.log 2>&1 &
```

如果您仍想尝试 systemd，请确保它已启用：

1. 打开 `/etc/wsl.conf`（如果不存在则创建）
2. 添加：
   ```ini
   [boot]
   systemd=true
   ```
3. 在 PowerShell 中执行：`wsl --shutdown`
4. 重新打开您的 WSL 终端
5. 验证：`systemctl is-system-running` 应显示 "running" 或 "degraded"

:::tip Windows 启动时自动启动
要实现可靠的自动启动，请使用 Windows 任务计划程序在登录时启动 WSL + 消息网关：
1. 创建一个任务，运行 `wsl -d Ubuntu -- bash -lc 'hermes gateway run'`
2. 将其设置为在用户登录时触发
:::

#### macOS：消息网关找不到 Node.js / ffmpeg / 其他工具

**原因：** launchd 服务继承了一个最小的 PATH（`/usr/bin:/bin:/usr/sbin:/sbin`），其中不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常会破坏 WhatsApp 桥接（`node not found`）或语音转录（`ffmpeg not found`）。

**解决方案：** 消息网关在您运行 `hermes gateway install` 时会捕获您的 shell PATH。如果您在设置消息网关之后安装了工具，请重新运行安装命令以捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照您当前的 PATH
hermes gateway start      # 检测更新后的 plist 并重新加载
```

您可以验证 plist 是否具有正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

### 性能问题

#### 响应缓慢

**原因：** 大型模型、遥远的 API 服务器，或包含大量工具的系统提示词过于繁重。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少活动的工具集：`hermes chat -t "terminal"`
- 检查您到提供商的网络延迟
- 对于本地模型，请确保您有足够的 GPU VRAM

#### Token 使用量过高

**原因：** 长对话、冗长的系统提示词，或许多工具调用累积了上下文。

**解决方案：**
```bash
# 压缩对话以减少 Token 使用
/compress

# 检查会话 Token 使用情况
/usage
```

:::tip
在长会话期间定期使用 `/compress`。它会总结对话历史，在保留上下文的同时显著减少 Token 使用量。
:::

#### 会话变得过长

**原因：** 长时间的对话累积了消息和工具输出，接近上下文限制。

**解决方案：**
```bash
# 压缩当前会话（保留关键上下文）
/compress

# 启动一个引用旧会话的新会话
hermes chat

# 如果需要，稍后恢复特定会话
hermes chat --continue
```

---

### MCP 问题

#### MCP 服务器连接失败

**原因：** 找不到服务器二进制文件、命令路径错误，或缺少运行时环境。
**解决方案：**
```bash
# 确保 MCP 依赖已安装（标准安装已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

# 对于基于 npm 的服务器，确保 Node.js 可用
node --version
npx --version

# 手动测试服务器
npx -y @modelcontextprotocol/server-filesystem /tmp
```

验证你的 `~/.hermes/config.yaml` MCP 配置：
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
```

#### MCP 服务器工具未显示

**原因：** 服务器已启动但工具发现失败，工具被配置过滤掉，或者服务器不支持你期望的 MCP 能力。

**解决方案：**
- 检查消息网关/Agent 日志中的 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 检查该服务器下的任何 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 请记住，资源/提示词实用工具仅在会话实际支持这些能力时才会注册
- 更改配置后使用 `/reload-mcp`

```bash
# 验证 MCP 服务器已配置
hermes config show | grep -A 12 mcp_servers

# 更改配置后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP (Model Context Protocol)](/docs/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/docs/guides/use-mcp-with-hermes)
- [MCP 配置参考](/docs/reference/mcp-config-reference)

#### MCP 超时错误

**原因：** MCP 服务器响应时间过长，或者执行过程中崩溃。

**解决方案：**
- 如果支持，请在 MCP 服务器配置中增加超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，检查网络连接

:::warning
如果 MCP 服务器在请求中途崩溃，Hermes 将报告超时。请检查服务器自身的日志（不仅仅是 Hermes 日志）以诊断根本原因。
:::

---

## 配置文件

### 配置文件与仅设置 HERMES_HOME 有何不同？

配置文件是 `HERMES_HOME` 之上的一个管理层。你*可以*在每次命令前手动设置 `HERMES_HOME=/some/path`，但配置文件为你处理了所有底层工作：创建目录结构、生成 shell 别名（`hermes-work`）、在 `~/.hermes/active_profile` 中跟踪活动配置文件，以及自动在所有配置文件间同步技能更新。它们还与标签页补全集成，因此你无需记住路径。

### 两个配置文件可以共享同一个机器人 Token 吗？

不可以。每个消息平台（Telegram、Discord 等）都需要独占访问一个机器人 Token。如果两个配置文件尝试同时使用同一个 Token，第二个消息网关将无法连接。请为每个配置文件创建一个单独的机器人——对于 Telegram，请与 [@BotFather](https://t.me/BotFather) 对话以创建额外的机器人。

### 配置文件共享记忆或会话吗？

不共享。每个配置文件都有自己的记忆存储、会话数据库和技能目录。它们是完全隔离的。如果你想使用现有的记忆和会话创建一个新的配置文件，请使用 `hermes profile create newname --clone-all` 从当前配置文件复制所有内容。

### 运行 `hermes update` 时会发生什么？

`hermes update` 会拉取最新代码并重新安装依赖项**一次**（不是每个配置文件）。然后它会自动将更新后的技能同步到所有配置文件。你只需要运行一次 `hermes update`——它会覆盖机器上的每个配置文件。

### 我可以将配置文件移动到另一台机器吗？

可以。将配置文件导出为可移植的归档文件，然后在另一台机器上导入：

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后：
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件将包含导出时的所有配置、记忆、会话和技能。如果新机器的设置不同，你可能需要更新路径或重新向提供商进行身份验证。

### 我可以运行多少个配置文件？

没有硬性限制。每个配置文件只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及你的系统可以处理多少个并发消息网关（每个消息网关都是一个轻量级的 Python 进程）。运行数十个配置文件是可以的；每个空闲的配置文件不使用任何资源。

---

## 工作流与模式

### 为不同任务使用不同模型（多模型工作流）

**场景：** 你使用 GPT-5.4 作为日常主力，但 Gemini 或 Grok 能写出更好的社交媒体内容。每次手动切换模型很繁琐。

**解决方案：委派配置。** Hermes 可以自动将子 Agent 路由到不同的模型。在 `~/.hermes/config.yaml` 中设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # 子 Agent 使用此模型
  provider: "openrouter"                    # 子 Agent 的提供商
```

现在，当你告诉 Hermes“为我写一篇关于 X 的 Twitter 帖子”并且它生成了一个 `delegate_task` 子 Agent 时，该子 Agent 将在 Gemini 上运行，而不是你的主模型。你的主要对话仍保持在 GPT-5.4 上。

你也可以在提示词中明确说明：*“委派一个任务来撰写关于我们产品发布的社交媒体帖子。使用你的子 Agent 进行实际写作。”* Agent 将使用 `delegate_task`，它会自动获取委派配置。

对于无需委派的一次性模型切换，请在 CLI 中使用 `/model`：

```bash
/model google/gemini-3-flash-preview    # 为此会话切换
# ... 撰写你的内容 ...
/model openai/gpt-5.4                   # 切换回来
```

有关委派工作原理的更多信息，请参阅 [子 Agent 委派](../user-guide/features/delegation.md)。

### 在一个 WhatsApp 号码上运行多个 Agent（按聊天绑定）

**场景：** 在 OpenClaw 中，你有多个独立的 Agent 绑定到特定的 WhatsApp 聊天——一个用于家庭购物清单群组，另一个用于你的私人聊天。Hermes 能做到这一点吗？

**当前限制：** Hermes 的每个配置文件都需要自己的 WhatsApp 号码/会话。你无法将多个配置文件绑定到同一个 WhatsApp 号码上的不同聊天——WhatsApp 桥接器 (Baileys) 每个号码使用一个经过身份验证的会话。
**变通方案：**

1. **使用单一配置文件配合人格切换。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令来按聊天改变行为。Agent 能看到自己在哪个聊天中，并据此调整。

2. **为特定任务使用定时任务。** 对于购物清单跟踪器，可以设置一个定时任务来监控特定的聊天并管理清单——无需单独的 Agent。

3. **使用独立的号码。** 如果你需要真正独立的 Agent，可以为每个配置文件配备自己的 WhatsApp 号码。像 Google Voice 这样的服务提供的虚拟号码可用于此目的。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按聊天绑定——每个 Telegram 群组或 Discord 频道都有自己的会话，并且你可以在同一账户上运行多个机器人令牌（每个配置文件一个）。

更多详情请参阅[配置文件](../user-guide/profiles.md)和[WhatsApp 设置](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 中显示的内容（隐藏日志和推理过程）

**场景：** 你在 Telegram 中看到了消息网关执行日志、Hermes 的推理过程和工具调用详情，而不仅仅是最终输出。

**解决方案：** `config.yaml` 中的 `display.tool_progress` 设置控制显示多少工具活动：

```yaml
display:
  tool_progress: "off"   # 选项：off, new, all, verbose
```

- **`off`** — 仅显示最终响应。不显示工具调用、推理过程或日志。
- **`new`** — 显示新发生的工具调用（简短的单行信息）。
- **`all`** — 显示所有工具活动，包括结果。
- **`verbose`** — 完整详情，包括工具参数和输出。

对于消息平台，通常需要设置为 `off` 或 `new`。编辑 `config.yaml` 后，重启消息网关以使更改生效。

你也可以通过 `/verbose` 命令（如果启用）按会话切换此设置：

```yaml
display:
  tool_progress_command: true   # 在消息网关中启用 /verbose 命令
```

### 在 Telegram 上管理技能（斜杠命令限制）

**场景：** Telegram 有 100 个斜杠命令的限制，而你的技能数量超过了这个限制。你想在 Telegram 上禁用不需要的技能，但 `hermes skills config` 的设置似乎不生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用技能。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用的技能
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 telegram 上禁用的技能
```

更改此设置后，**重启消息网关**（`hermes gateway restart` 或终止并重新启动）。Telegram 机器人命令菜单会在启动时重建。

:::tip
在 Telegram 菜单中，描述过长的技能会被截断为 40 个字符，以保持在有效载荷大小限制内。如果技能没有出现，可能是总有效载荷大小问题，而不是 100 个命令的数量限制——禁用未使用的技能对两者都有帮助。
:::

### 共享线程会话（多用户，单一对话）

**场景：** 你有一个 Telegram 或 Discord 线程，其中有多人提及机器人。你希望该线程中所有的提及都属于一个共享的对话，而不是每个用户独立的会话。

**当前行为：** Hermes 在大多数平台上按用户 ID 创建会话，因此每个人都有自己的对话上下文。这是出于隐私和上下文隔离的设计。

**变通方案：**

1. **使用 Slack。** Slack 会话是按线程（thread）而不是按用户（user）创建的。同一线程中的多个用户共享一个对话——这正是你描述的行为。这是最自然的匹配方案。

2. **使用与单一用户的群聊。** 如果指定一个人作为“操作员”来转达问题，会话将保持统一。其他人可以阅读。

3. **使用 Discord 频道。** Discord 会话是按频道（channel）创建的，因此同一频道中的所有用户共享上下文。为共享对话使用一个专用频道。

### 将 Hermes 导出到另一台机器

**场景：** 你在一台机器上构建了技能、定时任务和记忆，现在想把所有内容迁移到一台新的专用 Linux 机器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

2. 复制整个 `~/.hermes/` 目录，**但排除** `hermes-agent` 子目录（那是代码仓库——新安装有自己的版本）：
   ```bash
   # 在源机器上
   rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
   ```

   或者使用配置文件导出/导入：
   ```bash
   # 在源机器上
   hermes profile export default ./hermes-backup.tar.gz

   # 在目标机器上
   hermes profile import ./hermes-backup.tar.gz default
   ```

3. 在新机器上，运行 `hermes setup` 以验证 API 密钥和提供商配置是否正常工作。重新验证任何消息平台（尤其是使用二维码配对的 WhatsApp）。

`~/.hermes/` 目录包含所有内容：`config.yaml`、`.env`、`SOUL.md`、`memories/`、`skills/`、`state.db`（会话）、`cron/` 以及任何自定义插件。代码本身位于 `~/.hermes/hermes-agent/` 中，是全新安装的。

### 安装后重新加载 shell 时权限被拒绝

**场景：** 运行 Hermes 安装程序后，`source ~/.zshrc` 出现权限被拒绝的错误。

**原因：** 这通常发生在 `~/.zshrc`（或 `~/.bashrc`）文件权限不正确，或者安装程序无法正常写入时。这不是 Hermes 特有的问题——而是 shell 配置的权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如果需要，修复权限（应为 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或者直接打开一个新的终端窗口——它会自动获取 PATH 更改
```

如果安装程序添加了 PATH 行但权限错误，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 首次运行 Agent 时出现错误 400

**场景：** 设置顺利完成，但首次尝试聊天时失败，并出现 HTTP 400 错误。
**原因：** 通常是模型名称不匹配——配置的模型在您的提供商处不存在，或者 API 密钥无权访问该模型。

**解决方案：**
```bash
# 检查配置了哪些模型和提供商
hermes config show | head -20

# 重新运行模型选择
hermes model

# 或者使用已知可用的模型进行测试
hermes chat -q "hello" --model anthropic/claude-opus-4.7
```

如果使用 OpenRouter，请确保您的 API 密钥有额度。来自 OpenRouter 的 400 错误通常意味着该模型需要付费计划，或者模型 ID 有拼写错误。

---

## 仍然无法解决？

如果此处未涵盖您的问题：

1.  **搜索现有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2.  **询问社区：** [Nous Research Discord](https://discord.gg/nousresearch)
3.  **提交错误报告：** 请包含您的操作系统、Python 版本 (`python3 --version`)、Hermes 版本 (`hermes --version`) 以及完整的错误信息