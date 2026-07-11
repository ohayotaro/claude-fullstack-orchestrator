---
name: a11y-audit
description: PM intake for accessibility audits and remediation to WCAG 2.2 AA and platform equivalents.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# A11y Audit

Audit is T0/T1 (read-only + localized fixes); remediation across shared primitives is T2.

## Intake

- Record the surfaces in scope and the target: WCAG 2.2 AA (web), platform guidelines (iOS/Android/Flutter).
- Choose tooling per surface: axe-core, Lighthouse, iOS Accessibility Inspector, Android Accessibility Scanner.

## Acceptance Checklist

- AC includes zero critical axe-core violations and Lighthouse a11y >= 95 (web).
- AC includes keyboard-only operability and visible focus for primary flows.
- AC includes screen-reader path verification for primary flows (VoiceOver/TalkBack/NVDA).
- AC includes contrast >= 4.5:1 normal text, >= 3:1 large text and UI components.
- AC includes reduced-motion preferences respected.

## Delegation

Create the task brief and delegate via `/codex-task`. Codex runs the automated tools and fixes; manual screen-reader verification steps are listed in Required Validation and confirmed with the user when hardware is needed.
