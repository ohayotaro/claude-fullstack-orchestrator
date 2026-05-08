# Fullstack AI Orchestrator

> Claude Code (Opus 4.7, 1M context) as orchestrator, coordinating Codex CLI and Gemini CLI as specialized agents for fullstack web/mobile/backend product development. Stack-agnostic — bring your own framework.

```
Claude Code (Orchestrator) ─┬─ Codex CLI       (architecture, contracts, debugging)
                             ├─ Gemini CLI      (UI / Figma / PDF / diagram analysis)
                             └─ Opus subagents  (exploration, implementation, review, parallel work)
```

- **14 role-based agents** (frontend, design system, state, mobile native, QA, a11y, perf, plus backend: api / data / auth-security / infra / job)
- **29 skills** across feature kickoff, parallel implementation, multi-track review, visual verification, design analysis, and ops
- **31 rules** in `common/` + per-language (`typescript`, `node-typescript`, `python`, `swift`, `kotlin`, `dart`)
- **10 hooks** with explicit severity (`suggest` / `warn` / `require-explicit-override`), including secret scan, contract-edit warning, migration check
- **Stack-agnostic via `/init-webdev` + `/backend-init`**: framework, languages, state lib, DB, auth, deploy target all chosen at init time and recorded in CLAUDE.md Zone B

## Quick start

Install prerequisites first (see [Prerequisites](#prerequisites)). Then, in your project directory:

```bash
cd /path/to/your-project
git clone --depth 1 https://github.com/ohayotaro/claude-fullstack-orchestrator.git .starter \
  && cp -r .starter/.claude .starter/.codex .starter/.gemini .starter/CLAUDE.md . \
  && rm -rf .starter
claude
```

Inside Claude Code:

```
/init-webdev      # frontend / mobile setup wizard
/backend-init     # backend setup wizard (run when backend is in scope)
```

After both wizards, `CLAUDE.md` Zone B describes your stack and the relevant `lang/*` rules are activated.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Claude Code | latest | `npm i -g @anthropic-ai/claude-code` |
| Codex CLI | ≥0.121 | `brew install codex` (macOS) or `npm i -g @openai/codex` |
| Gemini CLI | ≥0.38 | `npm i -g @google/gemini-cli` |
| Git | any | system package manager |
| Python | ≥3.10 | for hooks (`.claude/hooks/*.py`) |
| Figma Desktop (optional) | latest | for live Figma access via the `figma-dev-mode` MCP server registered in `.claude/settings.json`. Enable in Figma Desktop → Preferences → "Enable Dev Mode MCP Server" (requires Pro/Org/Enterprise + Dev Mode). When unreachable, `/design-extract` and `/design-research` fall back to Gemini static-export analysis. |

After install:

```bash
claude --version
codex --version  && codex login
gemini --version && gemini login
```

## What gets copied into your project

```
your-project/
├── CLAUDE.md                  # 3-Zone orchestrator contract
├── .claude/
│   ├── settings.json          # hooks + env + permission allowlist
│   ├── agents/                # 14 role-based Opus subagents
│   ├── hooks/                 # 10 Python hooks
│   ├── rules/                 # 13 common + 18 lang rules
│   ├── skills/                # 29 skill definitions
│   └── docs/                  # CODEX / GEMINI handoff playbooks
├── .codex/                    # Codex CLI contract + config
└── .gemini/                   # Gemini CLI contract + config
```

Your project code (`apps/`, `packages/`, `services/`, `src/`, etc.) is left alone. The template owns nothing outside the four targets above.

## Workflow

```
/start-feature → /team-implement → /team-review
                       ↓
                 /visual-verify (UI features)
```

Detailed pipelines:

```
Frontend feature:  /start-feature → /team-implement → /team-review → /visual-verify
Design (analyze):  /design-research → /design-extract → /component-build → /screen-build
Backend feature:   /api-build → /data-design → /auth-design → /team-review
Quality:           /a11y-audit, /perf-audit, /visual-regression, /architecture-review, /infra-review
Operations:        /codex-debugger, /incident-backend, /incident-response, /checkpointing
```

See `DESIGN.md` for the full architecture, routing policy, and rationale.

## Skills

| Category | Skills |
|---|---|
| Setup | `/init-webdev`, `/backend-init` |
| Feature pipeline | `/start-feature`, `/team-implement`, `/team-review`, `/architecture-review` |
| Design (analysis) | `/design-research`, `/design-extract`, `/component-build`, `/screen-build` |
| State / API / data / auth | `/state-design`, `/api-build`, `/data-design`, `/auth-design` |
| Backend specialty | `/job-design`, `/infra-review` |
| Quality | `/visual-verify`, `/visual-regression`, `/a11y-audit`, `/perf-audit`, `/e2e-test` |
| Ops | `/deploy`, `/codex-debugger`, `/incident-response`, `/incident-backend`, `/checkpointing` |
| Adapters | `/codex-system`, `/gemini-system`, `/parallel-batch` |

## Updating the template

Run `scripts/update.sh` from your project root. It backs up Zone B and your custom config, pulls the latest template, then restores the backups.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ohayotaro/claude-fullstack-orchestrator/main/scripts/update.sh)
```

Or, if you cloned the template into `.starter/` for inspection:

```bash
.starter/scripts/update.sh
```

## Architecture

```
┌────────────────────────────────────────────────────────┐
│      Claude Code (Opus 4.7, 1M)  — Orchestrator        │
├──────────────────┬──────────────┬──────────────────────┤
│  Opus Subagents  │  Codex CLI    │  Gemini CLI          │
│ exploration      │ architecture  │ multimodal           │
│ implementation   │ debugging     │ visual diff          │
│ review           │ contracts     │ Figma / PDF / video  │
│ parallel work    │ statistics    │ ER / arch diagrams   │
└──────────────────┴──────────────┴──────────────────────┘
```

- **Codex** receives English-only structured prompts (see `.claude/docs/CODEX_HANDOFF_PLAYBOOK.md`) and returns the standard contract: TL;DR → Analysis → Plan → Validation → Risks → Confidence.
- **Gemini** receives multimodal input and returns structured JSON (schemas in `.gemini/GEMINI.md`) with confidence ratings and `human_approval_required` flags.
- **Opus subagents** are role-named, stack-agnostic, and read CLAUDE.md Zone B at runtime.

## Language protocol

| Channel | Language |
|---|---|
| Orchestrator ↔ User | Japanese OR English (user preference) |
| Agent ↔ Agent | English (fixed) |
| Code / commit / docs | English (fixed) |

## Provenance

Modeled after the same author's [`claude-orchestrator`](https://github.com/ohayotaro/claude-orchestrator) (financial-trading specialization) with structural cues from [`DeL-TaiseiOzaki/claude-code-orchestra`](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) (multi-agent dev environment) and the multi-language rules layout from [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code). v0.3 design and decisions reviewed by Codex CLI (records in `DESIGN_REVIEW_codex_2026-05-09.md` and `DESIGN_DECISIONS_codex_2026-05-09.md`).

## License

This template is yours to use however you like. The agents, skills, rules, and prompts are released into your project alongside your own license — pick one that suits the project (MIT / Apache 2.0 / etc.).
