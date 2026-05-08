---
name: incident-response
description: Frontend / cross-cutting production incident response. Coordinates triage, mitigation, root-cause analysis (via Codex), recovery, and post-mortem. Use for incidents where the symptom is in the frontend or visible to end users; for backend-specific issues use /incident-backend.
---

# /incident-response

## Purpose

Bring an active production incident from "users are reporting X" to "fix deployed + post-mortem written" with structure and minimum thrashing.

## When to use

- Frontend regression visible in production (broken page, white screen, stuck flow, 500 from BFF)
- Cross-cutting incident affecting multiple platforms (auth flow broken on web + mobile)
- User-visible degradation that is not strictly a backend issue

For backend-only issues (5xx spike, queue stuck, DB outage), use `/incident-backend`.

## Phases

### Phase 1 — Stabilize

1. Confirm scope: which surfaces, which users, since when
2. Decide: rollback OR forward-fix
   - Rollback if the causing change is recent and well-defined
   - Forward-fix if the issue is ambient or rollback is risky
3. If rollback: execute via `/deploy` with the previous-good version
4. Communicate: status page / internal channel update with expected recovery time

### Phase 2 — Mitigate

1. If forward-fix: identify the smallest possible change that restores service
2. Get a code review from Codex via `/codex-system` before deploying a hotfix
3. Deploy via `/deploy` with `hotfix` override authorization

### Phase 3 — Root cause

After service is stable:

1. Use `/codex-debugger` for deep analysis
2. Identify:
   - Trigger (what change / event caused the symptom)
   - Latent issue (why the trigger caused failure)
   - Detection lag (how long before we noticed)
   - Mitigation cost (how long to recover)

### Phase 4 — Durable fix

1. Land the durable fix (separate from the hotfix)
2. Add regression test that would have caught this
3. If a hook would have caught it: extend `.claude/hooks/`

### Phase 5 — Post-mortem

Within 48 hours, write `.claude/logs/postmortems/<date>-<title>.md`:

```
## Summary
- What happened
- Impact (users / time / metrics)

## Timeline (UTC)
- Detection
- Mitigation
- Resolution
- Postmortem

## Trigger
- The change / event that caused the symptom

## Root cause
- The latent condition that allowed the trigger to cause failure

## Detection
- How we noticed (alert / user report / monitoring)
- Detection lag

## Response
- Steps taken in order
- What worked, what didn't

## Lessons
- Action items (owners + due dates)
- Process changes if any
```

### Phase 6 — Action items

Track follow-ups to closure:
- Process improvements (better alerting, runbook, hook)
- Architectural changes (boundary, redundancy, circuit breaker)
- Test coverage gaps

## Output

- Stabilization log
- Hotfix deploy record
- Codex debug record
- Post-mortem document
- Tracked action items

## Quality gates (during incident)

- Status updates every 30 minutes during active incident
- Decisions logged in real time (channel or doc)
- Hotfix has minimal blast radius and explicit rollback
- Communication is honest about uncertainty

## Notes

- Blameless culture: post-mortems analyze processes, not people
- Hotfix and durable fix are separate commits / deploys; do not combine
- "We rolled back; we're fine" is incomplete — the post-mortem and durable fix close the loop
