Status: PASS

Summary: Added the result-artifact capture subsection to `.claude/docs/CODEX_TASK_CONTRACT.md`.

Files changed:

- [.claude/docs/CODEX_TASK_CONTRACT.md](/Users/ohayotaro/claude-fullstack/.claude/docs/CODEX_TASK_CONTRACT.md)

Material design decisions: Used the existing `###` heading style and kept the guidance concise.

Added subsection:

> ### Result Artifact Capture
>
> The runner invokes Codex with `--output-last-message <result file>`: the phase result artifact (`plan.md`, `implementation-result.md`, `review.md`) is the final message Codex emits. Any direct edit Codex makes to that result file during the run is overwritten at phase end. Therefore, the complete required output—including mandated validation transcripts and evidence—must be emitted inline as the final message, never written to the result file directly.

Validation:

- `git diff --stat` → `.claude/docs/CODEX_TASK_CONTRACT.md | 4 ++++`; `1 file changed`
- `git diff --name-only` → only `.claude/docs/CODEX_TASK_CONTRACT.md`
- `git diff --check` → passed with no output
- Runtime tests not run; documentation-only change.

Acceptance criteria:

- AC1: PASS — all three required facts are documented in a clearly headed English subsection.
- AC2: PASS — only the target document was modified. The pre-existing untracked task brief was preserved.

Residual risks, debt, or blockers: None.