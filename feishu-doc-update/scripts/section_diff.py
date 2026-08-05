#!/usr/bin/env python3
"""
Calculate section-level diff between local Markdown and cloud Markdown.

Splits on ## headings, compares body SHA256, detects renames via previous_titles in cache.

Usage:
  python3 section_diff.py --local-file <path> --cloud-file <path> \
                           --cache-file <path> --output <path>

Output JSON:
{
  "sections": [
    {
      "section_id": "sec-intro",
      "title": "Introduction",
      "status": "modified",   // unchanged | modified | added | conflict | renamed | cloud_only
      "local_text": "...",
      "cloud_text": "...",
      "paragraphs": [
        { "before": "old text", "after": "new text", "change_type": "modified|added|deleted|unchanged" }
      ]
    }
  ],
  "has_conflict": false,
  "change_count": 1
}
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
FEISHU_BOARD_RE = re.compile(r'feishu://board/\S+')
# Whiteboard tag exported by Feishu: <whiteboard token="..." align="..." />
WHITEBOARD_TAG_RE = re.compile(r'<whiteboard\s+[^>]*/?>')
# Mermaid code block in local Markdown
MERMAID_BLOCK_RE = re.compile(r'```mermaid\s*\n.*?```', re.DOTALL)

def split_sections(text):
    parts = HEADING_RE.split(text)
    sections = []
    pre = parts[0] if parts else ""
    if pre.strip():
        sections.append({"level": 0, "title": "__preamble__", "body": pre})
    i = 1
    while i < len(parts) - 2:
        level = len(parts[i])
        title = parts[i + 1].strip()
        body  = parts[i + 2]
        sections.append({"level": level, "title": title, "body": body})
        i += 3
    return sections

LARK_TABLE_RE = re.compile(r'<lark-table[^>]*>.*?</lark-table>', re.DOTALL)
MD_TABLE_RE = re.compile(r'(?:^\|.+\|$\n?){2,}', re.MULTILINE)

def normalize_body(text):
    """Normalize body text for comparison: diagrams → placeholder, tables → placeholder, collapse whitespace.

    Formatting-only differences that are ignored:
    - Code fence language tag: ```plaintext / ```bash / etc → ```
    - Ordered list numbering: Feishu exports all items as "1." (1. 1. 1.) → normalize to sequential
    - Trailing whitespace and blank line count differences
    - Missing space around inline operators: `**A** +**B**` → `**A** + **B**`
    """
    cleaned = FEISHU_BOARD_RE.sub("<diagram-placeholder>", text)
    cleaned = WHITEBOARD_TAG_RE.sub("<diagram-placeholder>", cleaned)
    cleaned = MERMAID_BLOCK_RE.sub("<diagram-placeholder>", cleaned)
    # Feishu exports tables as <lark-table>; local uses Markdown pipe tables.
    # Both represent the same content, normalize to placeholder.
    cleaned = LARK_TABLE_RE.sub("<table-placeholder>", cleaned)
    cleaned = MD_TABLE_RE.sub("<table-placeholder>", cleaned)
    # Code fence language tag: ```plaintext / ```bash → ```
    cleaned = re.sub(r'```[a-zA-Z]+', '```', cleaned)
    # Ordered list: Feishu exports all items as "1." — normalize to sequential numbering
    def _renumber_ordered_list(m):
        items = m.group(0).split('\n')
        counter = 0
        out = []
        for item in items:
            mm = re.match(r'^(\s*)\d+\.\s', item)
            if mm:
                counter += 1
                out.append(re.sub(r'^(\s*)\d+\.', rf'\g<1>{counter}.', item, count=1))
            else:
                out.append(item)
        return '\n'.join(out)
    cleaned = re.sub(r'(?:^\s*\d+\..+\n?){2,}', _renumber_ordered_list, cleaned, flags=re.MULTILINE)
    # Inline spacing around + - → operators between bold/code spans
    cleaned = re.sub(r'(\*\*|\`)\s*\+\s*(\*\*|\`)', r'\1 + \2', cleaned)
    # List item continuation lines: merge indented continuation onto previous line
    # e.g. "- foo。\n  例：bar" → "- foo。例：bar"
    # Don't add space when preceding char is CJK or CJK punctuation
    def _merge_continuation(m):
        preceding = m.string[:m.start()]
        last_char = preceding[-1] if preceding else ''
        is_cjk = ('\u4e00' <= last_char <= '\u9fff') or last_char in '。，、；：！？「」【】""''…—'
        return '' if is_cjk else ' '
    cleaned = re.sub(r'\n {2,}', _merge_continuation, cleaned)
    # Feishu export uses single \n between paragraphs; local uses \n\n.
    cleaned = re.sub(r'\n{2,}', '\n', cleaned)
    return cleaned.strip()

def body_hash(text):
    return hashlib.sha256(normalize_body(text).encode()).hexdigest()[:16]

def make_section_id(title: str) -> str:
    return "sec-" + re.sub(r'[^\w\u4e00-\u9fff]', '-', title.lower()).strip('-')

def extract_paragraphs(body):
    chunks = re.split(r'\n{2,}', body.strip())
    return [c.strip() for c in chunks if c.strip()]

def diff_paragraphs(local_paras, cloud_paras):
    m, n = len(local_paras), len(cloud_paras)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if local_paras[i-1] == cloud_paras[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    changes = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and local_paras[i-1] == cloud_paras[j-1]:
            changes.append({"before": cloud_paras[j-1], "after": local_paras[i-1], "change_type": "unchanged"})
            i -= 1; j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            changes.append({"before": cloud_paras[j-1], "after": None, "change_type": "deleted"})
            j -= 1
        else:
            if j > 0 and dp[i-1][j] < dp[i][j-1] + 1:
                changes.append({"before": cloud_paras[j-1], "after": local_paras[i-1], "change_type": "modified"})
                i -= 1; j -= 1
            else:
                changes.append({"before": None, "after": local_paras[i-1], "change_type": "added"})
                i -= 1
    changes.reverse()
    return changes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-file",  required=True)
    parser.add_argument("--cloud-file",  required=True)
    parser.add_argument("--cache-file",  required=True)
    parser.add_argument("--output",      required=True)
    args = parser.parse_args()

    local_text = Path(args.local_file).read_text(encoding="utf-8")
    cloud_text = Path(args.cloud_file).read_text(encoding="utf-8")

    cache = {}
    cache_path = Path(args.cache_file)
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())

    prev_titles: dict[str, str] = {}
    for sec in cache.get("sections", []):
        for pt in sec.get("previous_titles", []):
            prev_titles[pt] = sec["section_id"]
        prev_titles[sec.get("title", "")] = sec["section_id"]

    local_secs = split_sections(local_text)
    cloud_secs = split_sections(cloud_text)

    cloud_by_title = {s["title"]: s for s in cloud_secs}
    cloud_by_sid: dict[str, dict] = {}
    for s in cloud_secs:
        sid = prev_titles.get(s["title"], make_section_id(s["title"]))
        cloud_by_sid[sid] = s

    results = []
    has_conflict = False

    for ls in local_secs:
        sid   = prev_titles.get(ls["title"], make_section_id(ls["title"]))
        cloud = cloud_by_sid.get(sid) or cloud_by_title.get(ls["title"])

        if cloud is None:
            status  = "added"
            changes = [{"before": None, "after": p, "change_type": "added"}
                       for p in extract_paragraphs(ls["body"])]
        elif body_hash(ls["body"]) == body_hash(cloud["body"]):
            status  = "unchanged"
            changes = []
        else:
            cached_sec = next((s for s in cache.get("sections", []) if s.get("section_id") == sid), None)
            if cached_sec and cached_sec.get("body_sha256") and \
               cached_sec["body_sha256"] != body_hash(cloud["body"]) and \
               cached_sec["body_sha256"] != body_hash(ls["body"]):
                status = "conflict"
                has_conflict = True
                changes = []
            else:
                status  = "renamed" if ls["title"] != (cloud.get("title") or "") else "modified"
                changes = diff_paragraphs(
                    extract_paragraphs(ls["body"]),
                    extract_paragraphs(cloud["body"])
                )

        results.append({
            "section_id": sid,
            "title":      ls["title"],
            "status":     status,
            "local_text": ls["body"],
            "cloud_text": cloud["body"] if cloud else None,
            "paragraphs": changes,
        })

    local_sids = {prev_titles.get(s["title"], make_section_id(s["title"])) for s in local_secs}
    for cs in cloud_secs:
        sid = prev_titles.get(cs["title"], make_section_id(cs["title"]))
        if sid not in local_sids:
            results.append({
                "section_id": sid, "title": cs["title"], "status": "cloud_only",
                "local_text": None, "cloud_text": cs["body"], "paragraphs": [],
            })

    change_count = sum(1 for s in results if s["status"] != "unchanged")
    output = {"sections": results, "has_conflict": has_conflict, "change_count": change_count}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"Diff: {change_count} changed sections, conflict={has_conflict}", file=sys.stderr)

if __name__ == "__main__":
    main()
