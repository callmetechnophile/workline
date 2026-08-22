# Workline Vercel Frontend Deployment Specification

**Document Version**: 1.0.0-rc1  
**Target Platform**: Vercel Edge / Serverless  
**Component**: `frontend/` (Next.js 16.2.9 / React 19.2.4)  
**Status**: **VERCEL PREVIEW READY (R1 CONNECTION PENDING)**  

---

## 1. Vercel Project Configuration

| Attribute | Value |
| :--- | :--- |
| **Project Name** | `workline` / `armourflow` |
| **Repository** | `callmetechnophile/workline` |
| **Root Directory** | `frontend/` (or repository root with workspace build) |
| **Framework Preset** | `Next.js` |
| **Package Manager** | `npm` (Lockfile: `package-lock.json`) |
| **Node.js Version** | `20.x` |
| **Build Command** | `npm run build` (`next build`) |
| **Install Command** | `npm install` |
| **Output Directory** | `.next` |

---

## 2. Environment Variable Matrix

| Variable | Scope | Safe for Browser? | Purpose / Value |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Client / Edge | **YES** | Target Render R1 Core Gateway URL (Default: `http://localhost:10000`) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Client / Edge | **YES** | Clerk client authentication key |
| `CLERK_SECRET_KEY` | Server Edge | **NO (Private)** | Clerk backend session verification secret |

> [!CAUTION]
> Privileged credentials (Qdrant admin tokens, SurrealDB credentials, GitHub personal access tokens, x402 wallet keys, supplier secrets) must **NEVER** be configured on Vercel or exposed under `NEXT_PUBLIC_*`.

---

## 3. Measured Build Footprint

| Layer / Directory | Measured Disk Size | Status |
| :--- | :--- | :--- |
| **Frontend Source (`frontend/src`)** | `0.81 MB` | Lightweight |
| **Frontend Public (`frontend/public`)** | `0.76 MB` | Lightweight |
| **Next.js Static (`.next/static`)** | `1.39 MB` | Optimized |
| **Next.js Server (`.next/server`)** | `12.68 MB` | Optimized |
| **Total `.next` Build Output** | **`15.00 MB`** | **100% Target Met** |

---

## 4. Frontend-to-Backend Architecture Boundary

```
  VERCEL EDGE (Next.js 16)
        │
        ▼ (HTTPS / JSON REST)
  RENDER R1: Core Gateway (:10000)
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
  R2 (AI / Research)    R3 (Knowledge DB)      R4 (Engineering)
```

- **Centralized API Client**: Located at `frontend/src/lib/api.ts`.
- **R1 Dependency**: In Preview/Production, the frontend communicates strictly through `NEXT_PUBLIC_API_URL` pointing to R1 Core Gateway. Direct client connections to internal microservices (R2–R5) or cloud databases are blocked by design.

---

## 5. Deployment Procedures

### A. Preview Deployment (Automated via GitHub CI / Vercel Bot)
Every pull request or commit pushed to `main` automatically triggers Vercel Preview generation.

### B. Production Deployment Procedure
1. Verify `npm run typecheck`, `npm run lint`, and `npm run build` pass with 0 errors.
2. Ensure Render R1 Gateway is provisioned and responsive at its public HTTPS URL.
3. In Vercel Project Settings $\to$ Environment Variables $\to$ set `NEXT_PUBLIC_API_URL=https://<your-r1-service>.onrender.com`.
4. Promote deployment to Production.

### C. Rollback Procedure
In the Vercel Dashboard, select **Deployments** $\to$ choose previous successful deployment $\to$ click **Instant Rollback**.
