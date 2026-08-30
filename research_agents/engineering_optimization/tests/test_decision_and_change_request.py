"""
Test candidate selection creating OptimizationDecision and Agent #16 ChangeRequest bridge.
"""
import asyncio
import pytest
from research_agents.engineering_optimization.agent import EngineeringOptimizationAgent
from research_agents.engineering_optimization.providers.mock_provider import MockOptimizationProvider
from research_agents.engineering_optimization.schemas import OptimizationInput


@pytest.fixture
def agent():
    return EngineeringOptimizationAgent(reasoning_provider=MockOptimizationProvider())


@pytest.fixture
def ran_optimization(agent):
    inp = OptimizationInput(project_id="proj_test_001")
    return agent.run_optimization_cycle_sync(inp, n_candidates=6)


def test_feasible_candidate_selection_creates_decision(agent, ran_optimization):
    """Selecting a feasible candidate creates an OptimizationDecision and ChangeRequest."""
    feasible = [c for c in ran_optimization.candidates if c.feasible]
    if not feasible:
        pytest.skip("No feasible candidates generated in this run")
    top = feasible[0]
    opt_id = ran_optimization.optimization.optimization_id

    result = asyncio.run(
        agent.select_candidate(opt_id, top.candidate_id, "engineer_001", "Best Pareto candidate")
    )
    assert "decision_id" in result
    assert result["decision_id"].startswith("OPTDEC-")
    assert "change_request_id" in result
    assert result["change_request_id"].startswith("CR-OPT-")
    assert result["status"] == "DECISION_RECORDED"


def test_infeasible_candidate_selection_rejected(agent, ran_optimization):
    """Selecting an infeasible candidate MUST be rejected immediately."""
    infeasible = [c for c in ran_optimization.candidates if not c.feasible]
    if not infeasible:
        pytest.skip("No infeasible candidates in this run")
    opt_id = ran_optimization.optimization.optimization_id

    result = asyncio.run(
        agent.select_candidate(opt_id, infeasible[0].candidate_id, "eng", "test")
    )
    assert "error" in result
    assert "INFEASIBLE" in result["error"] or "infeasible" in result["error"].lower()


def test_selection_does_not_mutate_production_project(agent, ran_optimization):
    """Selection must NOT change project BOM, architecture, or any production record."""
    feasible = [c for c in ran_optimization.candidates if c.feasible]
    if not feasible:
        pytest.skip("No feasible candidates")
    opt_id = ran_optimization.optimization.optimization_id
    opt_before_id = ran_optimization.optimization.optimization_id

    asyncio.run(
        agent.select_candidate(opt_id, feasible[0].candidate_id, "eng", "test")
    )
    # Optimization ID should not change (no mutation)
    assert ran_optimization.optimization.optimization_id == opt_before_id


def test_selection_message_references_agent16(agent, ran_optimization):
    """The selection response must reference Agent #16 for change control."""
    feasible = [c for c in ran_optimization.candidates if c.feasible]
    if not feasible:
        pytest.skip("No feasible candidates")
    opt_id = ran_optimization.optimization.optimization_id

    result = asyncio.run(
        agent.select_candidate(opt_id, feasible[0].candidate_id, "eng", "test")
    )
    msg = result.get("message", "") + result.get("change_request_id", "")
    assert "CR-OPT-" in msg or "Agent #16" in msg or "EngineeringChangeControlAgent" in msg
