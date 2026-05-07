# Manual verification — vibe-iterate v1.0.0

The plugin's "load + route correctly" behavior must be verified by invoking it in a real Claude Code session. This recipe is repeatable — run it after any change to a SKILL.

## Prerequisites

- Claude Code installed
- Local clone of vibe-iterate at `c:/Users/estev/Projects/vibe-iterate`
- A scratch project to test against (any repo with a `package.json` works; cart's own repo is a fine test target)

## Setup — install the plugin from local

In a terminal, in the scratch project's directory:

```
/plugin marketplace add c:/Users/estev/Projects/vibe-iterate
/plugin install vibe-iterate
```

## Verification 1 — bare router on a first-run project (graceful UX)

Goal: confirm `/vibe-iterate` recognizes a first-run state (no `.vibe-iterate/` dir) and routes gracefully to bootstrap WITHOUT a preachy "I'll need to infer your category and competitors before any banner mode can run productively" lecture.

Steps:
1. In the scratch project, ensure no `.vibe-iterate/` directory exists (`ls .vibe-iterate 2>/dev/null` → empty)
2. In Claude Code: `/vibe-iterate`
3. Expected: agent surfaces a one-line acknowledgment ("Fresh repo — no config yet. Let me get the lay of the land before recommending a mode.") then invokes bootstrap

Pass criteria:
- Output mentions first-run state in ONE short line — no enumeration of missing files
- Bootstrap is invoked next
- No mode runs without explicit user invocation

## Verification 2 — bootstrap (app-type identification + interview)

Goal: confirm `/vibe-iterate:bootstrap` auto-classifies the app type, confirms in one short question, asks for competitor URLs, and writes `.vibe-iterate/config.json`.

Steps:
1. Run from a fresh repo with no `.vibe-iterate/` (or after clearing it: `rm -rf .vibe-iterate`)
2. In Claude Code: `/vibe-iterate:bootstrap`
3. Expected:
   - Posture announcement (one line)
   - Auto-classification surfaced in the form `Looks like a [framework anchor] — I'd classify this as a [category]. Right? (yes / pick another / let me describe it)`
   - One question about competitors
   - `.vibe-iterate/config.json` written
   - One-line close-out

Pass criteria:
- Two questions max (classification confirm, competitor URLs)
- `.vibe-iterate/config.json` exists and validates against `plugins/vibe-iterate/skills/guide/schemas/config.schema.json`
- No `atlas.jsonl` or `radar.cache.json` pre-created (correct per the design)
- No mode auto-fires after bootstrap

## Verification 3 — bare router on a project with state

Goal: confirm `/vibe-iterate` reads existing state and produces a mode recommendation with rationale.

Steps:
1. After Verification 2, the scratch project has `.vibe-iterate/config.json`. Optionally seed `.vibe-iterate/atlas.jsonl` with the fixture: `cp <vibe-iterate-repo>/plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl .vibe-iterate/atlas.jsonl`
2. Optionally create `feedback.md` at the project root with one or two reported issues to test bug-bash signal detection
3. In Claude Code: `/vibe-iterate`
4. Expected output structure (verbatim section names; content varies based on signals):

```
Recommendation: /vibe-iterate:<mode>

Why:
- ...
- ...

Alternatives:
- /vibe-iterate:<other> — ...

Project state:
- Atlas: <N entries, last shipped YYYY-MM-DD>
- Config: <inferred YYYY-MM-DD>
- Radar cache: <absent|refreshed YYYY-MM-DD>
- Branch: <name>
- feedback.md: <present|absent>

Run /vibe-iterate:<mode>? (yes / pick alternative / not now)
```

Pass criteria:
- All five section labels present
- Recommendation matches the strongest signal per the logic in `skills/vibe-iterate/SKILL.md`
- Agent waits for user input before doing anything else

## Verification 4 — sidecar `:rate` (read-only scoring)

Goal: confirm `/vibe-iterate:rate <idea>` produces five scores with evidence cites, a verdict, and respects Atlas history.

Steps:
1. With `.vibe-iterate/config.json` and (optionally) `.vibe-iterate/atlas.jsonl` present:
2. In Claude Code: `/vibe-iterate:rate "add saved searches"`
3. Expected:
   - Five scores (impact, fit-with-stack, effort, regression-risk, user-trust-impact), each with an evidence cite
   - Total /25
   - One-paragraph rationale
   - Verdict: ship-now | queue | decline + one-line action

Pass criteria:
- Every score cites a specific file, commit, competitor URL, framework feature, or Atlas entry — not "(this seems important)"
- If the Atlas contains a near-duplicate rejected in the last 60 days, the rationale surfaces it
- No file writes (rate is read-only)

## Verification 5 — sidecar `:radar` (graceful when cache absent)

Goal: confirm `/vibe-iterate:radar` handles a missing cache gracefully.

Steps:
1. Ensure `.vibe-iterate/radar.cache.json` does NOT exist
2. In Claude Code: `/vibe-iterate:radar`
3. Expected: surface "No radar cache yet" + offer manual refresh; on opt-in, fetch + write cache; on opt-out, exit cleanly

Pass criteria:
- No noisy stack trace or "file not found" error
- User opt-in flow works (manual refresh writes cache; subsequent `:radar` calls render the digest)

## Verification 6 — banner mode `:bug-bash` dormant case

Goal: confirm `/vibe-iterate:bug-bash` surfaces the dormant nudge gracefully when `feedback.md` is absent.

Steps:
1. Ensure `feedback.md` does NOT exist at the project root
2. In Claude Code: `/vibe-iterate:bug-bash`
3. Expected: one-line nudge ("Bug-bash needs internal signal. Two options: ...") + exit

Pass criteria:
- No technical lecture
- No `feedback.md` auto-created
- Exits cleanly

## Verification 7 — guide SKILL is referenced and read

Goal: confirm command SKILLs read the guide before responding (i.e., posture and Cart-detection are in scope).

Steps:
1. Run any banner mode (e.g., `/vibe-iterate:feature-add`)
2. Mid-response, look for any of these markers (the guide influencing output):
   - Posture announcement at the top ("→ <mode> mode — <register>")
   - Mention of Cart-detection (if config and `vibe-cartographer:*` skills are both present)
   - Mention of Atlas read pattern

Pass criteria: at least one marker appears.

## Verification 8 — session + friction logging

Goal: confirm session + friction entries are written to `~/.claude/plugins/data/vibe-iterate/`.

Steps:
1. Run `/vibe-iterate:bootstrap` (or any banner mode) end-to-end
2. After completion, check:
   - `cat ~/.claude/plugins/data/vibe-iterate/sessions/<today>.jsonl` — should show TWO entries with the same `sessionUUID` (sentinel + terminal)
   - `cat ~/.claude/plugins/data/vibe-iterate/friction.jsonl` — should be empty (or show entries only if the user actually triggered a friction signal during the run)

Pass criteria:
- Sentinel `outcome: "in_progress"`, terminal `outcome: "completed"`
- Both share the same sessionUUID
- No PII beyond `project_dir` basename
- No telemetry — files stay local, never sent anywhere

## Verification 9 — `/vibe-iterate:evolve` on no data

Goal: confirm `:evolve` handles the no-data case gracefully.

Steps:
1. In a fresh state (no `~/.claude/plugins/data/vibe-iterate/sessions/` or empty), run `/vibe-iterate:evolve`
2. Expected: surface "No session or friction data yet. `:evolve` learns from your past `vibe-iterate` runs — invoke a banner mode a few times, then re-run `:evolve`." + exit

Pass criteria:
- No stack trace
- No `docs/proposed-changes.md` written

## Recording results

After each verification run, append a line to `docs/manual-verification-log.md`:

```
2026-MM-DD  v1.0.0  Verif 1-9 PASS  notes: ...
```

This is the historical record of which versions passed verification.
