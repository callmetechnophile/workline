# Workline Database Subsystem Audit

**Document ID:** `WORKLINE-DEBUG-03`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Scope:** SurrealDB Cloud, Qdrant Vector Cloud, SQLite Local Fallback  

---

## 1. Database Connectivity Matrix

| Database Engine | Target Endpoint | Connection Result | Latency / Error Details | Production Status |
| :--- | :--- | :---: | :--- | :---: |
| **SurrealDB Cloud** | `workline-06g2ni45jhpnf8mo1nials6hp4.aws-use1.surreal.cloud` | **FAILED** | WebSocket HTTP 403 Forbidden / Health 503 | `BLOCKED` |
| **Qdrant Cloud** | `05190f58-b6c5-462d-a021-bab38cffc291.us-east-2-0.aws.cloud.qdrant.io` | **FAILED** | Failed to obtain server version (Cluster Suspended) | `BLOCKED` |
| **SQLite Local** | `backend/user_storage.db` (WAL Mode) | **PASS** | Read/Write/Query completed in 28.37ms | `REAL_PASS` |

## 2. In-Memory & SQLite Degradation Behavior

When cloud databases are unavailable:
1. `armourflow.data.client.PlatformDatabaseClient` automatically switches to in-memory graph repository.
2. `backend.workline.database.surrealdb.surreal_db` flags `is_connected() == False`, allowing `/health/database` to accurately report `degraded`.
3. All critical local workflows (job queues, idempotency, package history, project metadata) persist cleanly into SQLite.

## 3. Schema & Table Verification (SQLite)

The following tables were verified in `backend/user_storage.db`:
- `packages`: User engineering packages, readiness/risk/optimization scores.
- `projects`: BOM items, power specs, dependencies, wiring, gantt chart data.
- `idempotency_keys`: Durable deduplication records for task & job execution.
- `pcb_visualizations`: Generated board render metadata and storage references.
- `teams`, `members`, `team_invitations`: Role-based access control state.
- `pipeline_runs`: Multi-stage pipeline tracking.
