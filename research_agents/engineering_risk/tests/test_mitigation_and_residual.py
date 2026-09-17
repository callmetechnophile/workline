"""Tests for Mitigations and Residual Risk (Sections 100, 101)."""
from research_agents.engineering_risk.schemas import FMEARecord, RiskMitigation
from research_agents.engineering_risk.services.mitigation_engine import MitigationEngine

def test_mitigation_creation_status():
    # Section 100: Create mitigation -> status must be PROPOSED (not auto-VERIFIED)
    mit = RiskMitigation(
        risk_id="RISK-01",
        action="Add thermal heat pipe",
        type="PREVENTIVE",
        target_reduction={"occurrence": 2, "severity": 0, "detection": 1},
    )
    assert mit.status == "PROPOSED"
    assert mit.verification_id is None

def test_mitigation_verification_integration():
    # Section 101: Agent #18 supplies passing verification evidence -> status becomes VERIFIED
    engine = MitigationEngine()
    mit = RiskMitigation(
        mitigation_id="MIT-01",
        risk_id="RISK-01",
        action="Install bulk decoupling capacitor bank",
        type="PREVENTIVE",
    )
    evidence = {
        "status": "PASS",
        "verification_id": "VER-TEST-8812",
        "evidence_ref": "Oscilloscope voltage drop < 100mV under 10A transient",
    }
    verified_mit = engine.verify_mitigation(mit, evidence)
    assert verified_mit.status == "VERIFIED"
    assert verified_mit.verification_id == "VER-TEST-8812"

def test_residual_risk_calculation():
    engine = MitigationEngine()
    fmea = FMEARecord(
        project_id="p1",
        failure_mode_id="FM-01",
        severity=8,
        occurrence=6,
        detection=5,
        risk_priority_number=240,
    )
    mits = [
        RiskMitigation(
            risk_id="RISK-01",
            action="Preventive firmware watchdog",
            type="PREVENTIVE",
            target_reduction={"occurrence": 3, "severity": 0, "detection": 0},
        ),
        RiskMitigation(
            risk_id="RISK-01",
            action="Continuous voltage monitoring",
            type="DETECTIVE",
            target_reduction={"occurrence": 0, "severity": 0, "detection": 2},
        ),
    ]
    res_fmea = engine.calculate_residual_risk(fmea, mits)
    assert res_fmea.residual_severity == 8  # Severity unchanged
    assert res_fmea.residual_occurrence == 3  # 6 - 3
    assert res_fmea.residual_detection == 3  # 5 - 2
    assert res_fmea.residual_rpn == 72  # 8 * 3 * 3 = 72
