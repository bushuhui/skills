# JavaScript Architecture Patterns

## Repository Pattern with Prisma

```typescript
// Abstract interface (port)
export interface Repository<T, ID> {
  findById(id: ID): Promise<T | null>;
  findAll(options?: { page?: number; limit?: number }): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: ID): Promise<void>;
}

// Prisma implementation
export class PrismaUserRepository implements Repository<User, string> {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    const record = await this.prisma.user.findUnique({ where: { id } });
    return record ? recordToEntity(record) : null;
  }

  async findAll({ page = 1, limit = 20 } = {}): Promise<User[]> {
    const records = await this.prisma.user.findMany({
      skip: (page - 1) * limit,
      take: limit,
      orderBy: { createdAt: "desc" },
    });
    return records.map(recordToEntity);
  }

  async save(user: User): Promise<User> {
    const record = await this.prisma.user.upsert({
      where: { id: user.id },
      create: entityToRecord(user),
      update: entityToPartialRecord(user),
    });
    return recordToEntity(record);
  }

  async delete(id: string): Promise<void> {
    await this.prisma.user.delete({ where: { id } });
  }
}
```

## Service Layer Pattern

```typescript
export class UserService {
  constructor(
    private repo: UserRepository,
    private events: EventEmitter,
  ) {}

  async create(input: CreateUserInput): Promise<User> {
    const existing = await this.repo.findByEmail(input.email);
    if (existing) throw new DuplicateEmailError(input.email);

    const user = User.create(input.name, input.email);
    const saved = await this.repo.save(user);

    this.events.emit("UserCreated", { userId: saved.id, email: saved.email });
    return saved;
  }

  async deactivate(userId: string): Promise<void> {
    const user = await this.repo.findById(userId);
    if (!user) throw new NotFoundError("User", userId);

    user.deactivate();
    await this.repo.save(user);
  }
}
```

## Event Bus

### Simple (Node.js EventEmitter)

```typescript
import { EventEmitter } from "node:events";

export const eventBus = new EventEmitter();

// Typed events
export type DomainEvent =
  | { type: "UserCreated"; userId: string; email: string }
  | { type: "OrderSubmitted"; orderId: string; total: number };

eventBus.on("UserCreated", (event) => {
  console.log(`New user: ${event.email}`);
});

eventBus.emit("UserCreated", { userId: "123", email: "alice@example.com" });
```

### Structured (with handler registry)

```typescript
type Handler<T> = (event: T) => Promise<void>;

export class EventBus {
  private handlers = new Map<string, Handler<unknown>[]>();

  register<T>(type: string, handler: Handler<T>): void {
    const list = this.handlers.get(type) ?? [];
    list.push(handler as Handler<unknown>);
    this.handlers.set(type, list);
  }

  async emit<T>(type: string, event: T): Promise<void> {
    const handlers = this.handlers.get(type) ?? [];
    await Promise.allSettled(handlers.map((h) => h(event)));
  }
}
```

## Circuit Breaker

```typescript
export class CircuitBreaker {
  private failures = 0;
  private state: "closed" | "open" | "half-open" = "closed";
  private readonly threshold: number;
  private readonly timeout: number;
  private lastFailureTime?: number;

  constructor(threshold = 5, timeout = 30_000) {
    this.threshold = threshold;
    this.timeout = timeout;
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === "open") {
      if (Date.now() - (this.lastFailureTime ?? 0) > this.timeout) {
        this.state = "half-open";
      } else {
        throw new Error("Circuit breaker is open");
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (err) {
      this.onFailure();
      throw err;
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this.state = "closed";
  }

  private onFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
    if (this.failures >= this.threshold) {
      this.state = "open";
    }
  }
}
```

## Retry with Exponential Backoff

```typescript
interface RetryOptions {
  maxAttempts?: number;
  baseDelay?: number;
  maxDelay?: number;
  jitter?: boolean;
}

export async function retry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<T> {
  const { maxAttempts = 3, baseDelay = 1000, maxDelay = 30000, jitter = true } = options;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxAttempts) throw err;

      let delay = baseDelay * 2 ** (attempt - 1);
      delay = Math.min(delay, maxDelay);
      if (jitter) delay *= 0.5 + Math.random() * 0.5;

      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw new Error("unreachable");
}
```

## CQRS Implementation

```typescript
// Commands (write side)
interface CommandHandler<C, R> {
  handle(command: C): Promise<R>;
}

class CreateOrderHandler implements CommandHandler<CreateOrderCommand, Order> {
  constructor(private repo: OrderRepository) {}

  async handle(command: CreateOrderCommand): Promise<Order> {
    const order = Order.create(command.items);
    return this.repo.save(order);
  }
}

// Queries (read side)
interface QueryHandler<Q, R> {
  handle(query: Q): Promise<R>;
}

class GetOrderSummaryHandler implements QueryHandler<GetOrderSummary, OrderSummary> {
  constructor(private readDb: ReadDatabase) {}

  async handle(query: GetOrderSummary): Promise<OrderSummary> {
    return this.readDb.query(
      `SELECT o.id, o.total, COUNT(oi.id) as item_count
       FROM orders o LEFT JOIN order_items oi ON o.id = oi.order_id
       WHERE o.id = $1 GROUP BY o.id`,
      [query.orderId],
    );
  }
}

// Command/query bus
export class CommandBus {
  private handlers = new Map<string, CommandHandler<unknown, unknown>>();

  register<T>(type: string, handler: CommandHandler<T, unknown>): void {
    this.handlers.set(type, handler);
  }

  async dispatch<T, R>(type: string, command: T): Promise<R> {
    const handler = this.handlers.get(type);
    if (!handler) throw new Error(`No handler for ${type}`);
    return handler.handle(command) as Promise<R>;
  }
}
```

## Middleware Patterns for Express/Fastify

### Express middleware chain

```typescript
// Request ID middleware
export function requestId(req: Request, res: Response, next: NextFunction) {
  req.id = crypto.randomUUID();
  res.setHeader("X-Request-ID", req.id);
  next();
}

// Request logger
export function requestLogger(logger: Logger) {
  return (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();
    res.on("finish", () => {
      logger.info({
        method: req.method,
        url: req.url,
        status: res.statusCode,
        duration: Date.now() - start,
        requestId: req.id,
      });
    });
    next();
  };
}

// Rate limiter
export function rateLimiter(redis: RedisClient, maxRequests = 100, windowMs = 60_000) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const key = `ratelimit:${req.ip}`;
    const count = await redis.incr(key);
    if (count === 1) await redis.expire(key, Math.ceil(windowMs / 1000));
    if (count > maxRequests) {
      return res.status(429).json({ error: { code: "RATE_LIMITED" } });
    }
    next();
  };
}
```
