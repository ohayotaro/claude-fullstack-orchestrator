#!/usr/bin/env python3
"""
Hook: agent-router
Event: UserPromptSubmit
Severity: suggest
Purpose: Suggest the optimal delegation route based on prompt keywords.
Reads .claude/routing-keywords.json with fallback defaults.
"""
import json
import os
import sys
from pathlib import Path

DEFAULT_KEYWORDS = {
    "codex": [
        "design", "architecture", "schema", "endpoint", "contract",
        "アーキ", "設計", "選定", "比較", "リファクタ", "migration",
    ],
    "gemini": [
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf",
        "figma", "screenshot", "スクショ", "mock", "モック",
    ],
    "incident": [
        "5xx", "500 error", "production down", "queue stuck",
        "本番", "障害", "incident", "outage",
    ],
}


def load_config():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    p = Path(project_dir) / ".claude" / "routing-keywords.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return DEFAULT_KEYWORDS


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = (event.get("prompt") or "").lower()
    if not prompt:
        sys.exit(0)

    cfg = load_config()
    suggestions = []

    if any(w.lower() in prompt for w in cfg.get("codex", [])):
        suggestions.append(
            "[router] Detected design/architecture cue — consider /codex-system, "
            "/architecture-review, /api-build, /data-design, or /auth-design."
        )
    if any(w.lower() in prompt for w in cfg.get("gemini", [])):
        suggestions.append(
            "[router] Detected multimodal reference — consider /design-research, "
            "/design-extract, /visual-verify, or /gemini-system."
        )
    if any(w.lower() in prompt for w in cfg.get("incident", [])):
        suggestions.append(
            "[router] Detected incident signal — consider /incident-backend "
            "(backend) or /incident-response (frontend)."
        )

    if suggestions:
        print("\n".join(suggestions), file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
