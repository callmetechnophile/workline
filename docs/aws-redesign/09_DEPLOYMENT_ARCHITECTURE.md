# Workline Deployment Architecture, Docker & Infrastructure as Code

**Document ID:** `WORKLINE-AWS-09`  
**Status:** CANONICAL DEPLOYMENT SPECIFICATION  

---

## 1. Container Strategy & Multi-Stage Dockerfiles

Workline is deployed as a suite of hardened, lightweight OCI-compliant container images:

1. **`Dockerfile.api` (Workline FastAPI API / BFF Gateway):**
   - Base: `python:3.11-slim-bookworm`
   - Role: Handles HTTP ingress, Cognito auth validation, Control Fabric dispatch, and SSE streaming.
   - Size: < 220 MB.
2. **`Dockerfile.worker` (Agent Compute Worker):**
   - Base: `python:3.11-slim-bookworm`
   - Role: Heavy compute worker pool containing PyTorch, PINN dependencies, CAD geometry parsers, and 27 agents.
   - Scales horizontally based on SQS queue depth (`ApproximateNumberOfMessagesVisible`).
3. **`Dockerfile.surrealdb` (Authoritative State DB):**
   - Official image: `surrealdb/surrealdb:v2.0` (or latest).
   - Deployed with persistent volume mount (`/var/lib/surrealdb/data`).
4. **`Dockerfile.qdrant` (Authoritative Vector Search Engine):**
   - Official image: `qdrant/qdrant:v1.11.0`.
   - Deployed with persistent volume mount (`/qdrant/storage`).

---

## 2. Local Stack Orchestration (`docker-compose.yml`)

For local development and testing, developers run the identical architecture via `docker-compose.yml`:

```yaml
version: '3.8'

services:
  surrealdb:
    image: surrealdb/surrealdb:v2.0.4
    container_name: workline-surrealdb
    command: start --bind 0.0.0.0:8000 --user root --pass root file:/data/workline.db
    ports:
      - "8001:8000"
    volumes:
      - surreal_data:/data
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:v1.11.0
    container_name: workline-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: workline-redis
    ports:
      - "6379:6379"

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - SURREALDB_URL=ws://surrealdb:8000/rpc
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - surrealdb
      - qdrant
      - redis

volumes:
  surreal_data:
  qdrant_data:
```

---

## 3. Terraform Infrastructure as Code (IaC) Modules

Infrastructure is defined declaratively under `infrastructure/terraform/`:
- `modules/vpc`: Multi-AZ VPC, subnets, NAT Gateways, route tables, and VPC Endpoints.
- `modules/security`: Security groups, IAM Task Roles, KMS Customer Managed Keys.
- `modules/surrealdb`: ECS task definition / EC2 instance with persistent EBS gp3 volume, internal NLB, and backup cron.
- `modules/qdrant`: ECS task definition with persistent EBS gp3 volume and snapshot automation.
- `modules/ecs`: ECS Cluster, API service (ALB target), Worker service (SQS auto-scaling).
- `modules/sqs`: Standard task queue, FIFO queues, and Dead Letter Queues (DLQ).
- `modules/s3`: Artifact bucket with SSE-KMS, versioning, and lifecycle rules.
- `modules/cognito`: User Pool, App Client, and RBAC resource server.
- `modules/edge`: CloudFront distribution, AWS WAF ACL, and Route 53 records.
