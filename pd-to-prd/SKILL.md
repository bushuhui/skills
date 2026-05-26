---
name: pd-to-prd
description: Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context.
---

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run `/pd-setup` if not.

## Process

1. Read `.scratch/<feature>/RAD.md` if it exists — it contains the outcomes of a prior brainstorming or grilling session. Use it as the primary source for the PRD rather than starting from scratch.

If no `.scratch/<feature>/RAD.md` exists for any feature, fall back to `docs/RAD.md` for backwards compatibility. If neither exists, synthesize from the current conversation context.

Map `.scratch/<feature>/RAD.md` sections to PRD fields:

| `.scratch/<feature>/RAD.md` section | → PRD section | How to transform |
|---|---|---|
| 需求分析 | Problem Statement & Solution | Synthesize into user-facing problem + solution |
| 架构与方案 | Implementation Decisions | Remove file paths/line numbers; keep interfaces, types, config shapes |
| 决策记录 | Implementation Decisions | Preserve decisions and rationale as-is |
| 待办事项 | User Stories / Out of Scope | Actionable items → user stories; blocked/deferred items → out of scope |
| 需要考虑的细节 | Further Notes | Direct mapping |

2. Resolve open items from RAD

After reading the RAD, inspect the `### 待办事项` section. Every item must fall into exactly one of these three categories BEFORE proceeding:

1. **Actionable** → Will be turned into User Stories or Implementation Decisions in the PRD
2. **Deferred / out of scope** → Will be moved to `## Out of Scope` in the PRD
3. **Unresolved / "待进一步分析" / TBD** → **MUST be resolved now.** Ask the user for the decision, record it in the PRD. Do NOT leave "待细化" or "TBD" markers in the PRD.

If any item cannot be resolved immediately, **STOP and do not generate the PRD.** Tell the user which items are blocking and what decisions are needed.

After resolving the open items, **synchronize the changes back to `RAD.md`**:
- For each resolved item, update its checklist status: `- [ ]` → `- [x]`
- Append a resolution note after the item, e.g. `→ 已确认：采用XX方案，写入 PRD Implementation Decisions` or `→ 已确认：归入 Out of Scope`
- If the item was reclassified (e.g. deferred), note the new classification
- Write the updated content back to `.scratch/<feature>/RAD.md` (overwrite in-place)

3. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.

4. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

5. Write the PRD using the template below.

6. Save the PRD to `.scratch/<feature>/PRD.md`:
   - If `.scratch/<feature>/` does not exist, create it
   - Write the full PRD content to `.scratch/<feature>/PRD.md` (overwrite if it already exists)
   - This file serves as the local canonical source of the PRD

7. Publish the PRD to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

Once the PRD is saved and published, guide the user to the next step:

- **If the PRD needs to be broken into independently-grabbable issues** → run `/pd-to-issues` (splits the PRD into vertical tracer-bullet slices, each a complete end-to-end issue that an AFK agent can pick up)
- **If key design decisions need validation before committing** → run `/pd-prototype` (builds a throwaway prototype to verify the riskiest assumptions)

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>
