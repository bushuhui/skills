# API Gateway Pattern

**Problem:** Need single entry point for clients that routes to multiple backend services.

**When to use:**
- Multiple backend services
- Cross-cutting concerns (auth, rate limiting, logging)
- Different clients need different APIs
- Service aggregation needed

**When NOT to use:**
- Single backend service
- Simplicity is priority
- Team can't maintain gateway

**Trade-offs:**

| Pros | Cons |
|------|------|
| Single entry point | Single point of failure |
| Cross-cutting concerns centralized | Additional latency |
| Backend service abstraction | Complexity |
| Client-specific APIs | Can become bottleneck |

**Responsibilities:**
- Authentication/Authorization
- Rate limiting
- Request/Response transformation
- Load balancing
- Circuit breaking
- Caching
- Logging/Monitoring

```
┌─────────────────────────────────────┐
│            API Gateway              │
├─────────────────────────────────────┤
│ • Auth  • Rate limit  • Transform  │
│ • Balance  • Circuit break  • Log  │
└─────────────────────────────────────┘
         │         │         │
         ▼         ▼         ▼
    ┌─────┐   ┌─────┐   ┌─────┐
    │Svc A│   │Svc B│   │Svc C│
    └─────┘   └─────┘   └─────┘
```
