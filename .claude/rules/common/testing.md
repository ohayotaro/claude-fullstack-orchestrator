# Rule: Testing

## Pyramid

- **Unit**: many, fast, isolated
- **Component / contract**: medium count, partial integration
- **E2E**: few, slow, full-stack
- **Visual regression**: per UI change set, gated review

## Coverage

- Unit: ≥70% line coverage (project-tunable in Zone B)
- E2E: every primary user flow has at least one happy-path test
- Backend: every public endpoint has a contract test
- Mobile: golden screen flows have UI / integration tests

## Determinism

- **Flaky tests are quarantined and tracked**, never silenced silently
- Avoid wall-clock dependence; use injected clocks
- Avoid network dependence in unit tests; mock at boundaries
- Database tests use transactions or per-test schemas
- E2E tests run against a known seed dataset

## Visual regression

- Baselines stored with traceability (git LFS / object storage / committed in repo per project)
- New baselines reviewed (Gemini-driven via `/visual-verify`)
- Diff verdicts: pass / review / fail; `review` requires human approval

## Test tooling per stack (read Zone B `testing.*`)

- TS frontend: vitest or jest, RTL, Playwright
- TS backend: vitest or jest, supertest, Pact for contract
- Python backend: pytest, httpx for client, pytest-asyncio
- Swift: XCTest, ViewInspector for SwiftUI, XCUITest for e2e
- Kotlin: JUnit 5, Compose UI Test, Espresso for e2e
- Flutter: flutter_test, integration_test
- Cross-platform e2e: Detox (RN), Playwright (web)

## Hand-off

- Test authoring and triage: `qa-engineer`
- Visual diff judgment: `visual-analyst` (Gemini)
- Test failure root cause: `/codex-debugger` if non-trivial
