# vibe-iterate — design spec

**Date:** 2026-05-04
**Status:** draft, awaiting builder review
**Brainstorming session:** 2026-05-04, locked through 5 sections + persona refinement
**Co-authors:** Este (builder), The Architect (brainstorm pair)
**Proposed agent persona:** Ptolemy

---

## Marketing frame

**Tagline:** *vibe-iterate maintains your Atlas.*

**One-paragraph pitch:** vibe-iterate is the post-ship sibling to vibe-cartographer. Cart takes you from idea to v1; vibe-iterate takes you from v1 to v1+n, indefinitely. The plugin you reach for when the app is in users' hands and you need to know what's next — to establish your roadmap, or to turn the one you have into an Atlas.

---

## Identity

vibe-iterate fills a gap in the Vibe Plugins family: **post-ship product iteration.**

Existing plugins:
- **Cart (vibe-cartographer)** — greenfield: idea → v1
- **Doc (vibe-doc)** — documentation completeness
- **Test (vibe-test)** — test coverage and tier enforcement
- **Sec (vibe-sec)** — security posture
- **Thesis Engine + Vibe Thesis** — research authoring

None answer: *the app is shipped, users have hands on it, what do I build next?* That's vibe-iterate.

---

## Persona — Ptolemy

Named for Claudius Ptolemy — the systematist who, in *Geographia*, built the framework for maps (the coordinate system, the projections, the multi-source synthesis), not just the maps themselves. He worked over already-known territory, not the frontier. Cart is the field-explorer; Ptolemy is the senior cartographer who maintains the Atlas as territory shifts.

**Posture: shipped-product-conservative.**
- **Regression-aware** — runs existing tests before opening the PR; surfaces regressions explicitly rather than shipping over them
- **User-trust-aware** — no surprise breaking changes; if behavior users rely on changes, the PR description names it and suggests a deprecation path
- **Small-diff-preferred** — defaults to the smallest diff that delivers the value; reaches for refactor only when refactor IS the value

**Different brain from Cart.** Cart is greenfield-optimistic ("ship the thing"); Ptolemy is shipped-product-conservative ("don't break the working bits"). Both belong in the family.

**Posture switch at session-start.** Ptolemy reads the brief at the top of every run and explicitly states its register, e.g., *"Bug-bash mode → conservative posture, smallest-diff fix, regression checks aggressive."* Makes the brain setting visible to the user.

---

## Architecture — Hybrid C

Dual-shape: **banner modes** (end-to-end workflows, one PR per session) + **sidecar tools** (grab-and-go spot-tools, also used internally by the modes).

### Composition with Cart (Pattern #13 with discovery upsell)

- **Default — own build muscle.** vibe-iterate ships the PR itself, with build muscle intentionally lighter than Cart's full `/scope → /prd → /spec → /build` flow. Works without Cart installed.
- **Cart-present enhancement.** Auto-detects Cart's namespace. For heavy iterations (large surface, multiple subsystems touched, exceeds one-PR threshold), delegates the planning chunks (`/scope`, `/prd`, `/spec`) to Cart, then takes back over for build + commit shape. User gets Cart's discipline without leaving vibe-iterate.
- **Cart-missing discovery beat.** When Cart's missing AND the iteration is heavy enough to warrant Cart's depth, surfaces a one-line nudge: *"This iteration would benefit from Cart's structured flow — install it, or proceed with vibe-iterate's lighter flow?"* Discovery upsell, never blocks.

### "Heavy iteration" threshold (judgment call, lean own-muscle)

Ptolemy decides at brief-time whether to escalate to Cart. v1.0 leans toward under-delegation — default to own muscle, only escalate when clearly heavy. Heuristic, not a hard rule:

- Touches **3 or more subsystems** (e.g., API + UI + auth + data layer), OR
- Introduces **a new domain concept** that needs its own data shape, OR
- Estimated **>1 day of focused work** if a senior engineer did it manually.

Below this bar: Ptolemy ships solo. At or above: Ptolemy delegates `/scope → /prd → /spec` to Cart (if installed), or surfaces the discovery beat (if Cart's missing). Telemetry-free, so this threshold won't auto-tune from data — refine it via session friction logs and explicit user feedback.

---

## Banner modes (v1.0 ships four)

Each invocation produces one PR.

### `/vibe-iterate feature-add` — what should we build next?

- **Signal:** competitor URLs (A) + Product Hunt category (B) + framework releases (E) + `feedback.md` if present
- **Flow:** scan signal → cluster into candidate features → score on impact, fit-with-stack, effort, and Atlas history (don't re-propose recently rejected items) → pick one → produce brief → ship the PR
- **Output:** one feature PR + Atlas entry logging the candidates considered, the one chosen, the runners-up

### `/vibe-iterate competitive` — what do they have that we don't?

- **Signal:** competitor URLs (A) + Product Hunt category (B); no internal sources
- **Flow:** scan competitor changelogs/releases since last run → diff against your shipped feature set → identify gaps → rank by *strategic relevance, not parity* (don't ship because they shipped) → pick one → ship
- **Output:** one feature PR + Atlas entry of the diff and the rationale for what we did and didn't copy
- **Strategic relevance rubric:** does this gap reflect a real differentiator the user's product should match given their category, stack, and audience? *Not* "they shipped it, so we should." Ptolemy explicitly notes one of: (a) **match** — gap closes a feature parity our users actually expect; (b) **differentiate** — they shipped X, we should ship Y instead because it's more aligned with our positioning; (c) **decline** — gap is real but not relevant to us, log and move on

### `/vibe-iterate ux-polish` — what's shipped but rough?

- **Signal:** none external. Agent walks the shipped UI surfaces (routes, components, key flows)
- **Flow:** identify rough patches (inconsistent spacing, weak hierarchy, missing empty/loading/error states, dead-end paths) → score by user-trust impact → pick one → ship the polish PR
- **Output:** one polish PR + Atlas entry of the rough-spot catalog, what got fixed, what's still pending
- **User-trust-impact rubric:** does the rough patch make the user pause, lose confidence, or see something visibly broken? Ranked tiers: (a) **breaks trust** — empty state with no message, error swallowed silently, dead-end path with no exit, broken-looking layout (high priority); (b) **erodes trust** — inconsistent spacing across the same flow, missing loading state on a slow action, weak visual hierarchy on a primary screen (medium); (c) **cosmetic** — 4px alignment drift, font-weight inconsistency in a secondary surface (low, often skipped). Same rubric used by `/vibe-iterate:rate` when scoring `user-trust-impact`

### `/vibe-iterate bug-bash` — what's broken according to users?

- **Signal v1.0:** `feedback.md` only (escape hatch). Real connectors (GH Issues, Discord, Dashboard) defer to v1.1
- **Flow:** read the feedback file → triage by severity × frequency × blast-radius → pick highest-priority → reproduce → ship the fix
- **Output:** one fix PR + Atlas entry of the bug, reproduction, fix
- **v1.0 caveat:** dormant for repos without `feedback.md`. Surfaces a one-line nudge at invocation: *"No internal signal connected. Add a feedback.md, or wait for v1.1."*

### Bare router — `/vibe-iterate` (no mode)

- Reads project state (Atlas, radar cache, recent commits) → recommends a mode for the moment → asks before launching → never auto-fires

### Cross-cutting posture (all modes)

- Regression-aware: existing tests run before PR opens
- User-trust-aware: breaking changes named explicitly in PR description
- Small-diff-preferred: smallest diff that delivers the value
- Atlas-write: every PR appends a one-line entry to `.vibe-iterate/atlas.jsonl`

---

## Sidecar tools (v1.0 ships all six)

Same agent brain (Ptolemy). Smaller scope per call. Each is independently useful AND used internally by banner modes — improvements to a sidecar lift every mode that uses it.

### `/vibe-iterate:radar` — what's new across your stack + competitor set since last visit

- Reads the cached scheduled-refresh file (per-project, weekly)
- Output: digest grouped by category (framework releases / competitor changelogs / Product Hunt buzz). Highlights deltas since last `:radar` call
- Used by: every banner mode as the cheap first-pass scan

### `/vibe-iterate:spy <url>` — one-shot competitive read on a single URL

- Fetches and reads the URL (changelog, "what's new", landing page)
- Output: structured read — what they shipped, what they emphasize, gaps you might have, things you do better
- Used by: `competitive` mode internally for each user-supplied competitor URL

### `/vibe-iterate:scan-releases [package]` — what's new in this lib since you last bumped (or all libs if no arg)

- Reads `package.json` pins, queries release notes (context7 when present, web search as fallback) since your pinned version
- Output: per-package list of breaking changes, new features, security fixes. Flags codemod availability
- Used by: `feature-add` for "is there a fresh framework feature that unblocks the highest-impact item?"; `:upgrade` for the bump itself

### `/vibe-iterate:rate <idea>` — score a feature idea against your shipped product

- Takes a one-line idea ("add saved searches"), reads your codebase, reads the Atlas
- Output: scores on impact, fit-with-stack, effort, regression-risk, user-trust-impact + one-paragraph rationale + one-line *ship-now / queue / decline* verdict
- Used by: every banner mode internally to rank candidates

### `/vibe-iterate:ship <brief>` — skip ingestion, ship from a hand-written brief

- Takes a markdown brief (or inline prompt), runs the build directly with the regression-aware / small-diff posture
- Output: one PR + Atlas entry tagged `source: manual-brief`
- Used by: anyone who already knows what they want — bypasses the signal-ingestion phase

### `/vibe-iterate:upgrade <package>` — bump one library + codemods if available

- Surgical version of the cut Modernize mode. Reads release notes, runs the codemod if one exists, runs your test suite, ships the bump as one PR
- Output: one upgrade PR + Atlas entry tagged `source: upgrade-tool`
- Used by: anyone responding to a `:scan-releases` finding or a security advisory

---

## Cutting-edge knowledge (Ptolemy's brain)

How the agent stays current on big-shoulder software (Next, React, Tailwind, the SDKs in `package.json`):

- **Live spot-checks via context7 MCP** — at decision-time, when the agent reaches for "is there a current way to do X in [framework]?", it queries context7 for fresh docs. No staleness, one MCP call per question
- **Scheduled refresh** — weekly job (via the `schedule` plugin) pulls release notes for every framework/SDK pinned in active projects' `package.json`, caches per-project at `.vibe-iterate/radar.cache.json`. The `:radar` sidecar reads this cache; modes use it as their cheap first-pass scan
- **Web-search fallback** — when context7 doesn't cover the library or it's down, the agent falls back to web search. Same answer, slower

---

## State and file layout

All per-project, under `.vibe-iterate/`:

| File | Purpose | Writer |
|---|---|---|
| `atlas.jsonl` | Append-only ledger of every iteration considered, shipped, rejected. Source of truth for "don't re-propose the same thing twice." | Ptolemy (agent) |
| `config.json` | `competitors[]`, `category`, `framework_pins[]`. Generated at first run from codebase + README inference, confirmed by user. | Ptolemy at first run; user edits anytime |
| `radar.cache.json` | Weekly scheduled-refresh output. Read by `:radar` and modes. | Schedule job |
| `feedback.md` | Escape-hatch internal-signal source for v1.0. | User-maintained |

### Atlas entry shape

One JSONL line per iteration:

```json
{
  "ts": "2026-05-04T15:30:00Z",
  "mode": "feature-add",
  "outcome": "shipped",
  "title": "Add saved-search feature",
  "rationale": "Top-scored on impact + fit-with-stack...",
  "rejected_runners_up": ["dark mode", "export to CSV"],
  "pr": "https://github.com/.../pull/42"
}
```

`mode` values (the command the user invoked): `feature-add` | `competitive` | `ux-polish` | `bug-bash` | `ship` | `upgrade`.
`outcome` values: `shipped` | `rejected` | `queued`.

A separate `source` field may return in v1.1 if the idea-queue feature lands (so a `ship` invocation can trace back to the `rate`-call that originally queued the idea). For v1.0, `mode` is enough.

---

## Cadence

- **Manual** — modes + sidecars run on demand. Modes ship code, want intentional kickoff
- **Scheduled** — weekly radar refresh via the `schedule` plugin's cron. Read-only, low-risk. No mode auto-fires; only the cache gets refreshed

---

## MVP scope split

| Surface | v1.0 | v1.1 |
|---|---|---|
| Banner modes | `feature-add`, `competitive`, `ux-polish`, `bug-bash` (`feedback.md` only) | `perf`, `accessibility` |
| Sidecar tools | All six (`:radar`, `:spy`, `:scan-releases`, `:rate`, `:ship`, `:upgrade`) | — |
| Bare router | Yes | — |
| External signal | A (competitor URLs) + B (Product Hunt) + E (framework releases) | C (HN/Reddit/Twitter), D (App Store/Play Store reviews) |
| Internal signal | `feedback.md` | GH Issues, Discord (via MCP), 626Labs Dashboard, in-app widget |
| Cart-detection | Pattern #13 deferral + discovery upsell | — |
| Trigger | Manual modes + scheduled radar | Watch+react (auto-Bug-bash on issue threshold) |

---

## Cross-plugin composition

| Plugin | Required? | Role |
|---|---|---|
| `vibe-cartographer` | Optional (recommended for heavy iterations) | Pattern #13 deferral target for scope/prd/spec on big iterations |
| `schedule` | Required | Powers the weekly radar refresh |
| `vibe-doc` | Optional | Surfaced as a follow-up: *"shipped the iteration — want vibe-doc to update the affected docs?"* |
| `vibe-test` | Optional | Surfaced as a pre-flight: *"vibe-test gate would catch regressions before this PR — install it?"* |
| `vibe-sec` | Optional | Surfaced for security-sensitive iterations: *"this touches auth — vibe-sec would audit before ship"* |
| `discord` (MCP) | Optional | v1.1: internal-signal ingestion from a feedback channel |
| `context7` (MCP) | Optional (recommended) | Cutting-edge framework docs at decision-time |

---

## Cross-plugin meta-principle (lifted from session)

This design embodies a principle worth eventually lifting into the framework: **plugins are toolboxes, not single-purpose workflows.** Each plugin should expose:

1. **Banner workflows** — the headline use cases (e.g., `/vibe-doc:scan` for full-repo audit; vibe-iterate's modes for full mode runs)
2. **Sidecar tools** — the spot-tools the workflows use internally, exposed as standalone commands for "I just need this one thing" cases (e.g., a `/vibe-doc:check <single-doc>` style sidecar; vibe-iterate's six sidecars)

Worth retrofitting into vibe-doc, vibe-test, and vibe-sec when capacity allows. Logging to dashboard decisions when this design ships.

---

## Shipping details

- **Solo repo:** `vibe-iterate` (matches Cart, Doc, Thesis Engine pattern)
- **Path within solo:** `plugins/vibe-iterate` (matches Cart, Thesis Engine, Vibe Thesis pattern)
- **Tag naming:** `vX.Y.Z` (matches Cart, Doc, Thesis Engine, Vibe Thesis lineage; not the `<plugin>-vX.Y.Z` pattern Test and Sec inherited from `git-filter-repo` extraction)
- **Shared core consumption:** `@626labs/plugin-core` once it's past v0.0.1 (interface skeleton today)
- **Marketplace entry:** added to `.claude-plugin/marketplace.json` in this repo only after the solo repo has a v0.1.0 tag with a usable v1.0 build

---

## Decisions log (locked through Q&A)

| # | Decision | Rationale |
|---|---|---|
| 1 | Hybrid C: brief + build with own brain | "Reaching for Domain Expansion" — structured shell, full reach inside |
| 2 | v1.0 modes: feature-add, competitive, ux-polish, bug-bash. Stretch: perf, a11y. Cut: modernize. | User ranked 2,4,5,1,6,7; explicitly skipped 3 |
| 3 | External-signal-first for v1.0 | Apps are pre-user-volume; internal signal is thin |
| 4 | v1.0 sources: A + B + E | High signal, low noise; ships fast |
| 5 | Competitor inference from codebase + README, user confirms | Q3c ii — agent does work, user confirms; matches Cart's onboarding shape |
| 6 | Build engine: own muscle + Cart-detection enhancement + discovery upsell when missing | Avoids hard Cart dependency; surfaces Cart as a discovery moment |
| 7 | Knowledge: context7 + scheduled refresh + web-search fallback | III — both for the look up |
| 8 | One PR per session (α) | "On its toes," easier to review, tightest blast radius |
| 9 | Manual modes + scheduled radar (II) | Read-only radar can be scheduled; modes need intentional kickoff |
| 10 | Toolbox principle: 4 banner modes + 6 sidecar tools + 1 router | Multi-tool, not single-purpose; lifts cross-plugin |
| 11 | Persona: Ptolemy | Senior to Cart's field-cartographer; multi-source synthesis over already-shipped territory |
| 12 | Marketing one-liner: "vibe-iterate maintains your Atlas" | Atlas frame ties to Cart's cartography lineage |

---

## Open questions / deferred to v1.1

- Internal-signal connectors: GH Issues, Discord (via MCP), 626Labs Dashboard tasks, in-app feedback widget
- Watch+react trigger (auto-Bug-bash on issue threshold)
- `perf` and `accessibility` banner modes
- HN / Reddit / Twitter signal source (C); App Store / Play Store reviews (D)

---

## Out of scope (cut, not deferred)

- **Modernize banner mode.** Cut at Q2 ranking. The `:upgrade` sidecar covers the surgical "I want this one library current" case; full-repo dependency sweep is not in scope.
- **Auto-firing modes.** No mode runs without explicit user invocation. Even in v1.1's watch+react, the agent only proposes; the user kicks off.
- **Telemetry.** Per Este's standing rule (no telemetry in his plugins or apps), vibe-iterate emits no usage pings, no opt-in metrics, no phone-home. Atlas data stays local to the project.
