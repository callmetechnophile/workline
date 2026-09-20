import pytest
from backend.workline.jobs.models import Job
from backend.workline.jobs.states import JobState
from backend.workline.jobs.sqs_queue import SQSJobQueue


@pytest.mark.asyncio
async def test_sqs_job_queue_lifecycle():
    queue = SQSJobQueue()  # Uses fallback LocalJobQueue when SQS URL is not set
    
    job = Job(
        job_id="test-job-001",
        job_type="thermal_simulation",
        project_id="proj-101",
        payload={"ambient": 25.0}
    )

    # Enqueue
    enqueued = await queue.enqueue(job)
    assert enqueued.status == JobState.QUEUED

    # Dequeue
    dequeued = await queue.dequeue()
    assert dequeued is not None
    assert dequeued.job_id == "test-job-001"

    # DLQ routing test
    await queue.send_to_dlq(dequeued, error_reason="Simulation convergence failure")
    dlq_job = await queue.get_job("test-job-001")
    assert dlq_job.status == JobState.DEAD_LETTER
    assert dlq_job.error == "Simulation convergence failure"
