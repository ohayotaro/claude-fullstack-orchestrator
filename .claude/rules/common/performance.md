# Rule: Performance

Measurement-first. Every recommendation cites a profile, trace, or benchmark.

## Default thresholds (override in Zone B `perf-thresholds.json`)

### Web
- LCP <2.5s, INP <200ms, CLS <0.1
- Initial JS bundle <200KB gzip
- Image budget per route declared
- Lighthouse Performance ≥90

### Mobile
- RN cold start <2s
- iOS frame budget 16.7ms (60fps) or 8.3ms (120fps when ProMotion target)
- Android cold start TTID <2s, TTFD <5s
- Compose: minimize recomposition; track via Macrobenchmark

### Backend
- Per-endpoint p95 latency budget declared in Zone B
- p99 latency tracked for alerting
- Throughput target declared for capacity-planning endpoints

## Process rules

- **No premature optimization**: optimize what was profiled, not what feels slow
- **Budget-driven**: declare a number before changing code, verify after
- **Document tradeoffs**: bundle size vs cache friendliness, latency vs consistency
- **Regression test**: when a numeric threshold motivated a change, add a benchmark or e2e timing assertion

## Tools by stack

- Web: Lighthouse, source-map-explorer, Bundle Analyzer, Web Vitals lib
- iOS: Xcode Instruments (Time Profiler / Hangs / Allocations / SwiftUI)
- Android: Android Profiler, Macrobenchmark, Compose recomposition counts
- Flutter: Timeline, DevTools, performance overlay
- RN: Hermes profiles, Flipper, FlatList virtualization checks
- Backend: language-specific profilers, DB EXPLAIN, APM traces

## Hand-off

- Measurement and code-level fixes: `perf-optimizer`
- Schema-level fixes: `data-engineer`
- Infra-level fixes (autoscale, cache layer): `infra-engineer`
