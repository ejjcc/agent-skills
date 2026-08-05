#!/usr/bin/env python3
"""
Render annotated copy or revision document from diff.

Usage:
  python3 render_revision.py --mode annotated|revision \
                              --diff <tmp_dir>/diff.json \
                              --title "<doc_title>" \
                              --source-url "<feishu_url>" \
                              --output <tmp_dir>/output.md
"""
import argparse, json, sys
from datetime import date
from pathlib import Path

def render_annotated(diff: dict, title: str, source_url: str) -> str:
    today = date.today().isoformat()
    lines = [
        f"# {title}（评论标注副本 {today}）",
        "",
        f"> 原文档：{source_url}",
        f"> 生成日期：{today}",
        f"> 本文档用于在原文存在未解决评论期间同步变更，勿直接编辑原文档。",
        "",
    ]
    for sec in diff.get("sections", []):
        if sec["status"] == "unchanged":
            lines.append(f"## {sec['title']}")
            lines.append(sec.get("cloud_text", "") or "")
            lines.append("")
        elif sec["status"] in ("modified", "renamed"):
            lines.append(f"## {sec['title']}")
            for para in sec.get("paragraphs", []):
                ct = para["change_type"]
                if ct == "unchanged":
                    lines.append(para["after"] or "")
                elif ct == "modified":
                    lines.append(f"> [变更前] {para['before']}")
                    lines.append("")
                    lines.append(f"{para['after']}")
                elif ct == "added":
                    lines.append(f"**[新增]** {para['after']}")
                elif ct == "deleted":
                    lines.append(f"~~{para['before']}~~")
            lines.append("")
        elif sec["status"] == "added":
            lines.append(f"## {sec['title']} **[新增]**")
            lines.append(sec.get("local_text", "") or "")
            lines.append("")
        elif sec["status"] == "cloud_only":
            lines.append(f"## {sec['title']} **[本地已删除，云端保留]**")
            lines.append(sec.get("cloud_text", "") or "")
            lines.append("")
        elif sec["status"] == "conflict":
            lines.append(f"## {sec['title']} **[⚠️ 冲突]**")
            lines.append("> 本地和云端均有变更，请手动合并。")
            lines.append("")
            lines.append("**本地版本：**")
            lines.append(sec.get("local_text", "") or "")
            lines.append("")
            lines.append("**云端版本：**")
            lines.append(sec.get("cloud_text", "") or "")
            lines.append("")
    return "\n".join(lines)

def render_revision(diff: dict, title: str, source_url: str) -> str:
    today = date.today().isoformat()
    lines = [
        f"# {title}（修订版 {today}）",
        "",
        f"> 原文档：{source_url}",
        f"> 生成日期：{today}",
        f"> 本修订版包含本地与云端的对比变更，供人工 review 后决定是否更新原文档。",
        "",
    ]
    changed = [s for s in diff.get("sections", []) if s["status"] != "unchanged"]
    unchanged_count = sum(1 for s in diff.get("sections", []) if s["status"] == "unchanged")

    lines.append(f"**变更摘要**：{len(changed)} 个 section 有变更，{unchanged_count} 个未变更。")
    lines.append("")

    for sec in diff.get("sections", []):
        status = sec["status"]
        if status == "unchanged":
            continue
        # skip preamble artefact from lark export (text before first heading)
        if "__preamble__" in sec.get("section_id", ""):
            continue
        lines.append(f"## {sec['title']}")
        if status in ("modified", "renamed"):
            if status == "renamed":
                lines.append(f"> *标题已重命名*")
                lines.append("")
            cloud_text = (sec.get("cloud_text") or "").strip()
            local_text = (sec.get("local_text") or "").strip()
            lines.append("**云端（修改前）：**")
            lines.append("")
            lines.append(cloud_text)
            lines.append("")
            lines.append("**本地（修改后）：**")
            lines.append("")
            lines.append(local_text)
            lines.append("")
        elif status == "added":
            lines.append(f"> *本地新增 section*")
            lines.append("")
            lines.append(sec.get("local_text", "") or "")
        elif status == "cloud_only":
            lines.append(f"> *⚠️ 本地已删除，云端仍存在*")
            lines.append("")
            lines.append(sec.get("cloud_text", "") or "")
        elif status == "conflict":
            lines.append(f"> *⚠️ 冲突：本地和云端均有独立变更*")
            lines.append("")
            lines.append("**本地：**")
            lines.append(sec.get("local_text", "") or "")
            lines.append("")
            lines.append("**云端：**")
            lines.append(sec.get("cloud_text", "") or "")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",       required=True, choices=["annotated", "revision"])
    parser.add_argument("--diff",       required=True)
    parser.add_argument("--title",      required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--output",     required=True)
    args = parser.parse_args()

    diff = json.loads(Path(args.diff).read_text())
    if args.mode == "annotated":
        content = render_annotated(diff, args.title, args.source_url)
    else:
        content = render_revision(diff, args.title, args.source_url)

    Path(args.output).write_text(content, encoding="utf-8")
    print(f"Rendered {args.mode} → {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
