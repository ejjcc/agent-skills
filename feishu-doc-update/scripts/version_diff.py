#!/usr/bin/env python3
"""Diff a fresh client_vars snapshot against the last-synced version map.

Usage:
  version_diff.py \
      --current <tmp_dir/cv_snapshot.json> \
      --cache   <persisted_cache_path or "">  \
      --output  <tmp_dir/version-diff.json>

Inputs:
  --current: output of scripts/fetch_client_vars.sh for the current cloud state.
  --cache  : persisted sync cache (schema v3+) containing last block_versions +
             structure_version. If the file does not exist (first run), all
             current blocks are treated as "cloud_added" and the cloud is
             considered changed.

Output JSON:
  {
    "doc_id": "...",
    "cache_present": bool,
    "structure_version": { "before": int|null, "after": int },
    "structure_changed": bool,
    "cloud_changed":  ["<block_id>", ...],  # version increased
    "cloud_added":    ["<block_id>", ...],  # present now, missing in cache
    "cloud_deleted":  ["<block_id>", ...],  # in cache, missing now
    "counts": { "changed": int, "added": int, "deleted": int },
    "current": { "structure_version": int, "block_count": int }
  }

Exit code is always 0 on success; non-zero only on I/O / schema errors.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--current", required=True, help="fresh client_vars snapshot")
    ap.add_argument("--cache", default="", help="persisted sync cache (optional)")
    ap.add_argument("--output", required=True, help="diff JSON output")
    args = ap.parse_args()

    cur_path = pathlib.Path(args.current)
    out_path = pathlib.Path(args.output)
    cur = load(cur_path)
    if not cur.get("ok", True):
        print(f"version_diff: current snapshot marked not ok: {cur.get('error')}", file=sys.stderr)
        return 2

    cur_versions: dict[str, int] = cur.get("block_versions") or {}
    cur_struct: int | None = cur.get("structure_version")
    doc_id: str = cur.get("doc_id") or ""

    cache_present = False
    prev_versions: dict[str, int] = {}
    prev_struct: int | None = None
    if args.cache:
        cache_path = pathlib.Path(args.cache)
        if cache_path.exists():
            cache = load(cache_path)
            cache_present = True
            prev_versions = cache.get("block_versions") or {}
            prev_struct = cache.get("structure_version")

    cur_ids = set(cur_versions)
    prev_ids = set(prev_versions)

    cloud_added = sorted(cur_ids - prev_ids) if cache_present else sorted(cur_ids)
    cloud_deleted = sorted(prev_ids - cur_ids) if cache_present else []
    cloud_changed = sorted(
        bid for bid in cur_ids & prev_ids
        if cur_versions[bid] > prev_versions[bid]
    )

    structure_changed = (
        not cache_present
        or (prev_struct is not None and cur_struct is not None and cur_struct != prev_struct)
        or bool(cloud_added)
        or bool(cloud_deleted)
    )

    result = {
        "doc_id": doc_id,
        "cache_present": cache_present,
        "structure_version": {"before": prev_struct, "after": cur_struct},
        "structure_changed": structure_changed,
        "cloud_changed": cloud_changed,
        "cloud_added": cloud_added,
        "cloud_deleted": cloud_deleted,
        "counts": {
            "changed": len(cloud_changed),
            "added": len(cloud_added),
            "deleted": len(cloud_deleted),
        },
        "current": {
            "structure_version": cur_struct,
            "block_count": cur.get("block_count") or len(cur_versions),
        },
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        "version_diff: changed={changed} added={added} deleted={deleted} "
        "structure_changed={sc} -> {out}".format(
            **result["counts"],
            sc=result["structure_changed"],
            out=out_path,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
