"""
Workline R2 - AI, Multi-Agent Orchestration & Research Service
Production Entrypoint for Internal Render Worker Container
"""

import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Import Core AI & Agent Route Modules
from backend.routes.research import router as research_router
from backend.workline.api.agents import router as workline_agents_router
from backend.workline.api.generation import router as generation_router
from backend.workline.api.cache import router as cache_router
from backend.routes.speech import router as speech_router

SERVICE_NAME = "workline-r2"
SERVICE_VERSION = "1.0.0-rc1"

# Service-to-service internal authentication key (injected by Render)
INTERNAL_SERVICE_TOKEN = os.getenv("WORKLINE_SERVICE_AUTH_KEY", "")
API_KEY_HEADER = APIKeyHeader(name="X-Workline-Service-Token", auto_error=False)


async def verify_service_token(token: Optional[str] = Security(API_KEY_HEADER)) -> bool:
    """
    Validates internal service-to-service authorization token from R1 Core Gateway.
    If no internal token is configured in environment, allows local/dev internal routing.
    """
    if not INTERNAL_SERVICE_TOKEN:
        return True
    if token and token == INTERNAL_SERVICE_TOKEN:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Invalid or missing X-Workline-Service-Token",
    )


app = FastAPI(
    title="Workline R2 - AI & Research Agents Service",
    description="Internal microservice for multi-agent hardware research, OmniRoute pipelines, and multimodal generation.",
    version=SERVICE_VERSION,
    docs_url="/docs" if os.getenv("WORKLINE_ENV") != "production" else None,
    redoc_url=None,
)

# CORS Policy: R2 is an internal service, not directly exposed to public browsers.
# Restricted exclusively to internal cluster communications.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:10000", "http://127.0.0.1:10000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Lightweight health probe endpoint for Render uptime monitoring.
    Never executes external AI APIs or network crawling.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


# Include Internal AI / Agent / Research Routers
app.include_router(research_router, dependencies=[Depends(verify_service_token)])
app.include_router(workline_agents_router, dependencies=[Depends(verify_service_token)])
app.include_router(generation_router, dependencies=[Depends(verify_service_token)])
app.include_router(cache_router, dependencies=[Depends(verify_service_token)])
app.include_router(speech_router, dependencies=[Depends(verify_service_token)])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10002"))
    uvicorn.run("backend.r2.main:app", host="0.0.0.0", port=port, reload=False)
