---
name: design-extract
description: Extract structured design tokens and screen decomposition from an input image (Figma export, competitor screenshot, brand guideline page) via Gemini. Returns JSON with confidence ratings and human_approval_required flags. Use when starting a new visual feature with reference material.
---

# /design-extract

## Purpose

Turn a visual reference into structured, machine-readable design data:

- **Token JSON**: color, typography, spacing, radius, motion approximations
- **Screen decomposition**: regions, components, props, hierarchy

Both come with confidence ratings; uncertain items are flagged for human approval.

## When to use

- Starting a feature with a competitor or reference screenshot
- Importing a Figma export and wanting tokens + structure separately
- Reading a brand PDF page to seed the design system

## Prerequisites

- The input file (image / PDF page) is on disk; provide its path

## Steps

### 1. Validate the input

- File exists and is a supported format (PNG / JPG / PDF page)
- Resolution is reasonable (>=1024px on the long side); if low, warn and proceed with reduced confidence

### 2. Determine the extraction goal

Use `AskUserQuestion`:

- `tokens-only`: just produce token JSON
- `screen-only`: just produce screen decomposition
- `both` (default): produce both

### 3. Delegate to Gemini

Invoke the Gemini-side `/design-extract` flow (under `.gemini/skills/design-extract/`) with:

- Input file path
- Goal (tokens / screen / both)
- Schema reminder (so Gemini emits the expected JSON structure)
- Confidence rubric:
  - `high`: clearly visible and unambiguous
  - `medium`: visible but with possible variance (e.g., color sampled from a small region)
  - `low`: inferred from incomplete information

### 4. Receive structured output

**Token JSON**:
```json
{
  "tokens": {
    "color": {
      "primary": {"value": "#0F62FE", "confidence": "high"},
      "background": {"value": "#FFFFFF", "confidence": "high"},
      "text.primary": {"value": "#161616", "confidence": "high"},
      "text.secondary": {"value": "#525252", "confidence": "medium"}
    },
    "spacing": {"scale": [4, 8, 16, 24, 32], "confidence": "medium"},
    "typography": {
      "h1": {"size": 32, "weight": 600, "lineHeight": 1.25, "confidence": "high"}
    },
    "radius": {"sm": 4, "md": 8, "lg": 16, "confidence": "high"}
  },
  "source": "<input-path>",
  "confidence_overall": "high|medium|low",
  "human_approval_required": ["color tokens with low confidence", "typography scale beyond h1"]
}
```

**Screen decomposition**:
```json
{
  "screen": "<inferred-name>",
  "regions": [
    {"name": "header", "bbox": [0, 0, 1024, 80], "components": ["Logo", "NavBar", "AvatarMenu"]}
  ],
  "components": [
    {"type": "Input", "props": {"placeholder": "Email", "type": "email"}, "confidence": "high"}
  ],
  "human_approval_required": ["interaction details", "error states", "hover/active states", "wording / i18n"]
}
```

### 5. Persist artifacts

- Token JSON → `design/extracted/<source-name>-tokens.json`
- Screen JSON → `design/extracted/<source-name>-screen.json`
- Raw Gemini output → `.claude/logs/gemini/<timestamp>.txt`

### 6. Surface to user

Print a summary with confidence breakdown. If `confidence_overall == low` or any `human_approval_required` items remain, prompt the user to confirm before downstream agents act on the data.

## Output

- `design/extracted/*-tokens.json`
- `design/extracted/*-screen.json`
- Raw log

## Hand-off

- Tokens → `design-system-engineer` to merge into the project's token source-of-truth (after user approval of new values)
- Screen → `ui-engineer` (for `/screen-build`) or `design-system-engineer` (if new primitives needed)

## Notes

- Gemini approximates colors and sizes — never treat output as authoritative without human verification.
- The orchestrator does NOT generate visuals. This skill is analysis-only.
