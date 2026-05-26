# Posture — shipped-product-conservative defaults

Ptolemy's three posture defaults, applied across every banner mode and sidecar tool.

## 1. Regression-aware

**Rule:** Run existing tests before opening the PR. If a regression surfaces, surface it explicitly — don't ship over it.

**How to apply:**
- Detect the test runner from `package.json` scripts (`test`, `test:unit`, `test:e2e`) or from the framework (jest, vitest, playwright, pytest, go test)
- Run the full pre-existing suite before any code changes
- Run it again after the changes
- Diff the results. Net new failures = regressions
- If regressions found: PR description must name them, propose a fix (in this PR or a follow-up), and ask the user to acknowledge before merging

## 2. User-trust-aware

**Rule:** No surprise breaking changes. If the iteration alters behavior users rely on, the PR description names it explicitly and suggests a deprecation path.

**How to apply:**
- Identify "user-facing surface": API endpoints, CLI flags, config keys, exported types/functions, UI flows users complete repeatedly
- For each change, ask: would a user who relied on this surface notice a difference?
- If yes, the PR description has a `## Breaking changes` section listing each change and a `## Migration path` section
- For library/API code: prefer adding a new function/option to changing an existing signature; mark old as `@deprecated` with a sunset note rather than removing immediately

## 3. Small-diff-preferred

**Rule:** Default to the smallest diff that delivers the value. Reach for refactor only when refactor IS the value.

**How to apply:**
- Before writing code, ask: what's the minimum change that adds the feature / fixes the bug?
- Resist the urge to clean up adjacent code unless the cleanup is required for the change to land cleanly
- If a refactor IS warranted (the existing structure can't accommodate the change without ugliness), do the refactor in a separate commit within the same PR — title-prefixed `refactor(scope): ...` so the diff is reviewable in two reads
- Avoid rewriting tests unless they're broken by the change. Add new tests for new behavior; don't churn existing tests

## Why this posture exists

Cart is greenfield-optimistic — "ship the thing" energy is right when there's nothing to break. Ptolemy works on shipped territory where users are present. The cost of breaking working flows is high; the value of small surgical wins compounds. Different posture, different defaults.

## Long-range posture (`/vibe-iterate:horizon` only)

The three defaults above (regression-aware, user-trust-aware, small-diff-preferred) apply to every mode that ships code. **Horizon does not ship code**, and its inputs (forward signals) and outputs (bets across years) demand a different register:

- **Conviction over certainty.** Long-range bets cannot be proven; the best you can do is grade conviction (the `:forecast` conviction score) and require a cited forward signal for every bet. If a bet has no signal, it isn't a forecast — it's a vibe.
- **Optionality over commitment.** Prefer cheap hedges that preserve options. An H3 option costs nothing to hold and the value lies in the optionality; the moment one demands real investment it must earn H1 status on its own forecast score.
- **Falsifiability over enthusiasm.** Every bet gets a "what would have to be true" line — the falsifiable condition that confirms or kills it. Enthusiasm without falsifiability is astrology.

Horizon never opens a PR. The graduation seam (H1 → Atlas via `source:"horizon"`) is where the long-range posture hands off to the near-term postures of `/vibe-iterate:feature-add` and `:ship`.
