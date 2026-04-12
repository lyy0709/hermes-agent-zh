#!/usr/bin/env python3
"""
构建脚本 - 克隆上游仓库 + 应用翻译 + 构建项目。

流程:
1. 克隆/更新上游 hermes-agent 仓库
2. 应用所有翻译（文件覆盖 + 字符串替换）
3. 验证翻译完整性
4. 输出构建结果
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT_DIR / "translations"
CONFIG_FILE = TRANSLATIONS_DIR / "config.json"
UPSTREAM_DIR = ROOT_DIR / "upstream"
LAST_SHA_FILE = ROOT_DIR / ".last-synced-sha"
LAST_VERSION_FILE = ROOT_DIR / ".last-synced-version"


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cmd(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """执行命令并打印输出"""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        for line in result.stdout.strip().split("\n")[:5]:
            print(f"    {line}")
        if result.stdout.strip().count("\n") > 5:
            print(f"    ... ({result.stdout.strip().count(chr(10))} 行)")
    if result.returncode != 0 and check:
        print(f"  错误: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result


def clone_or_update_upstream(config: dict, tag: str | None = None, sha: str | None = None):
    """克隆或更新上游仓库"""
    upstream_url = config["upstream"]["url"]

    if UPSTREAM_DIR.exists():
        print("📥 更新上游仓库...")
        run_cmd(["git", "fetch", "--all", "--tags"], cwd=UPSTREAM_DIR)
    else:
        print("📥 克隆上游仓库...")
        run_cmd(["git", "clone", "--depth", "1", upstream_url, str(UPSTREAM_DIR)])
        if tag or sha:
            # 需要完整历史才能 checkout 特定版本
            run_cmd(["git", "fetch", "--unshallow"], cwd=UPSTREAM_DIR, check=False)

    if tag:
        print(f"📌 切换到 tag: {tag}")
        run_cmd(["git", "checkout", tag], cwd=UPSTREAM_DIR)
    elif sha:
        print(f"📌 切换到 commit: {sha[:12]}")
        run_cmd(["git", "fetch", "origin", sha], cwd=UPSTREAM_DIR, check=False)
        run_cmd(["git", "checkout", sha], cwd=UPSTREAM_DIR)
    else:
        print("📌 使用最新 main 分支")
        run_cmd(["git", "checkout", config["upstream"].get("branch", "main")], cwd=UPSTREAM_DIR)
        run_cmd(["git", "pull", "origin", config["upstream"].get("branch", "main")], cwd=UPSTREAM_DIR)


def get_upstream_info() -> dict:
    """获取上游仓库的版本信息"""
    # 获取当前 SHA
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=UPSTREAM_DIR, capture_output=True, text=True
    )
    sha = result.stdout.strip()

    # 获取最新 tag
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=UPSTREAM_DIR, capture_output=True, text=True
    )
    version = result.stdout.strip() if result.returncode == 0 else "unknown"

    return {"sha": sha, "version": version}


def save_sync_state(sha: str, version: str):
    """保存同步状态"""
    LAST_SHA_FILE.write_text(sha)
    LAST_VERSION_FILE.write_text(version)


def main():
    parser = argparse.ArgumentParser(description="构建 hermes-agent 中文版")
    parser.add_argument("--tag", type=str, help="克隆上游指定 tag")
    parser.add_argument("--sha", type=str, help="克隆上游指定 commit SHA")
    parser.add_argument("--clean", action="store_true", help="清理上游目录后重新克隆")
    parser.add_argument("--skip-clone", action="store_true", help="跳过克隆步骤（使用已有的 upstream/）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    args = parser.parse_args()

    config = load_config()

    # Step 1: 克隆/更新上游
    if not args.skip_clone:
        if args.clean and UPSTREAM_DIR.exists():
            print("🧹 清理上游目录...")
            shutil.rmtree(UPSTREAM_DIR)

        clone_or_update_upstream(config, tag=args.tag, sha=args.sha)
    else:
        if not UPSTREAM_DIR.exists():
            print("错误: upstream/ 目录不存在，无法跳过克隆", file=sys.stderr)
            sys.exit(1)
        print("⏩ 跳过克隆步骤")

    # Step 2: 获取上游信息
    info = get_upstream_info()
    print(f"\n📋 上游信息:")
    print(f"  SHA: {info['sha'][:12]}")
    print(f"  版本: {info['version']}")

    # Step 3: 应用翻译
    print("\n🔄 应用翻译...")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from apply import apply_all
    stats = apply_all(UPSTREAM_DIR, verbose=args.verbose)
    print(f"\n📊 应用统计: {stats['applied']} 应用, {stats['existed']} 已存在, {stats['skipped']} 跳过, {stats['failed']} 失败")

    # Step 4: 验证
    print("\n🔍 验证翻译...")
    verify_result = subprocess.run(
        [sys.executable, str(ROOT_DIR / "scripts" / "verify.py"), "--upstream", str(UPSTREAM_DIR), "--strict"],
        capture_output=True, text=True
    )
    print(verify_result.stdout)
    if verify_result.stderr:
        print(verify_result.stderr, file=sys.stderr)

    if verify_result.returncode != 0:
        print("❌ 翻译验证失败，不保存同步状态", file=sys.stderr)
        sys.exit(1)

    # Step 5: 保存同步状态（仅在验证通过后）
    save_sync_state(info["sha"], info["version"])
    print(f"\n✅ 构建完成! 同步状态已保存。")
    print(f"  上游版本: {info['version']}")
    print(f"  上游 SHA: {info['sha'][:12]}")
    print(f"  构建产物: {UPSTREAM_DIR}")


if __name__ == "__main__":
    main()
