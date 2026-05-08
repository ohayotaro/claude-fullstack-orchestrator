# Rule: Python Coding Principles (Backend)

Applies to backend Python services: FastAPI, Django, Litestar, Flask.

## Version

- Python 3.11+ default (3.12 / 3.13 acceptable)
- Set in `pyproject.toml` `requires-python`

## Lint and format

- **ruff** as the canonical lint + format tool (replaces black + isort + flake8 + many plugins)
- Configuration in `pyproject.toml` under `[tool.ruff]`
- Lint errors fail CI

## Type checking

- **mypy strict** OR **pyright strict** — pick one, enforce consistently
- Type hints required on every public function and method
- `from __future__ import annotations` for forward references when beneficial
- `typing.Annotated` for FastAPI dependencies and validators
- Avoid `Any`; narrow with `TypeGuard` or runtime check

## Models and DTOs

- **Pydantic v2** for HTTP boundaries and config (FastAPI / Litestar)
- **dataclasses** (with `frozen=True` where appropriate) for internal value objects
- Django: model classes; Pydantic for request/response DTOs (django-ninja or DRF serializers if Django REST)

## Naming

- Variables / functions / modules: `snake_case`
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private: leading underscore

## Errors

- Custom exception hierarchy rooted at a project base exception
- No bare `except:`; catch specific types
- Async errors propagate; convert at handler boundary to API error envelope

## Async

- FastAPI / Litestar: prefer `async def` for I/O-bound handlers and dependencies
- Django: standard sync ORM still common; async views available in 4.1+; use carefully with ORM
- Never block the event loop with sync I/O in async handlers

## Imports and modules

- Group: stdlib, third-party, first-party, local (ruff `isort` enforces)
- Absolute imports inside the project; relative imports only within tightly-coupled packages
- No circular imports

## Env config

- Pydantic `BaseSettings` (pydantic-settings) for typed env config
- Validation runs at process start; fail fast

## Logging

- `structlog` or stdlib `logging` with JSON formatter
- `loguru` acceptable; converge on one per project
