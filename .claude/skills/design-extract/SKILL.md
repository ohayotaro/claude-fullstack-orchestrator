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
- Live Figma file analysis when Dev Mode MCP is available (preferred over static export)

## Source of truth (preferred order)

1. **Figma Dev Mode MCP** (if available): live read of layers, components, design Variables, Code Connect mappings. Highest fidelity.
2. **Figma static export** (PNG / SVG / PDF): Gemini visual analysis. Useful when MCP is not configured or the user only has assets, not file access.
3. **Competitor / brand reference**: Gemini visual analysis.

The `figma-dev-mode` MCP server is registered in `.claude/settings.json`. When reachable (Figma Desktop running with Dev Mode MCP enabled at `http://127.0.0.1:3845/mcp`), prefer the MCP path. Otherwise fall back to Gemini.

## Prerequisites

- For static-export path: input file (image / PDF page) on disk; provide its path
- For MCP path: Figma Desktop running with Dev Mode MCP enabled, plus the Figma URL / file key / node id of the target

## Steps

### 1. Decide path

Check whether the `figma-dev-mode` MCP server is reachable. If yes AND the input is a Figma URL / file key, prefer the MCP path. Otherwise use the Gemini static-export path.

### 1a. MCP path (live Figma)

Use the Figma Dev Mode MCP tools (typically `get_code`, `get_image`, `get_variable_defs`, `get_code_connect_map`):

- `get_variable_defs` → dump design Variables → map directly to `design/extracted/<source>-tokens.json` with `confidence: high` (these are the source of truth)
- `get_code` on the selected frame → returns suggested code structure that informs the screen schema
- `get_image` → snapshot for the visual record
- `get_code_connect_map` → resolve which Figma components are already wired to code components

When MCP gives authoritative data (Variables, Code Connect), confidence is `high` for those fields and `human_approval_required` only flags genuinely ambiguous interactive details.

Skip steps 2 and 3 (they are for the Gemini path); jump to step 5 with the MCP-derived JSON.

### 1b. Validate the static-export input (Gemini path)

- File exists and is a supported format (PNG / JPG / SVG / PDF page)
- Resolution is reasonable (>=1024px on the long side); if low, warn and proceed with reduced confidence

### 2. Determine the extraction goal

Use `AskUserQuestion`:

- `tokens-only`: just produce token JSON
- `screen-only`: just produce screen decomposition
- `both` (default): produce both

### 3. Delegate to Gemini (static-export path only)

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
