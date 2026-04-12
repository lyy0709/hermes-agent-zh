---
sidebar_position: 3
title: "Nix & NixOS 配置"
description: "使用 Nix 安装和部署 Hermes Agent —— 从快速的 `nix run` 到完全声明式的 NixOS 模块（包含容器模式）"
---

# Nix & NixOS 配置

Hermes Agent 提供了一个 Nix flake，包含三个级别的集成：

| 级别 | 适用人群 | 你将获得 |
|-------|-------------|--------------|
| **`nix run` / `nix profile install`** | 任何 Nix 用户（macOS, Linux） | 包含所有依赖的预构建二进制文件 —— 然后使用标准的 CLI 工作流 |
| **NixOS 模块（原生）** | NixOS 服务器部署 | 声明式配置、强化的 systemd 服务、托管的密钥 |
| **NixOS 模块（容器）** | 需要自我修改的 Agent | 以上所有功能，外加一个持久的 Ubuntu 容器，Agent 可以在其中执行 `apt`/`pip`/`npm install` |

:::info 与标准安装有何不同
`curl | bash` 安装程序自行管理 Python、Node 和依赖项。Nix flake 取代了所有这些 —— 每个 Python 依赖项都是由 [uv2nix](https://github.com/pyproject-nix/uv2nix) 构建的 Nix derivation，运行时工具（Node.js, git, ripgrep, ffmpeg）被包装到二进制文件的 PATH 中。没有运行时的 pip，没有 venv 激活，没有 `npm install`。

**对于非 NixOS 用户**，这只会改变安装步骤。之后的所有操作（`hermes setup`, `hermes gateway install`, 配置编辑）与标准安装完全相同。

**对于 NixOS 模块用户**，整个生命周期都不同：配置位于 `configuration.nix` 中，密钥通过 sops-nix/agenix 管理，服务是一个 systemd 单元，并且 CLI 配置命令被阻止。你管理 hermes 的方式与管理任何其他 NixOS 服务的方式相同。
:::

## 先决条件

- **启用了 flakes 的 Nix** —— 推荐使用 [Determinate Nix](https://install.determinate.systems)（默认启用 flakes）
- 你想要使用的服务的 **API 密钥**（至少需要：OpenRouter 或 Anthropic 密钥）

---

## 快速开始（任何 Nix 用户）

无需克隆。Nix 会获取、构建并运行一切：

```bash
# 直接运行（首次使用时构建，之后缓存）
nix run github:NousResearch/hermes-agent -- setup
nix run github:NousResearch/hermes-agent -- chat

# 或者持久化安装
nix profile install github:NousResearch/hermes-agent
hermes setup
hermes chat
```

在 `nix profile install` 之后，`hermes`、`hermes-agent` 和 `hermes-acp` 将被添加到你的 PATH 中。从此刻起，工作流与[标准安装](./installation.md)完全相同 —— `hermes setup` 会引导你完成提供商选择，`hermes gateway install` 会设置 launchd（macOS）或 systemd 用户服务，配置位于 `~/.hermes/`。

<details>
<summary><strong>从本地克隆构建</strong></summary>

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
nix build
./result/bin/hermes setup
```

</details>

---

## NixOS 模块

该 flake 导出了 `nixosModules.default` —— 一个完整的 NixOS 服务模块，以声明式方式管理用户创建、目录、配置生成、密钥、文档和服务生命周期。

:::note
此模块需要 NixOS。对于非 NixOS 系统（macOS，其他 Linux 发行版），请使用 `nix profile install` 和上面提到的标准 CLI 工作流。
:::

### 添加 Flake 输入

```nix
# /etc/nixos/flake.nix（或你的系统 flake）
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    hermes-agent.url = "github:NousResearch/hermes-agent";
  };

  outputs = { nixpkgs, hermes-agent, ... }: {
    nixosConfigurations.your-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        hermes-agent.nixosModules.default
        ./configuration.nix
      ];
    };
  };
}
```

### 最小配置

```nix
# configuration.nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];
    addToSystemPackages = true;
  };
}
```

就这样。`nixos-rebuild switch` 会创建 `hermes` 用户，生成 `config.yaml`，连接密钥，并启动消息网关 —— 这是一个长期运行的服务，用于将 Agent 连接到消息平台（Telegram, Discord 等）并监听传入的消息。

:::warning 密钥是必需的
上面的 `environmentFiles` 行假设你已经配置了 [sops-nix](https://github.com/Mic92/sops-nix) 或 [agenix](https://github.com/ryantm/agenix)。该文件应至少包含一个 LLM 提供商密钥（例如，`OPENROUTER_API_KEY=sk-or-...`）。完整设置请参阅[密钥管理](#secrets-management)。如果你还没有密钥管理器，可以先使用一个纯文本文件作为起点 —— 只需确保它不是全局可读的：

```bash
echo "OPENROUTER_API_KEY=sk-or-your-key" | sudo install -m 0600 -o hermes /dev/stdin /var/lib/hermes/env
```

```nix
services.hermes-agent.environmentFiles = [ "/var/lib/hermes/env" ];
```
:::

:::tip addToSystemPackages
设置 `addToSystemPackages = true` 会做两件事：将 `hermes` CLI 放在你的系统 PATH 中，**并且** 系统范围内设置 `HERMES_HOME`，以便交互式 CLI 与消息网关服务共享状态（会话、技能、定时任务）。如果没有它，在 shell 中运行 `hermes` 会创建一个单独的 `~/.hermes/` 目录。
:::

:::info 容器感知的 CLI
当 `container.enable = true` 且 `addToSystemPackages = true` 时，主机上的 **每一个** `hermes` 命令都会自动路由到托管的容器中。这意味着你的交互式 CLI 会话在与消息网关服务相同的执行环境中运行 —— 可以访问所有容器内安装的软件包和工具。

- 路由是透明的：`hermes chat`、`hermes sessions list`、`hermes version` 等命令都会在底层 exec 到容器中
- 所有 CLI 标志都会按原样转发
- 如果容器未运行，CLI 会短暂重试（交互式使用时有 5 秒的旋转器，脚本中静默等待 10 秒），然后以清晰的错误信息失败 —— 不会静默回退
- 对于在 hermes 代码库上工作的开发者，设置 `HERMES_DEV=1` 可以绕过容器路由，直接运行本地检出
:::
设置 `container.hostUsers` 以创建指向服务状态目录的 `~/.hermes` 符号链接，使主机 CLI 与容器共享会话、配置和记忆：

```nix
services.hermes-agent = {
  container.enable = true;
  container.hostUsers = [ "your-username" ];
  addToSystemPackages = true;
};
```

`hostUsers` 中列出的用户会自动添加到 `hermes` 组以获取文件权限访问。

**Podman 用户：** NixOS 服务以 root 身份运行容器。Docker 用户通过 `docker` 组套接字获取访问权限，但 Podman 的 rootful 容器需要 sudo。为你的容器运行时授予无密码 sudo 权限：

```nix
security.sudo.extraRules = [{
  users = [ "your-username" ];
  commands = [{
    command = "/run/current-system/sw/bin/podman";
    options = [ "NOPASSWD" ];
  }];
}];
```

CLI 会自动检测何时需要 sudo 并透明地使用它。若不进行此设置，你将需要手动运行 `sudo hermes chat`。
:::

### 验证运行

执行 `nixos-rebuild switch` 后，检查服务是否正在运行：

```bash
# 检查服务状态
systemctl status hermes-agent

# 查看日志（按 Ctrl+C 停止）
journalctl -u hermes-agent -f

# 如果 addToSystemPackages 为 true，测试 CLI
hermes version
hermes config       # 显示生成的配置
```

### 选择部署模式

该模块支持两种模式，由 `container.enable` 控制：

| | **原生**（默认） | **容器** |
|---|---|---|
| 运行方式 | 主机上的强化 systemd 服务 | 持久化的 Ubuntu 容器，绑定挂载了 `/nix/store` |
| 安全性 | `NoNewPrivileges`、`ProtectSystem=strict`、`PrivateTmp` | 容器隔离，在内部以非特权用户运行 |
| Agent 能否自行安装软件包 | 否 — 仅限 Nix 提供的 PATH 上的工具 | 是 — `apt`、`pip`、`npm` 安装会在重启后持久化 |
| 配置界面 | 相同 | 相同 |
| 何时选择 | 标准部署、最高安全性、可复现性 | Agent 需要运行时安装软件包、可变环境、实验性工具 |

要启用容器模式，添加一行：

```nix
{
  services.hermes-agent = {
    enable = true;
    container.enable = true;
    # ... 其余配置相同
  };
}
```

:::info
容器模式通过 `mkDefault` 自动启用 `virtualisation.docker.enable`。如果你使用 Podman，请设置 `container.backend = "podman"` 和 `virtualisation.docker.enable = false`。
:::

---

## 配置

### 声明式设置

`settings` 选项接受一个任意的属性集，该属性集会被渲染为 `config.yaml`。它支持跨多个模块定义的深度合并（通过 `lib.recursiveUpdate`），因此你可以在多个文件间拆分配置：

```nix
# base.nix
services.hermes-agent.settings = {
  model.default = "anthropic/claude-sonnet-4";
  toolsets = [ "all" ];
  terminal = { backend = "local"; timeout = 180; };
};

# personality.nix
services.hermes-agent.settings = {
  display = { compact = false; personality = "kawaii"; };
  memory = { memory_enabled = true; user_profile_enabled = true; };
};
```

两者在求值时会进行深度合并。Nix 声明的键总是优先于磁盘上现有 `config.yaml` 中的键，但 **Nix 未触及的用户添加的键会被保留**。这意味着如果 Agent 或手动编辑添加了像 `skills.disabled` 或 `streaming.enabled` 这样的键，它们会在 `nixos-rebuild switch` 后保留。

:::note 模型命名
`settings.model.default` 使用你的提供商期望的模型标识符。使用 [OpenRouter](https://openrouter.ai)（默认）时，这些标识符看起来像 `"anthropic/claude-sonnet-4"` 或 `"google/gemini-3-flash"`。如果你直接使用提供商（Anthropic、OpenAI），请设置 `settings.model.base_url` 指向他们的 API，并使用他们原生的模型 ID（例如 `"claude-sonnet-4-20250514"`）。当没有设置 `base_url` 时，Hermes 默认使用 OpenRouter。
:::

:::tip 发现可用的配置键
运行 `nix build .#configKeys && cat result` 以查看从 Python 的 `DEFAULT_CONFIG` 中提取的每个叶子配置键。你可以将现有的 `config.yaml` 粘贴到 `settings` 属性集中 — 结构是 1:1 映射的。
:::

<details>
<summary><strong>完整示例：所有常用自定义设置</strong></summary>

```nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    container.enable = true;

    # ── 模型 ──────────────────────────────────────────────────────────
    settings = {
      model = {
        base_url = "https://openrouter.ai/api/v1";
        default = "anthropic/claude-opus-4.6";
      };
      toolsets = [ "all" ];
      max_turns = 100;
      terminal = { backend = "local"; cwd = "."; timeout = 180; };
      compression = {
        enabled = true;
        threshold = 0.85;
        summary_model = "google/gemini-3-flash-preview";
      };
      memory = { memory_enabled = true; user_profile_enabled = true; };
      display = { compact = false; personality = "kawaii"; };
      agent = { max_turns = 60; verbose = false; };
    };

    # ── 密钥 ────────────────────────────────────────────────────────
    environmentFiles = [ config.sops.secrets."hermes-env".path ];

    # ── 文档 ──────────────────────────────────────────────────────
    documents = {
      "SOUL.md" = builtins.readFile /home/user/.hermes/SOUL.md;
      "USER.md" = ./documents/USER.md;
    };

    # ── MCP 服务器 ────────────────────────────────────────────────────
    mcpServers.filesystem = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-filesystem" "/data/workspace" ];
    };

    # ── 容器选项 ──────────────────────────────────────────────
    container = {
      image = "ubuntu:24.04";
      backend = "docker";
      hostUsers = [ "your-username" ];
      extraVolumes = [ "/home/user/projects:/projects:rw" ];
      extraOptions = [ "--gpus" "all" ];
    };

    # ── 服务调优 ─────────────────────────────────────────────────
    addToSystemPackages = true;
    extraArgs = [ "--verbose" ];
    restart = "always";
    restartSec = 5;
  };
}
```

</details>

### 逃生舱：使用你自己的配置
如果您更希望在 Nix 之外完全管理 `config.yaml`，请使用 `configFile`：

```nix
services.hermes-agent.configFile = /etc/hermes/config.yaml;
```

这将完全绕过 `settings` —— 不进行合并，也不生成。该文件在每次激活时都会按原样复制到 `$HERMES_HOME/config.yaml`。

### 自定义速查表

Nix 用户最常需要自定义内容的快速参考：

| 我想... | 选项 | 示例 |
|---|---|---|
| 更改 LLM 模型 | `settings.model.default` | `"anthropic/claude-sonnet-4"` |
| 使用不同的提供商端点 | `settings.model.base_url` | `"https://openrouter.ai/api/v1"` |
| 添加 API 密钥 | `environmentFiles` | `[ config.sops.secrets."hermes-env".path ]` |
| 赋予 Agent 个性 | `documents."SOUL.md"` | `builtins.readFile ./my-soul.md` |
| 添加 MCP 工具服务器 | `mcpServers.<name>` | 参见 [MCP 服务器](#mcp-servers) |
| 将主机目录挂载到容器中 | `container.extraVolumes` | `[ "/data:/data:rw" ]` |
| 将 GPU 访问权限传递给容器 | `container.extraOptions` | `[ "--gpus" "all" ]` |
| 使用 Podman 代替 Docker | `container.backend` | `"podman"` |
| 在主机 CLI 和容器之间共享状态 | `container.hostUsers` | `[ "sidbin" ]` |
| 向服务 PATH 添加工具（仅限原生） | `extraPackages` | `[ pkgs.pandoc pkgs.imagemagick ]` |
| 使用自定义基础镜像 | `container.image` | `"ubuntu:24.04"` |
| 覆盖 hermes 包 | `package` | `inputs.hermes-agent.packages.${system}.default.override { ... }` |
| 更改状态目录 | `stateDir` | `"/opt/hermes"` |
| 设置 Agent 的工作目录 | `workingDirectory` | `"/home/user/projects"` |

---

## 密钥管理

:::danger 切勿将 API 密钥放入 `settings` 或 `environment`
Nix 表达式中的值最终会进入 `/nix/store`，该目录是全局可读的。请始终使用带有密钥管理器的 `environmentFiles`。
:::

`environment`（非机密变量）和 `environmentFiles`（机密文件）都会在激活时（`nixos-rebuild switch`）合并到 `$HERMES_HOME/.env` 中。Hermes 在每次启动时都会读取此文件，因此更改会在 `systemctl restart hermes-agent` 后生效 —— 无需重新创建容器。

### sops-nix

```nix
{
  sops = {
    defaultSopsFile = ./secrets/hermes.yaml;
    age.keyFile = "/home/user/.config/sops/age/keys.txt";
    secrets."hermes-env" = { format = "yaml"; };
  };

  services.hermes-agent.environmentFiles = [
    config.sops.secrets."hermes-env".path
  ];
}
```

密钥文件包含键值对：

```yaml
# secrets/hermes.yaml (使用 sops 加密)
hermes-env: |
    OPENROUTER_API_KEY=sk-or-...
    TELEGRAM_BOT_TOKEN=123456:ABC...
    ANTHROPIC_API_KEY=sk-ant-...
```

### agenix

```nix
{
  age.secrets.hermes-env.file = ./secrets/hermes-env.age;

  services.hermes-agent.environmentFiles = [
    config.age.secrets.hermes-env.path
  ];
}
```

### OAuth / 认证信息预置

对于需要 OAuth 的平台（例如 Discord），使用 `authFile` 在首次部署时预置凭据：

```nix
{
  services.hermes-agent = {
    authFile = config.sops.secrets."hermes/auth.json".path;
    # authFileForceOverwrite = true;  # 每次激活时都覆盖
  };
}
```

仅当 `auth.json` 尚不存在时才会复制该文件（除非设置了 `authFileForceOverwrite = true`）。运行时 OAuth Token 刷新会写入状态目录，并在重建过程中保留。

---

## 文档

`documents` 选项将文件安装到 Agent 的工作目录（即 `workingDirectory`，Agent 将其视为其工作空间）。Hermes 按照约定查找特定的文件名：

- **`SOUL.md`** — Agent 的系统提示词 / 人格。Hermes 在启动时读取此文件，并将其用作持久的指令，以塑造其在所有会话中的行为。
- **`USER.md`** — 关于 Agent 交互用户的信息。
- 您放置在此处的任何其他文件都将作为工作空间文件对 Agent 可见。

```nix
{
  services.hermes-agent.documents = {
    "SOUL.md" = ''
      您是一位专门研究 NixOS 打包的乐于助人的研究助手。
      请始终引用来源，并优先选择可复现的解决方案。
    '';
    "USER.md" = ./documents/USER.md;  # 路径引用，从 Nix store 复制
  };
}
```

值可以是内联字符串或路径引用。文件在每次 `nixos-rebuild switch` 时都会安装。

---

## MCP 服务器

`mcpServers` 选项以声明方式配置 [MCP（模型上下文协议）](https://modelcontextprotocol.io) 服务器。每个服务器使用 **stdio**（本地命令）或 **HTTP**（远程 URL）传输方式。

### Stdio 传输（本地服务器）

```nix
{
  services.hermes-agent.mcpServers = {
    filesystem = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-filesystem" "/data/workspace" ];
    };
    github = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-github" ];
      env.GITHUB_PERSONAL_ACCESS_TOKEN = "\${GITHUB_TOKEN}"; # 从 .env 解析
    };
  };
}
```

:::提示
`env` 值中的环境变量在运行时从 `$HERMES_HOME/.env` 解析。使用 `environmentFiles` 来注入密钥 —— 切勿将 Token 直接放在 Nix 配置中。
:::

### HTTP 传输（远程服务器）

```nix
{
  services.hermes-agent.mcpServers.remote-api = {
    url = "https://mcp.example.com/v1/mcp";
    headers.Authorization = "Bearer \${MCP_REMOTE_API_KEY}";
    timeout = 180;
  };
}
```

### 使用 OAuth 的 HTTP 传输

对于使用 OAuth 2.1 的服务器，设置 `auth = "oauth"`。Hermes 实现了完整的 PKCE 流程 —— 元数据发现、动态客户端注册、Token 交换和自动刷新。

```nix
{
  services.hermes-agent.mcpServers.my-oauth-server = {
    url = "https://mcp.example.com/mcp";
    auth = "oauth";
  };
}
```

Token 存储在 `$HERMES_HOME/mcp-tokens/<server-name>.json` 中，并在重启和重建过程中持久保存。

<details>
<summary><strong>在无头服务器上进行初始 OAuth 授权</strong></summary>

首次 OAuth 授权需要基于浏览器的同意流程。在无头部署中，Hermes 会将授权 URL 打印到 stdout/日志，而不是打开浏览器。
</details>
**选项 A：交互式引导** — 通过 `docker exec`（容器模式）或 `sudo -u hermes`（原生模式）运行一次流程：

```bash
# 容器模式
docker exec -it hermes-agent \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth

# 原生模式
sudo -u hermes HERMES_HOME=/var/lib/hermes/.hermes \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
```

容器使用 `--network=host`，因此主机浏览器可以访问 `127.0.0.1` 上的 OAuth 回调监听器。

**选项 B：预置 Token** — 在工作站上完成流程，然后复制 Token：

```bash
hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
scp ~/.hermes/mcp-tokens/my-oauth-server{,.client}.json \
    server:/var/lib/hermes/.hermes/mcp-tokens/
# 确保：chown hermes:hermes, chmod 0600
```

</details>

### 采样（服务器发起的 LLM 请求）

一些 MCP 服务器可以向 Agent 请求 LLM 补全：

```nix
{
  services.hermes-agent.mcpServers.analysis = {
    command = "npx";
    args = [ "-y" "analysis-server" ];
    sampling = {
      enabled = true;
      model = "google/gemini-3-flash";
      max_tokens_cap = 4096;
      timeout = 30;
      max_rpm = 10;
    };
  };
}
```

---

## 托管模式

当 hermes 通过 NixOS 模块运行时，以下 CLI 命令会被**阻止**，并显示一个描述性错误，指引你查看 `configuration.nix`：

| 被阻止的命令 | 原因 |
|---|---|
| `hermes setup` | 配置是声明式的 — 在 Nix 配置中编辑 `settings` |
| `hermes config edit` | 配置由 `settings` 生成 |
| `hermes config set <key> <value>` | 配置由 `settings` 生成 |
| `hermes gateway install` | systemd 服务由 NixOS 管理 |
| `hermes gateway uninstall` | systemd 服务由 NixOS 管理 |

这可以防止 Nix 声明的内容与磁盘上的内容之间出现偏差。检测使用两个信号：

1. **`HERMES_MANAGED=true`** 环境变量 — 由 systemd 服务设置，对消息网关进程可见
2. **`.managed` 标记文件** 位于 `HERMES_HOME` 中 — 由激活脚本设置，对交互式 shell 可见（例如，`docker exec -it hermes-agent hermes config set ...` 也会被阻止）

要更改配置，请编辑你的 Nix 配置并运行 `sudo nixos-rebuild switch`。

---

## 容器架构

:::info
本节仅在你使用 `container.enable = true` 时相关。原生模式部署请跳过。
:::

启用容器模式时，hermes 在一个持久的 Ubuntu 容器内运行，Nix 构建的二进制文件以只读方式从主机绑定挂载：

```
主机                                    容器
────                                    ─────────
/nix/store/...-hermes-agent-0.1.0  ──►  /nix/store/... (ro)
~/.hermes -> /var/lib/hermes/.hermes       (符号链接桥接，按 hostUsers)
/var/lib/hermes/                    ──►  /data/          (rw)
  ├── current-package -> /nix/store/...    (符号链接，每次重建时更新)
  ├── .gc-root -> /nix/store/...           (防止 nix-collect-garbage)
  ├── .container-identity                  (sha256 哈希，触发重新创建)
  ├── .hermes/                             (HERMES_HOME)
  │   ├── .env                             (由 environment + environmentFiles 合并而来)
  │   ├── config.yaml                      (Nix 生成，由激活脚本深度合并)
  │   ├── .managed                         (标记文件)
  │   ├── .container-mode                  (路由元数据：后端、exec_user 等)
  │   ├── state.db, sessions/, memories/   (运行时状态)
  │   └── mcp-tokens/                      (MCP 服务器的 OAuth Token)
  ├── home/                                ──►  /home/hermes    (rw)
  └── workspace/                           (MESSAGING_CWD)
      ├── SOUL.md                          (来自 documents 选项)
      └── (agent 创建的文件)

容器可写层 (apt/pip/npm):   /usr, /usr/local, /tmp
```

Nix 构建的二进制文件可以在 Ubuntu 容器内工作，因为 `/nix/store` 被绑定挂载 — 它自带解释器和所有依赖项，因此不依赖于容器的系统库。容器入口点通过 `current-package` 符号链接解析：`/data/current-package/bin/hermes gateway run --replace`。在 `nixos-rebuild switch` 时，只更新符号链接 — 容器继续运行。

### 跨事件持久化情况

| 事件 | 容器是否重新创建？ | `/data` (状态) | `/home/hermes` | 可写层 (`apt`/`pip`/`npm`) |
|---|---|---|---|---|
| `systemctl restart hermes-agent` | 否 | 持久化 | 持久化 | 持久化 |
| `nixos-rebuild switch` (代码变更) | 否 (符号链接更新) | 持久化 | 持久化 | 持久化 |
| 主机重启 | 否 | 持久化 | 持久化 | 持久化 |
| `nix-collect-garbage` | 否 (GC 根) | 持久化 | 持久化 | 持久化 |
| 镜像变更 (`container.image`) | **是** | 持久化 | 持久化 | **丢失** |
| 卷/选项变更 | **是** | 持久化 | 持久化 | **丢失** |
| `environment`/`environmentFiles` 变更 | 否 | 持久化 | 持久化 | 持久化 |

容器仅在其**身份哈希**更改时才会重新创建。哈希涵盖：模式版本、镜像、`extraVolumes`、`extraOptions` 和入口点脚本。环境变量、设置、文档或 hermes 包本身的更改**不会**触发重新创建。

:::warning 可写层丢失
当身份哈希更改时（镜像升级、新卷、新容器选项），容器会被销毁并从 `container.image` 的新拉取中重新创建。可写层中的任何 `apt install`、`pip install` 或 `npm install` 包都会丢失。`/data` 和 `/home/hermes` 中的状态会被保留（这些是绑定挂载）。

如果 Agent 依赖特定的包，请考虑将它们烘焙到自定义镜像中 (`container.image = "my-registry/hermes-base:latest"`) 或在 Agent 的 SOUL.md 中编写安装脚本。
:::

### GC 根保护

`preStart` 脚本在 `${stateDir}/.gc-root` 处创建一个指向当前 hermes 包的 GC 根。这可以防止 `nix-collect-garbage` 删除正在运行的二进制文件。如果 GC 根意外损坏，重启服务会重新创建它。
---

## 开发

### 开发环境

该 flake 提供了一个包含 Python 3.11、uv、Node.js 和所有运行时工具的开发环境：

```bash
cd hermes-agent
nix develop

# Shell 提供：
#   - Python 3.11 + uv（首次进入时依赖项安装到 .venv）
#   - Node.js 20、ripgrep、git、openssh、ffmpeg 在 PATH 中
#   - 时间戳文件优化：如果依赖项未更改，重新进入几乎是即时的

hermes setup
hermes chat
```

### direnv（推荐）

包含的 `.envrc` 会自动激活开发环境：

```bash
cd hermes-agent
direnv allow    # 一次性操作
# 后续进入几乎是即时的（时间戳文件跳过依赖安装）
```

### Flake 检查

该 flake 包含在 CI 和本地运行的构建时验证：

```bash
# 运行所有检查
nix flake check

# 单独检查
nix build .#checks.x86_64-linux.package-contents   # 二进制文件存在 + 版本
nix build .#checks.x86_64-linux.entry-points-sync  # pyproject.toml ↔ Nix 包同步
nix build .#checks.x86_64-linux.cli-commands        # gateway/config 子命令
nix build .#checks.x86_64-linux.managed-guard       # HERMES_MANAGED 阻止修改
nix build .#checks.x86_64-linux.bundled-skills      # 包中包含技能
nix build .#checks.x86_64-linux.config-roundtrip    # 合并脚本保留用户键
```

<details>
<summary><strong>每个检查验证的内容</strong></summary>

| 检查项 | 测试内容 |
|---|---|
| `package-contents` | `hermes` 和 `hermes-agent` 二进制文件存在，且 `hermes version` 可运行 |
| `entry-points-sync` | `pyproject.toml` 中的每个 `[project.scripts]` 条目在 Nix 包中都有一个包装的二进制文件 |
| `cli-commands` | `hermes --help` 暴露 `gateway` 和 `config` 子命令 |
| `managed-guard` | `HERMES_MANAGED=true hermes config set ...` 打印 NixOS 错误 |
| `bundled-skills` | 技能目录存在，包含 SKILL.md 文件，包装器中设置了 `HERMES_BUNDLED_SKILLS` |
| `config-roundtrip` | 7 种合并场景：全新安装、Nix 覆盖、用户键保留、混合合并、MCP 附加合并、嵌套深度合并、幂等性 |

</details>

---

## 选项参考

### 核心

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `enable` | `bool` | `false` | 启用 hermes-agent 服务 |
| `package` | `package` | `hermes-agent` | 要使用的 hermes-agent 包 |
| `user` | `str` | `"hermes"` | 系统用户 |
| `group` | `str` | `"hermes"` | 系统组 |
| `createUser` | `bool` | `true` | 自动创建用户/组 |
| `stateDir` | `str` | `"/var/lib/hermes"` | 状态目录（`HERMES_HOME` 的父目录） |
| `workingDirectory` | `str` | `"${stateDir}/workspace"` | Agent 工作目录（`MESSAGING_CWD`） |
| `addToSystemPackages` | `bool` | `false` | 将 `hermes` CLI 添加到系统 PATH 并在系统范围内设置 `HERMES_HOME` |

### 配置

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `settings` | `attrs`（深度合并） | `{}` | 声明式配置，渲染为 `config.yaml`。支持任意嵌套；多个定义通过 `lib.recursiveUpdate` 合并 |
| `configFile` | `null` 或 `path` | `null` | 现有 `config.yaml` 的路径。如果设置，则完全覆盖 `settings` |

### 密钥与环境变量

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `environmentFiles` | `listOf str` | `[]` | 包含密钥的环境文件路径。在激活时合并到 `$HERMES_HOME/.env` 中 |
| `environment` | `attrsOf str` | `{}` | 非密钥环境变量。**在 Nix 存储中可见**——请勿在此处放置密钥 |
| `authFile` | `null` 或 `path` | `null` | OAuth 凭据种子。仅在首次部署时复制 |
| `authFileForceOverwrite` | `bool` | `false` | 在激活时始终从 `authFile` 覆盖 `auth.json` |

### 文档

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `documents` | `attrsOf (either str path)` | `{}` | 工作空间文件。键是文件名，值是内联字符串或路径。在激活时安装到 `workingDirectory` |

### MCP 服务器

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `mcpServers` | `attrsOf submodule` | `{}` | MCP 服务器定义，合并到 `settings.mcp_servers` 中 |
| `mcpServers.<name>.command` | `null` 或 `str` | `null` | 服务器命令（stdio 传输） |
| `mcpServers.<name>.args` | `listOf str` | `[]` | 命令参数 |
| `mcpServers.<name>.env` | `attrsOf str` | `{}` | 服务器进程的环境变量 |
| `mcpServers.<name>.url` | `null` 或 `str` | `null` | 服务器端点 URL（HTTP/StreamableHTTP 传输） |
| `mcpServers.<name>.headers` | `attrsOf str` | `{}` | HTTP 头，例如 `Authorization` |
| `mcpServers.<name>.auth` | `null` 或 `"oauth"` | `null` | 身份验证方法。`"oauth"` 启用 OAuth 2.1 PKCE |
| `mcpServers.<name>.enabled` | `bool` | `true` | 启用或禁用此服务器 |
| `mcpServers.<name>.timeout` | `null` 或 `int` | `null` | 工具调用超时（秒）（默认：120） |
| `mcpServers.<name>.connect_timeout` | `null` 或 `int` | `null` | 连接超时（秒）（默认：60） |
| `mcpServers.<name>.tools` | `null` 或 `submodule` | `null` | 工具过滤（`include`/`exclude` 列表） |
| `mcpServers.<name>.sampling` | `null` 或 `submodule` | `null` | 服务器发起的 LLM 请求的采样配置 |

### 服务行为

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `extraArgs` | `listOf str` | `[]` | `hermes gateway` 的额外参数 |
| `extraPackages` | `listOf package` | `[]` | 服务 PATH 上的额外包（仅限原生模式） |
| `restart` | `str` | `"always"` | systemd `Restart=` 策略 |
| `restartSec` | `int` | `5` | systemd `RestartSec=` 值 |

### 容器

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `container.enable` | `bool` | `false` | 启用 OCI 容器模式 |
| `container.backend` | `enum ["docker" "podman"]` | `"docker"` | 容器运行时 |
| `container.image` | `str` | `"ubuntu:24.04"` | 基础镜像（运行时拉取） |
| `container.extraVolumes` | `listOf str` | `[]` | 额外的卷挂载（`host:container:mode`） |
| `container.extraOptions` | `listOf str` | `[]` | 传递给 `docker create` 的额外参数 |
| `container.hostUsers` | `listOf str` | `[]` | 交互式用户，他们将获得指向服务 stateDir 的 `~/.hermes` 符号链接，并自动添加到 `hermes` 组 |
---

## 目录结构

### 原生模式

```
/var/lib/hermes/                     # stateDir (所有者 hermes:hermes，权限 0750)
├── .hermes/                         # HERMES_HOME
│   ├── config.yaml                  # Nix 生成（每次重建时深度合并）
│   ├── .managed                     # 标记：CLI 配置修改被阻止
│   ├── .env                         # 从 environment + environmentFiles 合并而来
│   ├── auth.json                    # OAuth 凭证（初始注入，之后自我管理）
│   ├── gateway.pid
│   ├── state.db
│   ├── mcp-tokens/                  # MCP 服务器的 OAuth Token
│   ├── sessions/
│   ├── memories/
│   ├── skills/
│   ├── cron/
│   └── logs/
├── home/                            # Agent 的 HOME 目录
└── workspace/                       # MESSAGING_CWD
    ├── SOUL.md                      # 来自 documents 选项
    └── (agent 创建的文件)
```

### 容器模式

相同的结构，挂载到容器中：

| 容器路径 | 主机路径 | 模式 | 说明 |
|---|---|---|---|
| `/nix/store` | `/nix/store` | `ro` | Hermes 二进制文件 + 所有 Nix 依赖 |
| `/data` | `/var/lib/hermes` | `rw` | 所有状态、配置、工作空间 |
| `/home/hermes` | `${stateDir}/home` | `rw` | 持久化的 Agent home 目录 — `pip install --user`、工具缓存 |
| `/usr`, `/usr/local`, `/tmp` | (可写层) | `rw` | `apt`/`pip`/`npm` 安装 — 在重启间持久化，容器重建时丢失 |

---

## 更新

```bash
# 更新 flake 输入
nix flake update hermes-agent --flake /etc/nixos

# 重建
sudo nixos-rebuild switch
```

在容器模式下，`current-package` 符号链接会被更新，Agent 在重启时会使用新的二进制文件。无需重建容器，已安装的包不会丢失。

---

## 故障排除

:::tip Podman 用户
以下所有 `docker` 命令在 `podman` 上同样适用。如果设置了 `container.backend = "podman"`，请相应替换。
:::

### 服务日志

```bash
# 两种模式使用相同的 systemd 单元
journalctl -u hermes-agent -f

# 容器模式：也可以直接查看
docker logs -f hermes-agent
```

### 容器检查

```bash
systemctl status hermes-agent
docker ps -a --filter name=hermes-agent
docker inspect hermes-agent --format='{{.State.Status}}'
docker exec -it hermes-agent bash
docker exec hermes-agent readlink /data/current-package
docker exec hermes-agent cat /data/.container-identity
```

### 强制重建容器

如果需要重置可写层（全新的 Ubuntu）：

```bash
sudo systemctl stop hermes-agent
docker rm -f hermes-agent
sudo rm /var/lib/hermes/.container-identity
sudo systemctl start hermes-agent
```

### 验证密钥是否已加载

如果 Agent 启动但无法与 LLM 提供商认证，请检查 `.env` 文件是否正确合并：

```bash
# 原生模式
sudo -u hermes cat /var/lib/hermes/.hermes/.env

# 容器模式
docker exec hermes-agent cat /data/.hermes/.env
```

### GC Root 验证

```bash
nix-store --query --roots $(docker exec hermes-agent readlink /data/current-package)
```

### 常见问题

| 症状 | 原因 | 修复方法 |
|---|---|---|
| `Cannot save configuration: managed by NixOS` | CLI 防护已激活 | 编辑 `configuration.nix` 并执行 `nixos-rebuild switch` |
| 容器意外重建 | `extraVolumes`、`extraOptions` 或 `image` 发生更改 | 预期行为 — 可写层重置。重新安装包或使用自定义镜像 |
| `hermes version` 显示旧版本 | 容器未重启 | `systemctl restart hermes-agent` |
| 对 `/var/lib/hermes` 权限被拒绝 | 状态目录权限为 `0750 hermes:hermes` | 使用 `docker exec` 或 `sudo -u hermes` |
| `nix-collect-garbage` 移除了 hermes | GC root 缺失 | 重启服务（preStart 会重新创建 GC root） |
| `no container with name or ID "hermes-agent"` (Podman) | Podman rootful 容器对普通用户不可见 | 为 podman 添加无密码 sudo（参见[容器感知 CLI](#container-aware-cli) 部分） |
| `unable to find user hermes` | 容器仍在启动中（入口点尚未创建用户） | 等待几秒钟后重试 — CLI 会自动重试 |