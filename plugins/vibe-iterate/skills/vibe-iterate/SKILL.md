---
name: vibe-iterate
description: "This skill should be used when the user says `/vibe-iterate` (bare, no subcommand). Reads project state (Atlas, radar cache, recent commits), recommends a mode for the moment (feature-add, competitive, ux-polish, bug-bash), and asks before launching. On first run (no .vibe-iterate/ directory), gracefully hands off to the bootstrap skill before recommending. Never auto-fires."
---

# /vibe-iterate — bare router

Read [`../guide/SKILL.md`](../guide/SKILL.md) for shared agent behavior (Ptolemy persona, posture, knowledge sources, Atlas conventions, Cart-detection), then follow this command.

## What this command does

Bare router. The user invoked `/vibe-iterate` with no subcommand — they want help choosing a mode. The agent's job is to:

1. **Detect the project state.** Is `.vibe-iterate/` set up? If not, the first-run path takes over (graceful — see below).
2. **Read the project's signals** (Atlas, radar cache, recent commits, branch state, presence of `feedback.md`).
3. **Synthesize:** what's the most useful mode RIGHT NOW for this project?
4. **Recommend ONE mode** with rationale.
5. **Surface 1-2 alternatives** with rationale for why they're second/third.
6. **Ask the user to confirm** before launching anything.

## Hard rules

- **Never auto-fire a mode.** Always ask the user before invoking another command.
- **Read-only by default.** This command does NOT write to the Atlas, the config, or any project file. (Bootstrap, when invoked from here, does write — but only after the user confirms.)
- **One recommendation, with alternatives.** Don't surface a 5-mode menu; that's not a recommendation.
- **No litany on first run.** When the project is fresh, don't enumerate everything that's missing. Acknowledge once, hand off to bootstrap, move on.

## First-run path (graceful)

If `.vibe-iterate/config.json` is **absent**, the project hasn't been set up. Ptolemy's response:

```
Fresh repo — no config yet. Let me get the lay of the land before recommending a mode.
```

Then immediately invoke the **bootstrap** SKILL ([`../bootstrap/SKILL.md`](../bootstrap/SKILL.md)). Bootstrap handles app-type identification, the brief interview, and writing `.vibe-iterate/config.json`. After bootstrap returns, the bare router does NOT auto-recommend a mode — bootstrap's output already prompts the user to re-run `/vibe-iterate` for a recommendation. This is intentional: the user makes the deliberate choice.

**Don't:**
- Don't say "First-time vibe-iterate run on this project. I'll need to infer your category and competitors before any banner mode can run productively." That's a lecture.
- Don't enumerate every state file that's missing.
- Don't try to recommend a mode without config — modes need the config to do their job.

**Do:**
- Acknowledge once, in one short line, that this is a fresh repo.
- Invoke bootstrap.
- Let bootstrap's output close the loop.

## Stale-config path (graceful)

If `.vibe-iterate/config.json` exists but `last_inferred_at` is **>30 days old**, surface a one-line nudge AT THE END of the recommendation (not the beginning — don't gate the recommendation on it):

```
(Config last refreshed N days ago — consider /vibe-iterate:bootstrap when you have a sec.)
```

Don't block. Don't re-bootstrap automatically. The recommendation is the headline; the refresh nudge is a sidebar.

## Project state to read (in order, when config exists)

1. **Atlas (`.vibe-iterate/atlas.jsonl`).** If absent or empty, no iterations have shipped yet — that's fine, just note "no shipped iterations yet" in project state.
2. **Config (`.vibe-iterate/config.json`).** Present (else first-run path took over). Read `category`, `competitors`, `framework_pins`, `last_inferred_at`.
3. **Radar cache (`.vibe-iterate/radar.cache.json`).** If absent or `refreshed_at` is >14 days old, mark cache as stale; surface as a follow-up nudge: *"Run `/vibe-iterate:radar` for a fresh signal scan."*
4. **Recent commits.** Last 10 on the current branch via `git log --oneline -10`. What's been shipped recently?
5. **Branch state.** On `main`/`master`? On a feature branch? Any uncommitted changes (`git status --porcelain`)?
6. **`feedback.md` presence.** If present at project root, surface as input for Bug-bash candidate. Read first 30 lines for context (don't read the whole file — that's the bug-bash mode's job).

## Mode recommendation logic

Pick ONE based on the strongest signal:

| Signal (in priority order) | Recommend |
|---|---|
| `feedback.md` exists with unaddressed items, AND last Atlas-shipped item was >7 days ago | **bug-bash** — users have things to say, address them |
| Radar cache shows competitor changelogs with new items in user's category | **competitive** — gap-close opportunity |
| Radar cache shows >3 framework releases since last shipped iteration | **feature-add** — fresh framework features may unblock prioritized items |
| Recent commits show 3+ feature lands but no polish PRs (no commits matching `^(fix|polish|ui)`) | **ux-polish** — the surfaces are getting rough |
| Atlas shows >5 recent shipped entries, no rejected ones | **feature-add** (with a gentle note: review the Atlas; you may be over-shipping without considering tradeoffs) |
| Nothing clearly in scope | **feature-add** as the safest default; let the user pivot |

When two signals tie, prefer the mode the user has invoked LEAST recently (per Atlas history — count `mode` occurrences in the last 30 days, prefer least-frequent).

## Output shape (when config exists)

Render the recommendation in this structure:

```
Recommendation: /vibe-iterate:<mode>

Why:
- [signal 1, with one-line evidence]
- [signal 2, with one-line evidence]

Alternatives:
- /vibe-iterate:<other-mode-1> — [why this is second]
- /vibe-iterate:<other-mode-2> — [why this is third]

Project state:
- Atlas: <N entries, last shipped YYYY-MM-DD>
- Config: <inferred YYYY-MM-DD>
- Radar cache: <refreshed YYYY-MM-DD or "absent">
- Branch: <main or feature/...>
- feedback.md: <present|absent>

Run /vibe-iterate:<mode>? (yes / pick alternative / not now)
```

Wait for the user's response. Do NOT invoke any subcommand on your own.

## Posture announcement at session-start

Before producing the recommendation, surface the register in one short line so the user knows what brain is loaded:

> *Routing → conservative read. I'm reading state, not writing anything.*

Skip the announcement on the first-run path (bootstrap does its own announcement).

## Cross-references

- Bootstrap SKILL: [`../bootstrap/SKILL.md`](../bootstrap/SKILL.md) — invoked on first run
- Banner modes: [`../feature-add/SKILL.md`](../feature-add/SKILL.md), [`../competitive/SKILL.md`](../competitive/SKILL.md), [`../ux-polish/SKILL.md`](../ux-polish/SKILL.md), [`../bug-bash/SKILL.md`](../bug-bash/SKILL.md)
- Sidecars: [`../radar/SKILL.md`](../radar/SKILL.md), [`../rate/SKILL.md`](../rate/SKILL.md), [`../spy/SKILL.md`](../spy/SKILL.md), [`../scan-releases/SKILL.md`](../scan-releases/SKILL.md), [`../ship/SKILL.md`](../ship/SKILL.md), [`../upgrade/SKILL.md`](../upgrade/SKILL.md)
- Guide: [`../guide/SKILL.md`](../guide/SKILL.md)
