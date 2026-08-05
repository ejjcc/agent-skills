# Mapping Schema

`docs/feishu-mapping.json` 用于保存本地 Markdown 与飞书文档的关联。

推荐结构：

```json
{
  "description": "本地 Markdown 文件与飞书文档的映射关系",
  "mappings": [
    {
      "local_file": "docs/plans/example.md",
      "feishu_doc_id": "CvPFdSO6go...",
      "feishu_wiki_token": "TDqzwQbl...",
      "feishu_url": "https://feishu.cn/docx/CvPFdSO6go...",
      "title": "文档标题",
      "sync_cache_file": ".feishu-sync/CvPFdSO6go....json",
      "snapshot_file": ".feishu-sync/CvPFdSO6go....source.snapshot.md",
      "annotated_doc_id": "可选",
      "annotated_url": "可选",
      "revision_doc_id": "可选",
      "revision_url": "可选",
      "updated_at": "2026-04-08"
    }
  ]
}
```

关键字段：

- `local_file`: 相对工作区的 Markdown 路径
- `feishu_doc_id`: docx token
- `feishu_wiki_token`: 可选；原文档是 wiki 链接时保留
- `feishu_url`: 原文档链接
- `sync_cache_file`: 可选；section 级同步缓存路径。不填时可默认推导为 `.feishu-sync/<doc_id>.json`
- `snapshot_file`: 可选；上次成功同步的本地快照。不填时可默认推导为 `.feishu-sync/<doc_id>.source.snapshot.md`
- `annotated_doc_id`: 标注副本 doc id
- `revision_doc_id`: 修订版 doc id

约束：

- `local_file` 应保持稳定，不要混用绝对路径和相对路径
- 同一个原文档最多维护一个标注副本和一个修订版
- `sync_cache_file` 和 `snapshot_file` 应随文档长期复用，不要每次同步新建一份
