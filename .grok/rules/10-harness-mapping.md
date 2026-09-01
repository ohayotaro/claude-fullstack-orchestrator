# Grok Build Harness Mapping

`.claude/` is the canonical orchestration data store even when Grok Build is
the PM. Never mirror or relocate these artifacts.

| Purpose | Canonical path |
|---|---|
| Task brief, plan, approval, result, review, state | `.claude/tasks/<task-id>/` |
| Checkpoints | `.claude/checkpoints/` |
| Shared plans | `.claude/plans/` |
| Deploy acknowledgments and PM state | `.claude/state/` |
| Review records | `.claude/docs/reviews/` |
| Engineering handoff contract | `.claude/docs/CODEX_TASK_CONTRACT.md` |
| Codex runner | `.claude/scripts/codex_handoff.py` |
| Canonical rules, skills, and hooks | `.claude/rules/`, `.claude/skills/`, `.claude/hooks/` |

The hook adapter normalizes Grok tool names to the Claude hook contract:

| Grok name or alias | Canonical hook name |
|---|---|
| `Write`, `write`, `write_file` | `Write` |
| `Edit`, `edit`, `edit_file` | `Edit` |
| `MultiEdit`, `multi_edit` | `MultiEdit` |
| `NotebookEdit`, `notebook_edit` | `NotebookEdit` |
| `Bash`, `bash`, `shell` | `Bash` |

Grok camelCase hook fields (`hookEventName`, `toolName`, `toolInput`,
`workspaceRoot`) and Claude snake_case fields are accepted at the adapter
boundary. Conflicting aliases, unknown tools, route mismatches, and workspace
identity mismatches are errors. PreToolUse errors deny the call.
