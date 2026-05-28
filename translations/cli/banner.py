"""欢迎横幅、ASCII 艺术、技能摘要和 CLI 更新检查。

纯显示函数，不依赖 HermesCLI 状态。
"""

import json
import logging
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from hermes_constants import get_hermes_home
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prompt_toolkit import print_formatted_text as _pt_print
from prompt_toolkit.formatted_text import ANSI as _PT_ANSI

logger = logging.getLogger(__name__)


# =========================================================================
# ANSI building blocks for conversation display
# =========================================================================

_GOLD = "\033[1;38;2;255;215;0m"  # True-color #FFD700 bold
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RST = "\033[0m"


def cprint(text: str):
    """通过 prompt_toolkit 的渲染器打印 ANSI 彩色文本。"""
    _pt_print(_PT_ANSI(text))


# =========================================================================
# Skin-aware color helpers
# =========================================================================

def _skin_color(key: str, fallback: str) -> str:
    """从当前皮肤获取颜色，或返回回退值。"""
    try:
        from hermes_cli.skin_engine import get_active_skin
        return get_active_skin().get_color(key, fallback)
    except Exception:
        return fallback


def _skin_branding(key: str, fallback: str) -> str:
    """从当前皮肤获取品牌字符串，或返回回退值。"""
    try:
        from hermes_cli.skin_engine import get_active_skin
        return get_active_skin().get_branding(key, fallback)
    except Exception:
        return fallback


# =========================================================================
# ASCII Art & Branding
# =========================================================================

from hermes_cli import __version__ as VERSION, __release_date__ as RELEASE_DATE

HERMES_AGENT_LOGO = """[bold #FFD700]██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗       █████╗  ██████╗ ███████╗███╗   ██╗████████╗[/]
[bold #FFD700]██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝      ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝[/]
[#FFBF00]███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗█████╗███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║[/]
[#FFBF00]██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║╚════╝██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║[/]
[#CD7F32]██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║      ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║[/]
[#CD7F32]╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝      ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝[/]"""

HERMES_CADUCEUS = """[#CD7F32]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⣀⣀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#CD7F32]⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣇⠸⣿⣿⠇⣸⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀[/]
[#FFBF00]⠀⢀⣠⣴⣶⠿⠋⣩⡿⣿⡿⠻⣿⡇⢠⡄⢸⣿⠟⢿⣿⢿⣍⠙⠿⣶⣦⣄⡀⠀[/]
[#FFBF00]⠀⠀⠉⠉⠁⠶⠟⠋⠀⠉⠀⢀⣈⣁⡈⢁⣈⣁⡀⠀⠉⠀⠙⠻⠶⠈⠉⠉⠀⠀[/]
[#FFD700]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⡿⠛⢁⡈⠛⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#FFD700]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⣦⣤⣈⠁⢠⣴⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#FFBF00]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠻⢿⣿⣦⡉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#FFBF00]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣦⣈⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#CD7F32]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⠦⠈⠙⠿⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#CD7F32]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣤⡈⠁⢤⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#B8860B]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#B8860B]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠑⢶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#B8860B]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⢰⡆⠈⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#B8860B]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠈⣡⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]
[#B8860B]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]"""



# =========================================================================
# Skills scanning
# =========================================================================
def get_available_skills() -> Dict[str, List[str]]:
    """Return skills grouped by category, filtered by platform and disabled state.

    Delegates to ``_find_all_skills()`` from ``tools/skills_tool`` which already
    handles platform gating (``platforms:`` frontmatter) and respects the
    user's ``skills.disabled`` config list.
    """
    try:
        from tools.skills_tool import _find_all_skills
        all_skills = _find_all_skills()  # already filtered
    except Exception:
        return {}

    skills_by_category: Dict[str, List[str]] = {}
    for skill in all_skills:
        category = skill.get("category") or "general"
        skills_by_category.setdefault(category, []).append(skill["name"])
    return skills_by_category


# =========================================================================
# 更新检查
# =========================================================================

# 缓存更新检查结果6小时，避免重复的 git fetch
_UPDATE_CHECK_CACHE_SECONDS = 6 * 3600

# 当我们知道有更新但无法统计提交数时返回的标记值
# (例如 nix 构建的 hermes — 没有本地 git 历史记录可用来计数)。
UPDATE_AVAILABLE_NO_COUNT = -1

_UPSTREAM_REPO_URL = "https://github.com/NousResearch/hermes-agent.git"


def _check_via_rev(local_rev: str) -> Optional[int]:
    """通过 ls-remote 将嵌入的 git 修订版本与上游 main 分支进行比较。

    如果是最新则返回 0，如果落后则返回 ``UPDATE_AVAILABLE_NO_COUNT``，
    失败时返回 ``None``。
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", _UPSTREAM_REPO_URL, "refs/heads/main"],
            capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return None
    if result.returncode != 0 or not result.stdout:
        return None
    upstream_rev = result.stdout.split()[0]
    if not upstream_rev:
        return None
    return 0 if upstream_rev == local_rev else UPDATE_AVAILABLE_NO_COUNT


def _check_via_local_git(repo_dir: Path) -> Optional[int]:
    """统计本地检出仓库中落后于 origin/main 的提交数量。"""
    try:
        subprocess.run(
            ["git", "fetch", "origin", "--quiet"],
            capture_output=True, timeout=10,
            cwd=str(repo_dir),
        )
    except Exception:
        pass  # 离线或超时 — 使用过时的引用，这没问题

    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True, timeout=5,
            cwd=str(repo_dir),
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except Exception:
        pass
    return None


def _version_tuple(v: str) -> tuple[int, ...]:
    """将 '0.13.0' 解析为 (0, 13, 0) 以进行比较。非数字段变为 0。"""
    parts = []
    for segment in v.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _fetch_pypi_latest(package: str = "hermes-agent") -> Optional[str]:
    """从 PyPI 获取软件包的最新版本。失败时返回 None。"""
    try:
        import urllib.request
        url = f"https://pypi.org/pypi/{package}/json"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("info", {}).get("version")
    except Exception:
        return None
def check_via_pypi() -> Optional[int]:
    """Compare installed version against PyPI latest.

    Returns 0 if up-to-date, 1 if behind, None on failure.
    """
    latest = _fetch_pypi_latest()
    if latest is None:
        return None
    if latest == VERSION:
        return 0
    try:
        if _version_tuple(latest) > _version_tuple(VERSION):
            return 1
        return 0
    except Exception:
        return 1 if latest != VERSION else 0


def check_for_updates() -> Optional[int]:
    """检查是否有 Hermes 更新可用。

    两条路径：如果设置了 ``HERMES_REVISION``（Nix 构建会嵌入它），则通过 ``git ls-remote`` 将其与上游 main 分支比较。否则，查找本地 git 仓库并计算落后于 ``origin/main`` 的提交数。

    返回落后提交数，如果落后但数量未知则返回 ``UPDATE_AVAILABLE_NO_COUNT`` (-1)，如果是最新则返回 ``0``，如果检查失败或不适用则返回 ``None``。缓存 6 小时。
    """
    hermes_home = get_hermes_home()
    cache_file = hermes_home / ".update_check"
    embedded_rev = os.environ.get("HERMES_REVISION") or None

    # 读取缓存 — 如果自上次检查以来嵌入的修订版本已更改，则使缓存失效
    now = time.time()
    try:
        if cache_file.exists():
            cached = json.loads(cache_file.read_text())
            if (
                now - cached.get("ts", 0) < _UPDATE_CHECK_CACHE_SECONDS
                and cached.get("rev") == embedded_rev
            ):
                return cached.get("behind")
    except Exception:
        pass

    if embedded_rev:
        behind = _check_via_rev(embedded_rev)
    else:
        # 优先使用运行代码的位置而非配置文件作用域的路径。
        # $HERMES_HOME/hermes-agent/ 可能是来自 --clone-all 的陈旧副本；
        # Path(__file__) 始终解析到实际安装的检出位置。
        repo_dir = Path(__file__).parent.parent.resolve()
        if not (repo_dir / ".git").exists():
            repo_dir = hermes_home / "hermes-agent"
        if not (repo_dir / ".git").exists():
            behind = check_via_pypi()
        else:
            behind = _check_via_local_git(repo_dir)

    try:
        cache_file.write_text(json.dumps({"ts": now, "behind": behind, "rev": embedded_rev}))
    except Exception:
        pass

    return behind


def _resolve_repo_dir() -> Optional[Path]:
    """返回活跃的 Hermes git 检出目录，如果这不是 git 安装则返回 None。

    优先使用运行代码的位置而非配置文件作用域的路径，
    因为 ``$HERMES_HOME/hermes-agent/`` 可能是由 ``--clone-all`` 携带过来的陈旧副本。
    """
    repo_dir = Path(__file__).parent.parent.resolve()
    if not (repo_dir / ".git").exists():
        hermes_home = get_hermes_home()
        repo_dir = hermes_home / "hermes-agent"
    return repo_dir if (repo_dir / ".git").exists() else None


def _git_short_hash(repo_dir: Path, rev: str) -> Optional[str]:
    """将 git 修订版本解析为 8 字符短哈希。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=8", rev],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_dir),
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    value = (result.stdout or "").strip()
    return value or None
def get_git_banner_state(repo_dir: Optional[Path] = None) -> Optional[dict]:
    """Return upstream/local git hashes for the startup banner.

    For source installs and dev images this runs ``git rev-parse`` against
    the active checkout.  When no checkout is available — the canonical case
    is the published Docker image, which excludes ``.git`` from the build
    context — we fall back to the baked-in build SHA (see
    ``hermes_cli/build_info.py``) and return it as a frozen
    ``upstream == local`` state with ``ahead=0``.  A built image is by
    definition pinned to one commit, so "ahead" is always zero and the
    banner correctly shows ``· upstream <sha>`` with no carried-commits
    annotation.
    """
    repo_dir = repo_dir or _resolve_repo_dir()
    if repo_dir is None:
        # No git checkout — try the baked build SHA (Docker image path).
        try:
            from hermes_cli.build_info import get_build_sha
            baked = get_build_sha(short=8)
            if baked:
                return {"upstream": baked, "local": baked, "ahead": 0}
        except Exception:
            pass
        return None

    upstream = _git_short_hash(repo_dir, "origin/main")
    local = _git_short_hash(repo_dir, "HEAD")
    if not upstream or not local:
        # Live-git lookup failed (e.g. shallow clone without origin/main).
        # Fall back to the baked build SHA if available.
        try:
            from hermes_cli.build_info import get_build_sha
            baked = get_build_sha(short=8)
            if baked:
                return {"upstream": baked, "local": baked, "ahead": 0}
        except Exception:
            pass
        return None

    ahead = 0
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "origin/main..HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_dir),
        )
        if result.returncode == 0:
            ahead = int((result.stdout or "0").strip() or "0")
    except Exception:
        ahead = 0

    return {"upstream": upstream, "local": local, "ahead": max(ahead, 0)}


_RELEASE_URL_BASE = "https://github.com/NousResearch/hermes-agent/releases/tag"
_latest_release_cache: Optional[tuple] = None  # (tag, url) once resolved


def get_latest_release_tag(repo_dir: Optional[Path] = None) -> Optional[tuple]:
    """Return ``(tag, release_url)`` for the latest git tag, or None.

    Local-only — runs ``git describe --tags --abbrev=0`` against the
    Hermes checkout. Cached per-process. Release URL always points at the
    canonical NousResearch/hermes-agent repo (forks don't get a link).
    """
    global _latest_release_cache
    if _latest_release_cache is not None:
        return _latest_release_cache or None

    repo_dir = repo_dir or _resolve_repo_dir()
    if repo_dir is None:
        _latest_release_cache = ()  # falsy sentinel — skip future lookups
        return None

    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            timeout=3,
            cwd=str(repo_dir),
        )
    except Exception:
        _latest_release_cache = ()
        return None

    if result.returncode != 0:
        _latest_release_cache = ()
        return None

    tag = (result.stdout or "").strip()
    if not tag:
        _latest_release_cache = ()
        return None

    url = f"{_RELEASE_URL_BASE}/{tag}"
    _latest_release_cache = (tag, url)
    return _latest_release_cache
def format_banner_version_label() -> str:
    """Return the version label shown in the startup banner title."""
    base = f"Hermes Agent v{VERSION} ({RELEASE_DATE})"
    state = get_git_banner_state()
    if not state:
        return base

    upstream = state["upstream"]
    local = state["local"]
    ahead = int(state.get("ahead") or 0)

    if ahead <= 0 or upstream == local:
        return f"{base} · 上游 {upstream}"

    carried_word = "个提交" if ahead == 1 else "个提交"
    return f"{base} · 上游 {upstream} · 本地 {local} (+{ahead} 个未推送的 {carried_word})"


# =========================================================================
# Non-blocking update check
# =========================================================================

_update_result: Optional[int] = None
_update_check_done = threading.Event()


def prefetch_update_check():
    """Kick off update check in a background daemon thread."""
    def _run():
        global _update_result
        _update_result = check_for_updates()
        _update_check_done.set()
    t = threading.Thread(target=_run, daemon=True)
    t.start()


def get_update_result(timeout: float = 0.5) -> Optional[int]:
    """Get result of prefetched check. Returns None if not ready."""
    _update_check_done.wait(timeout=timeout)
    return _update_result


# =========================================================================
# Welcome banner
# =========================================================================

def _format_context_length(tokens: int) -> str:
    """Format a token count for display (e.g. 128000 → '128K', 1048576 → '1M')."""
    if tokens >= 1_000_000:
        val = tokens / 1_000_000
        rounded = round(val)
        if abs(val - rounded) < 0.05:
            return f"{rounded}M"
        return f"{val:.1f}M"
    elif tokens >= 1_000:
        val = tokens / 1_000
        rounded = round(val)
        if abs(val - rounded) < 0.05:
            return f"{rounded}K"
        return f"{val:.1f}K"
    return str(tokens)


def _display_toolset_name(toolset_name: str) -> str:
    """Normalize internal/legacy toolset identifiers for banner display."""
    if not toolset_name:
        return "未知"
    return (
        toolset_name[:-6]
        if toolset_name.endswith("_tools")
        else toolset_name
    )


def build_welcome_banner(console: Console, model: str, cwd: str,
                         tools: List[dict] = None,
                         enabled_toolsets: List[str] = None,
                         session_id: str = None,
                         get_toolset_for_tool=None,
                         context_length: int = None):
    """Build and print a welcome banner with caduceus on left and info on right.

    Args:
        console: Rich Console instance.
        model: Current model name.
        cwd: Current working directory.
        tools: List of tool definitions.
        enabled_toolsets: List of enabled toolset names.
        session_id: Session identifier.
        get_toolset_for_tool: Callable to map tool name -> toolset name.
        context_length: Model's context window size in tokens.
    """
    from model_tools import check_tool_availability, TOOLSET_REQUIREMENTS
    if get_toolset_for_tool is None:
        from model_tools import get_toolset_for_tool

    tools = tools or []
    enabled_toolsets = enabled_toolsets or []

    _, unavailable_toolsets = check_tool_availability(quiet=True)
    disabled_tools = set()
    # Tools whose toolset has a check_fn are lazy-initialized (e.g. honcho,
    # homeassistant) — they show as unavailable at banner time because the
    # check hasn't run yet, but they aren't misconfigured.
    lazy_tools = set()
    for item in unavailable_toolsets:
        toolset_name = item.get("name", "")
        ts_req = TOOLSET_REQUIREMENTS.get(toolset_name, {})
        tools_in_ts = item.get("tools", [])
        if ts_req.get("check_fn"):
            lazy_tools.update(tools_in_ts)
        else:
            disabled_tools.update(tools_in_ts)

    layout_table = Table.grid(padding=(0, 2))
    layout_table.add_column("left", justify="center")
    layout_table.add_column("right", justify="left")

    # Resolve skin colors once for the entire banner
    accent = _skin_color("banner_accent", "#FFBF00")
    dim = _skin_color("banner_dim", "#B8860B")
    text = _skin_color("banner_text", "#FFF8DC")
    session_color = _skin_color("session_border", "#8B8682")

    # Use skin's custom caduceus art if provided
    try:
        from hermes_cli.skin_engine import get_active_skin
        _bskin = get_active_skin()
        _hero = _bskin.banner_hero if hasattr(_bskin, 'banner_hero') and _bskin.banner_hero else HERMES_CADUCEUS
    except Exception:
        _bskin = None
        _hero = HERMES_CADUCEUS
    left_lines = ["", _hero, ""]
    model_short = model.split("/")[-1] if "/" in model else model
    if model_short.endswith(".gguf"):
        model_short = model_short[:-5]
    if len(model_short) > 28:
        model_short = model_short[:25] + "..."
    ctx_str = f" [dim {dim}]·[/] [dim {dim}]{_format_context_length(context_length)} 上下文[/]" if context_length else ""
    left_lines.append(f"[{accent}]{model_short}[/]{ctx_str} [dim {dim}]·[/] [dim {dim}]Nous Research[/]")

    if os.getenv("HERMES_YOLO_MODE"):
        left_lines.append(f"[bold red]⚠ YOLO 模式[/] [dim {dim}]— 所有确认提示已绕过[/]")
    left_lines.append(f"[dim {dim}]{cwd}[/]")
    if session_id:
        left_lines.append(f"[dim {session_color}]会话: {session_id}[/]")
    left_content = "\n".join(left_lines)

    right_lines = [f"[bold {accent}]可用工具[/]"]
    toolsets_dict: Dict[str, list] = {}

    for tool in tools:
        tool_name = tool["function"]["name"]
        toolset = _display_toolset_name(get_toolset_for_tool(tool_name) or "其他")
        toolsets_dict.setdefault(toolset, []).append(tool_name)

    for item in unavailable_toolsets:
        toolset_id = item.get("id", item.get("name", "unknown"))
        display_name = _display_toolset_name(toolset_id)
        if display_name not in toolsets_dict:
            toolsets_dict[display_name] = []
        for tool_name in item.get("tools", []):
            if tool_name not in toolsets_dict[display_name]:
                toolsets_dict[display_name].append(tool_name)

    sorted_toolsets = sorted(toolsets_dict.keys())
    display_toolsets = sorted_toolsets[:8]
    remaining_toolsets = len(sorted_toolsets) - 8

    for toolset in display_toolsets:
        tool_names = toolsets_dict[toolset]
        colored_names = []
        for name in sorted(tool_names):
            if name in disabled_tools:
                colored_names.append(f"[red]{name}[/]")
            elif name in lazy_tools:
                colored_names.append(f"[yellow]{name}[/]")
            else:
                colored_names.append(f"[{text}]{name}[/]")

        tools_str = ", ".join(colored_names)
        if len(", ".join(sorted(tool_names))) > 45:
            short_names = []
            length = 0
            for name in sorted(tool_names):
                if length + len(name) + 2 > 42:
                    short_names.append("...")
                    break
                short_names.append(name)
                length += len(name) + 2
            colored_names = []
            for name in short_names:
                if name == "...":
                    colored_names.append("[dim]...[/]")
                elif name in disabled_tools:
                    colored_names.append(f"[red]{name}[/]")
                elif name in lazy_tools:
                    colored_names.append(f"[yellow]{name}[/]")
                else:
                    colored_names.append(f"[{text}]{name}[/]")
            tools_str = ", ".join(colored_names)

        right_lines.append(f"[dim {dim}]{toolset}:[/] {tools_str}")

    if remaining_toolsets > 0:
        right_lines.append(f"[dim {dim}](以及 {remaining_toolsets} 个更多工具集...)[/]")

    # MCP Servers section (only if configured)
    try:
        from tools.mcp_tool import get_mcp_status
        mcp_status = get_mcp_status()
    except Exception:
        mcp_status = []

    if mcp_status:
        right_lines.append("")
        right_lines.append(f"[bold {accent}]MCP 服务器[/]")
        for srv in mcp_status:
            if srv["connected"]:
                right_lines.append(
                    f"[dim {dim}]{srv['name']}[/] [{text}]({srv['transport']})[/] "
                    f"[dim {dim}]—[/] [{text}]{srv['tools']} 个工具[/]"
                )
            else:
                right_lines.append(
                    f"[red]{srv['name']}[/] [dim]({srv['transport']})[/] "
                    f"[red]— 连接失败[/]"
                )

    right_lines.append("")
    right_lines.append(f"[bold {accent}]可用技能[/]")
    skills_by_category = get_available_skills()
    total_skills = sum(len(s) for s in skills_by_category.values())

    if skills_by_category:
        for category in sorted(skills_by_category.keys()):
            skill_names = sorted(skills_by_category[category])
            if len(skill_names) > 8:
                display_names = skill_names[:8]
                skills_str = ", ".join(display_names) + f" +{len(skill_names) - 8} 更多"
            else:
                skills_str = ", ".join(skill_names)
            if len(skills_str) > 50:
                skills_str = skills_str[:47] + "..."
            right_lines.append(f"[dim {dim}]{category}:[/] [{text}]{skills_str}[/]")
    else:
        right_lines.append(f"[dim {dim}]未安装任何技能[/]")

    right_lines.append("")
    mcp_connected = sum(1 for s in mcp_status if s["connected"]) if mcp_status else 0
    summary_parts = [f"{len(tools)} 个工具", f"{total_skills} 个技能"]
    if mcp_connected:
        summary_parts.append(f"{mcp_connected} 个 MCP 服务器")
    summary_parts.append("/help 查看命令")
    # Indicate when the codex_app_server runtime is active so users
    # understand why tool counts may not match what's actually reachable
    # (codex builds its own tool list inside the spawned subprocess).
    try:
        from hermes_cli.codex_runtime_switch import get_current_runtime
        from hermes_cli.config import load_config as _load_cfg
        if get_current_runtime(_load_cfg()) == "codex_app_server":
            right_lines.append(
                f"[bold {accent}]运行时:[/] [{text}]codex app-server[/] "
                f"[dim {dim}](终端/文件操作/MCP 在 codex 内部运行)[/]"
            )
    except Exception:
        pass
    # Show active profile name when not 'default'
    try:
        from hermes_cli.profiles import get_active_profile_name
        _profile_name = get_active_profile_name()
        if _profile_name and _profile_name != "default":
            right_lines.append(f"[bold {accent}]配置文件:[/] [{text}]{_profile_name}[/]")
    except Exception:
        pass  # Never break the banner over a profiles.py bug

    right_lines.append(f"[dim {dim}]{' · '.join(summary_parts)}[/]")

    # Update check — use prefetched result if available
    try:
        behind = get_update_result(timeout=0.5)
        if behind is not None and behind != 0:
            from hermes_cli.config import get_managed_update_command, recommended_update_command
            if behind > 0:
                commits_word = "个提交" if behind == 1 else "个提交"
                right_lines.append(
                    f"[bold yellow]⚠ 落后 {behind} {commits_word}[/]"
                    f"[dim yellow] — 运行 [bold]{recommended_update_command()}[/bold] 以更新[/]"
                )
            else:
                # UPDATE_AVAILABLE_NO_COUNT: nix-built hermes; we know an update
                # exists but not by how much, and we don't know how the user
                # installed it (nix run, profile, system flake, home-manager).
                managed_cmd = get_managed_update_command()
                line = "[bold yellow]⚠ 有可用更新[/]"
                if managed_cmd:
                    line += f"[dim yellow] — 运行 [bold]{managed_cmd}[/bold][/]"
                right_lines.append(line)
    except Exception:
        pass  # Never break the banner over an update check

    right_content = "\n".join(right_lines)
    layout_table.add_row(left_content, right_content)

    title_color = _skin_color("banner_title", "#FFD700")
    border_color = _skin_color("banner_border", "#CD7F32")
    version_label = format_banner_version_label()
    release_info = get_latest_release_tag()
    if release_info:
        _tag, _url = release_info
        title_markup = f"[bold {title_color}][link={_url}]{version_label}[/link][/]"
    else:
        title_markup = f"[bold {title_color}]{version_label}[/]"
    outer_panel = Panel(
        layout_table,
        title=title_markup,
        border_style=border_color,
        padding=(0, 2),
    )

    console.print()
    term_width = shutil.get_terminal_size().columns
    if term_width >= 95:
        _logo = _bskin.banner_logo if _bskin and hasattr(_bskin, 'banner_logo') and _bskin.banner_logo else HERMES_AGENT_LOGO
        console.print(_logo)
        console.print()
    console.print(outer_panel)