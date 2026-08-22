"""Tests for engineering requirements, status lifecycle, traceability, and conflict detection."""

import pytest

from backend.workline.knowledge import (
    Actor,
    ActorType,
    ConflictDetector,
    DecisionCategory,
    DecisionStatus,
    EngineeringDecision,
    EngineeringRequirement,
    RequirementCategory,
    RequirementPriority,
    RequirementService,
    RequirementStatus,
)


@pytest.fixture
def clean_requirement_service() -> RequirementService:
    return RequirementService()


def test_requirement_creation_and_status(clean_requirement_service: RequirementService):
    """Test 7 & 8: Creating and updating requirement status."""
    req = EngineeringRequirement(
        requirement_id="REQ-023",
        project_id="proj_rover",
        title="3.3V power rail current delivery",
        description="3.3V rail must support minimum 2A continuous current with < 50mV ripple",
        category=RequirementCategory.ELECTRICAL,
        priority=RequirementPriority.CRITICAL,
        value="2.0",
        unit="A",
        status=RequirementStatus.PROPOSED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="sys_architect"),
    )

    created = clean_requirement_service.create_requirement(req)
    assert created.requirement_id == "REQ-023"
    assert created.status == RequirementStatus.PROPOSED

    # Update status
    updated = clean_requirement_service.update_status(
        "REQ-023",
        RequirementStatus.APPROVED,
        actor=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"),
    )
    assert updated.status == RequirementStatus.APPROVED


def test_requirement_traceability_graph(clean_requirement_service: RequirementService):
    """Test 9 & 10: Requirement traceability to Decision -> Implementation -> Validation."""
    req = EngineeringRequirement(
        requirement_id="REQ-023",
        project_id="proj_rover",
        title="3.3V rail must support 2A",
        description="Provide regulated 3.3V",
        category=RequirementCategory.ELECTRICAL,
        value="2.0",
        unit="A",
        status=RequirementStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        satisfied_by_decisions=["DEC-102"],
    )
    clean_requirement_service.create_requirement(req)

    dec = EngineeringDecision(
        decision_id="DEC-102",
        project_id="proj_rover",
        title="Select TPS62130 for 3.3V Rail",
        description="Power supply",
        category=DecisionCategory.POWER_ARCHITECTURE,
        status=DecisionStatus.VALIDATED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        selected_option="TPS62130",
        rationale="3A output capability",
        implemented_objects=["VCC_3V3", "U1_TPS62130"],
        validation_status="PASS",
    )

    chain = clean_requirement_service.get_traceability("REQ-023", decisions=[dec])

    assert chain.requirement_id == "REQ-023"
    assert len(chain.decisions) == 1
    assert chain.decisions[0]["decision_id"] == "DEC-102"
    assert len(chain.implementations) == 2
    assert len(chain.validations) == 1
    assert chain.validations[0]["validation_status"] == "PASS"

    # Verify requirement status
    verified_req = clean_requirement_service.verify_requirement(
        "REQ-023",
        validation_id="VAL-042",
        passed=True,
        actor=Actor(actor_type=ActorType.HUMAN, actor_id="test_runner"),
    )
    assert verified_req.status == RequirementStatus.VERIFIED


def test_conflict_detection_thermal_and_voltage():
    """Test 11: Conflict detector identifying contradictory constraints."""
    detector = ConflictDetector()

    req_thermal = EngineeringRequirement(
        requirement_id="REQ-TH-01",
        project_id="proj_rover",
        title="Maximum board operating temperature",
        description="Enclosure must maintain internal temp below 70°C",
        category=RequirementCategory.THERMAL,
        value="70.0",
        unit="°C",
        status=RequirementStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
    )

    dec_thermal_violator = EngineeringDecision(
        decision_id="DEC-TH-01",
        project_id="proj_rover",
        title="Compact Enclosure Design",
        description="Sealed IP67 enclosure allows internal hotspot 80°C under full load",
        category=DecisionCategory.THERMAL,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        selected_option="Sealed Aluminum Enclosure",
        rationale="Cost optimization",
        constraints=["thermal design allows 80°C peak hotspot"],
    )

    report = detector.detect_conflicts("proj_rover", [req_thermal], [dec_thermal_violator])

    assert report.has_conflicts is True
    assert report.conflict_count >= 1
    assert any(c.conflict_type == "THERMAL_LIMIT_EXCEEDED" for c in report.conflicts)
