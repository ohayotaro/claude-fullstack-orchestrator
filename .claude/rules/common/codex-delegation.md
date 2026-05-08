# Rule: Codex Delegation

Codex CLI (gpt-5.4) is the deep-reasoning external agent. Use deliberately, not by default.

## When to delegate to Codex

- Architecture decisions (frontend, backend, mobile, infra)
- API / event / DB schema contract design
- Authn/authz flow design
- Performance-optimization strategy (after measurement)
- Algorithm design
- Debugging when Opus subagents cannot localize the cause
- Code review for high-blast-radius changes (contracts, auth, migrations)
- Backend incident triage (`/incident-backend`)

## When NOT to delegate to Codex

- Tasks fully solvable with codebase exploration → `general-purpose` Opus subagent
- Multimodal input (images, PDFs, video) → Gemini
- High-throughput parallel mechanical work → Opus subagents in parallel

## Invocation patterns

- **Foreground** (`codex exec ... < /dev/null`): when the orchestrator must wait for the result before proceeding (design review, statistical validation, contract decisions)
- **Background** (long-running research): only when the orchestrator has independent work to do in parallel; otherwise foreground is simpler
- **Always pipe `< /dev/null`** when invoking from a non-interactive context to avoid stdin-wait hangs
- Use `--skip-git-repo-check` when the working directory is not a git repo

## Approval policy

`.codex/config.toml` sets `approval_policy = "never"` for non-interactive flows. Codex operates in a read-only sandbox by default. Code changes proposed by Codex are applied via `codex apply` (or by the orchestrator via Edit/Write).

## Expected output format from Codex

Prefer this structure in delegation prompts:

```
TL;DR (max 3 lines)
Analysis (numbered)
Plan (numbered, actionable, with file/section pointers)
Code (only when implementation is in scope)
Validation (how to verify)
Risks
Confidence: H/M/L per major recommendation
```

## Persisted artifacts

Save Codex reviews and decisions as files under repo root or `.claude/docs/reviews/` (e.g., `DESIGN_REVIEW_codex_<date>.md`). They are commit-worthy and serve as decision records.

## Hand-off

- Skill that wraps Codex: `/codex-system`, `/codex-debugger`, `/incident-backend`
- Hooks that escalate to Codex: `check-codex-on-contract-edit.py`, `error-to-codex.py`
