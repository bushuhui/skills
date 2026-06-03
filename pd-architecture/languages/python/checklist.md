# Python Architecture Review Checklist

## System Architecture
- [ ] Architecture style matches scale and complexity
- [ ] Service boundaries are well-defined
- [ ] No unnecessary over-engineering
- [ ] Single points of failure identified
- [ ] Framework choice is justified (FastAPI/Django/Flask)
- [ ] Async patterns properly utilized

## Database Architecture
- [ ] Database type selection is appropriate
- [ ] Schema is properly normalized/denormalized
- [ ] Indexes are strategically placed
- [ ] Read replicas planned for scale
- [ ] Caching layer is implemented
- [ ] N+1 query issues are prevented
- [ ] ORM choice is appropriate (SQLAlchemy 2.0 recommended)
- [ ] Migration strategy is defined (Alembic)

## API Design
- [ ] API design pattern is consistent (REST/GraphQL/gRPC)
- [ ] Endpoints follow naming conventions (plural nouns)
- [ ] Versioning strategy is defined
- [ ] Authentication/authorization is implemented
- [ ] Rate limiting exists
- [ ] Error handling is consistent (RFC 7807)
- [ ] Pagination is implemented
- [ ] Input validation uses Pydantic

## Security
- [ ] Authentication mechanism is secure (JWT/OAuth2)
- [ ] Authorization model is well-defined (RBAC/ABAC)
- [ ] CORS is properly configured
- [ ] Data encrypted in transit (HTTPS/TLS)
- [ ] Secrets management (env vars, not hardcoded)
- [ ] SQL injection prevented (parameterized queries)
- [ ] Password hashing uses bcrypt/argon2
- [ ] Dependency scanning automated (bandit, safety)

## Scalability & Performance
- [ ] Scaling strategy defined (horizontal/vertical)
- [ ] Load balancer configured
- [ ] Background jobs use queue (Celery/RQ/Dramatiq)
- [ ] ASGI server is production-ready (Uvicorn/Gunicorn)
- [ ] Performance monitoring in place

## Observability
- [ ] Structured logging (structlog)
- [ ] Metrics collected (prometheus-client)
- [ ] Error tracking (sentry-sdk)
- [ ] Health check endpoints exist

## Deployment & Infrastructure
- [ ] Dockerfile optimized (multi-stage)
- [ ] CI/CD pipeline automated
- [ ] Environment parity (dev/staging/prod)
- [ ] Configuration externalized (Pydantic Settings)
- [ ] Secrets managed securely

## Code Organization
- [ ] Project structure is clear and logical
- [ ] Module boundaries well-defined
- [ ] No circular dependencies
- [ ] Type hints used throughout
- [ ] Tests well-organized (pytest)
- [ ] Linting/formatting automated (ruff)

## Resilience
- [ ] Retry logic for external calls (tenacity)
- [ ] Circuit breakers protect external services
- [ ] Timeouts configured
- [ ] Error handling consistent
