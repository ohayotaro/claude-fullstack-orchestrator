---
name: deploy
description: Execute or scaffold a deployment to the target declared in Zone B (Vercel / Cloudflare / ECS Fargate / GKE / Render / Fly / TestFlight / Play Console / etc.). Owned by infra-engineer. Run after /infra-review approves and CI passes.
---

# /deploy

## Purpose

Go from "merged to main / release branch" to "running in the target environment" with the right pre-flight checks and rollback affordance.

## When to use

- Production deploy (after CI + staging smoke pass)
- Hotfix deploy (with abbreviated process and explicit rationale)
- New environment provisioning
- Rollback (treated as a deploy)

## Prerequisites

- Zone B `deployment_target` set
- CI pipeline green for the commit being deployed
- (For prod) staging smoke check passed
- Migrations either run or designed for online execution per `data-design`

## Steps

### 1. Pre-flight checklist

- Zone B `runtime_envs` matches the target
- Secrets present in the secret manager for the target environment
- Version tag / commit SHA recorded
- Recent infra changes reviewed via `/infra-review`
- For breaking changes: deprecation window respected; consumers ready

### 2. Choose path per Zone B target

#### Vercel
- `vercel deploy --prod` (CLI) or git-driven deploy
- Verify env vars present in the Vercel project per environment
- Preview URLs for non-prod branches

#### Cloudflare (Workers / Pages)
- `wrangler deploy` (Workers) or git-driven (Pages)
- KV / R2 / D1 bindings present in target environment

#### ECS Fargate / GKE / k8s self-managed
- Image tag updated in IaC
- `terraform apply` / `pulumi up` / `kubectl apply -k overlays/<env>`
- Watch deploy progression (`kubectl rollout status`)

#### Render / Fly / Railway
- Service config in repo; deploy via CLI or git-driven
- Health check endpoint must respond OK before traffic shift

#### iOS — TestFlight
- `eas submit -p ios` (Expo) or `xcodebuild` + `altool`
- App Store Connect API key configured in CI
- TestFlight build available to testers; production submission per release process

#### Android — Play Console
- `eas submit -p android` (Expo) or `gradle bundleRelease` + Play Console API
- Internal track first; promote to closed / open / production per release process

### 3. Run migrations (when applicable)

Per `data-design` plan:

- For standard migrations: run before app deploy
- For online migrations: per the documented procedure
- Verify migrations succeeded before promoting traffic

### 4. Deploy

Execute the path-specific command. Capture deploy ID / build ID.

### 5. Post-deploy smoke check

- Hit health endpoints
- Run smoke test suite (a tagged subset of e2e)
- Verify key business metrics in observability (no error spike, latency stable)

### 6. Promote traffic (canary / blue-green if applicable)

- Send a small percentage first
- Watch error rate and latency for the configured bake time
- Promote to 100% if metrics hold, otherwise rollback

### 7. Rollback procedure (always documented)

- One command (or one revert + redeploy)
- Backout for any data migration documented inline in the migration

### 8. Persist deploy record

Save to `.claude/logs/deploys/<env>-<timestamp>.md`:
- Commit SHA / version tag
- Migrations run
- Deploy ID
- Smoke check result
- Anomalies (if any)

## Output

- Deployed artifact
- Deploy record
- Verified smoke check + observability snapshot

## Hand-off

- If smoke or post-deploy metrics fail → `/incident-backend` or `/incident-response`
- If the deploy reveals an architectural concern → `/architecture-review` post-mortem

## Notes

- Production deploy is gated by CI + staging smoke. Hotfix override requires explicit user authorization with rationale.
- Rollback is a deploy of the previous good version, not a branch revert. Treat both with the same rigor.
- Schema migrations are deployed BEFORE app code, unless the migration is explicitly designed to run online.
