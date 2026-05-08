# Rule: Flutter Patterns

Applies to Flutter UI code.

## Widget structure

- `StatelessWidget` by default; `StatefulWidget` only when local state is necessary
- `build(BuildContext context)` is pure: same input → same output, no side effects
- Composition over inheritance — small widgets composed into bigger ones
- Const constructors wherever data is compile-time known (significant perf win)

## State management (Zone B-driven)

- **Riverpod** (recommended for new projects): `Provider`, `NotifierProvider`, `AsyncNotifierProvider`; `AsyncValue<T>` for async state
- **Bloc / Cubit**: when project standardizes on it; clear separation of UI from logic
- **provider** (legacy `ChangeNotifier`): acceptable for small projects but Riverpod is the modern path
- **InheritedWidget**: use directly only for tightly-scoped configuration / theme contexts

## Side effects

- `initState` / `dispose` for lifecycle in StatefulWidget
- Riverpod: `ref.listen` for reactive side effects; `ref.read` inside callbacks
- Bloc: events drive state transitions; UI emits events, listens to states

## Navigation

- `go_router` (recommended) for deep linking, type-safe routes, and nested navigation
- `Navigator 2.0` (`Router` + `RouteInformationParser`) when go_router doesn't fit
- Avoid `Navigator.push` for new flows in apps that need deep linking

## Performance

- Wrap rebuilding-frequently widgets with `const` where possible
- `RepaintBoundary` for expensive subtrees that shouldn't repaint with siblings
- `ListView.builder` / `GridView.builder` for large lists; provide `itemExtent` when uniform
- Avoid `MediaQuery.of(context)` chains in hot paths — extract once
- Profile with DevTools Performance tab and Timeline

## Theming

- Material 3 (`useMaterial3: true`) by default
- `Theme.of(context)` for tokens; avoid hard-coded colors / sizes
- `ColorScheme` and `TextTheme` extended via `extensions` field for project tokens

## Accessibility

- `Semantics` widget for non-default-semantic content
- `tooltip:` on icon buttons
- `MergeSemantics` / `ExcludeSemantics` deliberately
- Test with TalkBack / VoiceOver
- Respect `MediaQuery.textScaleFactor` for typography

## Localization

- `flutter_localizations` + `intl` package
- ARB files for translations
- Avoid hard-coded user-facing strings

## Architecture

- Repository for data access (network, local DB, key-value)
- Service for cross-cutting concerns (auth, analytics)
- Riverpod / Bloc owns presentation state
- Pure data classes for models (consider `freezed` for immutable + sealed unions)

## Async UI

- `FutureBuilder` / `StreamBuilder` available but caution: rebuilds entire subtree
- Prefer Riverpod's `AsyncValue` or Bloc state with explicit loading/error/data
