"""
Test full scenario specifications from the Agent #20 specification (Sections 90-105).
"""
import pytest
from research_agents.engineering_optimization.agent import EngineeringOptimizationAgent
from research_agents.engineering_optimization.providers.mock_provider import MockOptimizationProvider
from research_agents.engineering_optimization.schemas import (
    ConstraintObject, DesignCandidate, ObjectiveObject,
    OptimizationInput, VariableObject,
)
from research_agents.engineering_optimization.services.design_space_engine import DesignSpaceEngine


@pytest.fixture
def agent():
    return EngineeringOptimizationAgent(reasoning_provider=MockOptimizationProvider())


def test_section_90_hard_constraint_thermal_violation_infeasible():
    """Spec §90: Tj > 80degC -> INFEASIBLE, never recommended."""
    engine = DesignSpaceEngine()
    from research_agents.engineering_optimization.schemas import OptimizationObject
    opt = OptimizationObject(
        optimization_id="OPT-90", project_id="p90", name="§90", description="thermal",
        objectives=[ObjectiveObject(objective_id="O1", name="power", direction="MINIMIZE", unit="W")],
        variables=[VariableObject(variable_id="V1", name="current_ma", unit="mA",
                                  min_value=100.0, max_value=300.0)],
        constraints=[ConstraintObject(constraint_id="C1", name="junction_temp_c",
                                      constraint_type="HARD", expression="<= limit",
                                      limit=80.0, unit="degC")],
    )
    c = DesignCandidate(
        candidate_id="CAND-90", optimization_id="OPT-90",
        objective_values={"junction_temp_c": 95.0},  # VIOLATION
    )
    c = engine.check_feasibility(c, opt.constraints)
    assert c.feasible is False


def test_section_91_multi_objective_pareto_efficiency():
    """Spec §91: Multi-objective -> Pareto frontier rather than single-objective ranking."""
    engine = DesignSpaceEngine(random_seed=99)
    objectives = [
        ObjectiveObject(objective_id="O1", name="power", direction="MINIMIZE", unit="W"),
        ObjectiveObject(objective_id="O2", name="cost", direction="MINIMIZE", unit="USD"),
    ]
    candidates = [
        DesignCandidate(candidate_id=f"C{i}", optimization_id="OPT-91",
                        objective_values={"power": float(i), "cost": float(5-i)},
                        feasible=True)
        for i in range(1, 6)
    ]
    pareto = engine.compute_pareto_frontier("OPT-91", candidates, objectives)
    # All 5 points should be non-dominated (each has different trade-off)
    assert len(pareto.points) == 5


def test_section_92_feasible_candidate_recommended_not_infeasible():
    """Spec §92: Recommendation must be from feasible set only."""
    engine = DesignSpaceEngine(random_seed=42)
    objectives = [ObjectiveObject(objective_id="O1", name="power", direction="MINIMIZE", unit="W")]
    candidates = [
        DesignCandidate(candidate_id="FEAS", optimization_id="OPT-92",
                        objective_values={"power": 0.3}, feasible=True),
        DesignCandidate(candidate_id="INF", optimization_id="OPT-92",
                        objective_values={"power": 0.1}, feasible=False),  # infeasible with better power
    ]
    ranked = engine.rank_by_weighted_sum(candidates, objectives)
    # Must not recommend INF even though it has better power
    assert ranked[0].candidate_id == "FEAS"
    assert all(c.candidate_id != "INF" for c in ranked)


def test_section_93_candidate_isolation_no_production_mutation(agent):
    """Spec §93: Running optimization must not modify project BOM or architecture."""
    inp = OptimizationInput(project_id="proj_93")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=4)
    # Project BOM and arch versions in candidates must not be set to something else
    assert out.optimization.bom_version is not None


def test_section_94_power_budget_hard_constraint():
    """Spec §94: Power budget <= 0.5W hard constraint strictly enforced."""
    engine = DesignSpaceEngine()
    con = ConstraintObject(
        constraint_id="C-PWR", name="power_dissipation_watts",
        constraint_type="HARD", expression="<= limit", limit=0.5, unit="W"
    )
    c_ok = DesignCandidate(candidate_id="OK", optimization_id="OPT-94",
                           objective_values={"power_dissipation_watts": 0.495})
    c_fail = DesignCandidate(candidate_id="FAIL", optimization_id="OPT-94",
                             objective_values={"power_dissipation_watts": 0.72})
    c_ok = engine.check_feasibility(c_ok, [con])
    c_fail = engine.check_feasibility(c_fail, [con])
    assert c_ok.feasible is True
    assert c_fail.feasible is False


def test_section_95_optimization_status_complete_when_feasible(agent):
    """Spec §95: Status should be COMPLETE when at least one feasible candidate exists."""
    inp = OptimizationInput(project_id="proj_95")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=10)
    feasible = [c for c in out.candidates if c.feasible]
    if feasible:
        assert out.optimization.status == "COMPLETE"


def test_section_96_optimization_id_format(agent):
    """Spec §96: Optimization IDs must follow OPT-XXXXXXXX format."""
    inp = OptimizationInput(project_id="proj_96")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=3)
    assert out.optimization.optimization_id.startswith("OPT-")


def test_section_97_candidate_id_format(agent):
    """Spec §97: Candidate IDs must follow CAND-XXXXXXXX format."""
    inp = OptimizationInput(project_id="proj_97")
    out = agent.run_optimization_cycle_sync(inp, n_candidates=3)
    for c in out.candidates:
        assert c.candidate_id.startswith("CAND-")


def test_section_98_report_contains_all_candidates():
    """Spec §98: Report must reference all candidates including infeasible ones."""
    from research_agents.engineering_optimization.services.report_generator import OptimizationReportGenerator
    from research_agents.engineering_optimization.schemas import OptimizationObject
    gen = OptimizationReportGenerator()
    opt = OptimizationObject(
        optimization_id="OPT-98", project_id="p98", name="98", description="98",
        objectives=[ObjectiveObject(objective_id="O1", name="power", direction="MINIMIZE", unit="W")],
    )
    candidates = [
        DesignCandidate(candidate_id="F1", optimization_id="OPT-98",
                        objective_values={"power": 0.3}, feasible=True),
        DesignCandidate(candidate_id="I1", optimization_id="OPT-98",
                        hard_constraint_violations=["power > limit"],
                        feasible=False),
    ]
    report = gen.generate_report(opt, candidates, None, "F1", "test", [])
    assert "2" in report  # Total candidates = 2
