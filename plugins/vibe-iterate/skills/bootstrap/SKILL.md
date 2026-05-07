---
name: bootstrap
description: "Internal SKILL — invoked by the bare router on first run, or directly when the user says 'set up vibe-iterate', 'init vibe-iterate', or '/vibe-iterate:bootstrap'. Identifies the app type, confirms with the user, infers framework pins from package.json, asks for competitor URLs, and writes .vibe-iterate/config.json. Idempotent — re-runnable to refresh stale config."
---

# /vibe-iterate:bootstrap — set up the lay of the land

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources, Atlas conventions), then follow this command.

## What this command does

Bootstrap. The repo doesn't have a `.vibe-iterate/` directory yet (or its `config.json` is stale), so the agent doesn't know what app this is, who you compete with, or which framework pins to track. The agent's job is to:

1. **Auto-classify the app type** by reading the codebase (`package.json`, `README.md`, top-level dirs, presence of `.claude-plugin/`, etc.) — don't ask if you can infer.
2. **Confirm classification** with the user in ONE short question. Surface the inference; let them correct.
3. **Auto-extract framework pins** from `package.json` (or pyproject.toml / Cargo.toml / etc., depending on stack).
4. **Ask the user for competitor URLs** — this is the only thing Ptolemy can't reliably infer. One short question, with category-aware suggestions.
5. **Write `.vibe-iterate/config.json`** validated against [`../guide/schemas/config.schema.json`](../guide/schemas/config.schema.json).
6. **Hand back to the bare router** (or to whatever mode the user wanted) with a one-line acknowledgment. No lecture.

## Hard rules

- **Do work first, ask second.** Never ask the user something you could have inferred from the codebase. Two questions max — one for classification confirmation, one for competitors.
- **Never auto-fire a mode after bootstrap.** Bootstrap writes config; the user kicks off the next step.
- **Validate before writing.** Read [`../guide/schemas/config.schema.json`](../guide/schemas/config.schema.json) and ensure the config object matches before calling Write.
- **No telemetry.** Per the guide's hard rules. Bootstrap writes one local file and stops.
- **Idempotent.** If `.vibe-iterate/config.json` already exists, ask the user if this is a refresh (default: yes if `last_inferred_at` is >30 days; default: no otherwise). Don't silently overwrite.

## Session + friction logging

At command start — call `session-logger.start("bootstrap", <project_dir>)` (see [`../session-logger/SKILL.md`](../session-logger/SKILL.md)) to get a sessionUUID. Hold it in memory for the duration of this run. Pass it to every `friction-logger.log()` invocation.

At command end — call `session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome: null, atlas_title: null, pr_url: null })`. Bootstrap doesn't write Atlas, so `atlas_outcome` and `atlas_title` are `null`.

Honor the friction trigger map at [`../guide/references/friction-triggers.md`](../guide/references/friction-triggers.md) — section `/vibe-iterate:bootstrap` — for which friction types to log at which confidence. Universal triggers (`repeat_question`, `rephrase_requested`) also apply; honor the defensive default — without a quoted prior turn in `symptom`, do not log.

## Posture announcement

At the start of the bootstrap conversation, surface the register in one short line:

> *Bootstrap mode → conservative. I'll do as much as I can from the codebase, then check two things with you. Two minutes max.*

This sets the user's expectation and prevents the "wait, what's it about to do?" moment.

## Procedure

### Step 1 — auto-classify the app type

Read these files (in order; stop reading once classification is unambiguous):

1. **`.claude-plugin/plugin.json`** present at project root → **Claude Code plugin**. Done.
2. **`package.json`** — read `dependencies` + `devDependencies` + `scripts`:
   - Has `next` / `react` / `vue` / `svelte` / `nuxt` / `astro` / `remix` → **web app**
   - Has `react-native` / `expo` → **mobile app**
   - Has `electron` → **desktop app**
   - Has `commander` / `yargs` / `oclif` / `clap` AND no UI framework → **CLI tool**
   - `"main"` field set, `"bin"` absent, no UI framework → **library / SDK**
3. **`pyproject.toml`** or `setup.py` — read project metadata:
   - Has `flask` / `django` / `fastapi` / `streamlit` → **web app** (Python)
   - Has `click` / `typer` / `argparse`-only → **CLI tool**
   - Otherwise → **library / SDK**
4. **`Cargo.toml`** — `[[bin]]` present → **CLI tool**; only `[lib]` → **library / SDK**
5. **`go.mod`** — has `main` package in `cmd/` or root → **CLI tool / service**; only sub-packages → **library**
6. **Multiple workspaces** (pnpm-workspace.yaml, lerna.json, Cargo workspace, multi-`package.json` under `packages/` or `apps/`) → **monorepo** (set as primary; sub-classify the most active workspace as the iteration target)
7. **None of the above match cleanly** — read `README.md` first 50 lines and infer; if still ambiguous, classify as **other** and surface the inference uncertainty in step 2.

Categories the agent classifies into (canonical strings — match exactly when writing config):

- `web-app`
- `mobile-app`
- `desktop-app`
- `cli-tool`
- `library-sdk`
- `claude-code-plugin`
- `monorepo` (with sub-type as suffix, e.g., `monorepo:web-app`)
- `data-research`
- `other`

For each, also note the **framework anchor** (e.g., `Next.js 16`, `React Native + Expo`, `Click`, `Cargo lib`) — the user-facing classification uses this to make the inference concrete.

### Step 2 — confirm with the user (ONE question)

Render the inference and ask for confirmation. Short. Like this:

```
Looks like a [framework anchor] — I'd classify this as a [category].

Right? (yes / pick another / let me describe it)
```

If user picks "another" — show the canonical list, let them pick.
If user picks "let me describe it" — take a one-line free-text description, then map it back to the closest canonical category.

### Step 3 — auto-extract framework pins

From the inferred stack's manifest file:

- **`package.json`** — read `dependencies` and `devDependencies`. Extract pins for: any framework named in step 1's classification (`next`, `react`, `vue`, etc.) + the top 5 most-impactful runtime deps (skip dev-only utilities like `eslint`, `prettier`, `typescript`, `@types/*` unless they're load-bearing). Cap at 8 entries.
- **`pyproject.toml`** — read `[project.dependencies]` (PEP 621) or `[tool.poetry.dependencies]` (Poetry). Same cap.
- **`Cargo.toml`** — read `[dependencies]`. Same cap.
- **`go.mod`** — read top-level `require` block. Same cap.

For each pin, capture `{ "name": "<package>", "version": "<version-string>" }`. If the version is a range (`^16.0.0`, `~4.1.0`), keep the range string verbatim — don't resolve to a concrete version.

If no manifest file exists (e.g., a pure-shell or pure-content repo), `framework_pins` is `[]`.

### Step 4 — ask for competitor URLs (ONE question)

Surface category-aware suggestions to make the question concrete. Examples by category:

- **web-app (note-taking, productivity)** → "e.g., notion.so/blog/category/product, obsidian.md/changelog, github.com/logseq/logseq/releases"
- **web-app (SaaS, B2B)** → "e.g., stripe.com/changelog, vercel.com/changelog, github.com/<competitor>/releases"
- **claude-code-plugin** → "e.g., other plugins in your category — github.com/<owner>/<plugin>/releases"
- **cli-tool** → "e.g., gh.io changelog, github.com/<competitor>/releases"
- **mobile-app** → "e.g., App Store / Play Store changelogs (paste the listing URL), competitor blogs"
- **library-sdk** → "e.g., comparable libraries' changelogs or release pages"

Ask:

```
Who do you compete with? Drop 2-5 URLs (one per line) — changelogs, release pages, or what's-new pages work best.

Examples for [category]: <category-aware suggestions>

Or hit enter to skip — you can add competitors later by editing .vibe-iterate/config.json.
```

If user provides 0 URLs, set `competitors: []` and continue. If user provides 1-5, validate each is a syntactically valid URL (must start with `http://` or `https://`); skip malformed ones with a one-line warning.

### Step 5 — synthesize the category description

Generate a one-line `category` string for `config.json`. Format: `<framework anchor> — <one-line description of what the app does>`.

Example: `Next.js 16 web app — AI-powered note-taking with vector search and shared workspaces`.

To produce the description, read the first 10 lines of `README.md` and extract the project's purpose. If `README.md` is missing or sparse, use the `package.json` `"description"` field. If both are missing, use `<framework anchor> — purpose unclear (edit .vibe-iterate/config.json to set)`.

### Step 6 — write `.vibe-iterate/config.json`

Build the config object:

```json
{
  "category": "<from step 5>",
  "competitors": [<from step 4>],
  "framework_pins": [<from step 3>],
  "last_inferred_at": "<ISO-8601 UTC timestamp, now>"
}
```

**Validate against the schema** at [`../guide/schemas/config.schema.json`](../guide/schemas/config.schema.json) before writing. If validation fails, fix and re-validate; do NOT write a malformed config.

Create `.vibe-iterate/` directory if it doesn't exist. Write `config.json`. Atomic (no read-modify-write — this is a fresh write).

Do NOT create `atlas.jsonl` here. The Atlas is created by the first banner mode that ships, rejects, or queues an iteration. An empty Atlas file is meaningless and confuses downstream readers.

Do NOT create `radar.cache.json` here. That's the schedule plugin's job (or `:radar` on a manual refresh).

### Step 7 — hand back

Acknowledge in one short line and stop. Like this:

```
Set up:
- Category: [category]
- Competitors: [N URLs] (or "none — add later")
- Framework pins: [N tracked]
- Written: .vibe-iterate/config.json

Want a mode recommendation now? Run /vibe-iterate (no args).
```

Do NOT auto-fire the bare router. The user kicks off the next step.

## Refresh case (config already exists)

If `.vibe-iterate/config.json` already exists when bootstrap runs:

1. Read `last_inferred_at` from the existing config.
2. If >30 days old, surface: *"Config last refreshed [N days] ago. Refresh now? (yes / no — keep existing)"* — default yes.
3. If <30 days old, surface: *"Config is current (refreshed [N days] ago). Refresh anyway? (yes / no)"* — default no.
4. If user says yes, run steps 1-6 above. Step 6 overwrites the existing config; that's intentional. Capture and surface what changed (framework pins added/removed, category drift).
5. If user says no, exit cleanly with a one-line acknowledgment.

## Output template — first-run (success)

```
Bootstrap mode → conservative. I'll do as much as I can from the codebase, then check two things with you. Two minutes max.

[reads files]

Looks like a [framework anchor] — I'd classify this as a [category].

Right? (yes / pick another / let me describe it)

[user confirms]

Who do you compete with? Drop 2-5 URLs (one per line). Examples for [category]: [...]

Or hit enter to skip.

[user provides URLs]

Set up:
- Category: [category]
- Competitors: [N URLs]
- Framework pins: [N tracked]
- Written: .vibe-iterate/config.json

Want a mode recommendation now? Run /vibe-iterate (no args).
```

## Anti-patterns (don't do these)

- **Don't list every missing file.** "There's no .vibe-iterate/, no atlas.jsonl, no config.json, no radar cache..." — that's a litany, not a setup. The user knows it's a fresh repo. Acknowledge once, move on.
- **Don't ask for the framework when you can read package.json.** Same for the project name, the description, the language.
- **Don't write an empty atlas.jsonl** "to be ready." Empty files mislead future reads.
- **Don't kick off any mode after bootstrap.** The user kicks off the next step. Bootstrap exits cleanly.
- **Don't lecture about what vibe-iterate does.** The user invoked it; they know. Skip the marketing copy.

## Cross-references

- Schema: [`../guide/schemas/config.schema.json`](../guide/schemas/config.schema.json)
- Reference doc: [`../guide/references/atlas-conventions.md`](../guide/references/atlas-conventions.md) (for why we don't pre-create atlas.jsonl)
- Sibling SKILL: [`../vibe-iterate/SKILL.md`](../vibe-iterate/SKILL.md) (the bare router that invokes this on first run)
