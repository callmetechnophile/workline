import os
from typing import Optional, Dict, Any
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
from backend.routes.project_data import router as project_data_router
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
from backend.workline.x402 import x402_router
from backend.workline.armouriq import armouriq_router
from backend.workline.collaboration.teams import teams_router
from backend.workline.collaboration.tasks import tasks_router
from backend.workline.collaboration.comments import comments_router
from backend.workline.collaboration.approvals import approvals_router
from backend.workline.collaboration.notifications import notifications_router
from backend.workline.collaboration.activity import activity_router
from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager
from backend.database import init_db
from backend.workline.jobs import default_job_worker
from backend.workline.jobs.api import router as jobs_router
from backend.workline.observability import ObservabilityMiddleware, observability_router


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
    except Exception:
        pass

    # 4. Start background job worker
    await default_job_worker.start()

    yield

    # Shutdown job worker
    await default_job_worker.stop()

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

# Add Observability and Correlation ID Middleware
app.add_middleware(ObservabilityMiddleware)

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
app.include_router(x402_router)
app.include_router(armouriq_router)
app.include_router(teams_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(approvals_router)
app.include_router(notifications_router)
app.include_router(activity_router)
app.include_router(project_data_router)
app.include_router(jobs_router)
app.include_router(observability_router)

# Mount official ArmourFlow GraphQL Client/Application API Layer
try:
    from armourflow.graphql import get_graphql_router
    graphql_router = get_graphql_router()
    app.include_router(graphql_router, prefix="", tags=["GraphQL"])
except Exception as e:
    import logging
    logging.getLogger("uvicorn.error").warning(f"[GraphQL] Could not mount GraphQL router: {e}")



@app.post("/api/projects/{project_id}/pcb/generate", tags=["PCB"])
async def project_pcb_generate_endpoint(project_id: str, payload: Optional[dict] = None):
    from backend.workline.api.pcb import generate_pcb_visualization_api, GeneratePCBVisRequest
    req_obj = GeneratePCBVisRequest(**payload) if payload else GeneratePCBVisRequest(project_id=project_id)
    return await generate_pcb_visualization_api(project_id=project_id, payload=req_obj)


@app.get("/api/projects/{project_id}/pcb/visualization", tags=["PCB"])
async def project_pcb_visualization_endpoint(project_id: str):
    from backend.workline.api.pcb import get_pcb_visualization_api
    return await get_pcb_visualization_api(project_id=project_id)


@app.get("/api/projects/{project_id}/thermal", tags=["Thermal"])
@app.get("/api/thermal/{project_id}", tags=["Thermal"])
async def get_project_thermal_analysis_endpoint(project_id: str):
    from backend.services.thermal_service import calculate_project_thermal_analysis
    from backend.database import get_project_by_id
    
    clean_id = project_id.strip()
    proj = get_project_by_id(clean_id)
    components = []
    if proj:
        components = proj.get("bom") or proj.get("components") or []
    return calculate_project_thermal_analysis(components=components, project_id=clean_id)


@app.post("/api/projects/{project_id}/thermal", tags=["Thermal"])
@app.post("/api/thermal/{project_id}", tags=["Thermal"])
async def calculate_project_thermal_endpoint(project_id: str, payload: Optional[dict] = None):
    from backend.services.thermal_service import calculate_project_thermal_analysis
    from backend.database import get_project_by_id

    clean_id = project_id.strip()
    components = []
    if payload and "components" in payload:
        components = payload["components"]
    else:
        proj = get_project_by_id(clean_id)
        if proj:
            components = proj.get("bom") or proj.get("components") or []
    return calculate_project_thermal_analysis(components=components, project_id=clean_id)



@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/health/live", tags=["Health"])
@app.get("/health/ready", tags=["Health"])
@app.get("/version", tags=["Health"])
@app.get("/service", tags=["Health"])
async def health_check():
    """Health check probe for AWS ALB and ECS Fargate."""
    return {
        "status": "healthy",
        "service": "workline-api-bff",
        "version": "1.0.0-aws",
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


@app.get("/health/cluster")
async def cluster_health():
    """Live health probes across all 5 Render microservices in the Workline mesh."""
    from backend.workline.mesh.gateway import ServiceMeshGateway
    return await ServiceMeshGateway.check_cluster_health()


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
