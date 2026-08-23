# Workline R4 Service Boundary Audit

## Service Identification
- **Service Name**: `workline-r4` (`workline-engineering-simulation`)
- **Service Role**: Internal Engineering Computation, PINN Physics Solvers, Thermal Modeling, PCB DRC Validation & Architecture Decision Support
- **Deployment Model**: Render Web Service (Docker Runtime)
- **Exposure**: Internal Private Network / Authenticated Service API (R1 Gateway Gatewayed)

---

## 1. R4 Module Inventory & Engineering Ownership Map

| Module Path | Primary Purpose | Dependencies | R4 Responsibility | Status |
| :--- | :--- | :--- | :--- | :--- |
| [`backend/workline/validation/units.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/validation/units.py) | Unit Conversion Engine across electrical, thermal, power, and physical dimensions | `pydantic` | Unit Normalization & Precision | ✅ Active |
| [`backend/workline/validation/service.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/validation/service.py) | Requirement parsing, conflict detection & candidate component validation (10F) | `pydantic` | Requirement Validation Engine | ✅ Active |
| [`backend/workline/decision/tradeoffs.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/decision/tradeoffs.py) | Multi-criteria decision matrix scoring, Pareto frontier analysis & trade-offs (10H) | `pydantic`, `numpy` | Engineering Decision Support | ✅ Active |
| [`backend/workline/pcb/engine/validation.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/pcb/engine/validation.py) | PCB design rule checking (DRC), clearance, trace width & electrical constraints (10I) | `pydantic` | Geometric DRC Engine | ✅ Active |
| [`backend/workline/pcb/pinn/inference.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/pcb/pinn/inference.py) | Fast batch PINN forward pass predicting 2D board temperature fields (10J) | `numpy`, `pydantic` | Physics-Informed Neural Surrogates | ✅ Active |
| [`backend/workline/pcb/physics/solver.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/pcb/physics/solver.py) | 2D finite-difference heat diffusion baseline solver & boundary condition validator | `numpy` | Reference Numerical Physics | ✅ Active |
| [`backend/workline/pcb/services/pcb_service.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/pcb/services/pcb_service.py) | Authoritative PCB project lifecycle & board stackup management | `pydantic` | PCB Project Orchestration | ✅ Active |
| [`backend/workline/api/pcb.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/pcb.py) | PCB routing, layout optimization & PINN training/inference REST API | `fastapi`, `pydantic` | Public Internal API | ✅ Active |
| [`backend/workline/validation/api.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/validation/api.py) | Requirement validation & candidate component comparison REST API | `fastapi`, `pydantic` | Public Internal API | ✅ Active |
| [`backend/workline/decision/api.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/decision/api.py) | Engineering decision creation, scoring & sensitivity REST API | `fastapi`, `pydantic` | Public Internal API | ✅ Active |

---

## 2. Service Boundary Enforcement

### What R4 Owns:
1. **Engineering Computation**: Unit conversion (10G), mathematical constraint evaluation, numerical physics.
2. **Requirement Validation (10F)**: Category-based requirement parsing, missing constraint detection, candidate component validation.
3. **Decision Support & Trade-offs (10H)**: Multi-criteria sensitivity matrices, weighted scoring, alternative component trade-off evaluation.
4. **PCB Geometric Validation & DRC (10I)**: Trace clearance, component overlap, net connectivity, keepout violations.
5. **PINN & Thermal Multi-Physics (10J)**: Physics-Informed Neural Network forward inference, component hotspot identification, 2D temperature grid evaluation.

### What R4 DOES NOT Own (Excluded from R4 Container):
- ❌ **Frontend UI**: Next.js App Router (owned by Netlify).
- ❌ **AI Agent Orchestration & LLM Prompting**: Google Gemini / Groq reasoning pipelines (owned by R2).
- ❌ **Vector & Graph Database Administration**: Qdrant vector database & SurrealDB graph database (owned by R3).
- ❌ **Procurement & x402 Payments**: Vendor ordering, escrow, and supplier APIs (owned by R5).
- ❌ **Public Gateway**: Clerk JWT authentication, public CORS routing (owned by R1).

---

## 3. Communication & Data Flow
```
[User / Frontend]
       │
       ▼ (Public HTTPS)
[R1 Core Gateway]
       │
       ▼ (Internal HTTP + Authorization: Bearer <R4_SERVICE_TOKEN>)
[R4 Engineering & Simulation]
   ├── Requirement & Constraint Engine (10F)
   ├── Unit Conversion Precision Layer (10G)
   ├── Trade-off & Decision Matrix Solver (10H)
   ├── PCB DRC & Geometric Analyzer (10I)
   └── PINN Neural Thermal Surrogate (10J)
```
