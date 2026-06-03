# JavaScript/TypeScript Tech Stack Recommendations

## Web Frameworks

| Framework | Type | Performance | Ecosystem | When to use |
|-----------|------|-------------|-----------|-------------|
| **Fastify** | REST API | Excellent (fastest) | Growing | Default choice for new APIs |
| **Express** | REST API | Good | Largest | Legacy compatibility, simple apps |
| **NestJS** | Full framework | Good | Large | Enterprise, Angular teams, needs DI/AOP |
| **Hono** | REST API | Excellent | Growing | Edge runtime (Cloudflare Workers, Deno) |

**Default**: Fastify for new projects. Express only if team familiarity or existing middleware dependency.

## Databases

### PostgreSQL

Default relational database. Use with:
- **node-postgres (pg)**: Lowest-level, full control
- **Prisma**: Type-safe ORM with schema-first workflow (recommended default)
- **Drizzle**: SQL-transparent, zero-magic query builder

### MongoDB

Use when: document model fits naturally (content management, catalogs), schema flexibility needed, rapid prototyping.

### Redis

Caching, sessions, rate limiting, pub/sub, task queues (BullMQ).

## ORMs / Query Builders

| Library | Pattern | Type safety | Migration | Learning curve |
|---------|---------|-------------|-----------|----------------|
| **Prisma** | Schema-first | Auto-generated | Excellent | Low |
| **Drizzle** | Code-first | Auto-inferred | Good | Low |
| **Kysely** | Query builder | Manual types | None | Low |
| TypeORM | Active Record/Data Mapper | Decorator-based | Flaky | Medium |

**Default**: Prisma. Switch to Drizzle if you need transparent SQL or are working with an existing database.

## Validation

| Library | Size | TypeScript | Async | Ecosystem |
|---------|------|------------|-------|-----------|
| **Zod** | ~13KB | `z.infer<T>` | Yes | Largest |
| Valibot | ~3KB | Yes | Yes | Emerging (tree-shakeable) |
| ArkType | ~4KB | Yes | Yes | Emerging |

**Default**: Zod. Valibot if bundle size is critical.

## Task Queues

| Library | Backend | When to use |
|---------|---------|-------------|
| **BullMQ** | Redis | Default — reliable, priority queues, delayed jobs |
| Agenda | MongoDB | Already using MongoDB, simpler needs |

## Testing

| Tool | Purpose | Notes |
|------|---------|-------|
| **Vitest** | Unit/integration | Fast, ESM-native, Jest-compatible API |
| **Supertest** | API integration | HTTP assertions against Express/Fastify apps |
| **Playwright** | E2E | Browser automation |
| **msw** | Mocking | Intercept HTTP requests in tests |

## Observability

| Library | Purpose | Notes |
|---------|---------|-------|
| **Pino** | Logging | Fastest JSON logger, child loggers |
| Winston | Logging | More transports, slightly slower |
| **OpenTelemetry** | Tracing/metrics | Industry standard, vendor-neutral |

**Default**: Pino + OpenTelemetry.

## Authentication

| Library | Purpose | Notes |
|---------|---------|-------|
| **Passport.js** | Auth strategies | Mature, 500+ strategies |
| **Lucia** | Session auth | Modern, type-safe, no vendor lock-in |
| **Clerk / Auth0** | Managed auth | Fastest setup, vendor-dependent |

**Default**: Lucia for self-hosted session auth. Passport.js if OAuth2 social login is the primary need.

## Recommended Modern Stack

```
Fastify + TypeScript + Zod + Prisma + PostgreSQL + BullMQ + Pino + Vitest + Lucia
```
