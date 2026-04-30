---
title: "Node Inspect 调试器 — 调试 Node"
sidebar_label: "Node Inspect 调试器"
description: "调试 Node"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Node Inspect 调试器

通过 --inspect + Chrome DevTools Protocol CLI 调试 Node.js。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/node-inspect-debugger` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `debugging`, `nodejs`, `node-inspect`, `cdp`, `breakpoints`, `ui-tui` |
| 相关技能 | [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy), [`debugging-hermes-tui-commands`](/docs/user-guide/skills/bundled/software-development/software-development-debugging-hermes-tui-commands) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Node.js Inspect 调试器

## 概述

当 `console.log` 不够用时，从终端以编程方式驱动 Node 内置的 V8 检查器。你可以获得真正的断点、步入/步过/步出、调用栈遍历、局部/闭包作用域转储以及在暂停帧中任意表达式求值。

两种工具，任选其一：

- **`node inspect`** — 内置，零安装，CLI REPL。最适合快速探查。
- **`ndb` / 通过 `chrome-remote-interface` 的 CDP** — 可从 Node/Python 编写脚本；当你想要自动化多个断点、跨运行收集状态或从 Agent 循环非交互式调试时最佳。

**首选 `node inspect`。** 它始终可用且 REPL 速度快。

## 何时使用

- Node 测试失败，你需要查看中间状态
- ui-tui 崩溃或行为异常，你想在渲染前检查 React/Ink 状态
- tui_gateway 子进程（`_SlashWorker`、PTY 桥接工作进程）行为异常
- 你需要检查闭包中的某个值，而 `console.log` 在不打补丁的情况下无法访问
- 性能：附加到正在运行的进程以捕获 CPU 性能分析或堆快照

**不要用于：** `console.log` 能在一分钟内解决的问题。断点驱动的调试更重量级；在回报真实存在时使用它。

## 快速参考：`node inspect` REPL

在第一行暂停启动：

```bash
node inspect path/to/script.js
# 或使用 tsx
node --inspect-brk $(which tsx) path/to/script.ts
```

`debug>` 提示符接受：

| 命令 | 操作 |
|---|---|
| `c` 或 `cont` | 继续 |
| `n` 或 `next` | 步过 |
| `s` 或 `step` | 步入 |
| `o` 或 `out` | 步出 |
| `pause` | 暂停正在运行的代码 |
| `sb('file.js', 42)` | 在 file.js 第 42 行设置断点 |
| `sb(42)` | 在当前文件的第 42 行设置断点 |
| `sb('functionName')` | 在函数被调用时中断 |
| `cb('file.js', 42)` | 清除断点 |
| `breakpoints` | 列出所有断点 |
| `bt` | 回溯（调用栈） |
| `list(5)` | 显示当前位置周围 5 行源代码 |
| `watch('expr')` | 每次暂停时对表达式求值 |
| `watchers` | 显示被监视的表达式 |
| `repl` | 进入当前作用域的 REPL（按 Ctrl+C 退出 REPL） |
| `exec expr` | 对表达式求值一次 |
| `restart` | 重启脚本 |
| `kill` | 终止脚本 |
| `.exit` | 退出调试器 |

**在 `repl` 子模式下：** 输入任何 JS 表达式，包括访问局部/闭包变量。`Ctrl+C` 退出回到 `debug>`。

## 附加到正在运行的进程

当进程已在运行时（例如长期运行的开发服务器或 TUI 消息网关）：

```bash
# 1. 向现有进程发送 SIGUSR1 以启用检查器
kill -SIGUSR1 <pid>
# Node 打印：Debugger listening on ws://127.0.0.1:9229/<uuid>

# 2. 附加调试器 CLI
node inspect -p <pid>
# 或通过 URL
node inspect ws://127.0.0.1:9229/<uuid>
```

从一开始就启动带检查器的进程：

```bash
node --inspect script.js           # 监听 127.0.0.1:9229，继续运行
node --inspect-brk script.js       # 监听并在第一行暂停
node --inspect=0.0.0.0:9230 script.js   # 自定义主机:端口
```

对于通过 tsx 的 TypeScript：

```bash
node --inspect-brk --import tsx script.ts
# 或旧版 tsx
node --inspect-brk -r tsx/cjs script.ts
```

## 编程式 CDP（从终端编写脚本）

当你想自动化时——设置多个断点、捕获作用域状态、编写重现脚本——使用 `chrome-remote-interface`：

```bash
npm i -g chrome-remote-interface        # 或项目本地安装
# 启动你的目标：
node --inspect-brk=9229 target.js &
```

驱动程序脚本（保存为 `/tmp/cdp-debug.js`）：

```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames, reason }) => {
    const top = callFrames[0];
    console.log(`PAUSED: ${reason} @ ${top.url}:${top.location.lineNumber + 1}`);

    // 遍历作用域以获取局部变量
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId,
          ownProperties: true,
        });
        for (const p of result) {
          console.log(`  ${scope.type}.${p.name} =`, p.value?.value ?? p.value?.description);
        }
      }
    }

    // 在暂停帧中求值表达式
    const { result } = await Debugger.evaluateOnCallFrame({
      callFrameId: top.callFrameId,
      expression: 'typeof state !== "undefined" ? JSON.stringify(state) : "n/a"',
    });
    console.log('state =', result.value ?? result.description);

    await Debugger.resume();
  });

  await Runtime.enable();
  await Debugger.enable();

  // 通过 URL 正则表达式 + 行号设置断点
  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$',
    lineNumber: 119,       // 0 索引
    columnNumber: 0,
  });

  await Runtime.runIfWaitingForDebugger();
})();
```

运行它：

```bash
node /tmp/cdp-debug.js
```

Hermes 特定说明：`chrome-remote-interface` 不在 `ui-tui/package.json` 中。如果你不想弄脏项目，请将其安装到临时位置：

```bash
mkdir -p /tmp/cdp-tools && cd /tmp/cdp-tools && npm i chrome-remote-interface
NODE_PATH=/tmp/cdp-tools/node_modules node /tmp/cdp-debug.js
```

## 调试 Hermes ui-tui

TUI 使用 Ink + tsx 构建。两种常见场景：

### 调试开发中的单个 Ink 组件

`ui-tui/package.json` 有 `npm run dev` (tsx --watch)。通过直接运行 tsx 添加 `--inspect-brk`：

```bash
cd /home/bb/hermes-agent/ui-tui
npm run build    # 生成一次 dist/，这样首次加载时就不需要转译
node --inspect-brk dist/entry.js
# 在另一个终端中：
node inspect -p <node pid>
```

然后在 `debug>` 内部：

```
sb('dist/app.js', 220)     # 或可疑渲染所在的任何位置
cont
```

当它暂停时，`repl` → 检查 `props`、状态引用、`useInput` 处理程序值等。

### 调试正在运行的 `hermes --tui`

TUI 从 Python CLI 生成 Node。最简单的方法：

```bash
# 1. 启动 TUI
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)

# 2. 在该 Node PID 上启用检查器
kill -SIGUSR1 "$TUI_PID"

# 3. 找到 WS URL
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'

# 4. 附加
node inspect ws://127.0.0.1:9229/<uuid>
```

与 TUI 交互（在其窗口中输入）会继续推进执行；你的调试器可以在任何 `sb(...)` 断点处暂停它。

### 调试 `_SlashWorker` / PTY 子进程

那些是 Python，不是 Node —— 对它们使用 `python-debugpy` 技能。只有 Node 部分（Ink UI、tui_gateway 客户端、`ui-tui/` 下的 tsx-run 测试）使用此技能。

## 在调试器下运行 Vitest 测试

```bash
cd /home/bb/hermes-agent/ui-tui
# 在入口处暂停运行单个测试文件
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism src/app/foo.test.tsx
```

在另一个终端中：`node inspect -p <pid>`，然后 `sb('src/app/foo.tsx', 42)`，`cont`。

使用 `--no-file-parallelism` (vitest) 或 `--runInBand` (jest) 以便只存在一个工作进程 —— 调试一个进程池很痛苦。

## 堆快照和 CPU 性能分析（非交互式）

从上面的 CDP 驱动程序中，将 Debugger 替换为 `HeapProfiler` / `Profiler`：

```javascript
// 5 秒的 CPU 性能分析
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));
// 在 Chrome DevTools → Performance 标签页中打开 /tmp/cpu.cpuprofile
```

```javascript
// 堆快照
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot({ reportProgress: false });
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```

## 常见陷阱

1.  **TS 源代码中的行号错误。** 断点命中的是编译后的 JS，而不是 `.ts`。要么 (a) 在构建的 `dist/*.js` 中中断，要么 (b) 启用源映射（`node --enable-source-maps`）并使用 `sb('src/app.tsx', N)` —— 但仅限于遵循源映射的 CDP 客户端。`node inspect` CLI 不遵循。

2.  **`--inspect` 与 `--inspect-brk`。** `--inspect` 启动检查器但不暂停；如果你附加得太晚，你的脚本会在你设置第一个断点之前就运行过去了。当需要在任何代码运行之前设置断点时，使用 `--inspect-brk`。

3.  **端口冲突。** 默认是 `9229`。如果多个 Node 进程都在检查，传递 `--inspect=0`（随机端口）并从 `/json/list` 读取实际的 URL：
    ```bash
    curl -s http://127.0.0.1:9229/json/list   # 列出主机上所有可检查的目标
    ```

4.  **子进程。** 父进程上的 `--inspect` 不会检查其子进程。使用 `NODE_OPTIONS='--inspect-brk' node parent.js` 传播到每个子进程；注意它们都需要唯一的端口（当 `NODE_OPTIONS='--inspect'` 被继承时，Node 会自动递增）。

5.  **后台终止。** 如果你在目标暂停时按 `Ctrl+C` 退出 `node inspect`，目标将保持暂停状态。要么先 `cont`，要么显式 `kill` 目标。

6.  **通过 Agent 终端运行 `node inspect`。** 它是一个支持 PTY 的 REPL。在 Hermes 中，使用 `terminal(pty=true)` 或 `background=true` + `process(action='submit', data='...')` 启动它。非 PTY 前台模式适用于一次性命令，但不适用于交互式单步执行。

7.  **安全性。** `--inspect=0.0.0.0:9229` 暴露了任意代码执行。始终绑定到 `127.0.0.1`（默认值），除非你有一个隔离的网络。

## 验证清单

设置调试会话后，验证：

- [ ] `curl -s http://127.0.0.1:9229/json/list` 返回的正是你期望的目标
- [ ] 第一个断点确实命中（如果没有，你可能错过了 `--inspect-brk` 或在执行完成后才附加）
- [ ] 暂停时的源代码列表显示正确的文件（不匹配 = 源映射问题，见陷阱 1）
- [ ] `repl` 中的 `exec process.pid` 返回你打算附加的 PID

## 一次性配方

**“为什么这个变量在第 X 行是 undefined？”**
```bash
node --inspect-brk script.js &
node inspect -p $!
# debug>
sb('script.js', X)
cont
# 已暂停。现在：
repl
> myVariable
> Object.keys(this)
```

**“进入这个函数的调用路径是什么？”**
```
debug> sb('suspectFn')
debug> cont
# 在入口处暂停
debug> bt
```

**“这个异步链挂起了——在哪里？”**
```
# 使用 --inspect（不带 -brk）启动，让它运行到挂起，然后：
debug> pause
debug> bt
# 现在你看到了卡住的帧
```