# Claude plugin directory — remaining submissions

Copy-paste values for the rest of the family. Paste fields as-is (real line breaks where shown — never type literal `\n`).

**Status:** vibe-iterate submitted; vibe-doc, vibe-keystone, vibe-cartographer published. Below are the five not yet in the directory — including **vibe-taker**, which was missed from the original sweep (it shipped to the marketplace after this doc was first assembled).

**Privacy policy** (same for every plugin — paste into the privacy field on each submission):
```
https://626labs.dev/privacy
```

> ⚠️ **vibe-sec — recommend holding.** The plugin is pre-release: it reserves the directory slot but has no working slash commands yet (only the CLI secret scanner ships today). Submitting a plugin whose commands don't run risks rejection. Either hold until the commands land, or submit with the honest "CLI available, plugin rolling out" framing below — your call.

---

## vibe-test

**Link to plugin**
```
https://github.com/estevanhernandez-stack-ed/vibe-test
```
**Plugin homepage**
```
https://626labs.dev/vibe-test/
```
**Plugin name**
```
vibe-test
```
**Plugin description**
```
Test coverage for vibe-coded apps that actually matters. vibe-test reads your app, classifies it by type and deployment risk, and generates tests proportional to that risk — not a boilerplate dump, not a pass/fail meter. It catches the broken harnesses other tools assume away: runners that silently report 0%, missing test binaries, coverage cherry-picked over a fraction of your files. Seven commands cover audit, generate, fix, coverage, gate, and posture, and the handoff artifacts (test plan, runbook, CI stub) survive uninstalling the plugin. JS/TS today.
```
**Example use cases**
```
Your CI reports green but you suspect it's lying: /vibe-test:audit classifies your app, measures coverage with an honest denominator, and surfaces broken runners and cherry-picked coverage as first-class findings.
You shipped with thin coverage and don't know where to start: /vibe-test:generate writes tests proportional to your app's risk tier, matching your existing framework idioms.
A test broke in CI: /vibe-test:fix tells you whether it's the harness or the test logic and repairs by confidence.
You want a deploy gate: /vibe-test:gate applies a tier-appropriate threshold and exits pass/fail with GitHub Actions annotations.
```

---

## vibe-thesis

**Link to plugin**
```
https://github.com/estevanhernandez-stack-ed/Vibe-Thesis
```
**Plugin homepage**
```
https://626labs.dev/vibe-thesis/
```
**Plugin name**
```
vibe-thesis
```
**Plugin description**
```
Academic thesis authoring in Claude Code. vibe-thesis scaffolds and co-authors thesis-shaped artifacts — dissertations, master's theses, long-form research articles, position essays — with a rendered PDF skeleton in about 30 minutes. Its voice pipeline captures whose prose anchors your writing and applies it to drafts without changing your claims, while a tone lint catches the inflationary, self-praising patterns LLM-assisted academic writing tends to accumulate. Six commands: render, status, voice, guard, smooth, audit.
```
**Example use cases**
```
You're starting a thesis and want structure fast: scaffold a project and get a rendered PDF skeleton in about 30 minutes.
You want Claude to draft in your voice, not a generic one: /vibe-thesis:voice captures your anchors and /vibe-thesis:smooth applies them without altering claims or structure.
Your draft reads inflated: /vibe-thesis:guard flags self-praise and over-qualification with file:line suggestions.
You need it as a PDF: /vibe-thesis:vibe-render runs the Pandoc + xelatex pipeline and reports the manifest.
```

---

## thesis-engine

**Link to plugin**
```
https://github.com/estevanhernandez-stack-ed/Thesis-Engine
```
**Plugin homepage**
```
https://626labs.dev/thesis-engine/
```
**Plugin name**
```
thesis-engine
```
**Plugin description**
```
Research feeder for thesis and long-form writing. thesis-engine does the cold-start work before you can write: it scans a field for live, low-competition topics, gathers primary sources across five research axes, and emits research notes plus a BibTeX bibliography ready to drop into a thesis project. An optional stage adapts the same research into a Smart Brevity blog draft. Four commands across three stages: discover, write, run, and blog. Pairs with vibe-thesis — the engine feeds, the thesis tooling drafts.
```
**Example use cases**
```
You don't know what to write about: /thesis-engine:discover searches your field and ranks live, low-competition topics by novelty, thesis potential, and relevance.
You have a topic and need sources: /thesis-engine:write gathers primary sources across five axes and emits per-axis notes plus a BibTeX bibliography, with quality gates.
You want the whole cold start in one run: /thesis-engine:run does discovery and source-gathering into a thesis-ready folder.
You want a blog post out of the research: /thesis-engine:blog adapts a run folder into an 800–1,200 word Smart Brevity draft.
```

---

## vibe-taker

**Link to plugin**
```
https://github.com/estevanhernandez-stack-ed/vibe-taker
```
**Plugin homepage**
```
https://626labs.dev/vibe-taker/
```
**Plugin name**
```
vibe-taker
```
**Plugin description**
```
Move a feature between repos without copy-paste archaeology. vibe-taker captures a feature out of one codebase as a portable bundle — architecture sketch, contract surface, the AI prompts that built it, a verbatim source snapshot, and the gotchas — then plants it into another repo with stack-aware adaptation. It reads source autonomously and only asks you when the WHY can't be derived from the code; on plant it detects the target's stack and picks code-lift on a high match, spec-driven re-implementation on a low one, or declines a hard cross-language mismatch — always with a diff you confirm before anything is written. Three commands: capture, plant, list. Local-only by default; ~/.vibe-taker/library/ is the single source of truth.
```
**Example use cases**
```
You built a clean feature in one app and want it in the next: /vibe-taker:capture bundles it — source, contracts, the prompts that built it, and the gotchas — into a portable shelf entry.
You're starting a new repo and want a feature you already solved: /vibe-taker:plant detects the target stack and lifts the code on a high match or re-implements from the spec on a low one, always with a diff you confirm before anything is written.
You can't remember what's on your cross-repo shelf: /vibe-taker:list searches your library and flags near-duplicate captures with Jaccard hints.
You want a transplant that respects a different language: /vibe-taker:plant declines a hard cross-language mismatch instead of producing broken code.
```

---

## vibe-sec (pre-release — see warning above)

**Link to plugin**
```
https://github.com/estevanhernandez-stack-ed/vibe-sec
```
**Plugin homepage**
```
https://626labs.dev/vibe-sec/
```
**Plugin name**
```
vibe-sec
```
**Plugin description** (honest pre-release framing)
```
Security audit for the app your AI just shipped. vibe-sec scans vibe-coded apps for the predictable gaps AI prototyping leaves behind — secrets in source, sketchy auth, stale dependencies, open CORS — and scales every finding to your app's actual tier, so a missing rate limit is critical for a payment API and informational for a static site. Three layers: hygiene (auto-fixable), architecture, and threat modeling. The CLI secret scanner ships today via npm; the full Claude Code plugin is rolling out from the framework spec.
```
**Example use cases**
```
You vibe-coded an app and want to know what's insecure before you deploy: vibe-sec classifies the app and runs a three-layer audit — secrets, auth, dependencies — prioritized by your tier.
You want the obvious gaps fixed fast: high-confidence hygiene fixes (gitignore, security headers, secret removal) auto-apply; the rest come as guided templates.
You want a CI security gate: a tier-appropriate pass/fail check drops into a GitHub Action without configuration.
```

---

## Notes
- **Homepages** — the four pages from PR #10 (vibe-test, vibe-thesis, thesis-engine, vibe-sec) are live. **vibe-taker still needs a `626labs.dev/vibe-taker/` page built and deployed** — it wasn't in PR #10.
- **Names** — each is your own, distinctive, and matches the install id; no brand-ownership conflict.
- **Example use cases** — paste with real line breaks; the form's `\n` placeholder is just illustrating "one per line."
- **Repo casing** — vibe-thesis and thesis-engine repos use capitalized names (`Vibe-Thesis`, `Thesis-Engine`); the URLs above are correct as written.
- **Per-repo copies** — if you want each plugin's submission copy living in its own repo later, these blocks lift straight into each `docs/`.
