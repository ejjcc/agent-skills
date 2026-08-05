#!/usr/bin/env bash
# Skill structure auditor: validate a skill directory against design patterns
# Usage: audit_structure.sh <skill-dir-path>
# Output: JSON with paradigm detection, issues, and suggestions

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo '{"error": "Usage: audit_structure.sh <skill-dir-path>"}' >&2
  exit 1
fi

SKILL_DIR="${1%/}"
SKILL_MD="$SKILL_DIR/SKILL.md"
DIR_NAME="$(basename "$SKILL_DIR")"

# Collectors
issues=()
suggestions=()

add_issue() {
  local severity="$1" check="$2" message="$3"
  issues+=("$(printf '{"severity":%s,"check":%s,"message":%s}' \
    "$(echo "$severity" | jq -R .)" \
    "$(echo "$check" | jq -R .)" \
    "$(echo "$message" | jq -R .)")")
}

add_suggestion() {
  local type="$1" detail="$2"
  suggestions+=("$(printf '{"type":%s,"detail":%s}' \
    "$(echo "$type" | jq -R .)" \
    "$(echo "$detail" | jq -R .)")")
}

# ── Check 1: SKILL.md exists ──
if [[ ! -f "$SKILL_MD" ]]; then
  add_issue "error" "skill-md-exists" "SKILL.md not found in $SKILL_DIR"
  # Can't proceed without SKILL.md
  printf '{"skill":%s,"paradigm_detected":"unknown","issues":[%s],"suggestions":[%s]}\n' \
    "$(echo "$DIR_NAME" | jq -R .)" \
    "$(IFS=,; echo "${issues[*]}")" \
    "$(IFS=,; echo "${suggestions[*]}")"
  exit 0
fi

# Extract frontmatter (between first two --- lines)
frontmatter=$(awk '/^---$/{n++; next} n==1{print} n>=2{exit}' "$SKILL_MD")
body=$(awk 'BEGIN{n=0} /^---$/{n++; if(n==2){p=1; next}} p{print}' "$SKILL_MD")
body_lines=$(echo "$body" | wc -l | tr -d ' ')

# ── Check 2: Frontmatter has name ──
fm_name=$(echo "$frontmatter" | grep -E '^name:\s*' | head -1 | sed 's/^name:\s*//' | tr -d ' ')
if [[ -z "$fm_name" ]]; then
  add_issue "error" "frontmatter-name" "Missing required 'name' field in frontmatter"
else
  # ── Check 3: Name compliance ──
  if [[ ${#fm_name} -gt 64 ]]; then
    add_issue "error" "name-length" "Name '$fm_name' exceeds 64 characters (${#fm_name})"
  fi
  if [[ ! "$fm_name" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]]; then
    add_issue "error" "name-format" "Name '$fm_name' must be lowercase alphanumeric + hyphens, not start/end with hyphen"
  fi
  if [[ "$fm_name" =~ -- ]]; then
    add_issue "error" "name-consecutive-hyphens" "Name '$fm_name' contains consecutive hyphens"
  fi
  if [[ "$fm_name" != "$DIR_NAME" ]]; then
    add_issue "warning" "name-dir-mismatch" "Name '$fm_name' does not match directory name '$DIR_NAME'"
  fi
fi

# ── Check 4: Frontmatter has description ──
# Handle multi-line description (>- or | syntax, or single line)
fm_desc=$(echo "$frontmatter" | awk '
  /^description:/{
    sub(/^description:[ \t]*/, "")
    # Multi-line folded (>) or literal (|) scalar
    if ($0 ~ /^[>|]-?[ \t]*$/) { ml=1; next }
    # Single-line description (possibly quoted)
    gsub(/^["'"'"']|["'"'"']$/, "")
    print; exit
  }
  ml && /^[ \t]/{
    s = $0; sub(/^[ \t]+/, "", s)
    buf = buf ? buf " " s : s
    next
  }
  ml && buf {print buf; exit}
  END {if(ml && buf) print buf}
')
if [[ -z "$fm_desc" ]]; then
  add_issue "error" "frontmatter-description" "Missing required 'description' field in frontmatter"
else
  desc_len=${#fm_desc}
  if [[ $desc_len -gt 1024 ]]; then
    add_issue "warning" "description-length" "Description is $desc_len chars (recommended max 1024)"
  fi
  if [[ $desc_len -lt 20 ]]; then
    add_issue "warning" "description-too-short" "Description is only $desc_len chars — may not trigger reliably"
  fi
fi

# ── Check 5: Body line count ──
if [[ $body_lines -gt 500 ]]; then
  add_issue "warning" "body-too-long" "SKILL.md body is $body_lines lines (recommended <500)"
  add_suggestion "extract-references" "Body exceeds 500 lines — consider splitting domain knowledge into references/"
fi
if [[ $body_lines -gt 1000 ]]; then
  add_issue "error" "body-excessive" "SKILL.md body is $body_lines lines — strongly recommend splitting"
fi

# ── Check 6: Inline bash block count ──
bash_blocks=$(echo "$body" | grep -c '```bash\|```sh\|```shell' || true)
if [[ $bash_blocks -gt 5 ]]; then
  add_issue "warning" "inline-bash-heavy" "Found $bash_blocks inline bash blocks in SKILL.md"
  add_suggestion "extract-scripts" "$bash_blocks inline bash blocks detected — consider extracting deterministic operations to scripts/"
fi

# ── Check 7: Reference chains (anti-pattern #3) ──
# The anti-pattern is "references/a.md → references/b.md → references/c.md" — chains
# of references pointing at each other, forcing agents to follow multi-hop navigation.
# This is about INDIRECTION DEPTH in the progressive-disclosure load path, NOT about
# filesystem nesting. A skill is free to organize references/ into subdirectories as
# long as SKILL.md reaches each reference in a single hop.
#
# Detection scope: ONLY true markdown link syntax `](references/...)`. We deliberately
# do NOT flag bare-text mentions like `see \`references/x.md\`` because:
#   1. Agents are much more likely to follow a markdown link than a prose mention.
#   2. Meta-documentation about the anti-pattern itself (e.g. references/anti-patterns.md
#      explaining "don't do references/a.md → references/b.md") uses backticked prose
#      as examples — flagging those is a self-reference false positive.
if [[ -d "$SKILL_DIR/references" ]]; then
  chain_refs=$(grep -rnE '\]\(references/' "$SKILL_DIR/references" 2>/dev/null | head -5 || true)
  if [[ -n "$chain_refs" ]]; then
    add_issue "warning" "reference-chain" "Found reference→reference markdown links inside references/ — progressive disclosure expects a single hop from SKILL.md, no chains"
  fi
fi

# ── Check 8: Directory naming ──
known_dirs="scripts references assets evals agents templates examples"
while IFS= read -r dir; do
  [[ -z "$dir" ]] && continue
  dirname="$(basename "$dir")"
  is_known=false
  for k in $known_dirs; do
    [[ "$dirname" == "$k" ]] && is_known=true && break
  done
  if ! $is_known; then
    add_issue "info" "nonstandard-dir" "Non-standard directory '$dirname' — consider using scripts/, references/, or assets/"
  fi
done < <(find "$SKILL_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)

# ── Check 9: Self-containment (hardcoded absolute paths) ──
abs_paths=$(echo "$body" | grep -nE '/Users/|/home/|/root/' | head -5 || true)
if [[ -n "$abs_paths" ]]; then
  count=$(echo "$abs_paths" | wc -l | tr -d ' ')
  add_issue "warning" "hardcoded-paths" "Found $count hardcoded absolute path(s) in SKILL.md — skill may not be portable"
fi

# ── Check 10: Script executability ──
if [[ -d "$SKILL_DIR/scripts" ]]; then
  while IFS= read -r script; do
    [[ -z "$script" ]] && continue
    if [[ ! -x "$script" ]]; then
      sname="$(basename "$script")"
      add_issue "warning" "script-not-executable" "scripts/$sname is not executable (missing +x)"
    fi
  done < <(find "$SKILL_DIR/scripts" -type f 2>/dev/null)
fi

# ── Paradigm detection ──
has_scripts=false
has_refs=false
has_assets=false
[[ -d "$SKILL_DIR/scripts" ]] && [[ -n "$(ls -A "$SKILL_DIR/scripts" 2>/dev/null)" ]] && has_scripts=true
[[ -d "$SKILL_DIR/references" ]] && [[ -n "$(ls -A "$SKILL_DIR/references" 2>/dev/null)" ]] && has_refs=true
[[ -d "$SKILL_DIR/assets" ]] && [[ -n "$(ls -A "$SKILL_DIR/assets" 2>/dev/null)" ]] && has_assets=true

if $has_scripts && $has_refs && $has_assets; then
  paradigm="mixed-full"
elif $has_scripts && $has_refs; then
  paradigm="script-driven+reference-doc"
elif $has_scripts; then
  paradigm="script-driven"
elif $has_refs; then
  paradigm="reference-doc"
elif $has_assets; then
  paradigm="asset-bundled"
else
  paradigm="pure-instruction"
fi

# Suggest paradigm upgrades
if [[ "$paradigm" == "pure-instruction" ]]; then
  if [[ $bash_blocks -gt 2 ]]; then
    add_suggestion "upgrade-paradigm" "Currently pure-instruction with $bash_blocks bash blocks — consider upgrading to script-driven"
  fi
  if [[ $body_lines -gt 300 ]]; then
    add_suggestion "upgrade-paradigm" "Currently pure-instruction with $body_lines lines — consider splitting into references/"
  fi
fi

# ── Output JSON ──
printf '{\n'
printf '  "skill": %s,\n' "$(echo "$DIR_NAME" | jq -R .)"
printf '  "paradigm_detected": %s,\n' "$(echo "$paradigm" | jq -R .)"
printf '  "body_lines": %d,\n' "$body_lines"
printf '  "inline_bash_blocks": %d,\n' "$bash_blocks"
printf '  "issues": [\n'
for i in "${!issues[@]}"; do
  printf '    %s' "${issues[$i]}"
  [[ $i -lt $((${#issues[@]} - 1)) ]] && printf ','
  echo
done
printf '  ],\n'
printf '  "suggestions": [\n'
for i in "${!suggestions[@]}"; do
  printf '    %s' "${suggestions[$i]}"
  [[ $i -lt $((${#suggestions[@]} - 1)) ]] && printf ','
  echo
done
printf '  ]\n'
printf '}\n'
