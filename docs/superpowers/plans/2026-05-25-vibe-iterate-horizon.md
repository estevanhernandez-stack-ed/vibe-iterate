# Vibe Iterate Horizon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold `/vibe-iterate:horizon` (long-range banner mode) and its companion `/vibe-iterate:forecast` sidecar, with all wiring (atlas schema, router, guide, references, README, CHANGELOG) so the existing test harness stays green and the mode is discoverable.

**Architecture:** Skill-authoring, not code — each task creates or edits a markdown SKILL/reference (or a JSON schema/fixture) and validates via the repo's two shell harnesses: `tests/check-skill-references.sh` (every relative link in a SKILL.md resolves) and `tests/validate-schemas.sh` (ajv-cli against atlas/config/radar fixtures). The new mode mirrors the existing `feature-add` shape; the new sidecar mirrors `rate`. The full design (output, signals, scoring, tiers, graduation seam) is locked in the companion spec — read it before starting.

**Tech Stack:** Markdown SKILL.md files with YAML frontmatter · JSON Schema draft-2019-09 · `ajv-cli@5` (via `npx --yes`) · bash test scripts · `git`.

**Companion spec (read first):** [`../specs/2026-05-25-vibe-iterate-horizon-design.md`](../specs/2026-05-25-vibe-iterate-horizon-design.md)

**Working branch:** `feat/horizon-mode` (already created off `main` in `C:/Users/estev/Projects/vibe-iterate`). All commits land on this branch; final merge is a separate step at the end of execution.

---

## File map (decomposition lock-in)

**Create (2):**
- `plugins/vibe-iterate/skills/horizon/SKILL.md` — the banner mode (Task 3)
- `plugins/vibe-iterate/skills/forecast/SKILL.md` — the long-range scoring sidecar (Task 2)

**Modify (8):**
- `plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json` — add `"horizon"` to `mode` enum + optional `source` field (Task 1)
- `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl` — add a horizon-seeded valid line (Task 1)
- `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl` — add a bad-`source` invalid line (Task 1)
- `plugins/vibe-iterate/skills/vibe-iterate/SKILL.md` — router rule + mode-table entry (Task 4)
- `plugins/vibe-iterate/skills/guide/SKILL.md` — list horizon + forecast + horizon.md state file (Task 5)
- `plugins/vibe-iterate/skills/guide/references/posture.md` — long-range posture (Task 6)
- `plugins/vibe-iterate/skills/guide/references/friction-triggers.md` — horizon section (Task 7)
- `README.md` + `plugins/vibe-iterate/CHANGELOG.md` — surface the new mode (Task 8)

Tasks run in this order; each is one commit. Task 1 must land first (later SKILLs reference the schema). Tasks 4-7 can run in any order after the SKILLs in Tasks 2-3 exist. Task 9 is the full-harness pass.

---

## Task 1: Extend the Atlas schema for horizon entries

**Files:**
- Modify: `plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json`
- Modify: `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl`
- Modify: `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl`

The schema has `additionalProperties: false`, so unless we explicitly add `source` to `properties`, a horizon-seeded H1 bet with `source: "horizon"` fails. Same logic for `mode: "horizon"` — must be added to the enum.

- [ ] **Step 1: Edit the schema**

In `plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json`:

In `properties.mode.enum`, add `"horizon"` at the end so it reads:

```json
"enum": ["feature-add", "competitive", "ux-polish", "bug-bash", "ship", "upgrade", "horizon"]
```

In `properties`, add (between `pr` and the closing `}`):

```json
"source": {
  "type": "string",
  "enum": ["horizon"],
  "description": "Provenance marker. Set to \"horizon\" when this entry was seeded by /vibe-iterate:horizon (an H1 bet graduating into the tactical loop). Absent for ordinary entries."
}
```

`source` is optional (not in `required`) and enum'd to the only currently meaningful value, which gives us a real negative test in Step 3.

- [ ] **Step 2: Add a valid fixture line**

Append to `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl`:

```json
{"ts":"2026-05-25T18:00:00Z","mode":"horizon","outcome":"queued","title":"Adopt on-device inference for the bacon-trail widget","rationale":"H1 bet seeded by /vibe-iterate:horizon. Forecast 17/20 (conviction 4, time-to-relevance 5, optionality 4, strategic fit 4). Signal: model-cost curves + Anthropic on-device roadmap. What would have to be true: a sub-100ms local model handles the trail-step inference.","rejected_runners_up":[],"pr":null,"source":"horizon"}
```

- [ ] **Step 3: Add an invalid fixture line**

Append to `plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl`:

```json
{"ts":"2026-05-25T18:01:00Z","mode":"horizon","outcome":"queued","title":"bad source value","rationale":"x","rejected_runners_up":[],"pr":null,"source":"not-a-known-source"}
```

This proves the `source` enum is enforced.

- [ ] **Step 4: Run the schema validator**

Run from the repo root:

```bash
bash tests/validate-schemas.sh
```

Expected: every existing fixture line still passes; the new valid line passes; the new invalid line is correctly rejected. Final line should read `Results: N passed, 0 failed` (N grows by 2).

- [ ] **Step 5: Commit**

```bash
git add plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json \
        plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl \
        plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.invalid.jsonl
git commit -m "schema(atlas): add horizon mode + source provenance marker

Extends atlas-entry.schema.json so H1 bets seeded by /vibe-iterate:horizon
validate as ordinary Atlas entries with mode:\"horizon\" and a
source:\"horizon\" provenance marker. additionalProperties:false made both
fields explicit-or-bust. Fixtures cover one valid horizon-seeded line and
one invalid bad-source line."
```

---

## Task 2: Create the `:forecast` sidecar SKILL

**Files:**
- Create: `plugins/vibe-iterate/skills/forecast/SKILL.md`

Mirror the structure of `plugins/vibe-iterate/skills/rate/SKILL.md` (read it first — it's the template). Same section headings, same tone, same hard rules — but the dimensions, the verdict bands, and the output shape are future-tuned per the spec.

- [ ] **Step 1: Read the template**

Open `plugins/vibe-iterate/skills/rate/SKILL.md` and `../specs/2026-05-25-vibe-iterate-horizon-design.md` § "The two new skills" → "forecast" and § "Anti-patterns / cadence". The forecast SKILL is the rate SKILL with these adaptations:

- /20 not /25 (4 dimensions, not 5)
- Dimensions: Conviction, Time-to-relevance, Optionality / cost-of-waiting, Strategic fit
- Verdict bands: `hedge now` (16-20) · `watch` (11-15) · `park` (≤10)
- "Atlas check (recent-rejection guard)" stays, but extends to `outcome:"queued"` with `source:"horizon"` — a near-duplicate horizon-seeded bet has *already* been logged, surface it
- "When invoked internally by a banner mode" — names `horizon` as the caller, not the four near-term modes
- Cross-refs drop the cart-detection link (Horizon never opens a PR) and the ux-polish rubric link (different lens)

- [ ] **Step 2: Write the SKILL.md**

Create `plugins/vibe-iterate/skills/forecast/SKILL.md`. Use this exact frontmatter:

```yaml
---
name: forecast
description: "This skill should be used when the user says `/vibe-iterate:forecast <bet>` and wants to score a long-range bet on the future-tuned lens. Reads the codebase + Atlas + horizon.md, scores on conviction, time-to-relevance, optionality (cost-of-waiting), and strategic fit. Outputs scores + rationale + hedge-now/watch/park verdict. Used internally by the horizon banner mode to rank bets."
---
```

Then write the body following the `:rate` template, swapping in:

- **Title line:** `# /vibe-iterate:forecast <bet> — score a long-range bet against your shipped product`
- **Hard rules:** read-only, no auto-fire, score-with-evidence, **honor recent horizon seeds** (if a near-duplicate bet was seeded to the Atlas with `source:"horizon"` in the last 90 days, surface it — verdict skews `watch` unless the rationale has materially changed).
- **Inputs:** `$1` is the bet as a one-line string; same config + atlas + recent-commits read as `:rate`.
- **Scoring rubric:** the 4 dimensions on a **1-5 scale**, each anchored to evidence. Use the bullet-list-per-tier shape from `:rate`. The exact dimension copy is in the spec — write each with 5 numbered tiers and an "Evidence cites" line. Key anchors:
  - **Conviction (5 = multiple independent signals converge; 1 = one weak signal)**
  - **Time-to-relevance (5 = bites within 6mo → H1; 3 = 1-2yr → H2; 1 = 3+ yr → H3)**
  - **Optionality / cost-of-waiting (5 = cheap to hedge now, brutal to retrofit later; 1 = symmetric, no penalty for waiting)**
  - **Strategic fit (5 = extends the core or an adjacent S-curve; 1 = orthogonal/distracting)**
- **Atlas check:** scan `atlas.jsonl` for the last 90 days; surface near-duplicate `outcome:"queued"` + `source:"horizon"` or `outcome:"rejected"` entries. Quote the prior title + rationale.
- **Verdict logic:**
  | Total | Verdict | Notes |
  |---|---|---|
  | **16-20** | `hedge now` | Likely H1/H2 seed. If time-to-relevance = 5, seed to Atlas; if 3-4, leave on the map with a hedge note. |
  | **11-15** | `watch` | On the map, revisit next horizon run. |
  | **5-10** | `park` | Note it, don't chase. |
  - Recent-seed override: if the Atlas check surfaced a same-bet `source:"horizon"` entry < 90 days old without new rationale, force `watch`.
- **Output shape:**

  ```
  Bet: <the bet, verbatim>

  Scores:
  - Conviction:        <N>/5  ← <evidence cite>
  - Time-to-relevance: <N>/5  ← <evidence cite>  (5 = H1, 3 = H2, 1 = H3)
  - Optionality:       <N>/5  ← <evidence cite>
  - Strategic fit:     <N>/5  ← <evidence cite>

  Total: <N>/20

  Rationale:
  <one-paragraph synthesis>

  Verdict: <hedge now | watch | park>
  Tier: <H1 | H2 | H3>  (derived from time-to-relevance)
  <one-line action — e.g., "Seed to Atlas + place on H1 of horizon.md" or "Note on H3, revisit next quarterly run.">
  ```

- **When invoked internally by a banner mode:** explicitly names `horizon` as the caller. Internal callers consume scores only; standalone calls render the full template.
- **Anti-patterns:** don't score without a forward signal cited; don't ignore recent horizon seeds; don't conflate `:forecast` with `:rate` (different lens, different time scale); don't render a tier that contradicts time-to-relevance.
- **Cross-references** (link block at the bottom — every link must resolve, the harness checks):
  - Schema: `[../guide/schemas/atlas-entry.schema.json](../guide/schemas/atlas-entry.schema.json)`
  - Sibling scoring sidecar: `[../rate/SKILL.md](../rate/SKILL.md)`
  - Calling mode: `[../horizon/SKILL.md](../horizon/SKILL.md)`
  - Posture (long-range): `[../guide/references/posture.md](../guide/references/posture.md)`
  - Guide: `[../guide/SKILL.md](../guide/SKILL.md)`

- [ ] **Step 3: Verify every cross-reference resolves**

Run from the repo root:

```bash
bash tests/check-skill-references.sh
```

Expected: all PASS lines; final `Cross-reference results: N passed, 0 failed`. The `../horizon/SKILL.md` link will FAIL at this step because Task 3 hasn't created it yet — that's fine. **Skip-state for this task:** every link other than `../horizon/SKILL.md` must PASS; only that one outstanding FAIL is acceptable. It clears in Task 3.

- [ ] **Step 4: Commit**

```bash
git add plugins/vibe-iterate/skills/forecast/SKILL.md
git commit -m "feat(forecast): long-range scoring sidecar (/20)

New /vibe-iterate:forecast sidecar — scores a long-range bet on conviction
x time-to-relevance x optionality x strategic fit (/20). Mirrors :rate's
read-only, evidence-required contract; verdict bands hedge-now / watch /
park; tier (H1/H2/H3) derives from time-to-relevance. Called internally
by /vibe-iterate:horizon; usable standalone."
```

---

## Task 3: Create the `/vibe-iterate:horizon` banner mode SKILL

**Files:**
- Create: `plugins/vibe-iterate/skills/horizon/SKILL.md`

Mirror the structure of `plugins/vibe-iterate/skills/feature-add/SKILL.md`. Same anatomy: posture announcement, hard rules, session+friction logging, inputs, procedure (numbered steps), anti-patterns, cross-references.

- [ ] **Step 1: Read the template + spec**

Open `plugins/vibe-iterate/skills/feature-add/SKILL.md` (the closest banner-mode analog) and `../specs/2026-05-25-vibe-iterate-horizon-design.md` § "Horizon mode procedure". The procedure has 8 steps — they translate one-to-one into the SKILL's "Procedure" section.

- [ ] **Step 2: Write the SKILL.md**

Create `plugins/vibe-iterate/skills/horizon/SKILL.md`. Exact frontmatter:

```yaml
---
name: horizon
description: "This skill should be used when the user says `/vibe-iterate:horizon` and wants to think long-range — what bets to make now to be ahead in months and years, not days and weeks. Ingests four forward signals (stack/platform roadmaps, ecosystem/model curves, competitor trajectory, own-product trajectory), scores bets via :forecast, places them on a Three-Horizon map (H1 ~3-6mo, H2 ~1-2yr, H3 ~3-5yr), and seeds H1 bets into the Atlas for feature-add to pick up. Never ships a PR — matured bets graduate to feature-add."
---
```

Body sections, in order:

1. **Title + one-line description.** `# /vibe-iterate:horizon — what bet do we make now to be ahead in 2027?`
2. **Read the guide.** Standard line: `Read [\`../guide/SKILL.md\`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources, Atlas conventions), then follow this command.`
3. **What this command does** — three-sentence summary: produces a living Horizon Map (`.vibe-iterate/horizon.md`) and seeds H1 bets into `atlas.jsonl`. Never opens a PR. Run quarterly or at inflection points.
4. **Hard rules** — copy the four anti-patterns from the spec verbatim as a bulleted list:
   - **No PR.** Horizon never opens a pull request. If a bet is ripe enough to build, that's `feature-add`'s job.
   - **Cite signals, don't speculate.** Every bet must name the forward signal(s) that drive it. A bet with no signal is a vibe, not a forecast.
   - **Don't chase every trend.** The `:forecast` conviction score is the filter — park low-conviction bets, don't map them.
   - **Don't let H3 harden.** H3 options are cheap to hold; the moment one demands real investment it must earn its way up to H1 on its own score.
   - **Horizon Map write is mandatory.** Every invocation rewrites `.vibe-iterate/horizon.md` (revised, dated header). If the user pauses mid-flow, write the partial map with a `[partial]` revision note.
5. **Session + friction logging** — mirror feature-add's section. `session-logger.start("horizon", <project_dir>)` at start; `session-logger.end({ outcome, ... })` at end. Honor friction-triggers.md § `/vibe-iterate:horizon` (added in Task 7).
6. **Inputs** — no required arguments. Optional `--from <signal>` to restrict ingestion to one source (`roadmaps` | `ecosystem` | `competitors` | `trajectory`). Requires `.vibe-iterate/config.json` (hand off to bootstrap if absent — same pattern as feature-add).
7. **Procedure** — 8 numbered steps, one-to-one with the spec § "Horizon mode procedure":
   1. Posture announcement (long-range; copy the spec block verbatim).
   2. Pre-flight: read existing `horizon.md` (this run revises, not replaces blind) + Atlas (skip already-graduated bets).
   3. Ingest the four forward signals — live (no cache), via WebSearch + context7 per the guide's knowledge-sources contract. Use `--from <signal>` to restrict.
   4. Cluster into ≤10 candidate bets; tag each with its driving signal(s).
   5. Score each via `:forecast --silent`; capture `/20` + per-dimension notes.
   6. Place on H1/H2/H3 by time-to-relevance. Each bet gets a one-line **"what would have to be true"** (falsifiable condition).
   7. Seed H1 → `atlas.jsonl` as `{outcome:"queued", mode:"horizon", source:"horizon"}` entries (schema enforces this — extended in Task 1). Include the forecast rationale + falsifiable condition. Validate against `../guide/schemas/atlas-entry.schema.json` before writing.
   8. Write `.vibe-iterate/horizon.md` — living doc, rewritten, dated revision header at top. Use the template shape from the spec.
8. **Horizon Map output shape** — embed the markdown template from the spec § "The Horizon Map artifact" verbatim as a code block.
9. **Close out** — the format mirrors feature-add's close-out:

   ```
   Horizon scanned:
   - Bets considered: <N>
   - H1 seeded to Atlas: <N>  (graduates to feature-add when their time comes)
   - H2 on the map: <N>
   - H3 options: <N>
   - Parked: <N>
   - Map: .vibe-iterate/horizon.md  (revised <date>)
   - Next review: ~<+90 days>

   Next:
   - Run /vibe-iterate:feature-add to ship the next near-term iteration (H1 candidates now in the Atlas)
   - Or re-run /vibe-iterate:horizon at the next inflection
   ```

10. **Anti-patterns** — repeat the hard-rules anti-patterns + the cadence anti-pattern: *Don't run Horizon every session.* It's a quarterly/inflection move. The bare `/vibe-iterate` router surfaces it after long tactical-shipping streaks; don't pre-empt that.
11. **Cross-references** — every link must resolve (the harness checks). Required links:
    - Sidecar: `[../forecast/SKILL.md](../forecast/SKILL.md)`
    - Schema: `[../guide/schemas/atlas-entry.schema.json](../guide/schemas/atlas-entry.schema.json)`
    - Atlas conventions: `[../guide/references/atlas-conventions.md](../guide/references/atlas-conventions.md)`
    - Posture: `[../guide/references/posture.md](../guide/references/posture.md)`
    - Knowledge sources: `[../guide/references/knowledge-sources.md](../guide/references/knowledge-sources.md)`
    - Friction triggers: `[../guide/references/friction-triggers.md](../guide/references/friction-triggers.md)`
    - Session logger: `[../session-logger/SKILL.md](../session-logger/SKILL.md)`
    - Friction logger: `[../friction-logger/SKILL.md](../friction-logger/SKILL.md)`
    - Bootstrap (first-run handoff): `[../bootstrap/SKILL.md](../bootstrap/SKILL.md)`
    - Guide: `[../guide/SKILL.md](../guide/SKILL.md)`

- [ ] **Step 3: Verify every cross-reference resolves**

```bash
bash tests/check-skill-references.sh
```

Expected: `Cross-reference results: N passed, 0 failed`. The earlier-failing `../horizon/SKILL.md` link from Task 2's `forecast/SKILL.md` now resolves too.

- [ ] **Step 4: Commit**

```bash
git add plugins/vibe-iterate/skills/horizon/SKILL.md
git commit -m "feat(horizon): long-range banner mode

New /vibe-iterate:horizon — ingests four forward signals (stack/platform
roadmaps, ecosystem/model curves, competitor trajectory, own-product
trajectory), scores via :forecast, places bets on a Three-Horizon map
(H1/H2/H3), and seeds H1 bets into the Atlas for feature-add to pick up.
Never ships a PR; horizon.md is the living artifact, git is the audit
trail. Run quarterly."
```

---

## Task 4: Wire Horizon into the bare-router SKILL

**Files:**
- Modify: `plugins/vibe-iterate/skills/vibe-iterate/SKILL.md`

The router recommends ONE mode + 1-2 alternatives. Horizon is never the default — it's surfaced as an alternative when the user has been heads-down shipping with no long-range pause.

- [ ] **Step 1: Add the recommendation rule**

Find the mode-recommendation logic table in `plugins/vibe-iterate/skills/vibe-iterate/SKILL.md` (the section titled `## Mode recommendation logic`). Append this row to the table:

```markdown
| Atlas shows ≥5 shipped tactical entries in the last 90 days AND no `mode:"horizon"` entry in that window | **horizon** (as alternative, never default) — you've been heads-down shipping; worth a look up? |
```

- [ ] **Step 2: Add cross-reference**

In the `## Cross-references` section at the bottom of the same file, in the "Banner modes" line, add Horizon:

Replace:

```markdown
- Banner modes: [`../feature-add/SKILL.md`](../feature-add/SKILL.md), [`../competitive/SKILL.md`](../competitive/SKILL.md), [`../ux-polish/SKILL.md`](../ux-polish/SKILL.md), [`../bug-bash/SKILL.md`](../bug-bash/SKILL.md)
```

With:

```markdown
- Banner modes: [`../feature-add/SKILL.md`](../feature-add/SKILL.md), [`../competitive/SKILL.md`](../competitive/SKILL.md), [`../ux-polish/SKILL.md`](../ux-polish/SKILL.md), [`../bug-bash/SKILL.md`](../bug-bash/SKILL.md), [`../horizon/SKILL.md`](../horizon/SKILL.md)
```

In the "Sidecars" line of the same `## Cross-references` section, add Forecast after `:rate`:

Replace:

```markdown
- Sidecars: [`../radar/SKILL.md`](../radar/SKILL.md), [`../rate/SKILL.md`](../rate/SKILL.md), [`../spy/SKILL.md`](../spy/SKILL.md), [`../scan-releases/SKILL.md`](../scan-releases/SKILL.md), [`../ship/SKILL.md`](../ship/SKILL.md), [`../upgrade/SKILL.md`](../upgrade/SKILL.md)
```

With:

```markdown
- Sidecars: [`../radar/SKILL.md`](../radar/SKILL.md), [`../rate/SKILL.md`](../rate/SKILL.md), [`../forecast/SKILL.md`](../forecast/SKILL.md), [`../spy/SKILL.md`](../spy/SKILL.md), [`../scan-releases/SKILL.md`](../scan-releases/SKILL.md), [`../ship/SKILL.md`](../ship/SKILL.md), [`../upgrade/SKILL.md`](../upgrade/SKILL.md)
```

- [ ] **Step 3: Verify cross-references**

```bash
bash tests/check-skill-references.sh
```

Expected: `Cross-reference results: N passed, 0 failed`. The new `../horizon/SKILL.md` and `../forecast/SKILL.md` links from the router resolve (the targets exist after Tasks 2-3).

- [ ] **Step 4: Commit**

```bash
git add plugins/vibe-iterate/skills/vibe-iterate/SKILL.md
git commit -m "feat(router): surface horizon as alternative on tactical-shipping streaks

Adds the recommendation rule to /vibe-iterate (bare router): when the Atlas
shows >=5 shipped tactical entries in the last 90 days and no mode:horizon
entry in that window, surface horizon as an alternative (never default).
Also adds horizon + forecast to the cross-references list."
```

---

## Task 5: List Horizon + Forecast in the guide

**Files:**
- Modify: `plugins/vibe-iterate/skills/guide/SKILL.md`

The guide enumerates banner modes and state files. Horizon adds one of each.

- [ ] **Step 1: Read the guide**

Open `plugins/vibe-iterate/skills/guide/SKILL.md`. Locate the "State files" section (lists `atlas.jsonl`, `config.json`, `radar.cache.json`, `feedback.md`) and the cross-references / banner-modes list (similar shape to Task 4's edits).

- [ ] **Step 2: Add the horizon.md state file**

In the `## State files (per host project, under `.vibe-iterate/`)` section, after the `feedback.md` bullet, add:

```markdown
- `horizon.md` — living long-range strategy map (rewritten each `/vibe-iterate:horizon` run with a dated revision header). Git history is the audit trail of how it evolved; no separate ledger. Schema: none (markdown). H1 bets ALSO get an `atlas.jsonl` entry with `source: "horizon"` per [`schemas/atlas-entry.schema.json`](schemas/atlas-entry.schema.json).
```

- [ ] **Step 3: Add horizon as a banner mode (if the guide lists them)**

If the guide has a "Banner modes" enumeration anywhere in its body (likely a paragraph or cross-ref block), add `horizon` to it as the long-range mode. Also add `forecast` to any sidecar enumeration. (Inspect the file; if no such enumeration exists, skip this sub-step — Task 4 already wired the router's enumeration.)

- [ ] **Step 4: Verify cross-references**

```bash
bash tests/check-skill-references.sh
```

Expected: `Cross-reference results: N passed, 0 failed`.

- [ ] **Step 5: Commit**

```bash
git add plugins/vibe-iterate/skills/guide/SKILL.md
git commit -m "docs(guide): list horizon.md state file + horizon/forecast skills

Adds .vibe-iterate/horizon.md to the state-files enumeration and lists
horizon (banner mode) + forecast (sidecar) wherever the guide enumerates
modes/sidecars."
```

---

## Task 6: Add the long-range posture to `references/posture.md`

**Files:**
- Modify: `plugins/vibe-iterate/skills/guide/references/posture.md`

The posture doc enumerates "regression-aware / user-trust-aware / small-diff-preferred" — the near-term defaults. Horizon's posture is genuinely different and should be named explicitly so the guide stays coherent.

- [ ] **Step 1: Read the file**

Open `plugins/vibe-iterate/skills/guide/references/posture.md`. Identify where the three near-term postures are defined (likely H2-level sections). The new posture is an addition, not a replacement.

- [ ] **Step 2: Add a new section at the end of the file**

Append:

```markdown
## Long-range posture (`/vibe-iterate:horizon` only)

The default three postures (regression-aware, user-trust-aware, small-diff-preferred)
apply to every mode that ships code. Horizon does not ship code, and its
inputs (forward signals) and outputs (bets across years) demand a different
register:

- **Conviction over certainty.** Long-range bets cannot be proven; the best you
  can do is grade conviction (`:forecast` conviction score) and require a
  cited forward signal for every bet. If a bet has no signal, it isn't a forecast — it's a vibe.
- **Optionality over commitment.** Prefer cheap hedges that preserve options.
  An H3 option costs nothing to hold and the value lies in the optionality;
  the moment one demands real investment it must earn H1 status on its own
  forecast score.
- **Falsifiability over enthusiasm.** Every bet gets a "what would have to be
  true" line — the falsifiable condition that confirms or kills it.
  Enthusiasm without falsifiability is astrology.

Horizon never opens a PR. The graduation seam (H1 → Atlas via
`source:"horizon"`) is where the long-range posture hands off to the
near-term postures of `/vibe-iterate:feature-add` and `:ship`.
```

- [ ] **Step 3: Verify cross-references**

```bash
bash tests/check-skill-references.sh
```

Expected: `Cross-reference results: N passed, 0 failed`. (No new links in this file's edits.)

- [ ] **Step 4: Commit**

```bash
git add plugins/vibe-iterate/skills/guide/references/posture.md
git commit -m "docs(posture): add long-range posture for /vibe-iterate:horizon

Names the three long-range stances explicitly (conviction-over-certainty,
optionality-over-commitment, falsifiability-over-enthusiasm) so the guide
stays coherent now that horizon ships no code. Hands off at the H1 ->
Atlas seam to the existing near-term postures."
```

---

## Task 7: Add the horizon section to `references/friction-triggers.md`

**Files:**
- Modify: `plugins/vibe-iterate/skills/guide/references/friction-triggers.md`

The friction-triggers doc lists, per banner mode, which friction types to log at which confidence. Horizon needs its own section so the friction-logger SKILL knows what to log when running it.

- [ ] **Step 1: Read the file**

Open `plugins/vibe-iterate/skills/guide/references/friction-triggers.md`. Identify the structure used by existing mode sections (e.g., `## /vibe-iterate:feature-add`). The new section copies that structure.

- [ ] **Step 2: Add the horizon section**

Append at the end of the file:

```markdown
## /vibe-iterate:horizon

| Friction type | When to log | Confidence |
|---|---|---|
| `signal_drought` | Fewer than 3 candidate bets clustered from the four signals | high |
| `forecast_low_conviction` | All scored bets score < 11/20 — nothing crosses `watch` | high |
| `repeat_seed` | A bet near-duplicates an Atlas entry seeded by horizon < 90 days ago | high |
| `cadence_drift` | User invoked horizon < 30 days after the last horizon run (not an inflection — too soon) | medium |
| `forced_pr_request` | User asks Horizon to open a PR instead of seeding | high |

Universal triggers (`repeat_question`, `rephrase_requested`) also apply.
Defensive default applies: no quoted prior turn in `symptom` → don't log.
```

- [ ] **Step 3: Verify cross-references**

```bash
bash tests/check-skill-references.sh
```

Expected: `Cross-reference results: N passed, 0 failed`.

- [ ] **Step 4: Commit**

```bash
git add plugins/vibe-iterate/skills/guide/references/friction-triggers.md
git commit -m "docs(friction): add /vibe-iterate:horizon trigger map

Five mode-specific friction types: signal_drought, forecast_low_conviction,
repeat_seed, cadence_drift, forced_pr_request. Universal triggers and the
defensive default still apply."
```

---

## Task 8: README + CHANGELOG

**Files:**
- Modify: `README.md`
- Modify: `plugins/vibe-iterate/CHANGELOG.md`

The new mode + sidecar need to be discoverable from the top-level docs.

- [ ] **Step 1: Inspect both files**

Read `README.md` and `plugins/vibe-iterate/CHANGELOG.md` to find:
- The mode/sidecar table or enumeration in the README (likely a "Commands" or "Modes" section).
- The CHANGELOG's most recent entry shape (date, version, bullets).

- [ ] **Step 2: Edit the README**

Add Horizon to the modes enumeration. If the README has a table, add a row:

```markdown
| `/vibe-iterate:horizon` | Long-range banner mode — ingests forward signals, scores bets via `:forecast`, places them on a Three-Horizon map (H1/H2/H3), seeds H1 bets into the Atlas. Never ships a PR. Run quarterly. |
```

If it has a sidecar list, add `:forecast`:

```markdown
| `/vibe-iterate:forecast` | Long-range scoring sidecar — scores a bet /20 on conviction, time-to-relevance, optionality, strategic fit. Called by `:horizon`; usable standalone. |
```

(If the README uses a different format, adapt — but the description text above is the canonical one-liner; reuse it.)

- [ ] **Step 3: Edit the CHANGELOG**

At the top of `plugins/vibe-iterate/CHANGELOG.md` (above the most recent entry), add:

```markdown
## [Unreleased]

### Added
- `/vibe-iterate:horizon` — long-range banner mode. Ingests four forward signals (stack/platform roadmaps, ecosystem/model curves, competitor trajectory, own-product trajectory), scores bets via `:forecast`, places them on a Three-Horizon map, and seeds H1 bets into the Atlas. Never ships a PR. See `plugins/vibe-iterate/skills/horizon/SKILL.md`.
- `/vibe-iterate:forecast` — long-range scoring sidecar (/20: conviction, time-to-relevance, optionality, strategic fit). Mirrors `:rate`'s read-only / evidence-required contract for long-range bets. See `plugins/vibe-iterate/skills/forecast/SKILL.md`.
- Bare router recommends Horizon as an alternative after ≥5 tactical shipped entries with no horizon run in 90 days.
- `atlas-entry.schema.json` extended: `mode` enum gains `"horizon"`; optional `source` field (enum `["horizon"]`) marks horizon-seeded entries.
- New living state file: `.vibe-iterate/horizon.md` (rewritten each horizon run; git history is the audit trail).
- Long-range posture documented in `guide/references/posture.md`.
- `/vibe-iterate:horizon` friction-trigger map added.
```

- [ ] **Step 4: Verify cross-references**

```bash
bash tests/check-skill-references.sh
```

Expected: `Cross-reference results: N passed, 0 failed` (README/CHANGELOG aren't scanned by the harness, but the run confirms no SKILL.md regressed).

- [ ] **Step 5: Commit**

```bash
git add README.md plugins/vibe-iterate/CHANGELOG.md
git commit -m "docs: surface horizon + forecast in README and CHANGELOG

README modes/sidecars enumeration gains horizon + forecast; CHANGELOG
Unreleased section captures the schema extension, the new living state
file, the long-range posture, and the friction-trigger map."
```

---

## Task 9: Full validation pass

**Files:** none (validation only).

- [ ] **Step 1: Run both harnesses end-to-end**

```bash
bash tests/check-skill-references.sh
bash tests/validate-schemas.sh
```

Expected: both finish with `0 failed`.

- [ ] **Step 2: Confirm the branch is ready for PR**

```bash
git log --oneline main..HEAD
```

Expected: 8 commits, one per Task 1-8, on `feat/horizon-mode`.

- [ ] **Step 3: (Manual smoke test — recommended but not gating)**

Have the executor open `plugins/vibe-iterate/skills/horizon/SKILL.md` and `plugins/vibe-iterate/skills/forecast/SKILL.md` in the IDE and re-read them top-to-bottom for voice/flow against the design spec. The harness catches structural failure, not prose drift; a human eye catches the latter.

- [ ] **Step 4: (Optional) Open the PR**

```bash
git push -u origin feat/horizon-mode
gh pr create --title "feat: vibe-iterate horizon — long-range banner mode + :forecast sidecar" \
  --body-file docs/superpowers/specs/2026-05-25-vibe-iterate-horizon-design.md
```

Or hold for Este's review of the branch before pushing — his call.

---

## Spec coverage self-check

| Spec section | Covered by |
|---|---|
| Problem / What Horizon is | Tasks 3, 5, 8 |
| Posture announcement | Task 3 (Step 2 § Procedure step 1), Task 6 |
| Design decisions table | Tasks 1-3 (encoded in schema + SKILL bodies) |
| `horizon` skill | Task 3 |
| `forecast` skill | Task 2 |
| Horizon mode procedure (8 steps) | Task 3 (Step 2 § Procedure) |
| Signal ingestion (4 sources, live) | Task 3 (Procedure step 3) |
| Horizon Map artifact template | Task 3 (Step 2 § Horizon Map output shape) |
| Graduation seam (H1 → Atlas) | Tasks 1, 3 |
| Router integration | Task 4 |
| Anti-patterns / cadence | Tasks 3, 6 |
| Files to create / modify | All tasks |
| Out of scope (YAGNI) | (no tasks — intentional negative space) |
| Testing / validation | Task 9 |

All spec sections accounted for. No placeholders, no "TBD", no "similar to Task N" — each task is self-contained.
