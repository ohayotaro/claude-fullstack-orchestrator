---
name: codex-task
description: Create and run a canonical Claude PM to Codex engineering task using T0-T3 risk gates.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Codex Task

Use this for any repository task that needs substantial inspection, design, implementation, tests, or review.

## Workflow

1. Create `.claude/tasks/<task-id>/brief.md` using `.claude/docs/CODEX_TASK_CONTRACT.md`.
2. Classify risk as T0, T1, T2, or T3 based on scope, contract impact (API/DB/event), external effects, secrets/auth, deployment, and data migration.
3. Add stable acceptance criteria (`AC1`, `AC2`, ...), required validation, and forbidden actions. For UI-affecting tasks, require screenshot/preview capture for visual acceptance.
4. For T1, run one implementation phase:

```bash
python3 .claude/scripts/codex_handoff.py implement <task-id>
```

5. For T2, run plan, write Claude approval to `approval.md`, run implementation, then run review. Launch long-running `implement` and `review` commands through Claude Code background Bash execution when appropriate:

```bash
python3 .claude/scripts/codex_handoff.py plan <task-id>
python3 .claude/scripts/codex_handoff.py implement <task-id>
python3 .claude/scripts/codex_handoff.py review <task-id>
python3 .claude/scripts/codex_handoff.py status <task-id>
python3 .claude/scripts/codex_handoff.py collect <task-id>
python3 .claude/scripts/codex_handoff.py cancel <task-id>
```

6. For T3, obtain explicit user approval before implementation or any external action. Production deploys additionally require the `deploy-gate` acknowledgment.
7. Accept or reject by comparing the brief, the `implementation-result` Markdown artifact, `state.json`, validation evidence, and independent review. Use `codex-events.jsonl` only as an operational log, not as review input.

## PM Rules

- Claude writes only task briefs, approvals, checkpoints, plans, and acceptance notes.
- Do not create a competing technical design before Codex planning.
- Do not relax acceptance criteria silently. Update the brief when scope changes.
- Keep user interaction in Japanese; task artifacts and code are English.
