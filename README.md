# My Claude Code Skills

Personal **self-authored** skill collection for Claude Code.

Vendor-shipped skills are intentionally not mirrored here — see [Related collections](#related-collections) for where they live.

## Categories

- [Feishu / Lark](#feishu--lark) — 在官方 lark-cli 之上的自研工作流
- [Writing & Content](#writing--content) — 写作、内容生产
- [Diagrams & Frontend](#diagrams--frontend) — 图表、HTML 产出
- [Skill & Knowledge Management](#skill--knowledge-management) — Skill 的创建、进化、知识沉淀
- [Browser & Web](#browser--web) — 浏览器自动化、网页内容
- [Productivity](#productivity) — 效率工具

---

## Feishu / Lark

在官方 [larksuite/cli](https://github.com/larksuite/cli) 及其自带 skills 之上的自研补充层。

| Skill | Description |
|-------|-------------|
| [lark-doc-expert](./lark-doc-expert/) | 飞书文档专家层：block 结构诊断、原始 OpenAPI 访问、上传后格式修复 |
| [feishu-doc-to-md](./feishu-doc-to-md/) | 将飞书文档/知识库导出为本地 Markdown（含图片本地化） |
| [feishu-doc-update](./feishu-doc-update/) | 将本地 Markdown 变更同步回飞书文档（block 级直更/冲突修订版） |
| [feishu-comment-loop](./feishu-comment-loop/) | 飞书文档评论处理闭环：分类处理、融入正文、resolve |
| [lark-animated-flowchart](./lark-animated-flowchart/) | 生成动画流程图 HTML 并通过 HTML Box 嵌入飞书文档 |
| [feishu-html-box](./feishu-html-box/) | 在飞书文档嵌入可执行 HTML 单页应用（HTML Box / 妙笔），含 window.magic 运行时 |

## Writing & Content

| Skill | Description |
|-------|-------------|
| [content-pipeline](./content-pipeline/) | 内容生产流水线：写作、Fact Check、10 维评分、标准进化 |
| [writing-pipeline](./writing-pipeline/) | 写作评分与内容流水线，支持全流程串联 |
| [tech-doc-writing](./tech-doc-writing/) | 技术文档写作规范：自顶向下结构化表达 |
| [think-deeper](./think-deeper/) | 提示词优化助手：将模糊想法转化为清晰可执行任务 |
| [grill-me](./grill-me/) | 方案压力测试：对计划/设计进行不留情面的连环拷问 |

## Diagrams & Frontend

| Skill | Description |
|-------|-------------|
| [mermaid-diagrams](./mermaid-diagrams/) | 用 Mermaid 语法创建流程图、时序图、类图、ER 图等 |
| [excalidraw-diagram](./excalidraw-diagram/) | 生成可编辑的 .excalidraw 手绘风格技术图 |
| [png-diagram](./png-diagram/) | 通过 HTML/SVG + Playwright 截图生成专业 PNG 图表 |
| [image-to-svg](./image-to-svg/) | 将架构图、流程图等图片转换为 SVG 矢量格式 |
| [engineering-artifact-design](./engineering-artifact-design/) | 温暖编辑风格的自包含 HTML artifact 设计规范 |
| [frontend-harness-slides](./frontend-harness-slides/) | 高标准 HTML slide deck 工作流：可局部编辑不互相破坏 |

## Skill & Knowledge Management

| Skill | Description |
|-------|-------------|
| [eat](./eat/) | 吸收外部知识（URL / 代码片段 / 文档），内化为 Skill 或规则 |
| [shit](./shit/) | 代谢掉过时、冗余、冲突的 Skill、Rule 和 Memory |
| [codify](./codify/) | 将上下文的核心要点、踩坑经验沉淀为结构化 Markdown 文档 |
| [ruminate](./ruminate/) | 回顾会话工作过程，提炼可沉淀的模式，改进 Skill 和规则 |
| [skill-creator](./skill-creator/) | 创建新 Skill、改进现有 Skill、运行评测和 benchmark |
| [skill-reflect](./skill-reflect/) | Skill 失败后即时改进：定位根因、选择修复层级、执行 |
| [install-skill](./install-skill/) | 从 GitHub 安装 Skill 到本地 Claude Code 配置 |

## Browser & Web

| Skill | Description |
|-------|-------------|
| [agent-browser](./agent-browser/) | 浏览器自动化 CLI：导航、填表、点击、截图、数据抓取 |
| [browser-use](./browser-use/) | 基于 CDP 的无头浏览器自动化，用于测试和数据提取 |
| [reqable-capture](./reqable-capture/) | 通过 Reqable 抓包获取 Cookie / Token，解决登录态问题 |
| [searxng-search](./searxng-search/) | 通过私有 SearXNG 实例搜索网络，支持多引擎聚合 |
| [youtube-transcript](./youtube-transcript/) | 提取 YouTube 视频字幕/逐字稿，支持带/不带时间戳 |
| [onchain-investigator](./onchain-investigator/) | 区块链地址链上数据调查分析（TRON / Ethereum 等） |
| [cdp-fetch](./cdp-fetch/) | 通过本机 9222 共享 CDP 浏览器抓取登录态页面内容与网络请求 |

## Productivity

| Skill | Description |
|-------|-------------|
| [pdf-edit](./pdf-edit/) | 用 PyMuPDF 精确编辑 PDF 文字：替换/删除文本、保留排版 |
| [smart-ocr](./smart-ocr/) | 基于 macOS Vision 框架从图片提取文字 |
| [1password](./1password/) | 配置和使用 1Password CLI：读取/注入密钥 |
| [daily-digest](./daily-digest/) | 从多个 RSS 源筛选 AI / 开发者内容，推送每日精选 |
| [init-project](./init-project/) | 长周期项目初始化：生成特性列表、进度日志、启动脚本 |
| [ip](./ip/) | 查看本机所有网络接口的 IP 地址（公网、VPN、局域网） |
| [pua](./pua/) | 反懒惰模式：强制穷举所有可能方案后才能放弃 |
| [post-test-cleanup](./post-test-cleanup/) | 测试完成后的扫尾清理，防止测试消息残留消耗 token |
| [tmux-cli](./tmux-cli/) | 与其他 tmux 窗格中的 CLI Agent / 脚本通信 |
| [interactive-shell](./interactive-shell/) | 交互式命令工作流：PTY session 或 tmux fallback 处理 OAuth/SSH/REPL |

---

## Install

```bash
# skills CLI (skills.sh) — pick skills interactively
npx skills add ejjcc/agent-skills

# or install one skill in Claude Code
/install-skill ejjcc/agent-skills@<skill-name>

# or plain copy
cp -R <skill-name> ~/.claude/skills/
```

## Related collections

Skills I use but do not mirror here, because they are maintained upstream:

- [larksuite/cli](https://github.com/larksuite/cli) — official Lark CLI, ships 27 lark-* skills (doc/base/sheets/im/calendar/...)
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic official skills (frontend-design, docx/pptx/xlsx/pdf, ...)
- [fireworks-tech-graph](https://www.npmjs.com/package/@yizhiyanhua-ai/fireworks-tech-graph) — publication-ready SVG/PNG technical diagrams
- [ejjcc/managed-skills](https://github.com/ejjcc/managed-skills) — per-project skill loading (pool + profile symlinks)

## License

MIT
