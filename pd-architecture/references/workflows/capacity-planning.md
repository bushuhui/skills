# Capacity Planning Workflow

## Step 1: Gather Requirements

| Metric | Current | 6 months | 1 year |
|--------|---------|----------|--------|
| Monthly active users | | | |
| Peak concurrent users | | | |
| Requests per second | | | |
| Data storage (GB) | | | |

## Step 2: Calculate Compute Requirements

```
Peak RPS:           3,600
Requests per server: 500 (conservative)
Servers needed:     3,600 / 500 = 8 servers
With redundancy (N+2): 10 servers
```

**CPU estimation:**
```
Per request: 50ms CPU time
Peak RPS:    3,600
CPU cores:   3,600 × 0.05 = 180 cores
With headroom (70% target): 180 / 0.7 = 257 cores
```

## Step 3: Calculate Storage Requirements

```
Records per day:    100,000
Record size:        2KB
Daily growth:       200MB
With indexes (2x):  400MB/day
Retention (1 year): 146GB
With replication (3x): 438GB
```

## Step 4: Calculate Network Requirements

```
Response size:      10KB average
Peak RPS:           3,600
Outbound:           3,600 × 10KB = 36MB/s = 288 Mbps
With headroom (50%): 432 Mbps ≈ 500 Mbps connection
```

## Step 5: Document and Review

Create capacity plan document: current requirements, growth projections, infrastructure recommendations, cost estimates, review triggers.
