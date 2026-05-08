#!/usr/bin/env python3
"""
Hook: check-codex-on-contract-edit
Event: PreToolUse (Edit / Write)
Severity: warn
Purpose: Warn when editing contract-boundary files; recommend Codex review.
Reads .claude/contract-watch.json for patterns; falls back to defaults.
"""
import fnmatch
import json
import os
import sys
from pathlib import Path

DEFAULT_PATTERNS = [
    "apis/**/*.yaml", "apis/**/*.yml",
    "apis/**/*.graphql", "apis/**/*.gql", "apis/**/*.proto",
    "**/openapi.*", "**/schema.graphql", "**/schema.gql",
    "**/migrations/**/*.sql", "**/migrations/**/*.py",
    "**/migrations/**/*.ts", "**/migrations/**/*.js",
    "**/db/migrate/**", "**/alembic/versions/**",
    "**/prisma/migrations/**", "**/drizzle/**/*.sql",
    "packages/api-client/**", "packages/api/**",
    "packages/contracts/**", "packages/events/**",
]


def load_patterns():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    p = Path(project_dir) / ".claude" / "contract-watch.json"
    if p.exists():
        try:
            return json.loads(p.read_text()).get("patterns", DEFAULT_PATTERNS)
        except Exception:
            pass
    return DEFAULT_PATTERNS


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") not in ("Edit", "Write"):
        sys.exit(0)

    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    patterns = load_patterns()
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            file_path, "**/" + pattern
        ):
            print(
                f"[contract-watch] WARN: editing contract-boundary file {file_path}.\n"
                f"  Recommended: request Codex review via /codex-system, "
                f"/api-build, or /data-design before proceeding.\n"
                f"  This change may affect downstream consumers.",
                file=sys.stderr,
            )
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
