---
sidebar_position: 3
---

# 配置文件分发：分享完整的 Agent

**配置文件分发**将一个完整的 Hermes Agent —— 包括人格、技能、定时任务、MCP 连接、配置 —— 打包成一个 git 仓库。任何能访问该仓库的人都可以通过一条命令安装整个 Agent，就地更新，并保持他们自己的记忆、会话和 API 密钥不变。

如果说[配置文件](./profiles.md)是本地的 Agent，那么分发就是该 Agent 的可分享版本。

## 这意味着什么

在分发功能出现之前，分享一个 Hermes Agent 意味着需要发送给对方：

1. 你的 SOUL.md
2. 需要安装的技能列表
3. 你的 config.yaml（不含密钥）
4. 你所连接的 MCP 服务器的描述
5. 你设置的任何定时任务
6. 设置哪些环境变量的说明

……并希望他们能正确组装。每次版本更新或错误修复都意味着重复这个过程。

有了分发功能，所有这些都存在于一个 git 仓库中：

```
my-research-agent/
├── distribution.yaml    # 清单：名称、版本、环境变量要求
├── SOUL.md              # Agent 的人格 / 系统提示词
├── config.yaml          # 模型、温度、推理、工具默认值
├── skills/              # 随 Agent 捆绑的技能
├── cron/                # Agent 运行的定时任务
└── mcp.json             # Agent 连接的 MCP 服务器
```

接收者运行：

```bash
hermes profile install github.com/you/my-research-agent --alias
```

……他们现在就拥有了整个 Agent。他们填写自己的 API 密钥（`.env.EXAMPLE` → `.env`），然后就可以运行 `my-research-agent chat` 或通过 Telegram / Discord / Slack / 任何消息网关平台来使用它。当你推送新版本时，他们运行 `hermes profile update my-research-agent` 来拉取你的更改 —— 他们的记忆和会话保持不变。

## 为什么选择 git？

我们考虑过 tarball、HTTP 存档、自定义格式。但都不如 git：

- **对作者来说零构建步骤。** 推送到 GitHub；用户安装。没有“打包这个、上传那个、更新索引”的循环。
- **标签、分支和提交本身就是版本控制系统。** 推送一个标签对我们来说，就相当于其他工具的“打包 + 上传发布版”。
- **更新就是一次拉取。** 而不是重新下载整个存档。
- **透明。** 用户可以浏览仓库，阅读版本间的差异，针对它提交问题，或者 fork 它来自定义。
- **私有仓库免费可用。** SSH 密钥、`git credential` 助手、GitHub CLI 存储的凭证 —— 你的终端已经设置好的任何认证方式都能透明地应用。
- **可复现性就是一个提交 SHA。** 这和 pip、npm 记录的一样。

代价是：接收者需要安装 git。在 2026 年任何运行 Hermes 的机器上，这已经是事实。

## 何时应该使用分发？

适合的场景：

- **你正在与团队或社区分享一个专门的 Agent** —— 合规监控员、代码审查员、研究助手、客户支持机器人。
- **你将同一个 Agent 部署到多台机器**，并且不想每次都手动复制文件。
- **你正在迭代一个 Agent**，并希望接收者通过一条命令就能获取新版本。
- **你正在将 Agent 构建成一个产品** —— 包含预设的默认值、精选的技能、调优的提示词 —— 其他人可以将其作为起点。

不适合的场景：

- **你只是想在自己的机器上备份一个配置文件。** 使用 [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) —— 这些命令就是为此设计的。
- **你想与 Agent 一起分享 API 密钥。** `auth.json` 和 `.env` 被特意排除在分发之外。每个安装者都使用自己的凭证。
- **你想分享记忆 / 会话 / 对话历史。** 这些是用户数据，不是分发内容。永远不会被分发。

## 生命周期：从作者到安装者再到更新

以下是完整的端到端流程。选择你关心的那一侧。

---

## 对于作者：发布分发

### 步骤 1 —— 从一个可用的配置文件开始

像构建其他配置文件一样构建和完善 Agent：

```bash
hermes profile create research-bot
research-bot setup                    # 配置模型、API 密钥
# 编辑 ~/.hermes/profiles/research-bot/SOUL.md
# 安装技能、连接 MCP 服务器、安排定时任务等。
research-bot chat                     # 亲自测试直到感觉合适
```

### 步骤 2 —— 添加 `distribution.yaml`

创建 `~/.hermes/profiles/research-bot/distribution.yaml`：

```yaml
name: research-bot
version: 1.0.0
description: "具备 arXiv 和网络工具的自研研究助手"
hermes_requires: ">=0.12.0"
author: "你的名字"
license: "MIT"

# 告诉安装者 Agent 需要哪些环境变量。这些会与安装者的 shell 和现有的 .env 文件进行比对，
# 这样他们就不会被已经配置好的密钥所困扰。
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API 密钥（用于模型访问）"
    required: true
  - name: SERPAPI_KEY
    description: "用于网络搜索的 SerpAPI 密钥"
    required: false
    default: ""
```

这就是整个清单。除了 `name` 之外，每个字段都有合理的默认值。

### 步骤 3 —— 推送到 git 仓库

```bash
cd ~/.hermes/profiles/research-bot
git init
git add .
git commit -m "v1.0.0"
git remote add origin git@github.com:you/research-bot.git
git tag v1.0.0
git push -u origin main --tags
```

现在这个仓库就是一个分发版了。任何有访问权限的人都可以安装它。

:::note
git 仓库包含**配置文件目录中的所有内容，除了那些已经被排除在分发之外的东西**：`auth.json`、`.env`、`memories/`、`sessions/`、`state.db*`、`logs/`、`workspace/`、`*_cache/`、`local/`。这些会留在你的机器上。如果你想排除额外的路径，也可以添加一个 `.gitignore`。
:::

### 步骤 4 —— 为版本发布打标签

每次 Agent 达到一个稳定点时，更新版本号并打标签：

```bash
# 编辑 distribution.yaml: version: 1.1.0
git add distribution.yaml SOUL.md skills/
git commit -m "v1.1.0: 更精确的研究 SOUL，添加 arxiv 技能"
git tag v1.1.0
git push --tags
```
运行 `hermes profile update research-bot` 的接收者将拉取最新版本。

### 仓库结构

一个完整的已发布发行版：

```
research-bot/
├── distribution.yaml            # 必需
├── SOUL.md                      # 强烈推荐
├── config.yaml                  # 模型、提供商、工具默认值
├── mcp.json                     # MCP 服务器连接
├── skills/
│   ├── arxiv-search/SKILL.md
│   ├── paper-summarization/SKILL.md
│   └── citation-lookup/SKILL.md
├── cron/
│   └── weekly-digest.json       # 定时任务
└── README.md                    # 面向用户的描述（可选）
```

### 发行版所有 vs 用户所有

当安装者更新到新版本时，有些内容会被替换（作者领域），有些内容则保持不变（安装者领域）。默认情况如下：

| 类别 | 路径 | 更新时 |
|---|---|---|
| **发行版所有** | `SOUL.md`, `config.yaml`, `mcp.json`, `skills/`, `cron/`, `distribution.yaml` | 从新克隆的仓库中替换 |
| **配置覆盖** | `config.yaml` | 默认情况下实际会被保留 —— 安装者可能已调整模型或提供商。更新时传递 `--force-config` 以重置。 |
| **用户所有** | `memories/`, `sessions/`, `state.db*`, `auth.json`, `.env`, `logs/`, `workspace/`, `plans/`, `home/`, `*_cache/`, `local/` | 从不触碰 |

你可以在清单中覆盖发行版所有的列表：

```yaml
distribution_owned:
  - SOUL.md
  - skills/research/            # 仅我的研究技能；其他已安装的技能保留
  - cron/digest.json
```

当省略时，应用上述默认值 —— 这也是大多数发行版想要的。

---

## 对于安装者：使用发行版

### 安装

```bash
hermes profile install github.com/you/research-bot --alias
```

会发生什么：

1.  将仓库克隆到一个临时目录。
2.  读取 `distribution.yaml`，向你展示清单（名称、版本、描述、作者、必需的环境变量）。
3.  针对你的 shell 环境和目标配置文件的现有 `.env` 检查每个必需的环境变量。将每个标记为 `✓ 已设置` 或 `需要设置`，以便你确切知道需要配置什么。
4.  请求确认。传递 `-y` / `--yes` 以跳过。
5.  将发行版所有的文件复制到 `~/.hermes/profiles/research-bot/`（或清单的 `name` 解析到的任何位置）。
6.  写入 `.env.EXAMPLE`，其中注释掉了必需的键 —— 复制到 `.env` 并填写。
7.  使用 `--alias` 时，创建一个包装器，以便你可以直接运行 `research-bot chat`。

### 源类型

任何 Git URL 都有效：

```bash
# GitHub 简写
hermes profile install github.com/you/research-bot

# 完整 HTTPS
hermes profile install https://github.com/you/research-bot.git

# SSH
hermes profile install git@github.com:you/research-bot.git

# 自托管、GitLab、Gitea、Forgejo —— 任何 Git 主机
hermes profile install https://git.example.com/team/research-bot.git

# 使用你配置的 git 认证的私有仓库
hermes profile install git@github.com:your-org/internal-bot.git

# 开发期间的本地目录（无需 git push）
hermes profile install ~/my-profile-in-progress/
```

### 覆盖配置文件名称

两个用户希望同一发行版使用不同的配置文件名称：

```bash
# Alice
hermes profile install github.com/acme/support-bot --name support-us --alias
# Bob (同一发行版，不同的本地名称)
hermes profile install github.com/acme/support-bot --name support-eu --alias
```

### 填写环境变量

安装后，Agent 的配置文件包含一个 `.env.EXAMPLE`：

```
# 此 Hermes 发行版所需的环境变量。
# 复制到 `.env` 并在运行前填写你自己的值。

# OpenAI API 密钥（用于模型访问）
# (必需)
OPENAI_API_KEY=

# 用于网络搜索的 SerpAPI 密钥
# (可选)
# SERPAPI_KEY=
```

复制它：

```bash
cp ~/.hermes/profiles/research-bot/.env.EXAMPLE ~/.hermes/profiles/research-bot/.env
# 编辑 .env，粘贴你的真实密钥
```

在安装过程中，已在你 shell 环境中设置的必需键（例如，在你的 `~/.zshrc` 中导出的 `OPENAI_API_KEY`）会被标记为 `✓ 已设置` —— 你无需在 `.env` 中重复它们。

### 检查你安装的内容

```bash
hermes profile info research-bot
```

显示：

```
发行版: research-bot
版本:      1.0.0
描述:  具有 arXiv 和网络工具的自主研究助手
作者:      Your Name
要求:     Hermes >=0.12.0
源:       https://github.com/you/research-bot
安装时间:    2026-05-08T17:04:32+00:00

环境变量:
  OPENAI_API_KEY (必需) — OpenAI API 密钥（用于模型访问）
  SERPAPI_KEY (可选) — 用于网络搜索的 SerpAPI 密钥
```

`hermes profile list` 还会显示一个 `发行版` 列，以便一目了然地查看你的哪些配置文件来自仓库，哪些是你手动构建的：

```
 配置文件         模型                       消息网关      别名        发行版
 ───────────────    ───────────────────────────    ───────────    ───────────    ────────────────────
 ◆default         claude-sonnet-4              已停止      —            —
  coder           gpt-5                        已停止      coder        —
  research-bot    claude-opus-4                已停止      research-bot research-bot@1.0.0
  telemetry       claude-sonnet-4              运行中      telemetry    telemetry@2.3.1
```

### 更新

```bash
hermes profile update research-bot
```

会发生什么：

1.  从记录的源 URL 重新克隆仓库。
2.  替换发行版所有的文件（SOUL、技能、cron、mcp.json）。
3.  **保留** 你的 `config.yaml` —— 你可能已经调整了模型、温度或其他设置。传递 `--force-config` 以覆盖。
4.  **从不触碰** 用户数据：记忆、会话、认证、`.env`、日志、状态。

无需重新下载整个存档。不会覆盖你对配置的本地更改。不会删除你的对话历史记录。

### 移除

```bash
hermes profile delete research-bot
```

删除提示会在要求你确认之前显示发行版信息：

```
配置文件: research-bot
路径:    ~/.hermes/profiles/research-bot
模型:   claude-opus-4 (anthropic)
技能:  12
发行版: research-bot@1.0.0
安装自: https://github.com/you/research-bot

这将永久删除:
  • 所有配置、API 密钥、记忆、会话、技能、定时任务
  • 命令别名 (~/.local/bin/research-bot)

输入 'research-bot' 以确认:
```
这样你就永远不会在不知道来源或无法重新安装的情况下意外删除一个 Agent。

---

## 使用场景和模式

### 个人：在多台机器间同步一个 Agent

你在笔记本电脑上构建了一个研究助手。你想在工作站上拥有相同的 Agent。

```bash
# 笔记本电脑
cd ~/.hermes/profiles/research-bot
git init && git add . && git commit -m "initial"
git remote add origin git@github.com:you/research-bot.git
git push -u origin main

# 工作站
hermes profile install github.com/you/research-bot --alias
# 填写 .env。完成。
```

在笔记本电脑上的任何迭代（`git commit && push`）都可以通过 `hermes profile update research-bot` 拉取到工作站上。记忆保持每台机器独立——笔记本电脑记住自己的对话，工作站记住自己的，它们不会冲突。

### 团队：分发一个经过评审的内部 Agent

你的工程团队想要一个共享的 PR 审查机器人，具有特定的灵魂、特定的技能，以及一个定时任务，让每个 PR 都通过它运行。

```bash
# 工程负责人
cd ~/.hermes/profiles/pr-reviewer
# ... 构建和调试 ...
git init && git add . && git commit -m "v1.0 PR reviewer"
git tag v1.0.0
git push -u origin main --tags    # 推送到你公司的内部 Git 主机

# 每个工程师
hermes profile install git@github.com:your-org/pr-reviewer.git --alias
# 用他们自己的 API 密钥（费用由他们承担）填写 .env，.env.EXAMPLE 指明了需要哪些密钥
pr-reviewer chat
```

当负责人发布 v1.1（更好的灵魂、新技能）时，工程师们运行 `hermes profile update pr-reviewer`，几分钟内所有人就都更新到了新版本。

### 社区：发布一个公开的 Agent

你构建了一些新颖的东西——可能是一个“Polymarket 交易员”或一个“学术论文总结器”或一个“Minecraft 服务器运维助手”。你想分享它。

```bash
# 你
cd ~/.hermes/profiles/polymarket-trader
# 在仓库根目录写一个可靠的 README.md —— GitHub 会在仓库页面显示它
git init && git add . && git commit -m "v1.0"
git tag v1.0.0
# 发布到公共 GitHub 仓库
git remote add origin https://github.com/you/hermes-polymarket-trader.git
git push -u origin main --tags

# 任何人
hermes profile install github.com/you/hermes-polymarket-trader --alias
```

在推特上发布安装命令。尝试它的人会给你发 issue 和 PR。如果有人想定制，他们可以 fork —— 使用每个人都已经熟悉的相同 git 工作流。

### 产品：分发一个具有特定设计的 Agent

你在 Hermes 之上构建了一个产品——可能是一个合规监控框架、一个客户支持栈、一个特定领域的研究平台。你想把它作为一个产品来分发。

```yaml
# distribution.yaml
name: telemetry-harness
version: 2.3.1
description: "合规遥测框架 —— 监控和审查受监管的工作流"
hermes_requires: ">=0.13.0"
author: "Acme Compliance Inc."
license: "Commercial"

env_requires:
  - name: ACME_API_KEY
    description: "你的 Acme Compliance 许可证密钥（发邮件至 support@acme.com）"
    required: true
  - name: OPENAI_API_KEY
    description: "用于模型访问的 OpenAI API 密钥"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "你的 Graphiti 知识图谱实例的 URL"
    required: false
    default: "http://127.0.0.1:8000/sse"
```

你的客户通过一个命令安装；安装预览会确切地告诉他们需要准备哪些密钥；你标记新版本后，更新会立即推出；他们的合规数据（`memories/`、`sessions/`）永远不会离开他们的机器。

### 临时：在共享基础设施上运行一次性脚本

你是运维负责人。你想要一个临时的 Agent 来诊断生产事故——一个包含正确工具和 MCP 连接的预设灵魂——并在接下来的一周内在三个待命工程师的笔记本电脑上运行。

```bash
# 你
# 构建配置文件，提交，推送到私有仓库
git push -u origin main

# 每个待命人员
hermes profile install git@github.com:your-org/incident-2026-q2.git --alias

# 事故解决 —— 拆除它
hermes profile delete incident-2026-q2
```

安装-删除周期足够廉价，可以随意处置。

---

## 配方

### 固定到特定版本

:::note
Git 引用固定（`#v1.2.0`）已规划但未在初始版本中提供 —— 目前安装会跟踪默认分支。通过 `hermes profile info <name>` 跟踪你安装的版本，并在准备好之前暂不更新。
:::

### 检查你当前的版本与最新版本

```bash
# 你安装的版本
hermes profile info research-bot | grep Version

# 最新的上游版本（无需安装）
git ls-remote --tags https://github.com/you/research-bot | tail -5
```

### 在更新过程中保留本地配置自定义

默认的更新行为已经做到了这一点：`config.yaml` 会被保留。为了安全起见，请将你的本地调整写入一个分发不拥有的文件：

```yaml
# ~/.hermes/profiles/research-bot/local/my-overrides.yaml
# (分发永远不会触及 local/)
```

…并根据需要从 `config.yaml` 或你的灵魂中引用它。

### 强制进行干净的重新安装

```bash
# 彻底删除并从头重新安装（也会丢失记忆/会话）
hermes profile delete research-bot --yes
hermes profile install github.com/you/research-bot --alias

# 更新到当前的主分支，但将 config.yaml 重置为分发的默认值
hermes profile update research-bot --force-config --yes
```

### Fork 并自定义

标准的 git 工作流 —— 分发只是仓库：

```bash
# 在 GitHub 上 fork 该仓库，然后安装你的 fork
hermes profile install github.com/yourname/forked-research-bot --alias

# 在 ~/.hermes/profiles/forked-research-bot/ 中本地迭代
# 编辑 SOUL.md，提交，推送到你的 fork
# 上游更改：以通常的方式将它们拉取到你的 fork 中
```

### 在推送前测试一个分发

从作者的机器上：

```bash
# 从本地目录安装（无需 git push）
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test --alias

# 调整、删除、重新安装，直到正确为止
hermes profile delete research-bot-test --yes
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test
```
---

## 发行版中永不包含的内容

安装程序会硬性排除以下路径，即使作者意外打包了它们。没有任何配置选项可以覆盖此设置——这个安全防护是一个经过回归测试的不变量：

- `auth.json` — OAuth Token、平台凭证
- `.env` — API 密钥、密钥
- `memories/` — 对话记忆
- `sessions/` — 对话历史
- `state.db`, `state.db-shm`, `state.db-wal` — 会话元数据
- `logs/` — Agent 和错误日志
- `workspace/` — 生成的工作文件
- `plans/` — 草稿计划
- `home/` — Docker 后端中用户的主目录挂载点
- `*_cache/` — 图像 / 音频 / 文档缓存
- `local/` — 为用户保留的自定义命名空间

当你克隆一个发行版时，这些内容根本不存在。当你更新时，它们保持不变。如果你在五台机器上安装了同一个发行版，你将拥有五组独立的数据——每台机器一组。

## 安全与信任

配置文件发行版默认是未签名的。你需要信任：

- **Git 托管服务**（GitHub / GitLab 等）会提供作者推送的字节。
- **作者**不会打包恶意的灵魂（人格）、技能或定时任务。

发行版中的定时任务**不会自动调度**——安装程序会打印 `hermes -p <name> cron list`，你需要显式启用它们。SOUL.md 和技能在你开始与配置文件聊天时**立即生效**，因此，如果你是从不认识的来源安装，请在首次运行前阅读它们。

粗略类比：安装发行版就像安装浏览器扩展或 VS Code 扩展。低摩擦、高权限、信任来源。对于公司内部发行版，使用私有仓库和你正常的 git 认证——无需配置新东西。

未来版本可能会添加签名、包含已解析提交 SHA 的锁文件（`.distribution-lock.yaml`），以及一个在应用更新前打印差异的 `--dry-run` 标志。这些功能目前都尚未发布。

## 底层原理

关于实现细节、精确的 CLI 行为以及所有标志，请参阅 [配置文件命令参考](../reference/profile-commands.md#distribution-commands)。

简要版本：

- `install`、`update`、`info` 命令位于 `hermes profile` 内部——而不是一个平行的命令树。
- 清单格式是 YAML，具有一个极小的必需模式（仅 `name`）。
- 安装程序使用你本地的 `git` 二进制文件进行克隆，因此你的 shell 已经处理的任何认证（SSH 密钥、凭证助手）都能透明地工作。
- 克隆后，`.git/` 目录会被剥离——已安装的配置文件本身不是一个 git 检出，避免了“哎呀，我不小心把我的 `.env` 提交到了发行版的 git 历史中”这类陷阱。
- 保留的配置文件名称（`hermes`、`test`、`tmp`、`root`、`sudo`）在安装时会被拒绝，以避免与常见二进制文件冲突。

## 另请参阅

- [配置文件：运行多个 Agent](./profiles.md) — 基本概念
- [配置文件命令参考](../reference/profile-commands.md) — 每个标志、每个选项
- [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) — 本地备份 / 恢复（非发行版）
- [在 Hermes 中使用 SOUL](../guides/use-soul-with-hermes.md) — 创作人格
- [人格与 SOUL](./features/personality.md) — SOUL 如何融入 Agent
- [技能目录](../reference/skills-catalog.md) — 你可以打包的技能