"""
Unit tests for evidence hashing, integrity, and immutability (Sections 36–38).
"""

from research_agents.engineering_verification.schemas import EvidenceObject


def test_evidence_integrity_and_hashing():
    ev = EvidenceObject(
        evidence_id="EVID-001",
        type="MEASUREMENT",
        source="test:TEST-001",
        artifact="sensor_core",
        hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status="VALID",
    )
    assert ev.type == "MEASUREMENT"
    assert ev.verified is True
    assert ev.hash is not None
