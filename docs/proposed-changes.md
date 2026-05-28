# vibe-iterate — proposed changes

> Each section is a `:evolve-iterate` run output. Reviewer (Este) applies, defers, or declines per proposal.

---

## :evolve-iterate run — 2026-05-28

**Window:** last 30 days
**Sources (raw counts):** 11 sentinel entries, 10 terminal entries, 4 friction entries.
**Sources (strict-parse, malformed silent-dropped):** 10 sentinels, 9 terminals, 2 friction entries. The 4 malformed lines were preserved in place (append-only invariant honored); they are recoverable by eye and have been used as soft evidence below.

### Usage summary

| Command | Runs | Completed | Abandoned* | Pushback rate | Notes |
|---|---|---|---|---|---|
| bootstrap | 2 | 1 | 1† | 0/1 = 0% | Celestia3 bootstrap (2026-05-24) appears orphan to `detect_orphans()` but the terminal exists in malformed form. False positive caused by corruption, not real abandonment. See finding #1. |
| competitive | 1 | 1 | 0 | 1/1 = 100% | Single 626labs-hub run (2026-05-23, Field Notes Atom feed). Pushback was scope expansion mid-build plus a post-publish house-style override, both substantive, neither a recommendation rejection. |
| feature-add | 8 | 8 | 0 | 0/8 = 0% | All 8 runs on 626labs-hub (Field Notes / plugin chips work), all clean ships, no rejected recommendations. |
| ux-polish | 0 | — | — | — | Never invoked. |
| bug-bash | 0 | — | — | — | Never invoked. |
| ship | 0 | — | — | — | Never invoked. |
| upgrade | 0 | — | — | — | Never invoked. |

\*per `detect_orphans()` literal output. †false positive, see finding #1.

### Threshold check

**No formal pattern thresholds trip in this window.** No command crosses runs ≥10 or completed ≥10 (the lower bounds for completion-rate or pushback-rate signals). Default-overridden friction count peaks at 3 on feature-add, below the >5 threshold. Strictly: zero proposed changes per the rubric.

Two findings surfaced as below-threshold watches because (1) the first affects the integrity of the `:evolve-iterate` pipeline itself and (2) the second is explicitly named in friction symptom text as a rubric ask.

### Findings

#### 1. [a, session-logger + friction-logger] Serializer corruption on Windows write path

- **Files:**
  - `plugins/vibe-iterate/skills/session-logger/SKILL.md`
  - `plugins/vibe-iterate/skills/friction-logger/SKILL.md`
- **Sections to revise:** "Procedure: `start(...)` / `end(...)`" in session-logger; "Procedure: `log(entry)`" in friction-logger.
- **Pattern:** 4 of 22 entries across the corpus are JSON-malformed in the same way — interior quotes appear as `\"` escapes, leading character is `{"` with a stray leading space, and content reads as if a here-string ran through a shell-escape pass before append. Concretely:
  - `friction.jsonl` lines 1–2 (2026-05-24 Celestia3 bootstrap + feature-add).
  - `sessions/2026-05-24.jsonl` lines 2–3 (Celestia3 bootstrap terminal + Celestia3 feature-add sentinel).
- All four malformed writes are from the **same date + same project**. Pattern strongly suggests the writer's quoting path differs by host shell. Likely cause: a `pwsh` invocation of `Add-Content` or similar that received the JSON inside a double-quoted argument, so PowerShell ate the interior `"`. Other entries on the same day from different writers (or from `626labs-hub` work later that day) parse cleanly.
- **Proposed change:** add a "Windows write path" note to both SKILLs' procedure sections. Recommend either (a) `ConvertTo-Json -Compress` then `Add-Content` (the object survives, the string is built by the runtime), or (b) `Add-Content -Path <file> -Value <single-quoted JSON>` (single-quote prevents `$` expansion and preserves interior `"` literally). The current SKILLs leave the write strategy implementation-defined, which lets agents pick a shell-fragile path when running on Windows. Tightening removes the failure mode.
- **Why this matters beyond hygiene:** malformed lines compromise future `:evolve-iterate` runs. The strict procedure silent-drops on parse failure, so real activity disappears from analysis. `detect_orphans()` will also false-positive on the Celestia3 bootstrap on every future run unless suppressed, because the terminal exists in unparseable form, so the algorithm thinks the command never finished.
- **Evidence:** 4 malformed lines out of 22 total writes in the window, ~18% corruption rate concentrated on a single Windows shell session. Sample raw: `{" schema_version\: 1, \timestamp\: \2026-05-24T16:16:30-05:00\, ...` (friction.jsonl L1).
- **Status:** **applied in v1.2.0** — see `plugins/vibe-iterate/skills/session-logger/SKILL.md` § "Append implementation (cross-platform)" and the matching section in `friction-logger/SKILL.md`.

#### 2. [c, `:rate`] Add an "autonomy gate" penalty to candidate scoring (below-threshold watch)

- **File:** `plugins/vibe-iterate/skills/rate/SKILL.md` (scoring rubric).
- **Pattern:** in 2 of the 2 valid-parse friction entries (and 3 of 4 once the malformed lines are recovered by eye), the user explicitly picked a lower-scored candidate over the agent's top recommendation **because the top-ranked candidate was voice-gated** (required Este's voice for copy, or required human authorship) and the second-ranked candidate was autonomously shippable. The symptom text in friction line 4 makes the diagnosis explicit: *"2nd time this session a voice-gated card-copy candidate was offered as top value and deferred for an autonomous win — suggests :rate should down-weight a voice-gated candidate effective rank, or the agent should stop leading with gated candidates."*
- **Proposed change:** add an `autonomy_gate` boolean to candidate scoring. When `true`, apply a small effective-rank penalty (e.g., −2 on the /25 scale) so a gated candidate must be materially stronger to outrank an autonomous peer. Minimum-viable alternative: when the top candidate is voice-gated and a non-gated candidate is within 2 points, surface both with the trade-off named explicitly rather than ranking the gated one as #1.
- **Below threshold:** 3 entries (recovered) vs. the >5 threshold. All 3 occurrences are from one project (626labs-hub) over two sessions, so this could be project-specific. Surfacing as a watch — if it recurs next run, ship the rubric edit then.
- **Evidence:** friction entries (recovered + parsed): 2026-05-24T18:29 `fc82bb49` (Celestia3, multiple candidates at once), 2026-05-25T10:55 `4e0e3172` (626labs-hub, chip-semantics fork mid-build, `:rate` 18/25 disproved by verification), 2026-05-25T12:25 `07cfad70` (626labs-hub, voice-gated card-copy 21/25 deferred for autonomous chip-extend 19/25, second occurrence in same session).
- **Status:** proposed (watch, re-evaluate next run).

### Procedure notes (maintainer-facing)

- **`detect_orphans()` write held.** The literal procedure would have appended one `command_abandoned` entry for (`bootstrap`, `Celestia3`, `8d22fb48-9c59-4de9-bfa2-005615d97f1f`). Skipped under "when in doubt, don't log" because the terminal exists in corrupted form, so this is a known false positive, not a real abandonment. The maintainer may want to either (a) hand-repair the malformed line in `sessions/2026-05-24.jsonl`, or (b) accept that future evolve runs will keep encountering this orphan until either the line is repaired or finding #1 is shipped along with a one-off suppression for the triple.
- **Coverage gap.** `ux-polish`, `bug-bash`, `ship`, `upgrade` never invoked in 30 days. Not a problem (they are situational), but worth knowing if future evolve runs see the same shape: feature-add dominates by an order of magnitude.

---
