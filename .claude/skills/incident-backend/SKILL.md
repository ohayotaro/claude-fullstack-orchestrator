---
name: incident-backend
description: Backend-focused production incident triage. 5xx spikes, queue stuck, DB issues, auth outage. Coordinates infra-engineer + data-engineer + auth-security-engineer + Codex CLI. Faster than /incident-response when symptoms point clearly at backend.
---

# /incident-backend

## Purpose

Backend incident triage with the right specialists wired in. Faster than `/incident-response` because the agent set is narrower and the runbook patterns are backend-specific.

## When to use

- 5xx spike on one or more endpoints
- Latency spike beyond p95 SLO
- Queue stuck (depth growing, processing rate dropping)
- DB issues (connection pool exhausted, replica lag, locking)
- Auth outage (login failures, token issuance failing)
- Schema migration that went wrong

## Triage decision tree

### Step 1 — Classify

| Symptom | First responder |
|---|---|
| 5xx with stack traces | `api-engineer` + `/codex-debugger` |
| 5xx without stack traces (gateway / LB / infra) | `infra-engineer` |
| Latency spike | `perf-optimizer` + `data-engineer` (likely DB) + `infra-engineer` |
| Queue stuck (consumers OK) | `job-engineer` (look at producer / payload) |
| Queue stuck (consumers down) | `infra-engineer` (deploy / health) + `job-engineer` |
| DB connection pool exhausted | `data-engineer` + `api-engineer` (leak detection) |
| DB replica lag | `data-engineer` + `infra-engineer` (replication health) |
| Auth outage | `auth-security-engineer` + `api-engineer` |
| Schema migration broken | `data-engineer` (rollback or forward-fix) |

### Step 2 — Stabilize

1. Confirm impact: which endpoints / services / users / since when
2. Decide rollback vs forward-fix
3. If queue is stuck and consumers OK: scale workers or pause producer briefly
4. If DB pool exhausted: identify leak (long transactions / N+1 in code path) and short-term scale up
5. Communicate (status page / internal)

### Step 3 — Root cause via Codex

Use `/codex-debugger` or the "Incident triage" template in `CODEX_HANDOFF_PLAYBOOK.md`:

```
Symptom: <e.g., 5xx spike on /api/checkout>
Started: <timestamp>
Recent deploys: <list>
Recent migrations: <list>
Observability snapshot:
- Error rate: <%>
- Latency p95: <ms>
- Affected endpoints: <list>
- Logs sample: <paste>
```

Codex returns ranked hypotheses, verification steps, mitigation options.

### Step 4 — Mitigate or fix

- For root-cause fixes: hotfix via `/deploy` with explicit hotfix override
- For workaround mitigations (e.g., circuit breaker open, queue paused): document as temporary, plan durable fix

### Step 5 — Verify recovery

- Error rate, latency, queue depth back to baseline
- Affected user paths verified working
- Observability metrics quiet

### Step 6 — Post-mortem

Within 48h, write `.claude/logs/postmortems/<date>-<title>.md` per the template in `/incident-response`.

## Backend-specific runbook hooks

### 5xx spike on a single endpoint
- Check recent deploy diff for that endpoint
- Check downstream dependency health
- Check input validation failures vs server failures (often a payload regression)

### Queue stuck
- Check DLQ size + age of oldest message
- Check consumer health (logs, restart loop, OOM)
- Check producer rate (sudden surge vs steady)
- Check broker health (visibility timeout / ack timeout misconfig)

### DB pool exhausted
- Identify long transactions (lock report, pg_stat_activity, etc.)
- Identify N+1 in recent code path (recent log sample)
- Pool tuning vs leak fix decision

### Replica lag
- Check write rate vs replica capacity
- Check replication health
- Reroute reads to primary temporarily if user-facing

### Schema migration broken
- Rollback path: per `/data-design` backout plan
- Forward-fix only if rollback is more dangerous than fix

## Output

- Stabilization log
- Codex debug record
- Hotfix deploy record (if applicable)
- Post-mortem document

## Hand-off

- Frontend symptoms during a backend incident → `/incident-response` for cross-cutting communication
- Architectural follow-up → `/architecture-review` post-mortem
- Schema-level durable fix → `/data-design`
- Auth-level durable fix → `/auth-design`

## Notes

- Backend incidents often have a faster diagnostic path because metrics + logs are richer than frontend; use that.
- Rollback is the default for incidents triggered by a recent deploy. Forward-fix only when the deploy is many releases ago or rollback is itself risky.
- Hotfix and durable fix are separate; do not bundle.
