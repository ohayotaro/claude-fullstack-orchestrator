# Rule: Security

OWASP Top 10 is the baseline floor, not the ceiling.

## Mandatory rules

- **Secrets**: env vars or secret manager only. Never in code, never in commits. The `secret-scan.py` hook blocks writes containing secret-like values.
- **HTTPS**: enforced in production. HSTS planned with the infra work (`/infra-review`).
- **Validation**: at the edge. Never trust inbound data — validate type, shape, range, length, encoding.
- **Authentication**: every endpoint declares its auth requirement (or is explicitly marked public)
- **Authorization**: every resource access enforces ownership / membership; IDOR vectors considered for `/resource/:id` paths
- **CSP** (web): set; `unsafe-inline` and `unsafe-eval` avoided
- **CSRF** (web): SameSite cookie + CSRF token where state-changing
- **XSS**: rely on framework escape; `dangerouslySetInnerHTML` / `unsafe HTML` only with sanitizer + reason
- **SSRF**: outbound requests from server-side validate target host against allowlist where possible
- **Clickjacking**: `X-Frame-Options: DENY` or CSP `frame-ancestors`
- **Dependency audit**: `npm audit` / `pip-audit` / `cargo audit` etc. run in CI; high/critical block merge

## Sensitive data handling

- Passwords: hash with Argon2id or bcrypt; never store reversibly
- Tokens: HttpOnly + Secure + SameSite cookies, OR Authorization header (never URL params)
- PII: classified per applicable law (GDPR / CCPA / etc.); access logged
- Logging: no secrets, no PII unless explicitly justified and access-controlled

## Mobile specifics

- Secure storage: Keychain (iOS) / EncryptedSharedPreferences or DataStore-encrypted (Android) / SecureStore (RN/Expo) / flutter_secure_storage (Flutter)
- Certificate pinning evaluated for high-value clients
- App transport security on iOS not weakened without justification

## Threat modeling

For features touching auth, payments, PII, file upload/download: produce a brief threat model with the change set (assets, threats, mitigations).

## Ownership

All engineering work in this domain is delegated to Codex through a task brief (`/codex-task`, see `common/codex-delegation.md`). Claude captures the requirements above as acceptance criteria in the brief; Codex designs, implements, and validates them.
