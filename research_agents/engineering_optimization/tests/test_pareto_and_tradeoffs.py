"""
Test Pareto frontier computation and multi-objective trade-off analysis.
"""
from research_agents.engineering_optimization.schemas import (
    DesignCandidate, ObjectiveObject,
)
from research_agents.engineering_optimization.services.design_space_engine import DesignSpaceEngine


def _make_objectives():
    return [
        ObjectiveObject(objective_id="OBJ-P", name="power", direction="MINIMIZE", unit="W"),
        ObjectiveObject(objective_id="OBJ-C", name="cost", direction="MINIMIZE", unit="USD"),
    ]


def _make_candidate(cid, power, cost, feasible=True):
    return DesignCandidate(
        candidate_id=cid, optimization_id="OPT-PARETO",
        objective_values={"power": power, "cost": cost},
        feasible=feasible,
    )


def test_pareto_simple_two_objectives():
    """A dominates B if A <= B in all objectives and strictly < in one."""
    engine = DesignSpaceEngine()
    objectives = _make_objectives()
    # C1: (1.0, 2.0) - non-dominated
    # C2: (2.0, 1.0) - non-dominated
    # C3: (2.0, 3.0) - dominated by C1 and C2
    candidates = [
        _make_candidate("C1", 1.0, 2.0),
        _make_candidate("C2", 2.0, 1.0),
        _make_candidate("C3", 2.0, 3.0),
    ]
    pareto = engine.compute_pareto_frontier("OPT-PARETO", candidates, objectives)
    pareto_ids = {p.candidate_id for p in pareto.points}
    assert "C1" in pareto_ids
    assert "C2" in pareto_ids
    assert "C3" not in pareto_ids  # C3 is dominated
    assert pareto.dominated_count == 1


def test_pareto_infeasible_excluded():
    """Infeasible candidates MUST NOT appear on the Pareto frontier."""
    engine = DesignSpaceEngine()
    objectives = _make_objectives()
    candidates = [
        _make_candidate("GOOD", 0.5, 1.0, feasible=True),
        _make_candidate("BAD", 0.3, 0.5, feasible=False),  # violates hard constraint
    ]
    pareto = engine.compute_pareto_frontier("OPT-PARETO", candidates, objectives)
    pareto_ids = {p.candidate_id for p in pareto.points}
    assert "BAD" not in pareto_ids
    assert pareto.infeasible_count == 1


def test_pareto_single_candidate_is_pareto():
    """A single feasible candidate is trivially non-dominated."""
    engine = DesignSpaceEngine()
    objectives = _make_objectives()
    candidates = [_make_candidate("ONLY", 1.0, 1.0)]
    pareto = engine.compute_pareto_frontier("OPT-PARETO", candidates, objectives)
    assert len(pareto.points) == 1
    assert pareto.points[0].candidate_id == "ONLY"


def test_pareto_maximize_direction():
    """MAXIMIZE objectives: higher value is better."""
    engine = DesignSpaceEngine()
    objs = [
        ObjectiveObject(objective_id="OBJ-E", name="efficiency", direction="MAXIMIZE", unit="%"),
    ]
    candidates = [
        _make_candidate("HIGH", power=0.0, cost=90.0),   # efficiency=90%
        _make_candidate("LOW", power=0.0, cost=70.0),    # efficiency=70%
    ]
    # Re-map objective_values for efficiency test
    candidates[0].objective_values = {"efficiency": 90.0}
    candidates[1].objective_values = {"efficiency": 70.0}
    pareto = engine.compute_pareto_frontier("OPT-MAX", candidates, objs)
    pareto_ids = {p.candidate_id for p in pareto.points}
    assert "HIGH" in pareto_ids
    assert "LOW" not in pareto_ids


def test_weighted_sum_ranking_returns_feasible_only():
    engine = DesignSpaceEngine()
    objectives = _make_objectives()
    candidates = [
        _make_candidate("A", 1.0, 3.0, feasible=True),
        _make_candidate("B", 2.0, 2.0, feasible=True),
        _make_candidate("C", 0.5, 0.5, feasible=False),  # infeasible
    ]
    ranked = engine.rank_by_weighted_sum(candidates, objectives)
    ranked_ids = [c.candidate_id for c in ranked]
    assert "C" not in ranked_ids
    assert len(ranked) == 2


def test_robustness_score_between_0_and_1():
    engine = DesignSpaceEngine()
    from research_agents.engineering_optimization.schemas import DesignCandidate
    c = DesignCandidate(
        candidate_id="ROB-1", optimization_id="OPT-R",
        variable_values={"current_ma": 150.0},
        objective_values={"power": 0.495},
    )
    objectives = [ObjectiveObject(objective_id="OBJ-P", name="power", direction="MINIMIZE", unit="W")]
    rob = engine.compute_robustness(c, objectives)
    assert 0.0 <= rob.robustness_score <= 1.0
    assert "current_ma" in rob.sensitivity_map
