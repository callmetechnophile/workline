"""Tests for engineering findings, failure memory, and lessons learned."""

import pytest

from backend.workline.knowledge import (
    Actor,
    ActorType,
    EngineeringFinding,
    EngineeringLesson,
    FindingService,
    FindingSeverity,
    FindingStatus,
    LessonService,
    knowledge_summarizer,
)


@pytest.fixture
def finding_svc() -> FindingService:
    return FindingService()


@pytest.fixture
def lesson_svc() -> LessonService:
    return LessonService()


def test_finding_creation_and_resolution(finding_svc: FindingService):
    """Test 12, 13 & 14: Creating an anomaly finding and resolving it via a decision."""
    finding = EngineeringFinding(
        finding_id="THERMAL-001",
        project_id="proj_rover",
        title="Regulator placement thermal hotspot",
        description="PCB thermal analysis shows peak temperature 85°C near MCU",
        category="THERMAL",
        severity=FindingSeverity.CRITICAL,
        source="PINN_SIMULATION",
        source_id="SIM-RUN-402",
        status=FindingStatus.OPEN,
        created_by=Actor(actor_type=ActorType.AGENT, actor_id="PcbAgent"),
    )

    created = finding_svc.create_finding(finding)
    assert created.finding_id == "THERMAL-001"
    assert created.status == FindingStatus.OPEN

    # Resolve finding linking to corrective decision
    resolved = finding_svc.resolve_finding(
        finding_id="THERMAL-001",
        resolution="Relocated buck converter to board edge and added 4x thermal vias connected to bottom ground pour.",
        resolved_by_decision_id="DEC-TH-02",
        actor=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"),
    )

    assert resolved.status == FindingStatus.RESOLVED
    assert resolved.resolved_by_decision_id == "DEC-TH-02"


def test_lesson_creation_and_recommendation(lesson_svc: LessonService):
    """Test 15 & 16: Recording engineering lessons learned and formatting."""
    lesson = EngineeringLesson(
        lesson_id="LES-001",
        project_id="proj_rover",
        title="High-current regulator placement caused thermal hotspot",
        description="Thermal management guidelines for compact boards",
        context="PCB thermal analysis and PINN simulation",
        cause="Regulator placed near sensitive MCU without dedicated heat dissipation path",
        impact="Predicted peak temperature exceeded 85°C operating limit",
        recommendation="Separate high-power switching components from sensitive logic and provide copper/thermal-via area connected to ground planes.",
        derived_from_finding_id="THERMAL-001",
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"),
    )

    created = lesson_svc.create_lesson(lesson)
    assert created.lesson_id == "LES-001"
    assert "Separate high-power" in created.recommendation

    lessons_list = lesson_svc.list_lessons("proj_rover")
    assert len(lessons_list) == 1
    assert lessons_list[0].derived_from_finding_id == "THERMAL-001"
