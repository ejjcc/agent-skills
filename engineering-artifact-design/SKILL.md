---
name: engineering-artifact-design
metadata:
  version: 0.1.0
description: Recreate the warm editorial, browser-native HTML artifact style from thariqs.github.io/html-effectiveness. Use when building or restyling self-contained HTML artifacts for software R&D understanding, technical research, and decision-making, including code reviews, architecture/concept/process explainers, technology investigations, option evaluations, incident/debug pages, ADRs, migration plans, API/data contracts, performance/security/test/release/onboarding/audit pages, prototypes, or custom editors.
---

# Engineering Artifact Design

Use this skill to design or implement paper-like, browser-native engineering artifacts: warm ivory background, serif editorial headings, mono metadata, paper panels, restrained borders, inline SVG diagrams, native HTML controls, and lightweight interactions.

## Quick Start

1. Pick the closest pattern from the `Pattern Selector` table in `references/design-style.md`.
2. If the artifact needs a non-trivial diagram, read `references/diagram-grammar.md` and choose one dominant diagram type before drawing.
3. Copy the matching starter template from `assets/`:
   - `starter.html` — generic single-document
   - `starter-review.html` — PR/code review with risk map and file cards
   - `starter-arch.html` — architecture map with key files and boundaries
   - `starter-research.html` — technology evaluation with candidate cards and matrix
   - `diagram-templates.html` — tokenized architecture, sequence, and timeline SVG skeletons
4. Replace content, keep tokens, CSS classes, and diagram primitives intact.
5. Verify visually at desktop and mobile widths, including dark mode for SVG diagrams.

### Minimal Example

```html
<header>
  <div class="eyebrow">system / artifact type</div>
  <h1>Artifact Title</h1>
  <p>One-line problem or scope statement.</p>
  <div class="chips">
    <span class="chip"><span class="dot clay"></span>needs attention</span>
    <span class="chip"><span class="dot olive"></span>verified</span>
  </div>
</header>
<div class="callout">
  <strong>TL;DR.</strong> Key finding or decision in one paragraph.
</div>
```

## Workflow

1. Classify the artifact: review, architecture, concept, process, technical research, option evaluation, incident, decision, migration, contract, ownership, performance, security, test, rollout, onboarding, requirement, audit, prototype, or editor.
2. Read `references/design-style.md` from the top through `Pattern Selector`, then jump to the matching pattern section. Read foundations when you need tokens, component details, or motion rules.
3. For diagrams beyond tiny schematics, read `references/diagram-grammar.md`; select one diagram grammar and stay within its complexity budget.
4. For new standalone HTML, start from the appropriate `assets/starter-*.html` and adapt the shell instead of rebuilding tokens and primitives from scratch.
5. Apply the shared visual system: ivory/paper/slate/clay/oat/olive palette, serif/sans/mono type stack, 1.5px warm-gray borders, 8-14px panel radii, and inline SVG diagrams.
6. Prefer semantic HTML and native browser behavior: `<details>`, `<summary>`, tables, forms, range inputs, checkboxes, anchors, sticky nav, and inline SVG.
7. Keep interactions functional: navigation, comparison, filtering, drag/drop, copy/export, collapse/expand, tabs, or small stateful demos.
8. Verify the result visually at desktop and mobile widths when building a page, including wrapped toolbar/tab states and diagram legibility.

## Core Rules

- Make the artifact feel like a carefully typeset engineering memo that happens to be interactive.
- Use serif headings for narrative hierarchy, system sans for body/UI, and monospace for file paths, labels, tokens, counters, code, and metadata.
- Use clay sparingly for emphasis, selected states, attention, links, hot paths, and important chart marks.
- Use olive for success/safe/completed states; use rust/clay for danger or attention.
- Use inline SVG diagrams and schematic thumbnails instead of generic stock imagery or icon libraries; for real diagrams, apply the diagram grammar reference or copy from `assets/diagram-templates.html` instead of ad hoc boxes and arrows.
- Keep SVG fills, strokes, labels, markers, and masks token-driven through CSS classes; avoid hard-coded `fill="#fff"` / `stroke="#D1CFC5"` style literals in production artifacts because they break dark mode and palette consistency.
- Put wide SVGs inside a local `.diagram-shell` with `overflow-x: auto`; never let an SVG widen the whole page on mobile.
- For SVG arrows, define markers with `markerUnits="userSpaceOnUse"` so arrowheads stay consistent across normal, dashed, and hot-path strokes.
- For SVG connectors, stop arrow endpoints before the target node border with 6-10px clearance; if using an explicit orthogonal landing segment, keep it micro, usually 6-10px, so it does not dominate the curve.
- For SVG arrow and boundary labels, use paper-filled masks with warm-gray borders and darker text; labels should never disappear into oat-tinted regions or pale backgrounds.
- For Chinese or bilingual artifacts, use the CJK typography rules in `references/design-style.md`: Chinese quotes `「」`, spaces between Chinese and English/number/code terms, and CJK font stacks.
- For long Chinese or bilingual hero titles, manually control line breaks with title-line spans or equivalent responsive markup; do not rely on browser auto-wrapping to choose polished CJK breaks.
- For any control group that may wrap, such as tabs, segmented controls, toolbar actions, or role filters, use the wrapped-control rules in `references/design-style.md`: panel-radius outer shell, inner control focus rings, no oversized pill container. Page-level nav/tool rails should span their layout column with `display: flex; width: 100%`; inline filters may stay content-width.
- Default control states must look interactive before hover. Navigation links, tabs, segmented controls, toolbar buttons, and filter chips need a visible paper/gray fill, border, or equivalent affordance; hover/focus can strengthen the cue but must not be the only signal that an item is clickable.
- For long paths, file names, URLs, API names, code headers, tab labels, and mixed Chinese/English paragraphs, use the long-token rules in `references/design-style.md`: `min-width: 0`, `overflow-wrap: anywhere`, and local scroll shells where appropriate.
- Do not let the whole page become horizontally scrollable. Only deliberate local surfaces such as code blocks, wide tables, and SVG diagram shells should scroll horizontally.
- For sliders, meters, toggles, and live controls with labels or status chips, use explicit control-stack spacing from `references/design-style.md`; never rely on incidental margins from generic `.chips`.
- For page-level sections that place a callout, intro panel, table, diagram, metric grid, or card grid next to another block, use section-body spacing from `references/design-style.md`; a child grid's `gap` does not create spacing above that grid.
- For panels that mix headings, metadata, dividers, callouts, tables, code blocks, and chip rows, use content-stack spacing from `references/design-style.md`; adjacent blocks should never touch or visually share borders.
- Reset browser default margins on semantic containers used as panels or grid items, especially `<figure class="panel">`; `.panel` and `.card` should set `margin: 0` so blocks align to the layout grid.
- For mixed rows such as file path + badge + explanation, use adaptive-info-row rules from `references/design-style.md`; never let machine text squeeze prose into one-character-per-line columns.
- For copy/export buttons, handle clipboard denial gracefully with a visible fallback such as selecting the target text; the button should still leave a useful state behind.
- Make each page skimmable: the user should see intent, structure, and next action within a few seconds.
- Include `@media (prefers-color-scheme: dark)` token overrides in every artifact for automatic dark mode support.
- Include `@media print` styles that hide interactive controls, force white background, and avoid break-inside on cards/panels.
- Wrap all non-essential animations in `@media (prefers-reduced-motion: no-preference)` or add a blanket reduce block.
- Add `.sr-only` utility for screen-reader-only labels on icon buttons and status dots.

## Common Pitfalls

Avoid these recurring mistakes:

| ❌ Don't | ✓ Do |
|----------|------|
| Put wrapping tabs in a `border-radius: 999px` pill | Use `16px` panel-radius outer shell |
| Let wrapped tabs keep content-sized buttons on mobile | Give tab buttons a responsive `flex-basis`, `min-width: 0`, and a stacked mobile fallback |
| Let page-level nav tabs shrink to content width | Use a full-width rail: `.nav-wrap .tabs { display: flex; width: 100%; }` |
| Make default nav/tab buttons transparent and rely on hover | Give every clickable item a default paper fill or warm-gray border |
| Use mono font for Chinese labels/badges | Use sans for Chinese text, mono only for machine values |
| Trust browser CJK wrapping for long hero titles | Compose deliberate title lines and adjust them at mobile widths |
| Let a long path or bilingual sentence widen the page | Set `min-width: 0`, `overflow-wrap: anywhere`, and keep overflow local |
| Keep `p { max-width: 42em }` on a 1100px+ wide layout | Set `p { max-width: none }` for dashboards/reports; scope `42em` to prose-only sections |
| Let a top-level callout touch a following metric/card/table grid | Wrap section contents in `.section-body` or add scoped sibling spacing |
| Let callout touch chips/code below without gap | Wrap in `.content-stack` with `gap: 14px` |
| Use `<figure class="panel">` without margin reset | Add `.panel { margin: 0; }` or `figure.panel { margin: 0; }` |
| Use `--clay` for every accent | Reserve clay for attention; use olive for success, gray for neutral |
| Force three rigid columns in info rows | Use adaptive grid with `minmax` and container queries |
| Hard-code SVG hex colors in diagram nodes and arrows | Use classed SVG primitives backed by CSS variables |
| Let a wide SVG determine `body` width on mobile | Wrap it in `.diagram-shell` with local horizontal scrolling |
| Let hot-path SVG arrows have larger heads than normal arrows | Set `markerUnits="userSpaceOnUse"` on arrow markers |
| Let target node fills cover SVG arrowheads | End connectors 6-10px before the target node border |
| Make hard landing segments long enough to read as elbows | Keep landing segments micro, usually 6-10px |
| Let SVG labels blend into pale diagram regions | Give label masks paper fill, warm border, and gray-700/slate text |
| Add icon libraries or emoji decoration | Draw simple SVG or use text glyphs (`→`, `›`, `+`) |
| Put heavy box-shadow on static elements | Only use `--shadow-lift` on hover or floating panels |
| Forget `:focus-visible` on interactive elements | Every button, tab, link needs a visible focus ring |
| Show only `Copy failed` when clipboard is denied | Fall back to selecting the target text and show a useful state |
| Skip `prefers-reduced-motion` | Wrap transitions in motion-safe media query |
| Use cool blue-gray tones | Keep all grays warm (no blue cast) |

## Verification Checklist

Before delivering an artifact, verify:

- [ ] Colors use only design tokens (ivory/paper/slate/clay/oat/olive/rust/info/grays)
- [ ] Headings use serif, body uses sans, paths/code/metrics use mono
- [ ] Chinese text uses sans (not mono); Chinese quotes use `「」`
- [ ] Spaces between Chinese and English/number/code terms
- [ ] Tabs/segmented controls use panel-radius wrapper (no 999px pill for wrapping groups)
- [ ] Page-level nav/tool rails visibly span their intended grid column or full content width
- [ ] Navigation, tabs, toolbar actions, and filter controls look clickable in their default state, without relying on hover
- [ ] Semantic panel containers such as `figure.panel` align with sibling grid items because default margins are reset
- [ ] Adjacent top-level callouts, metric grids, card grids, tables, diagrams, and panels have explicit section spacing and never touch border-to-border
- [ ] On wide layouts (1100px+), paragraphs fill the container width — no `42em` cap creating visual gaps next to full-width tables/charts
- [ ] All interactive elements have `:focus-visible` styles
- [ ] `prefers-reduced-motion` disables non-essential animations
- [ ] Content renders correctly at 360px, 768px, and 1200px widths
- [ ] Wrapped controls don't overflow their container on narrow screens
- [ ] Long titles, paths, URLs, tab labels, and code headers do not create whole-page horizontal overflow
- [ ] Only intentional local surfaces such as code blocks, wide tables, and SVG diagram shells scroll horizontally
- [ ] Copy buttons show success state (olive "Copied" or a clear selected-text fallback)
- [ ] SVG diagrams are inline (no external image dependencies)
- [ ] SVG diagrams use tokenized CSS classes for fills/strokes/text/markers, not hard-coded light-mode hex colors
- [ ] SVG diagrams include useful `<title>`, `<desc>`, or adjacent HTML text for critical facts
- [ ] SVG arrowheads stay visually consistent across normal, dashed, and hot-path strokes
- [ ] SVG arrowheads are not clipped, hidden, or covered by target node fills/borders
- [ ] Explicit SVG landing segments are short enough that the curve still feels graceful
- [ ] SVG arrow labels and boundary labels have bordered masks with enough contrast against the diagram ground
- [ ] Diagram type fits the data, stays under budget, and uses only 1-2 focal accents
- [ ] Page is skimmable: intent visible in 5 seconds
- [ ] Print styles hide interactive controls and preserve readability

## Resources

- `references/design-style.md`: Full design system — tokens, typography, layout, components, accessibility, motion, dark mode, print styles, and all page patterns.
- `references/diagram-grammar.md`: Diagram selection, complexity budgets, SVG primitives, type recipes, annotation rules, and diagram taste gate.
- `assets/starter.html`: Generic self-contained HTML starter.
- `assets/starter-review.html`: Code Review starter with PR header, risk map, and file cards.
- `assets/starter-arch.html`: Architecture starter with SVG diagram and key files.
- `assets/starter-research.html`: Technical Research starter with candidate cards and criteria matrix.
- `assets/diagram-templates.html`: Tokenized SVG skeletons for architecture, sequence, and timeline diagrams.
