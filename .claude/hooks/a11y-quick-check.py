#!/usr/bin/env python3
"""
Hook: a11y-quick-check
Event: PostToolUse (Edit / Write)
Severity: suggest
Purpose: Static a11y heuristics on edited UI files. Recommend /a11y-audit on findings.
"""
import json
import re
import sys
from pathlib import Path

UI_EXT = {".tsx", ".jsx", ".swift", ".kt", ".dart"}

JSX_HEURISTICS = [
    (re.compile(r"<img\b(?![^>]*\balt=)", re.IGNORECASE), "img element missing alt"),
    (
        re.compile(r"<button\b[^>]*>\s*<svg", re.IGNORECASE),
        "icon-only button — verify aria-label",
    ),
    (
        re.compile(r"<a\b(?![^>]*\bhref=)[^>]*onClick=", re.IGNORECASE),
        "anchor without href but with onClick — should be a button",
    ),
    (
        re.compile(r"role=[\"']presentation[\"']", re.IGNORECASE),
        "role='presentation' — confirm decorative",
    ),
]
SWIFT_HEURISTICS = [
    (
        re.compile(r"\.onTapGesture\b"),
        "onTapGesture — verify accessibilityLabel/Hint on the tappable element",
    ),
    (
        re.compile(r"\bImage\([^)]*\)(?![^\n]*accessibilityLabel)"),
        "Image without accessibilityLabel — confirm decorative or add label",
    ),
]
COMPOSE_HEURISTICS = [
    (
        re.compile(r"\bIcon\([^)]*contentDescription\s*=\s*null"),
        "Icon contentDescription=null — confirm decorative",
    ),
    (
        re.compile(r"\bModifier\.clickable\b(?![^\n]*semantics)"),
        "Modifier.clickable without semantics — confirm a11y role",
    ),
]


def heuristics_for(suffix):
    if suffix in (".tsx", ".jsx"):
        return JSX_HEURISTICS
    if suffix == ".swift":
        return SWIFT_HEURISTICS
    if suffix == ".kt":
        return COMPOSE_HEURISTICS
    return []


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
    if p.suffix not in UI_EXT or not p.exists():
        sys.exit(0)

    try:
        content = p.read_text(errors="replace")
    except Exception:
        sys.exit(0)

    findings = []
    for pattern, message in heuristics_for(p.suffix):
        if pattern.search(content):
            findings.append(f"  - {message}")

    if findings:
        print(
            f"[a11y-quick] Possible a11y issues in {file_path}:\n"
            + "\n".join(findings)
            + "\n  Consider /a11y-audit before merging.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
