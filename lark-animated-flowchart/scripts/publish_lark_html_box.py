#!/usr/bin/env python3
"""Create or append a Feishu/Lark HTML Box widget for a self-contained HTML file.

This helper is intentionally self-contained except for `lark-cli`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


HTML_LANGUAGE = 24
HTML_BOX_COMPONENT_TYPE_ID = "blk_6900429af84180025ce76527"


def run_json(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not return JSON: {' '.join(args)}\n{proc.stdout}") from exc


def create_doc(title: str, summary: str | None) -> str:
    intro = summary or f"这个动画以交互式网页形式展示「{title}」，可直接在文档中查看和体验。"
    markdown = f"# {title}\n\n{intro}\n"
    resp = run_json(["lark-cli", "docs", "+create", "--title", title, "--markdown", markdown])
    doc_token = resp.get("data", {}).get("doc_id")
    if not doc_token:
        raise RuntimeError(f"failed to create doc: {json.dumps(resp, ensure_ascii=False)}")
    return doc_token


def post_children(doc_token: str, payload: dict) -> dict:
    return run_json([
        "lark-cli",
        "api",
        "POST",
        f"/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
        "--as",
        "user",
        "--data",
        json.dumps(payload, ensure_ascii=False),
    ])


def insert_code_block(doc_token: str, html: str) -> tuple[str, dict]:
    payload = {
        "children": [
            {
                "block_type": 14,
                "code": {
                    "style": {"language": HTML_LANGUAGE, "wrap": True},
                    "elements": [{"text_run": {"content": html}}],
                },
            }
        ],
        "index": -1,
    }
    resp = post_children(doc_token, payload)
    child = resp.get("data", {}).get("children", [{}])[0]
    block_id = child.get("block_id")
    language = child.get("code", {}).get("style", {}).get("language")
    if language != HTML_LANGUAGE or not block_id:
        raise RuntimeError(f"HTML code block was not created correctly: {json.dumps(resp, ensure_ascii=False)}")
    return block_id, resp


def insert_html_box(doc_token: str, html: str) -> tuple[str, dict]:
    record = json.dumps({"html": html}, ensure_ascii=False)
    payload = {
        "children": [
            {
                "block_type": 40,
                "add_ons": {
                    "component_id": "",
                    "component_type_id": HTML_BOX_COMPONENT_TYPE_ID,
                    "record": record,
                },
            }
        ],
        "index": -1,
    }
    resp = post_children(doc_token, payload)
    child = resp.get("data", {}).get("children", [{}])[0]
    block_id = child.get("block_id")
    persisted_record = child.get("add_ons", {}).get("record") or ""
    try:
        persisted_html = json.loads(persisted_record).get("html")
    except json.JSONDecodeError:
        persisted_html = None
    if not block_id or persisted_html != html:
        raise RuntimeError(f"HTML Box record was not persisted correctly: {json.dumps(resp, ensure_ascii=False)}")
    return block_id, resp


def root_children(doc_token: str) -> list[str]:
    resp = run_json([
        "lark-cli",
        "api",
        "GET",
        f"/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}",
        "--as",
        "user",
    ])
    return resp.get("data", {}).get("block", {}).get("children", [])


def delete_root_child(doc_token: str, block_id: str) -> bool:
    children = root_children(doc_token)
    try:
        idx = children.index(block_id)
    except ValueError:
        return False
    payload = {"start_index": idx, "end_index": idx + 1}
    run_json([
        "lark-cli",
        "api",
        "DELETE",
        f"/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children/batch_delete",
        "--as",
        "user",
        "--data",
        json.dumps(payload),
    ])
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, help="Self-contained HTML file")
    parser.add_argument("--title", help="Create a new doc with this title")
    parser.add_argument("--summary", help="Optional intro text when creating a new doc")
    parser.add_argument("--doc-token", help="Append into an existing Docx token")
    parser.add_argument("--keep-source", action="store_true", help="Keep the HTML source code block visible")
    args = parser.parse_args(argv)

    html_path = Path(args.html)
    if not html_path.is_file():
        raise SystemExit(f"HTML file not found: {html_path}")
    if not args.title and not args.doc_token:
        raise SystemExit("need --title for a new doc or --doc-token to append into an existing doc")

    html = html_path.read_text(encoding="utf-8")
    doc_token = args.doc_token or create_doc(args.title, args.summary)
    code_block_id, _ = insert_code_block(doc_token, html)
    html_box_block_id, _ = insert_html_box(doc_token, html)
    source_deleted = False
    if not args.keep_source:
        source_deleted = delete_root_child(doc_token, code_block_id)

    print(json.dumps({
        "ok": True,
        "doc_token": doc_token,
        "doc_url": f"https://www.feishu.cn/docx/{doc_token}",
        "code_block_id": code_block_id,
        "html_box_block_id": html_box_block_id,
        "code_language": HTML_LANGUAGE,
        "source_deleted": source_deleted,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
