# Workline Current Architecture: Forensic Analysis & Baseline Audit

**Document ID:** `WORKLINE-AWS-01`  
**Phase:** Phase 0 — Baseline Repository Forensic Inspection  
**Date:** September 2026  
**Status:** COMPLETE / FROZEN BASELINE  

---

## 1. Forensic Summary & Codebase Structure

Workline was engineered as an advanced engineering lifecycle platform supporting hardware CAD, PCB generation, thermal analysis, multi-agent research, and automated bill-of-materials (BOM) optimization. Over its evolution, multiple architectural patterns were introduced in parallel:

1. **Monolithic Core + Microservices Attempt (Render R1–R5):**
   - The primary gateway (`backend/main.py`) operates as a FastAPI application with 50 registered routes.
   - Separate subdirectories (`backend/r2`, `backend/r3`, `backend/r4`, `backend/r5`) attempted to carve out domain microservices for Render hosting (AI, Knowledge, Engineering, Procurement), resulting in redundant Dockerfiles, network isolation friction, and import boundary issues.
2. **Authoritative Dual Data Foundation (SurrealDB + Qdrant):**
   - **SurrealDB** is the authoritative multi-model graph and relational database for engineering state, project models, lifecycle transitions, BOM items, milestone DAGs, and provenance trees (`backend/workline/database/surrealdb.py`).
   - **Qdrant** is the authoritative vector retrieval and semantic search engine for engineering datasheets, components, project domains, and trade-study research (`backend/workline/retrieval/qdrant.py`).
   - In local development, when external cloud database instances were temporarily unreachable, graceful in-memory and local SQLite fallbacks kept development active. The AWS platform redesign provides robust, high-availability AWS hosting for both SurrealDB and Qdrant.
3. **CLI vs Web Duality:**
   - A canonical CLI executable (`wline` under `cli/wline`) was maintained alongside the web backend. Per current architectural directives, **the CLI is completely frozen and out of scope**.
4. **Multi-Agent Fabric:**
   - 27 engineering agents are registered in `armourflow/registry/manifests/agent.01.json` through `agent.27.json`.
   - Coordination is mediated by `AgentControlFabric` (`armourflow/fabric/fabric.py`) and backed by `LocalJobQueue` (`backend/workline/jobs/queue.py`).

---

## 2. Component Inventory Matrix

| Subsystem | Existing Implementation Location | Current Technology | Role in Workline |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | `frontend/` | Next.js 16.2.9, React 19.2.4, Tailwind CSS v4, Framer Motion | Web UI for projects, workflows, 3D CAD viewer, and agent monitoring. |
| **Backend API Gateway** | `backend/main.py`, `backend/routes/` | FastAPI, Uvicorn, Starlette | 50 registered routes; correlation ID logging; handles health, thermal, pcb, jobs, x402. |
| **Control Fabric** | `armourflow/fabric/fabric.py` | Python Singleton, Task Router | Central execution router; handles task lifecycle, contract validation, and agent dispatch. |
| **Job Queue & Worker** | `backend/workline/jobs/` | `LocalJobQueue`, `JobWorker` | Thread-safe async in-memory queue with Dead Letter Queue (DLQ). |
| **Multi-Agent Runtime** | `research_agents/`, `armourflow/registry/` | Python classes, Pydantic schemas | 27 logical agents loaded into AuthoritativeAgentRegistry. |
| **LLM Gateway** | `backend/workline/llm/` | `LLMGateway`, `BedrockProvider`, `NvidiaProvider` | AWS Bedrock primary with NVIDIA text fallback. |
| **Authoritative State DB** | `backend/workline/database/surrealdb.py` | **SurrealDB** | **KEPT — Authoritative Workline engineering and application state & graph.** |
| **Vector Search Engine** | `backend/workline/retrieval/qdrant.py` | **Qdrant** | **KEPT — Authoritative vector retrieval and similarity engine.** |

---

## 3. Existing SurrealDB Schema & Graph Inventory

SurrealDB holds the structured engineering state, graph relationships, and provenance trees across Workline:

### Core Tables & Record Schemas:
- `project`: Primary engineering project records (`id`, `name`, `description`, `stage`, `budget`, `thermal_envelope`, `created_at`, `updated_at`).
- `user`: System users, organization members, and engineering personas.
- `team`: Engineering teams, access scopes, and role bindings.
- `agent`: Agent catalog definitions, capabilities (1-90), runtime statuses, and health metrics.
- `workflow`: Multi-stage workflow specifications, state machine transitions, and execution DAGs.
- `task`: Discrete unit of execution dispatched via Control Fabric (`task_id`, `agent_id`, `status`, `input_payload`, `output_payload`, `error`).
- `milestone`: Schedule milestones and gate checkpoints (`milestone_id`, `project_id`, `status`, `target_date`).
- `requirement`: Engineering requirements, functional specs, and constraints (`req_id`, `project_id`, `text`, `type`, `status`).
- `finding`: Research and validation findings emitted by agents.
- `decision`: Engineering trade-study and design space decisions.
- `optimization`: Design space exploration objects (`variables`, `constraints`, `objectives`, `status`).
- `candidate`: Evaluated design candidates in Pareto exploration.
- `pareto_frontier`: Calculated Pareto-optimal points for hardware tradeoffs.
- `optimization_decision`: Recorded optimization selections with rationales.
- `evidence`: Verified data records, test reports, and datasheet extractions supporting decisions.
- `bom_item`: Detailed bill-of-materials line items (`mpn`, `manufacturer`, `cost`, `footprint`, `status`).
- `audit_event`: Immutable append-only audit trail records.

### Graph Edges & Relationships:
- `project -> has_optimization -> optimization`
- `optimization -> evaluates_candidate -> candidate`
- `optimization -> has_pareto_frontier -> pareto_frontier`
- `optimization -> has_decision -> optimization_decision`
- `milestone -> BLOCKS -> milestone`
- `task -> DEPENDS_ON -> task`
- `agent -> PRODUCES -> finding / decision`
- `finding -> EVIDENCES -> requirement`
- `user -> BELONGS_TO -> team`

---

## 4. Existing Qdrant Collections Inventory

Qdrant holds the high-dimensional vector embeddings, payloads, and similarity indexes across Workline:

| Collection Name | Dimension | Distance Metric | Content & Payload Schema |
| :--- | :---: | :---: | :--- |
| `workline_documents` | 1536 (or Titan 1024) | Cosine | Engineering datasheets, compliance standards, PDF chunks, and architecture specs. |
| `workline_components` | 1536 (or Titan 1024) | Cosine | Electronic component specifications, parametric attributes, MPN, pinouts, and manufacturer data. |
| `workline_projects` | 1536 (or Titan 1024) | Cosine | Project domain profiles, design problem statements, and semantic search vectors. |
| `workline_research` | 1536 (or Titan 1024) | Cosine | Agent research outputs, trade studies, literature summaries, and evidence fragments. |

---

## 5. Identified Defects & Platform Bottlenecks

1. **BUG-001: Local In-Memory Job Queue Vulnerability:**
   - The current `LocalJobQueue` is ephemeral in-process memory. If the backend process crashes or restarts, active jobs are lost. Needs migration to durable Amazon SQS.
2. **BUG-002: Agent #23 Manifest Mapping Defect:**
   - `armourflow/registry/manifests/agent.23.json` points to `SecurityThreatModelingAgent` rather than thermal analysis. Needs correction to `HardwareThermalAgent`.
3. **BUG-003: Insecure JWT Validation Fallback:**
   - `backend/auth.py` falls back to accepting unverified tokens if JWKS signature verification fails. Needs strict RS256 token verification via Amazon Cognito User Pools.
4. **Platform Hosting Defect: External Database Reachability:**
   - Cloud endpoints for SurrealDB and Qdrant were external and fragile. The AWS redesign establishes robust, highly available self-hosted or managed deployments within private AWS VPC subnets.
