<p align="center">
  <img alt="Vibe Iterate — post-ship product iteration, one PR at a time" src="https://626labs.dev/assets/brand/plugins/vibe-iterate-banner-1500x500.png" />
</p>

# Vibe Iterate

**Post-ship product iteration — where vibe-cartographer takes you idea → v1, vibe-iterate takes you v1 → v1+n, indefinitely.**

[![stable](https://img.shields.io/github/v/tag/estevanhernandez-stack-ed/vibe-iterate?label=stable&color=17d4fa)](https://github.com/estevanhernandez-stack-ed/vibe-iterate/tags)

## What it does

You shipped v1. Now what's next? Vibe Iterate maintains your Atlas — the running ledger of what you've shipped and why — and turns "what should we build next" into one focused PR per session. The posture is fixed: regression-aware, user-trust-aware, small-diff-preferred. The agent (Ptolemy) stays current on big-shoulder software via context7 and a weekly framework-release scan.

Pick a banner mode for the moment, or reach for a sidecar tool when you already know the move:

**Banner modes** — one PR per run, each with an Atlas entry:

- `/vibe-iterate` — bare router; recommends a mode for the moment, asks before launching. On first run, hands off gracefully to `/vibe-iterate:bootstrap`.
- `/vibe-iterate:feature-add` — what should we build next? Multi-source candidate-driven (competitors + Product Hunt + framework releases + `feedback.md`).
- `/vibe-iterate:competitive` — what do they have that we don't? Strategic-relevance scoring (match / differentiate / decline), not parity.
- `/vibe-iterate:ux-polish` — what's shipped but rough? Walks routes/components/flows, scores by user-trust impact.
- `/vibe-iterate:bug-bash` — what's broken according to users? Reads `feedback.md`; triages by severity × frequency × blast-radius. Dormant when `feedback.md` is missing (one-line nudge only).

**Sidecar tools** — sharp single-purpose reads and surgical moves:

- `/vibe-iterate:radar` — what's new across your stack + competitor set since last visit. Reads weekly cache; offers manual refresh.
- `/vibe-iterate:spy <url>` — one-shot competitive read on a single URL. Quotes positioning verbatim; analyzes overlap with your product.
- `/vibe-iterate:scan-releases [package]` — what's new in this lib (or all libs) since you last bumped. Surfaces breaking changes, new features, security fixes, codemod availability.
- `/vibe-iterate:rate <idea>` — score a feature idea against your shipped product on impact / fit / effort / regression-risk / user-trust-impact. Outputs *ship-now / queue / decline*.
- `/vibe-iterate:ship <brief>` — express lane: skip ingestion, ship from a hand-written brief. Same regression-aware posture as the banner modes.
- `/vibe-iterate:upgrade <package>` — surgical library bump with codemod if available, pre/post-flight tests, one PR.

## How it works

- **Bootstrap on first touch.** First invocation in any repo runs an app-type identification + brief interview, then writes `.vibe-iterate/config.json`. Categories supported: web app, mobile app, desktop app, CLI tool, library/SDK, Claude Code plugin, monorepo, data/research, other. The step is graceful — no preachy enumeration of what's missing; it acknowledges, infers what it can from the codebase, asks for what it can't (competitors), writes config. Idempotent — re-run to refresh stale config.
- **One PR per session, by design.** Every banner mode lands a single regression-aware, small-diff PR plus an Atlas entry naming the candidates considered and the runners-up — so the *why* survives, not just the *what*.
- **Composes with Cartographer, stands alone without it.** When vibe-cartographer is installed, vibe-iterate defers to it (Pattern #13 deferral with a discovery upsell); when it's not, vibe-iterate works standalone.
- **Self-evolves on your machine, no telemetry.** `/vibe-iterate:evolve-iterate` reads the local session + friction logs (under `~/.claude/plugins/data/vibe-iterate/`), surfaces patterns, and writes proposed plugin improvements to `docs/proposed-changes.md` for the maintainer to review. Never auto-applies. Per Este's standing rule, the data stays local — Levels 2 + 3 of the Self-Evolving Plugin Framework.

See [`docs/2026-05-04-vibe-iterate-design.md`](docs/2026-05-04-vibe-iterate-design.md) for the locked design.

## Validated on

Used repeatedly on real repos — and proven cross-agent: ran under Gemini in Antigravity 2.0, adapting on the fly. The plugin is not Claude-Code-locked; the posture and the Atlas discipline travel across agents.

## Install

**Stable (recommended) — as a Claude Code plugin via the marketplace:**

```text
/plugin marketplace add estevanhernandez-stack-ed/vibe-plugins
/plugin install vibe-iterate@vibe-plugins
```

**Canary — track this repo's `main`:**

```text
/plugin install vibe-iterate@estevanhernandez-stack-ed/vibe-iterate
```

## Part of the Vibe ecosystem

One of 11 plugins in the **[Vibe Plugins](https://github.com/estevanhernandez-stack-ed/vibe-plugins)** marketplace from [626 Labs](https://626labs.dev) — foundations (Thesis Engine, Keystone) and process pillars (Cartographer, Doc, Sec, Test, Thesis, Iterate, Taker, Walk, Insights) for AI-assisted creation. Iterate is the post-ship pillar: where Cartographer takes you idea → v1, Iterate takes you v1 → v1+n.

```text
/plugin marketplace add estevanhernandez-stack-ed/vibe-plugins
```

## License

MIT — *Imagine Something Else.*
