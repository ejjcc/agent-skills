#!/usr/bin/env bash
# Fetch the full client_vars snapshot for a Lark docx via an attached playwright-cli session.
#
# Usage:
#   fetch_client_vars.sh --doc-id <obj_token> \
#                        [--wiki-token <wiki_node_token>] \
#                        [--wiki-space-id <id>] \
#                        [--host https://bytedance.larkoffice.com] \
#                        --output <path.json>
#
# Prerequisites:
#   - playwright-cli in PATH, PLAYWRIGHT_MCP_EXTENSION_TOKEN exported
#   - The user has run `playwright-cli attach --extension` and is logged into the host
#
# Output JSON shape (written to --output):
#   {
#     "ok": true,
#     "fetched_at": "2026-04-18T...",
#     "doc_id": "...",
#     "host": "https://bytedance.larkoffice.com",
#     "structure_version": 1,
#     "block_count": 486,
#     "pages_fetched": 5,
#     "block_versions": {"<block_id>": <int>, ...},
#     "block_types":    {"<block_id>": "<type_str>", ...},
#     "block_sequence": ["<block_id>", ...],
#     "skip_blocks":    ["<block_id>", ...],
#     "meta_map":       { ... raw meta_map from response ... }
#   }

set -euo pipefail

DOC_ID=""
WIKI_TOKEN=""
WIKI_SPACE_ID=""
OUTPUT=""
HOST="https://bytedance.larkoffice.com"
LIMIT=100

while [[ $# -gt 0 ]]; do
  case "$1" in
    --doc-id) DOC_ID="$2"; shift 2;;
    --wiki-token) WIKI_TOKEN="$2"; shift 2;;
    --wiki-space-id) WIKI_SPACE_ID="$2"; shift 2;;
    --output) OUTPUT="$2"; shift 2;;
    --host) HOST="$2"; shift 2;;
    --limit) LIMIT="$2"; shift 2;;
    *) echo "Unknown flag: $1" >&2; exit 2;;
  esac
done

if [[ -z "$DOC_ID" || -z "$OUTPUT" ]]; then
  echo "fetch_client_vars: missing --doc-id or --output" >&2
  exit 2
fi

CONTAINER_TYPE="docx"
CONTAINER_ID="$DOC_ID"
if [[ -n "$WIKI_TOKEN" ]]; then
  CONTAINER_TYPE="wiki2.0"
  CONTAINER_ID="$WIKI_TOKEN"
fi

if ! command -v playwright-cli >/dev/null 2>&1; then
  echo "fetch_client_vars: playwright-cli not found in PATH" >&2
  exit 3
fi

if [[ -z "${PLAYWRIGHT_MCP_EXTENSION_TOKEN:-}" ]]; then
  echo "fetch_client_vars: PLAYWRIGHT_MCP_EXTENSION_TOKEN not set (run: playwright-cli attach --extension)" >&2
  exit 3
fi

# Ensure the tab is on the right host so cookies get attached.
playwright-cli goto "$HOST" >/dev/null 2>&1 || true

# Build the fetch loop as a single-line async function.
JS='async()=>{'
JS+='const csrf=(document.cookie.split("; ").find(c=>c.startsWith("csrf_token=")) || "").split("=")[1]||"";'
JS+='const qs=new URLSearchParams({id:"'"$DOC_ID"'",mode:"7",limit:"'"$LIMIT"'",cursor:"",open_type:"1",container_type:"'"$CONTAINER_TYPE"'",container_id:"'"$CONTAINER_ID"'"});'
if [[ -n "$WIKI_SPACE_ID" ]]; then
  JS+='qs.set("wiki_space_id","'"$WIKI_SPACE_ID"'");'
fi
JS+='let cursor="",page=0;const allBlocks={};let structureVersion=null,metaMap=null;const sequence=[],skipped=[];'
JS+='while(page<50){page++;qs.set("cursor",cursor);const url="/space/api/docx/pages/client_vars?"+qs.toString();'
JS+='const r=await fetch(url,{credentials:"include",headers:{"Accept":"application/json","X-CSRFToken":csrf}});'
JS+='const j=await r.json();if(j.code!==0)return{ok:false,error:j};'
JS+='const d=j.data;Object.assign(allBlocks,d.block_map||{});'
JS+='if(Array.isArray(d.block_sequence))sequence.push(...d.block_sequence);'
JS+='if(Array.isArray(d.skip_blocks))skipped.push(...d.skip_blocks);'
JS+='if(structureVersion===null)structureVersion=d.structure_version;'
JS+='if(metaMap===null)metaMap=d.meta_map;'
JS+='if(!d.has_more||!d.cursor||d.cursor===cursor)break;cursor=d.cursor;}'
JS+='const versions={},types={};for(const[bid,b]of Object.entries(allBlocks)){versions[bid]=b.version;if(b.data&&b.data.type)types[bid]=b.data.type;}'
JS+='return{ok:true,fetched_at:new Date().toISOString(),doc_id:"'"$DOC_ID"'",host:location.origin,structure_version:structureVersion,block_count:Object.keys(allBlocks).length,pages_fetched:page,block_versions:versions,block_types:types,block_sequence:sequence,skip_blocks:skipped,meta_map:metaMap};}'

playwright-cli eval --filename "$OUTPUT" "$JS" >/dev/null

# Unwrap double-encoded JSON (eval --filename writes JSON-encoded string) and validate.
python3 - "$OUTPUT" <<'PY'
import json, sys
p = sys.argv[1]
raw = open(p).read()
obj = json.loads(raw)
if isinstance(obj, str):
    obj = json.loads(obj)
if not obj.get("ok"):
    print(f"fetch_client_vars: error from client_vars: {json.dumps(obj.get('error'), ensure_ascii=False)[:500]}", file=sys.stderr)
    sys.exit(5)
open(p, "w").write(json.dumps(obj, ensure_ascii=False, indent=2))
print(f"fetch_client_vars: {obj['block_count']} blocks, structure_version={obj['structure_version']}, pages={obj['pages_fetched']} -> {p}")
PY
