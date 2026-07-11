---
name: deploy
description: PM intake and gate procedure for production deployment.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Deploy

Deployment is T3. Claude never executes the deploy; the user (or an explicitly user-approved gated command) does.

## Preconditions

- The delivering task's independent review verdict is `APPROVE`.
- CI is green on the target revision.
- Migrations in the release have a backout plan.
- Explicit user approval is recorded in the task directory.

## Gate

The `deploy-gate` hook blocks production-deploy commands until acknowledged:

```bash
mkdir -p .claude/state
touch .claude/state/deploy-$(date +%Y-%m-%d).ack
```

Create `.claude/state/DEPLOY_FREEZE` to freeze all deploys during incidents.

## Post-Deploy

- Verify the declared health signal (error rate, latency, uptime check) and report it to the user.
- On regression, prefer rollback over forward-fix; open an incident brief via `/incident-response`.
