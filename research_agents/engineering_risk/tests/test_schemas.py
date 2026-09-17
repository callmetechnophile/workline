"""Tests for EngineeringRiskAgent schemas."""
from research_agents.engineering_risk.schemas import (
    CauseObject,
    FailureMode,
    FMEARecord,
    RatingProfile,
    RiskMatrixProfile,
    RiskMitigation,
    RiskObject,
)

def test_risk_object_schema():
    risk = RiskObject(
        risk_id="RISK-001",
        project_id="proj_01",
        title="Thermal Throttling Risk",
        category="THERMAL",
        severity=8,
        likelihood=4,
        detectability=5,
        risk_score=160,
        risk_level="HIGH",
        status="IDENTIFIED",
    )
    assert risk.risk_id == "RISK-001"
    assert risk.risk_score == 160
    assert risk.risk_level == "HIGH"

def test_failure_mode_schema():
    fm = FailureMode(
        failure_mode_id="FM-001",
        description="Power surge brownout",
        failure_type="ELECTRICAL",
        is_single_point_failure=True,
    )
    assert fm.failure_mode_id == "FM-001"
    assert fm.is_single_point_failure is True

def test_fmea_schema():
    fmea = FMEARecord(
        project_id="proj_01",
        failure_mode_id="FM-001",
        severity=9,
        occurrence=3,
        detection=4,
        risk_priority_number=108,
    )
    assert fmea.risk_priority_number == 108
    assert fmea.status == "OPEN"
