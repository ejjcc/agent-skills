---
name: interactive-shell
description: 跑确实需要 stdin 或持续终端交互的命令（OAuth 登录、SSH 首次确认、REPL 等）。使用 Codex unified exec 的 PTY/session 工作流：exec_command 设置 tty=true 启动，再用 write_stdin 轮询或输入。非交互命令直接使用普通 exec_command。
metadata:
  version: 0.1.0
---

# interactive-shell

仅在命令确实需要终端交互时使用，例如 OAuth 登录、SSH 首次连接确认、REPL，或必须从 stdin 输入的命令。能通过参数非交互完成的命令，直接使用普通 `exec_command`。

## 工作流

1. 用 `exec_command` 启动命令，设置 `tty=true`，并给出合适的 `yield_time_ms`。
2. 如果命令尚未退出，记录返回的 `session_id`。
3. 用 `write_stdin` 操作该会话：
   - 仅等待新输出：省略 `chars`，设置合适的 `yield_time_ms`。
   - 回答提示：通过 `chars` 写入文本；需要回车时包含 `\n`。
   - 中断命令：写入 `\u0003`（Ctrl-C）。
4. 持续使用同一个 `session_id`，直到命令返回退出码；根据退出码和最终输出判断结果。

## 交互边界

- 密码、验证码、2FA、授权确认等敏感或需要用户判断的输入，明确提示用户，并等待用户操作或提供输入；不要猜测或绕过。
- 不要把密钥、密码或 token 直接写进命令行，避免进入 shell history 或工具日志。
- 不要无期限轮询。等待外部人工操作时定期报告状态，必要时中断并说明如何继续。
- 使用 PTY 不代表获得额外权限；仍遵守当前审批、沙箱和外部操作约束。

## 示例

启动交互命令：

```text
exec_command({ cmd: "gh auth login", tty: true, yield_time_ms: 1000 })
```

命令返回 `session_id` 后，等待输出或回答提示：

```text
write_stdin({ session_id: 123, yield_time_ms: 5000 })
write_stdin({ session_id: 123, chars: "y\n", yield_time_ms: 1000 })
```

## Fallback：exec_command 运行时不可用时

部分会话（如 CCD/headless）没有加载 Codex unified exec 工具（`exec_command` / `write_stdin` 不存在，
ToolSearch 也查不到）。此时退回 tmux detached session 方案（细节见 tmux skill 的 Raw tmux fallback）：

```bash
tmux new-session -d -s job '<command>; echo CMD_EXIT:$?; sleep 60'
# 轮询 capture-pane 直到出现预期提示（不要裸 sleep 固定时长）
tmux capture-pane -t job -p | grep -q '<prompt-pattern>'
# 文本与 Enter 拆成两次发送
tmux send-keys -t job -l -- "<answer>"
tmux send-keys -t job Enter
# 轮询到 CMD_EXIT: 出现后收尾
tmux capture-pane -t job -p -S - -J | tail -15
tmux kill-session -t job
```

注意：clack 等 TUI 确认框对管道 stdin 和手写 pty.fork 都可能不接收输入，tmux 是已验证可行的路径
（2026-07-21 agentbuddy unpublish CONFIRM 实测）。敏感输入的边界规则与上文一致。
