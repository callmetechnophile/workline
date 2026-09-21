from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.auth import get_current_user
from backend.services.workspace_service import (
    save_project, load_project, list_user_projects, 
    clone_project, delete_project, get_project_versions
)
from backend.services.bundle_service import (
    save_bundle, load_bundle, list_bundles, delete_bundle
)
from backend.services.connection_chatbot_service import ask_connection_assistant

router = APIRouter(prefix="/api/workspace", tags=["Workspace"])


class ProjectSaveSchema(BaseModel):
    name: str
    prompt: str
    bom: List[Dict[str, Any]]
    power_analysis: Dict[str, Any]
    dependency_graph: Dict[str, Any]
    wiring_diagram: Dict[str, Any]
    papers: List[Dict[str, Any]]
    gantt: List[Dict[str, Any]]
    code: Dict[str, Any]
    exports: Dict[str, Any]

class ProjectCloneSchema(BaseModel):
    project_id: int
    new_name: str

class ChatMessageSchema(BaseModel):
    message: str
    context: Dict[str, Any]

@router.get("/list")
async def get_projects_list(user_id: str = Depends(get_current_user)):
    try:
        return list_user_projects(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_active_project(payload: ProjectSaveSchema, user_id: str = Depends(get_current_user)):
    try:
        res = save_project(
            user_id=user_id,
            name=payload.name,
            prompt=payload.prompt,
            bom=payload.bom,
            power=payload.power_analysis,
            dependencies=payload.dependency_graph,
            wiring=payload.wiring_diagram,
            papers=payload.papers,
            gantt=payload.gantt,
            code=payload.code,
            exports=payload.exports
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load/{project_id}")
async def load_project_version(project_id: int, user_id: str = Depends(get_current_user)):
    try:
        return load_project(user_id, project_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clone")
async def duplicate_project(payload: ProjectCloneSchema, user_id: str = Depends(get_current_user)):
    try:
        return clone_project(user_id, payload.project_id, payload.new_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{project_id}")
async def delete_project_version(project_id: int, user_id: str = Depends(get_current_user)):
    try:
        return delete_project(user_id, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{name}")
async def get_name_versions(name: str, user_id: str = Depends(get_current_user)):
    try:
        return get_project_versions(user_id, name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_assistant(payload: ChatMessageSchema, user_id: str = Depends(get_current_user)):
    try:
        reply = ask_connection_assistant(payload.message, payload.context, user_id=user_id)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Bundle endpoints ───────────────────────────────────────────────────────────

class BundleSaveSchema(BaseModel):
    name: str
    description: Optional[str] = ""
    pipeline_data: Dict[str, Any]  # complete pipelineData object from frontend


@router.post("/save-bundle")
async def save_workspace_bundle(payload: BundleSaveSchema, user_id: str = Depends(get_current_user)):
    """
    Save the entire pipeline output as a single compressed bundle in PostgreSQL.
    Automatically increments version if a bundle with the same name already exists.
    """
    try:
        result = save_bundle(
            user_id=user_id,
            name=payload.name,
            pipeline_data=payload.pipeline_data,
            description=payload.description or ""
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bundle save failed: {str(e)}")


@router.get("/bundles")
async def get_bundles_list(user_id: str = Depends(get_current_user)):
    """List all saved bundles for the authenticated user."""
    try:
        return list_bundles(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bundle/{bundle_id}")
async def get_bundle(bundle_id: int, user_id: str = Depends(get_current_user)):
    """Load and decompress a specific bundle by ID."""
    try:
        return load_bundle(user_id, bundle_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bundle/{bundle_id}")
async def remove_bundle(bundle_id: int, user_id: str = Depends(get_current_user)):
    """Delete a specific workspace bundle."""
    try:
        return delete_bundle(user_id, bundle_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

