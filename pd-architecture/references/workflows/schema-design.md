# Database Schema Design Workflow

## Step 1: Identify Entities

List the things you need to store:
```
E-commerce:
- User (id, email, name, created_at)
- Product (id, name, price, stock)
- Order (id, user_id, status, total)
- OrderItem (id, order_id, product_id, quantity, price)
```

## Step 2: Define Relationships

```
User ──1:N──▶ Order       (one user, many orders)
Order ──1:N──▶ OrderItem  (one order, many items)
Product ──1:N──▶ OrderItem (one product, many order items)
```

## Step 3: Choose Primary Keys

| Type | Pros | Cons |
|------|------|------|
| Auto-increment | Simple, ordered | Not distributed-friendly |
| UUID | Globally unique | Larger, random |
| ULID | Globally unique, sortable | Larger |

## Step 4: Add Indexes

```sql
-- Index columns used in WHERE clauses
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Index columns used in JOINs
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- Composite indexes for common queries
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index for filtered queries
CREATE INDEX idx_orders_active ON orders(created_at) WHERE status = 'active';
```

## Step 5: Plan for Scale

**Partitioning:**
```sql
-- Partition by date (time-series data)
CREATE TABLE events (id BIGINT, created_at TIMESTAMP, data JSONB)
PARTITION BY RANGE (created_at);

-- Partition by hash (distribute evenly)
CREATE TABLE users (id BIGINT, email VARCHAR(255))
PARTITION BY HASH (id);
```

**Sharding considerations:** Shard key selection, cross-shard query limitations, rebalancing strategy.
