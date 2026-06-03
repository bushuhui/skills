# Modular Monolith

**Problem:** Need monolith simplicity but with clear boundaries that enable future extraction to services.

**When to use:**
- Medium team (5-15 developers)
- Domain boundaries are becoming clearer
- Want option to extract services later
- Need better code organization than traditional monolith

**When NOT to use:**
- Already need independent deployment
- Teams can't coordinate releases

**Trade-offs:**

| Pros | Cons |
|------|------|
| Clear module boundaries | Still single deployment |
| Easier to extract services later | Requires discipline to maintain boundaries |
| Single database simplifies transactions | Can drift back to coupled monolith |
| Team ownership of modules | |

**Structure:**
```
modular-monolith/
├── modules/
│   ├── users/
│   │   ├── api/           # Public interface
│   │   ├── internal/      # Implementation
│   │   └── index.ts       # Module exports
│   ├── orders/
│   │   ├── api/
│   │   ├── internal/
│   │   └── index.ts
│   └── payments/
├── shared/                # Cross-cutting concerns
└── main.ts
```

**Key rule:** Modules communicate only through their public API, never by importing internal files.
