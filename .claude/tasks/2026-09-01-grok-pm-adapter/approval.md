# PM Approval: 2026-09-01-grok-pm-adapter

- Date: 2026-09-01
- Decision: APPROVED for implementation (T2)
- Approved plan: `plan.md` (Codex plan phase output, this task directory)

## Rationale

- The plan follows `.claude/plans/grok-pm-adapter-design.md` including the 2026-09-01 verified-facts addendum, and maps every AC1-AC9 to concrete evidence.
- Keeping every existing `.claude/hooks/*.py` byte-identical (adapter-side normalization, `CLAUDE_PROJECT_DIR` set in the child env) is stronger than the brief's optional env-fallback allowance; accepted.
- Single registration source (`.grok/hooks/hooks.json`) with explicit expected-event/handler arguments addresses the duplicate-key and identity-binding failure classes.
- Enforcement fail-closed conversion (exit 2 + denial JSON on any internal error) correctly compensates for Grok's documented fail-open hook behavior, with residual platform risk documented rather than hidden.
- Deferral of `sync-rules.sh` and live Grok verification to PM/user acceptance matches the brief's Open Decisions.

## Conditions

1. Test location `.claude/hooks/tests/` approved; tests must run offline with no Grok CLI.
2. No changes to `.claude/settings.json`, `codex_handoff.py`, or existing hook scripts (AC5 hash evidence required).
3. Model/effort: implementation runs on the strong tier (CLI default model) at the T2 default effort matrix — first implementation per the tier policy.

---

# Corrections Addendum (2026-09-01, after first review)

The first fresh review (`review.md`) returned CHANGES_REQUIRED with exactly one finding. This addendum enumerates the complete corrections scope; nothing else may change.

## Finding 1 (High) — deny-rule shell-boundary bypass in `.grok/config.toml`

Deny patterns at config.toml lines 17, 23, 29 require whitespace or end-of-string after the forbidden flag, so commands like `codex --search; true`, `codex --dangerously-bypass-approvals-and-sandbox; true`, and `git commit --no-verify;` escape the deny rules while matching the broad `allow-codex` rule (line 59). This fails AC6.

### Required fix (approved design)

1. Extend the boundary in the three deny patterns so the forbidden flag also matches when followed by shell separators: at minimum `;`, `&`, `|` (and closing parens/newlines if the syntax allows), not only whitespace/end-of-string. Keep patterns anchored so legitimate commands are not over-blocked.
2. Extend `.claude/hooks/tests/test_grok_configuration.py` with regression tests proving that EVERY forbidden variant — plain, and each separator-adjacent form (`;`, `&&`, `&`, `|`, `||`) — matches at least one deny rule, including cases where an allow-family rule also matches (deny precedence collision cases).
3. Re-run the full validation set: complete pytest suite, `ruff check` and `ruff format --check` on touched files, TOML parse check.
4. Update the `.grok/README.md` translation table only if the pattern change makes its documented expressions stale.

### Out of scope for this corrections run

Any change to the adapter, hooks.json, rules files, `.claude/` content, or other config.toml rules beyond the three deny patterns and their tests/docs.

## Tier selection (recorded per codex-delegation policy)

- Corrections implementation: mid tier (`gpt-5.6-terra`), effort `high` — permitted because the sole finding is enumerated with an approved fix design.
- Next review: final pre-acceptance full-scope review on the strong tier at effort `high` (no intermediate delta review; single bounded finding).

---

# Corrections Addendum 2 (2026-09-01, after mid-tier corrections run)

The mid-tier corrections run fixed the config.toml deny boundaries (verified: the per-rule assertion passes), but its new test code is defective and its self-validation was not run with pytest. PM verification:

```
$HOME/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/pytest .claude/hooks/tests -q
-> 18 failed, 38 passed
```

All 18 failures are the same defect in `test_grok_configuration.py::test_forbidden_flags_match_with_shell_separator_boundaries` (line ~115):

```python
assert any(pattern.search(command) for pattern in deny_patterns), command
# AttributeError: 'str' object has no attribute 'search' — iterating the dict yields keys
```

## Finding 1a (escalated to strong tier per policy rule 4)

1. Fix the defective iteration (e.g., `deny_patterns.values()`); audit the rest of the new test additions for the same class of bug and for assertions that never exercise the allow/deny collision intent (`matches_allow` parameter appears unused — verify it asserts something).
2. Re-run the FULL validation set and report actual outcomes: `pytest` (all tests must pass; the uv-cached runner above is available offline), `ruff check` and `ruff format --check` (cached at `$HOME/.cache/uv/archive-v0/JLy7sYrDEnNW04yKGmRkk/ruff-0.15.12.data/scripts/ruff`), TOML parse via the cached Python 3.11+ interpreter (`$HOME/.cache/uv/archive-v0/1THrNXMjbbr8cJws42Qrd/bin/python`). Do not report validation as passed on any substitute methodology.
3. Scope remains: `test_grok_configuration.py` (and `.grok/config.toml` only if the audit exposes a real pattern gap). Nothing else.
4. Reminder: task artifacts must be written in English (the previous result was partially Japanese — contract deviation, do not repeat).

Tier: strong (CLI default model), effort `high` — one-way escalation after defective mid-tier output.

---

# Corrections Addendum 3 (2026-09-01, after final full-scope review)

The final strong-tier review returned CHANGES_REQUIRED with one High and one Medium finding. Complete corrections scope; nothing else may change.

## Finding 2 (High) — malformed Bash payloads fail open through the deploy-gate route

The adapter validates only that `toolInput` is an object. A Bash PreToolUse payload with a missing, empty, whitespace-only, or non-string `command` (e.g. `{"toolName":"Bash","toolInput":{}}` or `{"command":0}`) passes through and `deploy-gate.py` allows falsey commands → exit 0. Violates AC3.

Required fix:

1. In `grok_hook_adapter.py`, for PreToolUse Bash enforcement events, require `command` to be a non-empty, non-whitespace string; otherwise deny (exit 2 + denial JSON). Do not modify `deploy-gate.py`.
2. Decide and document the analogous check for write-tool enforcement events (missing/non-string `file_path`): if not already fail-closed, make it so consistently.
3. Add regression tests on the REAL deploy-gate route for: missing `command`, empty string, whitespace-only, and non-string values (and the write-tool analogues if changed). The existing malformed-route test targeting pm-write-guard stays.

## Finding 3 (Medium) — implementation result lacks mandated transcripts

The brief's Required Validation mandates exact manual command transcripts with exit codes for every AC4 deny scenario. The new implementation result must embed the full `echo '<payload>' | python3 .grok/hooks/grok_hook_adapter.py ...` transcripts (command, key output, `echo $?`) for each deny scenario, including the new malformed-Bash denials.

## Validation for this run

Full suite via the offline cached toolchain (paths in Addendum 2): pytest all-pass, `ruff check`, `ruff format --check`, TOML parse. Report actual outputs. English only.

## Tier selection (deviation recorded per policy rule 5)

Strong tier (CLI default model), effort `high` — deviates from the mid-tier default for enumerated corrections because (a) the fix is on the fail-closed enforcement surface itself, and (b) the prior mid-tier run misreported validation, exhausting PM confidence in the economized gate for this task. A further final full-scope review (strong, `high`) will follow before acceptance.

---

# Corrections Addendum 4 (2026-09-01, after second final review)

Second final review: CHANGES_REQUIRED — one High, two Low. Complete corrections scope; nothing else may change.

## Finding 4 (High) — enforcement downgraded to advisory via `--event` mismatch

`grok_hook_adapter.py` classifies enforcement solely from the CLI `--event` argument. Invoking an enforcement handler with `--event PostToolUse` routes payload/route validation failures to `warn()` + exit 0 (reproduced: `--event PostToolUse --handler pm-write-guard` with a PreToolUse payload → exit 0). Violates AC3.

Required fix:

1. Classify a call as advisory ONLY when the handler itself is an advisory handler (post-bash-dispatcher route) AND the CLI event AND any payload/environment event consistently identify the advisory PostToolUse route. Any enforcement handler (pm-write-guard, secret-scan, deploy-gate) with any event inconsistency fails closed (exit 2 + denial JSON). Apply the same trust rule to the pre-execution event hint noted at lines 374-395.
2. Add regression tests: every enforcement handler invoked with `--event PostToolUse` (and with mismatched payload events) must exit 2.

## Finding 5 (Low) — secret-pattern literal stored in a tracked artifact

The new implementation result must not contain any contiguous secret-pattern-matching literal. In transcripts, construct or redact the fake secret (e.g. show the payload with a placeholder like `credential=sk-<32 redacted>` and note the runtime construction), consistent with the approved plan's runtime-construction approach. Confirm no other tracked file matches the repository secret patterns.

## Finding 6 (Low) — complete file accounting

The new implementation result's "Files changed" section must enumerate the complete task change set relative to the pre-task baseline: the full `.grok/` tree, all three test files, and the three tracked doc/rule modifications (CLAUDE.md Zone C, document-lifecycle.md, checkpointing SKILL.md), marking which files this corrections run touched.

## Validation for this run

Full suite via the offline cached toolchain (paths in Addendum 2), ruff check + format check, TOML/JSON parse, and manual transcripts for the new mismatch denials. English only.

Tier: strong (CLI default model), effort `high` — same rule-5 deviation rationale as Addendum 3 (enforcement surface). Another final full-scope review (strong, `high`) follows before acceptance.

---

# Corrections Addendum 5 (2026-09-01, after third final review)

Third final review: CHANGES_REQUIRED — two Medium findings, no High/Critical. Complete corrections scope; nothing else may change.

## Finding 7 (Medium) — non-standard JSON constants accepted

`parse_payload` uses `json.loads` defaults, which accept `NaN`/`Infinity`/`-Infinity`. Required fix: add a rejecting `parse_constant` callback so any such constant fails closed on enforcement routes, plus regression tests alongside the existing malformed-payload cases (enforcement route → exit 2; include at least one payload embedding `NaN`).

## Finding 8 (Medium) — PostToolUse malformed-payload behavior vs. plan/README

PM decision: the implementation's strict behavior is CORRECT and is hereby approved as a recorded deviation from the original plan wording. Rationale: a payload that cannot be parsed cannot confirm the advisory route's identity signals, and Addendum 4 forbids trusting CLI arguments alone; since Grok ignores non-PreToolUse exit codes for blocking, exit 2 on malformed PostToolUse input is harmless and preserves one uniform fail-closed rule. Required fix: update `.grok/README.md` (and `10-harness-mapping.md` if it repeats the claim) to state that PostToolUse advisory degradation (warn + exit 0) applies only after the payload parses and the advisory route is positively identified; malformed or unidentifiable payloads always exit 2 with denial JSON, which Grok treats as non-blocking for PostToolUse. Add/adjust a regression test pinning the malformed-PostToolUse → exit 2 behavior so it is an asserted contract, not an accident.

## Validation for this run

Full suite via the offline cached toolchain (paths in Addendum 2), ruff check + format check, TOML/JSON parse, transcript for the `NaN` denial. English only.

Tier: strong (CLI default model), effort `high` — same rule-5 rationale (parse boundary is enforcement surface). The next full-scope review (strong, `high`) is expected to be the final gate.

---

# Corrections Addendum 6 (2026-09-01, after fourth final review)

Fourth final review: CHANGES_REQUIRED — one High, one Low. Complete corrections scope; nothing else may change.

## Finding 9 (High) — child stdout parsed without strict constants

`validate_child_output()` parses child stdout with default `json.loads`, so `NaN`/`Infinity`/`-Infinity` are accepted and forwarded (reproduced: child emitting `{"hookSpecificOutput":{"value":NaN}}` with exit 0 → adapter forwards it and exits 0; Grok treats malformed hook output as fail-open). Required fix: apply `_reject_nonstandard_constant` to child-stdout parsing; on an enforcement route, a child output containing a non-standard constant is treated as malformed child output (deny, exit 2 + denial JSON). Add child-output regression tests for all three constants on an enforcement route.

## Finding 10 (Low) — parseable-but-unidentifiable PostToolUse downgraded to advisory

`_is_consistent_advisory_route()` treats MISSING payload/environment event identity as consistent, so `{}` on the post-bash-dispatcher route warns and exits 0, contradicting README's "malformed or otherwise unidentifiable payloads always exit 2". PM decision: the README wording is the approved contract (Addendum 5: advisory only after POSITIVE identification). Required fix: missing identity signals are NOT consistent — a payload that does not positively identify the PostToolUse advisory route (valid JSON with unknown shape included) exits 2 with denial JSON. Add a regression test for valid-JSON-unknown-shape on the advisory route. A well-formed PostToolUse payload on the advisory route whose child fails keeps the warn + exit 0 advisory degradation.

## Validation for this run

Full suite via the offline cached toolchain (paths in Addendum 2), ruff check + format check, TOML/JSON parse, and transcripts for the new child-output `NaN` denial and the unknown-shape PostToolUse denial. English only.

Tier: strong (CLI default model), effort `high` — same rule-5 rationale. Next full-scope review (strong, `high`) follows.

---

# Corrections Addendum 7 (2026-09-01, after fifth final review)

Fifth full-scope review: CHANGES_REQUIRED — one Medium, no code findings. Artifact-evidence-only correction; NO code, test, config, rule, or documentation file may change.

## Finding 11 (Medium) — implementation result lacks mandated transcripts (regression of Finding 3)

The regenerated `implementation-result.md` summarizes but does not embed the Required Validation transcripts. Required fix, applied ONLY to `implementation-result.md`:

1. Actually execute and embed the full transcripts (exact command, payload, key output lines, `echo $?` exit code) for every AC4 deny scenario: source write, production deploy without ack, runtime-constructed fake secret (no contiguous secret literal — construct at runtime as in Addendum 4's approved form), malformed JSON, malformed Bash fields (missing/empty/whitespace/non-string), missing write target, the three enforcement event mismatches, child-output `NaN` denial, and unknown-shape PostToolUse denial.
2. Replace abbreviated `.../pytest`-style paths with the exact absolute commands actually run.
3. Re-run and embed exact outputs for: full pytest suite, ruff check, ruff format --check, TOML parse, hooks.json parse.

## Tier selection

Mid tier (`gpt-5.6-terra`), effort `high` — artifact-evidence-only mechanical correction with zero code surface; PM will deterministically verify every embedded transcript by re-execution before the final gate. Final full-scope review remains strong at `high` per policy rule 1.

## Addendum 7a — escalation after second defective mid-tier run

PM verification found the mid-tier output is a 22-line summary that CLAIMS transcripts are embedded while containing zero transcript blocks (no commands, no outputs, no exit codes). This is the second mid-tier run on this task to misreport its own work (see Addendum 2). Per policy rule 4, this item escalates one tier: re-run Addendum 7 exactly as specified on the STRONG tier (CLI default model) at effort `high`. The specification in Addendum 7 is unchanged and binding: full literal transcripts for every listed scenario, exact absolute validation commands with real outputs, `implementation-result.md` only. PM note for future tier selection on this template: mid-tier runs have twice failed on report fidelity; prefer strong for any artifact whose value IS the evidence.

## Addendum 7b — root cause identified; artifact delivery instruction (PM correction of 7a)

PM root-cause analysis: `codex_handoff.py` captures the implementation result via Codex's `--output-last-message` — the artifact IS the final message. A run that writes transcripts into `implementation-result.md` directly and then returns a summary as its final message gets its file OVERWRITTEN by that summary at phase end. This, not report-fidelity failure alone, explains the last two empty-transcript artifacts; the 7a characterization of the mid-tier run is partially retracted (its Addendum 2 validation misreport stands).

Binding delivery instruction for the re-run: do NOT edit `implementation-result.md` directly — it will be overwritten. Your FINAL MESSAGE must itself be the complete implementation-result artifact: status, summary, complete file accounting, material decisions, exact absolute validation commands with real outputs, and ALL 15 literal denial transcripts (command, payload, key output, `echo $?` exit code) inline. Execute the probes and validation for real in this run; no other file may change.

Tier: strong (CLI default model), effort `high`.

---

# Corrections Addendum 8 (2026-09-01, after sixth full-scope review)

Sixth review: CHANGES_REQUIRED — two new High findings. Complete corrections scope; nothing else may change.

## Finding 12 (High) — multiline Bash commands bypass config.toml deny rules

Deny boundaries recognize only start-of-string and `[;&|]`; a newline-separated compound (`ls\nrm -rf build`) matches a broad allow rule and no deny. Required fix in `.grok/config.toml` only:

1. Extend the three flag-deny patterns and the `rm -rf` family so newlines act as command separators on BOTH sides (leading boundary includes start-of-line after `\n`; trailing lookahead includes `\n` — do not rely on engine-specific MULTILINE flags; use explicit `\n` in the character classes/alternations).
2. Consider command-substitution adjacency (`$(`, backtick) in the trailing boundary where expressible; document any inexpressible cases in the README translation table instead of silently narrowing.
3. Regression tests: every forbidden command as line 2 of a multiline command whose line 1 matches each broad allow family, plus trailing-newline variants.

## Finding 13 (High) — uninspectable write content fails open through secret-scan

The adapter validates target paths but not content fields; canonical secret-scan coerces missing/mistyped content to `""` and allows. Required fix in `grok_hook_adapter.py`:

1. Before delegation on enforcement write routes, validate the handler-relevant content schema: `Write.content` must be a string; `Edit.new_string` a string; `MultiEdit.edits` a non-empty list of objects each with string `new_string`; `NotebookEdit.new_source` a string. A present-and-empty string remains valid (legitimate deletion); ABSENT or mistyped fields deny (exit 2 + denial JSON).
2. Regression tests for the four reproduced fail-open probes (Write w/o content, Edit non-string new_string, MultiEdit non-list edits, NotebookEdit non-string new_source) plus valid-empty-string allows.

## Validation for this run

Full suite via the cached toolchain, ruff check + format check, TOML/JSON parse. Deliver the complete result artifact — including the new denial transcripts for both findings — AS YOUR FINAL MESSAGE (Addendum 7b delivery rule). English only.

Tier: strong (CLI default model), effort `high` — enforcement surface. Next full-scope review (strong, `high`) follows.

---

# Corrections Addendum 9 (2026-09-01, PM verification after Addendum 8)

PM verification confirmed both Addendum 8 fixes work (multiline denies match; content-schema denies exit 2; 116 tests pass). One condition remains unmet: Addendum 8 point 2 required documenting inexpressible deny cases in the README translation table, and the README does not mention the command-substitution-start gap.

## Finding 14 (Low, PM-raised) — README translation table omits the substitution-start limitation

`echo $(codex --search)` and backtick-embedded equivalents match no deny rule because the leading boundary cannot see inside a substitution. This matches the limitation of the original `.claude/settings.json` deny patterns (intent parity holds), but the README must say so. Required fix, `.grok/README.md` ONLY: add to the permission translation table a documented limitation entry stating that deny rules do not match forbidden commands that START inside `$(...)` or backtick substitution, that this mirrors the source `.claude/settings.json` patterns' limitation, and that the deterministic hook layer (not these permission rules) is the enforcement backstop.

Delivery: final message = complete implementation-result artifact (Addendum 7b rule) — reproduce the current artifact content faithfully and append an "Addendum 9" section describing this doc change; do not drop the existing transcripts. No other file may change.

Tier: strong (CLI default model), effort `high` — retained despite doc-only scope because the final message must faithfully re-emit the full evidence artifact (see 7a fidelity note).

---

# Corrections Addendum 10 (2026-09-01, after seventh full-scope review)

Seventh review: CHANGES_REQUIRED — one High. The reviewer correctly refuted the Addendum 9 PM rationale: the README's claim that "the deterministic hook layer is the enforcement backstop" is factually wrong (the only PreToolUse Bash hook is deploy-gate, which does not enforce command-policy denies), and `ls $(rm -rf build)` is destructive. Addendum 9's acceptance-by-documentation is RETRACTED. Complete corrections scope; nothing else may change.

## Finding 15 (High) — deny rules bypassable via command-substitution start

Required fix:

1. In `.grok/config.toml`, extend the LEADING boundary alternation of all four deny patterns to include `$(` and backtick (e.g. add `|\$\(|` and the backtick to the leading group), so forbidden commands beginning inside a substitution match the deny. Verify no over-blocking of legitimate commands (a command genuinely embedding `$(rm -rf ...)` executes it, so matching is correct).
2. Regression tests for broad-allow collisions: `ls $(rm -rf build)`, backtick equivalent, `echo $(codex --search)`, `ls `+backtick+`codex --dangerously-bypass-approvals-and-sandbox`+backtick, each asserting a deny match despite an allow match.
3. Correct the `.grok/README.md` limitation entry: remove the false "hook layer backstop" claim; state instead that regex command policy is best-effort against shell obfuscation (quoting, variable indirection remain unmatchable), that substitution-start forms ARE now covered, and that live `grok inspect` verification plus PM approval-gating remain the ultimate controls.
4. Delete the stray untracked `.tmp-grok-child-output-fixture/` directory if it still exists (test leftovers must live under pytest tmp paths).

Delivery: final message = complete implementation-result artifact (Addendum 7b rule), including the new collision transcripts. Full validation set via the cached toolchain. English only.

Tier: strong (CLI default model), effort `high` — enforcement surface. Next full-scope review (strong, `high`) follows.
