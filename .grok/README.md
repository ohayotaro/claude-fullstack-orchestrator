# Grok Build PM Adapter

This directory lets Grok Build assume the PM role defined in `CLAUDE.md` while
keeping `.claude/` as the single source of truth. Codex remains the engineering
executor through `.claude/scripts/codex_handoff.py`.

## Setup and trust

1. Start Grok Build in the repository root.
2. Run `/hooks-trust`, or start Grok with its documented `--trust` option.
   Project hooks do not run before this explicit trust step; without it, the
   safety gates are not active.
3. Run `grok inspect` and complete the verification checklist below before
   allowing a PM session to modify artifacts.

Do not run Claude Code and Grok Build as PMs concurrently against the same
checkout.

## Adapter contract

`.grok/hooks/hooks.json` registers one hook source:

- PreToolUse writes run `secret-scan` and then `pm-write-guard`.
- PreToolUse Bash runs `deploy-gate`.
- PostToolUse Bash runs `post-bash-dispatcher` as advisory processing.

Each registration passes an expected event and an allowlisted handler to
`grok_hook_adapter.py`. The adapter strictly parses JSON, rejects duplicate
keys and conflicting camelCase/snake_case aliases, normalizes Grok payloads to
the Claude hook shape, verifies the tool/event/handler route and repository
identity, sets `CLAUDE_PROJECT_DIR` only for the child process, and delegates
through the current Python interpreter. It performs no network I/O and uses
only the Python standard library.

For PreToolUse, canonical exit codes 0 (allow) and 2 (deny) pass through.
Malformed payloads, missing scripts, timeouts, unexpected child exits, and
other adapter errors produce exit 2 plus denial JSON. PostToolUse failures
degrade to a warning and exit 0 only after the payload parses and the handler,
CLI event, and any payload or environment event positively identify the
advisory PostToolUse route. Malformed or otherwise unidentifiable payloads
always produce exit 2 plus denial JSON. Grok treats that exit as non-blocking
for PostToolUse because only PreToolUse can block a tool call.

Grok itself fails open when a hook times out, crashes, emits malformed output,
or was never trusted. The adapter hardens failures after it starts, but cannot
make the host fail closed if the adapter process is never launched or is
externally killed. Trust and live registration inspection remain mandatory.

## Permission translation

`.grok/config.toml` is a best-effort, boundary-aware regex translation of
`.claude/settings.json`. Deny rules are listed first and declare precedence over
allow rules.

| Claude intent | Grok rule intent |
|---|---|
| `Bash(git status:*)`, `git diff`, `git log` | Anchored allow regexes for the three read-only Git families |
| `python3`, `codex`, `mkdir`, `ls` | Anchored allow regexes for each command family |
| JS, Python, mobile, and E2E test/lint runners | Anchored allow regexes preserving every allowed family |
| `Bash(rm -rf:*)` | Deny a command segment beginning with `rm -rf` |
| `Bash(* --no-verify)` | Deny a boundary-delimited `--no-verify` argument |
| `Bash(codex * --search *)` | Deny `codex` with a `--search` argument |
| Codex dangerous sandbox-bypass flag | Deny `codex` with `--dangerously-bypass-approvals-and-sandbox` |
| Command substitution and shell obfuscation | Forbidden commands that start inside `$(...)` or backtick substitution are covered. Regex command policy remains best-effort against other shell obfuscation, including quoting and variable indirection; live `grok inspect` verification and PM approval gates remain the ultimate controls. |

The source matcher language and Grok regex schema are not proven equivalent
offline. In particular, compound shell parsing, alternate option spellings,
quoting, variable indirection, and precedence behavior may differ. Treat the
permission translation as best-effort until it passes live inspection. If `grok inspect` rejects or
reinterprets the `[permissions]` / `[[permissions.rules]]` schema, stop the PM
session and update this translation from the installed CLI's local help or
trusted documentation; do not silently remove a deny.

## `grok inspect` verification

After trust, run `grok inspect` and verify all of the following:

- The project `.grok/config.toml`, `CLAUDE.md`, `AGENTS.md`, both files under
  `.grok/rules/`, and `.grok/skills` are discovered.
- The four adapter commands are registered exactly once: two ordered write
  handlers, one PreToolUse Bash handler, and one PostToolUse Bash handler.
- Compatibility loading of `.claude/settings.json` did not create duplicate
  enforcement or telemetry calls.
- Every permission allow/deny rule is parsed, deny precedence is effective,
  and sandboxed attempts of the four documented deny families are rejected.
- `.claude/rules/common/*.md` and the active language rules selected in
  `CLAUDE.md` Zone B are loaded recursively.

Recursive `.claude/rules/**` discovery is not confirmed by the available
offline facts. If the nested common or active-language files are absent, stop
the session and open a Codex task to add the design's idempotent rule-sync
fallback. That fallback should create flat symlinks under `.grok/rules/` (for
example, `common--security.md`) for common rules and only Zone B's active
language rules, then repeat `grok inspect`. Do not copy rule contents or enable
all language variants speculatively.

Finally, fire harmless live checks: allow a PM task-artifact write; deny a
source write, a runtime-generated fake-secret write, and a production-deploy
command without an acknowledgment. Do not execute an actual deployment.
