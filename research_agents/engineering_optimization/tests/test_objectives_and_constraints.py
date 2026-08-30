"""
Test objectives and constraint definitions for EngineeringOptimizationAgent.
"""
import pytest
from research_agents.engineering_optimization.schemas import (
    ConstraintObject, ObjectiveObject, VariableObject,
)


def test_objective_minimize_direction():
    obj = ObjectiveObject(
        objective_id="OBJ-1", name="power", direction="MINIMIZE", unit="W", weight=1.0
    )
    assert obj.direction == "MINIMIZE"
    assert obj.unit == "W"


def test_objective_maximize_direction():
    obj = ObjectiveObject(
        objective_id="OBJ-2", name="efficiency", direction="MAXIMIZE", unit="%", weight=0.5
    )
    assert obj.direction == "MAXIMIZE"


def test_hard_constraint_type():
    con = ConstraintObject(
        constraint_id="CON-1", name="temp", constraint_type="HARD",
        expression="<= limit", limit=80.0, unit="degC"
    )
    assert con.constraint_type == "HARD"
    assert con.penalty is None


def test_soft_constraint_with_penalty():
    con = ConstraintObject(
        constraint_id="CON-2", name="cost", constraint_type="SOFT",
        expression="<= limit", limit=5.0, unit="USD", penalty=1.5
    )
    assert con.constraint_type == "SOFT"
    assert con.penalty == 1.5


def test_variable_discrete_step():
    var = VariableObject(
        variable_id="VAR-1", name="current_ma", unit="mA",
        min_value=100.0, max_value=200.0, step=25.0
    )
    assert var.step == 25.0


def test_variable_continuous():
    var = VariableObject(
        variable_id="VAR-2", name="voltage", unit="V",
        min_value=1.8, max_value=3.6, step=None
    )
    assert var.step is None


def test_objective_invalid_direction_rejected():
    with pytest.raises(Exception):
        ObjectiveObject(
            objective_id="OBJ-BAD", name="x", direction="SIDEWAYS", unit="V"
        )
