---
title: "注册 Microsoft Graph 应用程序"
description: "通过 Azure 门户创建为 Teams 会议流水线提供支持的应用程序注册"
---

# 注册 Microsoft Graph 应用程序

Teams 会议流水线使用**仅应用**（守护进程）身份验证从 Microsoft Graph 读取会议转录、录制和相关文件——无需用户登录，也无需每次会议进行交互式同意。这需要一个已获得管理员同意的应用程序权限的 Azure AD 应用程序注册。

本指南将逐步介绍：

1.  创建应用程序注册
2.  创建客户端密钥
3.  授予流水线所需的 Graph API 权限
4.  管理员同意这些权限
5.  （可选）使用应用程序访问策略将应用范围限定到特定用户

您需要**租户管理员权限**（或由管理员代表您授予同意）才能完成此操作。请记下您收集的值——它们最终将填入 `~/.hermes/.env` 文件中。

## 先决条件

-   一个拥有 Teams Premium 或能生成会议转录和录制的 Teams 许可证的 Microsoft 365 租户
-   对 [entra.microsoft.com](https://entra.microsoft.com) 上的 Azure 门户的管理员访问权限
-   一个 Graph 变更通知可公开访问的 HTTPS 端点（稍后在 Webhook 监听器步骤中设置）

## 步骤 1：创建应用程序注册

1.  以租户管理员身份登录 [entra.microsoft.com](https://entra.microsoft.com)。
2.  导航到 **标识 → 应用程序 → 应用注册**。
3.  点击 **新注册**。
4.  填写：
    -   **名称：** `Hermes Teams Meeting Pipeline`（或任何您能识别的名称）。
    -   **支持的帐户类型：** *仅此组织目录中的帐户（单租户）*。
    -   **重定向 URI：** 留空——仅应用身份验证不需要此字段。
5.  点击 **注册**。

您将进入应用的概览页面。复制两个值：

-   **应用程序（客户端）ID** → `MSGRAPH_CLIENT_ID`
-   **目录（租户）ID** → `MSGRAPH_TENANT_ID`

## 步骤 2：创建客户端密钥

1.  在左侧导航栏中，打开 **证书和密码**。
2.  点击 **新客户端密码**。
3.  **说明：** `hermes-graph-secret`。**过期时间：** 选择符合您轮换策略的值（通常为 6-24 个月）。
4.  点击 **添加**。
5.  立即复制 **值** 列——它只显示一次。该值就是 `MSGRAPH_CLIENT_SECRET`。

> **密码 ID** 列不是密钥。您需要的是 **值** 列。

## 步骤 3：授予 Graph API 权限

流水线使用一组最小可行的应用程序权限。仅添加您需要的权限；每个权限都会扩大应用在整个租户内的读取能力。

1.  在左侧导航栏中，打开 **API 权限**。
2.  点击 **添加权限** → **Microsoft Graph** → **应用程序权限**。
3.  添加下表中与您希望流水线执行的操作相匹配的权限。
4.  添加后，点击 **为 `<您的租户>` 授予管理员同意**。状态列应为每个权限显示绿色勾选标记。

### 转录优先摘要所需的权限

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `OnlineMeetings.Read.All` | 读取 Teams 在线会议元数据（主题、参与者、加入 URL）。 |
| `OnlineMeetingTranscript.Read.All` | 读取 Teams 生成的会议转录。 |

### 回退到录制（当转录不可用时）所需的权限

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `OnlineMeetingRecording.Read.All` | 下载 Teams 会议录制文件以进行离线 STT 处理。 |
| `CallRecords.Read.All` | 当仅知道加入 URL 时，从通话记录中解析会议。 |

### 出站摘要交付所需的权限（仅限 Graph 模式）

如果 `platforms.teams.extra.delivery_mode` 设置为 `graph`，流水线将通过 Graph API 将摘要发布到 Teams 频道或聊天中。如果您使用 `incoming_webhook` 交付模式，请跳过这些。

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `ChannelMessage.Send` | 代表应用向 Teams 频道发布消息。 |
| `Chat.ReadWrite.All` | 向 1:1 和群组聊天发布消息（仅当您将 `chat_id` 设置为交付目标时）。 |

### 不推荐的权限

-   `OnlineMeetings.ReadWrite.All` / 不带 `.All` 的 `Chat.ReadWrite` —— 比流水线需要的范围更广。
-   委派权限 —— 流水线使用仅应用（客户端凭据）流程；没有用户登录，委派权限将无法工作。

## 步骤 4：（推荐）使用应用程序访问策略限定应用范围

默认情况下，像 `OnlineMeetings.Read.All` 这样的应用程序权限授予应用访问租户中**每个**会议的权限。对于合作伙伴演示和开发租户来说，这没问题；但对于生产环境，您几乎肯定希望限制应用可以读取哪些用户的会议。

Microsoft 为此专门为 Teams 提供了**应用程序访问策略**。该策略仅通过 PowerShell 界面管理；门户没有相关 UI。

在已安装 MicrosoftTeams 模块并已连接（`Connect-MicrosoftTeams`）的管理员 PowerShell 中执行：

```powershell
# 创建一个限定 Hermes 应用范围的策略
New-CsApplicationAccessPolicy `
  -Identity "Hermes-Meeting-Pipeline-Policy" `
  -AppIds "<MSGRAPH_CLIENT_ID>" `
  -Description "将 Hermes 会议流水线限制为允许列表中的用户"

# 将策略授予流水线可以读取其会议的特定用户
Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "alice@example.com"

Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "bob@example.com"
```

授予后，传播最多可能需要 30 分钟。使用以下命令验证：

```powershell
Test-CsApplicationAccessPolicy -Identity "alice@example.com" -AppId "<MSGRAPH_CLIENT_ID>"
```

如果没有此策略，**任何**用户的会议都是可读的——这是该权限在技术上授予的权限。在生产租户上不要跳过此步骤。

## 步骤 5：将凭据写入您的环境变量文件

将您收集的三个值放入 `~/.hermes/.env`：

```bash
MSGRAPH_TENANT_ID=<directory-tenant-id>
MSGRAPH_CLIENT_ID=<application-client-id>
MSGRAPH_CLIENT_SECRET=<client-secret-value>
```

设置文件权限，确保只有您可以读取密钥：

```bash
chmod 600 ~/.hermes/.env
```

## 步骤 6：验证令牌流程

Hermes 附带了一个 Graph 身份验证冒烟测试。在您的 Hermes 安装目录下运行：

```python
python -c "
import asyncio
from tools.microsoft_graph_auth import MicrosoftGraphTokenProvider
provider = MicrosoftGraphTokenProvider.from_env()
token = asyncio.run(provider.get_access_token())
print('Token acquired, length:', len(token))
print(provider.inspect_token_health())
"
```

成功运行会打印一个长令牌字符串和一个健康字典，显示 `cached: True` 和接近 3600 的 `expires_in_seconds` 值。失败会产生一个带有 Azure 错误代码的 `MicrosoftGraphTokenError` —— 最常见的是：

| Azure 错误 | 含义 | 修复方法 |
|-------------|---------|-----|
| `AADSTS7000215: Invalid client secret` | 密钥值不匹配或已过期。 | 在步骤 2 中生成新密钥；更新 `.env`。 |
| `AADSTS700016: Application not found` | 错误的 `MSGRAPH_CLIENT_ID` 或错误的租户。 | 再次检查步骤 1 中的值是否来自同一个应用。 |
| `AADSTS90002: Tenant not found` | `MSGRAPH_TENANT_ID` 拼写错误。 | 再次从应用概览复制目录（租户）ID。 |
| 调用时（非令牌获取时）出现 `insufficient_claims` | 令牌获取成功但 Graph 返回 401/403。 | 您跳过了步骤 3 的管理员同意，或者添加了权限但未重新同意。请重新访问 API 权限并再次点击 **授予管理员同意**。 |

## 轮换客户端密钥

Azure 客户端密钥有硬性过期时间。在您的密钥过期之前：

1.  在步骤 2 中创建第二个客户端密钥，不要删除第一个。
2.  使用新值更新 `~/.hermes/.env` 中的 `MSGRAPH_CLIENT_SECRET`。
3.  重启消息网关以获取新密钥：`hermes gateway restart`。
4.  使用上面的冒烟测试进行验证。
5.  从 Azure 门户删除旧密钥。

## 后续步骤

一旦凭据验证无误，请继续：

-   **Webhook 监听器设置** —— 启动接收 Graph 变更通知的 `msgraph_webhook` 消息网关平台。
-   **流水线配置** —— 配置 Teams 会议流水线运行时和操作员 CLI。
-   **出站交付** —— 将摘要发送回 Teams 频道或聊天。

这些页面对应于添加相应运行时的 PR。此凭据设置是一个独立的先决条件，可以安全地提前完成。