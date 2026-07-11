# Rule: Accessibility

Target: WCAG 2.2 AA (web) and platform-equivalent guidelines (iOS Accessibility, Android Accessibility, Flutter Accessibility).

## Mandatory baseline

- **Color contrast**: ≥4.5:1 normal text, ≥3:1 large text and UI components
- **Keyboard operability**: every interactive element reachable and operable; focus visible; no keyboard traps; logical tab order
- **Screen reader path**: primary flows verified with VoiceOver / TalkBack / NVDA or JAWS
- **Form labels**: programmatically associated; error messages announced and linked via `aria-describedby` (web) or platform analogue
- **Headings**: hierarchical, used for structure not styling
- **Landmarks** (web): main, nav, header, footer present and unique
- **Motion**: respect `prefers-reduced-motion` (web), Reduce Motion (iOS), Remove Animations (Android); no flashing >3Hz

## Native specifics

- **SwiftUI**: `accessibilityLabel`, `accessibilityHint`, `accessibilityValue`; Dynamic Type support; `accessibilityElement(children:)` for composed views
- **Compose**: `semantics` modifier; `contentDescription` for non-text content; large-text scaling tested
- **Flutter**: `Semantics` widget; `ExcludeSemantics` / `MergeSemantics` used intentionally

## Audit checklist

Run `/a11y-audit` to execute axe-core (web), Lighthouse, iOS Accessibility Inspector, Android Accessibility Scanner.

## Quality gates

- Lighthouse a11y ≥95
- Zero axe-core critical violations
- Keyboard-only flow verified for primary paths
- Screen reader paths verified for primary paths

## Ownership

All engineering work in this domain is delegated to Codex through a task brief (`/codex-task`, see `common/codex-delegation.md`). Claude captures the requirements above as acceptance criteria in the brief; Codex designs, implements, and validates them.
