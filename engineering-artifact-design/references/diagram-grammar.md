# Diagram Grammar For Engineering Artifacts

Source influence: `cathrynlavery/diagram-design` (MIT). This reference adapts the transferable diagram craft rules to the `engineering-artifact-design` visual system. Keep the warm ivory/paper/slate/clay/oat/olive palette, CJK typography rules, and browser-native artifact layout from this skill; do not import the external skill's brand skin, font dependencies, or decorative variants wholesale.

## Table Of Contents

1. Fit Test
2. Type Selector
3. Complexity Budget
4. Shared SVG Grammar
5. Type Recipes
6. Engineering Artifact Integration
7. Taste Gate

## Fit Test

Draw a diagram only when it teaches faster than prose, a table, or a short list.

Use a diagram when the reader needs to see:

- Components and connections.
- Time-ordered messages or events.
- State transitions and guards.
- Ownership, handoffs, or boundaries.
- Data relationships.
- Prioritization across two axes.
- Nested scope or dependency structure.

Avoid a diagram when:

- A paragraph would explain the point just as well.
- The content is a simple list.
- The visual would be one box with one label.
- A true matrix/table is needed for comparison.
- The only goal is decoration.

The highest-quality move is often deletion: merge nodes that always move together, remove obvious arrows, and keep only labels that change understanding.

## Type Selector

Pick one dominant diagram grammar. Do not mix grammars unless the page intentionally separates them into multiple diagrams.

| If showing | Use | Common software R&D placement |
| --- | --- | --- |
| Components, services, data stores, integrations | Architecture | Architecture understanding, migration, security boundary |
| Branching decision logic | Flowchart | Process, auth decisions, support triage |
| Time-ordered messages between actors | Sequence | API handshake, incident trace, protocol flow |
| Lifecycle states and transitions | State machine | Job queues, connection lifecycle, order/auth state |
| Entities, fields, cardinality | ER / data model | API contract, schema migration, domain model |
| Events positioned in time | Timeline | Incident, rollout, project milestones |
| Teams/systems with handoffs | Swimlane | Process/mechanism, release, incident response |
| Two-axis positioning | Quadrant / landscape | Technical research, option evaluation, roadmap priority |
| Scope through containment | Nested boundary | Trust zones, repo scopes, config inheritance |
| Parent-child hierarchy | Tree | Dependency tree, folder tour, requirement breakdown |
| People, teams, agents, ownership | Org / ownership map | Ownership, escalation, review routing |
| Abstraction levels | Layer stack | Architecture, concept explanation, platform layers |
| Overlapping sets | Venn | Capability overlap, consumer impact, policy scope |
| Ranked hierarchy or drop-off | Pyramid / funnel | Prioritization, rollout funnel, risk pyramid |

Rules of thumb:

- If there are branches with conditions, use a flowchart, not an architecture graph.
- If time flows top-to-bottom across actors, use a sequence diagram, not swimlanes.
- If ownership is the point, use swimlane/org; if data movement is the point, use architecture/sequence.
- If a diagram exceeds budget, split into overview + detail.

## Complexity Budget

These limits are defaults for one diagram inside an engineering artifact. Exceeding them is a signal to split the figure.

| Limit | Target |
| --- | --- |
| Nodes | 5-9 ideal, 11 max |
| Arrows / transitions | 12 max |
| Focal clay elements | 1-2 max |
| Sequence lifelines | 5 max |
| Swimlanes | 5 max |
| ER entities | 8 max |
| Timeline events | 8 major events per visible figure |
| Tree depth | 4 max |
| Nested levels | 5-6 max |
| Quadrant items | 12 max |
| Annotation callouts | 2 max |

Density target: complete enough to orient the reader, sparse enough to read without a guide.

## Shared SVG Grammar

### Coordinate And Spacing Discipline

- Use a stable `viewBox`; avoid relying on CSS-only scaling to repair bad layout.
- Put important coordinates, node sizes, and gaps on a small spacing system. Prefer multiples of `4px`; common gaps are `20`, `24`, `32`, `40`, `48`.
- Keep text inside nodes short. Move explanations to adjacent cards, callouts, or adaptive info rows.
- If text must wrap, use HTML beside the SVG. SVG text wrapping is fragile.

### Palette Mapping

Use current skill tokens, not external colors:

| Semantic role | Token treatment |
| --- | --- |
| Page / diagram ground | `--ivory` or transparent on page |
| Normal node fill | `--paper` |
| Normal stroke | `--gray-300` or `--gray-500` |
| Primary text | `--slate` |
| Secondary labels / arrows | `--gray-500` |
| Focal path or risky node | `--clay` / clay tint |
| Success / stable path | `--olive` |
| Danger / regression | `--rust` |
| Region / layer fill | `--oat` tint |
| External or optional path | dashed gray stroke |

Clay is editorial focus, not a general importance color. If more than two nodes are clay, the diagram has not decided what matters.

### Tokenized SVG Primitives

Inline SVG examples should use classes backed by CSS custom properties, not repeated hard-coded hex fills and strokes. This is what keeps diagrams aligned with the page palette, dark mode, print mode, and future token edits.

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

### Typography

- Human-readable node names: sans.
- Technical sublabels, ports, endpoints, table names, event names: mono.
- Diagram title and section heading: page-level serif, outside the SVG when possible.
- Chinese labels inside SVG should use sans and stay short; put longer Chinese prose outside the SVG.
- Do not use mono as a blanket "developer" font for all labels.

### Arrow Markers

Define separate markers for normal, focal, and optional/link arrows when needed.

```svg
<defs>
  <marker id="arrow" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
    <path class="diagram-arrow" d="M0,0 L8,4 L0,8 Z"></path>
  </marker>
  <marker id="arrow-hot" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
    <path class="diagram-arrow is-hot" d="M0,0 L8,4 L0,8 Z"></path>
  </marker>
</defs>
```

Rules:

- Draw arrows before boxes so node fills cover line ends.
- Use `markerUnits="userSpaceOnUse"` so arrowheads stay the same size when focal paths use thicker strokes.
- Terminate connector endpoints outside the target node with 6-10px clearance from the node border. If the endpoint sits exactly on or inside the target rectangle, the later-drawn node fill/border will cover the arrowhead.
- If using an explicit orthogonal landing segment before the arrowhead, keep it micro, usually 6-10px. Longer landing segments start reading as mechanical elbows and make architecture maps feel less graceful.
- Prefer shortening the connector path over drawing arrows above nodes; arrows above nodes make lines cut through borders and reduce the clean schematic feel.
- Solid gray arrows are default movement.
- Clay arrows mark the hot path, risk path, or chosen path.
- Dashed arrows mark async, optional, return, passive, or background movement.
- Avoid bidirectional arrows unless both directions are genuinely meaningful.

### Node Boxes

Recommended node pattern:

```svg
<rect class="diagram-node" x="120" y="72" width="144" height="48" rx="8"></rect>
<text class="diagram-label" x="192" y="98" text-anchor="middle">Gateway</text>
<text class="diagram-label-mono" x="192" y="114" text-anchor="middle">ws://room</text>
```

Use type tags sparingly. If used, keep them rectangular, not pill-shaped, and reserve them for information that changes interpretation (`API`, `STORE`, `WORKER`, `EXT`).

### Boundary Labels

For trust zones, layers, VPCs, tenants, or ownership regions, put labels on a paper-colored mask with a warm-gray border so the boundary line does not run through text and the label does not blend into oat-tinted regions.

```svg
<rect class="diagram-region" x="24" y="40" width="520" height="96" rx="12"></rect>
<rect class="diagram-mask" x="40" y="32" width="96" height="18" rx="3"></rect>
<text class="diagram-label-mono" x="48" y="45">browser zone</text>
```

### Arrow Labels

Every arrow label needs an opaque paper background plus a warm-gray border, otherwise the line cuts through the text or the label disappears into a pale diagram region.

```svg
<rect class="diagram-mask" x="268" y="80" width="48" height="16" rx="3"></rect>
<text class="diagram-label-mono" x="292" y="92" text-anchor="middle">WRITE</text>
```

Rules:

- Keep labels under 14 characters when possible.
- Use `--paper`/white fill, a `--gray-300` border, and `--gray-700` or `--slate` text for label masks.
- Place labels near the segment midpoint.
- Never use vertical `writing-mode` for arrow labels.
- If label text gets long, move the explanation to a note beside the diagram.

### Legends

Avoid floating legends inside the active diagram area. Prefer one of:

- A short horizontal legend strip below the SVG.
- Chips or notes in the surrounding panel.
- Direct labels on nodes and paths, with no legend.

Use a legend only for symbols that repeat. Do not add a legend for a one-off clay highlight; label it directly.

### Annotation Callouts

Use at most two editorial callouts for non-obvious insights. They should live in diagram margins, not inside the active path.

Recommended pattern:

- Serif italic or calm sans aside text.
- Dashed leader line.
- Tiny landing dot.
- No solid arrowhead; that would read as flow.

Use callouts for "why this matters", not for labels the diagram should already carry.

## Type Recipes

For production artifacts, prefer starting from `assets/diagram-templates.html` when its architecture, sequence, or timeline skeleton is close. Keep the classes and token-driven CSS, then change labels and coordinates. If the template is not close, still reuse its marker, mask, node, edge, and local-scroll shell patterns.

### Architecture

Best for system overviews, data flow, infra topology, trust boundaries.

- Group by tier, trust zone, or ownership zone.
- Main flow runs left-to-right or top-to-bottom. Pick one and hold it.
- Use oat-tinted boundary bands for layers.
- Clay marks the critical integration point, risky boundary, or hot path.
- Avoid legends inside the graph.
- Do not make every service a separate node; group low-signal clusters.

### Flowchart

Best for decision logic, algorithms, routing, support triage.

- Shape carries type: oval start/end, rounded rectangle action, diamond decision.
- Flow runs top-to-bottom by default.
- Label every decision branch.
- Use clay for the happy path or the single most consequential decision, not every branch.
- Avoid decisions with 4+ exits; split into nested decisions.

### Sequence

Best for API handshakes, protocol exchanges, request traces, incident reconstruction.

- Actors are boxes across the top.
- Time flows top-to-bottom.
- Lifelines are dashed vertical lines.
- Messages are horizontal arrows between lifelines.
- Return messages are dashed.
- Do not draw arrows upward.
- Keep labels out of other lifelines; shift rows if needed.

### State Machine

Best for connection lifecycle, queue/job status, auth/session state, form wizard.

- States are rounded rectangles.
- Start is a filled dot; end is a ringed dot.
- Transitions are curved or straight arrows labeled `event [guard] / action`.
- Clay marks the state or transition the reader should notice.
- Avoid "from any state" spaghetti; use one annotation like `* -> Error on timeout`.

### ER / Data Model

Best for schemas, domain models, API resources.

- Entity boxes have a header and field list.
- Use mono for fields, `#` for primary key, `->` or `FK` for foreign key.
- Put cardinality near entity edges: `1`, `N`, `0..1`, `1..*`.
- Group related entities and omit low-signal relationships.
- Clay marks aggregate root or central entity.

### Timeline

Best for incidents, rollout history, migrations, project milestones.

- Use a hairline baseline.
- Place events at honest relative positions; do not fake equal spacing when intervals differ.
- Alternate labels above/below or use stacked rows to avoid collisions.
- Clay marks the major milestone, fault point, or "now".
- If the middle is too dense, use a visible break or split the timeline.

### Swimlane

Best for handoffs between teams, services, vendors, or roles.

- One lane per actor/team/system.
- Steps sit inside the lane of the owner performing them.
- Handoffs crossing lanes are the important edges; one may be clay.
- Do not draw a step across two lanes. Pick one owner.
- Avoid arrows that snake back and forth; reorder into a mostly straight flow.

### Quadrant / Landscape

Best for technology research, option evaluation, product/architecture positioning.

- Use two meaningful axes.
- Labels at axis tips should be short words or phrases; avoid parenthetical paragraphs.
- Put the recommended or surprising option in clay, not all good options.
- Use cards below the diagram for evidence; do not pack evidence into the quadrants.
- If criteria are discrete rather than continuous, use a matrix instead.

### Nested Boundary

Best for trust zones, containment, config inheritance, scope hierarchy.

- Use nested rectangles or bands.
- Each level needs a short label.
- Clay marks the innermost/current/risky scope.
- Stop at 5-6 levels; deeper nesting becomes unreadable.
- Keep descriptions outside the rings.

### Tree / Dependency

Best for parent-child hierarchy, dependency trees, folder tours.

- Use orthogonal elbow connectors; avoid diagonal spaghetti.
- Parent drops to a horizontal bus, then each child drops from the bus.
- Clay marks root or critical leaf, not both unless the contrast is the point.
- Max depth 4; deeper trees need collapsed groups or separate detail diagrams.

### Org / Ownership

Best for teams, agents, review ownership, escalation paths.

- Top node is front door or accountable owner.
- Limit visible nodes; group specialists under pods.
- Nodes can carry three short facts: scope, invocation path, escalation/reviewer.
- Put approval rules in a side note, not as extra nodes.
- Use this instead of a generic tree when responsibility is the point.

### Layer Stack

Best for abstraction layers, platform stacks, request pipeline layers.

- Stack broad horizontal bands.
- Label each layer directly.
- Use clay on the layer that changed, failed, or owns the decision.
- Do not mix layer stack with flowchart arrows unless the arrows are minimal.

### Venn

Best for capability overlap, consumer impact, policy scope.

- Use 2-3 circles max.
- Label circles outside or at calm edges; label intersections only when they matter.
- Use soft tints; avoid saturated overlapping color noise.
- If there are many sets, use a matrix or table instead.

### Pyramid / Funnel

Best for ranked priority, risk hierarchy, conversion/drop-off.

- Pyramid points up for importance/rarity/value.
- Funnel points down for conversion/drop-off.
- Use 4-6 layers.
- Layer widths should honestly reflect meaning when quantitative.
- Do not mix pyramid and funnel meanings in one figure.

## Engineering Artifact Integration

### Pair Diagrams With Reading Surfaces

A good engineering artifact rarely leaves a diagram alone. Pair it with:

- `Adaptive Info Rows` for key files/modules.
- Evidence cards for claims behind a research landscape.
- Logs/metrics beside incident timelines.
- Runbook steps beside mechanism diagrams.
- Checklists after release or review diagrams.

### Use Interaction To Clarify, Not Decorate

Useful interactions:

- Click a diagram node to highlight the matching file row.
- Toggle risk overlays, async paths, or failure paths.
- Switch tabs between `Diagram / Code / Metrics`.
- Filter timeline events by signal type.

Avoid interactions that only animate the diagram without changing reading state.

### Responsive Rules

- SVGs may scroll horizontally inside a panel if shrinking would make labels unreadable.
- For narrow screens, prefer a simplified overview SVG plus details below.
- Move long prose out of SVG into nearby HTML.
- Recheck at `360px`, `768px`, and desktop width.

### Accessibility

- Give every SVG a useful `role="img"` and `aria-label`.
- If the diagram encodes critical facts, repeat them in adjacent HTML text or a table/list.
- Do not rely on color alone. Use stroke style, label, shape, or position.
- Keep focusable overlays and click-linked nodes keyboard reachable when implemented.

## Taste Gate

Before delivering a diagram:

- Is the diagram type correct for the information?
- Would a table or paragraph be clearer?
- Are all nodes necessary?
- Are all arrows meaningful?
- Are there no more than 1-2 clay focal elements?
- Are arrow labels masked and short?
- Are legends outside the active graph, or removed entirely?
- Are all long explanations outside the SVG?
- Does the diagram use the current artifact tokens rather than a borrowed palette?
- Does the diagram remain legible at mobile and desktop widths?
