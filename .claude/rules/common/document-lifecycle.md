# Rule: Document Lifecycle

Each document has a single source-of-truth role and explicit update triggers. Drift detection runs in `/checkpointing`.

## Document roles

| Document | Source of truth for | Update trigger |
|---|---|---|
| `CLAUDE.md` Zone A | PM/engineering orchestration policy | template version bump only |
| `CLAUDE.md` Zone B | project stack and active rules | `/init-webdev`, `/backend-init`, manual edit when stack changes |
| `CLAUDE.md` Zone C | active work context | session changes, `/checkpointing` rotation |
| `AGENTS.md` | Codex engineering contract | when delegation policy or correctness rules change |
| `.claude/docs/CODEX_TASK_CONTRACT.md` | task schema, risk tiers, runner usage | when the handoff protocol changes |
| `DESIGN.md` | template architectural decisions (ADRs) | when policy changes |
| `README.md` | how to install / use the template | when distribution flow or prerequisites change |
| `.claude/docs/reviews/*.md` | commit-worthy review and incident records | per accepted T2/T3 task or incident |
| `.claude/tasks/<id>/` (gitignored) | per-task working artifacts | per task |

## Drift detection (run during `/checkpointing`)

Trigger an alert if any of the following:

1. Zone C exceeds 10 entries — needs rotation/archive
2. `DESIGN.md` references file paths or commands that no longer exist
3. A skill referenced in CLAUDE.md is missing under `.claude/skills/`
4. `AGENTS.md` repository commands disagree with Zone B Key Commands

Each alert lists the gap and the responsible doc.

## Update protocol

- Documentation update accompanies any policy / contract change in the same commit when feasible
- Conflicting updates between Zone A and Zone B: Zone A wins; Zone B narrows
- DESIGN.md updates use a version bump comment in the header
