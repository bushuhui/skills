# CQRS (Command Query Responsibility Segregation)

**Problem:** Read and write workloads have different requirements and need to be optimized separately.

**When to use:**
- Read/write ratio is heavily skewed (10:1 or more)
- Read and write models differ significantly
- Complex queries that don't map to write model
- Different scaling needs for reads vs writes

**When NOT to use:**
- Simple CRUD with balanced reads/writes
- Read and write models are nearly identical
- Team unfamiliar with pattern
- Added complexity isn't justified

**Trade-offs:**

| Pros | Cons |
|------|------|
| Optimized read models | Eventual consistency between models |
| Independent scaling | Complexity |
| Simplified queries | Synchronization logic |
| Better performance | More code to maintain |

**Structure:**

Write side (Commands) — mutates state, validates business rules.
Read side (Queries) — optimized read models, denormalized for fast retrieval.

**When to adopt:** Only when read and write models genuinely diverge. Don't adopt CQRS just because it sounds sophisticated — start with a unified model and split when the pain is real.
