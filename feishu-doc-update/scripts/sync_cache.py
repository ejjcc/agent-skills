#!/usr/bin/env python3
"""
Manage section-level sync cache (.feishu-sync/<doc_id>.json).

Subcommands:
  scaffold  -- build working copy of cache for current sync run
  finalize  -- persist updated cache after successful block update

Usage:
  python3 sync_cache.py scaffold \
    --local-file <md> --cache-file <persisted> \
    --previous-local-file <snapshot> --doc-id <doc_id> \
    [--wiki-token <token>] --output <tmp/sync-cache.json>

  python3 sync_cache.py finalize \
    --cache-file <tmp/sync-cache.json> \
    --plan <tmp/block-plan.json> \
    --meta <tmp/meta.json> \
    --local-file <md> --snapshot-file <persisted_snapshot> \
    --output <persisted_cache>
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
FEISHU_BOARD_RE = re.compile(r'feishu://board/\S+')
WHITEBOARD_TAG_RE = re.compile(r'<whiteboard\s+[^>]*/?>')
MERMAID_BLOCK_RE = re.compile(r'```mermaid\s*\n.*?```', re.DOTALL)

def make_section_id(title):
    return "sec-" + re.sub(r'[^\w\u4e00-\u9fff]', '-', title.lower()).strip('-')

LARK_TABLE_RE = re.compile(r'<lark-table[^>]*>.*?</lark-table>', re.DOTALL)
MD_TABLE_RE = re.compile(r'(?:^\|.+\|$\n?){2,}', re.MULTILINE)

def body_hash(text):
    cleaned = FEISHU_BOARD_RE.sub("<diagram-placeholder>", text)
    cleaned = WHITEBOARD_TAG_RE.sub("<diagram-placeholder>", cleaned)
    cleaned = MERMAID_BLOCK_RE.sub("<diagram-placeholder>", cleaned)
    cleaned = LARK_TABLE_RE.sub("<table-placeholder>", cleaned)
    cleaned = MD_TABLE_RE.sub("<table-placeholder>", cleaned)
    cleaned = re.sub(r'\n{2,}', '\n', cleaned)
    return hashlib.sha256(cleaned.strip().encode()).hexdigest()[:16]

def split_sections(text):
    parts = HEADING_RE.split(text)
    sections = []
    pre = parts[0] if parts else ""
    if pre.strip():
        sections.append({"level": 0, "title": "__preamble__", "body": pre})
    i = 1
    while i < len(parts) - 2:
        sections.append({"level": len(parts[i]), "title": parts[i+1].strip(), "body": parts[i+2]})
        i += 3
    return sections

def scaffold(args):
    doc_id     = args.doc_id
    local_text = Path(args.local_file).read_text(encoding="utf-8")
    local_secs = split_sections(local_text)

    existing = {}
    if args.cache_file and Path(args.cache_file).exists():
        existing = json.loads(Path(args.cache_file).read_text())

    prev_sec_map = {s["section_id"]: s for s in existing.get("sections", [])}
    prev_title_map = {}
    for s in existing.get("sections", []):
        prev_title_map[s.get("title", "")] = s["section_id"]
        for pt in s.get("previous_titles", []):
            prev_title_map[pt] = s["section_id"]

    sections = []
    for ls in local_secs:
        sid = prev_title_map.get(ls["title"], make_section_id(ls["title"]))
        old = prev_sec_map.get(sid, {})
        prev_titles = list(set(old.get("previous_titles", []) + [old.get("title", "")] if old else []))
        prev_titles = [t for t in prev_titles if t and t != ls["title"]]

        paras = [p.strip() for p in re.split(r'\n{2,}', ls["body"].strip()) if p.strip()]
        first_prefix = paras[0][:60] if paras else ""

        sections.append({
            "section_id":      sid,
            "title":           ls["title"],
            "previous_titles": prev_titles,
            "heading_path":    [ls["title"]],
            "body_sha256":     body_hash(ls["body"]),
            "body_preview":    first_prefix,
            "remote":          old.get("remote", {}),
            "fingerprint":     old.get("fingerprint", {
                "heading_text":    ls["title"],
                "first_body_prefix": first_prefix,
            }),
        })

    cache = {
        "schema_version": 3,
        "doc_id":         doc_id,
        "wiki_token":     getattr(args, "wiki_token", None),
        "source_file":    args.local_file,
        "last_local_sha256":   body_hash(local_text),
        "last_doc_revision_id": existing.get("last_doc_revision_id"),
        "structure_version":   existing.get("structure_version"),
        "block_versions":      existing.get("block_versions", {}),
        "sections":       sections,
    }
    Path(args.output).write_text(json.dumps(cache, ensure_ascii=False, indent=2))
    print(f"Scaffolded cache: {len(sections)} sections, {len(cache['block_versions'])} known block versions → {args.output}", file=sys.stderr)

def finalize(args):
    cache    = json.loads(Path(args.cache_file).read_text())
    plan     = json.loads(Path(args.plan).read_text())
    local    = Path(args.local_file).read_text(encoding="utf-8")

    meta = {}
    if args.meta and Path(args.meta).exists():
        meta = json.loads(Path(args.meta).read_text())

    if meta.get("document_revision_id"):
        cache["last_doc_revision_id"] = meta["document_revision_id"]
    cache["last_local_sha256"] = hashlib.sha256(local.encode()).hexdigest()[:16]

    if args.cv_snapshot:
        cv = json.loads(Path(args.cv_snapshot).read_text())
        cache["structure_version"] = cv.get("structure_version")
        cache["block_versions"]    = cv.get("block_versions") or {}

    updated_sids = {p["section_id"] for p in plan.get("plan", [])}
    for sec in cache.get("sections", []):
        if sec["section_id"] in updated_sids:
            matched_plan = next(p for p in plan["plan"] if p["section_id"] == sec["section_id"])
            sec["remote"]["matched_by"] = "updated"
            sec["body_sha256"] = body_hash(sec.get("local_text", ""))

    cache["schema_version"] = 3
    Path(args.output).write_text(json.dumps(cache, ensure_ascii=False, indent=2))
    # also write local snapshot
    if args.snapshot_file:
        Path(args.snapshot_file).write_text(local, encoding="utf-8")
    print(f"Cache finalized → {args.output} (block_versions={len(cache.get('block_versions') or {})}, structure_version={cache.get('structure_version')})", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    sc = sub.add_parser("scaffold")
    sc.add_argument("--local-file",          required=True)
    sc.add_argument("--cache-file")
    sc.add_argument("--previous-local-file")
    sc.add_argument("--doc-id",              required=True)
    sc.add_argument("--wiki-token")
    sc.add_argument("--output",              required=True)

    fn = sub.add_parser("finalize")
    fn.add_argument("--cache-file",    required=True)
    fn.add_argument("--plan",          required=True)
    fn.add_argument("--meta")
    fn.add_argument("--cv-snapshot",   help="fresh client_vars snapshot (fetch_client_vars output)")
    fn.add_argument("--local-file",    required=True)
    fn.add_argument("--snapshot-file")
    fn.add_argument("--output",        required=True)

    args = parser.parse_args()
    if args.cmd == "scaffold":
        scaffold(args)
    elif args.cmd == "finalize":
        finalize(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
