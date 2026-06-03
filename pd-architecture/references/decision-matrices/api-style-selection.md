# API Style Selection

## REST vs GraphQL vs gRPC

| Factor | REST | GraphQL | gRPC |
|--------|------|---------|------|
| Use case | General purpose | Flexible queries | Microservices |
| Learning curve | Low | Medium | High |
| Over-fetching | Common | Solved | N/A |
| Caching | HTTP native | Complex | Custom |
| Browser support | Native | Native | Limited |
| Performance | Good | Good | Excellent |

## Decision Matrix

| Requirement | Recommendation |
|-------------|----------------|
| Public API | REST |
| Mobile apps with varied needs | GraphQL |
| Microservices communication | gRPC |
| Real-time updates | GraphQL subscriptions or WebSocket |
| File uploads | REST |
| Internal services only | gRPC |
| Third-party developers | REST + OpenAPI |

## Choose REST when:
- Building public APIs
- Need HTTP caching
- Simple CRUD operations
- Team experienced with REST

## Choose GraphQL when:
- Multiple clients with different data needs
- Rapid frontend iteration
- Complex, nested data relationships

## Choose gRPC when:
- Service-to-service communication
- Performance critical
- Streaming required
- Strong typing important

## API Versioning Strategies

| Strategy | Pros | Cons |
|----------|------|------|
| URL path (`/v1/`) | Clear, easy to implement | URL pollution |
| Query param (`?version=1`) | Flexible | Easy to miss |
| Header (`Accept-Version: 1`) | Clean URLs | Less discoverable |

**Recommendation:** URL path versioning for public APIs, header versioning for internal.
