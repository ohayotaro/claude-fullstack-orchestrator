# Rule: Design System

Applies to all UI work, all platforms.

## Principles

- **Tokens are the single source of truth**. Color, typography, spacing, radius, motion, elevation. Hard-coded values in feature code are a violation.
- **Primitives compose into features**. Feature code consumes primitives (Box / Stack / Text / Button / Input / etc.); it does not reach past them to underlying styling APIs.
- **A11y is built into primitives**, not bolted on. Focus visible, semantic role, contrast verified by default.
- **Cross-platform parity** when Zone B has multiple platforms: the same primitive name behaves consistently across web / iOS / Android.

## Token rules

- Naming follows semantic intent (`color.text.primary`) over visual description (`gray-700`)
- Adding or changing a token requires Codex review (severity: warn) because it ripples across all consumers
- Tokens are declarative data, not code

## Primitives rules

- Every primitive ships with a preview / story / Snapshot
- Prop contracts documented and stable
- Escape hatches (`style`, `className`) are last resort; first try to extend the primitive

## Hand-off

- Token / primitive changes: `design-system-engineer`
- Feature surface composition: `ui-engineer`
- Visual reference analysis: `visual-analyst` (Gemini)
