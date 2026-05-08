---
name: component-build
description: Build a single design-system component (primitive or composed) with preview/storybook entry, a11y semantics, and tests. Owned by design-system-engineer. Use for design system layer changes; for feature-screen composition use /screen-build.
---

# /component-build

## Purpose

Create or evolve a single component in the design system layer. Produces the component, its preview / storybook entry, and tests in one pass. Reads `common/design-system.md` and the active lang rules.

## When to use

- New primitive (Button, Input, Card variant, etc.) that does not exist
- Significant change to an existing primitive (new variant, prop, or behavior)
- Cross-platform component when Zone B includes multiple platforms

Skip when:
- The work is feature-screen composition → `/screen-build`
- Tokens-only change (no component) → directly edit token files via `design-system-engineer`

## Steps

### 1. Confirm the contract

Define before coding:
- Component name
- Props (with types, defaults, required vs optional)
- Variants (semantic, e.g., `intent: primary | secondary | danger`)
- Sizes / shapes / states (hover, focus, disabled, loading)
- A11y guarantees (semantic role, keyboard support, screen-reader behavior)
- Composition surface (children-as-content vs explicit slots)

If novel: request Codex review (severity: warn) for the contract before coding.

### 2. Implement

Per Zone B framework (read CLAUDE.md):

- React / Next: typed FC with `forwardRef` if it forwards to a DOM node; CSS via Zone B styling (Tailwind / vanilla-extract / CSS Modules)
- SwiftUI: `View` struct with parameters; modifier-style API for variants when sensible
- Compose: `@Composable fun` accepting a `Modifier` parameter and stable types
- Flutter: `StatelessWidget` (or `StatefulWidget` if internal state needed); const constructor

### 3. A11y baseline (always)

- Semantic role (button / link / heading / region / etc.)
- Focus visible
- Color contrast verified against tokens
- Keyboard support (Enter/Space activate; Esc to dismiss for overlays)
- ARIA attributes for the framework's analogue (jsx aria-*, SwiftUI accessibility*, Compose semantics, Flutter Semantics)

### 4. Preview / Storybook entry

- React: Storybook `*.stories.tsx` with at least: default, all variants, disabled state, dark mode, edge content
- SwiftUI: `#Preview` per state including Dynamic Type and dark mode
- Compose: `@Preview` per state including font scale and theme
- Flutter: widget book or per-state golden test

### 5. Tests

- Unit / component test per `common/testing.md` (RTL, ViewInspector, Compose UI Test, flutter_test)
- A11y test (jest-axe / iOS Accessibility Audit / Compose semantics test)
- Visual regression baseline if applicable (`/visual-regression`)

### 6. Document the prop contract

- TSDoc / Swift doc / KDoc / Dart doc on the public API
- Storybook controls or preview parameters reflecting the prop surface

### 7. Update the component index

If the project exposes a barrel export (`packages/ui/index.ts` or equivalent), add the new component.

## Output

- Component file(s)
- Preview / story
- Tests
- Updated index (if applicable)
- A11y audit pass (axe / inspector)

## Hand-off

- Feature surfaces consuming this component → `ui-engineer` (`/screen-build`)
- Token changes implied by the component → `design-system-engineer` (token PR, separate)
- Visual regression sweep on consumers → `/visual-regression`

## Notes

- Avoid `style` / `className` escape hatches in feature code; if a primitive cannot express what's needed, extend the primitive's API.
- Cross-platform parity: same primitive name behaves consistently across web / iOS / Android when applicable. Document any intentional divergence.
