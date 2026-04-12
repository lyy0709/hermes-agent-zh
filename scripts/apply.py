#!/usr/bin/env python3
"""
翻译应用引擎 - 将翻译结果应用到上游源码。

两种应用模式:
1. file_override: 用翻译后的文件直接覆盖上游对应文件
2. string_replace: 读取 JSON 替换规则，对源码执行字符串替换
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

ROOT_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT_DIR / "translations"
CONFIG_FILE = TRANSLATIONS_DIR / "config.json"


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_file_override(source_file: Path, target_file: Path) -> str:
    """文件覆盖模式：用翻译文件替换上游文件"""
    if not source_file.exists():
        return "skipped"  # 翻译文件不存在，跳过

    target_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, target_file)
    return "applied"


def apply_string_replace(rules_file: Path, target_file: Path) -> tuple[str, int, int]:
    """字符串替换模式：读取 JSON 规则，对源码执行替换"""
    if not rules_file.exists():
        return "skipped", 0, 0

    if not target_file.exists():
        return "target_missing", 0, 0

    with open(rules_file, "r", encoding="utf-8") as f:
        rules = json.load(f)

    replacements = rules.get("replacements", {})
    if not replacements:
        return "no_rules", 0, 0

    content = target_file.read_text(encoding="utf-8")
    original_content = content
    applied = 0
    existed = 0

    # 按原文长度降序排列，避免短字符串替换破坏长字符串
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

    for original, translated in sorted_replacements:
        if original in content:
            content = content.replace(original, translated)
            applied += 1
        elif translated in content:
            existed += 1

    if content != original_content:
        target_file.write_text(content, encoding="utf-8")

    return "applied", applied, existed


def apply_all(upstream_dir: Path, verbose: bool = False) -> dict:
    """应用所有翻译到上游源码"""
    config = load_config()
    stats = {"applied": 0, "skipped": 0, "failed": 0, "existed": 0}

    for module in config.get("modules", []):
        module_name = module["name"]
        module_type = module.get("type", "file_override")

        print(f"\n📦 模块: {module_name} ({module.get('description', '')})")

        if "files" in module:
            for file_entry in module["files"]:
                source_path = file_entry["source"]
                translation_path = file_entry["translation"]

                translation_file = ROOT_DIR / translation_path
                target_file = upstream_dir / source_path

                if module_type == "file_override":
                    status = apply_file_override(translation_file, target_file)
                    if status == "applied":
                        stats["applied"] += 1
                        if verbose:
                            print(f"  ✓ {source_path}")
                    else:
                        stats["skipped"] += 1
                        if verbose:
                            print(f"  - {source_path} ({status})")

                elif module_type == "string_replace":
                    status, applied, existed = apply_string_replace(translation_file, target_file)
                    if status == "applied" and applied > 0:
                        stats["applied"] += applied
                        stats["existed"] += existed
                        if verbose:
                            print(f"  ✓ {source_path}: {applied} applied, {existed} existed")
                    elif status == "skipped":
                        stats["skipped"] += 1
                        if verbose:
                            print(f"  - {source_path} (翻译规则不存在)")
                    elif status == "target_missing":
                        stats["failed"] += 1
                        if verbose:
                            print(f"  ✗ {source_path} (上游文件不存在)")
                    else:
                        stats["skipped"] += 1
                        if verbose:
                            print(f"  - {source_path} ({status}, existed: {existed})")

        if "source_dir" in module:
            source_dir = module["source_dir"]
            translation_dir = ROOT_DIR / module["translation_dir"]
            pattern = module.get("pattern", "**/*.md")

            if translation_dir.exists():
                for trans_file in sorted(translation_dir.glob(pattern)):
                    rel_path = trans_file.relative_to(translation_dir)
                    target_file = upstream_dir / source_dir / rel_path

                    status = apply_file_override(trans_file, target_file)
                    if status == "applied":
                        stats["applied"] += 1
                        if verbose:
                            print(f"  ✓ {source_dir}/{rel_path}")
                    else:
                        stats["skipped"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="应用翻译到上游源码")
    parser.add_argument("--upstream", type=str, default=None, help="上游仓库本地路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    args = parser.parse_args()

    upstream_dir = Path(args.upstream) if args.upstream else ROOT_DIR / "upstream"
    if not upstream_dir.exists():
        print(f"错误: 上游目录不存在: {upstream_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"应用翻译到: {upstream_dir}")
    stats = apply_all(upstream_dir, verbose=args.verbose)

    print(f"\n📊 统计:")
    print(f"  应用: {stats['applied']}")
    print(f"  已存在: {stats['existed']}")
    print(f"  跳过: {stats['skipped']}")
    print(f"  失败: {stats['failed']}")


if __name__ == "__main__":
    main()
