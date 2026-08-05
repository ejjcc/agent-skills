#!/bin/bash
# Obsidian callout → 飞书 <callout> 转换
# Usage: cat local.md | bash scripts/obsidian-to-lark-callout.sh
# Or: bash scripts/obsidian-to-lark-callout.sh < local.md > /tmp/lark.md

declare -A CALLOUT_MAP=(
  ["warning"]="⚠️|light-orange"
  ["info"]="💡|light-blue"
  ["danger"]="🔴|light-red"
  ["tip"]="✅|light-green"
  ["note"]="📝|light-grey"
  ["success"]="✅|light-green"
  ["question"]="❓|light-orange"
  ["example"]="📋|light-grey"
  ["quote"]="💬|light-grey"
  ["bug"]="🐛|light-red"
  ["abstract"]="📄|light-blue"
  ["todo"]="☑️|light-blue"
  ["caution"]="🔴|light-red"
  ["important"]="❗|light-orange"
)

in_callout=false

while IFS= read -r line || [[ -n "$line" ]]; do
  if [[ "$line" =~ ^\>\ \[!([a-zA-Z]+)\]\ ?(.*) ]]; then
    type="${BASH_REMATCH[1],,}"
    title="${BASH_REMATCH[2]}"

    mapping="${CALLOUT_MAP[$type]:-📝|light-grey}"
    emoji="${mapping%%|*}"
    color="${mapping##*|}"

    if $in_callout; then
      echo ""
      echo "</callout>"
      echo ""
    fi

    echo "<callout emoji=\"$emoji\" background-color=\"$color\" border-color=\"$color\">"
    echo ""
    if [[ -n "$title" ]]; then
      echo "**$title**"
      echo ""
    fi
    in_callout=true
  elif $in_callout && [[ "$line" =~ ^\>\ ?(.*) ]]; then
    echo "${BASH_REMATCH[1]}"
  elif $in_callout; then
    echo ""
    echo "</callout>"
    echo ""
    in_callout=false
    echo "$line"
  else
    echo "$line"
  fi
done

if $in_callout; then
  echo ""
  echo "</callout>"
fi
