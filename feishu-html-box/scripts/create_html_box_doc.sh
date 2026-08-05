#!/usr/bin/env bash
# Create (or append into) a Feishu doc that embeds an HTML Box (妙笔 / Magic Page).
# Pair: HTML code block (block_type=14, code.style.language=24) + HTML Box widget
# (block_type=40, component_type_id="blk_6900429af84180025ce76527", record="{}").
#
# Default behavior: insert code block + widget, then DELETE the code block — the
# HTML is auto-mirrored into widget.add_ons.record, so the iframe still renders
# but the source doesn't bloat the doc. Use --keep-source to keep the code block
# visible (e.g. when you want to edit HTML in the Feishu UI later).
#
# Usage:
#   create_html_box_doc.sh --html <file> --title <title> [--summary <text>] [--keep-source]
#   create_html_box_doc.sh --html <file> --doc-token <docx_token> [--keep-source]
#
# Requires: lark-cli (logged in as user), jq.

set -euo pipefail

HTML_LANGUAGE=24
HTML_BOX_COMPONENT_TYPE_ID="blk_6900429af84180025ce76527"

usage() {
  cat >&2 <<USAGE
Usage:
  $(basename "$0") --html <file> --title <title> [--summary <text>] [--keep-source]
  $(basename "$0") --html <file> --doc-token <docx_token> [--keep-source]

  --keep-source   keep the HTML code block visible in the doc (default: deleted)
USAGE
  exit 2
}

HTML_FILE=""
TITLE=""
SUMMARY=""
DOC_TOKEN=""
KEEP_SOURCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --html)         HTML_FILE="$2"; shift 2 ;;
    --title)        TITLE="$2";     shift 2 ;;
    --summary)      SUMMARY="$2";   shift 2 ;;
    --doc-token)    DOC_TOKEN="$2"; shift 2 ;;
    --keep-source)  KEEP_SOURCE=1;  shift   ;;
    -h|--help)      usage ;;
    *)              usage ;;
  esac
done

[[ -n "$HTML_FILE" && -f "$HTML_FILE" ]] || { echo "missing --html <file>" >&2; usage; }
[[ -n "$TITLE" || -n "$DOC_TOKEN" ]]    || { echo "need --title (new) or --doc-token (append)" >&2; usage; }
command -v lark-cli >/dev/null || { echo "lark-cli not found" >&2; exit 1; }
command -v jq >/dev/null       || { echo "jq not found" >&2; exit 1; }

HTML_CONTENT="$(cat "$HTML_FILE")"

if [[ -z "$DOC_TOKEN" ]]; then
  intro="${SUMMARY:-这个妙笔应用以交互式网页的形式展示「$TITLE」，可直接在文档中查看和体验。}"
  md="# ${TITLE}\n\n${intro}\n"
  resp="$(lark-cli docs +create --title "$TITLE" --markdown "$(printf '%b' "$md")")"
  DOC_TOKEN="$(jq -r '.data.doc_id' <<<"$resp")"
  [[ -n "$DOC_TOKEN" && "$DOC_TOKEN" != "null" ]] || { echo "failed to create doc: $resp" >&2; exit 1; }
fi

# 1) Insert HTML code block
code_payload="$(jq -n --arg c "$HTML_CONTENT" --argjson lang "$HTML_LANGUAGE" '{
  children: [{
    block_type: 14,
    code: {
      style: { language: $lang, wrap: true },
      elements: [{ text_run: { content: $c } }]
    }
  }],
  index: -1
}')"
code_resp="$(lark-cli api POST "/open-apis/docx/v1/documents/$DOC_TOKEN/blocks/$DOC_TOKEN/children" \
  --as user --data "$code_payload")"
code_block_id="$(jq -r '.data.children[0].block_id' <<<"$code_resp")"
code_lang="$(jq -r '.data.children[0].code.style.language' <<<"$code_resp")"
[[ "$code_lang" == "$HTML_LANGUAGE" ]] || { echo "code block language mismatch ($code_lang != $HTML_LANGUAGE): $code_resp" >&2; exit 1; }

# 2) Insert HTML Box widget right after. Prefill add_ons.record directly instead of
# relying on Feishu's async code-block -> widget mirror; otherwise immediate
# source deletion can leave record as "{}" and render a blank box.
box_payload="$(jq -n --arg t "$HTML_BOX_COMPONENT_TYPE_ID" --arg h "$HTML_CONTENT" '{
  children: [{
    block_type: 40,
    add_ons: { component_id: "", component_type_id: $t, record: ({html: $h} | tojson) }
  }],
  index: -1
}')"
box_resp="$(lark-cli api POST "/open-apis/docx/v1/documents/$DOC_TOKEN/blocks/$DOC_TOKEN/children" \
  --as user --data "$box_payload")"
box_block_id="$(jq -r '.data.children[0].block_id // empty' <<<"$box_resp")"
box_record="$(jq -r '.data.children[0].add_ons.record // empty' <<<"$box_resp")"
if ! jq -e --arg h "$HTML_CONTENT" '.html == $h' >/dev/null 2>&1 <<<"$box_record"; then
  echo "html box record was not persisted correctly" >&2
  echo "$box_resp" >&2
  exit 1
fi

# 3) Default: delete the source code block. The widget already has its own record.
source_deleted=false
if [[ "$KEEP_SOURCE" == "0" ]]; then
  idx="$(lark-cli api GET "/open-apis/docx/v1/documents/$DOC_TOKEN/blocks/$DOC_TOKEN" --as user \
    | jq --arg id "$code_block_id" '.data.block.children | index($id)')"
  if [[ -n "$idx" && "$idx" != "null" ]]; then
    end=$((idx + 1))
    lark-cli api DELETE "/open-apis/docx/v1/documents/$DOC_TOKEN/blocks/$DOC_TOKEN/children/batch_delete" \
      --as user --data "{\"start_index\":$idx,\"end_index\":$end}" >/dev/null
    source_deleted=true
  fi
fi

jq -n \
  --arg doc "$DOC_TOKEN" \
  --arg url "https://www.feishu.cn/docx/$DOC_TOKEN" \
  --arg cb  "$code_block_id" \
  --arg bb  "$box_block_id" \
  --argjson lang "$HTML_LANGUAGE" \
  --argjson sd  "$source_deleted" \
  '{ ok: true, doc_token: $doc, doc_url: $url, code_block_id: $cb, html_box_block_id: $bb, code_language: $lang, source_deleted: $sd }'
