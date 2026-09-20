"""
Amazon SQS Job Queue implementation with Dead Letter Queue (DLQ) support,
exponential backoff, and transparent local queue fallback.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional
from loguru import logger

from backend.workline.jobs.models import Job
from backend.workline.jobs.states import JobState
from backend.workline.jobs.queue import JobQueue, LocalJobQueue


class SQSJobQueue(JobQueue):
    """
    Production-ready Amazon SQS Job Queue.
    Dispatches asynchronous agent execution tasks to AWS SQS and routes failed tasks to DLQ.
    """

    def __init__(
        self,
        queue_url: Optional[str] = None,
        dlq_url: Optional[str] = None,
        region_name: Optional[str] = None,
        fallback_queue: Optional[JobQueue] = None,
    ):
        self.queue_url = queue_url or os.environ.get("WORKLINE_SQS_QUEUE_URL")
        self.dlq_url = dlq_url or os.environ.get("WORKLINE_SQS_DLQ_URL")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.fallback = fallback_queue or LocalJobQueue()
        self._sqs_client = None
        self._receipt_handles: Dict[str, str] = {}  # job_id -> receipt_handle
        self._jobs_cache: Dict[str, Job] = {}
        self._init_sqs_client()

    def _init_sqs_client(self):
        if not self.queue_url:
            logger.debug("[SQSJobQueue] WORKLINE_SQS_QUEUE_URL not set; operating on LocalJobQueue fallback.")
            return

        try:
            import boto3
            from botocore.config import Config
            config = Config(
                region_name=self.region_name,
                retries={"max_attempts": 3, "mode": "standard"},
            )
            self._sqs_client = boto3.client("sqs", config=config)
            logger.info(f"[SQSJobQueue] Initialized SQS client for queue {self.queue_url}")
        except Exception as e:
            logger.warning(f"[SQSJobQueue] Failed to initialize boto3 SQS client ({e}); using local fallback.")
            self._sqs_client = None

    async def enqueue(self, job: Job) -> Job:
        job.status = JobState.QUEUED
        self._jobs_cache[job.job_id] = job

        if not self._sqs_client or not self.queue_url:
            return await self.fallback.enqueue(job)

        try:
            body = job.model_dump_json()
            params: Dict[str, Any] = {
                "QueueUrl": self.queue_url,
                "MessageBody": body,
                "MessageAttributes": {
                    "JobId": {"DataType": "String", "StringValue": job.job_id},
                    "JobType": {"DataType": "String", "StringValue": job.job_type},
                    "ProjectId": {"DataType": "String", "StringValue": job.project_id},
                },
            }

            if self.queue_url.endswith(".fifo"):
                params["MessageGroupId"] = job.project_id or "default-group"
                params["MessageDeduplicationId"] = f"{job.job_id}-{int(time.time())}"

            resp = self._sqs_client.send_message(**params)
            logger.info(f"[SQSJobQueue] Enqueued job {job.job_id} to SQS (MessageId: {resp.get('MessageId')})")
            return job
        except Exception as e:
            logger.warning(f"[SQSJobQueue] SQS enqueue failed ({e}); falling back to local queue.")
            return await self.fallback.enqueue(job)

    async def dequeue(self) -> Optional[Job]:
        if not self._sqs_client or not self.queue_url:
            return await self.fallback.dequeue()

        try:
            resp = self._sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=2,  # Short poll for responsiveness, production ECS uses 20
                MessageAttributeNames=["All"],
                AttributeNames=["All"],
            )
            messages = resp.get("Messages", [])
            if not messages:
                return None

            msg = messages[0]
            receipt_handle = msg["ReceiptHandle"]
            body = msg["Body"]
            
            job_dict = json.loads(body)
            job = Job(**job_dict)
            self._receipt_handles[job.job_id] = receipt_handle
            self._jobs_cache[job.job_id] = job
            return job
        except Exception as e:
            logger.warning(f"[SQSJobQueue] SQS dequeue error ({e}); evaluating fallback.")
            return await self.fallback.dequeue()

    async def acknowledge_job(self, job_id: str) -> bool:
        """Deletes processed message from SQS queue."""
        receipt_handle = self._receipt_handles.pop(job_id, None)
        if not self._sqs_client or not self.queue_url or not receipt_handle:
            return True

        try:
            self._sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
            logger.info(f"[SQSJobQueue] Acknowledged/Deleted job {job_id} from SQS.")
            return True
        except Exception as e:
            logger.warning(f"[SQSJobQueue] Failed to delete SQS message for job {job_id}: {e}")
            return False

    async def send_to_dlq(self, job: Job, error_reason: str) -> bool:
        """Move failed job to Dead Letter Queue."""
        job.status = JobState.DEAD_LETTER
        job.error = error_reason
        self._jobs_cache[job.job_id] = job

        # Delete from main queue first
        await self.acknowledge_job(job.job_id)

        if not self._sqs_client or not self.dlq_url:
            await self.fallback.update_job(job)
            return True

        try:
            body = job.model_dump_json()
            self._sqs_client.send_message(
                QueueUrl=self.dlq_url,
                MessageBody=body,
                MessageAttributes={
                    "JobId": {"DataType": "String", "StringValue": job.job_id},
                    "Reason": {"DataType": "String", "StringValue": error_reason[:250]},
                }
            )
            logger.info(f"[SQSJobQueue] Job {job.job_id} sent to DLQ: {self.dlq_url}")
            return True
        except Exception as e:
            logger.error(f"[SQSJobQueue] Failed to forward job {job.job_id} to DLQ: {e}")
            return False

    async def get_job(self, job_id: str) -> Optional[Job]:
        if job_id in self._jobs_cache:
            return self._jobs_cache[job_id]
        return await self.fallback.get_job(job_id)

    async def update_job(self, job: Job) -> Job:
        self._jobs_cache[job.job_id] = job
        return await self.fallback.update_job(job)

    async def list_jobs(self, project_id: Optional[str] = None, job_type: Optional[str] = None) -> List[Job]:
        jobs = list(self._jobs_cache.values())
        if project_id:
            jobs = [j for j in jobs if j.project_id == project_id]
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        if not jobs:
            return await self.fallback.list_jobs(project_id, job_type)
        return jobs

    async def cancel_job(self, job_id: str) -> Optional[Job]:
        await self.acknowledge_job(job_id)
        job = await self.get_job(job_id)
        if job:
            job.status = JobState.CANCELLED
            self._jobs_cache[job_id] = job
        return await self.fallback.cancel_job(job_id)


# Factory function
def get_job_queue() -> JobQueue:
    """Returns SQSJobQueue if WORKLINE_SQS_QUEUE_URL is set, else LocalJobQueue."""
    if os.environ.get("WORKLINE_SQS_QUEUE_URL"):
        return SQSJobQueue()
    return LocalJobQueue()
