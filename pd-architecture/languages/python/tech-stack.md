# Python Tech Stack Recommendations

## Web Frameworks

| Framework | Best For | When to Avoid |
|-----------|----------|---------------|
| **FastAPI** | Microservices, REST APIs, async-first | Need admin UI, batteries-included |
| **Django** | Full-featured apps, admin-heavy, rapid dev | Microservices, async-critical |
| **Flask** | Small apps, prototypes, simple APIs | Large apps, need built-in features |

## Database

**PostgreSQL** — default for most applications. Libraries: `asyncpg` (async), `psycopg3` (sync/async).

**MongoDB** — flexible schema, document-oriented. Library: `motor` (async).

**Redis** — caching, sessions, real-time. Library: `redis-py`.

## ORM

**SQLAlchemy 2.0** — most mature, database agnostic, good async support.
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

**Tortoise ORM** — async-first, Django-like syntax, simpler but less powerful.

## Task Queues

**Celery** — complex workflows, scheduled tasks. Broker: Redis or RabbitMQ.

**Dramatiq** — simpler than Celery, good performance, type-safe.

## HTTP Client

**httpx** — modern async/sync HTTP client.
```python
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com")
```

## Auth

- **JWT**: `python-jose[cryptography]` or `PyJWT`
- **OAuth2**: `authlib`
- **Password hashing**: `passlib[bcrypt]` or `argon2-cffi`

## Observability

- **Logging**: `structlog` (structured), `python-json-logger`
- **Metrics**: `prometheus-client`, `statsd`
- **Tracing**: `opentelemetry-api` + `opentelemetry-sdk`
- **Error tracking**: `sentry-sdk`

## Development Tools

- **Linting**: `ruff` (fast, recommended)
- **Type checking**: `mypy`
- **Testing**: `pytest` + `pytest-asyncio` + `pytest-cov`
- **Dependencies**: `poetry` (recommended) or `pdm`

## ASGI Server

**Uvicorn** — recommended for FastAPI. Production: `gunicorn -k uvicorn.workers.UvicornWorker`.

## Recommended Stack (Modern Microservices)

- Framework: FastAPI
- Database: PostgreSQL (asyncpg)
- ORM: SQLAlchemy 2.0 (async)
- Cache: Redis
- Task Queue: Celery or Dramatiq
- Validation: Pydantic
- Testing: pytest + httpx
- Observability: OpenTelemetry + Sentry
- Deployment: Uvicorn + Docker + Kubernetes
