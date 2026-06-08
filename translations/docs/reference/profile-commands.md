---
sidebar_position: 7
---

# 配置文件命令参考

本页涵盖了所有与 [Hermes 配置文件](../user-guide/profiles.md) 相关的命令。关于通用 CLI 命令，请参阅 [CLI 命令参考](./cli-commands.md)。

## `hermes profile`

```bash
hermes profile <子命令>
```

管理配置文件的总命令。不带子命令运行 `hermes profile` 会显示帮助信息。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use` | 设置活动（默认）配置文件。 |
| `create` | 创建新的配置文件。 |
| `describe` | 读取或设置配置文件的描述（用于看板编排器进行路由）。 |
| `delete` | 删除配置文件。 |
| `show` | 显示配置文件的详细信息。 |
| `alias` | 为配置文件重新生成 shell 别名。 |
| `rename` | 重命名配置文件。 |
| `export` | 将配置文件导出到 tar.gz 归档文件。 |
| `import` | 从 tar.gz 归档文件导入配置文件。 |
| `install` | 从 git URL 或本地目录安装配置文件分发版。参见 [配置文件分发版](../user-guide/profile-distributions.md)。 |
| `update` | 重新拉取由分发版管理的配置文件并重新应用其捆绑包。 |
| `info` | 显示配置文件的分布元数据（来源 URL、提交记录、最后更新时间）。 |

## `hermes profile list`

```bash
hermes profile list
```

列出所有配置文件。当前活动的配置文件用 `*` 标记。

**示例：**

```bash
$ hermes profile list
  default
* work
  dev
  personal
```

无选项。

## `hermes profile use`

```bash
hermes profile use <名称>
```

将 `<名称>` 设置为活动配置文件。所有后续的 `hermes` 命令（不带 `-p`）都将使用此配置文件。

| 参数 | 描述 |
|----------|-------------|
| `<名称>` | 要激活的配置文件名称。使用 `default` 可返回基础配置文件。 |

**示例：**

```bash
hermes profile use work
hermes profile use default
```

## `hermes profile create`

```bash
hermes profile create <名称> [选项]
```

创建一个新的配置文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<名称>` | 新配置文件的名称。必须是有效的目录名（字母数字、连字符、下划线）。 |
| `--clone` | 从当前配置文件复制 `config.yaml`、`.env` 和 `SOUL.md`。 |
| `--clone-all` | 从当前配置文件复制所有内容（配置、记忆、技能、会话、状态）。 |
| `--clone-from <配置文件>` | 从特定配置文件克隆，而不是当前配置文件。与 `--clone` 或 `--clone-all` 一起使用。 |
| `--no-alias` | 跳过包装脚本的创建。 |
| `--description "<文本>"` | 关于此配置文件擅长什么的一两句话描述。用于看板编排器根据角色（而不仅仅是配置文件名称）来路由任务。可以跳过，稍后通过 `hermes profile describe` 添加。保存在 `<profile_dir>/profile.yaml` 中。 |
| `--no-skills` | 创建一个**空**配置文件，不启用任何捆绑技能。在配置文件中写入一个 `.no-bundled-skills` 标记，以便未来的 `hermes update` 运行不会重新植入捆绑集，并且拒绝与 `--clone` / `--clone-all` 结合使用（因为后者无论如何都会复制技能）。适用于不应继承完整技能目录的窄范围编排器配置文件或沙盒配置文件。要在已创建的配置文件（包括默认的 `~/.hermes`）上切换此设置，请使用 `hermes skills opt-out` / `hermes skills opt-in`。 |

创建配置文件**不会**使该配置文件目录成为终端命令的默认项目/工作空间目录。如果你希望配置文件在特定项目中启动，请在该配置文件的 `config.yaml` 中设置 `terminal.cwd`。

**示例：**

```bash
# 空白配置文件 — 需要完整设置
hermes profile create mybot

# 仅从当前配置文件克隆配置
hermes profile create work --clone

# 从当前配置文件克隆所有内容
hermes profile create backup --clone-all

# 从特定配置文件克隆配置
hermes profile create work2 --clone --clone-from work
```

## `hermes profile describe`

```bash
hermes profile describe [<名称>] [选项]
```

读取或设置配置文件的描述。该描述由看板编排器使用，用于根据每个配置文件擅长什么来路由任务，而不是仅从配置文件名称猜测。保存在 `<profile_dir>/profile.yaml` 中，以便在重启后保留并与消息网关共享。

不带标志时，打印当前描述（如果为空，则打印 `(no description set for '<名称>')`）。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<名称>` | 要描述的配置文件。除非使用 `--all --auto`，否则为必需。 |
| `--text "<文本>"` | 将描述设置为这个确切的文本（用户编写）。覆盖任何现有描述。 |
| `--auto` | 基于配置文件已安装的技能、配置的模型和名称，通过辅助 LLM 自动生成一两句话的描述。在 `config.yaml` 的 `auxiliary.profile_describer` 下配置模型。自动生成的描述标记为 `description_auto: true`，以便仪表板可以标记它们以供审查。 |
| `--overwrite` | 与 `--auto` 一起使用时，也替换用户编写的描述（默认：跳过描述已明确设置的配置文件）。 |
| `--all` | 与 `--auto` 一起使用时，扫描每个缺少描述的配置文件。 |

**示例：**

```bash
# 读取当前描述
hermes profile describe researcher

# 明确设置它
hermes profile describe researcher --text "阅读源代码并撰写发现。"

# 让 LLM 生成一个
hermes profile describe researcher --auto

# 为每个没有描述的配置文件填写描述
hermes profile describe --all --auto
```

## `hermes profile delete`

```bash
hermes profile delete <名称> [选项]
```

删除配置文件并移除其 shell 别名。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<名称>` | 要删除的配置文件。 |
| `--yes`, `-y` | 跳过确认提示。 |

**示例：**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
这将永久删除配置文件的整个目录，包括所有配置、记忆、会话和技能。无法删除当前活动的配置文件。
:::
## `hermes profile show`

```bash
hermes profile show <name>
```

显示配置文件的详细信息，包括其主目录、配置的模型、消息网关状态、技能数量以及配置文件状态。

此处显示的是配置文件的主目录，而非终端工作目录。终端命令从 `terminal.cwd`（或在本地后端启动时，若 `cwd: "."` 则从启动目录）开始执行。

| 参数 | 描述 |
|----------|-------------|
| `<name>` | 要检查的配置文件名称。 |

**示例：**

```bash
$ hermes profile show work
配置文件： work
路径：    ~/.hermes/profiles/work
模型：   anthropic/claude-sonnet-4 (anthropic)
消息网关： 已停止
技能：  12
.env：    存在
SOUL.md： 存在
别名：   ~/.local/bin/work
```

## `hermes profile alias`

```bash
hermes profile alias <name> [options]
```

在 `~/.local/bin/<name>` 处重新生成 shell 别名脚本。如果别名被意外删除，或者在移动 Hermes 安装位置后需要更新，此命令非常有用。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<name>` | 要为其创建/更新别名的配置文件。 |
| `--remove` | 移除包装脚本，而不是创建它。 |
| `--name <alias>` | 自定义别名名称（默认：配置文件名称）。 |

**示例：**

```bash
hermes profile alias work
# 创建/更新 ~/.local/bin/work

hermes profile alias work --name mywork
# 创建 ~/.local/bin/mywork

hermes profile alias work --remove
# 移除包装脚本
```

## `hermes profile rename`

```bash
hermes profile rename <old-name> <new-name>
```

重命名配置文件。更新目录和 shell 别名。

| 参数 | 描述 |
|----------|-------------|
| `<old-name>` | 当前配置文件名称。 |
| `<new-name>` | 新的配置文件名称。 |

**示例：**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `hermes profile export`

```bash
hermes profile export <name> [options]
```

将配置文件导出为压缩的 tar.gz 归档文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<name>` | 要导出的配置文件。 |
| `-o`, `--output <path>` | 输出文件路径（默认：`<name>.tar.gz`）。 |

**示例：**

```bash
hermes profile export work
# 在当前目录创建 work.tar.gz

hermes profile export work -o ./work-2026-03-29.tar.gz
```

## `hermes profile import`

```bash
hermes profile import <archive> [options]
```

从 tar.gz 归档文件导入配置文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<archive>` | 要导入的 tar.gz 归档文件路径。 |
| `--name <name>` | 导入配置文件的名称（默认：从归档文件推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# 从归档文件推断配置文件名称

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

## 分发命令

:::tip
**初次接触分发？** 请从 [配置文件分发用户指南](../user-guide/profile-distributions.md) 开始——它涵盖了原因、时机和方法，并提供了完整的示例。以下部分是当你明确需求时的简明 CLI 参考。
:::

分发将配置文件转换为可共享、版本化的工件，并作为 **git 仓库** 发布。接收者只需一条命令即可安装分发，并且以后可以在不触及本地记忆、会话或凭据的情况下就地更新。

`auth.json` 和 `.env` 从不属于分发的一部分——它们保留在安装用户的机器上。

接收者的用户数据（记忆、会话、认证信息、他们对 `.env` 的编辑）在初始安装和后续更新中始终会被保留。

:::info
`hermes profile export` / `import` 仍然是用于 **本地备份和恢复** 自己机器上配置文件的正确命令。分发（`install` / `update` / `info`）是一个独立的概念：通过 git 交付配置文件，以便他人可以安装它。
:::

### `hermes profile install`

```bash
hermes profile install <source> [--name <name>] [--alias] [--force] [--yes]
```

从 git URL 或本地目录安装配置文件分发。

| 选项 | 描述 |
|--------|-------------|
| `<source>` | Git URL（`github.com/user/repo`、`https://...`、`git@...`、`ssh://`、`git://`）或包含根目录下 `distribution.yaml` 的本地目录。 |
| `--name NAME` | 覆盖清单中的配置文件名称。 |
| `--alias` | 同时创建 shell 包装器（例如 `telemetry` → `hermes -p telemetry`）。 |
| `--force` | 覆盖同名的现有配置文件。用户数据仍会被保留。 |
| `-y`, `--yes` | 跳过清单预览确认提示。 |

安装程序会显示清单，列出所需的环境变量，并在请求确认前警告有关定时任务的信息。所需的环境变量会放入一个 `.env.EXAMPLE` 文件中，你需要将其复制为 `.env` 并填写。

**示例：**

```bash
# 从 GitHub 仓库安装（简写形式）
hermes profile install github.com/kyle/telemetry-distribution --alias

# 从完整的 HTTPS git URL 安装
hermes profile install https://github.com/kyle/telemetry-distribution.git

# 从 SSH 安装
hermes profile install git@github.com:kyle/telemetry-distribution.git

# 在开发期间从本地目录安装
hermes profile install ./telemetry/
```

### `hermes profile update`

```bash
hermes profile update <name> [--force-config] [--yes]
```

从其记录的源重新克隆分发并应用更新。分发拥有的文件（SOUL.md、skills/、cron/、mcp.json）会被覆盖；用户数据（记忆、会话、认证信息、.env）永远不会被触及。

默认情况下，`config.yaml` 会被保留以维持你的本地覆盖设置。传递 `--force-config` 以将其重置为分发附带的配置。

### `hermes profile info`

```bash
hermes profile info <name>
```

打印配置文件的分布清单——名称、版本、所需的 Hermes 版本、作者、环境变量要求、源 URL/路径，以及分发上次被 `install` 或 `update` 时记录的 `Installed:` 时间戳。在安装共享配置文件之前检查其需求，以及发现“此配置文件是 6 个月前安装的且从未更新过”时非常有用。
`hermes profile list` 还会在 `Distribution` 列中显示发行版名称和版本，并且 `hermes profile show <名称>` / `delete <名称>` 会显示来源 URL，这样你一眼就能看出哪些配置文件来自 git 仓库，哪些是在本地创建的。

### 私有发行版

私有 git 仓库作为发行版源无需额外配置 —— 安装过程会调用你正常的 `git` 二进制文件，因此你的 shell 已设置的任何身份验证（SSH 密钥、`git credential` 助手、GitHub CLI 存储的 HTTPS 凭据）都会透明地应用。

```bash
# 使用你的 SSH 密钥，与任何其他 `git clone` 命令相同
hermes profile install git@github.com:your-org/internal-assistant.git

# 使用你的 git credential 助手
hermes profile install https://github.com/your-org/internal-assistant.git
```

如果在安装过程中，克隆操作在你的终端中交互式地提示输入凭据，该提示会正常显示。请先按照你通常对同一仓库使用 `git clone` 的方式设置身份验证，然后再进行安装。

### 发行版清单 (`distribution.yaml`)

每个发行版在其仓库根目录下都有一个 `distribution.yaml` 文件：

```yaml
name: telemetry
version: 0.1.0
description: "合规性监控工具"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API 密钥"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "记忆图 URL"
    required: false
    default: "http://127.0.0.1:8000/sse"
distribution_owned:   # 可选；默认为 SOUL.md, config.yaml,
                      #   mcp.json, skills/, cron/, distribution.yaml
  - SOUL.md
  - skills/compliance/
  - cron/
```

`hermes_requires` 支持 `>=`、`<=`、`==`、`!=`、`>`、`<`，或一个裸版本号（视为 `>=`）。如果当前的 Hermes 版本不满足规范，安装将失败并显示明确的错误信息。

`distribution_owned` 是可选的。如果设置了，则只有这些路径在更新时会被替换；配置文件中其他任何内容都保持为用户所有。如果省略，则应用上述默认值。

### 发布发行版

创作发行版只需进行 git push：

1.  在你的配置文件目录中，创建 `distribution.yaml`，至少包含 `name` 和 `version`。
2.  初始化一个 git 仓库（或使用现有仓库）并推送到 GitHub / GitLab / 任何 Hermes 可以克隆的主机。
3.  告诉接收者运行 `hermes profile install <你的仓库URL>`。

使用 git 标签进行版本化发布 —— 克隆 `HEAD` 的接收者将获得你的最新状态，并且你始终可以在清单中更新 `version:`。

## `hermes -p` / `hermes --profile`

```bash
hermes -p <名称> <命令> [选项]
hermes --profile <名称> <命令> [选项]
```

全局标志，用于在特定配置文件下运行任何 Hermes 命令，而无需更改粘性默认值。这会在命令执行期间覆盖活动配置文件。

| 选项 | 描述 |
|--------|-------------|
| `-p <名称>`, `--profile <名称>` | 用于此命令的配置文件。 |

**示例：**

```bash
hermes -p work chat -q "检查服务器状态"
hermes --profile dev gateway start
hermes -p personal skills list
hermes -p work config edit
```

## `hermes completion`

```bash
hermes completion <shell>
```

生成 shell 自动补全脚本。包括对配置文件名称和配置文件子命令的补全。

| 参数 | 描述 |
|----------|-------------|
| `<shell>` | 为其生成补全的 shell：`bash`、`zsh` 或 `fish`。 |

**示例：**

```bash
# 安装补全
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc
hermes completion fish > ~/.config/fish/completions/hermes.fish

# 重新加载 shell
source ~/.bashrc
```

安装后，Tab 键补全适用于：
- `hermes profile <TAB>` — 子命令（list, use, create 等）
- `hermes profile use <TAB>` — 配置文件名称
- `hermes -p <TAB>` — 配置文件名称

## 另请参阅

- [配置文件用户指南](../user-guide/profiles.md)
- [CLI 命令参考](./cli-commands.md)
- [FAQ — 配置文件部分](./faq.md#profiles)