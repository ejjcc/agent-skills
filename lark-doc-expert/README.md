# lark-doc-expert

飞书/Lark 文档诊断与原始 API 访问 skill。

它不是 `lark-cli` 的替代品，而是给 agent 使用的一层「专家路由 + 排障手册」：当常规的文档读写封装看不到真实差异、无法定位 block、或上传后格式不符合预期时，指导 agent 什么时候降到原始 OpenAPI、怎么查结构、怎么验证结果，以及哪些坑不能踩。

## 作用

`lark-doc-expert` 主要处理 `lark-cli` 常规命令之外的灰区：

- 判断 `docs +fetch`、raw content、v2 XML、blocks API 分别适合什么场景
- 解析 wiki token 与 docx token 的差异，避免把 wiki node token 当成 docx token 调 API
- 诊断 display settings、自动标题编号、默认展开状态等 markdown/block API 看不到的渲染层问题
- 用 blocks API 做结构 diff、block 类型调查、精准定位和编辑
- 维护 docx block 类型与本地上传语法对照，包括不可创建清单和实测陷阱
- 指导上传后格式优化：标题自动编号、图片插入、结构化内容增量插入
- 提供 Obsidian callout 到飞书 `<callout>` 的转换脚本

## 为什么不能被 `larksuite/cli` 的 skill 替代

`larksuite/cli` 或 `lark-cli` 适合作为稳定的执行层：读文档、写文档、导出、调用 OpenAPI。它关心的是“这条命令怎么跑”。

这个 skill 关心的是另一层问题：“什么时候不该相信常规 fetch 结果”“为什么 UI 里有编号但 markdown 里没有”“为什么 block_replace 后旧 block id 静默失效”“为什么 media-insert 输出不能直接 pipe 给 jq”。这些是文档系统的行为边界、组合流程和失败模式，通常来自实际排障，而不是 CLI 参数说明本身。

简单说：

- `lark-cli`：执行命令
- `larksuite/cli` skill：教 agent 使用 CLI 的通用能力
- `lark-doc-expert`：教 agent 在文档复杂场景里选择正确层级、验证真实结果、避开已知坑

所以它们是互补关系，不是替代关系。正常读写优先走 `lark-cli`/上游 skill；只有遇到结构、渲染、精准编辑、上传保真、diff 失真等问题时，才升级到 `lark-doc-expert`。

## 和上游能力的关系

建议把它放在三层模型里理解：

1. **CLI 执行层**：`lark-cli` 负责实际请求和文件操作。
2. **通用 skill 层**：`larksuite/cli` 或常规 `lark-doc` skill 负责常见读写流程。
3. **专家补丁层**：`lark-doc-expert` 负责诊断分流、原始 API 访问、block 结构调查、上传后修复和踩坑记录。

当上游 skill 更新时，这个 skill 仍然有价值，因为它保存的是更细的操作经验和失败案例；当这些经验被上游吸收后，对应条目可以再从这里删减。

## Files

- `SKILL.md`: main skill instructions
- `references/block-type-map.md`: block type mapping and upload syntax notes
- `scripts/obsidian-to-lark-callout.sh`: Obsidian callout converter

## Install

Copy or symlink this directory into your Codex/Claude skills directory, for example:

```bash
ln -s "$(pwd)" ~/.claude/skills/lark-doc-expert
```

The commands in this skill assume you have `lark-cli` installed and authenticated.

## Sanitization

This repository is a sanitized export of a personal local skill. Internal project names, private deployment commands, company domains, and local-only paths were removed or generalized before publishing.
