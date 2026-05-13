---
sidebar_position: 16
title: "LSP — 语义诊断"
description: "将真正的语言服务器（pyright、gopls、rust-analyzer 等）接入到 `write_file` 和 `patch` 使用的写入后 lint 检查中。"
---

# 语言服务器协议 (LSP)

Hermes 运行完整的语言服务器 —— pyright、gopls、rust-analyzer、typescript-language-server、clangd 以及约 20 多个其他服务器 —— 作为后台子进程，并将其语义诊断信息反馈给 `write_file` 和 `patch` 使用的写入后 lint 检查。当 Agent 编辑文件时，它能准确看到该编辑引入的错误 —— 不仅仅是语法错误，还包括**类型错误、未定义名称、缺失导入以及语言服务器检测到的项目级语义问题**。

这与顶级编码 Agent 使用的架构相同。Hermes 将其作为独立功能提供：无需编辑器宿主，无需安装插件，也无需管理单独的守护进程。

## LSP 何时运行

LSP 的运行取决于 **git 工作区检测**。当 Agent 的工作目录（或正在编辑的文件）位于 git 工作树内时，LSP 将针对该工作区运行。当两者都不在 git 仓库中时，LSP 保持休眠状态 —— 这对于消息网关很有用，因为其当前工作目录是用户的主目录，没有项目可供诊断。

检查是分层的：首先进行进程内语法检查（微秒级），然后在语法无误时进行 LSP 诊断。不稳定的或缺失的语言服务器永远不会中断写入操作 —— 所有 LSP 故障路径都会静默回退到仅语法检查的结果。

具体来说，在每次成功的 `write_file` 或 `patch` 操作中：

1.  Hermes 捕获文件当前诊断的基线。
2.  执行写入操作。
3.  重新查询语言服务器，过滤掉基线中已存在的诊断，并仅显示新增的诊断。

Agent 会看到类似以下的输出：

```
{
  "bytes_written": 42,
  "dirs_created": false,
  "lint": {"status": "ok", "output": ""},
  "lsp_diagnostics": "LSP diagnostics introduced by this edit:\n<diagnostics file=\"/path/to/foo.py\">\nERROR [42:5] Cannot find name 'foo' [reportUndefinedVariable] (Pyright)\nERROR [50:1] Argument of type \"str\" is not assignable to \"int\" [reportArgumentType] (Pyright)\n</diagnostics>"
}
```

`lint` 字段携带语法检查结果（通过 `ast.parse`、`json.loads` 等进行微秒级的进程内解析）；`lsp_diagnostics` 字段携带来自真实语言服务器的语义诊断。两个通道，独立的信号 —— Agent 会看到一个语法无误但存在语义问题的文件，表现为 `lint: ok` 加上一个已填充的 `lsp_diagnostics`。

## 支持的语言

| 语言 | 服务器 | 自动安装 |
|----------|--------|--------------|
| Python | `pyright-langserver` | npm |
| TypeScript / JavaScript / JSX / TSX | `typescript-language-server` | npm |
| Vue | `@vue/language-server` | npm |
| Svelte | `svelte-language-server` | npm |
| Astro | `@astrojs/language-server` | npm |
| Go | `gopls` | `go install` |
| Rust | `rust-analyzer` | 手动 (rustup) |
| C / C++ | `clangd` | 手动 (LLVM) |
| Bash / Zsh | `bash-language-server` | npm |
| YAML | `yaml-language-server` | npm |
| Lua | `lua-language-server` | 手动 (GitHub releases) |
| PHP | `intelephense` | npm |
| OCaml | `ocaml-lsp` | 手动 (opam) |
| Dockerfile | `dockerfile-language-server-nodejs` | npm |
| Terraform | `terraform-ls` | 手动 |
| Dart | `dart language-server` | 手动 (dart sdk) |
| Haskell | `haskell-language-server` | 手动 (ghcup) |
| Julia | `julia` + LanguageServer.jl | 手动 |
| Clojure | `clojure-lsp` | 手动 |
| Nix | `nixd` | 手动 |
| Zig | `zls` | 手动 |
| Gleam | `gleam lsp` | 手动 (gleam install) |
| Elixir | `elixir-ls` | 手动 |
| Prisma | `prisma language-server` | 手动 |
| Kotlin | `kotlin-language-server` | 手动 |
| Java | `jdtls` | 手动 |

对于标记为“手动”的条目，请通过该语言合适的工具链管理器（rustup、ghcup、opam、brew 等）安装服务器。Hermes 会自动检测 PATH 或 `<HERMES_HOME>/lsp/bin/` 中的二进制文件。

少数服务器需要安装一个 npm 不会自动拉取的同级依赖项。当前的情况是 `typescript-language-server`，它要求 `typescript` SDK 可以从同一个 `node_modules` 树中导入 —— 当你运行 `hermes lsp install typescript` 或在首次使用时触发自动安装时，Hermes 会同时安装这两个包。

## CLI

```
hermes lsp status          # 服务状态 + 每个服务器的安装状态
hermes lsp list            # 注册表，可选 --installed-only
hermes lsp install <id>    # 主动安装一个服务器
hermes lsp install-all     # 尝试每个已知安装方法的服务器
hermes lsp restart         # 关闭正在运行的客户端
hermes lsp which <id>      # 打印解析后的二进制路径
```

`hermes lsp status` 是最好的起点 —— 它显示哪些语言今天将获得语义诊断，哪些需要安装二进制文件。

## 配置

默认设置适用于典型配置；如果二进制文件在 PATH 上，则无需设置。

```yaml
# config.yaml
lsp:
  # 主开关。禁用将跳过整个子系统 —— 不会生成服务器，也不会运行后台事件循环。
  enabled: true

  # 每次写入后等待诊断结果的时间。
  wait_mode: document      # "document" 或 "full"
  wait_timeout: 5.0

  # 如何处理缺失的服务器二进制文件。
  #   auto    — 通过 npm/pip/go install 安装到 <HERMES_HOME>/lsp/bin
  #   manual  — 仅使用 PATH 上已有的二进制文件
  install_strategy: auto

  # 每个服务器的覆盖配置（均为可选）。
  servers:
    pyright:
      disabled: false
      command: ["/abs/path/to/pyright-langserver", "--stdio"]
      env: { PYRIGHT_LOG_LEVEL: "info" }
      initialization_options:
        python:
          analysis:
            typeCheckingMode: "strict"
    typescript:
      disabled: true       # 即使其扩展名匹配，也跳过 TS
```

### 每个服务器的配置项

*   `disabled: true` — 即使其扩展名匹配文件，也完全跳过此服务器。
*   `command: [bin, ...args]` — 指定自定义二进制路径。绕过自动安装。
*   `env: {KEY: value}` — 传递给生成进程的额外环境变量。
*   `initialization_options: {...}` — 合并到 LSP `initialize` 握手期间发送的 `initializationOptions` 负载中。服务器特定；请查阅语言服务器的文档。

## 安装位置

当 `install_strategy: auto` 时，Hermes 将二进制文件安装到 `<HERMES_HOME>/lsp/bin/`。NPM 包位于 `<HERMES_HOME>/lsp/node_modules/`，其二进制符号链接位于上一级目录。Go 二进制文件来自 `go install`，其中 `GOBIN` 指向暂存目录。

不会安装任何内容到 `/usr/local/`、`~/.local/` 或任何其他共享位置 —— 暂存目录完全由 Hermes 所有，并在重置配置文件时被移除。

## 性能特征

LSP 服务器在首次使用时**延迟生成**。在从未处理过 `.py` 流量的项目中编辑 Python 文件会生成 pyright；对于大多数服务器，生成过程需要 1-3 秒（rust-analyzer 在冷项目上可能需要 10 秒以上）。同一工作区中的后续编辑会重用正在运行的服务器。

当没有发出诊断信息时，LSP 层会给干净的写入操作增加几毫秒。当发出诊断信息时，等待预算为 `wait_timeout` 秒 —— 通常 pyright/tsserver 在几十毫秒内响应，而 rust-analyzer 在索引过程中可能需要几秒钟。

服务器在 Hermes 进程的生命周期内保持活动状态。没有空闲超时回收机制 —— 每次写入都重启服务器索引的成本远高于保持守护进程运行。

## 禁用

在 `config.yaml` 中设置 `lsp.enabled: false` 以禁用整个子系统。写入后检查将回退到进程内语法检查（Python 使用 `ast.parse`，JSON 使用 `json.loads` 等），这与早期版本保持不变。

要在不禁用整个层的情况下禁用单个语言：

```yaml
lsp:
  servers:
    rust-analyzer:
      disabled: true
```

## 故障排除

**`hermes lsp status` 显示服务器状态为 "missing"**

二进制文件不在 PATH 上，也不在 `<HERMES_HOME>/lsp/bin/` 中。运行 `hermes lsp install <server_id>` 尝试自动安装，或通过该语言的常规工具链手动安装二进制文件。

**`hermes lsp status` 中的 `Backend warnings` 部分**

一些服务器是围绕外部 CLI 的薄包装，用于实际诊断 —— 它们可以正常生成并接受请求，但当辅助二进制文件缺失时从不发出错误。最常见的情况是 `bash-language-server`，它将诊断委托给 `shellcheck`。当 `hermes lsp status` 显示 `Backend warnings` 部分时，请通过你的操作系统包管理器安装指定的工具：

```
apt install shellcheck      # Debian / Ubuntu
brew install shellcheck     # macOS
scoop install shellcheck    # Windows
```

相同的警告会在服务器生成时记录一次到 `~/.hermes/logs/agent.log`。

**服务器启动但从不返回诊断信息**

检查 `~/.hermes/logs/agent.log` 中的 `[agent.lsp.client]` 条目 —— 语言服务器的 stderr 和协议错误都会记录在那里。一些服务器（尤其是 rust-analyzer）需要完成项目范围的索引后才能发出每个文件的诊断信息；服务器启动后的第一次编辑可能在没有诊断信息的情况下完成，后续编辑才会获取到。

**服务器崩溃**

崩溃的服务器会被添加到损坏集合中，并且在会话的剩余时间内不会重试。运行 `hermes lsp restart` 以清除该集合；下一次编辑会重新生成服务器。

**在 git 仓库外编辑文件**

根据设计，LSP 仅在 git 工作树内运行。在项目中运行 `git init`，或者接受进程内仅语法检查的回退。