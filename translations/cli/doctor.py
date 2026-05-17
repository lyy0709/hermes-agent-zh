"""
Doctor command for hermes CLI.

Diagnoses issues with Hermes Agent setup.
"""

import os
import sys
import subprocess
import shutil
import importlib.util
from pathlib import Path

from hermes_cli.config import get_project_root, get_hermes_home, get_env_path
from hermes_cli.env_loader import load_hermes_dotenv
from hermes_constants import display_hermes_home

PROJECT_ROOT = get_project_root()
HERMES_HOME = get_hermes_home()
_DHH = display_hermes_home()  # 面向用户的显示路径（例如 ~/.hermes 或 ~/.hermes/profiles/coder）

# 从 ~/.hermes/.env 加载环境变量，以便 API 密钥检查正常工作
_env_path = get_env_path()
load_hermes_dotenv(hermes_home=_env_path.parent, project_env=PROJECT_ROOT / ".env")

from hermes_cli.colors import Colors, color
from hermes_cli.models import _HERMES_USER_AGENT
from hermes_cli.vercel_auth import describe_vercel_auth
from hermes_constants import OPENROUTER_MODELS_URL
from utils import base_url_host_matches


_PROVIDER_ENV_HINTS = (
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_TOKEN",
    "OPENAI_BASE_URL",
    "NOUS_API_KEY",
    "GLM_API_KEY",
    "ZAI_API_KEY",
    "Z_AI_API_KEY",
    "KIMI_API_KEY",
    "KIMI_CN_API_KEY",
    "GMI_API_KEY",
    "MINIMAX_API_KEY",
    "MINIMAX_CN_API_KEY",
    "KILOCODE_API_KEY",
    "DEEPSEEK_API_KEY",
    "DASHSCOPE_API_KEY",
    "HF_TOKEN",
    "AI_GATEWAY_API_KEY",
    "OPENCODE_ZEN_API_KEY",
    "OPENCODE_GO_API_KEY",
    "XIAOMI_API_KEY",
    "TOKENHUB_API_KEY",
)


from hermes_constants import is_termux as _is_termux


def _python_install_cmd() -> str:
    return "python -m pip install" if _is_termux() else "uv pip install"


def _system_package_install_cmd(pkg: str) -> str:
    if _is_termux():
        return f"pkg install {pkg}"
    if sys.platform == "darwin":
        return f"brew install {pkg}"
    return f"sudo apt install {pkg}"


def _safe_which(cmd: str) -> str | None:
    """shutil.which wrapper resilient to platform monkeypatching in tests."""
    try:
        return shutil.which(cmd)
    except Exception:
        return None


def _termux_browser_setup_steps(node_installed: bool) -> list[str]:
    steps: list[str] = []
    step = 1
    if not node_installed:
        steps.append(f"{step}) pkg install nodejs")
        step += 1
    steps.append(f"{step}) npm install -g agent-browser")
    steps.append(f"{step + 1}) agent-browser install")
    return steps


def _termux_install_all_fallback_notes() -> list[str]:
    return [
        "Termux 安装配置文件：使用 .[termux-all] 以获得广泛的兼容性（Termux 上的安装器默认选项）。",
        "Termux 上排除了 Matrix E2EE 额外组件（python-olm 目前构建失败）。",
        "Termux 上排除了本地 faster-whisper 额外组件（ctranslate2/av 构建路径不可用）。",
        "STT 后备方案：使用 Groq Whisper（设置 GROQ_API_KEY）或 OpenAI Whisper（设置 VOICE_TOOLS_OPENAI_KEY）。",
    ]


def _has_provider_env_config(content: str) -> bool:
    """Return True when ~/.hermes/.env contains provider auth/base URL settings."""
    return any(key in content for key in _PROVIDER_ENV_HINTS)
def _honcho_is_configured_for_doctor() -> bool:
    """Return True when Honcho is configured, even if this process has no active session."""
    try:
        from plugins.memory.honcho.client import HonchoClientConfig

        cfg = HonchoClientConfig.from_global_config()
        return bool(cfg.enabled and (cfg.api_key or cfg.base_url))
    except Exception:
        return False


def _is_kanban_worker_env_gate(item: dict) -> bool:
    """Return True when Kanban is unavailable only because this is not a worker process."""
    if item.get("name") != "kanban":
        return False
    if os.environ.get("HERMES_KANBAN_TASK"):
        return False

    tools = item.get("tools") or []
    return bool(tools) and all(str(tool).startswith("kanban_") for tool in tools)


def _doctor_tool_availability_detail(toolset: str) -> str:
    """Optional explanatory suffix for toolsets whose doctor status needs context."""
    if toolset == "kanban" and not os.environ.get("HERMES_KANBAN_TASK"):
        return "(运行时门控；仅加载给调度器生成的worker进程)"
    return ""


def _apply_doctor_tool_availability_overrides(available: list[str], unavailable: list[dict]) -> tuple[list[str], list[dict]]:
    """Adjust runtime-gated tool availability for doctor diagnostics."""
    updated_available = list(available)
    updated_unavailable = []
    for item in unavailable:
        name = item.get("name")
        if _is_kanban_worker_env_gate(item):
            if "kanban" not in updated_available:
                updated_available.append("kanban")
            continue
        if name == "honcho" and _honcho_is_configured_for_doctor():
            if "honcho" not in updated_available:
                updated_available.append("honcho")
            continue
        updated_unavailable.append(item)
    return updated_available, updated_unavailable


def _has_healthy_oauth_fallback_for_apikey_provider(provider_label: str) -> bool:
    """Return True when a direct API-key probe failure is non-blocking.

    Some provider families support both a direct API-key path and a separate
    OAuth runtime path. When the OAuth path is already healthy, doctor should
    still show a failed API-key connectivity row, but it should not promote
    that direct-key problem into the final blocking summary.
    """
    try:
        from hermes_cli.auth import (
            get_gemini_oauth_auth_status,
            get_minimax_oauth_auth_status,
        )
    except Exception:
        return False

    normalized = (provider_label or "").strip().lower()
    if normalized in {"google / gemini", "gemini"}:
        return bool((get_gemini_oauth_auth_status() or {}).get("logged_in"))
    if normalized == "minimax":
        return bool((get_minimax_oauth_auth_status() or {}).get("logged_in"))
    return False


def check_ok(text: str, detail: str = ""):
    print(f"  {color('✓', Colors.GREEN)} {text}" + (f" {color(detail, Colors.DIM)}" if detail else ""))

def check_warn(text: str, detail: str = ""):
    print(f"  {color('⚠', Colors.YELLOW)} {text}" + (f" {color(detail, Colors.DIM)}" if detail else ""))
def check_fail(text: str, detail: str = ""):
    print(f"  {color('✗', Colors.RED)} {text}" + (f" {color(detail, Colors.DIM)}" if detail else ""))

def check_info(text: str):
    print(f"    {color('→', Colors.CYAN)} {text}")


def _check_gateway_service_linger(issues: list[str]) -> None:
    """Warn when a systemd user gateway service will stop after logout."""
    try:
        from hermes_cli.gateway import (
            get_systemd_linger_status,
            get_systemd_unit_path,
            is_linux,
        )
    except Exception as e:
        check_warn("消息网关服务 linger 状态", f"(无法导入网关助手: {e})")
        return

    if not is_linux():
        return

    unit_path = get_systemd_unit_path()
    if not unit_path.exists():
        return

    print()
    print(color("◆ 消息网关服务", Colors.CYAN, Colors.BOLD))

    linger_enabled, linger_detail = get_systemd_linger_status()
    if linger_enabled is True:
        check_ok("Systemd linger 已启用", "(消息网关服务在登出后仍存活)")
    elif linger_enabled is False:
        check_warn("Systemd linger 已禁用", "(消息网关可能在登出后停止)")
        check_info("运行: sudo loginctl enable-linger $USER")
        issues.append("为用户的消息网关服务启用 linger: sudo loginctl enable-linger $USER")
    else:
        check_warn("无法验证 systemd linger", f"({linger_detail})")


_APIKEY_PROVIDERS_CACHE: list | None = None


def _build_apikey_providers_list() -> list:
    """Build the API-key provider health-check list once and cache it.

    Tuple format: (name, env_vars, default_url, base_env, supports_models_endpoint)
    Base list augmented with any ProviderProfile with auth_type="api_key" not
    already present — adding plugins/model-providers/<name>/ is sufficient to get into doctor.
    """
    _static = [
        ("Z.AI / GLM",      ("GLM_API_KEY", "ZAI_API_KEY", "Z_AI_API_KEY"), "https://api.z.ai/api/paas/v4/models", "GLM_BASE_URL", True),
        ("Kimi / Moonshot",  ("KIMI_API_KEY",),                              "https://api.moonshot.ai/v1/models",   "KIMI_BASE_URL", True),
        ("StepFun Step Plan", ("STEPFUN_API_KEY",),                          "https://api.stepfun.ai/step_plan/v1/models", "STEPFUN_BASE_URL", True),
        ("Kimi / Moonshot (China)", ("KIMI_CN_API_KEY",),                    "https://api.moonshot.cn/v1/models",   None, True),
        ("Arcee AI",         ("ARCEEAI_API_KEY",),                           "https://api.arcee.ai/api/v1/models",  "ARCEE_BASE_URL", True),
        ("GMI Cloud",        ("GMI_API_KEY",),                               "https://api.gmi-serving.com/v1/models", "GMI_BASE_URL", True),
        ("DeepSeek",         ("DEEPSEEK_API_KEY",),                          "https://api.deepseek.com/v1/models",  "DEEPSEEK_BASE_URL", True),
        ("Hugging Face",     ("HF_TOKEN",),                                  "https://router.huggingface.co/v1/models", "HF_BASE_URL", True),
        ("NVIDIA NIM",       ("NVIDIA_API_KEY",),                            "https://integrate.api.nvidia.com/v1/models", "NVIDIA_BASE_URL", True),
        ("Alibaba/DashScope", ("DASHSCOPE_API_KEY",),                        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/models", "DASHSCOPE_BASE_URL", True),
        # MiniMax global: /v1 endpoint supports /models.
        ("MiniMax",          ("MINIMAX_API_KEY",),                           "https://api.minimax.io/v1/models",    "MINIMAX_BASE_URL", True),
        # MiniMax CN: /v1 endpoint does NOT support /models (returns 404).
        ("MiniMax (China)",  ("MINIMAX_CN_API_KEY",),                        "https://api.minimaxi.com/v1/models",  "MINIMAX_CN_BASE_URL", False),
        ("Vercel AI Gateway", ("AI_GATEWAY_API_KEY",),                       "https://ai-gateway.vercel.sh/v1/models", "AI_GATEWAY_BASE_URL", True),
        ("Kilo Code",        ("KILOCODE_API_KEY",),                          "https://api.kilo.ai/api/gateway/models", "KILOCODE_BASE_URL", True),
        ("OpenCode Zen",     ("OPENCODE_ZEN_API_KEY",),                      "https://opencode.ai/zen/v1/models",  "OPENCODE_ZEN_BASE_URL", True),
        # OpenCode Go has no shared /models endpoint; skip the health check.
        ("OpenCode Go",      ("OPENCODE_GO_API_KEY",),                       None,                                  "OPENCODE_GO_BASE_URL", False),
    ]
    _known_names = {t[0] for t in _static}
    # Also index by profile canonical name so profiles without display_name
    # don't create duplicate entries for providers already in the static list.
    _known_canonical: set[str] = set()
    _name_to_canonical = {
        "Z.AI / GLM": "zai", "Kimi / Moonshot": "kimi-coding",
        "StepFun Step Plan": "stepfun", "Kimi / Moonshot (China)": "kimi-coding-cn",
        "Arcee AI": "arcee", "GMI Cloud": "gmi", "DeepSeek": "deepseek",
        "Hugging Face": "huggingface", "NVIDIA NIM": "nvidia",
        "Alibaba/DashScope": "alibaba", "MiniMax": "minimax",
        "MiniMax (China)": "minimax-cn", "Vercel AI Gateway": "ai-gateway",
        "Kilo Code": "kilocode", "OpenCode Zen": "opencode-zen",
        "OpenCode Go": "opencode-go",
    }
    for _label, _canonical in _name_to_canonical.items():
        _known_canonical.add(_canonical)
    # Providers that already have a dedicated health check above the generic
    # API-key loop (with custom headers/auth). Skip their pluggable profiles
    # here so the generic Bearer-auth loop doesn't run a duplicate, broken
    # check (e.g. Anthropic native API requires x-api-key, not Bearer).
    _dedicated_canonical = {"anthropic", "openrouter", "bedrock"}
    _known_canonical.update(_dedicated_canonical)
    try:
        from providers import list_providers
        from providers.base import ProviderProfile as _PP
        try:
            from hermes_cli.providers import normalize_provider as _normalize_provider
        except Exception:  # pragma: no cover - normalization is best-effort
            def _normalize_provider(_name: str) -> str:
                return (_name or "").strip().lower()
        for _pp in list_providers():
            if not isinstance(_pp, _PP) or _pp.auth_type != "api_key" or not _pp.env_vars:
                continue
            _label = _pp.display_name or _pp.name
            if _label in _known_names or _pp.name in _known_canonical:
                continue
            _candidates = {_normalize_provider(_pp.name)}
            for _alias in (_pp.aliases or ()):
                _candidates.add(_normalize_provider(_alias))
            if _candidates & _dedicated_canonical:
                continue
            # Separate API-key vars from base-URL override vars — the health-check
            # loop sends the first found value as Authorization: Bearer, so a URL
            # string must never be picked.
            _key_vars = tuple(
                v for v in _pp.env_vars
                if not v.endswith("_BASE_URL") and not v.endswith("_URL")
            )
            _base_var = next(
                (v for v in _pp.env_vars if v.endswith("_BASE_URL") or v.endswith("_URL")),
                None,
            )
            if not _key_vars:
                continue
            _models_url = (
                (_pp.models_url or (_pp.base_url.rstrip("/") + "/models"))
                if _pp.base_url else None
            )
            _hc = getattr(_pp, "supports_health_check", True)
            _static.append((_label, _key_vars, _models_url, _base_var, _hc))
    except Exception:
        pass
    return _static
def run_doctor(args):
    """运行诊断检查。"""
    should_fix = getattr(args, 'fix', False)
    ack_target = getattr(args, 'ack', None)

    # Doctor 从交互式 CLI 运行，因此 CLI 门控的工具可用性检查（如定时任务管理）应看到与 `hermes` 相同的上下文。
    os.environ.setdefault("HERMES_INTERACTIVE", "1")

    # 处理 `hermes doctor --ack <id>` 作为快速路径。持久化确认并返回，不运行其余诊断——用户已看到建议并只想静音它。
    if ack_target:
        from hermes_cli.security_advisories import (
            ADVISORIES,
            ack_advisory,
        )
        valid_ids = {a.id for a in ADVISORIES}
        if ack_target not in valid_ids:
            print(color(
                f"未知建议 ID: {ack_target!r}。已知 ID: "
                f"{', '.join(sorted(valid_ids)) or '(无)'}",
                Colors.RED,
            ))
            sys.exit(2)
        if ack_advisory(ack_target):
            print(color(
                f"  ✓ 已确认建议 {ack_target}。 "
                f"它将不再触发启动横幅。",
                Colors.GREEN,
            ))
        else:
            print(color(
                f"  ✗ 无法持久化对 {ack_target} 的确认。 "
                f"检查 ~/.hermes/config.yaml 是否可写。",
                Colors.RED,
            ))
            sys.exit(1)
        return

    issues = []
    manual_issues = []  # 无法自动修复的问题
    fixed_count = 0

    print()
    print(color("┌─────────────────────────────────────────────────────────┐", Colors.CYAN))
    print(color("│                 🩺 Hermes 医生诊断                        │", Colors.CYAN))
    print(color("└─────────────────────────────────────────────────────────┘", Colors.CYAN))

    # =========================================================================
    # 检查：安全建议（最先运行——这些是最紧急的）
    # =========================================================================
    print()
    print(color("◆ 安全建议", Colors.CYAN, Colors.BOLD))
    try:
        from hermes_cli.security_advisories import (
            detect_compromised,
            filter_unacked,
            full_remediation_text,
            get_acked_ids,
        )
        all_hits = detect_compromised()
        fresh_hits = filter_unacked(all_hits)
        if fresh_hits:
            for hit in fresh_hits:
                check_fail(
                    f"{hit.advisory.title}",
                    f"({hit.package}=={hit.installed_version})",
                )
                # 打印完整的修复块，缩进在 check_fail 标题下，使其作为一个部分阅读。
                for line in full_remediation_text(hit):
                    if line:
                        print(f"    {color(line, Colors.YELLOW)}")
                    else:
                        print()
                # 汇集到操作列表中，以便摘要块为滚动过此部分的用户显示它。
                manual_issues.append(
                    f"解决安全建议 {hit.advisory.id}: "
                    f"卸载 {hit.package}=={hit.installed_version} 并 "
                    f"轮换凭据，然后运行 "
                    f"`hermes doctor --ack {hit.advisory.id}`。"
                )
            # 已确认但仍安装的：显示为信息性，以便用户知道确认后包仍在磁盘上。
            acked_ids = get_acked_ids()
            for h in all_hits:
                if h.advisory.id in acked_ids:
                    check_warn(
                        f"{h.package}=={h.installed_version} 仍安装 "
                        f"(建议 {h.advisory.id} 已确认)",
                    )
        else:
            check_ok("无活跃安全建议")
    except Exception as e:
        # 绝不让建议检查中的错误阻塞 doctor 的其余部分。
        check_warn(f"安全建议检查失败: {e}")
    
    # =========================================================================
    # 检查：Python 版本
    # =========================================================================
    print()
    print(color("◆ Python 环境", Colors.CYAN, Colors.BOLD))
    
    py_version = sys.version_info
    if py_version >= (3, 11):
        check_ok(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    elif py_version >= (3, 10):
        check_ok(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
        check_warn("推荐 Python 3.11+ 用于 RL 训练工具 (tinker 要求 >= 3.11)")
    elif py_version >= (3, 8):
        check_warn(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}", "(推荐 3.10+)")
    else:
        check_fail(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}", "(要求 3.10+)")
        issues.append("升级 Python 到 3.10+")
    
    # 检查是否在虚拟环境中
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        check_ok("虚拟环境活跃")
    else:
        check_warn("不在虚拟环境中", "(推荐)")
    
    # =========================================================================
    # 检查：必需包
    # =========================================================================
    print()
    print(color("◆ 必需包", Colors.CYAN, Colors.BOLD))
    
    required_packages = [
        ("openai", "OpenAI SDK"),
        ("rich", "Rich (终端 UI)"),
        ("dotenv", "python-dotenv"),
        ("yaml", "PyYAML"),
        ("httpx", "HTTPX"),
    ]
    
    optional_packages = [
        ("croniter", "Croniter (cron 表达式)"),
        ("telegram", "python-telegram-bot"),
        ("discord", "discord.py"),
    ]
    
    for module, name in required_packages:
        try:
            __import__(module)
            check_ok(name)
        except ImportError:
            check_fail(name, "(缺失)")
            issues.append(f"安装 {name}: {_python_install_cmd()} {module}")
    
    for module, name in optional_packages:
        try:
            __import__(module)
            check_ok(name, "(可选)")
        except ImportError:
            check_warn(name, "(可选，未安装)")
    
    # =========================================================================
    # 检查：配置文件
    # =========================================================================
    print()
    print(color("◆ 配置文件", Colors.CYAN, Colors.BOLD))
    
    # 检查 ~/.hermes/.env（用户配置的主要位置）
    env_path = HERMES_HOME / '.env'
    if env_path.exists():
        check_ok(f"{_DHH}/.env 文件存在")
        
        # 检查常见问题。将编码固定为 UTF-8，因为 .env 文件在代码库中各处都写为 UTF-8，而 Path.read_text()
        # 默认使用系统区域设置——这会在非 UTF-8 Windows 区域设置（例如 GBK）下，一旦文件包含任何非 ASCII 字节时立即崩溃。
        content = env_path.read_text(encoding="utf-8")
        if _has_provider_env_config(content):
            check_ok("API 密钥或自定义端点已配置")
        else:
            check_warn(f"{_DHH}/.env 中未找到 API 密钥")
            issues.append("运行 'hermes setup' 来配置 API 密钥")
    else:
        # 也检查项目根目录作为回退
        fallback_env = PROJECT_ROOT / '.env'
        if fallback_env.exists():
            check_ok(".env 文件存在（在项目目录中）")
        else:
            check_fail(f"{_DHH}/.env 文件缺失")
            if should_fix:
                env_path.parent.mkdir(parents=True, exist_ok=True)
                env_path.touch()
                check_ok(f"已创建空的 {_DHH}/.env")
                check_info("运行 'hermes setup' 来配置 API 密钥")
                fixed_count += 1
            else:
                check_info("运行 'hermes setup' 来创建一个")
                issues.append("运行 'hermes setup' 来创建 .env")
    
    # 检查 ~/.hermes/config.yaml（主要）或项目 cli-config.yaml（回退）
    config_path = HERMES_HOME / 'config.yaml'
    if config_path.exists():
        check_ok(f"{_DHH}/config.yaml 存在")

        # 验证 model.provider 和 model.default 值
        try:
            import yaml as _yaml
            cfg = _yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            model_section = cfg.get("model") or {}
            provider_raw = (model_section.get("provider") or "").strip()
            provider = provider_raw.lower()
            default_model = (model_section.get("default") or model_section.get("model") or "").strip()

            known_providers: set = set()
            try:
                from hermes_cli.auth import (
                    PROVIDER_REGISTRY,
                    resolve_provider as _resolve_auth_provider,
                )
                known_providers = set(PROVIDER_REGISTRY.keys()) | {"openrouter", "custom", "auto"}
            except Exception:
                _resolve_auth_provider = None
                pass
            try:
                from hermes_cli.config import get_compatible_custom_providers as _compatible_custom_providers
                from hermes_cli.providers import (
                    normalize_provider as _normalize_catalog_provider,
                    resolve_provider_full as _resolve_provider_full,
                )
            except Exception:
                _compatible_custom_providers = None
                _normalize_catalog_provider = None
                _resolve_provider_full = None

            custom_providers = []
            if _compatible_custom_providers is not None:
                try:
                    custom_providers = _compatible_custom_providers(cfg)
                except Exception:
                    custom_providers = []

            user_providers = cfg.get("providers")
            if isinstance(user_providers, dict):
                known_providers.update(str(name).strip().lower() for name in user_providers if str(name).strip())
            for entry in custom_providers:
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("name") or "").strip()
                if name:
                    known_providers.add("custom:" + name.lower().replace(" ", "-"))

            valid_provider_ids = set(known_providers)
            provider_ids_to_accept = {provider} if provider else set()
            if _normalize_catalog_provider is not None:
                for known_provider in known_providers:
                    try:
                        valid_provider_ids.add(_normalize_catalog_provider(known_provider))
                    except Exception:
                        continue

            runtime_provider = provider
            if (
                provider
                and _resolve_auth_provider is not None
                and provider not in {"auto", "custom"}
            ):
                try:
                    runtime_provider = _resolve_auth_provider(provider)
                    provider_ids_to_accept.add(runtime_provider)
                except Exception:
                    runtime_provider = provider

            catalog_provider = provider
            if (
                provider
                and _resolve_provider_full is not None
                and provider not in {"auto", "custom"}
            ):
                provider_def = _resolve_provider_full(provider, user_providers, custom_providers)
                catalog_provider = provider_def.id if provider_def is not None else None
                if catalog_provider is not None:
                    provider_ids_to_accept.add(catalog_provider)

            if provider and provider != "auto":
                if catalog_provider is None or (
                    known_providers
                    and not (provider_ids_to_accept & valid_provider_ids)
                ):
                    known_list = ", ".join(sorted(known_providers)) if known_providers else "(不可用)"
                    check_fail(
                        f"model.provider '{provider_raw}' 不是可识别的提供商",
                        f"(已知: {known_list})",
                    )
                    issues.append(
                        f"model.provider '{provider_raw}' 未知。 "
                        f"有效提供商: {known_list}。 "
                        f"修复: 运行 'hermes config set model.provider <valid_provider>'"
                    )

            # 如果模型设置为使用提供商前缀的名称，而该提供商不使用它们，则发出警告
            provider_for_policy = runtime_provider or catalog_provider
            providers_accepting_vendor_slugs = {
                "openrouter",
                "custom",
                "auto",
                "ai-gateway",
                "kilocode",
                "opencode-zen",
                "huggingface",
                "lmstudio",
                "nous",
            }
            if (
                default_model
                and "/" in default_model
                and provider_for_policy
                and provider_for_policy not in providers_accepting_vendor_slugs
            ):
                check_warn(
                    f"model.default '{default_model}' 使用供应商/模型 slug，但提供商是 '{provider_raw}'",
                    "(供应商前缀的 slug 属于聚合器如 openrouter)",
                )
                issues.append(
                    f"model.default '{default_model}' 有供应商前缀，但 model.provider 是 '{provider_raw}'。 "
                    "要么将 model.provider 设置为 'openrouter'，要么去掉供应商前缀。"
                )

            # 检查已配置提供商的凭据。
            # 仅限于 PROVIDER_REGISTRY 中的 API 密钥提供商——其他提供商类型（OAuth、SDK、openrouter/anthropic/custom/auto）在 doctor 的其他地方有自己的环境变量检查，
            # 并且 get_auth_status() 对于任何它未明确分派的内容返回一个空的 {logged_in: False}，这会产生误报。
            if runtime_provider and runtime_provider not in {"auto", "custom", "openrouter"}:
                try:
                    from hermes_cli.auth import PROVIDER_REGISTRY, get_auth_status
                    pconfig = PROVIDER_REGISTRY.get(runtime_provider)
                    if pconfig and getattr(pconfig, "auth_type", "") == "api_key":
                        status = get_auth_status(runtime_provider) or {}
                        configured = bool(
                            status.get("configured")
                            or status.get("logged_in")
                            or status.get("api_key")
                        )
                        if not configured:
                            check_fail(
                                f"model.provider '{runtime_provider}' 已设置但未配置 API 密钥",
                                "(检查 ~/.hermes/.env 或运行 'hermes setup')",
                            )
                            issues.append(
                                f"未找到提供商 '{runtime_provider}' 的凭据。 "
                                f"运行 'hermes setup' 或在 {_DHH}/.env 中设置该提供商的 API 密钥， "
                                f"或使用 'hermes config set model.provider <name>' 切换提供商"
                            )
                except Exception:
                    pass

        except Exception as e:
            check_warn("无法验证模型/提供商配置", f"({e})")
    else:
        fallback_config = PROJECT_ROOT / 'cli-config.yaml'
        if fallback_config.exists():
            check_ok("cli-config.yaml 存在（在项目目录中）")
        else:
            if should_fix:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                example_config = PROJECT_ROOT / 'cli-config.yaml.example'
                if example_config.exists():
                    shutil.copy2(str(example_config), str(config_path))
                    check_ok(f"从 cli-config.yaml.example 创建了 {_DHH}/config.yaml")
                else:
                    from hermes_cli.config import DEFAULT_CONFIG, save_config
                    save_config(DEFAULT_CONFIG)
                    check_ok(f"从默认值创建了 {_DHH}/config.yaml")
                fixed_count += 1
            else:
                check_warn("未找到 config.yaml", "(使用默认值)")

    # 检查配置版本和过时键
    config_path = HERMES_HOME / 'config.yaml'
    if config_path.exists():
        try:
            from hermes_cli.config import check_config_version, migrate_config
            current_ver, latest_ver = check_config_version()
            if current_ver < latest_ver:
                check_warn(
                    f"配置版本过时 (v{current_ver} → v{latest_ver})",
                    "(有新设置可用)"
                )
                if should_fix:
                    try:
                        migrate_config(interactive=False, quiet=False)
                        check_ok("配置已迁移到最新版本")
                        fixed_count += 1
                    except Exception as mig_err:
                        check_warn(f"自动迁移失败: {mig_err}")
                        issues.append("运行 'hermes setup' 来迁移配置")
                else:
                    issues.append("运行 'hermes doctor --fix' 或 'hermes setup' 来迁移配置")
            else:
                check_ok(f"配置版本是最新的 (v{current_ver})")
        except Exception:
            pass

        # 检测过时的根级模型键（已知错误来源——PR #4329）
        try:
            import yaml
            with open(config_path, encoding="utf-8") as f:
                raw_config = yaml.safe_load(f) or {}
            stale_root_keys = [k for k in ("provider", "base_url") if k in raw_config and isinstance(raw_config[k], str)]
            if stale_root_keys:
                check_warn(
                    f"过时的根级配置键: {', '.join(stale_root_keys)}",
                    "(应放在 'model:' 部分下)"
                )
                if should_fix:
                    model_section = raw_config.setdefault("model", {})
                    for k in stale_root_keys:
                        if not model_section.get(k):
                            model_section[k] = raw_config.pop(k)
                        else:
                            raw_config.pop(k)
                    from utils import atomic_yaml_write
                    atomic_yaml_write(config_path, raw_config)
                    check_ok("已将过时的根级键迁移到模型部分")
                    fixed_count += 1
                else:
                    issues.append("config.yaml 中有过时的根级 provider/base_url — 运行 'hermes doctor --fix'")
        except Exception:
            pass

        # 验证配置结构（捕获格式错误的 custom_providers 等）
        try:
            from hermes_cli.config import validate_config_structure
            config_issues = validate_config_structure()
            if config_issues:
                print()
                print(color("◆ 配置结构", Colors.CYAN, Colors.BOLD))
                for ci in config_issues:
                    if ci.severity == "error":
                        check_fail(ci.message)
                    else:
                        check_warn(ci.message)
                    # 缩进显示提示
                    for hint_line in ci.hint.splitlines():
                        check_info(hint_line)
                    issues.append(ci.message)
        except Exception:
            pass

    # =========================================================================
    # 检查：认证提供商
    # =========================================================================
    print()
    print(color("◆ 认证提供商", Colors.CYAN, Colors.BOLD))

    try:
        from hermes_cli.auth import (
            get_nous_auth_status,
            get_codex_auth_status,
            get_gemini_oauth_auth_status,
            get_minimax_oauth_auth_status,
        )

        nous_status = get_nous_auth_status()
        if nous_status.get("logged_in"):
            check_ok("Nous Portal 认证", "(已登录)")
        else:
            check_warn("Nous Portal 认证", "(未登录)")

        codex_status = get_codex_auth_status()
        if codex_status.get("logged_in"):
            check_ok("OpenAI Codex 认证", "(已登录)")
        else:
            check_warn("OpenAI Codex 认证", "(未登录)")
            if codex_status.get("error"):
                check_info(codex_status["error"])

        gemini_status = get_gemini_oauth_auth_status()
        if gemini_status.get("logged_in"):
            email = gemini_status.get("email") or ""
            project = gemini_status.get("project_id") or ""
            pieces = []
            if email:
                pieces.append(email)
            if project:
                pieces.append(f"project={project}")
            suffix = f" ({', '.join(pieces)})" if pieces else ""
            check_ok("Google Gemini OAuth", f"(已登录{suffix})")
        else:
            check_warn("Google Gemini OAuth", "(未登录)")

        minimax_status = get_minimax_oauth_auth_status()
        if minimax_status.get("logged_in"):
            region = minimax_status.get("region", "global")
            check_ok("MiniMax OAuth", f"(已登录, region={region})")
        else:
            check_warn("MiniMax OAuth", "(未登录)")
    except Exception as e:
        check_warn("认证提供商状态", f"(无法检查: {e})")

    if _safe_which("codex"):
        check_ok("codex CLI")
    else:
        # 原生 OAuth 使用 Hermes 自己的设备代码流——Codex CLI 仅在你想从 ~/.codex/auth.json 导入现有令牌时才需要。
        # 降级为 info，以便运行 `hermes auth openai-codex` 的用户不会被告知他们缺少某些东西。
        check_info(
            "未安装 codex CLI "
            "(可选——仅当需要从现有的 Codex CLI 登录导入令牌时才需要)"
        )

    # =========================================================================
    # 检查：目录结构
    # =========================================================================
    print()
    print(color("◆ 目录结构", Colors.CYAN, Colors.BOLD))
    
    hermes_home = HERMES_HOME
    if hermes_home.exists():
        check_ok(f"{_DHH} 目录存在")
    elif should_fix:
        hermes_home.mkdir(parents=True, exist_ok=True)
        check_ok(f"已创建 {_DHH} 目录")
        fixed_count += 1
    else:
        check_warn(f"未找到 {_DHH}", "(将在首次使用时创建)")
    
    # 检查预期的子目录
    expected_subdirs = ["cron", "sessions", "logs", "skills", "memories"]
    for subdir_name in expected_subdirs:
        subdir_path = hermes_home / subdir_name
        if subdir_path.exists():
            check_ok(f"{_DHH}/{subdir_name}/ 存在")
        elif should_fix:
            subdir_path.mkdir(parents=True, exist_ok=True)
            check_ok(f"已创建 {_DHH}/{subdir_name}/")
            fixed_count += 1
        else:
            check_warn(f"未找到 {_DHH}/{subdir_name}/", "(将在首次使用时创建)")
    
    # 检查 SOUL.md 人格文件
    soul_path = hermes_home / "SOUL.md"
    if soul_path.exists():
        content = soul_path.read_text(encoding="utf-8").strip()
        # 检查是否只是模板注释（无实际内容）
        lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith(("<!--", "-->", "#"))]
        if lines:
            check_ok(f"{_DHH}/SOUL.md 存在（人格已配置）")
        else:
            check_info(f"{_DHH}/SOUL.md 存在但为空——编辑它以自定义个性")
    else:
        check_warn(f"未找到 {_DHH}/SOUL.md", "(创建它来给 Hermes 一个自定义人格)")
        if should_fix:
            soul_path.parent.mkdir(parents=True, exist_ok=True)
            soul_path.write_text(
                "# Hermes Agent 人格\n\n"
                "<!-- 编辑此文件以自定义 Hermes 的交流方式。 -->\n\n"
                "你是 Hermes，一个乐于助人的 AI 助手。\n",
                encoding="utf-8",
            )
            check_ok(f"已创建 {_DHH}/SOUL.md 并带有基本模板")
            fixed_count += 1
    
    # 检查记忆目录
    memories_dir = hermes_home / "memories"
    if memories_dir.exists():
        check_ok(f"{_DHH}/memories/ 目录存在")
        memory_file = memories_dir / "MEMORY.md"
        user_file = memories_dir / "USER.md"
        if memory_file.exists():
            size = len(memory_file.read_text(encoding="utf-8").strip())
            check_ok(f"MEMORY.md 存在 ({size} 字符)")
        else:
            check_info("MEMORY.md 尚未创建（将在 Agent 首次写入记忆时创建）")
        if user_file.exists():
            size = len(user_file.read_text(encoding="utf-8").strip())
            check_ok(f"USER.md 存在 ({size} 字符)")
        else:
            check_info("USER.md 尚未创建（将在 Agent 首次写入记忆时创建）")
    else:
        check_warn(f"未找到 {_DHH}/memories/", "(将在首次使用时创建)")
        if should_fix:
            memories_dir.mkdir(parents=True, exist_ok=True)
            check_ok(f"已创建 {_DHH}/memories/")
            fixed_count += 1
    
    # 检查 SQLite 会话存储
    state_db_path = hermes_home / "state.db"
    if state_db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(state_db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            conn.close()
            check_ok(f"{_DHH}/state.db 存在 ({count} 个会话)")
        except Exception as e:
            check_warn(f"{_DHH}/state.db 存在但有问题: {e}")
    else:
        check_info(f"{_DHH}/state.db 尚未创建（将在首次会话时创建）")

    # 检查 WAL 文件大小（无限制增长表示错过了检查点）
    wal_path = hermes_home / "state.db-wal"
    if wal_path.exists():
        try:
            wal_size = wal_path.stat().st_size
            if wal_size > 50 * 1024 * 1024:  # 50 MB
                check_warn(
                    f"WAL 文件很大 ({wal_size // (1024*1024)} MB)",
                    "(可能表示错过了检查点)"
                )
                if should_fix:
                    import sqlite3
                    conn = sqlite3.connect(str(state_db_path))
                    conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                    conn.close()
                    new_size = wal_path.stat().st_size if wal_path.exists() else 0
                    check_ok(f"已执行 WAL 检查点 ({wal_size // 1024}K → {new_size // 1024}K)")
                    fixed_count += 1
                else:
                    issues.append("WAL 文件很大 — 运行 'hermes doctor --fix' 来执行检查点")
            elif wal_size > 10 * 1024 * 1024:  # 10 MB
                check_info(f"WAL 文件是 {wal_size // (1024*1024)} MB（对于活跃会话是正常的）")
        except Exception:
            pass

    _check_gateway_service_linger(issues)

    # =========================================================================
    # 检查：命令安装（hermes bin 符号链接）
    # =========================================================================
    if sys.platform != "win32":
        print()
        print(color("◆ 命令安装", Colors.CYAN, Colors.BOLD))

        # 确定 venv 入口点位置
        _venv_bin = None
        for _venv_name in ("venv", ".venv"):
            _candidate = PROJECT_ROOT / _venv_name / "bin" / "hermes"
            if _candidate.exists():
                _venv_bin = _candidate
                break

        # 确定预期的命令链接目录（镜像 install.sh 逻辑）
        _prefix = os.environ.get("PREFIX", "")
        _is_termux_env = bool(os.environ.get("TERMUX_VERSION")) or "com.termux/files/usr" in _prefix
        if _is_termux_env and _prefix:
            _cmd_link_dir = Path(_prefix) / "bin"
            _cmd_link_display = "$PREFIX/bin"
        else:
            _cmd_link_dir = Path.home() / ".local" / "bin"
            _cmd_link_display = "~/.local/bin"
        _cmd_link = _cmd_link_dir / "hermes"

        if _venv_bin is None:
            check_warn(
                "未找到 Venv 入口点",
                "(hermes 不在 venv/bin/ 或 .venv/bin/ 中 — 使用 pip install -e '.[all]' 重新安装)"
            )
            manual_issues.append(
                f"重新安装入口点: cd {PROJECT_ROOT} && source venv/bin/activate && pip install -e '.[all]'"
            )
        else:
            check_ok(f"Venv 入口点存在 ({_venv_bin.relative_to(PROJECT_ROOT)})")

            # 检查命令链接位置的符号链接
            if _cmd_link.is_symlink():
                _target = _cmd_link.resolve()
                _expected = _venv_bin.resolve()
                if _target == _expected:
                    check_ok(f"{_cmd_link_display}/hermes → 正确目标")
                else:
                    check_warn(
                        f"{_cmd_link_display}/hermes 指向错误目标",
                        f"(→ {_target}, 期望 → {_expected})"
                    )
                    if should_fix:
                        _cmd_link.unlink()
                        _cmd_link.symlink_to(_venv_bin)
                        check_ok(f"已修复符号链接: {_cmd_link_display}/hermes → {_venv_bin}")
                        fixed_count += 1
                    else:
                        issues.append(f"{_cmd_link_display}/hermes 处的符号链接损坏 — 运行 'hermes doctor --fix'")
            elif _cmd_link.exists():
                # 它是常规文件，不是符号链接——可能是包装脚本
                check_ok(f"{_cmd_link_display}/hermes 存在（非符号链接）")
            else:
                check_fail(
                    f"未找到 {_cmd_link_display}/hermes",
                    "(hermes 命令在 venv 外可能无法工作)"
                )
                if should_fix:
                    _cmd_link_dir.mkdir(parents=True, exist_ok=True)
                    _cmd_link.symlink_to(_venv_bin)
                    check_ok(f"已创建符号链接: {_cmd_link_display}/hermes → {_venv_bin}")
                    fixed_count += 1

                    # 检查链接目录是否在 PATH 上
                    _path_dirs = os.environ.get("PATH", "").split(os.pathsep)
                    if str(_cmd_link_dir) not in _path_dirs:
                        check_warn(
                            f"{_cmd_link_display} 不在你的 PATH 上",
                            "(将其添加到你的 shell 配置: export PATH=\"$HOME/.local/bin:$PATH\")"
                        )
                        manual_issues.append(f"将 {_cmd_link_display} 添加到你的 PATH")
                else:
                    issues.append(f"缺少 {_cmd_link_display}/hermes 符号链接 — 运行 'hermes doctor --fix'")

    # =========================================================================
    # 检查：外部工具
    # =========================================================================
    print()
    print(color("◆ 外部工具", Colors.CYAN, Colors.BOLD))
    
    # Git
    if _safe_which("git"):
        check_ok("git")
    else:
        check_warn("未找到 git", "(可选)")
    
    # ripgrep（可选，用于更快的文件搜索）
    if _safe_which("rg"):
        check_ok("ripgrep (rg)", "(更快的文件搜索)")
    else:
        check_warn("未找到 ripgrep (rg)", "(文件搜索使用 grep 回退)")
        check_info(f"安装以获得更快搜索: {_system_package_install_cmd('ripgrep')}")
    
    # Docker（可选）
    terminal_env = os.getenv("TERMINAL_ENV", "local")
    if terminal_env == "docker":
        if _safe_which("docker"):
            # 检查 docker 守护进程是否正在运行
            try:
                result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
            except subprocess.TimeoutExpired:
                result = None
            if result is not None and result.returncode == 0:
                check_ok("docker", "(守护进程正在运行)")
            else:
                check_fail("docker 守护进程未运行")
                issues.append("启动 Docker 守护进程")
        else:
            check_fail("未找到 docker", "(TERMINAL_ENV=docker 时需要)")
            issues.append("安装 Docker 或更改 TERMINAL_ENV")
    elif _safe_which("docker"):
        check_ok("docker", "(可选)")
    elif _is_termux():
        check_info("Docker 后端在 Termux 内不可用（在 Android 上是预期的）")
    else:
        check_warn("未找到 docker", "(可选)")
    
    # SSH（如果使用 ssh 后端）
    if terminal_env == "ssh":
        ssh_host = os.getenv("TERMINAL_SSH_HOST")
        if ssh_host:
            # 尝试连接
            try:
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", ssh_host, "echo ok"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            except subprocess.TimeoutExpired:
                result = None
            if result is not None and result.returncode == 0:
                check_ok(f"SSH 连接到 {ssh_host}")
            else:
                check_fail(f"SSH 连接到 {ssh_host}")
                issues.append(f"检查 {ssh_host} 的 SSH 配置")
        else:
            check_fail("未设置 TERMINAL_SSH_HOST", "(TERMINAL_ENV=ssh 时需要)")
            issues.append("在 .env 中设置 TERMINAL_SSH_HOST")
    
    # Daytona（如果使用 daytona 后端）
    if terminal_env == "daytona":
        daytona_key = os.getenv("DAYTONA_API_KEY")
        if daytona_key:
            check_ok("Daytona API 密钥", "(已配置)")
        else:
            check_fail("未设置 DAYTONA_API_KEY", "(TERMINAL_ENV=daytona 时需要)")
            issues.append("设置 DAYTONA_API_KEY 环境变量")
        try:
            from daytona import Daytona  # noqa: F401 — SDK 存在性检查
            check_ok("daytona SDK", "(已安装)")
        except ImportError:
            check_fail("未安装 daytona SDK", "(pip install daytona)")
            issues.append("安装 daytona SDK: pip install daytona")

    # Vercel Sandbox（如果使用 vercel_sandbox 后端）
    if terminal_env == "vercel_sandbox":
        runtime = os.getenv("TERMINAL_VERCEL_RUNTIME", "node24").strip() or "node24"
        from tools.terminal_tool import _SUPPORTED_VERCEL_RUNTIMES
        if runtime in _SUPPORTED_VERCEL_RUNTIMES:
            check_ok("Vercel 运行时", f"({runtime})")
        else:
            supported = ", ".join(_SUPPORTED_VERCEL_RUNTIMES)
            check_fail("Vercel 运行时不受支持", f"({runtime}; 使用 {supported})")
            issues.append(f"将 TERMINAL_VERCEL_RUNTIME 设置为其中之一: {supported}")

        disk = os.getenv("TERMINAL_CONTAINER_DISK", "51200").strip()
        if disk in {"", "0", "51200"}:
            check_ok("Vercel 磁盘设置", "(使用平台默认值)")
        else:
            check_fail("Vercel 自定义磁盘不受支持", "(将 terminal.container_disk 重置为 51200)")
            issues.append("Vercel Sandbox 不支持自定义 container_disk；使用共享默认值 51200")

        if importlib.util.find_spec("vercel") is not None:
            check_ok("vercel SDK", "(已安装)")
        else:
            check_fail("未安装 vercel SDK", "(pip install 'hermes-agent[vercel]')")
            issues.append("安装 Vercel 可选依赖: pip install 'hermes-agent[vercel]'")

        auth_status = describe_vercel_auth()
        if auth_status.ok:
            check_ok("Vercel 认证", f"({auth_status.label})")
        elif auth_status.label.startswith("partial"):
            check_fail("Vercel 认证不完整", f"({auth_status.label})")
            issues.append("一起设置 VERCEL_TOKEN、VERCEL_PROJECT_ID 和 VERCEL_TEAM_ID")
        else:
            check_fail("Vercel 认证未配置", f"({auth_status.label})")
            issues.append(
                "使用 VERCEL_TOKEN、VERCEL_PROJECT_ID 和 VERCEL_TEAM_ID 配置 Vercel Sandbox 认证"
            )
        for line in auth_status.detail_lines:
            check_info(f"Vercel 认证 {line}")

        persistent = os.getenv("TERMINAL_CONTAINER_PERSISTENT", "true").lower() in {"1", "true", "yes", "on"}
        if persistent:
            check_info("Vercel 持久性: 仅快照文件系统；实时进程在沙盒重建后无法存活")
        else:
            check_info("Vercel 持久性: 临时文件系统")

    # Node.js + agent-browser（用于浏览器自动化工具）
    if _safe_which("node"):
        check_ok("Node.js")
        # 检查是否安装了 agent-browser
        agent_browser_path = PROJECT_ROOT / "node_modules" / "agent-browser"
        agent_browser_ok = False
        if agent_browser_path.exists():
            check_ok("agent-browser (Node.js)", "(浏览器自动化)")
            agent_browser_ok = True
        elif shutil.which("agent-browser"):
            check_ok("agent-browser", "(浏览器自动化)")
            agent_browser_ok = True
        elif _is_termux():
            check_info("未安装 agent-browser（在测试的 Termux 路径中是预期的）")
            check_info("稍后手动安装: npm install -g agent-browser && agent-browser install")
            check_info("Termux 浏览器设置:")
            for step in _termux_browser_setup_steps(node_installed=True):
                check_info(step)
        else:
            check_warn("未安装 agent-browser", "(运行: npm install)")

        # Chromium 存在性——当找到 agent-browser 但磁盘上没有 Playwright 管理的 Chromium 时，浏览器工具会静默失败注册
        # (tools/browser_tool.py::check_browser_requirements 在 Agent 看到它们之前将其过滤掉)。重用它使用的确切谓词，以便两个检查不会产生分歧。
        # 在 Termux 上跳过（不是测试路径）。
        if agent_browser_ok and not _is_termux():
            try:
                # 延迟导入: browser_tool 是一个约 150KB 的模块，我们不想在每次 `hermes doctor` 调用时都急切加载。
                from tools.browser_tool import (
                    _chromium_installed,
                    _is_camofox_mode,
                    _get_cloud_provider,
                    _get_cdp_override,
                    _using_lightpanda_engine,
                )
            except Exception:
                # 如果 browser_tool 甚至无法导入，那是其他地方会出现的单独错误；不要让 doctor 崩溃。
                pass
            else:
                # 仅当已安装的引擎实际需要 Chromium 时才发出警告: Camofox、CDP 覆盖、云提供商或 Lightpanda 都绕过了本地 Chromium 要求。
                skip_chromium_check = (
                    _is_camofox_mode()
                    or bool(_get_cdp_override())
                    or _get_cloud_provider() is not None
                    or _using_lightpanda_engine()
                )
                if not skip_chromium_check:
                    if _chromium_installed():
                        check_ok("Playwright Chromium", "(浏览器引擎)")
                    else:
                        check_warn(
                            "未安装 Playwright Chromium",
                            "(browser_* 工具将对 Agent 隐藏)",
                        )
                        if sys.platform == "win32":
                            check_info(
                                f"安装: cd {PROJECT_ROOT} && "
                                "npx playwright install chromium"
                            )
                        else:
                            check_info(
                                f"安装: cd {PROJECT_ROOT} && "
                                "npx playwright install --with-deps chromium"
                            )
    elif _is_termux():
        check_info("未找到 Node.js（在测试的 Termux 路径中浏览器工具是可选的）")
        check_info("在 Termux 上安装 Node.js: pkg install nodejs")
        check_info("Termux 浏览器设置:")
        for step in _termux_browser_setup_steps(node_installed=False):
            check_info(step)
    else:
        check_warn("未找到 Node.js", "(可选，浏览器工具需要)")
    
    # 对所有 Node.js 包进行 npm audit
    _npm_bin = _safe_which("npm")
    if _npm_bin:
        npm_dirs = [
            (PROJECT_ROOT, "浏览器工具 (agent-browser)"),
            (PROJECT_ROOT / "scripts" / "whatsapp-bridge", "WhatsApp 桥接"),
        ]
        for npm_dir, label in npm_dirs:
            if not (npm_dir / "node_modules").exists():
                continue
            try:
                # 使用解析的绝对路径，以便 Windows 可以执行 npm.cmd（CreateProcessW 无法运行裸的 .cmd 名称）。
                audit_result = subprocess.run(
                    [_npm_bin, "audit", "--json"],
                    cwd=str(npm_dir),
                    capture_output=True, text=True, timeout=30,
                )
                import json as _json
                audit_data = _json.loads(audit_result.stdout) if audit_result.stdout.strip() else {}
                vuln_count = audit_data.get("metadata", {}).get("vulnerabilities", {})
                critical = vuln_count.get("critical", 0)
                high = vuln_count.get("high", 0)
                moderate = vuln_count.get("moderate", 0)
                total = critical + high + moderate
                if total == 0:
                    check_ok(f"{label} 依赖", "(无已知漏洞)")
                elif critical > 0 or high > 0:
                    check_warn(
                        f"{label} 依赖",
                        f"({critical} 个严重, {high} 个高危, {moderate} 个中危 — 运行: cd {npm_dir} && npm audit fix)"
                    )
                    issues.append(
                        f"{label} 有 {total} 个 npm "
                        f"{'漏洞' if total == 1 else '漏洞'}"
                    )
                else:
                    check_ok(
                        f"{label} 依赖",
                        f"({moderate} 个中危 "
                        f"{'漏洞' if moderate == 1 else '漏洞'})",
                    )
            except Exception:
                pass

    if _is_termux():
        check_info("Termux 兼容性回退:")
        for note in _termux_install_all_fallback_notes():
            check_info(note)

    # =========================================================================
    # 检查：API 连接性
    # =========================================================================
    print()
    print(color("◆ API 连接性", Colors.CYAN, Colors.BOLD))

    # 重构: 下面的每个连接性探测都是 HTTP 绑定的且完全独立的。在典型工作站上，串行运行它们花费约 5 秒墙钟时间（其中 2 秒是 boto3 的 IMDS 查找 AWS 凭据，除非你实际在 EC2 上，否则会超时）。
    # 使用小型执行器池对它们进行线程化，将该部分压缩到大约最慢的单个探测时间——约 2 秒——而不改变输出格式。
    #
    # 每个 ``_probe_*`` 辅助函数都是纯函数: 接受其输入，进行一次 HTTP/SDK 调用，返回一个 ``_ConnectivityResult``，携带要打印的行和要追加的任何问题字符串。
    # 无全局变量，无共享可变状态，无在 worker 内部打印。
    import concurrent.futures as _futures
    from collections import namedtuple as _namedtuple

    _ConnectivityResult = _namedtuple(
        "_ConnectivityResult", ["label", "lines", "issues"]
    )
    _probes: list = []  # 按显示顺序提交的 (label, callable) 列表

    def _probe_openrouter() -> _ConnectivityResult:
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            return _ConnectivityResult(
                "OpenRouter API",
                [(color("⚠", Colors.YELLOW), "OpenRouter API",
                  color("(未配置)", Colors.DIM))],
                [],
            )
        try:
            import httpx
            r = httpx.get(
                OPENROUTER_MODELS_URL,
                headers={"Authorization": f"Bearer {key}"},
                timeout=10,
            )
            if r.status_code == 200:
                return _ConnectivityResult(
                    "OpenRouter API",
                    [(color("✓", Colors.GREEN), "OpenRouter API", "")],
                    [],
                )
            if r.status_code == 401:
                return _ConnectivityResult(
                    "OpenRouter API",
                    [(color("✗", Colors.RED), "OpenRouter API",
                      color("(无效的 API 密钥)", Colors.DIM))],
                    ["检查 .env 中的 OPENROUTER_API_KEY"],
                )
            if r.status_code == 402:
                return _ConnectivityResult(
                    "OpenRouter API",
                    [(color("✗", Colors.RED), "OpenRouter API",
                      color("(积分不足 — 需要付款)", Colors.DIM))],
                    ["OpenRouter 账户积分不足。 "
                     "修复: 运行 'hermes config set model.provider <provider>' "
                     "以切换提供商，或在 https://openrouter.ai/settings/credits 为你的 OpenRouter 账户充值"],
                )
            if r.status_code == 429:
                return _ConnectivityResult(
                    "OpenRouter API",
                    [(color("✗", Colors.RED), "OpenRouter API",
                      color("(速率受限)", Colors.DIM))],
                    ["OpenRouter 速率限制已触发 — 考虑切换到不同的提供商或等待"],
                )
            return _ConnectivityResult(
                "OpenRouter API",
                [(color("✗", Colors.RED), "OpenRouter API",
                  color(f"(HTTP {r.status_code})", Colors.DIM))],
                [],
            )
        except Exception as e:
            return _ConnectivityResult(
                "OpenRouter API",
                [(color("✗", Colors.RED), "OpenRouter API",
                  color(f"({e})", Colors.DIM))],
                ["检查网络连接性"],
            )

    def _probe_anthropic() -> _ConnectivityResult:
        from hermes_cli.auth import get_anthropic_key
        key = get_anthropic_key()
        if not key:
            return _ConnectivityResult("Anthropic API", [], [])
        try:
            import httpx
            from agent.anthropic_adapter import (
                _is_oauth_token,
                _COMMON_BETAS,
                _OAUTH_ONLY_BETAS,
                _CONTEXT_1M_BETA,
            )
            headers = {"anthropic-version": "2023-06-01"}
            is_oauth = _is_oauth_token(key)
            if is_oauth:
                headers["Authorization"] = f"Bearer {key}"
                headers["anthropic-beta"] = ",".join(_COMMON_BETAS + _OAUTH_ONLY_BETAS)
            else:
                headers["x-api-key"] = key
            r = httpx.get(
                "https://api.anthropic.com/v1/models",
                headers=headers, timeout=10,
            )
            # 反应性恢复: 没有 1M 上下文的 OAuth 订阅会以 400 "long context beta is not yet available for this subscription" 拒绝请求。
            # 重试一次，去掉该 beta，以便 doctor 检查不会错误地报告 Anthropic 不可达。
            if (
                is_oauth
                and r.status_code == 400
                and "long context beta" in r.text.lower()
                and "not yet available" in r.text.lower()
            ):
                headers["anthropic-beta"] = ",".join(
                    [b for b in _COMMON_BETAS if b != _CONTEXT_1M_BETA]
                    + list(_OAUTH_ONLY_BETAS)
                )
                r = httpx.get(
                    "https://api.anthropic.com/v1/models",
                    headers=headers, timeout=10,
                )
            if r.status_code == 200:
                return _ConnectivityResult(
                    "Anthropic API",
                    [(color("✓", Colors.GREEN), "Anthropic API", "")],
                    [],
                )
            if r.status_code == 401:
                return _ConnectivityResult(
                    "Anthropic API",
                    [(color("✗", Colors.RED), "Anthropic API",
                      color("(无效的 API 密钥)", Colors.DIM))],
                    [],
                )
            return _ConnectivityResult(
                "Anthropic API",
                [(color("⚠", Colors.YELLOW), "Anthropic API",
                  color("(无法验证)", Colors.DIM))],
                [],
            )
        except Exception as e:
            return _ConnectivityResult(
                "Anthropic API",
                [(color("⚠", Colors.YELLOW), "Anthropic API",
                  color(f"({e})", Colors.DIM))],
                [],
            )

    def _probe_apikey_provider(pname, env_vars, default_url, base_env,
                               supports_health_check) -> _ConnectivityResult:
        key = ""
        for ev in env_vars:
            key = os.getenv(ev, "")
            if key:
                break
        if not key:
            return _ConnectivityResult(pname, [], [])
        label = pname.ljust(20)
        if not supports_health_check:
            return _ConnectivityResult(
                pname,
                [(color("✓", Colors.GREEN), label,
                  color("(密钥已配置)", Colors.DIM))],
                [],
            )
        try:
            import httpx
            base = os.getenv(base_env, "") if base_env else ""
            # 自动检测 Kimi Code 密钥 (sk-kimi-) → api.kimi.com/coding/v1
            # (OpenAI 兼容接口，它暴露 /models 用于健康检查)。
            if not base and key.startswith("sk-kimi-"):
                base = "https://api.kimi.com/coding/v1"
            # Anthropic 兼容端点 (/anthropic, api.kimi.com/coding 没有 /v1) 不支持 /models。重写到 OpenAI 兼容的 /v1 接口进行健康检查。
            if base and base.rstrip("/").endswith("/anthropic"):
                from agent.auxiliary_client import _to_openai_base_url
                base = _to_openai_base_url(base)
            if base_url_host_matches(base, "api.kimi.com") and base.rstrip("/").endswith("/coding"):
                base = base.rstrip("/") + "/v1"
            url = (base.rstrip("/") + "/models") if base else default_url
            headers = {
                "Authorization": f"Bearer {key}",
                "User-Agent": _HERMES_USER_AGENT,
            }
            if base_url_host_matches(base, "api.kimi.com"):
                headers["User-Agent"] = "claude-code/0.1.0"
            r = httpx.get(url, headers=headers, timeout=10)
            if (
                pname == "Alibaba/DashScope"
                and not base
                and r.status_code == 401
            ):
                r = httpx.get(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
                    headers=headers, timeout=10,
                )
            if r.status_code == 200:
                return _ConnectivityResult(
                    pname,
                    [(color("✓", Colors.GREEN), label, "")],
                    [],
                )
            if r.status_code == 401:
                return _ConnectivityResult(
                    pname,
                    [(color("✗", Colors.RED), label,
                      color("(无效的 API 密钥)", Colors.DIM))],
                    [f"检查 .env 中的 {env_vars[0]}"],
                )
            return _ConnectivityResult(
                pname,
                [(color("⚠", Colors.YELLOW), label,
                  color(f"(HTTP {r.status_code})", Colors.DIM))],
                [],
            )
        except Exception as e:
            return _ConnectivityResult(
                pname,
                [(color("⚠", Colors.YELLOW), label,
                  color(f"({e})", Colors.DIM))],
                [],
            )

    def _probe_bedrock() -> _ConnectivityResult:
        try:
            from agent.bedrock_adapter import (
                has_aws_credentials,
                resolve_aws_auth_env_var,
                resolve_bedrock_region,
            )
        except ImportError:
            return _ConnectivityResult("AWS Bedrock", [], [])
        if not has_aws_credentials():
            return _ConnectivityResult("AWS Bedrock", [], [])
        auth_var = resolve_aws_auth_env_var()
        region = resolve_bedrock_region()
        label = "AWS Bedrock".ljust(20)
        try:
            import boto3
            from botocore.config import Config as _BotoConfig
            # 在实际的 Bedrock API 调用上减少重试，以便瞬时故障不会使 doctor 运行增加 30+ 秒。
            cfg = _BotoConfig(
                connect_timeout=5,
                read_timeout=10,
                retries={"max_attempts": 1},
            )
            client = boto3.client("bedrock", region_name=region, config=cfg)
            resp = client.list_foundation_models()
            n = len(resp.get("modelSummaries", []))
            return _ConnectivityResult(
                "AWS Bedrock",
                [(color("✓", Colors.GREEN), label,
                  color(f"({auth_var}, {region}, {n} 个模型)", Colors.DIM))],
                [],
            )
        except ImportError:
            return _ConnectivityResult(
                "AWS Bedrock",
                [(color("⚠", Colors.YELLOW), label,
                  color(f"(未安装 boto3 — {sys.executable} -m pip install boto3)",
                        Colors.DIM))],
                [f"为 Bedrock 安装 boto3: {sys.executable} -m pip install boto3"],
            )
        except Exception as e:
            err_name = type(e).__name__
            return _ConnectivityResult(
                "AWS Bedrock",
                [(color("⚠", Colors.YELLOW), label,
                  color(f"({err_name}: {e})", Colors.DIM))],
                [f"AWS Bedrock: {err_name} — 检查 bedrock:ListFoundationModels 的 IAM 权限"],
            )

    # 按显示顺序构建探测提交列表
    _probes.append(("OpenRouter API", _probe_openrouter))
    _probes.append(("Anthropic API", _probe_anthropic))

    global _APIKEY_PROVIDERS_CACHE
    if _APIKEY_PROVIDERS_CACHE is None:
        _APIKEY_PROVIDERS_CACHE = _build_apikey_providers_list()
    for _entry in _APIKEY_PROVIDERS_CACHE:
        _pname, _env_vars, _default_url, _base_env, _supports = _entry
        # 通过绑定默认参数捕获循环变量——没有这个，所有闭包将共享最终迭代的值，每个探测都会命中最后一个提供商的 URL。
        _probes.append((_pname, lambda p=_pname, e=_env_vars, u=_default_url,
                                       b=_base_env, s=_supports:
                                _probe_apikey_provider(p, e, u, b, s)))

    _probes.append(("AWS Bedrock", _probe_bedrock))

    # 打印单个状态行，以便用户看到有事情发生，然后扇出。``\r`` 在第一个真实结果行到达后清除它。
    print(f"  {color(f'正在并行运行 {len(_probes)} 个连接性检查…', Colors.DIM)}",
          end="", flush=True)

    # 在并行块期间禁用 boto3 的 EC2 实例元数据服务探测。boto 的默认凭据链在我们不在 EC2 上时尝试 169.254.169.254 并带有几秒的超时，
    # 这在该修复之前主导了该部分的墙钟时间（~2 秒在开发人员笔记本电脑上，即使其余部分已并行化）。
    # 在提交工作之前在父线程上设置，以便环境变量突变永远不会与另一个 worker 竞争。
    # bedrock 探测中的 has_aws_credentials() 已经根据真实的环境变量凭据进行门控，因此 IMDS 永远不会是 `hermes doctor` 的合法来源。
    _imds_prev = os.environ.get("AWS_EC2_METADATA_DISABLED")
    os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
    try:
        # 8 个 worker 足够了——每个探测是一次 HTTP 调用加上 TLS 握手。超过这个数量会浪费线程启动成本，并且如果任何东西曾经从 worker 内部打印，可能会产生嘈杂的输出。
        with _futures.ThreadPoolExecutor(max_workers=8,
                                         thread_name_prefix="doctor-probe") as _ex:
            _futures_in_order = [_ex.submit(_fn) for _, _fn in _probes]
            _results = [_f.result() for _f in _futures_in_order]
    finally:
        if _imds_prev is None:
            os.environ.pop("AWS_EC2_METADATA_DISABLED", None)
        else:
            os.environ["AWS_EC2_METADATA_DISABLED"] = _imds_prev

    # 清除“正在运行…”行并按提交顺序打印所有结果。
    print("\r" + " " * 70 + "\r", end="")
    for _r in _results:
        for _glyph, _label, _detail in _r.lines:
            if _detail:
                print(f"  {_glyph} {_label} {_detail}")
            else:
                print(f"  {_glyph} {_label}")
        _issues_to_add = list(_r.issues)
        if _issues_to_add and _has_healthy_oauth_fallback_for_apikey_provider(_r.label):
            _issues_to_add = []
        for _issue in _issues_to_add:
            issues.append(_issue)

    # =========================================================================
    # 检查：工具可用性
    # =========================================================================
    print()
    print(color("◆ 工具可用性", Colors.CYAN, Colors.BOLD))
    
    try:
        # 为导入添加项目根目录到路径
        sys.path.insert(0, str(PROJECT_ROOT))
        from model_tools import check_tool_availability, TOOLSET_REQUIREMENTS
        
        available, unavailable = check_tool_availability()
        available, unavailable = _apply_doctor_tool_availability_overrides(available, unavailable)
        
        for tid in available:
            info = TOOLSET_REQUIREMENTS.get(tid, {})
            check_ok(info.get("name", tid), _doctor_tool_availability_detail(tid))
        
        for item in unavailable:
            env_vars = item.get("missing_vars") or item.get("env_vars") or []
            if env_vars:
                vars_str = ", ".join(env_vars)
                check_warn(item["name"], f"(缺失 {vars_str})")
            else:
                check_warn(item["name"], "(系统依赖未满足)")

        # 统计具有 API 密钥要求的禁用工具
        api_disabled = [u for u in unavailable if (u.get("missing_vars") or u.get("env_vars"))]
        if api_disabled:
            issues.append("运行 'hermes setup' 来配置缺失的 API 密钥以获得完整的工具访问权限")
    except Exception as e:
        check_warn("无法检查工具可用性", f"({e})")
    
    # =========================================================================
    # 检查：技能中心
    # =========================================================================
    print()
    print(color("◆ 技能中心", Colors.CYAN, Colors.BOLD))

    hub_dir = HERMES_HOME / "skills" / ".hub"
    if hub_dir.exists():
        check_ok("技能中心目录存在")
        lock_file = hub_dir / "lock.json"
        if lock_file.exists():
            try:
                import json
                lock_data = json.loads(lock_file.read_text())
                count = len(lock_data.get("installed", {}))
                check_ok(f"锁定文件正常 ({count} 个中心安装的技能)")
            except Exception:
                check_warn("锁定文件", "(损坏或不可读)")
        quarantine = hub_dir / "quarantine"
        q_count = sum(1 for d in quarantine.iterdir() if d.is_dir()) if quarantine.exists() else 0
        if q_count > 0:
            check_warn(f"{q_count} 个技能在隔离区", "(待审查)")
    else:
        check_warn("技能中心目录未初始化", "(运行: hermes skills list)")

    from hermes_cli.config import get_env_value

    def _gh_authenticated() -> bool:
        """检查 gh CLI 是否通过令牌文件或设备流认证。"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status", "--json", "authenticated"],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    github_token = get_env_value("GITHUB_TOKEN") or get_env_value("GH_TOKEN")
    if github_token:
        check_ok("GitHub 令牌已配置（认证的 API 访问）")
    elif _gh_authenticated():
        check_ok("通过 gh CLI 认证的 GitHub", "(完整的 API 访问 — 不需要 GITHUB_TOKEN)")
    else:
        check_warn("无 GITHUB_TOKEN", f"(60 次请求/小时速率限制 — 在 {_DHH}/.env 中设置以获得更好的速率)")

    # =========================================================================
    # 记忆提供商（仅检查活跃的提供商，如果有的话）
    # =========================================================================
    print()
    print(color("◆ 记忆提供商", Colors.CYAN, Colors.BOLD))

    _active_memory_provider = ""
    try:
        import yaml as _yaml
        _mem_cfg_path = HERMES_HOME / "config.yaml"
        if _mem_cfg_path.exists():
            with open(_mem_cfg_path, encoding="utf-8") as _f:
                _raw_cfg = _yaml.safe_load(_f) or {}
            _active_memory_provider = (_raw_cfg.get("memory") or {}).get("provider", "")
    except Exception:
        pass

    if not _active_memory_provider:
        check_ok("内置记忆活跃", "(未配置外部提供商 — 这没问题)")
    elif _active_memory_provider == "honcho":
        try:
            from plugins.memory.honcho.client import HonchoClientConfig, resolve_config_path
            hcfg = HonchoClientConfig.from_global_config()
            _honcho_cfg_path = resolve_config_path()

            if not _honcho_cfg_path.exists():
                check_warn("未找到 Honcho 配置", "运行: hermes memory setup")
            elif not hcfg.enabled:
                check_info(f"Honcho 已禁用 (在 {_honcho_cfg_path} 中设置 enabled: true 以激活)")
            elif not (hcfg.api_key or hcfg.base_url):
                check_fail("未设置 Honcho API 密钥或基础 URL", "运行: hermes memory setup")
                issues.append("无 Honcho API 密钥 — 运行 'hermes memory setup'")
            else:
                from plugins.memory.honcho.client import get_honcho_client, reset_honcho_client
                reset_honcho_client()
                try:
                    get_honcho_client(hcfg)
                    check_ok(
                        "Honcho 已连接",
                        f"workspace={hcfg.workspace_id} mode={hcfg.recall_mode} freq={hcfg.write_frequency}",
                    )
                except Exception as _e:
                    check_fail("Honcho 连接失败", str(_e))
                    issues.append(f"Honcho 不可达: {_e}")
        except ImportError:
            check_fail("未安装 honcho-ai", "pip install honcho-ai")
            issues.append("Honcho 被设置为记忆提供商但未安装 honcho-ai")
        except Exception as _e:
            check_warn("Honcho 检查失败", str(_e))
    elif _active_memory_provider == "mem0":
        try:
            from plugins.memory.mem0 import _load_config as _load_mem0_config
            mem0_cfg = _load_mem0_config()
            mem0_key = mem0_cfg.get("api_key", "")
            if mem0_key:
                check_ok("Mem0 API 密钥已配置")
                check_info(f"user_id={mem0_cfg.get('user_id', '?')}  agent_id={mem0_cfg.get('agent_id', '?')}")
            else:
                check_fail("未设置 Mem0 API 密钥", "(在 .env 中设置 MEM0_API_KEY 或运行 hermes memory setup)")
                issues.append("Mem0 被设置为记忆提供商但 API 密钥缺失")
        except ImportError:
            check_fail("Mem0 插件无法加载", "pip install mem0ai")
            issues.append("Mem0 被设置为记忆提供商但未安装 mem0ai")
        except Exception as _e:
            check_warn("Mem0 检查失败", str(_e))
    else:
        # 对其他记忆提供商（openviking, hindsight 等）的通用检查
        try:
            from plugins.memory import load_memory_provider
            _provider = load_memory_provider(_active_memory_provider)
            if _provider and _provider.is_available():
                check_ok(f"{_active_memory_provider} 提供商活跃")
            elif _provider:
                check_warn(f"{_active_memory_provider} 已配置但不可用", "运行: hermes memory status")
            else:
                check_warn(f"{_active_memory_provider} 插件未找到", "运行: hermes memory setup")
        except Exception as _e:
            check_warn(f"{_active_memory_provider} 检查失败", str(_e))

    # =========================================================================
    # 配置文件
    # =========================================================================
    try:
        from hermes_cli.profiles import list_profiles, _get_wrapper_dir, profile_exists
        import re as _re

        named_profiles = [p for p in list_profiles() if not p.is_default]
        if named_profiles:
            print()
            print(color("◆ 配置文件", Colors.CYAN, Colors.BOLD))
            check_ok(f"找到 {len(named_profiles)} 个配置文件")
            wrapper_dir = _get_wrapper_dir()
            for p in named_profiles:
                parts = []
                if p.gateway_running:
                    parts.append("消息网关正在运行")
                if p.model:
                    parts.append(p.model[:30])
                if not (p.path / "config.yaml").exists():
                    parts.append("⚠ 缺少配置")
                if not (p.path / ".env").exists():
                    parts.append("无 .env")
                wrapper = wrapper_dir / p.name
                if not wrapper.exists():
                    parts.append("无别名")
                status = ", ".join(parts) if parts else "已配置"
                check_ok(f"  {p.name}: {status}")

            # 检查孤立的包装器
            if wrapper_dir.is_dir():
                for wrapper in wrapper_dir.iterdir():
                    if not wrapper.is_file():
                        continue
                    try:
                        content = wrapper.read_text()
                        if "hermes -p" in content:
                            _m = _re.search(r"hermes -p (\S+)", content)
                            if _m and not profile_exists(_m.group(1)):
                                check_warn(f"孤立别名: {wrapper.name} → 配置文件 '{_m.group(1)}' 不再存在")
                    except Exception:
                        pass
    except ImportError:
        pass
    except Exception:
        pass

    # =========================================================================
    # 摘要
    # =========================================================================
    print()
    remaining_issues = issues + manual_issues
    if should_fix and fixed_count > 0:
        print(color("─" * 60, Colors.GREEN))
        print(color(f"  已修复 {fixed_count} 个问题。", Colors.GREEN, Colors.BOLD), end="")
        if remaining_issues:
            print(color(f" {len(remaining_issues)} 个问题需要手动干预。", Colors.YELLOW, Colors.BOLD))
        else:
            print()
        print()
        if remaining_issues:
            for i, issue in enumerate(remaining_issues, 1):
                print(f"  {i}. {issue}")
            print()
    elif remaining_issues:
        print(color("─" * 60, Colors.YELLOW))
        print(color(f"  发现 {len(remaining_issues)} 个需要解决的问题:", Colors.YELLOW, Colors.BOLD))
        print()
        for i, issue in enumerate(remaining_issues, 1):
            print(f"  {i}. {issue}")
        print()
        if not should_fix:
            print(color("  提示: 运行 'hermes doctor --fix' 以自动修复可能的问题。", Colors.DIM))
    else:
        print(color("─" * 60, Colors.GREEN))
        print(color("  所有检查通过！🎉", Colors.GREEN, Colors.BOLD))
    
    print()