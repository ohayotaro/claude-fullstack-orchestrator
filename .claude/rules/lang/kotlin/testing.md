# Rule: Testing (Kotlin / Android)

## Tools

- **JUnit 5** preferred for new projects (Android needs Jupiter via plugin); JUnit 4 acceptable for legacy
- **Kotest** for expressive matchers / property tests (optional)
- **MockK** for mocking (Kotlin-aware, suspending function support)
- **Turbine** for `Flow` testing
- **coroutines-test** (`runTest`, `TestDispatcher`) for coroutine-aware tests
- **Compose UI Test** — `ComposeTestRule`, `onNodeWithText`, `performClick`
- **Espresso** — legacy or non-Compose UI tests
- **Robolectric** — JVM-side Android tests when full instrumentation is overkill
- **Macrobenchmark** — startup, scrolling, frame timing

## Unit principles

- One unit = one class / function / method
- Inject dependencies — no `Context` / framework singletons in pure unit tests
- Mock collaborators with MockK (`every { ... } returns ...`, `coEvery` for suspend)
- Tests fast (<50ms)

## Coroutine tests

- `runTest { ... }` from `kotlinx-coroutines-test` provides virtual time
- Inject a `TestDispatcher` (Standard or UnconfinedTestDispatcher) into ViewModels
- Replace `Dispatchers.Main` with `Dispatchers.setMain(testDispatcher)` in setUp / tearDown
- Avoid `Thread.sleep` and real-time dependencies

## Flow tests

- Turbine: `flow.test { awaitItem(); awaitComplete() }`
- Or `toList()` for terminal collection in tests
- Verify emissions, completion, errors

## Compose UI tests

- `composeTestRule.setContent { ... }` to mount the composable
- Query by semantics: `onNodeWithText`, `onNodeWithContentDescription`, `onNodeWithTag`
- Avoid relying on coordinates or implementation details
- Test interactions: `performClick`, `performTextInput`, `performScrollTo`

## Instrumented tests

- `androidTest/` source set
- Run on a device or emulator via `connectedAndroidTest` or Firebase Test Lab
- Reset state per test (clear shared prefs, room DB, in-memory data)

## Snapshot / golden tests

- Compose: Paparazzi (Square) for JVM-side rendering; or Roborazzi
- Commit baselines; review diffs

## Coverage

- Unit ≥70%; ViewModels and use cases ≥90%
- Coverage via JaCoCo for Android; Kover for Kotlin Multiplatform
- Reports uploaded in CI

## Test data

- Factory functions / builders over hard-coded fixtures
- Determinism: avoid `System.currentTimeMillis()`; inject a `Clock`
