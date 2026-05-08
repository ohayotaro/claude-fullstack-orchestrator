---
name: backend-init
description: Backend wizard. Asks the user about backend scope, languages, framework, API style, database, cache, message broker, blob storage, auth mode, deployment target, and observability. Writes answers into CLAUDE.md Zone B's backend section and updates active_rules. Run after /init-webdev when backend is in scope.
---

# /backend-init

## Purpose

Populate the backend section of CLAUDE.md Zone B and activate the relevant backend lang rules. After this runs, `api-engineer`, `data-engineer`, `auth-security-engineer`, `infra-engineer`, and `job-engineer` know what stack they are operating on.

## When to use

- After `/init-webdev` if `product_mode` includes backend (`fullstack`, `backend-only`, or any mode where `backend_scope != none`)
- Significant backend stack change (e.g., switching DB engine, adding a message broker)

## Steps

### 1. Read current CLAUDE.md Zone B

Confirm `/init-webdev` was run (Zone B placeholders for product_mode etc. are filled). If not, suggest running `/init-webdev` first.

### 2. Ask backend scope

Use `AskUserQuestion` (single-select):

- `none` — no backend; this skill exits
- `bff-only` — Backend for Frontend, optimized for the UI; no broader service contracts
- `full-backend` — durable contracts, may be consumed by multiple clients

If `none`: write `backend_scope: none` and exit. The `bff-engineer`-style work (if any) lives in the frontend's API routes per Zone B `bff_layer`.

### 3. Ask backend language(s)

Multi-select:

- `python` (FastAPI / Django / Litestar / Flask)
- `node-typescript` (Hono / Fastify / NestJS / Express)

If the user picks one not in v0.1 (`go / rust / java / kotlin-spring`), inform them that lang rules for that language are an extension and not bundled in v0.1; they may proceed but rule coverage will be lower.

### 4. Ask backend framework

Single-select per chosen language(s):

- Python: `fastapi / django / litestar / flask`
- Node-TS: `hono / fastify / nestjs / express`

### 5. Ask API style

Single-select: `rest / graphql / rpc / mixed`

### 6. Ask database

Compound question:

- Engine: `postgres / mysql / sqlite / dynamodb / mongodb / other`
- ORM/driver: depends on engine + lang (e.g., Postgres + Python → `sqlalchemy / tortoise / django-orm`; Postgres + Node-TS → `prisma / drizzle / kysely / typeorm / pg`)
- Migration tool: `alembic / prisma-migrate / drizzle-kit / typeorm-migrations / django / liquibase / flyway / atlas`

### 7. Ask cache

Single-select: `none / redis / memcached / cloudflare-kv / dynamodb-cache / other`

### 8. Ask message broker

Single-select: `none / sqs / pubsub / kafka / rabbitmq / sns / cloudflare-queues / nats / other`

### 9. Ask blob storage

Single-select: `none / s3 / gcs / r2 / azure-blob / supabase-storage / other`

### 10. Ask auth mode

Single-select: `session / jwt / oauth2-pkce / oidc / api-key / custom`

If `oauth2-pkce` or `oidc`: ask provider (`auth0 / clerk / cognito / firebase / supabase / keycloak / custom`).

### 11. Ask deployment target

Single-select: `vercel / cloudflare / ecs-fargate / gke / render / fly / k8s-self-managed / lambda / cloud-run / app-runner / other`

### 12. Ask observability stack

Compound:

- Logs: `cloudwatch / gcp-logging / datadog / new-relic / loki / honeycomb / self-hosted / other`
- Metrics: `cloudwatch / prometheus / datadog / new-relic / honeycomb / other`
- Tracing: `opentelemetry / xray / cloud-trace / datadog / honeycomb / other`

### 13. Ask runtime envs convention

Single-select: `local-staging-prod` (default) / `local-dev-staging-prod` / custom

### 14. Update `active_rules.lang`

Add backend langs to `active_rules.lang` (merge with frontend langs from `/init-webdev`):

- `python` → add `python`
- `node-typescript` → add `node-typescript`

### 15. Update CLAUDE.md Zone B backend section

Use `Edit` to replace placeholder values for: `backend_scope`, `backend_languages`, `backend_framework`, `api_style`, `database` block, `cache`, `message_broker`, `blob_storage`, `auth_mode`, `deployment_target`, `observability` block, `runtime_envs`.

### 16. Print summary

Output a summary table with the chosen backend values and updated `active_rules`. Confirm Zone B backend section is populated.

## Output

- Updated `CLAUDE.md` Zone B backend section
- Updated `active_rules.lang`
- Summary of choices to the user

## Notes

- For `bff-only`, the `api-engineer` agent will operate in BFF mode by default; the wizard does not need to ask separate BFF questions beyond standard framework + DB.
- `api-engineer` reads `backend_scope` at runtime to decide its mode.
- Do not create scaffold service directories — that is the user's project responsibility.
