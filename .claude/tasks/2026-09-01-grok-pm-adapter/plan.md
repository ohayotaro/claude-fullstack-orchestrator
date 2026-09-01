# Implementation Plan

## Recommended design and rationale

Implement `.grok/` as a thin, standard-library-only compatibility layer. Existing policy and hook implementations under `.claude/` remain canonical.

### Adapter structure

Create:

```text
.grok/
├── config.toml
├── README.md
├── skills -> ../.claude/skills
├── rules/
│   ├── 00-pm-identity.md
│   └── 10-harness-mapping.md
└── hooks/
    ├── hooks.json
    └── grok_hook_adapter.py
```

Use one hook-registration file to reduce registration drift and duplicate-key risk. It will register:

- `PreToolUse` write tools → `secret-scan`, then `pm-write-guard`
- `PreToolUse` Bash → `deploy-gate`
- `PostToolUse` Bash → `post-bash-dispatcher`

Each command invokes the adapter with an explicit expected event and allowlisted handler. This gives the adapter enough context to fail closed even when stdin is malformed or lacks recognizable event fields.

The adapter will:

1. Parse JSON strictly, rejecting duplicate JSON keys and conflicting camelCase/snake_case aliases.
2. Accept:
   - Grok fields: `hookEventName`, `toolName`, `toolInput`, `workspaceRoot`
   - Claude fields: `tool_name`, `tool_input`, with optional Claude event/session/result fields
3. Normalize known fields to the Claude contract, including post-tool result fields where supplied.
4. Map documented tool aliases conservatively to `Write`, `Edit`, `MultiEdit`, `NotebookEdit`, or `Bash`.
5. Validate that the payload tool/event matches the handler selected by the registration.
6. Derive the repository identity from the adapter’s own resolved path and reject conflicting payload/environment workspace roots for enforcement events.
7. set `CLAUDE_PROJECT_DIR` only in the child environment.
8. Run only an allowlisted `.claude/hooks/*.py` target through `sys.executable`, forwarding normalized JSON through stdin.
9. Preserve child stdout/stderr and exit codes `0` and `2`.
10. Convert missing scripts, unexpected child exit codes, timeouts, malformed payloads, normalization failures, and other internal errors into exit `2` plus valid `{"decision":"deny","reason":"..."}` output for enforcement calls.
11. Treat PostToolUse failures as advisory: report a warning and exit `0`, because PostToolUse cannot block.

Subprocess delegation is preferred over replacing the process because it permits timeout handling, output forwarding, exit-code validation, and fail-closed exception handling.

### Permissions and documentation

[.grok/config.toml](/Users/ohayotaro/claude-fullstack/.grok/config.toml) will translate all command-family intent from [.claude/settings.json](/Users/ohayotaro/claude-fullstack/.claude/settings.json), using boundary-aware Grok regex rules. Deny rules take precedence and explicitly cover:

- `rm -rf`
- `--no-verify`
- `codex --search`
- `codex --dangerously-bypass-approvals-and-sandbox`

The README will record the source-to-target translation, syntax uncertainties, trust prerequisite, native fail-open behavior, and exact `grok inspect` checks. TOML validity and pattern presence can be tested offline; actual Grok interpretation remains a PM/user acceptance check.

The rules will keep identity binding explicit:

- Grok assumes the PM role named “Claude” in `CLAUDE.md`.
- Codex remains the executor.
- User interaction is Japanese; artifacts and repository documentation are English.
- PM writes remain confined to approved `.claude/` artifact paths plus the existing root documentation exceptions.
- `AGENTS.md` is reference material addressed to Codex.
- After compaction, reload `CLAUDE.md`, `AGENTS.md`, `.claude/docs/CODEX_TASK_CONTRACT.md`, and the current brief.

### Minimal `.claude/` changes

- Add the configuration-intent drift check to [.claude/rules/common/document-lifecycle.md](/Users/ohayotaro/claude-fullstack/.claude/rules/common/document-lifecycle.md).
- Add the same check to [.claude/skills/checkpointing/SKILL.md](/Users/ohayotaro/claude-fullstack/.claude/skills/checkpointing/SKILL.md).
- Add one Grok adapter context entry to CLAUDE.md Zone C.
- Do not modify existing hook scripts: the current default-deny write guard already blocks `.grok/**`, and the adapter supplies `CLAUDE_PROJECT_DIR`.
- Do not modify `codex_handoff.py`.

## Alternatives considered

- Rely only on Grok’s `.claude/settings.json` compatibility: rejected because camelCase payload translation and `CLAUDE_PROJECT_DIR` behavior are undocumented, making enforcement fail open.
- Add Grok parsing to every existing hook: rejected because it duplicates adapter logic and increases regression risk in canonical Claude behavior.
- Add `GROK_WORKSPACE_ROOT` fallbacks to existing hooks: unnecessary because the adapter establishes `CLAUDE_PROJECT_DIR`; avoiding these edits strengthens AC5.
- Duplicate `.claude/rules` or skills into `.grok`: rejected because `.claude/` must remain the source of truth. Skills use the approved symlink; rules use native compatibility.
- Add `sync-rules.sh` immediately: deferred. The design addendum says Grok loads `.claude/rules/` natively; the README will describe the flatten/sync fallback only if `grok inspect` proves recursive loading is absent.
- Put tests in a generic root `tests/`: rejected because this template has no application test tree. `.claude/hooks/tests/` keeps safety-surface tests beside their canonical implementation.

## Impacted files/components

New:

- `.grok/config.toml`
- `.grok/README.md`
- `.grok/skills` symlink
- `.grok/rules/00-pm-identity.md`
- `.grok/rules/10-harness-mapping.md`
- `.grok/hooks/hooks.json`
- `.grok/hooks/grok_hook_adapter.py`
- `.claude/hooks/tests/conftest.py`
- `.claude/hooks/tests/test_grok_hook_adapter.py`
- `.claude/hooks/tests/test_hook_compatibility.py`
- Optionally `.claude/hooks/tests/test_grok_configuration.py` if configuration checks would otherwise make the adapter suite unclear

Modified:

- `CLAUDE.md` Zone C only
- `.claude/rules/common/document-lifecycle.md`
- `.claude/skills/checkpointing/SKILL.md`

Expected unchanged:

- Every existing `.claude/hooks/*.py`
- `.claude/settings.json`
- `.claude/scripts/codex_handoff.py`
- All other rule and skill content

## Implementation sequence

1. Record Git status and hashes of every existing hook script so unrelated work and byte identity can be verified afterward.
2. Add the English PM identity and harness-mapping rules, including the exact artifact-path and tool-name mappings.
3. Add the `.claude/skills` symlink and document symlink/rule-loading verification and fallback behavior.
4. Add `config.toml` with translated allow/deny intent and precedence.
5. Add `hooks.json`, using one registration source and explicit adapter event/handler arguments.
6. Implement strict payload parsing, normalization, workspace identity validation, handler allowlisting, child delegation, timeout handling, and enforcement fail-closed output.
7. Add isolated pytest fixtures that copy the adapter and canonical hooks into `tmp_path`, preventing real deploy acknowledgments, logs, or machine state from affecting tests.
8. Add adapter unit/integration tests for both payload shapes, routing, all required allow/deny cases, and failure handling.
9. Add direct Claude-shaped characterization tests for all six existing hook scripts.
10. Add the document-lifecycle, checkpointing, and Zone C deltas.
11. Run offline validation and compare hook hashes/diffs.
12. Provide manual deny transcripts and clearly defer Grok CLI inspection/live firing to PM acceptance.

## Test and validation plan

Run:

```bash
python3 -m pytest .claude/hooks/tests -q
ruff check .grok/hooks/grok_hook_adapter.py .claude/hooks/tests
python3 -m tomllib .grok/config.toml
python3 -m json.tool .grok/hooks/hooks.json
```

If `python3 -m tomllib` is unavailable as a CLI entry point, use a read-only `python3 -c` call to load the file with `tomllib`.

Tests will cover:

- Grok camelCase normalization.
- Claude snake_case normalization.
- Harmless write allow path.
- Source write blocked by `pm-write-guard`.
- `.grok/**` write blocked by the unchanged write guard.
- Production deploy blocked without acknowledgment.
- Runtime-constructed fake secret blocked without storing a contiguous secret-like literal in the repository.
- Missing handler script.
- Invalid JSON and unknown payload shape.
- Missing/malformed tool input.
- Unknown or mismatched tool/event/handler.
- Duplicate JSON keys and conflicting aliases.
- Child timeout and unexpected nonzero exit.
- Exact `0`/`2` propagation.
- PostToolUse delegation and non-blocking degradation.
- Direct Claude-shaped invocation of:
  - `pm-write-guard.py`
  - `secret-scan.py`
  - `deploy-gate.py`
  - `post-bash-dispatcher.py`
  - `error-to-codex.py`
  - `log-cli-tools.py`

Record manual implementation-result transcripts for each required deny scenario:

```bash
echo '<payload>' | python3 .grok/hooks/grok_hook_adapter.py ...
echo $?
```

Also validate:

- Existing hook hashes are unchanged.
- `git diff -- .claude/hooks/*.py` is empty.
- No adapter/test code performs network I/O.
- Registration targets exist and contain no duplicate JSON keys.
- Required deny expressions are present and match representative commands.
- `codex_handoff.py` has no diff.

Deferred PM/user validation on a machine with Grok Build:

- Run `/hooks-trust` or start with the documented trust option.
- Use `grok inspect` to verify config, identity rules, hook registrations, skill discovery, and recursive `.claude/rules/**` loading.
- Confirm each intended adapter hook is registered exactly once despite Claude-compat discovery.
- Fire live allow/deny scenarios without executing an actual deployment.
- Apply the documented flattened-rule fallback only if recursive rule loading is absent.

## Risks and blockers

- Exact Grok permission syntax cannot be verified offline. The file can be syntactically valid TOML and statically tested, but effective rule behavior requires `grok inspect` and sandboxed command attempts. This is a deferred acceptance risk, not a network requirement for implementation.
- Grok’s timeout/crash behavior remains fundamentally fail open if the adapter itself is never started or is externally killed. `/hooks-trust`, valid registration, short internal timeouts, and dual exit-code/JSON denial reduce but cannot eliminate that platform risk.
- Grok may discover both `.claude/settings.json` and `.grok/hooks/hooks.json`. `grok inspect` must verify effective registrations and identify duplicate invocation, especially duplicate PostToolUse telemetry.
- Recursive `.claude/rules/**` loading and symlink following remain unconfirmed. The README will provide explicit inspection and fallback steps; no speculative copies will be committed.
- Workspace-root validation must be exact to avoid delegating to hooks in a different checkout. The adapter-derived repository root will be authoritative.
- Tests cannot prove live Grok matcher names or permission-engine semantics without the CLI. They will prove payload compatibility and enforcement behavior independently of Grok.
- The untracked `.claude/plans/` and `.claude/tasks/` content is existing user/PM work and must remain untouched.
- No network access, external dependencies, deployment, migration, commit, push, or production credentials are needed.

## Acceptance-criteria mapping

| Criterion | Planned evidence |
|---|---|
| AC1 | Complete English `.grok/` tree, valid TOML/JSON, rules, registrations, adapter, README, and skills link reviewed against the approved design. |
| AC2 | Dual-shape normalization tests plus subprocess routing tests proving delegation and `0`/`2` propagation. |
| AC3 | Enforcement-context CLI arguments, strict parsing, top-level hardening, timeout/missing-script/error tests, and valid denial JSON with exit `2`. |
| AC4 | Pytest coverage for allow, source-write deny, deploy deny, secret deny, both payload shapes, and fail-closed cases without requiring Grok. |
| AC5 | Direct characterization tests for all existing scripts, unchanged source hashes, and an empty hook-script diff. |
| AC6 | Boundary-aware deny rules for all four required cases, static pattern tests, and a README translation/expressiveness table. |
| AC7 | README sections for trust, fail-open behavior, hardening limits, `grok inspect`, recursive rule verification, and fallback instructions. |
| AC8 | A direct regression test demonstrating the current default-deny guard blocks `.grok/**`; change the guard only if that test disproves inspection. |
| AC9 | Standard-library-only adapter, runtime-generated fake-secret fixture, source scan/review, and no network code or runtime network requirement. |