# Caching Strategy

## Cache Type Selection

| Type | Use Case | Invalidation | Complexity |
|------|----------|--------------|------------|
| Read-through | Frequent reads, tolerance for stale | On write/TTL | Low |
| Write-through | Data consistency critical | Automatic | Medium |
| Write-behind | High write throughput | Async | High |
| Cache-aside | Fine-grained control | Application | Medium |

## Cache Technology Selection

| Technology | Best For | Limitations |
|------------|----------|-------------|
| Redis | General purpose, data structures | Memory cost |
| Memcached | Simple key-value, high throughput | No persistence |
| CDN (CloudFront, Fastly) | Static assets, edge caching | Dynamic content |
| Application cache | Per-instance, small data | Not distributed |

## Cache-Aside Pattern (Most Common)

```
Read:
1. Check cache
2. If miss, read from DB
3. Store in cache
4. Return data

Write:
1. Write to DB
2. Invalidate cache
```

## TTL Guidelines

| Data Type | Suggested TTL |
|-----------|---------------|
| User sessions | 24-48 hours |
| API responses | 1-5 minutes |
| Static content | 24 hours - 1 week |
| Database queries | 5-60 minutes |
| Feature flags | 1-5 minutes |

**Default:** Redis with cache-aside pattern.
