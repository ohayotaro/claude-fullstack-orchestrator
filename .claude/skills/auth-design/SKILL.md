---
name: auth-design
description: PM intake for authentication, authorization, and session/token flow changes.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Auth Design

Auth work is T3 by default: it touches secrets, session integrity, and every protected surface.

## Intake

- Record the auth mode (per Zone B), the flows changing (login, refresh, logout, permissions), and affected clients.
- Capture compliance constraints (GDPR/CCPA scope, audit logging needs).
- State explicitly what must not change (existing sessions, token formats consumed by other services).

## Acceptance Checklist

- AC includes a sequence diagram and token/session lifecycle in the plan.
- AC includes a threat model note (assets, threats, mitigations).
- AC includes storage rules: HttpOnly/Secure cookies or platform secure storage; never plain storage or URL params.
- AC includes authorization checks per resource (IDOR considered) and tests for authz failure paths.
- AC includes hashing/crypto choices per `.claude/rules/common/security.md`.

## Delegation

Create the task brief and run `plan`. T3: explicit user approval before implementation. Credential values never appear in briefs, plans, or results.
