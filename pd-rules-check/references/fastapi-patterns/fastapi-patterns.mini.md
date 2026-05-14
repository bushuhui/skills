# OBEY FastAPI Patterns

## When to use

Use when building, reviewing, or testing FastAPI applications. Covers application factory, schema separation, dependency injection, async handlers, error handling, OpenAPI, testing, and production readiness.

## Primary bias to correct

FastAPI apps that "work" are not necessarily production-ready -- thin HTTP layers, explicit dependencies, and testability matter.

## Decision rules

- Application factory pattern. `create_app()` builds the app so tests can control settings. Use `lifespan` for startup/shutdown, not `@app.on_event`.
- Schema separation: distinct Pydantic models for create, update, and response. Never return raw ORM objects or password/token fields.
- Dependency injection for request-scoped resources (DB sessions, current user, pagination). No inline session/client creation in handlers.
- Async handlers use async I/O only. `httpx.AsyncClient` for external HTTP, async DB drivers. Never `requests` in an async route.
- Centralized error handling via custom exception classes + `@app.exception_handler`. Stable response shapes across errors.
- OpenAPI customization: assign callable to `app.openapi`, do not just call the function once.
- Testing: override `Depends` targets, not internal helpers. Clear `dependency_overrides` after each test.
- CORS: never `allow_origins=["*"]` with `allow_credentials=True`. Origins must be environment-specific.
- Security: hash passwords with argon2/bcrypt. Validate JWT issuer, audience, expiry, algorithm. Redact tokens/secrets from logs.
- Performance: explicit connection pooling. Pagination on list endpoints. Eager loading to prevent N+1. Async clients in async paths.

## Trigger rules

- When `app = FastAPI(...)` is at module level without a factory, wrap in `create_app()`.
- When `@app.on_event("startup")` is used, replace with `lifespan` context manager.
- When an endpoint returns an ORM model directly, add a response Pydantic model.
- When `requests` is imported in an async handler, use `httpx.AsyncClient`.
- When `Depends` is not used for DB/auth, refactor to dependency injection.
- When error handling is scattered across handlers, centralize with `@app.exception_handler`.
- When tests patch internal helpers instead of overriding dependencies, use `app.dependency_overrides`.
- When `allow_origins=["*"]` appears with credentials, restrict to specific origins.
- When no pagination on list endpoints, add `limit`/`offset` or cursor params.

## Final checklist

- Application factory with `create_app()`?
- `lifespan` instead of `@app.on_event`?
- Create/Update/Response schemas separated?
- Dependency injection for DB, auth, pagination?
- All async endpoints using async I/O only?
- Centralized exception handling?
- `app.openapi = custom_openapi` assigned?
- Tests use `dependency_overrides`?
- CORS origins environment-specific?
- Passwords hashed, JWT validated, secrets redacted?
- Connection pooling configured?
- N+1 queries prevented with eager loading?
