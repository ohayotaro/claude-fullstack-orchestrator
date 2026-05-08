# Rule: Language Protocol

Three-layer language policy. Mirror of CLAUDE.md §10.

## Layers

| Channel | Language |
|---------|----------|
| Orchestrator ↔ User | Japanese OR English (user preference) |
| Agent ↔ Agent (Codex / Gemini / subagent prompts and replies) | English (fixed) |
| Code / commit messages / docs / variable names | English (fixed) |

## Enforcement

- All `.codex/` and `.gemini/` skill prompts: English only
- All agent definitions in `.claude/agents/*.md`: English
- All rule files in `.claude/rules/**`: English
- All commits: Conventional Commits in English
- README, DESIGN.md and similar docs: English
- User-facing replies (orchestrator output): match user's language

## Naming conventions

- TS / Swift / Dart variables and functions: `camelCase`
- Python variables and functions: `snake_case`
- Classes / types in all langs: `PascalCase`
- Files: language-idiomatic — `kebab-case.ts` (TS, except components which often `PascalCase.tsx`), `PascalCase.swift`, `snake_case.py`, `snake_case.dart`
- Constants: `SCREAMING_SNAKE_CASE` (TS / Python / Swift `static let UPPER` / Kotlin `const val UPPER`)

## Commit format (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.

## Why English for agent-to-agent

- LLM token efficiency
- Consistent training distribution for code/tools
- Avoids translation drift
