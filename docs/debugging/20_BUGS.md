# Workline Master Bug Catalog & Triage Log

**Document ID:** `WORKLINE-DEBUG-20`  
**Execution Timestamp:** 2026-09-18T01:20:00+05:30  
**Inspector:** Senior Staff Software & Systems Debugger  

---

## Master Bug Catalog

| Bug ID | Severity | Component | Summary | Root Cause | Status |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **BUG-001** | **CRITICAL** | `backend/main.py` & `backend/database` | `GET /api/projects/{id}/thermal` crashes with HTTP 500 | `backend/database` lacked `get_project_by_id` implementation | **FIXED & VERIFIED** |
| **BUG-002** | **HIGH** | `armourflow/registry/manifests/agent.23.json` | Agent #23 manifest points to wrong entrypoint class | Manifest lists `SecurityThreatModelingAgent` instead of thermal agent | **CATALOGED** |
| **BUG-003** | **HIGH** | `backend/auth.py` | Unverified JWT signature fallback allows forged token authentication | JWKS decode exception caught and falls back to unverified payload `sub` | **CATALOGED (SECURITY)** |
| **BUG-004** | **MEDIUM** | `backend/workline/database/surrealdb.py` | Remote SurrealDB Cloud endpoint returns HTTP 403/503 | Cloud instance suspended or IP whitelisting blocking connection | **BLOCKED (INFRA)** |
| **BUG-005** | **MEDIUM** | `backend/workline/retrieval/qdrant.py` | Remote Qdrant Cloud cluster version check fails | Remote cluster inaccessible or suspended | **BLOCKED (INFRA)** |
| **BUG-006** | **LOW** | `cli/wline/commands/auth.py` | `wline auth status` subcommand name mismatch | Subcommand named `whoami` rather than `status` | **CATALOGED** |
