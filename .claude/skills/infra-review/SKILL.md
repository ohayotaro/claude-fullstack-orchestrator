---
name: infra-review
description: Review deployment topology, runtime config, container builds, CI/CD, observability, and cloud primitives. Owned by infra-engineer with Codex review for non-trivial changes. Use before introducing or changing any deploy / runtime / observability surface.
---

# /infra-review

## Purpose

Catch infra issues before they hit production: misconfigured health checks, secrets in images, unbounded cardinality metrics, missing rollback paths, autoscaling that doesn't.

## When to use

- New deployment target or major topology change
- Container build changes (base image, build steps)
- CI/CD pipeline changes
- Observability stack changes (logs / metrics / tracing)
- New cloud primitive (CDN, WAF, secret manager)
- Pre-release readiness check

## Lenses

### 1. Container

- Multi-stage build; minimal runtime base image (distroless / alpine / slim)
- Non-root user (`USER appuser`)
- No secrets baked in (verify via `docker history`)
- Health check defined
- Specific tags (no `:latest` in production)

### 2. Runtime config

- Env vars validated at startup (fail fast)
- Secrets via secret manager / mounted volumes (never in image / env in shell history)
- Feature flags wired with safe defaults
- Logs to stdout/stderr (12-factor); not to file inside container

### 3. CI/CD

- Tests + lint gating merge
- Build is reproducible from VCS state
- Deploy is one command (or one revert)
- Migrations run before app deploy unless explicitly designed for online migration
- Smoke check post-deploy
- Rollback procedure documented

### 4. Health checks

- Liveness / readiness / startup probes distinct (when applicable)
- Readiness reflects dependency reachability (DB, cache, broker)
- Failing readiness drains traffic; failing liveness restarts the pod

### 5. Autoscaling

- Targets are RED metrics (rate, errors, duration) or USE (utilization, saturation)
- Scale-out and scale-in policies prevent flapping
- Cold-start cost respected (warm pool / minimum instances when needed)

### 6. Networking

- Ingress + TLS + HSTS
- CDN configuration (cache headers, invalidation policy)
- Security groups / firewall: minimal exposed ports
- Service-to-service: TLS or mesh; no plain HTTP across networks

### 7. Observability

- Logs: structured JSON; correlation IDs; no PII / secrets
- Metrics: RED / USE / business KPIs; cardinality bounded
- Tracing: OpenTelemetry; sampling strategy declared
- Dashboards committed to repo (where supported by the tool)
- Alerting: symptom-based, mapped to runbooks

### 8. DR

- Backup schedule + retention
- Restore drilled
- RPO / RTO declared

### 9. Cost

- Idle resources right-sized
- Egress traffic monitored
- Reserved capacity vs on-demand decision deliberate

## Steps

### 1. Determine scope

Files touched: Dockerfile, IaC (terraform / pulumi / CDK / k8s manifests), CI workflow, helm charts, observability config.

### 2. Apply lenses

Walk through the relevant lenses for the change set. Cite findings per lens.

### 3. Codex review for non-trivial changes

Send the diff + lens findings to Codex with focus on:
- Failure modes during deploy / rollback
- Blast radius of the change
- Drift potential (manual changes vs IaC)
- Cost / performance tradeoffs

Codex returns standard contract output.

### 4. Categorize findings

```
### Critical (block deploy)
- file:line — finding — fix
### Major (resolve before deploy or explicitly defer)
- ...
### Minor (track)
- ...
```

### 5. Verify after fix

For deploy-related changes, perform the deploy in staging and verify. For IaC changes, plan / preview shows expected diff with no surprises.

### 6. Persist report

Save to `.claude/logs/reviews/infra-<run-id>.md`.

## Output

- Findings by severity
- Verification log (staging deploy / IaC preview)
- Verdict: `pass | review-required | block`

## Hand-off

- Application-side fixes → respective engineer (`api-engineer`, etc.)
- Schema-side fixes → `data-engineer`
- Auth-related (secret rotation, IAM) → `auth-security-engineer`

## Notes

- Production deploys must be reproducible from VCS — no manual artifacts.
- IaC drift is detected before each deploy (terraform plan / pulumi preview).
- A change that bypasses CI is a process bug, not a shortcut.
