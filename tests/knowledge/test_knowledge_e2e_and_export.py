"""End-to-end tests for requirement traceability, conflict detection, supersession, and .wlipjt package export."""

from pathlib import Path
import pytest

from backend.workline.knowledge import (
    Actor,
    ActorType,
    DecisionAlternative,
    DecisionCategory,
    DecisionEvidence,
    DecisionStatus,
    EngineeringDecision,
    EngineeringRequirement,
    EvidenceSourceType,
    KnowledgeService,
    RequirementCategory,
    RequirementPriority,
    RequirementStatus,
)
from backend.workline.project.export_service import ExportService


def test_end_to_end_traceability_lifecycle():
    """
    Test 28: Complete End-to-End Requirement Traceability Workflow
    1. Requirement: '3.3V rail must support 2A'
    2. Decision: 'Use TPS62130'
    3. Implementation: 'VCC_3V3'
    4. Validation: 'PASS'
    5. Query: 'Why did we select TPS62130?' -> returns Requirement + Decision + Evidence + Implementation + Validation!
    """
    svc = KnowledgeService()
    project_id = "proj_rover_e2e"

    # Step 1: Create Requirement
    req = EngineeringRequirement(
        requirement_id="REQ-023",
        project_id=project_id,
        title="3.3V rail must support minimum 2A",
        description="Provide 3.3V power rail with 2A continuous capability",
        category=RequirementCategory.ELECTRICAL,
        priority=RequirementPriority.CRITICAL,
        value="2.0",
        unit="A",
        status=RequirementStatus.PROPOSED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="sys_architect"),
    )
    svc.create_requirement(req)

    # Step 2: Create Decision with Evidence and link to Requirement
    ev = DecisionEvidence(
        evidence_id="EV-TPS-01",
        decision_id="DEC-102",
        source_type=EvidenceSourceType.DATASHEET,
        title="TI TPS62130 Datasheet",
        claim="Supports 3A continuous output current with > 90% efficiency",
    )
    dec = EngineeringDecision(
        decision_id="DEC-102",
        project_id=project_id,
        title="Select TPS62130 3.3V Step-Down Regulator",
        description="Power supply regulation",
        category=DecisionCategory.POWER_ARCHITECTURE,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="power_eng"),
        problem="Need 3.3V / 2A regulator meeting package constraints",
        rationale="Meets current requirement, package constraints, efficiency target, and available documentation.",
        selected_option="TPS62130RGTR",
        evidence=[ev],
        constraints=["V_in = 12V", "V_out = 3.3V", "I_out >= 2A"],
        project_version="0.4.0",
    )
    svc.create_decision(dec)

    # Link requirement to decision
    svc.requirements.link_satisfying_decision("REQ-023", "DEC-102")

    # Step 3: Link Implementation
    svc.decisions.link_implementation("DEC-102", "VCC_3V3_POWER_RAIL")
    svc.decisions.link_implementation("DEC-102", "U1_TPS62130")

    # Step 4: Validate
    svc.decisions.link_validation("DEC-102", validation_status="PASS", validation_id="VAL-042")
    svc.verify_requirement("REQ-023", validation_id="VAL-042", passed=True, actor=Actor(actor_type=ActorType.HUMAN, actor_id="qa_lead"))

    # Step 5: Query "Why did we select TPS62130?"
    search_results = svc.search_knowledge(project_id, "Why did we select TPS62130?")
    assert len(search_results) >= 1
    match = search_results[0]
    assert match.object_id == "DEC-102"
    assert "TPS62130" in match.title
    assert match.status in ("APPROVED", "VALIDATED", "IMPLEMENTED")

    # Verify full traceability graph
    chain = svc.get_requirement_traceability("REQ-023")
    assert chain.requirement_id == "REQ-023"
    assert len(chain.decisions) >= 1
    assert chain.decisions[0]["decision_id"] == "DEC-102"
    assert len(chain.implementations) >= 2
    assert len(chain.validations) >= 1
    assert chain.validations[0]["validation_status"] == "PASS"


def test_conflict_detection_e2e():
    """
    Test 29: Conflict Detection
    Requirement: maximum board temperature = 70°C
    Decision: thermal design allows 80°C
    Expected: CONFLICT detected (not silently resolved).
    """
    svc = KnowledgeService()
    project_id = "proj_conflict_test"

    req = EngineeringRequirement(
        requirement_id="REQ-TEMP-MAX",
        project_id=project_id,
        title="Maximum enclosure temperature limit",
        description="Board temperature must not exceed 70°C under full workload",
        category=RequirementCategory.THERMAL,
        value="70",
        unit="°C",
        status=RequirementStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_lead"),
    )
    svc.create_requirement(req)

    dec = EngineeringDecision(
        decision_id="DEC-ENC-01",
        project_id=project_id,
        title="Passive Heat Dissipation Enclosure",
        description="Sealed aluminium chassis allows 80°C hotspot in high ambient",
        category=DecisionCategory.THERMAL,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="mech_eng"),
        selected_option="Sealed Cast Aluminium Enclosure",
        rationale="Cost optimization",
        constraints=["thermal design allows 80°C hotspot"],
    )
    svc.create_decision(dec)

    report = svc.detect_conflicts(project_id)
    assert report.has_conflicts is True
    assert report.conflict_count >= 1
    assert any("THERMAL_LIMIT_EXCEEDED" in c.conflict_type for c in report.conflicts)


def test_supersession_query_e2e():
    """
    Test 30: Supersession Query
    Decision A: Use ESP32-S3
    Decision B: Use STM32H7 (B supersedes A)
    Query: 'What MCU are we currently using?' -> STM32H7
    Query: 'What did we previously use?' -> ESP32-S3
    """
    svc = KnowledgeService()
    project_id = "proj_mcu_evolve"

    dec_a = EngineeringDecision(
        decision_id="DEC-MCU-01",
        project_id=project_id,
        title="Initial Microcontroller Selection",
        description="Main system MCU",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_user"),
        selected_option="ESP32-S3",
        rationale="Built-in Wi-Fi and Bluetooth",
        project_version="0.3.0",
    )
    svc.create_decision(dec_a)

    dec_b = EngineeringDecision(
        decision_id="DEC-MCU-02",
        project_id=project_id,
        title="Upgrade to High Performance MCU",
        description="Replace ESP32-S3 with STM32H7 for motor control",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="eng_user"),
        selected_option="STM32H743ZI",
        rationale="480MHz Cortex-M7",
        project_version="0.6.0",
    )
    svc.supersede_decision("DEC-MCU-01", dec_b, actor=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"))

    # Check active decisions
    active_decs = svc.decisions.list_decisions(project_id, status=DecisionStatus.APPROVED)
    assert len(active_decs) == 1
    assert active_decs[0].selected_option == "STM32H743ZI"

    # Check superseded historical decision
    superseded_decs = svc.decisions.list_decisions(project_id, status=DecisionStatus.SUPERSEDED)
    assert len(superseded_decs) == 1
    assert superseded_decs[0].selected_option == "ESP32-S3"


def test_wlipjt_knowledge_package_export(tmp_path: Path):
    """Test 31: Exporting project with knowledge decisions into .wlipjt package."""
    svc = KnowledgeService()
    project_id = "proj_pkg_test"

    # Create dummy project directory
    proj_dir = tmp_path / "test_knowledge_proj"
    proj_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = proj_dir / "workline.yaml"
    manifest_file.write_text(
        f"project:\n  name: Test Knowledge Project\n  project_id: {project_id}\n  version: 1.0.0\n  schema_version: 1\n",
        encoding="utf-8",
    )

    # Add decision in knowledge service
    dec = EngineeringDecision(
        decision_id="DEC-EXP-01",
        project_id=project_id,
        title="Export Test Decision",
        description="Testing .wlipjt knowledge packaging",
        category=DecisionCategory.SYSTEM_ARCHITECTURE,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        selected_option="Modular Architecture",
    )
    svc.create_decision(dec)

    exporter = ExportService()
    pkg_path, manifest, warnings = exporter.export_project(proj_dir)

    assert pkg_path.exists()
    assert manifest.format == "wlipjt"
    assert manifest.project_id in (project_id, "test_knowledge_proj")
