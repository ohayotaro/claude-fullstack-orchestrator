# Rule: Language Protocol

Two-provider language policy. Mirror of the Language section in CLAUDE.md.

## Layers

| Target | Language |
|---|---|
| User interaction (Claude <-> user) | Japanese |
| Task artifacts (briefs, plans, approvals, reviews) | English |
| Code / commit messages / docs / variable names | English |
| Project docs | English unless the user requests Japanese |

## Enforcement

- AGENTS.md, `.claude/rules/**`, `.claude/skills/**`, and `.claude/docs/**`: English (machine-consumed)
- All commits: Conventional Commits in English
- User-facing replies (PM output): Japanese

## Naming conventions

- TS / Swift / Dart variables and functions: `camelCase`
- Python variables and functions: `snake_case`
- Classes / types in all langs: `PascalCase`
- Files: language-idiomatic — `kebab-case.ts` (TS; components often `PascalCase.tsx`), `PascalCase.swift`, `snake_case.py`, `snake_case.dart`
- Constants: `SCREAMING_SNAKE_CASE` (TS / Python) / Swift `static let UPPER` / Kotlin `const val UPPER`

## Commit format (Conventional Commits)

```
<type>(<scope>): <subject>
```

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.

## Why English for engineering artifacts

- LLM token efficiency
- Consistent training distribution for code/tools
- Avoids translation drift between brief, plan, and diff
