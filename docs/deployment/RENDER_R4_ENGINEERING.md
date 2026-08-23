# Workline — Render Deployment Guide: R4 Engineering & Simulation Services

## 1. Overview & Service Responsibilities
**R4 (`workline-engineering-simulation`)** is the internal engineering microservice responsible for high-throughput computation, Physics-Informed Neural Network (PINN) surrogate thermal prediction, PCB geometric Design Rule Checking (DRC), unit conversion, and multi-criteria architecture decision scoring.

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
       +--------------------+--------------------+
       |                    |                    |
  internal HTTP        internal HTTP        internal HTTP
       |                    |                    |
       v                    v                    v
+--------------+    +----------------+    +------------------+
| R2 AI/AGENTS |    |  R3 KNOWLEDGE  |    |  R4 ENGINEERING  |  (Render Docker - Internal)
|   RESEARCH   |    |  (SurrealDB +  |    |  & SIMULATION    |
+--------------+    |    Qdrant)     |    +------------------+
                    +----------------+             |
                                           +-------+-------+
                                           |       |       |
                                          PCB    PINN   Thermal
                                          DRC   Physics Solver
```

---

## 2. Docker Configuration
- **Dockerfile**: [`backend/r4/Dockerfile`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r4/Dockerfile)
- **Build Context**: Repository Root (`.`)
- **Base Image**: `python:3.12-slim`
- **Runtime User**: `workline` (UID 1000)
- **Default Port**: Dynamic Render `$PORT` (Defaults to `10004`)
- **Startup Command**: `uvicorn backend.r4.main:app --host 0.0.0.0 --port ${PORT:-10004}`

---

## 3. Dependency Closure
- **Requirements File**: [`backend/r4/requirements.txt`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r4/requirements.txt)
- **Target Dependencies**:
  - `fastapi`, `uvicorn`, `pydantic`
  - `numpy`, `scipy` (Numerical physics, finite difference baseline & PINN math)
  - `httpx`, `orjson`, `aiosqlite`, `loguru`

---

## 4. Health Check Endpoint
- **Path**: `GET /health` (aliased to `GET /`, `GET /version`, `GET /service`)
- **Status Code**: `200 OK`
- **Payload**:
  ```json
  {
    "status": "healthy",
    "service": "workline-r4",
    "version": "1.0.0-rc1"
  }
  ```
- **Behavior**: Lightweight process probe that verifies process liveness without running heavy PINN inferences or physical simulations.

---

## 5. Security & Internal Endpoints

### 5.1 Internal Endpoints
- `POST /internal/engineering/units/convert`: Dimensional and physical unit conversion.
- `POST /internal/engineering/requirements/validate`: Engineering constraint evaluator (10F).
- `POST /internal/engineering/tradeoffs/evaluate`: Multi-criteria decision matrix scoring (10H).
- `POST /internal/engineering/pcb/validate`: PCB DRC geometric validation (10I).
- `POST /internal/engineering/pinn/thermal`: PINN forward inference for 2D board temperature field prediction (10J).

### 5.2 Authentication
- **Header**: `Authorization: Bearer <R4_SERVICE_TOKEN>` (or `X-Workline-Service-Token: <R4_SERVICE_TOKEN>`)
- **Verification**: Constant-time token comparison (`secrets.compare_digest`).
- **Access Control**: R4 is strictly internal and never exposed to the public browser.

---

## 6. Render Environment Variables

| Variable | Description | Type |
| :--- | :--- | :--- |
| `PORT` | Dynamic listener port assigned by Render | System (10004) |
| `WORKLINE_ENV` | Environment identifier (`production`) | Config |
| `R4_SERVICE_TOKEN` | Shared secret token for R1 $\to$ R4 authentication | Secret |
| `R3_INTERNAL_URL` | Internal URL to R3 Knowledge Service | Config |
| `R3_SERVICE_TOKEN` | Shared secret token for R4 $\to$ R3 calls (if needed) | Secret |

---

## 7. Failure Isolation & Rollback
- **R1 Isolation**: If R4 is restarting or offline, R1 handles downtime gracefully via [`backend/services/r4_client.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/services/r4_client.py) without crashing.
- **Rollback**: Select the previous deployment commit in Render and click **Rollback**.
