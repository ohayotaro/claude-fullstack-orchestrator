---
name: perf-audit
description: Measurement-first performance audit across web (bundle, Core Web Vitals), iOS (Time Profiler, Hangs, SwiftUI render), Android (Profiler, Macrobenchmark, Compose recomposition), Flutter (DevTools), and backend (latency, query plans). Owned by perf-optimizer with Codex for strategy. Always cite numbers.
---

# /perf-audit

## Purpose

Diagnose and prioritize performance issues with concrete measurements. Every finding cites a profile, trace, or benchmark — no eyeballing.

## When to use

- A change set has likely perf impact (bundle size shift, hot path change, new query, new screen)
- A regression is reported (frame drop, slow response, increased bundle)
- Periodic check before release
- After a perf-targeted feature (e.g., "make checkout fast")

## Steps

### 1. Establish baseline

- Web: capture pre-change Lighthouse, bundle size, Web Vitals
- Mobile: capture pre-change Macrobenchmark / Time Profiler
- Backend: capture pre-change p50/p95/p99 per affected endpoint

If a baseline does not exist, declare one as part of this audit.

### 2. Run platform-specific profilers

#### Web
- **Lighthouse** (mobile + desktop simulated)
- **Bundle Analyzer** (e.g., `next build && next analyze`, source-map-explorer for raw bundles)
- **Web Vitals** captured via real-user monitoring or synthetic
- Record: LCP, INP, CLS, initial JS gzipped, total transfer

#### iOS
- **Xcode Instruments**: Time Profiler (CPU), Hangs (main-thread blocking), Allocations (memory), SwiftUI (view body cost)
- Frame budget: 16.7ms (60Hz) or 8.3ms (120Hz) — flag any frame exceeding budget

#### Android
- **Android Profiler** (CPU, memory, energy)
- **Macrobenchmark** for startup (TTID, TTFD) and frame timing
- **Compose recomposition count** via Layout Inspector / Macrobenchmark
- ANRs / frozen frames tracked

#### Flutter
- **DevTools Performance** tab; timeline events
- Build / paint / layout cost
- Skia / Impeller path; verify shader compilation hits at first frame are bounded

#### Backend
- Per-endpoint latency p50/p95/p99 from APM (Datadog / New Relic / Honeycomb / OTel)
- DB query plans: `EXPLAIN ANALYZE` on top queries
- N+1 detection (request log inspection or APM)
- Cache hit rate
- Error rate

### 3. Compare to thresholds

Read `.claude/perf-thresholds.json`. Default thresholds in `common/performance.md`. Flag anything exceeding.

### 4. Codex strategy review

For non-trivial findings, send to Codex:
- Measurements before
- Hypothesis on cause
- Proposed fix (if known)
- Tradeoffs of proposed fix

Codex returns standard contract output.

### 5. Categorize findings

```
### Critical (regression > X% on a budget metric)
- metric — measured value — threshold — proposed fix
### Major (close to threshold, trending wrong direction)
- ...
### Minor (improvement opportunities below threshold)
- ...
```

### 6. Remediation hand-off

- Code-level fixes → `perf-optimizer` (with `ui-engineer` / `api-engineer` for the code)
- Schema-level fixes → `data-engineer`
- Infra-level fixes (cache layer, autoscale, CDN) → `infra-engineer`

### 7. Verify after fix

Re-run profilers; report before/after numbers. A fix that does not move the number is not a fix.

### 8. Persist report

Save to `.claude/logs/reviews/perf-<run-id>.md`.

## Output

- Measurement table (before / threshold / after)
- Findings list with proposed owners
- Codex review record (when applicable)

## Quality gates

- LCP <2.5s, INP <200ms, CLS <0.1 (web; override per Zone B)
- iOS frame budget held
- Android cold start TTID <2s, TTFD <5s
- Backend p95 latency within Zone B endpoint budget
- No untracked regression on previously-OK metrics

## Notes

- Avoid optimizing without measurement. Every recommendation has a number.
- Some perf wins require trade-offs (bundle vs cache friendliness, latency vs consistency); document them.
- Add a regression test or benchmark when the threshold motivated the fix.
