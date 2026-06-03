# pd-architecture

Interactive architecture design skill — from requirements gathering to pattern recommendation, tech stack selection, and ADR generation.

## Structure

```
pd-architecture/
├── SKILL.md                          # Main instructions + interactive workflow
├── README.md                         # This file — reference materials index
├── references/
│   ├── patterns/                     # 9 architecture patterns (language-agnostic)
│   ├── decision-matrices/            # 5 technology decision guides
│   └── workflows/                    # 5 common design workflows
├── languages/
│   ├── python/                       # Python-specific architecture practices
│   └── javascript/                   # JavaScript-specific (skeleton, TBD)
├── scripts/                          # Utility tools
└── templates/                        # Output document templates
```

## Reference Materials

### Architecture Patterns (`references/patterns/`)

| File | Content |
|------|---------|
| `monolith.md` | Traditional monolithic architecture — pros, cons, when to use |
| `modular-monolith.md` | Modular monolith with clear module boundaries — future extraction to services |
| `microservices.md` | Microservices architecture — independent deployment, scaling, technology choices |
| `event-driven.md` | Event-driven architecture — loose coupling, async processing, domain events |
| `cqrs.md` | Command Query Responsibility Segregation — separate read/write models |
| `event-sourcing.md` | Event sourcing — complete audit trail, state reconstruction from events |
| `hexagonal.md` | Hexagonal/Ports & Adapters — business logic isolation from external concerns |
| `clean-architecture.md` | Clean Architecture — dependency rules, framework independence |
| `api-gateway.md` | API Gateway pattern — single entry point, cross-cutting concerns |

### Decision Matrices (`references/decision-matrices/`)

| File | Content |
|------|---------|
| `database-selection.md` | SQL vs NoSQL, database type selection, decision flow |
| `cache-strategy.md` | Cache types (read-through, write-through, cache-aside), TTL guidelines |
| `message-queue.md` | RabbitMQ vs Kafka vs SQS vs Redis Streams comparison |
| `auth-strategy.md` | Session vs JWT vs OAuth2, token lifetimes, OAuth2 flows |
| `api-style-selection.md` | REST vs GraphQL vs gRPC, versioning strategies |

### Workflows (`references/workflows/`)

| File | Content |
|------|---------|
| `api-design.md` | REST API design — resources, CRUD mapping, error handling, pagination |
| `capacity-planning.md` | Infrastructure sizing — compute, storage, network calculations |
| `schema-design.md` | Database schema design — entities, relationships, indexes, partitioning |
| `migration-planning.md` | System migration strategies — blue-green, canary, strangler fig |
| `scalability-assessment.md` | Scalability evaluation — bottleneck identification, load testing, scaling plans |

### Python Language Layer (`languages/python/`)

| File | Content |
|------|---------|
| `architecture.md` | Functional core/imperative shell, DDD, layered architecture in Python |
| `data-modeling.md` | dataclasses vs Pydantic, entity transformations, validation patterns |
| `fastapi.md` | FastAPI project structure, dependency injection, error handling |
| `tech-stack.md` | Curated Python tech stack — frameworks, ORMs, queues, observability |
| `patterns/common-patterns.md` | Repository, service layer, event bus, circuit breaker, retry, CQRS, settings, logging |
| `checklist.md` | Python architecture review checklist — 8 dimensions |

### Scripts (`scripts/`)

| File | Content |
|------|---------|
| `architecture_diagram_generator.py` | Generate architecture diagrams (Mermaid, PlantUML, ASCII) from project structure |
| `dependency_analyzer.py` | Analyze project dependencies for coupling, circular dependencies, outdated packages |
| `project_architect.py` | Analyze project structure, detect architectural patterns, code smells |

### Templates (`templates/`)

| File | Content |
|------|---------|
| `architecture-decision-record.md` | ADR template — context, options, decision, rationale, trade-offs |
| `architecture-review-report.md` | Architecture review report template — findings by dimension |
| `capacity-plan.md` | Capacity planning template — current state, projections, infrastructure |

## Reference Sources

This skill's content is derived from the following sources:

1. **Senior Architect Skill** (`senior-architect/`):
   - `references/architecture_patterns.md` → Split into `references/patterns/*.md` (9 files)
   - `references/tech_decision_guide.md` → Split into `references/decision-matrices/*.md` (5 files)
   - `references/system_design_workflows.md` → Split into `references/workflows/*.md` (5 files)
   - `scripts/` → Migrated to `scripts/`

2. **Python Architecture Skill** (`python-architecture/`):
   - `SKILL.md` + `references/functional-core.md` → Merged into `languages/python/architecture.md`
   - `references/ddd.md` → Merged into `languages/python/architecture.md`
   - `references/data-modeling.md` → `languages/python/data-modeling.md`

3. **Python FastAPI Skill** (`python-fastapi/`):
   - `SKILL.md` + `references/` (api-design, dependencies, middleware, validation) → `languages/python/fastapi.md`

4. **Python Architecture Review Skill** (`python-architecture-review/`):
   - `architecture-checklist.md` → `languages/python/checklist.md`
   - `common-patterns.md` → `languages/python/patterns/common-patterns.md`
   - `technology-recommendations.md` → `languages/python/tech-stack.md`

5. **Senior Backend Skill** (`senior-backend/`):
   - `references/forcing_questions.md` → Inspired the 6 forcing questions in SKILL.md
   - `scripts/` → Evaluated; useful ones migrated to `scripts/`

## License

Content derived from open-source architecture pattern references and industry best practices.
