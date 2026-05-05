---
name: vibe-iterate
description: "This skill should be used when the user says `/vibe-iterate` (bare, no subcommand). Reads project state (Atlas, radar cache, recent commits), recommends a mode for the moment (feature-add, competitive, ux-polish, bug-bash), and asks before launching. Never auto-fires."
---

# /vibe-iterate — bare router

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources), then follow this command.

## Status

**Implementation pending.** v0.1.0 scaffold stub. Locked design lives in [`../../../../docs/2026-05-04-vibe-iterate-design.md`](../../../../docs/2026-05-04-vibe-iterate-design.md) — see *Banner modes → Bare router*.

## Spec summary

Bare router. Reads project state — Atlas (`.vibe-iterate/atlas.jsonl`), radar cache (`.vibe-iterate/radar.cache.json`), recent commits, current branch state — and recommends a mode for the moment. Asks before launching. Never auto-fires.

## Implementation references

- Spec: `docs/2026-05-04-vibe-iterate-design.md` — *Banner modes → Bare router*
- Shared guide: [`../guide/SKILL.md`](../guide/SKILL.md) — Ptolemy persona, posture, knowledge sources
