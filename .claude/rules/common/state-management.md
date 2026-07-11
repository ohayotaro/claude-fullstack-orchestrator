# Rule: State Management (Client)

Default to the **least powerful tool** that solves the problem.

## State categories

- **Server state**: data fetched from the server (cache, sync, retry, mutation).
  - TS: TanStack Query / SWR / RTK Query
  - Swift: NSPersistentContainer + custom cache, or third-party
  - Compose: Repository + Flow
  - Flutter: Riverpod + AsyncValue, or Bloc
  - Do NOT reimplement caching manually if a lib is in use.
- **URL state**: filter, sort, page, dialog visibility for shareable views.
  - Use the router (Next router, react-router, SwiftUI NavigationPath, etc.) as the source.
- **Local component state**: ephemeral UI state.
  - `useState` (React), `@State` (SwiftUI), `remember` (Compose), `setState` (Flutter).
- **Global client state**: cross-feature, cross-screen.
  - LAST RESORT. Justify why URL / server cache / local does not suffice.
  - TS: Zustand or Jotai (small, ergonomic) over Redux unless team standard.
  - Swift: `@Observable` + parent injection, or TCA when the project uses it.
  - Compose: ViewModel with StateFlow + Hilt scope.
  - Flutter: Riverpod or Bloc per Zone B.

## Decision rules

- Prefer URL > server cache > local component > global
- Persistence (localStorage / AsyncStorage / DataStore / SwiftData / Hive): explicit decision with security rationale (no tokens in plain storage)
- One source per piece of state — no duplication between server cache and global store
- Optimistic updates: only when reconciliation strategy is documented

## Ownership

All engineering work in this domain is delegated to Codex through a task brief (`/codex-task`, see `common/codex-delegation.md`). Claude captures the requirements above as acceptance criteria in the brief; Codex designs, implements, and validates them.
