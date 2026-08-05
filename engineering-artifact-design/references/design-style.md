# Engineering Artifact Design Reference

Source analyzed: https://thariqs.github.io/html-effectiveness/ and its 20 linked demo pages.

## Quick Use

1. Pick the closest row in `Pattern Selector`.
2. Read the matching pattern section.
3. Use the foundations sections only as needed: `Design Tokens`, `Typography`, `Layout`, `Components`, `Imagery And Icons`, and `Motion And Interaction`.
4. For a new standalone HTML artifact, start from `assets/starter.html` and replace the content with the chosen pattern.

## Pattern Selector

| User intent | Pattern section | Layout and controls |
| --- | --- | --- |
| Gallery of examples or generated artifacts | `Index / Gallery` | Masthead, grouped card grid, pill table-of-contents |
| PR review, code review, module review | `Code Review & Understanding` | PR header, risk map, file cards, annotated diffs, checklist |
| Explain system structure or repo architecture | `Architecture Understanding` | Map-plus-detail, key files, boundaries, risk overlays |
| Explain a technical concept | `Technical Concept Understanding` | Two-column explainer, visual model, sliders/tabs/glossary |
| Research a technology, library, vendor, or engineering approach | `Technical Research / Evaluation` | Landscape map, candidate cards, criteria matrix, evidence board |
| Explain a workflow or mechanism | `Process / Mechanism Understanding` | Timeline, flowchart, state machine, swimlanes, runbook |
| Debug a production issue or regression | `Incident / Debug Investigation` | Timeline plus evidence board, hypothesis filters |
| Compare options and record a decision | `ADR / Technical Decision` | Option cards, trade-off matrix, decision band |
| Plan a migration or refactor | `Migration / Refactor Plan` | Before/after diagrams, phase stepper, risk heatmap |
| Document an API, event, schema, or contract | `API / Data Contract` | Request/response tabs, schema matrix, version diff |
| Show dependencies, ownership, or change radius | `Dependency / Ownership Map` | Ownership swimlanes, graph/table linking, risk overlay |
| Analyze latency, throughput, memory, query, or queue bottlenecks | `Performance Analysis` | Hot-path diagram, metric tabs, before/after cards |
| Explain auth, roles, permissions, tenant isolation, or secrets | `Security / Permission Model` | Role/resource matrix, trust-boundary map, failure paths |
| Plan test coverage or QA strategy | `Test Strategy / Coverage Map` | Coverage matrix, critical-path strip, gap filters |
| Plan a launch, flag ramp, or risky deploy | `Release / Rollout Plan` | Ramp timeline, guardrail metrics, rollback checklist |
| Help someone learn a repo/subsystem | `Onboarding / Codebase Tour` | Repo map, task-path selector, glossary rail |
| Break down requirements or audit AI-produced work | `Requirement / AI Work Audit` | Requirement board, risk map, evidence/checklist |
| Build a small direct-manipulation utility | `Tool / Editor` | Sticky toolbar, dense panels, filters, copy/export |

## Style Summary

This style is a warm, editorial, browser-native artifact system: it feels like a carefully typeset engineering memo that has grown interactive controls, diagrams, and small tools. The core mood is calm, readable, and craft-forward rather than glossy or app-like. It should look hand-authored, self-contained, and useful.

Use this style for explorable documents, technical research, design references, PR reviews, research explainers, implementation plans, status reports, and small throwaway editors.

## Design Tokens

Use these tokens as the default palette:

```css
:root {
  --ivory: #FAF9F5;
  --paper: #FFFFFF;
  --slate: #141413;
  --clay: #D97757;
  --clay-d: #B85C3E;
  --oat: #E3DACC;
  --olive: #788C5D;
  --rust: #B04A3F;
  --info: #5C7CA3;

  --gray-100: #F0EEE6;
  --gray-300: #D1CFC5;
  --gray-500: #87867F;
  --gray-700: #3D3D3A;

  --serif-latin: ui-serif, Georgia, "Times New Roman", Times, serif;
  --serif-cjk: "Songti SC", "Noto Serif CJK SC", "Source Han Serif SC", "SimSun", serif;
  --sans-latin: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --sans-cjk: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
  --serif: var(--serif-latin), var(--serif-cjk);
  --sans: var(--sans-latin), var(--sans-cjk);

  --border: 1.5px solid var(--gray-300);
  --radius-row: 8px;
  --radius-panel: 12px;
  --shadow-lift: 0 10px 30px rgba(20, 20, 19, 0.10);
}
```

Color roles:

- `--ivory`: page background, always warm off-white.
- `--paper`: main panels, cards, tables, controls.
- `--slate`: primary text, dark buttons, strong outlines.
- `--clay`: main accent for links, emphasis, selected state, warning attention, charts.
- `--oat`: quiet fill, secondary panels, neutral highlighted regions.
- `--olive`: success/completed/safe state.
- `--rust`: danger/regression/high-risk state.
- Grays are warm, not blue. Avoid cool slate UI themes.

## Typography

Use a three-family system:

- Serif for titles and section headings: Georgia-style Latin plus Songti/Noto Serif CJK for Chinese.
- System sans for body copy and interface text: system Latin plus PingFang/Microsoft YaHei/Noto Sans CJK for Chinese.
- Monospace for code, file paths, API names, tokens, counters, and metrics. Do not force Chinese prose or Chinese labels into monospace.

Recommended scale:

```css
body {
  background: var(--ivory);
  color: var(--gray-700);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

h1 {
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(38px, 5.4vw, 62px);
  line-height: 1.06;
  letter-spacing: -0.018em;
  color: var(--slate);
}

h2 {
  font-family: var(--serif);
  font-weight: 500;
  font-size: 21px;
  line-height: 1.25;
  color: var(--slate);
}

.eyebrow,
.meta,
.token {
  font-family: var(--sans);
}

code,
pre,
.path,
.metric {
  font-family: var(--mono);
}
```

The voice of the UI is concise and concrete. Use labels like `birchline/web · Pull Request #247`, `3 demos`, `Copy as markdown`, `worth a look`. Prefer practical nouns over marketing copy.

### Chinese / Bilingual Typography

Use this when the artifact contains Chinese or mixed Chinese/English text.

Font rules:

- Use `--sans` for Chinese body text, chips, badges, controls, and most labels.
- Use `--serif` for Chinese headings when you want the editorial/report feeling; avoid using Songti for dense body paragraphs.
- Use `--mono` only for code, paths, endpoints, identifiers, metrics, and short machine-readable values such as `p95`, `POST /v1/events`, `src/api/tasks.ts`.
- If a chip/badge is Chinese, keep it sans: `需要关注`, `已验证`, `待确认`. Use mono only for technical chips like `p95 latency` or `GET /tasks`.

Chinese layout defaults:

```css
:lang(zh) body,
body.zh {
  font-size: 15.5px;
  line-height: 1.75;
}

:lang(zh) h1,
body.zh h1 {
  line-height: 1.16;
  letter-spacing: 0;
}

:lang(zh) p,
body.zh p {
  max-width: 42em;
}
```

Chinese punctuation and spacing rules:

- Use Chinese corner quotes `「」` for quoted Chinese terms, UI labels, and concept names. Example: `点击「复制调研摘要」导出结论。`
- Use nested quotes as `『』` inside `「」` when needed.
- Keep a space between Chinese and English/number/code terms. Example: `在 API gateway 中检查 p95 latency。`
- Keep spaces around inline code in Chinese sentences. Example: 查看 `src/api/tasks.ts` 中的重试逻辑。
- Do not add letter spacing to Chinese body text. Use uppercase mono eyebrow sparingly; for Chinese eyebrow labels, prefer sans with normal letter spacing.
- Do not use straight English quotes `"..."` for Chinese copy unless quoting code or raw logs.

## Layout

The default page is a centered single document:

- Max width: `920px` for prose/review pages.
- Max width: `1100px` to `1180px` for indexes, boards, matrices, and dashboards.
- Outer padding: `48px 24px 80px`; larger index pages can use `80px 32px 140px`.
- Sections are separated by generous vertical whitespace, usually `40px` to `72px`.
- Use thin dividers: `1px` or `1.5px` warm gray.

Common page structures:

- Editorial index: masthead plus grouped card grid.
- Document with sidebar: `grid-template-columns: 200px minmax(0, 1fr)` with sticky nav.
- Tool/editor: header, sticky toolbar, then dense grid or split panes.
- Comparison page: 2 or 3 equal columns that collapse to one column below tablet widths.

Responsive behavior:

- Collapse multi-column grids to one column around `880px` to `960px`.
- Hide sticky side nav on narrow screens.
- Preserve generous spacing and readable line length instead of squeezing content.
- Keep whole-page horizontal overflow at zero. Use local scroll shells for wide code, tables, and diagrams instead of letting a child widen `body`.

Paragraph max-width by layout tier:

- For `920px` prose/review pages, keep `p { max-width: 720px; }` (CJK: `42em`) for comfortable reading line length.
- For `1100px`+ wide layouts (dashboards, reports, matrices, indexes), set `p { max-width: none; }` so paragraphs fill the same width as sibling tables, charts, and panels. A narrow paragraph next to a full-width table creates a visual gap that feels broken rather than intentional.
- If you want to limit line length on a wide page for specific prose-heavy sections, scope the constraint to those sections (e.g. `.prose-section p { max-width: 42em; }`) rather than applying it globally.

### Long Titles And Overflow Boundaries

Use this whenever a page has CJK/bilingual hero titles, long file paths, URLs, API names, wide tabs, or code headers.

The common failure mode is trusting browser auto-wrapping: Chinese title phrases break at awkward points, a long path widens the page, or tabs/code headers force the whole viewport to scroll sideways. Compose intended title lines and make every nested layout item allowed to shrink.

Rules:

- For long Chinese or bilingual H1s, manually compose title lines with spans such as `.title-line`; add mobile-specific line breaks when a phrase is still too long at `360px`.
- Set `min-width: 0` on grid/flex children that contain prose, code headers, tabs, info rows, or panels.
- Set `overflow-wrap: anywhere` on paragraphs and machine-text surfaces that may contain paths, URLs, long identifiers, or mixed Chinese/English text.
- Do not apply page-level horizontal scrolling as a fix. Keep `pre`, `.table-wrap`, and `.diagram-shell` as the only intentional horizontal scroll surfaces.
- If using a max-width page shell on very narrow mobile, make sure the shell is left-aligned or fits `calc(100% - padding)` exactly; avoid a centered shell that is wider than the visual viewport.

Recommended CSS:

```css
.page,
.main-flow,
section,
.panel,
.card,
.tab-panel {
  min-width: 0;
}

p,
.path,
.machine,
.code-head .path {
  overflow-wrap: anywhere;
}

.title-line {
  display: block;
}

@media (max-width: 620px) {
  .mobile-line {
    display: block;
  }
}

pre,
.table-wrap,
.diagram-shell {
  max-width: 100%;
  overflow-x: auto;
}
```

### Semantic Panel Reset

Use this whenever semantic HTML elements become cards, panels, figures, or grid items.

The common failure mode is `<figure class="panel">` inheriting the browser default `margin: 1em 40px`, which pushes the left card inward, lowers its top edge, and makes sibling panel gaps look inconsistent. Component classes should own their spacing; browser defaults should not participate in the layout grid.

Rules:

- Set `margin: 0` on shared panel/card primitives.
- If a standalone `<figure>` is used inside a grid or split pane, reset it explicitly before adding panel styling.
- Keep vertical rhythm in `.content-stack` or section spacing, not in native element margins.
- Recheck split panes where the left item is a `figure` and the right item is an `aside`; their outer borders should share the same top baseline.

Recommended CSS:

```css
.panel,
.card,
figure.panel,
figure.card {
  margin: 0;
}
```

### Section Body Rhythm

Use this for page-level sections that place a section header above several content blocks: callouts, metric grids, card grids, tables, diagrams, details, and panels.

The common failure mode is a bordered callout visually touching the following grid because the grid's own `gap` only separates its children. Section rhythm should be owned by the section body, not by incidental margins on the components.

Rules:

- Prefer wrapping the content area after the section heading in `.section-body` with `display: grid` and `gap: 16px` to `22px`.
- Reset direct child vertical margins inside `.section-body` so native heading, paragraph, figure, table, and details margins do not collapse or double-count.
- If a section is not wrapped, add scoped sibling spacing between direct section children such as a callout followed by a metric grid, card grid, table wrapper, diagram panel, or panel.
- Do not add global bottom margin to `.callout`, `.panel`, `.card`, or `.table-wrap`; those primitives may be used inside tighter stacks where the parent already controls spacing.
- Keep the section body gap at least as large as the internal grid gap when two bordered surfaces are adjacent, usually `18px`.

Recommended CSS:

```css
.section-body {
  display: grid;
  gap: 18px;
}

.section-body > * {
  margin-block: 0;
}

section > .callout + :is(.grid, .metric-grid, .card-grid, .table-wrap, .diagram-panel, .panel, details) {
  margin-top: 18px;
}
```

### Content Stacks

Use this inside panels or cards that mix different block types: headings, metadata rows, dividers, callouts, risk maps, chip rows, tables, code blocks, and checklists.

The common failure mode is a bordered callout touching a chip row, or a divider and following component visually sharing an edge. Do not rely on each child component's incidental margin; the parent stack should own the rhythm.

Rules:

- Wrap heterogeneous panel contents in `.content-stack` with `display: grid` and `gap: 12px` to `16px`.
- Reset direct child vertical margins so headings, paragraphs, dividers, callouts, and chip rows do not double-count or collapse margins.
- Give dividers a small explicit vertical allowance such as `margin: 4px 0`.
- Use `.content-stack` for PR headers, review summaries, research readouts, incident symptom bands, ADR decision bands, and any panel where a callout is followed by chips or action rows.

Recommended CSS:

```css
.content-stack {
  display: grid;
  gap: 14px;
}

.content-stack > * {
  margin-block: 0;
}

.content-stack > .divider {
  margin: 4px 0;
}
```

### Adaptive Info Rows

Use this for mixed-content rows such as key files, API fields, changed files, owners, dependencies, glossary terms, review focus items, and any `machine text + badge + prose explanation` pattern.

The common failure mode is treating these as a rigid three-column table: a long file path or endpoint consumes width, badges take their own column, and Chinese prose is squeezed into one or two characters per line. These rows are not true matrices; they should adapt before prose becomes unreadable.

Rules:

- Prefer list rows over tables unless users need to compare the same fields across many rows.
- Give the prose/explanation column a real minimum width, usually `minmax(16em, 1fr)` or wider.
- Let machine text absorb wrapping pressure: set path/API cells to `min-width: 0` and `overflow-wrap: anywhere`; insert `<wbr>` in very long paths when useful.
- Keep badges inline with the machine text on medium/narrow layouts instead of preserving a dedicated badge column at all costs.
- When the row container is too narrow, switch to `path + badge` on the first line and prose on the next line; on very narrow cards, stack all pieces vertically.
- Use container queries when possible because the relevant width is the card or panel, not the viewport.

Recommended CSS:

```css
.adaptive-info-list {
  display: grid;
  container-type: inline-size;
}

.info-row {
  display: grid;
  grid-template-columns: minmax(180px, 1.1fr) auto minmax(16em, 1.4fr);
  gap: 8px 14px;
  align-items: start;
  padding: 10px 0;
  border-bottom: 1px solid var(--gray-100);
}

.info-row:last-child {
  border-bottom: 0;
}

.info-row .path,
.info-row .machine {
  min-width: 0;
  overflow-wrap: anywhere;
}

.info-row .desc {
  min-width: 16em;
}

@container (max-width: 620px) {
  .info-row {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .info-row .desc {
    grid-column: 1 / -1;
    min-width: 0;
  }
}

@media (max-width: 720px) {
  .info-row {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .info-row .desc {
    grid-column: 1 / -1;
    min-width: 0;
  }
}
```

## Components

### Eyebrow

Small uppercase mono label, gray text, often with a clay accent line or chevron.

```css
.eyebrow {
  font-family: var(--mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-500);
}
```

On landing/index pages, add a `24px` clay line before the label.

### Cards

Cards are paper panels with warm gray borders and restrained rounding.

- Border: `1.5px solid var(--gray-300)`.
- Radius: `10px` to `14px`.
- Background: `var(--paper)`.
- Hover: lift by `translateY(-2px/-3px)`, darken border to slate, add a soft shadow.
- Content order: visual thumbnail, serif title, compact body, mono file/path footer.

Cards should feel like document tiles, not glossy product cards.

### Pills, Chips, Badges

Use pills for category nav, counts, filters, and status tags.

- Shape: `border-radius: 999px` for individual high-level pills that stay on one line.
- Shape: `6px` to `8px` radius for file/risk chips.
- Mono font at `11px` to `12.5px`.
- Default fill: paper or gray-100.
- Active/attention fill: transparent clay tint, oat, or olive tint.
- Do not put wrapping tabs, segmented controls, or multi-row toolbar actions inside a `999px` pill container. When a control group can wrap, use the `Wrapped Control Groups` pattern below.

### Buttons

Buttons are simple and textual.

- Primary tool actions can be black/slate pills with ivory text.
- Secondary buttons are transparent or paper with gray border.
- Buttons that sit inside navigation, tabs, segmented controls, toolbar groups, or filter rails must advertise clickability in the default state with a visible border, paper fill, or gray-100 fill. Do not rely on hover alone to reveal that text is interactive.
- Use mono text for utility actions.
- Hover changes background or border only; avoid loud color sweeps.
- Copied/success state turns olive.

```css
button.primary {
  background: var(--slate);
  color: var(--ivory);
  border: 1.5px solid var(--slate);
  border-radius: 999px;
  font-family: var(--mono);
  font-size: 12px;
  padding: 9px 16px;
}
```

### Tables And Lists

Tables use paper backgrounds, separated warm-gray rows, mono headers, and subtle row hover. Lists often avoid default bullets and use small square/dot markers in gray, clay, or olive.

### Code And Diffs

Inline code uses a warm gray pill background and mono font. Code panels can invert to slate with ivory text. Diff additions use olive tints; deletions use clay/rust tints and optional strikethrough.

Code panel chrome should not be the reason a mobile page overflows. Put long file paths or labels in a header row that can wrap, and keep horizontal scrolling inside the code body.

Recommended additions:

```css
.code-card {
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
}

.code-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.code-head .path {
  min-width: 0;
  overflow-wrap: anywhere;
}

pre {
  max-width: 100%;
  overflow-x: auto;
}
```

### Details / Accordions

Use native `<details>` / `<summary>` heavily. Hide default markers and provide a small clay chevron or plus/minus indicator. Keep the summary row paper/gray and the body plain.

### Forms And Controls

Use native controls styled lightly:

- Range sliders with clay accent.
- Segmented radio controls with paper labels and selected slate/clay border.
- Checkboxes with 5px radius and olive/clay selected states.
- Inputs are paper, `1.5px` border, `8px` radius, focus ring `rgba(217,119,87,0.15)`.

### Control Stacks

Use this for sliders, meters, toggles, live numeric controls, guardrail labels, chart legends, and any `control + value + status chips` cluster.

The common failure mode is placing a range input, progress meter, and chip labels back-to-back so labels visually touch the slider or meter. Do not rely on a generic `.chips { margin-top: ... }` to create the rhythm; the component should own its spacing.

Rules:

- Wrap the whole control cluster in `.control-stack` with `display: grid` and `gap: 12px` to `16px`.
- Reset incidental margins inside the stack: paragraphs, meters, and `.chips` should use `margin: 0`.
- Put the value label above or beside the slider using a dedicated row such as `.range-wrap`; give that row its own horizontal gap.
- Put guardrail/status chips at least `14px` below the slider or meter. If there is both a range input and a meter, chips belong after the meter.
- On narrow cards, allow chips to wrap, but keep the vertical gap between the meter and the first chip clear.

Recommended CSS:

```css
.control-stack {
  display: grid;
  gap: 14px;
}

.control-stack > p,
.control-stack .meter,
.control-stack .chips {
  margin: 0;
}

.control-stack .chips {
  padding-top: 2px;
}

.range-wrap {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
}
```

### Wrapped Control Groups

Use this for tabs, segmented controls, role filters, toolbar action groups, and any row of buttons that may wrap on narrow screens or inside a constrained column.

The common failure mode is an oversized `999px` outer pill with children wrapping into a second row; selected buttons or focus rings then overlap the outer rounded background. Treat the outer shell as a small panel, not a pill.

Rules:

- Outer wrapper: `inline-flex`, `flex-wrap: wrap`, `align-items: center`, `gap: 4px` to `6px`, `padding: 4px`, `border: var(--border)`, `background: var(--gray-100)`, `border-radius: 14px` to `16px`, and `max-width: 100%`.
- Width semantics depend on placement: inline filters and local segmented controls may shrink to content width; page-level nav bars, sticky rails, and toolbar rails should use `display: flex` with `width: 100%` so the visible background spans the intended grid column or full content width.
- Inner controls: `border-radius: 10px` to `12px`, stable `min-height` around `32px` to `36px`, compact horizontal padding, `min-width: 0`, and a responsive `flex-basis` when labels may wrap.
- Default state: each inner control should already read as clickable, usually with `background: var(--paper)` and `border-color: var(--gray-300)`. If only the wrapper has a background and the inner controls are transparent, users cannot tell which labels are buttons until hover.
- For tab rows with medium/long labels, use `flex: 1 1 140px` to `160px`; on narrow mobile, stack controls with `flex-basis: 100%` or a deliberate two-column layout after checking the longest label.
- Selected state: stronger contrast than default, such as white fill, darker warm border, slate text, or a restrained clay border. Clay is optional for attention, not required for every active tab.
- Focus state: use an inset ring, such as `box-shadow: inset 0 0 0 2px rgba(92,124,163,.42)`, and remove the default outline. Focus rings should never extend outside the outer wrapper.
- Single-row controls may still look like segmented pills, but use the same panel-radius wrapper if the labels may wrap in Chinese, bilingual copy, or mobile widths.

Recommended CSS:

```css
.tabs,
.segmented {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  max-width: 100%;
  padding: 4px;
  border: var(--border);
  border-radius: 16px;
  background: var(--gray-100);
}

.tab,
.segment {
  flex: 1 1 150px;
  min-width: 0;
  border: 1.5px solid var(--gray-300);
  border-radius: 12px;
  background: var(--paper);
  color: var(--gray-700);
  min-height: 34px;
  padding: 8px 12px;
}

.tab:hover,
.segment:hover {
  border-color: var(--gray-500);
  background: #fff;
}

.tab:focus-visible,
.segment:focus-visible {
  outline: 0;
  box-shadow: inset 0 0 0 2px rgba(92,124,163,.42);
}

.tab[aria-selected="true"],
.segment[aria-pressed="true"],
.segment.active {
  background: #fff;
  border-color: var(--slate);
  color: var(--slate);
}

.nav-wrap .tabs,
.toolbar-rail .segmented {
  display: flex;
  width: 100%;
}

@media (max-width: 620px) {
  .tab,
  .segment {
    flex-basis: 100%;
  }
}
```

## Imagery And Icons

Prefer inline SVG diagrams and small schematic thumbnails over raster imagery.

For any diagram more complex than a tiny thumbnail, read `references/diagram-grammar.md` and choose one dominant grammar before drawing. This keeps architecture maps, timelines, sequence diagrams, state machines, ER diagrams, swimlanes, quadrants, trees, and ownership maps from collapsing into generic boxes and arrows.

Visual language:

- Thin black/warm-gray strokes.
- Rounded rectangles, lines, dots, small bars, flow arrows.
- Fill colors pulled only from the token palette.
- Prefer SVG classes styled with CSS variables over repeated inline hex values. Inline SVG should react to dark-mode token remapping without rewriting the SVG.
- Slight rotations for handmade document metaphors.
- Diagrams should clarify structure: flowcharts, rings, timelines, call graphs, charts, boards.
- Use a complexity budget: 5-9 nodes ideal, about 11 max; 1-2 clay focal elements; split overview and detail when the graph grows beyond that.
- Draw arrows before boxes so lines sit behind nodes.
- Define SVG arrow markers with `markerUnits="userSpaceOnUse"` so hot-path or thick strokes do not create oversized arrowheads.
- End SVG connectors 6-10px before target node borders so later-drawn node fills do not cover arrowhead tips.
- Keep any explicit orthogonal landing segment micro, usually 6-10px, so it stabilizes the arrowhead without becoming a visible elbow.
- Put bordered paper masks behind arrow labels and boundary labels so strokes do not run through text and labels remain distinct from oat-tinted regions.
- Keep legends outside the active diagram area, or replace legends with direct labels.
- Keep long prose outside the SVG; pair the diagram with HTML callouts, adaptive info rows, cards, or checklists.

Reusable SVG shell:

```css
.diagram-shell {
  overflow-x: auto;
  overflow-y: hidden;
}

.diagram-shell svg {
  display: block;
  min-width: 640px;
  max-width: 100%;
  height: auto;
}

.diagram-node {
  fill: var(--paper);
  stroke: var(--gray-300);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
}

.diagram-node.is-hot {
  stroke: var(--clay);
  stroke-width: 2;
}

.diagram-edge {
  fill: none;
  stroke: var(--gray-500);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
}

.diagram-edge.is-hot {
  stroke: var(--clay);
  stroke-width: 2;
}

.diagram-region {
  fill: var(--oat);
  opacity: .24;
  stroke: var(--gray-300);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
}

.diagram-mask {
  fill: var(--paper);
  stroke: var(--gray-300);
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.diagram-label {
  fill: var(--slate);
  font-family: var(--sans);
  font-size: 12px;
}

.diagram-label-mono {
  fill: var(--gray-700);
  font-family: var(--mono);
  font-size: 10px;
}

.diagram-arrow {
  fill: var(--gray-500);
}

.diagram-arrow.is-hot {
  fill: var(--clay);
}
```

Avoid generic icon libraries, photo backgrounds, gradients, emoji decoration, and highly detailed illustration. If an icon is needed, draw it as a simple geometric SVG or use text glyphs like `→`, `›`, `+`, `−`.

## Motion And Interaction

Motion is short, tactile, and functional:

- Hover cards: `150ms ease`, translate up a few pixels.
- Chips/buttons: `120ms ease`, minor border/background change.
- Accordions/chevrons: `120ms` to `150ms`.
- Micro-interactions may use staged timings: fill at `0ms`, check at `80ms`, strike at `120ms`, burst at `200ms`, settle/collapse around `600ms`.
- For playful completion states, use clay flash settling into olive.

Recommended easings:

```css
--ease-standard: cubic-bezier(.16, 1, .3, 1);
--ease-spring: cubic-bezier(.34, 1.56, .64, 1);
```

Interactions should leave useful state behind: copied buttons say `Copied`, selected tabs stay selected, drag targets show dashed clay outlines, filters produce visible pills.

Copy/export interactions should handle local-file and embedded-browser clipboard denial. If `navigator.clipboard.writeText` fails, fall back to a hidden textarea plus `document.execCommand("copy")`; if that also fails, select the target text and show a clear state such as `Selected` instead of leaving the user at `Copy failed`.

```js
async function copyTextOrSelect(target, button) {
  const text = target.innerText.trim();
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = "Copied";
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      button.textContent = "Copied";
    } catch {
      const range = document.createRange();
      range.selectNodeContents(target);
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(range);
      button.textContent = "Selected";
    } finally {
      document.body.removeChild(textarea);
    }
  }
}
```

## Reusable Page Patterns

### Index / Gallery

- Masthead with serif H1, italic clay word, mono eyebrow, short intro.
- Optional right-side schematic hero figure.
- Pill table-of-contents.
- Sections with mono index number, serif section title, count pill, short explanation.
- Cards in `repeat(auto-fill, minmax(316px, 1fr))`.

### Code Review & Understanding

This scene should turn invisible code structure into a spatial reading surface. The page is not a raw diff dump; it is a review cockpit where intent, risk, changed files, data flow, and reviewer actions are visible at once.

Core information hierarchy:

- Start with a paper PR header: repo/package line, PR number, serif title, author avatar, opened time, branch chip, and compact diff stats.
- Follow with a plain-language `What this does` section before showing code.
- Put a `Risk map` near the top as clickable chips so reviewers can jump to hot files.
- Show high-risk files expanded by default; collapse low-risk or supporting files with `<details>`.
- End with a `Review checklist`, `Test plan`, or `Where to focus` section that converts reading into action.

PR header pattern:

```html
<header class="pr-head">
  <div class="repo-line">birchline/web · Pull Request #247</div>
  <h1>Add optimistic updates to task list mutations</h1>
  <div class="meta-row">
    <div class="author"><span class="avatar">MO</span><div>Mira Okafor<br><small>opened 2 days ago</small></div></div>
    <div class="branch">mo/optimistic-tasks <span>→</span> main</div>
    <div class="stat"><span class="add">+142</span> / <span class="del">−38</span> <span>6 files changed</span></div>
  </div>
</header>
```

Use a bordered white panel for the header, not a dark app bar. The title stays editorial and calm; metadata stays mono and compact.

Risk map:

- Represent each changed file as a chip with a small colored dot.
- Olive means safe/covered, oat means worth a look, clay/rust means needs attention.
- Chips should link to file sections by anchor.
- Include a tiny legend directly underneath.
- Use file names, not generic labels: `useOptimisticTasks.ts`, `TaskList.tsx`, `api/tasks.ts`.

File review cards:

- Each file is a bordered paper card with a mono path header.
- Put diff stats on the right: `+54 / −12`.
- Use a small badge for risk or type: `hook`, `api`, `test`, `new`, `mod`.
- Keep code blocks inside the card; keep reviewer notes in a right margin or below the relevant hunk.
- Use warm tinted backgrounds for added/removed lines, but keep the code text readable.

Diff styling:

```css
.code {
  background: var(--slate);
  color: #E8E6DE;
  border-radius: 10px;
  font-family: var(--mono);
  font-size: 12.5px;
  line-height: 1.65;
}
.code .add { background: rgba(120,140,93,.22); }
.code .del {
  background: rgba(217,119,87,.18);
  text-decoration: line-through;
  text-decoration-color: rgba(217,119,87,.6);
}
.note.attention { border-left: 3px solid var(--clay); }
.note.safe { border-left: 3px solid var(--olive); }
```

Reviewer notes:

- Notes should be anchored to concrete lines or hunks: `line 18`, `mutation rollback`, `missing test`.
- Use short severity labels: `safe`, `worth a look`, `needs attention`.
- Notes are small paper/oat boxes, not modal comments.
- Use clay only for actual attention, not every annotation.

Understanding views:

- For module maps and architecture notes, lead with one paragraph that states the trust boundary or main data path.
- Render code structure as inline SVG boxes and arrows.
- Highlight the hot path in clay; safe dependencies can be olive or gray.
- Pair diagrams with `Key files` lists using mono paths and one-line responsibilities.
- Use two-column supporting grids for concepts like `entry points`, `state owners`, `external calls`, and `failure paths`.

Flow diagram styling:

- Boxes are rounded rectangles, white fill, gray border.
- The central or risky node uses clay fill/border or a clay outline.
- Arrows are warm gray with clay used only for the highlighted path.
- Labels inside boxes are sans/mono, never icon-heavy.
- Keep diagrams shallow and legible; prefer 5-8 nodes over exhaustive architecture maps.

Review action components:

- `Focus` cards: numbered circles in clay, title in slate, description in gray.
- `Checklist`: custom checkboxes with olive checked state.
- `Rollout` or `Verification` strips: horizontal steps on desktop, stacked cards on mobile.
- `Collapsed files`: native `<details>` rows with plus/minus or chevron indicators.

Interaction behavior:

- Risk chips scroll to the file card and briefly highlight it with a soft clay glow.
- Details chevrons rotate in `120ms` to `150ms`.
- Checklist items can be checked locally; no persistence is required.
- Hovering chips or file rows should lift at most `1px`; review pages should feel stable, not playful.

### Explainer / Research Page

- Sticky left nav.
- TL;DR callout with clay left border.
- Collapsible request-path sections.
- Tabbed code samples.
- FAQ or glossary in compact serif/sans mix.

### Architecture Understanding

Use this page type to explain how a software system is put together: modules, services, boundaries, data ownership, dependencies, runtime paths, and change-risk areas.

Information hierarchy:

- Header: system name, repo/package, scope, freshness/date, and one-line responsibility.
- `At a glance`: 3-5 compact facts such as entry points, data stores, external systems, critical path, and owner.
- Main architecture map: inline SVG with layered boxes and arrows.
- `Key files / modules`: mono paths paired with one-line responsibilities.
- `Runtime path`: a request/event/job path shown as a numbered flow.
- `Boundaries`: trust boundary, network boundary, persistence boundary, ownership boundary.
- `Risks`: hotspots, coupling, unclear ownership, failure modes, and observability gaps.

Architecture map styling:

- Use white rounded rectangles for internal modules.
- Use oat panels for groups/layers such as `client`, `api`, `worker`, `storage`.
- Use clay for the critical/hot path or risky boundary.
- Use olive for stable or well-tested paths.
- Use dashed gray lines for optional/background/asynchronous paths.
- Keep diagrams to 5-10 major nodes. If the real system is larger, group nodes into layers and explain details below.

Architecture-specific components:

- `Boundary band`: horizontal or vertical oat region labeling a layer or trust zone.
- `Key file row`: use `Adaptive Info Rows` for mono path, type badge (`route`, `store`, `worker`, `schema`), and one-line responsibility so prose is never squeezed by long paths.
- `Hot path strip`: numbered steps with input/output labels.
- `Risk chip`: short label plus severity dot, linking to the relevant module.
- `Decision note`: paper callout for why the architecture is shaped this way.
- Preferred layout: map-plus-detail, with the architecture graph on top or left and selected node details beside or below it.
- Useful controls: owner filters, risk overlays, async-path toggles, and click-linked highlighting between diagram nodes, key files, and risk rows.

### Technical Concept Understanding

Use this page type to teach an engineering concept such as consistent hashing, rate limiting, optimistic updates, retry/backoff, isolation levels, streaming, caching, sharding, queues, feature flags, or auth/session models.

Information hierarchy:

- Header: concept name and the practical problem it solves.
- TL;DR callout: one paragraph with the core mental model.
- Visual model: ring, pipeline, state chart, layered stack, table, or small simulation.
- Controls when useful: sliders, segmented controls, toggles, add/remove buttons.
- Comparison table: alternatives, trade-offs, failure modes, and selection criteria.
- Glossary: sticky sidebar or compact term cards.
- Applied example: concrete repo/service/file scenario showing the concept in context.

Concept visual rules:

- Prefer one dominant explanatory diagram rather than many small decorative figures.
- Use clay for the moving/current/selected thing.
- Use olive for successful or healthy states.
- Use rust/clay for overloaded, failed, or unsafe states.
- Pair every visual element with direct labels; avoid legend-only interpretation.
- If the concept has parameters, expose 1-3 controls and update the visual live.

Useful concept components:

- `Mental model` callout with a clay left border.
- `Try it` sandbox panel with native controls.
- `Trade-off table` with mono headers.
- `Glossary rail` that stays visible on wide screens.
- `Failure mode cards` with severity chips and mitigation notes.
- Preferred layout: two-column explainer with the main visual/demo plus a sticky glossary or controls rail.
- Useful controls: sliders for tunable parameters, segmented controls for alternatives, tabs for `Diagram / Code / Metrics`, and copy buttons for example configs or prompts.

### Technical Research / Evaluation

Use this page type for technology investigations, library/framework/vendor comparisons, build-vs-buy analysis, architecture option research, emerging-tool evaluation, and proof-of-concept summaries. The goal is to turn scattered sources and experiments into an evidence-backed recommendation, not just a list of links.

Information hierarchy:

- Header: research question, decision deadline, scope, target environment, and owner.
- Executive readout: recommended direction, confidence, major caveats, and next action.
- Landscape map: candidate technologies grouped by category, maturity, deployment model, or ecosystem fit.
- Evaluation criteria: weighted dimensions such as integration cost, maturity, performance, security, licensing, operational burden, community health, vendor lock-in, and migration risk.
- Candidate cards: one card per option with fit summary, strengths, risks, unknowns, and evidence quality.
- Evidence board: sources, benchmarks, PoC notes, issue trackers, docs, release cadence, and real-world adoption signals.
- Experiment notes: setup, workload, constraints, results, surprising findings, and reproducibility.
- Decision support: shortlist, disqualifiers, recommendation, fallback option, and unresolved questions.

Technical research visual rules:

- Use a landscape matrix when many options exist: axes like `maturity` vs `fit`, or `control` vs `operational cost`.
- Use candidate cards for 3-6 serious options; collapse rejected options in `<details>`.
- Use a weighted score table only when criteria are explicit; avoid fake precision.
- Show confidence and evidence quality separately from score.
- Mark unknowns visibly. Use clay for caveats and risk, olive for validated strengths, and gray for unverified claims.
- Include source dates when information may age quickly.

Research-specific components:

- `Research question` callout with clay left border.
- `Criteria matrix`: rows as criteria, columns as candidates, with short text and optional score chips.
- `Candidate card`: summary, fit badge, evidence quality, key pros/cons, links/source notes.
- `Evidence strip`: docs, benchmarks, GitHub/issues, community examples, internal PoC, production references.
- `PoC result panel`: workload, environment, metric, result, interpretation.
- `Unknowns board`: open questions, owner, how to resolve, decision impact.
- `Recommendation band`: chosen path, confidence, fallback, and first implementation slice.

Best layout and interactions: research dashboard plus comparison matrix; use criteria filters, weight sliders only when weights are real, source-type filters, candidate tabs, evidence-quality toggles, expandable rejected options, and copyable research brief or ADR seed.

### Process / Mechanism Understanding

Use this page type to explain workflows and mechanisms such as deploy pipelines, incident response, CI checks, auth handshakes, billing reconciliation, webhook delivery, background jobs, data sync, cache invalidation, or release rollout.

Information hierarchy:

- Header: process name, scope, trigger, and expected output.
- `Happy path`: horizontal flowchart, timeline, or state machine.
- `Decision points`: branches with conditions and ownership.
- `Retries / timeouts`: show timing, backoff, and stop conditions.
- `Failure paths`: clay/rust branches leading to fallback, dead-letter, rollback, or escalation.
- `Observability`: logs, metrics, traces, dashboards, or alerts tied to steps.
- `Operator actions`: checklist or runbook strip.

Mechanism diagram styling:

- Use numbered steps in mono labels.
- Use arrows for movement and dotted arrows for async or delayed work.
- Use clay for the currently risky/important branch.
- Use small paper code/log panels beside the exact step they explain.
- Use timelines for time-sensitive processes; use state machines for lifecycle processes; use swimlanes for handoffs across owners/systems.

Mechanism-specific components:

- `Step card`: number, title, owner/system, input, output.
- `Event/log panel`: mono block with the relevant event names and payload fields.
- `Metric chip`: `p95`, `error rate`, `queue depth`, `retry count`, `SLO`.
- `Failure branch`: rust/clay path with mitigation.
- `Runbook checklist`: concrete operator actions with custom checkboxes.
- Preferred layout: timeline for time-sensitive processes, state machine for lifecycle processes, swimlanes for handoffs, and stepper/runbook for operator actions.
- Useful controls: segmented `Happy path / Failure path` views, failure-path toggles, metric overlays, details rows for optional branches, and copyable runbooks.

### Incident / Debug Investigation

Use this page type for production incidents, difficult bugs, performance regressions, flaky tests, and unknown-cause investigations.

- Header: incident title, severity, impacted systems, time window, status.
- Symptom band: user-visible impact, detected by, first signal, current mitigation.
- Timeline: minute-by-minute events with logs, deploys, alerts, and decisions.
- Hypothesis board: active, ruled out, confirmed; each card has evidence links.
- Evidence panels: log excerpts, query results, graphs, traces, screenshots.
- Root cause: one plain-language statement plus the failing mechanism.
- Fix and follow-ups: shipped fix, verification, owners, due dates.

Best layout and interactions: timeline plus evidence board; filter timeline by signal type, click hypothesis cards to highlight related evidence, toggle `user impact / system events`, and copy the postmortem summary.

### ADR / Technical Decision

Use this page type when a team needs to compare technical options and record a decision.

- Header: decision title, status, date, owner, affected systems.
- Context: problem, constraints, non-goals, decision drivers.
- Option cards: each option has diagram, pros, cons, risks, cost.
- Trade-off matrix: rows are criteria, columns are options.
- Decision band: chosen option, why now, what would change the decision.
- Consequences: new constraints, migration work, monitoring needs.

Best layout and interactions: three-column option comparison plus matrix; use segmented controls for options, toggles for scoring criteria, expandable evidence, and copyable ADR markdown.

### Migration / Refactor Plan

Use this page type for framework upgrades, service splits, schema migrations, storage changes, and large refactors.

- Before/after architecture: two diagrams or a slider-like side-by-side.
- Phases: numbered milestones with entry/exit criteria.
- Compatibility layer: what bridges old and new behavior.
- Risk files: concrete paths, owners, test coverage, rollback difficulty.
- Validation: automated checks, manual QA, shadow traffic, metrics.
- Rollback: exact trigger, owner, and steps.

Best layout and interactions: before/after diagrams plus phase stepper; use phase filters, before/after toggles, risk heatmaps, validation checklists, and copyable implementation plans.

### API / Data Contract

Use this page type for REST/RPC APIs, event payloads, database schemas, webhooks, and cross-service contracts.

- Contract header: endpoint/topic/table, version, owner, consumers.
- Request/response or event examples in mono paper/code panels.
- Schema table: field, type, required, nullable, default, meaning.
- State and error map: status codes, retryability, owner, user impact.
- Compatibility notes: breaking changes, deprecated fields, migration timeline.
- Consumer impact: which callers break or need updates.

Best layout and interactions: contract tabs plus schema matrix; use request/response/error tabs, field search/filter, version diff toggles, and copyable JSON/schema blocks.

### Dependency / Ownership Map

Use this page type to show who owns what and how changes propagate.

- Ownership map: modules/services grouped by team or domain.
- Dependency graph: upstream/downstream arrows and coupling strength.
- Change radius: what gets touched by a proposed change.
- Escalation path: owners, reviewers, Slack/channel, on-call.
- Risk zones: circular dependencies, abandoned modules, single-owner areas.

Best layout and interactions: ownership swimlane or map-plus-detail; use owner filters, module search, hover-linked graph/table rows, and risk overlay toggles.

### Performance Analysis

Use this page type for latency, throughput, memory, CPU, rendering, query, or queue bottleneck investigations.

- Header: metric, baseline, regression window, target.
- Latency budget: stacked bar or step chart by component.
- Hot path: flame-like path or numbered request route.
- Before/after: metric cards and trend chart.
- Experiments: hypothesis, change, observed result, confidence.
- Recommendation: chosen optimization, expected gain, risk.

Best layout and interactions: hot-path diagram plus metrics board; use metric tabs, before/after toggles, percentile selectors, bottleneck highlights, and copyable findings.

### Security / Permission Model

Use this page type for auth, RBAC/ABAC, tenant isolation, secrets, audit logs, and data access reviews.

- Actors and roles: human/service identities and trust level.
- Permission matrix: resource by action by role.
- Trust boundaries: browser, API, worker, database, third-party systems.
- Sensitive data flow: where data enters, rests, leaves, and is logged.
- Threat notes: misuse paths, missing checks, audit gaps.
- Verification: tests, logs, alerts, manual review points.

Best layout and interactions: role/resource matrix plus trust-boundary map; use role selectors, permission filters, trust-boundary overlays, and failure-path toggles.

### Test Strategy / Coverage Map

Use this page type for test plans, review readiness, risk-based coverage, and QA strategy.

- Coverage map: modules/flows by unit, integration, e2e, manual.
- Critical paths: user or system paths that must not break.
- Mock/real boundary: what is simulated and what is exercised for real.
- Gaps: untested branches, flaky areas, missing fixtures.
- Acceptance checklist: concrete verification steps.

Best layout and interactions: coverage matrix plus critical-path strip; use layer toggles, gap filters, acceptance checklists, and copyable test plans.

### Release / Rollout Plan

Use this page type for feature launches, migrations, flag ramps, infrastructure changes, and risky deploys.

- Release header: feature/change, owner, flag, target date.
- Ramp plan: percentages, cohorts, dates, entry/exit gates.
- Guardrails: metrics, thresholds, dashboards, alerts.
- Stop conditions: what pauses or rolls back rollout.
- Rollback path: owner, command/process, expected recovery time.
- Comms: stakeholders and update cadence.

Best layout and interactions: rollout timeline plus guardrail dashboard; use rollout percentage sliders, guardrail status chips, stop-condition filters, checklists, and copyable release notes/runbooks.

### Onboarding / Codebase Tour

Use this page type to help someone understand a repo or subsystem quickly.

- Map: major folders/modules and responsibilities.
- First files to read: ordered path list with why each matters.
- Common task paths: add endpoint, debug job, add flag, run tests.
- Local workflow: commands, ports, fixtures, debugging tips.
- Glossary: product and codebase terms.
- Danger zones: fragile modules, generated files, migration traps.

Best layout and interactions: repo map plus task-path selector; use task selectors, file-path jump lists, collapsible commands, sticky glossary rails, and copyable onboarding checklists.

### Requirement / AI Work Audit

Use this page type to turn vague product-engineering work or AI-produced changes into reviewable structure.

- Requirement breakdown: goal, users, workflow, constraints, non-goals.
- System impact: touched modules, APIs, data, flags, tests.
- Slices: implementation phases with acceptance criteria.
- Open questions: owner, decision needed, deadline.
- AI work audit: what changed, why, evidence, risks, human review focus.

Best layout and interactions: requirement board or AI audit board; use status filters, risk chips, linked evidence highlights, acceptance checklists, and copyable prompts/summaries.

### Tool / Editor

- Compact header, sticky toolbar, live summary.
- Dense paper panels in a grid.
- Export/copy primary action.
- Direct manipulation states: drag opacity, dashed drop area, active filter chip, changed-state badges.

## Do / Do Not

Do:

- Keep the page self-contained in one HTML file when possible.
- Use real HTML controls and semantic elements.
- Let layout carry meaning through columns, tables, diagrams, tabs, and timelines.
- Test controls in their wrapped state; no selected button, focus ring, chip, or toolbar item should overlap its container.
- Make every artifact skimmable in 5 seconds and useful in 5 minutes.
- Use warm borders and paper panels to create hierarchy.

Do not:

- Use glossy gradients, blue-gray SaaS chrome, large decorative blobs, or stock images.
- Over-round everything; reserve full pills for filters/buttons, use 8px to 14px for panels.
- Put wrapping tabs or segmented controls inside a huge pill-shaped background.
- Use heavy shadows except on hover or emphasized floating documents.
- Add icon noise where mono labels or simple SVG marks work better.
- Let interactivity become ornamental; each interaction should support reading, comparing, editing, or exporting.

## Accessibility

All artifacts must be usable with keyboard-only navigation, screen readers, and meet WCAG 2.1 AA contrast requirements.

### Contrast Requirements

Minimum contrast ratios (WCAG AA):

| Element | Foreground | Background | Ratio | Status |
|---------|-----------|------------|-------|--------|
| Body text | `--gray-700` (#3D3D3A) | `--ivory` (#FAF9F5) | 7.2:1 | Pass |
| Body text | `--gray-700` (#3D3D3A) | `--paper` (#FFFFFF) | 7.8:1 | Pass |
| Muted text | `--gray-500` (#87867F) | `--ivory` (#FAF9F5) | 3.5:1 | Pass (large text only) |
| Muted text | `--gray-500` (#87867F) | `--paper` (#FFFFFF) | 3.8:1 | Pass (large text only) |
| Clay on paper | `--clay` (#D97757) | `--paper` (#FFFFFF) | 3.2:1 | Fail for small text |
| Slate on ivory | `--slate` (#141413) | `--ivory` (#FAF9F5) | 15.8:1 | Pass |

Rules:

- Never use `--gray-500` for body-sized text (below 18px). Use it only for eyebrow labels (11px uppercase = large text equivalent) or decorative labels.
- Never use `--clay` alone for small text on white. Pair with an underline, bold weight, icon/dot, or background tint to ensure meaning is not conveyed by color alone.
- Use `--clay-d` (#B85C3E) when clay text must pass AA on white at body size (4.0:1).
- All status dots/badges must pair color with a text label; never rely on color alone.

### Keyboard Navigation

- All interactive elements must be reachable via Tab key in logical order.
- Use `tabindex="0"` only on custom interactive elements; prefer native `<button>`, `<a>`, `<input>`, `<details>`.
- Arrow keys navigate within compound widgets (tabs, segmented controls, radio groups).
- Escape closes popover/modal and returns focus to trigger.
- Enter/Space activates the focused element.

Tab patterns:

```html
<!-- Tabs: roving tabindex -->
<div role="tablist">
  <button role="tab" aria-selected="true" tabindex="0">Tab 1</button>
  <button role="tab" aria-selected="false" tabindex="-1">Tab 2</button>
</div>
<div role="tabpanel" aria-labelledby="tab-1">...</div>
```

### ARIA Patterns

Required ARIA attributes by component:

| Component | Role | Required attrs |
|-----------|------|---------------|
| Tabs | `tablist`, `tab`, `tabpanel` | `aria-selected`, `aria-controls`, `aria-labelledby` |
| Accordion | native `<details>` | None needed (browser provides) |
| Modal/Dialog | `dialog` | `aria-labelledby`, `aria-modal="true"` |
| Toast | `status` or `alert` | `aria-live="polite"` or `aria-live="assertive"` |
| Progress meter | `progressbar` | `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-label` |
| Chips (filter) | `button` or `checkbox` | `aria-pressed` or `aria-checked` |
| SVG diagrams | `img` | `aria-label` with text description |

### Focus Styles

Every interactive element must show a visible focus indicator:

```css
:focus-visible {
  outline: 0;
  box-shadow: inset 0 0 0 2px rgba(92, 124, 163, .42);
}

a:focus-visible {
  outline: 2px solid rgba(92, 124, 163, .42);
  outline-offset: 2px;
  border-radius: 3px;
}
```

### Reduced Motion

Wrap all non-essential animations in a motion-safe query:

```css
@media (prefers-reduced-motion: no-preference) {
  .card {
    transition: transform 150ms var(--ease-standard),
                box-shadow 150ms var(--ease-standard);
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Screen Reader Utilities

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

Use `.sr-only` for icon-only buttons, status dots that need text labels for assistive tech, and SVG diagram context.

## Dark Mode

Support `prefers-color-scheme: dark` by remapping design tokens. The overall mood shifts from warm ivory to warm charcoal; hues and relationships remain the same.

### Dark Tokens

```css
@media (prefers-color-scheme: dark) {
  :root {
    --ivory: #1C1B19;
    --paper: #262523;
    --slate: #F5F4F0;
    --clay: #E8936F;
    --clay-d: #D97757;
    --oat: #3D3832;
    --olive: #8FA86E;
    --rust: #D4635A;
    --info: #7FA0C7;

    --gray-100: #2E2D2A;
    --gray-300: #4A4843;
    --gray-500: #9C9B94;
    --gray-700: #D9D8D2;

    --border: 1.5px solid var(--gray-300);
    --shadow-lift: 0 10px 30px rgba(0, 0, 0, .35);
  }
}
```

### Dark Mode Rules

- Keep the same semantic color roles: clay for attention, olive for success, rust for danger.
- Swap text/background relationships: `--slate` becomes foreground, `--ivory` becomes background.
- Code blocks stay dark (no change needed); their contrast improves in dark mode.
- Borders become subtler; reduce contrast between panel and background.
- Increase the opacity of tinted fills (olive/clay tints in diffs and badges) by ~10% to remain visible.
- Test SVG diagrams: strokes and fills may need `currentColor` or CSS custom property awareness.

### Toggle Implementation

For manual dark mode toggle (not just OS-level):

```css
[data-theme="dark"] {
  /* same token overrides as above */
}
```

```html
<button class="btn secondary" id="theme-toggle" type="button">
  Toggle dark mode
</button>
```

```js
document.getElementById("theme-toggle").addEventListener("click", function () {
  var root = document.documentElement;
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
});
```

## Print Styles

Engineering artifacts should print cleanly as reference documents. Hide interactive chrome; preserve content hierarchy.

```css
@media print {
  body {
    background: white;
    color: #1a1a1a;
    font-size: 12pt;
    line-height: 1.5;
  }

  .page {
    max-width: 100%;
    padding: 0;
  }

  /* Hide interactive elements */
  .tabs,
  .segmented,
  .btn,
  .btn-group,
  aside,
  [data-copy],
  input[type="range"],
  .chips .chip:hover {
    /* only hide truly interactive controls, not content chips */
  }

  .btn,
  .btn-group,
  input[type="range"],
  .tabs {
    display: none !important;
  }

  /* Preserve content */
  .card, .panel, .callout, details {
    break-inside: avoid;
    page-break-inside: avoid;
    border-color: #ccc;
    box-shadow: none;
  }

  .card:hover {
    transform: none;
    box-shadow: none;
  }

  details {
    /* Force open in print */
  }

  details[open] summary {
    border-bottom-color: #ccc;
  }

  /* Expand details for print */
  details:not([open]) > *:not(summary) {
    display: block !important;
  }

  a { color: inherit; text-decoration: underline; }
  a::after { content: " (" attr(href) ")"; font-size: 0.8em; color: #666; }
  a[href^="#"]::after { content: ""; }

  /* Code blocks */
  .code {
    background: #f5f5f5 !important;
    color: #1a1a1a !important;
    border: 1px solid #ccc;
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  /* Page breaks */
  h1, h2, h3 {
    page-break-after: avoid;
    break-after: avoid;
  }

  /* Sidebar becomes inline */
  .rail {
    grid-template-columns: 1fr;
  }

  aside {
    position: static;
    display: block;
    border: 1px solid #ccc;
    margin-top: 24px;
  }
}
```

## Motion Guidelines

Detailed timing reference for all animated elements:

| Element | Property | Duration | Easing | Trigger |
|---------|----------|----------|--------|---------|
| Card hover | transform, box-shadow | 150ms | ease-standard | mouseenter |
| Card unhover | transform, box-shadow | 120ms | ease | mouseleave |
| Tab switch | background, border-color | 120ms | ease | click |
| Button hover | background, border-color | 120ms | ease | mouseenter |
| Accordion chevron | transform (rotate) | 150ms | ease-standard | toggle |
| Details body | — (no animation, instant) | 0ms | — | toggle |
| Copy success | background-color | 0ms in, 1200ms hold | — | click |
| Chip hover | border-color | 120ms | ease | mouseenter |
| Range slider thumb | — (native) | — | — | drag |
| Toast enter | transform, opacity | 250ms | ease-spring | programmatic |
| Toast exit | transform, opacity | 200ms | ease | timeout |
| Modal backdrop | opacity | 200ms | ease | programmatic |
| Modal panel | transform, opacity | 250ms | ease-spring | programmatic |
| Skeleton pulse | opacity | 1500ms | ease-in-out | infinite |
| Focus ring appear | box-shadow | 0ms (instant) | — | :focus-visible |

### Staged Micro-interactions

For completion or success states (e.g., checklist item checked):

```
0ms   — fill changes to olive
80ms  — checkmark appears (scale from 0 to 1, ease-spring)
120ms — text gets line-through (if applicable)
200ms — optional particle/burst (scale 0→1→0, 400ms total)
600ms — settle (all transitions complete)
```

### Easing Functions

```css
:root {
  --ease-standard: cubic-bezier(.16, 1, .3, 1);   /* quick start, gentle stop */
  --ease-spring: cubic-bezier(.34, 1.56, .64, 1); /* slight overshoot */
  --ease-in: cubic-bezier(.4, 0, 1, 1);           /* accelerate out */
  --ease-out: cubic-bezier(0, 0, .2, 1);          /* decelerate in */
}
```

Use `ease-standard` for most UI transitions. Use `ease-spring` for entrances and playful confirmations. Use linear for progress bars and loading indicators.

## Additional Components

### Toast / Notification

A temporary status message that appears, holds, and auto-dismisses.

Anatomy: icon area (optional) + message + optional action link + dismiss button.

```css
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%) translateY(0);
  background: var(--slate);
  color: var(--ivory);
  font-family: var(--mono);
  font-size: 13px;
  padding: 12px 18px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(20,20,19,.2);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  opacity: 0;
  transform: translateX(-50%) translateY(12px);
  transition: opacity 250ms var(--ease-spring), transform 250ms var(--ease-spring);
}

.toast.visible {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.toast.success {
  background: var(--olive);
}

.toast .action {
  color: var(--clay);
  text-decoration: underline;
  cursor: pointer;
}

.toast .dismiss {
  appearance: none;
  background: none;
  border: none;
  color: var(--gray-500);
  cursor: pointer;
  padding: 0 0 0 8px;
  font-size: 16px;
}
```

Behavior:

- Enter from bottom with `ease-spring` over `250ms`.
- Hold for `3000ms` to `5000ms` depending on content length.
- Exit downward with `ease` over `200ms`.
- Use `aria-live="polite"` for informational, `aria-live="assertive"` for errors.
- Stack multiple toasts vertically with `8px` gap.

### Modal / Dialog

A focused overlay for confirmations, detail views, or small editors.

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(20, 20, 19, .4);
  z-index: 900;
  opacity: 0;
  transition: opacity 200ms ease;
}

.modal-backdrop.visible {
  opacity: 1;
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(.96);
  background: var(--paper);
  border: var(--border);
  border-radius: var(--radius-panel);
  padding: 28px;
  max-width: 560px;
  width: calc(100% - 48px);
  max-height: 80vh;
  overflow-y: auto;
  z-index: 901;
  box-shadow: 0 20px 60px rgba(20,20,19,.18);
  opacity: 0;
  transition: opacity 250ms var(--ease-spring), transform 250ms var(--ease-spring);
}

.modal.visible {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  appearance: none;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--gray-500);
  padding: 4px;
  border-radius: 6px;
}

.modal-close:hover {
  background: var(--gray-100);
  color: var(--slate);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--gray-100);
}
```

Rules:

- Use native `<dialog>` element when browser support allows.
- Trap focus inside the modal when open.
- Escape key closes the modal.
- Return focus to the trigger element on close.
- Add `aria-modal="true"` and `aria-labelledby` pointing to the title.
- Backdrop click closes the modal (unless destructive action is pending).

### Dropdown / Select

A custom styled select menu or action menu.

```css
.dropdown-wrap {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  appearance: none;
  background: var(--paper);
  border: var(--border);
  border-radius: var(--radius-row);
  padding: 8px 32px 8px 12px;
  font-family: var(--sans);
  font-size: 14px;
  color: var(--gray-700);
  cursor: pointer;
  min-width: 140px;
}

.dropdown-trigger::after {
  content: "›";
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%) rotate(90deg);
  font-family: var(--mono);
  color: var(--gray-500);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 100%;
  background: var(--paper);
  border: var(--border);
  border-radius: var(--radius-row);
  box-shadow: var(--shadow-lift);
  padding: 4px;
  z-index: 100;
  opacity: 0;
  transform: translateY(-4px);
  pointer-events: none;
  transition: opacity 150ms ease, transform 150ms ease;
}

.dropdown-menu.open {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  text-align: left;
  font-family: var(--sans);
  font-size: 14px;
  color: var(--gray-700);
  border-radius: 6px;
  cursor: pointer;
}

.dropdown-item:hover,
.dropdown-item:focus-visible {
  background: var(--gray-100);
  color: var(--slate);
  outline: 0;
}

.dropdown-item.active {
  color: var(--clay);
  font-weight: 500;
}
```

Rules:

- Prefer native `<select>` for form submissions. Use custom dropdown only for action menus or styled selects.
- Use `aria-expanded`, `aria-haspopup="listbox"`, and `aria-activedescendant` for keyboard navigation.
- Arrow keys navigate items; Enter selects; Escape closes.
- Close on outside click or blur.

### Skeleton / Loading

Placeholder content shown while data loads.

```css
.skeleton {
  background: var(--gray-100);
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

@media (prefers-reduced-motion: no-preference) {
  .skeleton::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(255,255,255,.4) 50%,
      transparent 100%
    );
    animation: skeleton-pulse 1500ms ease-in-out infinite;
  }

  @keyframes skeleton-pulse {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
}

.skeleton-text {
  height: 14px;
  margin-bottom: 10px;
  width: 100%;
}

.skeleton-text.short { width: 60%; }
.skeleton-text.medium { width: 80%; }

.skeleton-heading {
  height: 24px;
  width: 40%;
  margin-bottom: 16px;
}

.skeleton-card {
  height: 120px;
  border-radius: var(--radius-panel);
}

.skeleton-chip {
  height: 28px;
  width: 80px;
  border-radius: 999px;
  display: inline-block;
}
```

Rules:

- Match skeleton shapes to the actual content that will replace them.
- Use `aria-busy="true"` on the container and `aria-hidden="true"` on skeleton elements.
- Respect `prefers-reduced-motion` — show static gray blocks without animation.
- Keep skeleton pulse subtle; avoid bright sweeping gradients.

### Tooltip

Contextual help shown on hover or focus. Use sparingly for supplementary information.

```css
[data-tooltip] {
  position: relative;
  cursor: help;
}

[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: var(--slate);
  color: var(--ivory);
  font-family: var(--sans);
  font-size: 12px;
  line-height: 1.4;
  padding: 6px 10px;
  border-radius: 6px;
  white-space: nowrap;
  max-width: 240px;
  white-space: normal;
  z-index: 50;
  pointer-events: none;
  opacity: 0;
  transition: opacity 150ms ease, transform 150ms ease;
}

[data-tooltip]:hover::after,
[data-tooltip]:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* Arrow */
[data-tooltip]::before {
  content: "";
  position: absolute;
  bottom: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: var(--slate);
  opacity: 0;
  transition: opacity 150ms ease;
}

[data-tooltip]:hover::before,
[data-tooltip]:focus-visible::before {
  opacity: 1;
}
```

Rules:

- Show tooltip on both hover and `:focus-visible` so keyboard users can access them.
- Keep tooltip text under 80 characters; for longer content use a popover or `<details>`.
- Add `aria-describedby` linking to a hidden tooltip text for screen readers, or use `title` attribute as fallback.
- Tooltip should not obscure the triggering element.
- On mobile (touch), consider revealing tooltips on long-press or providing the info inline.

### Progress / Status Bar

A horizontal status indicator for multi-step processes.

```css
.progress-steps {
  display: flex;
  align-items: center;
  gap: 0;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
  font-size: 12px;
  color: var(--gray-500);
}

.progress-step.done {
  color: var(--olive);
}

.progress-step.active {
  color: var(--clay);
  font-weight: 600;
}

.progress-step .step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--gray-300);
  flex-shrink: 0;
}

.progress-step.done .step-dot {
  background: var(--olive);
}

.progress-step.active .step-dot {
  background: var(--clay);
  box-shadow: 0 0 0 3px rgba(217,119,87,.2);
}

.progress-connector {
  width: 32px;
  height: 2px;
  background: var(--gray-300);
  margin: 0 4px;
}

.progress-connector.done {
  background: var(--olive);
}
```
