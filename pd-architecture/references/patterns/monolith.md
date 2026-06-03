# Monolithic Architecture

**Problem:** Build and deploy a complete application as a single unit with minimal operational complexity.

**When to use:**
- Small team (1-5 developers)
- MVP or early-stage product
- Simple domain with clear boundaries
- Deployment simplicity is priority

**When NOT to use:**
- Multiple teams need independent deployment
- Parts of system have vastly different scaling needs
- Technology diversity is required

**Trade-offs:**

| Pros | Cons |
|------|------|
| Simple deployment | Scaling is all-or-nothing |
| Easy debugging | Large codebase becomes unwieldy |
| No network latency between components | Single point of failure |
| Simple testing | Technology lock-in |

**Structure:**
```
monolith/
├── src/
│   ├── controllers/    # HTTP handlers
│   ├── services/       # Business logic
│   ├── repositories/   # Data access
│   ├── models/         # Domain entities
│   └── utils/          # Shared utilities
├── tests/
└── package.json
```
