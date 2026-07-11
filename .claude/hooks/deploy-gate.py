#!/usr/bin/env python3
"""PreToolUse hook (Bash): Block production deploy / destructive-release
commands unless a safety acknowledgment is in place.

Detection patterns (T3 external side effects):
  - Production deploys: vercel --prod, wrangler deploy/publish, fly/flyctl deploy,
    kubectl apply/delete, terraform apply/destroy, eas submit, fastlane deliver
  - Production migrations: prisma migrate deploy, alembic upgrade against prod env
  - Production env markers: NODE_ENV=production, --env production, *.env.production
  - Registry publishes: npm/pnpm/yarn publish

Gates (in order):
  1. Freeze: if .claude/state/DEPLOY_FREEZE exists -> block.
  2. Acknowledgment: .claude/state/deploy-{YYYY-MM-DD}.ack created within the
     last 24 hours. If absent or stale -> block with checklist.
  3. Otherwise -> allow.

Exit codes:
  0 = allow (no deploy indicator, or all gates pass)
  2 = block (Claude Code surfaces stderr to the model)
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

DEPLOY_PATTERNS = [
    r"\bvercel\b.*--prod\b",
    r"\bwrangler\s+(deploy|publish)\b",
    r"\bfly(ctl)?\s+deploy\b",
    r"\bkubectl\s+(apply|delete)\b",
    r"\bterraform\s+(apply|destroy)\b",
    r"\beas\s+submit\b",
    r"\bfastlane\s+(deliver|supply|pilot)\b",
    r"\bprisma\s+migrate\s+deploy\b",
    r"\b(npm|pnpm|yarn)\s+publish\b",
    r"\bNODE_ENV\s*=\s*['\"]?production\b",
    r"--env[\s=]+['\"]?production\b",
    r"--env-file\s+\S*\.env\.production\b",
]

# Verbs that can never deploy. If the command starts with one of these, skip
# the deploy-pattern scan entirely -- otherwise commit messages, echo strings,
# and grep queries mentioning deploy keywords would false-positive.
SAFE_LEAD_VERBS = {
    "git", "gh", "echo", "printf", "cat", "head", "tail", "less", "more",
    "grep", "rg", "awk", "sed", "wc", "sort", "uniq", "find", "ls", "pwd",
    "diff", "jq", "tr", "cut", "rm", "mkdir", "rmdir", "touch", "mv", "cp",
    "chmod", "chown", "stat", "tree", "which", "type",
}


def first_executable_verb(command: str) -> str | None:
    """Return the first non-env-var-assignment token's basename, or None."""
    for tok in command.strip().split():
        if "=" in tok and "/" not in tok and not tok.startswith("-"):
            continue
        return os.path.basename(tok)
    return None


CHECKLIST = """Production-deploy acknowledgment required.

Before acknowledging, confirm ALL of:
  [ ] The task brief risk tier is T3 and explicit user approval is recorded
  [ ] Independent Codex review verdict is APPROVE (review.md)
  [ ] CI is green on the deploy target revision
  [ ] Database migrations (if any) have a documented backout plan
  [ ] Rollback procedure for the deploy target is known and tested
  [ ] Secrets are sourced from env/secret manager, none in the diff

When all items are true, acknowledge with:

  mkdir -p .claude/state
  touch .claude/state/deploy-$(date +%Y-%m-%d).ack

The acknowledgment is valid for 24 hours; re-create it per deploy day.

See .claude/rules/common/security.md and the /deploy skill for rationale.
"""


def acknowledgment_valid(state_dir: str) -> bool:
    if not os.path.isdir(state_dir):
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)  # noqa: UP017
    for entry in os.listdir(state_dir):
        if not (entry.startswith("deploy-") and entry.endswith(".ack")):
            continue
        full = os.path.join(state_dir, entry)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=timezone.utc)  # noqa: UP017
        except OSError:
            continue
        if mtime >= cutoff:
            return True
    return False


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    verb = first_executable_verb(command)
    if verb and verb in SAFE_LEAD_VERBS:
        sys.exit(0)

    if not any(re.search(p, command) for p in DEPLOY_PATTERNS):
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

    # Gate 1: deploy freeze
    freeze_path = os.path.join(project_dir, ".claude", "state", "DEPLOY_FREEZE")
    if os.path.exists(freeze_path):
        print(
            "BLOCKED: Deploy freeze active (.claude/state/DEPLOY_FREEZE exists). "
            "Production deploys are denied until the freeze is lifted.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Gate 2: 24-hour acknowledgment file
    state_dir = os.path.join(project_dir, ".claude", "state")
    if acknowledgment_valid(state_dir):
        sys.exit(0)

    print(
        f"BLOCKED: Production-deploy command detected without valid acknowledgment.\n\n"
        f"Detected command:\n  {command}\n\n"
        f"{CHECKLIST}",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
