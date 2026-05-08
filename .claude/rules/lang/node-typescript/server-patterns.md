# Rule: Node-TS Server Patterns

Applies to Hono / Fastify / NestJS / Express / serverless handlers. Read Zone B `backend_framework`.

## Middleware ordering (general)

1. Request id / correlation id assignment (or extraction from header)
2. Logger
3. Tracing (OpenTelemetry)
4. CORS
5. Rate limit (when applicable)
6. Body parser (only when needed)
7. Auth middleware
8. Route handler
9. Error handler (terminal)

## Validation at edge

- Validate every inbound payload before passing into the handler logic
- `zod` / `valibot` / `typebox` schemas, parsed in middleware or per-route
- Validation failure returns the standard error envelope with `code: "validation_error"`

## Handler structure

- Handler is a thin shell: parse → call service → format response
- Business logic in services, not handlers
- Repositories isolate data access from services

## Async error handling

- **Hono**: `c.error` / `app.onError`
- **Fastify**: per-route `errorHandler` or global `setErrorHandler`
- **NestJS**: filters / interceptors
- **Express**: `next(err)` chain — wrap async handlers (e.g., `express-async-errors`) or use `try/catch`

## Response shape

- Success: per resource schema
- Error: standard envelope (`common/api-contracts.md`)
- HTTP status code matches semantic outcome (200/201/204/400/401/403/404/409/422/429/500/503)

## Logging

- Structured JSON via pino or framework logger
- Per-request log includes `request_id`, `method`, `path`, `status`, `latency_ms`, `user_id` (when authorized)
- No PII / secrets in logs unless explicitly justified

## Database access

- Connection pool tuned per Zone B `database` engine
- Transaction boundaries explicit; one transaction per logical unit of work
- ORM patterns per Zone B (`orm_or_driver`): Prisma, Drizzle, TypeORM, Kysely, raw

## Background work

- HTTP handlers do not perform long async work — enqueue to a job (per `common/data-modeling.md` and the `job-engineer` patterns)
- Fire-and-forget is forbidden; use a queue with at-least-once delivery

## Graceful shutdown

- SIGTERM / SIGINT handler closes server, drains active requests, closes DB / queue connections, then exits
- Health check returns NOT-READY during drain
