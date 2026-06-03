# Migration Planning Workflow

## Step 1: Assess Current State

Document: current architecture diagram, data volumes, dependencies, integration points, performance baselines.

## Step 2: Define Target State

Document: new architecture diagram, technology changes, expected improvements, success criteria.

## Step 3: Plan Migration Strategy

| Strategy | Risk | Downtime | Complexity |
|----------|------|----------|------------|
| Big bang | High | Yes | Low |
| Blue-green | Medium | Minimal | Medium |
| Canary | Low | None | High |
| Strangler fig | Low | None | High |

**Strangler fig pattern (recommended for large systems):**
1. Add facade in front of old system
2. Route small percentage of traffic to new system
3. Gradually increase traffic to new system
4. Retire old system when 100% migrated

## Step 4: Create Rollback Plan

For each step, define:
```
Step: Migrate user service to new database

Rollback trigger:
- Error rate > 1%
- Latency > 500ms P99
- Data inconsistency detected

Rollback steps:
1. Route traffic back to old database
2. Sync any new data back
3. Investigate root cause
Rollback time estimate: 15 minutes
```

## Step 5: Execute with Checkpoints

```
□ Backup current system
□ Verify backup restoration works
□ Deploy new infrastructure
□ Run smoke tests on new system
□ Migrate small percentage (1%)
□ Monitor for 24 hours
□ Increase to 10%
□ Monitor for 24 hours
□ Increase to 50%
□ Monitor for 24 hours
□ Complete migration (100%)
□ Decommission old system
□ Document lessons learned
```
