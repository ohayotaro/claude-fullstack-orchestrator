# Rule: Data Modeling

Applies to all persistent storage — relational DBs, document stores, key-value, search indexes.

## Migrations

- **Append-only**: never edit a committed migration; add a new one
- **Reversible where reasonable**: `down` documented
- **Destructive changes** (DROP / data deletion / NOT NULL on existing): T3-gated — explicit user approval and a documented backout plan in the task brief.
- **Long migrations on hot tables**: planned for online execution — split into batches, use shadow tables, or use the DB engine's online DDL where supported

## Schema design

- Decisions are paired with the access patterns that justify them
- No speculative indexes; every index supports a known query
- Foreign keys / referential integrity decisions explicit (in or out of the schema)
- `BIGINT` PKs by default for relational engines (avoid 32-bit exhaustion)
- `TIMESTAMPTZ` (Postgres) or equivalent UTC-aware type for time
- Soft-delete vs hard-delete: explicit decision, documented per table

## Data lifecycle

- Retention period declared for each table holding user data
- Archival / TTL strategy documented when applicable
- Backup / restore procedure documented and drilled

## Sensitive columns

- Sensitive columns (passwords, tokens, PII) flagged in the schema and in the ORM model
- Encryption-at-rest planned at infra level; column-level encryption only when justified
- Access logged where regulation requires (HIPAA / GDPR / PCI scope)

## Engine-specific

- **Postgres**: prefer `BIGINT` PKs, partial indexes for sparse predicates, `JSONB` over `JSON`
- **MySQL**: utf8mb4 default, attention to index column order on composite indexes
- **SQLite**: WAL mode for concurrent reads, single-writer awareness
- **DynamoDB**: access pattern first; single-table design considered, GSIs intentional
- **MongoDB**: schema validation enabled (`$jsonSchema`); indexes as code

## Ownership

All engineering work in this domain is delegated to Codex through a task brief (`/codex-task`, see `common/codex-delegation.md`). Claude captures the requirements above as acceptance criteria in the brief; Codex designs, implements, and validates them.
