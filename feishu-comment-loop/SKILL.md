---
name: feishu-comment-loop
description: 飞书文档评论处理闭环——列未解决评论、分类处理（答疑回帖/指令改产物）、有价值回答融入正文（云端+本地双写）、resolve、commit。当用户给出飞书文档链接并要求「解决评论/处理评论/回复评论」时使用。
metadata:
  version: 1.0.0
---

# 飞书文档评论处理闭环

处理一份飞书文档上的评论，直到全部 resolve。适用前提：文档由本仓某个 md 维护（有本地对应文件）；纯云端文档跳过「本地双写」步骤。

## 流程（五步）

### 1. 列未解决评论

```bash
lark-cli drive file.comments list --file-token <DOCX_TOKEN> --file-type docx --as user --page-all
```

- token 用 **docx token**（wiki 链接先经 lark-doc 解析出 obj_token）
- 过滤 `is_solved == false`；每条取 `comment_id`、`quote`（锚点文本）、`reply_list` 里的用户原话

### 2. 分类

| 类型 | 判定 | 处理 |
|---|---|---|
| 问答类 | 「怎么理解」「什么意思」「给出依据」 | 写带证据的回帖；答案对读者普遍有价值时，同时融入正文 |
| 指令类 | 「删掉」「改成 X」「不要 Y」「给出链接」 | 直接改产物（正文/画板/代码），回帖报告做了什么 + commit/位置 |
| 自答类 | 「不是问题」「不用管」 | 按批示执行（通常是删除对应内容），回帖确认 |

### 3. 改正文（云端 + 本地双写）

- 云端优先 `str_replace`（`lark-cli docs +update --command str_replace --pattern ... --content ...`）；改列表项/整段用 `block_replace` + block id（`+fetch --detail with-ids` 取 id）
- **同步改本地 md**，保持双向一致；改完 git commit

### 4. 回帖 + resolve

```bash
# 回帖
lark-cli drive file.comment.replys create --file-token <T> --file-type docx --comment-id <ID> \
  --data '{"content":{"elements":[{"type":"text_run","text_run":{"text":"..."}}]}}' --as user
# resolve
lark-cli drive file.comments patch --file-token <T> --file-type docx --comment-id <ID> \
  --data '{"is_solved":true}' --as user
```

回帖内容：做了什么 + 证据/位置（commit hash、章节名）；措辞过度被质疑时如实改口径，不辩解。

### 5. 终验

重新 list 一次确认 unsolved 归零；本地与云端各 grep 一次改动关键词确认双写成功。

## 已验证的坑

1. **str_replace 只匹配单一样式 run**：pattern 跨越 code span / 加粗边界不会命中。拆成纯文本段内的 pattern，或改用 block_replace
2. **本地 md 与云端的模式差异**：本地是 `` `code` `` 反引号、云端是样式化文本——同一条替换两边 pattern 不同；本地替换后必须 `git diff` 确认真的命中（`str.replace` 不命中会静默无操作）
3. **块级写返回值不可信**：同一块连续两次 block_replace 第二次会静默失效、insert 偶发丢块——每次块级写后必须 +fetch 回读验证（详见 memory `lark-publish-discipline`）
4. **block id 会因替换而变**：block_replace 过的块，后续操作前重新 fetch with-ids 取新 id，不要复用旧 id
5. 指令类评论删内容后，**有序列表编号云端自动重排，本地 md 需手工重排**

## 边界

- 不代替用户 resolve 与产物无关的讨论型评论（如两人对话中）；只处理指向本 agent 维护产物的评论
- 评论要求的操作超出文档范围（改代码仓、发消息）时，按对应领域的规则执行，回帖引用结果
