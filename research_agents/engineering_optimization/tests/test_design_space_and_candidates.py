"""
Test design space generation and feasibility enforcement for EngineeringOptimizationAgent.
"""
from research_agents.engineering_optimization.schemas import (
    ConstraintObject, ObjectiveObject, OptimizationObject, VariableObject,
)
from research_agents.engineering_optimization.services.design_space_engine import DesignSpaceEngine


def _make_optimization():
    return OptimizationObject(
        optimization_id="OPT-TEST",
        project_id="proj_001",
        name="Test Optimization",
        description="Test",
        objectives=[
            ObjectiveObject(objective_id="OBJ-1", name="power_dissipation_watts",
                            direction="MINIMIZE", unit="W", weight=1.0),
        ],
        variables=[
            VariableObject(variable_id="VAR-1", name="current_ma", unit="mA",
                           min_value=80.0, max_value=200.0, step=40.0),
            VariableObject(variable_id="VAR-2", name="voltage_v", unit="V",
                           min_value=1.8, max_value=3.6, step=0.9),
        ],
        constraints=[
            ConstraintObject(constraint_id="CON-PWR", name="power_dissipation_watts",
                             constraint_type="HARD", expression="<= limit", limit=0.5, unit="W"),
        ],
    )


def test_candidate_generation_count():
    engine = DesignSpaceEngine(random_seed=42)
    opt = _make_optimization()
    candidates = engine.generate_candidates(opt, n_candidates=5)
    assert len(candidates) == 5


def test_candidate_ids_unique():
    engine = DesignSpaceEngine(random_seed=42)
    opt = _make_optimization()
    candidates = engine.generate_candidates(opt, n_candidates=10)
    ids = [c.candidate_id for c in candidates]
    assert len(ids) == len(set(ids))


def test_variable_values_within_range():
    engine = DesignSpaceEngine(random_seed=42)
    opt = _make_optimization()
    candidates = engine.generate_candidates(opt, n_candidates=20)
    for c in candidates:
        assert 80.0 <= c.variable_values["current_ma"] <= 200.0
        assert 1.8 <= c.variable_values["voltage_v"] <= 3.6


def test_hard_constraint_violation_marks_infeasible():
    """Candidate with power > 0.5W must be marked INFEASIBLE (hard constraint)."""
    engine = DesignSpaceEngine(random_seed=42)
    opt = _make_optimization()
    from research_agents.engineering_optimization.schemas import DesignCandidate
    c = DesignCandidate(
        candidate_id="CAND-INFEASIBLE",
        optimization_id="OPT-TEST",
        variable_values={"current_ma": 200.0, "voltage_v": 3.6},
        objective_values={"power_dissipation_watts": 0.72},  # exceeds 0.5W limit
    )
    c = engine.check_feasibility(c, opt.constraints)
    assert c.feasible is False
    assert len(c.hard_constraint_violations) == 1


def test_feasible_candidate_below_hard_limit():
    engine = DesignSpaceEngine(random_seed=42)
    opt = _make_optimization()
    from research_agents.engineering_optimization.schemas import DesignCandidate
    c = DesignCandidate(
        candidate_id="CAND-FEASIBLE",
        optimization_id="OPT-TEST",
        variable_values={"current_ma": 80.0, "voltage_v": 1.8},
        objective_values={"power_dissipation_watts": 0.144},  # 1.8V * 80mA = 0.144W
    )
    c = engine.check_feasibility(c, opt.constraints)
    assert c.feasible is True
    assert len(c.hard_constraint_violations) == 0


def test_hard_constraint_never_converted_to_soft():
    """A HARD constraint must remain HARD. Feasible cannot become True if violated."""
    engine = DesignSpaceEngine(random_seed=42)
    constraint = ConstraintObject(
        constraint_id="CON-MUST-HARD", name="power_dissipation_watts",
        constraint_type="HARD", expression="<= limit", limit=0.3, unit="W"
    )
    from research_agents.engineering_optimization.schemas import DesignCandidate
    c = DesignCandidate(
        candidate_id="CAND-HARD-CHECK",
        optimization_id="OPT-TEST",
        variable_values={},
        objective_values={"power_dissipation_watts": 0.5},  # exceeds 0.3W
    )
    c = engine.check_feasibility(c, [constraint])
    # Hard constraint violation -> feasible MUST be False, no exceptions
    assert c.feasible is False
