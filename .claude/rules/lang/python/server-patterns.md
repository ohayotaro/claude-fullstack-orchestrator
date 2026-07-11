# Rule: Python Server Patterns

Applies to FastAPI / Litestar / Django / Flask. Read Zone B `backend_framework`.

## Framework choice (Zone B-driven)

- **FastAPI**: async-first, dependency injection, Pydantic v2, OpenAPI auto-gen
- **Litestar**: async-first, more conventions, also Pydantic / msgspec
- **Django**: sync ORM mature, async views possible, batteries included; pair with django-ninja or DRF for HTTP
- **Flask**: sync, minimal; Flask 2.3+ has async support but use deliberately

## ASGI / WSGI

- ASGI: uvicorn (default), hypercorn, gunicorn with uvicorn workers (production)
- WSGI: gunicorn for Django / Flask sync stacks
- Workers count tied to the deployment target; document in Zone B

## Dependency injection

- **FastAPI**: `Depends()` + `Annotated[X, Depends(...)]`
- **Litestar**: `Provide(...)` and dependency functions
- **Django**: less DI-friendly; service classes constructed at boundary
- DI for: DB session, current user, request context, feature flags

## Validation at edge

- Pydantic v2 BaseModel for request bodies, query params, response models
- `Field(...)` with constraints (`min_length`, `gt`, `pattern`, etc.)
- `model_config` with `frozen=True`, `extra="forbid"` on inputs to prevent drift

## Handler / view structure

- Handler is thin: parse → call service → return DTO
- Service layer is sync or async per project; mixing tracked carefully
- Repository isolates ORM queries from services
- DTOs convert between domain models and API contracts at the boundary

## Database access

- **SQLAlchemy 2.0+** async or sync, per Zone B
- **Django ORM** for Django projects; consider `select_related` / `prefetch_related` for N+1
- **Tortoise ORM** for FastAPI/Litestar when SQLAlchemy is overkill
- Migrations: Alembic (SQLAlchemy) or Django migrations
- Transactions: explicit context managers (`async with session.begin():`); one transaction per logical unit

## Error handling

- Custom exception hierarchy mapped to HTTP status by an exception handler
- FastAPI: `app.exception_handler(MyError)` returning standard envelope
- Litestar: `exception_handlers={...}` on Litestar app
- Django: middleware or DRF exception handler

## Logging and tracing

- Structured logging in middleware: request id, method, path, status, latency, user
- OpenTelemetry instrumentation for FastAPI / Django / Flask via `opentelemetry-instrumentation-*`
- No PII / secrets in logs

## Background work

- HTTP handlers do not perform long async work — enqueue to Celery / RQ / Dramatiq / Arq per Zone B
- Fire-and-forget forbidden; use a real queue
- Idempotency keys honored per `common/api-contracts.md`

## Graceful shutdown

- ASGI lifespan / Django signal handler closes DB pool, releases queue connections
- Health check returns NOT-READY during drain
