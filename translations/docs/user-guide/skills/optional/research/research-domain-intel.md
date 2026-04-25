---
title: "Domain Intel — 使用 Python 标准库进行被动域名侦察"
sidebar_label: "Domain Intel"
description: "使用 Python 标准库进行被动域名侦察"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# Domain Intel

使用 Python 标准库进行被动域名侦察。包括子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录查询、域名可用性检查以及批量多域名分析。无需 API 密钥。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/domain-intel` 安装 |
| 路径 | `optional-skills/research/domain-intel` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Domain Intelligence — 被动 OSINT

仅使用 Python 标准库进行被动域名侦察。
**零依赖。零 API 密钥。在 Linux、macOS 和 Windows 上均可运行。**

## 辅助脚本

此技能包含 `scripts/domain_intel.py` — 一个用于所有域名情报操作的完整 CLI 工具。

```bash
# 通过证书透明度日志发现子域名
python3 SKILL_DIR/scripts/domain_intel.py subdomains example.com

# SSL 证书检查（到期时间、密码套件、SANs、颁发者）
python3 SKILL_DIR/scripts/domain_intel.py ssl example.com

# WHOIS 查询（注册商、日期、名称服务器 — 支持 100+ 个 TLD）
python3 SKILL_DIR/scripts/domain_intel.py whois example.com

# DNS 记录查询（A, AAAA, MX, NS, TXT, CNAME）
python3 SKILL_DIR/scripts/domain_intel.py dns example.com

# 域名可用性检查（被动方式：DNS + WHOIS + SSL 信号）
python3 SKILL_DIR/scripts/domain_intel.py available coolstartup.io

# 批量分析 — 多个域名，并行执行多项检查
python3 SKILL_DIR/scripts/domain_intel.py bulk example.com github.com google.com
python3 SKILL_DIR/scripts/domain_intel.py bulk example.com github.com --checks ssl,dns
```

`SKILL_DIR` 是包含此 SKILL.md 文件的目录。所有输出均为结构化 JSON。

## 可用命令

| 命令 | 功能 | 数据源 |
|---------|-------------|-------------|
| `subdomains` | 从证书日志中查找子域名 | crt.sh (HTTPS) |
| `ssl` | 检查 TLS 证书详情 | 直接 TCP:443 连接到目标 |
| `whois` | 注册信息、注册商、日期 | WHOIS 服务器 (TCP:43) |
| `dns` | A, AAAA, MX, NS, TXT, CNAME 记录 | 系统 DNS + Google DoH |
| `available` | 检查域名是否已注册 | DNS + WHOIS + SSL 信号 |
| `bulk` | 对多个域名运行多项检查 | 以上所有 |

## 何时使用此技能 vs 内置工具

- **使用此技能** 处理基础设施相关问题：子域名、SSL 证书、WHOIS、DNS 记录、可用性
- **使用 `web_search`** 进行关于域名/公司做什么的一般性研究
- **使用 `web_extract`** 获取网页的实际内容
- **使用 `terminal` 配合 `curl -I`** 进行简单的“此 URL 是否可达”检查

| 任务 | 更合适的工具 | 原因 |
|------|-------------|-----|
| "example.com 是做什么的？" | `web_extract` | 获取页面内容，而非 DNS/WHOIS 数据 |
| "查找关于某公司的信息" | `web_search` | 一般性研究，非域名特定 |
| "这个网站安全吗？" | `web_search` | 信誉检查需要网络上下文 |
| "检查 URL 是否可达" | `terminal` 配合 `curl -I` | 简单的 HTTP 检查 |
| "查找 X 的子域名" | **此技能** | 这是唯一的被动来源 |
| "SSL 证书何时到期？" | **此技能** | 内置工具无法检查 TLS |
| "谁注册了这个域名？" | **此技能** | WHOIS 数据不在网络搜索中 |
| "coolstartup.io 可用吗？" | **此技能** | 通过 DNS+WHOIS+SSL 进行被动可用性检查 |

## 平台兼容性

纯 Python 标准库 (`socket`, `ssl`, `urllib`, `json`, `concurrent.futures`)。
在 Linux、macOS 和 Windows 上无需依赖即可完全一致地运行。

- **crt.sh 查询** 使用 HTTPS（端口 443）— 可在大多数防火墙后工作
- **WHOIS 查询** 使用 TCP 端口 43 — 在限制性网络中可能被阻止
- **DNS 查询** 使用 Google DoH (HTTPS) 查询 MX/NS/TXT — 对防火墙友好
- **SSL 检查** 连接到目标的 443 端口 — 唯一的“主动”操作

## 数据源

所有查询均为**被动** — 无端口扫描，无漏洞测试：

- **crt.sh** — 证书透明度日志（子域名发现，仅 HTTPS）
- **WHOIS 服务器** — 直接 TCP 连接到 100+ 个权威 TLD 注册商
- **Google DNS-over-HTTPS** — MX, NS, TXT, CNAME 解析（对防火墙友好）
- **系统 DNS** — A/AAAA 记录解析
- **SSL 检查** 是唯一的“主动”操作（TCP 连接到目标:443）

## 注意事项

- WHOIS 查询使用 TCP 端口 43 — 在限制性网络中可能被阻止
- 一些 WHOIS 服务器会隐藏注册人信息（GDPR）— 向用户说明这一点
- 对于非常流行的域名（数千个证书），crt.sh 可能较慢 — 请设定合理的预期
- 可用性检查基于启发式方法（3 个被动信号）— 不像注册商 API 那样权威

---

*由 [@FurkanL0](https://github.com/FurkanL0) 贡献*