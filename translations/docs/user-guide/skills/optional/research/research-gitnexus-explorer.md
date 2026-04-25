---
title: "Gitnexus Explorer"
sidebar_label: "Gitnexus Explorer"
description: "使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Gitnexus Explorer

使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/gitnexus-explorer` 安装 |
| 路径 | `optional-skills/research/gitnexus-explorer` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `gitnexus`, `code-intelligence`, `knowledge-graph`, `visualization` |
| 相关技能 | [`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp), [`codebase-inspection`](/docs/user-guide/skills/bundled/github/github-codebase-inspection) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GitNexus Explorer

将任何代码库索引为知识图谱，并提供交互式 Web UI 用于探索符号、调用链、集群和执行流。通过 Cloudflare 隧道实现远程访问。

## 使用时机

- 用户希望可视化探索代码库架构
- 用户要求获取仓库的知识图谱/依赖图
- 用户希望与他人共享交互式代码库探索器

## 先决条件

- **Node.js** (v18+) — GitNexus 和代理服务器所需
- **git** — 仓库必须包含 `.git` 目录
- **cloudflared** — 用于隧道（如果缺失，将自动安装到 ~/.local/bin）

## 大小警告

Web UI 在浏览器中渲染所有节点。约 5,000 个文件以下的仓库运行良好。大型仓库（30k+ 节点）会导致浏览器标签页卡顿或崩溃。CLI/MCP 工具适用于任何规模 — 仅 Web 可视化有此限制。

## 步骤

### 1. 克隆并构建 GitNexus（一次性设置）

```bash
GITNEXUS_DIR="${GITNEXUS_DIR:-$HOME/.local/share/gitnexus}"

if [ ! -d "$GITNEXUS_DIR/gitnexus-web/dist" ]; then
  git clone https://github.com/abhigyanpatwari/GitNexus.git "$GITNEXUS_DIR"
  cd "$GITNEXUS_DIR/gitnexus-shared" && npm install && npm run build
  cd "$GITNEXUS_DIR/gitnexus-web" && npm install
fi
```

### 2. 为远程访问修补 Web UI

Web UI 默认使用 `localhost:4747` 进行 API 调用。修补它以使用同源策略，使其能通过隧道/代理工作：

**文件：`$GITNEXUS_DIR/gitnexus-web/src/config/ui-constants.ts`**
更改：
```typescript
export const DEFAULT_BACKEND_URL = 'http://localhost:4747';
```
为：
```typescript
export const DEFAULT_BACKEND_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? window.location.origin : 'http://localhost:4747';
```

**文件：`$GITNEXUS_DIR/gitnexus-web/vite.config.ts`**
在 `server: { }` 块内添加 `allowedHosts: true`（仅在运行开发模式而非生产构建时需要）：
```typescript
server: {
    allowedHosts: true,
    // ... 现有配置
},
```

然后构建生产包：
```bash
cd "$GITNEXUS_DIR/gitnexus-web" && npx vite build
```

### 3. 索引目标仓库

```bash
cd /path/to/target-repo
npx gitnexus analyze --skip-agents-md
rm -rf .claude/    # 移除 Claude Code 特定的产物
```

添加 `--embeddings` 以启用语义搜索（较慢 — 分钟级而非秒级）。

索引位于仓库内的 `.gitnexus/` 目录中（自动被 gitignore 忽略）。

### 4. 创建代理脚本

将此内容写入文件（例如，`$GITNEXUS_DIR/proxy.mjs`）。它提供生产 Web UI 并将 `/api/*` 代理到 GitNexus 后端 — 同源，无 CORS 问题，无需 sudo，无需 nginx。

```javascript
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const API_PORT = parseInt(process.env.API_PORT || '4747');
const DIST_DIR = process.argv[2] || './dist';
const PORT = parseInt(process.argv[3] || '8888');

const MIME = {
  '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.wasm': 'application/wasm',
};

function proxyToApi(req, res) {
  const opts = {
    hostname: '127.0.0.1', port: API_PORT,
    path: req.url, method: req.method, headers: req.headers,
  };
  const proxy = http.request(opts, (upstream) => {
    res.writeHead(upstream.statusCode, upstream.headers);
    upstream.pipe(res, { end: true });
  });
  proxy.on('error', () => { res.writeHead(502); res.end('Backend unavailable'); });
  req.pipe(proxy, { end: true });
}

function serveStatic(req, res) {
  let filePath = path.join(DIST_DIR, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
  if (!fs.existsSync(filePath)) filePath = path.join(DIST_DIR, 'index.html');
  const ext = path.extname(filePath);
  const mime = MIME[ext] || 'application/octet-stream';
  try {
    const data = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': mime, 'Cache-Control': 'public, max-age=3600' });
    res.end(data);
  } catch { res.writeHead(404); res.end('Not found'); }
}

http.createServer((req, res) => {
  if (req.url.startsWith('/api')) proxyToApi(req, res);
  else serveStatic(req, res);
}).listen(PORT, () => console.log(`GitNexus proxy on http://localhost:${PORT}`));
```

### 5. 启动服务

```bash
# 终端 1: GitNexus 后端 API
npx gitnexus serve &

# 终端 2: 代理服务器（Web UI + API 在同一端口）
node "$GITNEXUS_DIR/proxy.mjs" "$GITNEXUS_DIR/gitnexus-web/dist" 8888 &
```

验证：`curl -s http://localhost:8888/api/repos` 应返回已索引的仓库。

### 6. 使用 Cloudflare 隧道（可选 — 用于远程访问）

```bash
# 如果需要，安装 cloudflared（无需 sudo）
if ! command -v cloudflared &>/dev/null; then
  mkdir -p ~/.local/bin
  curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    -o ~/.local/bin/cloudflared
  chmod +x ~/.local/bin/cloudflared
  export PATH="$HOME/.local/bin:$PATH"
fi

# 启动隧道（--config /dev/null 避免与现有命名隧道配置冲突）
cloudflared tunnel --config /dev/null --url http://localhost:8888 --no-autoupdate --protocol http2
```

隧道 URL（例如，`https://random-words.trycloudflare.com`）会打印到 stderr。
分享它 — 任何拥有链接的人都可以探索图谱。

### 7. 清理

```bash
# 停止服务
pkill -f "gitnexus serve"
pkill -f "proxy.mjs"
pkill -f cloudflared

# 从目标仓库移除索引
cd /path/to/target-repo
npx gitnexus clean
rm -rf .claude/
```

## 注意事项

- **`--config /dev/null` 对于 cloudflared 是必需的**，如果用户在 `~/.cloudflared/config.yml` 已有现有的命名隧道配置。没有它，配置中的通配入口规则会为所有快速隧道请求返回 404。

- **生产构建对于隧道是强制性的。** Vite 开发服务器默认阻止非 localhost 主机（`allowedHosts`）。生产构建 + Node 代理完全避免了这个问题。

- **Web UI 不会创建 `.claude/` 或 `CLAUDE.md`。** 这些是由 `npx gitnexus analyze` 创建的。使用 `--skip-agents-md` 来抑制 markdown 文件的生成，然后 `rm -rf .claude/` 移除其余部分。这些是 Claude Code 集成，hermes-agent 用户不需要。

- **浏览器内存限制。** Web UI 将整个图谱加载到浏览器内存中。5k+ 文件的仓库可能会卡顿。30k+ 文件很可能会导致标签页崩溃。

- **嵌入是可选的。** `--embeddings` 启用语义搜索，但在大型仓库上需要数分钟。快速探索时跳过它；如果希望通过 AI 聊天面板进行自然语言查询，则添加它。

- **多个仓库。** `gitnexus serve` 提供所有已索引的仓库。索引多个仓库，启动一次 serve，Web UI 允许你在它们之间切换。