"""
ECS Fargate Background Worker Pool Entrypoint.
Continuously consumes tasks from Amazon SQS, executes 27 engineering agents via
Control Fabric, commits state to SurrealDB, saves artifacts to S3, and handles DLQ routing.
"""

import asyncio
import os
import signal
import sys
import time
from typing import Any, Dict, Optional
from loguru import logger

from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager
from backend.workline.artifacts.store import default_artifact_store
from backend.workline.jobs.models import Job
from backend.workline.jobs.states import JobState
from backend.workline.jobs.sqs_queue import get_job_queue, SQSJobQueue
from armourflow.registry import AuthoritativeAgentRegistry


class ECSAgentWorker:
    """
    Worker task consumer running on AWS ECS Fargate.
    """

    def __init__(self):
        self.queue = get_job_queue()
        self.registry = AuthoritativeAgentRegistry()
        self.running = True
        self.tasks_processed = 0
        self.tasks_failed = 0

    def handle_shutdown(self, signum, frame):
        logger.info(f"[ECSWorker] Received shutdown signal {signum}. Initiating graceful shutdown...")
        self.running = False

    async def initialize(self):
        """Connect to SurrealDB and Qdrant with graceful resilience."""
        logger.info("[ECSWorker] Initializing ECS Agent Worker...")
        try:
            connected_surreal = await surreal_db.connect()
            logger.info(f"[ECSWorker] SurrealDB connection status: {connected_surreal}")
        except Exception as e:
            logger.warning(f"[ECSWorker] SurrealDB connect error: {e}")

        try:
            connected_qdrant = qdrant_manager.connect()
            if connected_qdrant:
                qdrant_manager.init_collections()
            logger.info(f"[ECSWorker] Qdrant connection status: {connected_qdrant}")
        except Exception as e:
            logger.warning(f"[ECSWorker] Qdrant connect error: {e}")

        logger.info(f"[ECSWorker] Agent Registry initialized with {len(self.registry._agents)} agents.")

    async def execute_task(self, job: Job) -> bool:
        """Execute task through target agent, commit results to SurrealDB and S3."""
        logger.info(f"[ECSWorker] Processing Job {job.job_id} | Type: {job.job_type} | Project: {job.project_id}")
        start_time = time.time()
        
        job.status = JobState.RUNNING
        job.started_at = time.time()
        await self.queue.update_job(job)

        # Update SurrealDB task status if available
        try:
            await surreal_db.query(
                "UPDATE type::thing('task', $job_id) SET status = 'RUNNING', started_at = time::now();",
                vars={"job_id": job.job_id}
            )
        except Exception:
            pass

        agent_id = job.payload.get("agent_id") or job.job_type
        manifest = self.registry.get_agent(agent_id)

        try:
            if not manifest:
                raise ValueError(f"Agent '{agent_id}' not found in AuthoritativeAgentRegistry.")

            # Load and instantiate agent
            entrypoint = manifest.entrypoint
            mod_path, cls_name = entrypoint.split(":")
            import importlib
            mod = importlib.import_module(mod_path)
            agent_cls = getattr(mod, cls_name)
            agent_instance = agent_cls()

            # Execute agent
            input_payload = job.payload.get("input", {})
            if hasattr(agent_instance, "run"):
                import inspect
                if inspect.iscoroutinefunction(agent_instance.run):
                    result = await agent_instance.run(input_payload)
                else:
                    result = agent_instance.run(input_payload)
            else:
                raise AttributeError(f"Agent class {cls_name} has no 'run' method.")

            # Serialize result
            result_dict = result.model_dump() if hasattr(result, "model_dump") else (result if isinstance(result, dict) else {"output": str(result)})
            
            # Check for binary output to save to S3
            if "binary_artifact" in result_dict:
                bin_data = result_dict.pop("binary_artifact")
                artifact = await default_artifact_store.put_artifact(
                    filename=result_dict.get("filename", f"{job.job_id}_output.bin"),
                    data=bin_data,
                    project_id=job.project_id,
                    category="agent_output",
                )
                result_dict["artifact_id"] = artifact.artifact_id
                result_dict["artifact_url"] = artifact.download_url

            duration = round(time.time() - start_time, 3)
            job.status = JobState.COMPLETED
            job.completed_at = time.time()
            job.result = result_dict
            await self.queue.update_job(job)

            # Persist completion in SurrealDB
            try:
                await surreal_db.query(
                    """
                    UPDATE type::thing('task', $job_id) SET 
                        status = 'COMPLETED',
                        completed_at = time::now(),
                        result = $result,
                        duration_sec = $duration;
                    """,
                    vars={"job_id": job.job_id, "result": result_dict, "duration": duration}
                )
            except Exception:
                pass

            # Acknowledge / Delete from SQS
            if isinstance(self.queue, SQSJobQueue):
                await self.queue.acknowledge_job(job.job_id)

            self.tasks_processed += 1
            logger.info(f"[ECSWorker] Successfully completed Job {job.job_id} in {duration}s.")
            return True

        except Exception as e:
            duration = round(time.time() - start_time, 3)
            logger.error(f"[ECSWorker] Error executing Job {job.job_id}: {e}")
            job.retry_count = getattr(job, "retry_count", 0) + 1
            max_retries = getattr(job, "max_retries", 3)

            if job.retry_count >= max_retries:
                logger.critical(f"[ECSWorker] Job {job.job_id} exceeded max retries ({max_retries}). Forwarding to DLQ.")
                if isinstance(self.queue, SQSJobQueue):
                    await self.queue.send_to_dlq(job, error_reason=str(e))
                else:
                    job.status = JobState.DEAD_LETTER
                    job.error = str(e)
                    await self.queue.update_job(job)
            else:
                job.status = JobState.FAILED
                job.error = str(e)
                await self.queue.update_job(job)

            # Persist failure in SurrealDB
            try:
                await surreal_db.query(
                    """
                    UPDATE type::thing('task', $job_id) SET 
                        status = $status,
                        error = $error,
                        completed_at = time::now();
                    """,
                    vars={"job_id": job.job_id, "status": job.status.value, "error": str(e)}
                )
            except Exception:
                pass

            self.tasks_failed += 1
            return False

    async def run_loop(self):
        """Main polling loop."""
        await self.initialize()
        logger.info("[ECSWorker] Worker polling loop started. Awaiting SQS jobs...")

        while self.running:
            try:
                job = await self.queue.dequeue()
                if job:
                    await self.execute_task(job)
                else:
                    await asyncio.sleep(1.0)
            except Exception as e:
                logger.error(f"[ECSWorker] Unexpected loop error: {e}")
                await asyncio.sleep(2.0)

        logger.info(f"[ECSWorker] Exiting worker loop. Stats: Processed={self.tasks_processed}, Failed={self.tasks_failed}")


def main():
    worker = ECSAgentWorker()
    signal.signal(signal.SIGINT, worker.handle_shutdown)
    signal.signal(signal.SIGTERM, worker.handle_shutdown)
    asyncio.run(worker.run_loop())


if __name__ == "__main__":
    main()
