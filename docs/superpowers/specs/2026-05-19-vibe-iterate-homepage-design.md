# vibe-iterate landing page — design

**Date:** 2026-05-19
**Status:** approved, ready for implementation plan
**Owner:** Estevan Hernandez
**Implementation surface:** [626labs-hub](https://github.com/estevanhernandez-stack-ed/626labs-hub) (the `626labs.dev` repo)
**Submission URL:** `https://626labs.dev/vibe-iterate/`

## Why

vibe-iterate is being submitted to Claude's plugin submission process. The submission expects a public landing URL that:

- Communicates what the plugin does in 5 seconds for a reviewer.
- Shows install instructions a developer can actually use.
- Carries 626 Labs brand identity (the plugin sits in a family).
- Stays in sync with how the rest of 626 Labs publishes — same fonts, same tokens, same renderer pipeline conventions.

The README in the solo repo is solid documentation, but it's not a storefront. This spec defines that storefront.

## Decisions locked

| Decision | Choice | Why |
|---|---|---|
| Surface type | GitHub Pages landing site | Public URL the submission form can point to |
| Brand | 626 Labs design system | The plugin sits in a 626 Labs family; consistency matters |
| Page shape | Hybrid — marketing + dev (single-scroll: hero → modes → sidecars → Ptolemy → install → family) | Serves reviewers (utility fast) and adopters (commands + install) in one scroll |
| Hosting | Standalone page on `626labs.dev` via the **626labs-hub** repo | Strongest branding; uses existing hub assets and fonts; submission URL is a real 626 Labs URL |
| Hero centerpiece | Designed terminal block in CSS | Ships today; easy to swap for a real GIF later |
| Composition | A · Modes-forward (utility-first) | Reviewers + adopters want utility fast; metaphor/story buries it |

## Architecture & hosting

- **Path in repo:** `626labs-hub/vibe-iterate/index.html` — a new top-level subfolder for a clean URL. Same idiom as the existing standalone pages (`thesis.html`, `workflow.html`, `rororo.html`), except in a subfolder.
- **Public URL:** `https://626labs.dev/vibe-iterate/`
- **Tech:** hand-written HTML + inline CSS + small vanilla JS file for install-block copy buttons. No build step, no framework. Matches the hub.
- **Tokens:** pull from the hub's existing `Design/colors_and_type.css` so the page stays in lockstep when tokens move.
- **Fonts:** same loader pattern the hub's `index.html` already uses (Google Fonts `@import` or local TTFs from `fonts/`).
- **Icons:** Lucide via CDN.
- **Renderer integration:** none. `scripts/render-hub.py` only touches `index.html`'s `SITE_JSON` zones. The new page stands alone.
- **OG image asset:** `626labs-hub/assets/og-vibe-iterate.png` (1200×630). Custom card: navy field, "vibe-iterate" in Space Grotesk, "Maintain your Atlas." subhead, cyan→magenta swoosh accent, 626 Labs mark in corner. Generated via a small addition to `scripts/export-brand.py` or hand-built.
- **Pipeline touchpoints:** the existing `link-check.yml` workflow picks up the new page on next push automatically.

## Page layout (top to bottom)

### 1. Top nav

- Minimal. 626 Labs mark (left) → links to `/`.
- Right side: single `Install` ghost button anchoring to `#install`.
- Backdrop blur on scroll (`backdrop-filter: blur(12px)`).

### 2. Hero (full viewport)

Two-column on desktop, stacked on mobile.

**Left column:**
- Eyebrow: `626 LABS · CLAUDE CODE PLUGIN` (mono, cyan, +0.12em)
- H1: **Maintain your Atlas.**
- Subhead: *"Cart took you idea → v1. vibe-iterate takes you v1 → v1+n. Ships one PR per session — regression-aware, small-diff-preferred."*
- Primary CTA: `Install plugin` (cyan→magenta gradient, anchors `#install`)
- Secondary CTA: `Read the spec` (ghost, links to design doc on GitHub)
- Meta row: `v1.0.0 · 4 modes · 6 sidecars · MIT`

**Right column:**
- Designed terminal block. Shows a real-looking `/vibe-iterate` bare-router session: agent reads the repo, recommends a mode, user accepts, agent ships one PR. ~420px tall, blinking cursor.

### 3. What it does — modes

- Eyebrow `01 · THE WORK`, H2 *"Four modes for what's next."*
- 2×2 grid of mode cards.
- Each card: mono command eyebrow, sentence-case title, 2-line description, "reach for it when…" line.

**Mode copy:**

- **feature-add** — *Ship the next feature.* Multi-source candidate scan: competitors, Product Hunt, framework releases, your feedback.md. Clusters, scores, picks one. Reach for it when *you don't know what to build next*.
- **competitive** — *Close the gaps that matter.* Reads competitor changelogs, diffs against your shipped product, ranks by strategic relevance — not parity. Reach for it when *a competitor shipped something loud*.
- **ux-polish** — *Tighten what's shipped but rough.* Walks routes, components, key flows. Scores by user-trust impact. Reach for it when *the product works but feels off*.
- **bug-bash** — *Fix the loudest bug.* Reads feedback.md, triages by severity × frequency × blast-radius. Dormant when feedback.md is missing. Reach for it when *users keep reporting the same thing*.

### 4. Sidecars (continuation, no section break)

- H3 *"Six tools when a mode is too much."*
- Compact 2×3 (desktop) / stacked (mobile) pill-grid.
- Each: command in mono, one-line description, small Lucide icon.

**Sidecar copy:**

- **`:radar`** (icon: `radar`) — what's new across your stack and competitors since last visit.
- **`:spy <url>`** (icon: `eye`) — one-shot competitive read on a single URL.
- **`:scan-releases [pkg]`** (icon: `package`) — what's new in this lib since you last bumped.
- **`:rate <idea>`** (icon: `scale`) — score an idea on impact / fit / effort / regression-risk / user-trust.
- **`:ship <brief>`** (icon: `ship`) — express lane. Skip ingestion, ship from a brief.
- **`:upgrade <pkg>`** (icon: `arrow-up`) — surgical library bump with codemods if available.

### 5. How it thinks — Ptolemy block

- Eyebrow `02 · THE BRAIN`, H2 *"Ptolemy stays current."*

**Paragraphs:**

> Ptolemy is vibe-iterate's agent — senior to Cart's field-cartographer, oriented for already-shipped territory. He reads your stack via context7, watches framework releases on a weekly scan, and keeps your Atlas — the running record of what you've shipped, what you considered, what got cut, and why — in continuity across sessions.

> When vibe-cartographer is installed in the same repo, Ptolemy defers cleanly (Pattern #13). When it's not, vibe-iterate stands on its own. Composes, never depends.

- Callout band (cyan hairline top/bottom): *"No telemetry. Atlas data stays on your machine."*

### 6. Install

- Eyebrow `03 · GET IT`, H2 *"Two channels."*
- Two side-by-side cards (stack on mobile):
  - **Stable** — *"Tagged releases, promoted via the Vibe Plugins marketplace."*
    ```
    /plugin marketplace add estevanhernandez-stack-ed/vibe-plugins
    /plugin install vibe-iterate
    ```
  - **Canary** — *"Bleeding edge. Latest `main` from this repo."*
    ```
    /plugin marketplace add estevanhernandez-stack-ed/vibe-iterate
    /plugin install vibe-iterate
    ```
- Each block has a copy-to-clipboard button (Lucide `copy` → `check` for 1.5s on success).
- Sub-note: *"Pick stable if you want to be told. Pick canary if you want to tell us."*

### 7. Family

- Eyebrow `04 · FAMILY`, H2 *"One plugin in a family."*
- Lead: *"Vibe Plugins are a coordinated family — installed independently, composed when present."*
- Cards (in this order, current plugin highlighted):
  - vibe-cartographer — idea → v1
  - **vibe-iterate — v1 → v1+n** *(you are here)*
  - vibe-doc — documentation completeness
  - vibe-test — test coverage and tier enforcement
  - vibe-sec — security posture
  - thesis-engine + vibe-thesis — research authoring
- Each card links to its hub product card section or GitHub repo.

### 8. Footer

- Left: `626 Labs LLC · MIT · 2026`
- Center: *"Imagine Something Else."*
- Right: GitHub link, marketplace link.

## Visual / brand application

### Background

- Baseline: `--brand-navy` `#0f1f31` everywhere.
- Hero only: faint circuit-trace pattern at ~6% opacity over the navy + radial duotone glow (`--brand-gradient-glow`) behind H1 and terminal block.
- No fade-ins anywhere.

### Type scale

| Role | Spec |
|---|---|
| H1 | `clamp(40px, 5vw, 64px)` · Space Grotesk · -0.025em · white |
| H2 | `clamp(28px, 3vw, 40px)` · Space Grotesk · -0.02em · white |
| H3 | `clamp(22px, 2vw, 28px)` · Space Grotesk · white |
| Eyebrow | 12px JetBrains Mono · UPPERCASE · +0.12em · `--brand-cyan` |
| Body | 16–18px Inter · `--ink-200` |
| Inline mono | JetBrains Mono · `--brand-cyan` for commands, `--brand-magenta` for flags |

### Terminal block

- Outer card: `--bg-2`, radius `--r-lg` 14px, inner stroke `inset 0 0 0 1px rgba(255,255,255,.06)`.
- Title bar: 3 dots (muted red/yellow/green) + label `vibe-iterate ~` in mono.
- Body: 20px padding, mono 13–14px.
- Prompts: `$` glyph in cyan, command in white.
- Agent output: ink-200 with inline `<span>` syntax — file paths cyan, decisions magenta, success markers `--success`.
- Cursor: solid 8×16 cyan block, 220ms steady blink.
- ~420px fixed height; content sized to fit (no scroll for v1).

### Cards (modes / sidecars / install / family)

- Default: `--bg-2`, 1px hairline `rgba(255,255,255,.08)`, radius 14px.
- Hover: border → `rgba(23,212,250,.45)` cyan accent. No lift, no scale.
- Featured / current: cyan border + faint cyan glow (used for the *you are here* card in Family).
- Padding: 24px desktop, 20px mobile.

### Buttons

- **Primary CTA:** filled `linear-gradient(135deg, --brand-cyan, --brand-magenta)`, white text, sentence case. Hover: glow intensifies. Press: dim 6%.
- **Secondary / ghost:** transparent bg, 1px hairline border, white text. Hover: bg → `rgba(255,255,255,.06)`, border strengthens.
- Both: 10px radius, 12px vertical / 20px horizontal padding.

### Code / install blocks

- Background `--bg-3`, 1px cyan-tinted border, 10px radius, mono 14px, 16px padding.
- Copy button top-right: ghost icon (Lucide `copy`) → `check` 1.5s on success.
- Multi-line blocks render as two stacked rows.

### Grid + max width

- Max content width 1240px (marketing spec).
- 12-column grid, 24px gutters.
- Section vertical rhythm: 96px between major sections desktop, 64px mobile.

### Animation budget

- Cursor blink on terminal block (220ms cycle).
- 120ms hover transitions on cards/buttons.
- 220ms transition on nav backdrop blur.
- Nothing else. No scroll-triggered animations.

## Voice constraints

- Builder-to-builder, second person. "We" for 626 Labs.
- Sentence case everywhere (H1, H2, buttons). Eyebrows are the exception (UPPERCASE mono).
- Periods at end of microcopy. Em-dashes welcome. No ellipses for drama. No emoji.
- Banned: empower, leverage, seamlessly, unlock, unleash, robust, best-in-class.

## Product card on the hub

Add to `626labs-hub/content/site.json` `products` array, slotted after `vibe-cartographer`:

```json
{
  "id": "vibe-iterate",
  "title": "Vibe Iterate",
  "tagline": "Maintain your Atlas.",
  "description": "Post-ship product iteration. Pick a banner mode — feature-add, competitive, ux-polish, bug-bash — or reach for a sidecar (:radar, :spy, :scan-releases, :rate, :ship, :upgrade). Ships one PR per session, regression-aware.",
  "tags": [
    { "label": "Plugin", "tone": "cyan" },
    { "label": "post-ship", "tone": "magenta" },
    { "label": "Live", "tone": "live" }
  ],
  "status": "live",
  "repo": "estevanhernandez-stack-ed/vibe-iterate",
  "npm": null,
  "install": "/plugin marketplace add estevanhernandez-stack-ed/vibe-plugins",
  "claudeCode": true,
  "anthropicApproved": false,
  "meta": "<code>/vibe-iterate</code> · post-ship iteration",
  "page": "/vibe-iterate/",
  "screenshots": []
}
```

**Renderer hookup (`scripts/render-hub.py`):**

The `page` field may or may not already be honored by the renderer. To verify and patch during implementation:

- If supported → product card on the main hub gets a "View page" link to `/vibe-iterate/` automatically.
- If not supported → small patch to `render-hub.py` to render the `page` field as an additional anchor on each product card. Backward-compatible — entries without `page` render as before.

**Hero chip update:** extend the `hero.chips` array in `site.json` with `{ "label": "vibe-iterate", "tone": "cyan" }`. Don't displace existing names.

**Family section consistency:** the new page's "Family" section is hand-maintained against the hub's `products` array order. Acceptable for 6 entries; candidate for a shared partial later if the list grows.

## Submission artifact

**Submission URL:** `https://626labs.dev/vibe-iterate/`

**Meta tags (head):**

```html
<title>vibe-iterate · Maintain your Atlas. · 626 Labs</title>
<meta name="description" content="Claude Code plugin for post-ship product iteration. Four modes, six sidecars, one PR per session. By 626 Labs.">
<link rel="canonical" href="https://626labs.dev/vibe-iterate/">
<meta property="og:title" content="vibe-iterate · Maintain your Atlas.">
<meta property="og:description" content="Claude Code plugin for post-ship product iteration. Four modes, six sidecars, one PR per session.">
<meta property="og:url" content="https://626labs.dev/vibe-iterate/">
<meta property="og:image" content="https://626labs.dev/assets/og-vibe-iterate.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="626 Labs">
<meta name="twitter:card" content="summary_large_image">
```

**Favicon:** inherit from the hub (`favicon-626.png`); no per-page favicon.

**Reviewer-facing sanity checklist** (what a submission reviewer sees on URL open):

- Above the fold: what the plugin is, what it does, how to install.
- Demo terminal showing a real-looking session.
- Install copy-block they can actually use.
- "By 626 Labs" signal (nav mark + footer).
- No broken links, no console errors.

## Verification

### Before pushing

- Open `626labs-hub/vibe-iterate/index.html` directly in a browser. Resize 320px → 1920px. Check hero stacks cleanly, mode grid collapses to a column, install cards stack, terminal block remains readable on mobile.
- DevTools console: zero errors, zero warnings (404s count).
- Lighthouse pass — aim for ≥95 accessibility, ≥90 performance. Sanity sniff, not a hard gate.
- Click every internal link manually. Click every external link manually.
- Test copy-to-clipboard on both install blocks; confirm icon swaps to `check` and back.
- Visual diff against `626labs-hub/Design/preview/*.html` cards — colors, type, spacing match.

### On push (automatic)

- `link-check.yml` (Lychee) catches broken links — runs on push to `**/*.html`.
- GitHub Pages redeploys from `main`.

### After deploy

- Visit `https://626labs.dev/vibe-iterate/` — confirm it serves.
- Visit `https://626labs.dev/` — confirm the new product card renders in the products grid.
- Check OG render: paste URL into Slack or use `opengraph.xyz`.
- Smoke test on iOS Safari + Android Chrome. Confirm hero legible, install copy-block works.

### Out of scope for v1

- Cross-browser regression suite (no Playwright).
- Performance benchmarks beyond Lighthouse spot-check.
- A/B variants.

### Definition of done

- Page loads at the URL.
- Product card visible on the hub.
- Hero, modes, sidecars, Ptolemy block, install, family, footer all present and styled per spec.
- Copy-to-clipboard works on both install blocks.
- Mobile + desktop both readable.
- No console errors. All internal + external links resolve.

## Open questions for implementation

1. **`render-hub.py` `page` field support** — verify whether the existing renderer honors a `page` field on product entries, or whether a small patch is needed.
2. **Local Design/ tokens** — confirm the hub repo's `Design/colors_and_type.css` is the right import path (vs. the global skill copy). If the hub doesn't have a local CSS token file, copy from the skill and store at `626labs-hub/vibe-iterate/styles.css`.

## Implementation surfaces

Files to add or modify:

- `626labs-hub/vibe-iterate/index.html` — new
- `626labs-hub/vibe-iterate/styles.css` — new (or inlined in `index.html`)
- `626labs-hub/vibe-iterate/copy.js` — new (small vanilla JS for install-block copy)
- `626labs-hub/content/site.json` — add product entry + hero chip
- `626labs-hub/scripts/render-hub.py` — patch if `page` field not already supported
- `626labs-hub/assets/og-vibe-iterate.png` — new (custom card)
- `626labs-hub/scripts/export-brand.py` — extend to render the custom OG card (optional; can be hand-built once instead)

## Related

- vibe-iterate solo repo: https://github.com/estevanhernandez-stack-ed/vibe-iterate
- vibe-iterate design spec: [`docs/2026-05-04-vibe-iterate-design.md`](../../2026-05-04-vibe-iterate-design.md)
- 626 Labs hub repo: `C:\Users\estev\Projects\626labs-hub`
- 626 Labs design skill: `~/.claude-personal/plugins/cache/626labs/626labs/0.1.0/skills/design/`
