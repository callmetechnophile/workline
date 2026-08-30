"""
Unit tests for DeepResearchSynthesizer and MarkdownReportFormatter.
"""

import pytest
from research_agents.deep_research_agent.providers.mock_provider import MockReasoningProvider
from research_agents.deep_research_agent.schemas import (
    ComponentTradeStudy,
    EngineeringRecommendation,
    EvidenceItem,
    ProjectMeta,
    SynthesizedClaim,
)
from research_agents.deep_research_agent.services.markdown_formatter import MarkdownReportFormatter
from research_agents.deep_research_agent.services.synthesizer import DeepResearchSynthesizer


@pytest.mark.asyncio
async def test_synthesizer_structured_output():
    mock_provider = MockReasoningProvider()
    synthesizer = DeepResearchSynthesizer(mock_provider)

    project = ProjectMeta(title="Autonomous SAR Drone", engineering_domain="Robotics")
    evidence = [
        EvidenceItem(
            evidence_id="ev_01",
            source_id="src_1",
            text="Jetson Orin Nano delivers 40 TOPS.",
        )
    ]

    result = await synthesizer.synthesize(project, evidence)

    assert result.executive_summary != ""
    assert result.architecture_analysis != ""
    assert len(result.component_trade_studies) >= 1
    assert len(result.extracted_claims) >= 1
    assert len(result.recommendations) >= 1


def test_markdown_formatter_generates_all_sections():
    formatter = MarkdownReportFormatter()
    project = ProjectMeta(title="Autonomous SAR Drone", engineering_domain="Robotics")

    report_md = formatter.format_report(
        project=project,
        executive_summary="Executive summary text.",
        architecture_analysis="Architecture details.",
        trade_studies=[
            ComponentTradeStudy(
                component_type="Edge Compute",
                candidates_evaluated=["Jetson Orin Nano", "RPi 5"],
                tradeoff_matrix={"Jetson Orin Nano": {"TOPS": 40}, "RPi 5": {"TOPS": 0}},
                recommended_option="Jetson Orin Nano",
                recommendation_reason="40 TOPS compute capability.",
            )
        ],
        claims=[
            SynthesizedClaim(
                claim="Jetson Orin Nano delivers 40 TOPS.",
                claim_type="explicit_source_claim",
                source_evidence_ids=["ev_01"],
            )
        ],
        comparisons=[],
        contradictions=[],
        implications=[],
        recommendations=[
            EngineeringRecommendation(
                recommendation="Deploy Jetson Orin Nano",
                category="hardware",
                priority="high",
                justification="Meets compute needs",
            )
        ],
        research_gaps=["Validation in rain."],
        evidence_used=[
            EvidenceItem(evidence_id="ev_01", source_id="src_1", text="Evidence 1")
        ],
    )

    assert "# Engineering Research Synthesis: Autonomous SAR Drone" in report_md
    assert "## 1. Executive Summary" in report_md
    assert "## 3. Component Trade Studies" in report_md
    assert "## 4. Synthesized Claims" in report_md
    assert "## 7. Actionable Design Guidance" in report_md
    assert "## 9. Evidence & Provenance Index" in report_md
