---
name: backend-init
description: PM wizard that captures the backend stack into CLAUDE.md Zone B and active rules.
allowed-tools: "Read Write Edit Glob Grep"
---

# Backend Init

T0-T1 PM activity: this skill only edits `CLAUDE.md` Zone B. Run after `/init-webdev` when backend is in scope.

## Wizard

Ask the user (Japanese) and record (English):

1. Backend scope: none / bff-only / full-backend
2. Language(s) and framework
3. API style (rest / graphql / rpc / mixed)
4. Database, ORM/driver, migration tool
5. Cache, message broker, blob storage
6. Auth mode
7. Deployment target and runtime envs
8. Observability (logs / metrics / tracing)

## Output

- Fill the Backend Stack section of Zone B and update `active_rules.lang`.
- Record per-endpoint latency budgets or SLOs if the user declares them.
- Service scaffolding is engineering work: create a brief and delegate via `/codex-task`.
