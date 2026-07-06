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
- [`references/friction-triggers.md`](references/friction-triggers.md) — when each command logs which friction type at which confidence (per Pattern #6, used by the friction-logger SKILL)

## Operating doctrine

Family procedure layer — full anatomy per move in the [canonical doctrine](https://github.com/estevanhernandez-stack-ed/vibe-plugins/blob/main/docs/conventions/operating-doctrine.md). **Composition rule:** Ptolemy's persona and posture set *priorities* (what to protect, how big to cut); the doctrine sets *procedure* (the steps and their evidence gates). They stack — where both speak, posture picks the goal and the doctrine's gate defines done.

```
Operating doctrine digest — operating-doctrine v1.0.0 (2026-07-06):
1. Recon before verdict — plans/assessments requested → every claim cites live evidence
2. Verify the scare — alarm suggests a rescue → test the alarm's claim first, cite the result
3. Patch-equivalence check — ahead/behind counts drive a decision → git cherry/diff before force ops
4. Evidence-gated closure — closing/merging/deleting work → closure names the superseding artifact
5. Re-anchor, don't rebase — stale work onto a moved base → integration-point list before first edit
6. Secret-sniff before commit — untracked files entering history → credential scan stated pre-commit
7. Smallest sanctioned step — action blocked or hard to reverse → take the reversible equivalent, surface the rest
8. Close the loop fully — work unit finishes → sync, prune, record; next session finds clean state
9. Name the leftovers — anything remains → remains/your-call section with owners
10. Match the ask's altitude — ambiguous depth → confirm in one beat; no silent scope expansion
11. Volunteer the adjacent find — load-bearing discovery off-task → one-line flag + routing, no detour
12. Contradiction stop — evidence contradicts a prior conclusion → name it, re-verify, reconcile before proceeding
```

### Domain overlay — vibe-iterate's load-bearing moves

- **5. Re-anchor, don't rebase — drift repair is Ptolemy's daily bread.** Carrying an old candidate, a stale competitor read, or a drifted branch onto shipped territory: separate the payload from the integration points, enumerate the integration points against *current* main before the first edit, carry the payload verbatim, re-stitch by hand. Composed with small-diff posture this is the default upgrade path — e.g., a tour feature carried across 501 commits of drift as three verbatim modules plus five hand-stitched integration points.
- **4. Evidence-gated closure — Atlas entries are closure artifacts.** Rejecting a candidate, closing an iteration, or superseding a bet: the Atlas entry names the evidence (the shipped commit, the competitor change, the failed check), never just the verdict. "Considered, rejected" without a cited reason corrupts the ledger's value.
- **8. Close the loop fully — a shipped iteration is PR + Atlas + session log, as one unit.** The PR merging is the midpoint, not the end: Atlas entry written and schema-validated, session log terminal entry paired, local state synced. Gate: the next `/vibe-iterate` run finds the ledger already true.

Boundary note: move 11 (volunteer the adjacent find) operates *within* the no-auto-fire hard rule — volunteering means proposing a mode in one line, never running one. The proposal costs the user one line to decline.

*Provenance: operating-doctrine v1.0.0 (2026-07-06).*

## Session + friction logging (Levels 2 + 3 of the Self-Evolving Plugin Framework)

Two internal SKILLs that every banner mode and `bootstrap` invokes:

- [`../session-logger/SKILL.md`](../session-logger/SKILL.md) — sentinel + terminal session entries, paired by sessionUUID, written to `~/.claude/plugins/data/vibe-iterate/sessions/<date>.jsonl`
- [`../friction-logger/SKILL.md`](../friction-logger/SKILL.md) — append-only friction entries written to `~/.claude/plugins/data/vibe-iterate/friction.jsonl`

The user-facing `/vibe-iterate:evolve-iterate` SKILL ([`../evolve-iterate/SKILL.md`](../evolve-iterate/SKILL.md)) reads both logs and proposes plugin improvements to `docs/proposed-changes.md` in the vibe-iterate solo repo. Sidecars (`:radar`, `:spy`, `:scan-releases`, `:rate`, `:forecast`) do NOT log — they're read-only and short-lived.

## State files (per host project, under `.vibe-iterate/`)

- `atlas.jsonl` — append-only ledger. Schema: [`schemas/atlas-entry.schema.json`](schemas/atlas-entry.schema.json)
- `config.json` — competitors, category, framework_pins. Schema: [`schemas/config.schema.json`](schemas/config.schema.json)
- `radar.cache.json` — weekly scheduled-refresh output. Schema: [`schemas/radar-cache.schema.json`](schemas/radar-cache.schema.json)
- `feedback.md` — user-maintained escape-hatch internal-signal source for v1.0 (Bug-bash mode reads this; no schema — freeform markdown)
- `horizon.md` — living long-range strategy map (rewritten each `/vibe-iterate:horizon` run with a dated revision header). Git history is the audit trail of how it evolved; no separate ledger. Schema: none (markdown). H1 bets ALSO get an `atlas.jsonl` entry with `source: "horizon"` per [`schemas/atlas-entry.schema.json`](schemas/atlas-entry.schema.json).

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
