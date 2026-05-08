---
name: visual-verify
description: Verify UI render correctness via screenshot capture (Playwright / Detox / XCTest / flutter integration_test) and Gemini-driven visual diff against a baseline. Run after UI changes; Gemini returns structured verdict (pass / review / fail) with confidence. UI changes are not "done" until /visual-verify passes or the user approves a diff.
---

# /visual-verify

## Purpose

Bridge the gap between "code compiles and tests pass" and "the UI actually looks right." Captures a screenshot of the changed surface, sends it to Gemini for diff judgment against a baseline, and surfaces the verdict.

## When to use

- After every UI feature change
- After design-system primitive changes (validate downstream surfaces did not break)
- Before declaring a UI task complete

## Prerequisites

- The relevant testing tool is installed (Playwright / Detox / XCTest / flutter integration_test)
- A baseline image exists, or this is the first capture (which becomes the new baseline pending approval)

## Steps

### 1. Identify the surface to capture

From the change set or user request, determine which routes / screens / components to screenshot.

### 2. Capture screenshots

Use the framework declared in Zone B `testing.e2e` / `testing.visual`:

| Stack | Capture method |
|---|---|
| Web | Playwright `page.screenshot()` per viewport size declared in `visual-regression.json` |
| iOS native | XCTest `XCUIScreenshot.image` |
| Android native | Compose UI Test or Espresso `takeScreenshot()` |
| React Native | Detox `device.takeScreenshot()` |
| Flutter | integration_test `binding.takeScreenshot()` or golden_toolkit |

Save under `.claude/logs/visual/<feature>/<surface>/<timestamp>.png`.

### 3. Compare to baseline

Locate baseline at `e2e/<framework>/baseline/<surface>.png` (or repo-equivalent path). If no baseline, the candidate becomes the proposed baseline pending approval.

### 4. Delegate diff judgment to Gemini

Invoke `/visual-verify` Gemini-side flow (under `.gemini/skills/visual-verify/`) with:

- Path to baseline
- Path to candidate
- Description of what changed (from change set context)
- Tolerance hints (font rendering jitter is minor; layout shift is major)

Gemini returns the structured diff JSON:

```json
{
  "task": "visual-verify",
  "baseline": "...",
  "candidate": "...",
  "regions_changed": [
    {"bbox": [x, y, w, h], "severity": "major|minor", "description": "..."}
  ],
  "verdict": "pass | review | fail",
  "confidence": "high | medium | low",
  "human_approval_required": ["..."]
}
```

### 5. Act on verdict

- `pass`: continue
- `review`: present diff regions to the user with explanation; ask whether to accept (update baseline) or reject (route back to `/team-implement`)
- `fail`: route back to `/team-implement` with the diff regions as context
- `confidence: low`: always treat as `review` regardless of verdict

### 6. Update baseline (only on user approval)

When the user approves a `review` outcome, copy the candidate to the baseline path and commit with a message describing the intentional visual change.

## Output

- Diff result JSON saved under `.claude/logs/visual/`
- Updated baseline (if approved)
- Verdict surfaced to user

## Notes

- Diff judgment is Gemini's strength; the orchestrator should not eyeball diffs without Gemini's structured output.
- For multi-platform UIs, run capture per platform and verify each separately.
- Visual regression baselines are version-controlled or referenced via stable paths — never ad-hoc.
