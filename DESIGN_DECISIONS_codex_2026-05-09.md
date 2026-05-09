# Codex Decisions — DESIGN.md v0.2 → v0.3

Decided by: Codex CLI (gpt-5.4) | Date: 2026-05-09 | Sandbox: read-only

> **Post-decision update:** Decision 2 below recommended `claude-fullstack-orchestrator` and that name was used initially. The repo was subsequently renamed to **`claude-fullstack`** to share naming symmetry with the sibling repo `claude-finance` (renamed from `claude-orchestrator`). The historical decision text is preserved as-is.

User delegated 4 open decisions (including new backend scope expansion) to Codex's judgment.

## Decision 1: Backend Scope (Confidence: H)

### New agents
- `api-engineer` — HTTP/gRPC API design and implementation, contracts, handlers, validation, and service boundaries
- `data-engineer` — schema design, migrations, query patterns, transactions, and data access performance
- `auth-security-engineer` — authentication, authorization, session/token flows, secrets, and backend security review
- `infra-engineer` — deployment topology, runtime config, containers, CI/CD, observability, and cloud primitives
- `job-engineer` — background jobs, queues, schedulers, retries, idempotency, and async workflows

### New skills
- `/backend-init` — extend `/init-webdev` choices for backend runtime, DB, broker, deploy target, and API style
- `/api-build` — scaffold or implement endpoints/services from an approved contract
- `/data-design` — schema, migration, indexing, and access-pattern review
- `/auth-design` — choose and validate authn/authz/session architecture
- `/infra-review` — deployment/runtime/secret/observability review
- `/job-design` — queue, worker, retry, and scheduled task design
- `/incident-backend` — backend-focused production incident triage

### Lang rules in v0.1
`python`, `node-typescript`

### Lang rules as extension
`go`, `rust`, `java`, `kotlin-spring`

### BFF vs full-backend boundary
`bff-engineer` is absorbed into `api-engineer` as a specialization, not a separate long-term role. A BFF is still an API surface, but optimized for UI composition and frontend consumption. Zone B retains `bff_layer` because it matters to frontend workflows, but all backend HTTP/service contract work routes through `api-engineer`; when `backend_scope=bff-only` it operates in BFF mode, when `backend_scope=full-backend` it handles broader service concerns.

### Zone B additions
- `backend_scope` (`none | bff-only | full-backend`)
- `backend_languages`
- `api_style` (`rest | graphql | rpc | mixed`)
- `backend_framework`
- `database` (`engine`, `orm_or_driver`, `migration_tool`)
- `cache` (`none | redis | other`)
- `message_broker` (`none | sqs | pubsub | kafka | rabbitmq | other`)
- `blob_storage`
- `auth_mode`
- `deployment_target`
- `observability`
- `runtime_envs` (`local | staging | prod` conventions)

### Rationale
The current draft already separates roles by responsibility and reads configuration from Zone B, so backend expansion should follow the same pattern instead of inventing backend-specific architecture elsewhere. For v0.1, `python` and `node-typescript` cover the largest real-world surface area with the least rule explosion; Go/Rust/Spring are valuable, but they are better shipped once the orchestration model is proven.

## Decision 2: Repo Name (Confidence: H)
`claude-fullstack-orchestrator`

### Rationale
`claude-webdev-orchestrator` becomes misleading once backend specialists are first-class scope, and `frontend-orchestrator` is now incorrect. `fullstack` is the clearest label for web/UI + backend while still leaving room for mobile and BFF-backed product work under one orchestrator.

## Decision 3: Vue/Svelte (Confidence: M)
Extension only.

### Rationale
Vue and Svelte are framework rules, not language rules, and the current rules architecture is explicitly language-first under `rules/lang/*`. For v0.1, keep the initial surface area tight and rely on `typescript` language rules plus framework-specific guidance later under a separate extension layer such as `rules/framework/{vue,svelte}`.

## Decision 4: active_rules Location (Confidence: H)
Declare in `CLAUDE.md` Zone B.

### Rationale
`active_rules` is project-semantic configuration chosen by `/init-webdev`, so it belongs with the rest of the project contract, not hidden in tool-local settings. Keeping it in Zone B also preserves the current design principle that agents, skills, and hooks all read one canonical project configuration source.

## Cross-cutting concerns
`DESIGN.md` should be updated beyond these four items in a few linked places: rename the document and examples from "Frontend / UI Orchestrator" to "Fullstack Orchestrator," replace the 10-agent model with the expanded set (14 agents), and remove the standalone `bff-engineer`. Update `/init-webdev` to include backend prompts or introduce `/backend-init` as a follow-on wizard, extend Zone B schema with backend fields, and change rules architecture language to distinguish `lang/*` from future `framework/*` rules. Revise the "resolved decisions" and implementation order so backend agents, backend rules, and backend skills are explicitly in v0.1 scope.
