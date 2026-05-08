# Rule: Observability

Three pillars: logs, metrics, traces. Plus health checks and error budgets.

## Logging

- **Structured JSON** in production. No `print` / `console.log` debug left in.
- **Correlation IDs**: request id propagated end-to-end (HTTP header `X-Request-Id` or W3C `traceparent`)
- **Log levels** used intentionally: error / warn / info / debug
- **No secrets, no PII** in logs unless explicitly justified and access-controlled
- **Context fields**: at minimum `request_id`, `user_id` (when authorized to log), `endpoint`, `latency_ms`, `status`

## Metrics

- **RED** (request-driven): Rate, Errors, Duration per endpoint / handler / job
- **USE** (resource-driven): Utilization, Saturation, Errors per CPU / memory / queue / pool
- **Business KPIs**: declared per project (signup rate, conversion, etc.)
- **Cardinality discipline**: high-cardinality labels (user id, request id) belong in traces, not metrics

## Tracing

- **OpenTelemetry** instrumentation as the default standard
- Spans for: incoming request, outgoing call (DB / HTTP / queue), business-critical work
- Trace context propagated across service boundaries (W3C trace-context)
- Sampling strategy declared (head-based with priority sampling for errors)

## Health checks (when `backend_scope != none`)

- Liveness: process responsive
- Readiness: dependencies reachable, ready to serve
- Startup: warm-up complete (when applicable)
- Distinct endpoints; not one merged check

## Error budgets / SLOs

- For user-facing services, declare an SLO (e.g., availability 99.9%, p95 latency <300ms)
- Error budget burn alerting configured
- Alerting maps to actionable runbooks; symptom-based not cause-based

## Frontend observability

- Web: Web Vitals reported, error tracking (Sentry / Datadog / etc.) configured, source maps uploaded
- Mobile: crash reporting, ANR/freeze tracking, performance monitoring (Firebase Performance / Sentry / etc.)

## Hand-off

- Implementation and tooling: `infra-engineer`
- Producer-side instrumentation in handlers / workers: `api-engineer`, `job-engineer`
- App-level error tracking and Web Vitals: `perf-optimizer`
