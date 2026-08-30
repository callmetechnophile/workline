"""
Test 21-section Markdown optimization report generation.
"""
import pytest
from research_agents.engineering_optimization.schemas import (
    ConstraintObject, DesignCandidate, ObjectiveObject,
    OptimizationObject, ParetoFrontierObject, ParetoPoint, VariableObject,
)
from research_agents.engineering_optimization.services.report_generator import OptimizationReportGenerator


def _make_opt():
    return OptimizationObject(
        optimization_id="OPT-RPT", project_id="proj_rpt",
        name="Thermal Optimization", description="Minimize power and cost",
        objectives=[
            ObjectiveObject(objective_id="OBJ-P", name="power", direction="MINIMIZE", unit="W"),
        ],
        variables=[
            VariableObject(variable_id="VAR-I", name="current_ma", unit="mA",
                           min_value=80.0, max_value=200.0, step=40.0),
        ],
        constraints=[
            ConstraintObject(constraint_id="CON-T", name="junction_temp_c",
                             constraint_type="HARD", expression="<= limit", limit=80.0, unit="degC"),
        ],
        status="COMPLETE",
    )


def test_report_has_21_sections():
    gen = OptimizationReportGenerator()
    opt = _make_opt()
    candidates = [
        DesignCandidate(candidate_id="C1", optimization_id="OPT-RPT",
                        variable_values={"current_ma": 100.0},
                        objective_values={"power": 0.33}, feasible=True),
    ]
    pareto = ParetoFrontierObject(
        frontier_id="PF-1", optimization_id="OPT-RPT",
        points=[ParetoPoint(candidate_id="C1", objective_values={"power": 0.33})],
    )
    report = gen.generate_report(opt, candidates, pareto, "C1", "Best candidate", [])
    for i in range(1, 22):
        assert f"## {i}." in report, f"Section {i} missing from report"


def test_report_contains_project_id():
    gen = OptimizationReportGenerator()
    opt = _make_opt()
    report = gen.generate_report(opt, [], None, None, "", [])
    assert "proj_rpt" in report


def test_report_no_recommendation_when_all_infeasible():
    gen = OptimizationReportGenerator()
    opt = _make_opt()
    c = DesignCandidate(
        candidate_id="INF-1", optimization_id="OPT-RPT",
        hard_constraint_violations=["junction_temp_c: 95 > 80 degC"],
        feasible=False,
    )
    report = gen.generate_report(opt, [c], None, None, "", [])
    assert "inconclusive" in report.lower() or "No recommendation" in report


def test_report_lists_hard_constraints():
    gen = OptimizationReportGenerator()
    opt = _make_opt()
    report = gen.generate_report(opt, [], None, None, "", [])
    assert "Hard Constraints" in report
    assert "junction_temp_c" in report


def test_report_marks_production_not_modified():
    gen = OptimizationReportGenerator()
    opt = _make_opt()
    report = gen.generate_report(opt, [], None, None, "", [])
    assert "NOT modified" in report or "isolated" in report.lower()
