# Rule: Testing (Python Backend)

## Tools (read Zone B `testing.backend_unit` / `testing.e2e`)

- **Runner**: pytest (canonical)
- **Async**: `pytest-asyncio` (or `anyio` plugin per project)
- **HTTP client (FastAPI / Litestar)**: `httpx.AsyncClient` against the ASGI app
- **HTTP client (Django)**: `Client` / `AsyncClient` from Django, or DRF's `APIClient`
- **DB testing**: `pytest-postgresql` / `pytest-mysql` / testcontainers / Django's `TestCase` with transactions
- **Factories**: `factory_boy` or `polyfactory`
- **Mocking**: `pytest-mock` (`mocker` fixture) over raw `unittest.mock`
- **Coverage**: `pytest-cov`

## Unit principles

- One unit = one function / method / small class
- Async tests use `pytest-asyncio` with `asyncio_mode = "auto"` configured
- Mock at boundaries (DB, HTTP, message broker); don't mock the unit
- Fast: <50ms per unit test

## Integration principles

- Real DB via testcontainers or per-test schema
- Transaction-per-test, rolled back at teardown — fastest
- Or per-test DB drop/create when transactions don't suffice (e.g., DDL changes)
- Async DB sessions managed via fixtures with proper teardown

## API tests

- **FastAPI**: `httpx.AsyncClient(app=app, base_url="http://test")` with overridden dependencies
- **Litestar**: `TestClient(app)` (sync) or `AsyncTestClient(app)`
- **Django**: `client.get(...)` / `async_client.get(...)`; use `pytest-django`

## Fixtures

- Project-wide in `conftest.py`; feature-local in nearby `conftest.py`
- Factory fixtures: parametrize via `pytest.fixture(params=...)` or factory_boy traits
- Avoid module-scoped DB state; prefer function-scoped fixtures with rollback

## Coverage

- Unit ≥70%; critical service paths ≥90%
- `pytest --cov=src --cov-report=term-missing --cov-fail-under=70` in CI

## Test data

- Factory functions over hard-coded fixtures for variants
- Deterministic IDs (UUIDs from a seeded source) for snapshot stability

## Async patterns

- `pytest-asyncio` with `loop_scope="session"` when sharing async resources
- No `time.sleep` — use `await asyncio.sleep` only when waiting on a real timer; prefer `asyncio.wait_for` or event signals
