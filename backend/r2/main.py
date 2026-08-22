"""
Workline R2 - AI, Multi-Agent Orchestration & Research Service
Production Entrypoint for Internal Render Worker Container
"""

import os
import secrets
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Import Core AI & Agent Route Modules & Schemas
from backend.routes.research import router as research_router, run_engineering_pipeline
from backend.schemas.research_schemas import ResearchRequest, ResearchResponse
from backend.workline.api.agents import router as workline_agents_router
from backend.workline.api.generation import router as generation_router
from backend.workline.api.cache import router as cache_router
from backend.routes.speech import router as speech_router

SERVICE_NAME = "workline-r2"
SERVICE_VERSION = "1.0.0-rc1"

# Service-to-service internal authentication token (injected via environment by Render)
R2_SERVICE_TOKEN = os.getenv("R2_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))

bearer_scheme = HTTPBearer(auto_error=False)


async def verify_internal_service_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> bool:
    """
    Validates internal service-to-service authorization token from R1 Core Gateway.
    Supports both Authorization: Bearer <token> and X-Workline-Service-Token headers.
    Uses constant-time comparison to prevent timing attacks.
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif "X-Workline-Service-Token" in request.headers:
        token = request.headers["X-Workline-Service-Token"]

    if not R2_SERVICE_TOKEN:
        # Development fallback if token is unset
        return True

    if not token or not secrets.compare_digest(token, R2_SERVICE_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing internal service authorization token",
        )

    return True


app = FastAPI(
    title="Workline R2 - AI & Research Agents Service",
    description="Internal microservice for multi-agent hardware research, OmniRoute pipelines, and multimodal generation.",
    version=SERVICE_VERSION,
    docs_url="/docs" if os.getenv("WORKLINE_ENV") != "production" else None,
    redoc_url=None,
)

# CORS Policy: Restricted strictly to internal cluster communications.
# Browser-facing requests must enter through R1 Gateway.
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
    Lightweight health probe and service info endpoint for Render uptime monitoring.
    Never executes external AI APIs, databases, or remote crawling.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)


@app.post("/internal/research", response_model=ResearchResponse, tags=["Internal"])
async def internal_research(
    payload: ResearchRequest,
    request: Request,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> ResearchResponse:
    """
    Dedicated secure internal endpoint for R1 Core Gateway -> R2 Research invocation.
    Requires valid Bearer service token authentication.
    """
    request_id = request.headers.get("X-Request-ID", "unknown")
    
    if not payload.intent or not payload.intent.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Engineering intent cannot be empty",
        )

    try:
        logger.info(f"Executing internal research pipeline (request_id={request_id}) for intent: {payload.intent[:60]}...")
        result = run_engineering_pipeline(payload.intent, payload.target_days)
        return result
    except Exception as e:
        logger.error(f"Internal research pipeline execution failed (request_id={request_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal research pipeline execution failed",
        )


# Include Additional Internal AI / Agent / Research Routers
app.include_router(research_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(workline_agents_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(generation_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(cache_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(speech_router, dependencies=[Depends(verify_internal_service_auth)])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10002"))
    uvicorn.run("backend.r2.main:app", host="0.0.0.0", port=port, reload=False)
