# Rule: React Patterns (Frontend TS)

Applies to React, Next.js, Remix, Vite, Astro (React island).

## Component model

- Functional components only; no class components
- Server Components by default in Next App Router; mark `"use client"` deliberately
- Composition over inheritance
- Children-as-content; render-props or composition before exposing many configuration props
- Avoid wrapper hell: extract a hook before adding 3+ HOCs

## Hooks rules

- Hooks called at the top level only; no conditional / loop / nested calls
- Custom hook starts with `use`
- Effects only for synchronization with external systems — not for derivable state
- `useEffect` dependency arrays accurate; avoid `eslint-disable react-hooks/exhaustive-deps` unless justified
- Cleanup functions for subscriptions, timers, observers

## State derivation

- Derive from props/state during render, not in `useEffect`
- Memoize expensive derivations with `useMemo` only after profiling shows benefit
- `useCallback` only when the callback is a dependency or passed to memoized child

## Data fetching

- Server Components for data needed at render (Next App Router)
- TanStack Query / SWR for client-side cache and mutations
- No raw `fetch` in components; wrap in a query hook or server component

## Boundaries

- **Suspense boundaries**: explicit; placed where the loading UX makes sense
- **Error boundaries**: scoped to feature surfaces, with recovery affordance
- **Form boundaries**: inputs and validation co-located; no globally-scoped form state unless multi-step

## Lists

- `key` is stable and unique per item (use id, not array index unless static)
- Virtualize lists exceeding ~50 items in the visible window

## Performance

- Profile before optimizing; React DevTools Profiler shows actual cost
- `React.memo` only when the component is expensive AND props are stable
- Avoid passing inline objects/arrays as memoized component props

## RSC / Server / Client split (Next App Router)

- Server Components: data, secrets, large dependencies
- Client Components: interactivity, browser APIs, state
- Move client-only deps behind `"use client"` boundary; do not import them in server tree
