from pathlib import Path
from kb.cli import main
from kb.index import generate, write_index
from kb.check import check

def setup_repo(tmp_path):
    (tmp_path / "kb.toml").write_text('schema_version = "1.0"\n', encoding="utf-8")
    for name in ("01-技术知识", "02-问题解决", "03-代码片段", "04-项目档案", "05-标准流程", "06-AI-Skills", "07-想法与学习"):
        (tmp_path / name).mkdir()
    return tmp_path

def test_doctor(tmp_path):
    root = setup_repo(tmp_path)
    assert main(["--repo", str(root), "doctor"]) == 0

def test_check_missing_frontmatter(tmp_path):
    root = setup_repo(tmp_path)
    (root / "01-技术知识" / "bad.md").write_text("# bad\n", encoding="utf-8")
    assert main(["--repo", str(root), "check"]) == 1

def test_index_idempotent(tmp_path):
    root = setup_repo(tmp_path)
    assert write_index(root, {}) is True
    assert write_index(root, {}) is False
    assert main(["--repo", str(root), "index", "--check"]) == 0

def test_invalid_repo(tmp_path):
    assert main(["--repo", str(tmp_path), "doctor"]) == 2

def test_link_traversal(tmp_path):
    root = setup_repo(tmp_path)
    fields = """---
id: x1
title: 测试
category: technical
tags: []
status: draft
created: 2026-11-10
updated: 2026-11-10
platform: Windows
source_project: ""
source_url: ""
sensitivity: public
---
[bad](../../outside.md)
"""
    (root / "01-技术知识" / "test.md").write_text(fields, encoding="utf-8")
    assert any("越出知识库" in x for x in check(root, {}))
