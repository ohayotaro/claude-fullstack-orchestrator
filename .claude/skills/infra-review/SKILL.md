---
name: infra-review
description: PM intake for deployment topology, CI/CD, containers, and observability changes.
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# Infra Review

Infra work is T2 by default; anything applying to production (IaC apply, cluster apply, DNS, IAM) is T3.

## Intake

- Record the deployment target (Zone B), the change (pipeline, container, runtime config, observability), and environments affected.
- Capture current vs desired state; link IaC paths.

## Acceptance Checklist

- AC includes environment parity notes (local/staging/prod) and rollback procedure.
- AC includes health checks (liveness/readiness distinct) and graceful shutdown behavior preserved.
- AC includes observability: structured logs, RED/USE metrics, tracing propagation.
- AC includes secret sourcing via env/secret manager only.

## Delegation

Create the task brief and run `plan`. Production application of infra changes follows the T3 flow plus `deploy-gate` acknowledgment.
