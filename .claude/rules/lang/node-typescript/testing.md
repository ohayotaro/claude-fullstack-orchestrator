# Rule: Testing (Node-TS Backend)

## Tools (read Zone B `testing.backend_unit` / `testing.e2e`)

- **Unit**: vitest or jest
- **HTTP integration**: supertest (Express/Fastify), Hono's built-in `app.request`, NestJS Testing module
- **Contract**: Pact, Spectral for OpenAPI lint, schema-driven tests
- **Mocks**: MSW for outbound HTTP; `@databases/pg-test` or testcontainers for real DB; ioredis-mock or testcontainers for Redis

## Unit principles

- One unit = one service / utility / pure function
- Mock at boundaries (DB, HTTP, queue); don't mock the unit's internals
- Fast: <10ms per unit test

## Integration principles

- Run against a real DB instance (testcontainers / docker-compose / per-test schema) when feasible
- Per-test transaction rolled back, OR per-test schema dropped
- Avoid sharing mutable state across tests

## Contract tests

- Provider tests verify the API matches the OpenAPI / GraphQL SDL
- Consumer tests (Pact) capture expected responses; provider verifies
- Required for any service consumed by other services

## E2E principles

- Run against the full app started in test mode
- Seed data via factories
- Verify happy path AND key failure paths (auth, validation, not found, conflict)

## Coverage

- Unit ≥70%, critical service paths ≥90%
- Coverage uploaded in CI

## Test data

- Factory functions (`makeUser({ overrides })`) over static fixtures
- IDs deterministic per test (avoid relying on auto-increment ordering)

## Async patterns

- Avoid `setTimeout` waits — use awaitable signals (event emitters, promises returned from the unit)
- Test timeouts explicit and short
