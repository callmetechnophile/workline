# Workline Backend Import Graph & Coupling Analysis

**Audit Date**: 2026-08-23  
**Modules Scanned**: 770 Python files across `backend/` and `cli/`

---

## 1. Domain Import Graph & Service Boundaries

```mermaid
graph TD
    subgraph R1_CORE [R1 - Core Gateway]
        Gateway["backend.main / app"]
        Auth["backend.auth"]
        Workspace["backend.routes.workspace"]
        Collab["backend.routes.collaboration"]
        ProjectPack["backend.workline.api.project"]
    end

    subgraph R2_AI [R2 - AI & Research Agents]
        Research["backend.routes.research"]
        Agents["backend.workline.api.agents"]
        GenAI["backend.workline.api.generation"]
        Scrapling["scrapling / search"]
    end

    subgraph R3_KNOWLEDGE [R3 - Knowledge & Documents]
        GraphExplorer["backend.routes.graph_explorer"]
        SurrealDB["backend.workline.database.surrealdb"]
        Qdrant["backend.workline.retrieval.qdrant"]
        Docs["backend.workline.documents.api"]
    end

    subgraph R4_ENGINEERING [R4 - Engineering & Simulation]
        PINN["backend.routes.packages (PINN)"]
        PCB["backend.workline.api.pcb"]
        Validation["backend.workline.validation.api"]
        DecisionEngine["backend.workline.decision.api"]
    end

    subgraph R5_PROCUREMENT [R5 - Procurement & Collab]
        BOM["backend.workline.api.bom"]
        Procurement["backend.workline.api.procurement"]
        Orders["backend.workline.api.orders"]
        Payments["backend.workline.api.payments (x402)"]
        Calendar["backend.routes.calendar"]
        GitSync["backend.workline.api.git"]
    end

    Gateway --> R2_AI
    Gateway --> R3_KNOWLEDGE
    Gateway --> R4_ENGINEERING
    Gateway --> R5_PROCUREMENT

    R2_AI -.->|Semantic Query| R3_KNOWLEDGE
    R4_ENGINEERING -.->|Component Constraints| R3_KNOWLEDGE
    R5_PROCUREMENT -.->|BOM Line Items| R4_ENGINEERING
```

---

## 2. Cross-Domain Coupling Findings

1. **Low-Coupling Periphery (R5 - Procurement & Orders)**:
   - `backend/workline/api/bom.py`, `backend/workline/api/procurement.py`, `backend/workline/api/orders.py`, and `backend/workline/api/payments.py` operate on self-contained schemas (`BOMItem`, `SupplierQuote`, `x402State`).
   - Zero dependencies on heavy ML or tensor libraries (`onnxruntime`, `torch`, `docling`).
   - **Extraction Risk**: **LOW**. Ideal candidate for first service extraction.

2. **Compute-Coupled Subsystems (R4 - Engineering vs R2 - AI)**:
   - R4 uses `numpy` for matrix transformations and derating equations.
   - R2 uses `google-genai`, `sarvamai`, and `scrapling` for prompt orchestration.
   - Both communicate through structured JSON contracts rather than shared in-memory object references.

3. **Shared Database Layer (R3 - Knowledge)**:
   - SurrealDB and Qdrant client connection managers are encapsulated within `backend/workline/database/surrealdb.py` and `backend/workline/retrieval/qdrant.py`.
   - Isolating R3 behind internal HTTP/gRPC endpoints allows other services to query knowledge graphs without directly managing database sockets.
