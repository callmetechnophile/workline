"""
Unit tests for change-driven evidence invalidation and re-verification scoping (Sections 53–57, 105).
"""

from research_agents.engineering_verification.schemas import EvidenceObject, TestObject
from research_agents.engineering_verification.services.reverification_engine import ReverificationEngine


def test_change_invalidation_and_regression_scoping():
    engine = ReverificationEngine()

    t1 = TestObject(
        test_id="TEST-001",
        project_id="p1",
        name="FLIR Lepton 2.5 SPI Test",
        type="INTERFACE",
        objective="Verify Lepton 2.5 interface",
    )
    t2 = TestObject(
        test_id="TEST-002",
        project_id="p1",
        name="Battery Rail Test",
        type="POWER",
        objective="Verify battery supply",
    )

    ev1 = EvidenceObject(
        evidence_id="EVID-001",
        type="TEST_RESULT",
        source="test:TEST-001",
        artifact="sensor_core",
        status="VALID",
    )

    inv_tests, inv_ev, reg_tests = engine.process_change_impact(
        target_artifact="sensor_core",
        tests=[t1, t2],
        evidence_list=[ev1],
    )

    assert "EVID-001" in inv_ev
    assert "TEST-001" in reg_tests
    assert "TEST-002" not in reg_tests
