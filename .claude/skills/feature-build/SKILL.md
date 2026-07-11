---
name: feature-build
description: PM intake for an end-to-end product feature spanning UI, API, and data layers.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Feature Build

Feature work is T2 by default. It is T3 if it changes auth flows, deletes or migrates data destructively, or requires a production deploy as part of delivery.

## Intake

- Record the user story, target surfaces (web/mobile), affected API endpoints, and data model impact.
- Capture design references (screenshots, Figma exports, competitor examples): Claude reads them directly and summarizes the intended visual outcome in the brief.
- Define non-goals: what adjacent surfaces stay untouched.
- Note contract boundaries crossed (API schema, DB migration, event schema, shared packages).

## Acceptance Checklist

- AC includes user-visible behavior stated as testable outcomes.
- AC includes API contract stability or an explicit versioned change.
- AC includes tests at the right layers (unit, component/contract, e2e happy path).
- AC includes screenshot/preview capture for visual acceptance of UI surfaces.
- AC includes accessibility criteria for new interactive UI.

## Delegation

Create the task brief and run `plan` before any implementation. Claude approves the Codex plan against user intent before implementation, performs visual acceptance on captured screenshots, and requires independent review before acceptance.
