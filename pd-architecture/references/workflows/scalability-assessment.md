# Scalability Assessment Workflow

## Step 1: Profile Current System

```
Current load:
- Average requests/sec: ___
- Peak requests/sec: ___
- Average latency: ___ ms
- P99 latency: ___ ms
- Error rate: ___%

Resource utilization:
- CPU: ___%   Memory: ___%   Disk I/O: ___%   Network: ___%
```

## Step 2: Identify Bottlenecks

| Layer | Bottleneck Signs |
|-------|------------------|
| Web servers | High CPU, connection limits |
| Application | Slow requests, thread pool exhaustion |
| Database | Slow queries, lock contention |
| Cache | High miss rate, memory pressure |
| Network | Bandwidth saturation, latency |

## Step 3: Load Test

```
1. Baseline: Current production load
2. 2x load: Expected growth in 6 months
3. 5x load: Stress test
4. Spike: Sudden 10x for 5 minutes
```

**Tools:** k6, Locust, JMeter for HTTP; pgbench for PostgreSQL; redis-benchmark for Redis.

## Step 4: Identify Scaling Strategy

**Vertical scaling (scale up):** Add more CPU, memory, disk. Simpler but has limits. Use when single server can handle more.

**Horizontal scaling (scale out):** Add more servers. Requires stateless design. Use when need linear scaling.

## Step 5: Create Scaling Plan

```
Trigger: When average CPU > 70% for 15 minutes

Action:
1. Add 2 more web servers
2. Update load balancer
3. Verify health checks pass

Rollback:
1. Remove added servers
2. Update load balancer
3. Investigate issue
```
