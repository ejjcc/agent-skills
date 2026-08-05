#!/usr/bin/env bash
# Fetch cloud state: cloud.md (markdown export), blocks.json (block tree), comments.json
# Usage: bash fetch_cloud_state.sh --doc-id <doc_id> [--wiki-token <wiki_token>] --out-dir <dir>
set -euo pipefail

DOC_ID=""
WIKI_TOKEN=""
OUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --doc-id)     DOC_ID="$2";     shift 2 ;;
    --wiki-token) WIKI_TOKEN="$2"; shift 2 ;;
    --out-dir)    OUT_DIR="$2";    shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$DOC_ID" ]]  && { echo "--doc-id required" >&2; exit 1; }
[[ -z "$OUT_DIR" ]] && { echo "--out-dir required" >&2; exit 1; }
mkdir -p "$OUT_DIR"

# 1. Fetch markdown (extract markdown field from +fetch JSON output)
lark-cli docs +fetch --doc "$DOC_ID" --as user -q '.data.markdown' > "$OUT_DIR/cloud.md"

# 2. Fetch block tree (full, paginated)
lark-cli api GET "/open-apis/docx/v1/documents/$DOC_ID/blocks" \
  --as user --page-all --format json > "$OUT_DIR/blocks.json"

# 3. Fetch comments
COMMENTS_FILE_ID="${WIKI_TOKEN:-$DOC_ID}"
lark-cli api GET "/open-apis/drive/v1/files/$COMMENTS_FILE_ID/comments" \
  --params '{"file_type":"docx"}' \
  --as user --page-all --format json > "$OUT_DIR/comments.json"

echo "Cloud state written to $OUT_DIR" >&2
