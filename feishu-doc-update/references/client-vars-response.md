# Client Vars API Response Structure

飞书文档内部 API，返回 block 级 `version` 和 `structure_version`。本 skill 的 **cloud 变更检测核心依赖此 API**（open API 没有 per-block 版本）。拉取方式见 [client-vars-fetch.md](client-vars-fetch.md)。

## 接口

```
GET /space/api/docx/pages/client_vars
  ?id=<root_page_block_id>        # = doc_id (obj_token)
  &mode=7                          # 分页模式
  &limit=100
  &cursor=<base64_cursor>          # 首次为空
  &open_type=1                     # 预加载模式：不触发 open 事件，不刷新云空间最近列表
  &container_type=docx|wiki2.0
  &container_id=<doc_id_or_wiki_token>
  [&wiki_space_id=<id>]            # wiki 文档必带
```

**登录态**：走 playwright-cli 附加的 Chrome session 即可；Cookie 由浏览器自动带。`X-CSRFToken` header 从 cookie `csrf_token` 读出。`ccm-meta` header **非必需**（实测不带也能返回 200）。

## 顶层结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "<root_page_block_id>",
    "type": "CLIENT_VARS",
    "structure_version": 2,
    "block_map": { "<block_id>": { "id": "...", "version": 2, "data": {...} } },
    "block_sequence": ["<block_id>", ...],
    "skip_blocks": ["<block_id>", ...],
    "has_more": false,
    "cursor": "<base64_cursor>",
    "next_cursors": [],
    "concurrent": true,
    "editor_map": { "<user_id>": { ... } },
    "meta_map": { "<page_block_id>": { ... } },
    "mention_page_title": {},
    "synced_block_url": {},
    "preloadedImages": null,
    "external_mention_url": null
  }
}
```

## version 字段语义（已实测）

### `block_map[*].version`

- **每个 block 一个独立的版本号**，来自服务端 OT op 提交计数
- 初始值为 1，每次该 block 的内容被编辑 +1
- **OT 聚合窗口**：激活 tab 1s 内的连续编辑会合并成一个 op，version 跳跃 +1（不是每个 keystroke +1）；非激活 60s 窗口
- **多人协同**：可能一次跳 +N；客户端本地 version 落后于服务端 version 时触发 fetch miss 补齐
- **撤销**：**不会**让 version 回退。undo 在 OT 里产生新的反向 op，version 继续 +1
- 严格单调递增，**永远不会减少**

这使得 version 成为非常可靠的 per-block 变更检测指标：只要 `current.version > snapshot.version` 就说明云端改过，无需比 hash、无需比文本。

参考项目文档：
- `collab/02-架构与设计/DocX 协同问题追查手册.md` — 「op 维度，1 个 op 对应 1 个 block version」
- `collab/02-架构与设计/Docx 协同模块梳理.md` — block version + fetchMiss 模型

### `data.structure_version`

- 文档级心跳版本号
- **结构变更**（block 增 / 删 / 重排）时递增
- 不会因单纯的文字编辑而变化
- 可做 fast-path：`current.structure_version == snapshot.structure_version` 说明文档结构完全未动，只需逐 block version 比对即可判断内容变更范围

## block_map 条目结构

### 文本类 block（paragraph / heading / bullet / code 等）

```json
"<block_id>": {
  "id": "<block_id>",
  "version": 2,
  "data": {
    "type": "text",                 // 或 "heading1"~"heading7", "bullet", "ordered", "code", "quote"
    "align": "left",
    "author": "<user_id>",
    "hidden": false,
    "locked": false,
    "parent_id": "<parent_block_id>",
    "children": ["<child_block_id>", ...],
    "comments": [],
    "revisions": [],               // 实测始终为空；OT 历史不走这里
    "text": {
      "apool": { ... },            // 协作编辑的 apool 结构（OT 内部用）
      "initialAttributedTexts": {
        "text": "段落纯文本",
        "attribs": "..."           // 富文本属性编码
      }
    },
    "folded": false                // 仅 heading 有
  }
}
```

**注意**：`data.text.initialAttributedTexts.text` 有时不是字符串而是 `{"0":"..."}` 形态（与 OT attribs 编码方式有关），消费前判空/判类型。

### 表格 block

```json
"<table_block_id>": {
  "id": "<table_block_id>",
  "version": 1,
  "data": {
    "type": "table",
    "parent_id": "<parent_block_id>",
    "header_row": true,
    "rows_id": ["<row_id>", ...],
    "columns_id": ["<col_id>", ...],
    "column_set": { "<col_id>": { "width": 200 } },
    "cell_set": {
      "row<row_id>col<col_id>": { "block_id": "<cell_block_id>" }
    }
  }
}
```

表格本身无文本；单元格内容在对应 cell block（`data.type = "table_cell"`）下的子 block（text / paragraph）里。

## 与 open API block 结构的对应关系

| client_vars 字段 | open API 字段 | 说明 |
|---|---|---|
| `id` | `block_id` | 相同 |
| `data.type` (字符串) | `block_type` (数字) | 见下表 |
| `data.text.initialAttributedTexts.text` | `elements[].text_run.content` 拼接 | 文本等价 |
| `data.parent_id` | `parent_id` | 相同 |
| `data.children` | `children` | 相同 |
| `version` | *无* | **client_vars 独有**，open API 没有任何版本字段 |

## block_type 字符串 vs 整数对照

| client_vars `data.type` | open API `block_type` |
|---|---|
| `page` | 1 |
| `text` / `paragraph` | 2 |
| `heading1`~`heading7` | 3~9 |
| `bullet` | 10 |
| `ordered` | 11 |
| `code` | 12 |
| `quote` | 13 |
| `todo` | 14 |
| `table` | 31 |
| `table_cell` | 32 |
| `image` | 27 |
| `whiteboard` | (client_vars 有，open API 无独立类型) |
| `callout` | (高阶容器类型) |
| `divider` | (高阶容器类型) |

## 分页循环（mode=7）

```
while True:
    GET client_vars?...&cursor=<cur>
    blocks += data.block_map
    if not data.has_more or not data.cursor or data.cursor == cur:
        break
    cur = data.cursor
```

响应中 `skip_blocks` 列出本页因 mode/limit 限制未返回内容的 block（通常是白板、表格这类大 block）。需要单独拉它们时用 `mode=4&block_id=<id>`（子树遍历）。

## meta_map 结构

`meta_map` 里只有根 page block 一项，记录文档级元信息：

```json
"<page_block_id>": {
  "page_id": "<page_block_id>",
  "note_id": "<docx_token>",
  "title": "文档标题",
  "creator_id": "<user_id>",
  "owner_id": "<user_id>",
  "editor_id": "<user_id>",
  "tenant_id": "<tenant>",
  "create_time": "2026-04-18T07:35:42Z",
  "edit_time": "2026-04-18T07:35:45Z",
  "update_time": "2026-04-18T07:35:47.535Z",
  "status": 0,
  "source": 17,
  "sub_type": 100,
  "product_mark": 0
}
```

`edit_time` / `update_time` 只是文档级戳，不能替代 block 级 version 做增量检测。
