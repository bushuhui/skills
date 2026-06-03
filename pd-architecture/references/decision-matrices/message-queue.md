# Message Queue Selection

## Queue Technology Comparison

| Feature | RabbitMQ | Kafka | SQS | Redis Streams |
|---------|----------|-------|-----|---------------|
| Throughput | Medium (10K/s) | Very High (100K+/s) | Medium | High |
| Ordering | Per-queue | Per-partition | FIFO optional | Per-stream |
| Durability | Configurable | Strong | Strong | Configurable |
| Replay | No | Yes | No | Yes |
| Complexity | Medium | High | Low | Low |

## Decision Matrix

| Requirement | Recommendation |
|-------------|----------------|
| Simple task queue | SQS or Redis |
| Event streaming | Kafka |
| Complex routing | RabbitMQ |
| Log aggregation | Kafka |
| Serverless integration | SQS |
| Real-time analytics | Kafka |
| Request/reply pattern | RabbitMQ |

## When to Use Each

**RabbitMQ:** Complex routing (topic, fanout, headers), request/reply, priority queues.

**Kafka:** Event sourcing, high throughput (>50K msg/sec), message replay, stream processing.

**SQS:** AWS-native, simple queue semantics, serverless, no infrastructure management.

**Redis Streams:** Already using Redis, moderate throughput, simple streaming needs.
