---
name: state-design
description: Decide where state lives (server / URL / local component / global), which lib manages it, and how to scope ownership. Owned by state-architect with Codex review for non-trivial cases. Run when introducing a feature whose state shape is non-obvious.
---

# /state-design

## Purpose

Make the state architecture decision before code is written. Avoids the trap of "we'll figure out state as we go" which usually ends with reactive global stores and tangled effects.

## When to use

- New feature with non-trivial state (multi-step form, optimistic mutations, cross-screen data, complex undo/redo, real-time collaboration)
- Migration between state libraries
- Refactor of an existing tangled state surface

Skip when:
- The feature trivially fits the project's existing state pattern → no decision needed
- Pure server data with no client mutation → use Zone B's `state_lib.server` (TanStack Query / SWR / etc.)

## Steps

### 1. Read context

- Zone B `state_lib.client`, `state_lib.server`, platform list
- Existing state patterns in the codebase (read 3-5 representative examples)
- The feature's actual state requirements (input from `/start-feature` or user)

### 2. Categorize the state

For each piece of state in the feature, classify:

- **Server**: from API; cache, refetch, retry, mutation rules
- **URL**: shareable, browser-back-friendly (filters, page, dialog visibility)
- **Local component**: ephemeral UI state (input value mid-typing, hover)
- **Global client**: cross-feature, cross-screen — last resort

### 3. Choose the tool per category

Per Zone B and `common/state-management.md`:

- Server → TanStack Query / SWR / RTK Query (TS); native equivalents for native platforms
- URL → router (Next router / react-router / NavigationPath / Compose Nav)
- Local → useState / @State / remember / setState
- Global → Zustand / Jotai (TS); @Observable + parent injection (Swift); ViewModel + StateFlow + DI scope (Compose); Riverpod / Bloc (Flutter)

### 4. Define ownership boundaries

- Which feature owns which slice
- How slices communicate (events vs shared state)
- Persistence per slice (memory / localStorage / SecureStore / Keychain / DataStore)

### 5. Codex review for non-trivial designs

Send the design to Codex when:
- State is shared across 3+ features
- Optimistic updates required
- Real-time / collaborative state
- Persistence with security implications (tokens, PII)

Codex review focuses on: testability, perf (selector recomputation, recomposition), persistence safety, race conditions.

### 6. Document the decision

Save to `design/decisions/state-<feature>.md`:
- The categorization (server / URL / local / global per piece)
- The lib choice per category with rationale
- Ownership boundaries
- Persistence strategy
- Test plan for the state behavior

### 7. Hand off to implementation

`ui-engineer` wires according to the decision. If a new global store is justified, `state-architect` defines its shape; `ui-engineer` consumes.

## Output

- Decision record at `design/decisions/state-<feature>.md`
- Proposed state shape (TS interfaces / Swift types / Kotlin sealed classes / Dart records)
- Persistence strategy
- Test plan

## Hand-off

- Implementation → `ui-engineer` (`/screen-build`)
- API impact (server state shape) → `api-engineer`
- Native persistence (Keychain / SecureStore) → `platform-integrator`

## Notes

- **Default to least powerful**: URL → server cache → local → global.
- Do not introduce a global store to "share state easily" — usually URL or server cache is the right answer.
- Optimistic updates require an explicit reconciliation strategy; document it.
