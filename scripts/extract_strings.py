#!/usr/bin/env python3
"""
字符串提取 - 从 Python 源码中提取用户面向的字符串。

扫描指定的 Python 文件，提取可能需要翻译的用户面向字符串，
输出为 JSON 格式供 translate.py 使用。
"""

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# 不需要翻译的字符串模式（统一小写，比对时也用 .lower()）
SKIP_PATTERNS = {
    # 技术标识符
    "utf-8", "utf8", "ascii", "latin-1",
    "get", "post", "put", "delete", "patch", "head", "options",
    "json", "yaml", "toml", "xml", "html", "css", "js",
    "true", "false", "null", "none",
    # 格式字符串片段
    "%s", "%d", "%f", "{}",
}


def is_user_facing(value: str) -> bool:
    """判断字符串是否是用户面向的文本"""
    value = value.strip()

    # 跳过空字符串和单字符
    if len(value) <= 1:
        return False

    # 跳过纯技术标识符
    if value.lower() in SKIP_PATTERNS:
        return False

    # 跳过纯数字/符号
    if not any(c.isalpha() for c in value):
        return False

    # 跳过看起来像路径/URL的字符串
    if value.startswith(("/", "http://", "https://", "file://", "./", "../")):
        return False

    # 跳过看起来像变量/函数名的字符串（全小写、下划线、点号）
    if all(c.isalnum() or c in "_." for c in value) and value == value.lower():
        return False

    # 包含空格或大写字母的多词字符串，更可能是用户面向的
    has_spaces = " " in value
    has_upper = any(c.isupper() for c in value)

    return has_spaces or has_upper or len(value) > 10


class StringExtractor(ast.NodeVisitor):
    """AST 访问器，提取用户面向的字符串"""

    def __init__(self):
        self.strings = []

    def visit_Constant(self, node):
        if isinstance(node.value, str) and is_user_facing(node.value):
            self.strings.append({
                "value": node.value,
                "line": node.lineno,
            })
        self.generic_visit(node)


def extract_strings(file_path: Path) -> list[dict]:
    """从 Python 文件中提取用户面向的字符串"""
    content = file_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    extractor = StringExtractor()
    extractor.visit(tree)
    return extractor.strings


def main():
    parser = argparse.ArgumentParser(description="从 Python 源码提取用户面向的字符串")
    parser.add_argument("files", nargs="+", help="要扫描的 Python 文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--min-length", type=int, default=3, help="最小字符串长度")
    args = parser.parse_args()

    all_results = {}
    for file_path_str in args.files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"警告: 文件不存在: {file_path}", file=sys.stderr)
            continue

        strings = extract_strings(file_path)
        strings = [s for s in strings if len(s["value"]) >= args.min_length]

        if strings:
            all_results[str(file_path)] = strings

    if args.json:
        print(json.dumps(all_results, indent=2, ensure_ascii=False))
    else:
        for file_path, strings in all_results.items():
            print(f"\n📄 {file_path} ({len(strings)} 个字符串):")
            for s in strings:
                preview = s["value"][:80]
                if len(s["value"]) > 80:
                    preview += "..."
                print(f"  L{s['line']:4d}: {preview!r}")

        total = sum(len(s) for s in all_results.values())
        print(f"\n总计: {len(all_results)} 个文件, {total} 个用户面向的字符串")


if __name__ == "__main__":
    main()
