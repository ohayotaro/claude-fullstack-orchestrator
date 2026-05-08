#!/usr/bin/env python3
"""
Hook: log-cli-tools
Event: PostToolUse (Bash)
Severity: (none — observability only)
Purpose: Append a JSONL line to .claude/logs/cli-tools.jsonl when codex / gemini
CLI is invoked.
"""
import datetime
import json
import os
import sys
from pathlib import Path

TRACKED_TOOLS = ("codex", "gemini")


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") != "Bash":
        sys.exit(0)

    cmd = event.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    first_token = cmd.strip().split()[0] if cmd.strip() else ""
    if first_token not in TRACKED_TOOLS:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    log_dir = Path(project_dir) / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "cli-tools.jsonl"

    response = event.get("tool_response", {})
    exit_code = response.get("exit_code") if isinstance(response, dict) else None

    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool": first_token,
        "cmd": cmd,
        "exit_code": exit_code,
    }

    try:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
