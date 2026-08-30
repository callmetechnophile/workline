"""
Test Google ADK-compliant EngineeringOptimizationAgent capability methods.
"""
import asyncio
import pytest
from research_agents.engineering_optimization.agent import EngineeringOptimizationAgent
from research_agents.engineering_optimization.providers.mock_provider import MockOptimizationProvider
from research_agents.engineering_optimization.schemas import OptimizationInput


@pytest.fixture
def agent():
    return EngineeringOptimizationAgent(reasoning_provider=MockOptimizationProvider())


def test_agent_name():
    assert EngineeringOptimizationAgent.NAME == "EngineeringOptimizationAgent"


def test_agent_capabilities_list():
    caps = EngineeringOptimizationAgent.CAPABILITIES
    assert "optimization.create" in caps
    assert "optimization.evaluate" in caps
    assert "optimization.pareto" in caps
    assert "optimization.tradeoff" in caps
    assert "optimization.select" in caps
    assert "graph.read" in caps


def test_run_optimization_cycle_sync_returns_output(agent):
    inp = OptimizationInput(project_id="proj_agent_test")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=4)
    assert out.optimization is not None
    assert len(out.candidates) == 4
    assert out.report_markdown != ""


def test_run_optimization_cycle_async(agent):
    inp = OptimizationInput(project_id="proj_async")
    out = asyncio.run(agent.run_optimization_cycle(inp, n_candidates=4))
    assert out.optimization.optimization_id.startswith("OPT-")


def test_create_optimization_capability(agent):
    result = asyncio.run(agent.create_optimization(
        project_id="proj_create",
        objectives=[{"objective_id": "O1", "name": "power", "direction": "MINIMIZE",
                     "unit": "W", "weight": 1.0}],
        variables=[{"variable_id": "V1", "name": "current_ma", "unit": "mA",
                    "min_value": 80.0, "max_value": 200.0}],
        constraints=[],
    ))
    assert "optimization_id" in result
    assert result["optimization_id"].startswith("OPT-")


def test_evaluate_candidates_capability(agent):
    # First create an optimization
    result = asyncio.run(agent.create_optimization(
        project_id="proj_eval",
        objectives=[{"objective_id": "O1", "name": "power", "direction": "MINIMIZE",
                     "unit": "W", "weight": 1.0}],
        variables=[{"variable_id": "V1", "name": "current_ma", "unit": "mA",
                    "min_value": 80.0, "max_value": 200.0, "step": 40.0}],
        constraints=[],
    ))
    opt_id = result["optimization_id"]
    eval_result = asyncio.run(agent.evaluate_candidates(opt_id, n_candidates=5))
    assert eval_result["candidates_generated"] == 5


def test_detect_reoptimization_capability(agent):
    inp = OptimizationInput(project_id="proj_reopt")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=3)
    opt_id = out.optimization.optimization_id
    result = asyncio.run(agent.detect_reoptimization(opt_id, "v99.0.0", "v99.0.0"))
    assert result.get("action") == "RE_OPTIMIZE" or result.get("status") in ("CURRENT", "STALE")


def test_generate_report_capability(agent):
    inp = OptimizationInput(project_id="proj_rep")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=3)
    opt_id = out.optimization.optimization_id
    result = asyncio.run(agent.generate_report(opt_id))
    assert "report_markdown" in result
    assert "## 1." in result["report_markdown"]
