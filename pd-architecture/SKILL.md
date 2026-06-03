---
name: pd-architecture
description: |
  Interactive architecture design workflow — from requirements gathering to pattern recommendation, tech stack selection, and ADR generation. Use when designing system architecture, choosing between monolith vs microservices, planning scalability, selecting databases or caches, reviewing architecture documents, or generating architecture diagrams. Supports Python and JavaScript projects. Covers 9 architecture patterns, technology decision matrices, and structured design workflows.
---

# Architecture Design

Interactive architecture design: clarify requirements → recommend patterns → select tech → generate docs.

## Quick start

Run the full workflow:

```bash
python3 "${SKILL_DIR}/scripts/project_architect.py" ./project --verbose
```

Generate architecture diagrams:

```bash
python3 "${SKILL_DIR}/scripts/architecture_diagram_generator.py" ./project --format mermaid
```

## Interactive workflow

**Always follow these steps in order. Do not skip to recommendations without understanding requirements.**

### Step 1: Clarify requirements

Ask these six forcing questions, one per turn:

1. **Team size and timeline?** (determines complexity budget)
2. **Expected QPS and read/write ratio?** (drives DB, cache, queue choices)
3. **Data sensitivity tier?** — public / internal / PII / PHI / PCI
4. **Tenancy model?** — single-tenant / shared multi-tenant / isolated multi-tenant
5. **SLO + RPO/RTO?** (e.g., 99.9% uptime, RPO=1h, RTO=15min)
6. **Language/framework preference?** — Python / JavaScript / no preference

If any answer is unknown, walk the question. Don't guess.

### Step 2: Recommend architecture pattern

Based on answers, read `references/patterns/*.md` and recommend 1-2 patterns with trade-off analysis.

Quick heuristic:

| If | Recommend |
|---|---|
| Team < 10, low QPS | Modular Monolith |
| Team > 15, independent deploy needed | Microservices |
| Read/write > 10:1 | CQRS |
| Audit trail required | Event Sourcing |
| Multiple external systems | Hexagonal |
| Complex domain logic | Domain-Driven Design |

Explain why other patterns were NOT chosen.

### Step 3: Technology selection

Walk `references/decision-matrices/*.md` based on the project's language:

- **Python projects**: Load `languages/python/tech-stack.md` for framework, ORM, and tooling recommendations
- **JavaScript projects**: Apply the same decision matrices, adapt to Node.js ecosystem
- **No preference**: Recommend defaults from `references/decision-matrices/database-selection.md`

Each selection must include: primary choice, alternative, and why.

### Step 4: Generate output documents

Fill the appropriate template from `templates/`:

1. **ADR** — `templates/architecture-decision-record.md` with context, options, decision, trade-offs
2. **Architecture diagram** — call `scripts/architecture_diagram_generator.py` with the project path
3. **Capacity plan** — if scale questions weren't trivial, fill `templates/capacity-plan.md`

### Step 5: Architecture review (optional)

When the user provides an existing design for review:

1. Walk `languages/python/checklist.md` (or equivalent for their language)
2. For each review area: strengths → concerns (HIGH/MEDIUM/LOW) → recommendations
3. Fill `templates/architecture-review-report.md`
4. Output prioritized next steps

## Reference files

| File | Use when |
|------|----------|
| `references/patterns/*.md` | "which architecture?", "monolith vs microservices", "CQRS" |
| `references/decision-matrices/*.md` | "which database?", "which cache?", "which auth?" |
| `references/workflows/*.md` | "how to design API?", "capacity planning", "migration" |
| `languages/python/*.md` | Python-specific architecture, DDD, FastAPI, data modeling |
| `scripts/` | Generate diagrams, analyze dependencies, assess project |
| `templates/` | Output ADRs, review reports, capacity plans |
