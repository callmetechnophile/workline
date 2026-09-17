"""
Pydantic data models for asynchronous jobs.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from backend.workline.jobs.states import JobState


class Job(BaseModel):
    """Generic Job schema representing an asynchronous execution task."""
    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:12]}")
    project_id: Optional[str] = None
    job_type: str = Field(description="Action/job type descriptor, e.g., 'pcb_simulation', 'procurement_search'")
    status: JobState = Field(default=JobState.PENDING)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    requested_by: Optional[str] = Field(default="system", description="User or agent identifier who requested the job")
    input_reference: Dict[str, Any] = Field(default_factory=dict, description="Job parameters or reference payload")
    output_reference: Optional[Dict[str, Any]] = Field(default=None, description="Output payload or artifact URIs")
    error: Optional[str] = Field(default=None, description="Detailed error message if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts executed")
    max_retries: int = Field(default=3, description="Maximum retry attempts allowed before DLQ")
    correlation_id: Optional[str] = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}", description="Distributed correlation ID")


class JobCreateRequest(BaseModel):
    """Request payload for dispatching a job."""
    job_type: str
    project_id: Optional[str] = None
    input_reference: Dict[str, Any] = Field(default_factory=dict)
    requested_by: Optional[str] = "system"
    max_retries: int = 3
    correlation_id: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Status inquiry response."""
    job: Job
    progress_percentage: Optional[float] = None
    logs: Optional[list[str]] = None
