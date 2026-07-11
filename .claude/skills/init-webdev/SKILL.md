---
name: init-webdev
description: PM wizard that captures the frontend/mobile stack into CLAUDE.md Zone B and active rules.
allowed-tools: "Read Write Edit Glob Grep"
---

# Init Webdev

T0-T1 PM activity: this skill only edits `CLAUDE.md` Zone B (between `@orchestra:template-boundary` and `@orchestra:repo-boundary`).

## Wizard

Ask the user (Japanese) and record (English):

1. Product mode: web-only / mobile-only / web+native / web+rn / web+flutter / fullstack / backend-only / desktop
2. Monorepo: yes/no; directory map
3. Web framework and styling
4. Mobile platform(s)
5. Client/server state libraries
6. Testing tools (unit, component, e2e)
7. Key commands (dev/test/lint)

## Output

- Fill Project Identity, Frontend Stack, Testing, Key Commands, and Directory Map in Zone B.
- Set `active_rules.lang` to the languages actually in use.
- If backend is in scope, run `/backend-init` next.
- Repository scaffolding itself (creating apps/, packages/, configs) is engineering work: create a brief and delegate via `/codex-task`.
