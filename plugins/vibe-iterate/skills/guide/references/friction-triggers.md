# Friction triggers — when each command logs what

Source of truth for `friction-logger.log()` calls across vibe-iterate. One section per command. Each row names the trigger condition + the `friction_type` enum value + the fixed `confidence` level.

**Rule:** confidence levels here are NOT agent-tunable. If a trigger feels mis-tuned, fix it here (and let `:evolve-iterate` propose the change) — don't override at log time.

**Universal triggers** apply to every command but require a quoted prior turn in `symptom`:

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User repeats a question agent already answered | `repeat_question` | `medium` | REQUIRES quoted prior-turn snippet in `symptom`. Defensive default: drop if no quote. |
| User asks for rephrase ("explain differently", "shorter") | `rephrase_requested` | `low` | Soft signal; common in normal conversation |

Per-command triggers below.

---

## `/vibe-iterate:bootstrap`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User picks "another" or "let me describe it" at classification confirm | `default_overridden` | `high` | The agent's auto-classification missed; capture the agent's pick + user's pick in `symptom` |
| User skips competitor URLs (hits enter at the prompt) | `default_overridden` | `low` | Skipping is fine; low-confidence signal that the prompt felt heavy |
| User declines re-bootstrap on a stale config | `default_overridden` | `medium` | They want the existing config to stand |

---

## `/vibe-iterate:feature-add`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User picks alternative #2 or #3 instead of recommended #1 | `default_overridden` | `high` | Quote the recommendation + user's pick in `symptom` |
| User pauses at candidate-selection step | `default_overridden` | `medium` | Atlas write happens with `outcome: queued`; no PR shipped |
| User declines Cart-delegation upsell at heavy-iteration check | `complement_rejected` | `high` | Set `complement_involved: "vibe-cartographer"` |
| User declines radar refresh when cache is stale/absent | `complement_rejected` | `medium` | Set `complement_involved: "schedule"` (the plugin that powers refresh) |
| User pivots to a different mode mid-flow | `sequence_revised` | `high` | Captured at next-command-time when the sentinel from this run has no terminal but a different mode's sentinel appears |
| User rewrites the chosen candidate's brief or PR description | `artifact_rewritten` | `medium` | Conservative — minor edits don't count; only heavy rewrites |

---

## `/vibe-iterate:competitive`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User picks a `decline`-tier gap to ship anyway | `default_overridden` | `high` | Strategic-relevance rubric was overridden |
| User picks alternative #2 or #3 | `default_overridden` | `high` | Same as feature-add |
| User declines Cart-delegation upsell | `complement_rejected` | `high` | `complement_involved: "vibe-cartographer"` |
| `:spy` fails for >50% of competitor URLs | `complement_rejected` | `low` | Soft signal — competitor pages are paywalled / blocked; `complement_involved: "WebFetch"` |
| User pauses at gap-selection step | `default_overridden` | `medium` | |

---

## `/vibe-iterate:ux-polish`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User picks a cosmetic-tier rough patch over a breaks-trust one | `default_overridden` | `high` | The agent ranked by user-trust impact; user disagreed |
| User picks alternative #2 or #3 | `default_overridden` | `high` | |
| User declines the surface-walk scope (says "just polish X surface") | `default_overridden` | `medium` | They wanted a narrower scope than the agent proposed |
| User pauses at rough-patch-selection step | `default_overridden` | `medium` | |
| User pivots from polish to a different mode mid-flow | `sequence_revised` | `high` | |

---

## `/vibe-iterate:bug-bash`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User picks a lower-priority bug over the recommended top-priority one | `default_overridden` | `high` | Triage rubric was overridden |
| Agent could not reproduce + user pauses | `default_overridden` | `medium` | Atlas entry: `outcome: queued`; ask user for repro steps |
| User asks agent to skip the regression test | `default_overridden` | `high` | Hard rule violation requested; CRITICAL signal for `:evolve-iterate` |
| User declines Cart-delegation upsell on a heavy bug fix | `complement_rejected` | `high` | `complement_involved: "vibe-cartographer"` |

---

## `/vibe-iterate:ship`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User declines Cart-delegation upsell on a heavy brief | `complement_rejected` | `high` | `complement_involved: "vibe-cartographer"` |
| User asks agent to skip the test run | `default_overridden` | `high` | Hard rule violation requested |
| User pauses or declines mid-build | `default_overridden` | `medium` | Atlas entry written with appropriate outcome |

---

## `/vibe-iterate:upgrade`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| User opts for a major bump | `default_overridden` | `high` | The major-bump gate was confirmed; capture the version range |
| User asks to skip the codemod | `default_overridden` | `medium` | `--no-codemod` flag or interactive opt-out |
| User asks to skip the test run | `default_overridden` | `high` | Hard rule violation requested |
| User picks "ship anyway with regressions" at post-flight gate | `default_overridden` | `high` | Regression-aware default was overridden |
| User rolls back the bump | `sequence_revised` | `high` | The upgrade attempt failed; bump didn't ship |

---

## `/vibe-iterate:horizon`

| Trigger | friction_type | confidence | Notes |
|---|---|---|---|
| **Signal drought** — fewer than 3 candidate bets cluster from the four forward signals | `default_overridden` | `high` | The agent's expectation of finding hedgeable candidates didn't hold. Quote the count + which signals were thin in `symptom`. Also captured: user's choice (continue with thin pool / pause). |
| **Low conviction** — every scored bet totals `< 11/20` (nothing crosses `watch`) | `default_overridden` | `high` | The forecast pool is high-noise. Quote the top score in `symptom`. |
| **Repeat seed** — user pushes to re-seed a bet near-duplicating an Atlas `source:"horizon"` entry < 90 days old | `default_overridden` | `high` | The de-dup default was overridden. Quote both entries in `symptom`. |
| **Cadence drift** — Horizon invoked < 30 days after the last horizon run with no inflection event named | `default_overridden` | `medium` | The quarterly cadence default was overridden. Soft signal — normal at inflection points. |
| **Forced PR request** — user asks Horizon to open a PR instead of seeding | `default_overridden` | `high` | Hard rule violation requested; CRITICAL signal for `:evolve-iterate`. Re-route to `feature-add`, log this. |
| `:forecast` returns rejection for ≥ 50% of candidates due to missing forward signals | `complement_rejected` | `medium` | Forward-signal sources (context7, WebSearch) failed or returned thin context. Set `complement_involved` to the failing source. |
| User pivots from Horizon to a different mode mid-flow | `sequence_revised` | `high` | Captured at next-command-time when the sentinel from this run has no terminal but a different mode's sentinel appears. |

Universal triggers (`repeat_question`, `rephrase_requested`) also apply. Defensive default applies: no quoted prior turn in `symptom` → don't log.

---

## Sidecar commands (`:radar`, `:spy`, `:scan-releases`, `:rate`, `:forecast`)

These are read-only and short-lived. **Do NOT call session-logger or friction-logger** from them. Sidecars are ephemeral spot-tools; the friction signal isn't worth the entry cost.

The exception: when a banner mode invokes a sidecar internally with `--silent`, friction captured during that invocation lives under the calling MODE's sessionUUID, not a separate sidecar entry.

## How to use this map

Each command SKILL has a "Session + friction logging" section that says: "Honor the trigger map at [`../guide/references/friction-triggers.md`](friction-triggers.md). Call `friction-logger.log()` at exactly these triggers, with exactly the listed confidence."

The agent reads this doc once per session (loaded as part of the guide), then logs as triggers fire during execution.

## Anti-patterns

- **Don't invent new friction types.** The seven enum values are the complete set. If an observation doesn't fit, it's not friction worth logging — let it pass.
- **Don't log on every disagreement.** Many user pivots are normal product decisions, not friction. Stick to the listed triggers.
- **Don't tune confidence per call.** The fixed level here is the calibrated value. Override at log time and you drift the model.
- **Don't log from sidecars.** They're ephemeral; their friction belongs to the calling mode's session.
