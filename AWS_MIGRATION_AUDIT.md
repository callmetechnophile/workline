# AWS Migration Audit: WorkflowGuide AI / ArmourFlow AI

This document provides a comprehensive component audit and mapping of all external infrastructure, API, and cloud dependencies in the WorkflowGuide AI / ArmourFlow AI platform to approved AWS services.

## Core Architectural Invariants
1. **Authoritative Graph & State Database:** **SurrealDB** is preserved as the authoritative engineering knowledge and multi-agent relationship database.
2. **Authoritative Vector Engine:** **Qdrant** is preserved as the specialized high-dimensional vector search engine for hardware components, research embeddings, and BOM items.
3. **Cryptographic Security & Governance:** **ArmorIQ SDK** is strictly preserved for explicit delegation chains (`capture_plan()`, `delegate()`, `invoke()`), cryptographic HMAC receipts, and policy evaluation.
4. **Multi-Agent Interoperability:** **Google ADK**, **A2A (Agent-to-Agent)**, and **Bindu** interoperability protocols are wrapped and maintained alongside Amazon Bedrock inference.
5. **Zero Frontend Redesign:** The existing Next.js/React frontend retains all UI components, pages, state stores, and flows, interfacing via standardized API Gateway endpoints.

---

## Infrastructure & Service Audit Table

| Existing Component | Current Provider | Current Purpose | AWS Target | Migration Required | Keep / Replace | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend Application** | Vercel / Next.js static & SSR | Web UI for engineers, BOM view, thermal graph, 3D/canvas viewers | **Amazon CloudFront + S3 / Amplify Hosting** | Yes (Gradual DNS cutover) | Keep frontend code, migrate hosting target | Low |
| **Core API Gateway & HTTP Routing** | Render (R1 Core Gateway container) | HTTP REST, GraphQL, SSE streams, CORS, request routing | **Amazon API Gateway (HTTP/REST) + AWS Lambda (Mangum)** | Yes | Replace Render with API Gateway + Lambda / ECS Fargate fallback | Medium |
| **Long-Running Multi-Agent Orchestration** | In-process Python async orchestrator & Render background threads | Sequential and parallel execution of 27 engineering/research agents | **AWS Step Functions** | Yes | Wrap orchestrator with Step Functions State Machine (ASL) | Medium |
| **Asynchronous Background Task Processing** | In-memory `LocalJobQueue` / Render worker | Heavy workloads: deep research synthesis, PDF compilation, large BOM optimization | **Amazon SQS + DLQ (Dead Letter Queue)** | Yes | Replace in-memory with SQS, keep local fallback | Low |
| **Application & Domain Event Routing** | In-process pub/sub & callback handlers | Emitting state events (`ProjectCreated`, `BOMGenerated`, `PolicyViolation`) | **Amazon EventBridge (Custom Event Bus)** | Yes | Replace custom callback bus with EventBridge | Low |
| **Broadcast & Alert Fan-out** | Direct webhook / in-memory notifier | Critical alerts, validation failures, security policy violations, team invites | **Amazon SNS (Simple Notification Service)** | Yes | Add SNS topics for fan-out notifications | Low |
| **Artifact & Document Object Storage** | Local filesystem (`exports/`, `artifacts/`) / Render disk | Research PDFs, datasheets, generated CAD/PCB exports, BOM CSVs, reports | **Amazon S3 (SSE-KMS, Presigned URLs)** | Yes | Migrate storage to S3 with structured prefixes (`projects/{id}/...`) | Low |
| **AWS Application Metadata & Idempotency** | In-memory cache / SQLite `user_storage.db` | Job status, API idempotency locks, user preferences, workflow execution state | **Amazon DynamoDB** | Yes | Add DynamoDB metadata adapter, eliminate SQLite reliance | Low |
| **Full-Text Research & Document Search** | In-memory search & SQLite text queries | Keyword search across research papers, component datasheets, and design notes | **Amazon OpenSearch Service** | Yes | Add OpenSearch indexer; complement SurrealDB & Qdrant | Low |
| **Engineering Knowledge Graph & Relationships** | SurrealDB (`localhost:8001` or Surreal Cloud) | Authoritative graph of projects, components, requirements, and agent relationships | **SurrealDB (AWS VPC / Surreal Cloud)** | No (Retained authoritative) | **KEEP** — Native multi-model graph queries required | Zero |
| **Vector Similarity Retrieval** | Qdrant (`localhost:6333` or Qdrant Cloud) | High-performance ANN vector search for papers, components, and design embeddings | **Qdrant (AWS VPC / Qdrant Cloud)** | No (Retained authoritative) | **KEEP** — Specialized vector indexing required | Zero |
| **User Authentication & RBAC** | Local dev bypass / Clerk JWKS | User login, signup, session validation, role enforcement | **Amazon Cognito User Pools** | Yes | Standardize on Cognito RS256 JWKS validation | Low |
| **Primary LLM & Foundation Models** | Amazon Bedrock (Claude 3.5 Sonnet, Haiku, Titan Embeddings) | Reasoning, research synthesis, schematic generation, code synthesis | **Amazon Bedrock** | No (Already integrated) | **KEEP** — Primary AI foundation | Zero |
| **Specialized Hardware Thermal/EDA Inference** | NVIDIA NIM / GroqCloud (Fallback) | Fast token inference fallback for thermal & circuit analysis | **NVIDIA NIM / AWS SageMaker AI Endpoint** | Optional | Keep as fallback; evaluate SageMaker for private models | Low |
| **Agent Governance & Delegation** | ArmorIQ SDK (`backend/armoriq`) | Cryptographic HMAC receipts, delegation chains, policy enforcement | **ArmorIQ SDK + AWS CloudWatch / EventBridge Audit Trail** | Partial | **KEEP** ArmorIQ core; pipe audit logs to CloudWatch/EventBridge | Zero |
| **Agent-to-Agent Communication** | A2A Protocol | Inter-agent structured message passing | **A2A Protocol + EventBridge/SQS Transport** | No | **KEEP** A2A semantics | Zero |
| **Agent Interoperability** | Bindu Intelligence SDK | External agent directory & interoperability | **Bindu SDK** | No | **KEEP** Bindu interoperability | Zero |
| **Agent Framework** | Google ADK / ArmourFlow custom agents | Agent runtime and prompt chaining | **Google ADK + AWS Step Functions Orchestration** | No | **KEEP** ADK agent definitions | Zero |
| **Component Pricing & Stock APIs** | Nexar / Octopart / DigiKey / Mouser APIs | Real-time electronic component supply chain and distributor data | **External REST APIs (Secured via AWS Secrets Manager)** | No (External partner) | **KEEP** external integration; store keys in Secrets Manager | Low |
| **Observability & Metrics** | In-memory Prometheus collector / local logs | Latency tracking, error rates, request duration, job metrics | **Amazon CloudWatch (Logs, Metrics, Alarms, Dashboard)** | Yes | Replace in-memory counters with CloudWatch EMF & metrics | Low |
| **DNS & Domain Management** | Third-party registrar / Vercel DNS | Domain resolution for web application and API | **Amazon Route 53** | Yes (Final phase) | Route traffic via Route 53 Alias to CloudFront & API Gateway | Low |

---

## Detailed Dependency Inventory

### 1. External APIs and Cloud Services
- **Amazon Bedrock**: Foundation model provider (`anthropic.claude-3-5-sonnet-20241022-v2:0`, `anthropic.claude-3-5-haiku-20241022-v1:0`, `amazon.titan-embed-text-v2:0`, `amazon.nova-canvas-v1:0`). Configured via `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`.
- **Tavily Search API**: Web intelligence queries for research agents (`TAVILY_API_KEY`).
- **Nexar / Octopart / DigiKey / Mouser**: Distributor component availability and pricing APIs (`OCTOPART_API_KEY`, `NEXAR_CLIENT_ID`, `DIGIKEY_CLIENT_ID`, etc.).
- **Algorand x402**: Optional decentralized micro-payment gateway (`WORKLINE_X402_*`).

### 2. Databases & Persistence
- **SurrealDB**: Primary authoritative graph database for engineering entities (`projects`, `components`, `requirements`, `runs`, `pareto_frontiers`, `decisions`). Uses WebSocket/HTTP binary protocol.
- **Qdrant**: Primary vector search engine with 4 collections (`workline_documents`, `workline_components`, `workline_projects`, `workline_research`).
- **SQLite (`user_storage.db`)**: Legacy local storage for user accounts, workspace sessions, and settings. **Targeted for migration to DynamoDB**.

### 3. File & Artifact Storage
- Current system saves files into local folders: `backend/exports/`, `backend/data/`, `scratch/`.
- **Migration**: Centralized via `S3ArtifactStore` to S3 bucket `workline-artifacts-prod` under organized prefixes:
  - `projects/{project_id}/research/`
  - `projects/{project_id}/datasheets/`
  - `projects/{project_id}/exports/`
  - `projects/{project_id}/artifacts/`

### 4. Authentication & RBAC
- Supported via `backend/auth.py` with RS256 JWKS verification.
- **Target**: Amazon Cognito User Pool with explicit JWT token claims (`sub`, `email`, `cognito:groups`) mapped to Workline `AuthenticatedUser`.

### 5. Orchestration & Background Workloads
- Background jobs handled in-process by `JobWorker` consuming `LocalJobQueue`.
- **Target**: Decoupled to **AWS Step Functions** for deterministic multi-agent state management, and **Amazon SQS + DLQ** for asynchronous processing.
