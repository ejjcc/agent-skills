# Skill Specification Constraints

Quick-reference for the official Agent Skills spec (agentskills.io/specification).

## Frontmatter Fields

| Field | Required | Max Length | Notes |
|-------|----------|-----------|-------|
| name | Yes | 64 chars | Lowercase letters, digits, hyphens only |
| description | Yes | 1024 chars | What the skill does + when to use it |
| version | No | — | Semantic version string |
| license | No | — | License name or reference to bundled file |
| allowed-tools | No | — | Space-delimited list of pre-approved tools |
| metadata | No | — | Arbitrary key-value map for custom data |
| compatibility | No | 500 chars | Environment requirements |

No other top-level keys are allowed.

## Name Rules

- 1-64 characters
- Only lowercase letters (`a-z`), digits (`0-9`), and hyphens (`-`)
- Must NOT start or end with a hyphen
- Must NOT contain consecutive hyphens (`--`)
- Must match the parent directory name exactly

## Description Guidelines

- 1-1024 characters
- Should describe both WHAT the skill does and WHEN to use it
- Include specific keywords for intent matching
- Be slightly "pushy" — undertriggering is worse than overtriggering
- Claude decides whether to load a skill based on this text alone

## SKILL.md Body

- Recommended: < 500 lines
- Hard guidance: < 5000 tokens
- If approaching the limit, split domain knowledge into `references/`
- No format restrictions on markdown content

## Directory Structure

```
skill-name/           # Directory name must match frontmatter name
├── SKILL.md          # Required
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation loaded on demand
├── assets/           # Optional: static resources
├── agents/           # Optional: subagent instructions
├── evals/            # Optional: test cases
└── examples/         # Optional: usage examples
```

## File References

- One level deep from SKILL.md: `references/x.md` OK
- No deeper chains: `references/sub/y.md` discouraged
- Use relative paths from skill root

## Self-Containment

- Entire skill directory must be `cp -r`-able to another machine
- No external path dependencies (no `/Users/<name>/...`)
- No leaked secrets or credentials
- Scripts should document their dependencies clearly
