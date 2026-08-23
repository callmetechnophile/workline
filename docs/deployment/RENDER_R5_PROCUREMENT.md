# Workline — Render Deployment Guide: R5 Procurement & x402 Payment Services

## 1. Overview & Service Responsibilities
**R5 (`workline-procurement-service`)** is the internal procurement microservice responsible for component search, multi-vendor quote consolidation (DigiKey, Mouser, Robu, Robocraze), BOM procurement optimization, order state machine execution, and cryptographic x402 payment authorization.

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
       +--------------------+--------------------+--------------------+
       |                    |                    |                    |
  internal HTTP        internal HTTP        internal HTTP        internal HTTP
       |                    |                    |                    |
       v                    v                    v                    v
+--------------+    +----------------+    +------------------+   +-------------------+
| R2 AI/AGENTS |    |  R3 KNOWLEDGE  |    |  R4 ENGINEERING  |   |  R5 PROCUREMENT   |  (Render Docker - Internal)
|   RESEARCH   |    |  (SurrealDB +  |    |  & SIMULATION    |   |     & x402        |
+--------------+    |    Qdrant)     |    +------------------+   +-------------------+
                    +----------------+             |                       |
                                           +-------+-------+       +-------+-------+
                                           |       |       |       |       |       |
                                          PCB    PINN   Thermal  Orders  Vendor  x402
                                          DRC   Physics Solver   States   APIs  Payment
```

---

## 2. Docker Configuration
- **Dockerfile**: [`backend/r5/Dockerfile`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r5/Dockerfile)
- **Build Context**: Repository Root (`.`)
- **Base Image**: `python:3.12-slim`
- **Runtime User**: `workline` (UID 1000)
- **Default Port**: Dynamic Render `$PORT` (Defaults to `10005`)
- **Startup Command**: `uvicorn backend.r5.main:app --host 0.0.0.0 --port ${PORT:-10005}`

---

## 3. Dependency Closure
- **Requirements File**: [`backend/r5/requirements.txt`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r5/requirements.txt)
- **Target Dependencies**:
  - `fastapi`, `uvicorn`, `pydantic`
  - `httpx`, `cryptography`, `python-jose`
  - `orjson`, `aiosqlite`, `loguru`

---

## 4. Health Check Endpoint
- **Path**: `GET /health` (aliased to `GET /`, `GET /version`, `GET /service`)
- **Status Code**: `200 OK`
- **Payload**:
  ```json
  {
    "status": "healthy",
    "service": "workline-r5",
    "version": "1.0.0-rc1"
  }
  ```
- **Behavior**: Lightweight process probe that verifies process liveness without calling external vendor APIs, executing live orders, or initiating blockchain transactions.

---

## 5. Security & Internal Endpoints

### 5.1 Internal Endpoints
- `POST /internal/procurement/search`: Multi-vendor catalog search (DigiKey, Mouser, Robu, Robocraze).
- `POST /internal/procurement/quote`: Optimized BOM quote package generation.
- `POST /internal/procurement/orders/plan`: Itemized OrderPlan derivation from BOM.
- `POST /internal/procurement/orders/create`: Order creation and state machine transition.
- `POST /internal/procurement/payments/request`: Non-custodial x402 HTTP 402 payment challenge generation.
- `POST /internal/procurement/payments/verify`: Cryptographic payment signature verification and settlement.

### 5.2 Authentication
- **Header**: `Authorization: Bearer <R5_SERVICE_TOKEN>` (or `X-Workline-Service-Token: <R5_SERVICE_TOKEN>`)
- **Verification**: Constant-time token comparison (`secrets.compare_digest`).
- **Access Control**: R5 is strictly internal and never exposed to the public browser.

---

## 6. Render Environment Variables

| Variable | Description | Type |
| :--- | :--- | :--- |
| `PORT` | Dynamic listener port assigned by Render | System (10005) |
| `WORKLINE_ENV` | Environment identifier (`production`) | Config |
| `R5_SERVICE_TOKEN` | Shared secret token for R1 $\to$ R5 authentication | Secret |
| `R4_INTERNAL_URL` | Internal URL to R4 Engineering Service | Config |
| `R4_SERVICE_TOKEN` | Shared secret token for R5 $\to$ R4 calls | Secret |
| `R3_INTERNAL_URL` | Internal URL to R3 Knowledge Service | Config |
| `R3_SERVICE_TOKEN` | Shared secret token for R5 $\to$ R3 calls | Secret |
| `WORKLINE_X402_ENABLED` | Enable x402 payment provider (`true`) | Config |
| `WORKLINE_X402_NETWORK` | Payment settlement network (`base-sepolia`) | Config |
| `WORKLINE_X402_ASSET` | Settlement asset (`USDC`) | Config |
| `WORKLINE_X402_PAYMENT_ADDRESS`| Treasury recipient address | Secret |

---

## 7. Failure Isolation & Rollback
- **R1 Isolation**: If R5 is restarting or offline, R1 handles downtime gracefully via [`backend/services/r5_client.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/services/r5_client.py) returning `503 Service Unavailable` without crashing.
- **Rollback**: Select the previous deployment commit in Render and click **Rollback**.
