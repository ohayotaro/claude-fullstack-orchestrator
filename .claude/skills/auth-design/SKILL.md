---
name: auth-design
description: Design or validate authentication, authorization, session/token flows. Owned by auth-security-engineer with Codex review for novel flows. Produces a sequence diagram, token lifecycle, threat model summary, and integration points for api-engineer / data-engineer / platform-integrator.
---

# /auth-design

## Purpose

Take an auth requirement (signup, login, social auth, MFA, role-based access, multi-tenant isolation, machine-to-machine) to a reviewed flow with explicit token lifecycle, storage, and threat model.

## When to use

- New authentication flow (signup / login / SSO / MFA)
- New authorization rule (role / permission / row-level)
- Token lifecycle change (refresh, rotation, revocation)
- Multi-tenant isolation review
- API key / service-to-service auth setup

## Steps

### 1. Read context

- Zone B: `auth_mode`, `database`, `runtime_envs`, `backend_framework`
- Existing auth code (middleware, guards, dependencies)
- Existing user / session / permission models

### 2. Pick or validate the auth strategy

Per Zone B `auth_mode`:

- **session**: server-side session + signed cookie; simplest for monolithic web apps
- **jwt**: stateless tokens; good for API-only or distributed services; revocation requires care (token blacklist or short TTL + refresh)
- **oauth2-pkce**: third-party identity provider with PKCE; mobile / SPA standard
- **oidc**: OAuth2 + identity layer; social auth via Google / Apple / Microsoft / etc.
- **api-key**: service-to-service or third-party developer access
- **custom**: justify

For a new flow, decide:
- Token format (signed JWT, opaque ID, etc.)
- Token TTL (access token short, refresh token long)
- Refresh strategy (rotate-on-use is the default secure path)
- Storage (HttpOnly cookie vs Authorization header vs platform SecureStore)
- Revocation strategy (blacklist DB, version field on user, ID tokens with TTL)

### 3. Authorization model

- RBAC (role-based) / ABAC (attribute-based) / ReBAC (relationship-based) — pick per project
- Policy enforcement points (middleware vs service vs row-level)
- Multi-tenant isolation: every query filters by tenant id; verified via tests

### 4. Sequence diagram (text)

Draft a sequence diagram of the flow:

```
Client → Auth API: POST /auth/login (email, password)
Auth API → DB: lookup user by email
DB → Auth API: user record (incl. password hash)
Auth API → Auth API: argon2 verify
Auth API → DB: create session (refresh token id)
Auth API → Client: 200 (Set-Cookie: refresh; body: access_token)
...
```

### 5. Codex review

Send the flow + token lifecycle + storage + threat model to Codex. Focus areas:
- Token leakage paths
- CSRF (if cookies)
- XSS impact on token storage
- Replay attacks
- Refresh token rotation correctness
- Multi-tenant isolation
- Session fixation / device binding
- Logout completeness

### 6. Threat model summary

For features touching auth, payments, PII, file upload:

| Asset | Threats | Mitigations |
|---|---|---|
| Refresh token | theft via XSS, leak in logs | HttpOnly, short TTL, rotate on use, never logged |
| User PII | unauthorized read | row-level filter, audit log, encryption at rest |
| ... | ... | ... |

### 7. Integration points

Identify the agents that will implement:
- `api-engineer`: handler, middleware, guards
- `data-engineer`: user / session / refresh-token tables, indexes for lookups
- `platform-integrator`: secure storage on mobile / RN / Flutter / desktop
- `infra-engineer`: secret manager wiring, WAF rules, IAM

### 8. Document

Save to `design/decisions/auth-<flow>.md` with:
- Sequence diagram
- Token lifecycle table
- Storage decisions
- Threat model
- Codex review summary

## Output

- Sequence diagram (text / mermaid)
- Token lifecycle spec
- Threat model
- Integration plan
- Codex review record

## Hand-off

- Implementation → `api-engineer`, `data-engineer`, `platform-integrator`
- Infra-level (secrets, WAF) → `infra-engineer`

## Notes

- Hard-coded credentials trip the `secret-scan.py` hook (severity: require-explicit-override). All secrets via env vars or secret manager.
- Refresh token rotation: the OLD refresh token must be invalidated when a new one is issued; reuse signals theft.
- Authorization checks happen on every request that accesses a resource — defense in depth, not a single edge check.
