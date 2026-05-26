---
name: forecast
description: "This skill should be used when the user says `/vibe-iterate:forecast <bet>` and wants to score a long-range bet on the future-tuned lens. Reads the codebase + Atlas + horizon.md, scores on conviction, time-to-relevance, optionality (cost-of-waiting), and strategic fit. Outputs scores + rationale + hedge-now/watch/park verdict. Used internally by the horizon banner mode to rank bets."
---

# /vibe-iterate:forecast &lt;bet&gt; — score a long-range bet against your shipped product

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources), then follow this command.

## What this command does

Takes a one-line **bet** (`"adopt on-device inference"`, `"MCP-as-infrastructure"`, `"agent-native UX as the default"`) and scores it on the long-range lens. The user gets back four scores, a one-paragraph rationale, and a one-line verdict — *hedge now / watch / park* — plus the tier (H1/H2/H3) the bet would land on if it were placed on the Horizon Map.

Used standalone by anyone who already has a long-range bet and wants a future-tuned sanity check. Used internally by the `horizon` banner mode to rank candidate bets against each other.

**This is not `:rate`.** `:rate` scores near-term iterations on effort + regression-risk, both knowable today. `:forecast` is for bets where those dimensions are guesses (months-to-years out). Different time scale, different lens. Don't conflate them.

## Hard rules

- **Read-only.** This command does NOT write to the Atlas, the config, `horizon.md`, or any project file.
- **No mode auto-fire.** A `hedge now` verdict is a recommendation, not an invocation. The user kicks off `/vibe-iterate:horizon` (to place the bet on the map and seed H1) or sits with it.
- **Score with forward signals, not vibes.** Each score is anchored to a specific forward signal (a roadmap URL, an RFC, a model-capability curve, a competitor public roadmap, the project's own Atlas trajectory). No score without a cited signal.
- **Honor recent horizon seeds.** If the Atlas shows this bet (or a near-duplicate) was seeded by `horizon` (`outcome:"queued"`, `source:"horizon"`) in the last 90 days, surface it — verdict skews `watch` unless the rationale has materially changed.

## Inputs

- **`$1`** — the bet, as a one-line string. If the user invoked the command without an argument, prompt: *"What's the bet? (one line)"* and wait.
- **Project state** — same as the bare router reads: `.vibe-iterate/config.json`, `.vibe-iterate/atlas.jsonl`, `.vibe-iterate/horizon.md` (if present), recent commits.

If `.vibe-iterate/config.json` is **absent**, surface: *"No config yet. Run /vibe-iterate first to set up — or pass --no-config to score against codebase only."* Don't silently score with no context.

## Scoring rubric

Four scores, each on a **1-5 scale** (5 = strongest). Anchor every score to a specific forward signal.

### 1. Conviction (1-5)

How sure are we this future actually arrives?

- **5** — multiple independent signals converge: framework roadmap + competitor trajectory + ecosystem standard + own-product extrapolation all point the same way
- **4** — two independent signals converge, one strong
- **3** — one strong signal (e.g., a credible framework RFC), no convergence yet
- **2** — one weak signal (a single rival's beta, a thought-leader essay)
- **1** — speculation; no forward signal beyond a hunch

**Evidence cites:** name the signals — roadmap URL, RFC #, model-curve reference, competitor public statement, Atlas extrapolation.

### 2. Time-to-relevance (1-5)

When does this bet start to matter?

- **5** — bites within ~6mo → places the bet on **H1** (graduates to Atlas)
- **4** — bites in ~6-12mo → H1/H2 boundary; lean H1 if conviction ≥ 4, else H2
- **3** — bites in ~1-2yr → **H2** (on the map, hedge cheaply)
- **2** — bites in ~2-3yr → H2/H3 boundary
- **1** — bites in ~3-5yr+ → **H3** (option, cheap to hold)

**Evidence cites:** name the trigger (a framework deprecation date, a model-cost-curve crossover, a competitor's stated ship target).

### 3. Optionality / cost-of-waiting (1-5)

How asymmetric is the value of seeding now vs. retrofitting later?

- **5** — cheap to hedge now (a small extension point, a flag, an abstraction); brutal to retrofit later (load-bearing architecture would have to change)
- **4** — modest hedge now, significant retrofit cost later
- **3** — moderate cost both ways
- **2** — comparable cost now and later; little optionality penalty
- **1** — symmetric — no penalty for waiting; might even be cheaper later (don't seed pure-FOMO bets)

**Evidence cites:** name the surface that would have to change later — the schema, the auth flow, the data layer, the contract.

### 4. Strategic fit (1-5)

Is this bet ours to win?

- **5** — extends the core directly or rides an adjacent S-curve we're already on
- **4** — fits the brand and the stack, slightly adjacent
- **3** — adjacent but not obviously ours
- **2** — would require a brand or capability stretch
- **1** — orthogonal or distracting; pursuing it would dilute the core

**Evidence cites:** name the core capability or adjacent S-curve; cite the product's stated positioning if present in config or README.

## Atlas check (recent horizon-seed guard)

Read `.vibe-iterate/atlas.jsonl` for the last 90 days. For each entry where `source == "horizon"` OR `outcome == "rejected"`, compare the entry's `title` to the rated bet. If the title is a near-duplicate (same noun phrase or same verb-object pair), surface it:

```
Atlas note: this bet (or a near-duplicate) was [seeded by horizon on YYYY-MM-DD | rejected on YYYY-MM-DD].
- Prior entry: "<title>"
- Rationale: "<rationale>"

[If recently seeded:] Verdict skews `watch` unless the new rationale materially changes the calculus (new signal converged, time-to-relevance shifted, optionality changed).
[If rejected:] Verdict skews `park` unless the new rationale materially changes the calculus.
```

If no near-duplicate, no Atlas note (don't pad).

## Verdict logic

Compute total score (sum of 4 scores, 4-20).

| Total | Verdict | Threshold conditions |
|---|---|---|
| **16-20** | `hedge now` | Conviction ≥ 4 AND no recent horizon-seed override |
| **11-15** | `watch` | "On the map; revisit next horizon run." |
| **4-10** | `park` | "Note it, don't chase. Re-rate when a new signal converges." |

**Tier (H1/H2/H3) derives from time-to-relevance:**
- time-to-relevance **5** → **H1** (and if total ≥ 16, seed to Atlas as `outcome:"queued", source:"horizon"`)
- time-to-relevance **3-4** → **H2** (leave on the map with a cheap hedge note)
- time-to-relevance **1-2** → **H3** (option; cheap to hold)

**Recent-seed override:** if the Atlas check surfaced a same-bet `source:"horizon"` entry < 90 days old AND the new rationale isn't materially different, force `watch` regardless of total score.

## Output shape

```
Bet: <the bet, verbatim>

Scores:
- Conviction:        <N>/5  ← <forward-signal cite>
- Time-to-relevance: <N>/5  ← <forward-signal cite>  (5 = H1, 3 = H2, 1 = H3)
- Optionality:       <N>/5  ← <forward-signal cite>
- Strategic fit:     <N>/5  ← <forward-signal cite>

Total: <N>/20

Rationale:
<one-paragraph synthesis — what the scores mean together, what would have to be true for this bet, any Atlas notes>

Verdict: <hedge now | watch | park>
Tier:    <H1 | H2 | H3>  (derived from time-to-relevance)
<one-line action — e.g., "Seed to Atlas + place on H1 of horizon.md." or "Note on H3 of the map; revisit next quarterly run." or "Park — log to horizon.md 'Parked / watching' with the signal that would promote it.">
```

## When invoked internally by a banner mode

When `horizon` calls `:forecast` to rank candidate bets, the calling mode is responsible for:

- Passing each candidate bet through `:forecast --silent`
- Sorting by total score
- Honoring the recent-horizon-seed override
- Placing each bet on the tier derived from time-to-relevance
- Writing H1 bets with total ≥ 16 to `atlas.jsonl` as `outcome:"queued", source:"horizon"`

The internal call doesn't render the full output template — it just consumes the scores + tier. The rendered template is for standalone user-invoked calls.

## Anti-patterns

- **Don't score without a forward signal.** "Conviction: 4 (this feels inevitable)" is astrology. Cite a roadmap, an RFC, a curve, an Atlas trajectory.
- **Don't ignore recent horizon seeds.** Re-scoring a bet that was seeded last month — without new convergence — wastes the user's time and the Atlas's purpose.
- **Don't conflate `:forecast` with `:rate`.** Different time scale, different lens. If the bet is shippable today, route to `:rate`. If it's a years-out bet, score with `:forecast`.
- **Don't render a tier that contradicts time-to-relevance.** If time-to-relevance is 1, the tier is H3 — full stop. Don't promote on enthusiasm.
- **Don't render a verdict that contradicts the scores.** If total is 8 but you wrote `hedge now`, something's wrong — re-score or check the rubric.

## Cross-references

- Schema: [`../guide/schemas/atlas-entry.schema.json`](../guide/schemas/atlas-entry.schema.json)
- Sibling scoring sidecar (near-term): [`../rate/SKILL.md`](../rate/SKILL.md)
- Calling mode: [`../horizon/SKILL.md`](../horizon/SKILL.md)
- Posture (long-range): [`../guide/references/posture.md`](../guide/references/posture.md)
- Knowledge sources (forward-signal gathering): [`../guide/references/knowledge-sources.md`](../guide/references/knowledge-sources.md)
- Guide: [`../guide/SKILL.md`](../guide/SKILL.md)
