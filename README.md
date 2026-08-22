# Workline / ArmourIQ-Workflow

Workline (ArmourIQ-Workflow) is an engineering lifecycle orchestration platform that transforms natural-language system requirements into validated engineering specifications, BOMs, multi-physics simulations, and procurement packages.

> **Status:** Architecture frozen for system testing.

---

## System Architecture

```
Requirements (Natural Language & Documents)
    ↓
Knowledge Graph (SurrealDB + Qdrant + LlamaIndex)
    ↓
Deterministic Engineering Validation Engine (PASS / FAIL / UNKNOWN / CONFLICT)
    ↓
Engineering Design Decision Engine (Trade-offs & Human Approval)
    ↓
BOM + Procurement Intelligence (Part Resolution & x402 Preparation)
    ↓
PCB Design & Multi-Physics Simulation Orchestrator (SPICE, Thermal FD, SI/PI, PINN Surrogate)
    ↓
Cross-Validation & Engineering Review
    ↓
EDA Package & Git Versioning
```

---

## Technology Stack

- **Backend:** Python 3.10+, FastAPI, Pydantic v2, Typer, NumPy, SciPy
- **Frontend:** Next.js, React 19, Tailwind CSS, Lucide Icons, TypeScript
- **Databases & Storage:**
  - **SurrealDB:** Multi-model relational, document, and graph database for project entities, constraints, and audit logs.
  - **Qdrant:** Vector database for semantic datasheet retrieval and design pattern discovery.
- **AI & Reasoning:** Google Agent Development Kit (ADK), Gemini, LlamaIndex for document grounding.
- **Physics & Simulation:**
  - SPICE nodal electrical solver
  - 2D finite-difference steady-state thermal conduction solver
  - Transmission line signal and power integrity (SI/PI) solver
  - Physics-Informed Neural Network (PINN) fast thermal surrogate model
- **Procurement & Payments:** Multi-distributor scrapers (DigiKey, Mouser, Robu, Robocraze), Nexar API, and x402 protocol preparation.
- **VCS & Project Management:** Native Git & GitHub integration with `.wlipjt` deterministic project bundles.

---

## Command Line Interface (`wline`)

Workline provides a command-line interface (`wline`) to operate the complete engineering lifecycle:

```bash
# General & Workspace
wline init
wline project list
wline project open <name>

# Requirements & Validation
wline requirement list
wline component validate <id>

# Decision Support
wline decision compare <id1> <id2>
wline decision approve <id>

# BOM & Procurement
wline bom create
wline bom validate
wline procurement package

# PCB & Multi-Physics Simulation
wline pcb create --width 100 --height 80
wline pcb validate
wline pcb analyze
wline pcb pinn train
wline pcb export --format kicad
```

---

## Multi-Physics Simulation & Cross-Validation

```
PCB DESIGN
    ↓
DESIGN VALIDATION
    ↓
SIMULATION ORCHESTRATOR
    ├── SPICE → electrical
    ├── Thermal Solver → thermal
    ├── SI/PI Solver → signal/power integrity
    └── PINN → fast surrogate prediction
    ↓
RESULT NORMALIZATION
    ↓
CROSS-VALIDATION
    ↓
PASS / FAIL / WARNING / UNKNOWN
    ↓
ENGINEERING REVIEW
```

- Discrepancy thresholds:
  - $\le 5\%$ relative error: `PASS`
  - $5\% - 15\%$ relative error: `WARNING`
  - $> 15\%$ relative error: `FAIL` (Authoritative reference numerical solver takes precedence)

---

## Testing & Verification

- **Automated Regression Suite:** 302 passed out of 302 unit/integration tests (100%).
- **TypeScript Static Verification:** Clean build with 0 type errors.
- **Testing Status:** Baseline frozen for full end-to-end multi-level verification (Level 0 through Phase 10K).

---

## Security & Invariants

- Deterministic numerical decisions are executed by code, not generative models.
- Human engineering review and sign-off are required for architectural decisions, BOM approvals, and PCB releases.
- Multi-tenant tenant/project isolation enforced across all database queries and vector indexes.
- No automated financial order execution without explicit human x402 approval.
