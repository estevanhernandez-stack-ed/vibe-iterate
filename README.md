# vibe-iterate

> **vibe-iterate maintains your Atlas.**

Post-ship product iteration. Where vibe-cartographer takes you idea → v1, vibe-iterate takes you v1 → v1+n — indefinitely. Pick a banner mode (feature-add, competitive, ux-polish, bug-bash) or reach for a sidecar tool (`:radar`, `:spy`, `:scan-releases`, `:rate`, `:ship`, `:upgrade`). Ships one PR per session — regression-aware, small-diff-preferred. The agent (Ptolemy) stays current on big-shoulder software via context7 and a weekly framework-release scan. Composes with vibe-cartographer when installed (Pattern #13 deferral); works standalone when it's not.

## Status

**v0.5.0 — Foundation.** Plugin shell loads, schemas validate, bare `/vibe-iterate` router works (reads project state, recommends a mode, asks before launching). No banner modes or sidecar tools yet — they land in Plan 2 onward. See [`docs/2026-05-04-vibe-iterate-design.md`](docs/2026-05-04-vibe-iterate-design.md) for the locked design and [`docs/superpowers/plans/`](docs/superpowers/plans/) for implementation plans.

## Banner modes (v1.0)

- `/vibe-iterate` — bare router; recommends a mode for the moment, asks before launching
- `/vibe-iterate:feature-add` — what should we build next?
- `/vibe-iterate:competitive` — what do they have that we don't?
- `/vibe-iterate:ux-polish` — what's shipped but rough?
- `/vibe-iterate:bug-bash` — what's broken according to users? (`feedback.md` only in v1.0)

## Sidecar tools (v1.0)

- `/vibe-iterate:radar` — what's new across your stack + competitor set since last visit
- `/vibe-iterate:spy <url>` — one-shot competitive read on a single URL
- `/vibe-iterate:scan-releases [package]` — what's new in this lib since you last bumped (or all libs)
- `/vibe-iterate:rate <idea>` — score a feature idea against your shipped product
- `/vibe-iterate:ship <brief>` — skip ingestion, ship from a hand-written brief
- `/vibe-iterate:upgrade <package>` — bump one library + codemods if available

## Install (once v1.0 ships)

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
