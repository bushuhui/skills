# Microservices Architecture

**Problem:** Need independent deployment, scaling, and technology choices for different parts of the system.

**When to use:**
- Large team (15+ developers) organized around business capabilities
- Different parts need different scaling
- Independent deployment is critical
- Technology diversity is beneficial

**When NOT to use:**
- Small team that can't handle operational complexity
- Domain boundaries are unclear
- Distributed transactions are common requirement
- Network latency is unacceptable

**Trade-offs:**

| Pros | Cons |
|------|------|
| Independent deployment | Network complexity |
| Independent scaling | Distributed system challenges |
| Technology flexibility | Operational overhead |
| Team autonomy | Data consistency challenges |
| Fault isolation | Testing complexity |

**Structure:**
```
microservices/
├── services/
│   ├── user-service/
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── order-service/
│   └── payment-service/
├── api-gateway/
├── infrastructure/
│   ├── kubernetes/
│   └── terraform/
└── docker-compose.yml
```

**Communication patterns:**
- Synchronous: REST, gRPC
- Asynchronous: Message queues (RabbitMQ, Kafka)
