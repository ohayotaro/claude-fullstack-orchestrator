# Fullstack PM/Engineering Orchestrator

> Claude Code as the user-facing PM and acceptance owner; Codex CLI as the technical lead and engineering executor. A stack-agnostic template for fullstack web / mobile / backend product development.

```text
Claude (PM)   -> Japanese user interaction, task briefs, risk tiers,
                 plan approval, visual acceptance, final accept/reject
Codex (Eng)   -> exploration, design, implementation, tests,
                 independent review, evidence
```

- **Two providers, exclusive ownership**: Claude never implements; Codex never accepts its own work
- **T0-T3 risk workflow**: plan -> approval -> implement -> independent review -> acceptance, scaled to risk
- **Canonical runner**: every Codex call goes through `.claude/scripts/codex_handoff.py` with per-phase sandboxing, artifacts, and audit logs
- **Deterministic safety hooks**: PM write guard, production deploy gate, secret scan
- **19 PM skills**: intake guides per domain (feature, UI, API, data, auth, state, jobs, infra, perf, a11y, e2e) plus flow skills (`/codex-task`, `/codex-review`, `/deploy`, `/incident-response`, `/checkpointing`, `/visual-verify`)
- **Stack-agnostic via `/init-webdev` + `/backend-init`**: stack recorded in CLAUDE.md Zone B; language rules activate accordingly

## Quick start

Install prerequisites first (see [Prerequisites](#prerequisites)). Then, in your project directory:

```bash
cd /path/to/your-project
git clone --depth 1 https://github.com/ohayotaro/claude-fullstack.git .starter \
  && cp -r .starter/.claude .starter/.codex .starter/CLAUDE.md .starter/AGENTS.md . \
  && rm -rf .starter
claude
```

Inside Claude Code:

```text
/init-webdev      # frontend / mobile setup wizard
/backend-init     # backend setup wizard (run when backend is in scope)
```

After both wizards, `CLAUDE.md` Zone B describes your stack and the relevant `lang/*` rules are activated.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Claude Code | latest | `npm i -g @anthropic-ai/claude-code` |
| Codex CLI | >=0.121 | `brew install codex` (macOS) or `npm i -g @openai/codex` |
| Git | any | system package manager |
| Python | >=3.10 | for hooks and the runner (`.claude/hooks/*.py`, `.claude/scripts/codex_handoff.py`) |

After install:

```bash
claude --version
codex --version && codex login
```

## What gets copied into your project

```text
your-project/
├── CLAUDE.md                  # PM contract (Zone A) + your stack (Zone B) + context (Zone C)
├── AGENTS.md                  # Codex engineering contract (+ project notes section)
├── .claude/
│   ├── settings.json          # hooks + permission allowlist
│   ├── scripts/               # codex_handoff.py — canonical Codex runner
│   ├── hooks/                 # pm-write-guard, deploy-gate, secret-scan, dispatcher
│   ├── rules/                 # common + per-language engineering standards
│   ├── skills/                # 19 PM skills
│   └── docs/                  # CODEX_TASK_CONTRACT.md, reviews/
└── .codex/                    # Codex CLI config (read-only sandbox, approval never)
```

Your project code (`apps/`, `packages/`, `services/`, `src/`, etc.) is left alone.

## Workflow

1. Describe what you want (Japanese is fine). Claude classifies the risk tier and writes a neutral task brief under `.claude/tasks/<task-id>/` with acceptance criteria and forbidden actions.
2. For T2/T3, Claude runs `codex_handoff.py plan`, reviews the plan against your intent, and writes `approval.md` (T3 additionally requires your explicit approval).
3. Codex implements in a workspace-write sandbox, runs tests, and reports evidence.
4. A fresh Codex invocation reviews the diff independently (`APPROVE` / `CHANGES_REQUIRED`).
5. Claude accepts or rejects: brief vs result vs review vs evidence. UI changes additionally require visual acceptance — Claude reads the captured screenshots directly.
6. Production deploys are T3: your explicit approval plus the `deploy-gate` acknowledgment.
7. Claude commits accepted work with Conventional Commits and pushes to the project remote. Destructive Git operations (history rewrite, force push, hard reset, branch deletion) stay outside PM ownership.

Task artifacts under `.claude/tasks/`, `.claude/checkpoints/`, and `.claude/plans/` are tracked in Git as the audit trail behind each acceptance. Only `.claude/tasks/*/codex-events.jsonl` (machine replay log) and `.claude/state/` (per-machine runtime state) stay local. These artifacts must never contain secrets.

## Skills

| Skill | Purpose |
|---|---|
| `/codex-task` | Canonical PM -> Codex task flow with T0-T3 gates |
| `/codex-review` | Fresh independent Codex review |
| `/feature-build` | Intake for end-to-end features (UI + API + data) |
| `/ui-build` | Intake for screens / components / design system work |
| `/api-build` | Intake for API contract work |
| `/data-design` | Intake for schema / migrations (destructive = T3) |
| `/auth-design` | Intake for auth flows (T3) |
| `/state-design` | Intake for client state architecture |
| `/job-design` | Intake for background jobs / queues |
| `/infra-review` | Intake for CI/CD, containers, observability |
| `/deploy` | T3 deploy procedure + gate acknowledgment |
| `/perf-audit` | Measurement-first performance intake |
| `/a11y-audit` | Accessibility audit intake (WCAG 2.2 AA) |
| `/e2e-test` | E2E test intake |
| `/visual-verify` | PM visual acceptance of captured screenshots |
| `/incident-response` | Production incident triage and gated mitigation |
| `/checkpointing` | PM checkpoints + Zone C rotation + drift detection |
| `/init-webdev` / `/backend-init` | Zone B setup wizards |

## Updating the template

```bash
./scripts/update.sh
```

Preserves CLAUDE.md Zone B, AGENTS.md project notes, `.claude/settings.local.json`, memory, tasks, checkpoints, plans, state, logs, and `.claude/docs/reviews/`. Overwrites template policy, hooks, rules, skills, and the runner.

## Language protocol

| Target | Language |
|---|---|
| User interaction | Japanese |
| Task artifacts, code, commits | English |
| Project docs | English unless requested otherwise |
