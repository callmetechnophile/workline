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

## 5. Security & Authentication
- **Service-to-Service Token**: `WORKLINE_SERVICE_AUTH_KEY`
- Requests from R1 to R2 must include the HTTP header:
  ```http
  X-Workline-Service-Token: <WORKLINE_SERVICE_AUTH_KEY>
  ```
- **CORS Policy**: Browser origins are strictly restricted. All public browser traffic must enter through R1 Gateway.

---

## 6. Render Environment Variables

| Variable | Description | Type |
| :--- | :--- | :--- |
| `PORT` | Dynamic listener port assigned by Render | System (10002) |
| `WORKLINE_ENV` | Environment identifier (`production`) | Config |
| `WORKLINE_SERVICE_AUTH_KEY` | Shared secret token for R1 $\to$ R2 authentication | Secret |
| `GROQ_API_KEY` | API Key for Groq ultra-fast Llama-3 / Mixtral inference | Secret |
| `SARVAM_API_KEY` | API Key for Sarvam speech-to-text transcription | Secret (Optional) |

---

## 7. Failure Isolation & Rollback
- **R1 Isolation**: If R2 is offline or restarting, R1 continues running and returns a controlled `503 Service Unavailable` on research routes without crashing.
- **Rollback**: To roll back R2, select the previous successful build commit in the Render dashboard and trigger **Rollback**.
