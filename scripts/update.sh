#!/usr/bin/env bash
#
# update.sh — refresh the Fullstack Orchestrator template in an existing
# project. Backs up Zone B + customizable JSON, pulls latest, restores
# backups.
#
# Usage (from project root):
#   bash <(curl -fsSL https://raw.githubusercontent.com/ohayotaro/claude-fullstack-orchestrator/main/scripts/update.sh)
#
# Or, if scripts/update.sh has already been copied locally:
#   ./scripts/update.sh
#
# Behavior:
#   1. Backs up CLAUDE.md Zone B (between @orchestra:template-boundary
#      and @orchestra:repo-boundary)
#   2. Backs up customizable JSON: routing-keywords.json,
#      perf-thresholds.json, visual-regression.json, contract-watch.json
#   3. Clones the latest template into .starter-update/
#   4. Overwrites .claude/, .codex/, .gemini/, CLAUDE.md
#   5. Restores Zone B and custom JSON from the backup
#   6. Cleans up
#
# What is preserved:
#   - CLAUDE.md Zone B (your project-specific stack config)
#   - .claude/routing-keywords.json (if customized)
#   - .claude/perf-thresholds.json (if customized)
#   - .claude/visual-regression.json (if customized)
#   - .claude/contract-watch.json (if customized)
#
# What is overwritten:
#   - CLAUDE.md Zone A (template orchestration policy)
#   - .claude/agents/, .claude/hooks/, .claude/rules/, .claude/skills/
#   - .claude/settings.json (re-add your custom permissions afterward
#     if needed; see settings.local.json for per-machine overrides)
#   - .claude/docs/CODEX_HANDOFF_PLAYBOOK.md, GEMINI_HANDOFF_PLAYBOOK.md
#   - .codex/, .gemini/
#
# Anything in your project tree (apps/, packages/, services/, src/,
# etc.) is left untouched.

set -euo pipefail

REPO_URL="https://github.com/ohayotaro/claude-fullstack-orchestrator.git"
TMP_DIR=".starter-update"
BACKUP_ZONE_B=".zone-b.backup.md"
BACKUP_ROUTING=".routing-keywords.backup.json"
BACKUP_PERF=".perf-thresholds.backup.json"
BACKUP_VISUAL=".visual-regression.backup.json"
BACKUP_CONTRACT=".contract-watch.backup.json"

red()    { printf "\033[31m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

require_file() {
  if [[ ! -f "$1" ]]; then
    red "Missing $1 — are you in the right project directory?"
    exit 1
  fi
}

# 1. Sanity check
if [[ ! -d ".claude" ]]; then
  red "No .claude/ here. Run this from the project root that already has the template installed."
  exit 1
fi
require_file "CLAUDE.md"

# 2. Backup Zone B
yellow "Backing up CLAUDE.md Zone B → $BACKUP_ZONE_B"
awk '
  /@orchestra:template-boundary/ { in_zone_b=1; next }
  /@orchestra:repo-boundary/     { in_zone_b=0; next }
  in_zone_b { print }
' CLAUDE.md > "$BACKUP_ZONE_B"

# 3. Backup customizable JSON
for pair in \
  ".claude/routing-keywords.json:$BACKUP_ROUTING" \
  ".claude/perf-thresholds.json:$BACKUP_PERF" \
  ".claude/visual-regression.json:$BACKUP_VISUAL" \
  ".claude/contract-watch.json:$BACKUP_CONTRACT"; do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if [[ -f "$src" ]]; then
    yellow "Backing up $src → $dst"
    cp "$src" "$dst"
  fi
done

# 4. Clone latest template
yellow "Cloning latest template into $TMP_DIR/"
rm -rf "$TMP_DIR"
git clone --depth 1 "$REPO_URL" "$TMP_DIR"

# 5. Overwrite the four targets
yellow "Overwriting .claude/, .codex/, .gemini/, CLAUDE.md"
rm -rf .claude .codex .gemini CLAUDE.md
cp -R "$TMP_DIR/.claude" .claude
cp -R "$TMP_DIR/.codex" .codex
cp -R "$TMP_DIR/.gemini" .gemini
cp "$TMP_DIR/CLAUDE.md" CLAUDE.md

# 6. Restore Zone B
if [[ -s "$BACKUP_ZONE_B" ]]; then
  yellow "Restoring Zone B"
  python3 - "$BACKUP_ZONE_B" <<'PY'
import sys
from pathlib import Path

backup = Path(sys.argv[1]).read_text()
claude_md = Path("CLAUDE.md")
text = claude_md.read_text()

start = "@orchestra:template-boundary"
end = "@orchestra:repo-boundary"
i = text.find(start)
j = text.find(end)
if i == -1 or j == -1:
    print("[update.sh] CLAUDE.md missing boundary markers; skipping Zone B restore", file=sys.stderr)
    sys.exit(0)

# Replace content between the line containing `start` and the line containing `end`.
i_eol = text.find("\n", i)
new = text[:i_eol + 1] + "\n" + backup.rstrip("\n") + "\n\n" + text[j:]
claude_md.write_text(new)
PY
fi

# 7. Restore customizable JSON
for pair in \
  "$BACKUP_ROUTING:.claude/routing-keywords.json" \
  "$BACKUP_PERF:.claude/perf-thresholds.json" \
  "$BACKUP_VISUAL:.claude/visual-regression.json" \
  "$BACKUP_CONTRACT:.claude/contract-watch.json"; do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if [[ -f "$src" ]]; then
    yellow "Restoring $dst"
    mv "$src" "$dst"
  fi
done

# 8. Make hooks executable
chmod +x .claude/hooks/*.py 2>/dev/null || true

# 9. Cleanup
rm -rf "$TMP_DIR"
rm -f "$BACKUP_ZONE_B"

green "Update complete."
yellow "Next steps:"
echo "  - Review changes: git diff"
echo "  - Re-add custom permissions to .claude/settings.json if you had any"
echo "  - Run /init-webdev or /backend-init if Zone B fields need reconfiguration"
