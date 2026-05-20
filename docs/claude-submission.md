# vibe-iterate — Claude plugin directory submission

Copy-paste values for the submission form. Paste fields as-is (real line breaks where shown — never type literal `\n`).

## Form fields

**Link to plugin**
```
https://github.com/estevanhernandez-stack-ed/vibe-iterate
```

**Plugin homepage**
```
https://626labs.dev/vibe-iterate/
```

**Privacy policy**
```
https://626labs.dev/privacy
```

**Plugin name**
```
vibe-iterate
```

**Plugin description**
```
Post-ship product iteration for Claude Code. Pick a banner mode — feature-add, competitive, ux-polish, or bug-bash — or reach for a sidecar (radar, spy, scan-releases, rate, ship, upgrade). Every run ships one PR, regression-aware and small-diff-preferred. The agent keeps an "Atlas" of what you've shipped, considered, and cut across sessions, and stays current on your stack via context7 plus a weekly framework-release scan. Composes with vibe-cartographer when it's installed; works standalone when it isn't. No telemetry — Atlas data stays local.
```

**Example use cases**
```
You shipped v1 and don't know what to build next: /vibe-iterate:feature-add scans competitors, Product Hunt, and framework releases, scores the candidates, and ships the highest-impact feature as one PR.
A competitor shipped something loud: /vibe-iterate:competitive diffs their changelog against your product and closes the gap that actually matters — not blind parity.
Your app works but feels rough: /vibe-iterate:ux-polish walks your routes, components, and flows and tightens the weak spots by user-trust impact.
Users keep reporting the same bug: /vibe-iterate:bug-bash reads feedback.md, triages by severity × frequency × blast-radius, and fixes the loudest one.
```

## Notes

- **Plugin name** — `vibe-iterate` is your own name, distinctive, and matches the install id, so there's no brand-ownership conflict (the form warns against names you don't own).
- **Homepage** — `https://626labs.dev/vibe-iterate/` is live (PR #8, deployed). It's the dedicated landing page, the right thing for this field.
- **Example use cases** — the form placeholder shows `\n` between examples; that's just illustrating "one per line." Paste the block with real line breaks; don't type literal `\n`.
- **Description length** — it's ~5 sentences: clear and concrete without padding. If there's a character limit and it's too long, cut the last two sentences first (the context7 / compose-with-cart / telemetry bits) — the first three carry the core pitch.
- **Shorter description fallback** (if needed):
  ```
  Post-ship product iteration for Claude Code. Pick a banner mode — feature-add, competitive, ux-polish, or bug-bash — or a sidecar (radar, spy, scan-releases, rate, ship, upgrade). Every run ships one PR, regression-aware and small-diff-preferred, with an "Atlas" that remembers what you've shipped across sessions. No telemetry.
  ```

## Reference
- README: https://github.com/estevanhernandez-stack-ed/vibe-iterate
- Design spec: `docs/2026-05-04-vibe-iterate-design.md`
- Landing page: https://626labs.dev/vibe-iterate/ (built in the 626labs-hub repo)
