# API Design Patterns — Nano

Resources: plural nouns, lowercase, kebab-case. No verbs in URLs. Semantic HTTP methods and status codes (not 200 for everything). Schema validation on input. Standard error envelope with code+message. Pagination on all lists (cursor for large, offset for small). Auth required unless explicitly public. Rate limiting with headers. URL path versioning, max 2 active versions. CORS never `*` with credentials. Non-breaking changes free, breaking changes require new version.
