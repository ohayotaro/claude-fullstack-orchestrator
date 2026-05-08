# Gemini Handoff Playbook

Templates for delegating to Gemini CLI from skills and agents. All Gemini prompts are English; output is structured JSON validated against the schemas in `.gemini/GEMINI.md`.

## Generic invocation

```bash
gemini chat --json '<prompt>' < /dev/null
```

(Adjust to the actual `gemini` CLI invocation form on this system; the output should be machine-readable JSON.)

## Template: design-extract (tokens)

```
Extract design tokens from <input-path>.

Goal: tokens-only | screen-only | both

Output format (MANDATORY): JSON only, conforming to the schema in
.gemini/GEMINI.md "Token extraction" / "Screen decomposition".

For every value, include a confidence field (high | medium | low).
Flag fields requiring human approval (interaction details, error
states, hover/active states, wording, motion).

Confidence rubric:
- high: clearly visible and unambiguous
- medium: visible but with reasonable variance (e.g., color sampled
  from a small region; font weight inferred from glyph metrics)
- low: inferred from incomplete information

Do NOT generate values; only extract what is observable.
```

## Template: design-research (competitor analysis)

```
Analyze the UI in <input-path> for a competitive comparison.

For each:
1. Layout structure: regions, hierarchy, content density
2. Visual identity: color palette, typography, spacing rhythm,
   imagery style
3. Interaction surface: visible buttons / inputs / selectors / states
4. Accessibility considerations visible in the design (contrast,
   target size, focus indication)
5. Notable patterns worth replicating or avoiding (with rationale)

Output: JSON with sections for each numbered item, plus
confidence_overall and human_approval_required.
```

## Template: visual-verify (diff judgment)

```
Compare baseline image at <baseline-path> to candidate at
<candidate-path>.

Context: <what changed in the code; what change you should expect>

Tolerance hints:
- Font rendering jitter and 1-2 px positional drift: minor
- Color tokens reflowing / typography metric changes: major
- Layout shifts of >4 px: major
- New / missing UI elements: major

Output (MANDATORY JSON, schema in .gemini/GEMINI.md "Visual diff"):
- regions_changed: array of {bbox, severity, description}
- verdict: pass | review | fail
- confidence: high | medium | low
- human_approval_required: array of strings

Verdict rules:
- pass: only minor differences and confidence == high
- review: any major difference OR confidence == low
- fail: layout broken, content missing, or contract-breaking visual
```

## Template: PDF brand guideline reading

```
Read the brand guideline at <pdf-path> and extract:
1. Primary / secondary / accent palette (with values, prefer named
   tokens if present)
2. Typography system (typefaces, hierarchy, weights, sizes)
3. Spacing / layout grid if specified
4. Iconography / illustration style (descriptive, not generative)
5. Voice and tone notes (if present)
6. Logo usage rules (if present)

Output: JSON, sections per topic. Confidence per field. Items the
guideline does NOT cover should be omitted, not invented.

human_approval_required: any inferred mapping to design tokens.
```

## Template: ER diagram analysis

```
Read the ER diagram at <input-path> and produce a textual data
model.

Output JSON:
{
  "entities": [
    {
      "name": "User",
      "fields": [{"name": "id", "type": "UUID", "constraints": ["PK"]}],
      "confidence": "high"
    }
  ],
  "relationships": [
    {"from": "User", "to": "Order", "cardinality": "1:N", "via": "user_id"}
  ],
  "confidence_overall": "...",
  "human_approval_required": ["unspecified field types", "..."]
}

Do NOT invent fields or types not visible in the diagram.
```

## Template: Architecture diagram analysis

```
Read the architecture diagram at <input-path> and produce a textual
component / dependency graph.

Output JSON:
{
  "components": [{"name": "Web App", "kind": "service|store|queue|cdn|...", "stack": "..."}],
  "edges": [{"from": "Web App", "to": "API", "kind": "http|grpc|queue|read|write|...", "label": "..."}],
  "boundaries": [{"name": "VPC-A", "contains": ["Web App", "API"]}],
  "confidence_overall": "...",
  "human_approval_required": ["..."]
}
```

## Template: Long-document summarization

```
Summarize <input-path> for an engineering audience.

Provide:
1. TL;DR (3 lines)
2. Key claims (5-10 bullets) with section references
3. Assumptions / context the document depends on
4. Open questions / gaps
5. Implications for our project (if any)

Output JSON with each section as a field. Confidence per major claim.
```

## Notes

- Persist raw Gemini output to `.claude/logs/gemini/<timestamp>.txt`. The structured JSON is the consumable artifact.
- When `confidence_overall == "low"`, the orchestrator MUST surface to the user before any agent acts on the result.
- Do NOT use Gemini for code generation tasks — that is Codex's domain.
- Visual generation is out of scope.

## Figma: prefer MCP over visual analysis

When the input is a Figma URL / file key AND the `figma-dev-mode` MCP server is reachable (registered in `.claude/settings.json`, Figma Desktop running with Dev Mode MCP enabled), use the MCP path instead of Gemini visual analysis:

- `get_variable_defs` returns authoritative design Variables — use as source-of-truth tokens (`confidence: high`) rather than approximating from pixels
- `get_code` and `get_code_connect_map` reveal which Figma components are already wired to code components
- `get_image` provides a visual record alongside the structured data

Fall back to Gemini only when MCP is unavailable or the input is a static export. Both `/design-extract` and `/design-research` already encode this preference.
