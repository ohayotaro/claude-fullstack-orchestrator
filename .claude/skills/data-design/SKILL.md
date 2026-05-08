---
name: data-design
description: Design schema, migrations, indexes, and access patterns. Owned by data-engineer with Codex review for non-trivial changes. Migration files are treated as a contract boundary — destructive changes require warn-level gating and a backout plan.
---

# /data-design

## Purpose

Take a data requirement to a reviewed schema + migration + index plan. Owned by `data-engineer`. Codex CLI provides review for non-trivial designs.

## When to use

- New table / collection / index
- Schema change (column add / drop / type change)
- New access pattern that requires an index
- Migration of existing data (backfill, reshape)

## Steps

### 1. Read context

- Zone B `database` block: `engine`, `orm_or_driver`, `migration_tool`
- Existing schema (read migrations + ORM models)
- Access patterns the new schema must serve (query mix)

### 2. Draft the model

Compose the change as a brief specification:

- Tables / collections affected
- Columns / fields with types and constraints
- Foreign keys / referential integrity
- Indexes (with the queries they support)
- Soft-delete vs hard-delete decision (per `common/data-modeling.md`)
- Sensitive columns (flag for `auth-security-engineer` review)
- Retention / TTL where applicable

### 3. Codex review for non-trivial designs

Send the design to Codex when:
- Touching hot tables (>1M rows)
- Adding a column requiring backfill
- Changing constraints (unique, NOT NULL on existing)
- Cross-table refactor

Codex review focuses on: index coverage for the access patterns, migration safety, lock duration estimate, backout plan.

### 4. Write migration

Per Zone B `migration_tool`:

- Append-only (never edit a committed migration)
- Reversible where reasonable; document why if not
- For destructive changes (DROP / NOT NULL on existing / data deletion):
  - The `migration-check.py` hook fires (severity: warn)
  - Document the backout plan inline
  - Plan staged rollout: shadow column → backfill → switch read → drop old, when applicable

### 5. Plan online execution for hot tables

If the migration affects a large table:
- Estimate lock duration
- Use online DDL features (Postgres `CREATE INDEX CONCURRENTLY`, MySQL pt-osc / gh-ost, etc.)
- Batch backfill with rate limit
- Verify replicas are not blocked

### 6. Update ORM models

Per Zone B `orm_or_driver`. Match field types and constraints to the migration. Add or update factories / seed data.

### 7. Test

- Unit: model-level (validation, defaults)
- Integration: migration applies cleanly on a test DB; data preserved
- Query plan: `EXPLAIN` for new query patterns confirms index use

### 8. Document

- Update ER snippet (if maintained)
- Update API surface (`api-engineer`) if shape changed
- Update access pattern doc in `design/decisions/` for non-trivial designs

## Output

- Migration file(s)
- Updated ORM model(s)
- Index additions
- Test coverage
- Query plan verification (if applicable)
- Codex review record (if non-trivial)

## Hand-off

- API surface impact → `api-engineer` (`/api-build`)
- Cache impact → `infra-engineer`
- Backup / restore policy update → `infra-engineer`

## Notes

- The `migration-check.py` hook will block destructive changes without an explicit override AND a backout plan in the migration message.
- Index choices are review-worthy: every index has a query that justifies it, no speculative indexes.
- Sensitive columns (passwords, tokens, PII) require `auth-security-engineer` review of column-level encryption / hashing strategy.
