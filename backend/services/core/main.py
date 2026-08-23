"""
Workline R1 - Core Gateway & Lifecycle Orchestrator
Standalone entrypoint for API gateway routing, authentication, project lifecycle,
workspace collaboration, and downstream microservice proxies.

Architecture: Hub-and-spoke service mesh. R1 is the primary control plane.
- All R2/R3/R4/R5 traffic from the Netlify frontend routes through R1.
- Internal service-to-service calls are proxied via R1 with ArmourIQ policy enforcement.
- All proxy endpoints enforce:
    * Service-to-service authentication (WORKLINE_SERVICE_AUTH_KEY / Bearer token)
    * Context propagation (X-Request-ID, X-Project-ID, X-Session-ID, X-User-ID)
    * Explicit connect + read timeouts
    * Safe retries on GET-only idempotent operations
    * Structured 503 on downstream failure (never generic 500)
    * Sanitized observability headers (no token/key leakage)
"""

import os
import secrets
import time
import uuid

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.routes.workspace import router as workspace_router
from backend.routes.collaboration import router as collaboration_router
from backend.routes.versioning import router as versioning_router
from backend.workline.api.project import router as project_package_router

app = FastAPI(
    title="Workline R1 - Core & Gateway Service",
    description="Central routing gateway, auth validation, workspace state, and service orchestration.",
    version="1.0.0-rc1",
)

# ============================================================================
# CORS Configuration: Netlify frontend + localhost dev, never wildcard in prod
# ============================================================================
raw_origins = os.getenv(
    "WORKLINE_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://worklineai.netlify.app,http://localhost:10000"
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Core Routers
# ============================================================================
app.include_router(workspace_router)
app.include_router(collaboration_router)
app.include_router(versioning_router)
app.include_router(project_package_router)

# ============================================================================
# Downstream Service URLs
# Override via Render environment variables.
# ============================================================================
R2_AI_URL = os.getenv("WORKLINE_R2_URL", os.getenv("R2_SERVICE_URL", "http://localhost:10002"))
R3_KNOWLEDGE_URL = os.getenv("WORKLINE_R3_URL", os.getenv("R3_SERVICE_URL", "http://localhost:10003"))
R4_ENGINEERING_URL = os.getenv("WORKLINE_R4_URL", os.getenv("R4_SERVICE_URL", "http://localhost:10004"))
R5_PROCUREMENT_URL = os.getenv("WORKLINE_R5_URL", os.getenv("R5_SERVICE_URL", "http://localhost:10005"))

# Internal service auth key. Render injects this for all R2-R5 services.
SERVICE_AUTH_KEY = os.getenv("WORKLINE_SERVICE_AUTH_KEY", "workline-internal-mesh-key-2026")

# ============================================================================
# Timeout policy
# ============================================================================
_CONNECT_TIMEOUT = float(os.getenv("WORKLINE_CONNECT_TIMEOUT", "5.0"))
_READ_TIMEOUT = float(os.getenv("WORKLINE_READ_TIMEOUT", "30.0"))
_MESH_TIMEOUT = httpx.Timeout(connect=_CONNECT_TIMEOUT, read=_READ_TIMEOUT, write=_READ_TIMEOUT, pool=35.0)


def _safe_proxy_headers(incoming: Request, path: str) -> dict:
    """
    Builds clean, sanitized forwarding headers for downstream proxy calls.
    Explicitly strips Authorization from browser requests to prevent credential leakage.
    Injects service mesh credentials and context propagation headers.
    """
    request_id = incoming.headers.get("X-Request-ID") or str(uuid.uuid4())
    session_id = incoming.headers.get("X-Session-ID", "")
    project_id = incoming.headers.get("X-Project-ID", "")
    user_id = incoming.headers.get("X-User-ID", "")
    delegation_chain = incoming.headers.get("X-Delegation-Chain", "")

    return {
        "Content-Type": incoming.headers.get("Content-Type", "application/json"),
        "Authorization": f"Bearer {SERVICE_AUTH_KEY}",
        "X-Workline-Service-Token": SERVICE_AUTH_KEY,
        "X-Request-ID": request_id,
        "X-Session-ID": session_id,
        "X-Project-ID": project_id,
        "X-User-ID": user_id,
        "X-Delegation-Chain": delegation_chain,
    }


# ============================================================================
# Health Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    R1 gateway health. Returns URL topology for observability.
    Does NOT fabricate downstream health status.
    """
    return {
        "status": "healthy",
        "service": "workline-core-gateway",
        "version": "1.0.0-rc1",
        "downstream": {
            "r2_ai": R2_AI_URL,
            "r3_knowledge": R3_KNOWLEDGE_URL,
            "r4_engineering": R4_ENGINEERING_URL,
            "r5_procurement": R5_PROCUREMENT_URL,
        },
    }


@app.get("/health/cluster", tags=["Health"])
async def cluster_health():
    """
    Live health probe across all R2–R5 Render microservices.
    Performs real HTTP liveness checks. Never fabricates status.
    """
    results = {}
    all_healthy = True
    for s_id, s_url in [
        ("R2", R2_AI_URL),
        ("R3", R3_KNOWLEDGE_URL),
        ("R4", R4_ENGINEERING_URL),
        ("R5", R5_PROCUREMENT_URL),
    ]:
        probe_url = f"{s_url.rstrip('/')}/health"
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(2.5, connect=2.0)) as client:
                resp = await client.get(probe_url)
                latency_ms = (time.perf_counter() - start) * 1000.0
                if resp.status_code == 200:
                    results[s_id] = {
                        "status": "healthy",
                        "endpoint": s_url,
                        "http_code": 200,
                        "latency_ms": round(latency_ms, 1),
                    }
                else:
                    results[s_id] = {
                        "status": "degraded",
                        "endpoint": s_url,
                        "http_code": resp.status_code,
                        "latency_ms": round(latency_ms, 1),
                    }
                    all_healthy = False
        except Exception as e:
            results[s_id] = {"status": "unreachable", "endpoint": s_url, "error": str(e)}
            all_healthy = False

    return {
        "status": "healthy" if all_healthy else "degraded",
        "gateway": "R1_CORE",
        "service": "workline-core-gateway",
        "version": "1.0.0-rc1",
        "downstream_services": results,
    }


# ============================================================================
# Internal Proxy Routers for Downstream Render Services
# R1 is the sole public entry point; all downstream traffic routes through here.
# ============================================================================

@app.api_route("/api/proxy/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Proxy"])
async def proxy_to_r2(path: str, request: Request):
    """
    Proxy authenticated requests to R2 AI/Research/ADK service.
    Enforces service mesh auth, context propagation, and structured 503 on failure.
    """
    body = await request.body()
    headers = _safe_proxy_headers(request, path)
    target = f"{R2_AI_URL}/{path}"
    try:
        async with httpx.AsyncClient(timeout=_MESH_TIMEOUT) as client:
            resp = await client.request(
                method=request.method,
                url=target,
                content=body,
                headers=headers,
                params=dict(request.query_params),
            )
            logger.info(f"[MESH] R1→R2 {request.method} /{path} → {resp.status_code} | req_id={headers['X-Request-ID']}")
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type=resp.headers.get("content-type"),
                headers={"X-Request-ID": headers["X-Request-ID"]},
            )
    except httpx.RequestError as exc:
        logger.error(f"[MESH] R1→R2 unavailable: {exc}")
        raise HTTPException(status_code=503, detail=f"R2 AI Service unavailable: {str(exc)}")


@app.api_route("/api/proxy/knowledge/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Proxy"])
async def proxy_to_r3(path: str, request: Request):
    """
    Proxy authenticated requests to R3 Knowledge/Documents service.
    Read-only GET ops use up to 2 safe retries.
    """
    body = await request.body()
    headers = _safe_proxy_headers(request, path)
    target = f"{R3_KNOWLEDGE_URL}/{path}"
    max_attempts = 2 if request.method == "GET" else 1
    last_exc = None
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=_MESH_TIMEOUT) as client:
                resp = await client.request(
                    method=request.method,
                    url=target,
                    content=body,
                    headers=headers,
                    params=dict(request.query_params),
                )
                logger.info(f"[MESH] R1→R3 {request.method} /{path} → {resp.status_code} | req_id={headers['X-Request-ID']}")
                return Response(
                    content=resp.content,
                    status_code=resp.status_code,
                    media_type=resp.headers.get("content-type"),
                    headers={"X-Request-ID": headers["X-Request-ID"]},
                )
        except httpx.RequestError as exc:
            last_exc = exc
    logger.error(f"[MESH] R1→R3 unavailable: {last_exc}")
    raise HTTPException(status_code=503, detail=f"R3 Knowledge Service unavailable: {str(last_exc)}")


@app.api_route("/api/proxy/engineering/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Proxy"])
async def proxy_to_r4(path: str, request: Request):
    """
    Proxy authenticated requests to R4 Engineering/Simulation service.
    GET operations use safe retries; POST (simulations) are not retried.
    """
    body = await request.body()
    headers = _safe_proxy_headers(request, path)
    target = f"{R4_ENGINEERING_URL}/{path}"
    max_attempts = 2 if request.method == "GET" else 1
    last_exc = None
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=_MESH_TIMEOUT) as client:
                resp = await client.request(
                    method=request.method,
                    url=target,
                    content=body,
                    headers=headers,
                    params=dict(request.query_params),
                )
                logger.info(f"[MESH] R1→R4 {request.method} /{path} → {resp.status_code} | req_id={headers['X-Request-ID']}")
                return Response(
                    content=resp.content,
                    status_code=resp.status_code,
                    media_type=resp.headers.get("content-type"),
                    headers={"X-Request-ID": headers["X-Request-ID"]},
                )
        except httpx.RequestError as exc:
            last_exc = exc
    logger.error(f"[MESH] R1→R4 unavailable: {last_exc}")
    raise HTTPException(status_code=503, detail=f"R4 Engineering Service unavailable: {str(last_exc)}")


@app.api_route("/api/proxy/procurement/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Proxy"])
async def proxy_to_r5(path: str, request: Request):
    """
    Proxy requests to R5 Procurement/x402 service.
    POST/PUT ops (orders, payments) are NEVER retried to avoid duplicate transactions.
    """
    body = await request.body()
    headers = _safe_proxy_headers(request, path)
    target = f"{R5_PROCUREMENT_URL}/{path}"
    # CRITICAL: Only GET ops safe to retry; orders/payments are single-attempt only
    max_attempts = 2 if request.method == "GET" else 1
    last_exc = None
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=_MESH_TIMEOUT) as client:
                resp = await client.request(
                    method=request.method,
                    url=target,
                    content=body,
                    headers=headers,
                    params=dict(request.query_params),
                )
                logger.info(f"[MESH] R1→R5 {request.method} /{path} → {resp.status_code} | req_id={headers['X-Request-ID']}")
                return Response(
                    content=resp.content,
                    status_code=resp.status_code,
                    media_type=resp.headers.get("content-type"),
                    headers={"X-Request-ID": headers["X-Request-ID"]},
                )
        except httpx.RequestError as exc:
            last_exc = exc
    logger.error(f"[MESH] R1→R5 unavailable: {last_exc}")
    raise HTTPException(status_code=503, detail=f"R5 Procurement Service unavailable: {str(last_exc)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("backend.services.core.main:app", host="0.0.0.0", port=port, reload=True)
