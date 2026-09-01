# Design: `.grok` — Grok Build PM Adapter

- Date: 2026-09-01
- Status: PROPOSED (PM design; implementation is a T2 Codex task)
- Decision inputs: user selected "thin adapter" coexistence model; Codex remains the engineering executor.

## Goal

Allow Grok Build (xAI's agentic CLI) to assume the PM role currently held by Claude Code, in the same repository, without forking policy. `.claude/` stays the single source of truth for orchestration policy, rules, skills, tasks, and safety hooks. `.grok/` is a thin adapter that maps Grok Build's discovery and hook mechanisms onto those shared assets.

## Non-goals

- Replacing Codex as the engineering executor (`codex_handoff.py` flow is unchanged).
- Rewriting `.claude/hooks/*` or `.claude/skills/*` for Grok-specific formats.
- Supporting both PMs concurrently in one session (one PM at a time; artifacts are shared).

## Relevant Grok Build facts (verify against docs.x.ai/build during implementation)

1. Auto-loads `AGENTS.md` and `CLAUDE.md` project instructions (skips `.gitignore`d files).
2. Auto-loads every `*.md` under `.grok/rules/`.
3. Skills are Anthropic-format compatible; loaded from project skills dir or `~/.grok/skills/`.
4. `.grok/config.toml` carries project-shared permission rules, plugins, MCP servers.
5. Hooks run scripts at tool/session lifecycle events (payload schema differs from Claude Code's).
6. `grok inspect` reports which config sources were discovered — use as the smoke test.

## Directory design

```text
.grok/
  config.toml              # permissions (translated from .claude/settings.json), MCP, plugins
  rules/
    00-pm-identity.md      # Grok-specific delta: "you are the PM defined in CLAUDE.md"
    10-harness-mapping.md  # Grok tool-name ↔ policy mapping, artifact path table
  skills -> ../.claude/skills          # symlink (Anthropic-compatible)
  hooks/
    grok_hook_adapter.py   # translates Grok hook payloads → Claude hook stdin schema
  README.md                # adapter contract + grok inspect verification steps
```

Everything else is intentionally absent: tasks, checkpoints, state, docs, scripts, and the hook implementations remain under `.claude/`.

### Key decision 1: `.claude/` paths are the orchestration data store, not a Claude-only namespace

Grok PM writes task briefs to `.claude/tasks/<id>/`, checkpoints to `.claude/checkpoints/`, deploy acks to `.claude/state/`, reviews to `.claude/docs/reviews/`. Rationale:

- One audit trail regardless of which PM ran the task (acceptance records must not split).
- `deploy-gate.py`, `codex_handoff.py`, and `document-lifecycle.md` all hard-code these paths; changing them is a much larger refactor for zero benefit.
- `pm-write-guard` allowlists keep working unchanged.

`00-pm-identity.md` states this explicitly so Grok does not "helpfully" mirror artifacts into `.grok/`.

### Key decision 2: PM identity is a delta file, not a CLAUDE.md fork

Grok reads `CLAUDE.md` natively, so Zone A policy, Zone B stack, and Zone C context transfer for free. `.grok/rules/00-pm-identity.md` contains only:

- "The PM role that CLAUDE.md assigns to 'Claude' applies to you (Grok Build) when you are the running agent. 'Codex' remains the engineering executor."
- Language protocol restated (user interaction in Japanese; artifacts in English).
- Write-scope restated (PM paths only), because prompt-level policy is the first line of defense if hook parity lags.
- Pointer to `.claude/docs/CODEX_TASK_CONTRACT.md` and the runner commands.

No edit to CLAUDE.md Zone A is required. Optional future cleanup (separate task): rename the actor in Zone A from "Claude" to "the PM agent".

### Key decision 3: rules loading

`.claude/rules/**` is loaded selectively by the Claude harness via CLAUDE.md `active_rules`. Grok auto-loads *all* `.grok/rules/*.md` (flat). Options considered:

- (a) Symlink the whole `.claude/rules` tree → loads all lang rules for every project; token waste but zero maintenance.
- (b) Selective symlinks created by an init step (`common/*` always; `lang/<active>` per Zone B) → chosen.
- (c) Duplicate content → rejected (drift).

Implementation: a small idempotent script `.grok/sync-rules.sh` (or a step in a future `/grok-init` skill) that reads Zone B `active_rules` and (re)creates symlinks under `.grok/rules/`. Nested-directory loading must be verified; if Grok only loads the top level, the script flattens names (`common--security.md`).

### Key decision 4: hook parity via adapter shim (fail-closed)

The three enforcement hooks (`secret-scan`, `pm-write-guard`, `deploy-gate`) are deterministic safety gates and MUST run under Grok too — prompt-level policy is not enforcement. Existing scripts stay canonical; `.grok/hooks/grok_hook_adapter.py`:

1. Reads the Grok hook event (schema per docs.x.ai; to be confirmed first in implementation).
2. Maps Grok tool names → Claude tool names (write-tool set, bash-tool name).
3. Builds the Claude-shaped stdin payload (`{"tool_name": ..., "tool_input": {...}}`).
4. Sets `CLAUDE_PROJECT_DIR` to the repo root.
5. Execs the corresponding `.claude/hooks/<name>.py` and translates exit codes / block semantics back into whatever Grok's hook contract expects.
6. Fails closed: unknown payload shape or adapter error on a write/bash event → block, not allow.

`config.toml` (or Grok's hook registration mechanism) wires: pre-write → secret-scan + pm-write-guard; pre-bash → deploy-gate; post-bash → post-bash-dispatcher (best effort; advisory hooks may degrade gracefully, enforcement hooks may not).

`pm-write-guard` needs one content change regardless of harness: `.grok/` itself is template config, so writes to `.grok/**` stay blocked for the PM (same as `.claude/hooks/**`) — no allowlist addition.

### Key decision 5: permissions translation

`.grok/config.toml` permission rules are hand-translated from `.claude/settings.json` allow/deny lists (same command families: git read-only, python3, codex, test/lint runners; deny `rm -rf`, `--no-verify`, codex bypass flags). Claude's `Bash(prefix:*)` pattern syntax will not match Grok's rule syntax 1:1 — the implementation task includes a translation table in `.grok/README.md` and keeps the two files' intent in sync. Drift check added to `/checkpointing` drift list: "`.grok/config.toml` permission intent disagrees with `.claude/settings.json`".

### Skills

Symlink `.grok/skills -> ../.claude/skills` (Anthropic-compatible per xAI docs). Skills that reference Claude-harness-specific behavior (`/visual-verify` screenshot reading, background Bash for `codex_handoff.py implement`) get a compatibility note in `00-pm-identity.md`; any that prove non-portable get a Grok variant only when actually needed.

## Failure modes / open questions (resolve during implementation)

| # | Risk | Mitigation |
|---|---|---|
| 1 | Grok hook payload schema unknown/undocumented | First implementation step: capture a real payload with a logging stub; fail closed until mapped |
| 2 | Symlinks not followed (or broken on Windows checkouts) | `grok inspect` smoke test; fall back to sync-script copies with a drift check |
| 3 | No `PreCompact` equivalent → context loss of contract docs | Put the reload instruction in `00-pm-identity.md` (always-loaded rule) |
| 4 | `.gitignore`d file skipping hides local overrides | Keep all adapter files tracked |
| 5 | Grok loads both CLAUDE.md and AGENTS.md → PM reads engineering contract addressed to Codex | `00-pm-identity.md` clarifies AGENTS.md is Codex's contract, loaded for reference only |
| 6 | Permission syntax mismatch weakens deny rules | Deny rules verified by attempting each blocked command in a sandbox during acceptance |

## Acceptance criteria (for the implementation brief)

1. `grok inspect` in the repo shows: CLAUDE.md, both `.grok/rules/*` files, common rules (+ active lang rules), skills, hooks, config.toml.
2. Grok PM session: writing to `services/` or `apps/` is blocked; writing `.claude/tasks/<id>/brief.md` succeeds.
3. Grok PM session: a fake secret in a task brief write is blocked by secret-scan.
4. Grok PM session: `vercel --prod` (dry) is blocked without a fresh `.claude/state/deploy-*.ack`.
5. `codex_handoff.py plan/implement/review/status/collect` run identically from a Grok session.
6. No file under `.claude/` is modified except the pm-write-guard/document-lifecycle/checkpointing deltas named above.
7. `.grok/README.md` documents the adapter contract and the permission translation table.

## Risk tier

T2 (multi-file, safety-hook surface, new adapter architecture) → Codex plan → PM approval → implementation → fresh Codex review → PM acceptance.

## Addendum (2026-09-01): facts verified against docs.x.ai/build

Fetched by PM; supersedes the "verify during implementation" items above where they conflict.

1. **Hooks compatibility**: Grok Build loads hook *registrations* from Claude Code's `.claude/settings.json` natively (also `~/.grok/hooks/*.json` and `<project>/.grok/hooks/*.json`). Whether it also delivers Claude-shaped *payloads* in compat mode is undocumented — Grok's own payload uses `hookEventName`, `sessionId`, `cwd`, `workspaceRoot`, `toolName`, `toolInput` (camelCase), vs. Claude's `tool_name`/`tool_input`. The adapter shim remains the safe design; it may shrink to a payload/env normalizer if compat mode already translates.
2. **Env vars**: Grok provides `GROK_HOOK_EVENT`, `GROK_HOOK_NAME`, `GROK_SESSION_ID`, `GROK_WORKSPACE_ROOT` — not `CLAUDE_PROJECT_DIR`. The adapter (or a two-line fallback in each hook) must map `GROK_WORKSPACE_ROOT`/`workspaceRoot` → `CLAUDE_PROJECT_DIR`.
3. **Blocking semantics**: only `PreToolUse` blocks; exit 0 allows, exit 2 denies, or stdout JSON `{"decision": "deny", "reason": "..."}`. Exit-2 semantics match our hooks. **However, Grok hooks fail OPEN on timeout/crash/malformed output** (Claude Code's enforcement assumption is fail-closed). Mitigations: adapter must be crash-hardened (top-level try/except that exits 2 on any internal error for enforcement events), default 5s timeout must comfortably exceed hook runtime, and this residual risk is documented in `.grok/README.md`.
4. **Rules compatibility**: Grok also loads `.claude/rules/` natively (plus `.grok/rules/*.md`, `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`; `.gitignore`d files skipped; no size cap). Recursion into `.claude/rules/common|lang/**` is not clearly documented. If recursive: Key decision 3's symlink/sync machinery is unnecessary (all lang rules load — acceptable token cost); verify with `grok inspect`. If top-level only: fall back to the sync-script design.
5. **Trust gate**: project hooks execute only after explicit trust (`/hooks-trust` or `--trust`; persisted in `~/.grok/trusted_folders.toml`). `.grok/README.md` setup steps must include this, since without trust all enforcement hooks silently do not run (fail-open at the system level).
6. **Hook events available**: `SessionStart/End`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionDenied`, `Stop/StopFailure`, `Notification`, `SubagentStart/Stop`, `PreCompact`/`PostCompact` — `PreCompact` exists, so risk item 3 in the table above is downgraded (the existing PreCompact echo hook may carry over).
