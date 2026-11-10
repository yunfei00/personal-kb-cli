"""知识库 Markdown 元数据与链接检查。"""
from pathlib import Path
import re
import yaml
from .config import iter_docs

REQUIRED = ("id", "title", "category", "tags", "status", "created", "updated",
            "platform", "source_project", "source_url", "sensitivity")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
SECRET = re.compile(r"(?i)(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)")

def check(root: Path, config: dict) -> list[str]:
    errors: list[str] = []
    ids: dict[str, str] = {}
    for path in iter_docs(root, config):
        relative = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8")
        if SECRET.search(content):
            errors.append(f"{relative}: 检测到疑似密钥")
        if not content.startswith("---\n"):
            errors.append(f"{relative}: 缺少 YAML Front Matter")
            continue
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            errors.append(f"{relative}: Front Matter 未正确闭合")
            continue
        try:
            metadata = yaml.safe_load(parts[1])
        except yaml.YAMLError as exc:
            errors.append(f"{relative}: YAML 格式错误：{exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{relative}: 元数据必须是映射")
            continue
        for field in REQUIRED:
            if field not in metadata:
                errors.append(f"{relative}: 缺少字段 {field}")
        doc_id = metadata.get("id")
        if not isinstance(doc_id, str) or not doc_id.strip():
            errors.append(f"{relative}: id 不能为空")
        elif doc_id in ids:
            errors.append(f"{relative}: 重复 ID {doc_id}（首次出现于 {ids[doc_id]}）")
        else:
            ids[doc_id] = relative
        if metadata.get("status") not in ("draft", "verified", "deprecated"):
            errors.append(f"{relative}: status 必须是 draft/verified/deprecated")
        if not isinstance(metadata.get("tags"), list):
            errors.append(f"{relative}: tags 必须是数组")
        if config.get("check", {}).get("validate_links", True):
            for target in LINK.findall(parts[2]):
                target = target.split("#", 1)[0].split("?", 1)[0].strip()
                if not target or "://" in target or target.startswith(("mailto:", "#")):
                    continue
                from urllib.parse import unquote
                resolved = (path.parent / unquote(target)).resolve()
                if not resolved.is_relative_to(root.resolve()):
                    errors.append(f"{relative}: 链接越出知识库 {target}")
                elif not resolved.exists():
                    errors.append(f"{relative}: 本地链接不存在 {target}")
    return errors
