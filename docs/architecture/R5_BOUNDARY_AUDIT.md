# Workline R5 Service Boundary Audit

## Service Identification
- **Service Name**: `workline-r5` (`workline-procurement-service`)
- **Service Role**: Internal Component Intelligence, Multi-Vendor Sourcing, BOM Optimization, Order State Machine, and Cryptographic x402 Payment Authorization
- **Deployment Model**: Render Web Service (Docker Runtime)
- **Exposure**: Internal Private Network / Authenticated Service API (R1 Gateway Gatewayed)

---

## 1. R5 Module Inventory & Responsibility Map

| Module Path | Primary Purpose | Dependencies | R5 Responsibility | Status |
| :--- | :--- | :--- | :--- | :--- |
| [`backend/workline/procurement/search.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/procurement/search.py) | Multi-vendor component search engine across DigiKey, Mouser, Robu, and Robocraze | `httpx`, `pydantic` | Sourcing & Discovery | ✅ Active |
| [`backend/workline/procurement/engine.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/procurement/engine.py) | BOM package optimization, price normalization & supplier quote consolidation | `pydantic` | Procurement Intelligence | ✅ Active |
| [`backend/workline/orders/service.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/orders/service.py) | Central ordering orchestrator, approval policy validator & lifecycle manager | `pydantic`, `cryptography` | Order State Machine | ✅ Active |
| [`backend/workline/orders/payment/x402.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/orders/payment/x402.py) | HTTP 402 Payment Required challenge generation & facilitator proof verification | `httpx`, `pydantic` | x402 Protocol Provider | ✅ Active |
| [`backend/workline/orders/payment/verification.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/orders/payment/verification.py) | Cryptographic signature and receipt verification | `cryptography` | Payment Settlement | ✅ Active |
| [`backend/workline/api/procurement.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/procurement.py) | Sourcing, search, validation and BOM optimization REST API | `fastapi`, `pydantic` | Public Internal API | ✅ Active |
| [`backend/workline/api/orders.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/orders.py) | OrderPlan creation, human approval & order status REST API | `fastapi`, `pydantic` | Public Internal API | ✅ Active |
| [`backend/workline/api/payments.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/payments.py) | x402 payment session status and verification REST API | `fastapi`, `pydantic` | Public Internal API | ✅ Active |

---

## 2. Service Boundary Enforcement

### What R5 Owns:
1. **Component Intelligence & Sourcing**: Sourcing vendor adapters (DigiKey, Mouser, Robu, Robocraze), real-time pricing and stock availability queries.
2. **BOM Procurement Optimization**: Matching engineering BOM parts to vendor catalogs and generating cost-optimized procurement plans.
3. **Order State Machine**: Strict legal transition management:
   `DRAFT` $\to$ `QUOTED` $\to$ `PENDING_APPROVAL` $\to$ `APPROVED` $\to$ `PAYMENT_PENDING` $\to$ `PAID` / `PAYMENT_VERIFIED` $\to$ `PROCESSING` $\to$ `ORDERED` / `COMPLETED`.
4. **x402 Payment Protocol**: Non-custodial HTTP 402 challenge generation, facilitator session coordination, and cryptographic signature proof verification.
5. **Procurement Security**: Isolated containment of supplier API keys and payment treasury addresses.

### What R5 DOES NOT Own (Excluded from R5 Container):
- ❌ **Frontend UI**: Next.js App Router (owned by Netlify).
- ❌ **Public Gateway**: Clerk JWT authentication, CORS, rate limits (owned by R1).
- ❌ **AI Model Orchestration & Prompts**: Multi-agent reasoning (owned by R2).
- ❌ **Database Administration**: Vector embeddings & multi-model graph persistence (owned by R3).
- ❌ **Engineering & PINN Physics**: PCB DRC, SPICE, thermal simulation (owned by R4).

---

## 3. Communication & Data Flow
```
[User / Frontend]
       │
       ▼ (Public HTTPS)
[R1 Core Gateway]
       │
       ▼ (Internal HTTP + Authorization: Bearer <R5_SERVICE_TOKEN>)
[R5 Procurement & x402]
   ├── Sourcing & Vendor Search (DigiKey / Mouser / Robu / Robocraze)
   ├── Pricing Normalization & Cost Optimization Engine
   ├── Order Lifecycle State Machine
   └── Non-Custodial x402 Payment Authorization
```
