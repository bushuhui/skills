# OBEY API Design Patterns

## When to use

Use when designing, reviewing, or versioning REST APIs. Covers resource naming, HTTP semantics, pagination, filtering, error responses, auth, rate limiting, and versioning.

## Primary bias to correct

APIs that "work" are not necessarily well-designed -- consistency, developer experience, and HTTP semantics matter for long-term maintainability.

## Decision rules

- Resources are nouns, plural, lowercase, kebab-case. URLs are not verbs. Use sub-resources for ownership.
- HTTP methods must be semantic: GET (read), POST (create), PUT (full replace), PATCH (partial), DELETE (remove).
- Status codes must be accurate: 200 for success, 201 for created (with Location), 204 for no-content deletes, 4xx for client errors, 5xx for server errors. Never 200 for errors.
- Input validation with schema libraries (Zod, Pydantic, Bean Validation). Reject early, return 400/422 with field-level details.
- Error responses consistent: `{"error": {"code": "...", "message": "...", "details": [...]}}`. Never expose stack traces or SQL errors.
- Pagination on all list endpoints. Cursor-based for feeds/large datasets; offset-based for admin dashboards/small data.
- Filtering via query params: equality, bracket notation for comparisons, comma-separated for multiple values. Sorting with `-` prefix for descending.
- Authentication required on all endpoints unless explicitly marked public. Authorization checked for resource ownership or role.
- Rate limiting configured with `X-RateLimit-*` headers. 429 on exceeded with `Retry-After`.
- URL path versioning (`/api/v1/`). Maintain at most 2 active versions. Deprecation requires 6-month notice + `Sunset` header.
- CORS origins environment-specific. Never `*` with credentials.
- Non-breaking changes don't need a new version (adding fields, optional params). Breaking changes do (removing/renaming fields, changing types).

## Trigger rules

- When a URL contains a verb (e.g., `/getUsers`), convert to resource noun.
- When singular resource names appear (e.g., `/user`), make plural.
- When snake_case appears in URLs, convert to kebab-case.
- When 200 is returned for errors or not-found, use proper 4xx/5xx status.
- When 200 is returned for creation, use 201 with Location header.
- When a list endpoint has no pagination, add cursor or offset pagination.
- When authentication is missing on a non-public endpoint, add it.
- When error responses leak internal details, redact and use standard error envelope.
- When a new field is added to a response, verify it's non-breaking; when removed, version the API.
- When CORS uses `*` with credentials, restrict to specific origins.

## Final checklist

- Resource URLs: plural nouns, kebab-case, no verbs?
- Correct HTTP method per operation?
- Appropriate status codes (not 200 for everything)?
- Input validated with schema before processing?
- Error responses follow standard format with codes?
- Pagination on all list endpoints?
- Authentication and authorization in place?
- Rate limiting configured?
- No internal details leaked (stack traces, SQL)?
- Consistent naming (camelCase vs snake_case) across endpoints?
- OpenAPI/Swagger spec updated?
