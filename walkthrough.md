# Workline — Phase 10E: Engineering Knowledge Graph + Entity Resolution Walkthrough

Phase 10E introduces a provenance-aware **Engineering Knowledge Graph & Prioritized Entity Resolution Engine** linking documents, components, manufacturers, specifications, requirements, decisions, BOM items, and research concepts across **SurrealDB**, **Qdrant**, and **KnowledgeCache**.

---

## 1. Architectural Role Separation

```
                         DOCUMENTS
                             │
                             ▼
                          DOCLING
                 (Structural Ingestion)
                             │
                             ▼
                           spaCy
                  (Entity Extraction)
                             │
                             ▼
                      ENTITY MENTIONS
                             │
                             ▼
                     ENTITY RESOLVER
         (Exact -> Mfr+MPN -> Alias -> UNRESOLVED)
                             │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
           SURREALDB                    QDRANT
      Authoritative Graph           Semantic Search
  (Entities, Edges, Specs,
    Conflicts, Decisions)
               │                           │
               └─────────────┬─────────────┘
                             │
                             ▼
                     KNOWLEDGE SERVICE
                             │
                             ▼
                        LLAMAINDEX
                             │
                             ▼
                      KNOWLEDGE CACHE
                             │
                             ▼
                     GOOGLE ADK AGENTS
```

---

## 2. Key Components Implemented

### A. TypeScript Knowledge Graph Package (`packages/knowledge-graph/`)
- [`entities/entity-types.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/entities/entity-types.ts): 25+ entity types (`COMPONENT`, `MANUFACTURER`, `SPECIFICATION`, `REQUIREMENT`, `DECISION`, etc.) and lifecycle statuses (`ACTIVE`, `UNRESOLVED`, `CONFLICTED`, `SUPERSEDED`, etc.).
- [`entities/entity-schema.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/entities/entity-schema.ts): Definitions for `CanonicalEntity`, `EntityMention`, `Specification`, and `SpecificationConflict`.
- [`entities/entity-normalizer.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/entities/entity-normalizer.ts): Deterministic unit parser converting voltages (`3V3` -> `3.3 V`), currents (`500mA` -> `0.5 A`), resistances (`10k` -> `10000.0 Ω`), and temperatures (`125°C`).
- [`entities/entity-resolver.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/entities/entity-resolver.ts): Multi-stage resolution pipeline preventing blind merges of packaging suffixes (e.g. `TPS62130` vs `TPS62130RGTR`).
- [`relationships/relationship-types.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/relationships/relationship-types.ts): 15+ relationship edge types (`MANUFACTURED_BY`, `HAS_SPECIFICATION`, `SATISFIED_BY`, `SELECTS`, etc.).
- [`validation/conflict-detection.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/validation/conflict-detection.ts): Detects and preserves contradictory specifications without overwriting.
- [`graph/graph-service.ts`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/packages/knowledge-graph/graph/graph-service.ts): Bounded graph query engine (`depth = 2`).

### B. Python Backend Knowledge Graph Engine (`backend/workline/knowledge/graph/`)
- [`KnowledgeGraphService`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/knowledge/graph/service.py): Graph storage in SurrealDB, bounded depth traversal, conflict preservation, deterministic numerical evaluation (`evaluate_requirement_candidate`), and Phase 10C cache invalidation.
- [`EntityNormalizer`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/knowledge/graph/normalizer.py): Quantity parser and standard unit scaler.
- [`EntityResolver`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/knowledge/graph/resolver.py): Prioritized mention resolution.

### C. CLI Commands (`cli/wline/commands/entity.py` & `graph.py`)
- `wline entity find <query>`: Search canonical entities with aliases and confidence.
- `wline entity inspect <id>`: View specifications, relationships, and metadata.
- `wline entity resolve <mention>`: Run prioritized resolution on an ambiguous mention.
- `wline entity conflicts`: Audit open specification conflicts across documents.
- `wline graph related <entity-id>`: Bounded 1-hop/2-hop relationship traversal.
- `wline graph evidence <entity-id>`: Full provenance chain audit.

### D. REST API (`backend/workline/knowledge/graph/api.py`)
- `GET /api/entities/search`
- `GET /api/entities/{id}`
- `GET /api/entities/{id}/relationships`
- `GET /api/entities/{id}/evidence`
- `GET /api/entities/{id}/specifications`
- `GET /api/entities/{id}/conflicts`
- `POST /api/entities/{mention}/resolve`
- `GET /api/graph/related/{id}`

### E. Frontend React Components (`frontend/src/components/`)
- `EntityExplorer.tsx`: Canonical entity explorer with alias tag list and search bar.
- `RelationshipPanel.tsx`: Interactive relationship graph edge viewer.
- `EvidencePanel.tsx`: Provenance chain with page/section citations.
- `ConflictPanel.tsx`: Side-by-side comparison of conflicting document specifications.
- `SpecificationTable.tsx`: Tabular specifications with unit normalization and validity flags.

---

## 3. Verification & Benchmark Summary

| Benchmark Category | Duration / Result |
|---|---|
| **Phase 10E Knowledge Graph Test Suite** | **12 Passed (100%)** in 6.36s |
| **Full Repository Test Suite** | **267 Passed (100%)** |
| **TypeScript 7 Typecheck (`tsc --noEmit`)** | **Passed (0 errors)** in 1.45s |
| **Numerical Requirement Matching** | **Verified** (`3.3V`, `>=2A` pass; `5V` fail) |
| **Ambiguous Part Number Separation** | **Verified** (Base vs Suffix handling) |
| **Conflicting Specifications Preserved** | **Verified** (Both values retained, conflict registered) |
| **Zero Unsupported Fact Creation** | **Verified** (No hallucinated efficiency specs) |
