"""
Pluggable Job Queue interface and In-Memory / SQLite queue implementations with DLQ.
"""

import abc
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from loguru import logger

from backend.workline.jobs.models import Job
from backend.workline.jobs.states import JobState


class JobQueue(abc.ABC):
    """Abstract Base Class for job queues."""

    @abc.abstractmethod
    async def enqueue(self, job: Job) -> Job:
        """Enqueue a new job."""
        pass

    @abc.abstractmethod
    async def dequeue(self) -> Optional[Job]:
        """Fetch next pending job to process."""
        pass

    @abc.abstractmethod
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve job record by ID."""
        pass

    @abc.abstractmethod
    async def update_job(self, job: Job) -> Job:
        """Persist updated job state."""
        pass

    @abc.abstractmethod
    async def list_jobs(self, project_id: Optional[str] = None, job_type: Optional[str] = None) -> List[Job]:
        """List jobs matching filters."""
        pass

    @abc.abstractmethod
    async def cancel_job(self, job_id: str) -> Optional[Job]:
        """Cancel a pending or running job."""
        pass


class LocalJobQueue(JobQueue):
    """Thread-safe In-Memory Job Queue with Dead Letter Queue (DLQ) support for local execution."""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._dlq: Dict[str, Job] = {}
        self._lock = asyncio.Lock()

    async def enqueue(self, job: Job) -> Job:
        async with self._lock:
            job.status = JobState.QUEUED
            self._jobs[job.job_id] = job
            await self._queue.put(job.job_id)
            logger.info(f"[JobQueue] Enqueued job {job.job_id} ({job.job_type})")
            return job

    async def dequeue(self) -> Optional[Job]:
        try:
            job_id = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            async with self._lock:
                job = self._jobs.get(job_id)
                if job:
                    self._queue.task_done()
                    return job
        except asyncio.TimeoutError:
            return None
        return None

    async def get_job(self, job_id: str) -> Optional[Job]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_job(self, job: Job) -> Job:
        async with self._lock:
            if job.status == JobState.DEAD_LETTER:
                self._dlq[job.job_id] = job
            self._jobs[job.job_id] = job
            return job

    async def list_jobs(self, project_id: Optional[str] = None, job_type: Optional[str] = None) -> List[Job]:
        async with self._lock:
            results = list(self._jobs.values())
            if project_id:
                results = [j for j in results if j.project_id == project_id]
            if job_type:
                results = [j for j in results if j.job_type == job_type]
            return results

    async def cancel_job(self, job_id: str) -> Optional[Job]:
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            if not job.status.is_terminal:
                job.status = JobState.CANCELLED
                job.completed_at = datetime.now(timezone.utc).isoformat()
                logger.info(f"[JobQueue] Cancelled job {job_id}")
            return job

    async def get_dlq_jobs(self) -> List[Job]:
        """Fetch all dead-lettered jobs."""
        async with self._lock:
            return list(self._dlq.values())


# Global singleton instance for local runtime
default_job_queue = LocalJobQueue()
