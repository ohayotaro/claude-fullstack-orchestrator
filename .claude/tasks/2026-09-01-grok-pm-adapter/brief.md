# 2026-09-01-grok-pm-adapter: Grok Build PM adapter (.grok)

## Objective

Allow Grok Build (xAI's agentic CLI) to run as the PM in this repository, in place of Claude Code, reusing `.claude/` as the single source of truth for policy, rules, skills, task artifacts, and safety hooks. Codex remains the engineering executor via `codex_handoff.py`, unchanged.

## Scope

Implement the design in `.claude/plans/grok-pm-adapter-design.md` (including its 2026-09-01 addendum of facts verified against docs.x.ai/build):

- `.grok/config.toml` — project-shared permission rules translated from `.claude/settings.json` allow/deny intent, plus hook/plugin registration as required by Grok Build.
- `.grok/rules/00-pm-identity.md` — Grok PM identity delta: the PM role CLAUDE.md assigns to "Claude" applies to the running Grok agent; Codex remains executor; Japanese user interaction / English artifacts; PM write-scope restated; AGENTS.md is Codex's contract (reference only); instruction to reload CLAUDE.md, AGENTS.md, CODEX_TASK_CONTRACT.md, and the current brief after compaction.
- `.grok/rules/10-harness-mapping.md` — tool-name and artifact-path mapping (task artifacts stay under `.claude/tasks/` etc.).
- `.grok/hooks/` — hook registration JSON (`<project>/.grok/hooks/*.json`) wiring PreToolUse (write tools → secret-scan + pm-write-guard; bash → deploy-gate) and PostToolUse (bash → post-bash-dispatcher), plus `grok_hook_adapter.py` that normalizes Grok payloads/env to the Claude hook contract and delegates to the existing `.claude/hooks/*.py` scripts.
- `.grok/README.md` — setup (`/hooks-trust` requirement), adapter contract, permission translation table, fail-open residual-risk note, `grok inspect` verification steps.
- Minimal deltas inside `.claude/`: pm-write-guard continues to block `.grok/**` writes (verify; add if needed), `document-lifecycle.md` and `checkpointing` drift list gain a `.grok/config.toml` vs `.claude/settings.json` intent-drift check, and CLAUDE.md Zone C gets a one-line context entry.
- If (and only if) hooks require an env fallback: existing `.claude/hooks/*.py` may add `GROK_WORKSPACE_ROOT` as a fallback for `CLAUDE_PROJECT_DIR` without behavior change under Claude Code.

## Non-Goals

- Replacing or abstracting the Codex executor path.
- Rewriting `.claude/hooks` or `.claude/skills` into Grok-native formats.
- Renaming the "Claude" actor in CLAUDE.md Zone A.
- Concurrent dual-PM sessions.
- Any change to `codex_handoff.py`.

## Acceptance Criteria

- AC1: `.grok/` contains config.toml, rules (00-pm-identity, 10-harness-mapping), hooks (registration JSON + adapter), and README.md, all in English, matching the approved plan.
- AC2: The hook adapter accepts a Grok-shaped PreToolUse payload (`hookEventName`, `toolName`, `toolInput`, `workspaceRoot`, camelCase) and a Claude-shaped payload (`tool_name`, `tool_input`), normalizes both, delegates to the correct `.claude/hooks/*.py`, and preserves exit-code semantics (0 allow / 2 deny).
- AC3: The adapter fails CLOSED for enforcement events: any internal error, unknown payload shape, or missing target script on a PreToolUse write/bash event results in exit 2 with a reason on stderr/stdout JSON. Unit tests prove this.
- AC4: Unit tests (pytest) cover the adapter: allow path, deny path (pm-write-guard blocking a source write; deploy-gate blocking a prod deploy command without ack; secret-scan blocking a fake secret), payload normalization both shapes, and fail-closed error handling. Tests run without the Grok CLI installed.
- AC5: Existing hooks continue to pass under Claude Code semantics: running each `.claude/hooks/*.py` with Claude-shaped stdin behaves exactly as before (no regression; add characterization tests if none exist).
- AC6: `.grok/config.toml` deny intent covers at least: `rm -rf`, `--no-verify`, `codex --search`, `codex --dangerously-bypass-approvals-and-sandbox`, in Grok's rule syntax; the README documents the translation table and any expressiveness gaps.
- AC7: `.grok/README.md` documents: `/hooks-trust` prerequisite, Grok's fail-open hook behavior and why the adapter hardens it, `grok inspect` verification checklist, and the rule-loading verification step (whether `.claude/rules/**` loads recursively; fallback instructions if not).
- AC8: pm-write-guard blocks PM writes into `.grok/**` (existing behavior confirmed by test, or a minimal allowlist-preserving change).
- AC9: No secrets in any artifact; no network required at runtime by the adapter.

## Constraints And Context

- Design doc: `.claude/plans/grok-pm-adapter-design.md` — follow it; deviations must be argued in plan.md.
- Verified Grok Build facts (PM-fetched from docs.x.ai/build, 2026-09-01; Codex has no network — do not attempt to re-verify online):
  - Hook registrations load from `~/.grok/hooks/*.json`, `<project>/.grok/hooks/*.json`, and compatibly from Claude Code's `.claude/settings.json`. Matchers are regex on tool names; handler types `command` | `http`; default timeout 5s.
  - Payload fields: `hookEventName`, `sessionId`, `cwd`, `workspaceRoot`, plus `toolName`, `toolInput` on tool events. Whether Claude-compat registration also delivers snake_case payloads is UNDOCUMENTED — hence the dual-shape adapter (AC2).
  - Env: `GROK_HOOK_EVENT`, `GROK_HOOK_NAME`, `GROK_SESSION_ID`, `GROK_WORKSPACE_ROOT`. No `CLAUDE_PROJECT_DIR`.
  - Blocking: PreToolUse only; exit 0 allow, exit 2 deny, or stdout `{"decision": "deny", "reason": "..."}`. Timeout/crash/malformed output fail OPEN — adapter must be crash-hardened per AC3.
  - Events include PreToolUse, PostToolUse, PreCompact, SessionStart, etc.
  - Instruction files: AGENTS.md, CLAUDE.md, CLAUDE.local.md, `.grok/rules/*.md`, and `.claude/rules/` (compat) auto-load; `.gitignore`d files skipped; no size cap; recursion into `.claude/rules/**` subdirectories unconfirmed.
  - Project hooks run only after explicit trust (`/hooks-trust` / `--trust`).
- Repo context: template repo, no product code yet; Python 3.11+, ruff, pytest conventions per `.claude/rules/lang/python/*`.
- Known-failure-class checklist applies: identity binding, fail-closed inspections, TOCTOU, cache trust, boundary exactness, reserved names, duplicate keys.
- Network access: not required.

## Risk Tier

T2 - multi-file, new adapter architecture touching the safety-hook enforcement surface; no production deployment, secrets, or destructive migration.

## Required Validation

- `pytest` for the new adapter/hook tests (place tests where the plan proposes, e.g. `.claude/hooks/tests/` or `tests/`; justify location).
- `ruff check` on all new/modified Python.
- Manual command transcripts in the implementation result: each deny scenario in AC4 exercised via `echo '<payload>' | python3 .grok/hooks/grok_hook_adapter.py ...` showing exit codes.
- Confirmation that Claude-shaped invocation of every existing hook is byte-identical in behavior (AC5 evidence).

## Forbidden Actions

- No modification of `codex_handoff.py`, skills, or rule content beyond the minimal deltas listed in Scope.
- No weakening of existing deny rules or hook blocking logic.
- No network calls at runtime or in tests.
- No new dependencies beyond the Python standard library for the adapter.
- No git commits (PM owns Git).

## Open Decisions Or Blockers

- Whether Grok's Claude-compat mode delivers snake_case payloads cannot be confirmed offline — resolved by the dual-shape adapter (AC2); real-CLI verification (`grok inspect`, live hook firing) is deferred to PM/user acceptance on a machine with Grok Build installed.
- `.grok/config.toml` exact permission-rule syntax is not fully documented offline; implement best-effort from the design doc, flag uncertainties in the result, and the README must instruct verifying with `grok inspect`.
