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

## :evolve-iterate run — 2026-06-09

**Window:** last 30 days (2026-05-10 → 2026-06-09)
**Sources (raw, in-window):** 11 sentinel lines, 11 terminal lines, 4 friction lines
**Sources (strict-parse, malformed silent-dropped):** 10 sentinels, 10 terminals, 2 friction entries
**Data delta since the 2026-05-28 run: zero new entries.** No session or friction writes since 2026-05-25 (file mtimes agree). The corpus is byte-identical to the prior run's; only the window moved — the 2026-05-07 vibe-Keystone bootstrap aged out, which is why bootstrap shows 1 run here vs 2 in the prior section.

### Usage summary

| Command | Runs | Completed | Abandoned | Pushback rate | Notes |
|---|---|---|---|---|---|
| bootstrap | 1 | 0 strict / 1 recovered | 0 | 0/1 = 0% | Celestia3 (2026-05-24). Terminal exists only as a corrupted line (pre-v1.2.0 serializer bug); reads as completed when recovered by eye. |
| competitive | 1 | 1 | 0 | 1/1 = 100% | Same single 626labs-hub run the prior section analyzed; below the completed ≥ 10 floor, no signal. |
| feature-add | 9 (8 strict) | 9 | 0 | 0/9 = 0% | 8 runs on 626labs-hub + 1 on Celestia3, all clean ships. The Celestia3 sentinel (`fc82bb49`) is one of the four corrupted 2026-05-24 lines, hence strict runs < completed. |
| ux-polish | 0 | — | — | — | Never invoked. |
| bug-bash | 0 | — | — | — | Never invoked. |
| ship | 0 | — | — | — | Never invoked. |
| upgrade | 0 | — | — | — | Never invoked. |

`detect_orphans()` ran first per procedure: its 7-day scan window (2026-06-02 onward) contains no session files, so zero orphans, zero friction writes. Side effect worth naming: the Celestia3-bootstrap false-positive orphan flagged in the prior run's procedure notes is now permanently retired — the 2026-05-24 sentinel has aged out of the orphan scan window and can't re-fire.

### Threshold check

**No pattern threshold trips.** With zero new entries, nothing could have crossed since 2026-05-28:

- `completion_rate < 0.6` needs runs ≥ 10 — max is feature-add at 9.
- `pushback_rate > 0.3` needs completed ≥ 10 — max is feature-add at 9; competitive's 100% sits on n=1.
- `default_overridden` > 5 per command — feature-add peaks at 3 recovered (2 strict).
- `complement_rejected` ≥ 5, `command_abandoned` > 3, `repeat_question` ≥ 3 — all at 0.

### Proposed changes

**None this run.** No threshold tripped and no new evidence arrived. Re-deriving proposals from the same corpus the 2026-05-28 section already analyzed would be noise, not signal.

### Watch item re-weigh — autonomy-gate penalty for `:rate` (prior finding #2)

**Stays parked.** Re-weighed with the full window:

- **No new signal.** 0 friction entries logged since 2026-05-25. Count holds at 3 recovered (2 strict-parse) `default_overridden` on feature-add vs the >5 threshold. Two of the three (`4e0e3172`, `07cfad70`) name the voice-gating mechanism; the third (`fc82bb49`) is a batch-ship ask the prior run grouped in.
- **Expiry warning.** All three supporting entries date 2026-05-24/25 and leave a 30-day window by 2026-06-25. If no banner-mode runs land before the next evolve run, the watch shows zero in-window evidence. That's the rubric working as designed — stale signal shouldn't drive edits — but the watch then expires by aging, not by resolution. Worth knowing when a future run reads "0 entries."
- **Counter-signal to carry forward** if the pattern ever crosses threshold: session `56db624f` (2026-05-24) shipped the long-deferred voice-gated candidate on direct request — agent-drafted copy + copy-reviewer + verify, PR as the approval surface — and logged the calibration note that "'needs your voice' doesn't always mean defer." If a fix ships someday, "draft the gated candidate and stage the PR as the approval surface" competes with (or complements) the rank-penalty shape proposed in the prior section. Decide then, with data.

### Below-threshold signals (excluded from proposals)

Logged so the exclusion is auditable; none crosses its bar.

1. **Voice-gated top-rank deferral** — 3 recovered / 2 strict vs >5. The watch item above.
2. **`:rate` scoring-assumption miss** — 1 entry (`4e0e3172`: 18/25 assumed a uniform command/skill structure; verification disproved it mid-build, forcing a semantics fork). Distinct mechanism from voice-gating (score confidence vs candidate gating); would need its own recurrence to act on.
3. **Batch-ship ask** — 1 recovered entry (`fc82bb49`: user wanted candidates #1+#2 in one run; flow forced sequential).
4. **Bootstrap competitor-input UX** — 1 recovered low-confidence entry (`8d22fb48`: non-URL competitor description skipped).
5. **Competitive pushback** — 1/1, below the completed ≥ 10 floor; both pushback events were substantive scope/style calls, not recommendation rejections (per prior section).
6. **Atlas-staleness candidate pollution** — 2 session friction_notes (`b4594611`, `42bf67b1`): already-shipped work re-surfaced as candidates because out-of-band ships had no Atlas record; verify-before-build caught both. No structured friction type covers this today; if it recurs, it may justify a trigger-map row (type b). Watch, don't act.

### Procedure notes (maintainer-facing)

- **Prior finding #1 (Windows serializer corruption): applied in v1.2.0, not re-proposed.** Field validation still pending — every entry in the corpus is plugin_version 1.0.0/1.1.0; zero post-v1.2.0 writes exist yet. The first post-v1.2.0 banner-mode run on a Windows shell is the real test; one glance at the appended line settles it.
- **Hand-repair of the four corrupted 2026-05-24 lines is now fidelity-only.** The orphan false-positive rationale is gone (aged out of the 7-day scan). Remaining cost of leaving them: strict-parse undercounts Celestia3 activity (bootstrap completion, `fc82bb49` sentinel, 2 friction entries) until evolve runs on/after 2026-06-24, when they leave the 30-day analysis window too. After that, repair is purely archival.
- **15 days of log silence (2026-05-25 → 2026-06-09).** The logs can't distinguish "no banner-mode runs happened" from "runs happened and logging silently failed." If banner modes were in fact run in this span, that's a logging regression to investigate — and it would also mean the v1.2.0 field validation above is overdue.
- **Coverage gap persists.** ux-polish, bug-bash, ship, upgrade: still zero lifetime runs. feature-add dominates by an order of magnitude, same shape as the prior section.

---
