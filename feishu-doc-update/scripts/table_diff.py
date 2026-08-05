#!/usr/bin/env python3
"""Compute cell-level diff for tables inside changed sections.

Tables in Markdown (local) vs cloud are parsed into (rows × cols) grids and
compared cell-by-cell. If dimensions match and no merges change, the diff
reports per-cell edits with the target text block_ids; callers can then
run normal block-level PATCH on just those cells.

Structural changes (row/col count differs, cells merged/unmerged) force
the section back onto the 6C revision path.

Usage:
  python3 table_diff.py \
      --diff   <tmp_dir>/diff.json \
      --blocks <tmp_dir>/blocks.json \
      --output <tmp_dir>/table-diff.json

Output JSON:
  {
    "per_section": {
      "<section_id>": {
        "safe": true,
        "tables": [
          {
            "table_block_id": "doxlg...",
            "rows": 3, "cols": 4,
            "cells_changed": [
              {
                "row": 1, "col": 2,
                "cell_block_id": "doxlg...",
                "text_block_id": "doxlg...",
                "before": "old text",
                "after": "new text"
              }
            ]
          }
        ],
        "unsafe_reason": null
      }
    }
  }
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Pipe table in local Markdown
PIPE_ROW_RE = re.compile(r'^\s*\|.+\|\s*$', re.MULTILINE)
# Separator row like |---|---|
PIPE_SEP_ROW_RE = re.compile(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$')
# Cloud exports tables as <lark-table>...</lark-table>
LARK_TABLE_RE = re.compile(r'<lark-table[^>]*>(.*?)</lark-table>', re.DOTALL)
LARK_ROW_RE = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
LARK_CELL_RE = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.DOTALL)
HTML_TAG_RE = re.compile(r'<[^>]+>')


def parse_pipe_tables(text: str) -> list[list[list[str]]]:
    """Return list of grids (rows × cols of cell text). Skips separator rows."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        if PIPE_ROW_RE.match(line):
            if PIPE_SEP_ROW_RE.match(line):
                continue  # skip |---|---| separator
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


def parse_lark_tables(text: str) -> list[list[list[str]]]:
    """Parse Feishu-exported <lark-table> blocks."""
    tables: list[list[list[str]]] = []
    for m in LARK_TABLE_RE.finditer(text):
        inner = m.group(1)
        rows: list[list[str]] = []
        for r in LARK_ROW_RE.finditer(inner):
            row_inner = r.group(1)
            cells = [HTML_TAG_RE.sub('', c.group(1)).strip()
                     for c in LARK_CELL_RE.finditer(row_inner)]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def normalize_cell(text: str) -> str:
    """Normalize whitespace / Feishu-specific markdown escapes for comparison."""
    # Feishu exports use \-, \~, \+, \* escapes — strip the backslashes
    text = re.sub(r'\\([\-~+*_.])', r'\1', text)
    return re.sub(r'\s+', ' ', text).strip()


def index_cell_blocks(blocks_items: list[dict]) -> dict[str, dict]:
    """Index blocks.json items by block_id."""
    return {b["block_id"]: b for b in blocks_items}


def extract_cell_text(cell_block: dict, index: dict[str, dict]) -> str:
    """Extract concatenated text_run content from all child blocks of a cell."""
    parts: list[str] = []
    for child_id in cell_block.get("children") or []:
        child = index.get(child_id)
        if not child:
            continue
        field = {2: "text", 3: "heading1", 4: "heading2", 5: "heading3",
                 6: "heading4", 7: "heading5", 8: "heading6", 9: "heading7",
                 10: "bullet", 11: "ordered", 12: "code", 13: "quote"}.get(child.get("block_type"))
        if not field:
            continue
        elements = (child.get(field) or {}).get("elements") or []
        parts.append("".join(e.get("text_run", {}).get("content", "") for e in elements))
    return "\n".join(parts).strip()


def first_text_child_id(cell_block: dict, index: dict[str, dict]) -> str | None:
    """Find the block_id of the first text-bearing child block inside a cell."""
    for child_id in cell_block.get("children") or []:
        child = index.get(child_id)
        if child and child.get("block_type") in {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}:
            return child_id
    return None


def find_section_tables(section: dict, blocks_by_id: dict[str, dict],
                        cache_remote: dict) -> list[dict]:
    """Return the table blocks (block_type=31) whose ancestor is within the section's range."""
    # Walk from start_block_id to end_block_id at the section's parent level, then recurse.
    start_id = cache_remote.get("start_block_id")
    block_ids = cache_remote.get("block_ids") or []
    found: list[dict] = []
    seen: set[str] = set()

    def walk(bid: str) -> None:
        if bid in seen:
            return
        seen.add(bid)
        b = blocks_by_id.get(bid)
        if not b:
            return
        if b.get("block_type") == 31:
            found.append(b)
        for cid in b.get("children") or []:
            walk(cid)

    targets = block_ids or ([start_id] if start_id else [])
    for bid in targets:
        walk(bid)
    return found


def diff_table(local_grid: list[list[str]], cloud_grid: list[list[str]],
               table_block: dict, blocks_by_id: dict[str, dict]) -> dict:
    """Compute cell-level diff for a single table. Returns {"safe": bool, ...}."""
    # Strip header separator artifacts already. Normalize dimensions ignoring trailing empty rows.
    local_rows = len(local_grid)
    local_cols = max((len(r) for r in local_grid), default=0)
    cloud_rows = len(cloud_grid)
    cloud_cols = max((len(r) for r in cloud_grid), default=0)

    cells = table_block.get("table", {}).get("cells") or table_block.get("children") or []
    col_size = (table_block.get("table", {}).get("property") or {}).get("column_size")
    merge_info = (table_block.get("table", {}).get("property") or {}).get("merge_info") or []

    if not col_size or not cells:
        return {"safe": False,
                "unsafe_reason": "remote table missing column_size or cells"}
    remote_rows = len(cells) // col_size
    remote_cols = col_size

    if any((m.get("col_span", 1) > 1 or m.get("row_span", 1) > 1) for m in merge_info):
        return {"safe": False, "unsafe_reason": "remote table has merged cells"}

    if not (local_rows == cloud_rows == remote_rows and
            local_cols == cloud_cols == remote_cols):
        return {"safe": False,
                "unsafe_reason": f"dim mismatch local={local_rows}x{local_cols} "
                                 f"cloud={cloud_rows}x{cloud_cols} "
                                 f"remote={remote_rows}x{remote_cols}"}

    cells_changed: list[dict] = []
    for r in range(remote_rows):
        for c in range(remote_cols):
            idx = r * remote_cols + c
            cell_block_id = cells[idx]
            cell_block = blocks_by_id.get(cell_block_id)
            if not cell_block:
                return {"safe": False,
                        "unsafe_reason": f"cell block {cell_block_id} missing from tree"}
            local_text = normalize_cell(local_grid[r][c] if c < len(local_grid[r]) else "")
            cloud_text = normalize_cell(cloud_grid[r][c] if c < len(cloud_grid[r]) else "")
            if local_text == cloud_text:
                continue
            text_id = first_text_child_id(cell_block, blocks_by_id)
            if not text_id:
                return {"safe": False,
                        "unsafe_reason": f"cell {cell_block_id} has no text block to patch"}
            cells_changed.append({
                "row": r, "col": c,
                "cell_block_id": cell_block_id,
                "text_block_id": text_id,
                "before": cloud_text,
                "after": local_text,
            })

    return {
        "safe": True,
        "table_block_id": table_block["block_id"],
        "rows": remote_rows,
        "cols": remote_cols,
        "cells_changed": cells_changed,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff", required=True)
    ap.add_argument("--blocks", required=True)
    ap.add_argument("--cache-file", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    diff = json.loads(Path(args.diff).read_text())
    blocks_raw = json.loads(Path(args.blocks).read_text())
    items = blocks_raw.get("data", {}).get("items") or blocks_raw.get("items") or []
    blocks_by_id = index_cell_blocks(items)

    cache = {}
    if Path(args.cache_file).exists():
        cache = json.loads(Path(args.cache_file).read_text())
    sec_cache = {s["section_id"]: s for s in cache.get("sections", [])}

    per_section: dict[str, dict] = {}
    for sec in diff.get("sections", []):
        if sec.get("status") not in ("modified", "renamed", "added"):
            continue
        local_text = sec.get("local_text") or ""
        cloud_text = sec.get("cloud_text") or ""
        local_tables = parse_pipe_tables(local_text)
        cloud_tables = parse_lark_tables(cloud_text) or parse_pipe_tables(cloud_text)
        if not local_tables and not cloud_tables:
            continue  # no tables in this section

        sid = sec["section_id"]
        cached_remote = (sec_cache.get(sid) or {}).get("remote", {})
        remote_tables = find_section_tables(sec, blocks_by_id, cached_remote)

        if len(local_tables) != len(cloud_tables) or len(local_tables) != len(remote_tables):
            per_section[sid] = {
                "safe": False,
                "unsafe_reason": (f"table count mismatch: local={len(local_tables)} "
                                  f"cloud={len(cloud_tables)} remote={len(remote_tables)}"),
                "tables": [],
            }
            continue

        results: list[dict] = []
        any_unsafe = False
        for local_g, cloud_g, tbl in zip(local_tables, cloud_tables, remote_tables):
            r = diff_table(local_g, cloud_g, tbl, blocks_by_id)
            results.append(r)
            if not r.get("safe"):
                any_unsafe = True
        per_section[sid] = {
            "safe": not any_unsafe,
            "unsafe_reason": next((r.get("unsafe_reason") for r in results
                                   if not r.get("safe")), None),
            "tables": results,
        }

    output = {"per_section": per_section}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2))
    counts = {
        "sections_with_tables": len(per_section),
        "safe": sum(1 for v in per_section.values() if v.get("safe")),
        "cells_changed": sum(sum(len(t.get("cells_changed") or [])
                                 for t in v.get("tables", []) if t.get("safe"))
                             for v in per_section.values()),
    }
    print(f"table_diff: {counts} -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
