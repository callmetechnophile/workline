"""Tests for Design Improvement Recommendations and Agent #16 Change Proposals (Section 13)."""
from research_agents.manufacturing_agent.schemas import DFMFinding
from research_agents.manufacturing_agent.services.recommendation_engine import RecommendationEngine

def test_recommendation_change_proposal():
    engine = RecommendationEngine()
    f = DFMFinding(
        finding_id="DFM-TOL-01",
        component_id="BEARING_HOUSING",
        category="TOLERANCE_DIFFICULTY",
        severity="MAJOR",
        description="Sub-10 micron bore tolerance",
    )
    recs = engine.generate_recommendations([f], [])
    assert len(recs) == 1
    assert "CHG-MFG-BEARING_HOUSING" in recs[0].change_request_id
    assert recs[0].confidence >= 0.90
