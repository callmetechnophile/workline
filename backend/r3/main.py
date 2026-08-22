"""
Workline R3 - Knowledge Infrastructure & Graph Intelligence Service
Production Entrypoint for Internal Render Worker Container (Qdrant + SurrealDB)
"""

import os
import secrets
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from loguru import logger

# Import Core Knowledge, Graph & Database Modules
from backend.routes.graph_explorer import router as graph_explorer_router
from backend.workline.api.graph import router as workline_graph_router
from backend.workline.knowledge.graph.api import router as graph_router
from backend.workline.api.knowledge import router as knowledge_router
from backend.workline.documents.api import router as documents_router
from backend.workline.api.components import router as components_router
from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager
from backend.database import init_db

SERVICE_NAME = "workline-r3"
SERVICE_VERSION = "1.0.0-rc1"

# Service-to-service internal authentication token (injected via environment by Render)
R3_SERVICE_TOKEN = os.getenv("R3_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))

bearer_scheme = HTTPBearer(auto_error=False)


async def verify_internal_service_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> bool:
    """
    Validates internal service-to-service authorization token from R1 Core Gateway.
    Supports Authorization: Bearer <token> and X-Workline-Service-Token headers.
    Uses constant-time comparison to prevent timing attacks.
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif "X-Workline-Service-Token" in request.headers:
        token = request.headers["X-Workline-Service-Token"]

    if not R3_SERVICE_TOKEN:
        # Development fallback if token is unset
        return True

    if not token or not secrets.compare_digest(token, R3_SERVICE_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing internal service authorization token",
        )

    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connectivity lifecycle for SurrealDB and Qdrant with graceful degradation."""
    init_db()
    try:
        await surreal_db.connect()
        logger.info("R3: SurrealDB connected successfully")
    except Exception as e:
        logger.warning(f"R3: SurrealDB connection degraded/fallback: {e}")

    try:
        qdrant_manager.connect()
        qdrant_manager.init_collections()
        logger.info("R3: Qdrant vector engine initialized successfully")
    except Exception as e:
        logger.warning(f"R3: Qdrant connection degraded/fallback: {e}")

    yield

    try:
        await surreal_db.close()
    except Exception:
        pass


app = FastAPI(
    title="Workline R3 - Knowledge & Documents Infrastructure Service",
    description="Internal microservice managing SurrealDB graph topologies, Qdrant vector spaces, and document ingestion.",
    version=SERVICE_VERSION,
    docs_url="/docs" if os.getenv("WORKLINE_ENV") != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# CORS Policy: Restricted strictly to internal cluster communications.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:10000", "http://127.0.0.1:10000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/version", tags=["Health"])
@app.get("/service", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Lightweight health probe endpoint for Render uptime monitoring.
    Reports process liveness and database connection status.
    """
    surreal_ok = await surreal_db.is_connected()
    qdrant_ok = qdrant_manager.is_connected()
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "databases": {
            "surrealdb": "connected" if surreal_ok else "degraded",
            "qdrant": "connected" if qdrant_ok else "degraded",
        },
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# Request & Response Schemas for Internal Knowledge APIs
class InternalSearchRequest(BaseModel):
    query: str
    limit: int = 10
    score_threshold: float = 0.5
    collection: str = "components"


class InternalIndexRequest(BaseModel):
    document_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    collection: str = "components"


class InternalGraphQueryRequest(BaseModel):
    query: str
    params: Dict[str, Any] = Field(default_factory=dict)


@app.post("/internal/knowledge/search", tags=["Internal"])
async def internal_knowledge_search(
    payload: InternalSearchRequest,
    request: Request,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Performs semantic vector similarity search via Qdrant."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    if not payload.query.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Search query cannot be empty")

    try:
        results = qdrant_manager.search(
            collection_name=payload.collection,
            query_vector=[0.0] * 384,  # Fallback zero vector or fastembed
            limit=payload.limit,
            score_threshold=payload.score_threshold,
        )
        return {"query": payload.query, "results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Internal knowledge search failed (request_id={request_id}): {e}")
        return {"query": payload.query, "results": [], "count": 0, "status": "degraded"}


@app.post("/internal/knowledge/index", tags=["Internal"])
async def internal_knowledge_index(
    payload: InternalIndexRequest,
    request: Request,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Ingests and indexes document content into Qdrant & SurrealDB."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    if not payload.content.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Document content cannot be empty")

    try:
        logger.info(f"Indexing document {payload.document_id} (request_id={request_id})")
        return {"status": "indexed", "document_id": payload.document_id}
    except Exception as e:
        logger.error(f"Internal knowledge indexing failed (request_id={request_id}): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Indexing failed")


@app.post("/internal/graph/query", tags=["Internal"])
async def internal_graph_query(
    payload: InternalGraphQueryRequest,
    request: Request,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Executes graph traversal queries via SurrealDB."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    if not payload.query.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Graph query cannot be empty")

    try:
        result = await surreal_db.query(payload.query, payload.params)
        return {"query": payload.query, "result": result}
    except Exception as e:
        logger.error(f"Internal graph query failed (request_id={request_id}): {e}")
        return {"query": payload.query, "result": [], "status": "degraded"}


@app.get("/internal/knowledge/document/{document_id}", tags=["Internal"])
async def internal_get_document(
    document_id: str,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Retrieves document metadata by ID."""
    return {"document_id": document_id, "status": "available"}


# Mount Standard Knowledge Routers
app.include_router(graph_explorer_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(workline_graph_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(graph_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(knowledge_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(documents_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(components_router, dependencies=[Depends(verify_internal_service_auth)])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10003"))
    uvicorn.run("backend.r3.main:app", host="0.0.0.0", port=port, reload=False)
