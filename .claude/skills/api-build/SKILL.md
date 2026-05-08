---
name: api-build
description: Design and implement an API endpoint or service. Phase 1 designs the contract with Codex review, Phase 2 implements the handler / validation / error envelope, Phase 3 adds tests and observability. Operates in BFF mode when Zone B backend_scope=bff-only; full-backend mode otherwise.
---

# /api-build

## Purpose

Take a feature requirement to a deployable, observable, tested API surface. Owned by `api-engineer`. Codex CLI provides architectural and contract review.

## When to use

- New endpoint / service / RPC method
- Significant change to an existing contract (breaking or non-breaking)
- BFF aggregation endpoint for a frontend feature

## Mode

Read Zone B `backend_scope`:

- `bff-only`: BFF mode — optimize for frontend consumption; no separate consumer audience
- `full-backend`: service mode — durable contract, version with care

## Steps

### Phase 1 — Contract design

#### 1.1 Read context

- Zone B: `api_style`, `backend_framework`, `backend_languages`, `auth_mode`
- Existing contract artifacts (OpenAPI / SDL / proto) for consistency

#### 1.2 Draft contract

- Path / operation name
- Request shape (path params, query, headers, body) with types
- Response shapes per status code (success + error envelope per `common/api-contracts.md`)
- Auth requirement (or explicit public marker)
- Idempotency requirement (mutations with side effects)
- Rate limit / quota note if applicable
- Pagination / filter / sort if applicable

#### 1.3 Codex review (foreground, severity: warn via hook)

Send the contract draft to Codex for review:
- Consistency with existing patterns
- Validation gaps
- Auth / authz considerations (cross-check with `auth-security-engineer`)
- Schema impact (cross-check with `data-engineer`)
- Versioning / deprecation impact (full-backend mode)

Codex returns a structured review. Resolve critical / major findings before Phase 2.

#### 1.4 Persist contract artifact

- OpenAPI: `apis/openapi.yaml` (or per-service equivalent)
- GraphQL: `apis/schema.graphql`
- gRPC: `apis/proto/*.proto`
- Custom: per project convention

### Phase 2 — Implementation

#### 2.1 Handler structure (per Zone B `backend_framework`)

Thin handler: parse → validate → call service → format response. Business logic in services; data access in repositories.

#### 2.2 Validation

Edge validation per `common/api-contracts.md`:
- Schema-driven (zod / Pydantic / typebox)
- Reject early
- Validation errors map to standard error envelope

#### 2.3 Error envelope

Consistent shape, machine-readable code, human-readable message, request id.

#### 2.4 Auth wiring

Per Zone B `auth_mode`. Use the framework's idiomatic mechanism (FastAPI `Depends`, Hono middleware, NestJS guards). No bespoke auth in handlers.

#### 2.5 Logging and tracing

Structured log per request: request_id, method, path, status, latency_ms, user_id (if authorized). OpenTelemetry span with consistent name.

### Phase 3 — Tests and observability

#### 3.1 Unit tests

- Service-level tests with mocked repositories
- Validation edge cases

#### 3.2 Integration / contract tests

- Real DB via testcontainers / per-test schema
- Provider tests verify the OpenAPI / GraphQL contract matches implementation
- Pact consumer tests when other services consume this API

#### 3.3 E2E

Cover happy path + auth failure + validation failure + not-found + conflict.

#### 3.4 Observability hooks

- Metrics: RED (rate, errors, duration) per endpoint
- Trace span attributes: status, error code, business outcome
- Alerting threshold declared (per Zone B SLO)

## Output

- Contract artifact updated
- Handler / service / repository code
- Tests
- Logging / tracing instrumentation
- Codex review record (saved if non-trivial)

## Hand-off

- DB schema changes → `data-engineer` (`/data-design`)
- Auth flow design → `auth-security-engineer` (`/auth-design`)
- Background work triggered → `job-engineer` (`/job-design`)
- Deploy → `infra-engineer` (`/deploy` or `/infra-review`)

## Notes

- For BFF mode, the contract may be tightly coupled to the consuming UI — that's fine; document the consumer.
- For full-backend mode, the contract is multi-consumer; breaking changes require explicit version handling.
