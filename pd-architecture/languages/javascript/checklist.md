# JavaScript Architecture Review Checklist

## System Architecture

- [ ] Architecture pattern selected and justified (monolith, modular, microservices, event-driven)
- [ ] Clear module boundaries with defined public APIs
- [ ] Dependency direction follows dependency inversion (inward toward domain)
- [ ] No circular dependencies between modules
- [ ] Composition root at application entry point, not scattered

## Database and ORM

- [ ] ORM/query builder selected with justification (Prisma/Drizzle/Kysely)
- [ ] Database schema designed with proper indexes, constraints, foreign keys
- [ ] Migrations are version-controlled and reversible
- [ ] N+1 query problem addressed (eager loading, DataLoader, or JOINs)
- [ ] Connection pooling configured and sized for expected load

## API Design

- [ ] RESTful resource naming conventions followed
- [ ] Request validation at boundary (Zod schemas)
- [ ] Consistent error response format (RFC 7807 or equivalent)
- [ ] Pagination implemented for list endpoints (cursor or offset+limit)
- [ ] Rate limiting configured
- [ ] API versioning strategy defined

## Security (OWASP for Node.js)

- [ ] Input validation on all external inputs (body, query, headers, params)
- [ ] Output encoding to prevent XSS
- [ ] Authentication and authorization on protected routes
- [ ] JWT tokens with reasonable expiration (<15 min access, <7 day refresh)
- [ ] CORS configured with explicit origins (not `*`)
- [ ] Helmet or equivalent security headers enabled
- [ ] Dependency audit running (`npm audit` / `npm audit fix`)
- [ ] No hardcoded secrets (use environment variables or secret manager)
- [ ] SQL injection prevention (parameterized queries, ORM usage)
- [ ] Prototype pollution guards (Zod validation, no `Object.merge`)

## Scalability and Performance

- [ ] Stateless application design (session data externalized)
- [ ] Horizontal scaling strategy documented
- [ ] Caching strategy defined (Redis, CDN, in-memory with TTL)
- [ ] Database query performance profiled (EXPLAIN ANALYZE)
- [ ] Hot paths identified and benchmarked
- [ ] Memory leak checks (no unbounded caches, event listener accumulation)

## Observability

- [ ] Structured JSON logging (Pino or equivalent)
- [ ] Request ID propagated through all services
- [ ] Error tracking integrated (Sentry or equivalent)
- [ ] Health check endpoint (`/health` or `/ready`)
- [ ] Metrics exposed (Prometheus format or vendor-specific)
- [ ] Distributed tracing configured (OpenTelemetry)

## Code Organization (TypeScript Best Practices)

- [ ] `strict: true` in tsconfig.json
- [ ] No `any` types (use `unknown` + type guards or Zod)
- [ ] No wildcard imports (`import * from`)
- [ ] No `// @ts-ignore` without documented justification
- [ ] Barrel exports limited (no re-exporting entire modules for convenience)
- [ ] Test files co-located or in parallel `__tests__` directories
- [ ] ESLint + Prettier configured and enforced in CI
- [ ] No console.log in production code (use structured logger)

## Resilience

- [ ] Circuit breaker for external service calls
- [ ] Retry with exponential backoff for transient failures
- [ ] Graceful shutdown handling (SIGTERM → drain connections → close DB pool → exit)
- [ ] Timeout configured on all outbound HTTP/database calls
- [ ] Idempotency keys on mutation endpoints
- [ ] Dead letter queue for failed async jobs
- [ ] Feature flags for risky deployments
