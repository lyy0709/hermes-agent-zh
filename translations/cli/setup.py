"""
Hermes Agent 的交互式设置向导。

模块化向导，包含可独立运行的章节：
  1. 模型与提供商 — 选择您的 AI 提供商和模型
  2. 终端后端 — 您的 Agent 运行命令的位置
  3. Agent 设置 — 迭代次数、压缩、会话重置
  4. 消息平台 — 连接 Telegram、Discord 等
  5. 工具 — 配置 TTS、网络搜索、图像生成等

配置文件存储在 ~/.hermes/ 以便于访问。
"""

import importlib.util
import json
import logging
import os
import re
import shutil
import sys
import copy
from pathlib import Path
from typing import Optional, Dict, Any

from hermes_cli.nous_subscription import get_nous_subscription_features
from tools.tool_backend_helpers import managed_nous_tools_enabled
from utils import base_url_hostname
from hermes_constants import get_optional_skills_dir

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

_DOCS_BASE = "https://hermes-agent.nousresearch.com/docs"


def _model_config_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    current_model = config.get("model")
    if isinstance(current_model, dict):
        return dict(current_model)
    if isinstance(current_model, str) and current_model.strip():
        return {"default": current_model.strip()}
    return {}


def _get_credential_pool_strategies(config: Dict[str, Any]) -> Dict[str, str]:
    strategies = config.get("credential_pool_strategies")
    return dict(strategies) if isinstance(strategies, dict) else {}


def _set_credential_pool_strategy(config: Dict[str, Any], provider: str, strategy: str) -> None:
    if not provider:
        return
    strategies = _get_credential_pool_strategies(config)
    strategies[provider] = strategy
    config["credential_pool_strategies"] = strategies


def _supports_same_provider_pool_setup(provider: str) -> bool:
    if not provider or provider == "custom":
        return False
    if provider == "openrouter":
        return True
    from hermes_cli.auth import PROVIDER_REGISTRY

    pconfig = PROVIDER_REGISTRY.get(provider)
    if not pconfig:
        return False
    return pconfig.auth_type in {"api_key", "oauth_device_code"}


# 每个提供商的默认模型列表 — 当无法访问实时的 /models 端点时用作后备。
_DEFAULT_PROVIDER_MODELS = {
    "copilot-acp": [
        "copilot-acp",
    ],
    "copilot": [
        "gpt-5.4",
        "gpt-5.4-mini",
        "gpt-5-mini",
        "gpt-5.3-codex",
        "gpt-5.2-codex",
        "gpt-4.1",
        "gpt-4o",
        "gpt-4o-mini",
        "claude-opus-4.6",
        "claude-sonnet-4.6",
        "claude-sonnet-4.5",
        "claude-haiku-4.5",
        "gemini-2.5-pro",
        "grok-code-fast-1",
    ],
    "gemini": [
        "gemini-3.1-pro-preview", "gemini-3-pro-preview",
        "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview",
    ],
    "zai": ["glm-5.1", "glm-5", "glm-4.7", "glm-4.5", "glm-4.5-flash"],
    "kimi-coding": ["kimi-k2.6", "kimi-k2.5", "kimi-k2-thinking", "kimi-k2-turbo-preview"],
    "kimi-coding-cn": ["kimi-k2.6", "kimi-k2.5", "kimi-k2-thinking", "kimi-k2-turbo-preview"],
    "stepfun": ["step-3.5-flash", "step-3.5-flash-2603"],
    "arcee": ["trinity-large-thinking", "trinity-large-preview", "trinity-mini"],
    "minimax": ["MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M2.1", "MiniMax-M2"],
    "minimax-cn": ["MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M2.1", "MiniMax-M2"],
    "ai-gateway": ["anthropic/claude-opus-4.6", "anthropic/claude-sonnet-4.6", "openai/gpt-5", "google/gemini-3-flash"],
    "kilocode": ["anthropic/claude-opus-4.6", "anthropic/claude-sonnet-4.6", "openai/gpt-5.4", "google/gemini-3-pro-preview", "google/gemini-3-flash-preview"],
    "opencode-zen": ["gpt-5.4", "gpt-5.3-codex", "claude-sonnet-4-6", "gemini-3-flash", "glm-5", "kimi-k2.5", "minimax-m2.7"],
    "opencode-go": ["kimi-k2.6", "kimi-k2.5", "glm-5.1", "glm-5", "mimo-v2.5-pro", "mimo-v2.5", "mimo-v2-pro", "mimo-v2-omni", "minimax-m2.7", "minimax-m2.5", "qwen3.6-plus", "qwen3.5-plus"],
    "huggingface": [
        "Qwen/Qwen3.5-397B-A17B", "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "Qwen/Qwen3-Coder-480B-A35B-Instruct", "deepseek-ai/DeepSeek-R1-0528",
        "deepseek-ai/DeepSeek-V3.2", "moonshotai/Kimi-K2.5",
    ],
}
def _current_reasoning_effort(config: Dict[str, Any]) -> str:
    agent_cfg = config.get("agent")
    if isinstance(agent_cfg, dict):
        return str(agent_cfg.get("reasoning_effort") or "").strip().lower()
    return ""


def _set_reasoning_effort(config: Dict[str, Any], effort: str) -> None:
    agent_cfg = config.get("agent")
    if not isinstance(agent_cfg, dict):
        agent_cfg = {}
        config["agent"] = agent_cfg
    agent_cfg["reasoning_effort"] = effort




# Import config helpers
from hermes_cli.config import (
    cfg_get,
    DEFAULT_CONFIG,
    get_hermes_home,
    get_config_path,
    get_env_path,
    load_config,
    save_config,
    save_env_value,
    remove_env_value,
    get_env_value,
    ensure_hermes_home,
)
# display_hermes_home imported lazily at call sites (stale-module safety during hermes update)

from hermes_cli.colors import Colors, color


def print_header(title: str):
    """Print a section header."""
    print()
    print(color(f"◆ {title}", Colors.CYAN, Colors.BOLD))


from hermes_cli.cli_output import (  # noqa: E402
    print_error,
    print_info,
    print_success,
    print_warning,
)


def is_interactive_stdin() -> bool:
    """Return True when stdin looks like a usable interactive TTY."""
    stdin = getattr(sys, "stdin", None)
    if stdin is None:
        return False
    try:
        return bool(stdin.isatty())
    except Exception:
        return False


def print_noninteractive_setup_guidance(reason: str | None = None) -> None:
    """Print guidance for headless/non-interactive setup flows."""
    print()
    print(color("⚕ Hermes 设置 — 非交互模式", Colors.CYAN, Colors.BOLD))
    print()
    if reason:
        print_info(reason)
    print_info("此处无法使用交互式向导。")
    print()
    print_info("请使用环境变量或配置命令来配置 Hermes：")
    print_info("  hermes config set model.provider custom")
    print_info("  hermes config set model.base_url http://localhost:8080/v1")
    print_info("  hermes config set model.default your-model-name")
    print()
    print_info("或在您的环境中设置 OPENROUTER_API_KEY / OPENAI_API_KEY。")
    print_info("在交互式终端中运行 'hermes setup' 以使用完整向导。")
    print()


def prompt(question: str, default: str = None, password: bool = False) -> str:
    """Prompt for input with optional default."""
    if default:
        display = f"{question} [{default}]: "
    else:
        display = f"{question}: "

    try:
        if password:
            import getpass

            value = getpass.getpass(color(display, Colors.YELLOW))
        else:
            value = input(color(display, Colors.YELLOW))

        cleaned = _sanitize_pasted_input(value)
        return cleaned.strip() or default or ""
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(1)


_BRACKETED_PASTE_PATTERN = re.compile(r"\x1b\[\s*200~|\x1b\[\s*201~")


def _sanitize_pasted_input(value: str) -> str:
    """Strip terminal bracketed-paste control markers from pasted text."""
    if not isinstance(value, str) or not value:
        return value
    return _BRACKETED_PASTE_PATTERN.sub("", value)
def _curses_prompt_choice(question: str, choices: list, default: int = 0, description: str | None = None) -> int:
    """Single-select menu using curses. Delegates to curses_radiolist."""
    from hermes_cli.curses_ui import curses_radiolist
    return curses_radiolist(question, choices, selected=default, cancel_returns=-1, description=description)



def prompt_choice(question: str, choices: list, default: int = 0, description: str | None = None) -> int:
    """Prompt for a choice from a list with arrow key navigation.

    Escape keeps the current default (skips the question).
    Ctrl+C exits the wizard.
    """
    idx = _curses_prompt_choice(question, choices, default, description=description)
    if idx >= 0:
        if idx == default:
            print_info("  已跳过（保持当前选项）")
            print()
            return default
        print()
        return idx

    print(color(question, Colors.YELLOW))
    for i, choice in enumerate(choices):
        marker = "●" if i == default else "○"
        if i == default:
            print(color(f"  {marker} {choice}", Colors.GREEN))
        else:
            print(f"  {marker} {choice}")

    print_info(f"  按回车键选择默认值 ({default + 1})  按 Ctrl+C 退出")

    while True:
        try:
            value = input(
                color(f"  请选择 [1-{len(choices)}] ({default + 1}): ", Colors.DIM)
            )
            if not value:
                return default
            idx = int(value) - 1
            if 0 <= idx < len(choices):
                return idx
            print_error(f"请输入一个介于 1 和 {len(choices)} 之间的数字")
        except ValueError:
            print_error("请输入一个数字")
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(1)


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt for yes/no. Ctrl+C exits, empty input returns default."""
    default_str = "Y/n" if default else "y/N"

    while True:
        try:
            value = (
                input(color(f"{question} [{default_str}]: ", Colors.YELLOW))
                .strip()
                .lower()
            )
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(1)

        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print_error("请输入 'y' 或 'n'")


def prompt_checklist(title: str, items: list, pre_selected: list = None) -> list:
    """
    Display a multi-select checklist and return the indices of selected items.

    Each item in `items` is a display string. `pre_selected` is a list of
    indices that should be checked by default. A "Continue →" option is
    appended at the end — the user toggles items with Space and confirms
    with Enter on "Continue →".

    Falls back to a numbered toggle interface when simple_term_menu is
    unavailable.

    Returns:
        List of selected indices (not including the Continue option).
    """
    if pre_selected is None:
        pre_selected = []

    from hermes_cli.curses_ui import curses_checklist

    chosen = curses_checklist(
        title,
        items,
        set(pre_selected),
        cancel_returns=set(pre_selected),
    )
    return sorted(chosen)
def _prompt_api_key(var: dict):
    """Display a nicely formatted API key input screen for a single env var."""
    tools = var.get("tools", [])
    tools_str = ", ".join(tools[:3])
    if len(tools) > 3:
        tools_str += f", +{len(tools) - 3} more"

    print()
    print(color(f"  ─── {var.get('description', var['name'])} ───", Colors.CYAN))
    print()
    if tools_str:
        print_info(f"  启用: {tools_str}")
    if var.get("url"):
        print_info(f"  获取密钥地址: {var['url']}")
    print()

    if var.get("password"):
        value = prompt(f"  {var.get('prompt', var['name'])}", password=True)
    else:
        value = prompt(f"  {var.get('prompt', var['name'])}")

    if value:
        save_env_value(var["name"], value)
        print_success("  ✓ 已保存")
    else:
        print_warning("  已跳过（稍后可通过 'hermes setup' 配置）")


def _print_setup_summary(config: dict, hermes_home):
    """Print the setup completion summary."""
    # Tool availability summary
    print()
    print_header("工具可用性概览")

    tool_status = []
    subscription_features = get_nous_subscription_features(config)

    # Vision — use the same runtime resolver as the actual vision tools
    try:
        from agent.auxiliary_client import get_available_vision_backends

        _vision_backends = get_available_vision_backends()
    except Exception:
        _vision_backends = []

    if _vision_backends:
        tool_status.append(("视觉（图像分析）", True, None))
    else:
        tool_status.append(("视觉（图像分析）", False, "运行 'hermes setup' 进行配置"))

    # Mixture of Agents — requires OpenRouter specifically (calls multiple models)
    if get_env_value("OPENROUTER_API_KEY"):
        tool_status.append(("混合 Agent", True, None))
    else:
        tool_status.append(("混合 Agent", False, "OPENROUTER_API_KEY"))

    # Web tools (Exa, Parallel, Firecrawl, or Tavily)
    if subscription_features.web.managed_by_nous:
        tool_status.append(("网络搜索与提取（Nous 订阅）", True, None))
    elif subscription_features.web.available:
        label = "网络搜索与提取"
        if subscription_features.web.current_provider:
            label = f"网络搜索与提取 ({subscription_features.web.current_provider})"
        tool_status.append((label, True, None))
    else:
        tool_status.append(("网络搜索与提取", False, "EXA_API_KEY, PARALLEL_API_KEY, FIRECRAWL_API_KEY/FIRECRAWL_API_URL, 或 TAVILY_API_KEY"))

    # Browser tools (local Chromium, Camofox, Browserbase, Browser Use, or Firecrawl)
    browser_provider = subscription_features.browser.current_provider
    if subscription_features.browser.managed_by_nous:
        tool_status.append(("浏览器自动化（Nous Browser Use）", True, None))
    elif subscription_features.browser.available:
        label = "浏览器自动化"
        if browser_provider:
            label = f"浏览器自动化 ({browser_provider})"
        tool_status.append((label, True, None))
    else:
        missing_browser_hint = "npm install -g agent-browser, 设置 CAMOFOX_URL, 或配置 Browser Use 或 Browserbase"
        if browser_provider == "Browserbase":
            missing_browser_hint = (
                "npm install -g agent-browser 并设置 "
                "BROWSERBASE_API_KEY/BROWSERBASE_PROJECT_ID"
            )
        elif browser_provider == "Browser Use":
            missing_browser_hint = (
                "npm install -g agent-browser 并设置 BROWSER_USE_API_KEY"
            )
        elif browser_provider == "Camofox":
            missing_browser_hint = "CAMOFOX_URL"
        elif browser_provider == "Local browser":
            missing_browser_hint = "npm install -g agent-browser"
        tool_status.append(
            ("浏览器自动化", False, missing_browser_hint)
        )

    # Image generation — FAL (direct or via Nous), or any plugin-registered
    # provider (OpenAI, etc.)
    if subscription_features.image_gen.managed_by_nous:
        tool_status.append(("图像生成（Nous 订阅）", True, None))
    elif subscription_features.image_gen.available:
        tool_status.append(("图像生成", True, None))
    else:
        # Fall back to probing plugin-registered providers so OpenAI-only
        # setups don't show as "missing FAL_KEY".
        _img_backend = None
        try:
            from agent.image_gen_registry import list_providers
            from hermes_cli.plugins import _ensure_plugins_discovered

            _ensure_plugins_discovered()
            for _p in list_providers():
                if _p.name == "fal":
                    continue
                try:
                    if _p.is_available():
                        _img_backend = _p.display_name
                        break
                except Exception:
                    continue
        except Exception:
            pass
        if _img_backend:
            tool_status.append((f"图像生成 ({_img_backend})", True, None))
        else:
            tool_status.append(("图像生成", False, "FAL_KEY 或 OPENAI_API_KEY"))

    # TTS — show configured provider
    tts_provider = cfg_get(config, "tts", "provider", default="edge")
    if subscription_features.tts.managed_by_nous:
        tool_status.append(("文本转语音（通过 Nous 订阅的 OpenAI）", True, None))
    elif tts_provider == "elevenlabs" and get_env_value("ELEVENLABS_API_KEY"):
        tool_status.append(("文本转语音（ElevenLabs）", True, None))
    elif tts_provider == "openai" and (
        get_env_value("VOICE_TOOLS_OPENAI_KEY") or get_env_value("OPENAI_API_KEY")
    ):
        tool_status.append(("文本转语音（OpenAI）", True, None))
    elif tts_provider == "minimax" and get_env_value("MINIMAX_API_KEY"):
        tool_status.append(("文本转语音（MiniMax）", True, None))
    elif tts_provider == "mistral" and get_env_value("MISTRAL_API_KEY"):
        tool_status.append(("文本转语音（Mistral Voxtral）", True, None))
    elif tts_provider == "gemini" and (get_env_value("GEMINI_API_KEY") or get_env_value("GOOGLE_API_KEY")):
        tool_status.append(("文本转语音（Google Gemini）", True, None))
    elif tts_provider == "neutts":
        try:
            neutts_ok = importlib.util.find_spec("neutts") is not None
        except Exception:
            neutts_ok = False
        if neutts_ok:
            tool_status.append(("文本转语音（NeuTTS 本地）", True, None))
        else:
            tool_status.append(("文本转语音（NeuTTS — 未安装）", False, "运行 'hermes setup tts'"))
    elif tts_provider == "kittentts":
        try:
            import importlib.util
            kittentts_ok = importlib.util.find_spec("kittentts") is not None
        except Exception:
            kittentts_ok = False
        if kittentts_ok:
            tool_status.append(("文本转语音（KittenTTS 本地）", True, None))
        else:
            tool_status.append(("文本转语音（KittenTTS — 未安装）", False, "运行 'hermes setup tts'"))
    else:
        tool_status.append(("文本转语音（Edge TTS）", True, None))

    if subscription_features.modal.managed_by_nous:
        tool_status.append(("Modal 执行（Nous 订阅）", True, None))
    elif cfg_get(config, "terminal", "backend") == "modal":
        if subscription_features.modal.direct_override:
            tool_status.append(("Modal 执行（直接 Modal）", True, None))
        else:
            tool_status.append(("Modal 执行", False, "运行 'hermes setup terminal'"))
    elif managed_nous_tools_enabled() and subscription_features.nous_auth_present:
        tool_status.append(("Modal 执行（可通过 Nous 订阅使用）", True, None))

    # Tinker + WandB (RL training)
    if get_env_value("TINKER_API_KEY") and get_env_value("WANDB_API_KEY"):
        tool_status.append(("强化学习训练（Tinker）", True, None))
    elif get_env_value("TINKER_API_KEY"):
        tool_status.append(("强化学习训练（Tinker）", False, "WANDB_API_KEY"))
    else:
        tool_status.append(("强化学习训练（Tinker）", False, "TINKER_API_KEY"))

    # Home Assistant
    if get_env_value("HASS_TOKEN"):
        tool_status.append(("智能家居（Home Assistant）", True, None))

    # Spotify (OAuth via hermes auth spotify — check auth.json, not env vars)
    try:
        from hermes_cli.auth import get_provider_auth_state
        _spotify_state = get_provider_auth_state("spotify") or {}
        if _spotify_state.get("access_token") or _spotify_state.get("refresh_token"):
            tool_status.append(("Spotify（PKCE OAuth）", True, None))
    except Exception:
        pass

    # Skills Hub
    if get_env_value("GITHUB_TOKEN"):
        tool_status.append(("技能中心（GitHub）", True, None))
    else:
        tool_status.append(("技能中心（GitHub）", False, "GITHUB_TOKEN"))

    # Terminal (always available if system deps met)
    tool_status.append(("终端/命令", True, None))

    # Task planning (always available, in-memory)
    tool_status.append(("任务规划（待办事项）", True, None))

    # Skills (always available -- bundled skills + user-created skills)
    tool_status.append(("技能（查看、创建、编辑）", True, None))

    # Print status
    available_count = sum(1 for _, avail, _ in tool_status if avail)
    total_count = len(tool_status)

    print_info(f"{available_count}/{total_count} 个工具类别可用:")
    print()

    for name, available, missing_var in tool_status:
        if available:
            print(f"   {color('✓', Colors.GREEN)} {name}")
        else:
            print(
                f"   {color('✗', Colors.RED)} {name} {color(f'(缺少 {missing_var})', Colors.DIM)}"
            )

    print()

    disabled_tools = [(name, var) for name, avail, var in tool_status if not avail]
    if disabled_tools:
        print_warning(
            "部分工具已禁用。运行 'hermes setup tools' 进行配置，"
        )
        from hermes_constants import display_hermes_home as _dhh
        print_warning(f"或直接编辑 {_dhh()}/.env 文件以添加缺失的 API 密钥。")
        print()

    # Done banner
    print()
    print(
        color(
            "┌─────────────────────────────────────────────────────────┐", Colors.GREEN
        )
    )
    print(
        color(
            "│              ✓ 设置完成！                          │", Colors.GREEN
        )
    )
    print(
        color(
            "└─────────────────────────────────────────────────────────┘", Colors.GREEN
        )
    )
    print()

    # Show file locations prominently
    from hermes_constants import display_hermes_home as _dhh
    print(color(f"📁 所有文件位于 {_dhh()}/:", Colors.CYAN, Colors.BOLD))
    print()
    print(f"   {color('设置:', Colors.YELLOW)}  {get_config_path()}")
    print(f"   {color('API 密钥:', Colors.YELLOW)}  {get_env_path()}")
    print(
        f"   {color('数据:', Colors.YELLOW)}      {hermes_home}/cron/, sessions/, logs/"
    )
    print()

    print(color("─" * 60, Colors.DIM))
    print()
    print(color("📝 编辑配置:", Colors.CYAN, Colors.BOLD))
    print()
    print(f"   {color('hermes setup', Colors.GREEN)}          重新运行完整向导")
    print(f"   {color('hermes setup model', Colors.GREEN)}    更改模型/提供商")
    print(f"   {color('hermes setup terminal', Colors.GREEN)} 更改终端后端")
    print(f"   {color('hermes setup gateway', Colors.GREEN)}  配置消息传递")
    print(f"   {color('hermes setup tools', Colors.GREEN)}    配置工具提供商")
    print()
    print(f"   {color('hermes config', Colors.GREEN)}         查看当前设置")
    print(
        f"   {color('hermes config edit', Colors.GREEN)}    在编辑器中打开配置"
    )
    print(f"   {color('hermes config set <key> <value>', Colors.GREEN)}")
    print("                          设置特定值")
    print()
    print("   或直接编辑文件:")
    print(f"   {color(f'nano {get_config_path()}', Colors.DIM)}")
    print(f"   {color(f'nano {get_env_path()}', Colors.DIM)}")
    print()

    print(color("─" * 60, Colors.DIM))
    print()
    print(color("🚀 准备就绪！", Colors.CYAN, Colors.BOLD))
    print()
    print(f"   {color('hermes', Colors.GREEN)}              开始聊天")
    print(f"   {color('hermes gateway', Colors.GREEN)}      启动消息网关")
    print(f"   {color('hermes doctor', Colors.GREEN)}       检查问题")
    print()
def _prompt_container_resources(config: dict):
    """Prompt for container resource settings (Docker, Singularity, Modal, Daytona)."""
    terminal = config.setdefault("terminal", {})

    print()
    print_info("容器资源设置:")

    # Persistence
    current_persist = terminal.get("container_persistent", True)
    persist_label = "yes" if current_persist else "no"
    print_info("  持久化文件系统会在会话间保留文件。")
    print_info("  设置为 'no' 以使用每次重置的临时沙盒。")
    persist_str = prompt(
        "  在会话间持久化文件系统？ (yes/no)", persist_label
    )
    terminal["container_persistent"] = persist_str.lower() in ("yes", "true", "y", "1")

    # CPU
    current_cpu = terminal.get("container_cpu", 1)
    cpu_str = prompt("  CPU 核心数", str(current_cpu))
    try:
        terminal["container_cpu"] = float(cpu_str)
    except ValueError:
        pass

    # Memory
    current_mem = terminal.get("container_memory", 5120)
    mem_str = prompt("  内存大小，单位 MB (5120 = 5GB)", str(current_mem))
    try:
        terminal["container_memory"] = int(mem_str)
    except ValueError:
        pass

    # Disk
    current_disk = terminal.get("container_disk", 51200)
    disk_str = prompt("  磁盘大小，单位 MB (51200 = 50GB)", str(current_disk))
    try:
        terminal["container_disk"] = int(disk_str)
    except ValueError:
        pass


def _prompt_vercel_sandbox_settings(config: dict):
    """Prompt for Vercel Sandbox settings without exposing unsupported disk sizing."""
    terminal = config.setdefault("terminal", {})

    print()
    print_info("Vercel 沙盒设置:")
    print_info("  文件系统持久化使用 Vercel 快照。")
    print_info("  快照仅恢复文件；沙盒重建后，正在运行的进程不会继续。")

    from tools.terminal_tool import _SUPPORTED_VERCEL_RUNTIMES

    current_runtime = terminal.get("vercel_runtime") or "node24"
    supported_label = ", ".join(_SUPPORTED_VERCEL_RUNTIMES)
    runtime = prompt(f"  运行时 ({supported_label})", current_runtime).strip() or current_runtime
    if runtime not in _SUPPORTED_VERCEL_RUNTIMES:
        print_warning(f"不支持的 Vercel 运行时 '{runtime}'，保持为 {current_runtime}。")
        runtime = current_runtime if current_runtime in _SUPPORTED_VERCEL_RUNTIMES else "node24"
    terminal["vercel_runtime"] = runtime
    save_env_value("TERMINAL_VERCEL_RUNTIME", runtime)

    current_persist = terminal.get("container_persistent", True)
    persist_label = "yes" if current_persist else "no"
    terminal["container_persistent"] = prompt(
        "  使用快照持久化文件系统？ (yes/no)", persist_label
    ).lower() in ("yes", "true", "y", "1")

    current_cpu = terminal.get("container_cpu", 1)
    cpu_str = prompt("  CPU 核心数", str(current_cpu))
    try:
        terminal["container_cpu"] = float(cpu_str)
    except ValueError:
        pass

    current_mem = terminal.get("container_memory", 5120)
    mem_str = prompt("  内存大小，单位 MB (5120 = 5GB)", str(current_mem))
    try:
        terminal["container_memory"] = int(mem_str)
    except ValueError:
        pass

    if terminal.get("container_disk", 51200) not in (0, 51200):
        print_warning("Vercel 沙盒不支持自定义磁盘大小；正在将 container_disk 重置为 51200。")
    terminal["container_disk"] = 51200

    print()
    print_info("Vercel 认证:")
    print_info("  使用长期有效的 Vercel 访问令牌以及项目/团队 ID。")
    linked_project = _read_nearest_vercel_project()
    if linked_project:
        print_info("  在最近的 .vercel/project.json 中找到了默认值。")

    remove_env_value("VERCEL_OIDC_TOKEN")
    token = prompt("    Vercel 访问令牌", get_env_value("VERCEL_TOKEN") or "", password=True)
    project = prompt(
        "    Vercel 项目 ID",
        get_env_value("VERCEL_PROJECT_ID") or linked_project.get("projectId", ""),
    )
    team = prompt(
        "    Vercel 团队 ID",
        get_env_value("VERCEL_TEAM_ID") or linked_project.get("orgId", ""),
    )
    if token:
        save_env_value("VERCEL_TOKEN", token)
    if project:
        save_env_value("VERCEL_PROJECT_ID", project)
    if team:
        save_env_value("VERCEL_TEAM_ID", team)
def _read_nearest_vercel_project(start: Path | None = None) -> dict[str, str]:
    """Read project/team defaults from the nearest Vercel link file."""
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        project_file = directory / ".vercel" / "project.json"
        if not project_file.exists():
            continue
        try:
            data = json.loads(project_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        return {
            key: value
            for key, value in {
                "projectId": data.get("projectId"),
                "orgId": data.get("orgId"),
            }.items()
            if isinstance(value, str) and value.strip()
        }
    return {}


# Tool categories and provider config are now in tools_config.py (shared
# between `hermes tools` and `hermes setup tools`).


# =============================================================================
# Section 1: Model & Provider Configuration
# =============================================================================



def setup_model_provider(config: dict, *, quick: bool = False):
    """Configure the inference provider and default model.

    Delegates to ``cmd_model()`` (the same flow used by ``hermes model``)
    for provider selection, credential prompting, and model picking.
    This ensures a single code path for all provider setup — any new
    provider added to ``hermes model`` is automatically available here.

    When *quick* is True, skips credential rotation, vision, and TTS
    configuration — used by the streamlined first-time quick setup.
    """
    from hermes_cli.config import load_config, save_config

    print_header("推理提供商")
    print_info("选择如何连接到您的主要聊天模型。")
    print_info(f"   指南: {_DOCS_BASE}/integrations/providers")
    print()

    # Delegate to the shared hermes model flow — handles provider picker,
    # credential prompting, model selection, and config persistence.
    from hermes_cli.main import select_provider_and_model
    try:
        select_provider_and_model()
    except (SystemExit, KeyboardInterrupt):
        print()
        print_info("提供商设置已跳过。")
    except Exception as exc:
        logger.debug("select_provider_and_model error during setup: %s", exc)
        print_warning(f"提供商设置遇到错误: {exc}")
        print_info("您可以稍后重试: hermes model")

    # Re-sync the wizard's config dict from what cmd_model saved to disk.
    # This is critical: cmd_model writes to disk via its own load/save cycle,
    # and the wizard's final save_config(config) must not overwrite those
    # changes with stale values (#4172).
    _refreshed = load_config()
    config["model"] = _refreshed.get("model", config.get("model"))
    if "custom_providers" in _refreshed:
        config["custom_providers"] = _refreshed["custom_providers"]
    else:
        config.pop("custom_providers", None)

    # Derive the selected provider for downstream steps (vision setup).
    selected_provider = None
    _m = config.get("model")
    if isinstance(_m, dict):
        selected_provider = _m.get("provider")

    # ── Same-provider fallback & rotation setup (full setup only) ──
    if not quick and _supports_same_provider_pool_setup(selected_provider):
        try:
            from types import SimpleNamespace
            from agent.credential_pool import load_pool
            from hermes_cli.auth_commands import auth_add_command

            pool = load_pool(selected_provider)
            entries = pool.entries()
            entry_count = len(entries)
            manual_count = sum(1 for entry in entries if str(getattr(entry, "source", "")).startswith("manual"))
            auto_count = entry_count - manual_count
            print()
            print_header("同提供商故障转移与轮换")
            print_info(
                "Hermes 可以为同一个提供商保存多个凭据，并在某个凭据耗尽或达到速率限制时在它们之间轮换。"
            )
            print_info(
                "这可以保留您的主要提供商，同时减少因配额问题导致的中断。"
            )
            print()
            if auto_count > 0:
                print_info(
                    f"当前为 {selected_provider} 池化的凭据: {entry_count} "
                    f"({manual_count} 手动添加, {auto_count} 从环境/共享认证自动检测)"
                )
            else:
                print_info(f"当前为 {selected_provider} 池化的凭据: {entry_count}")

            while prompt_yes_no("为同提供商故障转移添加另一个凭据?", False):
                auth_add_command(
                    SimpleNamespace(
                        provider=selected_provider,
                        auth_type="",
                        label=None,
                        api_key=None,
                        portal_url=None,
                        inference_url=None,
                        client_id=None,
                        scope=None,
                        no_browser=False,
                        timeout=15.0,
                        insecure=False,
                        ca_bundle=None,
                        min_key_ttl_seconds=5 * 60,
                    )
                )
                pool = load_pool(selected_provider)
                entry_count = len(pool.entries())
                print_info(f"提供商池现在有 {entry_count} 个凭据。")

            if entry_count > 1:
                strategy_labels = [
                    "填满优先 / 粘性 — 持续使用第一个健康的凭据直到其耗尽",
                    "轮询 — 每次选择后轮换到下一个健康的凭据",
                    "随机 — 每次随机选择一个健康的凭据",
                ]
                current_strategy = _get_credential_pool_strategies(config).get(selected_provider, "fill_first")
                default_strategy_idx = {
                    "fill_first": 0,
                    "round_robin": 1,
                    "random": 2,
                }.get(current_strategy, 0)
                strategy_idx = prompt_choice(
                    "选择同提供商轮换策略:",
                    strategy_labels,
                    default_strategy_idx,
                )
                strategy_value = ["fill_first", "round_robin", "random"][strategy_idx]
                _set_credential_pool_strategy(config, selected_provider, strategy_value)
                print_success(f"已保存 {selected_provider} 轮换策略: {strategy_value}")
        except Exception as exc:
            logger.debug("Could not configure same-provider fallback in setup: %s", exc)

    # ── Vision & Image Analysis Setup (full setup only) ──
    if quick:
        _vision_needs_setup = False
    else:
        try:
            from agent.auxiliary_client import get_available_vision_backends
            _vision_backends = set(get_available_vision_backends())
        except Exception:
            _vision_backends = set()

        _vision_needs_setup = not bool(_vision_backends)

        if selected_provider in _vision_backends:
            _vision_needs_setup = False

    if _vision_needs_setup:
        _prov_names = {
            "nous-api": "Nous Portal API key",
            "copilot": "GitHub Copilot",
            "copilot-acp": "GitHub Copilot ACP",
            "zai": "Z.AI / GLM",
            "kimi-coding": "Kimi / Moonshot",
            "kimi-coding-cn": "Kimi / Moonshot (China)",
            "stepfun": "StepFun Step Plan",
            "minimax": "MiniMax",
            "minimax-cn": "MiniMax CN",
            "anthropic": "Anthropic",
            "ai-gateway": "Vercel AI Gateway",
            "custom": "your custom endpoint",
        }
        _prov_display = _prov_names.get(selected_provider, selected_provider or "your provider")

        print()
        print_header("视觉与图像分析 (可选)")
        print_info(f"视觉使用独立的多模态后端。{_prov_display}")
        print_info("目前没有提供 Hermes 可以自动用于视觉的后端，")
        print_info("所以请现在选择一个后端，或者跳过稍后配置。")
        print()

        _vision_choices = [
            "OpenRouter — 使用 Gemini (免费层级在 openrouter.ai/keys)",
            "OpenAI 兼容端点 — 基础 URL、API 密钥和视觉模型",
            "暂时跳过",
        ]
        _vision_idx = prompt_choice("配置视觉:", _vision_choices, 2)

        if _vision_idx == 0:  # OpenRouter
            _or_key = prompt("  OpenRouter API 密钥", password=True).strip()
            if _or_key:
                save_env_value("OPENROUTER_API_KEY", _or_key)
                print_success("OpenRouter 密钥已保存 — 视觉将使用 Gemini")
            else:
                print_info("已跳过 — 视觉将不可用")
        elif _vision_idx == 1:  # OpenAI-compatible endpoint
            _base_url = prompt("  基础 URL (留空为 OpenAI)").strip() or "https://api.openai.com/v1"
            _api_key_label = "  API 密钥"
            _is_native_openai = base_url_hostname(_base_url) == "api.openai.com"
            if _is_native_openai:
                _api_key_label = "  OpenAI API 密钥"
            _oai_key = prompt(_api_key_label, password=True).strip()
            if _oai_key:
                save_env_value("OPENAI_API_KEY", _oai_key)
                # Save vision base URL to config (not .env — only secrets go there)
                _vaux = config.setdefault("auxiliary", {}).setdefault("vision", {})
                _vaux["base_url"] = _base_url
                if _is_native_openai:
                    _oai_vision_models = ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]
                    _vm_choices = _oai_vision_models + ["使用默认 (gpt-4o-mini)"]
                    _vm_idx = prompt_choice("选择视觉模型:", _vm_choices, 0)
                    _selected_vision_model = (
                        _oai_vision_models[_vm_idx]
                        if _vm_idx < len(_oai_vision_models)
                        else "gpt-4o-mini"
                    )
                else:
                    _selected_vision_model = prompt("  视觉模型 (留空 = 使用主模型/自定义默认值)").strip()
                if _selected_vision_model:
                    save_env_value("AUXILIARY_VISION_MODEL", _selected_vision_model)
                print_success(
                    f"视觉已配置，使用 {_base_url}"
                    + (f" ({_selected_vision_model})" if _selected_vision_model else "")
                )
            else:
                print_info("已跳过 — 视觉将不可用")
        else:
            print_info("已跳过 — 稍后可通过 'hermes setup' 添加或配置 AUXILIARY_VISION_* 设置")


    # Tool Gateway prompt is already shown by _model_flow_nous() above.
    save_config(config)

    if not quick and selected_provider != "nous":
        _setup_tts_provider(config)


# =============================================================================
# Section 1b: TTS Provider Configuration
# =============================================================================
def _check_espeak_ng() -> bool:
    """Check if espeak-ng is installed."""
    return shutil.which("espeak-ng") is not None or shutil.which("espeak") is not None


def _install_neutts_deps() -> bool:
    """Install NeuTTS dependencies with user approval. Returns True on success."""
    import subprocess
    import sys

    # Check espeak-ng
    if not _check_espeak_ng():
        print()
        print_warning("NeuTTS 需要 espeak-ng 进行音素化。")
        if sys.platform == "darwin":
            print_info("安装命令: brew install espeak-ng")
        elif sys.platform == "win32":
            print_info("安装命令: choco install espeak-ng")
        else:
            print_info("安装命令: sudo apt install espeak-ng")
        print()
        if prompt_yes_no("现在安装 espeak-ng 吗？", True):
            try:
                if sys.platform == "darwin":
                    subprocess.run(["brew", "install", "espeak-ng"], check=True)
                elif sys.platform == "win32":
                    subprocess.run(["choco", "install", "espeak-ng", "-y"], check=True)
                else:
                    subprocess.run(["sudo", "apt", "install", "-y", "espeak-ng"], check=True)
                print_success("espeak-ng 已安装")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print_warning(f"无法自动安装 espeak-ng: {e}")
                print_info("请手动安装后重新运行设置。")
                return False
        else:
            print_warning("NeuTTS 需要 espeak-ng。请在使用 NeuTTS 前手动安装。")

    # Install neutts Python package
    print()
    print_info("正在安装 neutts Python 包...")
    print_info("首次使用时还会下载 TTS 模型 (~300MB)。")
    print()
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "neutts[all]", "--quiet"],
            check=True, timeout=300,
        )
        print_success("neutts 安装成功")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print_error(f"安装 neutts 失败: {e}")
        print_info("尝试手动安装: python -m pip install -U neutts[all]")
        return False


def _install_kittentts_deps() -> bool:
    """Install KittenTTS dependencies with user approval. Returns True on success."""
    import subprocess
    import sys

    wheel_url = (
        "https://github.com/KittenML/KittenTTS/releases/download/"
        "0.8.1/kittentts-0.8.1-py3-none-any.whl"
    )
    print()
    print_info("正在安装 kittentts Python 包 (首次使用时会下载约 25-80MB 的模型)...")
    print()
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", wheel_url, "soundfile", "--quiet"],
            check=True, timeout=300,
        )
        print_success("kittentts 安装成功")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print_error(f"安装 kittentts 失败: {e}")
        print_info(f"尝试手动安装: python -m pip install -U '{wheel_url}' soundfile")
        return False
def _setup_tts_provider(config: dict):
    """Interactive TTS provider selection with install flow for NeuTTS."""
    tts_config = config.get("tts", {})
    current_provider = tts_config.get("provider", "edge")
    subscription_features = get_nous_subscription_features(config)

    provider_labels = {
        "edge": "Edge TTS",
        "elevenlabs": "ElevenLabs",
        "openai": "OpenAI TTS",
        "xai": "xAI TTS",
        "minimax": "MiniMax TTS",
        "mistral": "Mistral Voxtral TTS",
        "gemini": "Google Gemini TTS",
        "neutts": "NeuTTS",
        "kittentts": "KittenTTS",
    }
    current_label = provider_labels.get(current_provider, current_provider)

    print()
    print_header("文本转语音提供商（可选）")
    print_info(f"当前: {current_label}")
    print()

    choices = []
    providers = []
    if managed_nous_tools_enabled() and subscription_features.nous_auth_present:
        choices.append("Nous 订阅（托管的 OpenAI TTS，计入您的订阅账单）")
        providers.append("nous-openai")
    choices.extend(
        [
            "Edge TTS（免费，基于云端，无需设置）",
            "ElevenLabs（优质音质，需要 API 密钥）",
            "OpenAI TTS（良好音质，需要 API 密钥）",
            "xAI TTS（Grok 语音，需要 API 密钥）",
            "MiniMax TTS（高质量，支持语音克隆，需要 API 密钥）",
            "Mistral Voxtral TTS（多语言，原生 Opus 格式，需要 API 密钥）",
            "Google Gemini TTS（30 种预置语音，提示词可控，需要 API 密钥）",
            "NeuTTS（本地设备运行，免费，约 300MB 模型下载）",
            "KittenTTS（本地设备运行，免费，轻量级约 25-80MB ONNX）",
        ]
    )
    providers.extend(["edge", "elevenlabs", "openai", "xai", "minimax", "mistral", "gemini", "neutts", "kittentts"])
    choices.append(f"保持当前 ({current_label})")
    keep_current_idx = len(choices) - 1
    idx = prompt_choice("选择 TTS 提供商:", choices, keep_current_idx)

    if idx == keep_current_idx:
        return

    selected = providers[idx]
    selected_via_nous = selected == "nous-openai"
    if selected == "nous-openai":
        selected = "openai"
        print_info("OpenAI TTS 将使用托管的 Nous 消息网关并计入您的订阅账单。")
        if get_env_value("VOICE_TOOLS_OPENAI_KEY") or get_env_value("OPENAI_API_KEY"):
            print_warning(
                "直接配置的 OpenAI 凭据仍然存在，在从 ~/.hermes/.env 中移除之前可能优先使用。"
            )

    if selected == "neutts":
        # Check if already installed
        try:
            already_installed = importlib.util.find_spec("neutts") is not None
        except Exception:
            already_installed = False

        if already_installed:
            print_success("NeuTTS 已安装")
        else:
            print()
            print_info("NeuTTS 需要:")
            print_info("  • Python 包: neutts（约 50MB 安装包 + 首次使用约 300MB 模型）")
            print_info("  • 系统包: espeak-ng (phonemizer)")
            print()
            if prompt_yes_no("现在安装 NeuTTS 依赖吗？", True):
                if not _install_neutts_deps():
                    print_warning("NeuTTS 安装不完整。回退到 Edge TTS。")
                    selected = "edge"
            else:
                print_info("跳过安装。请在手动安装后将 tts.provider 设置为 'neutts'。")
                selected = "edge"

    elif selected == "elevenlabs":
        existing = get_env_value("ELEVENLABS_API_KEY")
        if not existing:
            print()
            api_key = prompt("ElevenLabs API 密钥", password=True)
            if api_key:
                save_env_value("ELEVENLABS_API_KEY", api_key)
                print_success("ElevenLabs API 密钥已保存")
            else:
                print_warning("未提供 API 密钥。回退到 Edge TTS。")
                selected = "edge"

    elif selected == "openai" and not selected_via_nous:
        existing = get_env_value("VOICE_TOOLS_OPENAI_KEY") or get_env_value("OPENAI_API_KEY")
        if not existing:
            print()
            api_key = prompt("用于 TTS 的 OpenAI API 密钥", password=True)
            if api_key:
                save_env_value("VOICE_TOOLS_OPENAI_KEY", api_key)
                print_success("OpenAI TTS API 密钥已保存")
            else:
                print_warning("未提供 API 密钥。回退到 Edge TTS。")
                selected = "edge"

    elif selected == "xai":
        existing = get_env_value("XAI_API_KEY")
        if not existing:
            print()
            api_key = prompt("用于 TTS 的 xAI API 密钥", password=True)
            if api_key:
                save_env_value("XAI_API_KEY", api_key)
                print_success("xAI TTS API 密钥已保存")
            else:
                from hermes_constants import display_hermes_home as _dhh
                print_warning(
                    "未提供用于 TTS 的 xAI API 密钥。请通过 hermes setup model 或 "
                    f"{_dhh()}/.env 配置 XAI_API_KEY 以使用 xAI TTS。"
                    "回退到 Edge TTS。"
                )
                selected = "edge"
        if selected == "xai":
            print()
            voice_id = prompt("xAI voice_id（按 Enter 使用默认 'eve'，或粘贴自定义语音 ID）")
            if voice_id and voice_id.strip():
                config.setdefault("tts", {}).setdefault("xai", {})["voice_id"] = voice_id.strip()
                print_success(f"xAI voice_id 设置为: {voice_id.strip()}")


    elif selected == "minimax":
        existing = get_env_value("MINIMAX_API_KEY")
        if not existing:
            print()
            api_key = prompt("用于 TTS 的 MiniMax API 密钥", password=True)
            if api_key:
                save_env_value("MINIMAX_API_KEY", api_key)
                print_success("MiniMax TTS API 密钥已保存")
            else:
                print_warning("未提供 API 密钥。回退到 Edge TTS。")
                selected = "edge"

    elif selected == "mistral":
        existing = get_env_value("MISTRAL_API_KEY")
        if not existing:
            print()
            api_key = prompt("用于 TTS 的 Mistral API 密钥", password=True)
            if api_key:
                save_env_value("MISTRAL_API_KEY", api_key)
                print_success("Mistral TTS API 密钥已保存")
            else:
                print_warning("未提供 API 密钥。回退到 Edge TTS。")
                selected = "edge"

    elif selected == "gemini":
        existing = get_env_value("GEMINI_API_KEY") or get_env_value("GOOGLE_API_KEY")
        if not existing:
            print()
            print_info("在 https://aistudio.google.com/app/apikey 获取免费 API 密钥")
            api_key = prompt("用于 TTS 的 Gemini API 密钥", password=True)
            if api_key:
                save_env_value("GEMINI_API_KEY", api_key)
                print_success("Gemini TTS API 密钥已保存")
            else:
                print_warning("未提供 API 密钥。回退到 Edge TTS。")
                selected = "edge"

    elif selected == "kittentts":
        # Check if already installed
        try:
            import importlib.util
            already_installed = importlib.util.find_spec("kittentts") is not None
        except Exception:
            already_installed = False

        if already_installed:
            print_success("KittenTTS 已安装")
        else:
            print()
            print_info("KittenTTS 是轻量级的（约 25-80MB，仅需 CPU，无需 API 密钥）。")
            print_info("语音: Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo")
            print()
            if prompt_yes_no("现在安装 KittenTTS 吗？", True):
                if not _install_kittentts_deps():
                    print_warning("KittenTTS 安装不完整。回退到 Edge TTS。")
                    selected = "edge"
            else:
                print_info("跳过安装。请在手动安装后将 tts.provider 设置为 'kittentts'。")
                selected = "edge"

    # Save the selection
    if "tts" not in config:
        config["tts"] = {}
    config["tts"]["provider"] = selected
    save_config(config)
    print_success(f"TTS 提供商设置为: {provider_labels.get(selected, selected)}")
def setup_tts(config: dict):
    """Standalone TTS setup (for 'hermes setup tts')."""
    _setup_tts_provider(config)


# =============================================================================
# Section 2: Terminal Backend Configuration
# =============================================================================


def setup_terminal_backend(config: dict):
    """Configure the terminal execution backend."""
    import platform as _platform
    print_header("终端执行后端")
    print_info("选择 Hermes 运行 shell 命令和代码的位置。")
    print_info("这会影响工具执行、文件访问和隔离性。")
    print_info(f"   指南: {_DOCS_BASE}/developer-guide/environments")
    print()

    current_backend = cfg_get(config, "terminal", "backend", default="local")
    is_linux = _platform.system() == "Linux"

    # Build backend choices with descriptions
    terminal_choices = [
        "本地 - 直接在此机器上运行（默认）",
        "Docker - 具有可配置资源的隔离容器",
        "Modal - 无服务器云沙盒",
        "SSH - 在远程机器上运行",
        "Daytona - 持久化云端开发环境",
        "Vercel Sandbox - 具有快照文件系统持久化的云端微虚拟机",
    ]
    idx_to_backend = {0: "local", 1: "docker", 2: "modal", 3: "ssh", 4: "daytona", 5: "vercel_sandbox"}
    backend_to_idx = {"local": 0, "docker": 1, "modal": 2, "ssh": 3, "daytona": 4, "vercel_sandbox": 5}

    next_idx = 6
    if is_linux:
        terminal_choices.append("Singularity/Apptainer - 面向 HPC 的容器")
        idx_to_backend[next_idx] = "singularity"
        backend_to_idx["singularity"] = next_idx
        next_idx += 1

    # Add keep current option
    keep_current_idx = next_idx
    terminal_choices.append(f"保持当前设置 ({current_backend})")
    idx_to_backend[keep_current_idx] = current_backend

    terminal_idx = prompt_choice(
        "选择终端执行后端:", terminal_choices, keep_current_idx
    )

    selected_backend = idx_to_backend.get(terminal_idx)

    if terminal_idx == keep_current_idx:
        print_info(f"保持当前后端: {current_backend}")
        return

    config.setdefault("terminal", {})["backend"] = selected_backend

    if selected_backend == "local":
        print_success("终端执行后端: 本地")
        print_info("命令直接在此机器上运行。")

        # Gateway/cron working directory
        print()
        print_info("消息网关工作目录:")
        print_info("  供 Telegram/Discord/定时任务会话使用。")
        print_info("  CLI/TUI 始终使用您的启动目录。")
        current_cwd = cfg_get(config, "terminal", "cwd", default="")
        cwd = prompt("  消息网关工作目录", current_cwd or str(Path.home()))
        if cwd:
            config["terminal"]["cwd"] = cwd

        # Sudo support
        print()
        existing_sudo = get_env_value("SUDO_PASSWORD")
        if existing_sudo:
            print_info("Sudo 密码: 已配置")
        else:
            if prompt_yes_no(
                "启用 sudo 支持？ (存储密码用于 apt install 等操作)", False
            ):
                sudo_pass = prompt("  Sudo 密码", password=True)
                if sudo_pass:
                    save_env_value("SUDO_PASSWORD", sudo_pass)
                    print_success("Sudo 密码已保存")

    elif selected_backend == "docker":
        print_success("终端执行后端: Docker")

        # Check if Docker is available
        docker_bin = shutil.which("docker")
        if not docker_bin:
            print_warning("在 PATH 中未找到 Docker！")
            print_info("安装 Docker: https://docs.docker.com/get-docker/")
        else:
            print_info(f"找到 Docker: {docker_bin}")

        # Docker image
        current_image = cfg_get(config, "terminal", "docker_image", default="nikolaik/python-nodejs:python3.11-nodejs20")
        image = prompt("  Docker 镜像", current_image)
        config["terminal"]["docker_image"] = image
        save_env_value("TERMINAL_DOCKER_IMAGE", image)

        _prompt_container_resources(config)

    elif selected_backend == "singularity":
        print_success("终端执行后端: Singularity/Apptainer")

        # Check if singularity/apptainer is available
        sing_bin = shutil.which("apptainer") or shutil.which("singularity")
        if not sing_bin:
            print_warning("在 PATH 中未找到 Singularity/Apptainer！")
            print_info(
                "安装: https://apptainer.org/docs/admin/main/installation.html"
            )
        else:
            print_info(f"找到: {sing_bin}")

        current_image = cfg_get(config, "terminal", "singularity_image", default="docker://nikolaik/python-nodejs:python3.11-nodejs20")
        image = prompt("  容器镜像", current_image)
        config["terminal"]["singularity_image"] = image
        save_env_value("TERMINAL_SINGULARITY_IMAGE", image)

        _prompt_container_resources(config)

    elif selected_backend == "modal":
        print_success("终端执行后端: Modal")
        print_info("无服务器云沙盒。每个会话获得自己的容器。")
        from tools.managed_tool_gateway import is_managed_tool_gateway_ready
        from tools.tool_backend_helpers import normalize_modal_mode

        managed_modal_available = bool(
            managed_nous_tools_enabled()
            and
            get_nous_subscription_features(config).nous_auth_present
            and is_managed_tool_gateway_ready("modal")
        )
        modal_mode = normalize_modal_mode(cfg_get(config, "terminal", "modal_mode"))
        use_managed_modal = False
        if managed_modal_available:
            modal_choices = [
                "使用我的 Nous 订阅",
                "使用我自己的 Modal 账户",
            ]
            if modal_mode == "managed":
                default_modal_idx = 0
            elif modal_mode == "direct":
                default_modal_idx = 1
            else:
                default_modal_idx = 1 if get_env_value("MODAL_TOKEN_ID") else 0
            modal_mode_idx = prompt_choice(
                "选择 Modal 执行应如何计费:",
                modal_choices,
                default_modal_idx,
            )
            use_managed_modal = modal_mode_idx == 0

        if use_managed_modal:
            config["terminal"]["modal_mode"] = "managed"
            print_info("Modal 执行将使用托管的 Nous 消息网关并计入您的订阅账单。")
            if get_env_value("MODAL_TOKEN_ID") or get_env_value("MODAL_TOKEN_SECRET"):
                print_info(
                    "直接 Modal 凭据仍已配置，但此后端已固定为托管模式。"
                )
        else:
            config["terminal"]["modal_mode"] = "direct"
            print_info("需要 Modal 账户: https://modal.com")

            # Check if modal SDK is installed
            try:
                __import__("modal")
            except ImportError:
                print_info("正在安装 modal SDK...")
                import subprocess

                uv_bin = shutil.which("uv")
                if uv_bin:
                    result = subprocess.run(
                        [
                            uv_bin,
                            "pip",
                            "install",
                            "--python",
                            sys.executable,
                            "modal",
                        ],
                        capture_output=True,
                        text=True,
                    )
                else:
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "modal"],
                        capture_output=True,
                        text=True,
                    )
                if result.returncode == 0:
                    print_success("modal SDK 已安装")
                else:
                    print_warning("安装失败 — 请手动运行: pip install modal")

            # Modal token
            print()
            print_info("Modal 认证:")
            print_info("  获取您的 Token: https://modal.com/settings")
            existing_token = get_env_value("MODAL_TOKEN_ID")
            if existing_token:
                print_info("  Modal Token: 已配置")
                if prompt_yes_no("  更新 Modal 凭据？", False):
                    token_id = prompt("    Modal Token ID", password=True)
                    token_secret = prompt("    Modal Token Secret", password=True)
                    if token_id:
                        save_env_value("MODAL_TOKEN_ID", token_id)
                    if token_secret:
                        save_env_value("MODAL_TOKEN_SECRET", token_secret)
            else:
                token_id = prompt("    Modal Token ID", password=True)
                token_secret = prompt("    Modal Token Secret", password=True)
                if token_id:
                    save_env_value("MODAL_TOKEN_ID", token_id)
                if token_secret:
                    save_env_value("MODAL_TOKEN_SECRET", token_secret)

        _prompt_container_resources(config)

    elif selected_backend == "daytona":
        print_success("终端执行后端: Daytona")
        print_info("持久化云端开发环境。")
        print_info("每个会话获得一个具有文件系统持久化的专用沙盒。")
        print_info("注册: https://daytona.io")

        # Check if daytona SDK is installed
        try:
            __import__("daytona")
        except ImportError:
            print_info("正在安装 daytona SDK...")
            import subprocess

            uv_bin = shutil.which("uv")
            if uv_bin:
                result = subprocess.run(
                    [uv_bin, "pip", "install", "--python", sys.executable, "daytona"],
                    capture_output=True,
                    text=True,
                )
            else:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "daytona"],
                    capture_output=True,
                    text=True,
                )
            if result.returncode == 0:
                print_success("daytona SDK 已安装")
            else:
                print_warning("安装失败 — 请手动运行: pip install daytona")
                if result.stderr:
                    print_info(f"  错误: {result.stderr.strip().splitlines()[-1]}")

        # Daytona API key
        print()
        existing_key = get_env_value("DAYTONA_API_KEY")
        if existing_key:
            print_info("  Daytona API 密钥: 已配置")
            if prompt_yes_no("  更新 API 密钥？", False):
                api_key = prompt("    Daytona API 密钥", password=True)
                if api_key:
                    save_env_value("DAYTONA_API_KEY", api_key)
                    print_success("    已更新")
        else:
            api_key = prompt("    Daytona API 密钥", password=True)
            if api_key:
                save_env_value("DAYTONA_API_KEY", api_key)
                print_success("    已配置")

        # Daytona image
        current_image = cfg_get(config, "terminal", "daytona_image", default="nikolaik/python-nodejs:python3.11-nodejs20")
        image = prompt("  沙盒镜像", current_image)
        config["terminal"]["daytona_image"] = image
        save_env_value("TERMINAL_DAYTONA_IMAGE", image)

        _prompt_container_resources(config)

    elif selected_backend == "vercel_sandbox":
        print_success("终端执行后端: Vercel Sandbox")
        print_info("具有快照支持的文件系统持久化的云端微虚拟机沙盒。")
        print_info("需要可选 SDK: pip install 'hermes-agent[vercel]'")

        try:
            __import__("vercel")
        except ImportError:
            print_info("正在安装 vercel SDK...")
            import subprocess

            uv_bin = shutil.which("uv")
            if uv_bin:
                result = subprocess.run(
                    [uv_bin, "pip", "install", "--python", sys.executable, "vercel"],
                    capture_output=True,
                    text=True,
                )
            else:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "vercel"],
                    capture_output=True,
                    text=True,
                )
            if result.returncode == 0:
                print_success("vercel SDK 已安装")
            else:
                print_warning("安装失败 — 请手动运行: pip install 'hermes-agent[vercel]'")
                if result.stderr:
                    print_info(f"  错误: {result.stderr.strip().splitlines()[-1]}")

        _prompt_vercel_sandbox_settings(config)

    elif selected_backend == "ssh":
        print_success("终端执行后端: SSH")
        print_info("通过 SSH 在远程机器上运行命令。")

        # SSH host
        current_host = get_env_value("TERMINAL_SSH_HOST") or ""
        host = prompt("  SSH 主机 (主机名或 IP)", current_host)
        if host:
            save_env_value("TERMINAL_SSH_HOST", host)

        # SSH user
        current_user = get_env_value("TERMINAL_SSH_USER") or ""
        user = prompt("  SSH 用户", current_user or os.getenv("USER", ""))
        if user:
            save_env_value("TERMINAL_SSH_USER", user)

        # SSH port
        current_port = get_env_value("TERMINAL_SSH_PORT") or "22"
        port = prompt("  SSH 端口", current_port)
        if port and port != "22":
            save_env_value("TERMINAL_SSH_PORT", port)

        # SSH key
        current_key = get_env_value("TERMINAL_SSH_KEY") or ""
        default_key = str(Path.home() / ".ssh" / "id_rsa")
        ssh_key = prompt("  SSH 私钥路径", current_key or default_key)
        if ssh_key:
            save_env_value("TERMINAL_SSH_KEY", ssh_key)

        # Test connection
        if host and prompt_yes_no("  测试 SSH 连接？", True):
            print_info("  正在测试连接...")
            import subprocess

            ssh_cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]
            if ssh_key:
                ssh_cmd.extend(["-i", ssh_key])
            if port and port != "22":
                ssh_cmd.extend(["-p", port])
            ssh_cmd.append(f"{user}@{host}" if user else host)
            ssh_cmd.append("echo ok")
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print_success("  SSH 连接成功！")
            else:
                print_warning(f"  SSH 连接失败: {result.stderr.strip()}")
                print_info("  请检查您的 SSH 密钥和主机设置。")

    # Sync terminal backend to .env so terminal_tool picks it up directly.
    # config.yaml is the source of truth, but terminal_tool reads TERMINAL_ENV.
    save_env_value("TERMINAL_ENV", selected_backend)
    if selected_backend == "modal":
        save_env_value("TERMINAL_MODAL_MODE", config["terminal"].get("modal_mode", "auto"))
    if selected_backend == "vercel_sandbox":
        save_env_value("TERMINAL_VERCEL_RUNTIME", config["terminal"].get("vercel_runtime", "node24"))
    save_config(config)
    print()
    print_success(f"终端执行后端已设置为: {selected_backend}")


# =============================================================================
# Section 3: Agent Settings
# =============================================================================
def _apply_default_agent_settings(config: dict):
    """Apply recommended defaults for all agent settings without prompting."""
    config.setdefault("agent", {})["max_turns"] = 90
    # config.yaml is the authoritative source for max_turns; the gateway
    # bridges it into HERMES_MAX_ITERATIONS at startup. We no longer write
    # to .env to avoid the dual-source inconsistency that caused the
    # 60-vs-500 bug (stale .env entry silently shadowing config.yaml).
    remove_env_value("HERMES_MAX_ITERATIONS")

    config.setdefault("display", {})["tool_progress"] = "all"

    config.setdefault("compression", {})["enabled"] = True
    config["compression"]["threshold"] = 0.50

    config.setdefault("session_reset", {}).update({
        "mode": "both",
        "idle_minutes": 1440,
        "at_hour": 4,
    })

    save_config(config)
    print_success("已应用推荐默认设置：")
    print_info("  最大迭代次数: 90")
    print_info("  工具进度: 全部")
    print_info("  压缩阈值: 0.50")
    print_info("  会话重置: 闲置 (1440 分钟) + 每日 (4:00)")
    print_info("  稍后运行 `hermes setup agent` 进行自定义。")


def setup_agent_settings(config: dict):
    """Configure agent behavior: iterations, progress display, compression, session reset."""

    print_header("Agent 设置")
    print_info(f"   指南: {_DOCS_BASE}/user-guide/configuration")
    print()

    # ── 最大迭代次数 ──
    # config.yaml 是权威来源；从那里读取。如果遗留的 .env
    # 条目仍然存在（来自 PR#18413 之前的设置），优先使用
    # config 值，这样我们就不会向用户显示过时的数字。
    current_max = str(cfg_get(config, "agent", "max_turns", default=90))
    print_info("每次对话的最大工具调用迭代次数。")
    print_info("越高 = 任务越复杂，但消耗更多 Token。")
    print_info(
        f"按 Enter 键保持 {current_max}。大多数任务使用 90，开放式探索使用 150+。"
    )

    max_iter_str = prompt("最大迭代次数", current_max)
    try:
        max_iter = int(max_iter_str)
        if max_iter > 0:
            # 仅写入 config.yaml（权威来源）。同时清理任何
            # 来自早期设置运行的过时 .env 条目 —— 消息网关的
            # 桥接现在在 gateway/run.py 中无条件地从 agent.max_turns 派生
            # HERMES_MAX_ITERATIONS 并在启动时设置。
            config.setdefault("agent", {})["max_turns"] = max_iter
            config.pop("max_turns", None)
            remove_env_value("HERMES_MAX_ITERATIONS")
            print_success(f"最大迭代次数设置为 {max_iter}")
    except ValueError:
        print_warning("无效数字，保持当前值")

    # ── 工具进度显示 ──
    print_info("")
    print_info("工具进度显示")
    print_info("控制显示多少工具活动（CLI 和消息传递）。")
    print_info("  off     — 静默，仅显示最终响应")
    print_info("  new     — 仅当工具名称更改时显示（减少噪音）")
    print_info("  all     — 显示每个工具调用并附带简短预览")
    print_info("  verbose — 完整参数、结果和调试日志")

    current_mode = cfg_get(config, "display", "tool_progress", default="all")
    mode = prompt("工具进度模式", current_mode)
    if mode.lower() in ("off", "new", "all", "verbose"):
        if "display" not in config:
            config["display"] = {}
        config["display"]["tool_progress"] = mode.lower()
        save_config(config)
        print_success(f"工具进度设置为: {mode.lower()}")
    else:
        print_warning(f"未知模式 '{mode}'，保持 '{current_mode}'")

    # ── 上下文压缩 ──
    print_header("上下文压缩")
    print_info("当上下文过长时自动总结旧消息。")
    print_info(
        "阈值越高 = 压缩越晚（使用更多上下文）。越低 = 压缩越早。"
    )

    config.setdefault("compression", {})["enabled"] = True

    current_threshold = cfg_get(config, "compression", "threshold", default=0.50)
    threshold_str = prompt("压缩阈值 (0.5-0.95)", str(current_threshold))
    try:
        threshold = float(threshold_str)
        if 0.5 <= threshold <= 0.95:
            config["compression"]["threshold"] = threshold
    except ValueError:
        pass

    print_success(
        f"上下文压缩阈值设置为 {config['compression'].get('threshold', 0.50)}"
    )

    # ── 会话重置策略 ──
    print_header("会话重置策略")
    print_info(
        "消息传递会话（Telegram、Discord 等）会随时间累积上下文。"
    )
    print_info(
        "每条消息都会添加到对话历史记录中，这意味着 API 成本会增长。"
    )
    print_info("")
    print_info(
        "为了管理这一点，会话可以在闲置一段时间后自动重置"
    )
    print_info(
        "或在每天固定时间重置。当重置发生时，Agent 会先将重要内容"
    )
    print_info(
        "保存到其持久记忆 —— 但对话上下文会被清除。"
    )
    print_info("")
    print_info("您也可以随时在聊天中输入 /reset 手动重置。")
    print_info("")

    reset_choices = [
        "闲置 + 每日重置（推荐 - 重置先到者）",
        "仅闲置（在 N 分钟无消息后重置）",
        "仅每日（每天固定小时重置）",
        "永不自动重置（上下文持续存在直到 /reset 或上下文压缩）",
        "保持当前设置",
    ]

    current_policy = config.get("session_reset", {})
    current_mode = current_policy.get("mode", "both")
    current_idle = current_policy.get("idle_minutes", 1440)
    current_hour = current_policy.get("at_hour", 4)

    default_reset = {"both": 0, "idle": 1, "daily": 2, "none": 3}.get(current_mode, 0)

    reset_idx = prompt_choice("会话重置模式:", reset_choices, default_reset)

    config.setdefault("session_reset", {})

    if reset_idx == 0:  # Both
        config["session_reset"]["mode"] = "both"
        idle_str = prompt("  闲置超时（分钟）", str(current_idle))
        try:
            idle_val = int(idle_str)
            if idle_val > 0:
                config["session_reset"]["idle_minutes"] = idle_val
        except ValueError:
            pass
        hour_str = prompt("  每日重置小时（0-23，本地时间）", str(current_hour))
        try:
            hour_val = int(hour_str)
            if 0 <= hour_val <= 23:
                config["session_reset"]["at_hour"] = hour_val
        except ValueError:
            pass
        print_success(
            f"会话在闲置 {config['session_reset'].get('idle_minutes', 1440)} 分钟后或每日 {config['session_reset'].get('at_hour', 4)}:00 重置"
        )
    elif reset_idx == 1:  # Idle only
        config["session_reset"]["mode"] = "idle"
        idle_str = prompt("  闲置超时（分钟）", str(current_idle))
        try:
            idle_val = int(idle_str)
            if idle_val > 0:
                config["session_reset"]["idle_minutes"] = idle_val
        except ValueError:
            pass
        print_success(
            f"会话在闲置 {config['session_reset'].get('idle_minutes', 1440)} 分钟后重置"
        )
    elif reset_idx == 2:  # Daily only
        config["session_reset"]["mode"] = "daily"
        hour_str = prompt("  每日重置小时（0-23，本地时间）", str(current_hour))
        try:
            hour_val = int(hour_str)
            if 0 <= hour_val <= 23:
                config["session_reset"]["at_hour"] = hour_val
        except ValueError:
            pass
        print_success(
            f"会话每日在 {config['session_reset'].get('at_hour', 4)}:00 重置"
        )
    elif reset_idx == 3:  # None
        config["session_reset"]["mode"] = "none"
        print_info(
            "会话将永不自动重置。上下文仅由压缩管理。"
        )
        print_warning(
            "长对话的成本会增长。需要时请手动使用 /reset。"
        )
    # else: keep current (idx == 4)

    save_config(config)


# =============================================================================
# Section 4: Messaging Platforms (Gateway)
# =============================================================================
def _setup_telegram():
    """Configure Telegram bot credentials and allowlist."""
    print_header("Telegram")
    existing = get_env_value("TELEGRAM_BOT_TOKEN")
    if existing:
        print_info("Telegram: 已配置")
        if not prompt_yes_no("重新配置 Telegram?", False):
            # Check missing allowlist on existing config
            if not get_env_value("TELEGRAM_ALLOWED_USERS"):
                print_info("⚠️  Telegram 未设置用户白名单 - 任何人都可以使用你的机器人!")
                if prompt_yes_no("现在添加允许的用户?", True):
                    print_info("   要查找你的 Telegram 用户 ID: 给 @userinfobot 发消息")
                    allowed_users = prompt("允许的用户 ID (逗号分隔)")
                    if allowed_users:
                        save_env_value("TELEGRAM_ALLOWED_USERS", allowed_users.replace(" ", ""))
                        print_success("Telegram 白名单已配置")
            return

    print_info("通过 Telegram 上的 @BotFather 创建一个机器人")
    import re

    while True:
        token = prompt("Telegram 机器人令牌", password=True)
        if not token:
            return
        if not re.match(r"^\d+:[A-Za-z0-9_-]{30,}$", token):
            print_error(
                "令牌格式无效。应为: <数字ID>:<字母数字哈希> "
                "(例如: 123456789:ABCdefGHI-jklMNOpqrSTUvwxYZ)"
            )
            continue
        break
    save_env_value("TELEGRAM_BOT_TOKEN", token)
    print_success("Telegram 令牌已保存")

    print()
    print_info("🔒 安全: 限制谁可以使用你的机器人")
    print_info("   要查找你的 Telegram 用户 ID:")
    print_info("   1. 在 Telegram 上给 @userinfobot 发消息")
    print_info("   2. 它会回复你的数字 ID (例如: 123456789)")
    print()
    allowed_users = prompt(
        "允许的用户 ID (逗号分隔，留空表示开放访问)"
    )
    if allowed_users:
        save_env_value("TELEGRAM_ALLOWED_USERS", allowed_users.replace(" ", ""))
        print_success("Telegram 白名单已配置 - 只有列出的用户可以使用机器人")
    else:
        print_info("⚠️  未设置白名单 - 任何发现你机器的人都可以使用它!")

    print()
    print_info("📬 主频道: Hermes 在此发送定时任务结果、")
    print_info("   跨平台消息和通知。")
    print_info("   对于 Telegram 私聊，这是你的用户 ID (与上面相同)。")

    first_user_id = allowed_users.split(",")[0].strip() if allowed_users else ""
    if first_user_id:
        if prompt_yes_no(f"使用你的用户 ID ({first_user_id}) 作为主频道?", True):
            save_env_value("TELEGRAM_HOME_CHANNEL", first_user_id)
            print_success(f"Telegram 主频道已设置为 {first_user_id}")
        else:
            home_channel = prompt("主频道 ID (或留空稍后在 Telegram 中使用 /set-home 设置)")
            if home_channel:
                save_env_value("TELEGRAM_HOME_CHANNEL", home_channel)
    else:
        print_info("   你也可以稍后在 Telegram 聊天中输入 /set-home 来设置。")
        home_channel = prompt("主频道 ID (留空稍后设置)")
        if home_channel:
            save_env_value("TELEGRAM_HOME_CHANNEL", home_channel)
def _setup_discord():
    """Configure Discord bot credentials and allowlist."""
    print_header("Discord")
    existing = get_env_value("DISCORD_BOT_TOKEN")
    if existing:
        print_info("Discord: 已配置")
        if not prompt_yes_no("重新配置 Discord?", False):
            if not get_env_value("DISCORD_ALLOWED_USERS"):
                print_info("⚠️  Discord 未设置用户白名单 - 任何人都可以使用你的机器人!")
                if prompt_yes_no("现在添加允许的用户?", True):
                    print_info("   查找 Discord ID: 启用开发者模式，右键点击用户名 → 复制 ID")
                    allowed_users = prompt("允许的用户 ID (逗号分隔)")
                    if allowed_users:
                        cleaned_ids = _clean_discord_user_ids(allowed_users)
                        save_env_value("DISCORD_ALLOWED_USERS", ",".join(cleaned_ids))
                        print_success("Discord 白名单已配置")
            return

    print_info("在 https://discord.com/developers/applications 创建一个机器人")
    token = prompt("Discord 机器人令牌", password=True)
    if not token:
        return
    save_env_value("DISCORD_BOT_TOKEN", token)
    print_success("Discord 令牌已保存")

    print()
    print_info("🔒 安全: 限制谁可以使用你的机器人")
    print_info("   查找你的 Discord 用户 ID:")
    print_info("   1. 在 Discord 设置中启用开发者模式")
    print_info("   2. 右键点击你的用户名 → 复制 ID")
    print()
    print_info("   你也可以使用 Discord 用户名 (在消息网关启动时解析)。")
    print()
    allowed_users = prompt(
        "允许的用户 ID 或用户名 (逗号分隔，留空表示开放访问)"
    )
    if allowed_users:
        cleaned_ids = _clean_discord_user_ids(allowed_users)
        save_env_value("DISCORD_ALLOWED_USERS", ",".join(cleaned_ids))
        print_success("Discord 白名单已配置")
    else:
        print_info("⚠️  未设置白名单 - 你机器人所在服务器中的任何人都可以使用它!")

    print()
    print_info("📬 主频道: Hermes 在此发送定时任务结果、")
    print_info("   跨平台消息和通知。")
    print_info("   获取频道 ID: 右键点击一个频道 → 复制频道 ID")
    print_info("   (需要在 Discord 设置中启用开发者模式)")
    print_info("   你也可以稍后在 Discord 频道中输入 /set-home 来设置。")
    home_channel = prompt("主频道 ID (留空稍后通过 /set-home 设置)")
    if home_channel:
        save_env_value("DISCORD_HOME_CHANNEL", home_channel)


def _clean_discord_user_ids(raw: str) -> list:
    """Strip common Discord mention prefixes from a comma-separated ID string."""
    cleaned = []
    for uid in raw.replace(" ", "").split(","):
        uid = uid.strip()
        if uid.startswith("<@") and uid.endswith(">"):
            uid = uid.lstrip("<@!").rstrip(">")
        if uid.lower().startswith("user:"):
            uid = uid[5:]
        if uid:
            cleaned.append(uid)
    return cleaned
def _setup_slack():
    """Configure Slack bot credentials."""
    print_header("Slack")
    existing = get_env_value("SLACK_BOT_TOKEN")
    if existing:
        print_info("Slack: 已配置")
        if not prompt_yes_no("重新配置 Slack?", False):
            # Even without reconfiguring, offer to refresh the manifest so
            # new commands (e.g. /btw, /stop, ...) get registered in Slack.
            if prompt_yes_no(
                "使用最新的命令列表重新生成 Slack 应用清单? (推荐在 `hermes update` 后执行)",
                True,
            ):
                _write_slack_manifest_and_instruct()
            return

    print_info("创建 Slack 应用的步骤:")
    print_info("   1. 访问 https://api.slack.com/apps → 创建新应用")
    print_info("      选择 'From an app manifest' — 我们将在下面为你生成一个。")
    print_info("   2. 启用 Socket 模式: 设置 → Socket 模式 → 启用")
    print_info("      • 创建一个具有 'connections:write' 权限的应用级 Token")
    print_info("   3. 安装到工作区: 设置 → 安装应用")
    print_info("   4. 安装后，邀请机器人到频道: /invite @YourBot")
    print()
    print_info("   完整指南: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/slack/")
    print()

    # Generate and write manifest up-front so the user can paste it into
    # the "Create from manifest" flow instead of clicking through scopes /
    # events / slash commands one at a time.
    _write_slack_manifest_and_instruct()

    print()
    bot_token = prompt("Slack Bot Token (xoxb-...)", password=True)
    if not bot_token:
        return
    save_env_value("SLACK_BOT_TOKEN", bot_token)
    app_token = prompt("Slack App Token (xapp-...)", password=True)
    if app_token:
        save_env_value("SLACK_APP_TOKEN", app_token)
    print_success("Slack Token 已保存")

    print()
    print_info("🔒 安全: 限制谁可以使用你的机器人")
    print_info("   查找成员 ID: 点击用户名 → 查看完整资料 → ⋮ → 复制成员 ID")
    print()
    allowed_users = prompt(
        "允许的用户 ID (逗号分隔，留空则拒绝所有未配对的用户)"
    )
    if allowed_users:
        save_env_value("SLACK_ALLOWED_USERS", allowed_users.replace(" ", ""))
        print_success("Slack 允许名单已配置")
    else:
        print_warning("⚠️  未设置 Slack 允许名单 - 默认将拒绝未配对的用户。")
        print_info("   仅当你确实希望开放工作区访问时，才设置 SLACK_ALLOW_ALL_USERS=true 或 GATEWAY_ALLOW_ALL_USERS=true。")

    print()
    print_info("📬 主频道: Hermes 在此发送定时任务结果、")
    print_info("   跨平台消息和通知。")
    print_info("   获取频道 ID: 在 Slack 中打开频道，然后右键点击")
    print_info("   频道名称 → 复制链接 — ID 以 C 开头 (例如 C01ABC2DE3F)。")
    print_info("   你也可以稍后在 Slack 频道中输入 /set-home 来设置。")
    home_channel = prompt("主频道 ID (留空则稍后使用 /set-home 设置)")
    if home_channel:
        save_env_value("SLACK_HOME_CHANNEL", home_channel.strip())
def _write_slack_manifest_and_instruct():
    """Generate the Slack manifest, write it under HERMES_HOME, and print
    paste-into-Slack instructions.

    Exposed as its own helper so both the initial setup flow and the
    "reconfigure? → no" branch can refresh the manifest without the user
    re-entering tokens. Failures are non-fatal — if the manifest write
    fails for any reason, we print a warning and skip rather than abort
    the whole Slack setup.
    """
    try:
        from hermes_cli.slack_cli import _build_full_manifest
        from hermes_constants import get_hermes_home

        manifest = _build_full_manifest(
            bot_name="Hermes",
            bot_description="您的 Hermes Agent 在 Slack 上",
        )
        target = Path(get_hermes_home()) / "slack-manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        import json as _json
        target.write_text(
            _json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print_success(f"Slack 应用清单已写入: {target}")
        print_info(
            "   将其粘贴到 https://api.slack.com/apps → 您的应用 → 功能 "
            "→ 应用清单 → 编辑，然后保存。如果权限范围或斜杠命令有更改，Slack 会提示 "
            "重新安装。"
        )
        print_info(
            "   在 Hermes 添加新命令后，随时可以重新运行 `hermes slack manifest --write` 来刷新。"
        )
    except Exception as exc:  # pragma: no cover - best-effort UX helper
        print_warning(f"无法写入 Slack 清单: {exc}")
        print_info(
            "   您稍后可以手动生成它，使用命令: "
            "hermes slack manifest --write"
        )


def _setup_matrix():
    """配置 Matrix 凭据。"""
    print_header("Matrix")
    existing = get_env_value("MATRIX_ACCESS_TOKEN") or get_env_value("MATRIX_PASSWORD")
    if existing:
        print_info("Matrix: 已配置")
        if not prompt_yes_no("重新配置 Matrix?", False):
            return

    print_info("适用于任何 Matrix 家庭服务器 (Synapse, Conduit, Dendrite, 或 matrix.org)。")
    print_info("   1. 在您的家庭服务器上创建一个机器人用户，或使用您自己的账户")
    print_info("   2. 从 Element 获取访问令牌，或提供用户 ID + 密码")
    print()
    homeserver = prompt("家庭服务器 URL (例如 https://matrix.example.org)")
    if homeserver:
        save_env_value("MATRIX_HOMESERVER", homeserver.rstrip("/"))

    print()
    print_info("认证: 提供访问令牌 (推荐)，或用户 ID + 密码。")
    token = prompt("访问令牌 (留空则使用密码登录)", password=True)
    if token:
        save_env_value("MATRIX_ACCESS_TOKEN", token)
        user_id = prompt("用户 ID (@bot:server — 可选，将自动检测)")
        if user_id:
            save_env_value("MATRIX_USER_ID", user_id)
        print_success("Matrix 访问令牌已保存")
    else:
        user_id = prompt("用户 ID (@bot:server)")
        if user_id:
            save_env_value("MATRIX_USER_ID", user_id)
        password = prompt("密码", password=True)
        if password:
            save_env_value("MATRIX_PASSWORD", password)
            print_success("Matrix 凭据已保存")

    if token or get_env_value("MATRIX_PASSWORD"):
        print()
        want_e2ee = prompt_yes_no("启用端到端加密 (E2EE)?", False)
        if want_e2ee:
            save_env_value("MATRIX_ENCRYPTION", "true")
            print_success("E2EE 已启用")

        matrix_pkg = "mautrix[encryption]" if want_e2ee else "mautrix"
        try:
            __import__("mautrix")
        except ImportError:
            print_info(f"正在安装 {matrix_pkg}...")
            import subprocess
            uv_bin = shutil.which("uv")
            if uv_bin:
                result = subprocess.run(
                    [uv_bin, "pip", "install", "--python", sys.executable, matrix_pkg],
                    capture_output=True, text=True,
                )
            else:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", matrix_pkg],
                    capture_output=True, text=True,
                )
            if result.returncode == 0:
                print_success(f"{matrix_pkg} 已安装")
            else:
                print_warning(f"安装失败 — 请手动运行: pip install '{matrix_pkg}'")
                if result.stderr:
                    print_info(f"  错误: {result.stderr.strip().splitlines()[-1]}")

        print()
        print_info("🔒 安全: 限制谁可以使用您的机器人")
        print_info("   Matrix 用户 ID 格式为 @username:server")
        print()
        allowed_users = prompt("允许的用户 ID (逗号分隔，留空则开放访问)")
        if allowed_users:
            save_env_value("MATRIX_ALLOWED_USERS", allowed_users.replace(" ", ""))
            print_success("Matrix 允许列表已配置")
        else:
            print_info("⚠️  未设置允许列表 - 任何可以向机器人发送消息的人都可以使用它!")

        print()
        print_info("📬 主房间: Hermes 在此发送定时任务结果和通知。")
        print_info("   房间 ID 格式为 !abc123:server (在 Element 房间设置中显示)")
        print_info("   您也可以稍后在 Matrix 房间中输入 /set-home 来设置。")
        home_room = prompt("主房间 ID (留空则稍后使用 /set-home 设置)")
        if home_room:
            save_env_value("MATRIX_HOME_ROOM", home_room)
def _setup_mattermost():
    """Configure Mattermost bot credentials."""
    print_header("Mattermost")
    existing = get_env_value("MATTERMOST_TOKEN")
    if existing:
        print_info("Mattermost: 已配置")
        if not prompt_yes_no("重新配置 Mattermost?", False):
            return

    print_info("适用于任何自托管的 Mattermost 实例。")
    print_info("   1. 在 Mattermost 中: 集成 → Bot 账户 → 添加 Bot 账户")
    print_info("   2. 复制 bot token")
    print()
    mm_url = prompt("Mattermost 服务器 URL (例如 https://mm.example.com)")
    if mm_url:
        save_env_value("MATTERMOST_URL", mm_url.rstrip("/"))
    token = prompt("Bot token", password=True)
    if not token:
        return
    save_env_value("MATTERMOST_TOKEN", token)
    print_success("Mattermost token 已保存")

    print()
    print_info("🔒 安全: 限制谁可以使用你的 bot")
    print_info("   要查找你的用户 ID: 点击你的头像 → 个人资料")
    print_info("   或使用 API: GET /api/v4/users/me")
    print()
    allowed_users = prompt("允许的用户 ID (逗号分隔，留空表示开放访问)")
    if allowed_users:
        save_env_value("MATTERMOST_ALLOWED_USERS", allowed_users.replace(" ", ""))
        print_success("Mattermost 允许名单已配置")
    else:
        print_info("⚠️  未设置允许名单 - 任何可以给 bot 发消息的人都可以使用它!")

    print()
    print_info("📬 主频道: Hermes 在此发送定时任务结果和通知。")
    print_info("   要获取频道 ID: 点击频道名称 → 查看信息 → 复制 ID")
    print_info("   你也可以稍后在 Mattermost 频道中输入 /set-home 来设置。")
    home_channel = prompt("主频道 ID (留空稍后通过 /set-home 设置)")
    if home_channel:
        save_env_value("MATTERMOST_HOME_CHANNEL", home_channel)
    print_info("   在编辑器中打开配置:  hermes config edit")


def _setup_bluebubbles():
    """Configure BlueBubbles iMessage gateway."""
    print_header("BlueBubbles (iMessage)")
    existing = get_env_value("BLUEBUBBLES_SERVER_URL")
    if existing:
        print_info("BlueBubbles: 已配置")
        if not prompt_yes_no("重新配置 BlueBubbles?", False):
            return

    print_info("通过 BlueBubbles 将 Hermes 连接到 iMessage — 一个免费、开源的")
    print_info("macOS 服务器，可将 iMessage 桥接到任何设备。")
    print_info("   需要一台运行 BlueBubbles Server v1.0.0+ 的 Mac")
    print_info("   下载: https://bluebubbles.app/")
    print()
    print_info("在 BlueBubbles Server → 设置 → API 中，记下你的服务器 URL 和密码。")
    print()

    server_url = prompt("BlueBubbles 服务器 URL (例如 http://192.168.1.10:1234)")
    if not server_url:
        print_warning("服务器 URL 是必需的 — 跳过 BlueBubbles 设置")
        return
    save_env_value("BLUEBUBBLES_SERVER_URL", server_url.rstrip("/"))

    password = prompt("BlueBubbles 服务器密码", password=True)
    if not password:
        print_warning("密码是必需的 — 跳过 BlueBubbles 设置")
        return
    save_env_value("BLUEBUBBLES_PASSWORD", password)
    print_success("BlueBubbles 凭据已保存")

    print()
    print_info("🔒 安全: 限制谁可以给你的 bot 发消息")
    print_info("   使用 iMessage 地址: 邮箱 (user@icloud.com) 或电话 (+15551234567)")
    print()
    allowed_users = prompt("允许的 iMessage 地址 (逗号分隔，留空表示开放访问)")
    if allowed_users:
        save_env_value("BLUEBUBBLES_ALLOWED_USERS", allowed_users.replace(" ", ""))
        print_success("BlueBubbles 允许名单已配置")
    else:
        print_info("⚠️  未设置允许名单 — 任何可以给你发 iMessage 的人都可以使用这个 bot!")

    print()
    print_info("📬 主频道: 用于定时任务投递和通知的电话或邮箱地址。")
    print_info("   你也可以稍后在 iMessage 聊天中使用 /set-home 来设置。")
    home_channel = prompt("主频道地址 (留空稍后设置)")
    if home_channel:
        save_env_value("BLUEBUBBLES_HOME_CHANNEL", home_channel)

    print()
    print_info("高级设置 (默认值适用于大多数配置):")
    if prompt_yes_no("配置 webhook 监听器设置?", False):
        webhook_port = prompt("Webhook 监听器端口 (默认: 8645)")
        if webhook_port:
            try:
                save_env_value("BLUEBUBBLES_WEBHOOK_PORT", str(int(webhook_port)))
                print_success(f"Webhook 端口设置为 {webhook_port}")
            except ValueError:
                print_warning("无效的端口号，使用默认值 8645")

    print()
    print_info("需要 BlueBubbles 私有 API 助手来实现输入指示器、")
    print_info("已读回执和轻点反应。基本消息功能无需此助手。")
    print_info("   安装: https://docs.bluebubbles.app/helper-bundle/installation")
def _setup_qqbot():
    """Configure QQ Bot (Official API v2) via gateway setup."""
    from hermes_cli.gateway import _setup_qqbot as _gateway_setup_qqbot
    _gateway_setup_qqbot()


def _setup_webhooks():
    """Configure webhook integration."""
    print_header("Webhooks")
    existing = get_env_value("WEBHOOK_ENABLED")
    if existing:
        print_info("Webhooks: already configured")
        if not prompt_yes_no("重新配置 Webhooks？", False):
            return

    print()
    print_warning("⚠  Webhook 和 SMS 平台需要将消息网关端口暴露到公网。")
    print_warning("   出于安全考虑，请在沙盒环境（Docker、虚拟机等）中运行消息网关，")
    print_warning("   以限制提示词注入攻击的爆炸半径。")
    print()
    print_info("   完整指南: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks/")
    print()

    port = prompt("Webhook 端口（默认 8644）")
    if port:
        try:
            save_env_value("WEBHOOK_PORT", str(int(port)))
            print_success(f"Webhook 端口已设置为 {port}")
        except ValueError:
            print_warning("端口号无效，使用默认值 8644")

    secret = prompt("全局 HMAC 密钥（在所有路由间共享）", password=True)
    if secret:
        save_env_value("WEBHOOK_SECRET", secret)
        print_success("Webhook 密钥已保存")
    else:
        print_warning("未设置密钥 — 您必须在 config.yaml 中配置每个路由的密钥")

    save_env_value("WEBHOOK_ENABLED", "true")
    print()
    print_success("Webhooks 已启用！后续步骤：")
    from hermes_constants import display_hermes_home as _dhh
    print_info(f"   1. 在 {_dhh()}/config.yaml 中定义 Webhook 路由")
    print_info("   2. 将您的服务（GitHub、GitLab 等）指向：")
    print_info("      http://your-server:8644/webhooks/<route-name>")
    print()
    print_info("   路由配置指南：")
    print_info("   https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks/#configuring-routes")
    print()
    print_info("   在编辑器中打开配置:  hermes config edit")
    print_info("   在编辑器中打开配置:  hermes config edit")


def setup_gateway(config: dict):
    """Configure messaging platform integrations."""
    from hermes_cli.gateway import _all_platforms, _platform_status, _configure_platform

    print_header("消息平台")
    print_info("连接到消息平台，以便随时随地与 Hermes 聊天。")
    print_info("使用空格键切换选择，按回车键确认。")
    print()

    platforms = _all_platforms()

    # Build checklist, pre-selecting already-configured platforms.
    items = []
    pre_selected = []
    for i, plat in enumerate(platforms):
        status = _platform_status(plat)
        items.append(f"{plat['emoji']} {plat['label']}  ({status})")
        if status == "configured":
            pre_selected.append(i)

    selected = prompt_checklist("选择要配置的平台：", items, pre_selected)

    if not selected:
        print_info("未选择任何平台。稍后运行 'hermes setup gateway' 进行配置。")
        return

    for idx in selected:
        _configure_platform(platforms[idx])

    # ── Gateway Service Setup ──
    # Count any platform (built-in or plugin) the user configured during this
    # setup pass — reuses ``_platform_status`` so plugin platforms like IRC
    # are picked up without another hard-coded env-var list.
    def _is_progress(status: str) -> bool:
        s = status.lower()
        return not (
            s == "not configured"
            or s.startswith("partially")
            or s.startswith("plugin disabled")
        )

    any_messaging = any(
        _is_progress(_platform_status(p)) for p in _all_platforms()
    )
    if any_messaging:
        print()
        print_info("━" * 50)
        print_success("消息平台已配置！")

        # Check if any home channels are missing
        missing_home = []
        if get_env_value("TELEGRAM_BOT_TOKEN") and not get_env_value(
            "TELEGRAM_HOME_CHANNEL"
        ):
            missing_home.append("Telegram")
        if get_env_value("DISCORD_BOT_TOKEN") and not get_env_value(
            "DISCORD_HOME_CHANNEL"
        ):
            missing_home.append("Discord")
        if get_env_value("SLACK_BOT_TOKEN") and not get_env_value("SLACK_HOME_CHANNEL"):
            missing_home.append("Slack")
        if get_env_value("BLUEBUBBLES_SERVER_URL") and not get_env_value("BLUEBUBBLES_HOME_CHANNEL"):
            missing_home.append("BlueBubbles")
        if get_env_value("QQ_APP_ID") and not (
            get_env_value("QQBOT_HOME_CHANNEL") or get_env_value("QQ_HOME_CHANNEL")
        ):
            missing_home.append("QQBot")

        if missing_home:
            print()
            print_warning(f"未设置主频道：{', '.join(missing_home)}")
            print_info("   没有主频道，定时任务和跨平台消息将无法发送到这些平台。")
            print_info("   稍后可以在聊天中使用 /set-home 设置，或使用：")
            for plat in missing_home:
                print_info(
                    f"     hermes config set {plat.upper()}_HOME_CHANNEL <channel_id>"
                )

        # Offer to install the gateway as a system service
        import platform as _platform

        _is_linux = _platform.system() == "Linux"
        _is_macos = _platform.system() == "Darwin"

        from hermes_cli.gateway import (
            _is_service_installed,
            _is_service_running,
            supports_systemd_services,
            has_conflicting_systemd_units,
            has_legacy_hermes_units,
            install_linux_gateway_from_setup,
            print_systemd_scope_conflict_warning,
            print_legacy_unit_warning,
            systemd_start,
            systemd_restart,
            launchd_install,
            launchd_start,
            launchd_restart,
            UserSystemdUnavailableError,
        )

        service_installed = _is_service_installed()
        service_running = _is_service_running()
        supports_systemd = supports_systemd_services()
        supports_service_manager = supports_systemd or _is_macos

        print()
        if supports_systemd and has_conflicting_systemd_units():
            print_systemd_scope_conflict_warning()
            print()

        if supports_systemd and has_legacy_hermes_units():
            print_legacy_unit_warning()
            print()

        if service_running:
            if prompt_yes_no("  重启消息网关以应用更改？", True):
                try:
                    if supports_systemd:
                        systemd_restart()
                    elif _is_macos:
                        launchd_restart()
                except UserSystemdUnavailableError as e:
                    print_error("  重启失败 — 用户 systemd 不可访问：")
                    for line in str(e).splitlines():
                        print(f"  {line}")
                except Exception as e:
                    print_error(f"  重启失败: {e}")
        elif service_installed:
            if prompt_yes_no("  启动消息网关服务？", True):
                try:
                    if supports_systemd:
                        systemd_start()
                    elif _is_macos:
                        launchd_start()
                except UserSystemdUnavailableError as e:
                    print_error("  启动失败 — 用户 systemd 不可访问：")
                    for line in str(e).splitlines():
                        print(f"  {line}")
                except Exception as e:
                    print_error(f"  启动失败: {e}")
        elif supports_service_manager:
            svc_name = "systemd" if supports_systemd else "launchd"
            if prompt_yes_no(
                f"  将消息网关安装为 {svc_name} 服务？（在后台运行，开机自启）",
                True,
            ):
                try:
                    installed_scope = None
                    did_install = False
                    if supports_systemd:
                        installed_scope, did_install = install_linux_gateway_from_setup(force=False)
                    else:
                        launchd_install(force=False)
                        did_install = True
                    print()
                    if did_install and prompt_yes_no("  现在启动服务？", True):
                        try:
                            if supports_systemd:
                                systemd_start(system=installed_scope == "system")
                            elif _is_macos:
                                launchd_start()
                        except UserSystemdUnavailableError as e:
                            print_error("  启动失败 — 用户 systemd 不可访问：")
                            for line in str(e).splitlines():
                                print(f"  {line}")
                        except Exception as e:
                            print_error(f"  启动失败: {e}")
                except Exception as e:
                    print_error(f"  安装失败: {e}")
                    print_info("  您可以尝试手动安装: hermes gateway install")
            else:
                print_info("  您可以稍后安装: hermes gateway install")
                if supports_systemd:
                    print_info("  或作为开机自启服务: sudo hermes gateway install --system")
                print_info("  或在前台运行:  hermes gateway")
        else:
            from hermes_constants import is_container
            if is_container():
                print_info("启动消息网关以使您的机器人上线：")
                print_info("   hermes gateway run          # 作为容器主进程运行")
                print_info("")
                print_info("要实现自动重启，请使用 Docker 重启策略：")
                print_info("   docker run --restart unless-stopped ...")
                print_info("   docker restart <container>  # 手动重启")
            else:
                print_info("启动消息网关以使您的机器人上线：")
                print_info("   hermes gateway              # 在前台运行")

        print_info("━" * 50)


# =============================================================================
# Section 5: Tool Configuration (delegates to unified tools_config.py)
# =============================================================================
def setup_tools(config: dict, first_install: bool = False):
    """Configure tools — delegates to the unified tools_command() in tools_config.py.

    Both `hermes setup tools` and `hermes tools` use the same flow:
    platform selection → toolset toggles → provider/API key configuration.

    Args:
        first_install: When True, uses the simplified first-install flow
            (no platform menu, prompts for all unconfigured API keys).
    """
    from hermes_cli.tools_config import tools_command

    tools_command(first_install=first_install, config=config)


# =============================================================================
# Post-Migration Section Skip Logic
# =============================================================================


def _model_section_has_credentials(config: dict) -> bool:
    """Return True when any known inference provider has usable credentials.

    Sources of truth:
      * ``PROVIDER_REGISTRY`` in ``hermes_cli.auth`` — lists every supported
        provider along with its ``api_key_env_vars``.
      * ``active_provider`` in the auth store — covers OAuth device-code /
        external-OAuth providers (Nous, Codex, Qwen, Gemini CLI, ...).
      * The legacy OpenRouter aggregator env vars, which route generic
        ``OPENAI_API_KEY`` / ``OPENROUTER_API_KEY`` values through OpenRouter.
    """
    try:
        from hermes_cli.auth import get_active_provider
        if get_active_provider():
            return True
    except Exception:
        pass

    try:
        from hermes_cli.auth import PROVIDER_REGISTRY
    except Exception:
        PROVIDER_REGISTRY = {}  # type: ignore[assignment]

    def _has_key(pconfig) -> bool:
        for env_var in pconfig.api_key_env_vars:
            # CLAUDE_CODE_OAUTH_TOKEN is set by Claude Code itself, not by
            # the user — mirrors is_provider_explicitly_configured in auth.py.
            if env_var == "CLAUDE_CODE_OAUTH_TOKEN":
                continue
            if get_env_value(env_var):
                return True
        return False

    # Prefer the provider declared in config.yaml, avoids false positives
    # from stray env vars (GH_TOKEN, etc.) when the user has already picked
    # a different provider.
    model_cfg = config.get("model") if isinstance(config, dict) else None
    if isinstance(model_cfg, dict):
        provider_id = (model_cfg.get("provider") or "").strip().lower()
        if provider_id in PROVIDER_REGISTRY:
            if _has_key(PROVIDER_REGISTRY[provider_id]):
                return True
        if provider_id == "openrouter":
            for env_var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
                if get_env_value(env_var):
                    return True

    # OpenRouter aggregator fallback (no provider declared in config).
    for env_var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
        if get_env_value(env_var):
            return True

    for pid, pconfig in PROVIDER_REGISTRY.items():
        # Skip copilot in auto-detect: GH_TOKEN / GITHUB_TOKEN are
        # commonly set for git tooling.  Mirrors resolve_provider in auth.py.
        if pid == "copilot":
            continue
        if _has_key(pconfig):
            return True
    return False
def _gateway_platform_short_label(label: str) -> str:
    """Strip trailing parenthetical qualifiers from a gateway platform label."""
    base = label.split("(", 1)[0].strip()
    return base or label


def _get_section_config_summary(config: dict, section_key: str) -> Optional[str]:
    """Return a short summary if a setup section is already configured, else None.

    Used after OpenClaw migration to detect which sections can be skipped.
    ``get_env_value`` is the module-level import from hermes_cli.config
    so that test patches on ``setup_mod.get_env_value`` take effect.
    """
    if section_key == "model":
        if not _model_section_has_credentials(config):
            return None
        model = config.get("model")
        if isinstance(model, str) and model.strip():
            return model.strip()
        if isinstance(model, dict):
            return str(model.get("default") or model.get("model") or "configured")
        return "configured"

    elif section_key == "terminal":
        backend = cfg_get(config, "terminal", "backend", default="local")
        return f"backend: {backend}"

    elif section_key == "agent":
        max_turns = cfg_get(config, "agent", "max_turns", default=90)
        return f"max turns: {max_turns}"

    elif section_key == "gateway":
        from hermes_cli.gateway import _all_platforms, _platform_status
        # Count any non-empty status other than the "not configured" sentinel —
        # platforms like WhatsApp ("enabled, not paired"), Matrix ("configured
        # + E2EE"), and Signal ("partially configured") all indicate the user
        # has already started setup and we shouldn't force the section to rerun.
        configured = [
            _gateway_platform_short_label(plat["label"])
            for plat in _all_platforms()
            if _platform_status(plat) and _platform_status(plat) != "not configured"
        ]
        if configured:
            return ", ".join(configured)
        return None  # No platforms configured — section must run

    elif section_key == "tools":
        tools = []
        if get_env_value("ELEVENLABS_API_KEY"):
            tools.append("TTS/ElevenLabs")
        if get_env_value("BROWSERBASE_API_KEY"):
            tools.append("Browser")
        if get_env_value("FIRECRAWL_API_KEY"):
            tools.append("Firecrawl")
        if tools:
            return ", ".join(tools)
        return None

    return None


def _skip_configured_section(
    config: dict, section_key: str, label: str
) -> bool:
    """Show an already-configured section summary and offer to skip.

    Returns True if the user chose to skip, False if the section should run.
    """
    summary = _get_section_config_summary(config, section_key)
    if not summary:
        return False
    print()
    print_success(f"  {label}: {summary}")
    return not prompt_yes_no(f"  重新配置 {label.lower()}?", default=False)


# =============================================================================
# OpenClaw Migration
# =============================================================================


_OPENCLAW_SCRIPT = (
    get_optional_skills_dir(PROJECT_ROOT / "optional-skills")
    / "migration"
    / "openclaw-migration"
    / "scripts"
    / "openclaw_to_hermes.py"
)
def _load_openclaw_migration_module():
    """Load the openclaw_to_hermes migration script as a module.

    Returns the loaded module, or None if the script can't be loaded.
    """
    if not _OPENCLAW_SCRIPT.exists():
        return None

    spec = importlib.util.spec_from_file_location(
        "openclaw_to_hermes", _OPENCLAW_SCRIPT
    )
    if spec is None or spec.loader is None:
        return None

    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules so @dataclass can resolve the module
    # (Python 3.11+ requires this for dynamically loaded modules)
    import sys as _sys
    _sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        _sys.modules.pop(spec.name, None)
        raise
    return mod


# Item kinds that represent high-impact changes warranting explicit warnings.
# Gateway tokens/channels can hijack messaging platforms from the old agent.
# Config values may have different semantics between OpenClaw and Hermes.
# Instruction/context files (.md) can contain incompatible setup procedures.
_HIGH_IMPACT_KIND_KEYWORDS = {
    "gateway": "⚠ 消息网关/消息传递 — 这将配置 Hermes 使用你的 OpenClaw 消息通道",
    "telegram": "⚠ Telegram — 这将使 Hermes 指向你的 OpenClaw Telegram 机器人",
    "slack": "⚠ Slack — 这将使 Hermes 指向你的 OpenClaw Slack 工作区",
    "discord": "⚠ Discord — 这将使 Hermes 指向你的 OpenClaw Discord 机器人",
    "whatsapp": "⚠ WhatsApp — 这将使 Hermes 指向你的 OpenClaw WhatsApp 连接",
    "config": "⚠ 配置值 — OpenClaw 设置可能无法 1:1 映射到 Hermes 的等效项",
    "soul": "⚠ 指令文件 — 可能包含 OpenClaw 特定的设置/重启流程",
    "memory": "⚠ 记忆/上下文文件 — 可能引用 OpenClaw 特定的基础设施",
    "context": "⚠ 上下文文件 — 可能包含 OpenClaw 特定的指令",
}


def _print_migration_preview(report: dict):
    """Print a detailed dry-run preview of what migration would do.

    Groups items by category and adds explicit warnings for high-impact
    changes like gateway token takeover and config value differences.
    """
    items = report.get("items", [])
    if not items:
        print_info("无需迁移。")
        return

    migrated_items = [i for i in items if i.get("status") == "migrated"]
    conflict_items = [i for i in items if i.get("status") == "conflict"]
    skipped_items = [i for i in items if i.get("status") == "skipped"]

    warnings_shown = set()

    if migrated_items:
        print(color("  将导入：", Colors.GREEN))
        for item in migrated_items:
            kind = item.get("kind", "unknown")
            dest = item.get("destination", "")
            if dest:
                dest_short = str(dest).replace(str(Path.home()), "~")
                print(f"      {kind:<22s} → {dest_short}")
            else:
                print(f"      {kind}")

            # Check for high-impact items and collect warnings
            kind_lower = kind.lower()
            dest_lower = str(dest).lower()
            for keyword, warning in _HIGH_IMPACT_KIND_KEYWORDS.items():
                if keyword in kind_lower or keyword in dest_lower:
                    warnings_shown.add(warning)
        print()

    if conflict_items:
        print(color("  将覆盖（与现有 Hermes 配置冲突）：", Colors.YELLOW))
        for item in conflict_items:
            kind = item.get("kind", "unknown")
            reason = item.get("reason", "already exists")
            print(f"      {kind:<22s}  {reason}")
        print()

    if skipped_items:
        print(color("  将跳过：", Colors.DIM))
        for item in skipped_items:
            kind = item.get("kind", "unknown")
            reason = item.get("reason", "")
            print(f"      {kind:<22s}  {reason}")
        print()

    # Print collected warnings
    if warnings_shown:
        print(color("  ── 警告 ──", Colors.YELLOW))
        for warning in sorted(warnings_shown):
            print(color(f"    {warning}", Colors.YELLOW))
        print()
        print(color("  注意：OpenClaw 配置值在 Hermes 中可能具有不同的语义。", Colors.YELLOW))
        print(color("  例如，OpenClaw 的 tool_call_execution: \"auto\" ≠ Hermes 的 yolo 模式。", Colors.YELLOW))
        print(color("  OpenClaw 的指令文件 (.md) 可能包含不兼容的流程。", Colors.YELLOW))
        print()
def _offer_openclaw_migration(hermes_home: Path) -> bool:
    """Detect ~/.openclaw and offer to migrate during first-time setup.

    Runs a dry-run first to show the user exactly what would be imported,
    overwritten, or taken over. Only executes after explicit confirmation.

    Returns True if migration ran successfully, False otherwise.
    """
    openclaw_dir = Path.home() / ".openclaw"
    if not openclaw_dir.is_dir():
        return False

    if not _OPENCLAW_SCRIPT.exists():
        return False

    print()
    print_header("检测到 OpenClaw 安装")
    print_info(f"在 {openclaw_dir} 找到 OpenClaw 数据")
    print_info("Hermes 可以在进行任何更改前预览将要导入的内容。")
    print()

    if not prompt_yes_no("是否查看可导入的内容？", default=True):
        print_info(
            "跳过迁移。您稍后可以通过以下命令运行：hermes claw migrate --dry-run"
        )
        return False

    # Ensure config.yaml exists before migration tries to read it
    config_path = get_config_path()
    if not config_path.exists():
        save_config(load_config())

    # Load the migration module
    try:
        mod = _load_openclaw_migration_module()
        if mod is None:
            print_warning("无法加载迁移脚本。")
            return False
    except Exception as e:
        print_warning(f"无法加载迁移脚本：{e}")
        logger.debug("OpenClaw migration module load error", exc_info=True)
        return False

    # ── Phase 1: Dry-run preview ──
    try:
        selected = mod.resolve_selected_options(None, None, preset="full")
        dry_migrator = mod.Migrator(
            source_root=openclaw_dir.resolve(),
            target_root=hermes_home.resolve(),
            execute=False,  # dry-run — no files modified
            workspace_target=None,
            overwrite=True,  # show everything including conflicts
            migrate_secrets=True,
            output_dir=None,
            selected_options=selected,
            preset_name="full",
        )
        preview_report = dry_migrator.migrate()
    except Exception as e:
        print_warning(f"迁移预览失败：{e}")
        logger.debug("OpenClaw migration preview error", exc_info=True)
        return False

    # Display the full preview
    preview_summary = preview_report.get("summary", {})
    preview_count = preview_summary.get("migrated", 0)

    if preview_count == 0:
        print()
        print_info("没有可从 OpenClaw 导入的内容。")
        return False

    print()
    print_header(f"迁移预览 — 将导入 {preview_count} 个项目")
    print_info("尚未进行任何更改。请查看以下列表：")
    print()
    _print_migration_preview(preview_report)

    # ── Phase 2: Confirm and execute ──
    if not prompt_yes_no("是否继续执行迁移？", default=False):
        print_info(
            "迁移已取消。您稍后可以通过以下命令运行：hermes claw migrate"
        )
        print_info(
            "使用 --dry-run 再次预览，或使用 --preset minimal 进行更轻量的导入。"
        )
        return False

    # Execute the migration — overwrite=False so existing Hermes configs are
    # preserved. The user saw the preview; conflicts are skipped by default.
    try:
        migrator = mod.Migrator(
            source_root=openclaw_dir.resolve(),
            target_root=hermes_home.resolve(),
            execute=True,
            workspace_target=None,
            overwrite=False,  # preserve existing Hermes config
            migrate_secrets=True,
            output_dir=None,
            selected_options=selected,
            preset_name="full",
        )
        report = migrator.migrate()
    except Exception as e:
        print_warning(f"迁移失败：{e}")
        logger.debug("OpenClaw migration error", exc_info=True)
        return False

    # Print final summary
    summary = report.get("summary", {})
    migrated = summary.get("migrated", 0)
    skipped = summary.get("skipped", 0)
    conflicts = summary.get("conflict", 0)
    errors = summary.get("error", 0)

    print()
    if migrated:
        print_success(f"从 OpenClaw 导入了 {migrated} 个项目。")
    if conflicts:
        print_info(f"跳过了 {conflicts} 个已存在于 Hermes 中的项目（使用 hermes claw migrate --overwrite 强制覆盖）。")
    if skipped:
        print_info(f"跳过了 {skipped} 个项目（未找到或未更改）。")
    if errors:
        print_warning(f"{errors} 个项目出现错误 — 请查看迁移报告。")

    output_dir = report.get("output_dir")
    if output_dir:
        print_info(f"完整报告已保存至：{output_dir}")

    print_success("迁移完成！继续设置...")
    return True


# =============================================================================
# Main Wizard Orchestrator
# =============================================================================

SETUP_SECTIONS = [
    ("model", "模型与提供商", setup_model_provider),
    ("tts", "文本转语音", setup_tts),
    ("terminal", "终端后端", setup_terminal_backend),
    ("gateway", "消息平台（消息网关）", setup_gateway),
    ("tools", "工具", setup_tools),
    ("agent", "Agent 设置", setup_agent_settings),
]
def run_setup_wizard(args):
    """Run the interactive setup wizard.

    Supports full, quick, and section-specific setup:
      hermes setup           — full or quick (auto-detected)
      hermes setup model     — just model/provider
      hermes setup tts       — just text-to-speech
      hermes setup terminal  — just terminal backend
      hermes setup gateway   — just messaging platforms
      hermes setup tools     — just tool configuration
      hermes setup agent     — just agent settings
    """
    from hermes_cli.config import is_managed, managed_error
    if is_managed():
        managed_error("run setup wizard")
        return
    ensure_hermes_home()

    reset_requested = bool(getattr(args, "reset", False))
    if reset_requested:
        save_config(copy.deepcopy(DEFAULT_CONFIG))
        print_success("配置已重置为默认值。")

    reconfigure_requested = bool(getattr(args, "reconfigure", False))
    quick_requested = bool(getattr(args, "quick", False))

    config = load_config()
    hermes_home = get_hermes_home()

    # Back up existing config before setup modifies it (#3522)
    config_path = get_config_path()
    if config_path.exists():
        from datetime import datetime as _dt
        _backup_path = config_path.with_suffix(
            f".yaml.bak.{_dt.now().strftime('%Y%m%d_%H%M%S')}"
        )
        try:
            import shutil
            shutil.copy2(config_path, _backup_path)
        except Exception:
            _backup_path = None
    else:
        _backup_path = None

    # Detect non-interactive environments (headless SSH, Docker, CI/CD)
    non_interactive = getattr(args, 'non_interactive', False)
    if not non_interactive and not is_interactive_stdin():
        non_interactive = True

    if non_interactive:
        print_noninteractive_setup_guidance(
            "运行在非交互式环境中（未检测到 TTY）。"
        )
        return

    # Check if a specific section was requested
    section = getattr(args, "section", None)
    if section:
        for key, label, func in SETUP_SECTIONS:
            if key == section:
                print()
                print(
                    color(
                        "┌─────────────────────────────────────────────────────────┐",
                        Colors.MAGENTA,
                    )
                )
                print(color(f"│     ⚕ Hermes 设置 — {label:<34s} │", Colors.MAGENTA))
                print(
                    color(
                        "└─────────────────────────────────────────────────────────┘",
                        Colors.MAGENTA,
                    )
                )
                func(config)
                save_config(config)
                print()
                print_success(f"{label} 配置完成！")
                return

        print_error(f"未知的设置部分：{section}")
        print_info(f"可用部分：{', '.join(k for k, _, _ in SETUP_SECTIONS)}")
        return

    # Check if this is an existing installation with a provider configured
    from hermes_cli.auth import get_active_provider

    active_provider = get_active_provider()
    is_existing = (
        bool(get_env_value("OPENROUTER_API_KEY"))
        or bool(get_env_value("OPENAI_BASE_URL"))
        or active_provider is not None
    )

    print()
    print(
        color(
            "┌─────────────────────────────────────────────────────────┐",
            Colors.MAGENTA,
        )
    )
    print(
        color(
            "│             ⚕ Hermes Agent 设置向导                    │", Colors.MAGENTA
        )
    )
    print(
        color(
            "├─────────────────────────────────────────────────────────┤",
            Colors.MAGENTA,
        )
    )
    print(
        color(
            "│  让我们来配置您的 Hermes Agent 安装。                  │", Colors.MAGENTA
        )
    )
    print(
        color(
            "│  随时按 Ctrl+C 退出。                                  │", Colors.MAGENTA
        )
    )
    print(
        color(
            "└─────────────────────────────────────────────────────────┘",
            Colors.MAGENTA,
        )
    )

    migration_ran = False

    if is_existing:
        # Existing install — default is the full-wizard reconfigure flow.
        # Every prompt shows the current value as its default, so pressing
        # Enter keeps it.  Opt into `--quick` for the narrow "just fill in
        # missing items" flow (useful after a partial OpenClaw migration
        # or when a required API key got cleared).
        if quick_requested:
            _run_quick_setup(config, hermes_home)
            return

        print()
        print_header("重新配置")
        print_success("您已经配置了 Hermes。")
        print_info("正在运行完整向导 — 每个提示都显示您当前的值。")
        print_info("按 Enter 键保留它，或输入新值进行更改。")
        print_info("")
        print_info("提示：使用 'hermes setup model|terminal|")
        print_info("     gateway|tools|agent' 直接跳转到某个部分，或使用 --quick 仅填充缺失项。")
        # Fall through to the "Full Setup — run all sections" block below.
        # --reconfigure is now the default on existing installs; the flag
        # is preserved for backwards compatibility but is a no-op here.
    else:
        # ── First-Time Setup ──
        print()

        # --reconfigure / --quick on a fresh install are meaningless — fall
        # through to the normal first-time flow.
        if reconfigure_requested or quick_requested:
            print_info("未找到现有配置 — 正在运行首次设置。")
            print()

        # Offer OpenClaw migration before configuration begins
        migration_ran = _offer_openclaw_migration(hermes_home)
        if migration_ran:
            config = load_config()

        setup_mode = prompt_choice("您希望如何设置 Hermes？", [
            "快速设置 — 提供商、模型和消息传递（推荐）",
            "完整设置 — 配置所有内容",
        ], 0)

        if setup_mode == 0:
            _run_first_time_quick_setup(config, hermes_home, is_existing)
            return

    # ── Full Setup — run all sections ──
    print_header("配置位置")
    print_info(f"配置文件：  {get_config_path()}")
    print_info(f"密钥文件： {get_env_path()}")
    print_info(f"数据文件夹：  {hermes_home}")
    print_info(f"安装目录：  {PROJECT_ROOT}")
    print()
    print_info("您可以直接编辑这些文件或使用 'hermes config edit'")

    if migration_ran:
        print()
        print_info("设置已从 OpenClaw 导入。")
        print_info("下面的每个部分将显示导入的内容 — 按 Enter 键保留，")
        print_info("或根据需要选择重新配置。")

    # Section 1: Model & Provider
    if not (migration_ran and _skip_configured_section(config, "model", "模型与提供商")):
        setup_model_provider(config)

    # Section 2: Terminal Backend
    if not (migration_ran and _skip_configured_section(config, "terminal", "终端后端")):
        setup_terminal_backend(config)

    # Section 3: Agent Settings
    if not (migration_ran and _skip_configured_section(config, "agent", "Agent 设置")):
        setup_agent_settings(config)

    # Section 4: Messaging Platforms
    if not (migration_ran and _skip_configured_section(config, "gateway", "消息平台")):
        setup_gateway(config)

    # Section 5: Tools
    if not (migration_ran and _skip_configured_section(config, "tools", "工具")):
        setup_tools(config, first_install=not is_existing)

    # Save and show summary
    save_config(config)
    if _backup_path and _backup_path.exists():
        print_info(f"之前的配置已备份到：{_backup_path}")
        print_info("如果设置更改了您自定义的值，请使用以下命令恢复：")
        print_info(f"  cp {_backup_path} {config_path}")
    _print_setup_summary(config, hermes_home)

    _offer_launch_chat()
def _offer_launch_chat():
    """Prompt the user to jump straight into chat after setup."""
    print()
    if not prompt_yes_no("现在启动 Hermes 聊天吗？", True):
        return

    from hermes_cli.relaunch import relaunch
    relaunch(["chat"])


def _run_first_time_quick_setup(config: dict, hermes_home, is_existing: bool):
    """Streamlined first-time setup: provider + model only.

    Applies sensible defaults for TTS (Edge), terminal (local), agent
    settings, and tools — the user can customize later via
    ``hermes setup <section>``.
    """
    # Step 1: Model & Provider (essential — skips rotation/vision/TTS)
    setup_model_provider(config, quick=True)

    # Step 2: Apply defaults for everything else
    _apply_default_agent_settings(config)
    config.setdefault("terminal", {}).setdefault("backend", "local")

    save_config(config)

    # Step 3: Offer messaging gateway setup
    print()
    gateway_choice = prompt_choice(
        "连接消息平台吗？ (Telegram, Discord 等)",
        [
            "现在设置消息平台 (推荐)",
            "跳过 — 稍后使用 'hermes setup gateway' 设置",
        ],
        0,
    )

    if gateway_choice == 0:
        setup_gateway(config)
        save_config(config)

    print()
    print_success("设置完成！您可以开始使用了。")
    print()
    print_info("  配置所有设置:    hermes setup")
    if gateway_choice != 0:
        print_info("  连接 Telegram/Discord:  hermes setup gateway")
    print()

    _print_setup_summary(config, hermes_home)

    _offer_launch_chat()


def _run_quick_setup(config: dict, hermes_home):
    """Quick setup — only configure items that are missing."""
    from hermes_cli.config import (
        get_missing_env_vars,
        get_missing_config_fields,
        check_config_version,
    )

    print()
    print_header("快速设置 — 仅配置缺失项")

    # Check what's missing
    missing_required = [
        v for v in get_missing_env_vars(required_only=False) if v.get("is_required")
    ]
    missing_optional = [
        v for v in get_missing_env_vars(required_only=False) if not v.get("is_required")
    ]
    missing_config = get_missing_config_fields()
    current_ver, latest_ver = check_config_version()

    has_anything_missing = (
        missing_required
        or missing_optional
        or missing_config
        or current_ver < latest_ver
    )

    if not has_anything_missing:
        print_success("所有配置已完成！无需操作。")
        print()
        print_info("运行 'hermes setup' 并选择 '完整设置' 以重新配置,")
        print_info("或从菜单中选择特定部分。")
        return

    # Handle missing required env vars
    if missing_required:
        print()
        print_info(f"{len(missing_required)} 个必需设置缺失:")
        for var in missing_required:
            print(f"     • {var['name']}")
        print()

        for var in missing_required:
            print()
            print(color(f"  {var['name']}", Colors.CYAN))
            print_info(f"  {var.get('description', '')}")
            if var.get("url"):
                print_info(f"  获取密钥地址: {var['url']}")

            if var.get("password"):
                value = prompt(f"  {var.get('prompt', var['name'])}", password=True)
            else:
                value = prompt(f"  {var.get('prompt', var['name'])}")

            if value:
                save_env_value(var["name"], value)
                print_success(f"  已保存 {var['name']}")
            else:
                print_warning(f"  已跳过 {var['name']}")

    # Split missing optional vars by category
    missing_tools = [v for v in missing_optional if v.get("category") == "tool"]
    missing_messaging = [
        v
        for v in missing_optional
        if v.get("category") == "messaging" and not v.get("advanced")
    ]

    # ── Tool API keys (checklist) ──
    if missing_tools:
        print()
        print_header("工具 API 密钥")

        checklist_labels = []
        for var in missing_tools:
            tools = var.get("tools", [])
            tools_str = f" → {', '.join(tools[:2])}" if tools else ""
            checklist_labels.append(f"{var.get('description', var['name'])}{tools_str}")

        selected_indices = prompt_checklist(
            "您想配置哪些工具？",
            checklist_labels,
        )

        for idx in selected_indices:
            var = missing_tools[idx]
            _prompt_api_key(var)

    # ── Messaging platforms (checklist then prompt for selected) ──
    if missing_messaging:
        print()
        print_header("消息平台")
        print_info("将 Hermes 连接到消息应用，以便随时随地聊天。")
        print_info("您稍后可以使用 'hermes setup gateway' 配置这些。")

        # Group by platform (preserving order)
        platform_order = []
        platforms = {}
        for var in missing_messaging:
            name = var["name"]
            if "TELEGRAM" in name:
                plat = "Telegram"
            elif "DISCORD" in name:
                plat = "Discord"
            elif "SLACK" in name:
                plat = "Slack"
            else:
                continue
            if plat not in platforms:
                platform_order.append(plat)
            platforms.setdefault(plat, []).append(var)

        platform_labels = [
            {
                "Telegram": "📱 Telegram",
                "Discord": "💬 Discord",
                "Slack": "💼 Slack",
            }.get(p, p)
            for p in platform_order
        ]

        selected_indices = prompt_checklist(
            "您想设置哪些平台？",
            platform_labels,
        )

        for idx in selected_indices:
            plat = platform_order[idx]
            vars_list = platforms[plat]
            emoji = {"Telegram": "📱", "Discord": "💬", "Slack": "💼"}.get(plat, "")
            print()
            print(color(f"  ─── {emoji} {plat} ───", Colors.CYAN))
            print()
            for var in vars_list:
                print_info(f"  {var.get('description', '')}")
                if var.get("url"):
                    print_info(f"  {var['url']}")
                if var.get("password"):
                    value = prompt(f"  {var.get('prompt', var['name'])}", password=True)
                else:
                    value = prompt(f"  {var.get('prompt', var['name'])}")
                if value:
                    save_env_value(var["name"], value)
                    print_success("  ✓ 已保存")
                else:
                    print_warning("  已跳过")
                print()

    # Handle missing config fields
    if missing_config:
        print()
        print_info(
            f"正在添加 {len(missing_config)} 个新配置选项并使用默认值..."
        )
        for field in missing_config:
            print_success(f"  已添加 {field['key']} = {field['default']}")

        # Update config version
        config["_config_version"] = latest_ver
        save_config(config)

    # Jump to summary
    _print_setup_summary(config, hermes_home)