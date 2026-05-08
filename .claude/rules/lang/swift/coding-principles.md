# Rule: Swift Coding Principles

Applies to iOS / macOS / watchOS / visionOS code in Swift.

## Version

- Swift 5.9+ default; Swift 6 mode for new projects when toolchain supports
- Targets: iOS 17+ default (Swift 5.9 + Observation framework); fall back to ObservableObject for older

## Lint and format

- **SwiftLint** with project-tuned config in `.swiftlint.yml`
- swift-format optional; SwiftLint covers most needs
- Lint errors fail CI

## Style

Follow [Swift API Design Guidelines](https://swift.org/documentation/api-design-guidelines/):
- Naming clarity at point of use over conciseness
- Method names read as English phrases
- Boolean methods read as assertions (`isEmpty`, not `empty`)
- Argument labels improve readability

## Optionals

- Force unwrap (`!`) only when an invariant guarantees non-nil; document the invariant
- `guard let` to bail out early
- `if let` / shorthand `if let value` (Swift 5.7+) for unwrapping
- Implicitly unwrapped optionals: only at `IBOutlet` and similar framework boundaries

## Types

- Prefer value types (`struct`, `enum`) over reference types (`class`) by default
- Reference types when identity, shared mutable state, or framework requirement
- `protocol` for behavior contracts; protocol-oriented design
- Avoid `AnyObject` unless necessary (existential overhead)
- Generics over type erasure where compile-time dispatch helps

## Errors

- `throws` for recoverable errors with custom `Error` types
- `Result<Success, Failure>` when async chain or storage required
- `try?` only when nil is meaningful; otherwise propagate
- No silent catch

## Concurrency

- `async`/`await` over completion handlers
- `@MainActor` annotation explicit on UI-touching code
- `@Sendable` closures across actor boundaries
- `Task { }` lifetime managed (prefer `task` view modifier in SwiftUI for cancellation tied to view lifetime)
- Avoid `DispatchQueue` in new code unless integrating with legacy

## Module boundaries

- `internal` is default; `public` only when truly part of a module's API
- `final class` by default for inheritance discipline (unless designed for subclassing)

## Naming

- Variables / methods: `camelCase`
- Types / protocols: `PascalCase`
- Acronyms: keep all-caps if 2 letters (`URL`), otherwise camel-case (`Url` only when at end of word)
- Files: `PascalCase.swift` matching the primary type
