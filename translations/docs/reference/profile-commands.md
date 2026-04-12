---
sidebar_position: 7
---

# 配置文件命令参考

此页面涵盖了所有与 [Hermes 配置文件](../user-guide/profiles.md) 相关的命令。关于通用 CLI 命令，请参阅 [CLI 命令参考](./cli-commands.md)。

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
| `delete` | 删除配置文件。 |
| `show` | 显示配置文件的详细信息。 |
| `alias` | 为配置文件重新生成 shell 别名。 |
| `rename` | 重命名配置文件。 |
| `export` | 将配置文件导出为 tar.gz 归档文件。 |
| `import` | 从 tar.gz 归档文件导入配置文件。 |

## `hermes profile list`

```bash
hermes profile list
```

列出所有配置文件。当前活动的配置文件会用 `*` 标记。

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
此操作将永久删除配置文件的整个目录，包括所有配置、记忆、会话和技能。无法删除当前活动的配置文件。
:::

## `hermes profile show`

```bash
hermes profile show <名称>
```

显示配置文件的详细信息，包括其主目录、配置的模型、消息网关状态、技能数量和配置文件状态。

| 参数 | 描述 |
|----------|-------------|
| `<名称>` | 要检查的配置文件。 |

**示例：**

```bash
$ hermes profile show work
配置文件: work
路径:    ~/.hermes/profiles/work
模型:   anthropic/claude-sonnet-4 (anthropic)
消息网关: 已停止
技能:  12
.env:    存在
SOUL.md: 存在
别名:   ~/.local/bin/work
```

## `hermes profile alias`

```bash
hermes profile alias <名称> [选项]
```

在 `~/.local/bin/<名称>` 处重新生成 shell 别名脚本。如果别名被意外删除，或者在移动 Hermes 安装位置后需要更新它，此命令很有用。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<名称>` | 要为其创建/更新别名的配置文件。 |
| `--remove` | 移除包装脚本而不是创建它。 |
| `--name <别名>` | 自定义别名名称（默认：配置文件名称）。 |

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
hermes profile rename <旧名称> <新名称>
```

重命名配置文件。更新目录和 shell 别名。

| 参数 | 描述 |
|----------|-------------|
| `<旧名称>` | 当前配置文件名称。 |
| `<新名称>` | 新的配置文件名称。 |

**示例：**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `hermes profile export`

```bash
hermes profile export <名称> [选项]
```

将配置文件导出为压缩的 tar.gz 归档文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<名称>` | 要导出的配置文件。 |
| `-o`, `--output <路径>` | 输出文件路径（默认：`<名称>.tar.gz`）。 |

**示例：**

```bash
hermes profile export work
# 在当前目录创建 work.tar.gz

hermes profile export work -o ./work-2026-03-29.tar.gz
```

## `hermes profile import`

```bash
hermes profile import <归档文件> [选项]
```

从 tar.gz 归档文件导入配置文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<归档文件>` | 要导入的 tar.gz 归档文件的路径。 |
| `--name <名称>` | 导入的配置文件的名称（默认：从归档文件推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# 从归档文件推断配置文件名称

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

## `hermes -p` / `hermes --profile`

```bash
hermes -p <名称> <命令> [选项]
hermes --profile <名称> <命令> [选项]
```

全局标志，用于在特定配置文件下运行任何 Hermes 命令，而无需更改粘性默认值。这将在命令执行期间覆盖活动配置文件。

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
| `<shell>` | 为其生成补全的 shell：`bash` 或 `zsh`。 |

**示例：**

```bash
# 安装补全
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc

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