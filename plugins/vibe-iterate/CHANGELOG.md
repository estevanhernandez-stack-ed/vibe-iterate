# Changelog

All notable changes to vibe-iterate are recorded here. Format loosely follows Keep a Changelog; versions track the `version` field in `.claude-plugin/plugin.json`.

## [1.3.0] — 2026-06-09 · .NET/NuGet lane (GAP-13 Tier 2)

From the quality-net gap analysis (vibe-plugins `docs/quality-net-gap-analysis-2026-06-09.md`): dependency upgrades are the riskiest operation on a store-shipped app, and the estate's MS Store app had zero support — bootstrap couldn't classify it, `:scan-releases` and `:upgrade` couldn't see its pins.

### Added

- **Bootstrap classifies .NET** — `.sln`/`*.csproj` detection (root + two levels down; real repos nest the .NET tree), `OutputType` + `UseWPF`/`UseWinUI` → desktop-app / cli-tool / library-sdk, framework anchor from `<TargetFramework>` (e.g. `.NET 10 WPF`).
- **Pin extraction from csproj** — `<PackageReference>` entries deduped across the solution, `PrivateAssets="all"` analyzers skipped (the `@types/*` equivalent), `<TargetFramework>` captured as a pseudo-pin (runtime bumps are the riskiest .NET upgrade class).
- **`:scan-releases` NuGet dispatch** — version resolution via the nuget.org flat-container API (no auth), release notes via the package's GitHub repo; `packages.lock.json` preferred for resolved versions when present.
- **`:upgrade` NuGet mechanics** — deduped `Version`-attribute bump across the solution's projects, `dotnet restore` + `dotnet build` as the install-equivalent, `dotnet list package --outdated` verification; codemods honestly declared N/A for the NuGet world.
- **Config schema:** `framework_pins[]` items gain optional `ecosystem` (`npm | nuget | pypi | cargo | go`).

### Migration note (state contract — promotion-checklist rule 6)

`ecosystem` is additive, and bootstrap **only writes it for non-npm pins** — JS-project configs stay byte-identical, so a config written by 1.3.0 for a JS app still validates against pre-1.3.0's `additionalProperties: false` schema. A `.NET` config will NOT validate on pre-1.3.0 plugins (they couldn't iterate on .NET anyway). No re-bootstrap needed for existing projects.

Dogfooded read-only on Sanduhr (the MS Store app, `windows-dotnet/src/*`): classifies desktop-app / `.NET 10 WPF`, extracts 5 pins + the `net10.0-windows` pseudo-pin, correctly skips `Microsoft.Windows.CsWin32` (PrivateAssets=all); live NuGet API check confirms `CommunityToolkit.Mvvm 8.4.2` is current — a true negative, the pins are fresh.

## [1.2.0] — 2026-05-28

### Added

- `/vibe-iterate:horizon` — long-range banner mode. Ingests four forward signals (stack/platform roadmaps, ecosystem/model curves, competitor trajectory, own-product trajectory), scores candidate bets via `:forecast`, places them on a Three-Horizon map (H1 defend/extend, H2 emerging S-curves, H3 options), and seeds H1 bets into the Atlas with `source:"horizon"` so `feature-add` picks them up when their time comes. **Never opens a PR.** Run quarterly or at inflection points. See `plugins/vibe-iterate/skills/horizon/SKILL.md`.
- `/vibe-iterate:forecast` — long-range scoring sidecar (/20: conviction, time-to-relevance, optionality, strategic fit). Mirrors `:rate`'s read-only / evidence-required contract for bets where effort + regression-risk are unknowable. Verdict bands: *hedge now* / *watch* / *park*; tier (H1/H2/H3) derives from time-to-relevance. See `plugins/vibe-iterate/skills/forecast/SKILL.md`.
- Bare router (`/vibe-iterate`) recommends Horizon as an alternative (never default) when the Atlas shows ≥5 shipped tactical entries in the last 90 days and no `mode:"horizon"` entry in that window.
- `guide/schemas/atlas-entry.schema.json` extended: `mode` enum gains `"horizon"`; optional `source` field (enum `["horizon"]`) marks horizon-seeded entries. Valid + invalid fixture lines added.
- New living state file: `.vibe-iterate/horizon.md` — long-range strategy map, rewritten each Horizon run (dated revision header). Git history is the audit trail.
- Long-range posture documented in `guide/references/posture.md` (conviction-over-certainty, optionality-over-commitment, falsifiability-over-enthusiasm).
- `/vibe-iterate:horizon` friction-trigger map added — five horizon-specific trigger conditions mapped to existing `friction_type` enum values (no new types invented).

### Fixed

- **Session + friction log writers — Windows write-path guidance.** Added a cross-platform "Append implementation" section to both `session-logger/SKILL.md` and `friction-logger/SKILL.md`. The `:evolve-iterate` run on 2026-05-28 surfaced ~18% corruption rate on entries written via double-quoted PowerShell append commands (interior `"` get escaped to `\"`, producing malformed JSON that the strict parser silent-drops, and `detect_orphans()` then false-positives against). Recommended path is `ConvertTo-Json -Compress | Add-Content` (or single-quoted literal); double-quoted append is now explicitly called out as the failure mode to avoid. See `docs/proposed-changes.md` for the evolve-iterate run report.

## [1.1.0]

### Changed

- Renamed `/evolve` → `/evolve-iterate` to disambiguate the evolve command across the plugin family. Every sibling plugin's evolve skill is becoming `evolve-<short>` so a bare `/evolve` is no longer ambiguous when multiple vibe-* plugins are installed. The skill directory, the `name:` field, the manifest description, and all internal cross-references now read `evolve-iterate`. Concept prose (self-evolution, the Self-Evolving Plugin Framework, Level 3) is unchanged — only the command name moved.

## [1.0.0]

### Added

- Full release. Plugin shell, schemas, shared guide, bare router, bootstrap (app-type identification + first-run interview), all 4 banner modes (feature-add, competitive, ux-polish, bug-bash), all 6 sidecars (radar, spy, scan-releases, rate, ship, upgrade), Cart-detection (Pattern #13 deferral with discovery upsell), session + friction logging (Levels 2 + 3 of the Self-Evolving Plugin Framework), and the self-reflection command.
