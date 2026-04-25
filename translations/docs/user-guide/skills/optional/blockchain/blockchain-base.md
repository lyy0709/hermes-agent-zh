---
title: "Base"
sidebar_label: "Base"
description: "查询 Base（以太坊 L2）区块链数据并附带美元计价——钱包余额、代币信息、交易详情、Gas 分析、合约检查、巨鲸检测、实时网络状态……"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# Base

查询 Base（以太坊 L2）区块链数据并附带美元计价——钱包余额、代币信息、交易详情、Gas 分析、合约检查、巨鲸检测以及实时网络状态。使用 Base RPC + CoinGecko。无需 API 密钥。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/blockchain/base` 安装 |
| 路径 | `optional-skills/blockchain/base` |
| 版本 | `0.1.0` |
| 作者 | youssefea |
| 许可证 | MIT |
| 标签 | `Base`, `Blockchain`, `Crypto`, `Web3`, `RPC`, `DeFi`, `EVM`, `L2`, `Ethereum` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Base 区块链技能

查询 Base（以太坊 L2）链上数据，并通过 CoinGecko 获取美元计价信息。
包含 8 个命令：钱包资产组合、代币信息、交易、Gas 分析、
合约检查、巨鲸检测、网络状态和价格查询。

无需 API 密钥。仅使用 Python 标准库（urllib, json, argparse）。

---

## 使用时机

- 用户询问 Base 钱包余额、代币持仓或资产组合价值时
- 用户想通过哈希值检查特定交易时
- 用户想获取 ERC-20 代币元数据、价格、供应量或市值时
- 用户想了解 Base Gas 成本和 L1 数据费用时
- 用户想检查合约（ERC 类型检测、代理解析）时
- 用户想查找大额 ETH 转账（巨鲸检测）时
- 用户想获取 Base 网络健康状况、Gas 价格或 ETH 价格时
- 用户询问“USDC/AERO/DEGEN/ETH 的价格是多少？”时

---

## 前提条件

辅助脚本仅使用 Python 标准库（urllib, json, argparse）。
无需外部包。

价格数据来自 CoinGecko 的免费 API（无需密钥，速率限制约为每分钟 10-30 次请求）。如需更快查询，请使用 `--no-prices` 标志。

---

## 快速参考

RPC 端点（默认）：https://mainnet.base.org
覆盖：export BASE_RPC_URL=https://your-private-rpc.com

辅助脚本路径：~/.hermes/skills/blockchain/base/scripts/base_client.py

```
python3 base_client.py wallet   <address> [--limit N] [--all] [--no-prices]
python3 base_client.py tx       <hash>
python3 base_client.py token    <contract_address>
python3 base_client.py gas
python3 base_client.py contract <address>
python3 base_client.py whales   [--min-eth N]
python3 base_client.py stats
python3 base_client.py price    <contract_address_or_symbol>
```

---

## 操作流程

### 0. 设置检查

```bash
python3 --version

# 可选：设置私有 RPC 以获得更好的速率限制
export BASE_RPC_URL="https://mainnet.base.org"

# 确认连通性
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py stats
```

### 1. 钱包资产组合

获取 ETH 余额和 ERC-20 代币持仓及其美元价值。
通过链上 `balanceOf` 调用检查约 15 个知名的 Base 代币（USDC, WETH, AERO, DEGEN 等）。
代币按价值排序，小额代币被过滤。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py \
  wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

标志：
- `--limit N` — 显示前 N 个代币（默认：20）
- `--all` — 显示所有代币，不过滤小额代币，无限制
- `--no-prices` — 跳过 CoinGecko 价格查询（更快，仅使用 RPC）

输出包括：ETH 余额 + 美元价值、按价值排序的代币列表及价格、小额代币数量、资产组合总美元价值。

注意：仅检查已知代币。未知的 ERC-20 代币不会被发现。
对于任何代币，请使用 `token` 命令并指定合约地址。

### 2. 交易详情

通过哈希值检查完整交易。显示转账的 ETH 价值、
使用的 Gas、以 ETH/USD 计价的费用、状态以及解码后的 ERC-20/ERC-721 转账。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py \
  tx 0xabc123...your_tx_hash_here
```

输出：哈希值、区块、发送方、接收方、价值（ETH + USD）、Gas 价格、使用的 Gas、
费用、状态、合约创建地址（如有）、代币转账。

### 3. 代币信息

获取 ERC-20 代币元数据：名称、符号、小数位、总供应量、价格、
市值和合约代码大小。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py \
  token 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

输出：名称、符号、小数位、总供应量、价格、市值。
通过 eth_call 直接从合约读取名称/符号/小数位。

### 4. Gas 分析

详细的 Gas 分析，包含常见操作的成本估算。
显示当前 Gas 价格、过去 10 个区块的基础费用趋势、区块
利用率，以及 ETH 转账、ERC-20 转账和兑换的估算成本。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py gas
```

输出：当前 Gas 价格、基础费用、区块利用率、10 个区块趋势、
以 ETH 和 USD 计价的成本估算。

注意：Base 是 L2 —— 实际交易成本包括 L1 数据发布费，该费用取决于 calldata 大小和 L1 Gas 价格。
显示的估算仅针对 L2 执行。

### 5. 合约检查

检查地址：确定是 EOA 还是合约，检测
ERC-20/ERC-721/ERC-1155 接口，解析 EIP-1967 代理
实现地址。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py \
  contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

输出：是否为合约、代码大小、ETH 余额、检测到的接口
（ERC-20, ERC-721, ERC-1155）、ERC-20 元数据、代理实现
地址。

### 6. 巨鲸检测器

扫描最新区块中的大额 ETH 转账及其美元价值。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py \
  whales --min-eth 1.0
```

注意：仅扫描最新区块 —— 是时间点快照，非历史数据。
默认阈值为 1.0 ETH（低于 Solana 的默认值，因为 ETH
价值更高）。

### 7. 网络状态

Base 网络实时健康状况：最新区块、链 ID、Gas 价格、基础费用、
区块利用率、交易数量和 ETH 价格。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py stats
```

### 8. 价格查询

通过合约地址或已知符号快速查询任何代币的价格。

```bash
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py price ETH
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py price USDC
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py price AERO
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py price DEGEN
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py price 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

已知符号：ETH, WETH, USDC, cbETH, AERO, DEGEN, TOSHI, BRETT,
WELL, wstETH, rETH, cbBTC。

---

## 注意事项

- **CoinGecko 速率限制** — 免费层允许约每分钟 10-30 次请求。
  价格查询每个代币使用 1 次请求。如需更快速度，请使用 `--no-prices`。
- **公共 RPC 速率限制** — Base 的公共 RPC 限制请求次数。
  生产环境使用，请将 BASE_RPC_URL 设置为私有端点
  （Alchemy, QuickNode, Infura）。
- **钱包仅显示已知代币** — 与 Solana 不同，EVM 链没有
  内置的“获取所有代币” RPC。钱包命令通过 `balanceOf` 检查约 15 个流行的
  Base 代币。未知的 ERC-20 代币不会出现。对于任何特定合约，
  请使用 `token` 命令。
- **代币名称从合约读取** — 如果合约未实现
  `name()` 或 `symbol()`，这些字段可能为空。已知代币有
  硬编码的标签作为后备。
- **Gas 估算仅针对 L2** — Base 交易成本包括 L1
  数据发布费（取决于 calldata 大小和 L1 Gas 价格）。gas
  命令仅估算 L2 执行成本。
- **巨鲸检测器仅扫描最新区块** — 非历史数据。结果
  因查询时刻而异。默认阈值为 1.0 ETH。
- **代理检测** — 仅检测 EIP-1967 代理。其他代理
  模式（EIP-1167 最小代理、自定义存储槽）未检查。
- **429 错误重试** — RPC 和 CoinGecko 调用在遇到速率限制错误时，
  都会重试最多 2 次，并采用指数退避。

---

## 验证

```bash
# 应打印 Base 链 ID (8453)、最新区块、Gas 价格和 ETH 价格
python3 ~/.hermes/skills/blockchain/base/scripts/base_client.py stats
```