---
name: parallel-batch
description: Run general-purpose Opus subagents in parallel for high-throughput mechanical work — lint fixes, renames, codemods, test scaffold generation across many files. Each subagent gets a bounded file scope. Use instead of /team-implement when the work is mechanical (no design judgment).
---

# /parallel-batch

## Purpose

Get high-throughput parallel work done across many files when the work itself is mechanical (no design decisions). The same Opus subagent role (`general-purpose`) is invoked N times with disjoint scopes, then the orchestrator integrates the results.

## When to use

- Many-file lint / format fix-up
- Many-file rename (variable, file, package import path)
- Codemod-style change (replace pattern X with Y across the codebase)
- Test scaffold generation across modules (describe / it stubs)
- Adding a small consistent annotation across files
- Updating import paths after a refactor

Skip when:
- The work involves design decisions → `/team-implement` with role-specific agents
- The work is small enough for one agent to do directly → no batch needed
- The work touches contract boundaries → `check-codex-on-contract-edit.py` will (correctly) gate it

## Prerequisites

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `settings.json`
- `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`
- A clear specification of the mechanical change (precise enough that subagents do not need judgment)

## Steps

### 1. Define the change crisply

Before launching any agent, write the change as:

- The find pattern (regex / structural)
- The replace pattern
- Files in scope (glob or list)
- Files NOT in scope (exclusions)
- Verification command (lint / typecheck / a smoke test)

If you cannot write the change this crisply, the work is not mechanical — go to `/team-implement` instead.

### 2. Partition by file scope

Split the in-scope files into N disjoint groups (default N=5; adjust based on file count and group cohesion). Disjoint scopes mean no merge conflicts between subagents.

Examples:

- By directory (`apps/web/**` to one teammate, `apps/mobile/**` to another)
- By file count (round-robin distribute 50 files into 5 groups of 10)
- By module ownership (when natural boundaries exist)

### 3. Launch N subagents in parallel

Each subagent receives:
- The crisp change spec (from step 1)
- The file scope assigned to it
- A reminder that this is mechanical work — no design decisions
- The verification command

Subagent role: `general-purpose`. Invoke via Agent Teams.

### 4. Collect results

Each subagent returns:
- List of files changed
- Verification command output (pass / fail)
- Any unexpected items it skipped (with rationale)

### 5. Integrate

- Verify file scopes did not overlap (sanity check)
- Run the project-wide verification command
- If any subagent reported a skip with rationale, surface to the user — that case may have hidden judgment
- Lint / format pass via `lint-on-save.py` hook

### 6. Commit

Single commit (mechanical change spans the project) with a clear message describing the change and the spec used.

## Output

- Files changed across scopes
- Verification result
- Per-subagent log (saved under `.claude/logs/agent-teams/parallel-batch/<run-id>/`)

## Notes

- Sonnet is NOT used for parallel work in this template (matching the financial sister template). Opus subagents handle parallel mechanical tasks.
- If a subagent reports judgment was required (the change is not as mechanical as you thought), STOP — do not continue automation. Switch to `/team-implement` with appropriate role agents.
- Contract-boundary edits caught by hook will block the subagent; route those out of the batch and handle individually with Codex review.
