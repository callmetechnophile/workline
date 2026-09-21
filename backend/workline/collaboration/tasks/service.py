"""
Workline AI — Collaboration Task Service.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from backend.workline.collaboration.tasks.models import (
    CollaborationTask,
    CreateTaskRequest,
    RelatedArtifact,
    TaskPriority,
    TaskStatus,
    UpdateTaskRequest,
)


class TaskService:
    """Service for managing engineering collaboration tasks and artifact linkages."""

    def __init__(self):
        # task_id -> CollaborationTask
        self._tasks: Dict[str, CollaborationTask] = {}

    def create_task(
        self,
        payload: CreateTaskRequest,
        creator_id: str,
        creator_name: Optional[str] = None,
    ) -> CollaborationTask:
        """Creates a new collaboration task with optional artifact link."""
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        task = CollaborationTask(
            id=task_id,
            project_id=payload.project_id,
            team_id=payload.team_id,
            title=payload.title.strip(),
            description=payload.description or "",
            status=payload.status or TaskStatus.TODO,
            priority=payload.priority or TaskPriority.MEDIUM,
            assignee_id=payload.assignee_id,
            assignee_name=payload.assignee_name,
            creator_id=creator_id,
            creator_name=creator_name or creator_id,
            due_date=payload.due_date,
            labels=payload.labels or [],
            related_artifact=payload.related_artifact,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task_id] = task
        logger.info(f"[Tasks] Created task {task_id}: '{task.title}' in project {task.project_id}")
        return task

    def get_task(self, task_id: str) -> Optional[CollaborationTask]:
        """Gets a single task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        project_id: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[CollaborationTask]:
        """Lists tasks filtered by project, team, status, assignee, or priority."""
        tasks = list(self._tasks.values())

        if project_id:
            tasks = [t for t in tasks if t.project_id == project_id]
        if team_id:
            tasks = [t for t in tasks if t.team_id == team_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if assignee_id:
            tasks = [t for t in tasks if t.assignee_id == assignee_id]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]

        # Sort by updated_at descending
        tasks.sort(key=lambda t: t.updated_at, reverse=True)
        return tasks

    def update_task(
        self,
        task_id: str,
        payload: UpdateTaskRequest,
        actor_id: str,
    ) -> CollaborationTask:
        """Updates an existing task."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task '{task_id}' not found.")

        now = datetime.now(timezone.utc).isoformat()

        if payload.title is not None and payload.title.strip():
            task.title = payload.title.strip()
        if payload.description is not None:
            task.description = payload.description
        if payload.status is not None:
            task.status = payload.status
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.assignee_id is not None:
            task.assignee_id = payload.assignee_id
        if payload.assignee_name is not None:
            task.assignee_name = payload.assignee_name
        if payload.due_date is not None:
            task.due_date = payload.due_date
        if payload.labels is not None:
            task.labels = payload.labels
        if payload.related_artifact is not None:
            task.related_artifact = payload.related_artifact

        task.updated_at = now
        logger.info(f"[Tasks] Updated task {task_id} by {actor_id}")
        return task

    def delete_task(self, task_id: str, actor_id: str) -> bool:
        """Deletes a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.info(f"[Tasks] Deleted task {task_id} by {actor_id}")
            return True
        return False


# Global singleton instance
task_service = TaskService()
