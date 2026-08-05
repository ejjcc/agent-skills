# Reporting Templates

## 标注副本

```text
文档存在未解决评论，已生成标注副本：
  标注副本：{annotated_url}
  原文档：{feishu_url}

变更标注：
  - [UPDATE] {section1}
  - [NEW] {section2}
  - [CONFLICT] {section3}
```

## Block 级直更

```text
已对原飞书文档执行 block 级更新：{feishu_url}
变更：{N} 个 section 已同步
方式：{patch_count} 个 block patch，{insert_count} 次 children create，{delete_count} 次精确 range delete
缓存：{cache_hit_count} 个 section 命中缓存，{cache_remap_count} 个 section 局部重建映射
```

## 修订版

```text
变更较多或结构不安全，已生成修订版文档：
  修订版：{revision_url}
  原文档：{feishu_url}

修订内容：
  - [修改] {section1}
  - [新增] {section2}
  - [冲突] {section3}
```
