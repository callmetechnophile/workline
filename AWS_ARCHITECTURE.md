# AWS Architecture: WorkflowGuide AI / ArmourFlow AI

## System Topology & Architecture Diagram

```
                                      ENGINEER / WEB CLIENT
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │   Amazon CloudFront   │
                                    │    (Global Edge CDN)  │
                                    └───────────┬───────────┘
                                                │
                         ┌──────────────────────┴──────────────────────┐
                         │                                             │
                         ▼                                             ▼
             ┌────────────────────────┐                   ┌────────────────────────┐
             │ Next.js Frontend (S3)  │                   │   Amazon API Gateway   │
             │   Static Assets & UI   │                   │ (REST / HTTP Gateway)  │
             └────────────────────────┘                   └────────────┬───────────┘
                                                                       │
                                                       ┌───────────────┴───────────────┐
                                                       │                               │
                                                       ▼                               ▼
                                            ┌─────────────────────┐         ┌─────────────────────┐
                                            │ AWS Lambda (Mangum) │         │ AWS Step Functions  │
                                            │ FastAPI Stateless   │         │ Multi-Agent State   │
                                            │  API Microservices  │         │ Machine Orchestrator│
                                            └──────────┬──────────┘         └──────────┬──────────┘
                                                       │                               │
                      ┌────────────────────────────────┼───────────────────────────────┤
                      │                                │                               │
                      ▼                                ▼                               ▼
           ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
           │      Amazon SQS      │        │  Amazon EventBridge  │        │      Amazon SNS      │
           │ Asynchronous Workers │        │  Domain Event Bus    │        │  Critical Alert      │
           │ & Dead Letter Queue  │        │ (Project/BOM Events) │        │  Fan-out Topics      │
           └──────────────────────┘        └──────────────────────┘        └──────────────────────┘
                      │
                      ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                           DATA TIER                                             │
 │                                                                                                 │
 │       ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐   ┌────────────────┐ │
 │       │    SurrealDB     │    │      Qdrant      │    │ Amazon DynamoDB  │   │   Amazon S3    │ │
 │       │  Authoritative   │    │  Authoritative   │    │  AWS Application │   │  SSE-KMS Asset │ │
 │       │ Engineering Graph│    │  Vector Database │    │  Metadata & Locks│   │ & Artifacts    │ │
 │       └──────────────────┘    └──────────────────┘    └──────────────────┘   └────────────────┘ │
 │                                                                                                 │
 │                           ┌───────────────────────────────────┐                                 │
 │                           │    Amazon OpenSearch Service      │                                 │
 │                           │ Full-Text Search & Document Index │                                 │
 │                           └───────────────────────────────────┘                                 │
 └─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                       │
                      ┌────────────────────────────────┼───────────────────────────────┐
                      │                                │                               │
                      ▼                                ▼                               ▼
           ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
           │    Amazon Bedrock    │        │  ArmorIQ Governance  │        │   Amazon Cognito     │
           │  Claude 3.5 Sonnet   │        │ Cryptographic HMAC   │        │ User Authentication  │
           │  Titan Embeddings    │        │ Receipts & Policies  │        │   & RBAC JWT (RS256) │
           └──────────────────────┘        └──────────────────────┘        └──────────────────────┘
```

---

## Component Mapping & Architectural Responsibilities

1. **Edge & Frontend Delivery:**
   - **Amazon CloudFront**: Caches and serves Next.js frontend assets with SSL/TLS termination, sub-second latency, and DDoS protection via AWS Shield Standard.
   - **Next.js Web Client**: Unchanged user interface providing BOM inspection, real-time Pareto charts, thermal risk visualizations, and team collaboration.

2. **API & Execution Compute:**
   - **Amazon API Gateway**: Directs incoming requests to AWS Lambda functions with CORS, throttling, and request validation.
   - **AWS Lambda (Mangum ASGI Adapter)**: Executes the stateless FastAPI backend endpoints (`/api/auth/*`, `/api/projects/*`, `/api/bom/*`, `/api/datasheets/*`, `/api/graph/*`, etc.).
   - **AWS Step Functions**: Coordinates multi-agent lifecycle workflows (Planner -> Research -> Extraction -> BOM -> Optimization -> Validation -> Simulation -> Report) with automated retries, parallel branches, and error capture.

3. **Asynchronous Compute & Messaging:**
   - **Amazon SQS + DLQ**: Handles heavy, asynchronous jobs (e.g., deep research document synthesis, high-resolution thermal matrix simulations, large export packages) with dead-letter queue isolation.
   - **Amazon EventBridge**: Routes business and agent lifecycle events (`ProjectCreated`, `ResearchCompleted`, `BOMOptimized`, `PolicyViolation`) across the platform.
   - **Amazon SNS**: Fan-out notification topics for high-priority security policy alerts and critical validation warnings.

4. **Multi-Model Data Platform (Invariants Strictly Preserved):**
   - **SurrealDB**: Authoritative engineering graph database storing component connections, sub-circuit hierarchies, multi-agent hypotheses, and Pareto frontiers.
   - **Qdrant**: Authoritative approximate nearest neighbor (ANN) vector database for hardware parts, research paper chunks, and design similarity.
   - **Amazon DynamoDB**: Fast serverless metadata storage for API idempotency locks, background job states, and user preferences.
   - **Amazon S3**: Secure object store for research PDFs, raw datasheets, generated CAD/PCB exports, and CSV BOM snapshots with SSE-KMS encryption.
   - **Amazon OpenSearch Service**: Full-text indexing layer for fuzzy and keyword search across datasheets, technical specifications, and research literature.

5. **AI, Governance & Security:**
   - **Amazon Bedrock**: Primary foundational LLM gateway (Anthropic Claude 3.5 Sonnet, Claude 3.5 Haiku, Amazon Titan Embeddings, Nova Canvas).
   - **ArmorIQ SDK**: Cryptographic policy enforcement and audit trails. Every agent delegation generates an HMAC-signed receipt (`capture_plan`, `delegate`, `invoke_tool`), with violations dispatched to EventBridge and CloudWatch.
   - **Amazon Cognito**: User authentication, password reset, and RS256 JWKS JWT verification with fine-grained RBAC roles.
   - **Amazon CloudWatch**: Centralized observability, EMF metrics, latency alarms, and security violation dashboards.
