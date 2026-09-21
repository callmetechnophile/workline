"""
FastAPI router for Collaboration Tasks.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query, Request

from backend.workline.collaboration.tasks.models import (
    CollaborationTask,
    CreateTaskRequest,
    TaskPriority,
    TaskStatus,
    UpdateTaskRequest,
)
from backend.workline.collaboration.tasks.service import task_service

router = APIRouter(prefix="/api/tasks", tags=["Collaboration Tasks"])


def get_current_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")) -> str:
    """Extracts authenticated user ID from headers."""
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()
    return "user_default_owner"


@router.post("", response_model=CollaborationTask)
def create_task(
    payload: CreateTaskRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
):
    """Creates a new engineering collaboration task."""
    actor_id = get_current_user_id(x_user_id)
    return task_service.create_task(
        payload=payload,
        creator_id=actor_id,
        creator_name=x_user_name or actor_id,
    )


@router.get("", response_model=List[CollaborationTask])
def list_tasks(
    project_id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    assignee_id: Optional[str] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
):
    """Lists tasks with optional status, priority, or assignee filtering."""
    return task_service.list_tasks(
        project_id=project_id,
        team_id=team_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
    )


@router.get("/{task_id}", response_model=CollaborationTask)
def get_task(task_id: str):
    """Retrieves a single task by ID."""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.patch("/{task_id}", response_model=CollaborationTask)
def update_task(
    task_id: str,
    payload: UpdateTaskRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Updates a task."""
    actor_id = get_current_user_id(x_user_id)
    try:
        return task_service.update_task(task_id, payload, actor_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Deletes a task."""
    actor_id = get_current_user_id(x_user_id)
    success = task_service.delete_task(task_id, actor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "DELETED", "task_id": task_id}
