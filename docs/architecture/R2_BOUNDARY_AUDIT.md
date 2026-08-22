# Workline R2 Service Boundary Audit

## Service Identification
- **Service Name**: `workline-r2` (`workline-ai-agents`)
- **Service Role**: Internal AI, Multi-Agent Orchestration, Web Research & Generation Worker
- **Deployment Model**: Render Web Service (Docker Runtime)
- **Exposure**: Internal Private Network / Authenticated Service API (R1 Gateway Gatewayed)

---

## 1. R2 Module Inventory & Dependency Map

| Module Path | Primary Purpose | Dependencies | R2 Responsibility | Cross-Service Dependency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`backend/routes/research.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/routes/research.py) | End-to-end multi-agent research pipeline | `fastapi`, `pydantic`, `google-genai`, `scrapling` | Core | Proxy invoked by R1 | ✅ Active |
| [`backend/agents/research_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/research_agent.py) | Literature & scientific paper retrieval | `httpx`, `pydantic`, `scrapling` | Core | None | ✅ Active |
| [`backend/agents/planner_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/planner_agent.py) | Project decomposition & agent task graph | `pydantic`, `google-genai` | Core | None | ✅ Active |
| [`backend/agents/retrieval_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/retrieval_agent.py) | Datasheet & reference lookup | `httpx`, `scrapling` | Core | None | ✅ Active |
| [`backend/agents/extraction_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/extraction_agent.py) | Component spec & parametric extraction | `pydantic`, `google-genai` | Core | None | ✅ Active |
| [`backend/agents/validation_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/validation_agent.py) | Engineering constraint & readiness score | `pydantic` | Core | None | ✅ Active |
| [`backend/agents/optimization_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/optimization_agent.py) | Cost & alternative component optimization | `pydantic` | Core | None | ✅ Active |
| [`backend/agents/export_agent.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/agents/export_agent.py) | Package serialization & audit logs | `pydantic` | Core | Delegated export | ✅ Active |
| [`backend/workline/api/agents.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/agents.py) | OmniRoute dynamic agent execution API | `fastapi`, `pydantic` | Core | None | ✅ Active |
| [`backend/workline/api/generation.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/generation.py) | Multimodal prompt & Gamma slide generation | `fastapi`, `pydantic` | Core | None | ✅ Active |
| [`backend/workline/api/cache.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/api/cache.py) | In-memory agent result caching | `fastapi` | Core | None | ✅ Active |
| [`backend/routes/speech.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/routes/speech.py) | Sarvam AI Speech-to-Text audio transcription | `fastapi`, `sarvamai`, `httpx` | Core | None | ✅ Active |
| [`backend/workline/scraping/engine.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/workline/scraping/engine.py) | Scrapling web extraction & rate limiting | `scrapling`, `httpx` | Core | None | ✅ Active |

---

## 2. Service Boundary Enforcement

### What R2 Owns:
1. Multi-Agent pipeline orchestration (8 sequenced agent stages).
2. Deep research and scientific literature search.
3. Web retrieval and datasheet parsing via Scrapling.
4. AI model routing and LLM reasoning (`google-genai`, `sarvamai`).
5. In-memory agent execution result caching.

### What R2 DOES NOT Own (Excluded from R2 Container):
- ❌ **Databases**: Qdrant Vector Store, SurrealDB, Neo4j, PostgreSQL (owned by dedicated storage/R3).
- ❌ **Engineering Physics**: PINN Neural Network, thermal simulations, layout solver (owned by R4).
- ❌ **Procurement & Sourcing**: Supplier API connectors, DigiKey/Mouser scrapers, x402 payment escrow (owned by R5).
- ❌ **Public Gateway & Auth**: Clerk JWT session verification, browser CORS (owned by R1).
- ❌ **Frontend & CLI**: Next.js App Router, wline Python SDK.

---

## 3. Communication Pattern
```
[Browser / User] 
       │
       ▼ (Public HTTPS + Clerk Auth)
[R1 Core Gateway]
       │
       ▼ (Internal HTTP + X-Workline-Service-Token)
[R2 AI & Research Service]
   ├── Planner Agent
   ├── Retrieval Agent (Scrapling)
   ├── Extraction Agent (Gemini)
   ├── Research Agent (Europe PMC / ArXiv)
   └── Speech STT (Sarvam AI)
```
