# Rule: API Contracts

Applies to REST / GraphQL / RPC / BFF surfaces. Contracts are treated as a stable interface — breaking changes require explicit gating.

## Contract-first

- **Document before implementing**: OpenAPI (REST), SDL (GraphQL), proto (gRPC), or equivalent
- The contract artifact lives in the repo and is reviewable
- Generated code (clients, types) regenerated from the contract, not hand-edited

## Validation

- Validate at the edge — type, shape, range, length, encoding
- Reject early; do not pass invalid data into the domain layer
- Validation errors map to a consistent error envelope

## Error envelope

Consistent shape across the surface:
```json
{
  "error": {
    "code": "string-stable-id",
    "message": "human-readable",
    "details": { },
    "request_id": "uuid"
  }
}
```

- `code` is stable and machine-readable; do not localize
- `message` is human-friendly; localize at presentation layer
- HTTP status code maps to error category (4xx client / 5xx server)

## Idempotency

- Non-idempotent mutations require an idempotency key (sourced from caller)
- Server stores key+result for a documented window (typically 24h)

## Versioning (full-backend mode)

- Breaking changes require explicit version bump
- Deprecation: `Deprecation` header (REST) or schema directive (GraphQL) with sunset date
- Migration path for clients documented before the deprecation lands

## Pagination, filtering, sorting

- Cursor-based pagination preferred over offset for large datasets
- Filter fields explicit; whitelist on the server
- Sort fields whitelisted; default sort declared

## Auth requirement

Every endpoint declares its auth requirement explicitly. Public endpoints are explicitly marked.

## Hand-off

- Contract design and impl: `api-engineer`
- Authn/authz on contracts: `auth-security-engineer`
- Schema impact of contract changes: `data-engineer`

The `check-codex-on-contract-edit.py` hook fires (severity: warn) on changes to contract artifacts.
