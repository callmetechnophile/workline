# Workline Netlify Frontend Deployment Specification

**Document Version**: 1.0.0-rc1  
**Target Platform**: Netlify Edge / Serverless (Next.js Runtime)  
**Component**: `frontend/` (Next.js 16.2.9 / React 19.2.4)  
**Status**: **NETLIFY PREVIEW READY (R1 CONNECTION PENDING)**  

---

## 1. Netlify Project Configuration

| Attribute | Value |
| :--- | :--- |
| **Site Name** | `workline` / `armourflow` |
| **Repository** | `https://github.com/callmetechnophile/workline` |
| **Base Directory** | `frontend` |
| **Build Command** | `npm run build` (`next build`) |
| **Publish Directory** | `.next` |
| **Node Version** | `20.x` |
| **Next.js Integration** | `@netlify/plugin-nextjs` |

Configuration file: [`netlify.toml`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/netlify.toml)
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = ".next"

[build.environment]
  NODE_VERSION = "20"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

---

## 2. Environment Variable Matrix

| Variable | Scope | Safe for Browser? | Value / Purpose |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Client / Edge | **YES** | `http://localhost:10000` (Dev) / `PENDING_R1_DEPLOYMENT` (Prod) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Client / Edge | **YES** | Clerk client authentication publishable key |
| `CLERK_SECRET_KEY` | Server Edge | **NO (Private)** | Server-side Clerk token verification secret |

> [!CAUTION]
> Privileged credentials (Qdrant admin tokens, SurrealDB credentials, GitHub personal access tokens, x402 wallet keys, supplier secrets) must **NEVER** be configured on Netlify or exposed under `NEXT_PUBLIC_*`.

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
  NETLIFY (Next.js 16)
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

### A. Preview Deployment (Netlify Deploy Preview)
Every pull request or commit pushed to `main` automatically triggers Netlify Deploy Preview generation via Netlify GitHub App / webhook.

### B. Production Deployment Procedure
1. Verify `npm run typecheck`, `npm run lint`, and `npm run build` pass with 0 errors.
2. Ensure Render R1 Gateway is provisioned and responsive at its public HTTPS URL.
3. In Netlify Site Settings $\to$ Environment Variables $\to$ set `NEXT_PUBLIC_API_URL=https://<your-r1-service>.onrender.com`.
4. Trigger Production deploy.

### C. Rollback Procedure
In the Netlify Dashboard, select **Deploys** $\to$ choose previous successful deploy $\to$ click **Publish deploy**.
