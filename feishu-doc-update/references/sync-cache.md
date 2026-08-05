# Sync Cache

`feishu-doc-update` 的增量同步依赖一份持久化的 sync cache，位于：

- `.feishu-sync/<doc_id>.json` — 缓存（schema v3）
- `.feishu-sync/<doc_id>.source.snapshot.md` — 上一次同步完成时的本地 markdown 快照

## 缓存承担的两件事

1. **云端变更检测**：记录上次同步完成时每个 block 的 `version`，下次同步时用新拉的 `version` 比对，找出云端改过的 block（来自 `client_vars`）
2. **本地 → 云端 block 映射**：按 `##` 切 section，每个 section 记录它对应的云端 block 范围；本地变更只需按 section diff，不用每次重建整篇文档映射

## v3 Schema

```json
{
  "schema_version": 3,
  "doc_id": "JaZadXTUmoR8S3xZbX1ljeDwgQw",
  "wiki_token": "UGN9wUBTeiiqwgkAZETcbNj5nRc",
  "wiki_space_id": "7202621824671252508",
  "source_file": "test.md",
  "last_synced_at": "2026-04-18T08:30:00Z",

  "structure_version": 2,
  "block_versions": {
    "<block_id>": 2,
    "<block_id>": 1
  },

  "last_local_sha256": "<hash of source_file at last sync>",
  "sections": [
    {
      "section_id": "sec-tldr",
      "title": "TL;DR",
      "previous_titles": [],
      "heading_path": ["TL;DR"],
      "md_range": {"start_line": 4, "end_line": 12},
      "body_sha256": "<hash of section body>",
      "remote": {
        "parent_block_id": "<doc root block_id>",
        "heading_block_id": "<heading block_id>",
        "start_block_id": "<first child block_id>",
        "end_block_id": "<last child block_id>",
        "block_ids": ["<all block_ids in this section>"],
        "matched_by": "cache"
      }
    }
  ]
}
```

### 核心字段说明

| 字段 | 作用 |
|---|---|
| `structure_version` | 来自 client_vars。下次同步时比对：相等 = 文档结构完全未动；不等 = 有增删/重排 |
| `block_versions` | `{block_id: int}`。云端变更检测的核心：`current.version > cached.version` 即云端改过 |
| `last_local_sha256` | 本地 md 文件整文 hash。相等 → 本地未动，跳过整条 local-diff 流水 |
| `sections[].body_sha256` | 每个 section 的内容 hash。用来定位具体哪个 section 本地被改 |
| `sections[].remote.block_ids` | 该 section 对应的云端 block_id 列表，反查 `block_versions` 判定该 section 是否也被云端动过 |

## 云端变更检测（核心升级）

之前靠 markdown 文本 diff 启发式，现在靠 block 级 version 数字比对：

```
prev_versions = cache.block_versions
curr_versions = fresh_client_vars.block_versions

cloud_changed = { b | curr_versions[b] > prev_versions.get(b, 0) }
cloud_added   = curr_versions.keys - prev_versions.keys
cloud_deleted = prev_versions.keys - curr_versions.keys
```

脚本：`scripts/version_diff.py` 读 cache 和新拉的 client_vars snapshot，写出 `version-diff.json`。

## 本地变更检测

1. 计算 `sha256(source_file)` → 和 `last_local_sha256` 比较
2. 相等：本地未动，`local_changed = ∅`，可跳过推送流程
3. 不等：按 section 切开，计算每个 section 的 `body_sha256`，和 cache 里的对比
4. 不一致的 section 集合就是 L（本地改过）；该 section `remote.block_ids` 即对应的云端 block 集合

## 为什么不能缓存「Markdown 行号 → block_id」

- 一行 Markdown 不一定对应一个 block（表格、代码块会展开成多个）
- 云端导出 Markdown 的版式不稳定，行号漂移
- 标题改名时 heading block 不变但标题文字已变
- 增删 block 会让行号整体错位

所以缓存 key 是 `section_id`（稳定主键）+ `remote.block_ids`（实际 id 列表），而不是行号。

## 标题改名

核心点：不要把标题文字当主键。

- `section_id` 才是 section 身份
- `previous_titles` 用于 rename 检测
- `heading_block_id` 在 `block_versions` 里若仍存在且 version 未变，就说明标题 block 没被别人改过，可以放心 patch 成新标题

重命名流程：

1. 用上次本地快照识别出「这是同一个 section 的重命名」，复用原 `section_id`
2. 用 cache 里的 `heading_block_id` 去当前 `block_versions` 里确认该 block 仍存在
3. 若其 version 未被云端变动（`block_versions[heading_block_id] == cache 中记录值`），直接 PATCH 标题文本
4. 若其 version 被动过 → C ∩ L 冲突，按 strategy 走 6A/6C

## 失效与回退

缓存命中后仍需轻量校验。以下命中任一时当前 section 的缓存视为失效：

- `heading_block_id` 不在最新 `block_versions` 里（被删除）
- `start_block_id` / `end_block_id` 不在同一父容器下
- section 内含白板、表格等不宜 block 级 patch 的结构
- section 对应的某个 block 在 `block_versions` 里找不到

失效后**不要**整篇重建；只对失败的 section 做局部 remap（重新从 open-apis block 树抓该段）。

## 首次同步

cache 不存在时：

1. `version_diff` 会把所有当前 block 标记为 `cloud_added`、`structure_changed: true`
2. 需要完整构建 `sections` 列表 + 每个 section 的 `remote.block_ids`（一次性映射）
3. 记录 `block_versions` 和 `structure_version` 为 baseline
4. 后续同步就走增量路径

首次同步的建立逻辑在 `scripts/sync_cache.py scaffold` 和 `finalize` 里。
