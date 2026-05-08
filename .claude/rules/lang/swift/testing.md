# Rule: Testing (Swift / iOS)

## Tools

- **XCTest** — base framework, broadly supported
- **Swift Testing** (Swift 6 / Xcode 16+) — newer, structured macros (`@Test`, `#expect`); use for new projects when toolchain supports
- **ViewInspector** — third-party, for SwiftUI view tree assertions
- **XCUITest** — e2e UI tests
- **swift-snapshot-testing** (pointfreeco) — snapshot / golden tests for views, layouts, JSON
- **Quick / Nimble** — BDD style; optional, project decision

## Unit principles

- Cover model logic, view models, services in unit tests
- Mock at boundaries (network, storage, time, location)
- Inject dependencies (constructor or environment) — no global singletons in tests
- Tests fast (<50ms) for true unit tests

## SwiftUI view tests

- ViewInspector to traverse the view tree and assert content
- Or snapshot tests with `swift-snapshot-testing` for visual stability
- Cover loading / error / empty / populated states explicitly

## UI tests (XCUITest)

- Page object pattern for screen abstraction
- Stable accessibility identifiers on key elements (`accessibilityIdentifier`)
- Test user flows, not implementation details
- Reset app state between tests (launch arguments / environment)

## Snapshot tests

- Baseline images committed (with care — review diffs in PRs)
- Generate per device size class as needed
- Re-record only when a visual change is intentional

## Async testing

- `XCTestExpectation` for legacy
- `await` async functions directly in tests (Swift 5.5+)
- Avoid `sleep` — use signals or expectations

## Performance

- `XCTMetric.applicationLaunch`, `XCTClockMetric`, `XCTMemoryMetric`
- Track regressions with baselines

## Coverage

- ≥70% line coverage for unit tests; critical paths ≥90%
- Enable in scheme settings; track per CI run
