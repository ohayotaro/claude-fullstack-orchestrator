---
name: screen-build
description: Compose a feature screen / page from existing primitives, wired with state, navigation, and data fetching. Owned by ui-engineer. Use for feature-level UI work; for primitive design changes use /component-build.
---

# /screen-build

## Purpose

Take an approved screen design (from `/start-feature` or `/design-extract`) to a working screen in the project's stack. Composition only — relies on existing primitives from the design system; if primitives are missing, hand off to `/component-build` first.

## When to use

- New screen / page / route in any platform
- Significant feature surface change

## Steps

### 1. Confirm the design source

- Reference a screen schema (from `/design-extract`) or an approved spec
- Identify primitives needed; if any missing → `/component-build` first
- Confirm Zone B values that affect this screen: framework, styling, state lib, BFF, mobile platform

### 2. Compose the screen

Per Zone B platform:

- **Next.js (App Router)**: Server Component for the page; Client Components for interactive sub-trees marked `"use client"`. Data fetching in the Server Component; mutations via Server Actions or API client.
- **Vite / Remix**: route component + loader / action.
- **SwiftUI**: a `View` struct per screen, with `@State` / `@Observable` view model
- **Compose**: a screen-level composable with a `ViewModel` injected via Hilt / Koin
- **Flutter**: a `StatelessWidget` or `ConsumerWidget` (Riverpod) / `BlocBuilder` (Bloc)
- **React Native**: a screen component plus React Navigation registration

### 3. Loading / error / empty states

Explicit, never implicit:

- Loading: skeleton, spinner, or shimmer per design system
- Error: per error envelope; recoverable actions (retry, go back)
- Empty: helpful message with an action (create the first item, etc.)

### 4. State wiring

Per `/state-design` decision for this feature (or per Zone B defaults if standard):

- Server state via Zone B `state_lib.server` (TanStack Query etc.)
- Client state via Zone B `state_lib.client` (Zustand / @State / StateFlow / Riverpod)
- URL state via the router (filters, dialog visibility, page)

### 5. Navigation

- Web: route entry; deep link compatibility verified
- iOS: NavigationStack push or sheet; preserve state on backgrounding
- Android: Compose Navigation type-safe route; predictive back gesture handled
- RN: React Navigation route; lifecycle (focus / blur) handlers as needed
- Flutter: go_router route; URL strategy on web

### 6. A11y, perf, i18n

- A11y baseline per `common/accessibility.md` — keyboard / focus / contrast / screen-reader path
- Perf: list virtualization, image loading strategy, code splitting if applicable
- i18n: no hard-coded strings; use the project's localization layer

### 7. Tests

- Component test for the screen's deterministic states
- Integration / e2e for primary user flow
- Visual regression baseline (`/visual-verify`)

### 8. Wire to backend

If the screen consumes a new API → coordinate with `api-engineer` to ensure the contract is in place. Use the project's API client (generated from OpenAPI / SDL / proto, or hand-rolled per Zone B).

## Output

- Screen / page file(s)
- Route registration
- Tests (component + e2e + visual baseline)
- Wired state and data fetching

## Hand-off

- Visual verification → `/visual-verify`
- Cross-track review → `/team-review`
- Backend changes implied by the screen → `api-engineer` (`/api-build`) and `data-engineer` (`/data-design`) if schema impact

## Notes

- Do not introduce new primitives in this skill — that is `/component-build`'s job.
- Loading / error / empty are first-class states. Never ship without them.
