# Fetching client_vars via playwright-cli

本 skill 的 cloud 变更检测依赖 `client_vars` 的 block 级 `version` 字段。该接口是**内部接口**，`lark-cli api` 调不了，必须走浏览器 session。

## 路径

1. `scripts/fetch_client_vars.sh` 封装了调用细节，所有 skill 流程只通过它访问
2. 背后用 `playwright-cli` attach 到用户 Chrome 扩展，借用已有的登录态
3. 不需要 `ccm-meta` header（实测可省）

## 前置条件（用户一次性配置）

```bash
# 安装 playwright-cli
npm install -g @playwright/cli@latest

# Chrome 装 Playwright MCP Bridge 扩展：
#   https://chromewebstore.google.com/detail/playwright-mcp-bridge/mmlmfjhmonkocbjadbfplnigmagldckm

# 从扩展图标复制 token，加到 shell rc：
export PLAYWRIGHT_MCP_EXTENSION_TOKEN=<token>

# 建立常驻会话：
playwright-cli attach --extension
```

用户必须已经在 Chrome 登录 `bytedance.larkoffice.com`（或对应 host）。skill 不负责登录，只复用已有 session。

## 脚本用法

```bash
bash scripts/fetch_client_vars.sh \
  --doc-id <obj_token> \
  [--wiki-token <wiki_node_token>] \
  [--wiki-space-id <space_id>] \
  [--host https://bytedance.larkoffice.com] \
  --output <tmp_dir>/cv_snapshot.json
```

### 入参

- `--doc-id`：docx 的 `obj_token`（从 `lark-cli wiki spaces get_node` 拿到）
- `--wiki-token`：wiki 节点 token。**wiki 文档必带**，不带会 404
- `--wiki-space-id`：wiki 所属 space id。wiki 文档建议带（有的场景不带也行，带着更稳）
- `--host`：默认 `https://bytedance.larkoffice.com`；海外租户换成 `.larksuite.com`

### 输出 shape

```json
{
  "ok": true,
  "fetched_at": "2026-04-18T08:26:00Z",
  "doc_id": "JaZadXTUmoR8S3xZbX1ljeDwgQw",
  "host": "https://bytedance.larkoffice.com",
  "structure_version": 2,
  "block_count": 486,
  "pages_fetched": 5,
  "block_versions": { "<block_id>": 1, ... },
  "block_types":    { "<block_id>": "text", ... },
  "block_sequence": ["<block_id>", ...],
  "skip_blocks":    ["<block_id>", ...],
  "meta_map":       { ... }
}
```

`block_versions` 和 `structure_version` 是后续 `version_diff.py` 消费的核心字段。

## 错误处理

| 退出码 | 含义 | 处理 |
|---|---|---|
| 2 | 参数错误 | 检查 `--doc-id` / `--output` |
| 3 | playwright 不可用或 token 未设 | 按「前置条件」重新配置并 `playwright-cli attach --extension` |
| 5 | client_vars 返回 `code != 0` | 看 stderr 错误体，常见：wiki 文档未带 `--wiki-token`、doc_id 对应不上、权限不足 |

退出码非零时调用方应**立即停止**后续 version-based 流程，回退到 6A（有评论时）或 6C（修订版）。不要盲目走 6B。

## 性能实测

- 486 blocks / 5 页 / `limit=100` ≈ 4-6 秒（大头是浏览器 IPC 来回）
- 同一份文档做 no-op diff 自身全量拉一次 ≈ 36 KB JSON 输出

## 为什么不用 open-apis

open-apis 的 `GET /documents/<id>/blocks` 返回的 block 对象里**完全没有**版本字段（实测）。只有 `document_revision_id` 是文档级乐观锁，不能做 per-block 增量检测。所以 cloud 侧变更识别只能走 client_vars。

写入侧（PATCH / POST / DELETE blocks）继续用 open-apis，见 [raw-api-templates.md](raw-api-templates.md)。

## 边界情况

### structure_version 永远为 1？

可能。`structure_version` 只在**结构变更**（加/删/重排 block）时递增。纯文字编辑不会让它动。

### skip_blocks 非空？

分页时某些复杂 block（白板、大表格）被跳过，内容不在本次响应里，但 block_id 出现在 `skip_blocks`。
**对 version 检测无影响**（`block_map[id].version` 仍返回）；对后续写入侧有影响：白板必须走 whiteboard-update 接口，不走 docx block PATCH。

### wiki 文档和 docx 裸文档的区别

| 维度 | wiki 文档 | docx 裸文档 |
|---|---|---|
| URL | `/wiki/<wiki_node_token>` | `/docx/<obj_token>` |
| `id` 参数 | 填 `obj_token`（不是 wiki_node_token） | 填 `obj_token` |
| `container_type` | `wiki2.0` | `docx` |
| `container_id` | `wiki_node_token` | `obj_token` |
| 需要 `wiki_space_id` | 是 | 否 |

所以 wiki 文档的映射必须同时记 `wiki_node_token` 和 `obj_token`。`lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}'` 返回里取 `obj_token`。
