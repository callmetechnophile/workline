# Database Architecture: WorkflowGuide AI / ArmourFlow AI

## Executive Architectural Summary
This document specifies the persistence and data storage topology for the WorkflowGuide AI / ArmourFlow AI platform following its AWS-native migration.

In accordance with strict architectural invariants, **Workline does not replace SurrealDB or Qdrant with generic relational or NoSQL alternatives**. Instead, each data platform fulfills a distinct, mathematically and architecturally justified role.

---

## 1. Storage Tier Architecture

```
                                  APPLICATIONS / AGENTS
                                            │
               ┌────────────────────┬───────┴────────────┬──────────────────┐
               │                    │                    │                  │
               ▼                    ▼                    ▼                  ▼
          SurrealDB             Qdrant            Amazon DynamoDB       Amazon S3
               │                    │                    │                  │
         Authoritative        Authoritative         AWS Application     Binary & Artifact
         Graph & Multi-Model  ANN Vector Engine     Metadata & Locks    Object Store
               │                    │                    │                  │
     - Engineering KG       - 1536d Embeddings   - Job States        - Export PDFs
     - Agent Topology       - Component Vectors  - Idempotency Locks - Raw Datasheets
     - BOM Relationships    - Research Chunks    - User Preferences  - CAD / PCB Files
     - Pareto Frontiers     - Design Matches     - Workflow Pointers - JSON Snapshots
```

---

## 2. Platform Roles & Justification

### A. SurrealDB (Authoritative Engineering Graph Layer) — KEPT
- **Role:** Primary authoritative database for hardware engineering topology, entity relationships, Pareto frontiers, and multi-agent execution graphs.
- **Why Retained:**
  - Hardware engineering requires deep relational traversals (e.g., `project -> has_bom -> bom_item -> connects_to -> pin_map -> constrained_by -> thermal_envelope`).
  - Graph traversals in native SurrealQL (`->relates_to->node`) provide single-query traversal across recursive sub-circuits and optimization frontiers without combinatorial SQL joins or denormalized document sprawl.
  - Multi-agent state isolation: Agents record hypotheses, decisions, and invalidations atomically across the graph.
- **Hosting in AWS:** Deployed inside the private VPC on AWS ECS Fargate or directly connected via Surreal Cloud VPC Peering / PrivateLink.

### B. Qdrant (Authoritative Vector Retrieval Engine) — KEPT
- **Role:** High-performance approximate nearest neighbor (ANN) vector database for hardware components, research paper embeddings, and engineering document chunks.
- **Standard Collections:**
  - `workline_documents`: System documentation, datasheets, and research papers.
  - `workline_components`: Electronic component vector embeddings (parametric & text features).
  - `workline_projects`: Prior project embeddings for similarity transfer and reuse.
  - `workline_research`: Deep academic research extracts and contradiction nodes.
- **Why Retained:** Sub-millisecond HNSW indexing with payload filtering (e.g., filtering component embeddings by `voltage <= 5.0` and `in_stock == True`) is not natively or efficiently matched by OpenSearch or DynamoDB.
- **Hosting in AWS:** Deployed in VPC on ECS Fargate or Qdrant Cloud on AWS.

### C. Amazon DynamoDB (AWS Application Metadata & Idempotency) — NEW
- **Role:** Fast, serverless, single-digit millisecond key-value metadata store.
- **Stored Entities:**
  - `IDEMPOTENCY#<key>`: Conditional write distributed locks preventing duplicate API submissions.
  - `JOB#<job_id>`: Lightweight job execution pointers and status flags for SQS/Step Functions workers.
  - `USER#<user_id>##PREFERENCES`: User theme, notification settings, and dashboard layouts.
  - `WORKFLOW#<execution_id>`: Step Functions execution checkpoint records.
- **TTL Support:** Automated time-to-live expiration for idempotency tokens (300s) and transient session data.

### D. Amazon S3 (Artifact & Object Store) — ENHANCED
- **Role:** Scalable, durable object storage for binary files, generated reports, and large assets.
- **Object Key Hierarchy:**
  ```
  projects/{project_id}/research/{hash}_{filename}.pdf
  projects/{project_id}/datasheets/{part_number}_{hash}.pdf
  projects/{project_id}/exports/{export_id}_bom.csv
  projects/{project_id}/artifacts/{artifact_id}_{filename}
  ```
- **Security:** Encrypted at rest via AWS KMS (`SSE-KMS`). Access governed via presigned GET/PUT URLs with strict 15-minute expirations.

### E. Amazon OpenSearch Service (Search & Indexing Engine) — NEW
- **Role:** Full-text BM25 search, stemming, and fuzzy search across academic literature, component datasheets, and design specifications.
- **Distinction from SurrealDB:** OpenSearch is strictly an indexing engine. It indexes documents stored in S3 and referenced in SurrealDB to enable rapid keyword and multi-match full-text searches.

---

## 3. Data Flow Example: Multi-Agent BOM Generation

1. **User Request:** User submits component requirements via API Gateway.
2. **Idempotency Check:** Lambda acquires an idempotency lock in **DynamoDB**.
3. **Step Functions Invocation:** Step Functions triggers the Planner Agent.
4. **Knowledge Retrieval:** Research Agent queries **OpenSearch** (full text) and **Qdrant** (vector similarity) to identify candidates.
5. **Graph Mutation:** Optimization Agent evaluates constraints and writes candidate nodes and Pareto frontiers into **SurrealDB**.
6. **Artifact Generation:** Final BOM is exported as CSV/PDF, saved to **Amazon S3**, and signed download URLs are returned.
7. **Event Emitted:** Completion event published to **EventBridge**; alerts published to **SNS**.
