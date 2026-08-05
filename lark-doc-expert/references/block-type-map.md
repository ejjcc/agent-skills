# Block 类型全表：raw API 读取 ↔ 本地上传方式

来源：2026-07-07 基于用户「Block Checklist For Agent」文档（覆盖 23 种 block_type）逐项提取，
并用 `docs +create` / `block_insert_after` / `media-insert` 建测试文档实测验证（含回读比对）。

## Block 级类型对照与上传语法

| block_type | 名称 | 本地上传方式（XML，经 `docs +create` 或 `--command block_insert_after --doc-format xml`） | 实测 |
|---|---|---|---|
| 1 | page | 自动生成（文档根） | — |
| 2 | text | `<p>` + 行内样式（见下表） | ✅ |
| 3-11 | heading1-9 | `<h1>`…`<h9>`，自动编号加 `seq="auto" seq-level="auto"` | ✅ |
| 12 | bullet | `<ul><li>` | ✅ |
| 13 | ordered | `<ol><li seq="auto">` | ✅ |
| 14 | code | `<pre lang="go" caption="说明"><code>…</code></pre>` | ✅（注意：raw blocks 的 `code.style` 看不到 language，验证语言要用 v2 full fetch） |
| 15 | quote（旧版单行引用） | 不要用；现 UI 的引用块是 34 | 未测 |
| 17 | todo | `<checkbox done="false">文本</checkbox>`，内可嵌 `<time>`（提醒）与 `<cite type="user">` | ✅ |
| 18 | bitable | **不可创建**（官方明确），只支持 `block_move_after` 移动已有块 | ❌ |
| 19 | callout 高亮块 | `<callout emoji="💡" background-color="light-orange" border-color="orange"><p>…</p></callout>` | ✅（`light-orange`→枚举 2；子块仅支持文本/标题/列表/待办/引用，**不支持表格**） |
| 20 | chat_card 群名片 | `<chat_card chat-id="oc_xxx"></chat_card>` | ✅ |
| 22 | divider 分割线 | `<hr/>` | ✅ |
| 23 | file 文件附件 | `docs +media-insert --doc <id> --file <path> --type file`（XML 无法空建，见陷阱 1） | ✅（产出 33 card 视图包裹的 23） |
| 24/25 | grid / grid_column 分栏 | `<grid><column width-ratio="0.5"><p>…</p></column>…</grid>` | ✅ |
| 26 | iframe（视频等嵌入） | **无创建语法**；`<a type="url-preview">` 实测降级为普通链接，不产生 26 | ❌ |
| 27 | image | 网络图 `<img href="https://…"/>`；本地图 `docs +media-insert --file x.png`；剪切板 `--from-clipboard` | ✅ |
| 30 | sheet 电子表格 | 空表 `<sheet type="blank"></sheet>`；复制已有 `<sheet sheet-id="SID" token="TOKEN">` | ✅（回读带新 token 与 sheet-id） |
| 31/32 | table / table_cell | `<table><colgroup><thead><th><tbody><td>`，单元格内容是嵌套 text block | ✅ |
| 33 | view 视图容器 | **不要手写 `<figure>`**（见陷阱 2）；由 `media-insert --type file` 自动产生（view_type=1 card） | ⚠️ |
| 34 | quote_container 引用块 | `<blockquote>内容</blockquote>` | ✅ |
| 43 | board 画板 | `<whiteboard type="mermaid">flowchart LR…</whiteboard>` 直接渲染；复杂图 `type="blank"` 占位再走 lark-whiteboard SVG 直推；`svg`/`plantuml` 同理 | ✅（mermaid 直渲染实测通过，且 CLI v2 fetch 能回读 mermaid 源文本） |
| 999 | undefined | API 无数据模型的块统称。**poll（投票）**：不可读不可写，仅 GUI；**bookmark（书签）**：`<bookmark name="标题" href="url"></bookmark>` 可创建，raw 读回 999，CLI v2 XML fetch 能还原成 `<bookmark>` | ⚠️ |

文件（23）在 GUI 有三形态，对应结构不同：inline（无包裹，file 块直挂正文）、card（33 view_type=1 包 23）、preview（33 view_type=2 包 23）。CLI 只能产出 card 形态；inline 与 preview 无 CLI 直达路径，只能 GUI 转换。

## 行内元素（存在于 text/todo 等块的 elements[] 内）

| 元素 | XML 语法 | 实测 |
|---|---|---|
| text_run 样式 | `<b><em><u><del><code>`（嵌套顺序固定：a→b→em→del→u→code→span） | ✅ |
| 文字颜色 | `<span text-color="green">`（green→text_color=4） | ✅ |
| link 超链接 | `<a href="https://…">文本</a>` | ✅ |
| equation 行内公式 | `<latex>E = mc^2</latex>` | ✅ |
| mention_user @人 | `<cite type="user" user-id="ou_xxx"></cite>` | ✅（回读附带 user-name） |
| mention_doc @文档 | `<cite type="doc" doc-id="<docx_token>"></cite>` | ✅（**标题自动跟随目标文档改名**，diff 时勿把标题变化误判为本文档编辑） |
| reminder 提醒 | `<time expire-time="毫秒" notify-time="毫秒" should-notify="false">文本</time>` | ✅ |
| button 按钮 | `<button action="OpenLink" src="…">` | ❌ 实测 degrade 1011 无变更 |

## 实测陷阱（按危险度排序）

1. **`<source name="x.txt"/>` 空占位会毁掉整个导入事务**：file 块 size=0 过不了 schema 校验，
   `+create` 返回 `ok:true` + doc_id + degrade warning（`too big file size` 字样，实为 size 非法），
   但**全部内容回滚、文档为空且随后被服务端清理**（后续对该 doc_id 操作报 `1061007 file has been delete`）。
   文件附件一律走 `media-insert --type file`，XML 里不要写裸 `<source>`。
2. **`<figure view-type>` 包 `<img>` 产出空 view 块**：view(33) 创建成功但 children 为 null，img 子块静默丢失。
   不要手写 figure；文件卡片视图由 media-insert 自动生成。
3. **`+create` 大内容可能 server timeout 假失败**：文档可能已建成。重试前先
   `drive +search --query "<标题>"` 防止重复创建。
4. **`<img href>` 在 `+create` 里可能静默丢块**（一次实测网络图未落块、无警告）；用
   `block_insert_after` 补插则成功。上传后按 `<img>` 计数核对。
5. **999 不是一种类型**：poll、bookmark 都读作 999，raw blocks 无法区分；
   区分手段是 CLI v2 XML fetch（bookmark 能还原标签，poll 仍不可见）。
6. **callout 颜色枚举实测**：`light-orange` 与 `orange` 边框都落为枚举 2；
   v2 XML 回读只显示 emoji，不回显颜色——查颜色用 raw blocks 的 `callout.background_color`。
