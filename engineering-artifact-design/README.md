# Engineering Artifact Design

`engineering-artifact-design` 是一个用于生成工程理解型 HTML artifact 的 skill。它适合把代码、架构、调研、事故、发布、迁移、契约和审计信息整理成一份可阅读、可交互、可复用的浏览器原生文档。

这个 skill 的目标不是「做一个漂亮页面」，而是让复杂工程信息更容易被看懂、比较、讨论和决策。

## 适合什么时候用

当你需要把软件研发中的复杂材料转成一个清晰 artifact 时使用它，例如：

- Code Review、PR 审阅、模块 Review。
- 架构理解、子系统导览、代码库 Onboarding。
- 技术调研、选型评估、ADR、迁移计划。
- 技术概念解释、流程机制说明、发布计划。
- Incident / Debug 调查、性能分析、安全权限模型。
- API / Data Contract 文档、测试策略、AI 工作审计。
- 小型工程工具、编辑器或可交互分析面板。

## 基本用法

在请求里明确三件事，效果通常最好：

1. **目标读者**：Reviewer、新同学、Tech Lead、SRE、产品工程协作方等。
2. **场景类型**：Code Review、Architecture Understanding、Technical Research、Incident 等。
3. **重点信息**：风险、困惑点、复杂路径、候选方案、证据、指标、日志、文件路径、决策约束。

推荐提示词结构：

```text
请使用 engineering-artifact-design 生成一个 self-contained HTML artifact。

场景：<Code Review / Architecture / Technical Research / Incident / ...>
读者：<谁会读它>
目标：<读完后应该理解什么或决定什么>
输入材料：<diff、文件列表、日志、指标、调研笔记、接口定义等>
重点：<风险、困惑、复杂度高、待确认、需要决策的内容>
输出要求：<需要哪些模块和交互>
```

## 场景最佳实践

### Code Review & Understanding

不要把 HTML 做成完整 diff dump。Review artifact 最有价值的部分，是帮助 reviewer 快速聚焦「有风险、有困惑或复杂度高」的内容。

应该重点呈现：

- PR header：repo、PR 号、分支、作者、diff stats。
- `What this does`：用一段人话说明变更意图。
- Risk map：把高风险文件做成可点击 chip。
- 高风险文件卡片：默认展开；低风险文件放入 `<details>`。
- Anchored notes：把 reviewer note 绑定到具体 hunk、line、状态迁移或缺失测试。
- Review checklist：把「读懂」转成可执行检查项。

示例：

```text
请使用 engineering-artifact-design 为这个 PR 生成 review HTML。
不要平均展示所有 diff，重点解释有风险、有困惑或复杂度高的内容。

请特别关注：
- 权限失败后是否正确 rollback。
- optimistic state 是否可能残留。
- 新增 API 是否破坏旧客户端。
- 测试是否覆盖 failure path。

输出包含：
PR header、What this does、Risk map、高风险 file cards、annotated diff、review checklist。
```

### Architecture Understanding

架构页应该帮助读者建立 mental model，而不是穷举所有模块。

应该重点呈现：

- Main architecture map：5 到 10 个关键节点。
- Boundaries：信任边界、网络边界、存储边界、 ownership 边界。
- Hot path：用 clay 标出核心路径或风险路径。
- Key files：使用 adaptive info rows，避免长路径挤压中文说明。
- Runtime path：把请求、事件或 job 的流转做成步骤。
- Risks：耦合、单点、观测缺口、owner 不清晰的地方。

示例：

```text
请为 realtime collaboration subsystem 生成 architecture understanding HTML。
读者是刚加入项目的新工程师。

请重点解释：
- WebSocket Gateway 如何连接 Editor、Worker 和 Snapshot Store。
- 哪些边界涉及 auth / tenant isolation。
- 哪条路径是 hot path。
- 哪些 key files 应该先读，以及每个文件承担什么责任。

避免画完整大图；请把细节折叠到 key files 和 runtime path 中。
```

### Technical Research / Evaluation

调研页的重点是「证据支持的建议」，不是链接清单。

应该重点呈现：

- Research question：问题、范围、目标环境和决策截止时间。
- Executive readout：推荐方向、信心、主要 caveat、下一步。
- Landscape map：候选方案按成熟度、适配度、成本或控制力分布。
- Criteria matrix：只有真实权重时才打分，避免假精确。
- Evidence board：文档、benchmark、issue、PoC、生产案例。
- Unknowns board：未知问题、负责人、验证方式、决策影响。

示例：

```text
请使用 engineering-artifact-design 输出一个技术调研 HTML。
研究问题：我们是否应该在编辑器协作中使用 CRDT，而不是 OT 或服务端锁？

候选方案：Yjs、Automerge、OT、server lock。
评价维度：集成成本、离线编辑、性能、运维负担、安全性、迁移风险。
请把 evidence quality 和 score 分开呈现，并列出会改变建议的未知问题。
```

### Technical Concept Understanding

概念页应该让读者能「看见」概念如何工作。

适合呈现：

- 一个主视觉模型：pipeline、state chart、ring、layered stack。
- 1 到 3 个真实参数控件：slider、tabs、toggle。
- Glossary：术语解释保持短小。
- Applied example：放到具体 repo、service、file 或 request path 里。
- Failure modes：什么时候概念会失效，如何缓解。

示例：

```text
请解释 backpressure 在消息队列写入链路中的作用。
输出一个 HTML artifact，包含视觉模型、可调节入站速率的 slider、失败模式卡片、以及在 src/jobs/compactSnapshot.ts 中的应用示例。
```

### Process / Mechanism Understanding

机制页适合解释 deploy pipeline、auth handshake、webhook delivery、billing reconciliation、cache invalidation 等流程。

应该重点呈现：

- Happy path 与 Failure path 分开。
- Decision points：分支条件和 owner。
- Retries / timeouts：重试次数、退避、停止条件。
- Observability：每一步对应的 log、metric、trace。
- Runbook：操作者下一步应该做什么。

示例：

```text
请为 webhook delivery 机制生成 HTML。
读者是 on-call 工程师。

请用 tabs 区分 Happy path 和 Failure path，
并把 retry、dead letter、alert metric、operator runbook 放在对应步骤旁边。
```

### Incident / Debug Investigation

事故页应该把「时间、假设、证据」连起来。

应该重点呈现：

- Symptom band：用户影响、发现方式、当前缓解。
- Timeline：日志、发布、告警、人工操作。
- Hypothesis board：active、ruled out、confirmed。
- Evidence panels：日志片段、指标、trace、query 结果。
- Root cause：一句人话解释失败机制。
- Follow-ups：owner、due date、验证方式。

示例：

```text
请把这次 p95 latency regression 整理成 Incident / Debug HTML。
重点不是复述所有日志，而是连接 timeline、hypothesis 和 evidence。
请标出哪些假设已排除，哪些证据支持 root cause。
```

### ADR / Technical Decision

ADR 页应该帮助团队在未来理解「为什么当时这么选」。

应该重点呈现：

- Context：问题、约束、非目标。
- Option cards：每个方案的收益、成本、风险。
- Trade-off matrix：标准清楚，避免过度打分。
- Decision band：选择什么、为什么现在选、什么条件会改变决策。
- Consequences：新约束、迁移工作、监控需求。

示例：

```text
请生成一个 ADR HTML：是否把 session storage 从 Redis 迁移到 Postgres。
请对比 Redis-only、Postgres-only、dual-write 三个方案。
重点呈现决策约束、风险、迁移成本、以及什么条件会重新打开决策。
```

### Migration / Refactor Plan

迁移页应该让读者知道「怎么安全地变更」。

应该重点呈现：

- Before / After architecture。
- Phases：每阶段 entry / exit criteria。
- Compatibility layer：如何桥接新旧行为。
- Risk files：具体路径、owner、测试覆盖、回滚难度。
- Validation：自动化检查、手工 QA、shadow traffic、指标。
- Rollback：触发条件、负责人、步骤和恢复时间。

示例：

```text
请为 schema migration 生成迁移计划 HTML。
请包含 before/after、阶段计划、兼容层、风险文件、验证矩阵和 rollback path。
特别标出哪些文件需要 reviewer 重点看。
```

### API / Data Contract

契约页应该让调用方知道「能不能安全接入」。

应该重点呈现：

- Contract header：endpoint/topic/table、version、owner、consumer。
- Request / response / error tabs。
- Schema matrix：字段、类型、required、nullable、默认值、含义。
- Compatibility notes：breaking change、deprecated field、迁移时间线。
- Consumer impact：哪些调用方会受影响。

示例：

```text
请为 POST /v1/realtime/sessions 生成 API contract HTML。
包含 request、response、error tabs，schema table，兼容性说明和 consumer impact。
请标出 retryable 与 non-retryable error。
```

### Performance / Security / Test / Release

这几类 artifact 尤其适合矩阵和仪表盘，但要避免把表格压得过窄。

建议：

- Performance：hot path、latency budget、before/after、实验记录。
- Security：role/resource matrix、trust boundary、sensitive data flow、threat notes。
- Test：coverage matrix、critical path、mock/real boundary、gaps、acceptance checklist。
- Release：ramp slider、guardrail metrics、stop conditions、rollback checklist。

示例：

```text
请为 realtime.resume_v2 生成 Release / Rollout HTML。
包含 rollout timeline、percentage slider、guardrail chips、stop conditions、rollback checklist。
请明确哪些指标超过阈值时暂停发布。
```

### Onboarding / AI Work Audit

Onboarding 让人更快进入代码库；AI work audit 让 AI 产物变得可审。

应该重点呈现：

- First files to read：路径、职责、为什么先读。
- Common task paths：新增 endpoint、debug job、加 feature flag。
- Danger zones：生成文件、迁移陷阱、脆弱模块。
- AI changed what：改了什么、为什么、证据、风险。
- Human review focus：人类必须重点确认的行为。

示例：

```text
请把这次 AI 生成的改动整理成 AI Work Audit HTML。
请列出 changed files、意图、证据、风险、测试缺口和 human review focus。
重点帮助 reviewer 快速判断哪些地方需要人工深看。
```

## 组件与布局避坑

使用这个 skill 生成 HTML 时，优先遵守这些通用规则：

- **Content stacks**：panel 内混合标题、metadata、divider、callout、chips 时，用 `.content-stack` 控制垂直节奏，避免组件互相贴边。
- **Control stacks**：slider、meter、status chips、legend 放在 `.control-stack` 里，不要依赖 `.chips` 的偶然 margin。
- **Wrapped controls**：tabs、segmented controls、role filters 会换行时，外层不要用 `999px` 大胶囊；用 14px 到 16px 的 panel radius。
- **Adaptive info rows**：`path + badge + explanation` 这类行用 adaptive rows；机器文本可以换行，中文说明不能被压成竖排。
- **Diagram grammar**：复杂图先选择一种主语法，不要临时拼盒子。架构图看组件和边界，sequence 看时间消息，state machine 看状态迁移，swimlane 看 owner handoff。
- **Diagram budget**：一个图里 5 到 9 个节点最舒服，最多约 11 个；clay 焦点控制在 1 到 2 个，超过就拆成 overview + detail。
- **SVG labels**：箭头标签和边界标签要有 paper mask，避免线穿过文字；长说明放到图外的 card、callout 或 adaptive info row。
- **Tables only for matrices**：只有真正需要横向比较时才用 table；普通信息清单用 cards 或 adaptive rows。
- **Chinese typography**：中文使用 `「」`，中英文、数字、code 之间保留空格。
- **Evidence over decoration**：图、表、交互都要服务理解、比较或决策，不做纯装饰。

## 质量检查清单

交付前建议检查：

- 首屏是否在 5 秒内说明 artifact 的目的和重点。
- 是否把重点放在风险、困惑、复杂度、证据和决策上。
- 高风险内容是否比低风险内容更突出。
- Tabs、toolbar、chips 在窄宽度下是否换行正常。
- 长路径、endpoint、identifier 是否没有挤压中文说明。
- Slider、meter、legend、status chips 是否有清楚间距。
- Diagram 是否选择了正确类型，是否没有超出复杂度预算。
- SVG 中箭头是否先于节点绘制，标签是否不会被线穿过。
- 中文是否使用 `「」`，中英文之间是否有空格。
- HTML 是否 self-contained，交互是否有实际阅读价值。

## 仓库内容

- `SKILL.md`：skill 入口和核心规则。
- `references/design-style.md`：完整设计系统、组件规则和各工程场景模式。
- `references/diagram-grammar.md`：融合 `diagram-design` 的可迁移图形语法，覆盖图型选择、复杂度预算、SVG primitives 和 taste gate。
- `assets/starter.html`：自包含 HTML starter，包含常用 tokens 和基础组件。
- `agents/openai.yaml`：UI metadata。
