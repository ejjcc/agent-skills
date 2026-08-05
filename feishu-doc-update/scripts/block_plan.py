#!/usr/bin/env python3
"""
Determine if section-level block update is safe (fallback from text-fingerprint path).

Checks: no conflict, ≤3 changed sections, each section uniquely maps to a cached block range,
content is within safe Markdown subset.

Usage:
  python3 block_plan.py --diff <tmp_dir>/diff.json \
                         --blocks <tmp_dir>/blocks.json \
                         --cache-file <tmp_dir>/sync-cache.json \
                         --output <tmp_dir>/block-plan.json

Output JSON:
{
  "eligible": true,
  "reason": "...",
  "plan": [
    {
      "section_id": "...",
      "title": "...",
      "status": "modified",
      "parent_block_id": "...",
      "heading_block_id": "...",
      "start_block_id": "...",
      "end_block_id": "...",
      "block_ids": [...],
      "new_content": "..."
    }
  ]
}
"""
import argparse, json, re, sys
from pathlib import Path

# Block types that are not safe for inline patch
UNSAFE_TYPES = {22, 27, 28, 34}  # whiteboard, image, file, diagram (tables handled via table_diff)
# Non-table unsafe patterns — always reject. Tables handled separately by table_diff.
NON_TABLE_UNSAFE_PATTERNS = [
    re.compile(r'!\[.*?\]\('),             # image
    re.compile(r'```mermaid'),             # mermaid
    re.compile(r'feishu://board/'),        # whiteboard link
]
PIPE_TABLE_PATTERN = re.compile(r'^\|.*\|', re.MULTILINE)


def has_non_table_unsafe(text: str) -> bool:
    return any(p.search(text) for p in NON_TABLE_UNSAFE_PATTERNS)


def has_table(text: str) -> bool:
    return bool(PIPE_TABLE_PATTERN.search(text))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff",       required=True)
    parser.add_argument("--blocks",     required=True)
    parser.add_argument("--cache-file", required=True)
    parser.add_argument("--table-diff", help="optional table_diff.py output", default="")
    parser.add_argument("--output",     required=True)
    args = parser.parse_args()

    diff   = json.loads(Path(args.diff).read_text())
    cache  = {}
    if Path(args.cache_file).exists():
        cache = json.loads(Path(args.cache_file).read_text())

    table_diff_by_section: dict[str, dict] = {}
    if args.table_diff and Path(args.table_diff).exists():
        tdiff = json.loads(Path(args.table_diff).read_text())
        table_diff_by_section = tdiff.get("per_section", {})

    blocks_raw = json.loads(Path(args.blocks).read_text())
    block_ids_set = {b["block_id"] for b in blocks_raw.get("data", {}).get("items", [])}

    sec_cache = {s["section_id"]: s for s in cache.get("sections", [])}

    if diff.get("has_conflict"):
        result = {"eligible": False, "reason": "has conflict", "plan": []}
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return

    changed = [s for s in diff["sections"] if s["status"] in ("modified", "renamed", "added")]

    if len(changed) > 3:
        result = {"eligible": False, "reason": f"too many changed sections: {len(changed)}", "plan": []}
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return

    plan = []
    for sec in changed:
        sid   = sec["section_id"]
        local = sec.get("local_text", "")

        if has_non_table_unsafe(local or ""):
            result = {"eligible": False,
                      "reason": f"section '{sec['title']}' has unsafe content (image/mermaid/board)",
                      "plan": []}
            Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
            return

        section_table_plans: list[dict] = []
        if has_table(local or ""):
            td = table_diff_by_section.get(sid)
            if not td:
                result = {"eligible": False,
                          "reason": f"section '{sec['title']}' has table but no table_diff was provided",
                          "plan": []}
                Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
                return
            if not td.get("safe"):
                result = {"eligible": False,
                          "reason": f"section '{sec['title']}' table unsafe: {td.get('unsafe_reason')}",
                          "plan": []}
                Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
                return
            for tbl in td.get("tables", []):
                if tbl.get("safe") and tbl.get("cells_changed"):
                    section_table_plans.append({
                        "table_block_id": tbl["table_block_id"],
                        "cells_changed":  tbl["cells_changed"],
                    })

        cached = sec_cache.get(sid)
        if not cached:
            result = {"eligible": False,
                      "reason": f"section '{sec['title']}' has no cache entry; needs remap",
                      "plan": []}
            Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
            return

        remote = cached.get("remote", {})
        heading_id = remote.get("heading_block_id")
        start_id   = remote.get("start_block_id")
        end_id     = remote.get("end_block_id")
        parent_id  = remote.get("parent_block_id")

        # validate cached ids still exist in block tree
        for bid in [heading_id, start_id]:
            if bid and bid not in block_ids_set:
                result = {"eligible": False,
                          "reason": f"cached block {bid} for section '{sec['title']}' not found in tree",
                          "plan": []}
                Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
                return

        plan.append({
            "section_id":      sid,
            "title":           sec["title"],
            "status":          sec["status"],
            "parent_block_id": parent_id,
            "heading_block_id": heading_id,
            "start_block_id":  start_id,
            "end_block_id":    end_id,
            "block_ids":       remote.get("block_ids", []),
            "new_content":     local,
            "table_plans":     section_table_plans,
        })

    result = {"eligible": True, "reason": f"{len(plan)} section(s) safely mapped", "plan": plan}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Block plan: eligible=True, sections={len(plan)}", file=sys.stderr)

if __name__ == "__main__":
    main()
