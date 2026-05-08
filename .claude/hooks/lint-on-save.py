#!/usr/bin/env python3
"""
Hook: lint-on-save
Event: PostToolUse (Edit / Write)
Severity: warn (when linter is available and the file fails)
Purpose: Run the appropriate linter for the edited file's language.
Silently exits if the linter binary is not available locally.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

EXT_TO_LINTERS = {
    ".ts": [["biome", "check", "--reporter=summary"], ["eslint", "--no-warn-ignored"]],
    ".tsx": [["biome", "check", "--reporter=summary"], ["eslint", "--no-warn-ignored"]],
    ".js": [["biome", "check", "--reporter=summary"], ["eslint", "--no-warn-ignored"]],
    ".jsx": [["biome", "check", "--reporter=summary"], ["eslint", "--no-warn-ignored"]],
    ".py": [["ruff", "check"]],
    ".swift": [["swiftlint", "lint", "--quiet"]],
    ".kt": [["ktlint"]],
    ".kts": [["ktlint"]],
    ".dart": [["dart", "analyze", "--fatal-warnings"]],
}


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

    p = Path(file_path)
    if not p.exists():
        sys.exit(0)

    candidates = EXT_TO_LINTERS.get(p.suffix)
    if not candidates:
        sys.exit(0)

    cmd = next((c for c in candidates if shutil.which(c[0])), None)
    if not cmd:
        sys.exit(0)

    try:
        result = subprocess.run(
            cmd + [str(p)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        sys.exit(0)
    except Exception:
        sys.exit(0)

    if result.returncode != 0:
        out = (result.stdout + result.stderr).strip()
        print(
            f"[lint-on-save] {p.suffix} lint failed for {file_path}:\n{out}",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
