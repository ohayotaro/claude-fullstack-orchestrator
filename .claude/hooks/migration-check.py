#!/usr/bin/env python3
"""
Hook: migration-check
Event: PostToolUse (Edit / Write)
Severity: warn
Purpose: Detect destructive patterns in migration files; require Codex review.
"""
import fnmatch
import json
import re
import sys
from pathlib import Path

MIGRATION_PATTERNS = [
    "**/migrations/**", "**/db/migrate/**", "**/alembic/versions/**",
    "**/prisma/migrations/**", "**/drizzle/**/*.sql",
    "**/typeorm/migrations/**",
]

DESTRUCTIVE = [
    re.compile(r"\bDROP\s+(TABLE|COLUMN|INDEX|CONSTRAINT|SCHEMA|VIEW|TYPE)\b", re.IGNORECASE),
    re.compile(r"\bALTER\s+TABLE\b[^;]*\bDROP\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b(?!\s+\w+\s+WHERE)", re.IGNORECASE),
    re.compile(r"\bSET\s+NOT\s+NULL\b", re.IGNORECASE),
    re.compile(r"\bdrop_table\b|\bremove_column\b|\bdrop_column\b"),
    re.compile(r"op\.drop_(table|column|index|constraint)\b"),
]


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

    if not any(fnmatch.fnmatch(file_path, p) for p in MIGRATION_PATTERNS):
        sys.exit(0)

    p = Path(file_path)
    if not p.exists():
        sys.exit(0)

    try:
        content = p.read_text(errors="replace")
    except Exception:
        sys.exit(0)

    findings = []
    for pattern in DESTRUCTIVE:
        if pattern.search(content):
            findings.append(f"  - destructive pattern: /{pattern.pattern}/")

    if findings:
        print(
            f"[migration-check] WARN: destructive change in {file_path}:\n"
            + "\n".join(findings)
            + "\n  Required: Codex review (/data-design or /codex-system) "
            "and an inline backout plan in the migration message.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
