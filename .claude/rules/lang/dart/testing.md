# Rule: Testing (Dart / Flutter)

## Tools

- **flutter_test** — widget tests, runs on Dart VM (fast, no device)
- **integration_test** — full-app e2e on device/emulator
- **mocktail** (preferred over mockito for null-safety ergonomics) for mocking
- **golden_toolkit** or `matchesGoldenFile` for golden / visual regression tests
- **bloc_test** (when using Bloc) for testing event → state transitions
- **riverpod ProviderContainer** with overrides for testing providers in isolation
- **patrol** (optional) for advanced e2e with native interactions

## Unit principles

- Pure Dart unit tests under `test/unit/` — no Flutter dependencies
- Mock at boundaries (network, storage, time)
- Inject dependencies — no global singletons in unit tests

## Widget tests

- `testWidgets` with `WidgetTester`
- `await tester.pumpWidget(...)` to render
- `await tester.pump()` for one frame; `await tester.pumpAndSettle()` to wait for animations to finish (avoid in long-running animations — use explicit pumps)
- `find.byType`, `find.text`, `find.byKey`, `find.byTooltip`, `find.byWidgetPredicate`
- Prefer `find.byKey(ValueKey(...))` for elements that may change text but have stable identity

## Riverpod testing

- `ProviderContainer(overrides: [...])` to substitute implementations
- `container.listen<State>(provider, (prev, next) { ... })` to assert state transitions
- For widgets: wrap with `ProviderScope(overrides: [...], child: ...)` in `pumpWidget`

## Bloc testing

- `bloc_test.blocTest<MyBloc, MyState>(...)` with `act`, `expect`, `verify`
- Asserts on emitted state sequence

## Integration tests

- `integration_test/` directory; runs on real device or emulator
- `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` at start
- Test golden user flows
- Use `flutter test integration_test` or Firebase Test Lab

## Golden tests

- Per device size + theme
- Baselines committed
- Re-record when intentional visual change is approved

## Async patterns

- Avoid `Future.delayed` and real-time waits — use `tester.pump(Duration(...))` for controlled time
- For streams: `expectLater(stream, emitsInOrder([...]))`

## Coverage

- Unit / widget ≥70%
- `flutter test --coverage` produces `coverage/lcov.info`
- Critical paths ≥90%
- Reports uploaded in CI
