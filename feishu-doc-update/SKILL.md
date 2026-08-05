---
name: feishu-doc-update
metadata:
  version: 2.0.1
description: >-
  将本地 Markdown 变更同步到已关联的飞书文档。适用于"同步文档、sync doc、更新飞书、上传修改、同步到飞书、update doc"等场景。
  有未解决评论时生成标注副本；本地与云端在同一 block 上冲突时生成修订版；否则走 block 级直更。
  Cloud 变更检测基于 client_vars `block.version`（内部 API，通过 playwright-cli 访问）。
---

# Feishu Doc Update

将本地 Markdown 变更同步到已关联的飞书文档。决策基于两个集合：
- `L` = 本地改过的 block 集合
- `C` = 云端改过的 block 集合（通过 client_vars 的 block.version 数值比对）

## 何时用这个 skill

- 本地 Markdown 已经通过 `docs/feishu-mapping.json` 关联到飞书文档
- 需要把本地变更同步回飞书
- 需要保护云端独立变更，不被本地覆盖
- 需要保护评论上下文，避免整文档覆盖

## 前置条件

- 工作区里存在 `docs/feishu-mapping.json`
- 机器上可执行 `lark-cli`，已完成对应身份的飞书认证
- 机器上可执行 `playwright-cli`，已 `attach --extension`，用户 Chrome 登录 `bytedance.larkoffice.com`（或对应 host）
  - 详见 [references/client-vars-fetch.md](references/client-vars-fetch.md)

## 工作流

### 1. 解析映射

`python3 scripts/load_mapping.py --mapping docs/feishu-mapping.json --local-file <local_markdown_path>`

映射字段：`doc_id`、`wiki_node_token`（wiki 文档必填）、`wiki_space_id`、`host`、`annotated_doc_id`、`revision_doc_id`（如有）。详见 [references/mapping-schema.md](references/mapping-schema.md)。

找不到映射 → 停止 skill，改走首次上传流程。

### 2. 生成 section 级缓存工作副本

`python3 scripts/sync_cache.py scaffold \
  --local-file <local_markdown_path> \
  --cache-file <persisted_cache_path or default> \
  --previous-local-file <snapshot_file_if_exists> \
  --doc-id <doc_id> \
  [--wiki-token <wiki_node_token>] \
  --output <tmp_dir/sync-cache.json>`

缓存 schema v3（含 `block_versions` 和 `structure_version`）详见 [references/sync-cache.md](references/sync-cache.md)。

### 3. 拉取云端状态

两路并行：

**3a. 开放 API 导出 + 评论列表**

`bash scripts/fetch_cloud_state.sh --doc-id <doc_id> [--wiki-token <wiki_node_token>] --out-dir <tmp_dir>`

产出：
- `<tmp_dir>/cloud.md` — 云端 markdown 导出（用来做 section 映射对齐）
- `<tmp_dir>/blocks.json` — open-apis block 树（写操作需要最新 `document_revision_id`）
- `<tmp_dir>/comments.json` — 评论列表

**3b. client_vars 拉 version map**

`bash scripts/fetch_client_vars.sh \
  --doc-id <doc_id> \
  [--wiki-token <wiki_node_token>] \
  [--wiki-space-id <space_id>] \
  --output <tmp_dir/cv_snapshot.json`

产出 `cv_snapshot.json` 含 `structure_version`、`block_versions`、`block_types`、`block_sequence`。

任一失败 → 跳到 6C 修订版（不允许盲推）。

### 4. 计算两侧 diff

**4a. 云端 diff（按 block.version）**

`python3 scripts/version_diff.py \
  --current <tmp_dir/cv_snapshot.json> \
  --cache   <persisted_cache_path> \
  --output  <tmp_dir/version-diff.json>`

产出 `cloud_changed` / `cloud_added` / `cloud_deleted` 三个 block_id 集合，合集 `C = changed ∪ added ∪ deleted`。首次同步（无 cache）时 `cloud_added = 当前全部 blocks`、`structure_changed = true`。

**4b. 本地 diff（按 section）**

`python3 scripts/section_diff.py \
  --local-file <local_markdown_path> \
  --cloud-file <tmp_dir/cloud.md> \
  --cache-file <tmp_dir/sync-cache.json> \
  --output     <tmp_dir/diff.json>`

按 `##` 拆 section，识别新增 / 修改 / 冲突 / 未变；忽略 `feishu://board/` 画板链接差异；结合 `previous_titles` 识别 rename。

产出本地改过的 section 列表；通过 cache 里的 `sections[].remote.block_ids` 映射到 block_id 集合 `L`。

**4c. 表格单元格 diff（只在 section 含表格时需要）**

`python3 scripts/table_diff.py \
  --diff       <tmp_dir/diff.json> \
  --blocks     <tmp_dir/blocks.json> \
  --cache-file <tmp_dir/sync-cache.json> \
  --output     <tmp_dir/table-diff.json>`

解析本地 markdown pipe 表 + 云端 `<lark-table>` 导出，按 `(row, col)` 比对，输出 `cell_block_id` + `text_block_id` + before/after。结构变更（行列数不一致 / 合并单元格）会标 `safe: false`，`block_plan` 看到就走 6C。表格分级规则见 [references/block-safe-subset.md](references/block-safe-subset.md)。

### 5. 选择策略

决策树完整版见 [references/strategy.md](references/strategy.md)。

**步骤 1**：评论里存在 `is_solved: false` → 走 **6A 标注副本**。

**步骤 2**：计算 `L ∩ C`（本地与云端共同动过的 block 集合）。

- `L ∩ C` 非空 → **6C 修订版**（真冲突，避免误覆盖）
- `L ∩ C` 为空，且 L 满足 block 级直更安全条件（section ≤ 3 / 安全 Markdown 子集 / 同父容器 / ...）→ **6B block 级直更**
- 其它（如 L 含表格 / 白板 / 大范围结构重构）→ **6C 修订版**

### 6A. 标注副本

存在未解决评论时：

`python3 scripts/render_revision.py --mode annotated \
  --diff <tmp_dir/diff.json> \
  --title "<doc_title>" --source-url "<feishu_url>" \
  --output <tmp_dir/annotated.md>`

随后创建 / 更新标注副本（复用 `annotated_doc_id`）。输出模板见 [references/reporting.md](references/reporting.md)。

### 6B. Block 级直更

从 [references/raw-api-templates.md](references/raw-api-templates.md) 取 API 模板，按 [references/strategy.md](references/strategy.md) 的「Block 级执行顺序」规则：

1. 优先复用缓存命中的 `remote.block_ids`
2. 缓存失效时，只对当前 section 做局部 remap；不要整篇重建
3. 一次只处理一个 section，处理完**重新拉** open-apis block 树和最新 `document_revision_id` 再做下一个
4. 优先使用：单块 `PATCH` / 同父容器内 `children create + batch_delete` / 精确 range delete
5. 所有 create / patch / delete 都带最新 `document_revision_id` + 唯一 `client_token`
6. 出现"不确定是否删对"的状态 → 立即停止原文档修改，回退到 6C

**表格单元格 PATCH**：若 plan 里 section 带 `table_plans`，对每个 `cells_changed` 条目直接 PATCH 其 `text_block_id` 的文字内容（和普通 paragraph PATCH 一样用 `update_paragraph` 或 `update_text`），**不要**碰 table block 或 cell_block 本身。

成功后写新快照：

`python3 scripts/sync_cache.py finalize \
  --cache-file <tmp_dir/sync-cache.json> \
  --plan <tmp_dir/block-plan.json> \
  --cv-snapshot <tmp_dir/cv_snapshot.json> \
  --local-file <local_markdown_path> \
  --snapshot-file <persisted_snapshot_path> \
  --output <persisted_cache_path>`

`finalize` 必须：
- 用**最新**的 client_vars 拉一次（6B 过程中 version 已经因 PATCH 递增）作为 `--cv-snapshot`
- 把 `block_versions` 和 `structure_version` 写入 cache
- 更新 `last_local_sha256`、`sections[].body_sha256`

### 6C. 修订版

block 级直更不安全时：

`python3 scripts/render_revision.py --mode revision \
  --diff <tmp_dir/diff.json> \
  --title "<doc_title>" --source-url "<feishu_url>" \
  --output <tmp_dir/revision.md>`

创建 / 更新修订版文档（复用 `revision_doc_id`）。

### 7. 报告结果

结果措辞模板见 [references/reporting.md](references/reporting.md)。报告须包含：

- 路径（6A/6B/6C）及原因
- `cloud_changed` / `cloud_added` / `cloud_deleted` 计数
- L ∩ C 的具体 block 列表（如走 6C，用户需要人工对比）
- 新快照的 `structure_version` 和 block 数

## 硬约束

- 有未解决评论 → **禁止**直接修改原 block（即使 L ∩ C 为空）
- `L ∩ C` 非空 → **禁止** 6B 路径，必须走 6C
- block 级更新**一次只处理一个 section**，每次处理后必须重新拉 block 树
- 不做猜测式删除；只允许删除已在 cache `sections[].remote.block_ids` 里唯一命中的目标
- 6B 失败后**立即保留原文**，切到修订版路径
- 新建副本 / 修订版时，**复用**既有 `annotated_doc_id` / `revision_doc_id`
- 禁止缺 `cv_snapshot.json` 或 `version-diff.json` 就进入决策步骤 5

## 文件布局

- 路由与总流程：`SKILL.md`
- 脚本：`scripts/`（load_mapping、sync_cache、fetch_cloud_state、fetch_client_vars、section_diff、version_diff、block_plan、render_revision）
- 策略、缓存设计、API 模板、接口参考：`references/`
