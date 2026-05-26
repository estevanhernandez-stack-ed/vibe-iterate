---
name: horizon
description: "This skill should be used when the user says `/vibe-iterate:horizon` and wants to think long-range — what bets to make now to be ahead in months and years, not days and weeks. Ingests four forward signals (stack/platform roadmaps, ecosystem/model curves, competitor trajectory, own-product trajectory), scores bets via :forecast, places them on a Three-Horizon map (H1 ~3-6mo, H2 ~1-2yr, H3 ~3-5yr), and seeds H1 bets into the Atlas for feature-add to pick up. Never ships a PR — matured bets graduate to feature-add."
---

# /vibe-iterate:horizon — what bet do we make now to be ahead in 2027?

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources, Atlas conventions), then follow this command.

## What this command does

The long-range banner mode. Where the tactical modes (`feature-add`, `competitive`, `ux-polish`, `bug-bash`, `upgrade`) ask "what's the next PR," Horizon asks "what bet do we make now so we're not playing catch-up in 2027." It ingests four forward signals, clusters them into candidate bets, scores each via the `:forecast` sidecar, and places them on a **Three-Horizon map** (`.vibe-iterate/horizon.md`). Near-term (H1) bets graduate into the Atlas as queued candidates so `feature-add` can pick them up when their time comes. The rest live on the map as standing strategy.

**Horizon never opens a PR.** Forcing a PR onto a years-out bet is the premature-commitment trap the mode exists to avoid. Run quarterly, or at inflection points — not every session.

## Hard rules

- **No PR.** Horizon never opens a pull request. If a bet is ripe enough to build, that's `feature-add`'s job.
- **Cite signals, don't speculate.** Every bet must name the forward signal(s) that drive it. A bet with no signal is a vibe, not a forecast.
- **Don't chase every trend.** The `:forecast` conviction score is the filter. Park low-conviction bets; don't map them as if they're real.
- **Don't let H3 harden.** H3 options are cheap to hold; the moment one demands real investment it must earn its way up to H1 on its own forecast score.
- **Horizon Map write is mandatory.** Every invocation rewrites `.vibe-iterate/horizon.md` (revised, dated header). If the user pauses mid-flow, write the partial map with a `[partial]` revision note so future runs know where things left off.

## Session + friction logging

At command start — call `session-logger.start("horizon", <project_dir>)` (see [`../session-logger/SKILL.md`](../session-logger/SKILL.md)) to get a sessionUUID. Hold it in memory; pass it to every `friction-logger.log()` invocation.

At command end — call `session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, bets_considered, h1_seeded, map_revised })`. `outcome` is `mapped` (a full map was written), `partial` (user paused mid-flow), or `aborted` (user declined the map).

Honor the friction trigger map at [`../guide/references/friction-triggers.md`](../guide/references/friction-triggers.md) — section `/vibe-iterate:horizon` — for the horizon-specific trigger conditions (signal drought, low conviction, repeat seed, cadence drift, forced-PR request) and which existing `friction_type` enum value each maps to. Universal triggers (`repeat_question`, `rephrase_requested`) also apply; honor the defensive default — no quoted prior turn in `symptom` means don't log.

## Inputs

- **No required arguments.** Optional `--from <signal>` to restrict ingestion to one source: `roadmaps` | `ecosystem` | `competitors` | `trajectory`.
- **Project state required:** `.vibe-iterate/config.json` (for `category`, `competitors[]`, `framework_pins[]`). If absent, hand off to bootstrap: *"No config yet. Run `/vibe-iterate` first to bootstrap, then re-invoke Horizon."*

## Procedure

### Step 1 — posture announcement

> *Horizon mode → long-range posture. Conviction over certainty, optionality over commitment, cheap hedges over big bets. Reading forward signals, scoring with :forecast, mapping three horizons. No PR — matured bets graduate to feature-add.*

### Step 2 — pre-flight

Read `.vibe-iterate/horizon.md` if it exists (this run **revises** it, not replaces it blind — carry forward any H2/H3 bets that still hold; surface what changed). Read `.vibe-iterate/atlas.jsonl` to know which bets have already graduated (`source: "horizon"`, last 90 days) — don't re-surface them this run unless their rationale has materially shifted.

### Step 3 — ingest the four forward signals

Gathered **live** at run time — foresight is a quarterly move, not a per-session one, so no daily cache. Follow the guide's knowledge-sources contract ([`../guide/references/knowledge-sources.md`](../guide/references/knowledge-sources.md)): context7 for framework docs/RFCs, WebSearch for the rest, scheduled-refresh cache where one exists (e.g. radar) but otherwise live.

If `--from <signal>` was passed, restrict to just that source. Otherwise gather all four:

**A. Stack & platform roadmaps** — read `config.framework_pins[]` and the platform the app runs on. Surface: announced direction, RFCs in flight, public betas, deprecation timelines. Not current releases (that's `:scan-releases`); the **next two majors out** and any roadmap signal.

**B. Ecosystem & model curves** — emerging protocols and standards (e.g. MCP, agent protocols), model capability + cost curves, shifts in how software gets built. WebSearch for credible sources (vendor blogs, standards bodies, primary research).

**C. Competitor trajectory** — for each `config.competitors[]`, read where they're **heading**: public roadmaps, betas, recent funding/hiring as direction signals, stated near-future plans. Distinct from `competitive` mode's "what they shipped."

**D. Own-product trajectory** — read this repo's `atlas.jsonl` + `git log --oneline -50` and extrapolate: where is this product heading, what foundational limit or architectural debt will bite at scale, what's the next plateau to clear.

### Step 4 — cluster into candidate bets

Synthesize the signals into ≤10 distinct candidate bets, each tagged with its driving signal(s). A bet named by 3 converging signals already wins on conviction before scoring — note the convergence.

If fewer than 3 bets cluster, log `signal_drought` (per friction-triggers) and ask the user before continuing: *"Only N candidate bets clustered from the four signals — the foresight pool is thin. Continue with what we have, or pause for a richer scan another time?"*

### Step 5 — score each via `:forecast`

For each candidate bet, call `:forecast "<bet>" --silent`. Capture the structured scores (conviction, time-to-relevance, optionality, strategic fit, total `/20`), the rationale, and the recent-seed override if any.

If every bet scores `< 11/20`, log `forecast_low_conviction` and surface to the user: *"Nothing crossed `watch` this run — the pool is high-noise. Want to park them all and try again with fresh signals, or place the highest as H3 options regardless?"*

### Step 6 — place on the Three-Horizon map

Place each scored bet by `:forecast`'s tier output (derived from time-to-relevance):

- **H1 — defend / extend the core (~3-6mo).** Bets with time-to-relevance 5 (and total ≥ 16) graduate to the Atlas in Step 7. Bets at the H1/H2 boundary (time-to-relevance 4) lean H1 only if conviction ≥ 4.
- **H2 — emerging S-curves to ride (~1-2yr).** Bets with time-to-relevance 3-4. These live on the map with a one-line "cheap hedge now" note where applicable.
- **H3 — options on what's coming (~3-5yr).** Bets with time-to-relevance 1-2. Cheap to hold; their value is the optionality.

Each bet, regardless of tier, gets a one-line **"what would have to be true"** — the falsifiable condition that confirms or kills it. Without falsifiability, it's astrology, not a forecast.

Bets scoring `≤ 10/20` go to a **Parked / watching** section with a note on the specific signal that would promote them.

### Step 7 — seed H1 → Atlas

For each H1 bet (time-to-relevance 5, total ≥ 16), append a line to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "horizon",
  "outcome": "queued",
  "title": "<bet title>",
  "rationale": "H1 bet seeded by /vibe-iterate:horizon. Forecast <N>/20 (conviction <n>, time-to-relevance <n>, optionality <n>, strategic fit <n>). Signal(s): <which converged>. What would have to be true: <falsifiable condition>.",
  "rejected_runners_up": [],
  "pr": null,
  "source": "horizon"
}
```

Validate the entry against [`../guide/schemas/atlas-entry.schema.json`](../guide/schemas/atlas-entry.schema.json) before writing — malformed lines corrupt the ledger. The `mode:"horizon"` + `source:"horizon"` fields are both schema-required for these entries.

If a near-duplicate `source:"horizon"` entry already exists in the last 90 days AND the new rationale isn't materially different, log `repeat_seed` (per friction-triggers) and **don't write a duplicate** — leave the existing entry alone.

H2 and H3 bets are NOT written to the Atlas. They live only on the map.

### Step 8 — write `.vibe-iterate/horizon.md`

Rewrite the map (don't append — this is a living doc, git is the audit trail). Dated revision header at the top. Use this shape:

```markdown
# Horizon Map — <project name from config or repo root>
_Revised <YYYY-MM-DD> · next review ~<+90 days>_

## H1 — defend / extend the core  (~3-6mo)  → graduates to Atlas
- **<bet>**  (forecast <N>/20)
  - Signals: <which of the 4 converged>
  - What would have to be true: <falsifiable condition>
  - Seeded to Atlas: yes (queued)

## H2 — emerging S-curves to ride  (~1-2yr)
- **<bet>**  (forecast <N>/20) — <one-line why it's a mid bet> · hedge: <cheap move now>

## H3 — options on what's coming  (~3-5yr)
- **<bet>**  (forecast <N>/20) — <the optionality: cheap to hold, expensive to miss>

## Parked / watching
- <bet> — <why it's below the line, what signal would promote it>
```

If the user paused mid-flow, write a `[partial]` note in the revision header so future runs know the map is mid-revision.

### Step 9 — close out

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

## Anti-patterns

- **Don't run Horizon every session.** It's a quarterly / inflection-point move. The bare `/vibe-iterate` router surfaces it after long tactical-shipping streaks; don't pre-empt that cadence. Log the cadence-drift trigger (per friction-triggers.md) if invoked < 30 days after the last run.
- **Don't open a PR.** If the user asks Horizon to ship something, log the forced-PR-request trigger (per friction-triggers.md) and re-route: *"Horizon doesn't ship. If this bet is ripe (time-to-relevance 5, conviction ≥ 4), seed it to the Atlas and run `/vibe-iterate:feature-add` to ship it."*
- **Don't conflate `:forecast` and `:rate`.** Long-range bets get `:forecast` (/20, future-tuned dimensions). Near-term iterations get `:rate` (/25, effort + regression-risk). Using `:rate` on a years-out bet manufactures false precision.
- **Don't promote a bet on enthusiasm.** Time-to-relevance derives the tier, not vibes. If a bet feels like an H1 but scores time-to-relevance 2, it's H3 — full stop.
- **Don't drop H2 bets between runs.** Pre-flight (Step 2) carries forward H2/H3 bets that still hold. The map is a living doc, not a fresh slate every quarter.

## Cross-references

- Scoring sidecar: [`../forecast/SKILL.md`](../forecast/SKILL.md)
- Schema: [`../guide/schemas/atlas-entry.schema.json`](../guide/schemas/atlas-entry.schema.json)
- Atlas conventions: [`../guide/references/atlas-conventions.md`](../guide/references/atlas-conventions.md)
- Posture (long-range): [`../guide/references/posture.md`](../guide/references/posture.md)
- Knowledge sources (live forward-signal gathering): [`../guide/references/knowledge-sources.md`](../guide/references/knowledge-sources.md)
- Friction triggers: [`../guide/references/friction-triggers.md`](../guide/references/friction-triggers.md)
- Session logger: [`../session-logger/SKILL.md`](../session-logger/SKILL.md)
- Friction logger: [`../friction-logger/SKILL.md`](../friction-logger/SKILL.md)
- Bootstrap (first-run handoff): [`../bootstrap/SKILL.md`](../bootstrap/SKILL.md)
- Guide: [`../guide/SKILL.md`](../guide/SKILL.md)
