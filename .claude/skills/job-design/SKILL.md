---
name: job-design
description: PM intake for background jobs, queues, schedulers, and async workflows.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Job Design

Job work is T2 by default. It is T3 if it mutates production data at scale or changes broker infrastructure.

## Intake

- Record the trigger (enqueue site), broker (Zone B), expected volume, and latency tolerance.
- Capture delivery semantics required: at-least-once vs exactly-once effect via idempotency.

## Acceptance Checklist

- AC includes idempotency keys and retry policy with backoff.
- AC includes dead-letter handling and an alert on DLQ growth.
- AC includes no fire-and-forget: handlers enqueue, workers process, evidence via tests.
- AC includes graceful shutdown draining for workers.

## Delegation

Create the task brief and run `plan` before implementation. Broker/infra changes pair with `/infra-review`.
