# Codex Handoff Playbook

Templates for delegating to Codex CLI from skills and agents. All Codex prompts are English. Always invoke with `< /dev/null` to avoid stdin-wait hangs in non-interactive contexts. Use `--skip-git-repo-check` when running before `/init-webdev`.

## Generic invocation

```bash
codex exec --skip-git-repo-check < /dev/null '<prompt>' 2>&1
```

For long outputs, redirect to a file:

```bash
codex exec --skip-git-repo-check < /dev/null '<prompt>' > /tmp/codex-<task>.txt 2>&1
```

## Template: Architecture review

```
You are reviewing an architecture proposal in <project-name> at <path>.

Context:
- Stack (read CLAUDE.md Zone B): <summary>
- Active lang rules: <list>
- Change scope: <files/modules>

Proposal:
<paste design or diff>

Review using the standard output contract (TL;DR / Analysis / Plan / Validation / Risks / Confidence). Cite file paths and line numbers. Flag any contract-boundary impact (api / state / package / migration / event).

Aim for under 600 words.
```

## Template: API contract review

```
Review the API contract draft below for <feature>.

Project context (CLAUDE.md Zone B):
- Backend stack: <framework>, <language>, <api_style>
- Auth mode: <auth_mode>
- Database: <engine>, <orm>

Contract draft:
<paste OpenAPI / SDL / proto>

Review for:
- Consistency with existing patterns in <repo>
- Validation gaps
- Auth/authz coverage
- Schema impact (cross-check the proposed mutations)
- Versioning / deprecation impact (if full-backend mode)
- Error envelope conformance per common/api-contracts.md

Output format: standard contract.
```

## Template: Schema / migration review

```
Review this DB change for <project>.

Engine: <postgres|mysql|...>
ORM: <sqlalchemy|prisma|...>
Migration tool: <alembic|prisma-migrate|...>
Estimated table size: <rows>
Hot table? <yes|no>

Migration:
<paste migration code>

Review for:
- Lock duration estimate
- Online execution safety on hot tables
- Reversibility / backout plan
- Index coverage for the access patterns introduced
- N+1 risk in the application code that consumes this

Output format: standard contract. Critical: flag any DROP / NOT-NULL-on-existing / TRUNCATE / DELETE without WHERE.
```

## Template: Auth flow review

```
Review this auth flow for <project>.

Auth mode: <session|jwt|oauth2-pkce|oidc|api-key>
Storage: <httpOnly cookie|Authorization header|SecureStore|...>
Token lifecycle:
- Access token TTL: <X>
- Refresh token TTL: <Y>
- Rotation: <rotate-on-use|never|...>

Sequence:
<paste sequence diagram or steps>

Review for OWASP-relevant concerns:
- Token leakage paths (XSS, CSRF, log capture)
- Replay attacks
- Refresh token rotation correctness (old token invalidation)
- Multi-tenant isolation
- Session fixation / device binding
- Logout completeness

Output: per concern, verdict (covered / mitigated / accepted with rationale / failing) plus standard contract.
```

## Template: Debugging (codex-debugger skill)

```
Debug this error in <project>.

Stack (Zone B): <summary>
Active rules: <list>

Error output:
<paste stack trace / log>

Recent changes (git diff if any):
<paste>

Files relevant to the error:
<paste contents or quote sections>

Diagnose:
1. Most likely root cause
2. Verification steps
3. Fix proposal (with diff if possible)
4. Tests that would have caught this

Output format: standard contract, full-auto mode (you may suggest specific edits).
```

## Template: Incident triage (incident-backend)

```
Triage this backend incident.

Symptom: <e.g., 5xx spike on /api/checkout>
Started: <timestamp>
Recent deploys: <list>
Recent migrations: <list>
Observability snapshot:
- Error rate: <%>
- Latency p95: <ms>
- Affected endpoints: <list>
- Logs sample: <paste>

Provide:
1. Top 3 hypotheses ranked by likelihood
2. Verification queries / commands per hypothesis
3. Mitigation options (immediate vs durable)
4. Post-incident actions (alerting gaps, documentation)

Output format: standard contract. Confidence per hypothesis is required.
```

## Template: Performance review (perf-audit follow-up)

```
Review this performance fix proposal.

Surface: <web|ios|android|backend>
Measurement before:
<paste profile / Lighthouse / latency numbers>

Proposed fix:
<paste diff>

Expected measurement after:
<paste predicted numbers>

Review for:
- Whether the fix targets what was actually slow
- Tradeoffs (complexity, cache cost, bundle size, etc.)
- Regression risk (does this change a contract or behavior?)
- Need for benchmarks / regression tests

Output format: standard contract.
```

## Notes

- Always include the standard output contract in the prompt — Codex's response shape depends on it.
- Persist non-trivial Codex reviews to `.claude/docs/reviews/<topic>-<date>.md` as decision records.
- For long-running reviews, run in foreground with explicit timeout; do NOT use `run_in_background` if stdin is open elsewhere (causes the documented stdin-wait bug — always pipe `< /dev/null`).
