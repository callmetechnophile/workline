# Workline R3 Service Boundary Audit

## Service Identification
- **Service Name**: `workline-r3` (`workline-knowledge-documents`)
- **Service Role**: Internal Knowledge Infrastructure, Vector Search (Qdrant), Multi-Model Graph (SurrealDB) & Document Ingestion
- **Deployment Model**: Render Web Service (Docker Runtime)
- **Exposure**: Internal Private Network / Authenticated Service API (R1 Gateway Gatewayed)

---

## 1. R3 Module Inventory & Database Ownership Map

| Module Path | Primary Purpose | Dependencies | Database | R3 Responsibility | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`backend/workline/retrieval/qdrant.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/retrieval/qdrant.py) | Qdrant vector database manager & collection lifecycle | `qdrant-client`, `fastembed` | Qdrant Cloud / Local | Primary Vector Store | ✅ Active |
| [`backend/workline/database/surrealdb.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/database/surrealdb.py) | SurrealDB async client, multi-model schema & connections | `surrealdb` | SurrealDB Cloud / Local | Primary Graph/Document Store | ✅ Active |
| [`backend/workline/retrieval/hybrid.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/retrieval/hybrid.py) | Hybrid dense + sparse vector & keyword search | `qdrant-client`, `numpy` | Qdrant | Vector Scoring & Ranking | ✅ Active |
| [`backend/workline/knowledge/graph/service.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/knowledge/graph/service.py) | Knowledge graph node & edge resolution | `surrealdb`, `pydantic` | SurrealDB | Graph Topology Traversal | ✅ Active |
| [`backend/workline/knowledge/indexing.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/knowledge/indexing.py) | Document chunking & vector indexing pipeline | `fastembed`, `pydantic` | Qdrant | Ingestion Pipeline | ✅ Active |
| [`backend/workline/knowledge/cache/`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/knowledge/cache/) | Persistent & in-memory knowledge cache | `aiosqlite`, `orjson` | SQLite / Memory | Knowledge Caching | ✅ Active |
| [`backend/workline/documents/service.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/documents/service.py) | Datasheet & document entity extraction | `pydantic` | SurrealDB | Document Storage | ✅ Active |
| [`backend/workline/api/knowledge.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/knowledge.py) | Knowledge search & chunking REST API | `fastapi`, `pydantic` | Qdrant | Public Internal API | ✅ Active |
| [`backend/workline/api/graph.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/graph.py) | Graph traversal & relationship query API | `fastapi`, `pydantic` | SurrealDB | Public Internal API | ✅ Active |

---

## 2. Service Boundary Enforcement

### What R3 Owns:
1. **Qdrant Vector Database**: Collection initialization, vector embedding generation, cosine similarity search.
2. **SurrealDB Multi-Model Graph**: Entity relations, project topology, collaborative nodes, graph queries.
3. **Knowledge Ingestion & Indexing**: Document chunking, datasheet parsing, semantic embedding storage.
4. **Internal Knowledge APIs**: `/internal/knowledge/search`, `/internal/knowledge/index`, `/internal/graph/query`.

### What R3 DOES NOT Own (Excluded from R3 Container):
- ❌ **Frontend & Web UI**: Next.js App Router.
- ❌ **AI Agent Orchestration & ADK**: LLM prompt synthesis, multi-agent workflows (owned by R2).
- ❌ **Physics & Simulation**: PINN Neural Networks, thermal simulation, solvers (owned by R4).
- ❌ **Procurement & Sourcing**: Component scraping, vendor APIs, x402 payment escrow (owned by R5).
- ❌ **Public Gateway**: Clerk JWT session verification, browser CORS (owned by R1).

---

## 3. Communication & Data Flow
```
[Browser / User] 
       │
       ▼ (Public HTTPS)
[R1 Core Gateway]
       │
       ▼ (Internal HTTP + Authorization: Bearer <R3_SERVICE_TOKEN>)
[R3 Knowledge Infrastructure]
   ├── Vector Store (Qdrant)
   ├── Graph Store (SurrealDB)
   └── Document Indexing Engine
```
