#!/usr/bin/env python3
"""
Hook: secret-scan
Event: PreToolUse (Edit / Write)
Severity: require-explicit-override
Purpose: Block writes that introduce hard-coded secrets / credentials.
Override: set CLAUDE_ALLOW_SECRET_WRITE=1 (NOT RECOMMENDED).
"""
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
PLACEHOLDER_HINTS = [
    r"<your[-_]",
    r"\{\{",
    r"REPLACE_ME",
    r"YOUR_",
    r"changeme",
    r"example",
    r"placeholder",
    r"xxxxxxxx",
]


def looks_like_placeholder(value: str) -> bool:
    return any(re.search(h, value, re.IGNORECASE) for h in PLACEHOLDER_HINTS)


def main():
    if os.environ.get("CLAUDE_ALLOW_SECRET_WRITE") == "1":
        sys.exit(0)

    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") not in ("Edit", "Write"):
        sys.exit(0)

    file_path = event.get("tool_input", {}).get("file_path", "")
    if any(file_path.endswith(a) for a in ALLOWLIST_FILES):
        sys.exit(0)

    new_content = (
        event.get("tool_input", {}).get("new_string")
        or event.get("tool_input", {}).get("content")
        or ""
    )
    if not isinstance(new_content, str) or not new_content:
        sys.exit(0)

    for pattern in SECRET_PATTERNS:
        match = pattern.search(new_content)
        if match and not looks_like_placeholder(match.group(0)):
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
