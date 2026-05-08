---
name: init-webdev
description: Frontend / mobile-side wizard. Asks the user about product mode, web framework, styling, mobile platforms, state libs, testing tools, and monorepo. Writes the answers into CLAUDE.md Zone B and updates active_rules. Run once at project start; re-run after major stack changes.
---

# /init-webdev

## Purpose

Populate the frontend / mobile section of CLAUDE.md Zone B and activate the appropriate lang rules. After this runs, agents and skills know which stack they are operating on.

This is the **frontend** wizard. For backend setup, run `/backend-init` next (when `backend_scope != none`).

## When to use

- First time setting up the project after copying the template in
- Significant frontend stack change (e.g., switching from Vite to Next, adding a mobile platform)

## Steps

### 1. Read current CLAUDE.md Zone B template

Read `CLAUDE.md` and locate the Zone B section between `@orchestra:template-boundary` and `@orchestra:repo-boundary`. Confirm the placeholder fields (`{PROJECT_NAME}`, `{PRODUCT_MODE}`, etc.) are present. If Zone B is already populated, ask the user whether to overwrite or extend.

### 2. Ask the user about the project shape

Use `AskUserQuestion` with single-select for `product_mode`:

- `web-only` (just a web app)
- `mobile-only` (no web)
- `web+native` (web + iOS/Android native)
- `web+rn` (web + React Native)
- `web+flutter` (web + Flutter)
- `fullstack` (web + native or RN/Flutter, plus backend)
- `backend-only` (no frontend; useful when this template is used for a service)
- `desktop` (Electron / Tauri)

### 3. Branch on `product_mode`

- If web is included: ask web framework (`nextjs / remix / vite / astro / none`) and styling (`tailwind / vanilla-extract / css-modules / none`).
- If `web+native`: ask which natives (`swift`, `kotlin`, both).
- If `web+rn`: confirm RN, ask Expo or bare.
- If `web+flutter`: confirm Flutter target platforms.
- If `mobile-only`: ask which mobile (`swift / kotlin / rn / flutter / multiple`).
- If `desktop`: ask which (`electron / tauri / both`).

### 4. Ask state lib

- Client: `zustand / jotai / redux / recoil / native-only / none`
- Server: `tanstack-query / swr / rtk-query / native-only / none`

### 5. Ask testing tools

- Unit: `vitest / jest / pytest (frontend N/A) / ...`
- Component: `rtl / vue-testing-library / ...`
- E2E: `playwright / detox / xcuitest / espresso / flutter-integration / cypress`
- Visual: `playwright + gemini / golden-toolkit / ...`

### 6. Ask monorepo

- `monorepo: true | false`
- If `true`: ask tool (`pnpm-workspaces / turbo / nx / yarn-workspaces / npm-workspaces / bun-workspaces`)

### 7. Compute `active_rules.lang`

Map answers to lang rule directories:

| Stack signal | `active_rules.lang` entry |
|---|---|
| Web framework chosen (any TS/JS framework) | `typescript` |
| Mobile: `swift` | `swift` |
| Mobile: `kotlin` | `kotlin` |
| Mobile: `rn` | `typescript` (already added if web is also TS) |
| Mobile: `flutter` | `dart` |
| Backend will be added in `/backend-init` | (deferred) |

Always include `common: [all]`.

### 8. Update CLAUDE.md Zone B

Use `Edit` to replace each placeholder with the chosen value. Preserve the boundary markers (`@orchestra:template-boundary`, `@orchestra:repo-boundary`).

### 9. Suggest next step

If the user did not yet decide backend scope, suggest `/backend-init`. If `backend-only` was chosen earlier, run `/backend-init` immediately.

### 10. Print summary

Output a summary table with the chosen values and a list of activated rules. Confirm Zone B is now populated.

## Output

- Updated `CLAUDE.md` Zone B
- Summary of choices to the user (in the user's language)

## Notes

- All questions go through `AskUserQuestion` so the user can pick from validated options.
- Use defaults sparingly — every choice should be intentional.
- Do not create scaffold files (apps/, packages/) here — that is the user's project responsibility.
