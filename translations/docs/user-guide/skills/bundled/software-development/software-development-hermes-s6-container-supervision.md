---
title: "Hermes S6 容器监管"
sidebar_label: "Hermes S6 容器监管"
description: "修改、调试或扩展 Hermes Agent Docker 镜像内的 s6-overlay 监管树 —— 添加新服务、调试配置文件网关、理解架构 B 主程序模式..."
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Hermes S6 容器监管

修改、调试或扩展 Hermes Agent Docker 镜像内的 s6-overlay 监管树 —— 添加新服务、调试配置文件网关、理解架构 B 主程序模式。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/hermes-s6-container-supervision` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `docker`, `s6`, `supervision`, `gateway`, `profiles` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent), `hermes-agent-dev` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Hermes s6-overlay 容器监管

## 何时使用此技能

在以下场景中加载此技能：
- 在 Hermes Docker 镜像中添加或移除静态服务（应在每次容器启动时被监管的服务，例如仪表板）
- 诊断为什么每个配置文件的网关没有启动、重启或在 `docker restart` 后存活
- 理解为什么容器的 CMD 是 `/opt/hermes/docker/main-wrapper.sh` 以及带前导破折号的参数如何到达用户的程序
- 修改 `cont-init.d` 启动脚本（UID 重映射、卷种子、配置文件协调）
- 更改每个配置文件网关的渲染运行脚本（阶段 4）

如果你只是运行 Hermes Agent 并想使用 Docker，请参阅 `website/docs/user-guide/docker.md`。

## 架构概览

<!-- ascii-guard-ignore -->
```
/init                                  ← PID 1 (s6-overlay v3.2.3.0)
├── cont-init.d                        ← 一次性设置，以 root 身份运行
│   ├── 01-hermes-setup                ← docker/stage2-hook.sh
│   │   ├── UID/GID 重映射
│   │   ├── chown /opt/data
│   │   ├── chown /opt/data/profiles (每次启动)
│   │   ├── 种子 .env / config.yaml / SOUL.md
│   │   └── skills_sync.py
│   └── 02-reconcile-profiles          ← hermes_cli.container_boot
│       ├── chown /run/service (hermes-writable for runtime register)
│       └── 遍历 $HERMES_HOME/profiles/<name>/gateway_state.json
│           → 重新创建 /run/service/gateway-<name>/
│           → 仅自动启动那些 prior_state == "running" 的
│
├── s6-rc.d (静态服务，位于 /etc/s6-overlay/s6-rc.d/)
│   ├── main-hermes/run                ← exec sleep infinity (无操作槽位)
│   └── dashboard/run                  ← 如果 HERMES_DASHBOARD=1，运行 `hermes dashboard`
│
├── /run/service (s6-svscan 监视；tmpfs)
│   ├── gateway-coder/                 ← 运行时注册的每个配置文件
│   │   ├── type        ("longrun")
│   │   ├── run         ("#!/command/with-contenv sh ... exec s6-setuidgid hermes hermes -p coder gateway run")
│   │   ├── down        (标记 —— 存在表示“已注册但不自动启动”)
│   │   └── log/run     (s6-log → $HERMES_HOME/logs/gateways/coder/current)
│   └── ...
│
└── CMD ("主程序")                     ← /opt/hermes/docker/main-wrapper.sh
    └── 路由用户参数：bare exec | hermes 子命令 | hermes (无参数)
        — 由 /init 执行，继承 stdin/stdout/stderr (TTY 用于 --tui)
```
<!-- ascii-guard-ignore-end -->

## 关键文件

| 路径 | 作用 |
|---|---|
| `Dockerfile` | s6-overlay 安装 + cont-init.d 布线 + `ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]` |
| `docker/stage2-hook.sh` | "旧的入口点逻辑" —— UID 重映射、chown、种子、技能同步。作为 cont-init.d/01-hermes-setup 运行。 |
| `docker/cont-init.d/02-reconcile-profiles` | 每次启动时调用 `hermes_cli.container_boot`，从持久化卷恢复配置文件网关槽位。 |
| `docker/main-wrapper.sh` | 容器的 CMD。路由用户参数，通过 `s6-setuidgid` 切换到 hermes，执行选定的程序。 |
| `docker/s6-rc.d/main-hermes/run` | 无操作 `sleep infinity` —— 槽位存在以确保 s6-rc 用户包有效；主 hermes 作为 CMD 运行，而非受监管的服务。 |
| `docker/s6-rc.d/dashboard/run` | 条件服务 —— `exec sleep infinity`，除非 `HERMES_DASHBOARD` 为真值。 |
| `docker/entrypoint.sh` | 向后兼容的垫片，`exec` 执行 stage2 hook。硬编码旧入口点路径的外部脚本仍然有效。 |
| `hermes_cli/service_manager.py` | `S6ServiceManager`: `register_profile_gateway`, `unregister_profile_gateway`, `start/stop/restart/is_running`, `list_profile_gateways`。 |
| `hermes_cli/container_boot.py` | `reconcile_profile_gateways()` —— 遍历持久化配置文件，重新生成 s6 槽位，输出 `container-boot.log`。 |
| `hermes_cli/gateway.py::_dispatch_via_service_manager_if_s6` | 拦截 `hermes gateway start/stop/restart` 并在容器中运行时路由到 s6。 |

## 为什么采用架构 B（CMD 作为主程序，而非 s6 监管）

最初的计划（v1–v3）要求主 hermes 作为受监管的 s6-rc 服务运行。两个真实的 s6-overlay v3 机制阻止了这一点：

1.  **cont-init.d 脚本接收不到 CMD 参数** —— 因此 stage2 hook 无法解析 `docker run <image> chat -q "hi"` 来为服务 `run` 脚本设置 `HERMES_ARGS`。
2.  **`/run/s6/basedir/bin/halt` 不会传播** 写入 `/run/s6-linux-init-container-results/exitcode` 的退出码。无论怎样，容器总是以 143 (SIGTERM) 退出。s6 作者 skarnet 在 [issue #477](https://github.com/just-containers/s6-overlay/issues/477) 中确认：_"如果你想关闭容器，你需要让你的 CMD 退出，或者，如果你没有 CMD，写入你想要的容器退出码然后调用 halt"_。
因此我们采用 s6-overlay-native 的 CMD 模式：`ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]`。/init 会自动将包装脚本前置到用户参数前——所以 `docker run <image> --version` 会变成 `/init main-wrapper.sh --version`，而 `--version` 不会被 /init 的 POSIX shell 拦截。包装脚本通过 `s6-setuidgid` 切换到 hermes 用户，然后 exec 执行选定的程序。程序的退出码成为容器的退出码，完全匹配 pre-s6 tini 的约定。

权衡：主要的 hermes 进程在 s6 下不受监管。这完全匹配其在 tini（pre-s6 镜像）下的行为。Dashboard 的监管是唯一**新增**的保证——而位于 `/run/service/` 下的每个 profile 的消息网关则获得完整的监管。

## 快速操作指南

### 验证 s6 是运行中容器的 PID 1

```sh
docker exec <c> sh -c 'cat /proc/1/comm; readlink /proc/1/exe'
# 期望输出：s6-svscan 或 init / /package/admin/s6/.../s6-svscan
```

### 检查一个 profile 消息网关服务

```sh
# /command/ 不在 docker-exec 的 PATH 中——使用绝对路径
docker exec <c> /command/s6-svstat /run/service/gateway-<name>
# "up (pid …) … seconds"            → 正在运行
# "down (exitcode N) … seconds, normally up, want up, …" → s6 希望它启动但进程持续退出（崩溃循环）
# "down … normally up, ready …"     → 用户停止了它
```

### 手动启动/停止一个服务

```sh
docker exec <c> /command/s6-svc -u /run/service/gateway-<name>   # 启动
docker exec <c> /command/s6-svc -d /run/service/gateway-<name>   # 停止
docker exec <c> /command/s6-svc -t /run/service/gateway-<name>   # SIGTERM（重启）
```

### 查看 cont-init 协调器日志

```sh
docker exec <c> tail -n 50 /opt/data/logs/container-boot.log
# 2026-05-21T06:18:05+0000 profile=coder prior_state=running action=started
# 2026-05-21T06:18:05+0000 profile=writer prior_state=stopped action=registered
```

### 添加一个新的静态服务

1. 创建 `docker/s6-rc.d/<name>/type`，内容为 `longrun\n`，并创建 `docker/s6-rc.d/<name>/run`（使用 `#!/command/with-contenv sh` + `# shellcheck shell=sh`）。
2. 在 run 脚本顶部通过 `s6-setuidgid hermes` 切换到 hermes 用户（除非你明确需要 root 权限）。
3. 创建空的 `docker/s6-rc.d/<name>/dependencies.d/base`，使其等待 base 服务包。
4. 创建空的 `docker/s6-rc.d/user/contents.d/<name>`，使其加入 user 服务包。
5. Dockerfile 中的 `COPY docker/s6-rc.d/` 会自动包含它——无需其他更改。

### 更改每个 profile 消息网关的运行命令

编辑 `hermes_cli/service_manager.py` 中的 `S6ServiceManager._render_run_script` 函数。该函数也会在启动协调期间被 `hermes_cli/container_boot.py::_register_service` 调用，因此它是唯一的事实来源。同时更新 `tests/hermes_cli/test_service_manager.py::test_s6_register_creates_service_dir_and_triggers_scan` 中相应的断言。

### 运行 Docker 测试套件

```sh
docker build -t hermes-agent-harness:latest .
HERMES_TEST_IMAGE=hermes-agent-harness:latest scripts/run_tests.sh tests/docker/ -v
# 期望结果：针对 s6 镜像，19 个测试通过，0 个预期失败
```

测试套件位于 `tests/docker/`，当 Docker 不可用时会被跳过。每个测试的超时时间已提升至 180 秒（参见 `tests/docker/conftest.py`）。

## 常见问题

### 通过 `docker exec` 出现 "command not found"

`/command/`（s6-overlay 放置其二进制文件的位置）仅在由监管树生成的进程（服务、cont-init.d、main-wrapper.sh）的 PATH 中。`docker exec <c> s6-svstat …` 会失败并提示 "command not found"；请始终使用绝对路径 `/command/s6-svstat`。`hermes` 二进制文件可以工作是因为 Dockerfile 将 `/opt/hermes/.venv/bin` 添加到了运行时的 `ENV PATH` 中。

### Profile 目录所有权

cont-init 协调器以 hermes 用户身份运行（`02-reconcile-profiles` 中的 `s6-setuidgid hermes`）。如果某个 profile 目录最终归 root 所有（例如，因为默认情况下 `docker exec <c> hermes profile create …` 以 root 身份运行），协调器将无法读取 SOUL.md 并因 `PermissionError` 而失败。缓解措施：`stage2-hook.sh` 在**每次**启动时，以幂等的方式将 `$HERMES_HOME/profiles` 的所有权更改为 hermes。不要移除该代码块。

### `docker exec` 写入的文件归 root 所有

`docker exec` 默认以 root 身份运行。要么传递 `--user hermes` 参数，要么依赖下一次重启时的 stage2 chown 清理。不要手动以 root 身份在 `$HERMES_HOME/profiles/<name>/` 下写入文件——下一次协调过程会清理它们，但正在进行的操作可能会遇到权限错误。

### 服务槽位存在但 s6-svstat 显示 "s6-supervise not running"

服务目录位于 tmpfs 上，并在容器重启时被清空。要么 cont-init 协调器尚未运行（在 `docker restart` 后稍等片刻），要么它运行失败了。检查 `docker logs <c> | grep '02-reconcile'`。

### 消息网关启动后立即退出（svstat 中显示 `down (exitcode 1)`）

很可能 profile 没有配置模型或认证。服务槽位是正确的——消息网关本身未配置。请先运行 `hermes -p <profile> setup`。s6 监管器会持续重启它；这是期望的行为（当你修复配置后，下一次尝试会成功并保持运行）。

### 协调器跳过了某个 profile

协调器以**是否存在 `SOUL.md`** 作为“真实 profile”的标记。`hermes profile create` 总是会创建它。如果一个 profile 目录缺少 SOUL.md（残留目录、部分恢复、备份进行中），协调器会故意跳过它。添加一个 `SOUL.md`（即使是空的）以重新纳入协调。

### "求助，容器以 143 退出！"

检查是否有东西调用了 `s6-svscanctl -t` 或 `/run/s6/basedir/bin/halt`——两者都会导致 /init 开始 stage 3 关闭，但返回 143 (SIGTERM) 而不是期望的退出码。这是从架构 A 转向架构 B 的 Phase 2 设计变更。要实现带有真实退出码的容器关闭，你必须让 CMD (main-wrapper.sh) 正常退出；**不要**尝试从 finish 脚本控制退出。

## 相关技能

- `hermes-agent-dev`: 通用 hermes-agent 代码库导航
- `hermes-tool-quirks`: 特定 Hermes 工具变通方案（sed/grep 等）——在调试 s6 栈与 hermes 内置工具的交互时加载。