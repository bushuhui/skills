# Database Selection

## SQL vs NoSQL

| Factor | Choose SQL | Choose NoSQL |
|--------|-----------|--------------|
| Data relationships | Complex, many-to-many | Simple, denormalized OK |
| Schema | Well-defined, stable | Evolving, flexible |
| Transactions | ACID required | Eventual consistency OK |
| Query patterns | Complex joins, aggregations | Key-value, document lookups |
| Scale | Vertical (some horizontal) | Horizontal first |

## Database Type Selection

**Relational:**
| Database | Best For | Avoid When |
|----------|----------|------------|
| PostgreSQL | General purpose, JSON support, extensions | Simple key-value only |
| MySQL | Web applications, read-heavy | Complex queries, JSON-heavy |
| SQLite | Embedded, development, small apps | Concurrent writes, scale |

**Document:**
| Database | Best For | Avoid When |
|----------|----------|------------|
| MongoDB | Flexible schema, rapid iteration | Complex transactions |

**Key-Value:**
| Database | Best For | Avoid When |
|----------|----------|------------|
| Redis | Caching, sessions, real-time | Persistence critical |
| DynamoDB | Serverless, auto-scaling | Complex queries |

**Time-Series:**
| Database | Best For | Avoid When |
|----------|----------|------------|
| TimescaleDB | Time-series with SQL | Non-time-series data |

**Search:**
| Database | Best For | Avoid When |
|----------|----------|------------|
| Elasticsearch | Full-text search, logs | Primary data store |

## Quick Decision Flow

```
Start
  ├─ Need ACID transactions? ──Yes──► PostgreSQL/MySQL
  ├─ Flexible schema needed? ──Yes──► MongoDB
  ├─ Write-heavy (>50K/sec)? ──Yes──► Cassandra/ScyllaDB
  ├─ Key-value access only? ──Yes──► Redis/DynamoDB
  ├─ Time-series data? ──Yes──► TimescaleDB/InfluxDB
  ├─ Full-text search? ──Yes──► Elasticsearch
  └─ Default ──────────────────────► PostgreSQL
```

**Default:** PostgreSQL for most applications.
