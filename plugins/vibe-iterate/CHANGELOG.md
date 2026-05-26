# Changelog

All notable changes to vibe-iterate are recorded here. Format loosely follows Keep a Changelog; versions track the `version` field in `.claude-plugin/plugin.json`.

## [Unreleased]

### Added

- `/vibe-iterate:horizon` — long-range banner mode. Ingests four forward signals (stack/platform roadmaps, ecosystem/model curves, competitor trajectory, own-product trajectory), scores candidate bets via `:forecast`, places them on a Three-Horizon map (H1 defend/extend, H2 emerging S-curves, H3 options), and seeds H1 bets into the Atlas with `source:"horizon"` so `feature-add` picks them up when their time comes. **Never opens a PR.** Run quarterly or at inflection points. See `plugins/vibe-iterate/skills/horizon/SKILL.md`.
- `/vibe-iterate:forecast` — long-range scoring sidecar (/20: conviction, time-to-relevance, optionality, strategic fit). Mirrors `:rate`'s read-only / evidence-required contract for bets where effort + regression-risk are unknowable. Verdict bands: *hedge now* / *watch* / *park*; tier (H1/H2/H3) derives from time-to-relevance. See `plugins/vibe-iterate/skills/forecast/SKILL.md`.
- Bare router (`/vibe-iterate`) recommends Horizon as an alternative (never default) when the Atlas shows ≥5 shipped tactical entries in the last 90 days and no `mode:"horizon"` entry in that window.
- `guide/schemas/atlas-entry.schema.json` extended: `mode` enum gains `"horizon"`; optional `source` field (enum `["horizon"]`) marks horizon-seeded entries. Valid + invalid fixture lines added.
- New living state file: `.vibe-iterate/horizon.md` — long-range strategy map, rewritten each Horizon run (dated revision header). Git history is the audit trail.
- Long-range posture documented in `guide/references/posture.md` (conviction-over-certainty, optionality-over-commitment, falsifiability-over-enthusiasm).
- `/vibe-iterate:horizon` friction-trigger map added — five horizon-specific trigger conditions mapped to existing `friction_type` enum values (no new types invented).

## [1.1.0]

### Changed

- Renamed `/evolve` → `/evolve-iterate` to disambiguate the evolve command across the plugin family. Every sibling plugin's evolve skill is becoming `evolve-<short>` so a bare `/evolve` is no longer ambiguous when multiple vibe-* plugins are installed. The skill directory, the `name:` field, the manifest description, and all internal cross-references now read `evolve-iterate`. Concept prose (self-evolution, the Self-Evolving Plugin Framework, Level 3) is unchanged — only the command name moved.

## [1.0.0]

### Added

- Full release. Plugin shell, schemas, shared guide, bare router, bootstrap (app-type identification + first-run interview), all 4 banner modes (feature-add, competitive, ux-polish, bug-bash), all 6 sidecars (radar, spy, scan-releases, rate, ship, upgrade), Cart-detection (Pattern #13 deferral with discovery upsell), session + friction logging (Levels 2 + 3 of the Self-Evolving Plugin Framework), and the self-reflection command.
