---
name: cdp-fetch
metadata:
  version: 0.1.1
description: Fetch URL content or capture network traffic through the shared logged-in CDP agent browser at localhost:9222. The device-local browser may be Chrome, Arc, or another Chromium browser. Use for login-walled content, XHR/fetch capture, API endpoints, auth headers, tokens, and JSON response bodies when public fetch is insufficient or reqable is overkill.
---

# CDP Fetch

**何时用**：
- WebFetch / Nitter / 公开抓取**失败**（402 付费墙、403、需登录态）
- 需要复用共享 CDP agent profile 的已有登录态（X / Twitter / Lark / GitHub privates / 内部站）

**何时不用**：
- 公开网页 → 优先 WebFetch（更快）
- 不需要登录态的交互或截图 → 优先 `agent-browser` 的干净环境

## 前置

- 设备本地的共享 CDP agent browser 暴露在 `localhost:9222`。约定：任选一个 Chromium 系浏览器（Chrome / Arc / Brave 等）以 remote debugging 方式常驻，并由用户完成所需登录；本 skill 只连接 `localhost:9222` 端点，不关心浏览器品牌，也不负责启动它
- 测试：`curl -s http://localhost:9222/json/version | head -1` 应返回 JSON

## 用法

```bash
python3 ~/.claude/skills/cdp-fetch/scripts/fetch.py <URL> [--selector <css>] [--wait <seconds>]
```

参数：
- `URL`：要抓的页面
- `--selector`：CSS selector 提取特定元素（默认 `article`，抓 tweet / article 列表）
- `--wait`：页面加载等待秒数（默认 10）

示例：

```bash
# 抓 X 帖子（默认 selector=article）
python3 ~/.claude/skills/cdp-fetch/scripts/fetch.py 'https://x.com/someuser/status/1234567890'

# 抓 GitHub PR body
python3 ~/.claude/skills/cdp-fetch/scripts/fetch.py 'https://github.com/repo/pull/123' --selector '.markdown-body'

# 长等待页面
python3 ~/.claude/skills/cdp-fetch/scripts/fetch.py 'https://lark.com/some/page' --wait 15
```

## 网络抓包（Network domain）

抓页面发出的 XHR/fetch 请求——拿 **API endpoint / 请求体 / 响应 JSON / Authorization 等 token header**。脚本在 `Network.enable` **之后才** `Page.navigate`，所以首屏就发出的请求也不会漏。复用共享 CDP profile 的登录态，所以抓的是**带 session 的真实接口调用**。

```bash
python3 ~/.claude/skills/cdp-fetch/scripts/capture.py <URL> \
    [--wait <s>] [--filter <substr>] [--types xhr,fetch|all] \
    [--body] [--headers] [--max <n>] [--json]
```

参数：
- `--wait`：采集时长秒数（默认 15；首屏请求多的站点调到 20-25）
- `--filter`：只保留 URL 含该子串的请求（如 `--filter '/api/'`）
- `--types`：资源类型，逗号分隔（默认 `XHR,Fetch`）；`--types all` 抓全部（含 document/script/image）
- `--body`：额外用 `Network.getResponseBody` 抓响应体（大响应体已做 WS 分片重组）
- `--headers`：输出请求/响应头；文本模式只打印敏感头（`authorization`/`cookie`/`x-csrf-token`/`x-guest-token`/`x-api-key`/`x-xsrf-token`），`--json` 输出全部头
- `--json`：结构化输出，便于程序消费

示例：

```bash
# 提取某站登录态下的 API + token（抓鉴权头）
python3 ~/.claude/skills/cdp-fetch/scripts/capture.py 'https://example.com/dashboard' \
    --filter '/api/' --headers --body --json

# 抓 X 时间线接口的 JSON 响应
python3 ~/.claude/skills/cdp-fetch/scripts/capture.py 'https://x.com/home' \
    --filter 'graphql' --body --wait 20

# 看页面打了哪些接口（只列清单，不取 body）
python3 ~/.claude/skills/cdp-fetch/scripts/capture.py 'https://lark.com/some/page' --wait 18
```

**抓包 vs `fetch.py`**：要**页面渲染后的可读文本/内容** → `fetch.py`；要**底层接口调用（URL/参数/token/原始 JSON）** → `capture.py`。

**抓包 vs `reqable-capture`**：

| | cdp-fetch capture.py | reqable-capture |
|---|---|---|
| 触发方式 | 主动导航一个 URL 后采集 | 被动监听用户已有操作 |
| 适合 | 「打开 X 页面，抓它的接口」一次性取 API/token | 抓用户**手动多步交互**产生的请求链 |
| 启动成本 | 秒级（复用共享 CDP 浏览器） | 需起 Reqable 代理 |

→ 单页一次性「打开就抓」用本 skill；要跟用户手动操作流程被动抓包用 reqable。

## 关键技术细节（**为什么不能用 websocket-client**）

部分 Chromium 浏览器启动时如果**没带** `--remote-allow-origins=*`，CDP WebSocket 会拒绝带 Origin header 的连接（403 Forbidden）。

```
Rejected an incoming WebSocket connection from the http://localhost:9222 origin. 
Use the command line flag --remote-allow-origins=* to allow all origins.
```

共享 CDP 浏览器不保证带有这个 flag。

**解决方案**：用 raw socket 手写 WebSocket handshake，**不发 Origin header**。`websocket-client` 库强制带 Origin，所以必须 raw socket。

脚本里实现了这个 trick——直接抄。

## 与其他工具的对比

| 工具 | 公开页 | 登录态 | 反爬 | 速度 |
|---|---|---|---|---|
| WebFetch | ✅ | ❌ | 中（402 / 403 常见）| 快 |
| `agent-browser` | ✅ | ✅（connect 9222）| 强 | 中 |
| **本 skill (cdp-fetch)** | ✅ | **✅（共享 CDP profile）**| 强 | 中 |
| reqable-capture | ✅ | ✅ | 强 | 适合抓 API |

→ **登录态抓页面**的首选是本 skill（共享 CDP 浏览器已在运行，复用 session 成本很低）。

## 行为契约

1. **绝不重启共享 CDP 浏览器**——会断掉用户当前 tab / 登录态
2. **每次创建 tab 后关闭**（脚本自动 close `/json/close/<tab_id>`）
3. **不残留 tab** 污染用户浏览器
4. **遇到登录失败**（X 让你登录）→ 提示用户在共享 CDP 浏览器重新登录，不主动操作 login

## 失败诊断

| 症状 | 原因 | 处理 |
|---|---|---|
| `curl localhost:9222` 不响应 | 设备本地的 CDP agent browser 未运行 | 按本机配置启动带 `--remote-debugging-port=9222` 的浏览器；不要猜测或调用品牌专用启动命令 |
| WebSocket 403 | Origin 检查未绕过 | 检查脚本是否真用 raw socket（非 websocket-client）|
| 抓回 `NO_ARTICLES` | 页面需要更长 load | `--wait 20` 或 selector 改成更具体的 |
| 抓回登录页 | session 失效 | 用户在共享 CDP 浏览器重新登录目标站 |
| capture 抓回 `NO_REQUESTS` | 请求晚于采集窗口 / 被 type 过滤掉 | `--wait 25`、`--types all`、或换 `--filter` |
| capture `--body` 某条空 | 响应体已被浏览器回收 / 是重定向 | 正常，换更早采集或针对该请求单独抓 |
