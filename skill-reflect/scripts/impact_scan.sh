#!/usr/bin/env bash
# Impact scanner: find all files referencing a keyword across skills, rules, and CLAUDE.md
# Usage: impact_scan.sh <skill-name> [keyword ...]
# If no keywords given, uses the skill name as keyword.

set -euo pipefail

CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
RULES_DIR="$CLAUDE_DIR/rules"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

if [[ $# -lt 1 ]]; then
  echo '{"error": "Usage: impact_scan.sh <skill-name> [keyword ...]"}' >&2
  exit 1
fi

SKILL_NAME="$1"
shift

# Build keyword list: explicit args, or fall back to skill name
if [[ $# -gt 0 ]]; then
  KEYWORDS=("$@")
else
  KEYWORDS=("$SKILL_NAME")
fi

echo "{"
echo "  \"skill\": \"$SKILL_NAME\","
echo "  \"keywords\": $(printf '%s\n' "${KEYWORDS[@]}" | jq -R . | jq -s .),"
echo "  \"matches\": ["

first_match=true

for keyword in "${KEYWORDS[@]}"; do
  # Search skills/ (exclude the target skill itself)
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    # Skip the target skill's own files
    if [[ "$file" == *"/skills/$SKILL_NAME/"* ]]; then
      continue
    fi
    lines=$(grep -n "$keyword" "$file" 2>/dev/null || true)
    [[ -z "$lines" ]] && continue
    while IFS= read -r line; do
      lineno="${line%%:*}"
      content="${line#*:}"
      $first_match || echo ","
      first_match=false
      printf '    {"file": %s, "line": %s, "keyword": %s, "content": %s}' \
        "$(echo "$file" | jq -R .)" \
        "$lineno" \
        "$(echo "$keyword" | jq -R .)" \
        "$(echo "$content" | jq -R .)"
    done <<< "$lines"
  done < <(grep -rl "$keyword" "$SKILLS_DIR" 2>/dev/null || true)

  # Search rules/
  if [[ -d "$RULES_DIR" ]]; then
    while IFS= read -r file; do
      [[ -z "$file" ]] && continue
      lines=$(grep -n "$keyword" "$file" 2>/dev/null || true)
      [[ -z "$lines" ]] && continue
      while IFS= read -r line; do
        lineno="${line%%:*}"
        content="${line#*:}"
        $first_match || echo ","
        first_match=false
        printf '    {"file": %s, "line": %s, "keyword": %s, "content": %s}' \
          "$(echo "$file" | jq -R .)" \
          "$lineno" \
          "$(echo "$keyword" | jq -R .)" \
          "$(echo "$content" | jq -R .)"
      done <<< "$lines"
    done < <(grep -rl "$keyword" "$RULES_DIR" 2>/dev/null || true)
  fi

  # Search CLAUDE.md
  if [[ -f "$CLAUDE_MD" ]]; then
    lines=$(grep -n "$keyword" "$CLAUDE_MD" 2>/dev/null || true)
    if [[ -n "$lines" ]]; then
      while IFS= read -r line; do
        lineno="${line%%:*}"
        content="${line#*:}"
        $first_match || echo ","
        first_match=false
        printf '    {"file": %s, "line": %s, "keyword": %s, "content": %s}' \
          "$(echo "$CLAUDE_MD" | jq -R .)" \
          "$lineno" \
          "$(echo "$keyword" | jq -R .)" \
          "$(echo "$content" | jq -R .)"
      done <<< "$lines"
    fi
  fi
done

echo ""
echo "  ]"
echo "}"
