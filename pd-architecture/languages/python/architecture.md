# Python Application Architecture

Modern Python application architecture: functional core / imperative shell, DDD, and layered design.

## Core Principle: Functional Core / Imperative Shell

Separate pure business logic from side effects:

- **Functional Core**: Pure functions, business logic, no IO
- **Imperative Shell**: Coordinates external dependencies, handles side effects

**Bad — mixed concerns:**
```python
def process_order(order_id):
    response = requests.get(f"/api/orders/{order_id}")  # IO
    order_data = response.json()
    if order_data["total"] > 100:  # Business logic
        discount = 0.1
    save_order(order_data)  # IO
```

**Good — separated:**
```python
# Functional Core (pure)
def calculate_discount(total: Decimal) -> Decimal:
    return Decimal("0.1") if total > 100 else Decimal("0")

# Imperative Shell (IO only)
def process_order(order_id: str) -> None:
    order = fetch_order(order_id)  # IO
    discount = calculate_discount(order.total)  # Pure
    save_order(order, discount)  # IO
```

## Layered Architecture

```
Router/Handler → Service → Repository → Entity → Database
```

Each layer depends only on layers below.

| Layer | Responsibility |
|-------|----------------|
| Entity | Domain models, validation, business rules |
| Repository | Abstract storage interface, returns domain entities |
| Service | Business workflows, orchestrates entities and repositories |
| Router/Handler | HTTP handling, delegates to services |

## Domain Models

**Entity:**
```python
@dataclass
class Order:
    id: UUID
    customer_id: UUID
    total: Decimal
    status: str

    def apply_discount(self, rate: Decimal) -> None:
        if self.status == "pending":
            self.total = self.total * (1 - rate)
```

**Value Object (immutable):**
```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
```

## Repository Pattern

```python
class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: UUID) -> Optional[Order]: ...
    @abstractmethod
    def save(self, order: Order) -> None: ...

class PostgresOrderRepository(OrderRepository):
    def get(self, order_id: UUID) -> Optional[Order]:
        record = self.session.get(OrderRecord, order_id)
        return Order.from_record(record) if record else None
```

## DDD Building Blocks

- **Entities**: Objects with identity (ID-based equality)
- **Value Objects**: Immutable, equality by attributes
- **Aggregates**: Cluster of entities treated as a unit (transaction boundary)
- **Domain Services**: Business logic spanning multiple entities
- **Application Services**: Use case orchestration with IO
- **Bounded Contexts**: Separate models for different subdomains

## Anti-Patterns

- **Anemic Domain Model**: Entities with only getters/setters, all logic in services
- **Transaction Script**: All logic in service layer, entities just data
- **Leaky Abstraction**: Repository exposing database details
- **God Object**: Entity with too many responsibilities
- **Mixed Concerns**: Business logic calling IO directly
