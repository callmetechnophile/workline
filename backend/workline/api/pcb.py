"""FastAPI router for PCB Engineering, Physics features, PINN Training/Inference, and Optimization."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.workline.pcb.engine.validation import PCBValidationReport
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.constraints import PCBConstraint
from backend.workline.pcb.models.net import Net
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.physics.dataset import ThermalDataset
from backend.workline.pcb.physics.features import PhysicsFeaturePoint
from backend.workline.pcb.pinn.inference import PINNInferenceResult
from backend.workline.pcb.pinn.trainer import TrainingRunResult
from backend.workline.pcb.services import (
    pcb_optimization_service,
    pcb_service,
    pcb_validation_service,
    physics_service,
)


router = APIRouter(prefix="/api/pcb", tags=["Workline PCB Engineering & PINN Engine"])


class CreatePCBRequest(BaseModel):
    project_id: str
    bom_id: Optional[str] = None
    board_width: float = 80.0
    board_height: float = 60.0


class TrainPINNRequest(BaseModel):
    epochs: int = 50
    learning_rate: float = 0.008


class OptimizePlacementRequest(BaseModel):
    max_iterations: int = 50


@router.post("/create", response_model=PCBProject)
async def create_pcb_api(payload: CreatePCBRequest):
    """Construct an authoritative PCBProject from project BOM."""
    try:
        project = await pcb_service.create_pcb_project(
            project_id=payload.project_id,
            bom_id_or_name=payload.bom_id,
            board_width=payload.board_width,
            board_height=payload.board_height,
        )
        return project
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"PCB creation failed: {str(exc)}")


@router.get("/{pcb_id}", response_model=PCBProject)
async def get_pcb_api(pcb_id: str):
    """Fetch complete PCB project state."""
    project = await pcb_service.get_pcb_project(pcb_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"PCB project '{pcb_id}' not found.")
    return project


@router.get("/{pcb_id}/components", response_model=List[PCBComponent])
async def get_pcb_components_api(pcb_id: str):
    """Fetch PCB components and coordinates."""
    project = await pcb_service.get_pcb_project(pcb_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"PCB project '{pcb_id}' not found.")
    return list(project.components.values())


@router.get("/{pcb_id}/nets", response_model=List[Net])
async def get_pcb_nets_api(pcb_id: str):
    """Fetch PCB nets and netlist topology."""
    project = await pcb_service.get_pcb_project(pcb_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"PCB project '{pcb_id}' not found.")
    return list(project.nets.values())


@router.get("/{pcb_id}/constraints", response_model=PCBConstraint)
async def get_pcb_constraints_api(pcb_id: str):
    """Fetch traceable PCB design rules and limits."""
    project = await pcb_service.get_pcb_project(pcb_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"PCB project '{pcb_id}' not found.")
    return project.constraints


@router.post("/{pcb_id}/validate", response_model=PCBValidationReport)
async def validate_pcb_api(pcb_id: str):
    """Execute all 12 PCB structural, electrical, and thermal validation checks."""
    try:
        report = await pcb_validation_service.validate_pcb_project(pcb_id)
        return report
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{pcb_id}/violations", response_model=PCBValidationReport)
async def get_pcb_violations_api(pcb_id: str):
    """Fetch current design violations."""
    return await validate_pcb_api(pcb_id)


@router.post("/{pcb_id}/physics/features", response_model=List[PhysicsFeaturePoint])
async def get_physics_features_api(pcb_id: str):
    """Extract dense numerical physics feature vectors across PCB domain."""
    try:
        return await physics_service.extract_features(pcb_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{pcb_id}/thermal/dataset", response_model=ThermalDataset)
async def generate_thermal_dataset_api(pcb_id: str):
    """Generate ground-truth dataset from numerical reference thermal solver."""
    try:
        return await physics_service.generate_thermal_dataset(pcb_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{pcb_id}/pinn/train", response_model=TrainingRunResult)
async def train_pinn_api(pcb_id: str, payload: TrainPINNRequest):
    """Train PCB Thermal PINN model."""
    try:
        return await pcb_optimization_service.train_pinn(
            project_id=pcb_id,
            epochs=payload.epochs,
            learning_rate=payload.learning_rate,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{pcb_id}/pinn/inference", response_model=PINNInferenceResult)
async def run_pinn_inference_api(pcb_id: str):
    """Evaluate 2D thermal field prediction using trained PINN model."""
    try:
        return await pcb_optimization_service.run_pinn_inference(project_id=pcb_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{pcb_id}/optimize")
async def optimize_pcb_placement_api(pcb_id: str, payload: OptimizePlacementRequest):
    """Run thermal placement optimization loop."""
    try:
        updated_proj, result = await pcb_optimization_service.optimize_placement(
            project_id=pcb_id,
            max_iterations=payload.max_iterations,
        )
        return {
            "status": "OPTIMIZED",
            "project": updated_proj.model_dump(),
            "optimization_result": result.model_dump(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{pcb_id}/pinn/metrics")
async def get_pinn_metrics_api(pcb_id: str):
    """Fetch latest PINN training and validation metrics."""
    result = pcb_optimization_service.get_latest_metrics(pcb_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"No PINN metrics found for project '{pcb_id}'.")
    return result.model_dump()
