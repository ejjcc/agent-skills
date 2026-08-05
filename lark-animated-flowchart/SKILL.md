---
name: lark-animated-flowchart
metadata:
  version: 0.1.0
description: Generate lightweight animated flowcharts/topology diagrams as self-contained HTML and embed them into Feishu/Lark docs via HTML Box. Use when the user asks to animate a flowchart, architecture chart, topology, agent workflow, multi-agent orchestration, sequence/flow visualization, or wants an interactive animation in a Feishu/Lark document.
---

# Lark Animated Flowchart

## What This Skill Produces

Create a zero-dependency single-file HTML animation from structured diagram data:

- SVG topology rendered from `nodes` and `edges`
- Auto-play timeline with node highlights, edge highlights, message tokens, captions, and progress dots
- Minimal controls: previous step, play/pause, next step, clickable progress dots
- Fixed light theme by default, suitable for Feishu documents
- No internal vertical scrollbar in the HTML Box iframe; inner scrolling interferes with document scrolling
- Responsive fullscreen behavior: the diagram should scale up when Feishu HTML Box is opened fullscreen
- Built-in publishing into Feishu/Lark Docx HTML Box using `lark-cli`

Default output should not use React, Framer Motion, Mermaid runtime, external CDNs, speed controls, replay buttons, keyboard-only controls, or an internally scrollable iframe.

## Quick Workflow

1. Collect or infer a `pattern.json` matching [PATTERN_SCHEMA.md](PATTERN_SCHEMA.md).
2. Generate HTML:

```bash
python3 ~/.claude/skills/lark-animated-flowchart/scripts/animate_diagram.py \
  --pattern pattern.json \
  --out animated-diagram.html
```

3. Preview locally:

```bash
python3 -m http.server 8799 --bind 127.0.0.1
```

Open `http://127.0.0.1:8799/animated-diagram.html`, verify:

- Auto-play advances through all timeline steps.
- Play/pause, previous/next, and progress dots work.
- Background is light, not black.
- The iframe content fits without a vertical scrollbar.
- Fullscreen preview uses the larger viewport instead of staying capped at a tiny card width.
- Tokens travel in the correct direction; `!edgeId` means reverse travel.

4. If the user wants it in Feishu/Lark docs, publish with the bundled HTML Box helper:

```bash
python3 ~/.claude/skills/lark-animated-flowchart/scripts/publish_lark_html_box.py \
  --html animated-diagram.html \
  --title "Animated Diagram"
```

For an existing Docx:

```bash
python3 ~/.claude/skills/lark-animated-flowchart/scripts/publish_lark_html_box.py \
  --html animated-diagram.html \
  --doc-token <docx_token>
```

## Pattern Data Rules

- Canvas coordinates assume `viewBox="0 0 900 540"`.
- Nodes need stable `id`, `x`, `y`, and `label`; `w`, `h`, `sub`, and `kind` are optional.
- Edges are keyed by edge ID. Timeline `fire` entries reference those IDs.
- Prefix a timeline `fire` entry with `!` to animate tokens in reverse.
- Keep captions short; HTML is allowed for inline `<b>` and `<code>`.
- Use `kind: "accent"` for the current orchestrator, `kind: "dark"` for final/output nodes, and `kind: "user"` for user pills.

## Feishu HTML Box Notes

- HTML Box works because the output is a self-contained HTML file with inline CSS/JS.
- Publishing only assumes `lark-cli` is installed and logged in as user.
- Keep the source code block deleted after insertion unless the user explicitly wants to edit HTML in the document UI.
- Use a fixed light theme unless the user explicitly asks for dark or theme-following behavior; Feishu docs are commonly light, and `prefers-color-scheme: dark` can produce an unwanted black card.
- Avoid inner scrollbars: set `html, body { overflow: hidden; }`, keep the card height compact, and prefer smaller canvas/caption/control spacing over relying on iframe scrolling.
- Avoid locking the card to a small fixed width such as `max-width: 720px`; use a responsive cap such as `max-width: min(1180px, calc(100vw - padding))` so Feishu fullscreen mode feels intentional.

## Files

- `scripts/animate_diagram.py`: generator script.
- `scripts/publish_lark_html_box.py`: create/append Feishu HTML Box widget with direct `add_ons.record` prefill.
- `PATTERN_SCHEMA.md`: input schema and conventions.
- `examples/supervisor.json`: sample from the successful Supervisor / Manager animation.
