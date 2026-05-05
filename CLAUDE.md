# vibe-iterate (solo repo)

> **Persona:** Inherits The Architect from `~/.claude/CLAUDE.md`. Project context below.

## What this repo is

The solo repo for the **vibe-iterate** Claude Code plugin. Pinned tags here get promoted to stable via the [vibe-plugins marketplace](https://github.com/estevanhernandez-stack-ed/vibe-plugins).

vibe-iterate is the post-ship product iteration plugin in the Vibe Plugins family — sibling to **vibe-cartographer**. Cart takes you idea → v1; vibe-iterate takes you v1 → v1+n indefinitely.

**Tagline:** *vibe-iterate maintains your Atlas.*

**Agent persona:** Ptolemy. Senior to Cart's field-cartographer; multi-source synthesis over already-shipped territory. Posture: shipped-product-conservative (regression-aware, user-trust-aware, small-diff-preferred).

## Source of truth

**The design spec is the authoritative document for what this plugin is and does:** [`docs/2026-05-04-vibe-iterate-design.md`](docs/2026-05-04-vibe-iterate-design.md). Read it before changing anything load-bearing.

## Repo shape

| Path | What it is |
|---|---|
| `plugins/vibe-iterate/.claude-plugin/plugin.json` | Plugin manifest. Load-bearing for Claude Code recognition. |
| `plugins/vibe-iterate/skills/<name>/SKILL.md` | Each skill = one slash-command worth of behavior. Bare router at `skills/vibe-iterate/`; banner modes + sidecars under named folders. |
| `.claude-plugin/marketplace.json` | Canary marketplace manifest — points at `./plugins/vibe-iterate`. Used by users on the bleeding edge channel. |
| `docs/2026-05-04-vibe-iterate-design.md` | Locked design spec from the brainstorming session. |
| `README.md` | Public storefront for the solo repo. |

## Conventions (matching the family)

- **Path within repo:** `plugins/vibe-iterate/` (matches Cart, Thesis Engine, Vibe Thesis pattern)
- **Tag style:** `vX.Y.Z` (matches Cart, Doc, Thesis Engine, Vibe Thesis lineage; not the `<plugin>-vX.Y.Z` form Test/Sec inherited)
- **Plugin namespace:** commands surface as `/vibe-iterate:<name>` plus the bare `/vibe-iterate` router
- **License:** MIT

## How this plugin promotes

1. Work lands here on `main`.
2. Tag a release: `vX.Y.Z`.
3. In the [vibe-plugins marketplace repo](https://github.com/estevanhernandez-stack-ed/vibe-plugins), bump the `vibe-iterate` ref in `.claude-plugin/marketplace.json` to the new tag.
4. Stable users pick it up on next `/plugin marketplace sync`.

Until v1.0, users on `main` get bleeding edge via the canary channel; tagged versions are stable.

## Decisions log

Significant decisions log to the **626Labs Dashboard** via MCP (`mcp__626Labs__manage_decisions log`). Tag with the bound project ID. Bar: *would future-you (or someone asking "why this approach?") want to know this in 3–6 months?*

Especially:
- **Architecture changes** to Ptolemy's brain (knowledge sources, build engine posture, composition with Cart)
- **Mode/sidecar additions or removals** beyond what's in the design spec
- **Telemetry decisions** — per Este's standing rule, NO telemetry. Document explicitly if anything ever even gets close to phone-home territory.
- **Atlas data shape changes** — downstream tooling will read this

## What NOT to do

- **No telemetry.** Per Este's standing rule, vibe-iterate emits no usage pings, no opt-in metrics, no phone-home. Atlas data stays local to the project.
- **Don't auto-fire modes.** No mode runs without explicit user invocation. The agent only proposes; the user kicks off.
- **Don't hard-depend on Cart.** vibe-iterate must work without vibe-cartographer installed. Cart-detection is opt-in enhancement, never a requirement.
- **Don't silently expand scope.** The design spec is the contract. Changes to scope (new modes, new sidecars, removed ones) need explicit decisions logged.
- **Don't normalize tag naming.** `vX.Y.Z` here. Test and Sec use `<plugin>-vX.Y.Z` for extraction-history reasons; don't "fix" their convention from this repo.

## References

- Design spec: [`docs/2026-05-04-vibe-iterate-design.md`](docs/2026-05-04-vibe-iterate-design.md)
- Vibe Plugins marketplace: https://github.com/estevanhernandez-stack-ed/vibe-plugins
- Sibling: vibe-cartographer (https://github.com/estevanhernandez-stack-ed/vibe-cartographer)
- Self-Evolving Plugin Framework: see vibe-cartographer's `docs/self-evolving-plugins-framework.md`
