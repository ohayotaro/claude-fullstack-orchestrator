#!/usr/bin/env python3
"""
Hook: secret-scan
Event: PreToolUse (Edit / Write / MultiEdit / NotebookEdit)
Severity: require-explicit-override
Purpose: Block writes that introduce hard-coded secrets / credentials.
Override: set CLAUDE_ALLOW_SECRET_WRITE=1 (NOT RECOMMENDED).
"""
from __future__ import annotations

import json
import os
import re
import sys

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                                       # AWS access key
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{40}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),                                 # Google API key
    re.compile(r"sk-[A-Za-z0-9]{32,}"),                                    # OpenAI / Anthropic-style
    re.compile(r"sk-ant-[A-Za-z0-9_-]{32,}"),                              # Anthropic
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),                                   # GitHub PAT
    re.compile(r"github_pat_[A-Za-z0-9_]{82}"),                            # GitHub fine-grained PAT
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),                               # Slack
    re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA|PRIVATE) ?(PRIVATE )?KEY-----"),
    re.compile(
        r"(?i)(api[_-]?key|secret|token|password|passphrase)\s*[:=]\s*"
        r"[\"'][A-Za-z0-9/_+=\-]{20,}[\"']"
    ),
]

ALLOWLIST_FILES = (
    ".env.example",
    ".env.template",
    "settings.example.json",
    "settings.local.json",
)
WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})
PLACEHOLDER_PATTERNS = [
    re.compile(r"^(?:sk-|ghp_|AKIA)?x{8,}$", re.IGNORECASE),
]
PLACEHOLDER_WORDS = frozenset(
    {
        "ACCESS",
        "API",
        "APP",
        "AWS",
        "CHANGE",
        "CHANGEME",
        "CLIENT",
        "DUMMY",
        "EXAMPLE",
        "FAKE",
        "GOOGLE",
        "GITHUB",
        "HERE",
        "ID",
        "KEY",
        "ME",
        "OPENAI",
        "PASSWORD",
        "PASSPHRASE",
        "PLACEHOLDER",
        "PRIVATE",
        "REPLACE",
        "SECRET",
        "SLACK",
        "TEST",
        "TOKEN",
        "VALUE",
        "YOUR",
    }
)


def looks_like_placeholder(value: str) -> bool:
    candidate = value.strip()
    assignment = re.search(r"[:=]\s*([\"']?)([^\"'\s]+)\1\s*$", candidate)
    if assignment:
        candidate = assignment.group(2)
    candidate = candidate.strip().strip("\"'")
    if any(pattern.fullmatch(candidate) for pattern in PLACEHOLDER_PATTERNS):
        return True

    if candidate.startswith("<") and candidate.endswith(">"):
        candidate = candidate[1:-1].strip()
    elif candidate.startswith("{{") and candidate.endswith("}}"):
        candidate = candidate[2:-2].strip()

    words = re.findall(r"[A-Za-z0-9]+", candidate)
    if not words:
        return False
    return all(word.upper() in PLACEHOLDER_WORDS for word in words)


def target_path_for_tool(tool_name: str, tool_input: dict[str, object]) -> str | None:
    if tool_name == "NotebookEdit":
        value = tool_input.get("notebook_path")
    elif tool_name in {"Write", "Edit", "MultiEdit"}:
        value = tool_input.get("file_path")
    else:
        return None
    if isinstance(value, str) and value.strip():
        return value
    return ""


def content_for_tool(tool_name: str, tool_input: dict[str, object]) -> str:
    if tool_name == "Write":
        value = tool_input.get("content")
        return value if isinstance(value, str) else ""
    if tool_name == "Edit":
        value = tool_input.get("new_string")
        return value if isinstance(value, str) else ""
    if tool_name == "MultiEdit":
        edits = tool_input.get("edits")
        if not isinstance(edits, list):
            return ""
        new_strings = [
            edit.get("new_string", "")
            for edit in edits
            if isinstance(edit, dict) and isinstance(edit.get("new_string"), str)
        ]
        return "\n".join(new_strings)
    if tool_name == "NotebookEdit":
        value = tool_input.get("new_source")
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "".join(item for item in value if isinstance(item, str))
    return ""


def main():
    if os.environ.get("CLAUDE_ALLOW_SECRET_WRITE") == "1":
        sys.exit(0)

    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = event.get("tool_name")
    if tool_name not in WRITE_TOOLS:
        sys.exit(0)

    tool_input = event.get("tool_input", {})
    if not isinstance(tool_input, dict):
        print(f"[secret-scan] BLOCKED: {tool_name} tool input must be a JSON object.", file=sys.stderr)
        sys.exit(2)

    file_path = target_path_for_tool(str(tool_name), tool_input)
    if not file_path:
        print(f"[secret-scan] BLOCKED: {tool_name} write target path is missing.", file=sys.stderr)
        sys.exit(2)

    if any(file_path.endswith(a) for a in ALLOWLIST_FILES):
        sys.exit(0)

    new_content = content_for_tool(str(tool_name), tool_input)
    if not isinstance(new_content, str) or not new_content:
        sys.exit(0)

    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(new_content):
            if looks_like_placeholder(match.group(0)):
                continue
            print(
                f"[secret-scan] BLOCKED: probable secret in {file_path} "
                f"matching /{pattern.pattern}/.\n"
                f"  Hard-coded secrets are forbidden. Use env vars or a secret manager.\n"
                f"  Override (NOT RECOMMENDED): CLAUDE_ALLOW_SECRET_WRITE=1 and retry.",
                file=sys.stderr,
            )
            sys.exit(2)  # block
    sys.exit(0)


if __name__ == "__main__":
    main()
