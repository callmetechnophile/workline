# Workline Build & Deployment Size Report

**Measurement Date**: 2026-08-23  
**Measurement Method**: Direct filesystem inspection of production builds and environment closures.

---

## 1. Measured Size Overview

```
============================================================
WORKLINE SIZES & DEPLOYMENT FOOTPRINT
============================================================
Repository Total Size:             882.14 MB
Frontend Source (frontend/src):      0.81 MB
Frontend Public (frontend/public):   0.76 MB
Root node_modules:                 494.55 MB
Frontend node_modules:               2.18 MB
Total .next Build Output:           15.00 MB
Static Assets (.next/static):        1.39 MB
Server Output (.next/server):       12.68 MB
Backend Source (backend/):          17.36 MB
CLI Source (cli/):                   0.54 MB
Python Environment (.venv):        345.28 MB
============================================================
```

---

## 2. Vercel Function & Frontend Bundle Analysis

- **Vercel Total Deployment Output (`BUILD_SIZE_MB`)**: **15.00 MB**
- **Vercel Static Assets (`.next/static`)**: **1.39 MB**
- **Vercel Server Prerender / Pages (`.next/server`)**: **12.68 MB**
- **Vercel Serverless Function Limit**: 50 MB (compressed) / 250 MB (uncompressed)
- **Status**: **PASS (Well within Vercel limits — ~6% of max threshold)**

---

## 3. Python Dependency Closure & Largest Packages

| Dependency Name | Measured Size (MB) | Purpose |
| :--- | :--- | :--- |
| **`onnxruntime`** | 43.44 MB | FastEmbed & PINN neural inference acceleration |
| **`google` (google-genai, protobuf)** | 34.56 MB | Gemini 2.0 multi-agent research and reasoning |
| **`numpy`** | 31.20 MB | Numerical tensor operations & matrix solvers |
| **`numpy.libs`** | 20.09 MB | Compiled BLAS / LAPACK linear algebra binaries |
| **`PIL` (Pillow)** | 15.43 MB | Datasheet diagram & PCB visual rendering |
| **`grpc`** | 12.67 MB | Qdrant gRPC high-throughput vector ingestion |
| **`surrealdb`** | 11.94 MB | Graph & document database client protocol |
| **`pip`** | 10.84 MB | Environment management |
| **`cryptography`** | 10.59 MB | `.wlipjt` project signing & tamper-evident hashing |
| **`hf_xet`** | 9.06 MB | HuggingFace embedding cache integration |
| **Remaining Packages** | 145.46 MB | FastAPI, Uvicorn, Pydantic, HTTPX, Scrapling, etc. |
| **Total Python Dependency Closure** | **345.28 MB** | Exceeds Vercel Serverless Function 250 MB ceiling |

---

## 4. Container / Podman Image Sizing

| Container Image | Base / Source | Estimated / Stored Image Size | Purpose |
| :--- | :--- | :--- | :--- |
| **`surrealdb/surrealdb:latest`** | Official Alpine | ~68 MB | Graph / Document Database Engine |
| **`qdrant/qdrant:latest`** | Official Debian-slim | ~125 MB | High-performance Vector DB Engine |
| **`workline-backend:1.0.0-rc1`** | `python:3.11-slim` | ~580 MB | FastAPI gateway, agents, PINN, PCB solvers |
