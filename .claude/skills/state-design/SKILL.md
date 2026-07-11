---
name: state-design
description: PM intake for client state architecture decisions (server/URL/local/global).
allowed-tools: "Bash(python3 *) Read Write Edit Glob Grep"
---

# State Design

State design is T2 by default: the decision ripples across features.

## Intake

- Record the feature surfaces, current state libraries (Zone B), and the pain motivating the change.
- Enumerate the state in question and its category candidates: server cache / URL / local component / global.

## Acceptance Checklist

- AC includes the least-powerful-tool decision rule: URL > server cache > local > global, with justification for any global store.
- AC includes one source of truth per piece of state (no duplication between server cache and global store).
- AC includes persistence decisions with security rationale (no tokens in plain storage).
- AC includes an optimistic-update reconciliation strategy when used.

## Delegation

Create the task brief and run `plan` before adopting or migrating a state library. Claude approves the direction; Codex implements and documents the pattern for future features.
