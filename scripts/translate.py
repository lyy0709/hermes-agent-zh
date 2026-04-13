#!/usr/bin/env python3
"""
翻译引擎 - 使用 OpenAI 兼容 API 自动翻译 hermes-agent 文档和代码文本。

支持增量翻译：通过 SHA-256 hash 追踪文件变更，仅翻译变化的内容。
支持并发翻译：多线程并行调用 API，内置 RPM 限速器。

环境变量:
    OPENAI_API_KEY: API 密钥（必填）
    OPENAI_BASE_URL: API 基础地址（默认 https://api.openai.com/v1）
    TRANSLATION_MODEL: 翻译模型（默认 gpt-4o）
    TRANSLATION_WORKERS: 并发线程数（默认 5）
    TRANSLATION_RPM: 每分钟最大请求数（默认 1000）
    TRANSLATION_TPM: 每分钟最大 token 数（默认 100000）
    TRANSLATION_TIMEOUT: 单次 API 调用超时秒数（默认 300）
"""

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# CI 环境下强制禁用 stdout/stderr 缓冲，确保日志实时输出
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT_DIR / "translations"
HASH_CACHE_FILE = TRANSLATIONS_DIR / ".hash-cache.json"
GLOSSARY_FILE = TRANSLATIONS_DIR / "glossary.json"
CONFIG_FILE = TRANSLATIONS_DIR / "config.json"


# ──────────────────────────────────────────
# 限速器
# ──────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """
    粗略估算文本的 token 数。

    规则（适用于大多数 GPT/LLM tokenizer）：
    - 英文：约 4 字符 ≈ 1 token
    - 中文/日文/韩文：约 1.5 字符 ≈ 1 token
    - 取混合文本的加权估算，再乘 1.1 留安全余量
    """
    cjk_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff')
    other_chars = len(text) - cjk_chars
    estimated = cjk_chars / 1.5 + other_chars / 4.0
    return int(estimated * 1.1) + 1


class TokenBudgetExceeded(Exception):
    """单个请求的 token 预估超过 TPM 上限，不可重试。"""


class RateLimiter:
    """
    RPM + TPM 双滑动窗口限速器（请求级记账）。

    - RPM：每分钟最大请求数
    - TPM：每分钟最大 token 数（使用安全水位 80% 为并发/重试保留余量）
    - 每次 acquire() 返回 reservation_id，release/report 通过 ID 精确操作
    - time_until_capacity() 精确计算需要等待的时间

    线程安全：多线程并发调用时自动排队等待。
    """

    def __init__(self, rpm: int = 1000, tpm: int = 100_000):
        if rpm <= 0:
            raise ValueError(f"RPM 必须为正整数，当前值: {rpm}")
        if tpm <= 0:
            raise ValueError(f"TPM 必须为正整数，当前值: {tpm}")
        self.rpm = rpm
        self.tpm = tpm
        self.tpm_safe = int(tpm * 0.8)  # 安全水位：为重试/并发保留 20% 余量
        self.window = 60.0
        self._req_records: list[float] = []
        self._token_ledger: dict[int, tuple[float, int]] = {}
        self._next_id = 0
        self._lock = threading.Lock()

    def _cleanup(self, now: float):
        """清理滑动窗口外的旧记录"""
        self._req_records = [t for t in self._req_records if now - t < self.window]
        expired = [rid for rid, (t, _) in self._token_ledger.items() if now - t >= self.window]
        for rid in expired:
            del self._token_ledger[rid]

    def _tokens_in_window(self) -> int:
        return sum(n for _, n in self._token_ledger.values())

    def time_until_capacity(self, needed_tokens: int) -> float:
        """计算需要等待多少秒才能释放出 needed_tokens 的额度。

        返回 0 表示立即可用，返回 >0 表示需等待的精确秒数。
        必须在持锁状态下调用。
        """
        now = time.monotonic()
        current = self._tokens_in_window()
        shortfall = (current + needed_tokens) - self.tpm_safe
        if shortfall <= 0:
            return 0.0

        # 按时间顺序累加即将过期的 token，直到释放够
        records_by_time = sorted(self._token_ledger.values(), key=lambda x: x[0])
        freed = 0
        for ts, tokens in records_by_time:
            expire_at = ts + self.window
            freed += tokens
            if freed >= shortfall:
                return max(0.0, expire_at - now + 0.1)
        # 所有记录都过期也不够（不应发生，因为 acquire 已检查单请求上限）
        return self.window

    def acquire(self, estimated_tokens: int = 0) -> int:
        """阻塞直到 RPM 和 TPM 配额均可用。使用安全水位（80% TPM）。"""
        if estimated_tokens > self.tpm:
            raise TokenBudgetExceeded(
                f"单个请求预估 {estimated_tokens:,} tokens 超过 TPM 上限 {self.tpm:,}，"
                f"请缩小文件分段或提高 TPM 配额"
            )

        while True:
            with self._lock:
                now = time.monotonic()
                self._cleanup(now)

                rpm_ok = len(self._req_records) < self.rpm
                tpm_ok = (self._tokens_in_window() + estimated_tokens) <= self.tpm_safe

                if rpm_ok and tpm_ok:
                    self._req_records.append(now)
                    rid = self._next_id
                    self._next_id += 1
                    if estimated_tokens > 0:
                        self._token_ledger[rid] = (now, estimated_tokens)
                    return rid

                # 精确计算等待时间
                wait_seconds = 0.5
                if not rpm_ok and self._req_records:
                    wait_seconds = max(wait_seconds, self._req_records[0] + self.window - now)
                if not tpm_ok:
                    wait_seconds = max(wait_seconds, self.time_until_capacity(estimated_tokens))

            time.sleep(min(wait_seconds + 0.1, 30.0))

    def release(self, reservation_id: int):
        """释放指定 reservation 的全部 token（请求失败时调用）。"""
        with self._lock:
            self._token_ledger.pop(reservation_id, None)

    def release_cautious(self, reservation_id: int):
        """谨慎释放：可能已被上游消耗的请求，只释放 50% token。"""
        with self._lock:
            if reservation_id in self._token_ledger:
                ts, tokens = self._token_ledger[reservation_id]
                self._token_ledger[reservation_id] = (ts, tokens // 2)

    def report_actual(self, reservation_id: int, actual_tokens: int):
        """用 API 返回的实际 token 数替换预估值。"""
        with self._lock:
            if reservation_id not in self._token_ledger:
                return
            ts, _ = self._token_ledger[reservation_id]
            if actual_tokens <= 0:
                del self._token_ledger[reservation_id]
            else:
                self._token_ledger[reservation_id] = (ts, actual_tokens)


# ──────────────────────────────────────────
# 配置加载
# ──────────────────────────────────────────

def load_env():
    """加载环境变量"""
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("错误: 未设置 OPENAI_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    def _int_env(name: str, default: int) -> int:
        """读取整数环境变量，空串/缺失/非法值时使用默认值"""
        val = os.getenv(name, "").strip()
        if not val:
            return default
        try:
            return int(val)
        except ValueError:
            print(f"警告: 环境变量 {name}={val!r} 不是有效整数，使用默认值 {default}", file=sys.stderr)
            return default

    return {
        "api_key": api_key,
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1",
        "model": os.getenv("TRANSLATION_MODEL", "gpt-4o") or "gpt-4o",
        "workers": _int_env("TRANSLATION_WORKERS", 5),
        "rpm": _int_env("TRANSLATION_RPM", 1000),
        "tpm": _int_env("TRANSLATION_TPM", 100_000),
        "timeout": _int_env("TRANSLATION_TIMEOUT", 300),
    }


def load_glossary() -> str:
    """加载术语表并格式化为 prompt 可用的文本"""
    if not GLOSSARY_FILE.exists():
        return ""
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    terms = data.get("terms", {})
    lines = [f"- {en} → {zh}" for en, zh in terms.items()]
    return "\n".join(lines)


def load_hash_cache() -> dict:
    """加载翻译 hash 缓存"""
    if not HASH_CACHE_FILE.exists():
        return {}
    with open(HASH_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


_cache_lock = threading.Lock()


def save_hash_cache(cache: dict):
    """线程安全地保存翻译 hash 缓存"""
    with _cache_lock:
        with open(HASH_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)


def compute_file_hash(file_path: Path) -> str:
    """计算文件的 SHA-256 hash"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def load_config() -> dict:
    """加载翻译配置"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def should_translate(source_path: str, source_file: Path, cache: dict, force: bool) -> bool:
    """判断文件是否需要翻译"""
    if force:
        return True
    if source_path not in cache:
        return True
    current_hash = compute_file_hash(source_file)
    return cache[source_path].get("source_hash") != current_hash


# ──────────────────────────────────────────
# Prompt 构建
# ──────────────────────────────────────────

def build_system_prompt(glossary_text: str, file_path: str = "") -> str:
    """构建翻译 system prompt，根据文件类型调整规则。"""
    ext = Path(file_path).suffix.lower() if file_path else ""

    if ext in (".html", ".htm"):
        return f"""你是一个专业的技术文档翻译员。将以下 HTML 页面中的英文内容翻译为简体中文。

规则：
1. 保持所有 HTML 标签、属性名、CSS 类名完全不变
2. 翻译标签内的用户可见文本（标题、段落、按钮、链接文字等）
3. 翻译 meta 标签的 content 属性中的描述性文本
4. 翻译 alt 属性和 title 属性中的文本
5. 不翻译 JavaScript 代码逻辑
6. 不翻译 URL、href、src 属性值
7. 不翻译 CSS 样式
8. 保持 HTML 结构和缩进完全不变
9. 技术术语按照术语表翻译
10. 只输出翻译后的完整 HTML，不要添加任何解释

术语表：
{glossary_text}"""
    elif ext in (".yml", ".yaml"):
        return f"""你是一个专业的技术文档翻译员。将以下 YAML 文件中的英文内容翻译为简体中文。

规则：
1. 只翻译 YAML 值中的用户可见文本（name、description、label、placeholder 等字段的值）
2. 保持 YAML 结构和缩进完全不变
3. 不翻译 YAML 的 key 名称
4. 不翻译以下机器字段的值：type、id、required、validations、render、assignees、labels（方括号内的标签名）
5. 不翻译 URL、GitHub 链接
6. 保持 YAML 多行字符串格式（| 和 > 标记）不变
7. 技术术语按照术语表翻译
8. 只输出翻译后的完整 YAML，不要添加任何解释

术语表：
{glossary_text}"""
    else:
        return f"""你是一个专业的技术文档翻译员。将以下英文内容翻译为简体中文。

规则：
1. 保持 Markdown 格式不变（标题、列表、代码块、链接、图片等）
2. 代码块（```...```）内的代码不翻译
3. 行内代码（`...`）不翻译
4. 技术术语按照术语表翻译，未收录的术语保留英文
5. URL、文件路径、命令行指令不翻译
6. 保持原文的段落结构和换行
7. 翻译要自然流畅，符合中文技术文档习惯
8. frontmatter（---...---）中的 title 和 description 翻译，其他字段保留原文
9. HTML 标签和属性不翻译
10. 只输出翻译结果，不要添加任何解释或说明

术语表：
{glossary_text}"""


def _detect_file_lang(filename: str) -> tuple[str, str]:
    """根据文件后缀检测语言类型，返回 (语言名, 代码块标记)。"""
    ext = Path(filename).suffix.lower()
    lang_map = {
        ".py": ("Python", "python"),
        ".html": ("HTML", "html"),
        ".htm": ("HTML", "html"),
        ".js": ("JavaScript", "javascript"),
        ".ts": ("TypeScript", "typescript"),
        ".yml": ("YAML", "yaml"),
        ".yaml": ("YAML", "yaml"),
        ".json": ("JSON", "json"),
        ".sh": ("Shell", "bash"),
        ".css": ("CSS", "css"),
    }
    return lang_map.get(ext, ("未知类型", "text"))


def build_string_extract_prompt(glossary_text: str, lang_name: str = "Python") -> str:
    """构建字符串提取和翻译的 system prompt，根据文件类型调整。"""
    if lang_name == "HTML":
        return f"""你是一个专业的技术文档翻译员。你需要从 HTML 页面中提取用户可见的文本，并翻译为简体中文。

任务：
1. 识别 HTML 中所有用户可见的文本（标题、段落、按钮文字、meta description、alt 属性等）
2. 忽略：HTML 标签名、CSS 类名、JavaScript 代码逻辑、URL、技术属性
3. 对每段需要翻译的文本，输出 JSON 替换规则

输出格式（严格 JSON）：
{{
  "file": "文件路径",
  "description": "页面功能描述",
  "replacements": {{
    "原始英文文本": "翻译后的中文文本"
  }}
}}

规则：
- key 是 HTML 中的原始英文文本（完整包含引号或标签内容）
- value 是对应的中文翻译
- 保持 HTML 实体和特殊字符不变
- 只输出 JSON，不要添加任何解释

术语表：
{glossary_text}"""
    else:
        return f"""你是一个专业的技术文档翻译员。你需要从{lang_name}源代码中提取用户面向的字符串，并翻译为简体中文。

任务：
1. 识别代码中所有用户可见的字符串（提示信息、错误消息、描述文本、标签等）
2. 忽略：变量名、函数名、导入语句、注释、docstring、日志格式字符串、技术标识符
3. 对每个用户面向的字符串，输出 JSON 替换规则

输出格式（严格 JSON）：
{{
  "file": "文件路径",
  "description": "文件功能描述",
  "replacements": {{
    "\"源码中带引号的精确原文\"": "\"翻译后的中文\""
  }}
}}

关键规则：
- key 和 value 都必须包含源码中的引号（如源码是 x = "hello" 则 key 为 "hello" 包含双引号）
- key 必须是源码中逐字连续出现的精确子串（直接从源码复制粘贴，包含引号字符）
- 如果文本被 Rich markup 包裹（如 [bold]text[/]），key 应包含完整 markup 标签
- 如果文本跨多行、涉及 f-string 插值 {{}} 或函数调用拼接，跳过不生成规则
- value 是对应的中文翻译，保持格式占位符（如 {{}}、%s、\\n、Rich markup 标签）不变
- 不要翻译 docstring 和注释
- 只输出 JSON，不要添加任何解释

术语表：
{glossary_text}"""


# ──────────────────────────────────────────
# 块感知智能分段
# ──────────────────────────────────────────

def split_content(content: str, file_path: str = "", max_chars: int = 12000) -> list[str]:
    """
    将大文件按结构化边界分割为多段，避免单段超过 token 限制。

    块感知：不会在代码块、HTML 标签对、YAML block scalar 内部切分。

    策略：
    - Markdown (.md): 按 # heading 分割，跳过 ``` 代码块内部
    - HTML (.html): 按顶层块标签分割
    - YAML (.yml): 按顶层 key 分割，跳过 block scalar 内部
    - 通用 fallback: 按空行分割
    """
    if len(content) <= max_chars:
        return [content]

    ext = Path(file_path).suffix.lower() if file_path else ""

    if ext == ".md":
        return _split_markdown(content, max_chars)
    elif ext in (".html", ".htm"):
        return _split_html(content, max_chars)
    elif ext in (".yml", ".yaml"):
        return _split_yaml(content, max_chars)
    else:
        return _split_by_blank_lines(content, max_chars)


def _emit(sections: list[str], current: list[str]):
    """将当前行缓冲区提交为一个段（跳过空段）。"""
    text = "\n".join(current)
    if text.strip():
        sections.append(text)


def _split_markdown(content: str, max_chars: int) -> list[str]:
    """
    Markdown 分段：按 heading 分割，跳过代码块内部。

    安全兜底：当段超过 max_chars//2 且不在代码块内时，在空行处切分。
    代码块追踪：记录 fence 标记长度（支持 ```/````/````` 等嵌套写法）。
    """
    lines = content.split("\n")
    sections: list[str] = []
    current: list[str] = []
    current_len = 0
    fence_len = 0  # 当前代码块 fence 的反引号数量，0 表示不在代码块内

    for line in lines:
        stripped = line.strip()
        line_len = len(line) + 1

        # 代码块状态追踪（支持不同长度的 fence）
        if stripped.startswith("```"):
            backtick_count = len(stripped) - len(stripped.lstrip("`"))
            if fence_len == 0:
                fence_len = backtick_count  # 进入代码块
            elif backtick_count >= fence_len:
                fence_len = 0  # 离开代码块（关闭 fence 长度 >= 开启 fence）

        in_code_block = fence_len > 0
        is_heading = not in_code_block and re.match(r"^#{1,3}\s", line)
        is_blank = not in_code_block and not stripped

        # 优先在 heading 处切分
        if is_heading and current_len > max_chars // 2:
            _emit(sections, current)
            current = [line]
            current_len = line_len
        # 兜底：超过半限且在安全位置（空行、非代码块）切分
        elif is_blank and current_len > max_chars // 2:
            _emit(sections, current)
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        _emit(sections, current)
    return sections if sections else [content]


def _split_html(content: str, max_chars: int) -> list[str]:
    """HTML 分段：按顶层块标签分割，兜底在空行处切分。"""
    lines = content.split("\n")
    sections: list[str] = []
    current: list[str] = []
    current_len = 0

    block_pattern = re.compile(
        r"^\s*<(?:section|header|main|footer|article|nav|aside|div\s+(?:class|id))[>\s]",
        re.IGNORECASE,
    )

    for line in lines:
        is_boundary = block_pattern.match(line)
        is_blank = not line.strip()
        line_len = len(line) + 1

        if is_boundary and current_len > max_chars // 2:
            _emit(sections, current)
            current = [line]
            current_len = line_len
        elif is_blank and current_len > max_chars // 2:
            _emit(sections, current)
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        _emit(sections, current)
    return sections if sections else [content]


def _split_yaml(content: str, max_chars: int) -> list[str]:
    """YAML 分段：按顶层 key 分割，跳过 block scalar (| / >) 和列表内部。"""
    lines = content.split("\n")
    sections: list[str] = []
    current: list[str] = []
    current_len = 0

    # 顶层 key：行首非空白字符开头，后跟冒号
    top_key_pattern = re.compile(r"^[^\s#].*:")

    for line in lines:
        is_top_key = top_key_pattern.match(line) and not line.startswith(" ") and not line.startswith("\t")
        line_len = len(line) + 1

        if is_top_key and current_len > max_chars // 2:
            _emit(sections, current)
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        _emit(sections, current)
    return sections if sections else [content]


def _split_by_blank_lines(content: str, max_chars: int) -> list[str]:
    """通用 fallback：按空行分割。"""
    lines = content.split("\n")
    sections: list[str] = []
    current: list[str] = []
    current_len = 0

    for line in lines:
        is_blank = not line.strip()
        line_len = len(line) + 1

        if is_blank and current_len > max_chars // 2:
            _emit(sections, current)
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        _emit(sections, current)
    return sections if sections else [content]


# ──────────────────────────────────────────
# API 调用（带 timeout + 限速 + 重试）
# ──────────────────────────────────────────

def translate_text(
    client: OpenAI,
    model: str,
    system_prompt: str,
    text: str,
    rate_limiter: RateLimiter,
    timeout: int = 300,
    max_retries: int = 3,
) -> str:
    """调用 LLM API 翻译文本，带 RPM+TPM 限速、超时和指数退避重试。

    TokenBudgetExceeded 不会被重试，直接向上抛出。
    """
    # 预估 token：system prompt + 用户文本 + 预留输出
    input_tokens = estimate_tokens(system_prompt) + estimate_tokens(text)
    output_estimate = int(input_tokens * 0.9)
    estimated_total = input_tokens + output_estimate

    for attempt in range(max_retries):
        # acquire 可能抛 TokenBudgetExceeded（不在 try 内，不会被重试）
        rid = rate_limiter.acquire(estimated_tokens=estimated_total)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
                timeout=timeout,
            )
            # 用 API 返回的实际 token 数修正本次 reservation（安全处理 None）
            actual_total = getattr(response.usage, "total_tokens", None) if response.usage else None
            if isinstance(actual_total, int) and actual_total >= 0:
                rate_limiter.report_actual(rid, actual_total)

            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            # 区分异常类型决定释放策略
            err_name = type(e).__name__
            if "timeout" in err_name.lower() or "reset" in err_name.lower() or "connect" in err_name.lower():
                # 超时/连接重置：可能上游已消耗 token，谨慎释放 50%
                rate_limiter.release_cautious(rid)
            else:
                # 其他错误（如认证失败）：确定未消耗，完全释放
                rate_limiter.release(rid)
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"  API 调用失败 ({err_name})，{wait_time}s 后重试: {e}", file=sys.stderr)
                time.sleep(wait_time)
            else:
                raise
    return ""


# ──────────────────────────────────────────
# 翻译执行器
# ──────────────────────────────────────────

class TranslationError(Exception):
    """翻译失败异常，用于阻止 hash 缓存写入"""


def translate_markdown_file(
    client: OpenAI,
    model: str,
    glossary_text: str,
    source_file: Path,
    target_file: Path,
    rate_limiter: RateLimiter,
    timeout: int = 300,
):
    """翻译 Markdown/HTML/YAML 等文本文件（整文件翻译模式，自动分段）。"""
    system_prompt = build_system_prompt(glossary_text, str(source_file))
    content = source_file.read_text(encoding="utf-8")
    sections = split_content(content, str(source_file))

    translated_parts = []
    for i, section in enumerate(sections):
        if len(sections) > 1:
            print(f"  翻译分段 {i + 1}/{len(sections)}...")
        translated = translate_text(client, model, system_prompt, section, rate_limiter, timeout)
        translated_parts.append(translated)

    result = "\n".join(translated_parts)
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(result, encoding="utf-8")


def translate_code_strings(
    client: OpenAI,
    model: str,
    glossary_text: str,
    source_file: Path,
    target_file: Path,
    rate_limiter: RateLimiter,
    timeout: int = 300,
):
    """提取并翻译代码中的用户面向字符串。大文件自动分段，合并结果。"""
    content = source_file.read_text(encoding="utf-8")
    lang_name, code_tag = _detect_file_lang(source_file.name)
    system_prompt = build_string_extract_prompt(glossary_text, lang_name)

    # 大文件分段处理
    max_code_chars = 10000  # 代码文件的分段阈值（比文档小，因为还有 prompt 开销）
    sections = split_content(content, str(source_file), max_chars=max_code_chars)

    all_replacements: dict[str, str] = {}
    failed_sections = 0
    for i, section in enumerate(sections):
        if len(sections) > 1:
            print(f"  提取分段 {i + 1}/{len(sections)}...")

        prompt = f"以下是{lang_name}文件 `{source_file.name}` 的第 {i + 1} 部分:\n\n```{code_tag}\n{section}\n```"

        # 每段：先调用 LLM，JSON 解析失败时尝试轻量修复（不重发源码）
        parsed = False
        result = translate_text(client, model, system_prompt, prompt, rate_limiter, timeout)

        # 提取 JSON（支持多种 LLM 输出格式）
        json_text = result
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", result)
        if json_match:
            json_text = json_match.group(1)

        try:
            part_data = json.loads(json_text)
        except json.JSONDecodeError:
            # 轻量修复：让 LLM 修复 JSON 格式（不重发整段源码，节省 TPM）
            print(f"  分段 {i + 1} JSON 解析失败，尝试轻量修复...", file=sys.stderr)
            fix_prompt = f"以下文本应该是 JSON 但格式有误，请修复为有效 JSON 并只输出 JSON：\n\n{result[:3000]}"
            fix_result = translate_text(client, model, "你是 JSON 格式修复工具。只输出修复后的有效 JSON。", fix_prompt, rate_limiter, timeout)
            fix_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", fix_result)
            if fix_match:
                fix_result = fix_match.group(1)
            try:
                part_data = json.loads(fix_result)
            except json.JSONDecodeError:
                part_data = None
                print(f"  分段 {i + 1} 轻量修复也失败", file=sys.stderr)

        if part_data is not None:
            part_replacements = part_data.get("replacements", {})
            if isinstance(part_replacements, dict):
                for key in part_replacements:
                    if key in all_replacements and all_replacements[key] != part_replacements[key]:
                        print(f"  警告: 分段 key 冲突 '{key[:50]}...'，使用后段翻译", file=sys.stderr)
                all_replacements.update(part_replacements)
                parsed = True

        if not parsed:
            failed_sections += 1
            if len(sections) == 1:
                raise TranslationError("LLM 返回的不是有效 JSON（已重试 3 次）") from None
            print(f"  警告: 分段 {i + 1} JSON 解析 3 次均失败", file=sys.stderr)

    # 任一分段失败 → 整体失败，不写入 hash cache
    if failed_sections > 0:
        raise TranslationError(f"{failed_sections}/{len(sections)} 个分段解析失败，中止以避免部分翻译")

    if not all_replacements:
        raise TranslationError("所有分段均未返回有效的 replacements")

    # ── 即时校验：过滤无法匹配源码的无效规则 ──
    validated: dict[str, str] = {}
    skipped_keys = 0
    for key, value in all_replacements.items():
        if key in content:
            validated[key] = value
        else:
            # 尝试 strip 外层引号后重试
            stripped = key.strip("'\"")
            if stripped != key and stripped in content:
                validated[stripped] = value
            else:
                skipped_keys += 1
                print(f"  丢弃无效 key [{skipped_keys}]: {key[:80]}", file=sys.stderr)

    if skipped_keys > 0:
        print(f"  即时校验汇总: {len(validated)} 有效, {skipped_keys} 无效已丢弃", file=sys.stderr)

    if not validated:
        raise TranslationError("所有规则经校验后均无效")

    # 丢弃率 >= 30% 说明 LLM 输出质量差，不标记 _validated
    total_keys = len(all_replacements)
    discard_rate = skipped_keys / total_keys if total_keys > 0 else 0
    is_validated = discard_rate < 0.3
    if not is_validated:
        print(f"  警告: 丢弃率 {discard_rate:.0%} >= 30%，不标记 _validated", file=sys.stderr)

    data = {
        "file": str(source_file.name),
        "description": f"{lang_name} 文件字符串翻译",
        "_validated": is_validated,
        "_stats": {"total": total_keys, "valid": len(validated), "discarded": skipped_keys},
        "replacements": validated,
    }
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────
# 文件扫描
# ──────────────────────────────────────────

def get_all_translate_files(config: dict, upstream_dir: Path) -> list[dict]:
    """从配置中获取所有需要翻译的文件列表"""
    files = []

    for module in config.get("modules", []):
        module_type = module.get("type", "file_override")

        if "files" in module:
            for file_entry in module["files"]:
                source = upstream_dir / file_entry["source"]
                translation = ROOT_DIR / file_entry["translation"]
                if source.exists():
                    files.append({
                        "source_path": file_entry["source"],
                        "source_file": source,
                        "target_file": translation,
                        "type": module_type,
                        "module": module["name"],
                        "priority": module.get("priority", "P2"),
                    })

        if "source_dir" in module:
            source_dir = upstream_dir / module["source_dir"]
            translation_dir = ROOT_DIR / module["translation_dir"]
            pattern = module.get("pattern", "**/*.md")
            if source_dir.exists():
                for source_file in sorted(source_dir.glob(pattern)):
                    rel_path = source_file.relative_to(source_dir)
                    target_file = translation_dir / rel_path
                    files.append({
                        "source_path": f"{module['source_dir']}/{rel_path}",
                        "source_file": source_file,
                        "target_file": target_file,
                        "type": module_type,
                        "module": module["name"],
                        "priority": module.get("priority", "P2"),
                    })

    return files


# ──────────────────────────────────────────
# 单文件翻译任务（供线程池调用）
# ──────────────────────────────────────────

def _translate_one(
    f: dict,
    index: int,
    total: int,
    client: OpenAI,
    model: str,
    glossary_text: str,
    rate_limiter: RateLimiter,
    timeout: int,
    cache: dict,
) -> tuple[str, bool, str]:
    """
    翻译单个文件。返回 (source_path, 是否成功, 错误信息)。
    成功时同时更新 cache（线程安全）。
    """
    source_path = f["source_path"]
    print(f"\n[{index}/{total}] 翻译 {source_path}...")

    try:
        if f["type"] == "file_override":
            translate_markdown_file(
                client, model, glossary_text, f["source_file"], f["target_file"],
                rate_limiter, timeout,
            )
        elif f["type"] == "string_replace":
            translate_code_strings(
                client, model, glossary_text, f["source_file"], f["target_file"],
                rate_limiter, timeout,
            )

        # 更新 hash 缓存（线程安全）
        with _cache_lock:
            cache[source_path] = {
                "source_hash": compute_file_hash(f["source_file"]),
                "translated_at": datetime.now(timezone.utc).isoformat(),
                "model": model,
            }
        save_hash_cache(cache)
        print(f"  完成 ✓")
        return source_path, True, ""

    except Exception as e:
        print(f"  失败 ✗: {e}", file=sys.stderr)
        return source_path, False, str(e)


# ──────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="hermes-agent-zh 翻译引擎")
    parser.add_argument("--force", action="store_true", help="强制重新翻译所有文件")
    parser.add_argument("--file", type=str, help="只翻译指定文件（source 路径）")
    parser.add_argument("--module", type=str, help="只翻译指定模块")
    parser.add_argument("--priority", type=str, help="只翻译指定优先级（P0/P1/P2）")
    parser.add_argument("--upstream", type=str, default=None, help="上游仓库本地路径")
    parser.add_argument("--dry-run", action="store_true", help="只显示需要翻译的文件，不执行翻译")
    parser.add_argument("--workers", type=int, default=None, help="并发线程数（覆盖环境变量）")
    parser.add_argument("--rpm", type=int, default=None, help="每分钟最大请求数（覆盖环境变量）")
    parser.add_argument("--tpm", type=int, default=None, help="每分钟最大 token 数（覆盖环境变量）")
    parser.add_argument("--timeout", type=int, default=None, help="单次 API 超时秒数（覆盖环境变量）")
    parser.add_argument("--serial", action="store_true", help="禁用并发，串行翻译（调试用）")
    args = parser.parse_args()

    # 加载配置
    env = load_env()
    config = load_config()
    glossary_text = load_glossary()
    cache = load_hash_cache()

    workers = args.workers or env["workers"]
    rpm = args.rpm or env["rpm"]
    tpm = args.tpm or env["tpm"]
    timeout = args.timeout or env["timeout"]

    if args.serial:
        workers = 1
    else:
        # 自适应：根据 TPM 限制调整并发数，避免线程争抢导致全部阻塞
        # 假设平均每请求 ~5000 tokens，每分钟最多 tpm/5000 个请求
        max_useful_workers = max(1, tpm // 5000)
        if workers > max_useful_workers:
            print(f"提示: 根据 TPM {tpm:,} 自动调整并发从 {workers} 降为 {max_useful_workers}", file=sys.stderr)
            workers = max_useful_workers

    # 确定上游目录
    upstream_dir = Path(args.upstream) if args.upstream else ROOT_DIR / "upstream"
    if not upstream_dir.exists():
        print(f"错误: 上游目录不存在: {upstream_dir}", file=sys.stderr)
        print("请先运行 scripts/build.py 克隆上游仓库，或使用 --upstream 指定路径", file=sys.stderr)
        sys.exit(1)

    # 获取所有需要翻译的文件
    all_files = get_all_translate_files(config, upstream_dir)

    # 过滤
    if args.file:
        all_files = [f for f in all_files if f["source_path"] == args.file]
    if args.module:
        all_files = [f for f in all_files if f["module"] == args.module]
    if args.priority:
        all_files = [f for f in all_files if f["priority"] == args.priority]

    # 增量检测
    to_translate = []
    skipped = 0
    for f in all_files:
        if should_translate(f["source_path"], f["source_file"], cache, args.force):
            to_translate.append(f)
        else:
            skipped += 1

    print(f"文件总数: {len(all_files)}, 需要翻译: {len(to_translate)}, 跳过(未变更): {skipped}")
    print(f"并发: {workers} 线程, 限速: {rpm} RPM / {tpm:,} TPM, 超时: {timeout}s/请求")

    if args.dry_run:
        for f in to_translate:
            print(f"  [{f['priority']}][{f['module']}] {f['source_path']}")
        return

    if not to_translate:
        print("所有文件均为最新，无需翻译。")
        return

    # 初始化
    client = OpenAI(api_key=env["api_key"], base_url=env["base_url"])
    model = env["model"]
    rate_limiter = RateLimiter(rpm=rpm, tpm=tpm)

    # 执行翻译（并发）— glossary_text 传入每个任务，由任务根据文件类型构建 prompt
    success = 0
    failed = 0
    total = len(to_translate)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                _translate_one,
                f, i + 1, total,
                client, model, glossary_text,
                rate_limiter, timeout, cache,
            ): f
            for i, f in enumerate(to_translate)
        }

        for future in as_completed(futures):
            _, ok, err = future.result()
            if ok:
                success += 1
            else:
                failed += 1

    print(f"\n翻译完成: 成功 {success}, 失败 {failed}, 跳过 {skipped}")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
