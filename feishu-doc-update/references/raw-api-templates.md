# Raw API Templates

block 级更新优先用 `lark-cli api`，不要依赖整文档 `docs +update`。

## 获取整棵 block 树

```bash
lark-cli api GET "/open-apis/docx/v1/documents/<doc_id>/blocks" \
  --as user \
  --page-all \
  --format json
```

## 获取单个 block

```bash
lark-cli api GET "/open-apis/docx/v1/documents/<doc_id>/blocks/<block_id>" \
  --as user \
  --format json
```

## 创建 children

```bash
lark-cli api POST "/open-apis/docx/v1/documents/<doc_id>/blocks/<parent_block_id>/children" \
  --as user \
  --params '{"document_revision_id":123,"client_token":"<uuid>"}' \
  --data '{...}' \
  --format json
```

## 更新单块

```bash
lark-cli api PATCH "/open-apis/docx/v1/documents/<doc_id>/blocks/<block_id>" \
  --as user \
  --params '{"document_revision_id":123,"client_token":"<uuid>"}' \
  --data '{...}' \
  --format json
```

## 批量更新块

```bash
lark-cli api PATCH "/open-apis/docx/v1/documents/<doc_id>/blocks/batch_update" \
  --as user \
  --params '{"document_revision_id":123,"client_token":"<uuid>"}' \
  --data '{...}' \
  --format json
```

## 删除一段 children

```bash
lark-cli api DELETE "/open-apis/docx/v1/documents/<doc_id>/blocks/<parent_block_id>/children/batch_delete" \
  --as user \
  --params '{"document_revision_id":123,"client_token":"<uuid>"}' \
  --data '{"start_index":5,"end_index":7}' \
  --format json
```

规则：

- `document_revision_id` 必须来自最新 block 拉取结果
- `client_token` 每次写操作都应唯一
- 不确定字段结构时，先从最新 block 响应抄 shape，再做最小修改

## 单 block PATCH body 模板

定位到 `block_id` 后（block_id 来自 cache 的 `sections[].remote.block_ids`），构造最小修改 PATCH body：

```bash
# paragraph block（block_type=2）改为新文本
lark-cli api PATCH "/open-apis/docx/v1/documents/<doc_id>/blocks/<block_id>" \
  --as user \
  --params '{"document_revision_id":<rev_id>,"client_token":"<uuid>"}' \
  --data '{
    "update_paragraph": {
      "elements": [{"text_run": {"content": "<new_text>"}}]
    }
  }' \
  --format json

# heading block（block_type=3, heading1）
lark-cli api PATCH "/open-apis/docx/v1/documents/<doc_id>/blocks/<block_id>" \
  --as user \
  --params '{"document_revision_id":<rev_id>,"client_token":"<uuid>"}' \
  --data '{
    "update_heading1": {
      "elements": [{"text_run": {"content": "<new_text>"}}]
    }
  }' \
  --format json
```

`update_<field>` 对应 block 的字段名：`update_paragraph`、`update_heading1` … `update_heading7`、`update_bullet`、`update_ordered`、`update_code`、`update_quote`。

注意：只传 `elements`，**不要**覆盖 `style`，避免清除原有格式。

## 删除单个 block

raw DELETE API 返回 404，必须用 `lark-cli docs +update`：

```bash
lark-cli docs +update --doc <doc_id> --command block_delete --block-id <block_id> --as user
```

不要用：
```bash
# ❌ 404 Not Found
lark-cli api DELETE "/open-apis/docx/v1/documents/<doc_id>/blocks/<block_id>" --as user
```

## block_type 速查

实测确认的 block_type 映射（飞书 docx v1 API）：

| block_type | 含义 | 创建时的 data key | PATCH 时的 update key |
|---|---|---|---|
| 2 | paragraph（文本段落） | `text` | `update_text_elements` |
| 4 | heading2 | `heading2` | `update_heading2` |
| 5 | heading3 | `heading3` | `update_heading3` |
| 12 | bullet（无序列表项） | `bullet` | `update_bullet` |
| 27 | image | `image` | — |
| 31 | table | `table` | — |
| 43 | whiteboard | `board` | — |

## 已知坑

### str_replace 不解析 markdown

`lark-cli docs +update --command str_replace` 的 `--content` 做纯文本替换，不会把 markdown 语法（表格、标题、列表）解析为飞书 block。插入结构化内容必须用 block 创建 API。

适用场景：修改已有 block 内的文字内容（改几个字、修链接）。
不适用：插入新的标题、表格、列表等结构化内容。

### 创建 block 时的 text vs update 字段名不一致

创建 paragraph block 时 data key 是 `text`，但 PATCH 更新时是 `update_text_elements`：

```python
# 创建
{"block_type": 2, "text": {"elements": [...]}}

# 更新
{"update_text_elements": {"elements": [...]}}
```

### 推荐：v2 XML 一次性插入完整表格

v1 API 创建表格需要 1+N+N 次调用（创建空表 → 获取 cell ID → 逐 cell PATCH）。v2 API 支持用 DocxXML 一次性插入带内容的完整表格：

```bash
cat << 'XML' | lark-cli docs +update --api-version v2 \
  --doc <doc_id> \
  --command block_insert_after \
  --block-id <after_block_id> \
  --content - --doc-format xml --as user
<table>
  <thead>
    <tr>
      <th><p><b>问题</b></p></th>
      <th><p><b>表现</b></p></th>
      <th><p><b>影响</b></p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><b>指针忘记更新</b></p></td>
      <td><p>描述内容</p></td>
      <td><p>影响内容</p></td>
    </tr>
  </tbody>
</table>
XML
```

优势：
- 1 次 API 调用完成（vs v1 的 21+ 次）
- `<thead>` 自动设为标题行（深色背景）
- `<th>` 自动加粗
- 列宽由飞书根据内容自动分配

限制：
- 无法在 XML 中指定 `column_width`（列宽自动分配）
- 无法指定 `header_column`——XML 没有对应标签，v1 PATCH `update_table_property` 也静默忽略（API 返回 code=0 但实际不生效）。`header_column` 只能在 v1 POST children 创建表格时指定，或手动在飞书 UI 设置

如果需要精确列宽或标题列，用 v1 API 创建表格（见下方 v1 专节）。

### v1 API 创建表格（仅在需要精确列宽或标题列时使用）

#### 表格列宽必须在创建时指定

默认 `column_width` 是 `[100, 100, ...]`，所有列等宽且很窄。必须在创建时根据内容量设置合理宽度：

```python
# 创建时指定 column_width
{"block_type": 31, "table": {"property": {
    "row_size": 7, "column_size": 3,
    "column_width": [150, 400, 250]  # 按内容量分配
}}}
```

创建后无法通过 PATCH 修改 `column_width`，只能删掉重建。

### 表格必须在创建时启用标题行/列

飞书表格的标题行（深色背景 + 加粗）和标题列通过 `header_row` / `header_column` 控制，必须在创建时指定：

```python
{"block_type": 31, "table": {"property": {
    "row_size": 7, "column_size": 3,
    "column_width": [150, 400, 250],
    "header_row": True,     # 第一行为标题行（深色背景）
    "header_column": True   # 第一列为标题列（加粗）
}}}
```

不指定则默认 `false`，表格没有视觉区分的标题行。

### 表格创建后需要逐 cell 填充

`POST children` 创建 table block 时只指定 `row_size` 和 `column_size`，返回的 cells 列表是空容器。每个 cell 内部有一个子 text block，需要逐个 PATCH 填充内容。

流程：
1. `POST children` → 创建 table，拿到 cell block_id 列表
2. 对每个 cell：`GET blocks/<cell_id>/children` → 拿到内部 text block_id
3. 对每个 text block：`PATCH blocks/<text_block_id>` → 填充内容

### 标题自动编号（seq）

飞书支持标题自动编号，通过 `seq="auto" seq-level="auto"` 属性控制。用 v2 `block_replace` 设置：

```bash
lark-cli docs +update --api-version v2 --doc <doc_id> \
  --command block_replace --block-id <heading_block_id> \
  --content '<h2 seq="auto" seq-level="auto">标题文本</h2>' \
  --doc-format xml --as user
```

如果本地 markdown 用手写序号（`## 1. 背景`），上传飞书后应替换为自动编号：去掉文本中的序号前缀，加上 `seq="auto"` 属性。

### docs +create 的图片相对路径限制

`lark-cli docs +create --markdown @./file.md` 中引用的图片必须是相对于 CWD 的路径。如果图片下载失败，会在文档中留下 `token=""` 的空 image block（显示为坏图占位符），需要手动删除后用 `docs +media-insert` 重新上传。

