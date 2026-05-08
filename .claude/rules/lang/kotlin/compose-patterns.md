# Rule: Jetpack Compose Patterns

Applies to Android UI written in Compose. Many patterns transfer to Compose Multiplatform.

## Composable structure

- Composables are functions; small and focused
- One concern per composable
- Stateless composables receive data + callbacks; stateful host owns state — **state hoisting**
- `@Composable` functions are pure: same input → same output (no side effects in body)

## State

- `remember { mutableStateOf(...) }` for local state
- `rememberSaveable { ... }` for state that survives configuration changes
- `collectAsStateWithLifecycle()` for `Flow`/`StateFlow` from a `ViewModel`
- ViewModel owns screen-level state; exposes `StateFlow<UiState>`
- `derivedStateOf { ... }` only when computation is expensive and inputs change less often than reads

## Side effects

- `LaunchedEffect(key) { ... }` — coroutine tied to composition; relaunches when key changes
- `DisposableEffect(key) { ... onDispose { ... } }` — for resources requiring cleanup
- `SideEffect { ... }` — fires on every successful composition; rare
- `produceState` — async state production
- `rememberCoroutineScope()` — when launching from a callback (not at composition)

## Modifiers

- Order matters; `Modifier.padding(8.dp).background(Color.Red)` differs from reverse
- Reuse modifier chains via top-level `val` for testability
- `Modifier.semantics { ... }` for accessibility (`contentDescription`, `role`, custom actions)

## Recomposition

- Mark stable types with `@Stable` / `@Immutable`
- Avoid passing unstable types (`List<T>`, lambdas without `remember`) where stability matters
- Inspect with Layout Inspector / `composeRecompositionEnabled = true` in Macrobenchmark

## Navigation

- Compose Navigation 2.8+ with type-safe routes (Kotlin serialization)
- `NavHost` at the screen graph root
- Avoid mixing Fragment-based navigation with Compose-only flows

## Architecture

- ViewModel + StateFlow + Compose: the de facto standard
- Repository for data access; UseCase optional based on project complexity
- DI via Hilt (default Android) or Koin (per Zone B)

## Accessibility

- `Modifier.semantics` on interactive elements that lack a default semantic role
- `contentDescription` for non-text visual content
- TalkBack tested for primary flows
- Large text scaling tested via `fontScale` in previews

## Previews

- `@Preview` for every reusable composable
- Multi-preview annotations (`@PreviewLightDark`, `@PreviewFontScale`) for state coverage
- Preview parameter providers for state variants

## Performance

- Macrobenchmark for app-startup, scroll perf
- Layout Inspector to spot unnecessary recompositions
- `LazyColumn` / `LazyRow` for large lists with stable `key`
- Avoid `Modifier.composed { }` in hot paths; prefer fused modifiers
