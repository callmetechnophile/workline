"""
Unit tests for search query planning and multi-angle query generation.
"""

from research_agents.research_paper_agent.schemas import ResearchPaperAgentInput
from research_agents.research_paper_agent.services.search import QueryPlanner


def test_multi_angle_query_generation():
    planner = QueryPlanner()
    input_data = ResearchPaperAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="A drone using computer vision and thermal sensing to locate humans in disaster environments.",
        engineering_domain="Robotics / Computer Vision",
        research_objectives=[
            "human detection",
            "thermal imaging",
            "autonomous navigation",
        ],
        components=[
            "Jetson Orin Nano",
            "thermal camera",
        ],
        technologies=[
            "YOLO",
            "computer vision",
        ],
        constraints=[
            "real-time inference",
            "edge deployment",
        ],
        keywords=[
            "thermal human detection",
            "UAV search and rescue",
        ],
        max_papers=20,
    )

    queries = planner.plan_queries(input_data, max_queries=5)

    assert 2 <= len(queries) <= 5
    # Ensure queries are clean, non-empty phrases
    for q in queries:
        assert len(q.split()) >= 2
        assert not q.endswith(".")
        assert "http" not in q

    combined = " ".join(queries).lower()
    assert "thermal" in combined or "human" in combined or "uav" in combined


def test_fallback_query_generation_with_sparse_input():
    planner = QueryPlanner()
    input_data = ResearchPaperAgentInput(
        project_title="High-efficiency 48V to 12V 20A Buck Converter",
        project_description="Synchronous buck converter design for high power telemetry distribution.",
    )

    queries = planner.plan_queries(input_data, max_queries=4)

    assert len(queries) >= 1
    assert any("buck" in q.lower() or "converter" in q.lower() for q in queries)
