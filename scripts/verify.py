#!/usr/bin/env python3
"""
翻译验证 - 验证翻译完整性和质量。

检查项:
1. 翻译覆盖率：所有配置中的文件是否都有翻译
2. JSON 格式验证：所有 JSON 翻译文件格式是否正确
3. 替换规则验证：string_replace 类型的规则是否能匹配上游源码
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

ROOT_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT_DIR / "translations"
CONFIG_FILE = TRANSLATIONS_DIR / "config.json"
GLOSSARY_FILE = TRANSLATIONS_DIR / "glossary.json"


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def check_coverage(config: dict, upstream_dir: Path) -> list[dict]:
    """检查翻译覆盖率"""
    issues = []

    for module in config.get("modules", []):
        if "files" in module:
            for f in module["files"]:
                trans_file = ROOT_DIR / f["translation"]
                source_file = upstream_dir / f["source"]

                if source_file.exists() and not trans_file.exists():
                    issues.append({
                        "level": "warning",
                        "module": module["name"],
                        "file": f["source"],
                        "message": f"缺少翻译: {f['translation']}",
                    })

        if "source_dir" in module:
            source_dir = upstream_dir / module["source_dir"]
            translation_dir = ROOT_DIR / module["translation_dir"]
            pattern = module.get("pattern", "**/*.md")

            if source_dir.exists():
                for sf in sorted(source_dir.glob(pattern)):
                    rel = sf.relative_to(source_dir)
                    tf = translation_dir / rel
                    if not tf.exists():
                        issues.append({
                            "level": "warning",
                            "module": module["name"],
                            "file": f"{module['source_dir']}/{rel}",
                            "message": f"缺少翻译: {module['translation_dir']}/{rel}",
                        })

    return issues


def check_json_format() -> list[dict]:
    """验证所有 JSON 翻译文件格式"""
    issues = []

    for json_file in TRANSLATIONS_DIR.rglob("*.json"):
        if json_file.name == ".hash-cache.json":
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            issues.append({
                "level": "error",
                "file": str(json_file.relative_to(ROOT_DIR)),
                "message": f"JSON 格式错误: {e}",
            })

    return issues


def check_replacements(config: dict, upstream_dir: Path, strict: bool = False) -> list[dict]:
    """验证字符串替换规则能否匹配上游源码。

    分级验证：
    - _validated=true 的文件（经过生成时校验）：不匹配 = error（strict 模式）
    - 无标记的旧格式文件：不匹配 = warning
    """
    issues = []

    for module in config.get("modules", []):
        if module.get("type") != "string_replace":
            continue
        if "files" not in module:
            continue

        for f in module["files"]:
            rules_file = ROOT_DIR / f["translation"]
            target_file = upstream_dir / f["source"]

            if not rules_file.exists() or not target_file.exists():
                continue

            try:
                with open(rules_file, "r", encoding="utf-8") as rf:
                    rules = json.load(rf)
            except (json.JSONDecodeError, OSError):
                continue

            content = target_file.read_text(encoding="utf-8")
            replacements = rules.get("replacements", {})
            is_validated = rules.get("_validated", False)

            # 分级：经过即时校验的文件用 strict，旧格式用 warning
            fail_level = "error" if (strict and is_validated) else "warning"

            matched = 0
            unmatched = 0
            for original, translated in replacements.items():
                if original in content:
                    matched += 1
                elif translated in content:
                    matched += 1  # 译文已存在（已被应用过）
                else:
                    unmatched += 1
                    issues.append({
                        "level": fail_level,
                        "module": module["name"],
                        "file": f["source"],
                        "message": "替换规则失效: 原文未找到",
                        "original": original[:80],
                    })

            # 输出匹配率统计
            total = matched + unmatched
            if total > 0:
                rate = matched / total * 100
                status = "validated" if is_validated else "legacy"
                print(f"  [{module['name']}] {f['source']}: {matched}/{total} 匹配 ({rate:.0f}%) [{status}]", file=sys.stderr)

    return issues


def load_glossary_terms() -> dict[str, str]:
    """加载术语表的英文→中文映射"""
    if not GLOSSARY_FILE.exists():
        return {}
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("terms", {})


def check_glossary_compliance() -> list[dict]:
    """
    校验已翻译的 Markdown 文件是否遵守术语表。

    检查逻辑：在翻译后的中文文本中搜索术语表中的英文原词。
    如果出现了英文原词且附近没有对应的中文译词，则报告为潜在的术语违规。
    排除代码块和行内代码中的出现。
    """
    terms = load_glossary_terms()
    if not terms:
        return []

    issues = []

    # 只检查值得校验的术语（排除保留英文的术语，如 MCP → MCP）
    checkable_terms = {
        en: zh for en, zh in terms.items()
        if en.lower() != zh.lower() and not zh.isascii()
    }

    if not checkable_terms:
        return []

    # 扫描所有已翻译的 Markdown 文件
    for md_file in sorted(TRANSLATIONS_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        rel_path = str(md_file.relative_to(ROOT_DIR))

        # 去除代码块和行内代码，只检查正文部分
        clean = re.sub(r"```[\s\S]*?```", "", content)
        clean = re.sub(r"`[^`]+`", "", clean)
        # 去除 URL
        clean = re.sub(r"https?://\S+", "", clean)
        # 去除 Markdown 链接目标
        clean = re.sub(r"\]\([^)]+\)", "]", clean)

        for en_term, zh_term in checkable_terms.items():
            # 使用单词边界匹配英文术语（大小写不敏感）
            pattern = rf"\b{re.escape(en_term)}\b"
            matches = list(re.finditer(pattern, clean, re.IGNORECASE))

            if not matches:
                continue

            # 检查附近 (同一段落) 是否有对应中文译词
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(clean), match.end() + 200)
                context = clean[start:end]

                if zh_term not in context:
                    issues.append({
                        "level": "warning",
                        "module": "glossary",
                        "file": rel_path,
                        "message": f"术语未按术语表翻译: \"{en_term}\" 应为 \"{zh_term}\"",
                    })
                    break  # 每个文件每个术语只报一次

    return issues


def main():
    parser = argparse.ArgumentParser(description="验证翻译完整性")
    parser.add_argument("--upstream", type=str, default=None, help="上游仓库本地路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--strict", action="store_true", help="严格模式：将替换规则失效也视为 error")
    args = parser.parse_args()

    upstream_dir = Path(args.upstream) if args.upstream else ROOT_DIR / "upstream"

    all_issues = []

    # JSON 格式检查（不需要上游目录）
    all_issues.extend(check_json_format())

    # 术语表合规检查（不需要上游目录）
    all_issues.extend(check_glossary_compliance())

    # 需要上游目录的检查
    if upstream_dir.exists():
        config = load_config()
        all_issues.extend(check_coverage(config, upstream_dir))
        all_issues.extend(check_replacements(config, upstream_dir, strict=args.strict))
    else:
        print(f"警告: 上游目录不存在 ({upstream_dir})，跳过覆盖率和替换规则检查", file=sys.stderr)

    if args.json:
        print(json.dumps(all_issues, indent=2, ensure_ascii=False))
    else:
        errors = [i for i in all_issues if i["level"] == "error"]
        warnings = [i for i in all_issues if i["level"] == "warning"]

        if errors:
            print(f"\n❌ 错误: {len(errors)}")
            for issue in errors:
                print(f"  [{issue.get('module', '-')}] {issue.get('file', '-')}: {issue['message']}")

        if warnings:
            print(f"\n⚠️  警告: {len(warnings)}")
            for issue in warnings:
                print(f"  [{issue.get('module', '-')}] {issue.get('file', '-')}: {issue['message']}")

        if not errors and not warnings:
            print("✅ 翻译验证通过，未发现问题。")

        print(f"\n总计: {len(errors)} 错误, {len(warnings)} 警告")

    sys.exit(1 if any(i["level"] == "error" for i in all_issues) else 0)


if __name__ == "__main__":
    main()
