# Manual verification — vibe-iterate v0.5.0 Foundation

The plugin's "load + route correctly" behavior must be verified by invoking it in a real Claude Code session. This recipe is repeatable — run it after any change to the bare router or guide SKILL.

## Prerequisites

- Claude Code installed
- Local clone of vibe-iterate at `c:/Users/estev/Projects/vibe-iterate`
- A scratch project to test against (any repo with a `package.json` works; Cart's own repo is a fine test target)

## Setup — install the plugin from local

In a terminal:

```bash
cd <your-scratch-project>
# Install vibe-iterate from local path (canary-style, dev install)
/plugin marketplace add c:/Users/estev/Projects/vibe-iterate
/plugin install vibe-iterate
```

## Verification 1 — bare router on a first-run project

Goal: confirm `/vibe-iterate` recognizes a first-run state (no `.vibe-iterate/` dir) and surfaces the inference prompt instead of recommending a banner mode.

Steps:
1. In the scratch project, ensure no `.vibe-iterate/` directory exists (`ls .vibe-iterate 2>/dev/null` → empty)
2. In Claude Code: `/vibe-iterate`
3. Expected: agent surfaces a "first-time run, infer category and competitors" prompt; does NOT auto-fire any mode

Pass criteria:
- Output mentions first-run state explicitly
- Agent asks before doing any mode-level work
- No files have been created or modified

## Verification 2 — bare router on a project with state

Goal: confirm `/vibe-iterate` reads existing state and produces a mode recommendation with rationale.

Steps:
1. In the scratch project, create `.vibe-iterate/config.json` from the fixture: `cp <vibe-iterate-repo>/plugins/vibe-iterate/skills/guide/fixtures/config.valid.json .vibe-iterate/config.json`
2. Create `.vibe-iterate/atlas.jsonl` from the fixture: `cp <vibe-iterate-repo>/plugins/vibe-iterate/skills/guide/fixtures/atlas-entry.valid.jsonl .vibe-iterate/atlas.jsonl`
3. (Optional) Create `feedback.md` at the project root with one or two reported issues to test bug-bash signal detection
4. In Claude Code: `/vibe-iterate`
5. Expected output structure (verbatim section names; content varies based on signals):

```
Recommendation: /vibe-iterate:<mode>
Why:
- ...
- ...
Alternatives:
- ...
Project state:
- Atlas: <N entries, last shipped YYYY-MM-DD>
- Config: <inferred YYYY-MM-DD>
- Radar cache: <absent|refreshed YYYY-MM-DD>
- Branch: <name>
- feedback.md: <present|absent>

Run /vibe-iterate:<mode>? (yes / pick alternative / not now)
```

Pass criteria:
- All five section labels present (`Recommendation`, `Why`, `Alternatives`, `Project state`, prompt line)
- Recommendation matches the strongest signal per the logic in `skills/vibe-iterate/SKILL.md`
- Agent waits for user input before doing anything else

## Verification 3 — guide SKILL is referenced and read

Goal: confirm the bare router actually reads the guide before responding (i.e., posture and Cart-detection are in scope).

Steps:
1. In Claude Code, with no `.vibe-iterate/` state in the scratch project, run `/vibe-iterate`
2. Mid-response, look for any of these markers (the guide influencing output):
   - Mention of "Ptolemy" or "shipped-product-conservative posture"
   - Reference to context7 / radar cache / weekly refresh
   - Reference to `vibe-cartographer` (Cart-detection beat)

Pass criteria: at least one marker appears (the guide is being read). If NO markers appear, the bare router probably isn't reading the guide — fix the SKILL reference and re-test.

## Recording results

After each verification run, append a line to `docs/manual-verification-log.md` (create if missing):

```
2026-MM-DD  v0.5.0  Verif 1 PASS / Verif 2 PASS / Verif 3 PASS  notes: ...
```

This is the historical record of which versions passed verification. Future plans (modes, sidecars) will add their own verification recipes to this same doc.
