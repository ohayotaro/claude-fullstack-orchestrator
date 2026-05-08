#!/usr/bin/env python3
"""
Hook: suggest-gemini-visual
Event: PreToolUse (Read / WebFetch)
Severity: suggest
Purpose: Suggest delegating multimodal input to Gemini.
"""
import json
import sys

VISUAL_EXT = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
    ".pdf", ".mp4", ".mov", ".webm", ".heic", ".tiff",
)
FIGMA_HOST = "figma.com"


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = event.get("tool_name", "")
    if tool not in ("Read", "WebFetch"):
        sys.exit(0)

    target = ""
    if tool == "Read":
        target = event.get("tool_input", {}).get("file_path", "")
    elif tool == "WebFetch":
        target = event.get("tool_input", {}).get("url", "")

    if not target:
        sys.exit(0)

    target_lower = target.lower()
    is_visual = (
        any(target_lower.endswith(ext) for ext in VISUAL_EXT)
        or FIGMA_HOST in target_lower
    )

    if is_visual:
        print(
            f"[gemini-suggest] Multimodal target detected: {target}\n"
            f"  Consider /design-research, /design-extract, /visual-verify, "
            f"or /gemini-system instead of reading directly.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
