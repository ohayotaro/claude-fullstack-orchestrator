# Rule: Testing (Frontend TS)

Applies to React, Next, Vite, Remix UIs.

## Tools (read Zone B `testing.unit` / `testing.component` / `testing.e2e`)

- **Unit / component**: vitest (preferred for Vite/Next 14+) or jest (jest required for some frameworks)
- **Component**: React Testing Library (RTL) + `@testing-library/user-event` (over fireEvent)
- **E2E**: Playwright (preferred) or Cypress
- **Visual regression**: Playwright screenshots judged by PM visual acceptance via `/visual-verify`

## Component testing principles

- Test behavior, not implementation. Query by accessible role / label / text, not test-id (test-id only as last resort).
- `userEvent` over `fireEvent` — closer to real user interaction.
- Mock at boundaries (network, timers, navigation), never module internals.
- Avoid snapshot tests for dynamic UI; use them sparingly for stable serialized output.

## Async patterns

- `findBy*` queries for elements that appear after async work
- `waitFor` for non-DOM assertions
- Avoid arbitrary `setTimeout` waits

## E2E principles

- Tests run against a known seed dataset
- One assertion per behavior, but multiple steps to reach it
- Use Playwright's auto-waiting; avoid manual `waitForTimeout`
- Run tests against multiple browsers when the surface is browser-sensitive

## Coverage

- Unit/component: ≥70% line (Zone B can override)
- Critical paths: e2e coverage required
- Coverage reports uploaded in CI

## Mocking

- MSW (Mock Service Worker) for HTTP in component tests
- `vi.mock` / `jest.mock` only for module-level needs
- Avoid mocking React internals or framework primitives

## Fixtures

- Co-locate fixtures with the test where possible
- Shared fixtures live in `test/fixtures/` or per-feature `__fixtures__/`
- Factory functions over static blobs for variants
