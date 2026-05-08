---
name: architecture-review
description: Dedicated review of state, navigation, package boundaries, and service boundaries against the change set. Codex CLI provides deep reasoning. Surfaces contract drift and structural issues that other review tracks (security/quality/a11y/perf) tend to miss.
---

# /architecture-review

## Purpose

Catch architectural drift early — boundary violations, contract drift, dependency direction inversions, premature globalization, and "just one more parameter" creep.

This skill complements `/team-review` (which includes architecture as one of five tracks) and can also run standalone when a more focused review is needed.

## When to use

- After significant cross-module work (`/team-implement` touched 3+ packages)
- Before a major version bump
- After a refactor proposal
- As a standalone check between feature work

## Lenses

### 1. Package / module boundaries

- Are dependencies flowing in the intended direction?
- Are public APIs at boundaries minimal and stable?
- Is a "just import it" sneaking past intended boundaries?
- For monorepo: is `packages/api/` only consumed by intended apps?

### 2. State boundaries

- Is global state introduced where local / URL / server cache would work?
- Are state slices cohesive (single owner) or scattered?
- Are optimistic updates reconciled correctly?

### 3. Navigation boundaries

- Routes are typed
- Deep link table consistent across platforms
- Navigation does not leak business logic
- Lifecycle (focus / blur, foreground / background) handled at the right level

### 4. Service boundaries (full-backend mode)

- Is a service boundary justified by team / scaling / domain?
- Are cross-service contracts versioned?
- Are sync calls where async would be safer (queue, event)?

### 5. Contract drift

- API contract artifact (OpenAPI / SDL / proto) matches the implemented handler
- Generated client types match the contract
- DB schema matches the ORM models
- Event schemas match producer + consumer expectations

## Steps

### 1. Determine scope

`git diff` against the merge base. List all files touched, plus their downstream consumers (via grep).

### 2. Run focused queries per lens

For each lens above, formulate a specific question and answer it from the code. Examples:

- "Did this PR introduce a `packages/ui` import in `services/api/`? (it shouldn't)"
- "Is `apps/web/api/auth/route.ts` matched in `apis/openapi.yaml`?"
- "Does the new event payload in `services/orders/events.ts` match the consumer in `services/notifications/handlers.ts`?"

### 3. Codex review

Send the change set + lens findings to Codex (template in `CODEX_HANDOFF_PLAYBOOK.md` → "Architecture review"):
- Boundary violations
- Contract drift
- Dependency direction issues
- Architectural smell (god objects, overly broad APIs, missing abstractions for genuine duplication)

Codex returns the standard contract format.

### 4. Consolidate findings

Output:

```
## Architecture review
### Critical (blocks merge)
- file:line — finding — recommendation
### Major (resolve before merge or explicitly defer)
- ...
### Minor (track)
- ...
### OK / Notes
- structural decisions deliberately preserved
```

### 5. Hand off

- Boundary violations → original implementing agent (e.g., `ui-engineer`, `api-engineer`)
- Contract drift → `api-engineer` (`/api-build`) for surface; `data-engineer` (`/data-design`) for schema
- Service boundary questions → escalate to user

## Output

- Consolidated architecture review (in conversation or `.claude/logs/reviews/`)
- Verdict: `pass | review-required | block`

## Notes

- This skill does NOT duplicate `/team-review` work. Run it standalone when there is a focused architectural concern, or as part of `/team-review`'s 5th track.
- "We always did it this way" is not a justification — preserve intentional structure with a stated rationale; flag accidental drift.
