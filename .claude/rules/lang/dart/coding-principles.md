# Rule: Dart Coding Principles

Applies to Flutter and Dart code.

## Version

- Dart 3.x default (sound null safety, records, patterns, sealed classes)
- Flutter: stable channel; pinned per project

## Lint and format

- **dart format** for formatting (canonical, no alternatives)
- **dart analyze** with strict settings via `analysis_options.yaml`
- Use `flutter_lints` (Flutter) or `lints` (pure Dart) as the baseline; project-specific rules added on top
- Lint errors fail CI

## Style

- Follow [Effective Dart](https://dart.dev/effective-dart)
- `final` everywhere reasonable; `const` for compile-time constants
- `var` only when type is obvious from RHS
- Avoid `dynamic` unless interfacing with untyped data; narrow with type checks
- `late` only when initialization is genuinely deferred and the value will be set before first use

## Records and patterns

- Records (`(int, String)`, `({int x, String name})`) for ad-hoc grouping
- Pattern matching with `switch` expression for state shapes
- Destructuring in assignments and parameters

## Sealed classes

- `sealed class` for closed hierarchies — exhaustive `switch` enforced by compiler
- Use for state shapes, result types, event types

## Null safety

- No `!` (force) unless the invariant is documented
- Use `?.`, `??`, `??=` idiomatically
- `late` final for one-time-init nullable-but-required fields

## Errors

- `throw` exceptions for failure cases; `Object` is the supertype but use specific types
- `Result<T, E>` pattern (community packages or hand-rolled) for chained fallible ops
- `Future` errors propagate; use `try/catch` at boundaries
- Avoid catching `Object` / `dynamic` indiscriminately

## Async

- `async` / `await` for `Future`
- `Stream` for series of values; `await for` to consume
- Cancellation via `StreamSubscription.cancel()` or `CancellationToken`-style patterns
- Avoid mixing `Future` and `Stream` casually; pick the right model

## Naming

- Variables / functions / parameters: `lowerCamelCase`
- Types / classes / enums / extensions: `PascalCase`
- Constants: `lowerCamelCase` per Effective Dart (NOT `SCREAMING_SNAKE_CASE`)
- Private: leading underscore (`_foo`)
- Files: `snake_case.dart`

## Imports

- `package:` imports preferred over relative paths
- Sort: dart, package, project (dart fix can apply); enforce via lint
