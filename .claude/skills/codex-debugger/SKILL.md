---
name: codex-debugger
description: Skill (not an agent) that wraps Codex CLI for deep error analysis. Used when an Opus subagent cannot localize the cause of a bug. Sends stack trace, recent diff, and relevant code to Codex; returns root-cause hypotheses, verification steps, and fix proposals.
---

# /codex-debugger

## Purpose

When an Opus subagent or the orchestrator cannot localize a bug from local context alone, escalate to Codex for deep reasoning. Returns hypotheses ranked by likelihood, with verification steps and a fix proposal.

This is a **skill**, not an agent. The internal flow is `general-purpose` agent → Codex CLI.

## When to use

- Stack trace is non-obvious or spans multiple modules
- The bug reproduces only sometimes (race condition, environment-dependent)
- The bug involves async, threading, or distributed state
- Initial investigation by `general-purpose` failed to localize

Skip when:
- The fix is visible from the stack trace + a single file read
- The bug is in a contract artifact (use `/api-build` review instead)
- The bug is a regression with a recent diff (try `git bisect` first)

## Steps

### 1. Gather context (Opus subagent)

Use `general-purpose` to collect:
- Full stack trace
- Recent git diff (last 5-10 commits or branch diff)
- The error-line file + 50 lines context
- Files imported by the error-line file (transitive once)
- Recent test output if available

### 2. Format the Codex prompt

Use the template in `.claude/docs/CODEX_HANDOFF_PLAYBOOK.md` "Debugging".

Include:
- Project stack (Zone B summary)
- Active rules
- Error output (raw)
- Recent diff
- Relevant file contents (quote sections, not entire files)
- What's already been tried

### 3. Invoke Codex

```bash
codex exec --skip-git-repo-check < /dev/null '<prompt>' 2>&1 | tee /tmp/codex-debug-<timestamp>.txt
```

Foreground; the orchestrator waits for the result.

### 4. Parse the response

Codex returns the standard contract:
- TL;DR of the most likely cause
- Analysis of evidence
- Plan with hypotheses ranked
- Code (diff) for the proposed fix when applicable
- Validation (how to verify)
- Risks
- Confidence per hypothesis

### 5. Verify the top hypothesis

For each hypothesis (highest first):
- Run the proposed verification command
- Check whether the symptom changes as predicted
- If verified, apply the fix; if not, move to next hypothesis

### 6. Apply the fix

Via Edit / Write — the orchestrator applies, not Codex directly. Add a regression test that would have caught this.

### 7. Persist

Save the Codex response to `.claude/logs/reviews/debug-<incident>-<timestamp>.md` for history and post-mortem use.

## Output

- Codex response (saved)
- Applied fix (with regression test)
- Verification log

## Hand-off

- Production-impacting issue → `/incident-backend` (backend) or `/incident-response` (frontend)
- Architecture-level issue revealed by debug → `/architecture-review`
- Schema / migration cause → `data-engineer`

## Notes

- Pipe `< /dev/null` always — codex hangs on stdin in non-interactive contexts otherwise.
- Persist the prompt + response together for post-mortem learning.
- If Codex confidence is L on the top hypothesis, present alternatives to the user instead of acting silently.
