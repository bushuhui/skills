# Event-Driven Architecture

**Problem:** Need loose coupling between components that react to business events asynchronously.

**When to use:**
- Components need loose coupling
- Audit trail of all changes is valuable
- Real-time reactions to events
- Multiple consumers for same events

**When NOT to use:**
- Simple CRUD operations
- Synchronous responses required
- Team unfamiliar with async patterns
- Debugging simplicity is priority

**Trade-offs:**

| Pros | Cons |
|------|------|
| Loose coupling | Eventual consistency |
| Scalability | Debugging complexity |
| Audit trail built-in | Message ordering challenges |
| Easy to add new consumers | Infrastructure complexity |

**Event structure:**
```typescript
interface DomainEvent {
  eventId: string;
  eventType: string;
  aggregateId: string;
  timestamp: Date;
  payload: Record<string, unknown>;
  metadata: {
    correlationId: string;
    causationId: string;
  };
}
```
