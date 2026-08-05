---
name: searxng-search
description: |
  通过已配置的私有 SearXNG 实例进行网络搜索，获取实时互联网信息。WebSearch 的可选补充，
  提供实例支持的多引擎聚合、分类过滤和 JSON 输出。使用前必须配置 SEARXNG_URL；未配置时改用 WebSearch。
  当用户明确要求使用 SearXNG，或任务需要其多引擎聚合、学术/新闻/开发等分类搜索时使用。
  普通网页搜索可直接使用 WebSearch。
metadata:
  version: 2.1.1
---

# SearXNG 网络搜索

通过用户配置的 SearXNG 实例执行互联网搜索，聚合多个搜索引擎的结果。

## 核心能力

- **多引擎聚合**：聚合实例已启用的搜索引擎，结果去重排序
- **分类搜索**：通用、IT/开发、学术、视频等不同类别
- **JSON API**：结构化返回，适合程序化处理
- **显式配置**：实例地址由 `SEARXNG_URL` 提供，不内置公共或私有端点

## 搜索方式

```bash
# 必需：配置可访问的 SearXNG 实例
export SEARXNG_URL="https://search.example.com"

# 基础搜索
~/.claude/skills/searxng-search/scripts/searx "关键词"

# 指定引擎和时间范围
~/.claude/skills/searxng-search/scripts/searx "关键词" --engines bing,brave

# 学术搜索
~/.claude/skills/searxng-search/scripts/searx "transformer attention" --category science

# 限制结果数
~/.claude/skills/searxng-search/scripts/searx "关键词" --limit 5

# 获取原始 JSON
~/.claude/skills/searxng-search/scripts/searx "关键词" --json
```

## 常用分类

| 分类 | 用途 |
|------|------|
| general | 通用网页搜索（默认） |
| science | 学术论文（arxiv、PubMed、Semantic Scholar） |
| news | 新闻 |
| it | 技术资源（GitHub、Docker Hub、crates.io） |
| packages | 包管理（npm、rubygems、pub.dev、pkg.go.dev） |
| repos | 代码仓库 |

## 环境变量

`SEARXNG_URL` 为必需配置，值应为可访问的 SearXNG 实例根地址，例如 `https://search.example.com`。

未配置时脚本会明确报错并退出；此时使用内置 WebSearch。实例必须启用 JSON 输出格式，否则脚本也会以非零状态退出。
