# Determinism Ladder — Fix-Layer Selection Guide

When fixing a skill issue, choose the MOST deterministic layer possible. Priority descends from top to bottom — always try the higher level first.

The reasoning: deterministic solutions eliminate entire categories of failure. A script always runs the same way; an LLM instruction might be followed differently each time. Pushing work up the ladder reduces the surface area for future failures.

## Level 1: Script (scripts/)

**Best for:** Operations with fixed input-to-output mapping — format conversion, file validation, grep-and-scan, packaging, template generation.

**Signal:** The correct action does not depend on understanding user intent or code semantics. Same input always produces same output.

**Examples:**
- Impact scanning (grep keyword across directories)
- Frontmatter validation (check required fields exist)
- File format conversion (markdown to docx)
- Structure auditing (count lines, detect patterns)

**Anti-pattern to detect:** SKILL.md says "must run `<exact command>`" — if the command is fixed, it belongs in a script.

## Level 2: Hook (settings.json hooks)

**Best for:** Pre/post event interception where the response is deterministic — something that should happen every time before or after a specific event, without exception.

**Signal:** "Before every X, always do Y" or "After every X, check Z." No judgment needed — just gate or transform.

**Examples:**
- Lint check before commit
- Format validation on file save
- Auto-backup before destructive operations

**When NOT to use:** The check requires understanding context or making a judgment call. If the action might sometimes be wrong, it's not a hook — it's an instruction.

## Level 3: SKILL.md Instruction

**Best for:** Decisions requiring judgment, creativity, context awareness, or theory of mind. The correct action depends on understanding the user's intent or the code's meaning.

**Signal:** "Choose the best approach", "decide whether X is appropriate", "evaluate the quality of Y."

**Examples:**
- Choosing which root cause category applies
- Drafting a proposal that explains why a fix prevents recurrence
- Deciding whether a skill needs restructuring vs a patch
- Interpreting audit results and recommending next steps

**Writing guidance:** Explain *why*, not just *what*. "Use memoization for expensive computations because re-renders trigger recalculation" is better than "MUST use useMemo." The LLM needs the reasoning to handle edge cases.

## Level 4: Rule (~/.claude/rules/)

**Best for:** Cross-skill behavioral constraints that apply broadly, not to just one skill.

**Signal:** The rule applies to agent behavior in general, across multiple skills or across the entire session.

**Examples:**
- "Default to Chinese for user-facing output"
- "Commit after each logical unit of work"
- "Auto-trigger /skill-reflect when a skill fails"

**When NOT to use:** The rule only applies to one skill — that logic belongs in the skill's SKILL.md, not in a global rule.

---

## Anti-Pattern Detection Checklist

When reviewing a skill, check for these layer mismatches:

| If you find... | It should probably be... |
|----------------|------------------------|
| SKILL.md says "run this exact command" | Level 1 (script) |
| SKILL.md says "always do X before Y" with no judgment needed | Level 2 (hook) |
| A rule that only applies to one skill | Level 3 (SKILL.md instruction) |
| A script that makes judgment calls or needs context | Level 3 (SKILL.md instruction) |
| SKILL.md instructions that are generic agent behavior | Level 4 (rule) |
