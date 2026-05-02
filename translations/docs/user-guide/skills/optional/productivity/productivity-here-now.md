---
title: "Here.Now — 将静态站点发布到 {slug}"
sidebar_label: "Here.Now"
description: "将静态站点发布到 {slug}"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Here.Now

将静态站点发布到 &#123;slug&#125;.here.now，并将私有文件存储在云端 Drives 中，以便进行 Agent 间交接。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/here-now` 安装 |
| 路径 | `optional-skills/productivity/here-now` |
| 版本 | `1.15.3` |
| 作者 | here.now |
| 许可证 | MIT |
| 平台 | macos, linux |
| 标签 | `here.now`, `herenow`, `publish`, `deploy`, `hosting`, `static-site`, `web`, `share`, `URL`, `drive`, `storage` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# here.now

here.now 允许 Agent 发布网站并将私有文件存储在云端 Drives 中。

here.now 用于两项工作：

- **站点**：在 `{slug}.here.now` 发布网站和文件。
- **Drives**：在云端文件夹中存储私有 Agent 文件。

## 当前文档

**在回答有关 here.now 功能、特性或工作流的问题之前，请阅读当前文档：**

→ **https://here.now/docs**

在以下情况阅读文档：

- 在对话中首次出现与 here.now 相关的交互时
- 任何时候用户询问如何做某事时
- 任何时候用户询问什么是可能的、受支持的或推荐的时
- 在告诉用户某个功能不受支持之前

需要参考当前文档的主题（不要仅依赖本地技能文本）：

- Drives 和 Drive 共享
- 自定义域名
- 支付和支付门控
- 分叉
- 代理路由和服务变量
- 句柄和链接
- 限制和配额
- SPA 路由
- 错误处理和补救
- 功能可用性

**如果文档与实时 API 行为不一致，请信任实时 API 行为。**

如果文档获取失败或超时，请继续使用本地技能和实时 API/脚本输出。对于主动操作，优先信任实时 API 行为。

## 要求

- 必需的二进制文件：`curl`, `file`, `jq`
- 可选环境变量：`$HERENOW_API_KEY`
- 可选 Drive Token 变量：`$HERENOW_DRIVE_TOKEN`
- 可选凭据文件：`~/.herenow/credentials`
- 技能助手路径：
  - `${HERMES_SKILL_DIR}/scripts/publish.sh` 用于发布站点
  - `${HERMES_SKILL_DIR}/scripts/drive.sh` 用于私有 Drive 存储

## 创建站点

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --client hermes
```

输出实时 URL（例如 `https://bright-canvas-a7k2.here.now/`）。

底层实现是一个三步流程：创建/更新 -> 上传文件 -> 完成。站点在完成步骤成功之前不会上线。

没有 API 密钥时，这会创建一个**匿名站点**，该站点在 24 小时后过期。
使用已保存的 API 密钥时，站点是永久性的。

**文件结构**：对于 HTML 站点，请将 `index.html` 放在要发布的目录的根目录下，而不是子目录内。目录的内容将成为站点根目录。例如，发布 `my-site/`，其中 `my-site/index.html` 存在——不要发布包含 `my-site/` 的父文件夹。

您也可以发布没有任何 HTML 的原始文件。单个文件会获得一个丰富的自动查看器（图像、PDF、视频、音频）。多个文件会获得一个自动生成的目录列表，包含文件夹导航和图片库。

## 更新现有站点

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --slug {slug} --client hermes
```

更新匿名站点时，脚本会自动从 `.herenow/state.json` 加载 `claimToken`。传递 `--claim-token {token}` 以覆盖。

经过身份验证的更新需要已保存的 API 密钥。

## 使用 Drive

当用户希望为 Agent 文件（文档、上下文、记忆、计划、资产、媒体、研究、代码以及任何其他应持久保存但不应作为网站发布的内容）提供私有云存储时，请使用 Drive。

每个已登录的账户都有一个名为 `My Drive` 的默认 Drive。

```bash
DRIVE="${HERMES_SKILL_DIR}/scripts/drive.sh"
bash "$DRIVE" default
bash "$DRIVE" ls "My Drive"
bash "$DRIVE" put "My Drive" notes/today.md --from ./notes/today.md
bash "$DRIVE" cat "My Drive" notes/today.md
bash "$DRIVE" share "My Drive" --perms write --prefix notes/ --ttl 7d
```

使用作用域受限的 Drive Token 进行 Agent 间交接。如果您收到一个 `herenow_drive` 共享块，请将其 `token` 用作 `Authorization: Bearer <token>` 来访问 `api_base`，存在 `pathPrefix` 时请遵守它，并在写入时保留 ETag。`pathPrefix` 为 `null` 表示对整个 Drive 的访问。如果技能可用，请优先使用 `drive.sh`；否则直接调用列出的 API 操作。

## API 密钥存储

发布脚本从以下来源读取 API 密钥（首次匹配成功即停止）：

1. `--api-key {key}` 标志（仅限 CI/脚本编写——避免在交互式使用中使用）
2. `$HERENOW_API_KEY` 环境变量
3. `~/.herenow/credentials` 文件（推荐用于 Agent）

要存储密钥，请将其写入凭据文件：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

**重要提示**：收到 API 密钥后，请立即保存——自己运行上述命令。不要要求用户手动运行它。在交互式会话中避免通过 CLI 标志（例如 `--api-key`）传递密钥；凭据文件是首选的存储方法。

切勿将凭据或本地状态文件（`~/.herenow/credentials`, `.herenow/state.json`）提交到源代码控制。

## 获取 API 密钥

要从匿名（24 小时）站点升级为永久站点：

1. 向用户询问他们的电子邮件地址。
2. 请求一次性登录代码：

```bash
curl -sS https://here.now/api/auth/agent/request-code \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

3. 告诉用户：“请检查您的收件箱，查找来自 here.now 的登录代码，并将其粘贴到这里。”
4. 验证代码并获取 API 密钥：

```bash
curl -sS https://here.now/api/auth/agent/verify-code \
  -H "content-type: application/json" \
  -d '{"email":"user@example.com","code":"ABCD-2345"}'
```

5. 自己保存返回的 `apiKey`（不要要求用户这样做）：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

## 状态文件

每次站点创建/更新后，脚本会将信息写入工作目录中的 `.herenow/state.json`：

```json
{
  "publishes": {
    "bright-canvas-a7k2": {
      "siteUrl": "https://bright-canvas-a7k2.here.now/",
      "claimToken": "abc123",
      "claimUrl": "https://here.now/claim?slug=bright-canvas-a7k2&token=abc123",
      "expiresAt": "2026-02-18T01:00:00.000Z"
    }
  }
}
```

在创建或更新站点之前，您可以检查此文件以查找先前的 slug。
请将 `.herenow/state.json` 仅视为内部缓存。
切勿将此本地文件路径作为 URL 呈现，也切勿将其用作身份验证模式、过期时间或认领 URL 的真实来源。

## 告知用户的内容

对于已发布的站点：

- 始终分享当前脚本运行的 `siteUrl`。
- 读取并遵循脚本 stderr 中的 `publish_result.*` 行来确定身份验证模式。
- 当 `publish_result.auth_mode=authenticated` 时：告诉用户站点是**永久性**的，并已保存到他们的账户。不需要认领 URL。
- 当 `publish_result.auth_mode=anonymous` 时：告诉用户站点**将在 24 小时后过期**。分享认领 URL（如果 `publish_result.claim_url` 非空且以 `https://` 开头），以便他们可以永久保留它。警告认领 Token 仅返回一次且无法恢复。
- 切勿告诉用户检查 `.herenow/state.json` 以获取认领 URL 或身份验证状态。

对于 Drives：

- 不要将 Drive 文件描述为公共 URL。
- 告诉用户 Drive 内容是私有的，除非使用作用域受限的 Token 共享。
- 与其他 Agent 共享访问权限时，优先使用具有狭窄 `pathPrefix` 和短 TTL 的作用域受限 Token。

## publish.sh 选项

| 标志                   | 描述                                  |
| ---------------------- | -------------------------------------------- |
| `--slug {slug}`        | 更新现有站点而不是创建新站点 |
| `--claim-token {token}`| 覆盖匿名更新的认领 Token    |
| `--title {text}`       | 查看器标题（非 HTML 站点）             |
| `--description {text}` | 查看器描述                            |
| `--ttl {seconds}`      | 设置过期时间（仅限已验证身份）               |
| `--client {name}`      | 用于归属的 Agent 名称（例如 `hermes`）    |
| `--base-url {url}`     | API 基础 URL（默认：`https://here.now`）    |
| `--allow-nonherenow-base-url` | 允许将身份验证发送到非默认的 `--base-url` |
| `--api-key {key}`      | API 密钥覆盖（优先使用凭据文件）    |
| `--spa`                | 启用 SPA 路由（为未知路径提供 index.html） |
| `--forkable`           | 允许其他人分叉此站点                           |

## 超越 publish.sh

对于 Drive 操作，请使用 `drive.sh` 或 Drive API。对于更广泛的账户和站点管理——删除、元数据、密码、支付、域名、句柄、链接、变量、代理路由、分叉、复制等——请参阅当前文档：

→ **https://here.now/docs**

完整文档：https://here.now/docs