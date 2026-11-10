"""kb 命令行入口。"""
import argparse
import json
import sys
from pathlib import Path
from . import __version__
from .config import locate_repo, load_config, DEFAULT_CATEGORIES
from .check import check
from .index import write_index

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="kb", description="个人知识库检查与索引工具")
    parser.add_argument("--version", action="version", version=f"kb {__version__}")
    parser.add_argument("--repo", help="知识库根目录（也可设置 PERSONAL_KB_HOME）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="检查环境和知识库配置")
    commands.add_parser("check", help="校验知识文档")
    index_cmd = commands.add_parser("index", help="生成 INDEX.md")
    index_cmd.add_argument("--check", action="store_true", help="仅检查索引是否需要更新")
    args = parser.parse_args(argv)
    try:
        root = locate_repo(args.repo)
        config = load_config(root)
        if args.command == "doctor":
            missing = [c for c in DEFAULT_CATEGORIES if not (root / c).is_dir()]
            problems = [f"缺少分类目录：{c}" for c in missing]
            result = {"root": str(root), "schema_version": config["schema_version"], "problems": problems}
        elif args.command == "check":
            problems = check(root, config)
            result = {"root": str(root), "problems": problems, "passed": not problems}
        else:
            changed = write_index(root, config, check_only=args.check)
            problems = ["INDEX.md 需要更新"] if args.check and changed else []
            result = {"root": str(root), "changed": changed, "problems": problems}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"知识库：{root}")
            for problem in problems:
                print(f"错误：{problem}")
            if not problems:
                print("检查通过" if args.command != "index" else "索引处理完成")
        return 1 if problems else 0
    except (OSError, ValueError) as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        else:
            print(f"错误：{exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
