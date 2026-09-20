# Workline AWS Service Mapping & Component Evaluation

**Document ID:** `WORKLINE-AWS-03`  
**Status:** ARCHITECTURAL DECISION RECORD  

---

## 1. Comprehensive AWS Service Mapping Matrix

The table below provides the authoritative classification for every Workline component, mapping it to native AWS services while strictly preserving SurrealDB and Qdrant.

| Component / Subsystem | Existing Implementation | Classification | Target Architecture / AWS Mapping | Rationale & Tradeoffs |
| :--- | :--- | :---: | :--- | :--- |
| **Authoritative State Database** | `backend/workline/database/surrealdb.py` | **KEPT** | **SurrealDB on AWS** (Self-hosted on private ECS/EC2 with EBS gp3, or Surreal Cloud with VPC Peering) | **Authoritative Workline state & graph.** Multi-model graph, document, and relation capabilities natively fit Workline's engineering DAGs. **NOT REPLACED.** |
| **Authoritative Vector Engine** | `backend/workline/retrieval/qdrant.py` | **KEPT** | **Qdrant on AWS** (Self-hosted on private ECS/EC2 with EBS gp3, or Qdrant Cloud with VPC Peering) | **Authoritative vector retrieval.** High-performance HNSW vector search with rich payload filtering for engineering datasheets and components. **NOT REPLACED.** |
| **Binary Artifact Storage** | Local filesystem (`uploads/`, `exports/`) | **AWS-MANAGED** | **Amazon S3** with SSE-KMS and pre-signed URLs | Scalable object storage for heavy CAD STEP files, Gerber zips, thermal contour plots, and DB backups. Complements SurrealDB. |
| **Ephemeral Cache & Pub/Sub** | In-memory Python dictionaries | **AWS-MANAGED** | **Amazon ElastiCache Redis 7** | Sub-millisecond caching of hot session tokens and pub/sub message broker for SSE progress streaming. Never authoritative. |
| **Control Fabric** | `armourflow/fabric/fabric.py` | **KEEP & REFACTOR** | Embedded in FastAPI API/BFF and ECS Worker runtime | Authoritative orchestrator for agent lifecycle, task contracts, and capability routing. Stateless coordination. |
| **API Gateway / BFF** | `backend/main.py`, `backend/routes/` | **REFACTOR** | **FastAPI on AWS ECS Fargate** behind Application Load Balancer (ALB) | Consolidates all 50 routes into a single containerized service with auto-scaling, health checks, and connection pooling. |
| **Legacy Render Microservices** | `backend/r2` through `backend/r5` | **REMOVE** | Consolidated into unified domain services under `backend/app/` | Eliminates high-latency inter-service HTTP hops, redundant Dockerfiles, and duplicate data schemas. |
| **Asynchronous Job Queue** | `backend/workline/jobs/queue.py` | **REPLACE** | **Amazon SQS** (Standard & FIFO Queues) + Dead Letter Queue (DLQ) | Replaces fragile in-process in-memory queue with durable, distributed AWS message queues with at-least-once delivery. |
| **Domain Event Broker** | Ad-hoc internal callbacks | **AWS-MANAGED** | **Amazon EventBridge** | Serverless event bus for decoupled asynchronous event routing and audit event streaming. |
| **Agent Worker Runtime** | In-process execution in API container | **MOVE & SCALE** | **ECS Fargate Agent Worker Pool** | Auto-scaling worker tasks in private subnets, consuming from SQS, executing 27 agents in isolated memory spaces. |
| **Web Frontend** | `frontend/` (Next.js 16) | **KEEP & MOVE** | **Amazon CloudFront + S3** (or AWS Amplify Gen 2) | Fast global CDN delivery of compiled static assets, SSR API integration via CloudFront path routing. |
| **Identity & Authentication** | `backend/auth.py` (ad-hoc JWT validator) | **REPLACE** | **Amazon Cognito User Pools** | Enterprise identity management, RS256 token verification, OAuth2/OIDC, and RBAC claims. Replaces insecure fallback. |
| **LLM Gateway** | `backend/workline/llm/` | **REFACTOR** | **Amazon Bedrock** (Primary) + **NVIDIA NIM** (Fallback) | Centralized model routing to Claude 3.5 Sonnet/Haiku and Titan Embeddings with Bedrock Guardrails safety filtering. |
| **DNS & Edge Security** | Custom domain configuration | **AWS-MANAGED** | **Amazon Route 53 + AWS WAF** | Global DNS failover, DDoS protection, rate limiting, and Layer 7 WAF rules at the CloudFront distribution. |
| **Secrets & Keys Management** | Local `.env` files | **AWS-MANAGED** | **AWS Secrets Manager + AWS KMS** | Zero plaintext secrets in code or containers; automatic key rotation; customer-managed KMS keys. |
| **Observability & Tracing** | Ad-hoc Loguru console logs | **AWS-MANAGED** | **Amazon CloudWatch + AWS X-Ray + OpenTelemetry** | Unified structured JSON logging, distributed trace spans across API and workers, and metric alarm dashboards. |

---

## 2. Explicit Database Confirmation

To satisfy all architectural standards and non-negotiable platform constraints:

- **SURREALDB:** **KEPT — authoritative Workline state**. Owns users, projects, tasks, workflows, requirements, findings, decisions, BOMs, and graph relations.
- **QDRANT:** **KEPT — authoritative vector retrieval**. Owns all vector collections, embeddings, and semantic similarity search.

Neither database is marked REPLACED, DEPRECATED, MIGRATED, or OPTIONAL.
