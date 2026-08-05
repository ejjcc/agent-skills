---
name: skill-reflect
metadata:
  version: 2.0.3
description: >-
  Skill 失败后即时改进（定位根因、影响扫描、选择最确定性修复层级、提案并执行）；
  也可主动审计任意 skill 的目录结构（检查是否符合设计模式、是否需要拆分 references 或抽取 scripts）。
  当 skill 执行失败、用户纠正 skill 行为、用户提供 workaround、临时修了 skill 脚本、
  skill 应触发但未触发时使用。也适用于：审计 skill 结构、优化 skill 目录、
  skill 结构有问题吗、这个 skill 该怎么优化、/reflect、/skill-reflect、/audit-skill。
---

# Skill Reflect — 失败改进 + 结构审计

两种工作模式，根据触发场景自动选择：

| 模式 | 触发场景 | 核心产出 |
|------|---------|---------|
| **Mode A: Failure Reflect** | Skill 执行失败、用户纠正、临时 workaround | 根因分析 + 修复提案 |
| **Mode B: Structure Audit** | 用户要求审计、或 reflect 累计 3+ 次 | 结构优化方案 |

---

## Mode A: Failure Reflect

### Step 1: 定位根因

明确问题属于哪一类：

| 根因类型 | 典型表现 |
|----------|----------|
| 指令模糊 | Agent 理解偏差，做了错误操作 |
| 脚本 bug | 脚本报错或输出错误数据 |
| 参考文档过时 | 引用的 API/格式已变更 |
| 触发条件太窄 | 用户意图匹配但 skill 未激活 |
| 触发条件太宽 | 不相关场景误触发 |
| 环境/依赖问题 | 缺少工具、权限、token 等 |

### Step 2: 重读原文

**必须**重新读取目标 skill 的 SKILL.md 和相关文件，确认 gap 确实存在。不凭记忆判断。

### Step 3: Impact Scan

运行影响扫描脚本，获取所有引用同一概念的文件列表：

```bash
bash ~/.claude/skills/skill-reflect/scripts/impact_scan.sh "<skill-name>" "<keyword>"
```

解读输出结果，判断哪些文件需要联动修改。

### Step 4: 选择修复层级

阅读 [references/determinism-ladder.md](references/determinism-ladder.md)，根据根因类型选择最确定性的修复层。核心原则：能用脚本解决的不写指令，能用 hook 拦截的不靠 LLM 记忆。

### Step 5: 提案

向用户展示修复方案，必须包含：

- **改什么文件**：具体路径和修改内容
- **为什么能防复发**：修复如何消除根因
- **影响扫描结果**：Step 3 中发现的联动修改（如果有）
- **风险评估**：改动是否可能影响其他功能

### Step 6: 用户确认后执行

等待用户确认后再执行修改。不要自行修改 skill 文件。

---

## Mode B: Structure Audit

### Step 1: 运行结构审计

```bash
bash ~/.claude/skills/skill-reflect/scripts/audit_structure.sh <skill-dir-path>
```

脚本输出 JSON 格式的审计结果，包含检测到的范式、issues 和 suggestions。

### Step 2: 加载设计知识

根据审计结果中的 issues，按需阅读对应 reference（不要全部加载）：

- frontmatter 问题 → 读 [references/spec-constraints.md](references/spec-constraints.md)
- 结构/范式问题 → 读 [references/design-patterns.md](references/design-patterns.md)
- 反模式检出 → 读 [references/anti-patterns.md](references/anti-patterns.md)
- 修复层级选择 → 读 [references/determinism-ladder.md](references/determinism-ladder.md)

### Step 3: 生成优化方案

基于审计结果和设计知识，输出结构化优化方案：

1. **当前范式** → **目标范式**（如 pure-instruction → script-driven + reference-doc）
2. **需要提取到 scripts/ 的内容**（列出具体的内联 bash 块或确定性操作）
3. **需要拆分到 references/ 的内容**（列出 SKILL.md 中可按需加载的章节）
4. **frontmatter 修复项**（如果有）
5. **预估改动量**

### Step 4: 用户确认后执行

等待用户确认后再执行。对于大的结构变更，建议分步执行并逐步验证。

---

## 升级规则

- 同一问题连续 reflect **2 次** → 停止打补丁，建议重新审视 skill 的基本设计思路
- 不同问题累计 reflect **3+ 次** → 结构性问题，主动建议运行 Mode B（Structure Audit）
- Mode B 审计发现 skill 应该被删除/合并 → 建议 `/shit`
- 审计发现需要吸收新的领域知识 → 建议 `/eat`
- 多次 reflect 积累了可沉淀的模式 → 建议 `/ruminate`

## 成熟度信号

当 skill 同时满足以下条件时，主动建议发布（详细规范见 [references/spec-constraints.md](references/spec-constraints.md)）：

- 真实任务中成功使用 >= 3 次
- 最近 3 天（或连续 5 次成功执行）无 reflect 修复
- SKILL.md <= 300 行，frontmatter 完整且合规
- 无硬编码路径或泄露的密钥

纯内部 skill（含组织特定逻辑）或用户已拒绝过发布的，不再建议。
