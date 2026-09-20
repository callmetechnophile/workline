# Workline Target Web Platform Architecture

**Document ID:** `WORKLINE-AWS-02`  
**Status:** CANONICAL TARGET ARCHITECTURE  

---

## 1. System Vision & Architecture Principles

Workline is rearchitected as a resilient, enterprise-grade, AWS-native web platform. The design guarantees:
- **Zero Database Replacement:** SurrealDB and Qdrant remain the authoritative structured and vector data platforms.
- **Strict Private Isolation:** Databases and internal microservices are located in private isolated subnets. The browser **NEVER** connects directly to SurrealDB or Qdrant.
- **Asynchronous Agent Compute:** Heavy engineering tasks (PINN thermal simulation, multi-vendor procurement search, CAD analysis) execute asynchronously via SQS and ECS Fargate worker pools.
- **Control Fabric as Orchestrator:** All inter-agent communication, workflow state transitions, and task dispatches are mediated strictly by the Workline Control Fabric.

---

## 2. Canonical Target Architecture Diagram

```
                    INTERNET
                       │
                    Route53
                       │
                      WAF
                       │
                  CloudFront
                    /      \
                   /        \
                  ▼          ▼
             Web Frontend   API
             (S3/Amplify)    │
                             ▼
                        API Gateway /
                            ALB
                             │
                             ▼
                        ECS/Fargate
                             │
                      CONTROL FABRIC
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
          AGENTS           JOBS             EVENTS
            │             (SQS)          (EventBridge)
      ┌─────┼───────────────┐
      │     │               │
      ▼     ▼               ▼
 SURREALDB QDRANT          S3
  (State)  (Vectors)   (Artifacts)
      │     │
      │     │
      └─────┴───────────────┐
                            ▼
                      LLM GATEWAY
                      /          \
                     ▼            ▼
                 BEDROCK       NVIDIA NIM
                  PRIMARY        FALLBACK
```

---

## 3. Supporting AWS Platform Services

The core architecture is supported and hardened by:
- **Amazon Cognito:** User Pools with OAuth2/OIDC, JWT issuance, and RBAC token claims.
- **AWS IAM:** Least-privilege Task Roles for ECS tasks (no hardcoded IAM access keys).
- **AWS KMS:** Envelope encryption for S3 artifacts, database volumes, and parameter secrets.
- **AWS Secrets Manager:** Centralized secret storage for SurrealDB credentials, Qdrant API keys, and vendor API tokens.
- **Amazon CloudWatch & AWS X-Ray:** Structured JSON logging, OpenTelemetry distributed tracing, metrics, and health alarms.
- **Amazon ECR:** Secure container image registry for API and Worker images.

---

## 4. Tier Responsibilities & Separation of Concerns

### Tier 1: Edge & Ingress (Route 53, AWS WAF, CloudFront)
- DNS resolution with automated health checks.
- WAF Layer 7 inspection defending against SQL/SurrealQL injection, XSS, and rate limiting.
- CloudFront CDN routes `/api/*` and `/events/*` to ALB, and serves static Next.js frontend assets from Amazon S3.

### Tier 2: Presentation (Next.js Web Frontend)
- Modern engineering portal (React 19, Tailwind CSS v4, Three.js 3D CAD visualization).
- Communicates exclusively with the Workline API/BFF via HTTPS Bearer tokens.
- **NEVER connects directly to SurrealDB, Qdrant, or internal message queues.**
- Consumes real-time agent execution progress via Server-Sent Events (SSE).

### Tier 3: API & BFF Gateway (FastAPI on ECS Fargate)
- Consolidated single-entrypoint REST API on ECS Fargate behind an Application Load Balancer.
- Validates Cognito JWTs (RS256) and enforces project/team RBAC policies.
- Integrates the **Workline Control Fabric** to coordinate workflows, query SurrealDB for state, and query Qdrant for semantic search.
- Offloads heavy agent execution to SQS queues.
- Generates pre-signed S3 URLs for large binary uploads (CAD STEP, Gerber, simulation inputs).

### Tier 4: Asynchronous Worker Pool (ECS Fargate Workers)
- Horizontally scalable ECS Fargate tasks running in private subnets.
- Consumes tasks from Amazon SQS with exponential backoff and Dead Letter Queue (DLQ).
- Executes 27 specialized engineering agents within isolated runtime contexts.
- Updates task execution state, findings, and graph relationships in SurrealDB.
- Stores output binaries (plots, Gerber archives, 3D meshes) in S3.

### Tier 5: Authoritative Data & Vector Layer
- **SurrealDB (KEPT — Authoritative State):** Owns all projects, users, teams, workflows, tasks, milestones, requirements, findings, decisions, BOM items, and graph relationships.
- **Qdrant (KEPT — Authoritative Vector Retrieval):** Owns all document embeddings, component vectors, and semantic search indexes.
- **Amazon S3 (Artifacts Storage):** Dedicated object store for heavy binary files (STEP, Gerber, thermal logs, DB backup dumps). S3 does NOT replace SurrealDB or Qdrant.
- **Amazon ElastiCache Redis:** Ephemeral cache for session tokens and real-time SSE pub/sub streaming. Redis does NOT store authoritative application state.

### Tier 6: Centralized LLM Gateway
- Central unified model routing layer used by all 27 agents.
- Primary: **Amazon Bedrock** (Claude 3.5 Sonnet for reasoning/synthesis, Claude 3.5 Haiku for classification, Titan for embeddings).
- Fallback: **NVIDIA NIM** (strictly for text completion; never for image/CAD tasks).
- Enforces Bedrock Guardrails for safety, PII redaction, and prompt injection filtering.
