---
name: pdf-edit
metadata:
  version: 0.1.0
description: 使用 PyMuPDF 精确编辑 PDF 文字内容：替换/删除文本、保留超链接和排版。当用户需要修改 PDF 中的文字、删除乱码字符、替换姓名/地址等内容时使用。
---

# PDF 精确编辑（PyMuPDF）

## 环境

- Python venv: `~/.venvs/pdf-tools`
- 执行命令前缀: `~/.venvs/pdf-tools/bin/python`
- 依赖: `pymupdf`（import 名为 `fitz`）

如果 venv 不存在，先创建：
```bash
uv venv ~/.venvs/pdf-tools && uv pip install --python ~/.venvs/pdf-tools/bin/python pymupdf
```

## 五步流程

### Step 1: Inspect — 了解 PDF 结构

```python
import fitz
doc = fitz.open(src)
page = doc[0]

# 全文提取
print(page.get_text())

# 超链接
for l in page.get_links():
    print(l)

# 精确定位目标文字的 bbox / font / size / origin
for block in page.get_text('dict')['blocks']:
    if block['type'] != 0: continue
    for line in block['lines']:
        for span in line['spans']:
            if TARGET in span['text']:
                # span['bbox'], span['font'], span['size'], span['color'], span['origin']
```

### Step 2: Backup — 备份原文件

```bash
cp "original.pdf" "original.backup.pdf"
```

### Step 3: Redact — 涂白目标区域

```python
page.add_redact_annot(fitz.Rect(span['bbox']), fill=(1, 1, 1))
page.apply_redactions(
    images=fitz.PDF_REDACT_IMAGE_NONE,      # 不删图片
    graphics=fitz.PDF_REDACT_LINE_ART_NONE,  # 不删线条/背景
)
```

**关键参数**：`images` 和 `graphics` 必须设为 NONE，否则 redact 区域内的图形元素会被一并删除。

### Step 4: Insert — 在原位置写入新文字

```python
page.insert_text(
    origin,                # span['origin']，即 baseline 坐标
    'New Text',
    fontname='helv',       # PDF 标准 14 字体之一，视觉接近 Inter/Helvetica
    fontsize=span['size'],
    color=(0, 0, 0),
)
```

**字体 fallback 策略**：
- PDF 内嵌字体（如 Inter-Regular）PyMuPDF 默认不可用
- 用 `helv`（Helvetica）替代，视觉差异极小
- 如果用户对字体要求严格，可加载本地字体文件：`fontfile="/path/to/Inter-Regular.ttf"`

### Step 5: Verify — 验证结果

```python
# 1. 检查文字内容
text = page.get_text()
assert TARGET not in text          # 旧文字已删
assert 'New Text' in text          # 新文字已写入

# 2. 检查链接是否保留
links_after = page.get_links()

# 3. 如果链接丢失，从备份记录中补回
page.insert_link({
    'kind': fitz.LINK_URI,
    'from': original_link['from'],   # Rect
    'uri': original_link['uri'],
})

# 4. 保存
doc.save(dst, garbage=4, deflate=True)
```

## 链接保留策略

`apply_redactions` 会删除 redact 区域**内**的 annotations（包括链接）。

**安全做法**：
1. Redact **前**记录所有 links: `links_before = page.get_links()`
2. Redact **后**对比: `links_after = page.get_links()`
3. 丢失的链接用 `page.insert_link()` 补回

如果 redact 区域远离链接区域，通常不会丢失，但始终检查。

## 常见场景

| 场景 | 做法 |
|------|------|
| 删除乱码字符（如句末 `?`） | search_for → redact，不需要 insert |
| 替换文字（如改姓名） | get_text('dict') 拿 bbox/origin → redact → insert |
| 批量替换 | 循环 search_for，逐个 redact，最后一次性 apply |
| 保留链接的编辑 | 必须走链接保留策略 |

## 注意事项

- `page.get_text()` 的顺序是 content stream 顺序，`insert_text` 追加到末尾，所以新文字在 `get_text()` 输出中可能出现在最后，但**视觉位置由坐标决定，不影响显示**
- MuPDF xref warning（如 `cannot find object in xref`）通常是原 PDF 的孤儿对象，无害
- 扫描件 PDF 的文字在图片层，不能直接 redact，需先 OCR
