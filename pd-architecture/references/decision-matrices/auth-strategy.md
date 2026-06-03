# Authentication Strategy

## Method Selection

| Method | Best For | Avoid When |
|--------|----------|------------|
| Session-based | Traditional web apps, server-rendered | Mobile apps, microservices |
| JWT | SPAs, mobile apps, microservices | Need immediate revocation |
| OAuth 2.0 | Third-party access, social login | Internal-only apps |
| API Keys | Server-to-server, simple auth | User authentication |
| mTLS | Service mesh, high security | Public APIs |

## JWT vs Sessions

| Factor | JWT | Sessions |
|--------|-----|----------|
| Scalability | Stateless, easy to scale | Requires session store |
| Revocation | Difficult (need blocklist) | Immediate |
| Payload | Can contain claims | Server-side only |
| Security | Token in client | Server-controlled |

## OAuth 2.0 Flow Selection

| Flow | Use Case |
|------|----------|
| Authorization Code | Web apps with backend |
| Authorization Code + PKCE | SPAs, mobile apps |
| Client Credentials | Machine-to-machine |
| Device Code | Smart TVs, CLI tools |

**Avoid:** Implicit flow (deprecated), Resource Owner Password (legacy only)

## Token Lifetimes

| Token Type | Suggested Lifetime |
|------------|-------------------|
| Access token | 15-60 minutes |
| Refresh token | 7-30 days |
| API key | No expiry (rotate quarterly) |
| Session | 24 hours - 7 days |
