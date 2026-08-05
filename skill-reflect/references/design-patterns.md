# Skill Design Patterns

Four directory paradigms for organizing a skill. Most skills combine paradigms; the label describes the primary pattern.

## 1. Pure Instruction (SKILL.md only)

A single SKILL.md file with no subdirectories.

**When to use:** The skill provides a thinking framework, style guide, or decision tree. It changes how the LLM reasons, not what it executes. There are no deterministic operations — no file conversions, no validation scripts, no grep-and-parse sequences.

**Signal:** The skill never needs to run bash commands or produce files in a fixed format.

**Examples:** ruminate, codify, frontend-design

## 2. Script-Driven (SKILL.md + scripts/)

SKILL.md acts as a dispatcher; deterministic operations live in `scripts/`.

**When to use:** The skill performs operations with fixed input-to-output mappings — format conversion, validation, file scanning, packaging. Same input always produces same output.

**Signal:** Test runs repeatedly generate similar helper scripts. SKILL.md contains >5 inline bash blocks. Instructions say "run this exact command."

**Determinism boundary:** LLM handles judgment and creativity; scripts handle format conversion, validation, grep/scan, packaging.

**Examples:** docx (pack/unpack/validate scripts), excalidraw-diagram (render script)

**Anti-pattern to detect:** SKILL.md says "must run `grep -rl ... | sort`" — a fixed command that should be a script, not an instruction the LLM must remember.

## 3. Reference-Doc (SKILL.md + references/)

SKILL.md holds the workflow and routing logic; domain knowledge lives in `references/` and is loaded on demand.

**When to use:** The skill covers multiple variants, frameworks, or domains. The SKILL.md body would exceed 500 lines without splitting. Large sections apply only to specific sub-cases.

**Reference depth rule:** SKILL.md -> references/x.md is OK. references/x.md -> references/y.md is NOT OK. Keep references one level deep — LLMs lose track of multi-level reference chains.

**Examples:** mcp-builder (node vs python references), png-diagram (26 diagram type references)

## 4. Asset-Bundled (SKILL.md + assets/)

The skill needs static resources that the LLM should not generate from scratch.

**When to use:** The skill requires fonts, HTML templates, icons, XML schemas, or other files that are deterministic assets — not something the LLM should invent each time.

**Self-containment rule:** Bundle assets into the skill directory. Don't reference system fonts or external URLs that might change. The entire skill dir must be `cp -r`-able.

**Examples:** canvas-design (40+ .ttf fonts), algorithmic-art (HTML viewer template), skill-creator (eval_review.html)

---

## Choosing a Paradigm

| Question | Yes | No |
|----------|-----|-----|
| Does the skill run deterministic operations (grep, convert, validate, package)? | Add scripts/ | Skip |
| Does the skill have domain knowledge >200 lines that varies by sub-case? | Add references/ | Skip |
| Does the skill need static resources (fonts, templates, schemas)? | Add assets/ | Skip |
| None of the above? | Pure instruction | — |

Multiple "Yes" answers = mixed paradigm. This is normal and expected for complex skills.

## Progressive Disclosure Budget

| Layer | Token budget | When loaded |
|-------|-------------|-------------|
| L1: name + description | ~100 tokens | Always in context |
| L2: SKILL.md body | <5000 tokens (~500 lines) | When skill triggers |
| L3: scripts/references/assets | Unlimited | On demand, by explicit reference from SKILL.md |

If SKILL.md approaches 500 lines, that's a strong signal to extract content to references/.

## Directory Names Are Semantic

No configuration needed — the directory name tells the LLM what to expect:

- `scripts/` = executable files, run them
- `references/` = markdown docs, read on demand
- `assets/` = static resources, use them in output
- `agents/` = subagent instructions (specialized)
- `evals/` = test cases (used by skill-creator)
