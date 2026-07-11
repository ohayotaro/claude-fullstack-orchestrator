#!/usr/bin/env bash
#
# update.sh — refresh the Fullstack PM/Engineering Orchestrator template in an
# existing project. Backs up Zone B + Codex project notes, pulls latest,
# restores backups.
#
# Usage (from project root):
#   bash <(curl -fsSL https://raw.githubusercontent.com/ohayotaro/claude-fullstack/main/scripts/update.sh)
#
# Or, if scripts/update.sh has already been copied locally:
#   ./scripts/update.sh
#
# Behavior:
#   1. Backs up CLAUDE.md Zone B (between @orchestra:template-boundary
#      and @orchestra:repo-boundary)
#   2. Backs up AGENTS.md project notes (between @codex:template-boundary
#      and @codex:repo-boundary)
#   3. Clones the latest template into .starter-update/
#   4. Overwrites .claude/, .codex/, CLAUDE.md, AGENTS.md
#   5. Restores Zone B and Codex project notes from the backups
#   6. Cleans up
#
# What is preserved:
#   - CLAUDE.md Zone B (your project-specific stack config)
#   - AGENTS.md project-specific Codex notes
#   - .claude/settings.local.json (per-machine overrides)
#   - .claude/projects/ (auto-memory store)
#   - .claude/tasks/, .claude/checkpoints/, .claude/plans/, .claude/state/,
#     .claude/logs/, .claude/.cache/ (PM orchestration artifacts and caches)
#   - .claude/docs/reviews/ (commit-worthy review and incident records)
#
# What is overwritten:
#   - CLAUDE.md Zone A (PM orchestration policy)
#   - AGENTS.md outside the project-notes section (Codex contract)
#   - .claude/hooks/, .claude/rules/, .claude/skills/, .claude/scripts/
#   - .claude/docs/CODEX_TASK_CONTRACT.md
#   - .claude/settings.json (re-add your custom permissions afterward
#     if needed; see settings.local.json for per-machine overrides)
#   - .codex/
#
# Anything in your project tree (apps/, packages/, services/, src/,
# etc.) is left untouched.

set -euo pipefail

REPO_URL="https://github.com/ohayotaro/claude-fullstack.git"
TMP_DIR=".starter-update"
BACKUP_ZONE_B=".zone-b.backup.md"
BACKUP_CODEX_NOTES=".codex-notes.backup.md"
BACKUP_STATE_DIR=".claude-state.backup"
BACKUP_REVIEWS_DIR=".claude-reviews.backup"

# Runtime state and user data preserved across updates.
# Each entry is moved aside before the .claude/ wipe and moved back after,
# so user memory and per-machine state survive even if the template no
# longer ships these paths.
STATE_ITEMS=(
  "settings.local.json"
  "projects"
  "tasks"
  "checkpoints"
  "plans"
  "state"
  "logs"
  ".cache"
)

red()    { printf "\033[31m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

require_file() {
  if [[ ! -f "$1" ]]; then
    red "Missing $1 — are you in the right project directory?"
    exit 1
  fi
}

# If the script crashes between the backup and restore steps, runtime state
# is sitting in $BACKUP_STATE_DIR/. Tell the user how to recover.
on_error() {
  if [[ -d "$BACKUP_STATE_DIR" ]] && [[ -n "$(ls -A "$BACKUP_STATE_DIR" 2>/dev/null)" ]]; then
    red ""
    red "update.sh failed mid-flight."
    red "Your runtime state (memory, tasks, checkpoints, logs, etc.) is preserved in:"
    red "  $BACKUP_STATE_DIR/"
    red "To recover after fixing the issue:"
    red "  cp -R $BACKUP_STATE_DIR/. .claude/ && rm -rf $BACKUP_STATE_DIR"
  fi
}
trap on_error ERR

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

# 3. Backup AGENTS.md project notes
if [[ -f "AGENTS.md" ]]; then
  yellow "Backing up AGENTS.md project notes → $BACKUP_CODEX_NOTES"
  awk '
    /@codex:template-boundary/ { in_notes=1; next }
    /@codex:repo-boundary/     { in_notes=0; next }
    in_notes { print }
  ' AGENTS.md > "$BACKUP_CODEX_NOTES"
fi

# 4. Clone latest template
yellow "Cloning latest template into $TMP_DIR/"
rm -rf "$TMP_DIR"
git clone --depth 1 "$REPO_URL" "$TMP_DIR"

# 5. Save runtime state before wiping .claude/
yellow "Saving runtime state → $BACKUP_STATE_DIR/"
rm -rf "$BACKUP_STATE_DIR" "$BACKUP_REVIEWS_DIR"
mkdir -p "$BACKUP_STATE_DIR"
for item in "${STATE_ITEMS[@]}"; do
  if [[ -e ".claude/$item" ]]; then
    mv ".claude/$item" "$BACKUP_STATE_DIR/$item"
  fi
done
if [[ -d ".claude/docs/reviews" ]]; then
  mv ".claude/docs/reviews" "$BACKUP_REVIEWS_DIR"
fi

# 6. Overwrite the template targets
yellow "Overwriting .claude/, .codex/, CLAUDE.md, AGENTS.md"
rm -rf .claude .codex CLAUDE.md AGENTS.md
cp -R "$TMP_DIR/.claude" .claude
cp -R "$TMP_DIR/.codex" .codex
cp "$TMP_DIR/CLAUDE.md" CLAUDE.md
cp "$TMP_DIR/AGENTS.md" AGENTS.md

# 7. Restore runtime state (user data wins over anything the new template ships)
yellow "Restoring runtime state from $BACKUP_STATE_DIR/"
for item in "${STATE_ITEMS[@]}"; do
  if [[ -e "$BACKUP_STATE_DIR/$item" ]]; then
    rm -rf ".claude/$item"
    mv "$BACKUP_STATE_DIR/$item" ".claude/$item"
  fi
done
rmdir "$BACKUP_STATE_DIR" 2>/dev/null || true
if [[ -d "$BACKUP_REVIEWS_DIR" ]]; then
  rm -rf ".claude/docs/reviews"
  mkdir -p ".claude/docs"
  mv "$BACKUP_REVIEWS_DIR" ".claude/docs/reviews"
fi

# 8. Restore Zone B
if [[ -s "$BACKUP_ZONE_B" ]]; then
  yellow "Restoring Zone B"
  python3 - "$BACKUP_ZONE_B" "CLAUDE.md" "@orchestra:template-boundary" "@orchestra:repo-boundary" <<'PY'
import sys
from pathlib import Path

backup = Path(sys.argv[1]).read_text()
target = Path(sys.argv[2])
start, end = sys.argv[3], sys.argv[4]
text = target.read_text()

i = text.find(start)
j = text.find(end)
if i == -1 or j == -1:
    print(f"[update.sh] {target} missing boundary markers; skipping restore", file=sys.stderr)
    sys.exit(0)

i_eol = text.find("\n", i)
new = text[:i_eol + 1] + "\n" + backup.rstrip("\n") + "\n\n" + text[j:]
target.write_text(new)
PY
fi

# 9. Restore AGENTS.md project notes
if [[ -s "$BACKUP_CODEX_NOTES" ]]; then
  yellow "Restoring AGENTS.md project notes"
  python3 - "$BACKUP_CODEX_NOTES" "AGENTS.md" "@codex:template-boundary" "@codex:repo-boundary" <<'PY'
import sys
from pathlib import Path

backup = Path(sys.argv[1]).read_text()
target = Path(sys.argv[2])
start, end = sys.argv[3], sys.argv[4]
text = target.read_text()

i = text.find(start)
j = text.find(end)
if i == -1 or j == -1:
    print(f"[update.sh] {target} missing boundary markers; skipping restore", file=sys.stderr)
    sys.exit(0)

i_eol = text.find("\n", i)
new = text[:i_eol + 1] + "\n" + backup.rstrip("\n") + "\n\n" + text[j:]
target.write_text(new)
PY
fi

# 10. Make hooks and runner executable
chmod +x .claude/hooks/*.py .claude/scripts/*.py 2>/dev/null || true

# 11. Cleanup
rm -rf "$TMP_DIR"
rm -f "$BACKUP_ZONE_B" "$BACKUP_CODEX_NOTES"
rm -rf "$BACKUP_STATE_DIR" "$BACKUP_REVIEWS_DIR" 2>/dev/null || true

green "Update complete."
yellow "Next steps:"
echo "  - Review changes: git diff"
echo "  - Re-add custom permissions to .claude/settings.json if you had any"
echo "  - Run /init-webdev or /backend-init if Zone B fields need reconfiguration"
