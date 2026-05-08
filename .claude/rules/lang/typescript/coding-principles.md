# Rule: TypeScript Coding Principles (Frontend)

Applies to frontend TS code: React, Next.js, Vite, Remix, Astro.

## Compiler

- `strict: true` mandatory
- `noUncheckedIndexedAccess: true` recommended
- `target: ES2022` or newer
- `moduleResolution: "bundler"` for bundled apps; `"nodenext"` for Node-only

## Lint and format

- **ESLint** (with `@typescript-eslint`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-jsx-a11y`) OR **Biome** (single tool for lint+format)
- Prettier when ESLint is chosen; Biome bundles formatting
- Lint errors fail CI

## Type usage

- Avoid `any`. Use `unknown` and narrow.
- Prefer `interface` for object shapes that may extend; `type` for unions, intersections, mapped/conditional types.
- Type assertions (`as`) are last resort; prefer type guards or schema-validated parsing.
- Discriminated unions over boolean flags for state shapes.
- `readonly` arrays and properties when immutability is the contract.

## Naming

- Variables / functions: `camelCase`
- Types / interfaces / classes / React components: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE` for module-level invariants
- Files: `kebab-case.ts` generally; React component files often `PascalCase.tsx`
- Hook files: `use-foo.ts` exporting `useFoo`

## Module structure

- Path alias (`@/`) over deep relative paths beyond 2 levels
- Index re-exports allowed at package boundaries; avoided inside features (hurts tree-shaking)
- One default export per module is fine for components; avoid mixing default + multiple named heavily

## Errors

- Throw `Error` subclasses, not strings
- Async errors handled at call site or boundary (error boundary, route-level handler)
- No silent catch — log or rethrow
