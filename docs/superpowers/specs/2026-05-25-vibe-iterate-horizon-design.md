# Vibe Iterate Horizon — design spec

**Date:** 2026-05-25
**Status:** approved (brainstorm), pending implementation plan
**Author:** Este + The Architect

## Problem

Every vibe-iterate banner mode answers a near-term question:

- `feature-add` — what's the next PR?
- `competitive` — what gap did a rival just open?
- `ux-polish` — which surface is getting rough?
- `bug-bash` — what feedback is unaddressed?
- `upgrade` — what framework bump is due?

There is no mode that thinks in **quarters and years**. Nothing asks: *what bet
do we make now so we're not playing catch-up in 2027?* The plugin can keep a
project current; it cannot keep a project **ahead**.

## What Horizon is

`/vibe-iterate:horizon` — the long-range banner mode. It ingests forward-looking
signals, clusters them into candidate bets, scores each on a future-tuned lens,
and places them on a **Three-Horizon map**. The near-horizon bets graduate into
the tactical loop (the Atlas, where `feature-add` picks them up); the rest live
on the map as standing strategy. **Horizon never ships a PR itself** — forcing a
PR onto a years-out bet is the premature-commitment trap the mode exists to avoid.

**Posture announcement (session-start):**

> *Horizon mode → long-range posture. Conviction over certainty, optionality over
> commitment, cheap hedges over big bets. Reading forward signals, scoring with
> :forecast, mapping three horizons. No PR — matured bets graduate to feature-add.*

## Design decisions (from the brainstorm)

| Decision | Choice | Why |
|---|---|---|
| Output | **Horizon Map + seed the pipeline** | A durable artifact you revisit, plus near-bets that graduate to `feature-add`. Clean separation: Horizon thinks long, feature-add ships near. |
| Signals | **All four** — stack/platform roadmaps, ecosystem/model curves, competitor trajectory, own-product trajectory | Foresight is only as credible as its inputs; one source is a guess. |
| Scoring | **New `:forecast` sidecar** (not `:rate`) | `:rate` scores effort + regression-risk, both unknowable years out — using it would manufacture false precision. |
| Tiers | **Three Horizons** (H1 defend/extend, H2 emerging S-curves, H3 options) | Each tier carries a strategic *role*, not just a date — and defines the graduation seam (H1 → Atlas). |
| Rubric size | **4 dimensions / 20** | The four that matter long-range; no forced fifth. Breaks `/25` parity with `:rate` deliberately. |
| Map storage | **Living `.vibe-iterate/horizon.md` + git history** | The map is meant to be read and revised, not appended. Git is the audit trail of how it evolved. |

## The two new skills

### `horizon` — banner mode

The mode itself. Orchestrates: ingest → cluster → score (`:forecast`) → place on
tiers → seed H1 → write the map. Logs a session + friction entry like the other
banner modes (per the guide's logging contract). Cart-detection applies only if a
seeded H1 bet later turns heavy — Horizon itself opens nothing.

### `forecast` — sidecar

The long-range scoring analog to `:rate`. Read-only, `--silent`-capable, **no
logging** (sidecars are short-lived per the guide). Scores one bet `/20`:

| Dimension | /5 | Asks |
|---|---|---|
| **Conviction** | 5 = multiple independent signals converge | Will this future actually arrive? |
| **Time-to-relevance** | 5 = bites soonest (places it in H1) | When does this start to matter? |
| **Optionality / cost-of-waiting** | 5 = cheap to hedge now, brutal to retrofit later | What does waiting cost us? |
| **Strategic fit** | 5 = extends the core or an adjacent S-curve | Is this ours to win? |

Verdict bands: **16-20 hedge now** (likely H1/H2 seed) · **11-15 watch** (on the
map, revisit next run) · **≤10 park** (note it, don't chase). Time-to-relevance is
also the primary tier-placement signal: high → H1, mid → H2, low → H3.

## Horizon mode procedure

1. **Posture announcement** (above).
2. **Pre-flight:** require `.vibe-iterate/config.json` (hand off to bootstrap if
   absent). Read the existing `horizon.md` if present (this run revises it, not
   replaces it blind) and the Atlas (to avoid re-surfacing already-graduated bets).
3. **Ingest the four forward signals**, gathered **live** at run time — foresight is
   a quarterly move, not a per-session one, so no daily cache:
   - **Stack/platform roadmaps** — framework RFCs, roadmaps, deprecation
     timelines, public betas (context7 + WebSearch; the guide's knowledge-sources
     contract). Reads the `framework_pins` from config to know what to look ahead on.
   - **Ecosystem/model curves** — emerging protocols/standards, model cost +
     capability trajectory (WebSearch).
   - **Competitor trajectory** — where `config.competitors` are *heading* (public
     roadmaps, betas, funding/hiring as direction), distinct from `competitive`
     mode's "what they shipped."
   - **Own-product trajectory** — extrapolate from this repo's Atlas + `git log`:
     where it's heading, what foundational limit bites at scale, the next plateau.
4. **Cluster into candidate bets** (cap ~10), each tagged with its driving
   signal(s). A bet named by 3 converging signals scores higher conviction.
5. **Score each via `:forecast --silent`**, capture the `/20` + per-dimension notes.
6. **Place on the Three-Horizon map** by time-to-relevance (H1 ~3-6mo, H2 ~1-2yr,
   H3 ~3-5yr). Each bet gets a one-line **"what would have to be true"** — the
   falsifiable condition that would confirm or kill the bet.
7. **Seed H1 → Atlas.** Write each H1 bet to `atlas.jsonl` as a queued entry with
   `source: "horizon"` so `feature-add`'s existing Atlas read surfaces it as a
   real candidate when its time comes (provenance preserved). H2/H3 stay on the map.
8. **Write `horizon.md`** (revised, dated revision header) and close out.

## The Horizon Map artifact (`.vibe-iterate/horizon.md`)

A living markdown doc, rewritten each run, git-versioned. Sketch:

```markdown
# Horizon Map — <project>
_Revised 2026-05-25 · next review ~2026-08_

## H1 — defend / extend the core  (~3-6mo)  → graduates to Atlas
- **<bet>**  (forecast 17/20)
  - Signals: <which of the 4 fired>
  - What would have to be true: <falsifiable condition>
  - Seeded to Atlas: yes (queued)

## H2 — emerging S-curves to ride  (~1-2yr)
- **<bet>**  (forecast 14/20) — <one-line why it's a mid bet> · hedge: <cheap move now>

## H3 — options on what's coming  (~3-5yr)
- **<bet>**  (forecast 12/20) — <the optionality: cheap to hold, expensive to miss>

## Parked / watching
- <bet> — <why it's below the line, what signal would promote it>
```

## Graduation seam (H1 → tactical loop)

Horizon writes H1 bets to `atlas.jsonl` with `outcome: "queued"`, `source:
"horizon"`, and the forecast rationale. No change to `feature-add` is required —
it already reads Atlas history and clusters/filters by it, so a horizon-seeded
queued entry appears as a candidate (with visible provenance) in a later run. The
`source: "horizon"` marker lets future tooling distinguish strategy-originated
candidates from signal-scan ones.

## Router integration

The bare `/vibe-iterate` router gains one recommendation rule: **if the Atlas
shows ≥5 shipped tactical entries and no `mode: "horizon"` entry in the last 90
days → surface Horizon as an alternative** ("you've been shipping heads-down;
worth a look up?"). Horizon is never the *default* recommendation — it's a
deliberate, occasional move.

## Anti-patterns / cadence

- **Run quarterly or at inflection points**, not every session. The router nudge
  enforces the cadence; the mode doesn't auto-fire.
- **Never force a PR.** If a bet is ripe enough to build, that's `feature-add`'s job.
- **Don't let H3 options harden into commitments.** Options are cheap to hold; the
  moment one demands real investment it must earn its way up to H1 on its own score.
- **Don't chase every speculative trend.** The `:forecast` conviction score is the
  filter; park low-conviction bets, don't map them as if they're real.
- **Cite signals, don't speculate.** Every bet names the forward signal that drives
  it. A bet with no signal is a vibe, not a forecast.

## Files to create / modify

**New:**
- `plugins/vibe-iterate/skills/horizon/SKILL.md`
- `plugins/vibe-iterate/skills/forecast/SKILL.md`

**Modified:**
- `plugins/vibe-iterate/skills/vibe-iterate/SKILL.md` — add the Horizon
  recommendation rule + mode-table/cross-ref entry
- `plugins/vibe-iterate/skills/guide/SKILL.md` — list `horizon` as a banner mode,
  `forecast` as a sidecar; note the `horizon.md` state file
- `plugins/vibe-iterate/skills/guide/schemas/atlas-entry.schema.json` — add an
  optional `source` field (e.g. `"horizon"`) so horizon-seeded H1 bets are valid
  Atlas entries. No separate bet schema: the map is markdown, the seed is an
  ordinary Atlas entry with provenance.
- `plugins/vibe-iterate/skills/guide/references/friction-triggers.md` — a
  `/vibe-iterate:horizon` section
- `plugins/vibe-iterate/skills/guide/references/posture.md` — add the long-range posture
- `README.md` + `plugins/vibe-iterate/CHANGELOG.md`

## Out of scope (YAGNI)

- No forward-signal *cache* (no `:radar` analog). Live gathering only — foresight
  runs are rare.
- No new `feature-add` plumbing — the Atlas marker convention is enough.
- No automated "review reminder" scheduling — the router nudge covers cadence.
- No PR/seed-planting path — explicitly rejected in the brainstorm.

## Testing / validation

- `forecast` returns a structured `/20` with per-dimension notes on a sample bet.
- `horizon` produces a well-formed `horizon.md` and appends valid H1 entries to a
  scratch `atlas.jsonl` (validates against the updated atlas-entry schema, with
  `source: "horizon"`).
- The router surfaces Horizon under the new rule and not otherwise.
- Existing tests stay green; if the repo's suite validates schemas, confirm the
  `source`-field addition to atlas-entry doesn't break existing Atlas fixtures.
