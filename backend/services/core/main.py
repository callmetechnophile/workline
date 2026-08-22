"""
Workline R1 - Core Gateway & Lifecycle Orchestrator
Standalone entrypoint for API gateway routing, authentication, project lifecycle,
workspace collaboration, and downstream microservice proxies.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

from backend.routes.workspace import router as workspace_router
from backend.routes.collaboration import router as collaboration_router
from backend.routes.versioning import router as versioning_router
from backend.workline.api.project import router as project_package_router

app = FastAPI(
    title="Workline R1 - Core & Gateway Service",
    description="Central routing gateway, auth validation, workspace state, and service orchestration.",
    version="1.0.0-rc1",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Routers
app.include_router(workspace_router)
app.include_router(collaboration_router)
app.include_router(versioning_router)
app.include_router(project_package_router)

# Downstream Service URLs (Configurable via Environment Variables)
R2_AI_URL = os.getenv("WORKLINE_R2_URL", "http://localhost:10002")
R3_KNOWLEDGE_URL = os.getenv("WORKLINE_R3_URL", "http://localhost:10003")
R4_ENGINEERING_URL = os.getenv("WORKLINE_R4_URL", "http://localhost:10004")
R5_PROCUREMENT_URL = os.getenv("WORKLINE_R5_URL", "http://localhost:10005")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health endpoint for R1 Gateway."""
    return {
        "status": "healthy",
        "service": "workline-core-gateway",
        "version": "1.0.0-rc1",
        "downstream": {
            "r2_ai": R2_AI_URL,
            "r3_knowledge": R3_KNOWLEDGE_URL,
            "r4_engineering": R4_ENGINEERING_URL,
            "r5_procurement": R5_PROCUREMENT_URL,
        }
    }


# ==============================================================================
# Internal Proxy Routers for Downstream Render Services
# ==============================================================================

@app.post("/api/proxy/ai/{path:path}", tags=["Proxy"])
async def proxy_to_r2(path: str, request: Request):
    """Proxy requests to R2 AI/Research service with graceful error handling."""
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{R2_AI_URL}/{path}", content=body, headers=dict(request.headers))
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"R2 AI Service unavailable: {str(exc)}")


@app.post("/api/proxy/knowledge/{path:path}", tags=["Proxy"])
async def proxy_to_r3(path: str, request: Request):
    """Proxy requests to R3 Knowledge/Documents service."""
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{R3_KNOWLEDGE_URL}/{path}", content=body, headers=dict(request.headers))
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"R3 Knowledge Service unavailable: {str(exc)}")


@app.post("/api/proxy/engineering/{path:path}", tags=["Proxy"])
async def proxy_to_r4(path: str, request: Request):
    """Proxy requests to R4 Engineering/Simulation service."""
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{R4_ENGINEERING_URL}/{path}", content=body, headers=dict(request.headers))
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"R4 Engineering Service unavailable: {str(exc)}")


@app.post("/api/proxy/procurement/{path:path}", tags=["Proxy"])
async def proxy_to_r5(path: str, request: Request):
    """Proxy requests to R5 Procurement/Collaboration service."""
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{R5_PROCUREMENT_URL}/{path}", content=body, headers=dict(request.headers))
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"R5 Procurement Service unavailable: {str(exc)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.core.main:app", host="0.0.0.0", port=10000, reload=True)
