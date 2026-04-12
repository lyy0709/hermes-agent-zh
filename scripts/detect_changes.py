#!/usr/bin/env python3
"""
变更检测 - 检测上游哪些文件发生了变更，需要重新翻译。

双重检测机制:
1. Git diff 粗筛: 比较上次同步 SHA 与当前 HEAD
2. Hash 精确比对: 计算文件 SHA-256 hash 与缓存比对
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT_DIR / "translations"
CONFIG_FILE = TRANSLATIONS_DIR / "config.json"
HASH_CACHE_FILE = TRANSLATIONS_DIR / ".hash-cache.json"
LAST_SHA_FILE = ROOT_DIR / ".last-synced-sha"


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_hash_cache() -> dict:
    if not HASH_CACHE_FILE.exists():
        return {}
    with open(HASH_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def get_last_synced_sha() -> str | None:
    if LAST_SHA_FILE.exists():
        return LAST_SHA_FILE.read_text().strip()
    return None


def get_git_changed_files(upstream_dir: Path, last_sha: str | None) -> tuple[set[str], bool]:
    """通过 git diff 获取变更文件列表。返回 (文件集合, diff是否可靠)。"""
    if not last_sha:
        return set(), False  # 无基线，标记不可靠以强制 hash 检查

    # 验证 SHA 是否存在（浅克隆可能不包含）
    verify = subprocess.run(
        ["git", "rev-parse", "--verify", f"{last_sha}^{{commit}}"],
        cwd=upstream_dir,
        capture_output=True,
        text=True,
    )
    if verify.returncode != 0:
        print(f"  警告: SHA {last_sha[:12]} 不在仓库历史中（浅克隆），将对所有文件做 hash 比对", file=sys.stderr)
        return set(), False

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", last_sha, "HEAD"],
            cwd=upstream_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        files = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
        return files, True
    except subprocess.CalledProcessError:
        return set(), False


def get_tracked_files(config: dict) -> set[str]:
    """从配置中获取所有被追踪的源文件路径"""
    tracked = set()
    for module in config.get("modules", []):
        if "files" in module:
            for f in module["files"]:
                tracked.add(f["source"])
        if "source_dir" in module:
            tracked.add(f"DIR:{module['source_dir']}")
    return tracked


def detect_changes(upstream_dir: Path, force_hash_check: bool = False) -> dict:
    """
    检测需要���译的文件变更。

    返回:
        {
            "needs_translation": [...],   # 需��翻译的文件
            "new_files": [...],           # 新增的未翻��文件
            "unchanged": [...],           # 未变更的文件
        }
    """
    config = load_config()
    cache = load_hash_cache()
    last_sha = get_last_synced_sha()

    # Git diff 粗筛
    git_changed, diff_reliable = get_git_changed_files(upstream_dir, last_sha)

    # 如果 diff 不可靠（浅克隆/SHA 不存在），强制对所有文件做 hash 比对
    if not diff_reliable:
        force_hash_check = True

    needs_translation = []
    new_files = []
    unchanged = []

    for module in config.get("modules", []):
        files_to_check = []

        if "files" in module:
            for f in module["files"]:
                source_file = upstream_dir / f["source"]
                if source_file.exists():
                    files_to_check.append({
                        "source_path": f["source"],
                        "source_file": source_file,
                        "module": module["name"],
                    })

        if "source_dir" in module:
            source_dir = upstream_dir / module["source_dir"]
            pattern = module.get("pattern", "**/*.md")
            if source_dir.exists():
                for sf in sorted(source_dir.glob(pattern)):
                    rel = sf.relative_to(upstream_dir)
                    files_to_check.append({
                        "source_path": str(rel),
                        "source_file": sf,
                        "module": module["name"],
                    })

        for entry in files_to_check:
            sp = entry["source_path"]

            # 未翻译过
            if sp not in cache:
                new_files.append(entry)
                continue

            # Git diff 或强制 hash 检查
            in_git_diff = sp in git_changed or any(sp.startswith(d) for d in git_changed)
            if in_git_diff or force_hash_check:
                current_hash = compute_file_hash(entry["source_file"])
                if current_hash != cache[sp].get("source_hash"):
                    needs_translation.append(entry)
                else:
                    unchanged.append(entry)
            else:
                unchanged.append(entry)

    return {
        "needs_translation": needs_translation,
        "new_files": new_files,
        "unchanged": unchanged,
    }


def main():
    parser = argparse.ArgumentParser(description="检测上游变更")
    parser.add_argument("--upstream", type=str, default=None, help="上游仓库本地路径")
    parser.add_argument("--hash-check", action="store_true", help="对所有文件进行 hash 比对（不仅依赖 git diff）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    upstream_dir = Path(args.upstream) if args.upstream else ROOT_DIR / "upstream"
    if not upstream_dir.exists():
        print(f"错误: 上游目录不存在: {upstream_dir}", file=sys.stderr)
        sys.exit(1)

    result = detect_changes(upstream_dir, force_hash_check=args.hash_check)

    if args.json:
        output = {
            "needs_translation": [e["source_path"] for e in result["needs_translation"]],
            "new_files": [e["source_path"] for e in result["new_files"]],
            "unchanged_count": len(result["unchanged"]),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"需要重新翻��: {len(result['needs_translation'])} 个文件")
        for e in result["needs_translation"]:
            print(f"  [变更] {e['source_path']}")

        print(f"\n新增未翻译: {len(result['new_files'])} 个文件")
        for e in result["new_files"]:
            print(f"  [新增] {e['source_path']}")

        print(f"\n未变更: {len(result['unchanged'])} 个文件")


if __name__ == "__main__":
    main()
