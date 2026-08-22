import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routes.research import router as research_router
from backend.routes.packages import router as packages_router
from backend.routes.workspace import router as workspace_router
from backend.routes.collaboration import router as collaboration_router
from backend.routes.versioning import router as versioning_router
from backend.routes.graph_explorer import router as graph_explorer_router
from backend.routes.calendar import router as calendar_router
from backend.routes.speech import router as speech_router
from backend.workline.api.agents import router as workline_agents_router
from backend.workline.api.bom import router as bom_router
from backend.workline.api.components import router as components_router
from backend.workline.api.git import router as git_router
from backend.workline.api.graph import router as workline_graph_router
from backend.workline.api.orders import router as orders_router
from backend.workline.api.payments import router as payments_router
from backend.workline.api.pcb import router as pcb_router
from backend.workline.api.project import router as project_package_router
from backend.workline.api.procurement import router as procurement_router
from backend.workline.api.knowledge import router as knowledge_router
from backend.workline.api.generation import router as generation_router
from backend.workline.api.cache import router as cache_router
from backend.workline.documents.api import router as documents_router
from backend.workline.knowledge.graph.api import router as graph_router
from backend.workline.validation.api import router as validation_router
from backend.workline.decision.api import router as decision_engine_router
from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan context manager for SurrealDB and Qdrant database connections."""
    # 1. Initialize SQLite fallback for local compatibility
    init_db()

    # 2. Connect SurrealDB
    try:
        await surreal_db.connect()
    except Exception:
        pass

    # 3. Connect Qdrant
    try:
        qdrant_manager.connect()
        qdrant_manager.init_collections()
    except Exception:
        pass

    yield

    # Shutdown
    try:
        await surreal_db.close()
    except Exception:
        pass


app = FastAPI(
    title="WORKLINE",
    description="Workline - Engineering Lifecycle Orchestration Platform.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow CORS for easy Next.js integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include sub-routes
app.include_router(research_router)
app.include_router(packages_router)
app.include_router(workspace_router)
app.include_router(collaboration_router)
app.include_router(versioning_router)
app.include_router(graph_explorer_router)
app.include_router(workline_graph_router)
app.include_router(workline_agents_router)
app.include_router(procurement_router)
app.include_router(bom_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(pcb_router)
app.include_router(components_router)
app.include_router(git_router)
app.include_router(project_package_router)
app.include_router(knowledge_router)
app.include_router(generation_router)
app.include_router(cache_router)
app.include_router(documents_router)
app.include_router(graph_router)
app.include_router(validation_router)
app.include_router(decision_engine_router)
app.include_router(calendar_router)
app.include_router(speech_router)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/version", tags=["Health"])
@app.get("/service", tags=["Health"])
async def health_check():
    """Health check probe for Render."""
    return {
        "status": "healthy",
        "service": "workline-core-gateway",
        "version": "1.0.0-rc1",
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/health/database")
async def database_health():
    """Database connectivity health check for SurrealDB and Qdrant."""
    surreal_ok = await surreal_db.is_connected()
    qdrant_ok = qdrant_manager.is_connected()

    return {
        "surrealdb": "connected" if surreal_ok else "degraded",
        "qdrant": "connected" if qdrant_ok else "degraded",
    }


EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")


@app.get("/api/exports/{filename}")
def download_export(filename: str):
    file_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested file was not found or has expired.")

    return FileResponse(file_path, filename=filename)


# Mount static files for Next.js frontend export
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {
            "status": "healthy",
            "service": "workline-core-gateway",
            "version": "1.0.0-rc1",
        }
