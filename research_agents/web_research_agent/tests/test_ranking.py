"""
Unit tests for web source relevance scoring and transparent reason generation.
"""

from research_agents.web_research_agent.schemas import RawWebResult, WebResearchAgentInput
from research_agents.web_research_agent.services.ranking import WebRelevanceScorer


def test_high_relevance_source_scoring():
    scorer = WebRelevanceScorer()
    input_data = WebResearchAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="UAV system for locating humans using thermal imaging.",
        engineering_domain="Robotics / Computer Vision",
        research_objectives=["thermal human detection", "edge inference"],
        components=["Jetson Orin Nano", "FLIR Lepton"],
        technologies=["YOLOv8", "ROS 2"],
        constraints=["real-time inference"],
        keywords=["thermal human detection", "UAV search and rescue"],
    )

    relevant_result = RawWebResult(
        title="Thermal Human Detection on NVIDIA Jetson Orin Nano with YOLOv8 and ROS 2",
        url="https://github.com/example/thermal-uav-rescue",
        snippet="Open source ROS 2 package running YOLOv8 on Jetson Orin Nano for thermal UAV search missions.",
        content="Provides launch files and TensorRT engines for FLIR Lepton cameras with real-time inference.",
    )

    score, reasons = scorer.score_source(relevant_result, input_data)
    assert score >= 0.70
    assert len(reasons) >= 3
    assert any("Jetson" in r or "FLIR" in r for r in reasons)
    assert any("YOLO" in r or "ROS" in r for r in reasons)


def test_low_relevance_source_scoring():
    scorer = WebRelevanceScorer()
    input_data = WebResearchAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="UAV thermal search.",
        keywords=["thermal human detection"],
    )

    irrelevant = RawWebResult(
        title="10 Best Coffee Brewing Techniques for Beginners",
        url="https://example.com/coffee-guide",
        snippet="Learn how to brew pour over and espresso coffee at home.",
    )

    score, reasons = scorer.score_source(irrelevant, input_data)
    assert score < 0.20
