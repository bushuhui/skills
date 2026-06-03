# JavaScript/TypeScript Data Modeling

## TypeScript Interfaces vs Classes for Domain Models

| Approach | When to use | Pros | Cons |
|----------|-------------|------|------|
| `interface` | Read-only DTOs, API boundaries | Zero runtime cost, structural typing | No behavior, no validation |
| `class` | Domain entities with behavior | Methods, encapsulation, invariants | More boilerplate |
| `type` | Unions, mapped types | Flexible, composable | No runtime representation |

**Rule**: Use `interface` for external contracts (API requests/responses), `class` for domain entities with invariants.

## Runtime Validation with Zod

TypeScript types are compile-time only. Use Zod for runtime validation at system boundaries.

```typescript
import { z } from "zod";

// Schema doubles as TypeScript type
const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(["admin", "user", "guest"]).default("user"),
});

type CreateUserInput = z.infer<typeof CreateUserSchema>;

// Validate at the boundary
function handleCreateUser(raw: unknown): CreateUserInput {
  const result = CreateUserSchema.safeParse(raw);
  if (!result.success) {
    throw new ValidationError(result.error.flatten().fieldErrors);
  }
  return result.data;
}
```

### Zod vs Yup vs io-ts

| Library | Bundle size | TypeScript inference | Async validation | Ecosystem |
|---------|------------|---------------------|-----------------|-----------|
| **Zod** | ~13KB | `z.infer<T>` | Yes | Largest (Fastify, tRPC, React Hook Form) |
| Yup | ~16KB | Manual | Yes | Mature (Formik) |
| io-ts | ~8KB | Automatic | No | FP-heavy (fp-ts ecosystem) |

**Default choice**: Zod. Best TypeScript integration and ecosystem support.

## ORM: Prisma vs TypeORM vs Drizzle

### Prisma (recommended default)

Type-safe, schema-first, excellent DX.

```prisma
// schema.prisma
model User {
  id        String   @id @default(uuid())
  name      String
  email     String   @unique
  role      Role     @default(USER)
  posts     Post[]
  createdAt DateTime @default(now())
}
```

```typescript
const user = await prisma.user.create({
  data: { name: "Alice", email: "alice@example.com" },
  include: { posts: true },
});
```

**Pros**: Auto-generated types, excellent migrations, great introspection.
**Cons**: Black-box query builder, complex queries can be slow, limited raw SQL.

### Drizzle ORM

SQL-like syntax, zero magic, full TypeScript inference.

```typescript
const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  name: varchar("name", { length: 100 }).notNull(),
  email: varchar("email", { length: 255 }).notNull().unique(),
});

const result = await db.select().from(users).where(eq(users.role, "admin"));
```

**Pros**: Transparent SQL, no codegen black box, works with existing databases.
**Cons**: Less auto-magic than Prisma, smaller community.

### TypeORM

Active Record + Data Mapper patterns, decorator-based.

```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn("uuid")
  id: string;

  @Column()
  name: string;

  @OneToMany(() => Post, (post) => post.user)
  posts: Post[];
}
```

**Pros**: Familiar to Java/Spring developers, supports both patterns.
**Cons**: Decorator magic is hard to debug, slow migrations, type inference gaps.

**Recommendation**: Prisma for new projects, Drizzle for SQL-transparent needs, avoid TypeORM unless required by existing codebase.

## DTO Patterns and Transformers

```typescript
// Request DTO (validated by Zod)
const CreateOrderRequest = z.object({
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().positive(),
  })),
});

// Response DTO
interface OrderResponse {
  id: string;
  items: { productId: string; quantity: number; price: number }[];
  total: number;
  status: string;
}

// Transform: domain → response
function orderToResponse(order: Order): OrderResponse {
  return {
    id: order.id.value,
    items: order.items.map((item) => ({
      productId: item.productId.value,
      quantity: item.quantity,
      price: item.unitPrice.amount,
    })),
    total: order.total().amount,
    status: order.status,
  };
}

// Transform: request → command
function toCreateOrderCommand(input: z.infer<typeof CreateOrderRequest>): CreateOrderCommand {
  return {
    items: input.items.map((item) => ({
      productId: new ProductId(item.productId),
      quantity: item.quantity,
    })),
  };
}
```
