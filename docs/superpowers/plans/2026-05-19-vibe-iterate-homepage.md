# vibe-iterate Landing Page — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a public landing page for the vibe-iterate Claude Code plugin at `https://626labs.dev/vibe-iterate/` so it can be linked from a Claude submission.

**Architecture:** Hand-written HTML page with inline `<style>` and inline `<script>` (matches the hub's existing idiom — no build step, no framework). Lives in a new `vibe-iterate/` subfolder of the `626labs-hub` repo. Adds a product card to the main hub at `626labs.dev` that links to the new page. Brand applied via the hub's own `Design/colors_and_type.css` tokens plus inline CSS variables (same pattern as `index.html`).

**Tech Stack:** HTML5, vanilla CSS (Space Grotesk + Inter + JetBrains Mono via Google Fonts `@import`), vanilla JS (copy-to-clipboard), Python (the hub's `scripts/render-hub.py` renderer), Pillow + the hub's `scripts/export-brand.py` style for the OG card. No npm, no bundler.

**Repository under work:** `C:\Users\estev\Projects\626labs-hub` (NOT the vibe-iterate solo repo — only the plan and spec live there).

---

## File Structure

| Path | Role | New / Modified |
|---|---|---|
| `626labs-hub/vibe-iterate/index.html` | The landing page. All HTML + inline `<style>` + inline `<script>`. | New |
| `626labs-hub/content/site.json` | Add `vibe-iterate` product entry; add `vibe-iterate` hero chip. | Modified |
| `626labs-hub/scripts/render-hub.py` | Add `vibe-iterate` to `PRODUCT_SIGILS` dict (line 189). | Modified |
| `626labs-hub/index.html` | Re-rendered by `render-hub.py` from `site.json`. **Do not hand-edit.** | Modified (by renderer) |
| `626labs-hub/assets/og-vibe-iterate.png` | Custom 1200×630 OG card. Hand-built or via small `export-brand.py` extension. | New |

The page is single-file on purpose. The hub's `index.html` is also single-file with inline styles; matching that convention keeps the surface predictable.

---

## Reference material the engineer should read first

- `626labs-hub/CLAUDE.md` — repo guide. Key points: hand-written HTML, no build step on the marketing surface; brand tokens in `Design/colors_and_type.css`; voice is builder-to-builder, second person, no emoji.
- `626labs-hub/index.html` lines 1–250 — example of the hub's HTML + inline style idiom. Use as a structural template.
- `626labs-hub/Design/colors_and_type.css` — the canonical token source. Copy the variables we need.
- `~/.claude-personal/plugins/cache/626labs/626labs/0.1.0/skills/design/README.md` — brand voice + visual rules.
- `C:\Users\estev\Projects\vibe-iterate\docs\superpowers\specs\2026-05-19-vibe-iterate-homepage-design.md` — the design spec this plan implements.
- `C:\Users\estev\Projects\vibe-iterate\README.md` — the source of truth for what each mode and sidecar does.

---

## Task 1: Confirm working directory + branch

**Files:**
- Touch: none (verification only)

- [ ] **Step 1: Set working directory to the hub repo**

Run:
```
cd "C:\Users\estev\Projects\626labs-hub"
```

- [ ] **Step 2: Verify git state is clean and on main**

Run:
```
git status
git rev-parse --abbrev-ref HEAD
```

Expected: working tree clean, branch is `main`. If not clean, stash or commit existing work before starting.

- [ ] **Step 3: Create a feature branch**

Run:
```
git checkout -b feat/vibe-iterate-landing
```

Expected: `Switched to a new branch 'feat/vibe-iterate-landing'`.

- [ ] **Step 4: Verify required files exist**

Run:
```
ls Design/colors_and_type.css scripts/render-hub.py content/site.json index.html
```

Expected: all four print, no "No such file." If any are missing, stop and investigate before proceeding.

---

## Task 2: Scaffold the page (head, nav, footer skeleton)

**Files:**
- Create: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Create the subfolder**

Run:
```
mkdir vibe-iterate
```

- [ ] **Step 2: Write the page skeleton**

Create `626labs-hub/vibe-iterate/index.html` with this content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>vibe-iterate · Maintain your Atlas. · 626 Labs</title>
  <meta name="description" content="Claude Code plugin for post-ship product iteration. Four modes, six sidecars, one PR per session. By 626 Labs." />
  <link rel="canonical" href="https://626labs.dev/vibe-iterate/" />
  <link rel="icon" type="image/png" href="/favicon-626.png" />

  <meta property="og:title" content="vibe-iterate · Maintain your Atlas." />
  <meta property="og:description" content="Claude Code plugin for post-ship product iteration. Four modes, six sidecars, one PR per session." />
  <meta property="og:url" content="https://626labs.dev/vibe-iterate/" />
  <meta property="og:image" content="https://626labs.dev/assets/og-vibe-iterate.png" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="626 Labs" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="https://626labs.dev/assets/og-vibe-iterate.png" />

  <style>
    /* 626 Labs Design System tokens — see ../Design/colors_and_type.css */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
      --navy-deep: #0f1f31;
      --navy-mid:  #192e44;
      --navy-hi:   #223a54;
      --navy-line: #2a3a5c;
      --cyan:      #17d4fa;
      --cyan-pale: #5ce6ff;
      --cyan-dim:  #0fa8c9;
      --magenta:   #f22f89;
      --magenta-pale: #ff66a8;
      --success:   #2bd99a;
      --ink-0:     #ffffff;
      --ink-100:   #e8eef7;
      --ink-200:   #c0cad8;
      --ink-300:   #8a98ad;
      --ink-400:   #5e6e84;
      --r-sm: 6px;
      --r-md: 10px;
      --r-lg: 14px;
      --r-xl: 20px;
      --maxw: 1240px;
      --gutter: 24px;
      --grad-duo: linear-gradient(135deg, var(--cyan) 0%, var(--magenta) 100%);
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body {
      background: var(--navy-deep);
      color: var(--ink-100);
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }
    a { color: var(--cyan); text-decoration: none; }
    a:hover { text-decoration: underline; text-decoration-color: var(--magenta); }

    .container { max-width: var(--maxw); margin: 0 auto; padding: 0 var(--gutter); }

    /* Eyebrows */
    .eyebrow {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--cyan);
    }

    /* Headings */
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink-0); margin: 0 0 16px; font-weight: 600; }
    h1 { font-size: clamp(40px, 5vw, 64px); letter-spacing: -0.025em; line-height: 1.05; }
    h2 { font-size: clamp(28px, 3vw, 40px); letter-spacing: -0.02em; line-height: 1.1; }
    h3 { font-size: clamp(22px, 2vw, 28px); line-height: 1.2; }

    /* Buttons */
    .btn {
      display: inline-block;
      padding: 12px 20px;
      border-radius: var(--r-md);
      font-family: 'Inter', sans-serif;
      font-size: 15px;
      font-weight: 500;
      transition: all 120ms cubic-bezier(.2,.7,.2,1);
      cursor: pointer;
      border: none;
      text-decoration: none;
    }
    .btn-primary {
      background: var(--grad-duo);
      color: var(--ink-0);
    }
    .btn-primary:hover { filter: brightness(1.08); box-shadow: 0 0 24px rgba(23,212,250,.35); text-decoration: none; }
    .btn-ghost {
      background: transparent;
      color: var(--ink-0);
      border: 1px solid rgba(255,255,255,.16);
    }
    .btn-ghost:hover { background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.32); text-decoration: none; }

    /* Nav */
    nav.top {
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(15,31,49,.7);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255,255,255,.06);
    }
    nav.top .row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 56px;
    }
    nav.top .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--ink-0);
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 600;
      font-size: 16px;
    }
    nav.top .brand:hover { text-decoration: none; }
    nav.top .brand img { height: 28px; width: auto; }

    /* Footer */
    footer {
      margin-top: 96px;
      padding: 32px 0 48px;
      border-top: 1px solid rgba(255,255,255,.06);
      color: var(--ink-300);
      font-size: 14px;
    }
    footer .row { display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap; }
    footer .tagline { font-family: 'Space Grotesk', sans-serif; color: var(--ink-200); }
    footer .links { display: flex; gap: 20px; }

    @media (max-width: 720px) {
      footer .row { flex-direction: column; gap: 12px; }
    }
  </style>
</head>
<body>

  <nav class="top">
    <div class="container row">
      <a href="/" class="brand">
        <img src="/favicon-626.png" alt="626 Labs" />
        <span>626 Labs</span>
      </a>
      <a href="#install" class="btn btn-ghost">Install</a>
    </div>
  </nav>

  <main>
    <!-- HERO (Task 3) -->
    <!-- MODES (Task 4) -->
    <!-- SIDECARS (Task 5) -->
    <!-- PTOLEMY (Task 6) -->
    <!-- INSTALL (Task 7) -->
    <!-- FAMILY (Task 8) -->
  </main>

  <footer>
    <div class="container row">
      <div>626 Labs LLC · MIT · 2026</div>
      <div class="tagline">Imagine Something Else.</div>
      <div class="links">
        <a href="https://github.com/estevanhernandez-stack-ed/vibe-iterate">GitHub</a>
        <a href="https://github.com/estevanhernandez-stack-ed/vibe-plugins">Marketplace</a>
      </div>
    </div>
  </footer>

</body>
</html>
```

- [ ] **Step 3: Open in browser to verify the skeleton renders**

Run:
```
start vibe-iterate\index.html
```

Expected: a mostly-empty navy page with a top nav (626 Labs mark + "Install" ghost button) and a footer with three slots. No console errors. If `start` doesn't open it, double-click the file or open with `file:///C:/Users/estev/Projects/626labs-hub/vibe-iterate/index.html` in a browser.

- [ ] **Step 4: Commit**

Run:
```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): scaffold landing page with nav + footer"
```

---

## Task 3: Build the hero section

**Files:**
- Modify: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Add hero styles inside `<style>` (append after existing CSS)**

Add this block to the `<style>` element, right before the closing `</style>`:

```css
    /* Hero */
    section.hero {
      position: relative;
      padding: 80px 0 96px;
      overflow: hidden;
    }
    section.hero::before {
      content: '';
      position: absolute;
      inset: 0;
      background:
        radial-gradient(60% 50% at 30% 20%, rgba(23,212,250,.18) 0%, transparent 60%),
        radial-gradient(40% 40% at 80% 60%, rgba(242,47,137,.14) 0%, transparent 60%);
      pointer-events: none;
      z-index: 0;
    }
    section.hero .container { position: relative; z-index: 1; }
    .hero-grid {
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 48px;
      align-items: center;
    }
    .hero-left .eyebrow { margin-bottom: 16px; display: inline-block; }
    .hero-subhead {
      color: var(--ink-200);
      font-size: clamp(17px, 1.4vw, 19px);
      max-width: 560px;
      margin: 0 0 28px;
    }
    .hero-ctas { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 28px; }
    .hero-meta {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      color: var(--ink-300);
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 13px;
    }
    .hero-meta span { color: var(--ink-200); }

    /* Terminal block */
    .term {
      background: var(--navy-mid);
      border-radius: var(--r-lg);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.06), 0 8px 32px rgba(0,0,0,.35);
      overflow: hidden;
    }
    .term-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      background: rgba(0,0,0,.18);
      border-bottom: 1px solid rgba(255,255,255,.04);
    }
    .term-dot { width: 10px; height: 10px; border-radius: 50%; }
    .term-dot.r { background: #ff5f57; }
    .term-dot.y { background: #febc2e; }
    .term-dot.g { background: #28c840; }
    .term-label {
      margin-left: 12px;
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 12px;
      color: var(--ink-300);
    }
    .term-body {
      padding: 20px;
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 13px;
      line-height: 1.65;
      color: var(--ink-200);
      max-height: 420px;
    }
    .term-body .prompt { color: var(--cyan); }
    .term-body .cmd { color: var(--ink-0); }
    .term-body .agent { color: var(--cyan); }
    .term-body .path { color: var(--cyan-pale); }
    .term-body .key { color: var(--magenta-pale); }
    .term-body .ok { color: var(--success); }
    .term-body .muted { color: var(--ink-400); }
    .term-cursor {
      display: inline-block;
      width: 8px;
      height: 14px;
      background: var(--cyan);
      vertical-align: -2px;
      animation: blink 1.05s steps(1) infinite;
    }
    @keyframes blink { 50% { opacity: 0; } }

    @media (max-width: 900px) {
      .hero-grid { grid-template-columns: 1fr; gap: 32px; }
    }
```

- [ ] **Step 2: Replace the `<!-- HERO (Task 3) -->` comment with the hero markup**

```html
    <section class="hero">
      <div class="container">
        <div class="hero-grid">
          <div class="hero-left">
            <span class="eyebrow">626 Labs · Claude Code plugin</span>
            <h1>Maintain your Atlas.</h1>
            <p class="hero-subhead">Cart took you idea &rarr; v1. vibe-iterate takes you v1 &rarr; v1+n. Ships one PR per session &mdash; regression-aware, small-diff-preferred.</p>
            <div class="hero-ctas">
              <a href="#install" class="btn btn-primary">Install plugin</a>
              <a href="https://github.com/estevanhernandez-stack-ed/vibe-iterate/blob/main/docs/2026-05-04-vibe-iterate-design.md" class="btn btn-ghost">Read the spec</a>
            </div>
            <div class="hero-meta">
              <span>v1.0.0</span><span>·</span><span>4 modes</span><span>·</span><span>6 sidecars</span><span>·</span><span>MIT</span>
            </div>
          </div>

          <div class="hero-right">
            <div class="term">
              <div class="term-bar">
                <span class="term-dot r"></span>
                <span class="term-dot y"></span>
                <span class="term-dot g"></span>
                <span class="term-label">vibe-iterate ~</span>
              </div>
              <div class="term-body">
                <div><span class="prompt">$</span> <span class="cmd">/vibe-iterate</span></div>
                <div><span class="agent">[Ptolemy]</span> Reading project state...</div>
                <div>  &rarr; Atlas: <span class="key">12 entries</span>, last shipped 4 days ago</div>
                <div>  &rarr; Stack: <span class="path">Next.js 15.2.0</span>, <span class="path">Tailwind 4</span>, <span class="path">Supabase</span></div>
                <div>  &rarr; Radar cache: 6 days old <span class="muted">(stale)</span></div>
                <div>&nbsp;</div>
                <div><span class="agent">[Ptolemy]</span> Recommended mode for the moment:</div>
                <div>  <span class="key">feature-add</span> &mdash; Product Hunt surfaced 3 candidates,</div>
                <div>  framework releases include <span class="path">Tailwind v4.1</span>,</div>
                <div>  feedback.md has 2 fresh requests.</div>
                <div>&nbsp;</div>
                <div>Launch <span class="key">feature-add</span>? [y/N]: <span class="cmd">y</span></div>
                <div>&nbsp;</div>
                <div><span class="agent">[Ptolemy]</span> Scanning... <span class="ok">done</span> (3 comp, 1 PH, 1 fwk, 2 feedback)</div>
                <div><span class="agent">[Ptolemy]</span> Top candidate: <span class="key">inline AI command palette</span></div>
                <div>  impact: <span class="ok">high</span> · fit: <span class="ok">high</span> · risk: <span class="ok">low</span></div>
                <div>&nbsp;</div>
                <div><span class="agent">[Ptolemy]</span> PR ready: <span class="path">feat: inline AI command palette (Cmd+K)</span><span class="term-cursor"></span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Open in browser, verify hero looks right**

Refresh the page. Expected:
- Two-column layout on desktop, stacked on mobile (<900px).
- H1 reads "Maintain your Atlas." in white Space Grotesk, large.
- Cyan eyebrow above it.
- Subhead in slightly-dim white.
- Cyan→magenta gradient on "Install plugin" button.
- Terminal block to the right with the fake session, blinking cursor at the end.
- Soft radial cyan + magenta glow in the background.

Test at narrow width (resize browser to ~600px): terminal stacks below.

- [ ] **Step 4: Commit**

```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): hero with tagline, install CTA, terminal demo"
```

---

## Task 4: Build the modes grid

**Files:**
- Modify: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Add modes styles to `<style>` (append)**

```css
    /* Section base */
    section.work, section.brain, section.install, section.family {
      padding: 80px 0;
    }
    .section-head { margin-bottom: 40px; }
    .section-head .eyebrow { display: inline-block; margin-bottom: 12px; }
    .section-head .lead {
      color: var(--ink-200);
      font-size: 17px;
      max-width: 640px;
      margin: 8px 0 0;
    }

    /* Card */
    .card {
      background: var(--navy-mid);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--r-lg);
      padding: 24px;
      transition: border-color 120ms cubic-bezier(.2,.7,.2,1);
    }
    .card:hover { border-color: rgba(23,212,250,.45); }
    .card .cmd {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--cyan);
      display: inline-block;
      margin-bottom: 10px;
    }
    .card h3 { margin: 0 0 8px; font-size: 22px; }
    .card .desc { color: var(--ink-200); margin: 0 0 12px; }
    .card .reach {
      color: var(--ink-300);
      font-size: 14px;
      border-top: 1px solid rgba(255,255,255,.06);
      padding-top: 12px;
      margin-top: 12px;
    }
    .card .reach em { color: var(--magenta-pale); font-style: normal; }

    .modes-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    @media (max-width: 720px) {
      .modes-grid { grid-template-columns: 1fr; }
      section.work, section.brain, section.install, section.family { padding: 56px 0; }
      .card { padding: 20px; }
    }
```

- [ ] **Step 2: Replace the `<!-- MODES (Task 4) -->` comment with the modes markup**

```html
    <section class="work" id="work">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">01 · The work</span>
          <h2>Four modes for what's next.</h2>
          <p class="lead">Pick the mode for the moment. Each ships one PR per session, with Atlas continuity across runs.</p>
        </div>

        <div class="modes-grid">
          <div class="card">
            <span class="cmd">/vibe-iterate:feature-add</span>
            <h3>Ship the next feature.</h3>
            <p class="desc">Multi-source candidate scan: competitors, Product Hunt, framework releases, your feedback.md. Clusters, scores, picks one.</p>
            <p class="reach">Reach for it when <em>you don't know what to build next</em>.</p>
          </div>

          <div class="card">
            <span class="cmd">/vibe-iterate:competitive</span>
            <h3>Close the gaps that matter.</h3>
            <p class="desc">Reads competitor changelogs, diffs against your shipped product, ranks by strategic relevance &mdash; not parity.</p>
            <p class="reach">Reach for it when <em>a competitor shipped something loud</em>.</p>
          </div>

          <div class="card">
            <span class="cmd">/vibe-iterate:ux-polish</span>
            <h3>Tighten what's shipped but rough.</h3>
            <p class="desc">Walks routes, components, key flows. Scores by user-trust impact.</p>
            <p class="reach">Reach for it when <em>the product works but feels off</em>.</p>
          </div>

          <div class="card">
            <span class="cmd">/vibe-iterate:bug-bash</span>
            <h3>Fix the loudest bug.</h3>
            <p class="desc">Reads feedback.md, triages by severity &times; frequency &times; blast-radius. Dormant when feedback.md is missing.</p>
            <p class="reach">Reach for it when <em>users keep reporting the same thing</em>.</p>
          </div>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Refresh browser, verify the modes grid**

Expected:
- 2×2 grid on desktop, single column on mobile.
- Each card: cyan mono command at top, white sentence-case title, dim description, separator, "Reach for it when…" line with magenta accent on the italic phrase.
- Hover any card: border turns cyan, no lift.

- [ ] **Step 4: Commit**

```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): four-mode grid with reach-for cues"
```

---

## Task 5: Build the sidecars grid (continues the same section)

**Files:**
- Modify: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Add sidecars styles to `<style>` (append)**

```css
    .sidecars-head {
      margin-top: 56px;
      margin-bottom: 24px;
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
    }
    .sidecars-head h3 { margin: 0; }
    .sidecars-head .hint { color: var(--ink-300); font-size: 14px; }
    .sidecars-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }
    .sidecar {
      background: var(--navy-mid);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--r-md);
      padding: 16px 18px;
      display: flex;
      gap: 14px;
      align-items: flex-start;
      transition: border-color 120ms cubic-bezier(.2,.7,.2,1);
    }
    .sidecar:hover { border-color: rgba(23,212,250,.45); }
    .sidecar svg {
      flex-shrink: 0;
      width: 20px;
      height: 20px;
      stroke: var(--cyan);
      fill: none;
      stroke-width: 1.75;
      stroke-linecap: round;
      stroke-linejoin: round;
      margin-top: 2px;
    }
    .sidecar .body { flex: 1; }
    .sidecar .name {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 13px;
      color: var(--cyan);
      display: block;
      margin-bottom: 4px;
    }
    .sidecar .desc { color: var(--ink-200); font-size: 14px; margin: 0; }
    @media (max-width: 900px) {
      .sidecars-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 540px) {
      .sidecars-grid { grid-template-columns: 1fr; }
    }
```

- [ ] **Step 2: Add the sidecars markup before the closing `</div></section>` of the work section**

Find the `</div></section>` that closes `section.work` (after the modes-grid div) and insert this just before it:

```html
        <div class="sidecars-head">
          <h3>Six tools when a mode is too much.</h3>
          <span class="hint">Run any sidecar directly &mdash; no mode required.</span>
        </div>
        <div class="sidecars-grid">

          <div class="sidecar">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>
            <div class="body">
              <span class="name">:radar</span>
              <p class="desc">What's new across your stack and competitors since last visit.</p>
            </div>
          </div>

          <div class="sidecar">
            <svg viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>
            <div class="body">
              <span class="name">:spy &lt;url&gt;</span>
              <p class="desc">One-shot competitive read on a single URL.</p>
            </div>
          </div>

          <div class="sidecar">
            <svg viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.27 6.96 12 12.01l8.73-5.05M12 22.08V12"/></svg>
            <div class="body">
              <span class="name">:scan-releases [pkg]</span>
              <p class="desc">What's new in this lib since you last bumped.</p>
            </div>
          </div>

          <div class="sidecar">
            <svg viewBox="0 0 24 24"><path d="M16 16.5V8L8 16V8M3 21h18"/></svg>
            <div class="body">
              <span class="name">:rate &lt;idea&gt;</span>
              <p class="desc">Score an idea on impact / fit / effort / regression-risk / user-trust.</p>
            </div>
          </div>

          <div class="sidecar">
            <svg viewBox="0 0 24 24"><path d="M2 20a4 4 0 0 0 4 0 4 4 0 0 1 4 0 4 4 0 0 0 4 0 4 4 0 0 1 4 0 4 4 0 0 0 4 0M3 16l9-13 9 13M12 3v13"/></svg>
            <div class="body">
              <span class="name">:ship &lt;brief&gt;</span>
              <p class="desc">Express lane. Skip ingestion, ship from a brief.</p>
            </div>
          </div>

          <div class="sidecar">
            <svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
            <div class="body">
              <span class="name">:upgrade &lt;pkg&gt;</span>
              <p class="desc">Surgical library bump with codemods if available.</p>
            </div>
          </div>

        </div>
```

- [ ] **Step 3: Refresh browser, verify**

Expected:
- 3-column grid on desktop, 2-column on tablet, 1-column on mobile.
- Each sidecar: cyan Lucide-style icon left, mono command name, one-line description.
- Hover: border turns cyan.
- Section flows naturally below the modes grid with `Six tools when a mode is too much.` subhead.

- [ ] **Step 4: Commit**

```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): six-sidecar grid below modes"
```

---

## Task 6: Build the Ptolemy / brain section

**Files:**
- Modify: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Add brain section styles to `<style>` (append)**

```css
    section.brain { background: linear-gradient(180deg, transparent 0%, rgba(23,212,250,.03) 100%); }
    .brain-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 48px;
      align-items: start;
    }
    .brain-grid p {
      color: var(--ink-200);
      margin: 0 0 16px;
      max-width: 540px;
    }
    .brain-grid strong { color: var(--ink-0); font-weight: 500; }
    .callout {
      margin-top: 32px;
      padding: 20px 24px;
      border-top: 1px solid rgba(23,212,250,.35);
      border-bottom: 1px solid rgba(23,212,250,.35);
      background: rgba(23,212,250,.04);
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 14px;
      color: var(--ink-100);
      max-width: 540px;
    }
    @media (max-width: 900px) {
      .brain-grid { grid-template-columns: 1fr; gap: 24px; }
    }
```

- [ ] **Step 2: Replace the `<!-- PTOLEMY (Task 6) -->` comment with the brain section**

```html
    <section class="brain">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">02 · The brain</span>
          <h2>Ptolemy stays current.</h2>
        </div>
        <div class="brain-grid">
          <div>
            <p><strong>Ptolemy is vibe-iterate's agent</strong> &mdash; senior to Cart's field-cartographer, oriented for already-shipped territory. He reads your stack via context7, watches framework releases on a weekly scan, and keeps your Atlas &mdash; the running record of what you've shipped, what you considered, what got cut, and why &mdash; in continuity across sessions.</p>
            <p>When <strong>vibe-cartographer</strong> is installed in the same repo, Ptolemy defers cleanly (Pattern #13). When it's not, vibe-iterate stands on its own. <strong>Composes, never depends.</strong></p>
          </div>
          <div>
            <div class="callout">No telemetry. Atlas data stays on your machine.</div>
          </div>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Refresh browser, verify**

Expected:
- Two columns: paragraphs on the left, callout band on the right.
- Callout band: cyan hairlines top and bottom, faint cyan-tinted background, mono type.
- On mobile, stacks vertically.

- [ ] **Step 4: Commit**

```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): Ptolemy / brain section with no-telemetry callout"
```

---

## Task 7: Build the install section with copy-to-clipboard JS

**Files:**
- Modify: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Add install styles to `<style>` (append)**

```css
    .install-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 24px;
    }
    .install-card { padding: 24px; }
    .install-card h3 {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 0 0 6px;
    }
    .install-card .badge {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 3px 8px;
      border-radius: var(--r-sm);
      background: rgba(23,212,250,.12);
      color: var(--cyan);
    }
    .install-card .badge.magenta { background: rgba(242,47,137,.12); color: var(--magenta-pale); }
    .install-card .blurb { color: var(--ink-200); margin: 0 0 16px; font-size: 14px; }
    .codeblock {
      position: relative;
      background: var(--navy-deep);
      border: 1px solid rgba(23,212,250,.25);
      border-radius: var(--r-md);
      padding: 14px 44px 14px 16px;
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 13px;
      color: var(--ink-100);
      line-height: 1.7;
      overflow-x: auto;
    }
    .codeblock .copybtn {
      position: absolute;
      top: 8px;
      right: 8px;
      background: transparent;
      border: 1px solid rgba(255,255,255,.12);
      border-radius: var(--r-sm);
      padding: 4px 8px;
      cursor: pointer;
      color: var(--ink-300);
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 11px;
      transition: all 120ms cubic-bezier(.2,.7,.2,1);
    }
    .codeblock .copybtn:hover { color: var(--cyan); border-color: rgba(23,212,250,.45); }
    .codeblock .copybtn.ok { color: var(--success); border-color: rgba(43,217,154,.45); }
    .install-note {
      margin-top: 20px;
      color: var(--ink-300);
      font-size: 14px;
    }
    @media (max-width: 720px) {
      .install-grid { grid-template-columns: 1fr; }
    }
```

- [ ] **Step 2: Replace the `<!-- INSTALL (Task 7) -->` comment with the install section**

```html
    <section class="install" id="install">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">03 · Get it</span>
          <h2>Two channels.</h2>
        </div>

        <div class="install-grid">
          <div class="card install-card">
            <h3>Stable <span class="badge">marketplace</span></h3>
            <p class="blurb">Tagged releases, promoted via the Vibe Plugins marketplace.</p>
            <div class="codeblock">
              <button class="copybtn" data-target="copy-stable">copy</button>
              <pre id="copy-stable" style="margin:0;white-space:pre">/plugin marketplace add estevanhernandez-stack-ed/vibe-plugins
/plugin install vibe-iterate</pre>
            </div>
          </div>

          <div class="card install-card">
            <h3>Canary <span class="badge magenta">bleeding edge</span></h3>
            <p class="blurb">Latest <code>main</code> from this repo. Re-syncs on every push.</p>
            <div class="codeblock">
              <button class="copybtn" data-target="copy-canary">copy</button>
              <pre id="copy-canary" style="margin:0;white-space:pre">/plugin marketplace add estevanhernandez-stack-ed/vibe-iterate
/plugin install vibe-iterate</pre>
            </div>
          </div>
        </div>

        <p class="install-note">Pick stable if you want to be told. Pick canary if you want to tell us.</p>
      </div>
    </section>
```

- [ ] **Step 3: Add the copy-to-clipboard script just before `</body>`**

```html
  <script>
    document.querySelectorAll('.copybtn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var targetId = btn.getAttribute('data-target');
        var target = document.getElementById(targetId);
        if (!target) return;
        var text = target.textContent;
        navigator.clipboard.writeText(text).then(function() {
          var orig = btn.textContent;
          btn.textContent = 'copied';
          btn.classList.add('ok');
          setTimeout(function() {
            btn.textContent = orig;
            btn.classList.remove('ok');
          }, 1500);
        });
      });
    });
  </script>
```

- [ ] **Step 4: Refresh browser, verify**

Expected:
- Two cards side-by-side: Stable (cyan badge) and Canary (magenta badge).
- Each has a code block with a `copy` button top-right.
- Click `copy` — button text changes to `copied` in green for 1.5s, then back. Paste in a text editor and verify the two-line install command.
- Both code blocks have cyan hairline borders.
- Below: italic note about picking a channel.

- [ ] **Step 5: Commit**

```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): install section with stable + canary + copy-to-clipboard"
```

---

## Task 8: Build the family section

**Files:**
- Modify: `626labs-hub/vibe-iterate/index.html`

- [ ] **Step 1: Add family styles to `<style>` (append)**

```css
    .family-lead { color: var(--ink-200); margin: 0 0 32px; max-width: 640px; }
    .family-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }
    .family-card {
      background: var(--navy-mid);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--r-md);
      padding: 18px 20px;
      display: block;
      color: var(--ink-100);
      transition: all 120ms cubic-bezier(.2,.7,.2,1);
    }
    .family-card:hover {
      border-color: rgba(23,212,250,.45);
      text-decoration: none;
    }
    .family-card.here {
      border-color: rgba(23,212,250,.55);
      box-shadow: 0 0 24px rgba(23,212,250,.18);
    }
    .family-card .name {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 17px;
      font-weight: 600;
      color: var(--ink-0);
      margin-bottom: 2px;
    }
    .family-card .role { color: var(--ink-300); font-size: 14px; }
    .family-card .you {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--cyan);
      margin-top: 6px;
    }
    @media (max-width: 720px) {
      .family-grid { grid-template-columns: 1fr; }
    }
```

- [ ] **Step 2: Replace the `<!-- FAMILY (Task 8) -->` comment with the family section**

```html
    <section class="family">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">04 · Family</span>
          <h2>One plugin in a family.</h2>
        </div>
        <p class="family-lead">Vibe Plugins are a coordinated family &mdash; installed independently, composed when present.</p>

        <div class="family-grid">
          <a href="https://github.com/estevanhernandez-stack-ed/vibe-cartographer" class="family-card">
            <div class="name">vibe-cartographer</div>
            <div class="role">idea &rarr; v1</div>
          </a>
          <a href="/vibe-iterate/" class="family-card here">
            <div class="name">vibe-iterate</div>
            <div class="role">v1 &rarr; v1+n</div>
            <div class="you">You are here</div>
          </a>
          <a href="https://github.com/estevanhernandez-stack-ed/Vibe-Doc" class="family-card">
            <div class="name">vibe-doc</div>
            <div class="role">documentation completeness</div>
          </a>
          <a href="https://github.com/estevanhernandez-stack-ed/vibe-plugins" class="family-card">
            <div class="name">vibe-test</div>
            <div class="role">test coverage and tier enforcement</div>
          </a>
          <a href="https://github.com/estevanhernandez-stack-ed/vibe-plugins" class="family-card">
            <div class="name">vibe-sec</div>
            <div class="role">security posture</div>
          </a>
          <a href="https://github.com/estevanhernandez-stack-ed/vibe-plugins" class="family-card">
            <div class="name">thesis-engine + vibe-thesis</div>
            <div class="role">research authoring</div>
          </a>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Refresh browser, verify**

Expected:
- 3-column grid (1-column on mobile).
- vibe-iterate card has cyan border + faint cyan glow + "You are here" eyebrow.
- Other cards hover-highlight on mouseover.
- All six entries clickable.

- [ ] **Step 4: Commit**

```
git add vibe-iterate/index.html
git commit -m "feat(vibe-iterate): family section with you-are-here marker"
```

---

## Task 9: Full-page in-browser verification before integration

**Files:**
- Touch: none (verification only)

- [ ] **Step 1: Open the page at multiple widths**

Open `626labs-hub/vibe-iterate/index.html` in Chrome. Open DevTools (F12), toggle device toolbar. Test these widths:
- 1920px (desktop)
- 1280px (laptop)
- 768px (tablet)
- 375px (iPhone SE)

For each: confirm hero stacks cleanly, modes go to 1 column, sidecars go to 1 column, install cards stack, family grid goes to 1 column. No horizontal scroll on the body.

- [ ] **Step 2: Verify zero console errors**

In DevTools console: no red errors, no yellow warnings related to the page (404s on assets are fine if they reference deployed-only paths).

- [ ] **Step 3: Click every link and button**

- Top nav "Install" → scrolls to install section.
- Hero primary CTA "Install plugin" → scrolls to install.
- Hero secondary CTA "Read the spec" → opens GitHub design doc in new tab (will need to verify after deploy; locally just confirm the href is correct).
- All 6 sidecars hover-highlight.
- Copy buttons work on both install blocks.
- All 6 family cards have correct hrefs.
- Footer GitHub and Marketplace links resolve.

- [ ] **Step 4: Lighthouse spot-check**

DevTools → Lighthouse → run for Performance, Accessibility, Best Practices, SEO. Expected:
- Accessibility: ≥95
- Performance: ≥90 (locally may be lower due to font-loading delay; not a hard gate)
- Best Practices: ≥90
- SEO: ≥95

If accessibility scores below 95, check for: missing alt text, low color contrast, missing landmarks. Fix inline before continuing.

- [ ] **Step 5: Commit any inline fixes**

If you made fixes in step 4:
```
git add vibe-iterate/index.html
git commit -m "fix(vibe-iterate): accessibility / verification touch-ups"
```

If no fixes needed, skip the commit.

---

## Task 10: Add vibe-iterate product entry + hero chip to site.json

**Files:**
- Modify: `626labs-hub/content/site.json`

- [ ] **Step 1: Read the current `products` array in `site.json`**

Open `626labs-hub/content/site.json`. Find the `products` array (begins around line 130). Confirm the structure: it's a JSON array of product objects.

- [ ] **Step 2: Insert the vibe-iterate entry immediately after vibe-cartographer**

Find the closing `}` of the `vibe-cartographer` entry. Add a comma after it, then insert this object:

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
      "productPage": "/vibe-iterate/",
      "screenshots": []
    },
```

Make sure the entry **before** it (vibe-cartographer's closing `}`) ends with a comma, and the entry **after** it (vibe-keystone, vibe-doc, etc.) is intact.

- [ ] **Step 3: Add a vibe-iterate chip to the hero**

Find the `hero.chips` array (around line 31). Add a new chip entry. The current chips end with:

```json
      {
        "label": "claude-code",
        "tone": "cyan"
      }
    ]
```

Change it to add vibe-iterate before claude-code (or extend the array — doesn't matter functionally; both look fine):

```json
      {
        "label": "vibe-iterate",
        "tone": "cyan"
      },
      {
        "label": "claude-code",
        "tone": "cyan"
      }
    ]
```

- [ ] **Step 4: Validate JSON**

Run:
```
python -c "import json; json.load(open('content/site.json'))"
```

Expected: no output, exit code 0. If there's a parse error, fix the syntax (likely a missing comma or extra trailing comma).

- [ ] **Step 5: Commit**

```
git add content/site.json
git commit -m "feat(hub): add vibe-iterate product entry + hero chip"
```

---

## Task 11: Add vibe-iterate sigil to PRODUCT_SIGILS in render-hub.py

**Files:**
- Modify: `626labs-hub/scripts/render-hub.py:189-222`

- [ ] **Step 1: Read the current PRODUCT_SIGILS dict**

Open `626labs-hub/scripts/render-hub.py`. Find the `PRODUCT_SIGILS` dict starting at line 189. Note the existing entries are short SVGs with stroke paths, no fills, viewBox 24x24.

- [ ] **Step 2: Add a vibe-iterate entry to the dict**

Insert this entry after `"vibe-cartographer": (...)` and before `"vibe-doc": (...)`:

```python
    "vibe-iterate": (
        '<svg class="ic-lg ic" viewBox="0 0 24 24">'
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M12 3v18M3 12h18"/>'
        '<path d="M12 7l3 5-3 5-3-5z"/>'
        '</svg>'
    ),
```

This renders as a compass-rose: circle, crosshair, central diamond — fits the atlas/cartography theme.

- [ ] **Step 3: Verify the file still parses**

Run:
```
python -m py_compile scripts/render-hub.py
```

Expected: no output, exit code 0. A `SyntaxError` here means the dict edit broke something — likely a missing comma or unbalanced parenthesis.

- [ ] **Step 4: Commit**

```
git add scripts/render-hub.py
git commit -m "feat(hub): add vibe-iterate sigil to PRODUCT_SIGILS"
```

---

## Task 12: Run render-hub.py and verify hub index.html updates

**Files:**
- Auto-modified by renderer: `626labs-hub/index.html`

- [ ] **Step 1: Run the renderer**

Run:
```
python scripts/render-hub.py
```

Expected: no errors, no warnings. The script rewrites the `SITE_JSON:products` zone of `index.html` to include the new vibe-iterate card.

- [ ] **Step 2: Verify the diff**

Run:
```
git diff index.html
```

Expected diff contains:
- A new `<article class="product">` block for vibe-iterate.
- The compass-rose SVG sigil you defined.
- The title "Vibe Iterate", tagline, description.
- An "Open product page" link to `/vibe-iterate/`.
- A new chip in the hero's chip strip showing `vibe-iterate`.

If the diff doesn't contain these, run `python scripts/render-hub.py --check` and see what it reports.

- [ ] **Step 3: Open `index.html` in browser, verify card and chip**

Open `626labs-hub/index.html` directly. Find the products grid. Confirm:
- vibe-iterate card appears (in position 2 — right after vibe-cartographer).
- Card has the compass-rose sigil.
- "Open product page" link points to `/vibe-iterate/`.
- Hero chip strip shows `vibe-iterate` somewhere in the chip row.

- [ ] **Step 4: Click the "Open product page" link**

It should resolve to `/vibe-iterate/` — in local file mode, this will try to open a folder. To validate the link target is correct, hover and inspect the href: it should be `/vibe-iterate/` (root-relative). The link will only resolve in the deployed environment.

- [ ] **Step 5: Commit**

```
git add index.html
git commit -m "chore(hub): re-render index.html with vibe-iterate product card"
```

---

## Task 13: Generate the custom OG card

**Files:**
- Create: `626labs-hub/assets/og-vibe-iterate.png`
- Modify (optional): `626labs-hub/scripts/export-brand.py` or a new small script

Two paths — pick one based on engineer preference.

### Path A: Hand-built via image editor

- [ ] **Step 1: Create the OG card**

Build a 1200×630 PNG with these elements:
- Background: solid `#0f1f31` (navy-deep).
- Bottom-right corner: faint radial glow, cyan → magenta, at 15-20% opacity.
- Large title: `vibe-iterate` in Space Grotesk Bold, white, ~96px, left-aligned at x≈80px y≈260px.
- Subtitle below: `Maintain your Atlas.` in Space Grotesk Regular, color #c0cad8, ~36px.
- Eyebrow above title: `626 LABS · CLAUDE CODE PLUGIN` in JetBrains Mono Uppercase, cyan, ~16px, +0.12em tracking.
- Top-right: 626 Labs logo mark (from `assets/icon-626-64.png` or similar), 48px wide.
- Bottom-left: small text `626labs.dev/vibe-iterate` in JetBrains Mono, ink-300.

Save as `626labs-hub/assets/og-vibe-iterate.png`.

### Path B: Generate programmatically via Pillow

- [ ] **Step 1: Create a new script `626labs-hub/scripts/export-og-vibe-iterate.py`**

```python
"""
Generate the OG card for the vibe-iterate landing page.
Run: python scripts/export-og-vibe-iterate.py
Output: assets/og-vibe-iterate.png
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
NAVY = (15, 31, 49)
CYAN = (23, 212, 250)
INK_0 = (255, 255, 255)
INK_200 = (192, 202, 216)
INK_300 = (138, 152, 173)

FONTS_DIR = Path(__file__).resolve().parents[1] / "fonts"
DISPLAY = FONTS_DIR / "SpaceGrotesk-Bold.ttf"
DISPLAY_REG = FONTS_DIR / "SpaceGrotesk-Regular.ttf"
MONO = FONTS_DIR / "JetBrainsMono-Medium.ttf"

OUT = Path(__file__).resolve().parents[1] / "assets" / "og-vibe-iterate.png"

def main():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img, "RGBA")

    # Soft cyan glow bottom-right (layered low-alpha ellipses + a blur pass)
    from PIL import ImageFilter
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, alpha in [(500, 18), (380, 28), (260, 40)]:
        gd.ellipse([W - 200 - r, H - 100 - r, W - 200 + r, H - 100 + r], fill=(23, 212, 250, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img.paste(glow, (0, 0), glow)

    # Eyebrow
    eyebrow = ImageFont.truetype(str(MONO), 18)
    draw.text((80, 200), "626 LABS  ·  CLAUDE CODE PLUGIN", font=eyebrow, fill=CYAN)

    # Title
    title = ImageFont.truetype(str(DISPLAY), 96)
    draw.text((80, 240), "vibe-iterate", font=title, fill=INK_0)

    # Subtitle
    sub = ImageFont.truetype(str(DISPLAY_REG), 38)
    draw.text((80, 360), "Maintain your Atlas.", font=sub, fill=INK_200)

    # Footer URL
    footer = ImageFont.truetype(str(MONO), 16)
    draw.text((80, H - 60), "626labs.dev/vibe-iterate", font=footer, fill=INK_300)

    # 626 Labs logo (top-right)
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "icon-626-64.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA").resize((56, 56))
        img.paste(logo, (W - 56 - 80, 60), logo)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

Run:
```
python scripts/export-og-vibe-iterate.py
```

Expected: writes `assets/og-vibe-iterate.png`. If `Pillow` isn't installed: `pip install Pillow` then retry. If a font file is missing under `fonts/`, list the contents (`ls fonts/`) and adjust the script's font names to match (e.g., the file may be `SpaceGrotesk-Bold.ttf` or `SpaceGrotesk[wght].ttf` depending on which package was checked in).

- [ ] **Step 3: Open the generated PNG**

```
start assets\og-vibe-iterate.png
```

Expected: 1200×630 navy image with title, subtitle, eyebrow, footer URL, soft cyan glow, 626 Labs logo top-right. Text is sharp and readable. If text is fuzzy or fonts didn't load, fix font paths in the script and re-run.

- [ ] **Step 4: Commit**

```
git add assets/og-vibe-iterate.png
```

If you used Path B, also add the script:
```
git add scripts/export-og-vibe-iterate.py
```

Then:
```
git commit -m "feat(hub): add custom OG card for vibe-iterate landing"
```

---

## Task 14: Final cross-browser + mobile verification

**Files:**
- Touch: none (verification only)

- [ ] **Step 1: Cross-browser sweep**

Open `626labs-hub/vibe-iterate/index.html` in:
- Chrome (or Edge — same engine)
- Firefox

For each, confirm:
- Fonts load (no fallback serif/sans).
- Hero terminal cursor blinks.
- Hover states work on cards (border turns cyan).
- Copy buttons work in install section.
- Backdrop blur on nav (Firefox may need `-moz` prefix — if it doesn't blur, that's acceptable, content is still legible).

- [ ] **Step 2: Mobile spot-check via DevTools device emulation**

In Chrome DevTools → device toolbar → iPhone 14 Pro and Pixel 7. Test:
- Hero stacks vertically.
- Terminal block scrolls horizontally if needed (it shouldn't — content is sized to fit).
- Install code-blocks remain readable; copy button accessible.
- All buttons tap-target ≥44px height.

- [ ] **Step 3: Validate the OG card**

Open the PNG, eyeball it. Then mentally check: would a Twitter / Slack / Discord preview of `https://626labs.dev/vibe-iterate/` (using this OG card) look polished and identifiable as 626 Labs? If yes, proceed. If not, regenerate.

- [ ] **Step 4: HTML validation**

Paste the contents of `vibe-iterate/index.html` into https://validator.w3.org/ (or use a local tool). Fix any errors (warnings about CSS or autocomplete are fine).

- [ ] **Step 5: Note any deferred items**

If you find anything that's not a blocker but should be revisited (e.g., the terminal block content could be more realistic with actual file diffs), open a follow-up issue in the vibe-iterate solo repo — don't try to fix it in this PR.

- [ ] **Step 6: Commit any fixes**

If you made fixes in steps 1-4:
```
git add -A
git commit -m "fix(vibe-iterate): cross-browser and validation touch-ups"
```

If no fixes needed, skip the commit.

---

## Task 15: Push and verify deploy

**Files:**
- Touch: none on local

- [ ] **Step 1: Push the feature branch**

Run:
```
git push -u origin feat/vibe-iterate-landing
```

- [ ] **Step 2: Open a PR via gh CLI**

Run:
```
gh pr create --title "feat: vibe-iterate landing page" --body "Adds /vibe-iterate/ landing page on 626labs.dev for the Claude submission. New product card on the hub. Custom OG card. See docs/superpowers/specs/2026-05-19-vibe-iterate-homepage-design.md in the vibe-iterate solo repo for the design spec."
```

Capture the PR URL.

- [ ] **Step 3: Wait for CI**

The hub repo runs `link-check.yml` on `**/*.html` push. Wait for the workflow to complete. If links fail, fix them and push again.

- [ ] **Step 4: Merge the PR**

```
gh pr merge --merge
```

(Use `--squash` only if the hub repo uses squash merges — check existing merge history; the CLAUDE.md doesn't specify. Default to merge commit if unsure.)

- [ ] **Step 5: Verify GitHub Pages deploy**

GitHub Pages redeploys automatically on push to main. After ~1-2 minutes:

```
curl -sI https://626labs.dev/vibe-iterate/ | head -5
```

Expected: `HTTP/2 200` and the URL serves. Open in a real browser to confirm.

- [ ] **Step 6: Visit the main hub, confirm the product card**

Open `https://626labs.dev/` in a browser. Find the vibe-iterate card in the products grid. Click "Open product page" — should land at `/vibe-iterate/`.

- [ ] **Step 7: Validate OG preview**

Paste `https://626labs.dev/vibe-iterate/` into:
- Slack DM to yourself
- `https://www.opengraph.xyz/`

Expected: preview card shows the custom OG image, title, and description. If the OG image doesn't appear, check that `assets/og-vibe-iterate.png` was committed and that the meta tag URL is correct (`https://626labs.dev/assets/og-vibe-iterate.png`, not a relative path).

- [ ] **Step 8: Smoke-test on mobile**

Open the URL on a phone (iOS Safari or Android Chrome). Confirm:
- Page loads.
- Hero legible.
- Install copy-block works (the iOS / Android share menu may intercept; the native `navigator.clipboard.writeText` should still succeed).
- Family grid stacks correctly.

- [ ] **Step 9: Done — submission-ready**

The URL `https://626labs.dev/vibe-iterate/` is now the value for the Claude submission form's homepage field.

---

## Spec coverage check

| Spec section | Implementing task(s) |
|---|---|
| Architecture & hosting | Task 1 (setup), Task 2 (scaffold) |
| Page layout — top nav | Task 2 |
| Page layout — hero | Task 3 |
| Page layout — modes | Task 4 |
| Page layout — sidecars | Task 5 |
| Page layout — Ptolemy / brain | Task 6 |
| Page layout — install | Task 7 |
| Page layout — family | Task 8 |
| Page layout — footer | Task 2 |
| Visual / brand application | Tasks 2-8 (CSS distributed across sections) |
| Voice constraints | Tasks 2-8 (copy is part of each section) |
| Product card on hub | Tasks 10, 11, 12 |
| Submission artifact (meta tags, OG image) | Tasks 2, 13 |
| Verification | Tasks 9, 14, 15 |

## What's intentionally deferred (NOT in this plan)

- Adding a shared family-list partial. Hand-maintained in two places for v1 — acceptable for 6 entries.
- Replacing the designed terminal block with a real GIF / asciinema recording. v2.
- Adding a `vibe-iterate` entry to `PRODUCT_CATEGORY_LABELS` (flagship-only field; not applicable since vibe-iterate isn't flagship).
- Adding `anthropicApproved: true` — flip this after the submission is approved.
- Building out a multi-page docs site. Out of scope.
