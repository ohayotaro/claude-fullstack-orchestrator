# Rule: Document Lifecycle

Each document has a single source-of-truth role and explicit update triggers. Drift detection runs in `/checkpointing`.

## Document roles

| Document | Source of truth for | Update trigger |
|---|---|---|
| `CLAUDE.md` Zone A | orchestration policy | template version bump only |
| `CLAUDE.md` Zone B | project stack and active rules | `/init-webdev`, `/backend-init`, manual edit when stack changes |
| `CLAUDE.md` Zone C | active work context | session changes, `/checkpointing` rotation |
| `DESIGN.md` | template architectural decisions | when policy changes (route, agent, skill) |
| `README.md` | how to install / use the template | when distribution flow or prerequisites change |
| `.claude/docs/CODEX_HANDOFF_PLAYBOOK.md` | Codex prompt templates | when delegation patterns change |
| `.claude/docs/GEMINI_HANDOFF_PLAYBOOK.md` | Gemini prompt templates | when output schemas change |
| `design/decisions/*.md` (project) | architectural decision records | per significant decision |
| `api_specs/` (project) | external API integration docs | when integrating or upgrading external API |

## Drift detection (run during `/checkpointing` Step N)

Trigger an alert if any of the following:

1. Zone C exceeds N entries (default 10) — needs rotation/archive
2. `DESIGN.md` references file paths or commands that no longer exist
3. `api_specs/` mentions endpoints absent from current code
4. A skill referenced in CLAUDE.md is missing under `.claude/skills/`
5. `routing-keywords.json` references an agent name no longer in `.claude/agents/`

Each alert lists the gap and the responsible doc.

## Update protocol

- Documentation update accompanies any policy / contract change in the same commit when feasible
- Conflicting updates between Zone A and Zone B: Zone A wins; Zone B narrows
- DESIGN.md updates use a version bump comment in the header
