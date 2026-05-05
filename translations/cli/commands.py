"""Hermes CLI 的斜杠命令定义和自动补全。

所有斜杠命令的中央注册表。每个使用者——CLI 帮助、消息网关分发、Telegram BotCommands、Slack 子命令映射、自动补全——都从 ``COMMAND_REGISTRY`` 派生其数据。

添加命令：向 ``COMMAND_REGISTRY`` 添加一个 ``CommandDef`` 条目。
添加别名：在现有的 ``CommandDef`` 上设置 ``aliases=("short",)``。
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from utils import is_truthy_value

logger = logging.getLogger(__name__)

# prompt_toolkit 是一个可选的 CLI 依赖项——仅用于
# SlashCommandCompleter 和 SlashCommandAutoSuggest。缺少它的网关和测试
# 环境仍然必须能够导入此模块
# 用于 resolve_command、gateway_help_lines 和 COMMAND_REGISTRY。
try:
    from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
    from prompt_toolkit.completion import Completer, Completion
except ImportError:  # pragma: no cover
    AutoSuggest = object  # type: ignore[assignment,misc]
    Completer = object    # type: ignore[assignment,misc]
    Suggestion = None     # type: ignore[assignment]
    Completion = None     # type: ignore[assignment]


# ---------------------------------------------------------------------------
# CommandDef 数据类
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CommandDef:
    """单个斜杠命令的定义。"""

    name: str                          # 不带斜杠的规范名称："background"
    description: str                   # 人类可读的描述
    category: str                      # "Session", "Configuration", 等。
    aliases: tuple[str, ...] = ()      # 替代名称：("bg",)
    args_hint: str = ""                # 参数占位符："<prompt>", "[name]"
    subcommands: tuple[str, ...] = ()  # 可标签补全的子命令
    cli_only: bool = False             # 仅在 CLI 中可用
    gateway_only: bool = False         # 仅在网关/消息传递中可用
    gateway_config_gate: str | None = None  # 配置点路径；当为真值时，覆盖网关的 cli_only


# ---------------------------------------------------------------------------
# 中央注册表——单一事实来源
# ---------------------------------------------------------------------------

COMMAND_REGISTRY: list[CommandDef] = [
    # 会话
    CommandDef("new", "开始一个新会话（新的会话 ID + 历史记录）", "Session",
               aliases=("reset",), args_hint="[name]"),
    CommandDef("topic", "启用或检查 Telegram DM 话题会话", "Session",
               gateway_only=True, args_hint="[off|help|session-id]"),
    CommandDef("clear", "清屏并开始一个新会话", "Session",
               cli_only=True),
    CommandDef("redraw", "强制完全重绘 UI（从终端漂移中恢复）", "Session",
               cli_only=True),
    CommandDef("history", "显示对话历史记录", "Session",
               cli_only=True),
    CommandDef("save", "保存当前对话", "Session",
               cli_only=True),
    CommandDef("retry", "重试最后一条消息（重新发送给 Agent）", "Session"),
    CommandDef("undo", "移除最后一条用户/助手交换", "Session"),
    CommandDef("title", "为当前会话设置标题", "Session",
               args_hint="[name]"),
    CommandDef("branch", "分支当前会话（探索不同路径）", "Session",
               aliases=("fork",), args_hint="[name]"),
    CommandDef("compress", "手动压缩对话上下文", "Session",
               args_hint="[focus topic]"),
    CommandDef("rollback", "列出或恢复文件系统检查点", "Session",
               args_hint="[number]"),
    CommandDef("snapshot", "创建或恢复 Hermes 配置/状态的状态快照", "Session",
               cli_only=True, aliases=("snap",), args_hint="[create|restore <id>|prune]"),
    CommandDef("stop", "终止所有正在运行的后台进程", "Session"),
    CommandDef("approve", "批准一个待处理的危险命令", "Session",
               gateway_only=True, args_hint="[session|always]"),
    CommandDef("deny", "拒绝一个待处理的危险命令", "Session",
               gateway_only=True),
    CommandDef("background", "在后台运行一个提示", "Session",
               aliases=("bg", "btw"), args_hint="<prompt>"),
    CommandDef("agents", "显示活跃的 Agent 和正在运行的任务", "Session",
               aliases=("tasks",)),
    CommandDef("queue", "为下一轮排队一个提示（不中断）", "Session",
               aliases=("q",), args_hint="<prompt>"),
    CommandDef("steer", "在下一次工具调用后注入一条消息而不中断", "Session",
               args_hint="<prompt>"),
    CommandDef("goal", "设置一个 Hermes 在多个回合中持续努力直到达成的长期目标", "Session",
               args_hint="[text | pause | resume | clear | status]"),
    CommandDef("status", "显示会话信息", "Session"),
    CommandDef("profile", "显示活跃的配置文件名称和主目录", "Info"),
    CommandDef("sethome", "将此聊天设置为主频道", "Session",
               gateway_only=True, aliases=("set-home",)),
    CommandDef("resume", "恢复一个先前命名的会话", "Session",
               args_hint="[name]"),

    # 配置
    CommandDef("config", "显示当前配置", "Configuration",
               cli_only=True),
    CommandDef("model", "为此会话切换模型", "Configuration",
               aliases=("provider",), args_hint="[model] [--provider name] [--global]"),
    CommandDef("gquota", "显示 Google Gemini Code Assist 配额使用情况", "Info",
               cli_only=True),

    CommandDef("personality", "设置预定义的人格", "Configuration",
               args_hint="[name]"),
    CommandDef("statusbar", "切换上下文/模型状态栏", "Configuration",
               cli_only=True, aliases=("sb",)),
    CommandDef("verbose", "循环工具进度显示：关闭 -> 新 -> 全部 -> 详细",
               "Configuration", cli_only=True,
               gateway_config_gate="display.tool_progress_command"),
    CommandDef("footer", "切换最终回复上的网关运行时元数据页脚",
               "Configuration", args_hint="[on|off|status]",
               subcommands=("on", "off", "status")),
    CommandDef("yolo", "切换 YOLO 模式（跳过所有危险命令批准）",
               "Configuration"),
    CommandDef("reasoning", "管理推理努力和显示", "Configuration",
               args_hint="[level|show|hide]",
               subcommands=("none", "minimal", "low", "medium", "high", "xhigh", "show", "hide", "on", "off")),
    CommandDef("fast", "切换快速模式——OpenAI 优先处理 / Anthropic 快速模式（普通/快速）", "Configuration",
               args_hint="[normal|fast|status]",
               subcommands=("normal", "fast", "status", "on", "off")),
    CommandDef("skin", "显示或更改显示皮肤/主题", "Configuration",
               cli_only=True, args_hint="[name]"),
    CommandDef("indicator", "选择 TUI 忙碌指示器样式", "Configuration",
               cli_only=True, args_hint="[kaomoji|emoji|unicode|ascii]",
               subcommands=("kaomoji", "emoji", "unicode", "ascii")),
    CommandDef("voice", "切换语音模式", "Configuration",
               args_hint="[on|off|tts|status]", subcommands=("on", "off", "tts", "status")),
    CommandDef("busy", "控制 Hermes 工作时 Enter 键的作用", "Configuration",
               cli_only=True, args_hint="[queue|steer|interrupt|status]",
               subcommands=("queue", "steer", "interrupt", "status")),

    # 工具和技能
    CommandDef("tools", "管理工具：/tools [list|disable|enable] [name...]", "Tools & Skills",
               args_hint="[list|disable|enable] [name...]", cli_only=True),
    CommandDef("toolsets", "列出可用的工具集", "Tools & Skills",
               cli_only=True),
    CommandDef("skills", "搜索、安装、检查或管理技能",
               "Tools & Skills", cli_only=True,
               subcommands=("search", "browse", "inspect", "install")),
    CommandDef("cron", "管理定时任务", "Tools & Skills",
               cli_only=True, args_hint="[subcommand]",
               subcommands=("list", "add", "create", "edit", "pause", "resume", "run", "remove")),
    CommandDef("curator", "后台技能维护（状态、运行、固定、归档）",
               "Tools & Skills", args_hint="[subcommand]",
               subcommands=("status", "run", "pause", "resume", "pin", "unpin", "restore")),
    CommandDef("kanban", "多配置文件协作板（任务、链接、评论）",
               "Tools & Skills", args_hint="[subcommand]",
               subcommands=("list", "ls", "show", "create", "assign", "link", "unlink",
                            "claim", "comment", "complete", "block", "unblock", "archive",
                            "tail", "dispatch", "context", "init", "gc")),
    CommandDef("reload", "将 .env 变量重新加载到正在运行的会话中", "Tools & Skills",
               cli_only=True),
    CommandDef("reload-mcp", "从配置重新加载 MCP 服务器", "Tools & Skills",
               aliases=("reload_mcp",)),
    CommandDef("reload-skills", "重新扫描 ~/.hermes/skills/ 以查找新安装或移除的技能",
               "Tools & Skills", aliases=("reload_skills",)),
    CommandDef("browser", "通过 CDP 将浏览器工具连接到您正在运行的 Chrome", "Tools & Skills",
               cli_only=True, args_hint="[connect|disconnect|status]",
               subcommands=("connect", "disconnect", "status")),
    CommandDef("plugins", "列出已安装的插件及其状态",
               "Tools & Skills", cli_only=True),

    # 信息
    CommandDef("commands", "浏览所有命令和技能（分页）", "Info",
               gateway_only=True, args_hint="[page]"),
    CommandDef("help", "显示可用命令", "Info"),
    CommandDef("restart", "在排空活跃运行后优雅地重启网关", "Session",
               gateway_only=True),
    CommandDef("usage", "显示当前会话的 Token 使用情况和速率限制", "Info"),
    CommandDef("insights", "显示使用洞察和分析", "Info",
               args_hint="[days]"),
    CommandDef("platforms", "显示网关/消息传递平台状态", "Info",
               cli_only=True, aliases=("gateway",)),
    CommandDef("copy", "将最后一条助手响应复制到剪贴板", "Info",
               cli_only=True, args_hint="[number]"),
    CommandDef("paste", "从剪贴板附加图像", "Info",
               cli_only=True),
    CommandDef("image", "为您的下一个提示附加本地图像文件", "Info",
               cli_only=True, args_hint="<path>"),
    CommandDef("update", "将 Hermes Agent 更新到最新版本", "Info",
               gateway_only=True),
    CommandDef("debug", "上传调试报告（系统信息 + 日志）并获取可分享链接", "Info"),

    # 退出
    CommandDef("quit", "退出 CLI", "Exit",
               cli_only=True, aliases=("exit",)),
]


# ---------------------------------------------------------------------------
# 派生查找表——在导入时构建一次，由 rebuild_lookups() 刷新
# ---------------------------------------------------------------------------
def _build_command_lookup() -> dict[str, CommandDef]:
    """Map every name and alias to its CommandDef."""
    lookup: dict[str, CommandDef] = {}
    for cmd in COMMAND_REGISTRY:
        lookup[cmd.name] = cmd
        for alias in cmd.aliases:
            lookup[alias] = cmd
    return lookup


_COMMAND_LOOKUP: dict[str, CommandDef] = _build_command_lookup()


def resolve_command(name: str) -> CommandDef | None:
    """Resolve a command name or alias to its CommandDef.

    Accepts names with or without the leading slash.
    """
    return _COMMAND_LOOKUP.get(name.lower().lstrip("/"))


def _build_description(cmd: CommandDef) -> str:
    """Build a CLI-facing description string including usage hint."""
    if cmd.args_hint:
        return f"{cmd.description} (用法: /{cmd.name} {cmd.args_hint})"
    return cmd.description


# Backwards-compatible flat dict: "/command" -> description
COMMANDS: dict[str, str] = {}
for _cmd in COMMAND_REGISTRY:
    if not _cmd.gateway_only:
        COMMANDS[f"/{_cmd.name}"] = _build_description(_cmd)
        for _alias in _cmd.aliases:
            COMMANDS[f"/{_alias}"] = f"{_cmd.description} (/ {_cmd.name} 的别名)"


# Backwards-compatible categorized dict
COMMANDS_BY_CATEGORY: dict[str, dict[str, str]] = {}
for _cmd in COMMAND_REGISTRY:
    if not _cmd.gateway_only:
        _cat = COMMANDS_BY_CATEGORY.setdefault(_cmd.category, {})
        _cat[f"/{_cmd.name}"] = COMMANDS[f"/{_cmd.name}"]
        for _alias in _cmd.aliases:
            _cat[f"/{_alias}"] = COMMANDS[f"/{_alias}"]


# Subcommands lookup: "/cmd" -> ["sub1", "sub2", ...]
SUBCOMMANDS: dict[str, list[str]] = {}
for _cmd in COMMAND_REGISTRY:
    if _cmd.subcommands:
        SUBCOMMANDS[f"/{_cmd.name}"] = list(_cmd.subcommands)

# Also extract subcommands hinted in args_hint via pipe-separated patterns
# e.g. args_hint="[on|off|tts|status]" for commands that don't have explicit subcommands.
# NOTE: If a command already has explicit subcommands, this fallback is skipped.
# Use the `subcommands` field on CommandDef for intentional tab-completable args.
_PIPE_SUBS_RE = re.compile(r"[a-z]+(?:\|[a-z]+)+")
for _cmd in COMMAND_REGISTRY:
    key = f"/{_cmd.name}"
    if key in SUBCOMMANDS or not _cmd.args_hint:
        continue
    m = _PIPE_SUBS_RE.search(_cmd.args_hint)
    if m:
        SUBCOMMANDS[key] = m.group(0).split("|")


# ---------------------------------------------------------------------------
# Gateway helpers
# ---------------------------------------------------------------------------

# Set of all command names + aliases recognized by the gateway.
# Includes config-gated commands so the gateway can dispatch them
# (the handler checks the config gate at runtime).
GATEWAY_KNOWN_COMMANDS: frozenset[str] = frozenset(
    name
    for cmd in COMMAND_REGISTRY
    if not cmd.cli_only or cmd.gateway_config_gate
    for name in (cmd.name, *cmd.aliases)
)


def is_gateway_known_command(name: str | None) -> bool:
    """Return True if ``name`` resolves to a gateway-dispatchable slash command.

    This covers both built-in commands (``GATEWAY_KNOWN_COMMANDS`` derived
    from ``COMMAND_REGISTRY``) and plugin-registered commands, which are
    looked up lazily so importing this module never forces plugin
    discovery. Gateway code uses this to decide whether to emit
    ``command:<name>`` hooks — plugin commands get the same lifecycle
    events as built-ins.
    """
    if not name:
        return False
    if name in GATEWAY_KNOWN_COMMANDS:
        return True
    for plugin_name, _description, _args_hint in _iter_plugin_command_entries():
        if plugin_name == name:
            return True
    return False


# Commands with explicit Level-2 running-agent handlers in gateway/run.py.
# Listed here for introspection / tests; semantically a subset of
# "all resolvable commands" — which is the real bypass set (see
# should_bypass_active_session below).
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset(
    {
        "agents",
        "approve",
        "background",
        "commands",
        "deny",
        "help",
        "new",
        "profile",
        "queue",
        "restart",
        "status",
        "steer",
        "stop",
        "update",
    }
)
def should_bypass_active_session(command_name: str | None) -> bool:
    """Return True for any resolvable slash command.

    Rationale: every gateway-registered slash command either has a
    specific Level-2 handler in gateway/run.py (/stop, /new, /model,
    /approve, etc.) or reaches the running-agent catch-all that returns
    a "busy — wait or /stop first" response. In both paths the command
    is dispatched, not queued.

    Queueing is always wrong for a recognized slash command because the
    safety net in gateway.run discards any command text that reaches
    the pending queue — which meant a mid-run /model (or /reasoning,
    /voice, /insights, /title, /resume, /retry, /undo, /compress,
    /usage, /reload-mcp, /sethome, /reset) would silently
    interrupt the agent AND get discarded, producing a zero-char
    response. See issue #5057 / PRs #6252, #10370, #4665.

    ACTIVE_SESSION_BYPASS_COMMANDS remains the subset of commands with
    explicit Level-2 handlers; the rest fall through to the catch-all.
    """
    return resolve_command(command_name) is not None if command_name else False


def _resolve_config_gates() -> set[str]:
    """Return canonical names of commands whose ``gateway_config_gate`` is truthy.

    Reads ``config.yaml`` and walks the dot-separated key path for each
    config-gated command.  Returns an empty set on any error so callers
    degrade gracefully.
    """
    gated = [c for c in COMMAND_REGISTRY if c.gateway_config_gate]
    if not gated:
        return set()
    try:
        from hermes_cli.config import read_raw_config
        cfg = read_raw_config()
    except Exception:
        return set()
    result: set[str] = set()
    for cmd in gated:
        val: Any = cfg
        for key in cmd.gateway_config_gate.split("."):
            if isinstance(val, dict):
                val = val.get(key)
            else:
                val = None
                break
        if is_truthy_value(val, default=False):
            result.add(cmd.name)
    return result


def _is_gateway_available(cmd: CommandDef, config_overrides: set[str] | None = None) -> bool:
    """Check if *cmd* should appear in gateway surfaces (help, menus, mappings).

    Unconditionally available when ``cli_only`` is False.  When ``cli_only``
    is True but ``gateway_config_gate`` is set, the command is available only
    when the config value is truthy.  Pass *config_overrides* (from
    ``_resolve_config_gates()``) to avoid re-reading config for every command.
    """
    if not cmd.cli_only:
        return True
    if cmd.gateway_config_gate:
        overrides = config_overrides if config_overrides is not None else _resolve_config_gates()
        return cmd.name in overrides
    return False


def _requires_argument(args_hint: str) -> bool:
    """Return True when selecting a command without text would be incomplete."""
    return args_hint.strip().startswith("<")


def gateway_help_lines() -> list[str]:
    """Generate gateway help text lines from the registry."""
    overrides = _resolve_config_gates()
    lines: list[str] = []
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        args = f" {cmd.args_hint}" if cmd.args_hint else ""
        alias_parts: list[str] = []
        for a in cmd.aliases:
            # Skip internal aliases like reload_mcp (underscore variant)
            if a.replace("-", "_") == cmd.name.replace("-", "_") and a != cmd.name:
                continue
            alias_parts.append(f"`/{a}`")
        alias_note = f" (别名: {', '.join(alias_parts)})" if alias_parts else ""
        lines.append(f"`/{cmd.name}{args}` -- {cmd.description}{alias_note}")
    return lines
def _iter_plugin_command_entries() -> list[tuple[str, str, str]]:
    """Yield (name, description, args_hint) tuples for all plugin slash commands.

    Plugin commands are registered via
    :func:`hermes_cli.plugins.PluginContext.register_command`. They behave
    like ``CommandDef`` entries for gateway surfacing: they appear in the
    Telegram command menu, in Slack's ``/hermes`` subcommand mapping, and
    (via :func:`gateway.platforms.discord._register_slash_commands`) in
    Discord's native slash command picker.

    Lookup is lazy so importing this module never forces plugin discovery
    (which can trigger filesystem scans and environment-dependent
    behavior).
    """
    try:
        from hermes_cli.plugins import get_plugin_commands
    except Exception:
        return []
    try:
        commands = get_plugin_commands() or {}
    except Exception:
        return []
    entries: list[tuple[str, str, str]] = []
    for name, meta in commands.items():
        if not isinstance(name, str) or not isinstance(meta, dict):
            continue
        description = str(meta.get("description") or f"执行 /{name}")
        args_hint = str(meta.get("args_hint") or "").strip()
        entries.append((name, description, args_hint))
    return entries


def telegram_bot_commands() -> list[tuple[str, str]]:
    """Return (command_name, description) pairs for Telegram setMyCommands.

    Telegram command names cannot contain hyphens, so they are replaced with
    underscores.  Aliases are skipped -- Telegram shows one menu entry per
    canonical command. Commands that require arguments are skipped because
    selecting a Telegram BotCommand sends only ``/command`` and would execute
    an incomplete command.

    Plugin-registered slash commands are included so plugins get native
    autocomplete in Telegram without touching core code.
    """
    overrides = _resolve_config_gates()
    result: list[tuple[str, str]] = []
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        if _requires_argument(cmd.args_hint):
            continue
        tg_name = _sanitize_telegram_name(cmd.name)
        if tg_name:
            result.append((tg_name, cmd.description))
    for name, description, args_hint in _iter_plugin_command_entries():
        if _requires_argument(args_hint):
            continue
        tg_name = _sanitize_telegram_name(name)
        if tg_name:
            result.append((tg_name, description))
    return result


_CMD_NAME_LIMIT = 32
"""Max command name length shared by Telegram and Discord."""

# Backward-compat alias — tests and external code may reference the old name.
_TG_NAME_LIMIT = _CMD_NAME_LIMIT

# Telegram Bot API allows only lowercase a-z, 0-9, and underscores in
# command names.  This regex strips everything else after initial conversion.
_TG_INVALID_CHARS = re.compile(r"[^a-z0-9_]")
_TG_MULTI_UNDERSCORE = re.compile(r"_{2,}")


def _sanitize_telegram_name(raw: str) -> str:
    """Convert a command/skill/plugin name to a valid Telegram command name.

    Telegram requires: 1-32 chars, lowercase a-z, digits 0-9, underscores only.
    Steps: lowercase → replace hyphens with underscores → strip all other
    invalid characters → collapse consecutive underscores → strip leading/
    trailing underscores.
    """
    name = raw.lower().replace("-", "_")
    name = _TG_INVALID_CHARS.sub("", name)
    name = _TG_MULTI_UNDERSCORE.sub("_", name)
    return name.strip("_")
def _clamp_command_names(
    entries: list[tuple[str, ...]],
    reserved: set[str],
) -> list[tuple[str, ...]]:
    """Enforce 32-char command name limit with collision avoidance.

    Both Telegram and Discord cap slash command names at 32 characters.
    Names exceeding the limit are truncated.  If truncation creates a duplicate
    (against *reserved* names or earlier entries in the same batch), the name is
    shortened to 31 chars and a digit ``0``-``9`` is appended to differentiate.
    If all 10 digit slots are taken the entry is silently dropped.

    Accepts tuples of any length >= 2.  Extra elements beyond ``(name, desc)``
    (e.g. ``cmd_key``) are passed through unchanged, so callers can attach
    metadata that survives the rename.
    """
    used: set[str] = set(reserved)
    result: list[tuple] = []
    for entry in entries:
        name, desc, *extra = entry
        if len(name) > _CMD_NAME_LIMIT:
            candidate = name[:_CMD_NAME_LIMIT]
            if candidate in used:
                prefix = name[:_CMD_NAME_LIMIT - 1]
                for digit in range(10):
                    candidate = f"{prefix}{digit}"
                    if candidate not in used:
                        break
                else:
                    # All 10 digit slots exhausted — skip entry
                    continue
            name = candidate
        if name in used:
            continue
        used.add(name)
        result.append((name, desc, *extra))
    return result


# Backward-compat alias.
_clamp_telegram_names = _clamp_command_names


# ---------------------------------------------------------------------------
# Shared skill/plugin collection for gateway platforms
# ---------------------------------------------------------------------------

def _collect_gateway_skill_entries(
    platform: str,
    max_slots: int,
    reserved_names: set[str],
    desc_limit: int = 100,
    sanitize_name: "Callable[[str], str] | None" = None,
) -> tuple[list[tuple[str, str, str]], int]:
    """Collect plugin + skill entries for a gateway platform.

    Priority order:
      1. Plugin slash commands (take precedence over skills)
      2. Built-in skill commands (fill remaining slots, alphabetical)

    Only skills are trimmed when the cap is reached.
    Hub-installed skills are excluded.  Per-platform disabled skills are
    excluded.

    Args:
        platform: Platform identifier for per-platform skill filtering
            (``"telegram"``, ``"discord"``, etc.).
        max_slots: Maximum number of entries to return (remaining slots after
            built-in/core commands).
        reserved_names: Names already taken by built-in commands.  Mutated
            in-place as new names are added.
        desc_limit: Max description length (40 for Telegram, 100 for Discord).
        sanitize_name: Optional name transform applied before clamping, e.g.
            :func:`_sanitize_telegram_name` for Telegram.  May return an
            empty string to signal "skip this entry".

    Returns:
        ``(entries, hidden_count)`` where *entries* is a list of
        ``(name, description, cmd_key)`` triples and *hidden_count* is the
        number of skill entries dropped due to the cap.  ``cmd_key`` is the
        original ``/skill-name`` key from :func:`get_skill_commands`.
    """
    all_entries: list[tuple[str, str, str]] = []

    # --- Tier 1: Plugin slash commands (never trimmed) ---------------------
    plugin_pairs: list[tuple[str, str]] = []
    try:
        from hermes_cli.plugins import get_plugin_commands
        plugin_cmds = get_plugin_commands()
        for cmd_name in sorted(plugin_cmds):
            name = sanitize_name(cmd_name) if sanitize_name else cmd_name
            if not name:
                continue
            desc = plugin_cmds[cmd_name].get("description", "插件命令")
            if len(desc) > desc_limit:
                desc = desc[:desc_limit - 3] + "..."
            plugin_pairs.append((name, desc))
    except Exception:
        pass

    plugin_pairs = _clamp_command_names(plugin_pairs, reserved_names)
    reserved_names.update(n for n, _ in plugin_pairs)
    # Plugins have no cmd_key — use empty string as placeholder
    for n, d in plugin_pairs:
        all_entries.append((n, d, ""))

    # --- Tier 2: Built-in skill commands (trimmed at cap) -----------------
    _platform_disabled: set[str] = set()
    try:
        from agent.skill_utils import get_disabled_skill_names
        _platform_disabled = get_disabled_skill_names(platform=platform)
    except Exception:
        pass

    skill_triples: list[tuple[str, str, str]] = []
    try:
        from agent.skill_commands import get_skill_commands
        from tools.skills_tool import SKILLS_DIR
        from agent.skill_utils import get_external_skills_dirs
        _skills_dir = str(SKILLS_DIR.resolve())
        _hub_dir = str((SKILLS_DIR / ".hub").resolve()).rstrip("/") + "/"
        # Build set of allowed directory prefixes: local skills dir + any
        # user-configured ``skills.external_dirs``. Ensure each prefix ends
        # with ``/`` so ``/my-skills`` does not also match ``/my-skills-extra``.
        # Without this widening, external skills are visible in
        # ``hermes skills list`` and the agent's ``/skill-name`` dispatch but
        # silently excluded from gateway slash menus (#8110).
        _allowed_prefixes = [_skills_dir.rstrip("/") + "/"]
        _allowed_prefixes.extend(
            str(d).rstrip("/") + "/" for d in get_external_skills_dirs()
        )
        skill_cmds = get_skill_commands()
        for cmd_key in sorted(skill_cmds):
            info = skill_cmds[cmd_key]
            skill_path = info.get("skill_md_path", "")
            if not skill_path:
                continue
            if not any(skill_path.startswith(prefix) for prefix in _allowed_prefixes):
                continue
            if skill_path.startswith(_hub_dir):
                continue
            skill_name = info.get("name", "")
            if skill_name in _platform_disabled:
                continue
            raw_name = cmd_key.lstrip("/")
            name = sanitize_name(raw_name) if sanitize_name else raw_name
            if not name:
                continue
            desc = info.get("description", "")
            if len(desc) > desc_limit:
                desc = desc[:desc_limit - 3] + "..."
            skill_triples.append((name, desc, cmd_key))
    except Exception:
        pass

    # Clamp names; cmd_key is passed through as extra payload so it survives
    # any clamp-induced renames.
    skill_triples = _clamp_command_names(skill_triples, reserved_names)

    # Skills fill remaining slots — only tier that gets trimmed
    remaining = max(0, max_slots - len(all_entries))
    hidden_count = max(0, len(skill_triples) - remaining)
    for n, d, k in skill_triples[:remaining]:
        all_entries.append((n, d, k))

    return all_entries[:max_slots], hidden_count


# ---------------------------------------------------------------------------
# Platform-specific wrappers
# ---------------------------------------------------------------------------
def telegram_menu_commands(max_commands: int = 100) -> tuple[list[tuple[str, str]], int]:
    """返回受 Bot API 限制的 Telegram 菜单命令。

    优先级顺序（优先级越高 = 溢出时永不被挤掉）：
      1. 核心 CommandDef 命令（始终包含）
      2. 插件斜杠命令（优先于技能）
      3. 内置技能命令（填充剩余槽位，按字母顺序）

    技能是唯一在达到上限时会被修剪的层级。
    用户安装的 Hub 技能被排除在外 —— 可通过 /skills 访问。
    为 ``"telegram"`` 平台禁用的技能（通过 ``hermes skills
    config``）会完全从菜单中排除。

    返回：
        (menu_commands, hidden_count)，其中 hidden_count 是由于上限而被省略的技能命令数量。
    """
    core_commands = list(telegram_bot_commands())
    reserved_names = {n for n, _ in core_commands}
    all_commands = list(core_commands)

    remaining_slots = max(0, max_commands - len(all_commands))
    entries, hidden_count = _collect_gateway_skill_entries(
        platform="telegram",
        max_slots=remaining_slots,
        reserved_names=reserved_names,
        desc_limit=40,
        sanitize_name=_sanitize_telegram_name,
    )
    # 丢弃 cmd_key —— Telegram 只需要 (name, desc) 对。
    all_commands.extend((n, d) for n, d, _k in entries)
    return all_commands[:max_commands], hidden_count


def discord_skill_commands(
    max_slots: int,
    reserved_names: set[str],
) -> tuple[list[tuple[str, str, str]], int]:
    """返回用于 Discord 斜杠命令注册的技能条目。

    与 :func:`telegram_menu_commands` 相同的优先级和过滤逻辑
    （插件 > 技能，Hub 排除，按平台禁用排除），但适应了 Discord 的限制：

    - 名称中允许连字符（无 ``-`` → ``_`` 清理）
    - 描述限制在 100 个字符内（Discord 的每字段最大值）

    参数：
        max_slots: 可用的命令槽位（100 减去现有的内置命令数量）。
        reserved_names: 已注册的内置命令的名称。

    返回：
        ``(entries, hidden_count)``，其中 *entries* 是
        ``(discord_name, description, cmd_key)`` 三元组的列表。``cmd_key`` 是
        斜杠处理程序回调所需的原始 ``/skill-name`` 键。
    """
    return _collect_gateway_skill_entries(
        platform="discord",
        max_slots=max_slots,
        reserved_names=set(reserved_names),  # 复制 —— 不要修改调用者的集合
        desc_limit=100,
    )


def discord_skill_commands_by_category(
    reserved_names: set[str],
) -> tuple[dict[str, list[tuple[str, str, str]]], list[tuple[str, str, str]], int]:
    """返回按类别组织的技能条目，用于 Discord 的 ``/skill`` 自动补全。

    目录在扫描根目录下至少嵌套 2 层的技能
    （例如 ``creative/ascii-art/SKILL.md``）按其顶级类别分组。根级技能
    （例如 ``dogfood/SKILL.md``）作为 *未分类* 返回。

    扫描根目录包括本地 ``SKILLS_DIR`` **以及**任何配置的
    ``skills.external_dirs`` —— 匹配应用于 #18741 中扁平化
    ``discord_skill_commands()`` 收集器的拓宽过滤器。没有这种
    对等性，外部目录的技能将通过 ``hermes skills list`` 和
    Agent 的 ``/skill-name`` 调度可见，但在 Discord 的
    ``/skill`` 自动补全中却悄无声息地缺席。

    过滤镜像 :func:`discord_skill_commands`：Hub 技能排除，
    按平台禁用排除，名称限制为 32 个字符，描述
    限制为 100 个字符。

    旧的 25 组 × 25 子命令上限（来自旧的嵌套
    ``/skill <cat> <name>`` 布局）**不**适用 —— 实时调用者
    （``gateway/platforms/discord.py`` 中的 ``_register_skill_group``，在 PR #11580 中重构）
    将这些结果扁平化并馈送到单个自动补全回调中，该回调可以扩展到数千个条目而没有任何
    每个命令的有效负载问题。``hidden_count`` 保留在返回
    元组中是为了向后兼容，并且仍然报告由于其他原因被丢弃的技能
    （32 字符限制冲突与保留名称）。

    返回：
        ``(categories, uncategorized, hidden_count)``

        - *categories*: ``{category_name: [(name, description, cmd_key), ...]}``
        - *uncategorized*: ``[(name, description, cmd_key), ...]``
        - *hidden_count*: 由于名称限制冲突而丢弃的技能数量
          针对已注册的命令名称。
    """
    from pathlib import Path as _P

    _platform_disabled: set[str] = set()
    try:
        from agent.skill_utils import get_disabled_skill_names
        _platform_disabled = get_disabled_skill_names(platform="discord")
    except Exception:
        pass

    # 收集原始技能数据 --------------------------------------------------
    categories: dict[str, list[tuple[str, str, str]]] = {}
    uncategorized: list[tuple[str, str, str]] = []
    # 映射限制后的 32 字符名称 → 其来源，以便我们可以在冲突时发出
    # 可操作的警告。保留（gateway 内置）命令
    # 名称用哨兵标记，以便警告区分
    # “技能与保留命令冲突”和“两个技能在 32 字符限制上冲突”
    # —— 后者是需要重命名的情况。
    _names_used: dict[str, str] = {n: "<reserved>" for n in reserved_names}
    hidden = 0

    try:
        from agent.skill_commands import get_skill_commands
        from agent.skill_utils import get_external_skills_dirs
        from tools.skills_tool import SKILLS_DIR

        _skills_dir = SKILLS_DIR.resolve()
        _hub_dir = (SKILLS_DIR / ".hub").resolve()
        # 构建（已解析的根目录，是否为本地）元组列表。每个外部目录
        # 成为其自己的用于类别派生的扫描根目录 —— 位于
        # ``<external>/mlops/foo/SKILL.md`` 的技能仍归类为 "mlops"。
        _scan_roots: list[_P] = [_skills_dir]
        try:
            for ext in get_external_skills_dirs():
                try:
                    _scan_roots.append(_P(ext).resolve())
                except Exception:
                    continue
        except Exception:
            pass
        skill_cmds = get_skill_commands()

        for cmd_key in sorted(skill_cmds):
            info = skill_cmds[cmd_key]
            skill_path = info.get("skill_md_path", "")
            if not skill_path:
                continue
            sp = _P(skill_path).resolve()
            # Hub 技能通过技能中心加载，不作为
            # 斜杠命令公开。
            if str(sp).startswith(str(_hub_dir)):
                continue
            # 如果技能位于任何扫描根目录下，则接受；记录
            # 匹配的根目录，以便我们正确派生类别。
            matched_root: _P | None = None
            for root in _scan_roots:
                try:
                    sp.relative_to(root)
                except ValueError:
                    continue
                matched_root = root
                break
            if matched_root is None:
                continue

            skill_name = info.get("name", "")
            if skill_name in _platform_disabled:
                continue

            raw_name = cmd_key.lstrip("/")
            # 限制为 32 个字符（Discord 每个命令名称限制）
            discord_name = raw_name[:32]
            if discord_name in _names_used:
                # 两个技能的前 32 个字符相同。一个获胜
                # （看到的第一个，由于调用者迭代 ``sorted(skill_cmds)`` 而按字母顺序）；
                # 另一个从 Discord 的 /skill 自动补全中丢弃。
                #
                # 将此静默计为 ``hidden``（旧行为）
                # 意味着技能作者无法发现丢弃 ——
                # 他们的技能只是没有出现在选择器中。发出一个
                # WARNING 命名双方，以便作者可以重命名
                # 失败技能的前置名称，使其具有
                # 不同的 32 字符前缀。
                prior = _names_used[discord_name]
                if prior == "<reserved>":
                    logger.warning(
                        "Discord /skill: %r (来自 %r) 在其 32 字符限制上与保留的 gateway 命令名称 %r 冲突 —— "
                        "该技能将不会出现在 /skill 自动补全中。"
                        "重命名技能的前置 ``name:`` 使其前 32 个字符不同。",
                        discord_name, cmd_key, discord_name,
                    )
                else:
                    logger.warning(
                        "Discord /skill: %r 和 %r 在 Discord 的 32 字符命令名称限制上都限制为 %r —— "
                        "只有 %r 会出现在 /skill 自动补全中。重命名"
                        "一个技能的前置 ``name:`` 使其前 32 个字符不同。",
                        prior, cmd_key, discord_name, prior,
                    )
                hidden += 1
                continue
            _names_used[discord_name] = cmd_key

            desc = info.get("description", "")
            if len(desc) > 100:
                desc = desc[:97] + "..."

            # 根据匹配的扫描根目录内的相对路径确定类别。
            # 例如 creative/ascii-art/SKILL.md → ("creative", ...)
            rel = sp.parent.relative_to(matched_root)
            parts = rel.parts
            if len(parts) >= 2:
                cat = parts[0]
                categories.setdefault(cat, []).append((discord_name, desc, cmd_key))
            else:
                uncategorized.append((discord_name, desc, cmd_key))
    except Exception:
        pass

    return categories, uncategorized, hidden


# ---------------------------------------------------------------------------
# Slack 原生斜杠命令
# ---------------------------------------------------------------------------

# Slack 斜杠命令名称约束：小写 a-z、0-9、连字符、
# 下划线。最多 32 个字符。Slack 应用清单每个应用最多接受 50 个斜杠
# 命令。
_SLACK_MAX_SLASH_COMMANDS = 50
_SLACK_NAME_LIMIT = 32
_SLACK_INVALID_CHARS = re.compile(r"[^a-z0-9_\-]")
_SLACK_RESERVED_COMMANDS = frozenset({
    # 应用无法注册的内置 Slack 斜杠命令。
    # https://slack.com/help/articles/201259356-Use-built-in-slash-commands
    "me", "status", "away", "dnd", "shrug", "remind", "msg", "feed",
    "who", "collapse", "expand", "leave", "join", "open", "search",
    "topic", "mute", "pro", "shortcuts",
})
def _sanitize_slack_name(raw: str) -> str:
    """Convert a command name to a valid Slack slash command name.

    Slack allows lowercase a-z, digits, hyphens, and underscores. Max 32
    chars. Uppercase is lowercased; invalid chars are stripped.
    """
    name = raw.lower()
    name = _SLACK_INVALID_CHARS.sub("", name)
    name = name.strip("-_")
    return name[:_SLACK_NAME_LIMIT]


def slack_native_slashes() -> list[tuple[str, str, str]]:
    """Return (slash_name, description, usage_hint) triples for Slack.

    Every gateway-available command in ``COMMAND_REGISTRY`` is surfaced as
    a standalone Slack slash command (e.g. ``/btw``, ``/stop``, ``/model``),
    matching Discord's and Telegram's model where every command is a
    first-class slash and not a ``/hermes <verb>`` subcommand.

    Both canonical names and aliases are included so users can type any
    documented form (e.g. ``/background``, ``/bg``, and ``/btw`` all work).
    Plugin-registered slash commands are included too.

    Commands whose sanitized name collides with a Slack built-in
    (e.g. ``/status``, ``/me``, ``/join``) are silently skipped.  Users
    can still reach them via ``/hermes <command>``.

    Results are clamped to Slack's 50-command limit with duplicate-name
    avoidance. ``/hermes`` is always reserved as the first entry so the
    legacy ``/hermes <subcommand>`` form keeps working for anything that
    gets dropped by the clamp or for free-form questions.
    """
    overrides = _resolve_config_gates()
    entries: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    # Reserve /hermes as the catch-all top-level command.
    entries.append(("hermes", "与 Hermes 对话或运行子命令", "[子命令] [参数]"))
    seen.add("hermes")

    def _add(name: str, desc: str, hint: str) -> None:
        slack_name = _sanitize_slack_name(name)
        if not slack_name or slack_name in seen:
            return
        if slack_name in _SLACK_RESERVED_COMMANDS:
            return
        if len(entries) >= _SLACK_MAX_SLASH_COMMANDS:
            return
        # Slack description cap is 2000 chars; keep it short.
        entries.append((slack_name, desc[:140], hint[:100]))
        seen.add(slack_name)

    # First pass: canonical names (so they win slots if we hit the cap).
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        _add(cmd.name, cmd.description, cmd.args_hint or "")

    # Second pass: aliases.
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        for alias in cmd.aliases:
            # Skip aliases that only differ from canonical by case/punctuation
            # normalization (already covered by _add dedup).
            _add(alias, f"/{cmd.name} 的别名 — {cmd.description}", cmd.args_hint or "")

    # Third pass: plugin commands.
    for name, description, args_hint in _iter_plugin_command_entries():
        _add(name, description, args_hint or "")

    return entries
def slack_app_manifest(request_url: str = "https://hermes-agent.local/slack/commands") -> dict[str, Any]:
    """生成一个包含所有消息网关命令作为斜杠命令的 Slack 应用清单。

    Slack 的清单模式要求每个斜杠命令都必须有 ``request_url``，
    但在我们使用的 Socket 模式下，Slack 会忽略它并通过 WebSocket 路由命令事件。
    一个占位 URL 即可。

    返回的字典仅包含 ``features.slash_commands`` 部分 ——
    调用者将其组合成完整的清单（或合并到现有清单中）。
    保持范围狭窄可以避免我们与清单模式的其他部分（display_information、oauth_config、settings 等）耦合，
    这些部分用户在 Slack UI 中设置一次后很少更改。
    """
    slashes = []
    for name, desc, usage in slack_native_slashes():
        entry = {
            "command": f"/{name}",
            "description": desc or f"运行 /{name}",
            "should_escape": False,
            "url": request_url,
        }
        if usage:
            entry["usage_hint"] = usage
        slashes.append(entry)
    return {"features": {"slash_commands": slashes}}


def slack_subcommand_map() -> dict[str, str]:
    """返回 Slack /hermes 处理器的子命令 -> /命令映射。

    同时映射规范名称和别名，因此 /hermes bg do stuff 与 /hermes background do stuff 效果相同。

    包含插件注册的斜杠命令，以便 ``/hermes <plugin-cmd>`` 通过插件处理器路由。
    """
    overrides = _resolve_config_gates()
    mapping: dict[str, str] = {}
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        mapping[cmd.name] = f"/{cmd.name}"
        for alias in cmd.aliases:
            mapping[alias] = f"/{alias}"
    for name, _description, _args_hint in _iter_plugin_command_entries():
        if name not in mapping:
            mapping[name] = f"/{name}"
    return mapping


# ---------------------------------------------------------------------------
# 自动补全
# ---------------------------------------------------------------------------


# 用于 /model<space> LM Studio 自动补全的进程内缓存。每次按键都探测会阻塞 UI；
# 一个短的 TTL 可以保持其活跃状态，而不会对服务器造成压力。
_LMSTUDIO_COMPLETION_CACHE: tuple[float, list[str]] | None = None


def _lmstudio_completion_models() -> list[str]:
    """用于 /model 自动补全的本地加载的 LM Studio 模型（已缓存，受控）。"""
    global _LMSTUDIO_COMPLETION_CACHE
    # 控制：对于不使用 LM Studio 的用户，不要在每次按键时都探测 127.0.0.1。
    if not (os.environ.get("LM_API_KEY") or os.environ.get("LM_BASE_URL")):
        try:
            from hermes_cli.auth import _load_auth_store
            store = _load_auth_store() or {}
            if "lmstudio" not in (store.get("providers") or {}) \
               and "lmstudio" not in (store.get("credential_pool") or {}):
                return []
        except Exception:
            return []
    now = time.time()
    if _LMSTUDIO_COMPLETION_CACHE and (now - _LMSTUDIO_COMPLETION_CACHE[0]) < 30.0:
        return _LMSTUDIO_COMPLETION_CACHE[1]
    try:
        from hermes_cli.models import fetch_lmstudio_models
        models = fetch_lmstudio_models(
            api_key=os.environ.get("LM_API_KEY", ""),
            base_url=os.environ.get("LM_BASE_URL") or "http://127.0.0.1:1234/v1",
            timeout=0.8,
        )
    except Exception:
        models = []
    _LMSTUDIO_COMPLETION_CACHE = (now, models)
    return models
class SlashCommandCompleter(Completer):
    """内置斜杠命令、子命令和技能命令的自动补全。"""

    def __init__(
        self,
        skill_commands_provider: Callable[[], Mapping[str, dict[str, Any]]] | None = None,
        command_filter: Callable[[str], bool] | None = None,
    ) -> None:
        self._skill_commands_provider = skill_commands_provider
        self._command_filter = command_filter
        # 用于模糊 @ 补全的缓存项目文件列表
        self._file_cache: list[str] = []
        self._file_cache_time: float = 0.0
        self._file_cache_cwd: str = ""

    def _command_allowed(self, slash_command: str) -> bool:
        if self._command_filter is None:
            return True
        try:
            return bool(self._command_filter(slash_command))
        except Exception:
            return True

    def _iter_skill_commands(self) -> Mapping[str, dict[str, Any]]:
        if self._skill_commands_provider is None:
            return {}
        try:
            return self._skill_commands_provider() or {}
        except Exception:
            return {}

    # 无参数运行时打开选择器的命令。
    # 这些命令在补全中不应接收尾随空格，因为：
    # - TUI 的提交处理程序在输入不同时会在 Enter 键上应用补全
    # - 添加空格会使 "/model" → "/model "，从而阻止选择器执行
    _PICKER_COMMANDS = frozenset({"model", "skin", "personality"})

    @staticmethod
    def _completion_text(cmd_name: str, word: str) -> str:
        """返回补全的替换文本。

        当用户已经准确输入了完整命令（``/help``）时，
        返回 ``help`` 将是无操作，并且 prompt_toolkit 会抑制菜单。
        附加尾随空格可以保持下拉菜单可见，并使退格键自然地重新触发它。

        但是，打开选择器的命令（model、skin、personality）不应获得尾随空格 ——
        TUI 会在 Enter 键上应用补全，从而阻止选择器打开。
        """
        if cmd_name != word:
            return cmd_name
        # 不要为选择器命令添加空格 —— 允许 Enter 键执行它们
        if cmd_name in SlashCommandCompleter._PICKER_COMMANDS:
            return cmd_name
        return f"{cmd_name} "

    @staticmethod
    def _extract_path_word(text: str) -> str | None:
        """如果当前单词看起来像文件路径，则提取它。

        返回光标下的类似路径的标记，如果当前单词看起来不像路径，则返回 None。
        当单词以 ``./``、``../``、``~/``、``/`` 开头，或包含 ``/`` 分隔符（例如 ``src/main.py``）时，它就像路径。
        """
        if not text:
            return None
        # 向后遍历以查找当前“单词”的开头。
        # 单词由空格分隔，但路径可以包含几乎所有内容。
        i = len(text) - 1
        while i >= 0 and text[i] != " ":
            i -= 1
        word = text[i + 1:]
        if not word:
            return None
        # 仅对类似路径的标记触发路径补全
        if word.startswith(("./", "../", "~/", "/")) or "/" in word:
            return word
        return None

    @staticmethod
    def _path_completions(word: str, limit: int = 30):
        """为匹配 *word* 的文件路径生成 Completion 对象。"""
        expanded = os.path.expanduser(word)
        # 拆分为目录部分和前缀以在其中匹配
        if expanded.endswith("/"):
            search_dir = expanded
            prefix = ""
        else:
            search_dir = os.path.dirname(expanded) or "."
            prefix = os.path.basename(expanded)

        try:
            entries = os.listdir(search_dir)
        except OSError:
            return

        count = 0
        prefix_lower = prefix.lower()
        for entry in sorted(entries):
            if prefix and not entry.lower().startswith(prefix_lower):
                continue
            if count >= limit:
                break

            full_path = os.path.join(search_dir, entry)
            is_dir = os.path.isdir(full_path)

            # 构建补全文本（替换已输入单词的内容）
            if word.startswith("~"):
                display_path = "~/" + os.path.relpath(full_path, os.path.expanduser("~"))
            elif os.path.isabs(word):
                display_path = full_path
            else:
                # 保持相对路径
                display_path = os.path.relpath(full_path)

            if is_dir:
                display_path += "/"

            suffix = "/" if is_dir else ""
            meta = "目录" if is_dir else _file_size_label(full_path)

            yield Completion(
                display_path,
                start_position=-len(word),
                display=entry + suffix,
                display_meta=meta,
            )
            count += 1

    @staticmethod
    def _extract_context_word(text: str) -> str | None:
        """提取裸 ``@`` 标记以进行上下文引用补全。"""
        if not text:
            return None
        # 向后遍历以查找当前单词的开头
        i = len(text) - 1
        while i >= 0 and text[i] != " ":
            i -= 1
        word = text[i + 1:]
        if not word.startswith("@"):
            return None
        return word

    def _context_completions(self, word: str, limit: int = 30):
        """生成 Claude Code 风格的 @ 上下文补全。

        裸 ``@`` 或 ``@partial`` 显示静态引用和匹配的文件/文件夹。
        ``@file:path`` 和 ``@folder:path`` 由现有的路径补全路径处理。
        """
        lowered = word.lower()

        # 静态上下文引用
        _STATIC_REFS = (
            ("@diff", "Git 工作树差异"),
            ("@staged", "Git 暂存区差异"),
            ("@file:", "附加文件"),
            ("@folder:", "附加文件夹"),
            ("@git:", "带差异的 Git 日志（例如 @git:5）"),
            ("@url:", "获取网页内容"),
        )
        for candidate, meta in _STATIC_REFS:
            if candidate.lower().startswith(lowered) and candidate.lower() != lowered:
                yield Completion(
                    candidate,
                    start_position=-len(word),
                    display=candidate,
                    display_meta=meta,
                )

        # 如果用户输入了 @file: / @folder:（或只是 @file / @folder 且尚未输入冒号），则委托给路径补全。
        # 接受裸形式可以让选择器在用户输入 `@folder` 后立即显示目录，而无需他们先接受静态的 `@folder:` 提示并重新触发补全。
        for prefix in ("@file:", "@folder:"):
            bare = prefix[:-1]

            if word == bare or word.startswith(prefix):
                want_dir = prefix == "@folder:"
                path_part = '' if word == bare else word[len(prefix):]
                expanded = os.path.expanduser(path_part)

                if not expanded or expanded == ".":
                    search_dir, match_prefix = ".", ""
                elif expanded.endswith("/"):
                    search_dir, match_prefix = expanded, ""
                else:
                    search_dir = os.path.dirname(expanded) or "."
                    match_prefix = os.path.basename(expanded)

                try:
                    entries = os.listdir(search_dir)
                except OSError:
                    return

                count = 0
                prefix_lower = match_prefix.lower()
                for entry in sorted(entries):
                    if match_prefix and not entry.lower().startswith(prefix_lower):
                        continue
                    full_path = os.path.join(search_dir, entry)
                    is_dir = os.path.isdir(full_path)
                    # `@folder:` 必须仅显示目录；`@file:` 仅显示常规文件。
                    # 没有此过滤器，`@folder:` 会列出当前工作目录中的每个 .env / .gitignore，违背了明确的前缀，并让期望目录选择器的用户感到困惑。
                    if want_dir != is_dir:
                        continue
                    if count >= limit:
                        break
                    display_path = os.path.relpath(full_path)
                    suffix = "/" if is_dir else ""
                    meta = "目录" if is_dir else _file_size_label(full_path)
                    completion = f"{prefix}{display_path}{suffix}"
                    yield Completion(
                        completion,
                        start_position=-len(word),
                        display=entry + suffix,
                        display_meta=meta,
                    )
                    count += 1
                return

        # 裸 @ 或 @partial —— 模糊项目范围文件搜索
        query = word[1:]  # 去除 @
        yield from self._fuzzy_file_completions(word, query, limit)

    def _get_project_files(self) -> list[str]:
        """返回缓存的项目文件列表（每 5 秒刷新一次）。"""
        cwd = os.getcwd()
        now = time.monotonic()
        if (
            self._file_cache
            and self._file_cache_cwd == cwd
            and now - self._file_cache_time < 5.0
        ):
            return self._file_cache

        files: list[str] = []
        # 先尝试 rg（快速，尊重 .gitignore），然后 fd，最后 find。
        for cmd in [
            ["rg", "--files", "--sortr=modified", cwd],
            ["rg", "--files", cwd],
            ["fd", "--type", "f", "--base-directory", cwd],
        ]:
            tool = cmd[0]
            if not shutil.which(tool):
                continue
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=2,
                    cwd=cwd,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    raw = proc.stdout.strip().split("\n")
                    # 存储相对路径
                    for p in raw[:5000]:
                        rel = os.path.relpath(p, cwd) if os.path.isabs(p) else p
                        files.append(rel)
                    break
            except (subprocess.TimeoutExpired, OSError):
                continue

        self._file_cache = files
        self._file_cache_time = now
        self._file_cache_cwd = cwd
        return files

    @staticmethod
    def _score_path(filepath: str, query: str) -> int:
        """根据模糊查询对文件路径进行评分。分数越高 = 匹配越好。"""
        if not query:
            return 1  # 查询为空时显示所有内容

        filename = os.path.basename(filepath)
        lower_file = filename.lower()
        lower_path = filepath.lower()
        lower_q = query.lower()

        # 精确文件名匹配
        if lower_file == lower_q:
            return 100
        # 文件名以查询开头
        if lower_file.startswith(lower_q):
            return 80
        # 文件名包含查询作为子字符串
        if lower_q in lower_file:
            return 60
        # 完整路径包含查询
        if lower_q in lower_path:
            return 40
        # 首字母/缩写匹配：例如 "fo" 匹配 "file_operations"
        # 检查查询字符是否按顺序出现在文件名中
        qi = 0
        for c in lower_file:
            if qi < len(lower_q) and c == lower_q[qi]:
                qi += 1
        if qi == len(lower_q):
            # 如果匹配落在单词边界（_、-、/、. 之后）则加分
            boundary_hits = 0
            qi = 0
            prev = "_"  # 将开头视为边界
            for c in lower_file:
                if qi < len(lower_q) and c == lower_q[qi]:
                    if prev in "_-./":
                        boundary_hits += 1
                    qi += 1
                prev = c
            if boundary_hits >= len(lower_q) * 0.5:
                return 35
            return 25
        return 0

    def _fuzzy_file_completions(self, word: str, query: str, limit: int = 20):
        """为裸 @query 生成模糊文件补全。"""
        files = self._get_project_files()

        if not query:
            # 无查询 —— 显示最近修改的文件（已按修改时间排序）
            for fp in files[:limit]:
                is_dir = fp.endswith("/")
                filename = os.path.basename(fp)
                kind = "文件夹" if is_dir else "文件"
                meta = "目录" if is_dir else _file_size_label(
                    os.path.join(os.getcwd(), fp)
                )
                yield Completion(
                    f"@{kind}:{fp}",
                    start_position=-len(word),
                    display=filename,
                    display_meta=meta,
                )
            return

        # 评分和排序
        scored = []
        for fp in files:
            s = self._score_path(fp, query)
            if s > 0:
                scored.append((s, fp))
        scored.sort(key=lambda x: (-x[0], x[1]))

        for _, fp in scored[:limit]:
            is_dir = fp.endswith("/")
            filename = os.path.basename(fp)
            kind = "文件夹" if is_dir else "文件"
            meta = "目录" if is_dir else _file_size_label(
                os.path.join(os.getcwd(), fp)
            )
            yield Completion(
                f"@{kind}:{fp}",
                start_position=-len(word),
                display=filename,
                display_meta=f"{fp}  {meta}" if meta else fp,
            )

    @staticmethod
    def _skin_completions(sub_text: str, sub_lower: str):
        """从可用皮肤中为 /skin 生成补全。"""
        try:
            from hermes_cli.skin_engine import list_skins
            for s in list_skins():
                name = s["name"]
                if name.startswith(sub_lower) and name != sub_lower:
                    yield Completion(
                        name,
                        start_position=-len(sub_text),
                        display=name,
                        display_meta=s.get("description", "") or s.get("source", ""),
                    )
        except Exception:
            pass

    @staticmethod
    def _personality_completions(sub_text: str, sub_lower: str):
        """从配置的人格中为 /personality 生成补全。"""
        try:
            from hermes_cli.config import load_config
            personalities = load_config().get("agent", {}).get("personalities", {})
            if "none".startswith(sub_lower) and "none" != sub_lower:
                yield Completion(
                    "none",
                    start_position=-len(sub_text),
                    display="none",
                    display_meta="清除人格覆盖",
                )
            for name, prompt in personalities.items():
                if name.startswith(sub_lower) and name != sub_lower:
                    if isinstance(prompt, dict):
                        meta = prompt.get("description") or prompt.get("system_prompt", "")[:50]
                    else:
                        meta = str(prompt)[:50]
                    yield Completion(
                        name,
                        start_position=-len(sub_text),
                        display=name,
                        display_meta=meta,
                    )
        except Exception:
            pass

    def _model_completions(self, sub_text: str, sub_lower: str):
        """从配置别名 + 内置别名中为 /model 生成补全。"""
        seen = set()
        # 基于配置的直接别名（首选 —— 包含提供商信息）
        try:
            from hermes_cli.model_switch import (
                _ensure_direct_aliases, DIRECT_ALIASES, MODEL_ALIASES,
            )
            _ensure_direct_aliases()
            for name, da in DIRECT_ALIASES.items():
                if name.startswith(sub_lower) and name != sub_lower:
                    seen.add(name)
                    yield Completion(
                        name,
                        start_position=-len(sub_text),
                        display=name,
                        display_meta=f"{da.model} ({da.provider})",
                    )
            # 尚未覆盖的内置目录别名
            for name in sorted(MODEL_ALIASES.keys()):
                if name in seen:
                    continue
                if name.startswith(sub_lower) and name != sub_lower:
                    identity = MODEL_ALIASES[name]
                    yield Completion(
                        name,
                        start_position=-len(sub_text),
                        display=name,
                        display_meta=f"{identity.vendor}/{identity.family}",
                    )
        except Exception:
            pass
        # LM Studio：显示本地加载的模型。根据用户实际配置了 LM Studio（环境变量或身份验证存储条目）进行门控，这样我们就不会为不使用它的用户在每次按键时探测 127.0.0.1。
        for name in _lmstudio_completion_models():
            if name in seen:
                continue
            if name.startswith(sub_lower) and name != sub_lower:
                yield Completion(
                    name,
                    start_position=-len(sub_text),
                    display=name,
                    display_meta="LM Studio",
                )

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            # 尝试 @ 上下文补全（Claude Code 风格）
            ctx_word = self._extract_context_word(text)
            if ctx_word is not None:
                yield from self._context_completions(ctx_word)
                return
            # 尝试为非斜杠输入进行文件路径补全
            path_word = self._extract_path_word(text)
            if path_word is not None:
                yield from self._path_completions(path_word)
            return

        # 检查我们是否正在补全子命令（基本命令已输入）
        parts = text.split(maxsplit=1)
        base_cmd = parts[0].lower()
        if len(parts) > 1 or (len(parts) == 1 and text.endswith(" ")):
            sub_text = parts[1] if len(parts) > 1 else ""
            sub_lower = sub_text.lower()

            # 具有运行时列表的命令的动态补全
            if " " not in sub_text:
                if base_cmd == "/model":
                    yield from self._model_completions(sub_text, sub_lower)
                    return
                if base_cmd == "/skin":
                    yield from self._skin_completions(sub_text, sub_lower)
                    return
                if base_cmd == "/personality":
                    yield from self._personality_completions(sub_text, sub_lower)
                    return

            # 静态子命令补全
            if " " not in sub_text and base_cmd in SUBCOMMANDS and self._command_allowed(base_cmd):
                for sub in SUBCOMMANDS[base_cmd]:
                    if sub.startswith(sub_lower) and sub != sub_lower:
                        yield Completion(
                            sub,
                            start_position=-len(sub_text),
                            display=sub,
                        )
            return

        word = text[1:]

        for cmd, desc in COMMANDS.items():
            if not self._command_allowed(cmd):
                continue
            cmd_name = cmd[1:]
            if cmd_name.startswith(word):
                yield Completion(
                    self._completion_text(cmd_name, word),
                    start_position=-len(word),
                    display=cmd,
                    display_meta=desc,
                )

        for cmd, info in self._iter_skill_commands().items():
            cmd_name = cmd[1:]
            if cmd_name.startswith(word):
                description = str(info.get("description", "技能命令"))
                short_desc = description[:50] + ("..." if len(description) > 50 else "")
                yield Completion(
                    self._completion_text(cmd_name, word),
                    start_position=-len(word),
                    display=cmd,
                    display_meta=f"⚡ {short_desc}",
                )

        # 插件注册的斜杠命令
        try:
            from hermes_cli.plugins import get_plugin_commands
            for cmd_name, cmd_info in get_plugin_commands().items():
                if cmd_name.startswith(word):
                    desc = str(cmd_info.get("description", "插件命令"))
                    short_desc = desc[:50] + ("..." if len(desc) > 50 else "")
                    yield Completion(
                        self._completion_text(cmd_name, word),
                        start_position=-len(word),
                        display=f"/{cmd_name}",
                        display_meta=f"🔌 {short_desc}",
                    )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 斜杠命令的内联自动建议（幽灵文本）
# ---------------------------------------------------------------------------
class SlashCommandAutoSuggest(AutoSuggest):
    """Inline ghost-text suggestions for slash commands and their subcommands.

    Shows the rest of a command or subcommand in dim text as you type.
    Falls back to history-based suggestions for non-slash input.
    """

    def __init__(
        self,
        history_suggest: AutoSuggest | None = None,
        completer: SlashCommandCompleter | None = None,
    ) -> None:
        self._history = history_suggest
        self._completer = completer  # Reuse its model cache

    def get_suggestion(self, buffer, document):
        text = document.text_before_cursor

        # Only suggest for slash commands
        if not text.startswith("/"):
            # Fall back to history for regular text
            if self._history:
                return self._history.get_suggestion(buffer, document)
            return None

        parts = text.split(maxsplit=1)
        base_cmd = parts[0].lower()

        if len(parts) == 1 and not text.endswith(" "):
            # Still typing the command name: /upd → suggest "ate"
            word = text[1:].lower()
            for cmd in COMMANDS:
                if self._completer is not None and not self._completer._command_allowed(cmd):
                    continue
                cmd_name = cmd[1:]  # strip leading /
                if cmd_name.startswith(word) and cmd_name != word:
                    return Suggestion(cmd_name[len(word):])
            return None

        # Command is complete — suggest subcommands or model names
        sub_text = parts[1] if len(parts) > 1 else ""
        sub_lower = sub_text.lower()

        # Static subcommands
        if self._completer is not None and not self._completer._command_allowed(base_cmd):
            return None
        if base_cmd in SUBCOMMANDS and SUBCOMMANDS[base_cmd]:
            if " " not in sub_text:
                for sub in SUBCOMMANDS[base_cmd]:
                    if sub.startswith(sub_lower) and sub != sub_lower:
                        return Suggestion(sub[len(sub_text):])

        # Fall back to history
        if self._history:
            return self._history.get_suggestion(buffer, document)
        return None


def _file_size_label(path: str) -> str:
    """Return a compact human-readable file size, or '' on error."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return ""
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size / 1024:.0f}K"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}M"
    return f"{size / (1024 * 1024 * 1024):.1f}G"