"""Tests for Change Control Impact, Invalidation, and Reassessment (Sections 102, 103)."""
from research_agents.engineering_risk.schemas import (
    FailureMode,
    FMEARecord,
    RiskMitigation,
    RiskObject,
)
from research_agents.engineering_risk.services.change_impact_engine import ChangeImpactEngine

def test_change_impact_evaluation():
    # Section 102: Component is replaced -> affected risks identified, mitigations invalidated
    engine = ChangeImpactEngine()
    chg = {
        "change_id": "CHG-BOM-004",
        "project_id": "proj_01",
        "change_type": "COMPONENT_CHANGE",
        "target_artifact": "BOM",
        "description": "Replace PMIC with alternative supplier part",
    }
    risks = [
        RiskObject(risk_id="RISK-01", project_id="proj_01", title="Power brownout", status="CLOSED"),
    ]
    fms = [FailureMode(failure_mode_id="FM-01", description="Power sag")]
    fmea = [FMEARecord(project_id="proj_01", failure_mode_id="FM-01", severity=8, occurrence=4, detection=5, risk_priority_number=160)]
    mits = [
        RiskMitigation(mitigation_id="MIT-01", risk_id="RISK-01", action="Capacitor decoupling", status="VERIFIED")
    ]

    impact = engine.evaluate_change_impact(chg, risks, fms, fmea, mits)
    assert "RISK-01" in impact.affected_risk_ids
    assert "MIT-01" in impact.invalidated_mitigation_ids
    # Section 103: Risk Reopening -> previously closed risk becomes REOPENED
    assert risks[0].status == "REOPENED"

def test_reassessment_plan_creation():
    engine = ChangeImpactEngine()
    impact = engine.evaluate_change_impact(
        {"change_id": "CHG-01", "project_id": "proj_01"},
        [RiskObject(risk_id="R1", project_id="proj_01", title="Risk 1")],
        [],
        [],
        [RiskMitigation(mitigation_id="M1", risk_id="R1", action="Action", status="VERIFIED")],
    )
    plan = engine.create_reassessment_plan(impact)
    assert len(plan.tasks) == 1
    assert "M1" in plan.required_verifications
