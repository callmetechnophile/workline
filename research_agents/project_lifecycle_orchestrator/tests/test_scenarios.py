"""
Specification-mandated integration test scenarios for ProjectLifecycleOrchestrator (Sections 83–92).
"""

import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.project_lifecycle_orchestrator.agent import ProjectLifecycleOrchestrator
from research_agents.project_lifecycle_orchestrator.providers.mock_provider import MockOrchestratorProvider
from research_agents.project_lifecycle_orchestrator.schemas import OrchestrationInput


@pytest.mark.asyncio
async def test_scenario_83_normal_flow():
    """Section 83: QA Verified produces COMPLETE and project state VERIFIED."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    inp = OrchestrationInput(project_id="proj_83")
    out = await orchestrator.run(inp, qa_status="VERIFIED", validation_status="READY")

    assert out.next_action.action_type == "COMPLETE"
    assert out.run.completed is True


@pytest.mark.asyncio
async def test_scenario_84_qa_failure_routes_to_correction():
    """Section 84: QA test failure routes to ProjectExecutionAgent for correction."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    inp = OrchestrationInput(project_id="proj_84")
    out = await orchestrator.run(
        inp,
        qa_status="FAILED",
        last_failure_type="TEST_FAILURE",
        last_failure_details="Pytest assertion error in lepton driver",
    )

    assert out.next_action.target_agent == "ProjectExecutionAgent"
    assert out.next_action.next_state == "PLANNING"


@pytest.mark.asyncio
async def test_scenario_85_architecture_failure_routes_to_agent_6():
    """Section 85: Architecture Conformance Failure routes to EngineeringArchitectureAgent."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    inp = OrchestrationInput(project_id="proj_85")
    out = await orchestrator.run(
        inp,
        qa_status="FAILED",
        last_failure_type="ARCHITECTURE_CONFORMANCE_FAILURE",
        last_failure_details="Unapproved I2C bus bypassing SPI protocol",
    )

    assert out.next_action.target_agent == "EngineeringArchitectureAgent"
    assert out.next_action.next_state == "ARCHITECTURE"


@pytest.mark.asyncio
async def test_scenario_86_bom_failure_routes_to_agent_8():
    """Section 86: BOM Conformance Failure routes to BOMOptimizationAgent."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    inp = OrchestrationInput(project_id="proj_86")
    out = await orchestrator.run(
        inp,
        qa_status="FAILED",
        last_failure_type="BOM_CONFORMANCE_FAILURE",
        last_failure_details="Unapproved capacitor substituted by execution agent",
    )

    assert out.next_action.target_agent == "BOMOptimizationAgent"
    assert out.next_action.next_state == "BOM"


@pytest.mark.asyncio
async def test_scenario_87_human_approval_halts_execution():
    """Section 87: Human decision requirement sets state to AWAITING_HUMAN."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    orchestrator.human_manager.create_human_request(
        project_id="proj_87",
        reason="Voltage regulator upgrade required",
        requested_decision="Approve 5V buck converter revision",
    )

    inp = OrchestrationInput(project_id="proj_87")
    out = await orchestrator.run(inp)

    assert out.next_action.next_state == "AWAITING_HUMAN"
    assert out.next_action.human_approval_required is True


@pytest.mark.asyncio
async def test_scenario_88_authorization_failure_blocks_execution():
    """Section 88: ArmorIQ denial blocks execution without bypassing."""
    orchestrator = ProjectLifecycleOrchestrator(
        reasoning_provider=MockOrchestratorProvider(),
        simulate_auth_denial=True,
    )
    inp = OrchestrationInput(project_id="proj_88")
    out = await orchestrator.run(inp)

    assert out.run.status == "blocked"
    assert any(b.type == "AUTHORIZATION_DENIED" for b in out.run.blockers)


@pytest.mark.asyncio
async def test_scenario_89_loop_guard():
    """Section 89: 3 identical failures trigger AWAITING_HUMAN loop guard."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    inp = OrchestrationInput(project_id="proj_89")

    await orchestrator.run(inp, qa_status="FAILED", last_failure_type="SAME_TEST_FAILURE")
    await orchestrator.run(inp, qa_status="FAILED", last_failure_type="SAME_TEST_FAILURE")
    out3 = await orchestrator.run(inp, qa_status="FAILED", last_failure_type="SAME_TEST_FAILURE")

    assert out3.next_action.next_state == "AWAITING_HUMAN"
    assert "Loop Guard" in out3.next_action.reason


@pytest.mark.asyncio
async def test_scenario_91_documentation_change_zero_revalidation():
    """Section 91: Documentation change requires 0 engineering revalidation stages."""
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    plan = orchestrator.determine_revalidation_scope("DOCUMENTATION", "README.md")
    assert len(plan.required_stages) == 0


@pytest.mark.asyncio
async def test_scenario_92_database_failure_pauses_safely():
    """Section 92: SurrealDB outage pauses orchestration safely with zero false transitions."""
    db_fail = SurrealDBClient(simulate_failure=True)
    orchestrator = ProjectLifecycleOrchestrator(
        db_client=db_fail,
        reasoning_provider=MockOrchestratorProvider(),
    )
    inp = OrchestrationInput(project_id="proj_92")
    out = await orchestrator.run(inp)

    assert any(b.type == "DATABASE_UNAVAILABLE" for b in out.run.blockers)
    assert out.next_action.action_type == "WAIT_FOR_RESOURCE"
    assert out.run.completed is False
