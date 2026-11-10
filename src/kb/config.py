"""知识库配置与路径解析。"""
from pathlib import Path
import os
import tomllib

DEFAULT_CATEGORIES = (
    "01-技术知识", "02-问题解决", "03-代码片段",
    "04-项目档案", "05-标准流程", "06-AI-Skills", "07-想法与学习",
)
EXCLUDED = {"00-inbox", "99-archive", "templates", ".git"}

def locate_repo(explicit: str | None = None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if not (root / "kb.toml").is_file():
            raise ValueError(f"指定路径不是知识库（缺少 kb.toml）：{root}")
        return root
    env = os.environ.get("PERSONAL_KB_HOME")
    if env:
        return locate_repo(env)
    for directory in (Path.cwd(), *Path.cwd().parents):
        if (directory / "kb.toml").is_file():
            return directory
    raise ValueError("找不到知识库。请在知识库目录执行，或使用 --repo / PERSONAL_KB_HOME。")

def load_config(root: Path) -> dict:
    with (root / "kb.toml").open("rb") as handle:
        config = tomllib.load(handle)
    if config.get("schema_version") != "1.0":
        raise ValueError("不支持的知识库配置版本（要求 schema_version = 1.0）")
    return config

def iter_docs(root: Path, config: dict):
    exclude = set(config.get("documents", {}).get("exclude", list(EXCLUDED)))
    for path in sorted(root.rglob("*.md"), key=lambda p: p.as_posix()):
        relative = path.relative_to(root)
        if len(relative.parts) < 2 or relative.parts[0] in exclude or relative.parts[0].startswith("."):
            continue
        if path.is_symlink():
            continue
        yield path
