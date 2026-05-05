#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
SKILL_GUIDE="plugins/vibe-iterate/skills/guide"
PASS=0; FAIL=0

run_validate() {
  local schema="$1"; local data="$2"; local should_pass="$3"
  if npx --yes -p ajv-cli@5 -p ajv-formats ajv validate -s "$schema" -d "$data" --spec=draft2019 -c ajv-formats --all-errors >/dev/null 2>&1; then
    if [[ "$should_pass" == "pass" ]]; then echo "PASS  $data vs $schema"; PASS=$((PASS+1)); else echo "FAIL  $data should have failed against $schema"; FAIL=$((FAIL+1)); fi
  else
    if [[ "$should_pass" == "fail" ]]; then echo "PASS  $data correctly rejected by $schema"; PASS=$((PASS+1)); else echo "FAIL  $data should have passed $schema"; FAIL=$((FAIL+1)); fi
  fi
}

# Atlas entries — JSONL, validate line-by-line
while IFS= read -r line; do
  echo "$line" > /tmp/_atlas_entry.json
  run_validate "$SKILL_GUIDE/schemas/atlas-entry.schema.json" /tmp/_atlas_entry.json pass
done < "$SKILL_GUIDE/fixtures/atlas-entry.valid.jsonl"

while IFS= read -r line; do
  echo "$line" > /tmp/_atlas_entry.json
  run_validate "$SKILL_GUIDE/schemas/atlas-entry.schema.json" /tmp/_atlas_entry.json fail
done < "$SKILL_GUIDE/fixtures/atlas-entry.invalid.jsonl"

# Config + radar-cache (added in later tasks)
[[ -f "$SKILL_GUIDE/fixtures/config.valid.json" ]] && run_validate "$SKILL_GUIDE/schemas/config.schema.json" "$SKILL_GUIDE/fixtures/config.valid.json" pass
[[ -f "$SKILL_GUIDE/fixtures/radar-cache.valid.json" ]] && run_validate "$SKILL_GUIDE/schemas/radar-cache.schema.json" "$SKILL_GUIDE/fixtures/radar-cache.valid.json" pass

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
