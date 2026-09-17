"""
Job Worker, Dispatcher, and Registry with retry and error backoff handling.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, Optional
from loguru import logger

from backend.workline.jobs.models import Job
from backend.workline.jobs.queue import JobQueue, default_job_queue
from backend.workline.jobs.states import JobState

# Type alias for async job handler: func(job: Job) -> dict
JobHandler = Callable[[Job], Coroutine[Any, Any, Dict[str, Any]]]


class JobRegistry:
    """Registry mapping job_type strings to async callable worker functions."""

    def __init__(self):
        self._handlers: Dict[str, JobHandler] = {}

    def register(self, job_type: str, handler: JobHandler):
        """Register a handler for a specific job_type."""
        self._handlers[job_type] = handler
        logger.info(f"[JobRegistry] Registered handler for job type '{job_type}'")

    def get(self, job_type: str) -> Optional[JobHandler]:
        return self._handlers.get(job_type)


default_job_registry = JobRegistry()


class JobWorker:
    """Background worker daemon that polls the JobQueue and runs registered handlers."""

    def __init__(self, queue: Optional[JobQueue] = None, registry: Optional[JobRegistry] = None):
        self.queue = queue or default_job_queue
        self.registry = registry or default_job_registry
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start background processing loop."""
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._run_loop())
        logger.info("[JobWorker] Background worker started")

    async def stop(self):
        """Stop background worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("[JobWorker] Background worker stopped")

    async def _run_loop(self):
        while self._running:
            try:
                job = await self.queue.dequeue()
                if job:
                    # Run processing concurrently
                    asyncio.create_task(self._process_job(job))
                else:
                    await asyncio.sleep(0.2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[JobWorker] Unexpected error in loop: {e}")
                await asyncio.sleep(0.5)

    async def _process_job(self, job: Job):
        if job.status == JobState.CANCELLED:
            return

        job.status = JobState.RUNNING
        job.started_at = datetime.now(timezone.utc).isoformat()
        await self.queue.update_job(job)
        logger.info(f"[JobWorker] Processing job {job.job_id} ({job.job_type})")

        handler = self.registry.get(job.job_type)
        if not handler:
            job.status = JobState.FAILED
            job.error = f"No handler registered for job type '{job.job_type}'"
            job.completed_at = datetime.now(timezone.utc).isoformat()
            await self.queue.update_job(job)
            logger.error(job.error)
            return

        try:
            output = await handler(job)
            job.status = JobState.SUCCEEDED
            job.output_reference = output
            job.completed_at = datetime.now(timezone.utc).isoformat()
            await self.queue.update_job(job)
            logger.info(f"[JobWorker] Job {job.job_id} succeeded")
        except Exception as exc:
            logger.warning(f"[JobWorker] Job {job.job_id} failed with error: {exc}")
            job.retry_count += 1
            if job.retry_count <= job.max_retries:
                job.status = JobState.RETRYING
                job.error = str(exc)
                await self.queue.update_job(job)
                # Exponential backoff before re-enqueueing
                await asyncio.sleep(0.5 * (2 ** (job.retry_count - 1)))
                await self.queue.enqueue(job)
            else:
                job.status = JobState.DEAD_LETTER
                job.error = f"Max retries exceeded ({job.max_retries}). Last error: {exc}"
                job.completed_at = datetime.now(timezone.utc).isoformat()
                await self.queue.update_job(job)
                logger.error(f"[JobWorker] Job {job.job_id} moved to DLQ: {job.error}")


default_job_worker = JobWorker()
