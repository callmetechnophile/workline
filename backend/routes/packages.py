from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.auth import get_current_user
from backend.database import save_package, get_user_history

router = APIRouter(prefix="/api/packages", tags=["Packages"])

class SavePackageSchema(BaseModel):
    intent: str
    readiness_score: int
    risk_score: int
    optimization_score: int
    data: Dict[str, Any]
    project_name: Optional[str] = None
    system_specification: Optional[str] = None
    target_days: Optional[int] = 30
    engineering_template: Optional[str] = None
    team_id: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = "active"

class PackageResponseSchema(BaseModel):
    id: int
    project_id: Optional[str] = None
    project_name: Optional[str] = "Untitled Engineering Project"
    system_specification: Optional[str] = None
    intent: str
    target_days: Optional[int] = 30
    engineering_template: Optional[str] = None
    team_id: Optional[str] = None
    status: Optional[str] = "active"
    readiness_score: int
    risk_score: int
    optimization_score: int
    data: Dict[str, Any]
    timestamp: str

@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_user_package(
    payload: SavePackageSchema,
    user_id: str = Depends(get_current_user)
):
    try:
        save_package(
            user_id=user_id,
            intent=payload.intent,
            readiness=payload.readiness_score,
            risk=payload.risk_score,
            optimization=payload.optimization_score,
            data=payload.data,
            project_name=payload.project_name,
            system_specification=payload.system_specification,
            target_days=payload.target_days or 30,
            engineering_template=payload.engineering_template,
            team_id=payload.team_id,
            project_id=payload.project_id,
            status=payload.status or "active",
        )
        return {"status": "SUCCESS", "message": "Package saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save package: {str(e)}"
        )

@router.get("/history", response_model=List[PackageResponseSchema])
async def get_user_package_history(
    user_id: str = Depends(get_current_user)
):
    try:
        history = get_user_history(user_id=user_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )
