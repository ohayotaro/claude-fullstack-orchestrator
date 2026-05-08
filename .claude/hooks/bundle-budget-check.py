#!/usr/bin/env python3
"""
Hook: bundle-budget-check
Event: PostToolUse (Bash)
Severity: warn (heuristic; concrete numeric extraction is project-specific)
Purpose: After a build command, surface the configured bundle / app-size budgets.
"""
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_THRESHOLDS = {
    "web_initial_js_kb_gzip": 200,
    "ios_app_size_mb": 100,
    "android_apk_size_mb": 50,
    "rn_bundle_kb": 4000,
}

BUILD_PATTERNS = [
    re.compile(r"\bbuild\b.*\b(succeeded|complete|finished|done)\b", re.IGNORECASE),
    re.compile(r"\bRoute\s+\(/\S*\)\s+\d", re.IGNORECASE),
    re.compile(r"\bChunk Names\b", re.IGNORECASE),
    re.compile(r"webpack\s+compiled\s+with", re.IGNORECASE),
    re.compile(r"\bvite\b.*\bbuilt\b", re.IGNORECASE),
    re.compile(r"\bxcodebuild\b.*\bBUILD\s+SUCCEEDED\b"),
    re.compile(r"\bBUILD\s+SUCCESSFUL\b"),
]


def load_thresholds():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    p = Path(project_dir) / ".claude" / "perf-thresholds.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return DEFAULT_THRESHOLDS


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") != "Bash":
        sys.exit(0)

    response = event.get("tool_response", {})
    output = response.get("output", "") if isinstance(response, dict) else (response or "")
    if not isinstance(output, str) or not output:
        sys.exit(0)

    if not any(p.search(output) for p in BUILD_PATTERNS):
        sys.exit(0)

    th = load_thresholds()
    print(
        "[bundle-budget] Build detected. Configured thresholds "
        "(override in .claude/perf-thresholds.json):\n"
        f"  web initial JS gzipped: {th.get('web_initial_js_kb_gzip')}KB\n"
        f"  iOS app: {th.get('ios_app_size_mb')}MB\n"
        f"  Android APK: {th.get('android_apk_size_mb')}MB\n"
        f"  RN bundle: {th.get('rn_bundle_kb')}KB\n"
        "  Verify outputs against budget; route to perf-optimizer if exceeded.",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
