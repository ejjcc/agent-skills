# Pattern Schema

The generator accepts a JSON object with this shape:

```json
{
  "title": "Supervisor / Manager",
  "sub": "Agents-as-tools · centralized orchestration",
  "nodes": [
    {
      "id": "manager",
      "x": 230,
      "y": 230,
      "w": 180,
      "h": 54,
      "label": "Manager",
      "sub": "supervisor",
      "kind": "accent"
    }
  ],
  "edges": {
    "m-c": {
      "from": "manager",
      "to": "coder",
      "label": "call",
      "curve": 0,
      "dashed": false
    }
  },
  "timeline": [
    {
      "caption": "Manager calls <b>Coder</b> to write code.",
      "fire": ["m-c"],
      "activate": ["manager", "coder"],
      "dim": [],
      "duration": 1500
    }
  ]
}
```

## Required Fields

- `title`: Diagram title.
- `nodes`: Array of node objects.
- `edges`: Object keyed by edge ID.
- `timeline`: Ordered animation steps.

## Node Fields

- `id` required, unique.
- `x`, `y` required, top-left coordinates in a `900 x 540` canvas.
- `label` required.
- `w` optional, default `140`.
- `h` optional, default `54`.
- `sub` optional, small uppercase subtitle.
- `kind` optional: `plain`, `accent`, `dark`, `user`, `store`, `bus`.

## Edge Fields

- `from` required, node ID.
- `to` required, node ID.
- `label` optional.
- `curve` optional number. Positive and negative values bend the edge in opposite directions.
- `dashed` optional boolean.

## Timeline Fields

- `caption` required. Inline `<b>` and `<code>` are allowed.
- `fire` optional array of edge IDs. Prefix with `!` for reverse token movement.
- `activate` optional array of node IDs to pulse/highlight.
- `dim` optional array of node IDs to fade.
- `duration` optional milliseconds, default `1500`.

## Design Defaults

- Fixed light theme.
- Auto-play enabled.
- Minimal controls: previous, play/pause, next, progress dots.
- No keyboard shortcuts, speed controls, replay button, external assets, or runtime dependencies by default.
