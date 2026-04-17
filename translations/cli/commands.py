"""Hermes CLI 的斜杠命令定义和自动补全。

所有斜杠命令的中央注册表。每个使用者——CLI 帮助、消息网关分发、Telegram BotCommands、Slack 子命令映射、自动补全——都从 ``COMMAND_REGISTRY`` 派生其数据。

添加命令：在 ``COMMAND_REGISTRY`` 中添加一个 ``CommandDef`` 条目。
添加别名：在现有的 ``CommandDef`` 上设置 ``aliases=("short",)``。
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

# prompt_toolkit 是一个可选的 CLI 依赖项——仅用于
# SlashCommandCompleter 和 SlashCommandAutoSuggest。缺少它的网关和测试
# 环境仍然必须能够导入此模块
# 以用于 resolve_command、gateway_help_lines 和 COMMAND_REGISTRY。
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
    category: str                      # "会话"、"配置"等
    aliases: tuple[str, ...] = ()      # 替代名称：("bg",)
    args_hint: str = ""                # 参数占位符："<prompt>"、"[name]"
    subcommands: tuple[str, ...] = ()  # 可标签补全的子命令
    cli_only: bool = False             # 仅在 CLI 中可用
    gateway_only: bool = False         # 仅在网关/消息传递中可用
    gateway_config_gate: str | None = None  # 配置点路径；当为真值时，覆盖网关的 cli_only


# ---------------------------------------------------------------------------
# 中央注册表——单一事实来源
# ---------------------------------------------------------------------------

COMMAND_REGISTRY: list[CommandDef] = [
    # 会话
    CommandDef("new", "启动新会话（全新会话 ID + 历史记录）", "会话",
               aliases=("reset",)),
    CommandDef("clear", "清屏并启动新会话", "会话",
               cli_only=True),
    CommandDef("history", "显示对话历史记录", "会话",
               cli_only=True),
    CommandDef("save", "保存当前对话", "会话",
               cli_only=True),
    CommandDef("retry", "重试上一条消息（重新发送给 Agent）", "会话"),
    CommandDef("undo", "移除最后一条用户/助手交换", "会话"),
    CommandDef("title", "为当前会话设置标题", "会话",
               args_hint="[name]"),
    CommandDef("branch", "分支当前会话（探索不同路径）", "会话",
               aliases=("fork",), args_hint="[name]"),
    CommandDef("compress", "手动压缩对话上下文", "会话",
               args_hint="[focus topic]"),
    CommandDef("rollback", "列出或恢复文件系统检查点", "会话",
               args_hint="[number]"),
    CommandDef("snapshot", "创建或恢复 Hermes 配置/状态的状态快照", "会话",
               aliases=("snap",), args_hint="[create|restore <id>|prune]"),
    CommandDef("stop", "终止所有正在运行的后台进程", "会话"),
    CommandDef("approve", "批准一个待处理的危险命令", "会话",
               gateway_only=True, args_hint="[session|always]"),
    CommandDef("deny", "拒绝一个待处理的危险命令", "会话",
               gateway_only=True),
    CommandDef("background", "在后台运行一个提示", "会话",
               aliases=("bg",), args_hint="<prompt>"),
    CommandDef("btw", "使用会话上下文的临时旁侧问题（无工具，不持久化）", "会话",
               args_hint="<question>"),
    CommandDef("queue", "为下一轮排队一个提示（不中断）", "会话",
               aliases=("q",), args_hint="<prompt>"),
    CommandDef("status", "显示会话信息", "会话"),
    CommandDef("profile", "显示活动配置文件名称和主目录", "信息"),
    CommandDef("sethome", "将此聊天设置为主频道", "会话",
               gateway_only=True, aliases=("set-home",)),
    CommandDef("resume", "恢复先前命名的会话", "会话",
               args_hint="[name]"),

    # 配置
    CommandDef("config", "显示当前配置", "配置",
               cli_only=True),
    CommandDef("model", "为此会话切换模型", "配置", args_hint="[model] [--global]"),
    CommandDef("provider", "显示可用提供商和当前提供商",
               "配置"),
    CommandDef("gquota", "显示 Google Gemini Code Assist 配额使用情况", "信息"),

    CommandDef("personality", "设置预定义人格", "配置",
               args_hint="[name]"),
    CommandDef("statusbar", "切换上下文/模型状态栏", "配置",
               cli_only=True, aliases=("sb",)),
    CommandDef("verbose", "循环工具进度显示：关闭 -> 新 -> 全部 -> 详细",
               "配置", cli_only=True,
               gateway_config_gate="display.tool_progress_command"),
    CommandDef("yolo", "切换 YOLO 模式（跳过所有危险命令批准）",
               "配置"),
    CommandDef("reasoning", "管理推理努力和显示", "配置",
               args_hint="[level|show|hide]",
               subcommands=("none", "minimal", "low", "medium", "high", "xhigh", "show", "hide", "on", "off")),
    CommandDef("fast", "切换快速模式——OpenAI 优先处理 / Anthropic 快速模式（普通/快速）", "配置",
               args_hint="[normal|fast|status]",
               subcommands=("normal", "fast", "status", "on", "off")),
    CommandDef("skin", "显示或更改显示皮肤/主题", "配置",
               cli_only=True, args_hint="[name]"),
    CommandDef("voice", "切换语音模式", "配置",
               args_hint="[on|off|tts|status]", subcommands=("on", "off", "tts", "status")),

    # 工具 & 技能
    CommandDef("tools", "管理工具：/tools [list|disable|enable] [name...]", "工具 & 技能",
               args_hint="[list|disable|enable] [name...]", cli_only=True),
    CommandDef("toolsets", "列出可用工具集", "工具 & 技能",
               cli_only=True),
    CommandDef("skills", "搜索、安装、检查或管理技能",
               "工具 & 技能", cli_only=True,
               subcommands=("search", "browse", "inspect", "install")),
    CommandDef("cron", "管理定时任务", "工具 & 技能",
               cli_only=True, args_hint="[subcommand]",
               subcommands=("list", "add", "create", "edit", "pause", "resume", "run", "remove")),
    CommandDef("reload", "将 .env 变量重新加载到运行中的会话", "工具 & 技能"),
    CommandDef("reload-mcp", "从配置重新加载 MCP 服务器", "工具 & 技能",
               aliases=("reload_mcp",)),
    CommandDef("browser", "通过 CDP 将浏览器工具连接到您的实时 Chrome", "工具 & 技能",
               cli_only=True, args_hint="[connect|disconnect|status]",
               subcommands=("connect", "disconnect", "status")),
    CommandDef("plugins", "列出已安装的插件及其状态",
               "工具 & 技能", cli_only=True),

    # 信息
    CommandDef("commands", "浏览所有命令和技能（分页）", "信息",
               gateway_only=True, args_hint="[page]"),
    CommandDef("help", "显示可用命令", "信息"),
    CommandDef("restart", "在排空活动运行后优雅地重启网关", "会话",
               gateway_only=True),
    CommandDef("usage", "显示当前会话的 Token 使用情况和速率限制", "信息"),
    CommandDef("insights", "显示使用洞察和分析", "信息",
               args_hint="[days]"),
    CommandDef("platforms", "显示网关/消息传递平台状态", "信息",
               cli_only=True, aliases=("gateway",)),
    CommandDef("paste", "检查剪贴板中是否有图像并附加它", "信息",
               cli_only=True),
    CommandDef("image", "为您的下一个提示附加本地图像文件", "信息",
               cli_only=True, args_hint="<path>"),
    CommandDef("update", "将 Hermes Agent 更新到最新版本", "信息",
               gateway_only=True),
    CommandDef("debug", "上传调试报告（系统信息 + 日志）并获取可分享链接", "信息"),

    # 退出
    CommandDef("quit", "退出 CLI", "退出",
               cli_only=True, aliases=("exit",)),
]


# ---------------------------------------------------------------------------
# 派生查找表——在导入时构建一次，通过 rebuild_lookups() 刷新
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
            COMMANDS[f"/{_alias}"] = f"{_cmd.description} (/别名 {_cmd.name})"

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
        if val:
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


def telegram_bot_commands() -> list[tuple[str, str]]:
    """Return (command_name, description) pairs for Telegram setMyCommands.

    Telegram command names cannot contain hyphens, so they are replaced with
    underscores.  Aliases are skipped -- Telegram shows one menu entry per
    canonical command.
    """
    overrides = _resolve_config_gates()
    result: list[tuple[str, str]] = []
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        tg_name = _sanitize_telegram_name(cmd.name)
        if tg_name:
            result.append((tg_name, cmd.description))
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
    entries: list[tuple[str, str]],
    reserved: set[str],
) -> list[tuple[str, str]]:
    """Enforce 32-char command name limit with collision avoidance.

    Both Telegram and Discord cap slash command names at 32 characters.
    Names exceeding the limit are truncated.  If truncation creates a duplicate
    (against *reserved* names or earlier entries in the same batch), the name is
    shortened to 31 chars and a digit ``0``-``9`` is appended to differentiate.
    If all 10 digit slots are taken the entry is silently dropped.
    """
    used: set[str] = set(reserved)
    result: list[tuple[str, str]] = []
    for name, desc in entries:
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
        result.append((name, desc))
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
        from hermes_cli.plugins import get_plugin_manager
        pm = get_plugin_manager()
        plugin_cmds = getattr(pm, "_plugin_commands", {})
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
        _skills_dir = str(SKILLS_DIR.resolve())
        _hub_dir = str((SKILLS_DIR / ".hub").resolve())
        skill_cmds = get_skill_commands()
        for cmd_key in sorted(skill_cmds):
            info = skill_cmds[cmd_key]
            skill_path = info.get("skill_md_path", "")
            if not skill_path.startswith(_skills_dir):
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

    # Clamp names; _clamp_command_names works on (name, desc) pairs so we
    # need to zip/unzip.
    skill_pairs = [(n, d) for n, d, _ in skill_triples]
    key_by_pair = {(n, d): k for n, d, k in skill_triples}
    skill_pairs = _clamp_command_names(skill_pairs, reserved_names)

    # Skills fill remaining slots — only tier that gets trimmed
    remaining = max(0, max_slots - len(all_entries))
    hidden_count = max(0, len(skill_pairs) - remaining)
    for n, d in skill_pairs[:remaining]:
        all_entries.append((n, d, key_by_pair.get((n, d), "")))

    return all_entries[:max_slots], hidden_count


# ---------------------------------------------------------------------------
# Platform-specific wrappers
# ---------------------------------------------------------------------------
def telegram_menu_commands(max_commands: int = 100) -> tuple[list[tuple[str, str]], int]:
    """返回受 Bot API 限制的 Telegram 菜单命令。

    优先级顺序（优先级越高 = 溢出时永不被移除）：
      1. 核心 CommandDef 命令（始终包含）
      2. 插件斜杠命令（优先于技能）
      3. 内置技能命令（填充剩余槽位，按字母顺序）

    技能是唯一在达到上限时会被修剪的层级。
    用户安装的 Hub 技能被排除在外——可通过 /skills 访问。
    为 ``"telegram"`` 平台禁用的技能（通过 ``hermes skills
    config``）会完全从菜单中排除。

    返回：
        (menu_commands, hidden_count)，其中 hidden_count 是
        因上限而被省略的技能命令数量。
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
    （插件 > 技能，排除 Hub，排除按平台禁用的技能），但
    适配了 Discord 的限制：

    - 名称中允许连字符（无需 ``-`` → ``_`` 清理）
    - 描述限制在 100 个字符内（Discord 的每字段上限）

    参数：
        max_slots: 可用命令槽位（100 减去现有内置命令数量）。
        reserved_names: 已注册的内置命令名称。

    返回：
        ``(entries, hidden_count)``，其中 *entries* 是
        ``(discord_name, description, cmd_key)`` 三元组的列表。``cmd_key`` 是
        斜杠处理回调所需的原始 ``/skill-name`` 键。
    """
    return _collect_gateway_skill_entries(
        platform="discord",
        max_slots=max_slots,
        reserved_names=set(reserved_names),  # 复制 —— 不修改调用者的集合
        desc_limit=100,
    )


def discord_skill_commands_by_category(
    reserved_names: set[str],
) -> tuple[dict[str, list[tuple[str, str, str]]], list[tuple[str, str, str]], int]:
    """返回按类别组织的技能条目，用于 Discord ``/skill`` 子命令组。

    目录在 ``SKILLS_DIR`` 下至少嵌套 2 层的技能
    （例如 ``creative/ascii-art/SKILL.md``）按其顶级
    类别分组。根层级的技能（例如 ``dogfood/SKILL.md``）作为
    *未分类* 返回 —— 调用者应将它们注册为 ``/skill`` 组的直接子命令。

    应用与 :func:`discord_skill_commands` 相同的过滤：排除 Hub
    技能，排除按平台禁用的技能，名称被截断。

    返回：
        ``(categories, uncategorized, hidden_count)``

        - *categories*: ``{category_name: [(name, description, cmd_key), ...]}``
        - *uncategorized*: ``[(name, description, cmd_key), ...]``
        - *hidden_count*: 因 Discord 组限制而被丢弃的技能数量
          （25 个子命令组，每组 25 个子命令）
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
    _names_used: set[str] = set(reserved_names)
    hidden = 0

    try:
        from agent.skill_commands import get_skill_commands
        from tools.skills_tool import SKILLS_DIR
        _skills_dir = SKILLS_DIR.resolve()
        _hub_dir = (SKILLS_DIR / ".hub").resolve()
        skill_cmds = get_skill_commands()

        for cmd_key in sorted(skill_cmds):
            info = skill_cmds[cmd_key]
            skill_path = info.get("skill_md_path", "")
            if not skill_path:
                continue
            sp = _P(skill_path).resolve()
            # 跳过不在 SKILLS_DIR 内或来自 Hub 的技能
            if not str(sp).startswith(str(_skills_dir)):
                continue
            if str(sp).startswith(str(_hub_dir)):
                continue

            skill_name = info.get("name", "")
            if skill_name in _platform_disabled:
                continue

            raw_name = cmd_key.lstrip("/")
            # 截断至 32 个字符（Discord 限制）
            discord_name = raw_name[:32]
            if discord_name in _names_used:
                continue
            _names_used.add(discord_name)

            desc = info.get("description", "")
            if len(desc) > 100:
                desc = desc[:97] + "..."

            # 根据 SKILLS_DIR 内的相对路径确定类别。
            # 例如 creative/ascii-art/SKILL.md → parts = ("creative", "ascii-art")
            try:
                rel = sp.parent.relative_to(_skills_dir)
            except ValueError:
                continue
            parts = rel.parts
            if len(parts) >= 2:
                cat = parts[0]
                categories.setdefault(cat, []).append((discord_name, desc, cmd_key))
            else:
                uncategorized.append((discord_name, desc, cmd_key))
    except Exception:
        pass

    # 强制执行 Discord 限制：25 个子命令组，每组 25 个子命令 ------
    _MAX_GROUPS = 25
    _MAX_PER_GROUP = 25

    trimmed_categories: dict[str, list[tuple[str, str, str]]] = {}
    group_count = 0
    for cat in sorted(categories):
        if group_count >= _MAX_GROUPS:
            hidden += len(categories[cat])
            continue
        entries = categories[cat][:_MAX_PER_GROUP]
        hidden += max(0, len(categories[cat]) - _MAX_PER_GROUP)
        trimmed_categories[cat] = entries
        group_count += 1

    # 未分类的技能也计入 25 个顶级限制
    remaining_slots = _MAX_GROUPS - group_count
    if len(uncategorized) > remaining_slots:
        hidden += len(uncategorized) - remaining_slots
        uncategorized = uncategorized[:remaining_slots]

    return trimmed_categories, uncategorized, hidden
def slack_subcommand_map() -> dict[str, str]:
    """Return subcommand -> /command mapping for Slack /hermes handler.

    Maps both canonical names and aliases so /hermes bg do stuff works
    the same as /hermes background do stuff.
    """
    overrides = _resolve_config_gates()
    mapping: dict[str, str] = {}
    for cmd in COMMAND_REGISTRY:
        if not _is_gateway_available(cmd, overrides):
            continue
        mapping[cmd.name] = f"/{cmd.name}"
        for alias in cmd.aliases:
            mapping[alias] = f"/{alias}"
    return mapping


# ---------------------------------------------------------------------------
# 自动补全
# ---------------------------------------------------------------------------

class SlashCommandCompleter(Completer):
    """为内置斜杠命令、子命令和技能命令提供自动补全。"""

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

    @staticmethod
    def _completion_text(cmd_name: str, word: str) -> str:
        """返回补全项的替换文本。

        当用户已经完整输入了命令（例如 ``/help``）时，返回 ``help`` 将是一个无操作，并且 prompt_toolkit 会隐藏菜单。
        在末尾添加一个空格可以保持下拉菜单可见，并使退格键能自然地重新触发它。
        """
        return f"{cmd_name} " if cmd_name == word else cmd_name

    @staticmethod
    def _extract_path_word(text: str) -> str | None:
        """如果当前单词看起来像文件路径，则提取它。

        返回光标下的类路径标记，如果当前单词看起来不像路径则返回 None。
        一个单词在以下情况下被认为是类路径的：以 ``./``、``../``、``~/``、``/`` 开头，或者包含 ``/`` 分隔符（例如 ``src/main.py``）。
        """
        if not text:
            return None
        # 向后遍历以找到当前“单词”的起始位置。
        # 单词由空格分隔，但路径可以包含几乎所有字符。
        i = len(text) - 1
        while i >= 0 and text[i] != " ":
            i -= 1
        word = text[i + 1:]
        if not word:
            return None
        # 仅对类路径标记触发路径补全
        if word.startswith(("./", "../", "~/", "/")) or "/" in word:
            return word
        return None

    @staticmethod
    def _path_completions(word: str, limit: int = 30):
        """为匹配 *word* 的文件路径生成 Completion 对象。"""
        expanded = os.path.expanduser(word)
        # 分割为目录部分和前缀，以便在其中匹配
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
        """提取一个裸的 ``@`` 标记用于上下文引用补全。"""
        if not text:
            return None
        # 向后遍历以找到当前单词的起始位置
        i = len(text) - 1
        while i >= 0 and text[i] != " ":
            i -= 1
        word = text[i + 1:]
        if not word.startswith("@"):
            return None
        return word

    def _context_completions(self, word: str, limit: int = 30):
        """生成 Claude Code 风格的 @ 上下文补全。

        裸的 ``@`` 或 ``@partial`` 显示静态引用和匹配的文件/文件夹。
        ``@file:path`` 和 ``@folder:path`` 由现有的路径补全路径处理。
        """
        lowered = word.lower()

        # 静态上下文引用
        _STATIC_REFS = (
            ("@diff", "Git 工作区差异"),
            ("@staged", "Git 暂存区差异"),
            ("@file:", "附加文件"),
            ("@folder:", "附加文件夹"),
            ("@git:", "Git 日志及差异（例如 @git:5）"),
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

        # 如果用户输入了 @file: 或 @folder:，委托给路径补全
        for prefix in ("@file:", "@folder:"):
            if word.startswith(prefix):
                path_part = word[len(prefix):] or "."
                expanded = os.path.expanduser(path_part)
                if expanded.endswith("/"):
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
                    if count >= limit:
                        break
                    full_path = os.path.join(search_dir, entry)
                    is_dir = os.path.isdir(full_path)
                    display_path = os.path.relpath(full_path)
                    suffix = "/" if is_dir else ""
                    kind = "folder" if is_dir else "file"
                    meta = "目录" if is_dir else _file_size_label(full_path)
                    completion = f"@{kind}:{display_path}{suffix}"
                    yield Completion(
                        completion,
                        start_position=-len(word),
                        display=entry + suffix,
                        display_meta=meta,
                    )
                    count += 1
                return

        # 裸 @ 或 @partial — 模糊项目范围文件搜索
        query = word[1:]  # 去掉 @
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
            # 无查询 — 显示最近修改的文件（已按修改时间排序）
            for fp in files[:limit]:
                is_dir = fp.endswith("/")
                filename = os.path.basename(fp)
                kind = "folder" if is_dir else "file"
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
            kind = "folder" if is_dir else "file"
            meta = "目录" if is_dir else _file_size_label(
                os.path.join(os.getcwd(), fp)
            )
            yield Completion(
                f"@{kind}:{fp}",
                start_position=-len(word),
                display=filename,
                display_meta=f"{fp}  {meta}" if meta else fp,
            )

    def _model_completions(self, sub_text: str, sub_lower: str):
        """为 /model 从配置别名 + 内置别名生成补全。"""
        seen = set()
        # 基于配置的直接别名（首选 — 包含提供商信息）
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
            # 内置目录别名，尚未覆盖的
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

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            # 尝试 @ 上下文补全（Claude Code 风格）
            ctx_word = self._extract_context_word(text)
            if ctx_word is not None:
                yield from self._context_completions(ctx_word)
                return
            # 为非斜杠输入尝试文件路径补全
            path_word = self._extract_path_word(text)
            if path_word is not None:
                yield from self._path_completions(path_word)
            return

        # 检查是否正在补全子命令（基础命令已输入）
        parts = text.split(maxsplit=1)
        base_cmd = parts[0].lower()
        if len(parts) > 1 or (len(parts) == 1 and text.endswith(" ")):
            sub_text = parts[1] if len(parts) > 1 else ""
            sub_lower = sub_text.lower()

            # 为 /model 动态模型别名补全
            if " " not in sub_text and base_cmd == "/model":
                yield from self._model_completions(sub_text, sub_lower)
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
    """斜杠命令及其子命令的内联幽灵文本建议。

    在您输入时以暗淡文本显示命令或子命令的其余部分。
    对于非斜杠输入，回退到基于历史的建议。
    """

    def __init__(
        self,
        history_suggest: AutoSuggest | None = None,
        completer: SlashCommandCompleter | None = None,
    ) -> None:
        self._history = history_suggest
        self._completer = completer  # 复用其模型缓存

    def get_suggestion(self, buffer, document):
        text = document.text_before_cursor

        # 仅对斜杠命令提供建议
        if not text.startswith("/"):
            # 对于常规文本，回退到历史建议
            if self._history:
                return self._history.get_suggestion(buffer, document)
            return None

        parts = text.split(maxsplit=1)
        base_cmd = parts[0].lower()

        if len(parts) == 1 and not text.endswith(" "):
            # 仍在输入命令名称：/upd → 建议 "ate"
            word = text[1:].lower()
            for cmd in COMMANDS:
                if self._completer is not None and not self._completer._command_allowed(cmd):
                    continue
                cmd_name = cmd[1:]  # 去除前导 /
                if cmd_name.startswith(word) and cmd_name != word:
                    return Suggestion(cmd_name[len(word):])
            return None

        # 命令已输入完整 — 建议子命令或模型名称
        sub_text = parts[1] if len(parts) > 1 else ""
        sub_lower = sub_text.lower()

        # 静态子命令
        if self._completer is not None and not self._completer._command_allowed(base_cmd):
            return None
        if base_cmd in SUBCOMMANDS and SUBCOMMANDS[base_cmd]:
            if " " not in sub_text:
                for sub in SUBCOMMANDS[base_cmd]:
                    if sub.startswith(sub_lower) and sub != sub_lower:
                        return Suggestion(sub[len(sub_text):])

        # 回退到历史建议
        if self._history:
            return self._history.get_suggestion(buffer, document)
        return None


def _file_size_label(path: str) -> str:
    """返回一个紧凑的人类可读文件大小，出错时返回空字符串。"""
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