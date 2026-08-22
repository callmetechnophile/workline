# Workline — Render Deployment Guide: R2 AI / Agents / Research

## 1. Overview & Service Responsibilities
**R2 (`workline-ai-agents`)** is the internal worker microservice responsible for multi-agent reasoning, deep research pipelines, datasheet extraction, multimodal hardware generation, and speech transcription.

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
             internal authenticated HTTP
             (X-Workline-Service-Token)
                       |
                       v
              +-------------------+
              |    R2 AI/AGENTS   |
              |     RESEARCH      |  (Render Docker - Internal Worker)
              +-------------------+
                 |       |      |
             Google    Sarvam  Scrapling
              GenAI      AI    Research
```

---

## 2. Docker Configuration
- **Dockerfile**: [`backend/r2/Dockerfile`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r2/Dockerfile)
- **Build Context**: Repository Root (`.`)
- **Base Image**: `python:3.12-slim`
- **Runtime User**: `workline` (UID 1000)
- **Default Port**: Dynamic Render `$PORT` (Defaults to `10002`)
- **Startup Command**: `uvicorn backend.r2.main:app --host 0.0.0.0 --port ${PORT:-10002}`

---

## 3. Dependency Closure & Footprint
- **Requirements File**: [`backend/r2/requirements.txt`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/r2/requirements.txt)
- **Target Dependencies**:
  - `fastapi`, `uvicorn`, `pydantic`
  - `google-genai` (Google Gemini reasoning & parametric extraction)
  - `sarvamai` (Speech-to-Text audio processing)
  - `scrapling` (Scientific paper & datasheet retrieval)
  - `httpx`, `python-dotenv`, `python-jose`, `orjson`, `loguru`
- **Estimated Footprint**: ~65 MB dependency closure (excluding large PyTorch, ONNX, and heavy database packages).

---

## 4. Health Check Endpoint
- **Path**: `GET /health`
- **Status Code**: `200 OK`
- **Payload**:
  ```json
  {
    "status": "healthy",
    "service": "workline-r2",
    "version": "1.0.0-rc1"
  }
  ```
- **Behavior**: Lightweight process probe that never calls external AI providers or remote URLs.

---

## 5. Security & Internal Endpoints

### 5.1 Internal Research Endpoint
- **Path**: `POST /internal/research`
- **Authentication**: `Authorization: Bearer <R2_SERVICE_TOKEN>`
- **Request Headers**:
  - `Authorization: Bearer <R2_SERVICE_TOKEN>`
  - `X-Request-ID: <trace-id>` (optional, propagated for telemetry)
- **Request Body**: [`ResearchRequest`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/schemas/research_schemas.py) (`intent: str`, `target_days: int`)
- **Response**: [`ResearchResponse`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/schemas/research_schemas.py)
- **Error Codes**:
  - `401 Unauthorized`: Missing or invalid Bearer token
  - `422 Unprocessable Entity`: Empty or malformed payload
  - `500 Internal Server Error`: Controlled pipeline execution error without secret leakage

### 5.2 CORS & Access Control
- **CORS Policy**: Browser origins are strictly restricted. Public frontend clients cannot directly reach R2.
- **R1 Boundary**: R1 Core Gateway proxies requests to R2 using internal service authentication.

---

## 6. Render Environment Variables

| Variable | Description | Type |
| :--- | :--- | :--- |
| `PORT` | Dynamic listener port assigned by Render | System (10002) |
| `WORKLINE_ENV` | Environment identifier (`production`) | Config |
| `R2_SERVICE_TOKEN` | Secret token for R1 $\to$ R2 authentication | Secret |
| `GROQ_API_KEY` | API Key for Groq ultra-fast Llama-3 / Mixtral inference | Secret |
| `SARVAM_API_KEY` | API Key for Sarvam speech-to-text transcription | Secret (Optional) |

---

## 7. Failure Isolation & Rollback
- **R1 Isolation**: If R2 is offline or restarting, R1 continues running and returns a controlled `503 Service Unavailable` on research routes without crashing.
- **Rollback**: To roll back R2, select the previous successful build commit in the Render dashboard and trigger **Rollback**.
