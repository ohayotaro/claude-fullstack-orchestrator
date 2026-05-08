---
name: start-feature
description: Multi-agent feature kickoff. Combines codebase exploration (Opus subagent, 1M context), parallel research (Opus + Gemini for any visual references), and architecture design (Codex CLI), then integrates the result into a plan presented for user approval. Run at the start of a non-trivial feature.
---

# /start-feature

## Purpose

Bring a feature from "the user just described what they want" to "we have a plan ready to execute" with the right specialists involved. Runs four phases in sequence and produces a single consolidated plan for user approval.

## When to use

- New feature affecting multiple files / agents / platforms
- Feature with non-obvious architecture (state, auth, contract, schema choices)
- Feature with visual references (competitor screenshots, Figma exports, brand assets)

Skip when:
- The change is mechanical (lint fix, rename, tiny bug). Use `/parallel-batch` or direct edits.
- The change is purely additive within a known pattern. Skip to `/team-implement` after a brief plan.

## Steps

### Phase 1 — Codebase exploration

Delegate to `general-purpose` Opus subagent (1M context):
- Find existing patterns relevant to the feature
- Identify files/modules likely to be touched
- Surface conventions the implementation must respect
- Identify risk areas (touching contracts, auth, migrations)

The orchestrator does NOT do this directly — the 1M context belongs to the subagent.

### Phase 2 — Research (parallel)

Branch by input type:

- **If visual references exist** (screenshots, Figma, brand PDFs): delegate to `visual-analyst` (Gemini) via `/design-research` to extract structured analysis.
- **If external libraries are in scope**: delegate to `general-purpose` subagent to research options + version constraints + conventions.

These run in parallel with Phase 3 when feasible.

### Phase 3 — Design (Codex CLI)

Delegate architecture decisions to Codex:
- Component / module decomposition
- State management pattern (consult `state-architect` review of Zone B)
- API contract and validation strategy (with `api-engineer`)
- DB schema impact (with `data-engineer`)
- Auth/authz impact (with `auth-security-engineer`)
- Cross-cutting concerns: error handling, observability hooks

Codex output format expected: TL;DR → Analysis → Plan → Validation → Risks → Confidence.

### Phase 4 — Plan integration

Orchestrator integrates Phase 1-3 outputs into a single plan:

- Affected files (with rationale)
- Agents who will execute each module
- Sequence and parallelizability
- Test plan (unit / component / e2e / visual)
- Observability hooks (logs, metrics, traces)
- Risk register

Present plan to the user with `AskUserQuestion`:
- Approve as-is
- Approve with modifications (collect modifications)
- Need more research (loop back)

## Output

- Plan document (in conversation)
- Optionally persist to `design/decisions/<feature-name>.md` for future reference
- Approved plan unblocks `/team-implement`

## Hand-off

Once approved → `/team-implement`. After implementation → `/visual-verify` (UI features) and `/team-review`.

## Notes

- Phase 1 + 2 + 3 use parallel delegation when independent. Foreground-wait for each before integrating.
- Save raw Codex / Gemini outputs to `.claude/logs/` for audit.
- The orchestrator must not skip the user approval step — designs are human-decided.
