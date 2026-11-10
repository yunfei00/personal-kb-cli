# personal-kb-cli

独立的个人知识库 CLI，供 Codex 和 Local Coding Agent 共用。

## 安装

从 GitHub 安装当前开发版本：

```powershell
pip install git+https://github.com/yunfei00/personal-kb-cli.git
```

正式发布 PyPI 后才可使用 `pip install personal-kb-cli`；当前不保证 PyPI 已存在该包。

## 使用

```powershell
kb --version
kb --repo D:\\personal-knowledge-base doctor
kb --repo D:\\personal-knowledge-base check
kb --repo D:\\personal-knowledge-base index
kb --repo D:\\personal-knowledge-base index --check
```

也可设置 `PERSONAL_KB_HOME`，或直接在知识库目录执行命令。

## 第一阶段

- `kb doctor`：检查知识库目录及配置版本
- `kb check`：检查正式 Markdown 文档的 YAML 元数据、重复 ID、相对链接和部分典型密钥
- `kb index`：生成稳定排序的 INDEX.md；`--check` 不写入

**限制：** 安全检查只是基础规则，不是完整的机密审计；索引生成默认跳过没有有效 Front Matter 的文档。发布前仍需人工检查公开内容。

第二阶段才实现 capture.py 和 archive.py。知识库内容存储在独立仓库 `yunfei00/personal-knowledge-base`。
