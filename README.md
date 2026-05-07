# vibe-iterate

> **vibe-iterate maintains your Atlas.**

Post-ship product iteration. Where vibe-cartographer takes you idea → v1, vibe-iterate takes you v1 → v1+n — indefinitely. Pick a banner mode (feature-add, competitive, ux-polish, bug-bash) or reach for a sidecar tool (`:radar`, `:spy`, `:scan-releases`, `:rate`, `:ship`, `:upgrade`). Ships one PR per session — regression-aware, small-diff-preferred. The agent (Ptolemy) stays current on big-shoulder software via context7 and a weekly framework-release scan. Composes with vibe-cartographer when installed (Pattern #13 deferral); works standalone when it's not.

## Status

**v1.0.0 — full release.** Plugin shell, schemas, shared guide, bare router, bootstrap (app-type identification + first-run interview), all 4 banner modes (feature-add, competitive, ux-polish, bug-bash), all 6 sidecars (radar, spy, scan-releases, rate, ship, upgrade), Cart-detection wired (Pattern #13 deferral with discovery upsell), session + friction logging (Levels 2 + 3 of the Self-Evolving Plugin Framework), and `:evolve` for self-reflection. See [`docs/2026-05-04-vibe-iterate-design.md`](docs/2026-05-04-vibe-iterate-design.md) for the locked design.

**Bootstrap** — first-time invocation in any repo runs an app-type identification + brief interview, then writes `.vibe-iterate/config.json`. Categories supported: web app, mobile app, desktop app, CLI tool, library/SDK, Claude Code plugin, monorepo, data/research, other. The bootstrap step is graceful — no preachy enumeration of what's missing; just acknowledges, infers what it can from the codebase, asks for what it can't (competitors), writes config.

## Banner modes

- `/vibe-iterate` — bare router; recommends a mode for the moment, asks before launching. On first run, hands off gracefully to `/vibe-iterate:bootstrap`.
- `/vibe-iterate:bootstrap` — app-type identification + brief interview, writes `.vibe-iterate/config.json`. Idempotent (re-runnable to refresh stale config).
- `/vibe-iterate:feature-add` — what should we build next? Multi-source candidate-driven (competitors + Product Hunt + framework releases + feedback.md).
- `/vibe-iterate:competitive` — what do they have that we don't? Strategic-relevance scoring (match / differentiate / decline), not parity.
- `/vibe-iterate:ux-polish` — what's shipped but rough? Walks routes/components/flows, scores by user-trust impact.
- `/vibe-iterate:bug-bash` — what's broken according to users? Reads `feedback.md`; triages by severity × frequency × blast-radius. Dormant when `feedback.md` is missing (one-line nudge only).

## Sidecar tools

- `/vibe-iterate:radar` — what's new across your stack + competitor set since last visit. Reads weekly cache; offers manual refresh.
- `/vibe-iterate:spy <url>` — one-shot competitive read on a single URL. Quotes positioning verbatim; analyzes overlap with your product.
- `/vibe-iterate:scan-releases [package]` — what's new in this lib (or all libs) since you last bumped. Surfaces breaking changes, new features, security fixes, codemod availability.
- `/vibe-iterate:rate <idea>` — score a feature idea against your shipped product on impact / fit / effort / regression-risk / user-trust-impact. Outputs *ship-now / queue / decline*.
- `/vibe-iterate:ship <brief>` — express lane: skip ingestion, ship from a hand-written brief. Same regression-aware posture as the banner modes.
- `/vibe-iterate:upgrade <package>` — surgical library bump with codemod if available, pre/post-flight tests, one PR.

## Self-evolution

- `/vibe-iterate:evolve` — reads the local session + friction logs (under `~/.claude/plugins/data/vibe-iterate/`), surfaces patterns, writes proposed plugin improvements to `docs/proposed-changes.md` for the maintainer to review. Never auto-applies. Per Este's standing rule: **no telemetry** — the data stays on your machine.

## Install

**Stable channel** — via the [Vibe Plugins marketplace](https://github.com/estevanhernandez-stack-ed/vibe-plugins):

```
/plugin marketplace add estevanhernandez-stack-ed/vibe-plugins
/plugin install vibe-iterate
```

**Canary channel** — bleeding edge, latest `main`:

```
/plugin marketplace add estevanhernandez-stack-ed/vibe-iterate
/plugin install vibe-iterate
```

## Family

vibe-iterate is one plugin in the [Vibe Plugins family](https://github.com/estevanhernandez-stack-ed/vibe-plugins):

- **vibe-cartographer** — greenfield: idea → v1
- **vibe-iterate** — post-ship: v1 → v1+n *(this plugin)*
- **vibe-doc** — documentation completeness
- **vibe-test** — test coverage and tier enforcement
- **vibe-sec** — security posture
- **thesis-engine + vibe-thesis** — research authoring

## License

MIT
