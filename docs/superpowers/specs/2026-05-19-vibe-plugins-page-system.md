# Vibe Plugins page system — design

**Date:** 2026-05-19
**Status:** proposed, awaiting approval
**Implementation surface:** `626labs-hub` repo
**Depends on:** PR #8 (merged — vibe-iterate page) + PR #9 (open — logo/generator)

## Why

We hand-built one plugin landing page (vibe-iterate, live at `626labs.dev/vibe-iterate/`). It worked. Now: roll the **same page type** out to every Vibe plugin, add a family index page, and document the process so it's repeatable — not a 7× copy-paste.

## Decisions locked (from scoping)

| Decision | Choice |
|---|---|
| Build approach | **Data-driven generator** — one template + per-plugin data + a render script. Matches the hub's `render-hub.py` pipeline. |
| Content source | **Each plugin's own repo** (all 7 are local under `C:\Users\estev\Projects\`). Read README / design spec / SKILL files for accurate per-command content. No fabrication. |
| Index page | **Dedicated `/plugins/` family page** — family hero, family glyph, grid of all plugins each linking to its page. |
| Icons | Extend `export-plugin-icons.py` to emit a **transparent glyph icon** per plugin (for navs/favicons), replacing the inline-SVG hack. |

## Plugins in scope

vibe-cartographer, vibe-iterate (done — becomes the template reference), vibe-doc, vibe-test, vibe-sec, vibe-keystone, vibe-thesis, thesis-engine. (8 total pages; vibe-iterate already exists and will be regenerated from the template to prove parity.)

## Architecture

### 1. Page generator — `scripts/render-plugin-pages.py`

- Reads `content/plugin-pages.json` (new) + the shared template (HTML built in Python, same idiom as `render-hub.py`).
- Emits `<plugin-id>/index.html` for each plugin.
- `--check` flag for idempotent drift detection (CI-friendly), matching `render-hub.py`.
- Shared chrome (nav, family section, footer, `<style>` tokens) lives in the template — change once, regenerate all.

### 2. Data model — `content/plugin-pages.json`

Keyed by plugin id. Each entry:

```jsonc
{
  "id": "vibe-cartographer",
  "name": "vibe-cartographer",          // wordmark (lowercase, no space in "626Labs")
  "tagline": "Vibe coding with a map.",
  "eyebrow": "626Labs · Claude Code plugin",
  "subhead": "...",
  "meta": { "title": "...", "description": "..." },
  "terminal": [ "<line>", ... ],         // optional designed terminal demo
  "ctas": { "primary": {...}, "secondary": {...} },
  "heroMeta": ["v1.0.0", "11 commands", "MIT"],
  "sections": [                           // flexible — modes, commands, tiers, phases, etc.
    {
      "eyebrow": "01 · The work",
      "heading": "...",
      "lead": "...",
      "cards": [ { "command": "...", "title": "...", "desc": "...", "reach": "..." } ]
    }
  ],
  "install": {
    "stable": "/plugin marketplace add ...\n/plugin install ...",
    "canary": "..."                       // optional
  },
  "about": { "eyebrow": "02 · The brain", "heading": "...", "paragraphs": ["..."], "callout": "..." },
  "ogImage": "/assets/brand/plugins/vibe-cartographer-banner-1280x640.png"
}
```

The `sections` array is generic (cards = command/title/desc/optional-reach) so it adapts to each plugin's shape: iterate's modes+sidecars, cartographer's 11 sequential commands, doc's gap types, test's tiers, sec's checks, thesis's phases.

### 3. Shared family section

The "One plugin in a family" grid is identical across all pages (current plugin highlighted via `here` class). Generated from the plugin list so it never drifts — solves the "hand-maintained in two places" debt flagged in the vibe-iterate spec.

### 4. Family index — `plugins/index.html`

Standalone page at `626labs.dev/plugins/`:
- Family hero using `vibe-plugins-square-1024.png` / family wordmark + "for Claude Code · 626Labs".
- Grid of all plugin cards (glyph icon + name + tagline + "Open page"), each linking to `/<plugin>/`.
- Same chrome/tokens as the plugin pages.
- Its own OG card (use `vibe-plugins-banner-1280x640.png`).

### 5. Transparent icons — extend `export-plugin-icons.py`

Add `build_icon(plugin)` → `assets/brand/plugins/<id>-icon-transparent-512.png`: the glyph centered on a transparent canvas (optionally in the cyan rounded tile). Used as the nav mark on each page (replaces the inline-SVG hack) and as per-plugin favicons if desired.

### 6. Hub product cards → per-plugin pages

Set `productPage: "/<id>/"` on every plugin entry in `site.json` (vibe-iterate already has it) so the main hub cards link to the new pages. Re-render `index.html`.

### 7. Documentation — `docs/vibe-plugins-pages.md`

The "document this process" deliverable. Covers: the data model, how to add a new plugin page (edit `plugin-pages.json` → run generator), how glyphs/icons are generated, the `/plugins/` index, and the deploy flow. Lives with the code it documents.

## Content sourcing (the bulk of the work)

For each of the 7 plugins, read its local repo and extract: tagline, what-it-does summary, the command/feature list with accurate descriptions, install commands (marketplace + npm if present), persona/differentiator. This is parallelizable — one independent research pass per plugin → structured `plugin-pages.json` entry. **Accuracy gate:** content comes from the repo, not invented.

## Build sequence

1. Generalize the vibe-iterate page into the template + extract its data into `plugin-pages.json`. Generator must regenerate vibe-iterate's page **byte-identical** (parity proof).
2. Add transparent-icon generation; switch vibe-iterate nav to the real icon.
3. Source content for the other 7 plugins (parallel research) → `plugin-pages.json`.
4. Generate all plugin pages.
5. Build `/plugins/` family index.
6. Wire hub product cards (`productPage`) + re-render.
7. Write `docs/vibe-plugins-pages.md`.
8. Verify (Playwright: each page renders, links resolve, mobile) + ship.

## Verification

- Generator `--check` is clean (no drift) after a fresh run.
- Each plugin page: renders desktop + mobile, no console errors, install copy works, family grid + nav correct, OG meta present.
- `/plugins/` index links resolve to all 8 pages.
- vibe-iterate page unchanged vs. its current live version (parity).

## Out of scope (v1)

- Real GIF/asciinema demos (designed terminal blocks only).
- Per-plugin custom OG cards beyond the generated banners.
- Localization, analytics, A/B.
- Pages for non-plugin products (sanduhr, rororo, etc.) — plugins only.

## Open questions

1. **Terminal demos per plugin** — vibe-iterate has a designed terminal block. Worth one per plugin (more sourcing) or only for the flagship + iterate? Proposed: optional per plugin; include where it adds clarity, skip where it's filler.
2. **Page parity vs. per-plugin variation** — some plugins (thesis-engine, vibe-thesis) are research-flavored, not "ship a PR" tools. The section model flexes, but the hero framing may need per-plugin tuning. Proposed: same chrome, plugin-appropriate copy.
