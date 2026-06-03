# JavaScript/TypeScript Application Architecture

## Functional Core / Imperative Shell in TypeScript

The same principle applies: pure functions at the core, side effects at the edges.

### Bad — Mixed concerns

```typescript
async function createUser(req: Request, res: Response) {
  const db = await getDb();
  const user = await db.query('INSERT INTO users ...', [req.body.name]);
  await sendEmail(user.email, 'Welcome!');
  res.json({ id: user.id });
}
```

### Good — Separated

```typescript
// Pure domain function
function createUserService(name: string, email: string): User {
  validateName(name);
  validateEmail(email);
  return { id: generateId(), name, email, createdAt: new Date() };
}

// Imperative shell (route handler)
async function createUserHandler(req: Request, res: Response) {
  const user = createUserService(req.body.name, req.body.email);
  await userRepository.save(user);
  await emailService.send(user.email, 'Welcome!');
  res.status(201).json(userToResponse(user));
}
```

## Layered Architecture for Node.js

```
┌─────────────────────────────────┐
│  Controllers / Route Handlers    │  ← Parse request, call service, return response
├─────────────────────────────────┤
│  Application Services            │  ← Orchestration, use-case logic, transaction boundaries
├─────────────────────────────────┤
│  Domain Services                 │  ← Business rules, pure functions
├─────────────────────────────────┤
│  Repository Interfaces (ports)   │  ← Abstract data access
├─────────────────────────────────┤
│  Domain Entities / Value Objects │  ← Core business concepts
└─────────────────────────────────┘
```

Dependency direction: Controllers → Services → Repositories → Entities (inward).

## Dependency Injection

### Simple manual DI (preferred for most cases)

```typescript
// Composition root (src/index.ts)
const config = loadConfig();
const db = new PostgresPool(config.databaseUrl);
const userRepo = new UserRepository(db);
const emailService = new SendGridEmailService(config.sendGridKey);
const userService = new UserService(userRepo, emailService);
const app = createApp({ userService });
```

### Container-based (for large apps)

Use `tsyringe` or `inversify` when the dependency graph is deep:

```typescript
import { injectable, container, inject } from "tsyringe";

@injectable()
class UserService {
  constructor(
    @inject("UserRepository") private repo: UserRepository,
    @inject("EmailService") private email: EmailService,
  ) {}
}
```

**Rule**: Start with manual composition root. Only add a DI container when you have >10 services with complex interdependencies.

## DDD Patterns in TypeScript

### Entity with identity

```typescript
export class User {
  constructor(
    public readonly id: UserId,
    public name: string,
    public readonly email: Email,
    private readonly status: UserStatus,
  ) {}

  activate(): Result<User, DomainError> {
    if (this.status === "banned") return Err(new UserBannedError(this.id));
    this.status = "active";
    return Ok(this);
  }
}
```

### Value Object

```typescript
export class Money {
  private constructor(
    public readonly amount: number,
    public readonly currency: string,
  ) {}

  static create(amount: number, currency: string): Money {
    if (amount < 0) throw new Error("Amount must be non-negative");
    return new Money(amount, currency);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) throw new Error("Currency mismatch");
    return Money.create(this.amount + other.amount, this.currency);
  }
}
```

### Aggregate Root

```typescript
export class Order {
  readonly id: OrderId;
  readonly items: OrderItem[];
  private status: OrderStatus;

  addItem(product: Product, quantity: number): void {
    if (this.status !== "draft") throw new Error("Can only add items to draft orders");
    this.items.push(new OrderItem(product.id, quantity, product.price));
  }

  submit(): void {
    if (this.items.length === 0) throw new Error("Cannot submit empty order");
    this.status = "submitted";
  }
}
```

## Event-Driven Patterns

### Node.js EventEmitter (simple)

```typescript
import { EventEmitter } from "node:events";

export const domainEvents = new EventEmitter();

// Publish
domainEvents.emit("OrderSubmitted", { orderId, userId, timestamp });

// Subscribe
domainEvents.on("OrderSubmitted", async (event) => {
  await inventoryService.reserve(event.orderId);
  await notificationService.sendConfirmation(event.userId);
});
```

### RxJS (for complex event flows)

Use RxJS when you need: windowing, debouncing, combining multiple streams, backpressure handling.

```typescript
import { Subject } from "rxjs";
import { debounceTime, filter, switchMap } from "rxjs/operators";

const orderEvents$ = new Subject<OrderEvent>();

orderEvents$
  .pipe(
    filter((e) => e.type === "OrderSubmitted"),
    debounceTime(100),
    switchMap((e) => processOrderAsync(e)),
  )
  .subscribe();
```
