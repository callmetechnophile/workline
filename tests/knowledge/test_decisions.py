"""Tests for engineering decision lifecycle, approval policies, alternatives, evidence, and linking."""

import pytest

from backend.workline.knowledge import (
    Actor,
    ActorType,
    DecisionAlternative,
    DecisionCategory,
    DecisionEvidence,
    DecisionService,
    DecisionStatus,
    EngineeringDecision,
    EvidenceSourceType,
    UnauthorizedApprovalError,
)


@pytest.fixture
def clean_decision_service() -> DecisionService:
    return DecisionService()


def test_decision_creation_and_fields(clean_decision_service: DecisionService):
    """Test 1: Creating an engineering decision with alternatives and evidence."""
    alt1 = DecisionAlternative(
        alternative_id="alt_01",
        decision_id="DEC-101",
        name="MPM3610",
        description="Integrated inductor module",
        advantages=["Smaller PCB footprint"],
        disadvantages=["Higher unit cost"],
        rejection_reason="Exceeds target BOM budget",
    )
    alt2 = DecisionAlternative(
        alternative_id="alt_02",
        decision_id="DEC-101",
        name="LM2596",
        description="Legacy switching regulator",
        advantages=["Low cost", "Widely available"],
        disadvantages=["Large inductor required", "Low efficiency 75%"],
        rejection_reason="Efficiency too low for thermal target",
    )

    ev1 = DecisionEvidence(
        evidence_id="ev_01",
        decision_id="DEC-101",
        source_type=EvidenceSourceType.DATASHEET,
        title="TI TPS62130 Datasheet",
        claim="Supports 3V to 17V input, 3A continuous output, 95% peak efficiency",
        confidence=1.0,
    )

    decision = EngineeringDecision(
        decision_id="DEC-101",
        project_id="proj_rover",
        title="Select 3.3V Step-Down Regulator",
        description="Selection of main system voltage regulator",
        category=DecisionCategory.POWER_ARCHITECTURE,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng", name="Lead Engineer"),
        problem="Need 3.3V / 2A regulator meeting package and efficiency constraints",
        rationale="Meets current requirement, package constraints, efficiency target, and low BOM cost.",
        selected_option="TPS62130RGTR",
        constraints=["V_in = 12V", "V_out = 3.3V", "I_out >= 2A", "Efficiency > 90%"],
        alternatives=[alt1, alt2],
        evidence=[ev1],
        project_version="0.3.0",
        git_commit="a83b1f2",
    )

    created = clean_decision_service.create_decision(decision)

    assert created.decision_id == "DEC-101"
    assert created.status == DecisionStatus.APPROVED
    assert len(created.alternatives) == 2
    assert len(created.evidence) == 1
    assert created.selected_option == "TPS62130RGTR"


def test_agent_proposal_defaults_to_proposed(clean_decision_service: DecisionService):
    """Test 2: Agent recommendations are strictly marked PROPOSED and cannot self-approve."""
    dec = EngineeringDecision(
        decision_id="DEC-AGENT-1",
        project_id="proj_rover",
        title="AI Recommends Replace LDO",
        description="Switch to buck converter",
        category=DecisionCategory.POWER_ARCHITECTURE,
        status=DecisionStatus.APPROVED,  # Agent attempts to declare itself approved
        created_by=Actor(actor_type=ActorType.AGENT, actor_id="PowerAgent"),
        selected_option="TPS62130",
        rationale="Efficiency improvements",
    )

    created = clean_decision_service.create_decision(dec)
    # Must be forced to PROPOSED
    assert created.status == DecisionStatus.PROPOSED

    # Agent cannot approve
    with pytest.raises(UnauthorizedApprovalError):
        clean_decision_service.approve_decision(
            "DEC-AGENT-1",
            actor=Actor(actor_type=ActorType.AGENT, actor_id="PowerAgent"),
        )

    # Human can approve
    approved = clean_decision_service.approve_decision(
        "DEC-AGENT-1",
        actor=Actor(actor_type=ActorType.HUMAN, actor_id="human_eng"),
    )
    assert approved.status == DecisionStatus.APPROVED


def test_decision_rejection(clean_decision_service: DecisionService):
    """Test 3: Rejecting a proposed decision."""
    dec = EngineeringDecision(
        decision_id="DEC-REJ",
        project_id="proj_rover",
        title="Use Wireless Charging Coil",
        description="Add Qi charging",
        category=DecisionCategory.POWER_ARCHITECTURE,
        status=DecisionStatus.PROPOSED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_user"),
        selected_option="Qi Coil 5W",
    )
    clean_decision_service.create_decision(dec)

    rejected = clean_decision_service.reject_decision(
        "DEC-REJ",
        actor=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"),
        reason="Mechanical enclosure too thick for magnetic coupling",
    )
    assert rejected.status == DecisionStatus.REJECTED
    assert rejected.metadata["rejection_reason"] == "Mechanical enclosure too thick for magnetic coupling"


def test_decision_supersession(clean_decision_service: DecisionService):
    """Test 4: Superseding an older decision preserves history and links both."""
    dec_a = EngineeringDecision(
        decision_id="DEC-MCU-01",
        project_id="proj_rover",
        title="Select Primary MCU",
        description="MCU selection for flight controller",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_user"),
        selected_option="ESP32-S3",
        rationale="Low cost, built-in Wi-Fi / BLE",
        project_version="0.3.0",
    )
    clean_decision_service.create_decision(dec_a)

    dec_b = EngineeringDecision(
        decision_id="DEC-MCU-02",
        project_id="proj_rover",
        title="Upgrade Primary MCU to STM32H7",
        description="Replace ESP32-S3 due to insufficient compute for real-time motor control",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_user"),
        selected_option="STM32H743ZI",
        rationale="480MHz Cortex-M7 required for 10kHz FOC motor loop",
        project_version="0.6.0",
    )

    old_dec, new_dec = clean_decision_service.supersede_decision(
        old_decision_id="DEC-MCU-01",
        new_decision=dec_b,
        actor=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"),
    )

    assert old_dec.status == DecisionStatus.SUPERSEDED
    assert old_dec.superseded_by == "DEC-MCU-02"
    assert new_dec.supersedes == "DEC-MCU-01"
    assert new_dec.status == DecisionStatus.APPROVED


def test_implementation_and_validation_linking(clean_decision_service: DecisionService):
    """Test 5 & 6: Linking engineering objects and validation results to decisions."""
    dec = EngineeringDecision(
        decision_id="DEC-PWR-01",
        project_id="proj_rover",
        title="Use TPS62130 for 3.3V Rail",
        description="Power supply design",
        category=DecisionCategory.POWER_ARCHITECTURE,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_user"),
        selected_option="TPS62130RGTR",
    )
    clean_decision_service.create_decision(dec)

    # Link implementation
    clean_decision_service.link_implementation("DEC-PWR-01", "VCC_3V3_RAIL")
    clean_decision_service.link_implementation("DEC-PWR-01", "U1_TPS62130")

    updated = clean_decision_service.get_decision("DEC-PWR-01")
    assert updated.status == DecisionStatus.IMPLEMENTED
    assert "VCC_3V3_RAIL" in updated.implemented_objects
    assert "U1_TPS62130" in updated.implemented_objects

    # Link validation PASS
    clean_decision_service.link_validation("DEC-PWR-01", validation_status="PASS", validation_id="VAL-RUN-101")
    val_dec = clean_decision_service.get_decision("DEC-PWR-01")
    assert val_dec.status == DecisionStatus.VALIDATED
    assert val_dec.validation_status == "PASS"
