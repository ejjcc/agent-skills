---
name: feishu-html-box
description: |-
  在飞书云文档中嵌入可执行的 HTML 单页应用（HTML Box / 妙笔 Magic Page）。标准做法是先插入 `block_type=14`、`code.style.language=24` 的 HTML 代码块，再插入 `block_type=40`、`add_ons.component_type_id="blk_6900429af84180025ce76527"` 的 widget。关键点：真正渲染依赖 widget 的 `add_ons.record`，代码块只是编辑入口，不是渲染必需；默认灌入后删掉代码块，只保留 iframe。适用于“在飞书文档里跑 HTML / 嵌交互页面 / one pager / 小工具 / 看板”等需求。与 `lark-doc` 不同，本 skill 处理会跑 JS 的沙箱页面；与白板类 skill 不同，它不是可编辑画板。运行时可用 `window.magic.*` / `window.lark.*` 做存储、AI、多维表、用户信息和分片上传；大资源应先上传到 TOS，再在 HTML 中引用 URL，避免把 record 撑爆。
metadata:
  version: 1.0.2
---

# 飞书文档里的 HTML Box（妙笔网页）

## 1. 它是什么 + 关键事实：源 HTML 实际存在 widget 自己的 record 里

文档里两个 block 协作完成嵌入：

- **HTML 代码块** —— `block_type: 14`，`code.style.language: 24`（必须是 24，HTML；`15` 是 Dart 别填错）。存的是单文件 HTML 源码。
- **HTML Box 小组件** —— `block_type: 40`，`add_ons.component_type_id: "blk_6900429af84180025ce76527"`。沙箱 iframe。

「关键事实」：插入代码块后，Feishu 会**自动把 HTML 同步进 widget 自己的 `add_ons.record`**（形如 `"{\"html\":\"<!DOCTYPE...\"}"`）。**沙箱 iframe 实际是从这个 record 读源码渲染的，不是读代码块**。所以两件事：

- **代码块的角色 = 编辑入口**。在文档 UI 里改它、Feishu 帮你同步到 widget。
- **代码块不是渲染必需**。灌完之后**可以删掉代码块、只留 widget**，iframe 照常工作。汇报 / 只读展示场景下应该这么做（默认就这么做）。

## 2. 标准流程：建 / 灌 / 删源 —— 默认不留源码在文档里

用 `lark-cli`（user 身份）。最常见的就是「建一篇文档，灌进 HTML，让用户看见交互页面、不看见源码」。**bundled 脚本默认就这么干**：

```bash
bash ~/.claude/skills/feishu-html-box/scripts/create_html_box_doc.sh \
  --html my_app.html --title "我的妙笔应用"
# 默认行为：建文档 → 插代码块 → 插 widget → 删代码块。返回 doc_url。
```

附加用法：

- 在已有文档里追加一个 widget：`--doc-token <docx_token>`（建文档步骤跳过）。
- 想保留代码块以便在文档 UI 里继续编辑源码：加 `--keep-source`。

手动 `lark-cli api` 调用（脚本不可用 / 想看实际请求时参考）：

```bash
# 1) 建文档
DOC=$(lark-cli docs +create --title "我的妙笔应用" \
  --markdown $'# 我的妙笔应用\n\n下方为可交互页面：' \
  | jq -r '.data.doc_id')

# 2) 插入 HTML 代码块（language=24, wrap=true）—— 拿到 code_block_id
HTML=$(cat my_app.html)
RESP=$(lark-cli api POST "/open-apis/docx/v1/documents/$DOC/blocks/$DOC/children" --as user \
  --data "$(jq -n --arg c "$HTML" '{
    children: [{ block_type: 14, code: { style: { language: 24, wrap: true }, elements: [{ text_run: { content: $c } }] } }],
    index: -1
  }')")
CB=$(echo "$RESP" | jq -r '.data.children[0].block_id')

# 3) 紧跟其后插入 HTML Box widget
lark-cli api POST "/open-apis/docx/v1/documents/$DOC/blocks/$DOC/children" --as user \
  --data '{
    "children": [{
      "block_type": 40,
      "add_ons": { "component_id": "", "component_type_id": "blk_6900429af84180025ce76527", "record": "{}" }
    }],
    "index": -1
  }'

# 4) 删代码块（默认动作 —— 源码已经同步进 widget 的 record，删掉只剩渲染）
IDX=$(lark-cli api GET "/open-apis/docx/v1/documents/$DOC/blocks/$DOC" --as user \
  | jq --arg id "$CB" '.data.block.children | index($id)')
lark-cli api DELETE "/open-apis/docx/v1/documents/$DOC/blocks/$DOC/children/batch_delete" --as user \
  --data "{\"start_index\":$IDX,\"end_index\":$((IDX+1))}"

echo "https://www.feishu.cn/docx/$DOC"
```

两块的插入顺序仍然是「先代码块、再 widget」—— 删代码块要在 widget 已经成功插入、`record` 同步好之后再做。

## 3. 替换已有文档里的 HTML

按代码块是否还在分两种情况。

### 3.1 文档里还有源代码块（用了 `--keep-source` 或人手改过）

PATCH 那个代码块即可，widget 的 `record` 会被自动同步：

```bash
BLOCK=$(lark-cli api GET "/open-apis/docx/v1/documents/$DOC/blocks" --as user --page-all \
  | jq -r '[.data.items[] | select(.block_type==14 and .code.style.language==24)][0].block_id')
HTML=$(cat my_app.html)
lark-cli api PATCH "/open-apis/docx/v1/documents/$DOC/blocks/$BLOCK" --as user \
  --data "$(jq -n --arg c "$HTML" '{ update_code: { style: { language: 24, wrap: true }, elements: [{ text_run: { content: $c } }] } }')"
```

### 3.2 默认情况：文档里只有 widget、源代码块已删

直接 PATCH widget 的 `add_ons.record`：

```bash
BOX=$(lark-cli api GET "/open-apis/docx/v1/documents/$DOC/blocks" --as user --page-all \
  | jq -r '[.data.items[]
      | select(.block_type==40 and .add_ons.component_type_id=="blk_6900429af84180025ce76527")
    ][0].block_id')
HTML=$(cat my_app.html)
RECORD=$(jq -cn --arg h "$HTML" '{html: $h}')   # 字符串化的 JSON
lark-cli api PATCH "/open-apis/docx/v1/documents/$DOC/blocks/$BOX" --as user \
  --data "$(jq -n --arg r "$RECORD" '{
    update_add_ons: { component_type_id: "blk_6900429af84180025ce76527", record: $r }
  }')"
```

注意 `record` 是**字符串**（值是 `"{\"html\":\"...\"}"`），不是对象。

## 4. 沙箱 iframe 里能用什么 API

运行时往 iframe 注入了 `window.magic.*` / `window.lark.*`。**别用 `localStorage`**，用下面的接口。

| 能力 | 调用 |
| --- | --- |
| 当前用户 | `await window.magic.getCurrentUserInfo()` → `{open_id,name,avatar_url,...}`；缓存在 `window.magic.currentUserInfo` / `window.magic.user`。也可 `fetch('/api/me')`，运行时会代理到父页面带登录 cookie。 |
| 按 ID 查用户 | `await window.magic.getUserInfoById(open_id)` |
| 私有存储（仅自己可见） | `await window.magic.store.set/get(key, value)`；持久化共享版：`window.magic.redis.set/get` |
| 共享存储（所有人可见） | `window.magic.store.global_set/global_get`、`window.magic.redis.global_set/global_get` |
| AI 调用 | `await window.magic.ai({ system, user, temperature, thinking, reasoning_effort })` → `{code:0,data:{result}}` |
| 文档 Markdown | `await window.magic.getDocAsMarkdown()` |
| 文档评论 | `await window.magic.doc_comments_get(doc_token)` |
| 文档元信息 | `await window.lark.getPageMeta()` |
| 多维表查询 | `await window.magic.base_records_search(app_token, table_id, view_id, filter, sort, page_token, page_size)` |
| 多维表批量取记录 | `await window.magic.base_records_get(app_token, table_id, record_ids)` |
| 多维表写入 | `await window.magic.base_record_create(app_token, table_id, fields)` |
| TOS 大文件上传（>16MB） | 走 `/api/tos/multipart/init` → `/part`（multipart/form-data，partNumber 从 1）→ `/complete`，`partNumber + etag` 必须齐 |

私有 vs 共享 + 阅读 vs 编辑权限对照：

| 作用域 | 私有数据（用户独享） | 共有数据（用户共享） | 权限要求 |
| --- | --- | --- | --- |
| 当前小组件独享 | `window.magic.store.get/set` | `window.magic.store.global_get/global_set` | 阅读权限 |
| 复制后共享 | `window.magic.redis.get/set` | `window.magic.redis.global_get/global_set` | 编辑权限 |

环境兼容：用 `window.magic` / `window.lark` 前先判断对象是否存在（本地调试要 mock）。

## 4.5 资源托管与上传 —— 别什么都塞进单文件 HTML

单文件 HTML 是硬约束（要落到 `code.style.language=24` 的代码块里），但「单文件」**不等于**「所有资源都内联」。重资源（图、视频、icon、不在公网 CDN 上的 JS / CSS、几十 KB 以上的预烤 JSON 数据）应该走 TOS，HTML 里只留 URL —— 否则代码块体积爆炸、iframe 启动慢、文档保存也慢。

**作者时（写 HTML 时）—— 先把资源上传到你可用的对象存储 / CDN（TOS、S3、R2、图床均可），拿到公网可访问的 URL**：

```bash
# 以 AWS S3 为例；换成你实际使用的存储 CLI 即可
aws s3 cp ./hero.png s3://<bucket>/magic-pages/<app-slug>/hero.png --acl public-read
# → https://<bucket>.s3.<region>.amazonaws.com/magic-pages/<app-slug>/hero.png
```

然后 HTML 里直接写：

```html
<img src="https://<your-cdn>/magic-pages/foo/hero.png" />
<script src="https://<your-cdn>/magic-pages/foo/big-lib.min.js"></script>
```

**运行时（iframe 里的 SPA 让终端用户传文件）—— 用 `window.magic` 的 TOS 分片代理**，不要也用不了 `toscli`：

```js
// init -> part(s, partNumber 从 1) -> complete
async function uploadInBox(file, partSize = 10 * 1024 * 1024) {
  const { data: { uploadId, key } } = await (await fetch('/api/tos/multipart/init', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename: file.name, contentType: file.type })
  })).json();
  const parts = [];
  let n = 1;
  for (let s = 0; s < file.size; s += partSize, n++) {
    const fd = new FormData();
    fd.append('file', file.slice(s, s + partSize));
    fd.append('uploadId', uploadId); fd.append('key', key); fd.append('partNumber', String(n));
    const { data: { etag } } = await (await fetch('/api/tos/multipart/part', { method: 'POST', body: fd })).json();
    parts.push({ partNumber: n, etag });
  }
  const { data: { url } } = await (await fetch('/api/tos/multipart/complete', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ uploadId, key, parts })
  })).json();
  return url;
}
```

> 两个路径**不能互换**：iframe 沙箱里没有 toscli、也拿不到 user-AK/SK；shell 里的 TOS 上传工具又上传不到 SPA 内部用户选的文件。**作者时用本机可用的 TOS 上传能力，运行时用 `window.magic` 的代理**。

## 5. 写 HTML 时的几条铁律

1. **单文件**：CSS / JS 内联到一份 HTML 里，外部依赖只能走 CDN（推荐 `https://cdn.tailwindcss.com`、`https://cdn.jsdelivr.net/npm/marked/marked.min.js` 等）。
2. **严禁 `localStorage`**：用 `window.magic.store` / `window.magic.redis`（见上表）。
3. **登录态请求走代理**：iframe 的 cookie 拿不到飞书登录态；`fetch('/api/me')` 由运行时代理到父页面。**前端不要保存 user access token**——需要走用户态接口的，用服务端代调用。
4. **UI 适配**：body 宽度约 800px，明确高度（HTML Box 在文档里宽度有限），别让横向滚动条出来。
5. **异步用 `async/await`**，加必要注释。
6. **代码块 language 一定填 24**：不是默认值、不是纯文本、不是 15（Dart）。

## 6. 几个实测的坑

- **language 写错（最常见）**：`code.style.language` 不显式填 24，飞书不会把代码块内容同步进 widget 的 record，iframe 拿不到 HTML、页面空白。`15` 是 Dart 不是 HTML。
- **代码块要先于 widget 插入、且要先存在过**：widget 的 `record` 是飞书在「代码块 → widget」的顺序下自动填入的。如果先 POST widget、再 POST 代码块，record 不会回填。**正确顺序：建文档 → POST 代码块（拿 code_block_id）→ POST widget → 视情况 DELETE 代码块**。
- **删代码块要在 widget 插入成功后**：record 必须在 widget 创建响应里确认已经包含 HTML；之后删代码块只是把 UI 上那个源码块拿掉，widget 的 record 不受影响。不要在 record 还是 `{}` 时删源码块。
- **想批量 / 跨文档操作时 `block_id` 拿错**：`POST .../blocks/{doc_token}/children` 这里第二个路径段是 doc_token（顶层 page），不是某个具体 block。
- **`record` 不要省**：HTML Box 创建时 `add_ons.record` 必须是字符串 `"{}"`（不是对象 `{}`），省了或写成对象会 400。
- **HTML 里写 `<` `>`**：在 JSON 里 escape 即可（`jq -n --arg` 自动处理）；在文档里再把 HTML 里 `&` 转义不要双转义，否则 iframe 里渲染不出标签。

## 7. 来源

机制和 API 表来自妙笔技能包 `magic-builder`（`/Users/geminiwen/Downloads/magic-builder`），本 skill 是把其中的 OpenAPI 调用、运行时 API、写法约定提炼成一份本地可复用的指南，并替换成 `lark-cli` 的调用方式（原 pack 的 bundled script 用 node `lark-cli` 也是同一套 API）。
