---
name: api-build
description: PM intake for API endpoint or service work with contract-first acceptance criteria.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# API Build

API work is T2 by default (contract boundary). It is T3 if it changes auth requirements or requires production migration/deploy in the same task.

## Intake

- Record the resource, operations, API style (per Zone B), consumers, and whether the change is additive or breaking.
- Capture idempotency needs, pagination/filter/sort requirements, and auth requirement per endpoint.
- Note downstream schema impact; pair with `/data-design` when the DB changes.

## Acceptance Checklist

- AC includes a contract artifact (OpenAPI/SDL/proto) updated before implementation.
- AC includes edge validation and the standard error envelope.
- AC includes contract tests for every public endpoint plus key failure paths (auth, validation, not-found, conflict).
- AC includes observability: request-id logging and RED metrics on new handlers.
- Breaking changes: explicit version bump and documented client migration path.

## Delegation

Create the task brief and run `plan` before any implementation. Claude approves the contract design against user intent before implementation.
