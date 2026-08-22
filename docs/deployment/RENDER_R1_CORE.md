# Workline Render Deployment Specification: R1 Core / Gateway

**Document Version**: 1.0.0-rc1  
**Target Service**: `workline-core-gateway` (Render Web Service)  
**Status**: **R1 RENDER READY (DEPLOYMENT BRANCH: deploy/render-r1)**  

---

## 1. Service Overview & Responsibilities

| Attribute | Value |
| :--- | :--- |
| **Service Name** | `workline-core-gateway` |
| **Repository** | `https://github.com/callmetechnophile/workline` |
| **Branch** | `deploy/render-r1` (and `main`) |
| **Root Directory** | `.` (Repository Root) |
| **Runtime** | `Python 3.12+` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `uvicorn backend.services.core.main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Endpoint** | `GET /health` |
| **Declared Footprint** | `~35 MB` (Lightweight Core Gateway) |

---

## 2. R1 Microservice Boundary & Dependency Isolation

R1 is strictly isolated as a **Core Gateway, Authentication, Workspace Lifecycle, and Proxy Service**:
- **Included Modules**: `FastAPI`, `Uvicorn`, `Pydantic`, `HTTPX`, `aiosqlite`, `loguru`, workspace routes, and downstream proxy endpoints.
- **Excluded Modules**: Does **NOT** load `Docling`, `spaCy`, `LlamaIndex`, `PyTorch`, `SciPy`, `SurrealDB server runtime`, or `Qdrant vector engine`.

---

## 3. Downstream Proxy Routing & Graceful Degradation

```
                     NETLIFY FRONTEND
                            │
                      HTTPS REST / BFF
                            │
                            ▼
               RENDER R1: CORE API GATEWAY
                        (:10000)
                            │
   ┌──────────────┬─────────┴─────────┬──────────────┐
   ▼              ▼                   ▼              ▼
R2: AI /      R3: Knowledge /     R4: Eng /      R5: Procurement /
Research       Documents          Simulation       Collaboration
(:10002)       (:10003)            (:10004)          (:10005)
```

- **Graceful Failure**: If any downstream microservice (R2, R3, R4, R5) is offline or undeployed, R1 catches `httpx.RequestError` and returns a clean `HTTP 503 Service Unavailable` with diagnostic details instead of crashing with HTTP 500.

---

## 4. Environment Variables Matrix

| Variable | Scope | Description / Value |
| :--- | :--- | :--- |
| `PORT` | Render Managed | Listening port (injected dynamically by Render) |
| `WORKLINE_CORS_ORIGINS` | Runtime | Allowed origins: `https://worklineai.netlify.app,http://localhost:3000` |
| `WORKLINE_R2_URL` | Internal Network | Destination for AI / OmniRoute proxy (`http://workline-ai-agents:10002`) |
| `WORKLINE_R3_URL` | Internal Network | Destination for Knowledge / Vector proxy (`http://workline-knowledge-documents:10003`) |
| `WORKLINE_R4_URL` | Internal Network | Destination for Engineering / PINN proxy (`http://workline-engineering-simulation:10004`) |
| `WORKLINE_R5_URL` | Internal Network | Destination for Procurement / BOM proxy (`http://workline-procurement-service:10005`) |

---

## 5. Verification & Test Suite

- **Unit Test Suite**: [`tests/unit/test_r1_core_standalone.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/tests/unit/test_r1_core_standalone.py) (3/3 PASSED):
  - `test_r1_health_endpoint`: Verified HTTP 200 with service identity and downstream map.
  - `test_r1_proxy_graceful_503_when_downstream_offline`: Verified 503 graceful handling for R2, R3, R4, R5.
  - `test_r1_cors_and_404_handling`: Verified CORS headers and clean 404 on unmapped paths.
- **Full Backend Regression**: **320/320 passed (100% SUCCESS)**.

---

## 6. Deployment & Rollback Procedures

### A. Initial Deployment via Render Dashboard
1. Log into [Render.com](https://dashboard.render.com).
2. Click **New +** $\to$ **Web Service**.
3. Connect GitHub repository: `callmetechnophile/workline`.
4. Configure:
   - **Name**: `workline-core-gateway`
   - **Branch**: `deploy/render-r1` (or `main`)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.services.core.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
5. Add Environment Variable:
   - `WORKLINE_CORS_ORIGINS` = `https://worklineai.netlify.app,http://localhost:3000`
6. Click **Create Web Service**.

### B. Rollback Procedure
In the Render Dashboard:
1. Navigate to `workline-core-gateway` $\to$ **Events**.
2. Locate previous stable deployment $\to$ click **Rollback to this deploy**.
