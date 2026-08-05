# Skill Anti-Patterns

Each anti-pattern includes what it looks like, why it fails, and how to fix it.

## 1. Deterministic Instructions in SKILL.md

**What:** SKILL.md says "run `grep -rl '<keyword>' ~/.claude/skills/ | sort`" — a fixed command sequence written as a prose instruction.

**Why it fails:** The LLM may modify flags, forget paths, add hallucinated options, or skip steps. Fixed command sequences are deterministic — they don't need LLM judgment.

**Fix:** Move to `scripts/`. Have SKILL.md call the script by path. The LLM's job becomes interpreting the output, not remembering the command.

## 2. Monolithic SKILL.md (>500 lines)

**What:** All domain knowledge packed into a single file — framework references, edge cases, multi-variant instructions all mixed together.

**Why it fails:** Tokens wasted on irrelevant sections. When a user triggers the skill for variant A, the LLM still loads 400 lines about variants B, C, D. Progressive disclosure is broken.

**Fix:** Split by domain/variant into `references/`. SKILL.md keeps the routing logic ("if user wants Node, read references/node.md"), each reference file stays focused.

## 3. Deep Reference Chains

**What:** references/a.md says "see references/b.md for details", which in turn says "see references/c.md".

**Why it fails:** LLMs lose context hierarchy reliability with each hop. Debugging which reference caused a wrong behavior becomes hard. The progressive disclosure model assumes one level of indirection, not multiple.

**Fix:** Flatten to one level. SKILL.md -> references/x.md, never deeper. If a reference file is too long, split it into two sibling references rather than nesting.

## 4. Hardcoded Absolute Paths

**What:** References to `/Users/<name>/.claude/...` or `/home/<name>/project/...` baked into SKILL.md or scripts.

**Why it fails:** The skill is not portable. It can't be `cp -r`-copied to another machine or shared with other users. Self-containment is broken.

**Fix:** Use relative paths from the skill directory for internal references. Use `~/.claude/` as the base for Claude environment paths. Use environment variables (`$HOME`, `$CLAUDE_DIR`) in scripts.

## 5. Trigger Description Too Narrow

**What:** Description only lists slash-command names or a single formal sentence: "A tool for reflecting on skill failures."

**Why it fails:** Claude matches user intent against the description text. Natural language variations ("this skill is broken", "why didn't the skill fire") won't match a narrow description. The skill undertriggers.

**Fix:** Describe the problem space, not just the solution. Include edge phrasings and synonyms. Be slightly "pushy" — it's better to overtrigger slightly (the LLM can decide not to use it) than to never trigger on valid use cases.

## 6. MUST/NEVER Without Reasoning

**What:** "MUST use useMemo for all computed values." "NEVER use tabs."

**Why it fails:** The LLM can't handle edge cases because it doesn't understand the principle. When the rule conflicts with another instruction, it has no basis to make a judgment call. Blindly following all-caps rules produces brittle behavior.

**Fix:** Explain the reasoning. "useMemo prevents recalculation on every render, which matters when the computation is expensive or the component re-renders frequently. For cheap operations, the overhead of memoization itself outweighs the benefit." The LLM can now handle edge cases.

## 7. Duplicate Trigger Logic

**What:** Trigger conditions listed in frontmatter description, in the SKILL.md body's "trigger scenarios" section, and in a separate rules/ file — all slightly different.

**Why it fails:** The three copies drift over time. One gets updated, the others don't. Maintenance becomes a game of whack-a-mole.

**Fix:** Single source of truth. The `description` field handles triggering. A `rules/` file can provide passive triggers for auto-invocation. The SKILL.md body describes the workflow after triggering, not the conditions for triggering.

## 8. Non-Standard Frontmatter Keys

**What:** Using `triggers:`, `user-invocable:`, `author:`, or other invented keys in YAML frontmatter.

**Why it fails:** The spec allows only: `name`, `description`, `version`, `license`, `allowed-tools`, `metadata`, `compatibility`. Non-standard keys may cause validation errors or be silently ignored by different agent implementations.

**Fix:** Use allowed keys. Put custom data under `metadata:` as key-value pairs. Move trigger phrases into the `description` field.
