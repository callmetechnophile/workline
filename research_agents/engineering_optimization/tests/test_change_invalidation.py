"""
Test change invalidation: upstream BOM/architecture changes mark optimization STALE or INVALIDATED.
"""
import asyncio
import pytest
from research_agents.engineering_optimization.agent import EngineeringOptimizationAgent
from research_agents.engineering_optimization.providers.mock_provider import MockOptimizationProvider
from research_agents.engineering_optimization.schemas import OptimizationInput
from research_agents.engineering_optimization.services.reoptimization_engine import ReoptimizationEngine


@pytest.fixture
def agent():
    return EngineeringOptimizationAgent(reasoning_provider=MockOptimizationProvider())


@pytest.fixture
def ran_optimization(agent):
    inp = OptimizationInput(project_id="proj_test_inval")
    return agent.run_optimization_cycle_sync(inp, n_candidates=4)


def test_bom_version_change_marks_optimization_stale(agent, ran_optimization):
    """When BOM version changes, optimization is STALE."""
    opt_id = ran_optimization.optimization.optimization_id
    current_bom = "v2.0.0"  # Different from the optimization's bom_version
    current_arch = ran_optimization.optimization.architecture_version

    result = asyncio.run(
        agent.detect_reoptimization(opt_id, current_bom, current_arch)
    )
    assert result.get("action") == "RE_OPTIMIZE" or result.get("status") in ("STALE", "INVALIDATED")


def test_same_versions_no_stale(agent, ran_optimization):
    """If versions match, optimization is current."""
    opt_id = ran_optimization.optimization.optimization_id
    current_bom = ran_optimization.optimization.bom_version
    current_arch = ran_optimization.optimization.architecture_version

    result = asyncio.run(
        agent.detect_reoptimization(opt_id, current_bom, current_arch)
    )
    assert result.get("status") == "CURRENT"


def test_reoptimization_engine_marks_stale_in_memory():
    """ReoptimizationEngine.mark_stale sets status = STALE."""
    from research_agents.engineering_optimization.schemas import OptimizationObject
    engine = ReoptimizationEngine()
    opt = OptimizationObject(
        optimization_id="OPT-STALE", project_id="p1",
        name="test", description="test",
        bom_version="v1.0.0", architecture_version="v1.0.0",
    )
    engine.mark_stale(opt)
    assert opt.status == "STALE"


def test_reoptimization_engine_marks_invalidated():
    """ReoptimizationEngine.mark_invalidated sets status = INVALIDATED."""
    from research_agents.engineering_optimization.schemas import OptimizationObject
    engine = ReoptimizationEngine()
    opt = OptimizationObject(
        optimization_id="OPT-INV", project_id="p1",
        name="test", description="test",
    )
    engine.mark_invalidated(opt)
    assert opt.status == "INVALIDATED"


def test_staleness_detected_when_bom_differs():
    from research_agents.engineering_optimization.schemas import OptimizationObject
    engine = ReoptimizationEngine()
    opt = OptimizationObject(
        optimization_id="OPT-S2", project_id="p1",
        name="test", description="test",
        bom_version="v1.0.0", architecture_version="v1.0.0",
    )
    stale = engine.check_staleness(opt, current_bom_version="v2.0.0", current_architecture_version="v1.0.0")
    assert stale is True


def test_not_stale_when_versions_match():
    from research_agents.engineering_optimization.schemas import OptimizationObject
    engine = ReoptimizationEngine()
    opt = OptimizationObject(
        optimization_id="OPT-OK", project_id="p1",
        name="test", description="test",
        bom_version="v1.0.0", architecture_version="v1.0.0",
    )
    stale = engine.check_staleness(opt, "v1.0.0", "v1.0.0")
    assert stale is False
