# Workline Platform Architecture — Current State

**Document Status:** Complete (Phase 0 Audit)  
**Date:** September 2026  
**Audited System:** Workline / ArmourFlow AI Engineering Lifecycle Orchestration Platform  

---

## 1. System Inventory

The repository represents an end-to-end cyber-physical engineering automation platform built to guide projects from initial specifications to hardware production, validation, PCB simulation, BOM optimization, and procurement.

### 1.1 Languages and Runtime Environments
- **Backend & Agents:** Python 3.12 / 3.13 (`.venv`, `uv`, standard package management via `pyproject.toml` and `backend/requirements.txt`).
- **Frontend:** Node.js, Next.js 16.2.9 (App Router), React 19.2.4, TypeScript 5.9.3, TailwindCSS 4.
- **CLI:** Python Typer (`cli/wline/main.py`), executable `wline`.

### 1.2 Core Subsystems & Directory Tree
- `backend/`
  - `main.py`: FastAPI gateway mounting REST endpoints and GraphQL.
  - `workline/`: Engineering domain logic:
    - `pcb/`: PCB models, constraints, physics feature extraction, and PINN (Physics-Informed Neural Network) thermal simulation.
    - `procurement/`: Multi-vendor supplier search engine (DigiKey, Mouser, Robu, Robocraze) and deterministic BOM analysis.
    - `orders/`: Governed ordering, risk assessment, human approval policies, X402 payment protocol, and receipt issuance.
    - `decision/`: Trade-space decision engine with criteria-weighting and recommendation generation.
    - `documents/`: Docling document ingestion, spaCy NER, and LlamaIndex chunking.
    - `database/`: SurrealDB graph client and repositories (`ProjectRepository`, `GraphRepository`).
    - `retrieval/`: Qdrant vector database connection manager and FastEmbed embeddings.
    - `armouriq/`: Trust, delegation, policy evaluation, and capability checks for Google ADK agents.
    - `agents/`: ADK agent runtime, session management, and local checkpointing.
  - `routes/`: Workspace, collaboration, speech, calendar, and package routes.
  - `services/`: Thermal operating range and datasheet verification service.
- `armourflow/`:
  - `fabric/`: Unified Agent Control Fabric routing tasks across 90 engineering capabilities.
  - `registry/`: Authoritative Agent Registry cataloging all 27 specialized domain engineering agents.
  - `models/`: Centralized Amazon Bedrock client with local offline fallback.
  - `graphql/`: Strawberry GraphQL schema, router, AST security depth limiters, and subscriptions.
- `cli/wline/`:
  - Canonical `wline` CLI exposing `system`, `project`, `agents`, `task`, `workflow`, `engineering`, `documents`, and `evidence`.
- `frontend/`:
  - Next.js dashboard, Clerk authentication, PeraWallet Algorand integrations, component explorer.
- `research_agents/`:
  - 27 domain agent implementations (e.g. `engineering_simulation`, `manufacturing_agent`, `security_threat`, `cost_supply_chain`, `documentation_agent`).

---

## 2. Identified Architectural Weaknesses & Gaps

### 2.1 Synchronous Long-Running Operations
Currently, several computationally heavy and I/O-intensive engineering operations run directly inside synchronous or async HTTP request cycles:
- **PCB Simulation & PINN Training:** `POST /api/pcb/{pcb_id}/pinn/train` and `POST /api/pcb/{pcb_id}/optimize` block HTTP execution or risk timeouts.
- **Deterministic Validation:** `POST /api/pcb/{pcb_id}/validate` checks 12 rule sets sequentially in-process.
- **Multi-Vendor Procurement Crawling:** `POST /api/procurement/search` queries multiple live supplier APIs synchronously.
- **Document Ingestion:** `POST /api/documents/ingest` runs Docling OCR and spaCy NLP pipeline synchronously.

### 2.2 Direct Infrastructure Coupling in Agents & Domain Logic
- Several modules import database singletons (`surreal_db`, `qdrant_manager`) directly rather than using a unified retrieval abstraction.
- Amazon Bedrock is accessed in multiple places with varying fallback mechanisms rather than a centralized, unified `LLMGateway` supporting token tracking, cost metrics, and provider pluggability.

### 2.3 Binary & Artifact Storage Inconsistency
- Generated Gerbers, simulation CSVs, drill files, BOM exports, and validation PDFs are currently saved directly to local disk subdirectories (`backend/exports/`, `~/.workline/`) or in SQLite/SurrealDB payloads, lacking a decoupled `ArtifactStore` abstraction (e.g. S3-compatible for production, local filesystem for development).

### 2.4 Governance vs. Recommendation Distinction
- While `ArmourIQ` provides policy checks, there is no system-wide formal separation between:
  1. `RECOMMENDATION` (produced by agents)
  2. `AUTHORIZED ACTION` (permitted by policy/human gate)
  3. `EXECUTED ACTION` (performed by background workers with audit receipts)

### 2.5 Observability & Correlation ID Propagation
- Correlation IDs are partially implemented in request headers and task contexts, but lack unified structured logging, metrics emission, and distributed tracing across async boundaries and job queues.

---

## 3. Preserved Assets & Foundations
- **Authoritative Registry:** 27 registered domain agents with individual manifests and health checks.
- **Agent Control Fabric:** Decoupled capability-based routing across 90 engineering capabilities.
- **GraphQL & REST APIs:** Fully validated Strawberry GraphQL layer and FastAPI routing table.
- **Canonical CLI:** Complete `wline` CLI suite with deterministic exit codes and `--json` support.
- **SurrealDB & Qdrant Integration:** Graph and vector retrieval with in-memory resilient fallbacks.
