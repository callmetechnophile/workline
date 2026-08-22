# Workline Multi-Render Architecture & Service Extraction Plan

**Document Version**: 1.0.0-rc1  
**Audit Date**: 2026-08-23  

---

## 1. Executive Summary

This document specifies the step-by-step extraction plan for decomposing the monolithic Workline backend into **5 specialized Render microservices** (R1 through R5), fronted by Vercel for the presentation tier.

```
                    WORKLINE EDGE (Vercel)
                              │
                              ▼ (HTTPS / API Route)
                 RENDER R1: Core API Gateway (:10000)
                              │
     ┌──────────────┬─────────┴─────────┬──────────────┐
     ▼              ▼                   ▼              ▼
 R2: AI /       R3: Knowledge /     R4: Eng /      R5: Procurement /
 Research        Documents          Simulation       Collaboration
 (:10002)        (:10003)            (:10004)          (:10005)
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
    SurrealDB (:8000)     Qdrant (:6333)
```

---

## 2. Multi-Render Service Specifications

| Service | Name | Responsibilities | Dedicated Dependencies | Est. Bundle Size | Memory (Min / Peak) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | `workline-core` | API Gateway, Auth, Project Archive | `fastapi`, `python-jose`, `cryptography` | ~35 MB | 256 MB / 512 MB |
| **R2** | `workline-ai` | Deep Research, OmniRoute, Agents | `google-genai`, `sarvamai`, `scrapling` | ~65 MB | 512 MB / 1024 MB |
| **R3** | `workline-knowledge` | SurrealDB Graph, Qdrant Vectors, PDF Parsing | `surrealdb`, `qdrant-client`, `fastembed`, `docx` | ~140 MB | 1024 MB / 2048 MB |
| **R4** | `workline-engineering` | PINN Physics, DRC Rules, PCB Netlists | `numpy`, `onnxruntime`, `pydantic` | ~110 MB | 512 MB / 1024 MB |
| **R5** | `workline-procurement`| BOM Line Items, Vendor Quotes, x402 | `fastapi`, `httpx`, `cryptography` | ~30 MB | 256 MB / 512 MB |

---

## 3. Safe Extraction Sequence

1. **Step 1: Extract R5 (Procurement & Collaboration)** *(Lowest coupling, self-contained schemas, zero heavy ML)*.
2. **Step 2: Extract R2 (AI & Research Agents)** *(Isolates LLM prompt loops and web scraping timeouts)*.
3. **Step 3: Extract R4 (Engineering & Simulation)** *(Isolates tensor math and DRC validation)*.
4. **Step 4: Extract R3 (Knowledge & Databases)** *(Encapsulates SurrealDB and Qdrant connections)*.
5. **Step 5: Stabilize R1 (Core Gateway)** *(Acts purely as a routing facade and session verifier)*.

---

## 4. Rollback & Failover Strategy

- If any Render microservice experiences degraded health, R1 API Gateway intercepts the HTTP 503 / timeout and gracefully responds with cached local data or synthetic fallback without crashing the client UI.
- All services maintain backward-compatible OpenAPI schemas.
