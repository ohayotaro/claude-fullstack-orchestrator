---
name: gemini-system
description: Tool adapter for direct Gemini CLI invocation. Use for one-off multimodal analysis that does not fit /design-research, /design-extract, or /visual-verify. Always returns structured JSON per .gemini/GEMINI.md schemas with confidence ratings and human_approval_required.
---

# /gemini-system

## Purpose

A thin wrapper around `gemini` CLI for one-off multimodal analysis that does not fit a dedicated skill. Encodes the structured-output contract so consumers always receive parseable JSON.

## When to use

- Ad-hoc image / PDF / video analysis
- One-off competitor / reference comparison without full `/design-research` flow
- Reading a long internal doc for summarization
- Any task that requires multimodal input but doesn't have a specific skill

For dedicated tasks, prefer:
- `/design-research` (visual reference comparison)
- `/design-extract` (token / screen extraction)
- `/visual-verify` (baseline diff judgment)
- `/visual-regression` (full-sweep)

## Steps

### 1. Compose the prompt in English

Gemini prompts are English (agent-to-agent rule). State explicitly that the response must be JSON.

```
You are Gemini CLI invoked from <project-name>.

Input: <file path or URL>

Task:
<the actual ask>

Respond as JSON only, conforming to the schemas in .gemini/GEMINI.md.
For every field, include confidence (high | medium | low).
Items requiring human judgment go in human_approval_required.

Do NOT generate visual content. Analysis only.
```

### 2. Invoke

```bash
gemini chat --json '<prompt>' < /dev/null 2>&1 | tee .claude/logs/gemini/<topic>-<timestamp>.txt
```

(Adjust to the actual Gemini CLI invocation form on the system.)

Save raw output to `.claude/logs/gemini/` for audit.

### 3. Parse the JSON

Validate against the expected schema. If JSON is malformed, retry once with stricter prompt; if it fails again, surface the raw output to the user.

### 4. Act on confidence

- `confidence_overall: high` → orchestrator may proceed
- `medium` → surface key uncertainties
- `low` → user must approve before downstream action

`human_approval_required` items are surfaced regardless of overall confidence.

### 5. Persist artifacts

- Raw output: `.claude/logs/gemini/<timestamp>.txt`
- Structured JSON (when persistent): under `design/` (for tokens / screens / research) or `.claude/logs/reviews/` (for diffs / audits)

## Output

- Structured JSON conforming to the relevant schema in `.gemini/GEMINI.md`
- Raw log saved
- Action plan based on confidence and human_approval_required

## Notes

- Gemini does NOT generate visual content — that is out of scope for this template.
- For tasks Codex can do better (architecture, code review, math), use `/codex-system`.
- Cardinality: don't send Gemini a hundred images in one prompt; batch sensibly per `.gemini/skills/` patterns.
