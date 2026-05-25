# Bitwarden Secrets Manager

在进程启动时从 [Bitwarden Secrets Manager](https://bitwarden.com/products/secrets-manager/) 拉取 API 密钥，而不是将它们以明文形式存储在 `~/.hermes/.env` 中。一个引导密钥（机器账户访问令牌）替代了 N 个按提供商的密钥，并且凭证轮换变成了在 Bitwarden 网页应用中的一次更改。

## 工作原理

1. 你在 Bitwarden Secrets Manager 中创建一个**机器账户**，授予其对某个项目的读取权限，并生成一个**访问令牌**。
2. Hermes 将该单个令牌作为 `BWS_ACCESS_TOKEN` 存储在 `~/.hermes/.env` 中。
3. 每次 `hermes`（或消息网关，或定时任务）启动时，在 `~/.hermes/.env` 加载后，Hermes 会调用 `bws secret list <project_id>` 并将返回的密钥设置到 `os.environ` 中。
4. 默认情况下，Hermes 会**覆盖**环境中已存在的值，因此 Bitwarden 是唯一可信源——在网页应用中轮换一次密钥，每个 Hermes 进程都会在下一次启动时获取它。如果你希望 `.env` 优先，请在配置中将 `override_existing: false` 翻转。

`bws` 二进制文件在首次使用时自动下载到 `~/.hermes/bin/` 中——无需 `apt`、`brew` 或 `sudo`。

## 为什么使用机器账户（以及为什么没有 2FA 提示）

Bitwarden Secrets Manager 专为非交互式工作负载设计：机器账户不能启用 2FA，因为没有人在循环中。访问令牌本身就是凭证。任何拥有它的人都可以读取该机器账户有权访问的每个密钥，因此请将其视为高价值的持有者令牌——将其存储在 `.env` 中（而非 `config.yaml`），如果它泄露，请从 Bitwarden 网页应用中撤销并重新生成。

你在网页应用中设置机器账户，在那里你的常规 2FA 适用。之后，令牌是自主的。

## 设置

### 1. 创建机器账户和访问令牌

在 [Bitwarden 网页应用](https://vault.bitwarden.com) 中（或欧盟账户使用 [vault.bitwarden.eu](https://vault.bitwarden.eu)）：

1. 从产品切换器切换到 **Secrets Manager**。
2. 创建或选择一个**项目**（例如 "Hermes keys"）。
3. 将你的提供商密钥添加为密钥。密钥的**名称**将成为环境变量名——使用 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等。
4. **机器账户 → 新建机器账户 → My Hermes machine** → **项目**选项卡 → 授予对你的项目的读取权限。
5. **访问令牌**选项卡 → **创建访问令牌** → **永不过期**（或选择一个日期）→ 复制令牌（以 `0.` 开头）。Bitwarden 无法再次检索它——请保管好副本。

Secrets Manager 包含在 Bitwarden 免费版中，但有使用限制；无需付费计划即可试用此功能。

### 2. 运行向导

```bash
hermes secrets bitwarden setup
```

它将：

1. 下载并验证 `bws v2.0.0` 到 `~/.hermes/bin/bws`。
2. 提示你输入访问令牌（输入被隐藏）。存储在 `~/.hermes/.env` 中作为 `BWS_ACCESS_TOKEN`。
3. 询问你的机器账户属于哪个 Bitwarden 区域——**US Cloud**、**EU Cloud** 或**自托管 / 自定义 URL**。存储在 `config.yaml` 中作为 `secrets.bitwarden.server_url`，并作为 `BWS_SERVER_URL` 传递给 `bws`。
4. 列出机器账户可以看到的项目；选择一个。存储在 `config.yaml` 中作为 `secrets.bitwarden.project_id`。
5. 测试获取项目的密钥，并显示哪些环境变量将被解析。
6. 将 `secrets.bitwarden.enabled: true` 翻转。

也支持通过标志进行非交互式设置：

```bash
hermes secrets bitwarden setup \
  --access-token "$BWS_ACCESS_TOKEN" \
  --server-url https://vault.bitwarden.eu \
  --project-id <project-uuid>
```

### 3. 确认

```bash
hermes secrets bitwarden status
```

从现在开始，每次调用 `hermes` 都会在启动时拉取最新的密钥。你将在 stderr 中看到一行摘要，这是首次在进程中应用密钥时。

## CLI

| 命令 | 功能 |
|---|---|
| `hermes secrets bitwarden setup` | 交互式向导（安装二进制文件、提示输入令牌、选择项目、测试获取） |
| `hermes secrets bitwarden status` | 显示配置 + 二进制版本 + 令牌存在情况 |
| `hermes secrets bitwarden sync` | 试运行：立即拉取密钥并显示将要应用的内容 |
| `hermes secrets bitwarden sync --apply` | 拉取并导出到当前 shell 的环境变量中 |
| `hermes secrets bitwarden install` | 仅下载固定的 `bws` 二进制文件（无需认证） |
| `hermes secrets bitwarden disable` | 将 `enabled: false` 翻转；保留令牌和项目 ID |

## 配置

`~/.hermes/config.yaml` 中的默认值：

```yaml
secrets:
  bitwarden:
    enabled: false
    access_token_env: BWS_ACCESS_TOKEN
    project_id: ""
    server_url: ""
    cache_ttl_seconds: 300
    override_existing: true
    auto_install: true
```

| 键 | 默认值 | 功能 |
|---|---|---|
| `enabled` | `false` | 主开关。当为 false 时，从不联系 Bitwarden。 |
| `access_token_env` | `BWS_ACCESS_TOKEN` | 存放引导令牌的环境变量名。如果你已将 `BWS_ACCESS_TOKEN` 用于其他用途，请更改此项。 |
| `project_id` | `""` | 要同步的项目的 UUID。 |
| `server_url` | `""` | Bitwarden 区域或自托管端点。空 = `bws` 默认值（US Cloud，`https://vault.bitwarden.com`）。对于 EU Cloud 设置为 `https://vault.bitwarden.eu`，或对于自托管设置为你自己的 URL。作为 `BWS_SERVER_URL` 传递给 `bws` 子进程。 |
| `cache_ttl_seconds` | `300` | 进程内获取结果被重用的时长。设置为 `0` 以禁用缓存。缓存是每个进程的；新的 `hermes` 调用会重新开始。 |
| `override_existing` | `true` | 当为 true 时，Bitwarden 的值会覆盖环境中已存在的任何内容（这样在网页应用中的轮换才能真正生效）。如果你希望 `.env` / shell 导出在本地优先，请翻转为 `false`。 |
| `auto_install` | `true` | 当为 true 时，`bws` 在首次使用时自动下载到 `~/.hermes/bin/`。 |

## 故障模式

Bitwarden 从不阻塞 Hermes 启动。如果出现任何问题，你将在 stderr 中看到一行警告，并且 Hermes 会继续使用 `.env` 中已有的任何凭证：

| 症状 | 原因 | 修复方法 |
|---|---|---|
| `BWS_ACCESS_TOKEN is not set` | 配置中已启用，但令牌已从 `.env` 中清除 | 重新运行 `hermes secrets bitwarden setup` |
| `bws exited 1: invalid access token` | 令牌已撤销或错误 | 生成新令牌，重新运行设置 |
| `[400 Bad Request] {"error":"invalid_client"}` | 令牌是针对 `bws` 正在调用的区域之外的 Bitwarden 区域的（例如，EU 令牌访问 US 身份端点） | 重新运行设置并选择正确的区域，或将 `secrets.bitwarden.server_url` 设置为 `https://vault.bitwarden.eu`（或你的自托管 URL） |
| `bws timed out` | 网络被阻止或 Bitwarden API 缓慢 | 检查到 `api.bitwarden.com`（或你的 `server_url`）的连接性 |
| `bws binary not available` | `auto_install: false` 且 `bws` 不在 PATH 上 | 从 [github.com/bitwarden/sdk-sm/releases](https://github.com/bitwarden/sdk-sm/releases) 手动安装，或将 `auto_install` 翻转为 on |
| `Checksum mismatch` | 下载损坏或被篡改 | 重新运行，将重试；如果持续存在，请提交问题 |

## 安全注意事项

- 引导令牌 (`BWS_ACCESS_TOKEN`) 本身是敏感的——任何拥有它的人都可以读取该机器账户有权访问的每个密钥。请像对待任何其他 API 密钥一样对待它。
- Hermes 将拒绝让 Bitwarden 覆盖引导令牌本身，即使 `override_existing: true`。如果你将 `BWS_ACCESS_TOKEN` 作为密钥存储在项目内，在应用期间它会被静默跳过。
- `bws` 二进制文件下载会与同一 GitHub 版本发布的 SHA-256 校验和进行验证。不匹配会中止安装。
- 固定的版本（撰写本文时为 `bws v2.0.0`）通过对此仓库的 PR 进行更新——Hermes 不会自动将 `bws` 升级到“最新”，因为上游发布形式可能会改变。

## 何时不使用此功能

- **单机个人设置**，其中 `~/.hermes/.env` 就足够了。你是在用一个凭证换取另一个凭证，并在启动时增加了网络依赖。
- **无法访问 `api.bitwarden.com` 的隔离环境**。
- **CI/CD**，其中现有的密钥注入机制（GitHub Actions secrets、Vault 等）已经设置好——选择一种路径，而不是两种。

此功能适用于多机集群、共享开发机、消息网关 VPS，或任何你希望在多个 Hermes 安装之间进行集中轮换和撤销的设置。