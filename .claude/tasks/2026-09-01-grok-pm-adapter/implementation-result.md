# Implementation Result

Status: PASS

## Summary

Completed Addendum 10:

- Closed command-substitution-start bypasses for all four Bash deny rules.
- Covered `$(` and backtick substitutions, including horizontal whitespace after the opener.
- Added regression tests for required substitution cases, allow/deny collisions, and all four deny families.
- Corrected the README: permission regexes are best-effort; it no longer claims Bash hooks enforce these command-policy rules.
- Removed `.tmp-grok-child-output-fixture/`.
- Preserved all unrelated worktree changes.
- No network, commits, deployment, migrations, production credentials, or destructive Git operations were used.

## Files changed

Complete task change set relative to the pre-task baseline:

New `.grok/` adapter tree:

- [.grok/config.toml](/Users/ohayotaro/claude-fullstack/.grok/config.toml:1) — touched in Addendum 10.
- [.grok/README.md](/Users/ohayotaro/claude-fullstack/.grok/README.md:49) — touched in Addendum 10.
- `.grok/skills` → `../.claude/skills`
- [.grok/rules/00-pm-identity.md](/Users/ohayotaro/claude-fullstack/.grok/rules/00-pm-identity.md:1)
- [.grok/rules/10-harness-mapping.md](/Users/ohayotaro/claude-fullstack/.grok/rules/10-harness-mapping.md:1)
- [.grok/hooks/hooks.json](/Users/ohayotaro/claude-fullstack/.grok/hooks/hooks.json:1)
- [.grok/hooks/grok_hook_adapter.py](/Users/ohayotaro/claude-fullstack/.grok/hooks/grok_hook_adapter.py:1)

New test support and test modules:

- [.claude/hooks/tests/conftest.py](/Users/ohayotaro/claude-fullstack/.claude/hooks/tests/conftest.py:1)
- [.claude/hooks/tests/test_grok_configuration.py](/Users/ohayotaro/claude-fullstack/.claude/hooks/tests/test_grok_configuration.py:194) — touched in Addendum 10.
- [.claude/hooks/tests/test_grok_hook_adapter.py](/Users/ohayotaro/claude-fullstack/.claude/hooks/tests/test_grok_hook_adapter.py:1)
- [.claude/hooks/tests/test_hook_compatibility.py](/Users/ohayotaro/claude-fullstack/.claude/hooks/tests/test_hook_compatibility.py:1)

Previously approved documentation/rule modifications:

- [CLAUDE.md](/Users/ohayotaro/claude-fullstack/CLAUDE.md:139)
- [.claude/rules/common/document-lifecycle.md](/Users/ohayotaro/claude-fullstack/.claude/rules/common/document-lifecycle.md:26)
- [.claude/skills/checkpointing/SKILL.md](/Users/ohayotaro/claude-fullstack/.claude/skills/checkpointing/SKILL.md:1)

Removed in Addendum 10:

- `.tmp-grok-child-output-fixture/` — untracked test debris, now absent.

No existing `.claude/hooks/*.py`, `.claude/settings.json`, or `.claude/scripts/codex_handoff.py` file changed.

## Material design decisions

- All four deny rules now recognize `$(` and backtick as leading command boundaries.
- Optional horizontal whitespace after substitution openers is covered, such as `$( rm -rf build)`.
- Deny precedence remains necessary because `ls $(rm -rf build)` matches both `allow-ls` and the recursive-delete deny.
- `echo $(codex --search)` correctly matches a deny but does not match a configured allow family; `ls $(codex --search)` additionally proves the allow/deny collision.
- Quoting and variable indirection remain outside reliable regex-shell interpretation. The README now accurately describes live `grok inspect` verification and PM approval gating as the ultimate controls.
- Canonical Claude hook behavior and the Codex executor path remain unchanged.

## Exact validation commands and results

All commands ran from `/Users/ohayotaro/claude-fullstack`.

### Full pytest suite

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/pytest .claude/hooks/tests -q
........................................................................ [ 57%]
.....................................................                    [100%]
125 passed in 3.21s
```

### Ruff lint

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/JLy7sYrDEnNW04yKGmRkk/ruff-0.15.12.data/scripts/ruff check .grok/hooks/grok_hook_adapter.py .claude/hooks/tests
All checks passed!
```

### Ruff format check

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/JLy7sYrDEnNW04yKGmRkk/ruff-0.15.12.data/scripts/ruff format --check .grok/hooks/grok_hook_adapter.py .claude/hooks/tests
5 files already formatted
```

### TOML parse

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python -c "import tomllib; tomllib.load(open('.grok/config.toml', 'rb')); print('TOML OK')"
TOML OK
```

### Hook-registration JSON parse

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python -m json.tool .grok/hooks/hooks.json >/dev/null && echo 'JSON OK'
JSON OK
```

### Canonical-hook byte identity

```console
$ shasum -a 256 .claude/hooks/*.py
a6f93d5842c4e87b9b5574c303b45445e03da6191681c12f0d9e4f11f2073d5e  .claude/hooks/deploy-gate.py
58dc0700aa48ff64870ad2849141f07b88bf922f7e824f523bd8cfb4aad8cd1d  .claude/hooks/error-to-codex.py
755492e6e3001182441e58e6ccf0a52fc5f1ccbac8630c6109e114bebb8883af  .claude/hooks/log-cli-tools.py
cc9dbea3f5fbfc6d0bb0977a2278b2ea4581acdb86cc2369655762dd363f8ea5  .claude/hooks/pm-write-guard.py
dd0239c280bfc3f7e84257d881ff8322f6bc1ec00b8313943bf058f35b1dabeb  .claude/hooks/post-bash-dispatcher.py
e5994787af94620bd14c7b4b5ba5013a67caef5061dc1e9a2faf38c1fb3e43d8  .claude/hooks/secret-scan.py

$ git diff --quiet -- .claude/hooks/'*.py' .claude/scripts/codex_handoff.py && echo 'CANONICAL HOOKS AND CODEX HANDOFF DIFF: EMPTY'
CANONICAL HOOKS AND CODEX HANDOFF DIFF: EMPTY
```

Characterization tests for all six canonical hooks are included in the 125 passing tests.

### Secret, network, and fixture checks

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python - <<'PY'
import pathlib
import runpy
import subprocess

patterns = runpy.run_path('.claude/hooks/secret-scan.py')['SECRET_PATTERNS']
paths = subprocess.run(
    ['git', 'ls-files', '-co', '--exclude-standard', '-z'],
    check=True,
    stdout=subprocess.PIPE,
).stdout.decode().split('\0')
matches = []
for item in paths:
    if not item:
        continue
    path = pathlib.Path(item)
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        continue
    for pattern in patterns:
        if pattern.search(text):
            matches.append((item, pattern.pattern))
if matches:
    for path, pattern in matches:
        print(f'{path}: {pattern}')
    raise SystemExit(1)
print('TASK-TREE SECRET SCAN OK')
PY
TASK-TREE SECRET SCAN OK

$ if rg -n '(^|[^A-Za-z])(socket|urllib|requests|http\.client)([^A-Za-z]|$)' .grok/hooks/grok_hook_adapter.py .claude/hooks/tests; then exit 1; else echo 'NO NETWORK CODE'; fi
NO NETWORK CODE

$ test ! -e .tmp-grok-child-output-fixture && echo 'REPOSITORY STRAY FIXTURE: ABSENT'
REPOSITORY STRAY FIXTURE: ABSENT
```

## Required denial transcripts

### 1. Source write

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":"services/api.py","content":"pass"},"workspaceRoot":"/Users/ohayotaro/claude-fullstack"}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler pm-write-guard; echo $?
BLOCKED: Claude source/config writes are blocked by default. Create or update a canonical task brief and delegate technical work through `.claude/scripts/codex_handoff.py`. Allowed write roots: .claude/tasks, .claude/checkpoints, .claude/plans, .claude/state, .claude/docs/reviews
2
```

### 2. Production deployment without acknowledgment

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Bash","toolInput":{"command":"vercel --prod"},"workspaceRoot":"/Users/ohayotaro/claude-fullstack"}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler deploy-gate; echo $?
BLOCKED: Production-deploy command detected without valid acknowledgment.

Detected command:
  vercel --prod

Production-deploy acknowledgment required.

Before acknowledging, confirm ALL of:
  [ ] The task brief risk tier is T3 and explicit user approval is recorded
  [ ] Independent Codex review verdict is APPROVE (review.md)
  [ ] CI is green on the deploy target revision
  [ ] Database migrations (if any) have a documented backout plan
  [ ] Rollback procedure for the deploy target is known and tested
  [ ] Secrets are sourced from env/secret manager, none in the diff

When all items are true, acknowledge with:

  mkdir -p .claude/state
  touch .claude/state/deploy-$(date +%Y-%m-%d).ack

The acknowledgment is valid for 24 hours; re-create it per deploy day.

See .claude/rules/common/security.md and the /deploy skill for rationale.

2
```

### 3. Runtime-constructed fake secret

No contiguous secret-like literal is stored in this artifact.

```console
$ fake_secret=$(printf 'sk-'; printf 'A%.0s' {1..32}); printf '%s\n' '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":".claude/tasks/example/brief.md","content":"credential='"$fake_secret"'"},"workspaceRoot":"/Users/ohayotaro/claude-fullstack"}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler secret-scan; echo $?
[secret-scan] BLOCKED: probable secret in .claude/tasks/example/brief.md matching /sk-[A-Za-z0-9]{32,}/.
  Hard-coded secrets are forbidden. Use env vars or a secret manager.
  Override (NOT RECOMMENDED): CLAUDE_ALLOW_SECRET_WRITE=1 and retry.
2
```

### 4. Malformed JSON

```console
$ echo 'not-json' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler pm-write-guard; echo $?
Grok hook adapter denied the tool call: hook payload is not valid JSON: Expecting value: line 1 column 1 (char 0)
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: hook payload is not valid JSON: Expecting value: line 1 column 1 (char 0)"}
2
```

### 5. Non-standard payload `NaN`

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":"README.md","content":"value","number":NaN}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler pm-write-guard; echo $?
Grok hook adapter denied the tool call: non-standard JSON constant is not allowed: NaN
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: non-standard JSON constant is not allowed: NaN"}
2
```

### 6. Missing Bash command

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Bash","toolInput":{}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler deploy-gate; echo $?
Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string"}
2
```

### 7. Empty Bash command

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Bash","toolInput":{"command":""}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler deploy-gate; echo $?
Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string"}
2
```

### 8. Whitespace-only Bash command

Two backslashes are passed to the shell so `echo` emits valid JSON containing `\t`.

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Bash","toolInput":{"command":" \\t "}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler deploy-gate; echo $?
Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string"}
2
```

### 9. Non-string Bash command

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Bash","toolInput":{"command":0}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler deploy-gate; echo $?
Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Bash command must be a non-empty, non-whitespace string"}
2
```

### 10. Missing write target

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"content":"harmless"}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler secret-scan; echo $?
Grok hook adapter denied the tool call: Write file_path must be a non-empty, non-whitespace string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Write file_path must be a non-empty, non-whitespace string"}
2
```

### 11. PM write-guard event downgrade attempt

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":".claude/tasks/example/brief.md","content":"harmless"}}' | python3 .grok/hooks/grok_hook_adapter.py --event PostToolUse --handler pm-write-guard; echo $?
Grok hook adapter denied the tool call: payload event 'PreToolUse' does not match expected 'PostToolUse'
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: payload event 'PreToolUse' does not match expected 'PostToolUse'"}
2
```

### 12. Secret-scan event downgrade attempt

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":".claude/tasks/example/brief.md","content":"harmless"}}' | python3 .grok/hooks/grok_hook_adapter.py --event PostToolUse --handler secret-scan; echo $?
Grok hook adapter denied the tool call: payload event 'PreToolUse' does not match expected 'PostToolUse'
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: payload event 'PreToolUse' does not match expected 'PostToolUse'"}
2
```

### 13. Deploy-gate event downgrade attempt

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Bash","toolInput":{"command":"pytest -q"}}' | python3 .grok/hooks/grok_hook_adapter.py --event PostToolUse --handler deploy-gate; echo $?
Grok hook adapter denied the tool call: payload event 'PreToolUse' does not match expected 'PostToolUse'
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: payload event 'PreToolUse' does not match expected 'PostToolUse'"}
2
```

### 14. Non-standard child-output `NaN`

The child fixture came from pytest’s managed temporary directory; no repository fixture was recreated.

```console
$ child_fixture=/private/var/folders/z8/dfl5rwgd58jcb4d7yy62876m0000gn/T/pytest-of-ohayotaro/pytest-131/test_nonstandard_constant_in_c0
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":".claude/tasks/example/brief.md","content":"harmless"},"workspaceRoot":"'"$child_fixture"'"}' | python3 "$child_fixture/.grok/hooks/grok_hook_adapter.py" --event PreToolUse --handler pm-write-guard; echo $?
Grok hook adapter denied the tool call: canonical hook emitted malformed JSON: non-standard JSON constant is not allowed: NaN
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: canonical hook emitted malformed JSON: non-standard JSON constant is not allowed: NaN"}
2
```

### 15. Unknown-shape PostToolUse payload

```console
$ echo '{}' | python3 .grok/hooks/grok_hook_adapter.py --event PostToolUse --handler post-bash-dispatcher; echo $?
Grok hook adapter denied the tool call: unknown payload shape: toolName/tool_name is missing
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: unknown payload shape: toolName/tool_name is missing"}
2
```

### 16. Missing `Write.content`

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Write","toolInput":{"file_path":".claude/tasks/example/brief.md"}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler secret-scan; echo $?
Grok hook adapter denied the tool call: Write content must be a string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Write content must be a string"}
2
```

### 17. Non-string `Edit.new_string`

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"Edit","toolInput":{"file_path":".claude/tasks/example/brief.md","new_string":0}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler secret-scan; echo $?
Grok hook adapter denied the tool call: Edit new_string must be a string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: Edit new_string must be a string"}
2
```

### 18. Non-list `MultiEdit.edits`

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"MultiEdit","toolInput":{"file_path":".claude/tasks/example/brief.md","edits":{}}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler secret-scan; echo $?
Grok hook adapter denied the tool call: MultiEdit edits must be a non-empty list
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: MultiEdit edits must be a non-empty list"}
2
```

### 19. Non-string `NotebookEdit.new_source`

```console
$ echo '{"hookEventName":"PreToolUse","toolName":"NotebookEdit","toolInput":{"notebook_path":".claude/tasks/example/notebook.ipynb","new_source":["source"]}}' | python3 .grok/hooks/grok_hook_adapter.py --event PreToolUse --handler secret-scan; echo $?
Grok hook adapter denied the tool call: NotebookEdit new_source must be a string
{"decision": "deny", "reason": "Grok hook adapter denied the tool call: NotebookEdit new_source must be a string"}
2
```

## Multiline allow/deny collision transcript

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python - <<'PY'
import re
import tomllib

with open('.grok/config.toml', 'rb') as stream:
    rules = tomllib.load(stream)['permissions']['rules']
allow = [re.compile(rule['pattern']) for rule in rules if rule['action'] == 'allow']
deny = [(rule['name'], re.compile(rule['pattern'])) for rule in rules if rule['action'] == 'deny']
commands = [
    'ls -la\nrm -rf build\n',
    'ls -la\ngit commit --no-verify\n',
    'ls -la\ncodex --search topic\n',
    'ls -la\ncodex --dangerously-bypass-approvals-and-sandbox exec\n',
]
for command in commands:
    matched_denies = [name for name, pattern in deny if pattern.search(command)]
    matched_allow = any(pattern.search(command) for pattern in allow)
    decision = 'deny' if matched_allow and matched_denies else 'unexpected'
    print(f'payload={command!r}')
    print(f'allow_collision={matched_allow} deny_rules={matched_denies} decision={decision}')
    if decision != 'deny':
        raise SystemExit(1)
PY
echo $?
payload='ls -la\nrm -rf build\n'
allow_collision=True deny_rules=['deny-recursive-force-delete'] decision=deny
payload='ls -la\ngit commit --no-verify\n'
allow_collision=True deny_rules=['deny-hook-bypass'] decision=deny
payload='ls -la\ncodex --search topic\n'
allow_collision=True deny_rules=['deny-codex-network-search'] decision=deny
payload='ls -la\ncodex --dangerously-bypass-approvals-and-sandbox exec\n'
allow_collision=True deny_rules=['deny-codex-sandbox-bypass'] decision=deny
0
```

## Addendum 10 substitution-start collision transcript

This probe loads the actual TOML expressions. It does not execute the embedded shell commands.

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python - <<'PY'
import re
import tomllib

with open('.grok/config.toml', 'rb') as stream:
    rules = tomllib.load(stream)['permissions']['rules']
allow = [re.compile(rule['pattern']) for rule in rules if rule['action'] == 'allow']
deny = [(rule['name'], re.compile(rule['pattern'])) for rule in rules if rule['action'] == 'deny']
commands = [
    'ls $(rm -rf build)',
    'ls `rm -rf build`',
    'echo $(codex --search)',
    'ls $(codex --search)',
    'ls `codex --dangerously-bypass-approvals-and-sandbox`',
]
for command in commands:
    matched_denies = [name for name, pattern in deny if pattern.search(command)]
    matched_allow = any(pattern.search(command) for pattern in allow)
    decision = 'deny' if matched_denies else 'unexpected'
    print(f'command={command!r}')
    print(f'allow_match={matched_allow} deny_rules={matched_denies} decision={decision}')
    if decision != 'deny':
        raise SystemExit(1)
PY
probe_status=$?
printf 'exit_code=%s\n' "$probe_status"
command='ls $(rm -rf build)'
allow_match=True deny_rules=['deny-recursive-force-delete'] decision=deny
command='ls `rm -rf build`'
allow_match=True deny_rules=['deny-recursive-force-delete'] decision=deny
command='echo $(codex --search)'
allow_match=False deny_rules=['deny-codex-network-search'] decision=deny
command='ls $(codex --search)'
allow_match=True deny_rules=['deny-codex-network-search'] decision=deny
command='ls `codex --dangerously-bypass-approvals-and-sandbox`'
allow_match=True deny_rules=['deny-codex-sandbox-bypass'] decision=deny
exit_code=0
```

The tests additionally cover `$(` and backtick forms of `--no-verify`, and whitespace immediately after substitution openers.

### Legitimate inert-text probe

```console
$ /Users/ohayotaro/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python - <<'PY'
import re
import tomllib

with open('.grok/config.toml', 'rb') as stream:
    rules = tomllib.load(stream)['permissions']['rules']
deny = [re.compile(rule['pattern']) for rule in rules if rule['action'] == 'deny']
commands = [
    "printf '%s' 'rm -rf build'",
    "printf '%s' 'codex --search'",
    "printf '%s' 'codex --dangerously-bypass-approvals-and-sandbox'",
]
for command in commands:
    matched = any(pattern.search(command) for pattern in deny)
    print(f'command={command!r} deny_match={matched}')
    if matched:
        raise SystemExit(1)
PY
probe_status=$?
printf 'exit_code=%s\n' "$probe_status"
command="printf '%s' 'rm -rf build'" deny_match=False
command="printf '%s' 'codex --search'" deny_match=False
command="printf '%s' 'codex --dangerously-bypass-approvals-and-sandbox'" deny_match=False
exit_code=0
```

## Acceptance-criteria mapping

| Criterion | Result |
|---|---|
| AC1 | PASS — complete English `.grok/` adapter tree, shared-skills link, rules, registration, config, adapter, and README are present. |
| AC2 | PASS — Grok camelCase and Claude snake_case normalization, delegation, and exit semantics are covered. |
| AC3 | PASS — malformed payloads, route mismatches, child failures, non-standard JSON, malformed Bash fields, and uninspectable write content fail closed. |
| AC4 | PASS — allow, source-write deny, deploy deny, runtime-secret deny, both payload shapes, and error paths run without Grok CLI. |
| AC5 | PASS — all six canonical hooks pass Claude-shaped characterization tests and remain byte-identical. |
| AC6 | PASS — required deny families cover shell separators, newlines, trailing newlines, closing parentheses, and command-substitution starts, including allow-rule collisions. |
| AC7 | PASS — README documents trust, fail-open behavior, inspection, recursive rule verification, fallback instructions, and regex-policy limitations without claiming a nonexistent hook backstop. |
| AC8 | PASS — regression coverage confirms unchanged `pm-write-guard.py` blocks `.grok/**`. |
| AC9 | PASS — adapter is standard-library-only, uses no network, stores no secret, and requires no runtime network access. |
| Finding 15 | PASS — all four leading boundaries cover `$(`/backticks; collision tests and transcripts pass; README corrected; stray fixture removed. |

## Residual risks, debt, or blockers

- Effective Grok permission-schema interpretation, matcher precedence, hook registration, recursive `.claude/rules/**` loading, and live firing still require `/hooks-trust` and `grok inspect` on a machine with Grok Build installed.
- Grok remains host-level fail-open if hooks are untrusted, never started, externally killed, or externally timed out.
- Regex permission checks cannot fully model shell quoting, variable expansion, aliases, `eval`, or other arbitrary obfuscation.
- `echo $(codex --search)` is denied but is not itself an allow-family collision; `ls $(codex --search)` proves deny precedence against an actual configured broad allow.
