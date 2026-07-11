# Acceptance Record: 2026-07-12-hook-runner-hardening

- Decision: ACCEPTED
- Risk tier: T2
- Accepted by: Claude (PM), 2026-07-12
- Task artifacts: `.claude/tasks/2026-07-12-hook-runner-hardening/` (gitignored)

## Background

A template meta-review found three major enforcement gaps in the deterministic safety layer and four minor issues:

1. `deploy-gate.py` scanned only the first command verb, so compound commands (`echo deploying && vercel deploy --prod`) bypassed the production-deploy gate.
2. `codex_handoff.py` ran the Codex subprocess without a timeout, allowing indefinite hangs pinned in `running` state.
3. `pm-write-guard.py` / `secret-scan.py` were wired only to `Edit|Write`, leaving `MultiEdit` and `NotebookEdit` (`notebook_path`) uncovered.

Minor: non-atomic `state.json` writes; substring-based placeholder allowlisting in secret-scan; `/state-design` missing from Skill Pipelines; doc drift in codex-delegation.md, DESIGN.md, and CLAUDE.md approved paths.

## Outcome

All fixed across nine files: `deploy-gate.py` (segment-wise + `$()`/backtick substitution scanning), `codex_handoff.py` (`CODEX_PHASE_TIMEOUT_SECONDS`, default 3600s, fail-closed; atomic state writes via temp file + `os.replace`), `pm-write-guard.py` / `secret-scan.py` / `settings.json` (four write tools covered, fail-closed on missing path for recognized tools, anchored whole-value placeholder matching, all matches scanned per pattern), plus doc alignment and DESIGN.md version bump.

## Process

- Codex plan -> PM approval -> implementation (PASS) -> independent review #1: CHANGES_REQUIRED (two High findings in secret-scan.py: mixed placeholder+secret values allowed; only first match per pattern evaluated — both reproduced by the reviewer).
- Brief Revision 1 -> remediation implementation (PASS, with exact repro commands) -> independent review #2: APPROVE, no findings.
- PM acceptance spot-check: compound deploy command, mixed-placeholder secret, and out-of-allowlist NotebookEdit all blocked with exit 2.

## Residual Risks

- Deploy and secret detection remain conservative stdlib scanners, not full shell/entropy parsers (accepted by design).
- Runner timeout path validated via local stub, not a live Codex run.
