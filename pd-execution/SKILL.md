---
name: pd-execution
description: Find incomplete issues on the local markdown issue tracker, execute their acceptance criteria in dependency order, and mark them as completed. Use when you want to批量执行未完成的任务、按依赖顺序实现 issue、或自动完成已规划的切片。
---

# Execution

Scan the project's local markdown issue tracker, identify incomplete issues, resolve their dependency order, execute each one's acceptance criteria, and write completion status back to the issue files.

The issue tracker and triage label vocabulary should have been provided to you — run `/pd-setup` if not.

## Process

### 1. Discover issues

Read `docs/agents/issue-tracker.md` to confirm the tracker layout. For local markdown, issues live under `.scratch/<feature-slug>/issues/`.

Glob for all `.md` files in each `.scratch/*/issues/` directory. Read every issue file to get its full content.

### 2. Assess completion status

For each issue file, check:

- **Explicit completion marker**: Look for a `## Completed` section with a date. If present, the issue is done — skip it.
- **Acceptance criteria**: Count how many `- [ ]` (unchecked) vs `- [x]` (checked) boxes exist. If ALL are checked and there's a completion marker, skip.
- **Implicit completion**: If all acceptance criteria appear satisfied based on codebase verification (grep for the described behavior), flag it as "appears done but not marked" — the user can confirm.

Present a summary table:

| # | Issue | Status | Blocked by |
|---|-------|--------|------------|
| 01 | Map loading | ✅ Completed | — |
| 02 | A* pathfinding | ⚠️ Appears done, not marked | 01 |
| 03 | LiDAR scanning | ❌ Incomplete | 01 |

### 3. Resolve dependency order

For all incomplete issues, parse their `## Blocked by` sections to build a dependency graph.

Perform a topological sort to determine execution order. Present the order to the user:

```
执行顺序：
1. 02-astar-pathfinding (无依赖)
2. 03-lidar-scanning (依赖 01 ✅)
3. 04-simulation-state-machine (依赖 02, 03)
```

If there are circular dependencies or unclear ordering, ask the user which to execute first.

### 4. Execute each issue in order

For each issue in dependency order:

**a. Read the issue fully** — understand the acceptance criteria and what to build.

**b. Verify current state** — explore the codebase to see what's already implemented vs what's missing.

**c. Report findings** — tell the user:
  - What already exists (if anything)
  - What needs to be built
  - Your implementation approach

**d. Wait for confirmation** — ask the user if the approach looks right before coding.

**e. Implement** — write the code, following the project's development principles (KISS, SOLID, single responsibility, minimal change scope).

**f. Verify acceptance criteria** — after implementation, verify each criterion:
  - For code behavior: run the relevant commands/tests
  - For API endpoints: curl the endpoint
  - For UI: use browser tools or manual verification
  - For format/structure: grep the codebase

**g. Mark as completed** — append a completion section to the issue file:

```markdown
## Completed

- **Date**: YYYY-MM-DD
- **Verification**:
  - [x] Criterion 1 — verified via `curl ...` / code inspection / browser
  - [x] Criterion 2 — verified via ...
- **Notes**: Any deviations from original plan or important decisions made
```

Also convert all remaining `- [ ]` acceptance criteria to `- [x]` in the original section.

**h. Move to next issue** — repeat until all incomplete issues are done.

### 5. Done

After all issues are executed and marked, summarize:

- How many issues were completed
- Any issues that were skipped (and why)
- The final state of all issues

Guide the user:

- **Want to plan the next feature** → run `/pd-brainstorming` to explore new ideas
- **Want to document what was just built** → run `/pd-doc` to update architecture/API docs and changelog
- **All issues done, nothing new** → you're caught up

## Safety rules

- **Never execute destructive operations** (git reset --hard, rm -rf, force push) without explicit user confirmation
- **Show the plan before coding** — especially for the first issue, so the user can redirect if your understanding is wrong
- **Respect existing code** — don't rewrite working code just because your approach differs
- **One issue at a time** — complete and verify one before starting the next
- **If stuck, ask** — if an acceptance criteria is ambiguous or can't be satisfied, flag it to the user rather than making assumptions

## Edge cases

- **No incomplete issues**: Tell the user all issues are already completed.
- **Blocked by unimplemented issue**: Skip until the blocker is done (the topological sort should handle this).
- **Issue references files that don't exist**: The issue may be outdated — flag this to the user before deciding whether to execute or skip.
- **Multiple feature directories**: If `.scratch/` has multiple `<feature-slug>/issues/` directories, process them one feature at a time — ask the user which feature to focus on first.
