# Whiteboard Block API Response Structure

飞书画板内部 API，返回白板的图形节点数据。**仅作结构参考**，同样需要浏览器 cookie。

## 接口

```
GET /space/api/whiteboard/block
  ?blockToken=<whiteboard_block_token>
  &reqVersion=1
  &clientVersion=11.6
```

**必需条件**：浏览器 session cookie + CSRF token，另需额外的 LSC headers：

```
x-lgw-app-id: 1161
x-lgw-os-type: 3
x-lgw-terminal-type: 2
x-lsc-bizid: 2
x-lsc-terminal: web
x-lsc-version: 1
```

`blockToken` 是白板的 block token（如 `FA2ywp0JMhKvakbkmZfl5zw3gZb`），来自 docx block 树中 type=whiteboard 的 block 的引用字段。

## 顶层结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "meta": {
      "version": 12345,
      "appliedVersion": 12344,
      "createTime": 1751234567,
      "templateType": "blank",
      "theme": 0
    },
    "nodes": [ ... ]
  }
}
```

## node 结构

每个 node 是白板上的一个图形元素（文本框、形状、连接线等）。

```json
{
  "id": "<node_id>",
  "info": {
    "borderV2": {
      "borderStyleItem": { ... }
    },
    "connectorV2": {
      "captions": [ ... ],
      "endObject": { ... },
      "startObject": { ... },
      "shape": { ... }
    },
    "theme": {
      "borderColorCode": "...",
      "borderColorCodeType": "...",
      "borderColorCodeVersion": "...",
      "borderHighPrecisionWidth": "...",
      "borderStyleCode": "...",
      "borderWidthCode": "...",
      "connectColor": "...",
      "connectStyleCode": "...",
      "connectTypeCode": "...",
      "connectWidthCode": "...",
      "fillCodeType": "...",
      "fillCodeVersion": "...",
      "fillColorCode": "...",
      "iconBorderColor": "...",
      "iconFillColor": "...",
      "textBackgroundColorCode": "..."
    },
    "zIndexCapabilityV2": {}
  }
}
```

## node 类型

| node 特征 | 说明 |
|---|---|
| `info.connectorV2` 非空 | 连接线 / 箭头节点；`startObject` 和 `endObject` 指向两端连接的形状 |
| 无 `connectorV2` | 形状节点（文本框、矩形、圆形等） |

形状节点预期还有 `textV2` 或类似字段存放文本内容（本次响应为 connector 节点，未见文本字段）。

## 与 docx block 树的关系

在 docx 文档的 block 树中，白板以特殊 block 引用：

- `type = "whiteboard"`（client_vars）/ `block_type = 22`（open API，具体值待确认）
- block data 中包含 `blockToken` 字段，对应此接口的 `blockToken` 参数

白板内容无法通过 open API 直接读取，只能通过此内部 API 获取图形节点数据。文本内容也不以 `initialAttributedTexts` 形式存储，而是嵌套在 node 的 text 字段中（结构与 docx block 不同）。

## 注意

- 白板**不走 block 级直更路径**；含白板变更的 section 必须走 6C 修订版
- 白板 block 在 docx 层面的 block_id 和白板内部 node id 是两个独立的命名空间
