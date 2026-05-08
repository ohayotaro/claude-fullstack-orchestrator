---
name: team-review
description: Parallel 5-track review of recent changes. Tracks Security, Quality, Accessibility, Performance, and Architecture run concurrently with Codex CLI as the deep-reasoning agent for each. Run after /team-implement.
---

# /team-review

## Purpose

Catch issues before merge by running five parallel reviews against the change set. Each track has a specific lens; the union covers the cross-cutting concerns.

## When to use

- After `/team-implement` (or any feature implementation)
- Before merging a non-trivial PR
- After auto-merged rebase or refactor when scope is wide

## Tracks (run in parallel)

### 1. Security review (`auth-security-engineer` + Codex)

Lens: OWASP Top 10, secret hygiene, IDOR, validation gaps, auth/authz coverage. Reads `common/security.md`.

### 2. Quality review (Codex via `general-purpose`)

Lens: lang-rules conformance (`lang/<active>/coding-principles.md`, `*-patterns.md`), code clarity, deduplication, error handling, type strictness. Reads relevant lang rule files.

### 3. Accessibility review (`a11y-auditor`)

Lens: WCAG 2.2 AA, native a11y guidelines for affected platforms, keyboard / screen reader / contrast / motion. Runs automated tooling (axe-core, Lighthouse, Accessibility Inspector / Scanner) where applicable.

### 4. Performance review (`perf-optimizer` + Codex)

Lens: bundle / LCP / INP / CLS impact (web), startup / frame budget (mobile), latency / N+1 / index coverage (backend). Cites measurements where possible.

### 5. Architecture review (`/architecture-review`)

Lens: state / navigation / package boundaries / service boundaries / contract drift. Reads `common/api-contracts.md`, `common/data-modeling.md`, `common/state-management.md`. Flags any change crossing a contract boundary that lacks a corresponding contract artifact update.

## Steps

### 1. Determine scope

Use `git diff` against the merge base to identify files changed.

### 2. Launch all five tracks in parallel

Each track receives:
- The changed files
- The relevant rule files
- A directive to use Codex for deep reasoning

### 3. Collect findings

Each track returns a structured report:

```
## <Track Name>
### Critical
- file:line — finding — recommendation
### Major
- ...
### Minor
- ...
### OK / Notes
- ...
```

### 4. Consolidate and prioritize

Orchestrator merges the five reports:
- Critical findings block merge
- Major findings require resolution or explicit deferral with rationale
- Minor findings tracked

Output a single deduplicated report to the user.

### 5. Loop back if needed

Critical findings → `/team-implement` again on the affected scope, then re-run `/team-review`.

## Output

- Consolidated review report (in conversation)
- Optionally persist to `.claude/logs/reviews/<timestamp>.md`
- Verdict: `pass | review-required | block`

## Notes

- The 5 tracks are **independent** — they run in true parallel via Agent Teams.
- Each track has a bounded scope; no track owns the entire change set.
- Avoid duplicate findings: if Security and Architecture both flag an auth contract issue, deduplicate during consolidation.
- The orchestrator does NOT vote on findings — it surfaces them. The user resolves disputes.
