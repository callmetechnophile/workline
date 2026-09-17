"""
tests/workline/test_fabric_and_llm_hardening.py

Integration test suite verifying:
1. AgentControlFabric task execution dispatching into the async job pipeline.
2. Durable SQLite idempotency deduplication across separate task queries.
3. LLM Gateway Bedrock -> NVIDIA text inference fallback.
4. Strict capability isolation: NVIDIA fallback strictly rejects image generation/editing.
5. Job error classification: Non-retryable errors (auth denial, validation) avoid retries and route directly to DLQ.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from armourflow.fabric.fabric import AgentControlFabric
from armourflow.fabric.schemas import TaskState
from backend.database import init_db, get_idempotency_record
from backend.workline.jobs.errors import AuthorizationError, ContractValidationError, NonRetryableJobError, is_error_retryable
from backend.workline.jobs.models import Job
from backend.workline.jobs.queue import LocalJobQueue
from backend.workline.jobs.states import JobState
from backend.workline.jobs.worker import JobRegistry, JobWorker
from backend.workline.llm.gateway import BedrockProvider, LLMGateway, LocalMockProvider, NvidiaProvider
from backend.workline.llm.models import LLMCapability, LLMRequest


@pytest.fixture(autouse=True)
def setup_sqlite_tables():
    """Ensure SQLite database has idempotency_keys table initialized."""
    init_db()


@pytest.mark.asyncio
async def test_fabric_submit_task_enqueues_job_and_completes():
    """Verify fabric.submit_task() enqueues a Job into LocalJobQueue and persists result."""
    fabric = AgentControlFabric.get_instance()
    
    # Submit task to SecurityThreatModelingAgent (agent.22) with declared operation
    payload = {
        "operation": "map_attack_surface",
        "system_name": "TelemetryGateway",
        "interfaces": [{"name": "CAN_BUS", "protocol": "CAN2.0B"}],
    }
    
    task = await fabric.submit_task(
        payload=payload,
        target_agent_id="agent.22",
        project_id="test_proj_1",
        sync_wait=True,
    )

    assert task.state == TaskState.COMPLETED
    assert task.result is not None
    
    # Check that job was recorded in fabric's job queue
    jobs = await fabric.job_queue.list_jobs(project_id="test_proj_1")
    assert len(jobs) >= 1
    recent_job = jobs[-1]
    assert recent_job.job_type == "fabric_agent_execution"
    assert recent_job.status == JobState.SUCCEEDED
    assert recent_job.input_reference.get("task_id") == task.task_id


@pytest.mark.asyncio
async def test_durable_sqlite_idempotency():
    """Verify idempotency persists in SQLite database and deduplicates subsequent task submissions."""
    import uuid
    fabric = AgentControlFabric.get_instance()
    idemp_key = f"durable-idemp-{uuid.uuid4().hex[:10]}"

    payload = {
        "operation": "discover_assets",
        "assets": [{"asset_id": "FLASH_KEY_STORE", "criticality": "HIGH"}],
    }

    # First submission
    task1 = await fabric.submit_task(
        payload=payload,
        target_agent_id="agent.22",
        project_id="test_proj_idemp",
        idempotency_key=idemp_key,
        sync_wait=True,
    )
    assert task1.state == TaskState.COMPLETED

    # Verify SQLite record was stored
    record = get_idempotency_record(idemp_key)
    assert record is not None
    assert record["task_id"] == task1.task_id
    assert record["status"] == "COMPLETED"

    # Wipe in-memory cache to simulate fresh server process restart
    fabric._idempotency_cache.clear()
    fabric._tasks.clear()

    # Second submission with same idempotency key
    task2 = await fabric.submit_task(
        payload=payload,
        target_agent_id="agent.22",
        project_id="test_proj_idemp",
        idempotency_key=idemp_key,
        sync_wait=True,
    )

    # Must reconstitute and return identical task without duplicate execution
    assert task2.task_id == task1.task_id
    assert task2.state == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_llm_gateway_nvidia_fallback_for_text():
    """Verify Bedrock falls back to NVIDIA for text generation when Bedrock fails."""
    # Mock NvidiaProvider
    mock_nvidia = NvidiaProvider(api_key="nvapi-mock-test-key")
    
    async def mock_nvidia_generate(req: LLMRequest):
        from backend.workline.llm.models import LLMResponse, LLMUsage
        return LLMResponse(
            text="NVIDIA NIM synthesized response for text inference.",
            model_id=mock_nvidia.model_name,
            provider="nvidia",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    mock_nvidia.generate = AsyncMock(side_effect=mock_nvidia_generate)

    # Bedrock provider configured with mock NVIDIA fallback
    bedrock = BedrockProvider(nvidia_fallback=mock_nvidia)
    gateway = LLMGateway(provider=bedrock)

    req = LLMRequest(
        prompt="Analyze EMI shielding for 5GHz RF transceiver",
        capability=LLMCapability.TEXT_GENERATION,
    )

    # Force Anthropic Bedrock adapter to fail to trigger fallback
    with patch("backend.workline.ai.bedrock.adapters.anthropic.anthropic_adapter.generate", side_effect=ConnectionError("Bedrock timeout")):
        resp = await gateway.provider.generate(req)
        assert resp.provider == "nvidia"
        assert "NVIDIA NIM synthesized response" in resp.text
        assert mock_nvidia.generate.called



@pytest.mark.asyncio
async def test_nvidia_strictly_rejects_image_generation():
    """
    CRITICAL ARCHITECTURAL SAFETY INVARIANT:
    NVIDIA fallback provider must NEVER accept image generation or editing requests.
    """
    nvidia = NvidiaProvider(api_key="nvapi-mock-key")

    img_request = LLMRequest(
        prompt="Render 4-layer PCB schematic in 3D isometric view",
        capability=LLMCapability.IMAGE_GENERATION,
    )

    with pytest.raises(ValueError) as exc_info:
        await nvidia.generate(img_request)

    err = str(exc_info.value)
    assert "strictly NOT supported" in err
    assert "must NEVER route image generation" in err


@pytest.mark.asyncio
async def test_job_error_classification_no_retry_for_fatal_errors():
    """Verify NonRetryableJobError, AuthorizationError, and contract faults avoid retry loops."""
    # Test error classifier
    auth_err = AuthorizationError("User unauthorized for agent action")
    contract_err = ContractValidationError("Missing required parameter 'project_id'")
    transient_err = ConnectionResetError("Remote connection closed unexpectedly")

    assert is_error_retryable(auth_err) is False
    assert is_error_retryable(contract_err) is False
    assert is_error_retryable(transient_err) is True

    # Test worker behavior on non-retryable fault: moves immediately to DLQ without retries
    queue = LocalJobQueue()
    registry = JobRegistry()

    async def auth_failing_handler(job: Job):
        raise AuthorizationError("AUTHORIZATION_DENIED: Policy boundary violation")

    registry.register("auth_failing_task", auth_failing_handler)
    worker = JobWorker(queue=queue, registry=registry)
    await worker.start()

    try:
        job = Job(job_type="auth_failing_task", max_retries=3)
        await queue.enqueue(job)

        # Allow worker processing
        await asyncio.sleep(0.4)
        dlq_job = await queue.get_job(job.job_id)
        assert dlq_job.status == JobState.DEAD_LETTER
        assert dlq_job.retry_count == 0  # Zero retries attempted because it's non-retryable!
        assert "NON_RETRYABLE_FAULT" in dlq_job.error
    finally:
        await worker.stop()
