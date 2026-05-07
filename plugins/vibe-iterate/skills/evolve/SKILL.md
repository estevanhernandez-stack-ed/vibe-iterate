---
name: evolve
description: "This skill should be used when the user says `/vibe-iterate:evolve` and wants vibe-iterate to reflect on past sessions and propose improvements to itself. Reads ~/.claude/plugins/data/vibe-iterate/ session logs + friction.jsonl, weights findings, writes proposed SKILL/trigger/rubric edits to docs/proposed-changes.md in the vibe-iterate solo repo. Never auto-applies. L3 self-evolution."
---

# /vibe-iterate:evolve — reflect on past sessions and propose improvements

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona), then follow this command.

## What this command does

Reads vibe-iterate's session log (`~/.claude/plugins/data/vibe-iterate/sessions/*.jsonl`) and friction log (`~/.claude/plugins/data/vibe-iterate/friction.jsonl`), weights observed patterns, and writes proposed improvements to **`docs/proposed-changes.md`** in the vibe-iterate solo repo. The proposed changes are not auto-applied — they're recommendations for the maintainer (Este) to review and apply manually (or via a follow-up `:ship` invocation).

This is **Level 3** of the Self-Evolving Plugin Framework: the plugin reflects on its own past behavior and surfaces what to change next.

## Hard rules

- **Read-only on the source data.** `:evolve` does not edit `~/.claude/plugins/data/vibe-iterate/` files. Sessions and friction logs are append-only; `:evolve` reads them.
- **Never auto-applies proposed changes.** The output is `docs/proposed-changes.md` — a human-readable proposal. The maintainer reviews and applies.
- **Suppress noise.** Apply confidence-weighted thresholds (described below). Don't surface every single friction entry as a proposal — only patterns.
- **Cite evidence.** Every proposed change names the friction entries / session entries that motivated it. The maintainer should be able to grep the logs and verify.

## Inputs

- **No required arguments.** Optional `--window <N>` to restrict analysis to the last N days (default: 30).
- **Source data:**
  - `~/.claude/plugins/data/vibe-iterate/sessions/*.jsonl` — daily session log files
  - `~/.claude/plugins/data/vibe-iterate/friction.jsonl` — append-only friction signals
- **Output target:** `docs/proposed-changes.md` in the vibe-iterate solo repo (this file). If the file already exists from a prior `:evolve` run, append a new section with today's date — don't overwrite.

If neither source data file exists (fresh install with no usage), surface: *"No session or friction data yet. `:evolve` learns from your past `vibe-iterate` runs — invoke a banner mode a few times, then re-run `:evolve`."* and exit.

## Procedure

### Step 1 — posture announcement

> *Evolve mode → analytical posture, conservative on proposals. Reading <N> days of sessions + friction, weighting patterns, drafting proposed changes. Output is a human-readable proposal — nothing auto-applies.*

### Step 2 — call `friction-logger.detect_orphans()`

Catches any backlog of abandoned commands (sentinel without terminal >24h old). These become `command_abandoned` friction entries before the analysis reads the friction log.

Per [`../friction-logger/SKILL.md`](../friction-logger/SKILL.md).

### Step 3 — load the data

- Enumerate `~/.claude/plugins/data/vibe-iterate/sessions/*.jsonl` files within the analysis window. Parse each line; skip malformed silently.
- Read `~/.claude/plugins/data/vibe-iterate/friction.jsonl`. Parse each line; skip malformed silently.
- Filter to entries within `--window` days.

If either file is missing, treat as empty array and continue. If both are empty, exit per the input case above.

### Step 4 — compute usage metrics (per command)

For each command (`bootstrap`, `feature-add`, `competitive`, `ux-polish`, `bug-bash`, `ship`, `upgrade`):

- `runs` — count of sentinel entries
- `completed` — count of terminal entries with `outcome: "completed"`
- `abandoned` — count of orphan entries (`command_abandoned` friction)
- `partial` — count of terminal entries with `outcome: "partial"`
- `error` — count of terminal entries with `outcome: "error"`
- `completion_rate` — `completed / runs`
- `pushback_rate` — count of terminal entries with `user_pushback: true` divided by `completed`

### Step 5 — compute friction patterns

For each `friction_type`:

- `count` — total entries in the window
- `by_command` — count grouped by command
- `confidence_distribution` — count grouped by confidence level
- `common_complement` (for `complement_rejected` only) — most frequent `complement_involved` value

### Step 6 — apply pattern thresholds

Surface a pattern as a proposed change only if at least one threshold trips:

| Threshold | Pattern observation |
|---|---|
| `completion_rate < 0.6` for a command with `runs >= 10` | The command fails too often. Investigate the workflow. |
| `pushback_rate > 0.3` for a command with `completed >= 10` | Users override the recommendation often. The default may be wrong. |
| `default_overridden` count for a command > 5 in the window | The recommendation logic should be revisited. |
| `complement_rejected` for a specific complement >= 5 in the window | The Pattern #13 upsell is firing too often or at the wrong moments. |
| `command_abandoned` for a specific command > 3 in the window | Users start the command but bail. Workflow may have a friction wall. |
| `repeat_question` for a specific command >= 3 (with confidence high) | The agent's first answer wasn't satisfying. Documentation gap or unclear output. |

For each tripped threshold, formulate a proposed change. Skip patterns that don't trip any threshold — they're noise.

### Step 7 — formulate proposed changes

For each pattern, generate one of these proposal shapes:

**(a) SKILL body edit**
- File: `plugins/vibe-iterate/skills/<command>/SKILL.md`
- Section to revise: name the H2/H3 heading
- Suggested change: one paragraph
- Evidence: list the session/friction entries (count + sample)

**(b) Trigger map edit**
- File: `plugins/vibe-iterate/skills/guide/references/friction-triggers.md`
- Trigger to add/remove/re-tune: name the row
- Suggested change: new confidence level OR new trigger condition
- Evidence: as above

**(c) Rubric edit**
- File: where the rubric lives (e.g., `:rate`'s scoring rubric, `:ux-polish`'s user-trust-impact tiers)
- Tier or scoring weight to adjust
- Suggested change
- Evidence

**(d) New SKILL or sidecar**
- Proposed name and scope
- What recurring friction it would address
- Evidence

### Step 8 — write `docs/proposed-changes.md`

Append (or create) `docs/proposed-changes.md` in the vibe-iterate solo repo. Section structure:

```markdown
# vibe-iterate — proposed changes

> Each section is a `:evolve` run output. Reviewer (Este) applies, defers, or declines per proposal.

---

## :evolve run — YYYY-MM-DD

**Window:** last <N> days
**Sources:** <count> sentinel entries, <count> terminal entries, <count> friction entries

### Usage summary

| Command | Runs | Completed | Abandoned | Pushback rate | Notes |
|---|---|---|---|---|---|
| feature-add | <N> | <N> | <N> | <pct> | <one-line> |
| ... | ... | ... | ... | ... | ... |

### Proposed changes

#### 1. [a/b/c/d type]: <one-line summary>

- **File:** <path>
- **Section:** <heading>
- **Pattern:** <which threshold tripped>
- **Proposed change:**
  > <one paragraph>
- **Evidence:** <count> entries (sample: `<friction entry summary>`, `<another>`)
- **Status:** proposed (not applied)

#### 2. ...

---

## :evolve run — <next date>
...
```

### Step 9 — close out

```
:evolve complete.

Window: last <N> days
Source: <count> sentinels / <count> terminals / <count> friction entries

Proposed changes: <N>  ← see docs/proposed-changes.md (latest section)

Patterns surfaced:
- <pattern 1 — one-line>
- <pattern 2 — one-line>
- ...

Next:
- Review docs/proposed-changes.md
- Apply via /vibe-iterate:ship "<paste proposal>" or hand-edit the affected files
```

## Anti-patterns

- **Don't auto-apply.** Even high-confidence patterns are proposals, not commits. The maintainer's eye is the gate.
- **Don't surface raw friction entries.** Patterns ≥ thresholds, not individual events. Otherwise the proposed-changes file becomes a friction dump.
- **Don't propose changes outside the plugin.** `:evolve` proposes edits to `plugins/vibe-iterate/` and `docs/`. It does NOT propose edits to host projects' code or other plugins.
- **Don't read project-level files.** `:evolve` is plugin-meta. It reads `~/.claude/plugins/data/vibe-iterate/`, NOT `.vibe-iterate/atlas.jsonl` (that's project state).

## Cross-references

- Session log SKILL: [`../session-logger/SKILL.md`](../session-logger/SKILL.md)
- Friction log SKILL: [`../friction-logger/SKILL.md`](../friction-logger/SKILL.md)
- Trigger map: [`../guide/references/friction-triggers.md`](../guide/references/friction-triggers.md)
- Framework reference (in vibe-cartographer): `docs/self-evolving-plugins-framework.md` Levels 2 + 3
