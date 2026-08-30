"""
End-to-end unit and integration tests for ResearchPaperAgent.
"""

import pytest
from typing import List, Optional

from research_agents.research_paper_agent.agent import ResearchPaperAgent
from research_agents.research_paper_agent.providers.base import (
    BasePaperProvider,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from research_agents.research_paper_agent.schemas import (
    RawPaperRecord,
    ResearchPaperAgentInput,
)


class MockFreephdlaborProvider(BasePaperProvider):
    """Mock provider generating realistic academic candidate records."""

    def __init__(self, should_fail: bool = False, fail_error=None):
        self.should_fail = should_fail
        self.fail_error = fail_error

    async def search(
        self,
        query: str,
        limit: int = 20,
        execution_id: Optional[str] = None,
    ) -> List[RawPaperRecord]:
        if self.should_fail:
            if self.fail_error:
                raise self.fail_error
            raise ProviderRateLimitError("Mock rate limit exceeded.")

        # Return mock candidates
        return [
            RawPaperRecord(
                paper_id="paper_001",
                title="Deep Thermal Object Detection for Autonomous Search and Rescue UAVs",
                authors=["Jane Doe", "John Smith"],
                abstract="Thermal sensor integration with YOLOv8 for edge UAV human rescue mission detection.",
                publication_date="2024-03-15",
                doi="10.1109/ICRA.2024.001",
                venue="IEEE International Conference on Robotics and Automation (ICRA)",
                paper_url="https://ieeexplore.ieee.org/document/001",
                pdf_url="https://ieeexplore.ieee.org/stamp/001.pdf",
                citation_count=22,
                keywords=["thermal vision", "UAV", "YOLOv8"],
            ),
            RawPaperRecord(
                paper_id="paper_002",
                title="Real-Time Human Location in Disaster Scenarios with Edge Jetson",
                authors=["Mark Lee"],
                abstract="Edge inference benchmark on NVIDIA Jetson Orin Nano for thermal rescue robotics.",
                publication_date="2023-11-02",
                doi="10.1109/IROS.2023.002",
                venue="IEEE/RSJ IROS",
                paper_url="https://ieeexplore.ieee.org/document/002",
                pdf_url=None,  # No PDF link available
                citation_count=8,
                keywords=["Jetson Orin", "edge compute"],
            ),
            RawPaperRecord(
                paper_id="paper_003",
                title="Autonomous Navigation in GPS-Denied Disaster Environments",
                authors=["Sarah Connor"],
                abstract="Multi-sensor SLAM and path planning for autonomous drone rescue.",
                publication_date="2024-01-20",
                doi="10.1007/s10514-023-003",
                venue="Autonomous Robots",
                paper_url="https://link.springer.com/article/10.1007/003",
                pdf_url="https://link.springer.com/content/pdf/10.1007/003.pdf",
                citation_count=35,
            ),
        ]


@pytest.mark.asyncio
async def test_agent_successful_run():
    mock_provider = MockFreephdlaborProvider()
    agent = ResearchPaperAgent(provider=mock_provider)

    input_data = ResearchPaperAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="A drone using thermal vision and edge models for locating humans in disaster zones.",
        engineering_domain="Robotics / Computer Vision",
        research_objectives=["thermal human detection", "autonomous navigation"],
        components=["Jetson Orin Nano", "thermal camera"],
        technologies=["YOLO", "computer vision"],
        constraints=["real-time inference"],
        keywords=["thermal human detection", "UAV search and rescue"],
        max_papers=5,
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert output.project.title == "Autonomous Search and Rescue Drone"
    assert output.papers_selected > 0
    assert len(output.papers) <= 5

    # Check top ranked paper
    top_paper = output.papers[0]
    assert top_paper.relevance_score > 0.4
    assert len(top_paper.relevance_reasons) > 0

    # Verify PDF availability logic
    paper_with_pdf = next((p for p in output.papers if p.paper_id == "paper_001"), None)
    assert paper_with_pdf is not None
    assert paper_with_pdf.pdf_available is True
    assert paper_with_pdf.pdf_url is not None

    paper_without_pdf = next((p for p in output.papers if p.paper_id == "paper_002"), None)
    assert paper_without_pdf is not None
    assert paper_without_pdf.pdf_available is False


@pytest.mark.asyncio
async def test_agent_limit_enforcement():
    mock_provider = MockFreephdlaborProvider()
    agent = ResearchPaperAgent(provider=mock_provider)

    input_data = ResearchPaperAgentInput(
        project_title="Search Drone",
        project_description="Thermal UAV search.",
        max_papers=2,
    )

    output = await agent.run(input_data)
    assert len(output.papers) == 2
    assert output.papers_selected == 2


@pytest.mark.asyncio
async def test_agent_error_handling_graceful():
    mock_provider = MockFreephdlaborProvider(
        should_fail=True,
        fail_error=ProviderTimeoutError("Search timed out"),
    )
    agent = ResearchPaperAgent(provider=mock_provider)

    input_data = ResearchPaperAgentInput(
        project_title="Search Drone",
        project_description="Thermal UAV search.",
        max_papers=5,
    )

    output = await agent.run(input_data)
    assert output.status == "error"
    assert len(output.errors) > 0
    assert output.errors[0].code == "PROVIDER_TIMEOUT"
    assert output.errors[0].retryable is True


def test_agent_sync_execution():
    mock_provider = MockFreephdlaborProvider()
    agent = ResearchPaperAgent(provider=mock_provider)

    input_data = ResearchPaperAgentInput(
        project_title="Synchronous Test Drone",
        project_description="Testing run_sync method.",
        max_papers=3,
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert output.papers_selected > 0
