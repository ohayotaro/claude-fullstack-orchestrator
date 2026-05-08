---
name: job-design
description: Design background jobs / queue workers / scheduled tasks. Owned by job-engineer with Codex review for non-trivial cases. Covers producer contract, broker config, worker logic, idempotency, retry policy, DLQ handling.
---

# /job-design

## Purpose

Take a "this should run async" requirement to a reviewed design with explicit delivery semantics, idempotency strategy, retry policy, and observability hooks.

## When to use

- Long-running work that should not block a request (email, image processing, sync to external service)
- Scheduled jobs (daily report, cleanup, retention enforcement)
- Event-driven processing (consume Pub/Sub topic, react to S3 upload, etc.)
- Periodic data hygiene (deduplication, recompaction)

## Steps

### 1. Read context

- Zone B `message_broker`, `backend_languages`, `backend_framework`, `database`
- Existing worker / queue patterns in the codebase
- The job's actual requirements: latency tolerance, retry tolerance, ordering, idempotency

### 2. Design the producer contract

- Where does the job get enqueued from? (HTTP handler / scheduler / event)
- Payload schema — versioned and validated
- Idempotency key sourced from input (request id / event id), not generated in worker
- Outbox pattern when DB write + publish must be atomic (with `data-engineer`)

### 3. Design broker topology

Per Zone B `message_broker`:

- **SQS**: queue + DLQ; visibility timeout > processing time; FIFO if ordering matters
- **Pub/Sub**: topic + subscription; ack deadline; ordered subscription if ordering matters
- **Kafka**: topic + consumer group; partition key; offset commit semantics
- **RabbitMQ**: exchange + queue + binding + DLX
- **Redis-backed (BullMQ / Sidekiq / RQ)**: persistence policy, single-region considerations

### 4. Design worker logic

- Per Zone B `backend_framework`: worker library (Celery / RQ / Dramatiq / Arq / Inngest / BullMQ / native consumer)
- Concurrency: workers × prefetch; tuned to broker visibility timeout
- Timeout per job; soft and hard limits
- Retry policy (default: exponential backoff with jitter; capped attempts; non-retryable types fail-fast)
- Cancellation: respect cancellation tokens / graceful shutdown
- Observability: per-job log entries (job_id, attempt, duration, outcome)

### 5. Idempotency strategy

- Idempotency key honored at the worker (skip duplicate inputs within a TTL window)
- Database mutations idempotent (upsert vs insert; conditional updates)
- External API calls: handle retry interaction (idempotency key forwarded)

### 6. DLQ and replay

- DLQ wired with appropriate retention
- Alerting on DLQ size / age of oldest message
- Manual replay tool documented (CLI command, UI button, or runbook)

### 7. Codex review for non-trivial designs

When the job involves:
- Cross-service eventual consistency
- Outbox + idempotency + ordering simultaneously
- Long-running work spanning multiple resources
- Critical-path SLA (user is waiting on the result)

Send to Codex with the design. Codex returns standard contract format with focus on correctness under failure modes.

### 8. Document

- Producer contract spec
- Topology diagram (text)
- Retry / DLQ policy
- Replay procedure
- Observability hooks (metrics: queue depth, processing rate, error rate, DLQ size, age of oldest)

Save to `design/decisions/job-<name>.md`.

## Output

- Design record
- Producer contract
- Worker scaffold
- Broker config (IaC if applicable, hand-off to `infra-engineer`)

## Hand-off

- Endpoint that enqueues → `api-engineer`
- Schema for outbox / job-state tables → `data-engineer`
- Broker provisioning + worker deployment → `infra-engineer`
- Auth/authz of who may enqueue → `auth-security-engineer`

## Notes

- Default to **at-least-once delivery + idempotent consumer**. Exactly-once is rarely needed and expensive.
- HTTP handlers do not perform long async work — enqueue. Fire-and-forget is forbidden.
- Every job has measurable SLA / SLO; alerting threshold tied to it.
