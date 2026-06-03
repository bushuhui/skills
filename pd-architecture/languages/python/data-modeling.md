# Python Data Modeling

## When to Use What

| Tool | Use For |
|------|---------|
| **dataclasses** | Domain models, internal data (standard library, lightweight) |
| **Pydantic** | API boundaries — request/response validation, JSON schema |
| **attrs** | Advanced cases when dataclasses aren't enough |

## dataclasses for Domain Layer

```python
@dataclass
class Product:
    id: UUID
    name: str
    price: Decimal
    in_stock: bool = True

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
```

**field() for advanced config:**
```python
@dataclass
class Order:
    id: UUID = field(default_factory=uuid4)
    items: list[str] = field(default_factory=list)  # Safe mutable default
    metadata: dict = field(default_factory=dict, compare=False)
```

**Validation with `__post_init__`:**
```python
@dataclass
class User:
    email: str
    age: int
    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError("Invalid email")
        if self.age < 18:
            raise ValueError("Must be 18+")
```

## Pydantic for API Boundaries

```python
class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=18, le=120)

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    model_config = {"from_attributes": True}
```

**Custom validators:**
```python
@field_validator("items")
@classmethod
def items_not_empty(cls, v):
    if not v:
        raise ValueError("Order must have at least one item")
    return v

@model_validator(mode="after")
def validate_discount_with_items(self):
    if self.discount > 0 and len(self.items) < 2:
        raise ValueError("Discount requires at least 2 items")
    return self
```

## Entity Transformations

Entity handles all data layer conversions:

```python
@dataclass
class Product:
    @classmethod
    def from_request(cls, req: CreateProductRequest) -> "Product":
        return cls(id=uuid4(), name=req.name, price=req.price, in_stock=True)

    def to_response(self) -> ProductResponse:
        return ProductResponse(id=self.id, name=self.name, price=self.price, in_stock=self.in_stock)

    @classmethod
    def from_record(cls, record: ProductRecord) -> "Product":
        return cls(id=record.id, name=record.name, price=record.price, in_stock=record.in_stock)

    def to_record(self) -> ProductRecord:
        return ProductRecord(id=self.id, name=self.name, price=self.price, in_stock=self.in_stock)
```

**Flow:**
- `from_request`: API → domain
- `to_response`: domain → API
- `from_record`: database → domain
- `to_record`: domain → database

## Best Practices

1. dataclasses for domain layer, Pydantic for API boundaries
2. `frozen=True` for value objects (immutability)
3. Keep transformations in entities, not services
4. Never expose database models to API layer
5. Validate at boundaries (Pydantic) or in entities (`__post_init__`)
