# Acceptance Record: 2026-09-01-grok-pm-adapter

- Date: 2026-09-01
- PM decision: **ACCEPTED**
- Risk tier: T2
- Final review verdict: APPROVE (fresh Codex, strong tier, effort high)

## Summary

Implemented `.grok/` — a thin adapter that lets Grok Build (xAI's agentic CLI) run as the PM in this repository while `.claude/` remains the canonical policy, rules, skills, task-artifact, and safety-hook store. Codex remains the engineering executor via `codex_handoff.py`, unchanged. Design: `.claude/plans/grok-pm-adapter-design.md` (with verified-facts addendum).

Deliverables: `.grok/config.toml` (permission translation with deny precedence), `.grok/rules/00-pm-identity.md` + `10-harness-mapping.md`, `.grok/hooks/hooks.json` + `grok_hook_adapter.py` (dual-shape payload normalizer delegating to canonical hooks, fail-closed on enforcement routes), `.grok/README.md`, `.grok/skills` symlink, and a 125-test offline suite under `.claude/hooks/tests/` including characterization tests for all six canonical hooks.

## Review history

Eight fresh full-scope reviews (all strong tier). Findings fixed across cycles: deny-rule shell-separator bypass; adapter test iteration bug; malformed Bash/write payload fail-open; enforcement-to-advisory downgrade via `--event` mismatch; non-standard JSON constants (input and child output); unidentifiable-PostToolUse advisory downgrade; multiline-command deny bypass; write-content schema fail-open; command-substitution-start deny bypass; evidence/transcript completeness. Root cause of repeated empty-evidence artifacts: the runner captures the result via `--output-last-message`, overwriting direct file edits (documented in approval Addendum 7b; template follow-up proposed below).

## Acceptance basis

- Final review: APPROVE, no High/Medium findings, AC1-AC9 all PASS.
- PM independent verification: 125 tests pass (uv-cached pytest); direct probes — deny scenarios exit 2 (source write, prod deploy without ack, secret, malformed/missing/non-string Bash and write fields, event mismatches, `NaN` input and child output, unknown-shape PostToolUse), allows exit 0; multiline and substitution-start collisions match deny rules; benign commands unaffected; canonical hooks byte-identical.
- Remaining Low (accepted with note): the implementation result transcribes the `error-to-codex.py` SHA-256 with one wrong character (`e824f523`, actual `e824b523`). PM verified the repository hash and the test expectation are correct; evidence-transcription error only, no re-run warranted.

## Deferred verification (user action items, on a machine with Grok Build)

1. Trust project hooks (`/hooks-trust` or `--trust`).
2. `grok inspect`: confirm config.toml, both rule files, hook registrations (exactly once each, no duplicate Claude-compat registration), skills symlink discovery, and whether `.claude/rules/**` loads recursively (README documents the fallback if not).
3. Fire live allow/deny scenarios (no real deploy) to confirm matcher and payload interpretation.

## Residual risks (documented, not blocking)

- Grok hooks are host-level fail-open if untrusted, never launched, killed, or host-timed-out; the adapter hardens only post-startup failures.
- Regex command policy is best-effort against shell obfuscation (quoting, variable indirection); deterministic hooks and PM approval gates remain the primary controls.
- Live Grok permission-engine semantics unverified offline.

## Template follow-ups proposed (separate tasks)

1. Document in `CODEX_TASK_CONTRACT.md` that the phase result artifact is captured from Codex's final message (`--output-last-message`) and direct edits to it are overwritten.
2. Investigate unattributed background-task kills observed during this task (three occurrences; one coincided with another local Claude Code session starting Codex work).
