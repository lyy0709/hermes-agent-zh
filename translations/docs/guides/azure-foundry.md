---
sidebar_position: 15
title: "Microsoft Foundry"
description: "将 Hermes Agent 与 Microsoft Foundry 结合使用 — 支持 OpenAI 风格和 Anthropic 风格的端点，自动检测传输协议和已部署的模型"
---

# Microsoft Foundry

Hermes Agent 的 `azure-foundry` 提供商支持 Microsoft Foundry（原 Azure AI Foundry）和 Azure OpenAI。单个 Foundry 资源可以托管使用两种不同传输格式的模型：

- **OpenAI 风格** — 在类似 `https://<resource>.openai.azure.com/openai/v1` 的端点上使用 `POST /v1/chat/completions`。用于 GPT-4.x、GPT-5.x、Llama、Mistral 和大多数开源模型。
- **Anthropic 风格** — 在类似 `https://<resource>.services.ai.azure.com/anthropic` 的端点上使用 `POST /v1/messages`。当 Microsoft Foundry 通过 Anthropic Messages API 格式提供 Claude 模型时使用。

设置向导会探测您的端点，并自动检测其使用的传输协议、可用的部署以及每个模型的上下文长度。

## 先决条件

- 一个至少有一个部署的 Microsoft Foundry 或 Azure OpenAI 资源
- 部署的端点 URL
- **要么** 是 API 密钥（来自 Azure 门户中的“密钥和终结点”），**要么** 是 Foundry 资源上的 **Azure AI User** RBAC 角色（如果您计划使用 Microsoft Entra ID，这是 Microsoft 推荐的无密钥路径）。在 Microsoft 重命名推广期间，某些租户可能将角色显示为 **Foundry User**。

## 快速开始

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入您的端点 URL
# → 选择身份验证方式：
#     1. API 密钥
#     2. Microsoft Entra ID  （托管标识 / 工作负载标识 / az login）
# → (Entra) Hermes 探测 DefaultAzureCredential；成功后不再询问密钥
# → (API 密钥) 输入您的 API 密钥
# Hermes 探测端点并自动检测传输协议和模型
# → 从列表中选择一个模型（或手动输入部署名称）
```

向导将执行以下操作：

1.  **嗅探 URL 路径** — 以 `/anthropic` 结尾的 URL 被识别为 Microsoft Foundry Claude 路由。
2.  **探测 `GET <base>/models`** — 如果端点返回 OpenAI 格式的模型列表，Hermes 将切换到 `chat_completions` 模式，并用返回的部署 ID 预填充选择器。
3.  **探测 Anthropic Messages 格式** — 对于不暴露 `/models` 但接受 Anthropic Messages 格式的端点，作为备用方案。
4.  **回退到手动输入** — 拒绝所有探测的私有/受控端点仍然有效；您需要手动选择 API 模式并输入部署名称。

所选模型的上下文长度通过 Hermes 的标准元数据链（`models.dev`、提供商元数据和硬编码的系列回退）解析，并存储在 `config.yaml` 中，以便模型可以正确调整其自身的上下文窗口大小。

## Microsoft Entra ID（无密钥，RBAC）— 推荐

Microsoft 建议生产环境的 Foundry 工作负载使用 [Microsoft Entra ID 的无密钥身份验证](https://learn.microsoft.com/zh-cn/azure/ai-foundry/foundry-models/how-to/configure-entra-id)。Hermes 支持 Entra ID 用于**两种** API 接口：

- **OpenAI 风格** (`api_mode: chat_completions` / `codex_responses`) — GPT-4/5、Llama、Mistral、DeepSeek 等。
- **Anthropic 风格** (`api_mode: anthropic_messages`) — Microsoft Foundry 上的 Claude 模型。

Foundry 的 RBAC 是按资源分配的（`Azure AI User` 授予两种接口权限；某些租户可能显示为 `Foundry User`），并且 Microsoft 为两者记录了相同的推理范围 (`https://ai.azure.com/.default`)。在底层：

- OpenAI 风格使用 OpenAI Python SDK 的原生可调用 `api_key=` 契约 — SDK 会自动为每个请求生成一个新的 JWT。
- Anthropic 风格使用一个安装了请求事件钩子的 `httpx.Client`，该钩子由 `agent.azure_identity_adapter.build_bearer_http_client` 安装，因为 Anthropic SDK 本身不接受可调用的 `auth_token`。该钩子会为每个出站请求重写 `Authorization: Bearer <fresh-jwt>`。相同的 Microsoft RBAC，相同的 Foundry 范围 — 唯一的区别是 SDK 契约。

### 为什么使用 Entra ID？

- 无需轮换或撤销长期存在的 API 密钥。
- 基于 RBAC 的访问控制 — 在 Foundry 资源上授予或移除 `Azure AI User` 角色，无需重写配置。
- 访问和审计日志按分配对象分段，而不是所有调用者共享一个静态密钥。
- 通过托管标识，为 Azure VM、AKS Pod、App Service、Functions、Container Apps 和 Foundry Agent Service 提供单一的身份验证接口。
- 为 CI/CD 流水线提供工作负载标识和服务主体流程。

### 一次性设置（Azure 端）

1.  在 Azure 门户中，打开您的 Foundry 资源 → **访问控制 (IAM)** → **添加 → 添加角色分配**。
2.  选择 **Azure AI User** 角色（如果您的租户已重命名该角色，则选择 **Foundry User**）。
3.  将其分配给：
    - **您的用户帐户**，用于通过 `az login` 进行本地开发。
    - **托管标识或工作负载标识**，用于 Azure 托管的计算资源（生产环境推荐）。
    - **Foundry Agent Service 托管 Agent 的 Agent 标识**，当 Hermes 在托管 Agent 内运行时。
    - **服务主体**，用于 CI/CD 流水线（当工作负载标识不可用时）。
4.  等待约 5 分钟，让角色生效。

Azure CLI 等效命令：

```bash
az role assignment create \
  --assignee <principal-or-agent-identity-client-id> \
  --role "Azure AI User" \
  --scope <foundry-resource-id>
```

### 一次性设置（Hermes 端）

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入您的端点 URL
# → 身份验证：2 (Microsoft Entra ID)
# → (可选) 用户分配的托管标识客户端 ID
# → (可选) Azure 租户 ID
# → Hermes 探测 DefaultAzureCredential() 并报告哪个内部
#    凭据成功（例如 AzureCliCredential、ManagedIdentityCredential）
```

向导运行一个有限制的预检探测（10 秒超时）。如果失败，它会提供“仍然保存，稍后验证”的选项 — 这在配置尚未拥有凭据但将在运行时拥有凭据的机器时很有用（例如，为托管标识部署准备配置）。

`azure-identity` 在首次使用时通过 Hermes 的延迟安装路径自动安装。要预安装：

```bash
pip install azure-identity
```
### 配置已写入 `config.yaml`

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  auth_mode: entra_id
  default: gpt-4o
  context_length: 128000
  entra:
    scope: https://ai.azure.com/.default        # 仅在需要覆盖默认值时设置
```

Hermes 在 `config.yaml` 中仅管理一个与 Entra 相关的配置项：

- **`scope`** — OAuth 资源范围。默认为 Microsoft 文档中记录的推理范围 (`https://ai.azure.com/.default`)。仅当你的资源是针对非标准受众配置时才需要覆盖此值。

其他所有内容（租户、服务主体密钥、联合令牌文件、主权云颁发机构、代理首选项）都由 `azure-identity` 直接从标准的 `AZURE_*` 环境变量中读取 — 请参阅下面的[凭据解析顺序](#credential-resolution-order)。请按照 Microsoft SDK 参考文档的描述，在 `~/.hermes/.env` 或你的部署环境中设置这些变量。

对于 Entra 模式，`~/.hermes/.env` 中不存储任何密钥 — `azure-identity` 会在进程内（并在可用时，在你的操作系统密钥链 / `~/.IdentityService` 中）缓存令牌。

### 凭据解析顺序

`azure-identity` 的 `DefaultAzureCredential` 在每次令牌请求时按此链式顺序查找，并在第一个返回令牌的凭据处停止：

1.  **环境凭据** — `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET`（或 `AZURE_CLIENT_CERTIFICATE_PATH` / `AZURE_FEDERATED_TOKEN_FILE`）。
2.  **工作负载标识** — `AZURE_FEDERATED_TOKEN_FILE`（AKS 联合令牌 / OIDC）。
3.  **托管标识** — 虚拟机的 IMDS 端点 (`169.254.169.254`)；应用服务 / Functions / 容器应用的 `IDENTITY_ENDPOINT`。Foundry Agent Service 托管的 Agent 使用托管 Agent 的 Agent 身份。
4.  **Visual Studio Code** — Azure 账户扩展。
5.  **Azure CLI** — `az login` 会话。
6.  **Azure Developer CLI** — `azd auth login`。
7.  **Azure PowerShell** — `Connect-AzAccount`。
8.  **代理**（仅限 Windows / WSL）— Web 账户管理器。

对于无人值守的 Hermes 运行，默认排除交互式浏览器凭据；请改用 Azure CLI、Azure Developer CLI、托管标识、工作负载标识或服务主体凭据。

### 部署模式

**本地开发：**
```bash
az login
hermes model   # 选择 Azure Foundry → Entra ID
hermes         # 使用你的 az login 令牌
```

**Azure VM / Functions / App Service / 容器应用（系统分配的托管标识）：**
1.  在计算资源上启用系统分配的标识。
2.  在 Foundry 资源上授予该标识 `Azure AI User`（或 `Foundry User`）角色。
3.  在 config.yaml 中设置 `model.auth_mode: entra_id` — 无需环境变量。

**Azure VM / Functions / App Service / 容器应用（用户分配的托管标识）：**
- 将 `AZURE_CLIENT_ID` 设置为用户分配标识的客户端 ID，以便 `DefaultAzureCredential` 选择正确的标识。

**Foundry Agent Service 托管 Agent：**
- 创建托管 Agent 并在 Foundry 资源上授予该 Agent 的身份 `Azure AI User`（或 `Foundry User`）角色。Hermes 在托管 Agent 内部使用 `ManagedIdentityCredential`；角色分配应授予 Agent 身份，而不仅仅是父项目或你的用户。

**AKS 工作负载标识（替代 AAD Pod 标识）：**
- 使用工作负载标识客户端 ID 注解 Pod 的服务账户。
- Pod 的联合令牌文件通过 `AZURE_FEDERATED_TOKEN_FILE` 自动检测。
- `model.auth_mode: entra_id` 无需进一步配置更改即可工作。

**CI 中的服务主体：**
- 在运行器环境中设置 `AZURE_TENANT_ID`、`AZURE_CLIENT_ID`、`AZURE_CLIENT_SECRET`。

#### 主权云（政府、中国）

导出 `AZURE_AUTHORITY_HOST`（例如，Azure Government 为 `https://login.microsoftonline.us`，Azure 中国为 `https://login.partner.microsoftonline.cn`）。`azure-identity` 会直接读取它。

### 健康检查

当 `model.auth_mode: entra_id` 时，`hermes doctor` 会对 `DefaultAzureCredential` 运行一个 10 秒的探测，报告哪个内部凭据胜出（环境变量存在、托管标识端点可达等）。

`hermes auth` 显示一个结构化的状态块：

```
azure-foundry (Microsoft Entra ID):
  Endpoint: https://my-resource.openai.azure.com/openai/v1
  Scope: https://ai.azure.com/.default
  Status: configured; live token probe is skipped here
```

### 限制

-   **Anthropic 风格端点使用 httpx 事件钩子。** Anthropic Python SDK 本身不接受可调用的 `auth_token`（≤ 0.86.0）。Hermes 在自定义的 `httpx.Client` 上安装了一个请求事件钩子，该钩子为每个出站请求生成一个新的 JWT 并重写 `Authorization: Bearer <jwt>`。这在功能上等同于 OpenAI SDK 原生的 `Callable[[], str]` 契约，但增加了一个间接层。如果 Anthropic SDK 在未来的版本中添加了一流的可调用身份验证支持，Hermes 将透明地切换到它。
-   **批量作业和 `multiprocessing.Pool`。** Entra 令牌提供程序是一个闭包，无法跨进程边界进行 pickle 序列化。`batch_runner.py` 会自动从工作进程配置中删除该可调用对象，并让每个工作进程从 `config.yaml` 重建自己的提供程序 — 无需用户操作，但每个工作进程在启动时需要支付一次链式查找的开销。
-   **`auth.json` 中不持久化承载者 JWT。** Hermes 不会复制 `azure-identity` 的内部令牌缓存；冷启动会在第一次推理时执行凭据链式查找。

## 配置（写入 `config.yaml`）

运行向导后，你将看到类似以下内容：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions         # 或 "anthropic_messages"
  default: gpt-5.4-mini              # 你的部署 / 模型名称
  context_length: 400000             # 自动检测
```

在 `~/.hermes/.env` 中：

```
AZURE_FOUNDRY_API_KEY=<your-azure-key>
```

## OpenAI 风格端点（GPT、Llama 等）

Azure OpenAI 的 v1 GA 端点接受标准的 `openai` Python 客户端，只需极少的改动：
```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5.4
```

重要行为：

- **GPT-5.x、codex 和 o 系列模型会自动路由到 Responses API。** Microsoft Foundry 将 GPT-5 / codex / o1 / o3 / o4 模型部署为仅支持 Responses API —— 对它们调用 `/chat/completions` 会返回 `400 "The requested operation is unsupported."`。Hermes 通过模型名称检测这些模型系列，并透明地将 `api_mode` 升级为 `codex_responses`，即使 `config.yaml` 中仍显示 `api_mode: chat_completions`。GPT-4、GPT-4o、Llama、Mistral 和其他部署则保持使用 `/chat/completions`。
- **自动使用 `max_completion_tokens`。** Azure OpenAI（与直接使用 OpenAI 类似）要求为 gpt-4o、o 系列和 gpt-5.x 模型提供 `max_completion_tokens` 参数。Hermes 会根据端点发送正确的参数。
- **需要 `api-version` 的 v1 之前版本端点。** 如果你有一个遗留的基础 URL，例如 `https://<resource>.openai.azure.com/openai?api-version=2025-04-01-preview`，Hermes 会提取查询字符串并通过每个请求的 `default_query` 转发它（否则 OpenAI SDK 在拼接路径时会丢弃它）。

## Anthropic 风格端点（通过 Microsoft Foundry 的 Claude）

对于 Claude 部署，请使用 Anthropic 风格的路由：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_mode: anthropic_messages
  default: claude-sonnet-4-6
```

重要行为：

- **从基础 URL 中移除 `/v1`。** Anthropic SDK 会在每个请求 URL 后追加 `/v1/messages` —— Hermes 在将 URL 交给 SDK 之前会移除任何尾随的 `/v1`，以避免出现重复的 `/v1` 路径。
- **`api-version` 通过 `default_query` 发送，而不是追加到 URL。** Azure Anthropic 需要一个 `api-version` 查询字符串。将其硬编码到基础 URL 中会产生格式错误的路径，如 `/anthropic?api-version=.../v1/messages` 并返回 404。Hermes 改为通过 Anthropic SDK 的 `default_query` 传递 `api-version=2025-04-15`。
- **使用 Bearer 认证而非 `x-api-key`。** Azure 的 Anthropic 兼容路由要求 `Authorization: Bearer <key>` 头，而不是 Anthropic 原生的 `x-api-key` 头。Hermes 检测到基础 URL 中包含 `azure.com`，并通过 SDK 的 `auth_token` 字段路由 API 密钥，以便正确的请求头到达上游。
- **保留 100 万上下文窗口 Beta 头。** Azure 仍将 100 万 Token 的 Claude 上下文（Opus 4.6/4.7, Sonnet 4.6）置于 `anthropic-beta: context-1m-2025-08-07` 请求头之后。Hermes 在 Azure 路径上保留该 Beta 头（在原生 Anthropic OAuth 请求中会移除该头，因为某些订阅会拒绝它，但 Azure 需要它）。
- **禁用 OAuth Token 刷新。** Azure 部署使用静态 API 密钥。适用于 Anthropic Console 的 `~/.claude/.credentials.json` OAuth Token 刷新循环会为 Azure 端点显式跳过，以防止 Claude Code OAuth Token 在会话中途覆盖你的 Azure 密钥。

## 替代方案：`provider: anthropic` + Azure 基础 URL

如果你已经配置了 `provider: anthropic`，并且只想将其指向 Microsoft Foundry 以使用 Claude，你可以完全跳过 `azure-foundry` 提供商：

```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  key_env: AZURE_ANTHROPIC_KEY
  default: claude-sonnet-4-6
```

在 `~/.hermes/.env` 中设置 `AZURE_ANTHROPIC_KEY`。Hermes 检测到基础 URL 中包含 `azure.com`，并绕过 Claude Code OAuth Token 链，以便直接使用 Azure 密钥进行 `x-api-key` 认证。

`key_env` 是规范的 snake_case 字段名；`api_key_env`（以及 camelCase 的 `keyEnv` / `apiKeyEnv`）作为别名也被接受。如果同时设置了 `key_env` 和 `AZURE_ANTHROPIC_KEY`/`ANTHROPIC_API_KEY`，则以 `key_env` 命名的环境变量优先。

## 模型发现

Azure **不** 暴露一个纯 API 密钥端点来列出你*已部署*的模型部署。部署枚举需要 Azure Resource Manager 认证（`az cognitiveservices account deployment list`）和 Azure AD 主体，而不是推理 API 密钥。

Hermes 可以做到：

- Azure OpenAI v1 端点（`<resource>.openai.azure.com/openai/v1`）通过 `GET /models` 暴露资源的**可用**模型目录。Hermes 使用此列表来预填充模型选择器。
- Microsoft Foundry `/anthropic` 路由：通过 URL 路径检测，模型名称手动输入。
- 私有 / 防火墙后的端点：手动输入，并显示友好的“无法探测”消息。

你始终可以直接输入部署名称 —— Hermes 不会根据返回的列表进行验证。

## 环境变量

| 变量 | 用途 |
|----------|---------|
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI 的主要 API 密钥（api_key 模式） |
| `AZURE_FOUNDRY_BASE_URL` | 端点 URL（通过 `hermes model` 设置；环境变量用作后备） |
| `AZURE_ANTHROPIC_KEY` | 被 `provider: anthropic` + Azure 基础 URL 使用（替代 `ANTHROPIC_API_KEY`） |
| `AZURE_TENANT_ID` | 用于服务主体流的 Entra ID 租户 |
| `AZURE_CLIENT_ID` | Entra ID 客户端 ID（服务主体、工作负载身份或用户分配的托管身份） |
| `AZURE_CLIENT_SECRET` | 服务主体密钥 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书（密钥的替代方案） |
| `AZURE_FEDERATED_TOKEN_FILE` | 工作负载身份联合 Token 路径（AKS） |
| `AZURE_AUTHORITY_HOST` | 主权云授权主机覆盖 |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | 用于应用服务、函数和容器应用的托管身份端点；VM 通常使用 IMDS |

Azure SDK 直接读取 `AZURE_*` 环境变量。除了在 `hermes doctor` 输出中报告存在哪些源之外，Hermes 从不检查它们。

## 故障排除

**在 gpt-5.x 部署上出现 401 未授权。**
Azure 在 `/chat/completions` 上提供 gpt-5.x，而不是 `/responses`。当 URL 包含 `openai.azure.com` 时，Hermes 会自动处理此问题，但如果你看到带有 `Invalid API key` 正文的 401 错误，请检查 `config.yaml` 中的 `api_mode` 是否为 `chat_completions`。
**访问 `/v1/messages?api-version=.../v1/messages` 时出现 404 错误。**
这是修复前 Azure Anthropic 配置中存在的 URL 格式错误问题。请升级 Hermes —— `api-version` 参数现在通过 `default_query` 传递，而不是硬编码在基础 URL 中，因此 SDK 在 URL 拼接时不会破坏它。

**向导提示“自动检测不完整”。**
端点同时拒绝了 `/models` 探测和 Anthropic Messages 探测。这对于位于防火墙后或具有 IP 白名单的私有端点来说是正常现象。请回退到手动 API 模式选择，并输入您的部署名称 —— 一切仍可正常工作，只是 Hermes 无法预填充选择器。

**选择了错误的传输模式。**
再次运行 `hermes model`，向导将重新探测。如果探测仍然选择了错误的模式，您可以直接编辑 `config.yaml`：

```yaml
model:
  provider: azure-foundry
  api_mode: anthropic_messages   # 或 chat_completions
```

**Entra ID：切换到 `auth_mode: entra_id` 后，出现“凭据链已用尽”或 401 未授权错误。**
- 运行 `az login` 以刷新您的开发者会话（缓存的 Token 可能已过期）。
- 验证 `Azure AI User`（或 `Foundry User`）角色分配是否生效：运行 `az role assignment list --assignee <用户或身份标识>` 应能在您的 Foundry 资源上列出该角色。角色传播最多可能需要 5 分钟。
- 对于用户分配的托管身份，请仔细检查 `AZURE_CLIENT_ID` 是否与附加到计算资源的身份匹配。
- 运行 `hermes doctor` —— Azure Entra 探测会报告 Token 获取是否成功，并包含修复提示。

**Entra ID：向导预检挂起或超时。**
10 秒的预检是一个软检查。选择“无论如何保存，稍后验证”，并在部署到目标环境后运行 `hermes doctor`。常见原因包括无法访问的 Token 服务或过期的本地登录状态 —— 在 CI 中建议使用工作负载身份，使用服务主体时设置 `AZURE_TENANT_ID`+`AZURE_CLIENT_ID`+`AZURE_CLIENT_SECRET`，或在本地开发时运行 `az login`。

**使用 Entra ID 访问 Anthropic 风格端点时出现 401 错误。**
验证 Foundry 资源上是否分配了相同的 `Azure AI User`（或 `Foundry User`）角色（该角色同时涵盖 `/openai/v1` 和 `/anthropic` 路径）。如果向导期间 OpenAI 风格的探测有效，但运行时 `claude-*` 请求失败，最常见的原因是早期向导运行后残留的过时 `model.entra.scope` —— 从 `config.yaml` 中删除 `entra.scope` 行，以便运行时回退到默认的 `https://ai.azure.com/.default` 作用域。

## 相关链接

- [环境变量](/reference/environment-variables)
- [配置](/user-guide/configuration)
- [AWS Bedrock](/guides/aws-bedrock) —— 另一项主要的云提供商集成
- [Microsoft: 为 Foundry 配置 Entra ID](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id) —— 无密钥路径的上游文档