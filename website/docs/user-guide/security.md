---
sidebar_position: 8
title: "安全"
description: "安全模型、危险命令审批、用户授权、容器隔离以及生产部署最佳实践"
---

# 安全

Hermes Agent 采用纵深防御安全模型设计。本页涵盖所有安全边界——从命令审批到容器隔离，再到消息平台上的用户授权。

## 概述

安全模型包含七层：

1.  **用户授权** — 谁可以与 Agent 对话（允许列表、私聊配对）
2.  **危险命令审批** — 对破坏性操作实施人工介入
3.  **容器隔离** — 使用 Docker/Singularity/Modal 沙盒及强化设置
4.  **MCP 凭证过滤** — 为 MCP 子进程隔离环境变量
5.  **上下文文件扫描** — 检测项目文件中的提示词注入
6.  **跨会话隔离** — 会话之间无法访问彼此的数据或状态；定时任务的存储路径经过强化，可防范路径遍历攻击
7.  **输入净化** — 终端工具后端中的工作目录参数会对照允许列表进行验证，以防止 Shell 注入

## 危险命令审批

在执行任何命令之前，Hermes 会对照一个精心策划的危险模式列表进行检查。如果发现匹配项，用户必须明确批准该命令。

### 审批模式

审批系统支持三种模式，通过 `~/.hermes/config.yaml` 中的 `approvals.mode` 配置：

```yaml
approvals:
  mode: manual    # manual | smart | off
  timeout: 60     # 等待用户响应的秒数（默认：60）
```

| 模式 | 行为 |
|------|----------|
| **manual** (默认) | 对于危险命令，始终提示用户审批 |
| **smart** | 使用辅助 LLM 评估风险。低风险命令（例如 `python -c "print('hello')"`）会自动批准。真正危险的命令会自动拒绝。不确定的情况会升级为手动提示。 |
| **off** | 禁用所有审批检查 — 等同于使用 `--yolo` 运行。所有命令无需提示即可执行。 |

:::warning
设置 `approvals.mode: off` 会禁用所有安全提示。仅在受信任的环境（CI/CD、容器等）中使用。
:::

### YOLO 模式

YOLO 模式会绕过当前会话的**所有**危险命令审批提示。可以通过三种方式激活：

1.  **CLI 标志**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话
2.  **斜杠命令**：在会话期间输入 `/yolo` 来切换开关
3.  **环境变量**：设置 `HERMES_YOLO_MODE=1`

`/yolo` 命令是一个**切换开关** — 每次使用都会切换模式：

```
> /yolo
  ⚡ YOLO 模式开启 — 所有命令自动批准。请谨慎使用。

> /yolo
  ⚠ YOLO 模式关闭 — 危险命令将需要审批。
```

YOLO 模式在 CLI 和消息网关会话中均可用。在内部，它会设置 `HERMES_YOLO_MODE` 环境变量，该变量在每次命令执行前都会被检查。

:::danger
YOLO 模式会禁用会话的**所有**危险命令安全检查。仅在完全信任生成的命令时使用（例如，在一次性环境中运行经过充分测试的自动化脚本）。
:::

### 审批超时

当出现危险命令提示时，用户有可配置的时间来响应。如果在超时时间内没有给出响应，命令将默认被**拒绝**（故障关闭）。

在 `~/.hermes/config.yaml` 中配置超时时间：

```yaml
approvals:
  timeout: 60  # 秒（默认：60）
```

### 触发审批的条件

以下模式会触发审批提示（定义在 `tools/approval.py` 中）：

| 模式 | 描述 |
|---------|-------------|
| `rm -r` / `rm --recursive` | 递归删除 |
| `rm ... /` | 在根路径删除 |
| `chmod 777/666` / `o+w` / `a+w` | 全局/其他用户可写权限 |
| `chmod --recursive` 配合不安全权限 | 递归设置全局/其他用户可写权限（长标志） |
| `chown -R root` / `chown --recursive root` | 递归将所有者更改为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 写入块设备 |
| `DROP TABLE/DATABASE` | SQL DROP |
| `DELETE FROM` (不带 WHERE) | 不带 WHERE 的 SQL DELETE |
| `TRUNCATE TABLE` | SQL TRUNCATE |
| `> /etc/` | 覆盖系统配置 |
| `systemctl stop/disable/mask` | 停止/禁用系统服务 |
| `kill -9 -1` | 终止所有进程 |
| `pkill -9` | 强制终止进程 |
| Fork bomb 模式 | Fork 炸弹 |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | 通过 `-c` 标志执行 Shell 命令（包括组合标志如 `-lc`） |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | 通过 `-e`/`-c` 标志执行脚本 |
| `curl ... \| sh` / `wget ... \| sh` | 将远程内容管道传输到 Shell |
| `bash <(curl ...)` / `sh <(wget ...)` | 通过进程替换执行远程脚本 |
| `tee` 到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过 tee 覆盖敏感文件 |
| `>` / `>>` 到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过重定向覆盖敏感文件 |
| `xargs rm` | 配合 rm 使用 xargs |
| `find -exec rm` / `find -delete` | 配合破坏性操作使用 find |
| `cp`/`mv`/`install` 到 `/etc/` | 将文件复制/移动到系统配置目录 |
| 对 `/etc/` 使用 `sed -i` / `sed --in-place` | 就地编辑系统配置 |
| `pkill`/`killall` hermes/gateway | 防止自我终止 |
| 配合 `&`/`disown`/`nohup`/`setsid` 使用 `gateway run` | 防止在服务管理器之外启动消息网关 |

:::info
**容器绕过**：当在 `docker`、`singularity`、`modal` 或 `daytona` 后端中运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。容器内的破坏性命令无法危害宿主机。
:::

### 审批流程 (CLI)

在交互式 CLI 中，危险命令会显示一个内联审批提示：

```
  ⚠️  危险命令：递归删除
      rm -rf /tmp/old-project

      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny

      选择 [o/s/a/D]:
```

四个选项：

- **once** — 允许此次单次执行
- **session** — 允许此模式在本次会话的剩余时间内执行
- **always** — 添加到永久允许列表（保存到 `config.yaml`）
- **deny** (默认) — 阻止该命令
### 审批流程（消息网关）

在消息平台上，Agent 会将危险命令的详细信息发送到聊天中，并等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

运行消息网关时，会自动设置 `HERMES_EXEC_ASK=1` 环境变量。

### 永久允许列表

使用 "always" 批准的命令会保存到 `~/.hermes/config.yaml`：

```yaml
# 永久允许的危险命令模式
command_allowlist:
  - rm
  - systemctl
```

这些模式在启动时加载，并在所有未来的会话中静默批准。

:::tip
使用 `hermes config edit` 来查看或从你的永久允许列表中移除模式。
:::

## 用户授权（消息网关）

当运行消息网关时，Hermes 通过分层授权系统控制谁可以与机器人交互。

### 授权检查顺序

`_is_user_authorized()` 方法按以下顺序检查：

1.  **平台级允许所有标志**（例如 `DISCORD_ALLOW_ALL_USERS=true`）
2.  **私信配对批准列表**（通过配对码批准的用户）
3.  **平台特定允许列表**（例如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4.  **全局允许列表**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5.  **全局允许所有**（`GATEWAY_ALLOW_ALL_USERS=true`）
6.  **默认：拒绝**

### 平台允许列表

在 `~/.hermes/.env` 中将允许的用户 ID 设置为逗号分隔的值：

```bash
# 平台特定允许列表
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# 跨平台允许列表（所有平台都会检查）
GATEWAY_ALLOWED_USERS=123456789

# 平台级允许所有（谨慎使用）
DISCORD_ALLOW_ALL_USERS=true

# 全局允许所有（极度谨慎使用）
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**未配置任何允许列表**且未设置 `GATEWAY_ALLOW_ALL_USERS`，**所有用户都将被拒绝**。网关在启动时会记录警告：

```
未配置用户允许列表。所有未授权用户将被拒绝。
在 ~/.hermes/.env 中设置 GATEWAY_ALLOW_ALL_USERS=true 以允许开放访问，
或配置平台允许列表（例如 TELEGRAM_ALLOWED_USERS=your_id）。
```
:::

### 私信配对系统

为了更灵活的授权，Hermes 包含一个基于代码的配对系统。无需预先知道用户 ID，未知用户会收到一个一次性配对码，由机器人所有者通过 CLI 批准。

**工作原理：**

1.  未知用户向机器人发送私信
2.  机器人回复一个 8 字符的配对码
3.  机器人所有者在 CLI 上运行 `hermes pairing approve <platform> <code>`
4.  该用户被永久批准访问该平台

在 `~/.hermes/config.yaml` 中控制如何处理未授权的私信：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

-   `pair` 是默认值。未授权的私信会收到配对码回复。
-   `ignore` 会静默丢弃未授权的私信。
-   平台特定配置会覆盖全局默认值，因此你可以在 Telegram 上保持配对，同时让 WhatsApp 保持静默。

**安全特性**（基于 OWASP + NIST SP 800-63-4 指南）：

| 特性 | 详情 |
|---------|---------|
| 代码格式 | 8 字符，来自 32 字符无歧义字母表（不含 0/O/1/I） |
| 随机性 | 加密随机（`secrets.choice()`） |
| 代码有效期 | 1 小时过期 |
| 速率限制 | 每用户每 10 分钟 1 次请求 |
| 待处理限制 | 每个平台最多 3 个待处理代码 |
| 锁定 | 5 次批准尝试失败 → 锁定 1 小时 |
| 文件安全 | 所有配对数据文件设置 `chmod 0600` |
| 日志记录 | 代码从不记录到 stdout |

**配对 CLI 命令：**

```bash
# 列出待处理和已批准的用户
hermes pairing list

# 批准一个配对码
hermes pairing approve telegram ABC12DEF

# 撤销用户的访问权限
hermes pairing revoke telegram 123456789

# 清除所有待处理代码
hermes pairing clear-pending
```

**存储：** 配对数据存储在 `~/.hermes/pairing/` 中，每个平台有独立的 JSON 文件：
-   `{platform}-pending.json` — 待处理的配对请求
-   `{platform}-approved.json` — 已批准的用户
-   `_rate_limits.json` — 速率限制和锁定跟踪

## 容器隔离

当使用 `docker` 终端后端时，Hermes 会对每个容器应用严格的安全加固。

### Docker 安全标志

每个容器都使用以下标志运行（定义在 `tools/environments/docker.py` 中）：

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # 丢弃所有 Linux 能力
    "--cap-add", "DAC_OVERRIDE",                  # Root 可以写入绑定挂载的目录
    "--cap-add", "CHOWN",                         # 包管理器需要文件所有权
    "--cap-add", "FOWNER",                        # 包管理器需要文件所有权
    "--security-opt", "no-new-privileges",         # 阻止权限提升
    "--pids-limit", "256",                         # 限制进程数量
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # 大小受限的 /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # 禁止执行的 /var/tmp
    "--tmpfs", "/run:rw,noexec,nosuid,size=64m",   # 禁止执行的 /run
]
```

### 资源限制

容器资源可在 `~/.hermes/config.yaml` 中配置：

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # 仅显式允许列表；为空则阻止密钥进入容器
  container_cpu: 1        # CPU 核心数
  container_memory: 5120  # MB（默认 5GB）
  container_disk: 51200   # MB（默认 50GB，需要在 XFS 上使用 overlay2）
  container_persistent: true  # 跨会话持久化文件系统
```

### 文件系统持久化

-   **持久化模式**（`container_persistent: true`）：从 `~/.hermes/sandboxes/docker/<task_id>/` 绑定挂载 `/workspace` 和 `/root`
-   **临时模式**（`container_persistent: false`）：对工作空间使用 tmpfs — 清理时所有内容都会丢失

:::tip
对于生产环境的消息网关部署，请使用 `docker`、`modal` 或 `daytona` 后端，将 Agent 命令与你的主机系统隔离。这完全消除了对危险命令审批的需求。
:::
:::warning
如果将变量名添加到 `terminal.docker_forward_env`，这些变量会被有意注入到容器中供终端命令使用。这对于任务特定的凭据（如 `GITHUB_TOKEN`）很有用，但也意味着在容器中运行的代码可以读取并泄露它们。
:::

## 终端后端安全性对比

| 后端 | 隔离性 | 危险命令检查 | 最佳适用场景 |
|---------|-----------|-------------------|----------|
| **local** | 无 — 在主机上运行 | ✅ 是 | 开发环境，受信任的用户 |
| **ssh** | 远程机器 | ✅ 是 | 在独立服务器上运行 |
| **docker** | 容器 | ❌ 跳过（容器即边界） | 生产环境消息网关 |
| **singularity** | 容器 | ❌ 跳过 | HPC 环境 |
| **modal** | 云沙盒 | ❌ 跳过 | 可扩展的云隔离 |
| **daytona** | 云沙盒 | ❌ 跳过 | 持久化的云工作空间 |

## 环境变量透传 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 都会从子进程中剥离敏感环境变量，以防止 LLM 生成的代码泄露凭据。然而，声明了 `required_environment_variables` 的技能确实需要访问这些变量。

### 工作原理

两种机制允许特定变量通过沙盒过滤器：

**1. 技能作用域的透传（自动）**

当技能被加载（通过 `skill_view` 或 `/skill` 命令）并声明了 `required_environment_variables` 时，环境中实际设置的任何这些变量都会自动注册为透传变量。缺失的变量（仍处于需要设置的状态）**不会**被注册。

```yaml
# 在技能的 SKILL.md frontmatter 中
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
```

加载此技能后，`TENOR_API_KEY` 将透传到 `execute_code`、`terminal`（本地）**以及远程后端（Docker、Modal）** — 无需手动配置。

:::info Docker 和 Modal
在 v0.5.1 之前，Docker 的 `forward_env` 是一个独立于技能透传的系统。现在它们已经合并 — 技能声明的环境变量会自动转发到 Docker 容器和 Modal 沙盒中，无需手动添加到 `docker_forward_env`。
:::

**2. 基于配置的透传（手动）**

对于任何技能都未声明的环境变量，请将它们添加到 `config.yaml` 中的 `terminal.env_passthrough`：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭据文件透传（OAuth 令牌等） {#credential-file-passthrough}

某些技能需要沙盒中的**文件**（不仅仅是环境变量）— 例如，Google Workspace 将 OAuth 令牌存储为活动配置文件的 `HERMES_HOME` 下的 `google_token.json`。技能在 frontmatter 中声明这些文件：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭据
```

加载时，Hermes 会检查这些文件是否存在于活动配置文件的 `HERMES_HOME` 中，并注册它们以进行挂载：

- **Docker**：只读绑定挂载（`-v host:container:ro`）
- **Modal**：在沙盒创建时挂载 + 在每个命令执行前同步（处理会话中的 OAuth 设置）
- **Local**：无需操作（文件已可访问）

您也可以在 `config.yaml` 中手动列出凭据文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径相对于 `~/.hermes/`。文件被挂载到容器内的 `/root/.hermes/`。

### 每个沙盒过滤的内容

| 沙盒 | 默认过滤器 | 透传覆盖 |
|---------|---------------|---------------------|
| **execute_code** | 阻止名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 的变量；只允许安全前缀的变量通过 | ✅ 透传变量绕过两项检查 |
| **terminal**（本地） | 阻止明确的 Hermes 基础设施变量（提供商密钥、消息网关令牌、工具 API 密钥） | ✅ 透传变量绕过阻止列表 |
| **terminal**（Docker） | 默认无主机环境变量 | ✅ 透传变量 + `docker_forward_env` 通过 `-e` 转发 |
| **terminal**（Modal） | 默认无主机环境变量/文件 | ✅ 凭据文件被挂载；环境变量通过同步透传 |
| **MCP** | 阻止除安全系统变量 + 明确配置的 `env` 之外的所有内容 | ❌ 不受透传影响（请改用 MCP 的 `env` 配置） |

### 安全注意事项

- 透传仅影响您或您的技能明确声明的变量 — 对于任意的 LLM 生成代码，默认的安全态势保持不变
- 凭据文件以**只读**方式挂载到 Docker 容器中
- 技能防护在安装前会扫描技能内容以查找可疑的环境变量访问模式
- 缺失/未设置的变量永远不会被注册（您无法泄露不存在的东西）
- Hermes 基础设施密钥（提供商 API 密钥、消息网关令牌）绝不应添加到 `env_passthrough` — 它们有专门的机制

## MCP 凭据处理

MCP（模型上下文协议）服务器子进程接收一个**经过过滤的环境**，以防止意外凭据泄露。

### 安全环境变量

只有以下变量会从主机透传到 MCP stdio 子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

加上任何 `XDG_*` 变量。所有其他环境变量（API 密钥、令牌、密钥）都**被剥离**。

在 MCP 服务器的 `env` 配置中明确定义的变量会被透传：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # 只有这个会被传递
```

### 凭据脱敏

来自 MCP 工具的错误消息在返回给 LLM 之前会被清理。以下模式会被替换为 `[REDACTED]`：

- GitHub PATs (`ghp_...`)
- OpenAI 风格的密钥 (`sk-...`)
- Bearer 令牌
- `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 参数
### 网站访问策略

你可以限制 Agent 通过其网页和浏览器工具访问哪些网站。这对于防止 Agent 访问内部服务、管理面板或其他敏感 URL 非常有用。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  website_blocklist:
    enabled: true
    domains:
      - "*.internal.company.com"
      - "admin.example.com"
    shared_files:
      - "/etc/hermes/blocked-sites.txt"
```

当请求被阻止的 URL 时，工具会返回一个错误，说明该域名已被策略阻止。该阻止列表在 `web_search`、`web_extract`、`browser_navigate` 以及所有支持 URL 的工具中强制执行。

完整详情请参阅配置指南中的[网站阻止列表](/docs/user-guide/configuration#website-blocklist)。

### SSRF 防护

所有支持 URL 的工具（网页搜索、网页提取、视觉、浏览器）在获取 URL 之前都会验证 URL，以防止服务器端请求伪造攻击。被阻止的地址包括：

- **私有网络**：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **环回地址**：`127.0.0.0/8`、`::1`
- **链路本地地址**：`169.254.0.0/16`（包括位于 `169.254.169.254` 的云元数据）
- **CGNAT / 共享地址空间**：`100.64.0.0/10`（Tailscale、WireGuard VPNs）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **保留地址、组播地址和未指定地址**

SSRF 防护始终处于启用状态且无法禁用。DNS 失败被视为被阻止（故障关闭）。重定向链会在每个跳转点重新验证，以防止基于重定向的绕过。

### Tirith 执行前安全扫描

Hermes 集成了 [tirith](https://github.com/sheeki03/tirith)，用于在执行前进行内容级别的命令扫描。Tirith 可以检测仅靠模式匹配会遗漏的威胁：

- 同形异义词 URL 欺骗（国际化域名攻击）
- 管道到解释器的模式（`curl | bash`、`wget | sh`）
- 终端注入攻击

Tirith 在首次使用时从 GitHub 发布版自动安装，并进行 SHA-256 校验和验证（如果 cosign 可用，还会进行 cosign 来源验证）。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  tirith_enabled: true       # 启用/禁用 tirith 扫描（默认：true）
  tirith_path: "tirith"      # tirith 二进制文件路径（默认：PATH 查找）
  tirith_timeout: 5          # 子进程超时时间（秒）
  tirith_fail_open: true     # 当 tirith 不可用时允许执行（默认：true）
```

当 `tirith_fail_open` 为 `true`（默认）时，如果 tirith 未安装或超时，命令将继续执行。在高安全环境中，将其设置为 `false`，以便在 tirith 不可用时阻止命令。

Tirith 的判定结果会集成到审批流程中：安全的命令直接通过，而可疑和被阻止的命令则会触发用户审批，并附上完整的 tirith 发现结果（严重性、标题、描述、更安全的替代方案）。用户可以批准或拒绝——默认选择是拒绝，以保持无人值守场景的安全。

### 上下文文件注入防护

上下文文件（AGENTS.md、.cursorrules、SOUL.md）在包含到系统提示词之前，会进行提示词注入扫描。扫描器检查以下内容：

- 忽略/无视先前指令的指示
- 包含可疑关键词的隐藏 HTML 注释
- 尝试读取密钥（`.env`、`credentials`、`.netrc`）
- 通过 `curl` 泄露凭据
- 不可见的 Unicode 字符（零宽空格、双向覆盖符）

被阻止的文件会显示警告：

```
[BLOCKED: AGENTS.md 包含潜在的提示词注入。内容未加载。]
```

## 生产部署最佳实践

### 消息网关部署清单

1.  **设置明确的允许列表** — 在生产环境中切勿使用 `GATEWAY_ALLOW_ALL_USERS=true`
2.  **使用容器后端** — 在 config.yaml 中设置 `terminal.backend: docker`
3.  **限制资源限制** — 设置适当的 CPU、内存和磁盘限制
4.  **安全存储密钥** — 将 API 密钥保存在 `~/.hermes/.env` 中，并设置适当的文件权限
5.  **启用 DM 配对** — 尽可能使用配对码而不是硬编码用户 ID
6.  **审查命令允许列表** — 定期审核 config.yaml 中的 `command_allowlist`
7.  **设置 `MESSAGING_CWD`** — 不要让 Agent 在敏感目录下操作
8.  **以非 root 用户身份运行** — 切勿以 root 身份运行消息网关
9.  **监控日志** — 检查 `~/.hermes/logs/` 中是否有未经授权的访问尝试
10. **保持更新** — 定期运行 `hermes update` 以获取安全补丁

### 保护 API 密钥

```bash
# 为 .env 文件设置适当的权限
chmod 600 ~/.hermes/.env

# 为不同的服务使用不同的密钥
# 切勿将 .env 文件提交到版本控制
```

### 网络隔离

为了获得最高安全性，请在单独的机器或虚拟机上运行消息网关：

```yaml
terminal:
  backend: ssh
  ssh_host: "agent-worker.local"
  ssh_user: "hermes"
  ssh_key: "~/.ssh/hermes_agent_key"
```

这可以将消息网关的消息连接与 Agent 的命令执行分离开来。