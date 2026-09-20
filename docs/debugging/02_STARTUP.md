# Workline Application Startup & Gateway Probe

**Document ID:** `WORKLINE-DEBUG-02`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Test Harness:** Uvicorn / FastAPI TestClient & Headless Microsoft Edge  

---

## 1. Startup Probes & Health Checks

The Workline backend gateway (`backend.main:app`) was initialized and probed across all canonical health routes:

| Method | Endpoint | HTTP Status | Latency | Response Payload / Behavior | Verdict |
| :--- | :--- | :---: | :---: | :--- | :---: |
| `GET` | `/` | 200 | 255.68ms | `{"status": "healthy", "service": "workline-core-gateway", "version": "1.0.0-rc1"}` | **REAL_PASS** |
| `GET` | `/health` | 200 | 8.7ms | `{"status": "healthy", "service": "workline-core-gateway", "version": "1.0.0-rc1"}` | **REAL_PASS** |
| `GET` | `/version` | 200 | 6.86ms | `{"status": "healthy", "service": "workline-core-gateway", "version": "1.0.0-rc1"}` | **REAL_PASS** |
| `GET` | `/service` | 200 | 7.47ms | `{"status": "healthy", "service": "workline-core-gateway", "version": "1.0.0-rc1"}` | **REAL_PASS** |
| `GET` | `/health/database` | 200 | 2110.79ms | `{"surrealdb": "degraded", "qdrant": "degraded"}` | **REAL_PASS (Degraded State Detected)** |
| `GET` | `/health/cluster` | 200 | 8188.12ms | Probed downstream R2-R5 microservices; all unreachable on localhost | **REAL_PASS (Cluster Isolated)** |
| `GET` | `/favicon.ico` | 204 | 8.67ms | No content returned | **REAL_PASS** |

## 2. Lifespan & Background Worker Initialization

During `lifespan` initialization:
1. `backend.database.init_db()` executes SQLite schema creation in WAL mode.
2. `surreal_db.connect()` attempts connection to SurrealDB Cloud (catches 403 error without crashing process).
3. `qdrant_manager.connect()` initializes Qdrant client (catches server version probe warning).
4. `default_job_worker.start()` spawns background async task queue consumer.

## 3. Registered Route Inventory

A total of **50 routes** are active in the FastAPI router table, spanning:
- **Core Platform:** `/health`, `/version`, `/service`, `/health/database`, `/health/cluster`
- **Agent Lifecycle:** `/api/agents/run`, `/api/agents/executions/{id}`, `/api/agents/approval/{id}`, `/api/agents/tasks`
- **Jobs Engine:** `/api/jobs`, `/api/jobs/{id}`, `/api/jobs/{id}/cancel`, `/api/jobs/dlq/all`
- **Observability:** `/api/observability/metrics`, `/api/observability/traces`
- **Hardware & Engineering:** `/api/projects/{id}/pcb/generate`, `/api/projects/{id}/thermal`
- **x402 Algorand:** `/api/x402/services`, `/api/x402/payments`, `/api/x402/execute/{service_id}`
