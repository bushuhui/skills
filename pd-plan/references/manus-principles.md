# Manus Context Engineering Principles

## Core Principle

Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)

Anything important gets written to disk.

## The Five Manus Principles

| Principle | Implementation |
|-----------|----------------|
| Filesystem as memory | Store in files, not context |
| Attention manipulation | Re-read plan before decisions (hooks) |
| Error persistence | Log failures in plan file |
| Goal tracking | Checkboxes show progress |
| Completion verification | Stop hook checks all phases |

## Critical Rules

1. **Create Plan First** — Never start without `task_plan.md`. Non-negotiable.
2. **The 2-Action Rule** — Save findings after every 2 view/browser/search operations.
3. **Log ALL Errors** — They help avoid repetition.
4. **Never Repeat Failures** — Track attempts, mutate approach instead.
5. **Continue After Completion** — Add new phases when user requests additional work.

## The 3-Strike Error Protocol

- **Attempt 1**: Diagnose and fix
- **Attempt 2**: Alternative approach
- **Attempt 3**: Broader rethink
- **After 3 failures**: Escalate to user

## The 5-Question Reboot Test

| Question | Answer Source |
|----------|---------------|
| Where am I? | Current phase in task_plan.md |
| Where am I going? | Remaining phases |
| What's the goal? | Goal statement in plan |
| What have I learned? | findings.md |
| What have I done? | progress.md |

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Use TodoWrite for persistence | Create task_plan.md file |
| State goals once and forget | Re-read plan before decisions |
| Hide errors and retry silently | Log errors to plan file |
| Stuff everything in context | Store large content in files |
| Start executing immediately | Create plan file FIRST |
| Repeat failed actions | Track attempts, mutate approach |
