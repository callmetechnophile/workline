"""
Workline R3 - Knowledge, Graph & Document Intelligence Service
Dedicated microservice for SurrealDB multi-model graph queries, Qdrant vector retrieval,
datasheet chunking, and knowledge synthesis.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.graph_explorer import router as graph_explorer_router
from backend.workline.api.graph import router as workline_graph_router
from backend.workline.knowledge.graph.api import router as graph_router
from backend.workline.api.knowledge import router as knowledge_router
from backend.workline.documents.api import router as documents_router
from backend.workline.api.components import router as components_router
from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connections for SurrealDB and Qdrant."""
    init_db()
    try:
        await surreal_db.connect()
    except Exception:
        pass
    try:
        qdrant_manager.connect()
        qdrant_manager.init_collections()
    except Exception:
        pass
    yield
    try:
        await surreal_db.close()
    except Exception:
        pass


app = FastAPI(
    title="Workline R3 - Knowledge & Documents Service",
    description="Dedicated microservice managing SurrealDB graph topologies, Qdrant vector spaces, and document ingestion.",
    version="1.0.0-rc1",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Knowledge Routers
app.include_router(graph_explorer_router)
app.include_router(workline_graph_router)
app.include_router(graph_router)
app.include_router(knowledge_router)
app.include_router(documents_router)
app.include_router(components_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health endpoint for R3 Knowledge service and database connectivity."""
    surreal_ok = await surreal_db.is_connected()
    qdrant_ok = qdrant_manager.is_connected()
    return {
        "status": "healthy",
        "service": "workline-knowledge-documents",
        "version": "1.0.0-rc1",
        "databases": {
            "surrealdb": "connected" if surreal_ok else "fallback",
            "qdrant": "connected" if qdrant_ok else "fallback",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.knowledge.main:app", host="0.0.0.0", port=10003, reload=True)
