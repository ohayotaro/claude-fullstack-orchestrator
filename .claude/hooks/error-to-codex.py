#!/usr/bin/env python3
"""
Hook: error-to-codex
Event: PostToolUse (Bash)
Severity: suggest
Purpose: Detect error patterns in command output; suggest /codex-debugger.
"""
import json
import re
import sys

PATTERNS = [
    re.compile(r"Traceback \(most recent call last\):"),
    re.compile(r"\bUnhandledPromiseRejection\b"),
    re.compile(r"\bSegmentation fault\b"),
    re.compile(r"\bSIGSEGV\b|\bSIGABRT\b|\bSIGBUS\b"),
    re.compile(r"\bpanic:\s"),
    re.compile(r"\bUncaughtException\b"),
    re.compile(r"\b(RuntimeError|TypeError|ReferenceError|ValueError|KeyError|AttributeError)\b"),
    re.compile(r"\bENOENT\b|\bEACCES\b|\bECONNREFUSED\b|\bETIMEDOUT\b"),
    re.compile(r"\bfatal error:", re.IGNORECASE),
    re.compile(r"\bcompilation\s+error\b", re.IGNORECASE),
]


def extract_output(event):
    response = event.get("tool_response", {})
    if isinstance(response, dict):
        return response.get("output", "") or ""
    if isinstance(response, str):
        return response
    return ""


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") != "Bash":
        sys.exit(0)

    output = extract_output(event)
    if not output:
        sys.exit(0)

    for pattern in PATTERNS:
        match = pattern.search(output)
        if match:
            snippet = match.group(0)
            print(
                f"[error-to-codex] Error pattern detected: {snippet}\n"
                f"  Consider /codex-debugger for deep analysis "
                f"(or /incident-backend for production issues).",
                file=sys.stderr,
            )
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
