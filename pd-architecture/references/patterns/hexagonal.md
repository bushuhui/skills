# Hexagonal Architecture (Ports & Adapters)

**Problem:** Need to isolate business logic from external concerns (databases, APIs, UI) for testability and flexibility.

**When to use:**
- Business logic is complex and valuable
- Multiple interfaces to same domain (API, CLI, events)
- Testability is priority
- External systems may change

**When NOT to use:**
- Simple CRUD with no business logic
- Single interface to domain
- Overhead isn't justified

**Trade-offs:**

| Pros | Cons |
|------|------|
| Business logic isolation | More abstractions |
| Highly testable | Initial setup overhead |
| External systems are swappable | Can be over-engineered |
| Clear boundaries | Learning curve |

**Structure:**
```
hexagonal/
├── domain/              # Business logic (no external deps)
│   ├── entities/
│   ├── services/
│   └── ports/           # Interfaces (what domain needs)
├── adapters/            # Implementations
│   ├── persistence/     # Database adapters
│   ├── external/        # External service adapters
│   └── api/             # HTTP adapters
└── config/              # Wiring it all together
```

**Dependency rule:** Domain → Ports (interfaces) → Adapters (implementations). The domain layer has zero external dependencies.
