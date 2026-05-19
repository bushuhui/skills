# Icon & Brand Color Reference

When diagrams mention specific products, use these brand colors as fillColor/strokeColor pairs in draw.io style strings.

## AI / ML Products

| Product | fillColor | strokeColor | Badge Text |
|---------|-----------|-------------|-----------|
| OpenAI / ChatGPT | #ffffff | #10A37F | OAI |
| Anthropic / Claude | #ffffff | #D97757 | Claude |
| Google Gemini | #ffffff | #4285F4 | Gemini |
| Meta LLaMA | #ffffff | #0467DF | LLaMA |
| Mistral | #ffffff | #FF7000 | Mistral |
| Cohere | #ffffff | #39594D | Cohere |
| Groq | #ffffff | #F55036 | Groq |
| Together AI | #ffffff | #6366F1 | Together |
| Hugging Face | #FFD21E | #1C1C1C | HF |

draw.io style for AI badge node:
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#10A37F;strokeWidth=2;arcSize=16;fontColor=#0d0d0d;fontSize=12;fontStyle=1;
```

## AI Memory & RAG Products

| Product | fillColor | strokeColor | Badge |
|---------|-----------|-------------|-------|
| Mem0 | #ffffff | #6366F1 | mem0 |
| LangChain | #ffffff | #1C3C3C | LC |
| LlamaIndex | #ffffff | #8B5CF6 | LI |
| LangGraph | #ffffff | #1C3C3C | LG |
| CrewAI | #ffffff | #EF4444 | Crew |
| AutoGen | #ffffff | #0078D4 | AG |
| DSPy | #ffffff | #7C3AED | DSPy |

## Vector Databases

| Product | fillColor | strokeColor | Badge |
|---------|-----------|-------------|-------|
| Pinecone | #1C1C2E | #00D68F | Pine |
| Weaviate | #ffffff | #FA0050 | Wea |
| Qdrant | #ffffff | #DC244C | Qdrant |
| Chroma | #ffffff | #FF6B35 | Chr |
| Milvus | #ffffff | #00A1EA | Milvus |
| pgvector | #ffffff | #336791 | pgv |

draw.io style for Vector DB cylinder:
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#1C1C2E;strokeColor=#00D68F;fontColor=#ffffff;fontSize=12;fontStyle=1;
```

## Classic Databases & Storage

| Product | fillColor | strokeColor |
|---------|-----------|-------------|
| PostgreSQL | #ffffff | #336791 |
| MySQL | #ffffff | #4479A1 |
| MongoDB | #ffffff | #47A248 |
| Redis | #ffffff | #DC382D |
| Elasticsearch | #ffffff | #005571 |
| Neo4j | #ffffff | #008CC1 |
| SQLite | #ffffff | #003B57 |

## Message Queues & Streaming

| Product | fillColor | strokeColor |
|---------|-----------|-------------|
| Apache Kafka | #ffffff | #231F20 |
| RabbitMQ | #ffffff | #FF6600 |
| AWS SQS | #ffffff | #FF9900 |
| NATS | #ffffff | #27AAE1 |

## Cloud & Infrastructure

| Product | fillColor | strokeColor |
|---------|-----------|-------------|
| AWS | #ffffff | #FF9900 |
| GCP | #ffffff | #4285F4 |
| Azure | #ffffff | #0089D6 |
| Cloudflare | #ffffff | #F48120 |
| Vercel | #ffffff | #000000 |
| Docker | #ffffff | #2496ED |
| Kubernetes | #ffffff | #326CE5 |
| Terraform | #ffffff | #7B42BC |
| Nginx | #ffffff | #009639 |
| FastAPI | #ffffff | #009688 |

## Observability

| Product | fillColor | strokeColor |
|---------|-----------|-------------|
| Grafana | #ffffff | #F46800 |
| Prometheus | #ffffff | #E6522C |
| Datadog | #ffffff | #632CA6 |
| LangSmith | #ffffff | #1C3C3C |
| Langfuse | #ffffff | #6366F1 |

## Azure Services

Azure brand color: `#0089D6`. Use `shape=mxgraph.azure.resourceIcon;mxgraph.azure.resourceIcon.icons=TYPE;` for native Azure stencils, or use brand colors with `rounded=1;` for simpler nodes.

### Azure Compute

| Service | strokeColor | Badge | shape= value |
|---------|-------------|-------|-------------|
| Azure Functions | #0062AD | Func | `mxgraph.azure.resourceIcon;mxgraph.azure.resourceIcon.icons=functions;` |
| Azure App Service | #0072C6 | App | `mxgraph.azure.resourceIcon;mxgraph.azure.resourceIcon.icons=app_services;` |
| Azure Container Apps | #3F8624 | ACA | `rounded=1;` with green |
| AKS | #326CE5 | AKS | `mxgraph.azure.resourceIcon;mxgraph.azure.resourceIcon.icons=kubernetes_services;` |
| Azure VMs | #0078D4 | VM | `mxgraph.azure.resourceIcon;mxgraph.azure.resourceIcon.icons=virtual_machines;` |

### Azure Data

| Service | strokeColor | Badge | shape= value |
|---------|-------------|-------|-------------|
| Azure SQL | #0066A1 | SQL | `shape=cylinder3;` with SQL blue |
| Cosmos DB | #3D7AB3 | Cosmos | `shape=cylinder3;` with Cosmos blue |
| PostgreSQL | #336791 | pg | `shape=cylinder3;` with PG blue |
| Redis Cache | #DC382D | Redis | `shape=cylinder3;` with Redis red |
| Synapse | #0078D4 | Syn | `rounded=1;` |
| Databricks | #FF3621 | Bricks | `rounded=1;` with DB red |

### Azure AI

| Service | strokeColor | Badge | shape= value |
|---------|-------------|-------|-------------|
| Azure OpenAI | #10A37F | AOAI | `rounded=1;double=1;` with green |
| AI Search | #0078D4 | AISrch | `rounded=1;` |
| AI Foundry | #742774 | Foundry | `rounded=1;` with purple |
| Azure ML | #0078D4 | AML | `rounded=1;` |

### Azure Networking

| Service | strokeColor | Badge |
|---------|-------------|-------|
| Front Door | #0078D4 | AFD |
| App Gateway | #0078D4 | AppGW |
| Load Balancer | #0078D4 | LB |
| API Management | #1FBA9F | APIM |
| VNet | #0078D4 | VNet |

### Azure Security

| Service | strokeColor | Badge |
|---------|-------------|-------|
| Entra ID (Azure AD) | #0072C6 | Entra |
| Key Vault | #FFB900 | KV |

### Azure Container Style

For Azure region/subscription boundaries:
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#0089D6;fillOpacity=4;strokeColor=#0089D4;dashed=1;dashPattern=6 4;fontColor=#0089D6;fontSize=10;fontStyle=1;
```

## GCP Services

GCP brand color: `#4285F4`.

| Service | strokeColor | Badge |
|---------|-------------|-------|
| Cloud Run | #4285F4 | Run |
| Cloud Functions | #4285F4 | CF |
| GKE | #326CE5 | GKE |
| BigQuery | #4285F4 | BQ |
| Cloud SQL | #4285F4 | SQL |
| Firestore | #4285F4 | FS |
| Pub/Sub | #4285F4 | PubSub |
| Cloud Storage | #4285F4 | GCS |
| Vertex AI | #4285F4 | VAI |
| Cloud CDN | #4285F4 | CDN |
| Cloud Load Balancing | #4285F4 | LB |

## AWS Services

AWS brand color: `#FF9900`. Use `shape=mxgraph.aws4.resourceIcon;mxgraph.aws4.resourceIcon.icons=TYPE;` for native AWS stencils.

| Service | strokeColor | Badge | shape= icons value |
|---------|-------------|-------|-------------------|
| Lambda | #FF9900 | Lambda | `lambda_function` |
| EC2 | #FF9900 | EC2 | `ec2_instance` |
| S3 | #FF9900 | S3 | `s3_bucket` |
| RDS | #FF9900 | RDS | `rds_instance` |
| DynamoDB | #FF9900 | DDB | `dynamodb_table` |
| API Gateway | #FF9900 | APIGW | `api_gateway` |
| SQS | #FF9900 | SQS | `sqs_queue` |
| SNS | #FF9900 | SNS | `sns_topic` |
| CloudFront | #FF9900 | CF | `cloudfront` |
| ECS | #FF9900 | ECS | `ecs` |
| EKS | #FF9900 | EKS | `eks` |
| VPC | #FF9900 | VPC | `vpc` |
| CloudWatch | #FF9900 | CW | `cloudwatch` |
| IAM | #FF9900 | IAM | `iam_role` |
| Route 53 | #FF9900 | R53 | `route53` |

draw.io style for AWS service node:
```
shape=mxgraph.aws4.resourceIcon;mxgraph.aws4.resourceIcon.icons=lambda_function;whiteSpace=wrap;html=1;
```

## Usage Pattern

For any product, create a node with the brand color as strokeColor:
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=BRAND_COLOR;strokeWidth=2;arcSize=16;fontColor=#0d0d0d;fontSize=14;fontStyle=1;
```

For dark styles (2, 3, 5), swap fillColor to a dark tint:
```
rounded=1;whiteSpace=wrap;html=1;fillColor=BRAND_DARK_TINT;strokeColor=BRAND_COLOR;arcSize=12;fontColor=#e2e8f0;fontSize=13;
```
