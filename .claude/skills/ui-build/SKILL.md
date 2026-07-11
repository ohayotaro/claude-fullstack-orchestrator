---
name: ui-build
description: PM intake for screen, component, or design-system work with visual acceptance criteria.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# UI Build

UI work is T1 when localized to one component; T2 when it spans screens, shared primitives, or design tokens (token changes ripple across all consumers).

## Intake

- Record target screens/components, platform (web/iOS/Android/Flutter), and whether shared design-system primitives or tokens change.
- Attach visual references; Claude describes the expected result in the brief (layout, states, responsive behavior).
- List required states: loading, empty, error, populated.

## Acceptance Checklist

- AC includes tokens over hard-coded values, and primitive composition over reaching past the design system.
- AC includes accessibility semantics (labels, roles, focus, contrast) for interactive elements.
- AC includes previews/stories for reusable components.
- AC includes screenshot capture per required state for Claude's visual acceptance.

## Delegation

Create the task brief and delegate via `/codex-task`. UI changes are not accepted until Claude has read the captured screenshots and judged render correctness (`/visual-verify`).
