"""
Workline R4 - Engineering Computation, PINN Physics & Simulation Service
Production Entrypoint for Internal Render Worker Container
"""

import os
import secrets
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from loguru import logger

# Import Core Engineering, Validation, Decision & PCB Modules
from backend.routes.packages import router as packages_router
from backend.workline.api.pcb import router as pcb_router
from backend.workline.validation.api import router as validation_router
from backend.workline.decision.api import router as decision_engine_router
from backend.workline.validation.units import UnitValidator
from backend.workline.validation.service import validation_service
from backend.workline.decision.service import decision_service
from backend.workline.pcb.engine.validation import PCBValidator
from backend.workline.pcb.pinn.inference import PINNInferenceEngine
from backend.workline.pcb.models.project import PCBProject

SERVICE_NAME = "workline-r4"
SERVICE_VERSION = "1.0.0-rc1"

# Service-to-service internal authentication token (injected via environment by Render)
R4_SERVICE_TOKEN = os.getenv("R4_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))

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

    if not R4_SERVICE_TOKEN:
        # Development fallback if token is unset
        return True

    if not token or not secrets.compare_digest(token, R4_SERVICE_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing internal service authorization token",
        )

    return True


app = FastAPI(
    title="Workline R4 - Engineering & Simulation Service",
    description="Internal microservice for PINN physics solvers, thermal simulation, PCB geometric DRC, and decision support.",
    version=SERVICE_VERSION,
    docs_url="/docs" if os.getenv("WORKLINE_ENV") != "production" else None,
    redoc_url=None,
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
    Never executes heavy PINN inference, numerical simulations, or remote calls.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# Request & Response Schemas for Internal Engineering APIs
class UnitConvertRequest(BaseModel):
    value: float
    from_unit: str
    to_unit: str
    unit_type: Optional[str] = None


class RequirementValidateRequest(BaseModel):
    requirement_id: str
    candidate_component_id: str


class TradeoffEvaluationRequest(BaseModel):
    decision_id: str
    candidates: List[Dict[str, Any]]
    raw_matrix: Optional[Dict[str, Dict[str, float]]] = None


class PCBValidateRequest(BaseModel):
    project_dict: Dict[str, Any]


class PINNThermalRequest(BaseModel):
    project_dict: Dict[str, Any]
    nx: int = 50
    ny: int = 40


@app.post("/internal/engineering/units/convert", tags=["Internal"])
async def internal_convert_units(
    payload: UnitConvertRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Performs high-precision engineering unit conversions."""
    try:
        success, converted_value, error = UnitValidator.convert(
            payload.value, payload.from_unit, payload.to_unit
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        return {
            "success": success,
            "converted_value": converted_value,
            "from_unit": payload.from_unit,
            "to_unit": payload.to_unit,
            "error": error,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unit conversion failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/internal/engineering/requirements/validate", tags=["Internal"])
async def internal_validate_requirement(
    payload: RequirementValidateRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Evaluates candidate components against engineering requirements and constraints."""
    try:
        val = validation_service.validate_candidate(payload.requirement_id, payload.candidate_component_id)
        return val.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Requirement validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Requirement validation failed")


@app.post("/internal/engineering/tradeoffs/evaluate", tags=["Internal"])
async def internal_evaluate_tradeoffs(
    payload: TradeoffEvaluationRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Calculates weighted multi-criteria decision matrix scores for component trade-offs."""
    try:
        dec = decision_service.get_decision(payload.decision_id)
        if not dec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
        from backend.workline.decision.models import DecisionCandidate
        candidates = [DecisionCandidate(**c) for c in payload.candidates]
        scored = decision_service.evaluate_decision(payload.decision_id, candidates, payload.raw_matrix)
        return scored.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade-off evaluation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Trade-off evaluation failed")


@app.post("/internal/engineering/pcb/validate", tags=["Internal"])
async def internal_validate_pcb(
    payload: PCBValidateRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Runs geometric PCB Design Rule Checking (DRC) and clearances."""
    try:
        project = PCBProject(**payload.project_dict)
        validator = PCBValidator()
        report = validator.validate_project(project)
        return report.model_dump()
    except Exception as e:
        logger.error(f"PCB validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"PCB validation failed: {str(e)}")


@app.post("/internal/engineering/pinn/thermal", tags=["Internal"])
async def internal_pinn_thermal(
    payload: PINNThermalRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Runs high-speed Physics-Informed Neural Network forward inference for thermal field prediction."""
    try:
        project = PCBProject(**payload.project_dict)
        engine = PINNInferenceEngine()
        result = engine.predict_project_thermal_field(project, nx=payload.nx, ny=payload.ny)
        return result.model_dump()
    except Exception as e:
        logger.error(f"PINN thermal inference failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PINN inference failed: {str(e)}")


# Mount Standard Engineering Routers
app.include_router(packages_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(pcb_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(validation_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(decision_engine_router, dependencies=[Depends(verify_internal_service_auth)])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10004"))
    uvicorn.run("backend.r4.main:app", host="0.0.0.0", port=port, reload=False)
