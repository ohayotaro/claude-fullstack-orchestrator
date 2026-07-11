---
name: data-design
description: PM intake for schema, migration, and query work with migration-safety gates.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Data Design

Schema work is T2 by default. It is T3 when the migration is destructive (DROP, data deletion, NOT NULL on existing columns) or runs against production data.

## Intake

- Record entities, access patterns that justify the design, and the migration tool from Zone B.
- Classify the migration: additive / online-safe / destructive.
- For destructive changes, require a documented backout plan in the brief.

## Acceptance Checklist

- AC includes append-only migrations with documented `down` where reasonable.
- AC includes indexes justified by known queries (no speculative indexes).
- AC includes retention/lifecycle notes for tables holding user data; sensitive columns flagged.
- AC includes N+1 and query-plan checks for new hot paths.

## Delegation

Create the task brief and run `plan` before any implementation. Destructive migrations follow the T3 flow with explicit user approval; production execution is additionally gated by `deploy-gate`.
