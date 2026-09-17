"""
Comprehensive unit and integration test suite verifying upgraded production platform architecture:
- Phase 1: Asynchronous Jobs & DLQ
- Phase 2: Agent Execution State & Checkpoints
- Phase 3: Pluggable Artifact Storage
- Phase 4: LLM Gateway with LocalMock Fallback
- Phase 5: Unified Retrieval & Evidence
- Phase 6: RBAC & Permission Boundaries
- Phase 7: Append-Only Immutable Audit Trail
- Phase 8: Observability & Metrics
- Phase 9/10: Engineering Lifecycle Stage Gates
"""

import pytest
import asyncio
from fastapi import HTTPException

# Phase 1: Jobs
from backend.workline.jobs.models import Job
from backend.workline.jobs.states import JobState
from backend.workline.jobs.queue import LocalJobQueue
from backend.workline.jobs.worker import JobWorker, JobRegistry

# Phase 2: Agent State
from backend.workline.agent_state.models import (
    AgentRun,
    AgentRunStatus,
    AgentCheckpoint,
    AgentDecision,
    ToolExecution,
)
from backend.workline.agent_state.store import LocalAgentStateStore

# Phase 3: Artifacts
from backend.workline.artifacts.store import FilesystemArtifactStore

# Phase 4: LLM Gateway
from backend.workline.llm.gateway import LLMGateway, LocalMockProvider
from backend.workline.llm.models import LLMRequest

# Phase 5: Retrieval
from backend.workline.retrieval_service.service import UnifiedRetrievalService
from backend.workline.retrieval_service.models import RetrievalQuery

# Phase 6: Security & RBAC
from backend.workline.security.models import Role, ActionTier, Permission, SecurityContext
from backend.workline.security.gates import GovernancePolicyGate

# Phase 7: Audit
from backend.workline.audit.models import AuditEvent
from backend.workline.audit.logger import AuditTrail

# Phase 8: Observability
from backend.workline.observability.metrics import MetricsCollector

# Phase 9/10: Lifecycle Gates
from backend.workline.pipeline.gates import LifecycleStageGate, LifecycleGateViolation


@pytest.mark.asyncio
async def test_job_queue_and_worker_success():
    """Verify job lifecycle from enqueue -> running -> succeeded."""
    queue = LocalJobQueue()
    registry = JobRegistry()
    
    async def sample_handler(job: Job):
        return {"result": f"processed_{job.input_reference.get('key')}"}

    registry.register("sample_task", sample_handler)
    worker = JobWorker(queue=queue, registry=registry)
    await worker.start()

    try:
        job = Job(job_type="sample_task", input_reference={"key": "val123"})
        enqueued = await queue.enqueue(job)
        assert enqueued.status == JobState.QUEUED

        # Allow worker processing
        await asyncio.sleep(0.3)
        completed_job = await queue.get_job(enqueued.job_id)
        assert completed_job.status == JobState.SUCCEEDED
        assert completed_job.output_reference == {"result": "processed_val123"}
        assert completed_job.completed_at is not None
    finally:
        await worker.stop()


@pytest.mark.asyncio
async def test_job_dlq_on_exceeded_retries():
    """Verify job moves to DLQ when handler continuously fails beyond max_retries."""
    queue = LocalJobQueue()
    registry = JobRegistry()

    async def failing_handler(job: Job):
        raise ValueError("Simulated irrecoverable compute fault")

    registry.register("failing_task", failing_handler)
    worker = JobWorker(queue=queue, registry=registry)
    await worker.start()

    try:
        job = Job(job_type="failing_task", max_retries=1)
        await queue.enqueue(job)

        # Allow worker retry and DLQ escalation
        await asyncio.sleep(1.5)
        failed_job = await queue.get_job(job.job_id)
        assert failed_job.status == JobState.DEAD_LETTER
        assert "Max retries exceeded" in failed_job.error

        dlq_list = await queue.get_dlq_jobs()
        assert len(dlq_list) == 1
        assert dlq_list[0].job_id == job.job_id
    finally:
        await worker.stop()


@pytest.mark.asyncio
async def test_agent_state_checkpoint_and_decision():
    """Verify agent run creation, tool execution logging, and checkpointing."""
    store = LocalAgentStateStore()
    run = AgentRun(agent_id="thermal_specialist_agent", prompt="Evaluate PCB thermal boundaries")
    created = await store.create_run(run)
    assert created.status == AgentRunStatus.INITIALIZED

    # Log tool execution
    tool_exec = ToolExecution(tool_name="calculate_heat_dissipation", arguments={"power_watts": 15.0})
    await store.append_tool_execution(created.run_id, tool_exec)

    # Save checkpoint
    chk = AgentCheckpoint(run_id=created.run_id, step_number=1, state_snapshot={"current_temp_c": 62.4})
    await store.save_checkpoint(chk)

    # Record decision
    dec = AgentDecision(
        run_id=created.run_id,
        action_type="recommend_heatsink",
        rationale="Junction temperature exceeds 60C without auxiliary cooling",
        confidence=0.96,
        requires_human_approval=False,
    )
    await store.record_decision(dec)

    retrieved = await store.get_run(created.run_id)
    assert len(retrieved.tool_executions) == 1
    assert len(retrieved.checkpoints) == 1
    assert len(retrieved.decisions) == 1
    assert retrieved.decisions[0].confidence == 0.96


@pytest.mark.asyncio
async def test_artifact_store_put_and_get(tmp_path):
    """Verify storing and retrieving binary/text artifacts."""
    store = FilesystemArtifactStore(base_dir=str(tmp_path))
    content = b"GERBER_DATA_LAYER_TOP_COPPER_V1"
    
    art = await store.put_artifact(
        filename="top_copper.gbr",
        data=content,
        content_type="application/vnd.gerber",
        project_id="proj_alpha",
    )
    assert art.size_bytes == len(content)
    assert art.storage_backend == "filesystem"

    retrieved_bytes = await store.get_artifact_bytes(art.artifact_id)
    assert retrieved_bytes == content


@pytest.mark.asyncio
async def test_llm_gateway_offline_mock():
    """Verify LLMGateway completes requests safely in offline mode with mock provider."""
    gateway = LLMGateway(provider=LocalMockProvider())
    res = await gateway.complete("Verify impedance matching on 50-ohm RF trace")
    assert "Verification checks passed" in res.text
    assert res.provider == "local_mock"
    assert res.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_unified_retrieval_service():
    """Verify unified evidence retrieval returns verified evidence."""
    service = UnifiedRetrievalService()
    res = await service.search(RetrievalQuery(query="clearance spacing IPC standard"))
    assert res.total_found > 0
    assert any("IPC" in e.title for e in res.evidence_items)
    assert all(e.verified is True for e in res.evidence_items)


def test_rbac_security_gates():
    """Verify permissions and role-based action enforcement."""
    agent_ctx = SecurityContext(user_id="agent_1", role=Role.AGENT)
    reviewer_ctx = SecurityContext(user_id="eng_lead", role=Role.REVIEWER)
    procurement_ctx = SecurityContext(user_id="buyer_jane", role=Role.PROCUREMENT)

    # Agents cannot execute orders
    with pytest.raises(HTTPException) as exc:
        GovernancePolicyGate.enforce_permission(agent_ctx, Permission.ORDER_EXECUTE)
    assert exc.value.status_code == 403

    # Procurement can execute orders
    GovernancePolicyGate.enforce_permission(procurement_ctx, Permission.ORDER_EXECUTE)

    # Validate 3-tier action transition: RECOMMENDATION directly to EXECUTED must fail
    with pytest.raises(HTTPException) as exc:
        GovernancePolicyGate.validate_action_tier_transition(
            ActionTier.RECOMMENDATION,
            ActionTier.EXECUTED_ACTION,
            reviewer_ctx,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_immutable_audit_trail():
    """Verify append-only audit trail logging and filtering."""
    trail = AuditTrail()
    ev1 = AuditEvent(event_type="simulation.dispatched", actor_id="user_123", actor_role="ENGINEER", project_id="proj_1")
    ev2 = AuditEvent(event_type="bom.approved", actor_id="lead_456", actor_role="REVIEWER", project_id="proj_1")
    await trail.log_event(ev1)
    await trail.log_event(ev2)

    events = await trail.get_events(project_id="proj_1")
    assert len(events) == 2
    assert events[1].event_type == "bom.approved"


def test_metrics_collector():
    """Verify Prometheus-style in-memory metrics recording."""
    metrics = MetricsCollector()
    metrics.record_request("GET", "/health", 200, 0.005)
    metrics.record_request("POST", "/api/jobs", 202, 0.012)
    metrics.record_job_status("pcb_simulation", "SUCCEEDED")

    summary = metrics.get_summary()
    assert summary["request_counts"]["GET_200"] == 1
    assert summary["request_counts"]["POST_202"] == 1
    assert summary["job_counts"]["pcb_simulation_SUCCEEDED"] == 1
    assert summary["total_errors"] == 0


def test_engineering_lifecycle_stage_gates():
    """Verify lifecycle gates reject failing simulations or EOL parts."""
    # 1. Thermal failure gate
    failing_sim = {"status": "SUCCEEDED", "peak_temperature_c": 118.5}
    with pytest.raises(LifecycleGateViolation) as exc:
        LifecycleStageGate.verify_simulation_pass(failing_sim)
    assert "THERMAL_SAFETY_GATE" in exc.value.gate_name

    # 2. BOM Sourcing EOL gate
    bom_with_eol = [{"mpn": "MAX232-DISCONTINUED", "status": "EOL"}]
    with pytest.raises(LifecycleGateViolation) as exc:
        LifecycleStageGate.verify_bom_approval(bom_with_eol, human_approval_signed=True)
    assert "BOM_SOURCING_GATE" in exc.value.gate_name

    # 3. Unapproved BOM gate
    clean_bom = [{"mpn": "STM32F405RGT6", "status": "ACTIVE"}]
    with pytest.raises(LifecycleGateViolation) as exc:
        LifecycleStageGate.verify_bom_approval(clean_bom, human_approval_signed=False)
    assert "HUMAN_GOVERNANCE_GATE" in exc.value.gate_name
