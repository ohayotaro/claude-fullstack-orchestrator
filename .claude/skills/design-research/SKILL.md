---
name: design-research
description: Gemini-led analysis of visual references (competitor screenshots, brand decks, mood boards, Figma exports). Returns structured comparison data with confidence ratings. Run early in /start-feature when references are available.
---

# /design-research

## Purpose

Turn visual references into structured engineering input. Identifies layout patterns, visual identity, interaction surface, accessibility cues, and notable patterns. Pure analysis — no generation.

## When to use

- New feature with competitor references the user wants to study
- Brand redesign or new product surface where we want to internalize references
- Pre-`/design-extract` step when the goal is "understand first, then extract"

## Inputs

- One or more image files (`.png`, `.jpg`, `.webp`) or PDFs
- Or live Figma frames via the `figma-dev-mode` MCP server (when registered in `.claude/settings.json` and Figma Desktop is running with Dev Mode MCP enabled)
- Optional: a list of focus questions (what specifically to compare)

## MCP vs static export

For competitor analysis the input is usually a static screenshot — use the Gemini path. For analyzing your own designs in Figma, the MCP path gives authoritative Variables / component data; use it when comparing your current design to a target.

## Steps

### 1. Validate inputs

- File paths exist
- Resolution adequate (>=1024px on long side preferred)
- Combine into a single Gemini call when possible (Gemini handles multi-image well)

### 2. Delegate to Gemini

Use the prompt template in `.claude/docs/GEMINI_HANDOFF_PLAYBOOK.md` "design-research". Pass:
- Each input file path
- Focus questions (or default analysis frame)

### 3. Parse JSON output

Expected schema:

```json
{
  "task": "design-research",
  "result": {
    "layout": [...],
    "visual_identity": {...},
    "interaction_surface": [...],
    "accessibility_cues": [...],
    "notable_patterns": [...],
    "comparisons": [...]
  },
  "confidence_overall": "...",
  "human_approval_required": [...]
}
```

### 4. Persist artifacts

- JSON → `design/research/<topic>-<date>.json`
- Raw Gemini output → `.claude/logs/gemini/<timestamp>.txt`

### 5. Surface to user

Present the structured result with a summary. Highlight:
- Patterns worth replicating (with rationale)
- Patterns worth avoiding (with rationale)
- Items requiring human judgment (motion, copy, brand tone)

## Output

- `design/research/*.json`
- Raw log
- Summary in conversation

## Hand-off

- Token / screen extraction → `/design-extract`
- Component creation from research → `/component-build` or `/screen-build`
- Strategy decision (e.g., "should we copy this nav pattern?") → escalate to user; do not decide silently

## Notes

- Gemini's role is descriptive. Do NOT use this skill for "what should we build" — that is a user decision informed by the research.
- For each notable pattern, include a confidence rating; low-confidence patterns are advisory.
