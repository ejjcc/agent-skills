---
name: lark-doc-expert
description: 飞书/Lark 文档诊断与原始 API 访问。当 lark-cli docs +fetch 的 markdown 信息不够、需要看 block 结构、查文档级设置（自动标题编号 / 权限 / 默认展开）、或 diff 不出表面差异时使用。也负责上传后的格式优化（标题自动编号、图片插入、增量结构化内容插入）。覆盖 wiki→docx token 解析、三层访问模型、display settings 盲区、全量 block 类型 ↔ 本地上传方式对照（含不可创建清单与实测陷阱）。
version: 0.2.0
---

# lark-doc-expert — 飞书/Lark 文档诊断与原始 API

上游 `lark-doc` skill 负责**常规读写**，本 skill 负责**升级路径**：什么时候跳出 `docs +fetch` 封装，直接调原生 OpenAPI，以及怎么避开常见盲区。

## 什么时候走本 skill

| 症状 / 需求 | 路由 |
|---|---|
| 简单「读内容」「拉到本地」 | ❌ 回 `lark-doc-read` rule（larkparser / `drive +export`）|
| 常规 append / overwrite markdown | ❌ 上游 `lark-doc` skill 的 `docs +update` |
| **`docs +fetch` 出来的 markdown 看起来"没变化"，但用户说改了** | ✅ 本 skill——查 block API 或 display settings |
| **精确找某个 block 编辑**（替换单个 heading / callout / 列项） | ✅ 本 skill——`blocks` + `batch_update` |
| **文档结构 diff / 样式调查**（block 类型、嵌套、样式码） | ✅ 本 skill——blocks API |
| **纯文本抽取**（喂给 LLM embedding / 全文搜索） | ✅ 本 skill——`raw_content` 端点 |
| 查**文档级设置**（自动编号、权限、默认折叠） | ✅ 本 skill——`GET /documents/{id}` 或 display settings 专用端点 |

---

## 三层访问模型

`lark-cli docs +fetch` 是**中层**；上下都有更底层 / 更简化的选项：

| 目的 | 工具 | 返回 | 丢什么 |
|---|---|---|---|
| **纯文本 / embedding / 全文搜索** | `lark-cli api GET /open-apis/docx/v1/documents/{docx_token}/raw_content --as user` | 纯文字，无格式 | 一切结构：heading 层级、加粗、表格、callout、whiteboard、mermaid 统统剥光 |
| **人类阅读 / 整体同步** | `lark-cli docs +fetch --format pretty` | Lark-flavored Markdown（含 `<lark-table>` / `<callout>` / `<whiteboard>` 等自定义标签） | 文档级 display 设置、ordered list 容器、细粒度样式 |
| **XML 保真检查** | `lark-cli docs +fetch --api-version v2 --doc <doc_id> --format json --as user` | v2 XML/HTML 片段，保留部分 XML 属性（如标题 `seq="auto"`） | 仍不是 UI 渲染截图；不保证包含所有 display settings |
| **结构 diff / 精准编辑 / 样式调查** | `lark-cli api GET /open-apis/docx/v1/documents/{docx_token}/blocks --params '{"page_size":500}' --page-all --as user` | 每个 block 的 `block_type` + 结构化字段 + 父子关系 | 文档级 display 设置（仍看不到自动编号等渲染层状态） |

---

## 必踩：wiki token ≠ docx token

Wiki URL（`/wiki/<wiki_token>`）里的 token 是**wiki obj_token**，不是 docx 原生 token。直接塞进 `/documents/{id}/blocks` 会返回 `1770002 not found`。

解析方法：

```bash
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}' --as user
# 从返回的 data.node.obj_token 拿真正的 docx_token
# 同时 data.node.obj_type 会告诉你目标资源类型（docx / sheet / bitable 等）
```

Docx URL（`/docx/<docx_token>`）里的 token 已经是 docx_token，无需解析。

---

## 盲区：display settings 不在 block 也不在 markdown

**自动标题编号 / 权限 / 默认展开状态**等是**渲染层配置**，heading block 只保留文本内容，编号完全由渲染层动态生成。所以：

- `docs +fetch` 出来的 markdown 看不到编号
- blocks API 返回的 `heading2.elements[0].text_run.content` 也不包含「1.」前缀
- `docs +fetch --api-version v2 --scope outline` 通常也不显示 `seq` 属性
- **v2 full fetch** 可以看到标题 XML 属性（例如 `<h2 seq="auto" seq-level="auto">...`），可用于确认 `block_replace` 是否写入自动编号
- UI 上实际显示的编号仍属于渲染层；最终视觉效果以渲染页为准

典型翻车场景：用户在 Feishu UI 开启「自动给标题加编号」，然后说「我改了文档结构，你发现吗？」——用 `docs +fetch` 做 diff 会得出「没变」的错误结论。

查 display settings：

```bash
lark-cli api GET /open-apis/docx/v1/documents/{docx_token} --as user
# 返回的 display_setting 字段包含部分设置
# 但自动标题编号字段目前不在 display_setting 里，可能要走其他 settings API
# 或直接让用户截图 / 看网页版
```

查标题 `seq` 属性（比 outline/blocks 更可靠）：

```bash
lark-cli docs +fetch --api-version v2 --doc <doc_id> --format json --as user \
  | jq -r '.data.document.content' \
  | rg '<h[1-6][^>]*seq="auto"'
```

注意：`--scope outline` 返回的是目录片段，可能剥掉 `seq`；要用 full fetch（不要加 `--scope outline`）。

---

## 常用 block_type 对照

| 值 | 含义 | 关键字段 |
|---|---|---|
| 1 | page（文档根） | — |
| 2 | text（普通段落） | `text.elements[]` |
| 3-11 | heading1-9 | `heading1.elements[]` … |
| 12 | bullet（无序列表） | `bullet.elements[]` |
| 13 | ordered（有序列表） | `ordered.elements[]` |
| 14 | code | `code.style`（raw 里看不到 language，用 v2 fetch） |
| 17 | todo（任务） | `todo.elements[]`（可含 reminder / mention_user） |
| 18 | bitable（多维表格） | `bitable.token`；**不可创建** |
| 19 | callout（高亮块） | `callout.background_color / emoji_id` + `children[]` |
| 20 | chat_card（群名片） | `chat_card.chat_id` |
| 22 | divider（分割线） | — |
| 23 | file（文件附件） | `file.token / name`；常被 33 view 包裹 |
| 24/25 | grid / grid_column（分栏） | `grid.column_size`、`grid_column.width_ratio` |
| 26 | iframe | `iframe.component.url`；**不可创建** |
| 27 | image | `image.token / width / height` |
| 30 | sheet（内嵌电子表格） | `sheet.token` |
| 31/32 | table / table_cell | 单元格内容是嵌套 text block |
| 33 | view（文件视图容器） | `view.view_type`：1=card，2=preview |
| 34 | quote_container（引用块） | `children[]`（15 是旧版 quote，现 UI 生成 34） |
| 43 | board（画板） | `board.token` |
| 999 | undefined（API 无模型） | poll、bookmark 等都读作 999，raw 无法区分 |

每种类型**如何从本地上传创建**（XML 语法 / media-insert 路径 / 不可创建清单 / 实测陷阱），见 [`references/block-type-map.md`](references/block-type-map.md)（2026-07-07 实测验证）。遇到不认识的 block_type 直接看 JSON 里的字段名，或查 [官方文档](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/data-structure/block)。

---

## 诊断顺序（决策树）

当用户说「文档看起来不对」/「你看我改了什么」/「diff 不出差异」：

1. **先问：改的是内容还是结构？**——不要直接动手
2. **内容层**（改了文字、加了段落、换了表格行）→ `docs +fetch --format pretty` 或 larkparser 够用
3. **结构层**（改了 block 类型、嵌套、样式）→ `api GET .../blocks`
4. **渲染层**（编号、颜色、默认折叠、权限）→ `api GET /documents/{id}` 或让用户截图；**千万不要用 block/markdown 做诊断**
5. **block 太多看不过来** → 先按 `block_type` 过滤，或按 `parent_id` 定位到目标 section 再展开

---

## 批量 block 编辑（超出 `docs +update` 能力时）

`docs +update --mode replace_range` 只支持按标题/文本定位，不支持 block_id 精准定位。需要改单个 block 的样式 / callout 颜色 / 列项顺序时，直接调：

```bash
lark-cli api PATCH /open-apis/docx/v1/documents/{docx_token}/blocks/batch_update \
  --data '{"requests":[{"block_id":"xxx","update_text_elements":{...}}]}' \
  --as user
```

具体 request schema 见 [官方文档](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/batch_update)。

---

## 白板 DSL 硬约束：不套最外层 root frame

白板 DSL（`@larksuite/whiteboard-cli` JSON v2）顶层**不要**一个占满画布的 `frame` 或 `rect` 作为"容器"。

**反面示例**（错）：

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame", "id": "root", "x": 0, "y": 0, "width": 1040, "height": 720,
      "fillColor": "#FFFFFF", "children": [ /* 所有节点 */ ]
    }
  ]
}
```

root frame 会被飞书白板渲染成一个**可见矩形框**（哪怕 fill 是白色或透明），多一圈边框不美观。2026-04 PIPO OnePage collaboration 白板实测被用户手动删除。

**正确做法**：`nodes[]` 直接放业务节点，用**绝对 x/y 坐标**定位，画布原点 (0,0) 就是天然锚点。分组背景用普通 `rect`（dashed + 浅色 fill），不是 frame 容器。子 frame（真正的"盒子"节点）照常用，**只是最外层不要**。

从现有 DSL 里**移除 root frame 的方法**：把 `root.children` 提到顶层，x/y 不需要改——root 在 (0,0) 时子节点坐标本来就等于画布绝对坐标。

---

## 白板更新硬约束：永不 overwrite

> **绝对禁止在白板上用 `--overwrite`**，**永远用 append**。

理由：飞书白板一旦 overwrite，原有节点 ID 全部废弃 / 原有手动调整（箭头位置、节点大小、注释等）全部丢失，不可恢复。append 模式会保留所有历史节点，新节点追加进去。

### 白板更新正确命令

**DSL 源（append 模式）**：

```bash
# 不加 --overwrite，默认就是 append
rtk proxy npx -y @larksuite/whiteboard-cli@^0.2.0 --to openapi \
    -i ./path/to/diagram.json --format json \
  | lark-cli whiteboard +update \
    --whiteboard-token <token> \
    --source - \
    --yes --as user
```

**Mermaid 源（append 模式）**：

```bash
lark-cli whiteboard +update \
  --whiteboard-token <token> \
  --input_format mermaid \
  --source @./path/to/file.mmd \
  --yes --as user
```

### 需要「替换」画板内容时的正确做法

**不要 overwrite**。改用以下方案之一：

1. **新建白板替换**：在 doc 里 append 一个新的 `<whiteboard type="blank"></whiteboard>`，获取新 token，推新内容，然后从 doc 里手动删除老白板块
2. **用户确认后再说**：如果用户明确要求「这个白板彻底重画，覆盖旧的」，先确认再用 `--overwrite --dry-run` 看影响范围，得到用户二次授权后再真推

`--overwrite` 出现在本 skill 任何默认示例里都是 bug——仅作「用户授权后的最后手段」。

## 白板上传完整 workflow

### 步骤 1：在目标 doc 里占位，拿 token

```bash
lark-cli docs +update --doc <doc_token> \
  --mode append \
  --markdown '<whiteboard type="blank"></whiteboard>' \
  --as user
# 返回 data.board_tokens[0]
```

需要**在指定位置**（而非文末）创建时，v2 XML 同样支持（2026-07-03 实测）：

```bash
lark-cli docs +update --doc <doc_id> --command block_insert_after \
  --block-id <anchor_block_id> \
  --content '<whiteboard type="blank"></whiteboard>' --doc-format xml --as user
# token 从 blocks API 取：block_type==43 的 board.token
```

批量创建：在 markdown 里写多个 `<whiteboard type="blank"></whiteboard>`，用 `--mode overwrite --markdown @file.md`（这是 **doc** 的 overwrite，不是白板的），会按 markdown 中出现顺序返回 `board_tokens[]` 数组。

### 步骤 2：推 DSL 到 token

用上面「DSL 源（append 模式）」或「Mermaid 源（append 模式）」命令。

### 步骤 3：回填本地 mapping

把新 token 写进 `docs/feishu-mapping.json` 的 `whiteboards` 段，方便下次同步。

---

## 飞书/Lark 文档发布规范（Authoring Standards）

任何**发布/同步到飞书/Lark**的文档正文（读者是他人）都适用；本地 md 源文件不受限（frontmatter、相对路径照常用）。

### 云端正文五条硬规范

1. **不携带 meta 信息**：frontmatter、同步映射、写作状态只留本地；云端从第一段叙述开始。h1 标题行也不上传（文档标题是独立字段，正文再放 h1 会重复）。
2. **跨文档引用必须超链接**：禁止纯文本《文档标题》形式。每篇文档独立自洽，需要背景就给可点击链接。
3. **出现的路径必须可直接打开**：禁止本地 wiki/workspace 相对路径、裸 `git@` SSH 串。替换为代码托管平台的网页 URL（如 `/tree/<branch>`、`/blob/<branch>/<path>`）或对应飞书/Lark 文档链接。**豁免**：代码块内的功能性配置（如配置文件里的 git URL 是配置内容本身）、契约条目里的文件名标识。
4. **章节编号用飞书原生自动编号**（`seq="auto"`），不用手写数字——手写 + 自动会双重编号。本地 md 保留手写序号（Obsidian 可读），上传时剥掉再打 seq（见下文标题自动编号）。
5. **缩写首次出现必须注释全称**：如「SDD（Spec-Driven Development）」——括号里**只写全称**，不加中文释义、不加解释性描述；后续出现直接用缩写。非缩写的普通术语不加注释。有了首次注释就**不要**再加文末术语表——两者重复，只留注释。全称不确定的先查证（原文档/wiki/代码仓），查不到就不注，不猜。

### 叙事与配图基线（文章类文档）

- **一条顺叙故事线**：不开头甩结论；从概念/张力起笔，每章回答一个问题往前推；章节清晰带编号。
- **叙事文档与工具使用文档分开**：故事文章和快迭代的使用指南不要耦合在一篇里，互相超链接。
- **配图对齐画板质量基线**：多泳道分区框、右上角图例、节点=粗体标题+副标细节、编号小节（①②③）、信息密度高、纯水平/垂直连线。反例：几个盒子飘在空白里 + 斜线。
- **技术图表（架构/流程/分层/对比图）以飞书/Lark 原生画板嵌入，不用静态 PNG**——画板可编辑、可协作批注；PNG 仅保留为本地 md 的预览与再生成源。已验证的落地管线：
  1. 本地仍用 SVG 作图（沿用上述视觉体系）；
  2. 目标位置插占位拿 token：`docs +update --command block_insert_after --content '<whiteboard type="blank"></whiteboard>' --doc-format xml`（v2 XML 可用，不必 markdown append），再从 blocks API 的 `board.token` 取画板 token；
  3. SVG 直推：`lark-cli whiteboard +update --whiteboard-token <t> --input_format svg --source @relative.svg --as user`（新建空板首写，不加 `--overwrite`）；
  4. `whiteboard +query --output_as image` 导出预览逐张目检（布局/文字/连线/配色）；
  5. 删除旧 PNG image block。修改已有画板内容遵守本 skill「永不 overwrite」规则：新建占位重推 + 删旧板。
  照片、截图类非图表内容仍走 `media-insert`。

### 标准上传工作流（云端变体）

1. **构建云端变体**：从本地 md 剥 frontmatter、剥 h1、剥图片引用行（记录锚点）、剥手写标题序号；
2. `docs +update --command overwrite --doc-format markdown --content @<变体>`（新文档用 `docs +create --title`；`@file` 只接 cwd 相对路径）；
3. `docs +media-insert --selection-with-ellipsis <锚点文本>` 逐图插入（含行内代码的段落锚点会匹配失败，换纯文本片段）；
4. 逐 heading `block_replace` 打 `seq="auto"`；
5. **自检**（v2 full fetch + `html.unescape`）：
   - `seq="auto"` 数量 = 标题数；
   - 排除代码块后无 `git@` / wiki 相对路径 / 本地目录残留；无纯文本《》引用残留；
   - 缩写首次出现处有全称注释（只写全称不加解释，不另设术语表）；
   - 技术图表以画板呈现（block_type 43），文档内不残留图表类静态 `<img>`（照片/截图除外）；
   - 代码块内 `<` 是否被吞（见下文「坑」）；
   - str_replace 后核对目标 block 仍存在——实测遇到过整个列表项被替换吞掉，需 `block_insert_after` 补回；
   - **block_replace 会给 block 换新 id**：同一批操作里后续的 `block_insert_after` / `block_delete` 必须重新拉 blocks 拿新 id——用旧 id 的操作**返回 ok:true 但静默无效**（2026-07-02 实测：插入的段落凭空消失）；
   - **验证插入/删除要在 block 层数块**（blocks API 按类型列出目标区块），不要只做全文 grep——同名文字可能在别处（代码块、正文）误命中造成假阳性（2026-07-03 实测：相关材料 bullet 静默丢失但 grep 显示 1，命中的是 §2 代码块里的同名注释）；
   - **media-insert 非幂等且输出混合**：其 stdout 是「人类日志 + JSON」，直接 pipe 给 jq 会 parse error 误判失败，重跑就重复插图。判定成功用 `grep '"ok"'` 或看 `Block created:` 行；操作后核对 `<img>` 数量。

## 上传后格式优化（Post-Upload Polish）

本地 Markdown 通过 `lark-doc` 的 `docs +create` 上传飞书后，以下格式需要额外处理——`docs +create` 不会自动完成。

### 标题自动编号

本地 markdown 用手写序号（`## 1. 背景`），上传飞书后应替换为原生自动编号。用 v2 `block_replace`：

```bash
# 先获取所有标题的 block_id
lark-cli docs +fetch --api-version v2 --doc <doc_id> --scope outline --as user

# 逐个替换：去掉文本中的序号前缀，加上 seq 属性
lark-cli docs +update --api-version v2 --doc <doc_id> \
  --command block_replace --block-id <heading_block_id> \
  --content '<h2 seq="auto" seq-level="auto">背景</h2>' \
  --doc-format xml --as user
```

`seq="auto" seq-level="auto"` 适用于 h1-h9，飞书会根据层级自动生成 `1.` `1.1` 等序号。

验证是否写入成功时，不要只看 blocks API 或 `docs +fetch --scope outline`；它们通常看不到 `seq`。用 v2 full fetch：

```bash
lark-cli docs +fetch --api-version v2 --doc <doc_id> --format json --as user \
  | jq -r '.data.document.content' \
  | rg '<h[1-6][^>]*seq="auto"'
```

### 本地图片上传

`docs +create --markdown @./file.md` 中的相对路径图片（`images/xxx.png`）会下载失败，留下 `token=""` 的空 image block（坏图占位符）。处理流程：

1. 上传前从 markdown 中去掉图片引用（避免坏图占位符）
2. 上传后用 `docs +media-insert` 逐张插入图片到正确位置
3. 或者先 `docs +create` 再删坏图 block 再 `+media-insert`

### 增量插入结构化内容

上传后如果需要追加表格、标题、列表等结构化内容到飞书文档，**不要用 `str_replace`**（它做纯文本替换，不解析 markdown 为飞书 block）。正确做法：

**插入表格**（v2 XML，1 次调用）：

```bash
cat << 'XML' | lark-cli docs +update --api-version v2 \
  --doc <doc_id> --command block_insert_after \
  --block-id <after_block_id> --content - --doc-format xml --as user
<table>
  <thead><tr><th><p><b>列A</b></p></th><th><p><b>列B</b></p></th></tr></thead>
  <tbody><tr><td><p>数据1</p></td><td><p>数据2</p></td></tr></tbody>
</table>
XML
```

注意：v2 XML 表格的 `<thead>` 自动映射 `header_row=true`，但无法设置 `header_column` 和精确 `column_width`。需要这两者时用 v1 API（见 `feishu-doc-update` skill 的 `references/raw-api-templates.md`）。

**插入标题 / 段落 / 列表**（v2 XML）：

```bash
lark-cli docs +update --api-version v2 --doc <doc_id> \
  --command block_insert_after --block-id <after_block_id> \
  --content '<h3 seq="auto" seq-level="auto">新章节</h3><p>内容</p><ul><li>要点一</li><li>要点二</li></ul>' \
  --doc-format xml --as user
```

**删除 block**：

```bash
lark-cli docs +update --doc <doc_id> --command block_delete --block-id <block_id> --as user
```

### 上传工作流总结

```
1. docs +create（markdown 或 XML，不含图片引用）
2. docs +media-insert（逐张插入本地图片）
3. block_replace 设置标题 seq="auto"（去掉手写序号）
4. wiki +move 挂到目标知识库节点
5. 转移所有权（如需要）
```

## Obsidian callout → 飞书 callout 转换

本地 markdown 使用 Obsidian callout 语法（`> [!type] 标题`），上传飞书前需要转换为飞书 `<callout>` 标签。

### 格式对照

| Obsidian | 飞书 |
|---|---|
| `> [!warning] 标题` | `<callout emoji="⚠️" background-color="light-orange" border-color="light-orange">` |
| `> [!info] 标题` | `<callout emoji="💡" background-color="light-blue" border-color="light-blue">` |
| `> [!danger] 标题` | `<callout emoji="🔴" background-color="light-red" border-color="light-red">` |
| `> [!tip] 标题` | `<callout emoji="✅" background-color="light-green" border-color="light-green">` |
| `> [!note] 标题` | `<callout emoji="📝" background-color="light-grey" border-color="light-grey">` |

### 转换规则

1. `> [!type] 标题` → `<callout ...>\n\n**标题**\n`
2. 后续 `> 内容行` → 去掉 `> ` 前缀
3. callout 内容结束（遇到非 `>` 开头的行）→ 插入 `\n</callout>`
4. **飞书 callout 内只支持文本、列表、代码块，不支持表格**——表格必须移到 callout 外面

### 转换脚本

脚本路径：`scripts/obsidian-to-lark-callout.sh`

### 使用时机

上传本地 markdown 到飞书时，如果文件包含 `> [!` 开头的行，先走转换脚本再传：

```bash
cat docs/my-doc.md \
  | bash scripts/obsidian-to-lark-callout.sh \
  | lark-cli docs +update --doc <token> --mode overwrite --as user --markdown -
```

## 坑：markdown 导入连代码块里的 `<` 也按标签解析

`docs +create` / `docs +update --doc-format markdown` 的 XML 标签解析**不豁免 fenced code block**：代码块里的 `<<'EOF'`（heredoc）、`<tag>` 等会被当成标签吞掉，云端代码块内容缺字。2026-07-02 实挂：quickstart 里 `cat > ai-plugin.json <<'EOF'` 上传后变成 `cat > ai-plugin.json `。

处理：

1. 上传前扫描代码块内的 `<`（尤其 `<<` heredoc、泛型、比较符）；
2. 命中时上传后用 `str_replace` 补回，`--content` 里用 `&lt;` 实体：
   ```bash
   lark-cli docs +update --doc <token> --command str_replace \
     --pattern "cat > ai-plugin.json" \
     --content "cat > ai-plugin.json &lt;&lt;'EOF'" --as user
   ```
3. 验证用 v2 full fetch + `html.unescape` 后核对原文，不要只看 pretty fetch。

## 拉取到本地的操作细节

```bash
# wiki URL 先解析 obj_token：
lark-cli wiki spaces get_node --params '{"token":"<wiki_node_token>"}' --as user
# 在目标目录下导出（--output-dir 只接相对路径）：
cd <target_dir> && lark-cli drive +export \
  --token <obj_token> --doc-type docx \
  --file-extension markdown --output-dir . --overwrite --as user
```

- `--output-dir` 绝对路径报 `unsafe output path`，必须先 `cd`
- 文件名用文档标题（lark-cli 自动命名；larkparser 落盘时手动用标题命名）
- 图片密集的文档额外跑 `drive +media-download`
- 拉取后在 `docs/feishu-mapping.json` 追加映射

## 允许用户覆盖默认路由

- 「用 larkparser 保存」→ 读场景工具也可落盘
- 「要 block 结构」「pretty 格式」→ `lark-cli docs +fetch --format pretty`
- 需要保真回写同一份文档 → `feishu-doc-update` skill

## 来源

- 2026-04 同步排障案例：用户在飞书 UI 开启「自动标题编号」display 设置，我用 `docs +fetch` 和 blocks API 都看不到编号，一度以为用户删了编号，误报告。追到 display settings 才定位真相。
- 2026-04 用户明确反馈：白板更新永远 append，永远不要 overwrite——避免丢失手动调整和历史节点。
- 相关: `lark-doc` skill（常规读写封装）
