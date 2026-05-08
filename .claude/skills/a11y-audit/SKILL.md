---
name: a11y-audit
description: Run accessibility audits across the project's surfaces. Targets WCAG 2.2 AA on web + native a11y guidelines on iOS / Android / Flutter. Owned by a11y-auditor. Combines automated tools (axe-core, Lighthouse, iOS Accessibility Inspector, Android Accessibility Scanner) with manual checklist guidance.
---

# /a11y-audit

## Purpose

Verify and remediate accessibility against WCAG 2.2 AA (web) and platform-equivalent guidelines (iOS, Android, Flutter). Combines automated tooling with manual checks for items that automation cannot catch.

## When to use

- New feature with user-facing UI
- Before merging a non-trivial UI change
- Periodically (release cadence) for full-app sweep

## Steps

### 1. Determine scope

- File-level: changed files in current diff
- Surface-level: affected screens / pages / flows
- Project-level: full sweep (use sparingly; expensive)

### 2. Run automated tools per platform

#### Web
- **axe-core** via Playwright integration: scan each surface, collect violations
- **Lighthouse a11y category**: target ≥95
- Color contrast: verified at runtime (axe rule + manual)

#### iOS
- **Xcode Accessibility Inspector** on every primary surface
- Audit for: missing labels, contrast, hit-target size, Dynamic Type support
- VoiceOver path test on primary flows (manual)

#### Android
- **Accessibility Scanner** (Google) on every primary surface
- Audit for: contentDescription gaps, contrast, target size, focus order
- TalkBack path test on primary flows (manual)

#### Flutter
- `flutter test --accessibility` for widget-level a11y
- Manual TalkBack / VoiceOver on integration_test surfaces

### 3. Manual checklist per surface

- **Keyboard** (web): every interactive element reachable; no traps; logical tab order; focus visible
- **Screen reader**: primary flow operable with eyes closed
- **Color contrast**: 4.5:1 normal, 3:1 large; verified with token values
- **Motion**: respects `prefers-reduced-motion` / Reduce Motion / Remove Animations
- **Forms**: labels associated; errors announced; helpful descriptions
- **Headings**: hierarchical (no skips); landmarks present (web)

### 4. Categorize findings

```
### Critical (block merge)
- file:line — WCAG criterion — finding — fix proposal

### Major (resolve before merge or explicitly defer)
- ...

### Minor (track)
- ...
```

### 5. Remediation hand-off

For each finding, route:
- Primitive-level fix (affects all consumers) → `design-system-engineer`
- Feature-level fix (this screen only) → `ui-engineer`
- Copy / wording fix → user (i18n-aware)

### 6. Verify after fix

Re-run the automated tools on the affected surfaces. Critical findings must move to "resolved" before merge.

### 7. Persist report

Save to `.claude/logs/reviews/a11y-<run-id>.md` for history.

## Output

- Findings list (Critical / Major / Minor)
- Verdict: `pass | review-required | block`
- Lighthouse a11y score (if web)

## Quality gates

- Lighthouse a11y ≥95 (web)
- Zero axe-core critical
- Keyboard-only operability for primary flows
- Screen reader path verified for primary flows
- All ARIA / native a11y attributes accurate

## Notes

- Automated tools catch about 30-50% of WCAG issues; manual review is required for the rest (especially semantics, motion, focus management, screen-reader experience).
- A finding that conflicts with a design decision is escalated to the user — do not silently override design.
