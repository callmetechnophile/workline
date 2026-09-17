"""
FastAPI router for asynchronous job submission, status queries, and cancellation.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from backend.workline.jobs.models import Job, JobCreateRequest, JobStatusResponse
from backend.workline.jobs.queue import default_job_queue
from backend.workline.jobs.states import JobState

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=Job, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(req: JobCreateRequest):
    """Submit a new asynchronous job."""
    job = Job(
        project_id=req.project_id,
        job_type=req.job_type,
        input_reference=req.input_reference,
        requested_by=req.requested_by or "system",
        max_retries=req.max_retries,
        correlation_id=req.correlation_id,
    )
    enqueued = await default_job_queue.enqueue(job)
    return enqueued


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get status and output of a specific job."""
    job = await default_job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Progress indication
    progress = 100.0 if job.status.is_terminal else (50.0 if job.status == JobState.RUNNING else 10.0)
    return JobStatusResponse(job=job, progress_percentage=progress)


@router.post("/{job_id}/cancel", response_model=Job)
async def cancel_job(job_id: str):
    """Cancel a pending or running job."""
    job = await default_job_queue.cancel_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("", response_model=List[Job])
async def list_jobs(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
):
    """List all registered jobs."""
    return await default_job_queue.list_jobs(project_id=project_id, job_type=job_type)


@router.get("/dlq/all", response_model=List[Job])
async def list_dlq_jobs():
    """Retrieve all dead-lettered jobs for investigation."""
    return await default_job_queue.get_dlq_jobs()
