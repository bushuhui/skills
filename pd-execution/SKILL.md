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

### 2. Assess completion status and resume interrupted work

For each issue file, check:

- **Explicit completion marker**: Look for a `## Completed` section with a date. If present, the issue is done — skip it.
- **Acceptance criteria**: Count how many `- [ ]` (unchecked) vs `- [x]` (checked) boxes exist. If ALL are checked and there's a completion marker, skip.
- **Implicit completion**: If all acceptance criteria appear satisfied based on codebase verification (grep for the described behavior), flag it as "appears done but not marked" — the user can confirm.
- **Interrupted work**: Look for a `## In Progress` section. If present **without** a `## Completed` section, this issue was previously started but not finished (e.g., session timed out, crash, or user exited). Capture:
  - The `Started` timestamp
  - The `Step` field (which sub-step it was in)
  - Any `Notes` about what was already done

Present a summary table:

| # | Issue | Status | Blocked by |
|---|-------|--------|------------|
| 01 | Map loading | ✅ Completed | — |
| 02 | A* pathfinding | ⚠️ Appears done, not marked | 01 |
| 03 | LiDAR scanning | ❌ Incomplete | 01 |
| 04 | Dynamic replanning | 🔄 Interrupted (Step: implementing) | 03 |

**Resumption strategy**:
- If interrupted issues exist, **ask the user** whether to resume from where it left off or restart from scratch.
- If resuming: skip the "Read" and "Verify current state" steps for that issue (already done), jump directly to the recorded `Step`.
- If restarting: remove the `## In Progress` section and treat as a fresh issue.

### 3. Resolve dependency order

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

**b. Write "In Progress" marker** — immediately after reading, append to the issue file:

```markdown
## In Progress

- **Started**: YYYY-MM-DD HH:MM
- **Step**: analyzing
- **Notes**: What has been understood so far (key acceptance criteria, constraints)
```

This marker serves as a progress checkpoint. If execution is interrupted, the next run of `/pd-execution` will detect this marker and offer to resume.

**c. Verify current state** — explore the codebase to see what's already implemented vs what's missing.

**d. Update marker → Step: reporting** — update the `## In Progress` section:

```markdown
## In Progress

- **Started**: YYYY-MM-DD HH:MM
- **Step**: reporting
- **Notes**: What already exists, what's missing, proposed approach
```

**e. Report findings** — tell the user:
  - What already exists (if anything)
  - What needs to be built
  - Your implementation approach

**f. Determine confirmation strategy** — judge whether the issue is "execution-ready" (sufficiently specified to implement without human confirmation):

  An issue is **execution-ready** only when ALL of the following are true:
  1. **Has `## Acceptance Criteria`** with `- [ ]` checklist items (explicit, verifiable criteria)
  2. **Has `## Blocked by`** section (dependency context is documented)
  3. **Has `## Parent` or references a parent issue/PRD** (upstream design context exists — this is the strongest signal of `pd-to-issues` origin; hand-written issues rarely include this)
  4. **A PRD or RAD exists in the same feature directory** (`.scratch/<feature>/PRD.md` or `RAD.md`) — confirms this issue came from a structured design workflow
  5. **No open questions or "TBD" / "待确认" markers** in the issue body — everything is already decided

  - **If ALL 5 conditions are met** → **execution-ready**: skip confirmation and proceed directly to implementation. The issue has already been grilled and approved during the design phase.
  - **If ANY condition is missing** → **needs confirmation**: report your findings and wait for the user to confirm the approach before coding.

**g. Update marker → Step: implementing** — before writing code, update the `## In Progress` section:

```markdown
## In Progress

- **Started**: YYYY-MM-DD HH:MM
- **Step**: implementing
- **Notes**: Approach confirmed, beginning implementation
```

**h. Implement** — write the code, following the project's development principles (KISS, SOLID, single responsibility, minimal change scope).

**i. Update marker → Step: verifying** — before verification, update the `## In Progress` section:

```markdown
## In Progress

- **Started**: YYYY-MM-DD HH:MM
- **Step**: verifying
- **Notes**: Implementation complete, running verification
```

**j. Verify acceptance criteria** — after implementation, verify each criterion:
  - For code behavior: run the relevant commands/tests
  - For API endpoints: curl the endpoint
  - For UI: use browser tools or manual verification
  - For format/structure: grep the codebase

**k. Mark as completed** — append a completion section to the issue file, then **remove the `## In Progress` section**:

```markdown
## Completed

- **Date**: YYYY-MM-DD
- **Verification**:
  - [x] Criterion 1 — verified via `curl ...` / code inspection / browser
  - [x] Criterion 2 — verified via ...
- **Notes**: Any deviations from original plan or important decisions made
```

Also convert all remaining `- [ ]` acceptance criteria to `- [x]` in the original section.

**l. Remove `## In Progress` marker** — delete the `## In Progress` section from the issue file. The issue now has a clean `## Completed` section as the final state.

**m. Move to next issue** — repeat until all incomplete issues are done.

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
- **Show the plan before coding** — especially for the first issue or unstructured issues, so the user can redirect if your understanding is wrong. For structured issues generated by `pd-to-issues`, the plan has already been vetted; proceed directly to implementation.
- **Respect existing code** — don't rewrite working code just because your approach differs
- **One issue at a time** — complete and verify one before starting the next
- **If stuck, ask** — if an acceptance criteria is ambiguous or can't be satisfied, flag it to the user rather than making assumptions

## Edge cases

- **No incomplete issues**: Tell the user all issues are already completed.
- **Blocked by unimplemented issue**: Skip until the blocker is done (the topological sort should handle this).
- **Issue references files that don't exist**: The issue may be outdated — flag this to the user before deciding whether to execute or skip.
- **Multiple feature directories**: If `.scratch/` has multiple `<feature-slug>/issues/` directories, process them one feature at a time — ask the user which feature to focus on first.
