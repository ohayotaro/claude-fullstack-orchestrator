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
git clone --depth 1 https://github.com/ohayotaro/claude-fullstack.git .starter \
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

29 skills organized by purpose. Full spec for each is at `.claude/skills/<name>/SKILL.md`. The "Owner" column lists the agent or external CLI that performs the heavy work; the orchestrator drives the flow but does not implement.

### Setup

| Skill | Purpose | Owner |
|---|---|---|
| `/init-webdev` | Frontend / mobile wizard. Asks framework, styling, state lib, testing tools, monorepo; populates CLAUDE.md Zone B and `active_rules.lang`. | — |
| `/backend-init` | Backend wizard. Asks scope, language(s), framework, API style, DB engine + ORM + migration tool, cache, broker, blob storage, auth mode, deploy target, observability stack. | — |

### Feature pipeline

| Skill | Purpose | Owner |
|---|---|---|
| `/start-feature` | Multi-agent feature kickoff: codebase exploration → parallel research → Codex design → plan integration with user approval. | general-purpose + Codex |
| `/team-implement` | Agent Teams parallel implementation across disjoint file scopes; per-teammate completion logs to `.claude/logs/agent-teams/`. | role-specific agents |
| `/team-review` | 5-track parallel review — Security, Quality, a11y, Perf, Architecture — with deduplicated, prioritized findings. | Codex per track |
| `/architecture-review` | Focused review of state / navigation / package / service boundaries and contract drift; usable standalone or as `/team-review`'s 5th track. | state-architect + api-engineer + Codex |

### Design (analysis-only — no generation)

| Skill | Purpose | Owner |
|---|---|---|
| `/design-research` | Structured analysis of references (competitor screenshots, brand decks, Figma frames). Returns layout / visual identity / interaction surface / a11y cues / patterns with confidence ratings. | visual-analyst → Gemini (or Figma MCP) |
| `/design-extract` | Token JSON + screen decomposition. Prefers Figma Dev Mode MCP (live Variables, Code Connect mappings); falls back to Gemini static-export analysis. | visual-analyst → Figma MCP / Gemini |
| `/component-build` | Single design-system component: primitives, preview/storybook, a11y semantics built in, unit + a11y tests. | design-system-engineer |
| `/screen-build` | Feature-screen composition consuming primitives, wired with state + navigation + data fetching. Explicit loading / error / empty states. | ui-engineer |
| `/state-design` | State architecture decision (server / URL / local / global) per Zone B `state_lib`; Codex review for non-trivial cases. | state-architect + Codex |

### Backend

| Skill | Purpose | Owner |
|---|---|---|
| `/api-build` | API endpoint or service. Phase 1 contract (with Codex review) → Phase 2 handler / validation / errors → Phase 3 tests + observability. BFF mode when `backend_scope=bff-only`, full-backend mode otherwise. | api-engineer + Codex |
| `/data-design` | Schema / migration / index design. `migration-check.py` hook gates destructive changes; Codex review for non-trivial cases. | data-engineer + Codex |
| `/auth-design` | Auth flow — sequence diagram, token lifecycle, storage decisions, threat model. Codex reviews for OWASP-relevant concerns. | auth-security-engineer + Codex |
| `/job-design` | Background jobs / queue workers / scheduled tasks. Producer contract + broker topology + worker logic + idempotency + retry + DLQ + replay procedure. | job-engineer + Codex |
| `/infra-review` | 9-lens review: container / runtime / CI-CD / health / autoscale / network / observability / DR / cost. | infra-engineer + Codex |

### Quality

| Skill | Purpose | Owner |
|---|---|---|
| `/visual-verify` | Per-surface render-correctness check: capture screenshot → Gemini diff against baseline → verdict `pass | review | fail` with confidence. | qa-engineer + Gemini |
| `/visual-regression` | Project-wide baseline management. Sweeps surfaces from `.claude/visual-regression.json`, runs `/visual-verify` per surface, gates baseline updates on user approval. | qa-engineer + Gemini |
| `/a11y-audit` | WCAG 2.2 AA + native a11y. Runs axe-core / Lighthouse / iOS Accessibility Inspector / Android Accessibility Scanner with manual checklist for items automation misses. | a11y-auditor |
| `/perf-audit` | Measurement-first audit: Lighthouse + Bundle Analyzer (web), Instruments (iOS), Macrobenchmark (Android), DevTools (Flutter), latency p95 + query plans (backend). | perf-optimizer + Codex |
| `/e2e-test` | Generate or extend e2e tests in the project's runner — Playwright / Detox / XCUITest / Espresso / integration_test — with page-object pattern and determinism rules. | qa-engineer |

### Operations

| Skill | Purpose | Owner |
|---|---|---|
| `/deploy` | Target-aware deploy: Vercel / Cloudflare / ECS Fargate / GKE / Render / Fly / TestFlight / Play Console / etc. Pre-flight, smoke check, explicit rollback. | infra-engineer |
| `/codex-debugger` | Skill (not agent) wrapping Codex CLI for deep bug analysis when Opus subagents cannot localize. Returns ranked hypotheses + verification + fix. | general-purpose → Codex |
| `/incident-response` | Frontend / cross-cutting incident — 6 phases (stabilize → mitigate → root cause → durable fix → post-mortem → action items). Includes post-mortem template. | Codex + relevant agents |
| `/incident-backend` | Backend-focused triage with decision tree mapping symptom (5xx / latency / queue stuck / pool exhausted / replica lag / migration broken) to the right agent. | infra/data/auth/api engineers + Codex |
| `/checkpointing` | Zone C snapshot + 6 drift checks (CLAUDE.md ↔ skills/agents, contract-watch dead patterns, Zone B vs project state, routing-keywords vs agents). | — |

### Adapters

| Skill | Purpose | Owner |
|---|---|---|
| `/codex-system` | One-off Codex consultation. Encodes the `< /dev/null` + `--skip-git-repo-check` invocation that prevents stdin-wait hangs. | Codex |
| `/gemini-system` | One-off Gemini multimodal task with JSON-only output contract per `.gemini/GEMINI.md` schemas. | Gemini |
| `/parallel-batch` | High-throughput mechanical work via `general-purpose` Opus × N with disjoint file scopes. Refuses (and routes to `/team-implement`) if judgment is required. | general-purpose × N |

## Updating the template

Run `scripts/update.sh` from your project root. It backs up Zone B and your custom config, pulls the latest template, then restores the backups.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ohayotaro/claude-fullstack/main/scripts/update.sh)
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

Modeled after the same author's [`claude-finance`](https://github.com/ohayotaro/claude-finance) (financial-trading specialization) with structural cues from [`DeL-TaiseiOzaki/claude-code-orchestra`](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) (multi-agent dev environment) and the multi-language rules layout from [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code). v0.3 design and decisions reviewed by Codex CLI (records in `DESIGN_REVIEW_codex_2026-05-09.md` and `DESIGN_DECISIONS_codex_2026-05-09.md`).

## License

This template is yours to use however you like. The agents, skills, rules, and prompts are released into your project alongside your own license — pick one that suits the project (MIT / Apache 2.0 / etc.).
