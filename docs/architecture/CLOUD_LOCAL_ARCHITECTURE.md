# Workline Cloud & Local Runtime Architecture

**Document Version**: 1.0.0-rc1  
**Audit Date**: 2026-08-23  

---

## 1. Architectural Philosophy: **ONE WORKLINE, TWO MODES**

The Workline platform supports **two execution modes exclusively**:
1. **CLOUD MODE**: Distributed microservice orchestration for multi-tenant web access, large-scale agent research, and collaborative enterprise procurement.
2. **LOCAL MODE**: Zero-latency, workstation-native execution where the `wline` CLI and Python SDK operate directly on `.wlipjt` archives, local Git, and local Qdrant/SurrealDB instances.

There are no distinct "cli mode", "fully local mode", or "desktop mode" concepts. The CLI (`wline`) **IS** the local runtime execution interface.

---

## 2. Cloud Mode Topology

```
                           NETLIFY
                      (Next.js Frontend)
                              │
                        HTTPS REST / BFF
                              │
                              ▼
                   RENDER R1: CORE API GATEWAY
                            (:10000)
                              │
     ┌──────────────┬─────────┴─────────┬──────────────┐
     ▼              ▼                   ▼              ▼
 R2: AI /       R3: Knowledge /     R4: Eng /      R5: Procurement /
 Research        Documents          Simulation       Collaboration
 (:10002)        (:10003)            (:10004)          (:10005)
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
    SurrealDB Cloud       Qdrant Cloud
```

- **Frontend Tier (Netlify)**: Next.js 16 App Router pages and Clerk authentication proxy deployed on Netlify.
- **Microservices (Render R1–R5)**: Dedicated FastAPI containers for routing (R1), LLM reasoning (R2), knowledge & databases (R3), physics/PINN solvers (R4), and BOM/procurement (R5).
- **Databases**: SurrealDB and Qdrant managed via R3 internal APIs.

---

## 3. Local Mode Topology

```
                         USER WORKSTATION
                                │
                            wline CLI
                                │
                           Python SDK
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
         Local Qdrant    Local SurrealDB    Local Tools
         (or In-Memory)   (or SQLite)       (DRC, Git)
               │                │                │
               └────────────────┼────────────────┘
                                │
                         .wlipjt Project
                                │
                            Local Git
```

- **Execution Boundary**: Runs 100% locally on the developer's laptop or workstation.
- **Local Stores**: Local Qdrant embeddings (`fastembed`), local SurrealDB / SQLite fallback (`user_storage.db`), and `.wlipjt` project archive format.
- **Offline Guarantee**: Basic project initialization, local Git version control, BOM calculation, DRC geometry evaluation, and doctor diagnostics run seamlessly without internet connectivity.

---

## 4. Python SDK Unified Abstraction

```python
from workline import Workline

# 1. Local Mode Execution
wl_local = Workline(mode="local")
results = await wl_local.search_knowledge("TPS62130 power derating")

# 2. Cloud Mode Execution
wl_cloud = Workline(
    mode="cloud",
    api_url="https://api.workline.dev",
    token="wl_sec_..."
)
cloud_results = await wl_cloud.search_knowledge("TPS62130 power derating")
```

### Store Abstraction Hierarchy
- `KnowledgeStore` $\to$ `LocalKnowledgeStore` (Local Qdrant) / `CloudKnowledgeStore` (R1 Gateway API).
- `GraphStore` $\to$ `LocalGraphStore` (Local SurrealDB) / `CloudGraphStore` (R1 Gateway API).
- `ProjectStore` $\to$ Local `.wlipjt` serialization / Cloud workspace synchronization.

---

## 5. Security & Credential Isolation

- **Browser & Frontend**: Zero administrative database credentials, API keys, or wallet private keys exposed to client bundles (`NEXT_PUBLIC_*`).
- **CLI Workstation**: Stores user-scoped bearer tokens in `~/.workline/config.json` without storing backend service credentials.
- **Database Boundary**: Direct browser access to SurrealDB and Qdrant is blocked; all operations are mediated by authenticated backend APIs.
