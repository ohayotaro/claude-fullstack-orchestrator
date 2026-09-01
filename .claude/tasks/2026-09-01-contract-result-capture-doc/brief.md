# 2026-09-01-contract-result-capture-doc: Document result-artifact capture mechanism in the task contract

## Objective

Prevent recurrence of the empty-evidence-artifact failure mode discovered in task `2026-09-01-grok-pm-adapter`: Codex phases that edit their result file directly get it silently overwritten, because the runner captures the phase result from Codex's final message.

## Scope

Edit `.claude/docs/CODEX_TASK_CONTRACT.md` only. In the "Implementation Output" section (and "Plan Output"/"Review Output" if a shared note fits better), add a short subsection stating:

1. The runner invokes Codex with `--output-last-message <result file>`: the phase result artifact (`plan.md`, `implementation-result.md`, `review.md`) IS the final message Codex emits.
2. Any direct edit Codex makes to that result file during the run is overwritten at phase end.
3. Therefore the complete required output — including any mandated validation transcripts and evidence — must be emitted inline as the final message, never written to the result file directly.

Keep it to one short subsection (roughly 3-6 lines), matching the document's existing tone and heading style.

## Non-Goals

- No changes to `codex_handoff.py` or any other file.
- No behavior change; documentation only.

## Acceptance Criteria

- AC1: `CODEX_TASK_CONTRACT.md` contains the three facts above in a clearly headed subsection, in English, consistent with the document's style.
- AC2: No other file is modified.

## Constraints And Context

- Root cause reference: `.claude/tasks/2026-09-01-grok-pm-adapter/approval.md` Addendum 7b; runner behavior at `codex_handoff.py` (`--output-last-message`, line ~544).
- Delivery reminder (self-referential): this very phase's result is captured from your final message — emit your implementation result inline.
- Network access: not required.

## Risk Tier

T1 - single-file documentation change, no runtime impact.

## Required Validation

- Quote the added subsection verbatim in the implementation result.
- `git diff --stat` output showing only `CODEX_TASK_CONTRACT.md` changed.

## Forbidden Actions

- No edits outside `.claude/docs/CODEX_TASK_CONTRACT.md`; no commits; no network.

## Open Decisions Or Blockers

None.
