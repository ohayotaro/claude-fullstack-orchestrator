# Rule: Kotlin Coding Principles

Applies to Android (Jetpack Compose) and Kotlin Multiplatform UI code in this template.

## Version

- Kotlin 2.0+ default
- Android: AGP 8.x+, Compose BOM 2025.x+
- Target SDK current; minSdk per project (typically 24+ today)

## Lint and format

- **ktlint** (with `.editorconfig`) OR **detekt** for static analysis
- Many projects use both: ktlint for style, detekt for code smells
- Lint errors fail CI

## Style

- `val` over `var`; immutability default
- Type inference where unambiguous; explicit types at public API boundaries
- `data class` for value types (with `equals`/`hashCode`/`copy` auto)
- `sealed class` / `sealed interface` for closed hierarchies and exhaustive `when`
- Extension functions for behavior addition without inheritance

## Null safety

- Avoid `!!` (assertion) — express intent with `?:` (Elvis), `let`, `requireNotNull`
- Platform types from Java: annotate parameters and return types when interfacing
- `lateinit var` only when initialization is genuinely deferred and never null after init

## Errors

- Exceptions for unexpected failures (consistent with Kotlin/Java conventions)
- `Result<T>` for fallible operations when chaining is helpful
- No silent catch
- Coroutine cancellation: never swallow `CancellationException`

## Coroutines

- Structured concurrency: scope-bound (`viewModelScope`, `lifecycleScope`)
- `Dispatchers.Default` for CPU; `Dispatchers.IO` for I/O; `Dispatchers.Main` for UI
- `Flow` for streams; `StateFlow` for screen state; `SharedFlow` for events
- `withContext` for switching dispatchers; not `launch` inside another launch
- Avoid `GlobalScope` in production code

## Module boundaries

- `internal` over `public` by default
- Multi-module: feature modules + core modules; explicit dependency direction
- `@JvmStatic` / `@JvmField` only at Java interop boundaries

## Naming

- Variables / functions / files: `camelCase` (functions: `lowerCamelCase`)
- Classes / objects: `PascalCase`
- Constants: `UPPER_SNAKE_CASE` (companion object `const val`)
- Files: `PascalCase.kt` matching the primary type, OR `feature-name.kt` for top-level functions

## Annotations

- `@Stable` / `@Immutable` for Compose stability
- `@Composable` only on composables
- `@Throws` for Java interop with checked exceptions
