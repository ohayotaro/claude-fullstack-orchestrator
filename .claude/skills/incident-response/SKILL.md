---
name: incident-response
description: PM intake for production incidents across frontend, backend, and infra, with Codex triage and gated mitigation.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Incident Response

Incidents are T3 by default when mitigation touches production (deploys, migrations, credentials); triage itself is T0/T1 read-only.

## Intake

- Record symptom, blast radius, affected surfaces (web/mobile/API/DB/queue), start time (UTC), and current user impact.
- Capture evidence paths: error tracker links, log excerpts (secrets scrubbed), 5xx rates, failing endpoints or screens.
- Declare what mitigation is pre-authorized by the user (rollback, feature flag off, scale up) and what requires a fresh approval.

## Acceptance Checklist

- AC includes restored service level with a measurable signal (error rate, latency, uptime check).
- AC includes root cause identified with evidence, or explicit `unknown` with a follow-up task.
- AC includes a regression guard (test, alert, or gate) for the failure mode.
- Post-incident notes saved to `.claude/docs/reviews/` for commit-worthy learnings.

## Delegation

Create the task brief and run read-only `plan` for triage first. Mitigation that mutates production follows the T3 flow: explicit user approval plus `deploy-gate` acknowledgment. Do not ask Codex to deploy; the user (or gated command) executes external actions.
