# Workline Deployment Architecture Specification

## 1. Overview & Architectural Boundary

The Workline platform implements a **Hybrid Edge-Compute Architecture**:
- **Vercel** delivers the global edge presentation tier, Next.js UI rendering, authentication gateways, and API routing.
- **Podman / Containerized Infrastructure** hosts the compute-intensive hardware engineering solvers, graph databases, vector engines, and multi-agent execution pipelines.

```
                    WORKLINE
                       │
          ┌────────────┴────────────┐
          │                         │
       VERCEL                  PODMAN / SERVER
          │                         │
   ┌──────┼────────┐         ┌──────┼─────────┐
   │      │        │         │      │         │
 Next.js FastAPI  API/BFF   Agents  Workers  Services
   │      │        │         │      │         │
   │      │        │        PINN  Simulation  PCB
   │      │        │         │      │         │
   │      │        │         └──────┼─────────┘
   │      │        │                │
   │      │        │        ┌───────┴───────┐
   │      │        │        │               │
   │      │        │    SurrealDB         Qdrant
   │      │        │
   └──────┴────────┴──── HTTPS ──────────────┘
```

---

## 2. Current Architecture Matrix

### A. Vercel Tier (Edge & Frontend)
- **Framework**: Next.js 16 (App Router with Turbopack), React 19.
- **Authentication**: Clerk authentication middleware (`proxy.ts`).
- **Workloads**:
  - Landing & Control Center Dashboard (`/`)
  - Team Workspaces (`/team/[uuid]`)
  - Team Invitations (`/invite/[token]`)
  - Authentication Gateways (`/login`, `/sign-in`, `/sign-up`)
  - Lightweight API / BFF Request Routing
  - Static Asset Delivery (`.next/static` — 1.39 MB)
- **Execution Limits**: Instant sub-second SSR/CSR response, zero heavy Python ML packages in bundle.

### B. Podman / Server Tier (Engineering Backend & Solvers)
- **Runtime**: Python 3.11 FastAPI service (`Dockerfile`), managed via `podman/compose.yml`.
- **Primary Workloads**:
  - **Multi-Agent Research Pipeline**: Deep datasheet crawling, web scraping (`scrapling`), and contradictory constraint detection (5s–120s runtime).
  - **Component & BOM Engine**: Multi-supplier price resolution, part stock checking, risk analysis.
  - **Physics & Simulation**: PINN neural surrogate solvers, thermal conduction modeling, SPICE netlist export.
  - **EDA & PCB Engine**: DRC geometric validation, trace impedance calculation, Gerber/KiCad netlist generation.
  - **Project Packaging**: Tamper-evident `.wlipjt` archive signing (`cryptography`).

### C. Persistent Storage & Databases
- **SurrealDB (`workline-surrealdb`)**: Multi-model graph database (`0.0.0.0:8000` / `8001`), hosting requirements graphs, component relationships, and contradiction topologies.
- **Qdrant (`workline-qdrant`)**: Vector similarity database (`0.0.0.0:6333` / `6334`), indexing datasheet embeddings (`fastembed`, `onnxruntime`).
- **SQLite Fallback (`user_storage.db`)**: Local single-tenant state storage.

---

## 3. Vercel Capability Matrix

| Component / Subsystem | Vercel | Podman | Decision | Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **Next.js UI & Dashboard** | **YES** | NO | **Vercel** | Ultra-fast edge rendering, low TTFB, 15.0 MB production build. |
| **Auth & Clerk Proxy** | **YES** | NO | **Vercel** | Edge middleware session verification and route protection. |
| **Lightweight BFF / Proxies** | **YES** | NO | **Vercel** | Next.js route handlers proxying authenticated HTTPS requests. |
| **x402 Payment & State Routes**| **YES** | YES | **Hybrid** | Verification on Vercel; on-chain settlement on backend worker. |
| **Project Workspace State** | **YES** | YES | **Hybrid** | Read cache on edge; persistent graph storage in SurrealDB. |
| **FastAPI Backend Gateway** | NO | **YES** | **Podman** | 345.28 MB Python dependency closure; exceeds Vercel limits. |
| **SurrealDB Graph DB** | NO | **YES** | **Podman** | Stateful database requiring persistent disk volume and live sockets. |
| **Qdrant Vector DB** | NO | **YES** | **Podman** | Dedicated gRPC/HTTP vector indexing engine with persistent storage. |
| **Multi-Agent Ingestion** | NO | **YES** | **Podman** | Long-running tasks (30s–120s) exceeding serverless execution timeouts. |
| **PINN & Physics Solvers** | NO | **YES** | **Podman** | CPU/GPU intensive tensor computations (`onnxruntime`, `numpy`). |
| **DRC & PCB Validation** | NO | **YES** | **Podman** | Deterministic geometric analysis requiring dedicated RAM and CPU. |

---

## 4. Security & Network Isolation

1. **Zero Direct Browser Access to Databases**:
   - The browser client NEVER establishes direct network connections to SurrealDB (`:8000`) or Qdrant (`:6333`).
   - All database reads/writes are mediated through the authenticated backend API gateway.
2. **Backend Authentication & Token Validation**:
   - All incoming API requests from Vercel to Podman carry validated bearer/session tokens.
3. **Internal Container Networking**:
   - In production, SurrealDB and Qdrant communicate with FastAPI across an isolated container network (`workline-net`).
