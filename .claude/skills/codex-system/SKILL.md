---
name: codex-system
description: Tool adapter for direct Codex CLI invocation. Wraps the < /dev/null + --skip-git-repo-check pattern that prevents stdin-wait hangs. Use when an existing skill (api-build, data-design, etc.) does not fit and a one-off Codex consultation is appropriate.
---

# /codex-system

## Purpose

A thin wrapper around `codex exec` for one-off Codex consultations that don't fit a more specific skill. Encodes the invocation hygiene (stdin redirection, git-repo check skip) so the user / orchestrator never has to remember it.

## When to use

- One-off architectural question
- Code review request that doesn't match `/api-build`, `/data-design`, `/auth-design`, `/architecture-review`, or `/team-review`
- Statistical / mathematical validation
- Library / tool comparison

For specific tasks, prefer the dedicated skill — `/codex-system` is the catch-all.

## Steps

### 1. Compose the prompt in English

Codex prompts are English (agent-to-agent rule). Use the standard contract format:

```
You are Codex CLI invoked from <project-name>.

Context:
- Stack (read CLAUDE.md Zone B): <summary>
- Active rules: <relevant ones>

Question / Task:
<the actual ask>

Respond using the standard contract:
TL;DR / Analysis / Plan / Code (if scope) / Validation / Risks / Confidence.

Aim for under <N> words.
```

### 2. Invoke

```bash
codex exec --skip-git-repo-check < /dev/null '<prompt>' 2>&1 | tee /tmp/codex-<topic>-<timestamp>.txt
```

Always:
- `< /dev/null` to avoid stdin-wait hangs
- `--skip-git-repo-check` for cases where the working dir is not a git repo (or to skip the check anyway)
- `2>&1` to capture both streams
- `tee` to persist the output

For long-running invocations (>2 min) that block the orchestrator, run in foreground anyway — using `run_in_background=true` re-introduces stdin issues. If parallelism is critical, run in a separate Bash with explicit `nohup` and `< /dev/null`.

### 3. Parse the response

Read the output file. Strip preamble (Codex banner, session ID line). Codex's actual response starts after `--------`.

### 4. Decide next action

Based on Codex's `Confidence`:
- High → orchestrator may act on the recommendation
- Medium → surface key uncertainties to user
- Low → user must approve before any agent acts

### 5. Persist

Codex output is saved to `/tmp/` by default. For decision records, copy to `.claude/docs/reviews/<topic>-<date>.md` if the consultation is non-trivial.

## Output

- Codex response (saved)
- Action plan based on Codex's Plan section
- Decision record (when applicable)

## Notes

- The stdin issue is real and recurring — never invoke Codex without `< /dev/null` in a non-interactive flow.
- Codex's read-only sandbox prevents direct mutations; the orchestrator applies changes via Edit / Write.
- For multimodal input (images, PDFs), use `/gemini-system` instead — Codex is text-only.
