# API Design Workflow

## Step 1: Identify Resources

List the nouns in your domain:
```
E-commerce example:
- Users
- Products
- Orders
- Payments
- Reviews
```

## Step 2: Define Operations

Map CRUD to HTTP methods:

| Operation | HTTP Method | URL Pattern |
|-----------|-------------|-------------|
| List | GET | /resources |
| Get one | GET | /resources/{id} |
| Create | POST | /resources |
| Update | PUT/PATCH | /resources/{id} |
| Delete | DELETE | /resources/{id} |

## Step 3: Design Request/Response Formats

**Request:**
```json
POST /api/v1/orders
{
  "customer_id": "cust-123",
  "items": [{"product_id": "prod-456", "quantity": 2}],
  "shipping_address": {"street": "123 Main St", "city": "SF", "state": "CA", "zip": "94102"}
}
```

**Response:**
```json
{
  "id": "ord-789",
  "status": "pending",
  "customer_id": "cust-123",
  "items": [...],
  "total": 99.99,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Step 4: Handle Errors Consistently

**Error format (RFC 7807):**
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Invalid request parameters",
  "errors": [{"field": "quantity", "message": "must be greater than 0"}]
}
```

## Step 5: Document the API

Include: authentication method, base URL and versioning, endpoints with examples, error codes, rate limits, pagination format.

## Best Practices

1. Use standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
2. Plural resource names: `/users`, not `/user`
3. Consistent naming: lowercase, kebab-case for URLs
4. Appropriate status codes: 201 for creation, 204 for deletion
5. Structured errors (RFC 7807 Problem Details)
6. Always paginate list endpoints
7. Plan for API evolution (versioning)
8. Safe retry for mutations (idempotency keys)
