#!/usr/bin/env python3
"""
Load feishu-mapping.json and find the entry for a given local file.
Exits with code 1 if not found.

Usage:
  python3 load_mapping.py --mapping docs/feishu-mapping.json \
                          --local-file docs/plans/example.md
Output (stdout, JSON):
  { "local_file": "...", "feishu_doc_id": "...", ... }
"""
import argparse, json, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--mapping", required=True)
parser.add_argument("--local-file", required=True)
args = parser.parse_args()

mapping_path = Path(args.mapping)
if not mapping_path.exists():
    print(f"ERROR: mapping file not found: {mapping_path}", file=sys.stderr)
    sys.exit(1)

data = json.loads(mapping_path.read_text())
local_file = args.local_file.lstrip("./")

for entry in data.get("mappings", []):
    if entry.get("local_file", "").lstrip("./") == local_file:
        print(json.dumps(entry, ensure_ascii=False))
        sys.exit(0)

print(f"ERROR: no mapping found for '{args.local_file}'", file=sys.stderr)
sys.exit(1)
