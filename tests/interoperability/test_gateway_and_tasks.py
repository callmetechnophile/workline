"""Tests for Interoperability Gateway task execution, idempotency, provenance, and audit trails."""

import pytest
from backend.workline.interoperability.capabilities import RiskLevel
from backend.workline.interoperability.gateway import InteroperabilityGateway
from backend.workline.interoperability.tasks import AuditEventType, TaskStatus


@pytest.mark.asyncio
async def test_gateway_task_submission_and_provenance():
    gw = InteroperabilityGateway()

    task = await gw.submit_task(
        project_id="rover_v2",
        team_id="embedded_systems",
        requesting_agent="PCBAgent",
        target_agent_id="ThermalSolver",
        capability_id="thermal_simulation",
        payload={
            "board_width": 120.0,
            "board_height": 90.0,
            "ambient_temp": 25.0,
            "components": [{"name": "MCU_STM32", "power_dissipation_watts": 0.8}],
        },
        idempotency_key="idemp-rover-thermal-001",
    )

    assert task.status == TaskStatus.COMPLETED
    assert task.target_agent == "ThermalSolver"
    assert task.provenance is not None
    assert task.provenance.input_hash != ""
    assert task.provenance.output_hash != ""
    assert task.provenance.execution_duration >= 0.0

    # Verify audit trail
    events = gw.get_audit_trail(task.task_id)
    event_types = [e.event_type for e in events]
    assert AuditEventType.AGENT_TASK_CREATED in event_types
    assert AuditEventType.AGENT_TASK_AUTHORIZED in event_types
    assert AuditEventType.AGENT_TASK_STARTED in event_types
    assert AuditEventType.AGENT_TASK_COMPLETED in event_types


@pytest.mark.asyncio
async def test_gateway_idempotency_deduplication():
    gw = InteroperabilityGateway()
    key = "unique-idemp-key-999"

    task1 = await gw.submit_task(
        project_id="rover_v2",
        team_id="team_main",
        requesting_agent="BuilderAgent",
        target_agent_id="ResearchAgent",
        capability_id="research",
        payload={"query": "Buck converter topology"},
        idempotency_key=key,
    )

    task2 = await gw.submit_task(
        project_id="rover_v2",
        team_id="team_main",
        requesting_agent="BuilderAgent",
        target_agent_id="ResearchAgent",
        capability_id="research",
        payload={"query": "Buck converter topology"},
        idempotency_key=key,
    )

    # Must return identical task instance without duplicating execution
    assert task1.task_id == task2.task_id
    assert task2.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_gateway_rejection_for_unregistered_agent_or_capability():
    gw = InteroperabilityGateway()

    # Non-existent agent
    task1 = await gw.submit_task(
        project_id="rover_v2",
        team_id="team_main",
        requesting_agent="User",
        target_agent_id="FakeGhostAgent",
        capability_id="magic_trick",
        payload={},
    )
    assert task1.status == TaskStatus.REJECTED
    assert "not registered" in task1.error

    # Non-existent capability on existing agent
    task2 = await gw.submit_task(
        project_id="rover_v2",
        team_id="team_main",
        requesting_agent="User",
        target_agent_id="ThermalSolver",
        capability_id="unsupported_quantum_sim",
        payload={},
    )
    assert task2.status == TaskStatus.REJECTED
    assert "does not offer capability" in task2.error
