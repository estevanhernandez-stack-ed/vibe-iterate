#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
SKILLS_DIR="plugins/vibe-iterate/skills"
PASS=0; FAIL=0

# For each SKILL.md, extract relative-path links (markdown [text](path) and bare paths in backticks)
# Verify each path resolves to an existing file relative to the SKILL's folder

while IFS= read -r -d '' skill; do
  skill_dir="$(dirname "$skill")"
  skill_name="$(basename "$skill_dir")"

  # Match markdown links of the form [text](relative/path) — extract the path
  # Skip http(s) URLs, anchors, and mailto:
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    # Strip any anchor fragment
    path="${path%%#*}"
    [[ -z "$path" ]] && continue
    target="$skill_dir/$path"
    if [[ -e "$target" ]]; then
      echo "PASS  $skill_name -> $path"
      PASS=$((PASS+1))
    else
      echo "FAIL  $skill_name -> $path  (resolves to $target, not found)"
      FAIL=$((FAIL+1))
    fi
  done < <(grep -oE '\]\([^)]+\)' "$skill" | sed -E 's/^\]\(//;s/\)$//' | grep -vE '^https?://|^mailto:|^#')

done < <(find "$SKILLS_DIR" -name SKILL.md -print0)

echo ""
echo "Cross-reference results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
