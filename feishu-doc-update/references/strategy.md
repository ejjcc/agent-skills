# Strategy

## 决策树

```text
有未解决评论？
  ├─ 是 → 6A 标注副本
  └─ 否 → L ∩ C（本地与云端同时改过同一 block）非空？
              ├─ 是 → 6C 修订版
              └─ 否 → block 级直更是否安全？
                          ├─ 是 → 6B block 级直更
                          └─ 否 → 6C 修订版
```

- `L` = 本地改过的 block 集合（按 section 级 hash 比对 + section.remote.block_ids 映射）
- `C` = 云端改过的 block 集合（`curr.block_versions[b] > cached.block_versions[b]` 或新增/删除）

## 决策输入来源

| 输入 | 来源 | 本 skill 拿法 |
|---|---|---|
| 未解决评论 | `lark-cli drive comments get_list` | `scripts/fetch_cloud_state.sh --comments` |
| 云端 block version map | client_vars `block_map[*].version` | `scripts/fetch_client_vars.sh --output ...` |
| structure_version | client_vars `data.structure_version` | 同上 |
| 本地 section diff | 本地 md vs `.source.snapshot.md` | `scripts/section_diff.py` |
| 表格单元格变更计划 | 本地 pipe 表 vs 云端 `<lark-table>` 按 (row,col) 比对 | `scripts/table_diff.py` |
| block 级变更计划 | 本地改过的 section → block_ids 映射（含 table cell patches） | `scripts/block_plan.py --table-diff ...` |
| 云端变更集合 | version map 比对 | `scripts/version_diff.py` |

## 6A 标注副本条件

- 评论列表中存在 `is_solved: false`

硬约束：此情形下**禁止**改原 block，不管 version 差集是否为空。

## L ∩ C（真冲突）判定

一个 block 同时被本地和云端改过，无法自动合并，只能人工。路径：6C 修订版，让人工对比。

计算方式：

1. 从 section_diff 得到本地改过的 section 列表
2. 每个 section 通过 cache 里的 `remote.block_ids` 展开成 block 集合 → `L`
3. 从 version_diff 直接得到 `C = cloud_changed ∪ cloud_added ∪ cloud_deleted`
4. `L ∩ C` 非空即真冲突

## 6B block 级直更条件（必须全部满足）

1. 无未解决评论
2. `L ∩ C = ∅`（即云端没改动和本地有重叠的 block）
3. 本地改过的 section 数 ≤ 3
4. 每个目标 section 都能唯一映射到一个 docx block 范围（cache 命中或局部 remap 成功）
5. 变更内容属于安全 Markdown 子集（见 [block-safe-subset.md](block-safe-subset.md)）
6. 目标 section 的起止 block 在同一个父容器下

命中上述条件后按 [SKILL.md](../SKILL.md) 6B 小节执行 block PATCH。

## 6C 修订版条件（任一命中即走）

- L ∩ C 非空（真冲突）
- 本地改过的 section 数 > 3
- 内容含表格、图片、附件、Mermaid、whiteboard、复杂 HTML 等不安全结构
- block 级直更执行中出现不确定状态（revision_id 冲突、block 不在预期位置等）

## structure_version 快速路径

`version_diff.json` 的 `structure_changed: false` 意味着云端没有任何结构变更（增/删/重排），只可能有纯内容编辑：

1. `C` 为空 → 云端完全未动，直接走本地 → 云端单向推
2. `C` 非空 → 云端只有 in-place 文字修改，无结构错位，block 级 PATCH 风险低
3. `structure_changed: true` → 必须重新拉 open-apis block 树，验证 cache 里每个 section 的 `remote.block_ids` 仍然有效；失效的 section 走局部 remap

## 标题改名

标题变更不应导致 section 身份丢失。

1. `section_id` 才是 section 主键
2. 用 `previous_titles` + 上次本地快照识别 rename
3. 查 cache 里的 `heading_block_id` 在最新 `block_versions` 里是否仍存在
4. 若存在且 version 未变（`L ∩ C` 对该 block 为空），直接 PATCH 原 heading block 的文字
5. 若 block 已不存在 → 对该 section 做局部 remap，视作新建 heading

## Block 级执行顺序（6B 路径）

1. 处理一个 section
2. 从 open-apis 重新拉最新 block 树获取最新 `document_revision_id`
3. 按缓存命中的 `remote.block_ids` 做最小 PATCH / children create / batch_delete
4. 再处理下一个 section

**禁止**一次性对多个 section 做盲删盲改，不是性能优化而是正确性要求——每处理一个 section 后云端 `document_revision_id` 会变，继续用旧 id 写会冲突。
