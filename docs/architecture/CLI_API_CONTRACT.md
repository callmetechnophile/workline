# Workline CLI to Backend API Contract

**Audit Date**: 2026-08-23  

---

## 1. Architectural Invariant

The `wline` CLI communicates **exclusively** with **Render R1 (Core / Gateway)** over HTTPS. The CLI never communicates directly with R2, R3, R4, or R5, and never receives direct database connection strings.

```
  wline CLI (Local Device)
        │
        ▼ (HTTPS REST / JSON)
  RENDER R1: Core Gateway (:10000)
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
  R2 (AI / Research)    R3 (Knowledge DB)      R4 (Engineering)
```

---

## 2. API Contract Endpoints

| CLI Command | R1 Gateway Route | Internal Destination | Description |
| :--- | :--- | :--- | :--- |
| **`wline agent run`** | `POST /api/proxy/ai/api/agents/run` | R2 (:10002) | Trigger OmniRoute agent pipeline |
| **`wline research`** | `POST /api/proxy/ai/api/research/query`| R2 (:10002) | Execute deep datasheet web research |
| **`wline document ingest`** | `POST /api/proxy/knowledge/api/documents` | R3 (:10003) | Upload & index PDF/DOCX specs |
| **`wline graph query`** | `GET /api/proxy/knowledge/api/graph/traverse` | R3 (:10003) | Query SurrealDB dependency topology |
| **`wline pcb check`** | `POST /api/proxy/engineering/api/pcb/validate` | R4 (:10004) | Execute deterministic DRC analysis |
| **`wline simulate`** | `POST /api/proxy/engineering/api/packages/run` | R4 (:10004) | Execute PINN neural thermal solver |
| **`wline bom generate`** | `POST /api/proxy/procurement/api/procurement/search` | R5 (:10005) | Multi-vendor price & stock search |

---

## 3. Resilience & Error Handling

- **Request Timeout**: 30.0s for compute operations; 10.0s for metadata queries.
- **Offline Behavior**: If R1 Gateway is unreachable, `wline` operates in **local-first mode**, reading/writing `.wlipjt` archives, local Git, and cached schemas.
- **Authentication**: Bearer tokens passed via `Authorization: Bearer <token>` header; validated by R1 against Clerk before routing.
