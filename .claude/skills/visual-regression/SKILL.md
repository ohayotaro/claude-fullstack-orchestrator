---
name: visual-regression
description: Manage visual regression baselines across surfaces. Run after a change set that may affect visuals. Builds on /visual-verify per surface; this skill orchestrates the full sweep, decides accept / reject per diff, and updates baselines after user approval.
---

# /visual-regression

## Purpose

Where `/visual-verify` checks one surface, `/visual-regression` runs the full sweep across the project's visual surfaces, consolidates Gemini's diff verdicts, and shepherds baseline updates safely.

## When to use

- After significant UI changes across multiple screens
- After design system primitive changes (downstream surface verification)
- Before merging a release branch

## Prerequisites

- Visual capture infrastructure configured (Playwright + Gemini, or per-platform equivalents)
- Baselines stored at `e2e/<framework>/baseline/` or repo-equivalent paths
- `.claude/visual-regression.json` lists surfaces to capture

## Steps

### 1. Read the surface manifest

Load `.claude/visual-regression.json`:

```json
{
  "web": [
    {"name": "login", "url": "/login", "viewports": ["mobile", "desktop"]},
    {"name": "dashboard", "url": "/dashboard", "viewports": ["desktop"]},
    ...
  ],
  "ios": [{"name": "LoginScreen", "test": "LoginUITests.testLayout"}, ...],
  "android": [{"name": "LoginScreen", "test": "LoginScreenTest"}, ...],
  "flutter": [{"name": "LoginPage", "golden": "test/golden/login.png"}, ...]
}
```

### 2. Run capture per platform

- Web: Playwright per surface × viewport
- iOS: XCTest snapshot per surface
- Android: Compose UI Test or Roborazzi per surface
- Flutter: golden_toolkit per surface
- RN: Detox per surface

Save candidates to `.claude/logs/visual/<run-id>/<platform>/<surface>.png`.

### 3. Diff per surface (Gemini)

For each surface where a baseline exists, invoke `/visual-verify` with baseline + candidate.

For new surfaces, the candidate becomes a *proposed* baseline pending approval.

### 4. Aggregate verdicts

```
Surface          | Verdict | Confidence | Notes
-----------------|---------|------------|---------------------------
login (mobile)   | pass    | high       | -
login (desktop)  | review  | high       | typography drift in CTA
dashboard        | fail    | high       | header logo missing
```

### 5. Triage

- `pass`: continue
- `review`: present per-surface diff to user with description; user accepts (update baseline) or rejects (route to `/team-implement`)
- `fail`: route to `/team-implement` with specific surface + finding
- `confidence: low`: treated as `review` regardless of verdict

### 6. Update baselines on approval

User-approved `review` outcomes:
- Copy candidate to baseline path
- Commit with message describing the intentional visual change

### 7. Generate report

Output to `.claude/logs/reviews/visual-<run-id>.md`:
- Summary table
- Per-surface verdict + Gemini reasoning
- Updated baselines list

## Output

- Aggregated visual regression report
- Updated baselines (where user approved)
- Routing back to `/team-implement` for any `fail`

## Notes

- Baselines are commit-tracked. Never auto-update without user approval — visual regressions are easy to slip through silently.
- For surfaces with intentional flakiness (animations, dynamic content), document in `visual-regression.json` and use Gemini's "minor" severity tolerance.
- Cross-browser / cross-OS sweeps require multi-environment runners; the manifest can split surfaces by environment.
