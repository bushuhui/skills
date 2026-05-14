# FastAPI Patterns — Nano

`create_app()` factory, not module-level app. `lifespan` not `@app.on_event`. Separate create/update/response Pydantic models. Dependency injection for DB/auth. Async I/O only in async handlers. Centralized `@app.exception_handler`. Assign `app.openapi = callable`. Tests use `dependency_overrides`. No `allow_origins=["*"]` with credentials. Hash passwords, validate JWT, redact secrets. Connection pooling, pagination, eager loading for N+1.
