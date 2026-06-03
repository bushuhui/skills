# Event Sourcing

**Problem:** Need complete audit trail and ability to reconstruct state at any point in time.

**When to use:**
- Audit trail is regulatory requirement
- Need to answer "how did we get here?"
- Complex domain with undo/redo requirements
- Debugging production issues requires history

**When NOT to use:**
- Simple CRUD applications
- No audit requirements
- Team unfamiliar with pattern
- Reporting on current state is primary need

**Trade-offs:**

| Pros | Cons |
|------|------|
| Complete audit trail | Storage grows indefinitely |
| Time-travel debugging | Query complexity |
| Natural fit for event-driven | Learning curve |
| Enables CQRS | Eventual consistency |

**Key concept:** State is derived from a sequence of events, not stored as a current snapshot.

```typescript
// Aggregate rebuilt from events
class Order {
  static fromEvents(events: OrderEvent[]): Order {
    const order = new Order();
    events.forEach(event => order.apply(event));
    return order;
  }
}
```

**Snapshotting:** Required for aggregates with many events. Snapshot current state periodically to avoid replaying thousands of events.
