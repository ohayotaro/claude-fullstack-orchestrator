# Fullstack PM/Engineering Orchestrator — Specification

Version 0.4.1 | 2026-07-12

## 1. Overview

Claude Code acts as the **user-facing PM, change controller, and acceptance owner**. Codex CLI acts as the **technical lead and engineering executor**. This is a general-purpose template for fullstack product development (web / mobile / backend), stack-agnostic via CLAUDE.md Zone B.

```text
Claude (PM)  -> Japanese user interaction, neutral task briefs, risk tiers,
                plan approval, visual acceptance, final accept/reject
Codex        -> repository exploration, technical design, implementation,
                tests, independent review, evidence
```

Design principles:

1. Claude never implements, explores broadly, or edits source/config directly. It writes only PM artifacts.
2. Codex owns everything engineering, driven by a neutral task brief with stable acceptance criteria.
3. Risk tiers (T0-T3) decide the workflow depth; hooks enforce only deterministic safety rules.
4. UI correctness is two-layer: code correctness (Codex validation) + render correctness (Claude visual acceptance of screenshots).
5. Two languages: Japanese with the user, English in every artifact.

## 2. Architecture

### 2.1 Role split

Defined normatively in `CLAUDE.md` (Claude side) and `AGENTS.md` (Codex side). The canonical handoff protocol is `.claude/docs/CODEX_TASK_CONTRACT.md`.

### 2.2 Risk workflow

| Tier | Flow |
|---|---|
| T0 | Advisory / no mutation. Claude answers directly; read-only Codex for substantial inspection. |
| T1 | Localized change. One Codex implementation run + self-review; Claude accepts. |
| T2 | Code / multi-file / architecture / contract changes. Codex plan -> Claude approval -> Codex implementation -> fresh Codex review -> Claude acceptance. |
| T3 | Production deploy, destructive migration, secrets/auth, external side effects. T2 + explicit user approval before implementation or external action. |

### 2.3 Runner

`.claude/scripts/codex_handoff.py` centralizes all Codex invocations:

- `codex exec --strict-config --sandbox {read-only|workspace-write} --cd <root> --ephemeral --json --output-last-message <path> -`
- Prompts via stdin; phase templates baked into `prompt_for_phase()`
- Read-only sandbox for plan/review, workspace-write for implement
- Model precedence: CLI > phase env > general env > optional T0 read-only `CODEX_FAST_MODEL` > omitted model flag
- Effort precedence: CLI > phase env > general env > risk-tier default matrix (T0/T1 medium, T2 high, T3 xhigh; T3 fails closed below xhigh unless lower effort is deliberately supplied by CLI)
- Phase timeout: `CODEX_PHASE_TIMEOUT_SECONDS`, default `3600` seconds, applies to `plan`, `implement`, and `review`
- Artifacts per task: `brief.md`, `plan.md`, `approval.md`, `implementation-result.md`, `review.md`, `state.json`, `codex-events.jsonl`
- Forbidden flags (`--full-auto`, `--yolo`, `--dangerously-bypass-approvals-and-sandbox`) are refused

### 2.4 Hooks (deterministic safety only)

| Hook | Event | Purpose |
|---|---|---|
| `pm-write-guard.py` | PreToolUse Edit\|Write\|MultiEdit\|NotebookEdit | Blocks Claude writes outside PM paths (`.claude/tasks|checkpoints|plans|state|docs/reviews`, `README.md`, `CLAUDE.md`) |
| `secret-scan.py` | PreToolUse Edit\|Write\|MultiEdit\|NotebookEdit | Blocks writes containing secret-like values |
| `deploy-gate.py` | PreToolUse Bash | Blocks production deploy / publish / prod-env commands without a 24h acknowledgment; `DEPLOY_FREEZE` freezes all deploys |
| `post-bash-dispatcher.py` | PostToolUse Bash | Runs `error-to-codex.py` (error patterns -> brief-flow suggestion) and `log-cli-tools.py` (CLI telemetry) |
| PreCompact echo | PreCompact | Reminds Claude to reload contracts and the current brief |

### 2.5 Skills (19, all PM intake or PM procedure)

- Canonical flow: `codex-task`, `codex-review`
- PM operations: `checkpointing`, `incident-response`, `visual-verify`, `deploy`
- Setup wizards: `init-webdev`, `backend-init`
- Domain intakes (brief authoring guides): `feature-build`, `ui-build`, `api-build`, `data-design`, `auth-design`, `state-design`, `job-design`, `infra-review`, `perf-audit`, `a11y-audit`, `e2e-test`

Every domain intake ends with a Delegation section: create the brief, run the tiered flow. None of them implement.

### 2.6 Rules

`.claude/rules/common/` holds cross-cutting engineering standards (api-contracts, data-modeling, security, testing, accessibility, performance, observability, state-management, design-system, codex-delegation, language-protocol, document-lifecycle). `.claude/rules/lang/<language>/` holds per-language standards, activated by Zone B `active_rules`. Codex reads only the rules relevant to the task.

### 2.7 CLAUDE.md 3-Zone layout

- Zone A (template policy, above `@orchestra:template-boundary`): PM/engineering contract. Overwritten by template updates.
- Zone B (between boundaries): project stack, commands, directory map, active rules. Preserved by `scripts/update.sh`.
- Zone C (below `@orchestra:repo-boundary`): active work context, rotated by `/checkpointing`.

`AGENTS.md` mirrors this with `@codex:template-boundary` / `@codex:repo-boundary` for project-specific Codex notes.

## 3. Decision Records

### ADR-001 (Accepted): Two-provider PM/engineering split

Claude is PM; Codex is engineering. Ownership is exclusive: Claude cannot write source, Codex cannot accept its own work. Rationale: single-owner responsibility per concern, reproducible handoffs, independent review as a first-class phase. Ported from `claude-finance`.

### ADR-002 (Accepted): Runner-centralized Codex invocation

All Codex calls go through `codex_handoff.py`. No inline `codex exec` in skills or hooks. Rationale: consistent flags, sandboxing, artifacts, and audit trail; prompts cannot drift per call site.

### ADR-003 (Accepted): Review isolation

The reviewer is a fresh Codex invocation that never receives the implementation transcript. It reads only the brief, approved plan, implementation result, repository, and diff.

### ADR-004 (Accepted): PM-native visual acceptance

Claude judges UI render correctness by reading captured screenshots/previews directly (Claude is natively multimodal). Codex produces the captures as part of Required Validation.

### ADR-S1 (Superseded): Role-based Opus subagent teams

Former decision: 14 role agents (ui-engineer, api-engineer, ...) implemented in parallel via Agent Teams (`/team-implement`, `/parallel-batch`). Superseded because ownership duplicated Codex's engineering role, always-loaded context grew, and responsibility boundaries blurred. Implementation is now exclusively Codex.

### ADR-S2 (Superseded): Gemini CLI as multimodal agent

Former decision: Gemini analyzed screenshots, Figma exports, PDFs, and diagrams with structured JSON output. Superseded because Claude and Codex now handle visual analysis natively at equivalent quality; a third provider added contracts, hooks, and confidence plumbing without unique value.

### ADR-S3 (Superseded): Keyword-routing and advisory hooks

Former decision: hooks routed prompts by keyword (agent-router) and advised per-edit (lint-on-save, a11y-quick-check, migration-check, contract-edit warning, gemini suggestion) under a 3-level severity model. Superseded: routing is a PM judgment; per-edit advisory hooks lost their subject once Claude stopped editing source. Hooks now enforce only deterministic safety (write guard, deploy gate, secret scan) plus telemetry.

## 4. Repository Layout (template)

```text
CLAUDE.md                        # PM contract (Zone A) + project stack (Zone B) + context (Zone C)
AGENTS.md                        # Codex engineering contract (+ project notes section)
DESIGN.md                        # this file
README.md                        # install / usage
scripts/update.sh                # template refresh preserving Zone B / notes / runtime state
.claude/
  settings.json                  # hooks + permissions
  scripts/codex_handoff.py       # canonical Codex runner
  hooks/                         # pm-write-guard, deploy-gate, secret-scan, dispatcher, error-to-codex, log-cli-tools
  skills/                        # 19 PM skills
  rules/common/ + rules/lang/    # engineering standards for Codex
  docs/CODEX_TASK_CONTRACT.md    # handoff protocol
  docs/reviews/                  # commit-worthy decision/review records
  tasks|checkpoints|plans|state/ # gitignored PM artifacts
.codex/config.toml               # read-only sandbox, approval never
```

## 5. Language Protocol

| Target | Language |
|---|---|
| User interaction | Japanese |
| Task artifacts, code, comments, commits | English |
| Project docs | English unless the user requests Japanese |
