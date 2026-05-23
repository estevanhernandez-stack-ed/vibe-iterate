# Changelog

All notable changes to vibe-iterate are recorded here. Format loosely follows Keep a Changelog; versions track the `version` field in `.claude-plugin/plugin.json`.

## [1.1.0]

### Changed

- Renamed `/evolve` → `/evolve-iterate` to disambiguate the evolve command across the plugin family. Every sibling plugin's evolve skill is becoming `evolve-<short>` so a bare `/evolve` is no longer ambiguous when multiple vibe-* plugins are installed. The skill directory, the `name:` field, the manifest description, and all internal cross-references now read `evolve-iterate`. Concept prose (self-evolution, the Self-Evolving Plugin Framework, Level 3) is unchanged — only the command name moved.

## [1.0.0]

### Added

- Full release. Plugin shell, schemas, shared guide, bare router, bootstrap (app-type identification + first-run interview), all 4 banner modes (feature-add, competitive, ux-polish, bug-bash), all 6 sidecars (radar, spy, scan-releases, rate, ship, upgrade), Cart-detection (Pattern #13 deferral with discovery upsell), session + friction logging (Levels 2 + 3 of the Self-Evolving Plugin Framework), and the self-reflection command.
