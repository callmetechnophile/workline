# Workline Service Module Mapping Matrix

**Audit Date**: 2026-08-23  
**Classification Target**: R1 CORE, R2 AI/AGENTS, R3 KNOWLEDGE, R4 ENGINEERING, R5 PROCUREMENT/COLLAB

---

## Service Module Mapping

| Module / Package | Current Location | Candidate Service | Primary Dependencies | Coupling | Extraction Difficulty |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`auth.py`** | `backend/auth.py` | **R1 CORE** | `python-jose`, `cryptography` | LOW | Easy |
| **`routes/workspace.py`** | `backend/routes/workspace.py` | **R1 CORE** | `fastapi`, `pydantic` | LOW | Easy |
| **`routes/collaboration.py`** | `backend/routes/collaboration.py` | **R1 CORE** | `fastapi`, `aiosqlite` | LOW | Easy |
| **`workline/api/project.py`** | `backend/workline/api/project.py` | **R1 CORE** | `fastapi`, `cryptography` | LOW | Easy |
| **`routes/research.py`** | `backend/routes/research.py` | **R2 AI** | `google-genai`, `httpx` | MEDIUM | Moderate |
| **`workline/api/agents.py`** | `backend/workline/api/agents.py` | **R2 AI** | `google-genai`, `pydantic` | MEDIUM | Moderate |
| **`workline/api/generation.py`**| `backend/workline/api/generation.py`| **R2 AI** | `google-genai`, `sarvamai` | MEDIUM | Moderate |
| **`workline/database/surrealdb.py`**| `backend/workline/database/surrealdb.py`| **R3 KNOWLEDGE** | `surrealdb` | HIGH | Complex |
| **`workline/retrieval/qdrant.py`** | `backend/workline/retrieval/qdrant.py` | **R3 KNOWLEDGE** | `qdrant-client`, `fastembed` | HIGH | Complex |
| **`routes/graph_explorer.py`** | `backend/routes/graph_explorer.py` | **R3 KNOWLEDGE** | `fastapi`, `surrealdb` | MEDIUM | Moderate |
| **`workline/documents/api.py`** | `backend/workline/documents/api.py` | **R3 KNOWLEDGE** | `python-docx`, `reportlab`, `lxml` | MEDIUM | Moderate |
| **`routes/packages.py` (PINN)** | `backend/routes/packages.py` | **R4 ENGINEERING** | `numpy`, `onnxruntime` | MEDIUM | Moderate |
| **`workline/api/pcb.py`** | `backend/workline/api/pcb.py` | **R4 ENGINEERING** | `fastapi`, `pydantic` | LOW | Easy |
| **`workline/validation/api.py`**| `backend/workline/validation/api.py`| **R4 ENGINEERING** | `fastapi`, `pydantic` | LOW | Easy |
| **`workline/decision/api.py`** | `backend/workline/decision/api.py` | **R4 ENGINEERING** | `fastapi`, `pydantic` | LOW | Easy |
| **`workline/api/bom.py`** | `backend/workline/api/bom.py` | **R5 PROCUREMENT** | `fastapi`, `pydantic` | **LOW** | **Lowest (First Extraction)** |
| **`workline/api/procurement.py`**| `backend/workline/api/procurement.py`| **R5 PROCUREMENT** | `httpx`, `pydantic` | **LOW** | **Lowest (First Extraction)** |
| **`workline/api/orders.py`** | `backend/workline/api/orders.py` | **R5 PROCUREMENT** | `fastapi`, `pydantic` | **LOW** | **Lowest (First Extraction)** |
| **`workline/api/payments.py`** | `backend/workline/api/payments.py` | **R5 PROCUREMENT** | `cryptography` (x402) | **LOW** | **Lowest (First Extraction)** |
| **`routes/calendar.py`** | `backend/routes/calendar.py` | **R5 PROCUREMENT** | `fastapi`, `reportlab` | **LOW** | **Lowest (First Extraction)** |
| **`workline/api/git.py`** | `backend/workline/api/git.py` | **R5 PROCUREMENT** | `httpx`, `pydantic` | **LOW** | **Lowest (First Extraction)** |
