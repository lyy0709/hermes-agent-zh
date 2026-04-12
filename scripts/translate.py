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
    - TPM：每分钟最大 token 数
    - 每次 acquire() 返回 reservation_id，release/report 通过 ID 精确操作

    线程安全：多线程并发调用时自动排队等待。
    """

    def __init__(self, rpm: int = 1000, tpm: int = 100_000):
        if rpm <= 0:
            raise ValueError(f"RPM 必须为正整数，当前值: {rpm}")
        if tpm <= 0:
            raise ValueError(f"TPM 必须为正整数，当前值: {tpm}")
        self.rpm = rpm
        self.tpm = tpm
        self.window = 60.0
        self._req_records: list[float] = []
        # 请求级记账：{reservation_id: (timestamp, tokens)}
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
        """当前窗口内已使用的 token 总数"""
        return sum(n for _, n in self._token_ledger.values())

    def acquire(self, estimated_tokens: int = 0) -> int:
        """
        阻塞直到 RPM 和 TPM 配额均可用。

        参数:
            estimated_tokens: 本次请求预估消耗的 token 数（输入+输出）

        返回:
            reservation_id: 用于后续 release/report 精确操作

        异常:
            TokenBudgetExceeded: 单个请求超过 TPM 上限（不可重试）
        """
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
                tpm_ok = (self._tokens_in_window() + estimated_tokens) <= self.tpm

                if rpm_ok and tpm_ok:
                    self._req_records.append(now)
                    rid = self._next_id
                    self._next_id += 1
                    if estimated_tokens > 0:
                        self._token_ledger[rid] = (now, estimated_tokens)
                    return rid

                wait_seconds = 0.5
                if not rpm_ok and self._req_records:
                    wait_seconds = max(wait_seconds, self._req_records[0] + self.window - now)
                if not tpm_ok and self._token_ledger:
                    earliest = min(t for t, _ in self._token_ledger.values())
                    wait_seconds = max(wait_seconds, earliest + self.window - now)

            time.sleep(min(wait_seconds + 0.1, 5.0))

    def release(self, reservation_id: int):
        """释放指定 reservation 的全部 token（请求失败时调用）。"""
        with self._lock:
            self._token_ledger.pop(reservation_id, None)

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

def build_system_prompt(glossary_text: str) -> str:
    """构建翻译 system prompt"""
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


def build_string_extract_prompt(glossary_text: str) -> str:
    """构建字符串提取和翻译的 system prompt"""
    return f"""你是一个专业的技术文档翻译员。你需要从 Python 源代码中提取用户面向的字符串，并翻译为简体中文。

任务：
1. 识别代码中所有用户可见的字符串（提示信息、错误消息、描述文本、标签等）
2. 忽略：变量名、函数名、导入语句、注释、日志格式字符串、技术标识符
3. 对每个用户面向的字符串，输出 JSON 替换规则

输出格式（严格 JSON）：
{{
  "file": "文件路径",
  "description": "文件功能描述",
  "replacements": {{
    "原始字符串（包含引号）": "翻译后的字符串（包含引号）"
  }}
}}

规则：
- 替换规则中的 key 和 value 都必须包含原始代码中的引号
- 只翻译用户面向的文本，不要翻译技术字符串
- 保持字符串中的格式占位符（如 {{}}、%s、\\n 等）
- 只输出 JSON，不要添加任何解释

术语表：
{glossary_text}"""


# ──────────────────────────────────────────
# Markdown 分段
# ──────────────────────────────────────────

def split_markdown_sections(content: str, max_chars: int = 12000) -> list[str]:
    """将大型 Markdown 文件按 heading 分割为多段"""
    if len(content) <= max_chars:
        return [content]

    sections = []
    current = []
    current_len = 0

    lines = content.split("\n")
    for line in lines:
        is_heading = re.match(r"^#{1,3}\s", line)
        line_len = len(line) + 1

        if is_heading and current_len > max_chars // 2:
            sections.append("\n".join(current))
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        sections.append("\n".join(current))

    return sections


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
            # API 调用失败：精确释放本次 reservation 的 token
            rate_limiter.release(rid)
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"  API 调用失败，{wait_time}s 后重试: {e}", file=sys.stderr)
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
    system_prompt: str,
    source_file: Path,
    target_file: Path,
    rate_limiter: RateLimiter,
    timeout: int = 300,
):
    """翻译 Markdown 文件"""
    content = source_file.read_text(encoding="utf-8")
    sections = split_markdown_sections(content)

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
    system_prompt: str,
    source_file: Path,
    target_file: Path,
    rate_limiter: RateLimiter,
    timeout: int = 300,
):
    """提取并翻译代码中的用户面向字符串。翻译失败时抛出 TranslationError。"""
    content = source_file.read_text(encoding="utf-8")

    prompt = f"以下是 Python 源代码文件 `{source_file.name}`:\n\n```python\n{content}\n```"
    result = translate_text(client, model, system_prompt, prompt, rate_limiter, timeout)

    # 提取 JSON（支持多种 LLM 输出格式）
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", result)
    if json_match:
        result = json_match.group(1)

    # 验证 JSON 格式 — 失败时抛异常，不写入缓存
    try:
        data = json.loads(result)
    except json.JSONDecodeError as e:
        raise TranslationError(f"LLM 返回的不是有效 JSON: {e}") from e

    if not data.get("replacements"):
        raise TranslationError("LLM 返回的 replacements 为空")

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
    md_prompt: str,
    code_prompt: str,
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
                client, model, md_prompt, f["source_file"], f["target_file"],
                rate_limiter, timeout,
            )
        elif f["type"] == "string_replace":
            translate_code_strings(
                client, model, code_prompt, f["source_file"], f["target_file"],
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

    md_system_prompt = build_system_prompt(glossary_text)
    code_system_prompt = build_string_extract_prompt(glossary_text)

    # 执行翻译（并发）
    success = 0
    failed = 0
    total = len(to_translate)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                _translate_one,
                f, i + 1, total,
                client, model, md_system_prompt, code_system_prompt,
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
