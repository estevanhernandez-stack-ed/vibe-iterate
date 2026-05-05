# vibe-iterate Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the vibe-iterate plugin shell — the engine, state schemas, shared guide (Ptolemy persona + posture + knowledge sources), and the bare `/vibe-iterate` router. No banner modes or sidecar tools ship in this plan; they land in subsequent plans.

**Architecture:** Pure SKILL-based Claude Code plugin. Markdown SKILL.md files contain the AI instructions; JSON schemas validate the per-project state files (`.vibe-iterate/atlas.jsonl`, `.vibe-iterate/config.json`, `.vibe-iterate/radar.cache.json`). No compiled code. Validation is performed via `ajv-cli` against fixture entries; SKILL cross-references are checked via a bash file-existence script.

**Tech Stack:** Markdown + YAML frontmatter (SKILL files), JSON Schema Draft 2019-09 (state files), `ajv-cli@5` + `ajv-formats` (CLI schema validation, both installed via `npx -p`), bash (test scripts).

> **Tooling note (2026-05-04):** Original plan called for Draft 2020-12, but `ajv-cli@5` doesn't expose `--spec=draft2020` in the CLI (only `draft7` and `draft2019`); the underlying `ajv@8` library supports 2020-12 but only via the `Ajv2020` constructor, not the CLI. For the schema features this plan uses (`enum`, `format`, `additionalProperties`, `required`, type unions), Drafts 2019-09 and 2020-12 are functionally identical, so we use 2019-09 to match the working tooling. `format: date-time` and `format: uri` validation requires the `ajv-formats` add-on; both are installed via `npx --yes -p ajv-cli@5 -p ajv-formats ajv ...`.

---

## Why this plan exists

The Foundation plan is the load-bearing layer for everything else in vibe-iterate. Modes and sidecars in subsequent plans ALL depend on:
- The shared `guide` SKILL (Ptolemy persona, posture, knowledge sources, Atlas conventions, Cart-detection)
- The Atlas/config/radar-cache schemas (so writes from modes are well-formed and reads from sidecars are predictable)
- The bare `/vibe-iterate` router (the entry point users hit when they don't know which mode to use)

If Foundation drifts, every subsequent plan inherits the drift. Lock the contract here.

## Source spec

[`docs/2026-05-04-vibe-iterate-design.md`](../../2026-05-04-vibe-iterate-design.md). Read the *Persona*, *Architecture*, *Cutting-edge knowledge*, *State and file layout*, and *Cross-cutting posture* sections before starting any task — those are the sections this plan implements.

---

## File structure (created/replaced in this plan)

```
plugins/vibe-iterate/skills/guide/
├── SKILL.md                              # REPLACE stub with full guide
├── references/
│   ├── ptolemy-persona.md                # CREATE — persona definition
│   ├── posture.md                        # CREATE — regression-aware/user-trust/small-diff
│   ├── knowledge-sources.md              # CREATE — context7 + scheduled refresh + web fallback
│   ├── cart-detection.md                 # CREATE — Pattern #13 + discovery upsell + heavy threshold
│   └── atlas-conventions.md              # CREATE — write conventions + entry shape
├── schemas/
│   ├── atlas-entry.schema.json           # CREATE — JSON Schema for one Atlas line
│   ├── config.schema.json                # CREATE — JSON Schema for .vibe-iterate/config.json
│   └── radar-cache.schema.json           # CREATE — JSON Schema for .vibe-iterate/radar.cache.json
└── fixtures/
    ├── atlas-entry.valid.jsonl           # CREATE — sample valid Atlas entries
    ├── atlas-entry.invalid.jsonl         # CREATE — sample invalid entries (for negative tests)
    ├── config.valid.json                 # CREATE — sample valid config
    └── radar-cache.valid.json            # CREATE — sample valid radar cache

plugins/vibe-iterate/skills/vibe-iterate/
└── SKILL.md                              # REPLACE stub with full bare-router behavior

tests/
├── validate-schemas.sh                   # CREATE — runs ajv-cli over schemas + fixtures
└── check-skill-references.sh             # CREATE — checks that file paths in SKILL bodies resolve

docs/
└── manual-verification.md                # CREATE — recipe for human-running the bare router

plugins/vibe-iterate/.claude-plugin/
└── plugin.json                           # MODIFY — bump version 0.1.0 → 0.5.0 (after all tasks pass)
```

---

## Task 1: Atlas entry JSON schema

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl`
- Create: `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl`
- Create: `plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json`
- Create: `tests/validate-schemas.sh`

- [ ] **Step 1: Write the valid fixture entries (the "test")**

Create `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl` with three sample lines, one per common case:

```jsonl
{"ts":"2026-05-04T15:30:00Z","mode":"feature-add","outcome":"shipped","title":"Add saved-search feature","rationale":"Top-scored on impact + fit-with-stack; competitor X shipped similar last month and our users requested it 4x in feedback.md.","rejected_runners_up":["dark mode","export to CSV"],"pr":"https://github.com/example/repo/pull/42"}
{"ts":"2026-05-04T16:00:00Z","mode":"competitive","outcome":"rejected","title":"AI-powered tagging","rationale":"Competitor X shipped this; we declined per strategic-relevance rubric — doesn't fit our positioning around manual curation.","rejected_runners_up":[],"pr":null}
{"ts":"2026-05-04T17:15:00Z","mode":"upgrade","outcome":"shipped","title":"Bump react 18.2 → 19.0","rationale":"Security advisory CVE-2026-XXXX; codemod available; tests passed clean.","rejected_runners_up":[],"pr":"https://github.com/example/repo/pull/43"}
```

- [ ] **Step 2: Write the invalid fixture entries**

Create `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl`:

```jsonl
{"mode":"feature-add","outcome":"shipped","title":"missing ts field"}
{"ts":"not-a-valid-timestamp","mode":"feature-add","outcome":"shipped","title":"bad ts format","rationale":"x","rejected_runners_up":[],"pr":null}
{"ts":"2026-05-04T15:30:00Z","mode":"unknown-mode","outcome":"shipped","title":"bad mode enum","rationale":"x","rejected_runners_up":[],"pr":null}
{"ts":"2026-05-04T15:30:00Z","mode":"feature-add","outcome":"maybe","title":"bad outcome enum","rationale":"x","rejected_runners_up":[],"pr":null}
```

- [ ] **Step 3: Write the schema-validation test runner**

Create `tests/validate-schemas.sh` (note: vibe-iterate repo root, not inside plugins/):

```bash
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
```

Make executable: `chmod +x tests/validate-schemas.sh`.

- [ ] **Step 4: Run the test runner — expect FAIL because schemas don't exist yet**

Run: `bash tests/validate-schemas.sh`
Expected: failure with messages like *"unable to read or parse schema atlas-entry.schema.json"*. This is the expected failing state — schema is missing.

- [ ] **Step 5: Write the Atlas entry schema**

Create `plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "https://vibe-iterate.626labs.dev/schemas/atlas-entry.json",
  "title": "Atlas entry",
  "description": "One JSONL line in .vibe-iterate/atlas.jsonl. Append-only ledger of every iteration considered, shipped, rejected.",
  "type": "object",
  "required": ["ts", "mode", "outcome", "title", "rationale", "rejected_runners_up", "pr"],
  "additionalProperties": false,
  "properties": {
    "ts": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 UTC timestamp (e.g., 2026-05-04T15:30:00Z)"
    },
    "mode": {
      "type": "string",
      "enum": ["feature-add", "competitive", "ux-polish", "bug-bash", "ship", "upgrade"],
      "description": "The command the user invoked"
    },
    "outcome": {
      "type": "string",
      "enum": ["shipped", "rejected", "queued"],
      "description": "What happened with this iteration"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "description": "One-line iteration title"
    },
    "rationale": {
      "type": "string",
      "minLength": 1,
      "description": "Why this iteration; why this rank; why these runners-up"
    },
    "rejected_runners_up": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Iteration candidates considered but not picked. May be empty."
    },
    "pr": {
      "type": ["string", "null"],
      "description": "PR URL if outcome == shipped; null otherwise"
    }
  }
}
```

- [ ] **Step 6: Run the test runner — expect PASS**

Run: `bash tests/validate-schemas.sh`
Expected: 7 passes (3 valid Atlas entries pass, 4 invalid Atlas entries are correctly rejected). 0 failures.

- [ ] **Step 7: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json tests/validate-schemas.sh
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "feat(schemas): add Atlas entry JSON schema with validation tests"
```

---

## Task 2: config.json schema

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/fixtures/config.valid.json`
- Create: `plugins/vibe-iterate/skills/guide/schemas/config.schema.json`

- [ ] **Step 1: Write the valid fixture**

Create `plugins/vibe-iterate/skills/guide/fixtures/config.valid.json`:

```json
{
  "category": "AI-powered note-taking app",
  "competitors": [
    "https://www.notion.so/blog/category/product",
    "https://obsidian.md/changelog",
    "https://github.com/logseq/logseq/releases"
  ],
  "framework_pins": [
    { "name": "next", "version": "16.0.3" },
    { "name": "react", "version": "19.0.0" },
    { "name": "tailwindcss", "version": "4.1.2" }
  ],
  "last_inferred_at": "2026-05-04T15:30:00Z"
}
```

- [ ] **Step 2: Run the test runner — expect FAIL**

Run: `bash tests/validate-schemas.sh`
Expected: failure on `config.schema.json` (missing).

- [ ] **Step 3: Write the schema**

Create `plugins/vibe-iterate/skills/guide/schemas/config.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "https://vibe-iterate.626labs.dev/schemas/config.json",
  "title": "vibe-iterate per-project config",
  "description": "Generated by Ptolemy at first run from codebase + README inference; user-editable. Lives at .vibe-iterate/config.json in the host project.",
  "type": "object",
  "required": ["category", "competitors", "framework_pins", "last_inferred_at"],
  "additionalProperties": false,
  "properties": {
    "category": {
      "type": "string",
      "minLength": 1,
      "description": "One-line description of the app's product category, used by Competitive mode and Product Hunt scans"
    },
    "competitors": {
      "type": "array",
      "items": { "type": "string", "format": "uri" },
      "description": "User-curated list of competitor URLs (changelogs, what's-new pages, GH releases). Used by Competitive mode."
    },
    "framework_pins": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "version"],
        "additionalProperties": false,
        "properties": {
          "name": { "type": "string", "minLength": 1 },
          "version": { "type": "string", "minLength": 1 }
        }
      },
      "description": "Framework/SDK pins as scanned from package.json. Used by scheduled radar refresh and :scan-releases."
    },
    "last_inferred_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 timestamp of last codebase+README inference run"
    }
  }
}
```

- [ ] **Step 4: Run the test runner — expect PASS**

Run: `bash tests/validate-schemas.sh`
Expected: prior 7 passes + 1 new pass for `config.valid.json`. 0 failures.

- [ ] **Step 5: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/fixtures/config.valid.json plugins/vibe-iterate/skills/guide/schemas/config.schema.json
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "feat(schemas): add config.json JSON schema"
```

---

## Task 3: radar-cache.json schema

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/fixtures/radar-cache.valid.json`
- Create: `plugins/vibe-iterate/skills/guide/schemas/radar-cache.schema.json`

- [ ] **Step 1: Write the valid fixture**

Create `plugins/vibe-iterate/skills/guide/fixtures/radar-cache.valid.json`:

```json
{
  "refreshed_at": "2026-05-04T14:00:00Z",
  "framework_releases": [
    {
      "package": "next",
      "current_pin": "16.0.0",
      "latest": "16.0.3",
      "highlights": ["Patch: server actions race condition", "Patch: HMR memory leak"],
      "codemod_available": false,
      "breaking": false
    }
  ],
  "competitor_changes": [
    {
      "url": "https://www.notion.so/blog/category/product",
      "fetched_at": "2026-05-04T14:00:00Z",
      "summary": "Notion shipped AI-powered tagging, faster mobile sync, dark mode improvements.",
      "items": ["AI-powered tagging", "Faster mobile sync", "Dark mode improvements"]
    }
  ],
  "product_hunt_buzz": []
}
```

- [ ] **Step 2: Run the test runner — expect FAIL**

Run: `bash tests/validate-schemas.sh`
Expected: failure on `radar-cache.schema.json` (missing).

- [ ] **Step 3: Write the schema**

Create `plugins/vibe-iterate/skills/guide/schemas/radar-cache.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "https://vibe-iterate.626labs.dev/schemas/radar-cache.json",
  "title": "vibe-iterate radar cache",
  "description": "Per-project cache of weekly scheduled refresh. Lives at .vibe-iterate/radar.cache.json in the host project. Read by /vibe-iterate:radar and used as cheap first-pass scan by banner modes.",
  "type": "object",
  "required": ["refreshed_at", "framework_releases", "competitor_changes", "product_hunt_buzz"],
  "additionalProperties": false,
  "properties": {
    "refreshed_at": {
      "type": "string",
      "format": "date-time",
      "description": "When this cache was last refreshed by the schedule plugin's cron"
    },
    "framework_releases": {
      "type": "array",
      "description": "Per-pin diff from current_pin to latest version, with highlights",
      "items": {
        "type": "object",
        "required": ["package", "current_pin", "latest", "highlights", "codemod_available", "breaking"],
        "additionalProperties": false,
        "properties": {
          "package": { "type": "string" },
          "current_pin": { "type": "string" },
          "latest": { "type": "string" },
          "highlights": { "type": "array", "items": { "type": "string" } },
          "codemod_available": { "type": "boolean" },
          "breaking": { "type": "boolean" }
        }
      }
    },
    "competitor_changes": {
      "type": "array",
      "description": "Per-URL summary of recent competitor changelog/what's-new content",
      "items": {
        "type": "object",
        "required": ["url", "fetched_at", "summary", "items"],
        "additionalProperties": false,
        "properties": {
          "url": { "type": "string", "format": "uri" },
          "fetched_at": { "type": "string", "format": "date-time" },
          "summary": { "type": "string" },
          "items": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "product_hunt_buzz": {
      "type": "array",
      "description": "Recent Product Hunt items in the project's category. May be empty.",
      "items": {
        "type": "object",
        "required": ["name", "tagline", "url", "votes"],
        "additionalProperties": false,
        "properties": {
          "name": { "type": "string" },
          "tagline": { "type": "string" },
          "url": { "type": "string", "format": "uri" },
          "votes": { "type": "integer", "minimum": 0 }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Run the test runner — expect PASS**

Run: `bash tests/validate-schemas.sh`
Expected: prior 8 passes + 1 new pass. 0 failures.

- [ ] **Step 5: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/fixtures/radar-cache.valid.json plugins/vibe-iterate/skills/guide/schemas/radar-cache.schema.json
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "feat(schemas): add radar-cache.json JSON schema"
```

---

## Task 4: Ptolemy persona reference doc

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/references/ptolemy-persona.md`

- [ ] **Step 1: Write the reference doc**

Create `plugins/vibe-iterate/skills/guide/references/ptolemy-persona.md`:

```markdown
# Ptolemy — the vibe-iterate persona

Named for Claudius Ptolemy. Author of *Geographia* — the systematic atlas that established the coordinate system, the map projections, and the multi-source synthesis methodology that defined cartography for ~1400 years. Ptolemy worked over already-known territory, not the frontier.

vibe-iterate's agent IS Ptolemy: senior to vibe-cartographer's field-cartographer, multi-source synthesis over already-shipped territory, maintains the Atlas as territory shifts.

## Posture (different from Cart)

Cart is greenfield-optimistic ("ship the thing"). Ptolemy is shipped-product-conservative ("don't break the working bits"). Both belong in the family.

## Defaults baked into Ptolemy

- **Regression-aware** — runs existing tests before opening the PR; surfaces regressions explicitly rather than shipping over them
- **User-trust-aware** — no surprise breaking changes; if behavior users rely on changes, the PR description names it and suggests a deprecation path
- **Small-diff-preferred** — defaults to the smallest diff that delivers the value; reaches for refactor only when refactor IS the value

See [`posture.md`](posture.md) for the full posture reference.

## Posture switch at session-start

Ptolemy reads the brief at the top of every run and explicitly states its register, e.g.:

> *Bug-bash mode → conservative posture, smallest-diff fix, regression checks aggressive.*
> *Feature-add mode → cutting-edge posture, current framework idioms, fit-with-stack scoring.*

Different modes need different brain settings. Making the switch visible at session-start keeps the user oriented.
```

- [ ] **Step 2: Verify the file is well-formed and cross-references resolve**

Run: `test -f plugins/vibe-iterate/skills/guide/references/ptolemy-persona.md && grep -q "posture.md" plugins/vibe-iterate/skills/guide/references/ptolemy-persona.md && echo OK`
Expected: `OK` printed (the file exists and references `posture.md`, which we'll create in Task 5).

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/references/ptolemy-persona.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "docs(guide): add Ptolemy persona reference"
```

---

## Task 5: Posture reference doc

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/references/posture.md`

- [ ] **Step 1: Write the reference doc**

Create `plugins/vibe-iterate/skills/guide/references/posture.md`:

```markdown
# Posture — shipped-product-conservative defaults

Ptolemy's three posture defaults, applied across every banner mode and sidecar tool.

## 1. Regression-aware

**Rule:** Run existing tests before opening the PR. If a regression surfaces, surface it explicitly — don't ship over it.

**How to apply:**
- Detect the test runner from `package.json` scripts (`test`, `test:unit`, `test:e2e`) or from the framework (jest, vitest, playwright, pytest, go test)
- Run the full pre-existing suite before any code changes
- Run it again after the changes
- Diff the results. Net new failures = regressions
- If regressions found: PR description must name them, propose a fix (in this PR or a follow-up), and ask the user to acknowledge before merging

## 2. User-trust-aware

**Rule:** No surprise breaking changes. If the iteration alters behavior users rely on, the PR description names it explicitly and suggests a deprecation path.

**How to apply:**
- Identify "user-facing surface": API endpoints, CLI flags, config keys, exported types/functions, UI flows users complete repeatedly
- For each change, ask: would a user who relied on this surface notice a difference?
- If yes, the PR description has a `## Breaking changes` section listing each change and a `## Migration path` section
- For library/API code: prefer adding a new function/option to changing an existing signature; mark old as `@deprecated` with a sunset note rather than removing immediately

## 3. Small-diff-preferred

**Rule:** Default to the smallest diff that delivers the value. Reach for refactor only when refactor IS the value.

**How to apply:**
- Before writing code, ask: what's the minimum change that adds the feature / fixes the bug?
- Resist the urge to clean up adjacent code unless the cleanup is required for the change to land cleanly
- If a refactor IS warranted (the existing structure can't accommodate the change without ugliness), do the refactor in a separate commit within the same PR — title-prefixed `refactor(scope): ...` so the diff is reviewable in two reads
- Avoid rewriting tests unless they're broken by the change. Add new tests for new behavior; don't churn existing tests

## Why this posture exists

Cart is greenfield-optimistic — "ship the thing" energy is right when there's nothing to break. Ptolemy works on shipped territory where users are present. The cost of breaking working flows is high; the value of small surgical wins compounds. Different posture, different defaults.
```

- [ ] **Step 2: Verify the file is well-formed**

Run: `test -f plugins/vibe-iterate/skills/guide/references/posture.md && wc -l plugins/vibe-iterate/skills/guide/references/posture.md`
Expected: File exists, prints a line count >= 30.

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/references/posture.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "docs(guide): add posture reference (regression/user-trust/small-diff)"
```

---

## Task 6: Knowledge sources reference doc

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/references/knowledge-sources.md`

- [ ] **Step 1: Write the reference doc**

Create `plugins/vibe-iterate/skills/guide/references/knowledge-sources.md`:

```markdown
# Knowledge sources — how Ptolemy stays cutting-edge

Three layers, in priority order at decision-time.

## 1. context7 MCP (primary, live)

**When to use:** at decision-time, whenever the agent reaches for "is there a current way to do X in [framework]?"

**Why:** context7 returns fresh framework docs (Next, React, Tailwind, Prisma, Express, Django, etc.) that may differ from training-data knowledge. Even for libraries the agent thinks it knows, context7 is preferred over web search for library-specific syntax, configuration, and migration questions.

**Usage:** call `mcp__context7__resolve-library-id` to get the canonical library ID, then `mcp__context7__query-docs` with the question.

**Fallback if missing:** if the user doesn't have the context7 MCP configured, fall through to layer 3 (web search).

## 2. Scheduled refresh cache (primary, fast)

**When to use:** whenever a banner mode or sidecar wants the "what's new" picture for the project's stack and competitor set, BEFORE doing any live lookup. The cache is the cheap first-pass scan.

**Where it lives:** `.vibe-iterate/radar.cache.json` in the host project. Schema: `skills/guide/schemas/radar-cache.schema.json`.

**How it gets refreshed:** weekly job via the `schedule` plugin's cron. The job reads `.vibe-iterate/config.json` for `framework_pins[]` and `competitors[]`, queries each, and writes the cache.

**Read pattern:**
- `:radar` reads the cache directly and renders a digest
- Banner modes read the cache as their first move; if cache is stale (>14 days) or missing, surface a one-line nudge: *"Radar cache is stale (last refreshed YYYY-MM-DD). Run `/vibe-iterate:radar` after the next scheduled refresh, or invoke a manual refresh."*

## 3. Web search (fallback)

**When to use:** when context7 doesn't cover the library, or context7 is unavailable, OR when the question is about something context7 doesn't index (Product Hunt category trends, competitor blog posts, HN/Reddit discussions about similar apps).

**Usage:** the standard `WebSearch` and `WebFetch` tools.

**Quality bar:** prefer official sources (vendor changelogs, release notes, GH releases) over secondary commentary. Cite the URL when surfacing a finding to the user.

## Anti-patterns

- **Don't** rely on training-data knowledge alone for "what's the current X?" — even when you're confident. Use context7 or web search to verify.
- **Don't** scrape competitor URLs at every banner-mode invocation. The cache exists for a reason; use it.
- **Don't** lean on web search when context7 covers the library. context7 is faster, more reliable, and fewer ambiguous matches.
```

- [ ] **Step 2: Verify the file is well-formed**

Run: `test -f plugins/vibe-iterate/skills/guide/references/knowledge-sources.md && grep -c "^##" plugins/vibe-iterate/skills/guide/references/knowledge-sources.md`
Expected: File exists, prints `4` (four `##` headings).

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/references/knowledge-sources.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "docs(guide): add knowledge sources reference (context7/refresh/web)"
```

---

## Task 7: Cart-detection reference doc

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/references/cart-detection.md`

- [ ] **Step 1: Write the reference doc**

Create `plugins/vibe-iterate/skills/guide/references/cart-detection.md`:

```markdown
# Cart-detection — Pattern #13 with discovery upsell

vibe-iterate composes with vibe-cartographer when Cart is installed; works standalone when it's not. This doc defines the detection logic, the delegation pattern, and the discovery upsell.

## Default — own build muscle

vibe-iterate ships the PR itself, with build muscle intentionally lighter than Cart's full `/scope → /prd → /spec → /build` flow. Works without Cart installed. This is the always-on baseline.

## Cart-present enhancement

**Detection:** at the start of every banner-mode invocation, check whether Cart's namespace is available. Concretely: scan the available-skills list (surfaced in each turn's system reminder) for `vibe-cartographer:*` entries. If any resolve, Cart is installed. This is read-only and has zero side effects — never invoke a Cart skill as a probe; that would actually start the skill's flow (e.g., `vibe-cartographer:scope` would launch a scope interview and write `scope.md`).

If Cart is installed AND the iteration is heavy (see "Heavy iteration threshold" below), delegate the planning chunks:
1. Hand the iteration brief to `vibe-cartographer:scope`
2. Take its output, hand to `vibe-cartographer:prd`
3. Take its output, hand to `vibe-cartographer:spec`
4. Take Cart's spec back, run vibe-iterate's own build phase against it
5. Cart owns the planning; vibe-iterate owns the build + commit shape

## Cart-missing discovery beat

If Cart is NOT installed AND the iteration is heavy, surface this exact one-line nudge BEFORE proceeding:

> *"This iteration touches [specific reasons — e.g., 3 subsystems, introduces a new domain concept, estimated >1 day]. Cart's structured `/scope → /prd → /spec` flow would be a stronger fit. Install vibe-cartographer (`/plugin install vibe-cartographer`), or proceed with vibe-iterate's lighter flow?"*

This is a discovery upsell, NEVER a hard block. If the user proceeds, vibe-iterate runs its own build muscle. If the user installs Cart and re-invokes, the next run takes the delegation path.

## "Heavy iteration" threshold (judgment call)

Ptolemy decides at brief-time. v1.0 leans toward under-delegation — default to own muscle, escalate only when clearly heavy.

Heuristic (any one triggers the discovery beat):
- Touches **3 or more subsystems** (e.g., API + UI + auth + data layer)
- Introduces **a new domain concept** that needs its own data shape, table, or model
- Estimated **>1 day of focused work** if a senior engineer did it manually

Below this bar: ship solo. At or above: delegate (if Cart present) or surface upsell (if Cart missing).

## Anti-patterns

- **Don't** hard-fail when Cart is missing. The plugin must work standalone.
- **Don't** auto-install Cart on the user's behalf. Surface the upsell, let the user decide.
- **Don't** delegate every iteration to Cart "just to be safe." The delegation path is for genuinely heavy work — over-delegating creates ceremony for surgical changes.
```

- [ ] **Step 2: Verify the file is well-formed**

Run: `test -f plugins/vibe-iterate/skills/guide/references/cart-detection.md && grep -q "Heavy iteration" plugins/vibe-iterate/skills/guide/references/cart-detection.md && echo OK`
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/references/cart-detection.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "docs(guide): add Cart-detection reference (Pattern #13 + discovery upsell)"
```

---

## Task 8: Atlas conventions reference doc

**Files:**
- Create: `plugins/vibe-iterate/skills/guide/references/atlas-conventions.md`

- [ ] **Step 1: Write the reference doc**

Create `plugins/vibe-iterate/skills/guide/references/atlas-conventions.md`:

```markdown
# Atlas conventions

The Atlas is the per-project ledger of every iteration vibe-iterate has considered, shipped, or rejected. Lives at `.vibe-iterate/atlas.jsonl` in the host project. JSONL — one JSON object per line, append-only, never edited.

## Why the Atlas exists

- **Don't re-propose the same thing twice.** Modes read the Atlas before scoring candidates; recently rejected items are demoted.
- **Build a navigable history.** Future-you (or a teammate) can scan the file and understand what was tried, what shipped, what was passed on, and why.
- **Compose with other plugins.** vibe-doc / vibe-test / vibe-sec can read the Atlas to scope their work to recently changed surfaces.

## Entry shape

See [`../schemas/atlas-entry.schema.json`](../schemas/atlas-entry.schema.json) for the canonical schema. Fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `ts` | ISO-8601 datetime | yes | UTC; when the entry was written |
| `mode` | enum | yes | `feature-add` \| `competitive` \| `ux-polish` \| `bug-bash` \| `ship` \| `upgrade` |
| `outcome` | enum | yes | `shipped` \| `rejected` \| `queued` |
| `title` | string | yes | One-line iteration title |
| `rationale` | string | yes | Why this iteration; why this outcome |
| `rejected_runners_up` | string array | yes | Iteration candidates considered but not picked. Empty array when N/A |
| `pr` | string \| null | yes | PR URL when `outcome == "shipped"`, else null |

## Write rules

- **Append-only.** Never edit existing lines; never delete the file. If a correction is needed, append a new entry that supersedes (with rationale referencing the prior entry).
- **One entry per banner-mode or sidecar invocation that ships, rejects, or queues something.** Read-only sidecars (`:radar`, `:spy`, `:scan-releases`, `:rate`) do NOT write Atlas entries.
- **Validate before write.** Read the schema (or use the in-plugin reference at `../schemas/atlas-entry.schema.json`); ensure required fields are present and enums are correct. A malformed entry corrupts the ledger for everyone downstream.
- **Atomic write.** If using a file API, prefer line-buffered append. Don't read-modify-write the whole file (race risk).

## Read patterns

- **Recent-rejection check.** When scoring a new candidate, scan the last N entries (default: 30 days) for `outcome == "rejected"` matches; demote if matched.
- **What-shipped review.** `/vibe-iterate` (bare router) reads the last K shipped entries to ground its mode recommendation.
- **Cross-plugin scope.** Other 626Labs plugins MAY read the Atlas to scope work; they MUST treat it as read-only.

## Privacy

The Atlas stays local to the project. **No telemetry, no phone-home.** If a user wants to share their Atlas (e.g., for a debrief), that's a manual `cat .vibe-iterate/atlas.jsonl` away. Per Este's standing rule: vibe-iterate emits no usage pings.
```

- [ ] **Step 2: Verify the file is well-formed**

Run: `test -f plugins/vibe-iterate/skills/guide/references/atlas-conventions.md && grep -q "atlas-entry.schema.json" plugins/vibe-iterate/skills/guide/references/atlas-conventions.md && echo OK`
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/references/atlas-conventions.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "docs(guide): add Atlas conventions reference (entry shape, write rules, read patterns)"
```

---

## Task 9: SKILL cross-reference checker

**Files:**
- Create: `tests/check-skill-references.sh`

- [ ] **Step 1: Write the checker script**

Create `tests/check-skill-references.sh`:

```bash
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
```

Make executable: `chmod +x tests/check-skill-references.sh`.

- [ ] **Step 2: Run the checker — expect PASS against the existing stub references**

Run: `bash tests/check-skill-references.sh`
Expected: all current SKILL stubs reference `../guide/SKILL.md` and `../../../../docs/2026-05-04-vibe-iterate-design.md`. All should resolve. 0 failures.

If FAIL: a stub has a broken cross-reference. Fix the path in the offending SKILL.md before continuing.

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add tests/check-skill-references.sh
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "test: add SKILL cross-reference checker"
```

---

## Task 10: Replace guide SKILL.md stub with full content

**Files:**
- Modify: `plugins/vibe-iterate/skills/guide/SKILL.md` (replace entire content)

- [ ] **Step 1: Write the full guide SKILL**

Replace the contents of `plugins/vibe-iterate/skills/guide/SKILL.md` with:

```markdown
---
name: guide
description: "Shared behavior for vibe-iterate commands — Ptolemy persona, posture (regression-aware/user-trust-aware/small-diff-preferred), knowledge sources (context7 + scheduled refresh + web fallback), Atlas write conventions, Cart-detection pattern. Referenced by every command SKILL."
---

# vibe-iterate guide — shared agent behavior (Ptolemy)

This skill is **referenced by every command SKILL**, never invoked directly. It defines the persona, posture, knowledge sources, and shared conventions that all banner modes and sidecar tools inherit. Read every reference doc below before starting any command-level work.

## Reference docs (read all of these)

- [`references/ptolemy-persona.md`](references/ptolemy-persona.md) — who Ptolemy is, how Ptolemy differs from Cart's persona, posture-switch announcement at session-start
- [`references/posture.md`](references/posture.md) — regression-aware, user-trust-aware, small-diff-preferred. The three defaults applied across every mode and sidecar
- [`references/knowledge-sources.md`](references/knowledge-sources.md) — context7 MCP, scheduled-refresh cache, web-search fallback. How Ptolemy stays cutting-edge on big-shoulder software
- [`references/cart-detection.md`](references/cart-detection.md) — Pattern #13 deferral, discovery upsell when Cart's missing, "heavy iteration" threshold
- [`references/atlas-conventions.md`](references/atlas-conventions.md) — Atlas write rules, entry shape, read patterns

## State files (per host project, under `.vibe-iterate/`)

- `atlas.jsonl` — append-only ledger. Schema: [`schemas/atlas-entry.schema.json`](schemas/atlas-entry.schema.json)
- `config.json` — competitors, category, framework_pins. Schema: [`schemas/config.schema.json`](schemas/config.schema.json)
- `radar.cache.json` — weekly scheduled-refresh output. Schema: [`schemas/radar-cache.schema.json`](schemas/radar-cache.schema.json)
- `feedback.md` — user-maintained escape-hatch internal-signal source for v1.0 (Bug-bash mode reads this; no schema — freeform markdown)

If a command writes any of these files, validate the write against the schema first. Malformed writes corrupt the ledger and break downstream consumers.

## Cross-plugin requirements (vibe-iterate v1.0)

| Plugin | Required? | Role |
|---|---|---|
| `schedule` | Required | Powers the weekly radar refresh |
| `vibe-cartographer` | Optional (auto-detected) | Heavy-iteration delegation target via Pattern #13 |
| `context7` (MCP) | Optional (auto-detected) | Live framework-docs lookups at decision-time |

For optional plugins: detect at command start, branch behavior based on availability. Never hard-fail when an optional plugin is absent. See `references/cart-detection.md` for the Cart-specific pattern; the optional-plugin detection technique generalizes, the delegation flow does not.

Note: `schedule` becomes load-bearing in Plan 4 (radar refresh); banner modes and sidecars in earlier plans work without it.

## Hard rules (do not violate without explicit user opt-in)

- **No telemetry.** Per Este's standing rule, vibe-iterate emits no usage pings, no opt-in metrics, no phone-home. Atlas data stays local.
- **No auto-fire.** No mode runs without explicit user invocation. The agent only proposes; the user kicks off.
- **No silent scope expansion.** If a banner mode discovers the iteration is heavier than initially briefed, surface that to the user (and trigger Cart-detection); don't quietly expand into a multi-PR sprawl.
- **No surprise breaking changes.** Changes to user-facing surfaces are named in the PR description with a deprecation/migration path. See `references/posture.md` § User-trust-aware.
```

- [ ] **Step 2: Run cross-reference checker — expect PASS**

Run: `bash tests/check-skill-references.sh`
Expected: all references in the new guide SKILL resolve (5 reference docs + 3 schemas). 0 failures.

If FAIL: a reference path is wrong. Fix and re-run.

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/guide/SKILL.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "feat(guide): replace stub with full shared-behavior SKILL"
```

---

## Task 11: Replace bare-router SKILL.md stub with full content

**Files:**
- Modify: `plugins/vibe-iterate/skills/vibe-iterate/SKILL.md` (replace entire content)

- [ ] **Step 1: Write the full bare-router SKILL**

Replace the contents of `plugins/vibe-iterate/skills/vibe-iterate/SKILL.md` with:

```markdown
---
name: vibe-iterate
description: "This skill should be used when the user says `/vibe-iterate` (bare, no subcommand). Reads project state (Atlas, radar cache, recent commits), recommends a mode for the moment (feature-add, competitive, ux-polish, bug-bash), and asks before launching. Never auto-fires."
---

# /vibe-iterate — bare router

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources, Atlas conventions, Cart-detection), then follow this command.

## What this command does

Bare router. The user invoked `/vibe-iterate` with no subcommand — they want help choosing a mode. The agent's job is to:

1. Read the project's current state (Atlas, radar cache, recent commits, branch state, presence of `feedback.md`)
2. Synthesize: what's the most useful mode RIGHT NOW for this project?
3. Recommend ONE mode with rationale
4. Surface 1-2 alternatives, with rationale for why they're second/third
5. Ask the user to confirm before launching anything

## Hard rules

- **Never auto-fire a mode.** Always ask the user before invoking another command.
- **Read-only by default.** This command does NOT write to the Atlas, the config, or any project file.
- **One recommendation, with alternatives.** Don't surface a 5-mode menu; that's not a recommendation.

## Project state to read (in order)

1. **Atlas (`.vibe-iterate/atlas.jsonl`).** If absent, this is a first run — flag it ("First-time vibe-iterate run on this project. I'll need to infer your category and competitors before any banner mode can run productively.").
2. **Config (`.vibe-iterate/config.json`).** If absent or `last_inferred_at` is >30 days old, suggest re-inference as a separate first move.
3. **Radar cache (`.vibe-iterate/radar.cache.json`).** If absent or `refreshed_at` is >14 days old, suggest a `/vibe-iterate:radar` refresh as a follow-up.
4. **Recent commits.** Last 10 on the current branch. What's been shipped recently?
5. **Branch state.** On `main`? On a feature branch? Any uncommitted changes?
6. **`feedback.md` presence.** If present, surface it as input for Bug-bash candidate.

## Mode recommendation logic

Pick ONE based on the strongest signal:

| Signal | Recommend |
|---|---|
| `feedback.md` exists with unaddressed items, AND last Atlas-shipped item was >7 days ago | **bug-bash** — users have things to say, address them |
| Radar cache shows >3 framework releases since last shipped iteration | **feature-add** — fresh framework features may unblock prioritized items |
| Radar cache shows competitor changelogs with new items in user's category | **competitive** — gap-close opportunity |
| Recent commits show 3+ feature lands but no polish PRs | **ux-polish** — the surfaces are getting rough |
| Atlas shows >5 recent shipped entries, no rejected ones | **(soft suggest)** review the Atlas; you may be over-shipping without considering tradeoffs |
| First run, config not yet inferred | **(meta)** "Let me infer your category and competitors first — confirm to proceed?" |

When two signals tie, prefer the mode the user has invoked LEAST recently (per Atlas history).

## Output shape

Render the recommendation in this structure:

```
**Recommendation:** /vibe-iterate:<mode>

Why:
- [signal 1, with one-line evidence]
- [signal 2, with one-line evidence]

Alternatives:
- /vibe-iterate:<other-mode-1> — [why this is second]
- /vibe-iterate:<other-mode-2> — [why this is third]

Project state:
- Atlas: <N entries, last shipped YYYY-MM-DD>
- Config: <inferred YYYY-MM-DD>
- Radar cache: <refreshed YYYY-MM-DD>
- Branch: <main or feature/...>
- feedback.md: <present|absent>

Run /vibe-iterate:<mode>? (yes / pick alternative / not now)
```

Wait for the user's response. Do NOT invoke any subcommand on your own.
```

- [ ] **Step 2: Run cross-reference checker — expect PASS**

Run: `bash tests/check-skill-references.sh`
Expected: bare-router SKILL references `../guide/SKILL.md` only. Should resolve. 0 failures.

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/skills/vibe-iterate/SKILL.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "feat(router): replace stub with full bare-router behavior"
```

---

## Task 12: Manual-verification recipe doc

**Files:**
- Create: `docs/manual-verification.md`

The plugin can't auto-test "does Claude Code load this and route correctly?" — that's a human-in-the-loop verification. Document the recipe so it's repeatable.

- [ ] **Step 1: Write the recipe doc**

Create `docs/manual-verification.md`:

```markdown
# Manual verification — vibe-iterate v0.5.0 Foundation

The plugin's "load + route correctly" behavior must be verified by invoking it in a real Claude Code session. This recipe is repeatable — run it after any change to the bare router or guide SKILL.

## Prerequisites

- Claude Code installed
- Local clone of vibe-iterate at `c:/Users/estev/Projects/vibe-iterate`
- A scratch project to test against (any repo with a `package.json` works; Cart's own repo is a fine test target)

## Setup — install the plugin from local

In a terminal:

```bash
cd <your-scratch-project>
# Install vibe-iterate from local path (canary-style, dev install)
/plugin marketplace add c:/Users/estev/Projects/vibe-iterate
/plugin install vibe-iterate
```

## Verification 1 — bare router on a first-run project

Goal: confirm `/vibe-iterate` recognizes a first-run state (no `.vibe-iterate/` dir) and surfaces the inference prompt instead of recommending a banner mode.

Steps:
1. In the scratch project, ensure no `.vibe-iterate/` directory exists (`ls .vibe-iterate 2>/dev/null` → empty)
2. In Claude Code: `/vibe-iterate`
3. Expected: agent surfaces a "first-time run, infer category and competitors" prompt; does NOT auto-fire any mode

Pass criteria:
- Output mentions first-run state explicitly
- Agent asks before doing any mode-level work
- No files have been created or modified

## Verification 2 — bare router on a project with state

Goal: confirm `/vibe-iterate` reads existing state and produces a mode recommendation with rationale.

Steps:
1. In the scratch project, create `.vibe-iterate/config.json` from the fixture: `cp <vibe-iterate-repo>/plugins/vibe-iterate/skills/guide/fixtures/config.valid.json .vibe-iterate/config.json`
2. Create `.vibe-iterate/atlas.jsonl` from the fixture: `cp <vibe-iterate-repo>/plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl .vibe-iterate/atlas.jsonl`
3. (Optional) Create `feedback.md` at the project root with one or two reported issues to test bug-bash signal detection
4. In Claude Code: `/vibe-iterate`
5. Expected output structure (verbatim section names; content varies based on signals):

```
Recommendation: /vibe-iterate:<mode>
Why:
- ...
- ...
Alternatives:
- ...
Project state:
- Atlas: <N entries, last shipped YYYY-MM-DD>
- Config: <inferred YYYY-MM-DD>
- Radar cache: <absent|refreshed YYYY-MM-DD>
- Branch: <name>
- feedback.md: <present|absent>

Run /vibe-iterate:<mode>? (yes / pick alternative / not now)
```

Pass criteria:
- All five section labels present (`Recommendation`, `Why`, `Alternatives`, `Project state`, prompt line)
- Recommendation matches the strongest signal per the logic in `skills/vibe-iterate/SKILL.md`
- Agent waits for user input before doing anything else

## Verification 3 — guide SKILL is referenced and read

Goal: confirm the bare router actually reads the guide before responding (i.e., posture and Cart-detection are in scope).

Steps:
1. In Claude Code, with no `.vibe-iterate/` state in the scratch project, run `/vibe-iterate`
2. Mid-response, look for any of these markers (the guide influencing output):
   - Mention of "Ptolemy" or "shipped-product-conservative posture"
   - Reference to context7 / radar cache / weekly refresh
   - Reference to `vibe-cartographer` (Cart-detection beat)

Pass criteria: at least one marker appears (the guide is being read). If NO markers appear, the bare router probably isn't reading the guide — fix the SKILL reference and re-test.

## Recording results

After each verification run, append a line to `docs/manual-verification-log.md` (create if missing):

```
2026-MM-DD  v0.5.0  Verif 1 PASS / Verif 2 PASS / Verif 3 PASS  notes: ...
```

This is the historical record of which versions passed verification. Future plans (modes, sidecars) will add their own verification recipes to this same doc.
```

- [ ] **Step 2: Verify the file is well-formed**

Run: `test -f docs/manual-verification.md && grep -c "^## Verification" docs/manual-verification.md`
Expected: prints `3` (three verification sections).

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add docs/manual-verification.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "docs: add manual-verification recipe for v0.5.0 Foundation"
```

---

## Task 13: Bump version to v0.5.0 and tag

**Files:**
- Modify: `plugins/vibe-iterate/.claude-plugin/plugin.json` (bump `version` field)
- Modify: `README.md` (update Status section)

- [ ] **Step 1: Run all tests as a final check**

Run: `bash tests/validate-schemas.sh && bash tests/check-skill-references.sh`
Expected: both scripts print `0 failed`.

If anything fails, STOP. Fix the failure, re-run, then proceed.

- [ ] **Step 2: Bump plugin.json version**

Modify `plugins/vibe-iterate/.claude-plugin/plugin.json`: change `"version": "0.1.0"` to `"version": "0.5.0"`.

- [ ] **Step 3: Update README Status section**

Modify `README.md`. Replace the existing `## Status` section with:

```markdown
## Status

**v0.5.0 — Foundation.** Plugin shell loads, schemas validate, bare `/vibe-iterate` router works (reads project state, recommends a mode, asks before launching). No banner modes or sidecar tools yet — they land in Plan 2 onward. See [`docs/2026-05-04-vibe-iterate-design.md`](docs/2026-05-04-vibe-iterate-design.md) for the locked design and [`docs/superpowers/plans/`](docs/superpowers/plans/) for implementation plans.
```

- [ ] **Step 4: Manually run Verification 1 from `docs/manual-verification.md`**

This is a human step, NOT automated. Open Claude Code in a scratch project, install vibe-iterate locally, run `/vibe-iterate` against a fresh state. Confirm Verification 1 passes per the recipe in `docs/manual-verification.md`.

If Verification 1 fails, do NOT tag. Fix the bare router or guide, re-test.

- [ ] **Step 5: Append to manual verification log**

Create `docs/manual-verification-log.md` if it doesn't exist (write a one-line header `# Manual verification log` + blank line). Append:

```
2026-MM-DD  v0.5.0  Verif 1 PASS  notes: foundation only; Verif 2 and 3 deferred until project has Atlas+config fixtures (next plan)
```

(Use today's date in YYYY-MM-DD form.)

- [ ] **Step 6: Commit, tag, push**

```bash
git -C "c:/Users/estev/Projects/vibe-iterate" add plugins/vibe-iterate/.claude-plugin/plugin.json README.md docs/manual-verification-log.md
git -C "c:/Users/estev/Projects/vibe-iterate" commit -m "release: v0.5.0 Foundation — plugin shell, schemas, guide, bare router"
git -C "c:/Users/estev/Projects/vibe-iterate" tag v0.5.0
git -C "c:/Users/estev/Projects/vibe-iterate" push origin main
git -C "c:/Users/estev/Projects/vibe-iterate" push origin v0.5.0
```

- [ ] **Step 7: Verify tag is live on origin**

Run: `gh api repos/estevanhernandez-stack-ed/vibe-iterate/git/refs/tags/v0.5.0`
Expected: JSON object with the tag's SHA. If 404, the tag didn't push — re-run `git push origin v0.5.0`.

---

## End of plan

After Task 13, vibe-iterate is at v0.5.0 — Foundation complete. Plugin shell loads in Claude Code, schemas validate, the bare router routes. No banner modes or sidecars yet.

**Next plans (in order):**
1. Plan 2 — first end-to-end mode (`:ship` sidecar + `:rate` sidecar)
2. Plan 3 — banner modes (feature-add, competitive, ux-polish, bug-bash) + `:radar`, `:spy`
3. Plan 4 — remaining sidecars (`:scan-releases`, `:upgrade`) + Cart-detection enhancement + scheduled radar via `schedule` plugin + v1.0 polish

Each plan is its own writing-plans run against this same source spec.

## Decision-log moment

After v0.5.0 ships, log a decision via `mcp__626Labs__manage_decisions log`:
- title: "vibe-iterate v0.5.0 Foundation shipped"
- rationale: "Plugin shell, schemas, shared guide, bare router live. Modes/sidecars to follow in subsequent plans."
- tag with the bound 626Labs project ID for vibe-iterate (create the project first if it doesn't exist)
