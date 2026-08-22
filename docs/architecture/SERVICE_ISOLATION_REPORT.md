# Workline Service Isolation & Database Boundary Validation Report

**Audit Date**: 2026-08-23  
**Status**: **ISOLATION VERIFIED**  

---

## 1. Service Isolation Matrix

| Service | Standalone Entrypoint | Health Check | Declared Dependencies | Isolation Verification |
| :--- | :--- | :--- | :--- | :--- |
| **R1 Core / Gateway** | `backend.services.core.main:app` | `/health` | `fastapi`, `python-jose`, `cryptography`, `httpx` | **PASSED** (Zero ML/PyTorch/Docling imports) |
| **R2 AI / Agents** | `backend.services.ai.main:app` | `/health` | `google-genai`, `sarvamai`, `scrapling` | **PASSED** (Isolated LLM & scraping runtime) |
| **R3 Knowledge / DBs** | `backend.services.knowledge.main:app` | `/health` | `surrealdb`, `qdrant-client`, `fastembed`, `docx` | **PASSED** (Dedicated owner of SurrealDB & Qdrant) |
| **R4 Engineering** | `backend.services.engineering.main:app` | `/health` | `numpy`, `onnxruntime`, `pydantic` | **PASSED** (Isolated PINN & DRC geometric solvers) |
| **R5 Procurement** | `backend.services.procurement.main:app` | `/health` | `fastapi`, `httpx`, `cryptography` | **PASSED** (Isolated BOM & x402 payment processor) |

---

## 2. Database Ownership Validation

```
     ┌────────────────────────────────────────────────────────┐
     │                R3: KNOWLEDGE & DOCUMENTS               │
     │                      (:10003)                          │
     └───────────────────────────┬────────────────────────────┘
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
            SurrealDB (:8000)          Qdrant (:6333)
            (Graph & Topologies)       (Dense Vectors)
```

- **Sole Owner**: **R3 (Knowledge / Documents)** is the single point of ownership for SurrealDB and Qdrant connections.
- **Access Policy**: R1, R2, R4, and R5 communicate with knowledge/graph repositories through authenticated R3 internal REST endpoints.
- **Failover / Degraded Mode**: All services implement fallback modes using local SQLite or memory caches when R3 or external databases are unreachable.

---

## 3. Failure Isolation & Degradation Matrix

| Simulated Failure | Impact on R1 Gateway | Impact on Other Services | System Behavior |
| :--- | :--- | :--- | :--- |
| **R2 (AI) Down** | R1 returns HTTP 503 for `/api/proxy/ai/*` | R3, R4, R5 continue normal operation | **Graceful Degradation** (Dashboard stays online) |
| **R3 (Knowledge) Down** | R1 returns HTTP 503 for `/api/proxy/knowledge/*` | R1, R2, R4, R5 use cached/local schema fallback | **Graceful Degradation** (Local SQLite active) |
| **R4 (Engineering) Down** | R1 returns HTTP 503 for `/api/proxy/engineering/*` | R1, R2, R3, R5 unaffected | **Graceful Degradation** |
| **R5 (Procurement) Down** | R1 returns HTTP 503 for `/api/proxy/procurement/*` | R1, R2, R3, R4 unaffected | **Graceful Degradation** |

---

## 4. Cross-Service Import & Coupling Classification

| Source Module | Target Domain | Reason | Classification | Severity |
| :--- | :--- | :--- | :--- | :--- |
| `backend.services.core` | Downstream Services (R2-R5) | HTTP Proxy Routing (`httpx`) | `VALID_SHARED` | NONE |
| `backend.workline.procurement` | Base Models (`pydantic`) | Shared Data Transfer Objects | `VALID_SHARED` | NONE |
| `backend.workline.database` | SQLite fallback (`aiosqlite`) | Local Persistence | `VALID_SHARED` | NONE |
| `backend.workline.retrieval` | `qdrant-client` | Vector Query Execution in R3 | `VALID_SHARED` | NONE |
