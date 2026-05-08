# Rule: Node-TypeScript Coding Principles (Backend)

Applies to backend Node.js services in TypeScript: Hono, Fastify, NestJS, Express, plus serverless handlers.

## Compiler

- `strict: true` mandatory
- `target: ES2022` or newer
- `moduleResolution: "nodenext"` (or `"bundler"` if bundled)
- `verbatimModuleSyntax: true` recommended
- ESM preferred for new projects (`"type": "module"`); CJS only for legacy compatibility

## Runtime

- Node 20 LTS or 22 LTS as default; bun / Deno as project decisions per Zone B
- Always async: `await` over `.then`; no callback-style APIs unless wrapping a node legacy interface

## Lint and format

- **ESLint** (`@typescript-eslint`, `eslint-plugin-import`, plus framework plugins) OR **Biome**
- Lint errors fail CI

## Type usage

- Same baseline as frontend TS (no `any`, narrow `unknown`, prefer interface/type appropriately)
- `zod` / `valibot` / `typebox` for runtime-validated boundaries (HTTP, env vars, message payloads)
- Brand types for IDs (`type UserId = string & { __brand: "UserId" }`) when correctness matters

## Env config

- Validate at process start with a schema; fail fast on missing required vars
- Single `config` module exporting a typed, frozen object

## Errors

- Throw typed `Error` subclasses or use a Result type — chosen and consistent
- Top-level handler converts errors to the API error envelope (per `common/api-contracts.md`)
- No silent catch
- Async error propagation tested

## Modules

- Domain logic separated from framework specifics (handler vs service vs repository)
- No circular imports
- Path aliases configured but used sparingly across domain boundaries

## Naming

- Variables / functions: `camelCase`
- Classes / types: `PascalCase`
- Files: `kebab-case.ts`
- Constants: `SCREAMING_SNAKE_CASE` for module-level invariants

## Process management

- Graceful shutdown handler (SIGTERM/SIGINT): drain in-flight requests, close connections
- Health check endpoint distinct from main route handlers
