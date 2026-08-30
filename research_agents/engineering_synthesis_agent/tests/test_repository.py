"""
Unit tests for EngineeringDecisionRepository interface (Section 28).
"""

import pytest
from research_agents.engineering_synthesis_agent.repository import InMemoryEngineeringDecisionRepository
from research_agents.engineering_synthesis_agent.schemas import (
    DecisionTraceability,
    EngineeringDecision,
    EngineeringRisk,
    EngineeringSynthesisAgentOutput,
    EngineeringTradeoff,
    ProjectMeta,
    RecommendationItem,
    RequirementAnalysis,
    TechnicalFinding,
    ValidationRequirement,
)


@pytest.mark.asyncio
async def test_repository_methods():
    repo = InMemoryEngineeringDecisionRepository()
    proj_id = "proj_test_01"

    # Save components
    await repo.save_requirement_analysis(RequirementAnalysis(requirement_id="REQ-01", requirement="Req 1"), proj_id)
    await repo.save_finding(TechnicalFinding(finding_id="FIND-01", category="compute", finding="Find 1", impact_on_project="None"), proj_id)
    await repo.save_tradeoff(EngineeringTradeoff(tradeoff_id="TRADE-01", decision_area="Compute", recommended_option="Jetson", reasoning="AI"), proj_id)
    await repo.save_decision(EngineeringDecision(decision_id="DEC-01", decision_area="Compute", selected_option="Jetson", decision_reason="AI"), proj_id)
    await repo.save_recommendation(RecommendationItem(recommendation_id="REC-01", category="hardware", recommendation="Rec 1", reason="Reason"), proj_id)
    await repo.save_risk(EngineeringRisk(risk_id="RISK-01", category="thermal", description="Risk 1", mitigation="Mitigation"), proj_id)
    await repo.save_validation_requirement(ValidationRequirement(validation_id="VAL-01", category="bench_test", description="Val 1", acceptance_criteria="OK"), proj_id)
    await repo.save_traceability(DecisionTraceability(decision_id="DEC-01", decision="Jetson", reasoning="AI"), proj_id)

    # Save full output
    output = EngineeringSynthesisAgentOutput(
        project=ProjectMeta(project_id=proj_id, title="Test Project"),
    )
    saved_id = await repo.save_output(output)
    assert saved_id == proj_id

    retrieved = await repo.get_output(proj_id)
    assert retrieved is not None
    assert retrieved.project.title == "Test Project"
