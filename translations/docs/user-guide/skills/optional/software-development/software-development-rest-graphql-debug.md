---
title: "Rest Graphql Debug — 调试 REST/GraphQL API：状态码、认证、模式、复现"
sidebar_label: "Rest Graphql Debug"
description: "调试 REST/GraphQL API：状态码、认证、模式、复现"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Rest Graphql Debug

调试 REST/GraphQL API：状态码、认证、模式、复现。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/software-development/rest-graphql-debug` 安装 |
| 路径 | `optional-skills/software-development/rest-graphql-debug` |
| 版本 | `1.2.0` |
| 作者 | eren-karakus0 |
| 许可证 | MIT |
| 标签 | `api`, `rest`, `graphql`, `http`, `debugging`, `testing`, `curl`, `integration` |
| 相关技能 | [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# API 测试与调试

通过 Hermes 工具驱动 REST 和 GraphQL 诊断 — 使用 `terminal` 执行 `curl`，使用 `execute_code` 执行 Python `requests`，使用 `web_extract` 获取供应商文档。在猜测修复方案之前，先隔离故障层。

## 使用时机

- API 返回意外的状态码或响应体
- 认证失败（令牌刷新后出现 401/403、OAuth、API 密钥问题）
- 在 Postman 中工作正常但在代码中失败
- Webhook / 回调集成调试
- 构建或审查 API 集成测试
- 速率限制或分页问题

对于 UI 渲染、数据库查询调优或 DNS/防火墙基础设施问题，请跳过（并上报）。

## 核心原则

**先隔离层，再修复。** 一个 200 OK 可能隐藏着损坏的数据。一个 500 错误可能掩盖了一个字符的认证拼写错误。按顺序检查链路；切勿跳过任何步骤。

```
1. 连通性   → 我们能否访问到主机？
1.5 超时      → 是连接慢还是读取慢？
2. TLS/SSL    → 证书是否有效且受信任？
3. 认证       → 凭据是否正确且未过期？
4. 请求格式   → 负载结构是否符合服务器预期？
5. 响应解析   → 我们的代码是否接受返回的内容？
6. 语义       → 数据的含义是否符合我们的假设？
```

## 5 分钟快速入门

### 通过终端调试 REST

```python
# 详细的请求/响应交换
terminal('curl -v https://api.example.com/users/1')

# 发送 JSON 的 POST 请求
terminal("""curl -X POST https://api.example.com/users \\
  -H 'Content-Type: application/json' \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"name":"test","email":"test@example.com"}'""")

# 仅获取响应头
terminal('curl -sI https://api.example.com/health')

# 美化打印 JSON
terminal('curl -s https://api.example.com/users | python3 -m json.tool')
```

### 通过终端调试 GraphQL

```python
terminal("""curl -X POST https://api.example.com/graphql \\
  -H 'Content-Type: application/json' \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"query":"{ user(id: 1) { name email } }"}'""")
```

**GraphQL 陷阱：** 即使查询失败，服务器也经常返回 HTTP 200。无论状态码如何，始终检查 `errors` 字段：

```python
execute_code('''
import os, requests
resp = requests.post(
    "https://api.example.com/graphql",
    json={"query": "{ user(id: 1) { name email } }"},
    headers={"Authorization": f"Bearer {os.environ['TOKEN']}"},
    timeout=10,
)
data = resp.json()
if data.get("errors"):
    for err in data["errors"]:
        print(f"GraphQL error: {err['message']} (path: {err.get('path')})")
print(data.get("data"))
''')
```

### 通过 execute_code 使用 Python (requests)

```python
execute_code('''
import requests
resp = requests.get(
    "https://api.example.com/users/1",
    headers={"Authorization": "Bearer <TOKEN>"},
    timeout=(3.05, 30),  # (connect, read)
)
print(resp.status_code, dict(resp.headers))
print(resp.text[:500])
''')
```

## 分层调试流程

### 步骤 1 — 连通性

```python
terminal('nslookup api.example.com')
terminal('curl -v --connect-timeout 5 https://api.example.com/health')
```

故障：DNS 无法解析、防火墙、需要 VPN、缺少代理。

### 步骤 1.5 — 超时

区分*无法连接*和*连接成功但响应慢*：

```python
terminal('''curl -w "dns:%{time_namelookup}s connect:%{time_connect}s tls:%{time_appconnect}s ttfb:%{time_starttransfer}s total:%{time_total}s\\n" \\
  -o /dev/null -s https://api.example.com/endpoint''')
```

在 Python 中，始终传递一个元组超时 — `requests` 没有默认值，会永远挂起：

```python
execute_code('''
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
try:
    requests.get(url, timeout=(3.05, 30))
except ConnectTimeout:
    print("无法连接到主机 — DNS、防火墙、VPN 问题")
except ReadTimeout:
    print("已连接但服务器响应慢")
''')
```

诊断：`time_connect` 高是网络/防火墙问题；`time_starttransfer` 高但 `time_connect` 低是服务器慢。

### 步骤 2 — TLS/SSL

```python
terminal('curl -vI https://api.example.com 2>&1 | grep -E "SSL|subject|expire|issuer"')
```

故障：证书过期、自签名、主机名不匹配、缺少 CA 包。仅在临时调试时使用 `-k`，切勿在代码中使用。

### 步骤 3 — 认证

```python
# 令牌有效性检查
terminal('curl -s -o /dev/null -w "%{http_code}\\n" -H "Authorization: Bearer $TOKEN" https://api.example.com/me')

# 解码 JWT exp 声明 — 正确处理 base64url 填充
execute_code('''
import json, base64, os
tok = os.environ["TOKEN"]
payload = tok.split(".")[1]
payload += "=" * (-len(payload) % 4)
print(json.dumps(json.loads(base64.urlsafe_b64decode(payload)), indent=2))
''')
```

检查清单：
- 令牌是否过期？（JWT 中的 `exp` 声明）
- 方案是否正确？Bearer vs Basic vs Token vs `X-Api-Key`
- 环境是否正确？在 prod 环境使用 staging 密钥是经典错误
- API 密钥在请求头中还是查询参数中？（`?api_key=…`）
### 步骤 4 — 请求格式

```python
terminal("""curl -v -X POST https://api.example.com/endpoint \\
  -H 'Content-Type: application/json' \\
  -d '{"key":"value"}' 2>&1""")
```

**Content-Type / 正文不匹配 — 静默的 415/400 错误：**

```python
# 错误 — data= 发送表单编码数据，但头部信息撒谎了
requests.post(url, data='{"k":"v"}', headers={"Content-Type": "application/json"})

# 正确 — json= 自动设置头部并序列化
requests.post(url, json={"k": "v"})

# 错误 — Accept 头部要求 XML，但代码调用了 .json()
requests.get(url, headers={"Accept": "text/xml"})

# 正确 — 让 requests 自动构建带边界的 multipart 数据
requests.post(url, files={"file": open("doc.pdf", "rb")})
```

常见问题：表单编码 vs JSON、缺少必填字段、错误的 HTTP 方法、未编码的查询参数。

### 步骤 5 — 响应解析

在调用 `.json()` 之前，务必检查 content-type：

```python
execute_code('''
import requests
resp = requests.post(url, json=payload, timeout=10)
print(f"status={resp.status_code}")
print(f"headers={dict(resp.headers)}")
ct = resp.headers.get("Content-Type", "")
if "application/json" in ct:
    print(resp.json())
else:
    print(f"unexpected content-type {ct!r}, body={resp.text[:500]!r}")
''')
```

常见失败情况：预期是 JSON 却返回了 HTML 错误页面、空响应体、错误的字符集。

### 步骤 6 — 语义验证

解析成功了 — 但数据*正确*吗？

- `"status": "active"` 的含义和你的代码理解一致吗？
- 响应中的 ID 是否与请求的 ID 匹配？
- 时间戳是否在预期的时区？
- 分页返回了所有结果，还是只返回了第一页？

## HTTP 状态码速查手册

### 401 Unauthorized — 凭证缺失或无效

1.  `Authorization` 头部确实存在吗？（用 `curl -v` 确认）
2.  Token 是否正确且未过期？
3.  认证方案是否正确？（`Bearer` vs `Basic` vs `Token`）
4.  某些 API 使用查询参数（`?api_key=…`）而非头部。

### 403 Forbidden — 已认证但未授权

1.  Token 是否具有所需的权限/范围？
2.  资源是否属于其他账户？
3.  是否被 IP 白名单阻止？
4.  浏览器中是 CORS 问题吗？（检查 `Access-Control-Allow-Origin`）

### 404 Not Found — 资源不存在或 URL 错误

1.  路径正确吗？（尾部斜杠、拼写错误、版本前缀）
2.  资源 ID 存在吗？
3.  API 版本正确吗？（`/v1/` vs `/v2/`）？
4.  基础 URL 正确吗？（测试环境 vs 生产环境）？

### 409 Conflict — 状态冲突

1.  资源已存在（重复创建）？
2.  `ETag` / `If-Match` 已过时？
3.  被其他进程并发修改？

### 422 Unprocessable Entity — JSON 格式有效，但数据无效

错误响应体通常会指出问题字段。检查：
- 字段类型（字符串 vs 整数，日期格式）
- 必填 vs 可选
- 枚举值是否在允许的集合内

### 429 Too Many Requests — 超出速率限制

检查 `Retry-After` 和 `X-RateLimit-*` 头部。使用指数退避：

```python
execute_code('''
import time, requests

def with_backoff(method, url, **kwargs):
    for attempt in range(5):
        resp = requests.request(method, url, **kwargs)
        if resp.status_code != 429:
            return resp
        wait = int(resp.headers.get("Retry-After", 2 ** attempt))
        time.sleep(wait)
    return resp
''')
```

### 5xx — 服务器端错误，通常不是你的问题

-   **500** — 服务器内部错误。记录关联 ID，向提供商提交工单。
-   **502** — 上游服务不可用。退避 + 重试。
-   **503** — 服务过载 / 维护中。检查状态页面。
-   **504** — 上游服务超时。减少负载或增加超时时间。

对于所有 5xx 错误：使用抖动退避，持续出现时发出警报。

## 分页与幂等性

**分页。** 验证你获取了*所有*结果。查找 `next_cursor`、`next_page`、`total_count`。两种模式：
- 偏移量（`?limit=100&offset=200`） — 简单，但如果数据变动可能会跳过项目。
- 游标（`?cursor=abc123`） — 对于实时或大型数据集更推荐。

**幂等性。** 对于非幂等操作（POST），发送 `Idempotency-Key: <uuid>`，以便重试时不会重复扣款/重复创建。对于支付和订单操作是必需的。

## 契约验证

在生产环境遇到模式漂移之前捕获它：

```python
execute_code('''
import requests

def validate_user(data: dict) -> list[str]:
    errors = []
    required = {"id": int, "email": str, "created_at": str}
    for field, expected in required.items():
        if field not in data:
            errors.append(f"missing field: {field}")
        elif not isinstance(data[field], expected):
            errors.append(f"{field}: want {expected.__name__}, got {type(data[field]).__name__}")
    return errors

resp = requests.get(f"{BASE}/users/1", headers=HEADERS, timeout=10)
issues = validate_user(resp.json())
if issues:
    print(f"contract violations: {issues}")
''')
```

在 API 升级后、集成新的第三方服务时，或在 CI 冒烟测试中运行。

## 关联 ID

务必记录提供商的请求 ID — 这是联系供应商支持的最快途径：

```python
execute_code('''
import requests
resp = requests.post(url, json=payload, headers=headers, timeout=10)
request_id = (
    resp.headers.get("X-Request-Id")
    or resp.headers.get("X-Trace-Id")
    or resp.headers.get("CF-Ray")  # Cloudflare
)
if resp.status_code >= 400:
    print(f"failed status={resp.status_code} req_id={request_id} ts={resp.headers.get('Date')}")
''')
```

**供应商错误报告模板：**

```
端点:      POST /api/v1/orders
请求 ID:   req_abc123xyz
时间戳:    2026-03-17T14:30:00Z
状态码:    500
预期:      201 并返回订单对象
实际:      500 {"error":"internal server error"}
复现步骤:  curl -X POST … (auth: <REDACTED>)
```

## 回归测试模板

将此代码放入 `tests/` 目录，并通过 `terminal('pytest tests/test_api_smoke.py -v')` 运行：

```python
import os, requests, pytest

BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com")
TOKEN    = os.environ.get("API_TOKEN", "")
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}

class TestAPISmoke:
    def test_health(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200

    def test_list_users_returns_array(self):
        resp = requests.get(f"{BASE_URL}/users", headers=HEADERS, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("data", data), list)

    def test_get_user_required_fields(self):
        resp = requests.get(f"{BASE_URL}/users/1", headers=HEADERS, timeout=10)
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            user = resp.json()
            assert "id" in user and "email" in user

    def test_invalid_auth_returns_401(self):
        resp = requests.get(
            f"{BASE_URL}/users",
            headers={"Authorization": "Bearer invalid-token"},
            timeout=10,
        )
        assert resp.status_code == 401
```
## 安全

### Token 处理
- 切勿记录完整的 Token。进行脱敏处理：`Bearer <REDACTED>`。
- 切勿在脚本中硬编码 Token。应从环境变量（`os.environ["API_TOKEN"]`）或 `~/.hermes/.env` 文件中读取。
- 如果 Token 出现在日志、错误信息或 git 历史记录中，请立即轮换。

### 安全日志记录

```python
def redact_auth(headers: dict) -> dict:
    sensitive = {"authorization", "x-api-key", "cookie", "set-cookie"}
    return {k: ("<REDACTED>" if k.lower() in sensitive else v) for k, v in headers.items()}
```

### 泄露检查清单

- [ ] **URL 中的凭据。** 查询字符串中的 API 密钥会出现在服务器日志、浏览器历史记录、Referrer 头部中——请使用头部。
- [ ] **错误响应中的 PII。** `404 on /users/123` 不应透露用户是否存在（枚举）。
- [ ] **生产环境中的堆栈跟踪。** 500 错误不应泄露文件路径、框架版本。
- [ ] **内部主机名/IP。** 错误正文中的 `10.x.x.x`、`internal-api.corp.local`。
- [ ] **Token 被回显。** 某些 API 会在错误详情中包含认证 Token。请验证它们没有这样做。
- [ ] **冗长的 `Server` / `X-Powered-By` 头部。** 堆栈信息泄露。注意进行安全审查。

## Hermes 工具模式

### terminal — 用于 curl、dig、openssl

```python
terminal('curl -sI https://api.example.com')
terminal('openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null 2>/dev/null | openssl x509 -noout -dates')
```

### execute_code — 用于多步骤的 Python 流程

当调试涉及 认证 → 获取 → 分页 → 验证 的流程时，使用 `execute_code`。变量在脚本中持续存在，结果打印到标准输出，没有 Token 污染上下文的危险：

```python
execute_code('''
import os, requests

token = os.environ["API_TOKEN"]
base  = "https://api.example.com"
H     = {"Authorization": f"Bearer {token}"}

# 1. auth
me = requests.get(f"{base}/me", headers=H, timeout=10)
print(f"auth {me.status_code}")

# 2. paginate
all_users, cursor = [], None
while True:
    params = {"cursor": cursor} if cursor else {}
    r = requests.get(f"{base}/users", headers=H, params=params, timeout=10)
    body = r.json()
    all_users.extend(body["data"])
    cursor = body.get("next_cursor")
    if not cursor:
        break
print(f"users={len(all_users)}")
''')
```

### web_extract — 用于供应商 API 文档

提取你正在调试的端点的规范，而不是猜测：

```python
web_extract(urls=["https://docs.example.com/api/v1/users"])
```

### delegate_task — 用于完整的 CRUD 测试扫描

```python
delegate_task(
    goal="测试 /api/v1/users 的所有 CRUD 端点",
    context="""
遵循 rest-graphql-debug 技能 (optional-skills/software-development/rest-graphql-debug)。
基础 URL: https://api.example.com
认证: 来自 API_TOKEN 环境变量的 Bearer token。

对于每个 HTTP 方法 (POST, GET, PATCH, DELETE):
  - 正常路径: 断言状态码 + 响应模式
  - 错误情况: 400, 404, 422
  - 记录任何失败的复现 curl 命令（脱敏 Token）

输出: 每个端点的通过/失败状态 + 失败的关联 ID。
""",
    toolsets=["terminal", "file"],
)
```

## 输出格式

报告发现时：

```
## 发现
端点: POST /api/v1/users
状态:   422 Unprocessable Entity
请求 ID:   req_abc123xyz

## 复现步骤
curl -X POST https://api.example.com/api/v1/users \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <REDACTED>' \
  -d '{"name":"test"}'

## 根本原因
缺少必填字段 `email`。服务器在处理前拒绝。

## 修复方法
-d '{"name":"test","email":"test@example.com"}'
```

## 相关

- `systematic-debugging` — 一旦隔离出失败的 API 层，就对你的代码进行根本原因分析
- `test-driven-development` — 在发布修复之前编写回归测试