# Workline — Render Deployment Guide: R3 Knowledge Infrastructure

## 1. Overview & Service Responsibilities
**R3 (`workline-knowledge-documents`)** is the internal database and knowledge microservice responsible for Qdrant vector retrieval, SurrealDB multi-model graph persistence, document chunking, and semantic similarity search.

```
                         NETLIFY
                     Next.js Frontend
                            |
                          HTTPS
                            |
                            v
                   +-------------------+
                   |      R1 CORE      |
                   |  API & GATEWAY    |  (Render Docker - Public Gateway)
                   +-------------------+
                            |
                 +----------+----------+
                 |                     |
     internal authenticated HTTP       internal authenticated HTTP
                 |                     |
                 v                     v
        +----------------+    +------------------+
        | R2 AI / AGENTS |    |   R3 KNOWLEDGE   |
        |    RESEARCH    |    |  INFRASTRUCTURE  |  (Render Docker - Internal)
        +----------------+    +------------------+
                                       |
                              +--------+--------+
                              |                 |
                            QDRANT          SURREALDB
                         Vector Store      Multi-Model Graph
```

---

## 2. Docker Configuration
- **Dockerfile**: [`backend/r3/Dockerfile`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r3/Dockerfile)
- **Build Context**: Repository Root (`.`)
- **Base Image**: `python:3.12-slim`
- **Runtime User**: `workline` (UID 1000)
- **Default Port**: Dynamic Render `$PORT` (Defaults to `10003`)
- **Startup Command**: `uvicorn backend.r3.main:app --host 0.0.0.0 --port ${PORT:-10003}`

---

## 3. Dependency Closure
- **Requirements File**: [`backend/r3/requirements.txt`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r3/requirements.txt)
- **Target Dependencies**:
  - `fastapi`, `uvicorn`, `pydantic`
  - `qdrant-client` (Qdrant Vector Database)
  - `surrealdb` (SurrealDB Multi-Model Graph)
  - `fastembed` (Local high-throughput dense embeddings)
  - `httpx`, `numpy`, `orjson`, `aiosqlite`, `loguru`

---

## 4. Health Check Endpoint
- **Path**: `GET /health` (also aliased to `GET /`, `GET /version`, `GET /service`)
- **Status Code**: `200 OK`
- **Payload**:
  ```json
  {
    "status": "healthy",
    "service": "workline-r3",
    "version": "1.0.0-rc1",
    "databases": {
      "surrealdb": "connected",
      "qdrant": "connected"
    }
  }
  ```
- **Behavior**: Lightweight process probe that verifies process liveness and reports database connectivity without failing liveness if a remote DB is offline.

---

## 5. Security & Internal Endpoints

### 5.1 Internal Endpoints
- `POST /internal/knowledge/search`: Vector similarity search across component knowledge.
- `POST /internal/knowledge/index`: Ingestion and embedding indexing.
- `POST /internal/graph/query`: SurrealQL graph traversal queries.
- `GET /internal/knowledge/document/{id}`: Document retrieval.

### 5.2 Authentication
- **Header**: `Authorization: Bearer <R3_SERVICE_TOKEN>` (or `X-Workline-Service-Token: <R3_SERVICE_TOKEN>`)
- **Verification**: Constant-time token comparison (`secrets.compare_digest`).
- **Access Control**: R3 is strictly internal and never exposed to the public browser.

---

## 6. Render Environment Variables

| Variable | Description | Type |
| :--- | :--- | :--- |
| `PORT` | Dynamic listener port assigned by Render | System (10003) |
| `WORKLINE_ENV` | Environment identifier (`production`) | Config |
| `R3_SERVICE_TOKEN` | Shared secret token for R1 $\to$ R3 authentication | Secret |
| `QDRANT_URL` | Qdrant Cloud or Cluster HTTP endpoint | Config |
| `QDRANT_API_KEY` | Qdrant Cloud API Key | Secret |
| `SURREALDB_URL` | SurrealDB connection URL (`wss://...` or `http://...`) | Config |
| `SURREALDB_USER` | SurrealDB database username | Secret |
| `SURREALDB_PASSWORD` | SurrealDB database password | Secret |

---

## 7. Failure Isolation & Rollback
- **R1 Isolation**: If R3 is restarting, R1 handles downtime gracefully via [`backend/services/r3_client.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/services/r3_client.py) without crashing.
- **Rollback**: Select the previous deployment commit in Render and click **Rollback**.
