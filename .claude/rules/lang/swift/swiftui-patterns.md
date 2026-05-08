# Rule: SwiftUI Patterns

Applies to SwiftUI on iOS 17+ (default) and other Apple platforms.

## View composition

- Decompose mega-Views into small views; views are cheap
- Each view should fit on a screen; extract subviews when readability suffers
- Pass data down via `let` properties; lift state up via bindings

## State property wrappers (iOS 17+, Observation framework)

- `@State` — local view-owned state for value types (or `@State var observable: SomeObservable` for `@Observable` types)
- `@Binding` — two-way reference to state owned elsewhere
- `@Environment` — read environment values / observed objects from ancestor
- `@Observable` — replaces `ObservableObject` for new code; auto-tracking on access
- `@Bindable` — bind to `@Observable` instances when needed

## Legacy (pre-iOS 17)

- `@StateObject` for owned reference type
- `@ObservedObject` for injected reference type
- `ObservableObject` + `@Published` for class-based view models

## View identity

- View identity drives state preservation; understand `id()` modifier
- Lists: provide stable `id` via `Identifiable` or explicit `id:` parameter

## Lifecycle and async

- `task { ... }` view modifier for async work tied to view lifetime — auto-cancels when view leaves
- `onAppear` / `onDisappear` for lighter signals
- Avoid `Task { }` orphans inside body — they outlive the view

## Navigation (iOS 16+)

- `NavigationStack` with `NavigationPath` for type-safe deep linking
- `navigationDestination(for:)` keyed by value type
- Avoid `NavigationLink(destination:)` for new code; prefer value-based push

## Architecture

- For small / medium views: View + `@Observable` view-model pair is sufficient
- For complex flows: TCA (The Composable Architecture) when the project standardizes on it (per Zone B)

## Accessibility

- `accessibilityLabel`, `accessibilityHint`, `accessibilityValue` per interactive view
- Dynamic Type respected (use `.font` with text styles, not fixed sizes)
- Reduce Motion / Reduce Transparency respected via `@Environment` flags

## Previews

- Every reusable view ships with a `#Preview`
- Preview multiple states (loading, empty, error, populated)
- Preview Dynamic Type, dark mode, accessibility size when relevant

## Performance

- Profile with Instruments (Time Profiler, Hangs, SwiftUI)
- Avoid expensive computation in `body`; cache via `@State` or pre-compute
- `@Observable` tracks property access — avoid reading unrelated properties in views
