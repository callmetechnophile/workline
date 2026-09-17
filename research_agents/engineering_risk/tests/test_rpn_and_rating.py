"""Tests for RPN and Rating Scale calculations (Sections 95, 96, 97)."""
from research_agents.engineering_risk.schemas import FailureMode
from research_agents.engineering_risk.services.fmea_engine import FMEAEngine
from research_agents.engineering_risk.services.rating_profile_engine import RatingProfileEngine

def test_deterministic_rpn_calculation():
    # Section 95: Severity: 8, Occurrence: 4, Detection: 5 -> RPN = 160
    engine = FMEAEngine()
    rpn = engine.calculate_rpn(severity=8, occurrence=4, detection=5)
    assert rpn == 160

def test_unknown_occurrence_handling():
    # Section 96: No historical failure data -> UNKNOWN or ESTIMATED
    engine = FMEAEngine()
    fm = FailureMode(failure_mode_id="FM-01", description="Optical sensor delamination")
    record = engine.evaluate_fmea(
        project_id="proj_01",
        failure_mode=fm,
        severity=7,
        occurrence=3,
        detection=4,
        occurrence_nature="ESTIMATED",
        occurrence_justification="No empirical field return history; conservative estimate applied",
    )
    assert record.occurrence_nature == "ESTIMATED"
    assert "No empirical field return history" in record.occurrence_justification
    assert record.risk_priority_number == 84

def test_critical_safety_override():
    # Section 97: Critical safety consequence forces CRITICAL_REVIEW
    engine = FMEAEngine()
    fm = FailureMode(failure_mode_id="FM-02", description="High-voltage isolation breakdown")
    record = engine.evaluate_fmea(
        project_id="proj_01",
        failure_mode=fm,
        severity=9,  # >= 9 threshold
        occurrence=1,
        detection=1,
    )
    assert record.critical_review_required is True
    level = engine.determine_risk_level(record.risk_priority_number, record.severity)
    assert level == "CRITICAL"

def test_rating_profile_and_matrix():
    rp_engine = RatingProfileEngine()
    profile = rp_engine.get_default_rating_profile()
    assert 9 in profile.severity_scale
    assert "Critical" in profile.severity_scale[9]

    mat_class = rp_engine.classify_matrix(likelihood_score=8, severity_score=8)
    assert mat_class in ("HIGH", "CRITICAL")
