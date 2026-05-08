# Rule: Gemini Delegation

Gemini CLI (Gemini 2.5 Pro) is the multimodal external agent. Use for input that requires visual or document understanding.

## When to delegate to Gemini

- UI screenshot comparison (competitor / baseline / candidate)
- Figma export decomposition (token JSON, screen schema)
- Brand guideline PDF reading
- Long-document summarization (research papers, RFCs)
- ER diagram analysis
- Architecture diagram analysis
- Video / audio analysis (when applicable)

## When NOT to delegate to Gemini

- Pure text reasoning → Codex
- Code-only tasks → Opus subagent or Codex
- Generating new visual content → out of scope (no image-gen path in v0.1)

## Invocation pattern

Wrapped through `visual-analyst` agent or directly via `/gemini-system`, `/design-research`, `/design-extract`, `/visual-verify` skills.

## Output contract (mandatory)

All Gemini-driven skills emit structured JSON, validated against the skill's schema. Common envelope:

```json
{
  "task": "design-extract | visual-verify | research | ...",
  "result": { },
  "confidence_overall": "high | medium | low",
  "human_approval_required": ["..."],
  "raw_output_path": ".claude/logs/gemini/<timestamp>.txt"
}
```

### Specific schemas

- `/design-extract` → token JSON + screen decomposition schema (per `.claude/skills/design-extract/SKILL.md`)
- `/visual-verify` → diff result JSON with `verdict: pass | review | fail`
- `/design-research` → structured comparison JSON

## Confidence handling

- `high`: orchestrator may proceed with the result
- `medium`: orchestrator should surface key uncertainties to the user before acting
- `low`: orchestrator MUST treat as advisory; user approval required before any agent acts

`human_approval_required` items are always surfaced regardless of confidence.

## Persisted artifacts

Raw Gemini output is saved to `.claude/logs/gemini/<timestamp>.txt` for audit. The structured JSON is the consumable artifact.

## Hand-off

- Wrapper agent: `visual-analyst`
- Skills that wrap Gemini: `/gemini-system`, `/design-research`, `/design-extract`, `/visual-verify`
- Hook that suggests Gemini: `suggest-gemini-visual.py`
