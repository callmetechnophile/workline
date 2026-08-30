"""
Unit tests for multi-factor relevance ranking and reasons explanation.
"""

from research_agents.research_paper_agent.schemas import RawPaperRecord, ResearchPaperAgentInput
from research_agents.research_paper_agent.services.ranking import RelevanceScorer


def test_high_relevance_paper_scoring():
    scorer = RelevanceScorer()
    input_data = ResearchPaperAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="A drone using thermal vision and edge YOLO models for human detection in disaster zones.",
        engineering_domain="Robotics / Computer Vision",
        research_objectives=["thermal human detection", "autonomous navigation"],
        components=["Jetson Orin Nano", "FLIR thermal camera"],
        technologies=["YOLOv8", "TensorRT"],
        constraints=["real-time inference", "low power"],
        keywords=["thermal human detection", "UAV search and rescue"],
    )

    highly_relevant_paper = RawPaperRecord(
        paper_id="p1",
        title="Thermal Human Detection for UAV Search and Rescue with YOLOv8 on Jetson Orin",
        abstract="We demonstrate real-time inference for autonomous thermal human detection using YOLOv8 optimized with TensorRT on Jetson Orin Nano hardware.",
        publication_date="2024",
        keywords=["thermal vision", "human detection", "YOLOv8"],
    )

    score, reasons = scorer.score_paper(highly_relevant_paper, input_data)

    assert 0.6 <= score <= 1.0
    assert len(reasons) >= 3
    assert any("Title directly addresses" in r or "Title contains" in r for r in reasons)
    assert any("YOLO" in r for r in reasons)
    assert any("Jetson" in r for r in reasons)


def test_irrelevant_paper_scoring():
    scorer = RelevanceScorer()
    input_data = ResearchPaperAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="Thermal UAV search.",
        keywords=["thermal human detection"],
    )

    irrelevant_paper = RawPaperRecord(
        paper_id="p99",
        title="Economic Impacts of Agricultural Subsidies in Western Europe",
        abstract="This paper analyzes fiscal agricultural policies and subsidy reforms from 1990 to 2010.",
        publication_date="2012",
    )

    score, reasons = scorer.score_paper(irrelevant_paper, input_data)

    assert score < 0.20


def test_score_bounds_and_recency():
    scorer = RelevanceScorer()
    input_data = ResearchPaperAgentInput(
        project_title="Drone Thermal Sensing",
        project_description="Thermal drone.",
        keywords=["thermal sensing"],
    )

    recent_paper = RawPaperRecord(
        paper_id="p1",
        title="Drone Thermal Sensing Advancements",
        publication_date="2025",
    )
    old_paper = RawPaperRecord(
        paper_id="p2",
        title="Drone Thermal Sensing Advancements",
        publication_date="2005",
    )

    score_recent, reasons_recent = scorer.score_paper(recent_paper, input_data)
    score_old, _ = scorer.score_paper(old_paper, input_data)

    assert 0.0 <= score_recent <= 1.0
    assert 0.0 <= score_old <= 1.0
    assert score_recent > score_old
    assert any("Recent" in r for r in reasons_recent)
