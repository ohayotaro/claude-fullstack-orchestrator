---
name: team-implement
description: Parallel multi-agent implementation. Spawns specialized agents (ui-engineer, api-engineer, data-engineer, etc.) on disjoint file scopes via Agent Teams. Each teammate writes a completion log. Run after /start-feature produces an approved plan.
---

# /team-implement

## Purpose

Execute an approved plan in parallel across the right agents, with file-scope isolation to avoid conflicts. Used when a feature touches multiple modules or platforms.

## When to use

- After `/start-feature` produces an approved plan with multiple modules
- When changes span 2+ disjoint file scopes (e.g., web + iOS + backend handler)
- When changes are mechanical and parallelizable (`/parallel-batch` is the lighter alternative for that case)

## Prerequisites

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `settings.json`
- `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`
- An approved plan from `/start-feature`

## Steps

### 1. Decompose the plan into Teammate assignments

Each Teammate gets:
- A specific role agent (e.g., `ui-engineer`, `api-engineer`)
- A bounded file scope (e.g., `apps/web/features/login/**`)
- A specific scope of responsibility (do this, do not touch that)
- A reference to the plan section it implements

Teammates with disjoint file scopes can run in parallel. Teammates with dependencies (B needs A's contract) run sequentially.

### 2. Launch Teammates

For independent teammates: launch in parallel via Agent Teams.

For dependent teammates: chain them — teammate B receives teammate A's output as context.

Common patterns:

| Pattern | Teammates |
|---|---|
| UI-only feature | `design-system-engineer` (if new primitive) → `ui-engineer` (screen) → `qa-engineer` (tests) |
| Fullstack feature | (parallel) `api-engineer` + `data-engineer` + `ui-engineer` + `qa-engineer` |
| Auth flow | `auth-security-engineer` (design) → (parallel) `api-engineer` + `data-engineer` + `ui-engineer` |
| Native + web | (parallel) `ui-engineer` (web) + `ui-engineer` (mobile, second invocation) + `design-system-engineer` |

### 3. Each Teammate writes a log

`.claude/logs/agent-teams/<feature>/<agent>-<timestamp>.md` with:
- Files changed
- Tests added
- Decisions made (and any deviations from the plan)
- Hand-off pointer (next teammate / orchestrator)

### 4. Orchestrator collects logs and integrates

After all teammates report:
- Verify file scopes did not collide
- Verify the contract between teammates' outputs is consistent (e.g., backend handler shape matches frontend client shape)
- Run lint / type check across the changes (via hooks)

If any teammate flagged a contract drift, route to `/architecture-review` before proceeding.

### 5. Hand off to verification

- UI features → `/visual-verify`
- Backend changes → `/api-build` continuation (if not already complete) and `/data-design` for migrations
- Always → `/team-review`

## Output

- Files changed across the project
- Logs at `.claude/logs/agent-teams/<feature>/`
- Status report to the user (counts, scopes, next steps)

## Notes

- Teammates respect Zone B (active rules, framework, etc.) the same way the orchestrator does.
- If a teammate hits a contract boundary edit, the `check-codex-on-contract-edit.py` hook fires (severity: warn) and the teammate must request a Codex review before proceeding.
- Sonnet workers are NOT used — all teammates are Opus.
