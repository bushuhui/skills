# Clean Architecture

**Problem:** Need clear dependency rules where business logic doesn't depend on frameworks or external systems.

**When to use:**
- Long-lived applications that will outlive frameworks
- Business logic is the core value
- Team discipline to maintain boundaries
- Multiple delivery mechanisms (web, mobile, CLI)

**When NOT to use:**
- Short-lived projects
- Framework-centric applications
- Simple CRUD operations

**Trade-offs:**

| Pros | Cons |
|------|------|
| Framework independence | More code |
| Testable business logic | Can feel over-engineered |
| Clear dependency direction | Learning curve |
| Flexible delivery mechanisms | Initial setup cost |

**Dependency rule:** Dependencies point inward. Inner circles know nothing about outer circles.

```
┌─────────────────────────────────────────┐
│           Frameworks & Drivers          │
│  ┌─────────────────────────────────┐    │
│  │     Interface Adapters          │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │    Application Layer    │    │    │
│  │  │  ┌─────────────────┐    │    │    │
│  │  │  │    Entities     │    │    │    │
│  │  │  │ (Domain Logic)  │    │    │    │
│  │  │  └─────────────────┘    │    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```
