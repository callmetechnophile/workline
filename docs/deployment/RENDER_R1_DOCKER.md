# Workline R1 Core / API Gateway Dockerization Specification

**Document Version**: 1.0.0-rc1  
**Service Name**: `workline-core-gateway`  
**Target Platform**: Render (Docker Runtime)  
**Status**: **R1 DOCKER + RENDER READY**  

---

## 1. Docker Build & Runtime Architecture

```
  GitHub Repository
         │
         ▼
  Render Cloud
         │ (Docker build Context: .)
         ▼
  Docker Engine (python:3.12-slim)
         │
         ▼
  Workline R1 Core Gateway Container (:10000)
         │
         ▼
  Netlify Frontend (https://worklineai.netlify.app)
```

| Parameter | Configuration |
| :--- | :--- |
| **Dockerfile Location** | [`backend/Dockerfile`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/Dockerfile) |
| **Docker Build Context** | `.` (Repository Root) |
| **Base Image** | `python:3.12-slim` |
| **Non-Root User** | `workline` (UID: 1000) |
| **Listening Port** | `0.0.0.0:$PORT` (Default: `10000`) |
| **Health Check Path** | `GET /health` |
| **Declared Footprint** | `~35 MB` (Dependencies) / `<160 MB` (Compressed Slim Container) |

---

## 2. Dockerfile Specification

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=10000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend

RUN useradd -m -u 1000 workline && \
    chown -R workline:workline /app

USER workline

EXPOSE 10000

CMD ["sh", "-c", "uvicorn backend.services.core.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
```

---

## 3. Dependency Isolation & Exclusions

The R1 Docker container exclusively bundles lightweight Core Gateway dependencies:
- **Included**: `fastapi`, `uvicorn`, `pydantic`, `httpx`, `cryptography`, `python-jose`, `python-multipart`, `aiosqlite`, `loguru`.
- **Strictly Excluded**: `torch`, `tensorflow`, `scipy`, `numpy`, `docling`, `spacy`, `llama-index`, `qdrant-client`, `surrealdb`, `onnxruntime`.

---

## 4. Local Execution & Validation

### Build Container Locally
```bash
docker build -t workline-r1 -f backend/Dockerfile .
```

### Run Container Locally
```bash
docker run -d --name workline-r1-dev -p 10000:10000 -e PORT=10000 workline-r1
```

### Health Check Verification
```bash
curl -i http://localhost:10000/health
```
**Expected Response (HTTP 200)**:
```json
{
  "status": "healthy",
  "service": "workline-core-gateway",
  "version": "1.0.0-rc1",
  "downstream": {
    "r2_ai": "http://localhost:10002",
    "r3_knowledge": "http://localhost:10003",
    "r4_engineering": "http://localhost:10004",
    "r5_procurement": "http://localhost:10005"
  }
}
```

---

## 5. Render Infrastructure-as-Code Configuration

In [`render.yaml`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/render.yaml):
```yaml
services:
  - type: web
    name: workline-core-gateway
    env: docker
    dockerfilePath: backend/Dockerfile
    dockerContext: .
    region: oregon
    plan: starter
    healthCheckPath: /health
    envVars:
      - key: PORT
        value: 10000
      - key: WORKLINE_CORS_ORIGINS
        value: "https://worklineai.netlify.app,http://localhost:3000"
      - key: WORKLINE_R2_URL
        value: http://workline-ai-agents:10002
      - key: WORKLINE_R3_URL
        value: http://workline-knowledge-documents:10003
      - key: WORKLINE_R4_URL
        value: http://workline-engineering-simulation:10004
      - key: WORKLINE_R5_URL
        value: http://workline-procurement-service:10005
```

---

## 6. Security & Audit Verification

1. **No Embedded Secrets**: `.dockerignore` prevents `.env`, `.env.*`, certificates, and keys from being copied into the container context.
2. **Non-Root Execution**: Container runs under unprivileged UID `1000` (`workline`).
3. **Environment-Driven Injection**: All production configurations and secrets are injected strictly at runtime via Render Environment Variables.
