---
name: e2e-test
description: PM intake for end-to-end test creation or extension in the project's runner.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# E2E Test

Test work is T1 for extending existing suites, T2 when introducing a runner or restructuring the suite.

## Intake

- Record the flows to cover (happy path + key failure paths), the runner (Zone B: Playwright/Detox/XCUITest/Espresso/integration_test), and the seed data strategy.

## Acceptance Checklist

- AC includes deterministic runs: known seed dataset, no arbitrary sleeps, auto-waiting or explicit signals.
- AC includes each primary user flow having at least one happy-path test.
- AC includes flaky tests quarantined and tracked, never silently skipped.
- AC includes CI integration with the suite green on the target revision.

## Delegation

Create the task brief and delegate via `/codex-task`.
