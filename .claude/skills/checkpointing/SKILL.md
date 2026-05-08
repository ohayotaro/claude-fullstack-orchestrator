---
name: checkpointing
description: Persist session state and run drift detection. Snapshots active context, rotates Zone C, detects when documentation has drifted from code, and produces a brief status report. Run periodically during long sessions and at the end of major features.
---

# /checkpointing

## Purpose

Two roles bundled:

1. **Session continuity**: snapshot Zone C (active work context) so a future session can pick up cleanly
2. **Drift detection**: surface gaps between documentation and actual repo state

## When to use

- End of a major feature work session
- Before switching to a different feature
- After a long session (>2h) when context is dense
- Periodically (release cadence) to keep documentation synced

## Steps

### 1. Snapshot Zone C

Read CLAUDE.md Zone C (after `@orchestra:repo-boundary`). Summarize active items:

- Currently in-progress work (with file paths)
- Recent design decisions
- Open questions awaiting user
- Hand-offs to specific agents

If Zone C exceeds the configured limit (default 10 entries): rotate older entries to `.claude/logs/checkpoints/<date>.md`, leave only the most recent N in Zone C.

### 2. Drift detection

Walk through these checks; report findings:

#### a. CLAUDE.md vs `.claude/skills/`

For every skill mentioned in CLAUDE.md (Skill Pipelines section): verify the skill directory exists.

```bash
grep -oE "/[a-z][a-z0-9-]+" CLAUDE.md | sort -u
```

Cross-reference with `ls .claude/skills/` — flag missing directories.

#### b. CLAUDE.md vs `.claude/agents/`

For every agent name in routing tables / examples: verify the agent file exists.

#### c. DESIGN.md vs reality

For every file path or command in DESIGN.md: verify it exists or is reasonable to expect.

#### d. `.claude/contract-watch.json` vs actual contracts

For every pattern in contract-watch.json: verify some file matches (otherwise the pattern is dead weight).

#### e. Zone B vs project state

- `framework: nextjs` declared but no `next.config.*`? Drift.
- `database.engine: postgres` declared but no Postgres connection config? Drift.
- `mobile.swift: true` declared but no `ios/` directory? Drift.

#### f. `routing-keywords.json` vs agents

Every agent name referenced in routing keywords must exist under `.claude/agents/`.

### 3. Generate report

```
## Checkpoint <date>

### Snapshot
- Active work: <summary>
- Open questions: <list>

### Zone C rotation
- Rotated <N> entries to .claude/logs/checkpoints/<date>.md
- Remaining in Zone C: <count>

### Drift findings
- [Severity] file/area: description — recommended action

### Action items
- [ ] ...
```

### 4. Persist

Save report to `.claude/logs/checkpoints/<date>.md`. Update Zone C in CLAUDE.md.

### 5. Surface to user

Print the report. Highlight any drift findings that need user attention.

## Output

- Checkpoint report at `.claude/logs/checkpoints/<date>.md`
- Updated CLAUDE.md Zone C (rotated)
- Drift findings list

## Drift severity

- `block`: policy artifact references something missing in the repo (e.g., agent file)
- `warn`: documentation references a path that may exist but cannot be verified
- `note`: minor inconsistency (e.g., outdated reference)

## Notes

- Run periodically — drift accumulates silently otherwise.
- Findings are routed back to the responsible doc owner (often the user, sometimes a specific agent).
- This skill does NOT auto-fix drift; it surfaces it. Auto-fix would risk overriding intentional state.
