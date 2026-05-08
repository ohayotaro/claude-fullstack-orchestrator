---
name: e2e-test
description: Generate or extend end-to-end tests in the project's chosen runner — Playwright (web), Detox (RN), XCUITest / XCTest (iOS), Espresso / Compose UI Test (Android), flutter integration_test (Flutter). Owned by qa-engineer with Codex for non-trivial scenarios.
---

# /e2e-test

## Purpose

Cover primary user flows with deterministic, runnable e2e tests using the project's declared tooling.

## When to use

- New primary user flow lacking e2e coverage
- After a feature change that affects an existing flow
- Pre-release sweep adding regression tests for past incidents

## Inputs

- The feature / flow to cover (description or list of steps)
- Zone B `testing.e2e` (the runner) and platform list

## Steps

### 1. Identify the runner per platform

Read Zone B:

- Web → Playwright (preferred) or Cypress
- iOS → XCUITest
- Android → Espresso (legacy) or Compose UI Test
- React Native → Detox
- Flutter → integration_test (with patrol for advanced needs)

### 2. Define the scenario

For each user flow:

- Preconditions (seed data, auth state, feature flags)
- Steps (user actions in order)
- Expected outcomes (assertions)
- Cleanup

Write these as a brief specification before code.

### 3. Generate test scaffolds

Page object pattern (or screen object on mobile) — encapsulate selectors and flows away from the test body.

Web (Playwright):

```ts
import { test, expect } from "@playwright/test";

test("login: happy path", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("user@example.com");
  await page.getByLabel("Password").fill("correct-horse-battery-staple");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL("/dashboard");
  await expect(page.getByRole("heading", { name: "Welcome" })).toBeVisible();
});
```

Mobile (Detox / XCUITest / Espresso / integration_test): equivalent page-object pattern.

### 4. Cover failure paths

Beyond happy path:
- Auth failure
- Validation failure
- Network timeout
- Not-found / forbidden / conflict
- Empty state and error state per surface

### 5. Determinism rules

- Tests run against a known seed dataset
- Avoid `waitForTimeout` / hard-coded sleeps; use auto-waiting (Playwright) or polling assertions
- Avoid wall-clock dependence; freeze time in the app or test where applicable
- IDs are deterministic (UUIDs from a seed)

### 6. Codex review for complex scenarios

When a flow has many branches or non-obvious failure modes, send the specification to Codex. Output standard contract; Codex flags missed edge cases.

### 7. Run and stabilize

- Run locally; iterate on flakies
- Run on CI; quarantine if flakes appear (track in a flaky-test list, do NOT silence)
- Tag with `@smoke` for pre-deploy run

### 8. Persist

Tests live alongside the project's e2e directory. Add an entry in the `e2e/README.md` (if maintained) describing the new flow.

## Output

- Test files in the e2e directory
- Page / screen objects updated
- Documentation entry (if maintained)

## Hand-off

- New visual surface created during the test → `/visual-regression` to add baselines
- Test reveals a real bug → `/codex-debugger` for root cause
- Coverage gap identified beyond the scope → backlog

## Notes

- E2E tests are slow and expensive. Cover primary flows comprehensively, not every variation.
- Per platform, the testing tool is set in Zone B — do not deviate without project agreement.
- A flaky test is a quality signal. Investigate; don't silence.
