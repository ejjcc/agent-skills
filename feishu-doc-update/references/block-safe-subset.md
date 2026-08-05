# Block-Safe Markdown Subset

只有下列内容适合走 block 级直更：

- 标题
- 普通段落
- 无序列表 / 有序列表
- 任务列表
- 引用
- 分隔线
- 代码块
- 简单粗体 / 斜体 / 行内代码 / 链接
- **表格**（仅限单元格文字改动；行/列增删、合并单元格视为不安全）

以下内容禁止走 block 级直更：

- Mermaid / Whiteboard
- 图片
- 附件
- 嵌入卡片
- HTML
- callout
- 多列布局
- 跨容器嵌套结构

## 表格分级细则

| 改动类型 | 判定 | 处理 |
|---|---|---|
| 单元格文字改动（rows × cols 不变） | ✅ 安全 | 由 `table_diff.py` 输出 cell PATCH 计划，走 6B |
| 列宽调整 | 暂不自动处理 | 走 6C（后续若需要，可加 `update_grid_column_width_ratio`） |
| 增删行 | 🔴 不安全 | 6C 修订版 |
| 增删列 | 🔴 不安全 | 6C 修订版 |
| 合并单元格（col_span/row_span > 1） | 🔴 不安全 | 6C 修订版 |
| 一个 section 里的表格数量不一致（local/cloud/remote） | 🔴 不安全 | 6C 修订版 |

表格安全性判定完全由 `scripts/table_diff.py` 输出的 `safe` 字段决定，`block_plan.py` 不做二次猜测。

如果不确定某段 Markdown 是否属于安全子集，按"不安全"处理，直接走修订版。
