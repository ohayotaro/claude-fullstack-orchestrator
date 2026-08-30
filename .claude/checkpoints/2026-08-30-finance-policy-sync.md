# Checkpoint: 2026-08-30 claude-finance policy sync

## Task

- Task ID: none (PM-only doc/policy change, T0; no Codex phase run)
- Risk tier: T0
- Commit: `da163c4` chore(pm): adopt codex tier policy, PM git ownership, and tracked task artifacts (pushed to `origin/main`)

## What changed

Ported from claude-finance commits `7f49fd5`, `14dd78b`, `92aba9f`:

- `.claude/rules/common/codex-delegation.md`: Model And Effort Tier Policy (strong/mid/light, per-phase table, final gate always strong+high).
- `.claude/docs/CODEX_TASK_CONTRACT.md`: pointer to tier policy; task dir now tracked in Git.
- `CLAUDE.md`: Claude PM owns routine Git (staging, Conventional Commits, push); destructive Git ops excluded.
- `.gitignore`: `.claude/tasks/`, `checkpoints/`, `plans/` tracked; only `*/codex-events.jsonl` and `.claude/state/` local.
- `README.md`, `document-lifecycle.md`: aligned.

## Decisions

- Runner keeps `python3` invocation (3.9-compatible via `timezone.utc` shim; no `pyproject.toml`), unlike finance's `uv run python`.
- `.claude/tasks/2026-07-12-hook-runner-hardening/` stays gitignored: artifacts contain secret-scan placeholder fixtures (`sk-xxx...`), not real secrets.
- Auto-mode classifier blocks `git commit` from Claude; user ran the commit manually. Consider allow rules `Bash(git commit:*)`, `Bash(git push:*)` in `.claude/settings.local.json`.

## Validation

- `git diff --stat`: 6 files, +45/-7. Docs only; no runtime code.

## Blockers

- None.

## Next action

- Apply tier policy on the next T1/T2 Codex task (`--model`/`--effort` per phase kind) and record deviations in `approval.md`.
- Optionally add git allow rules so PM commits work under auto mode.
