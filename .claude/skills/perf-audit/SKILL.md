---
name: perf-audit
description: PM intake for measurement-first performance audits across web, mobile, and backend.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Perf Audit

Perf work is T1 for a localized measured fix, T2 for cross-cutting changes (bundling strategy, caching layers, query redesign).

## Intake

- Record the symptom, the surface, and the budget breached (Core Web Vitals, bundle size, cold start, frame budget, p95 latency).
- Require a measurement first: profile, trace, Lighthouse run, EXPLAIN, or benchmark. No optimization without a number.

## Acceptance Checklist

- AC includes the target number declared before the change and verified after.
- AC includes the profiling evidence cited in the result (tool + measurement).
- AC includes a regression guard (benchmark or timing assertion) when a threshold motivated the change.
- AC includes documented tradeoffs (bundle vs cache, latency vs consistency).

## Delegation

Create the task brief with the measured baseline and delegate via `/codex-task`. Reject results that claim improvement without before/after numbers.
