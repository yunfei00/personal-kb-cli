"""生成确定性的 Markdown 索引。"""
from pathlib import Path
import yaml
from .config import iter_docs, DEFAULT_CATEGORIES

def generate(root: Path, config: dict) -> str:
    categories = list(DEFAULT_CATEGORIES)
    groups: dict[str, list[tuple[str, str]]] = {c: [] for c in categories}
    for path in iter_docs(root, config):
        rel = path.relative_to(root).as_posix()
        top = path.relative_to(root).parts[0]
        if top not in groups:
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if not content.startswith("---\n"):
                continue
            parts = content.split("---\n", 2)
            meta = yaml.safe_load(parts[1])
            if not isinstance(meta, dict):
                continue
            title = str(meta.get("title") or path.stem).replace("|", "\\|")
        except (OSError, yaml.YAMLError, IndexError):
            continue
        groups[top].append((title, rel))
    lines = ["# 知识索引", "", "> 由 personal-kb-cli 自动生成，请勿手动修改。", ""]
    for category in categories:
        lines.extend([f"## {category}", ""])
        entries = sorted(groups[category], key=lambda item: item[1])
        if not entries:
            lines.append("暂无正式知识文档。")
        else:
            for title, rel in entries:
                from urllib.parse import quote
                lines.append(f"- [{title}]({quote(rel, safe='/.-_')})")
        lines.append("")
    return "\n".join(lines)

def write_index(root: Path, config: dict, *, check_only: bool = False) -> bool:
    target = root / config.get("paths", {}).get("index", "INDEX.md")
    expected = generate(root, config)
    current = target.read_text(encoding="utf-8") if target.exists() else None
    if current == expected:
        return False
    if not check_only:
        from tempfile import NamedTemporaryFile
        import os
        with NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False, newline="\n") as handle:
            handle.write(expected)
            temporary = handle.name
        os.replace(temporary, target)
    return True
