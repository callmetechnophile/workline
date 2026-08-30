"""
End-to-end unit and integration tests for WebResearchAgent.
"""

import pytest
from typing import List, Optional

from research_agents.web_research_agent.agent import WebResearchAgent
from research_agents.web_research_agent.providers.base import (
    ProviderTimeoutError,
    WebResearchProvider,
)
from research_agents.web_research_agent.schemas import (
    RawWebResult,
    WebResearchAgentInput,
)


class MockTavilyProvider(WebResearchProvider):
    """Mock Tavily provider for test isolation."""

    async def search(
        self,
        query: str,
        limit: int = 10,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        return [
            RawWebResult(
                title="NVIDIA Jetson Orin Nano Developer Kit — Official Documentation",
                url="https://developer.nvidia.com/embedded/jetson-orin-nano",
                snippet="NVIDIA Jetson Orin Nano delivers 40 TOPS AI performance with 6-core ARM CPU and Ampere GPU.",
                content="Operating voltage is 5.0V to 20.0V DC. Features Gigabit Ethernet, USB-C, and PCIe Gen 4.",
                publisher="NVIDIA",
                source_tool="tavily",
            ),
            RawWebResult(
                title="GitHub - thermal-drone-rescue/yolov8-ros2",
                url="https://github.com/thermal-drone-rescue/yolov8-ros2",
                snippet="Real-time thermal human detection for autonomous UAV search with ROS 2 and TensorRT.",
                content="ROS 2 Humble package with Jetson Orin Nano deployment instructions and benchmark results.",
                publisher="GitHub",
                source_tool="tavily",
            ),
        ]

    async def extract(self, url: str, execution_id: Optional[str] = None):
        return None

    async def crawl(self, url: str, max_depth: int = 1, execution_id: Optional[str] = None):
        return []


class MockAnakinProvider(WebResearchProvider):
    """Mock Anakin provider for scraping / crawling test isolation."""

    async def search(
        self,
        query: str,
        limit: int = 10,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        return [
            RawWebResult(
                title="FLIR Lepton 3.5 Thermal Camera Module Datasheet",
                url="https://flir.com/products/lepton-3-5/datasheet.pdf",
                snippet="160x120 thermal sensor with shuttered radiometric temperature output.",
                content="Supply voltage: 3.3V operating voltage. SPI video interface and I2C command interface.",
                publisher="Teledyne FLIR",
                source_tool="anakin",
            )
        ]

    async def extract(self, url: str, execution_id: Optional[str] = None):
        return RawWebResult(
            title="FLIR Lepton 3.5 Technical Specs",
            url=url,
            content="Operating voltage: 3.3V. SPI interface.",
            source_tool="anakin",
        )

    async def crawl(self, url: str, max_depth: int = 1, execution_id: Optional[str] = None):
        return []


class FailingProvider(WebResearchProvider):
    """Failing provider for error testing."""

    async def search(self, query: str, limit: int = 10, execution_id: Optional[str] = None):
        raise ProviderTimeoutError("mock_failing", "Search request timed out.")

    async def extract(self, url: str, execution_id: Optional[str] = None):
        raise ProviderTimeoutError("mock_failing", "Extraction timed out.")

    async def crawl(self, url: str, max_depth: int = 1, execution_id: Optional[str] = None):
        return []


@pytest.mark.asyncio
async def test_web_research_agent_successful_run():
    agent = WebResearchAgent(
        tavily_provider=MockTavilyProvider(),
        anakin_provider=MockAnakinProvider(),
    )

    input_data = WebResearchAgentInput(
        project_title="Autonomous Search and Rescue Drone",
        project_description="A UAV using Jetson Orin and FLIR thermal sensor for human detection.",
        engineering_domain="Robotics / Computer Vision",
        research_objectives=["thermal human detection", "edge inference"],
        components=["Jetson Orin Nano", "FLIR Lepton"],
        technologies=["YOLOv8", "ROS 2"],
        constraints=["real-time inference"],
        keywords=["UAV search and rescue", "thermal human detection"],
        max_sources=5,
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert output.project.title == "Autonomous Search and Rescue Drone"
    assert output.sources_selected > 0
    assert len(output.sources) <= 5

    # Check top source
    top_src = output.sources[0]
    assert top_src.relevance_score > 0.4
    assert top_src.authority_score > 0.6
    assert len(top_src.authority_reasons) > 0

    # Check extracted engineering facts with provenance
    assert len(output.facts) > 0
    for fact in output.facts:
        assert fact.source_id is not None
        assert fact.source_url.startswith("http")
        assert fact.confidence > 0.5
        assert fact.retrieved_at is not None


@pytest.mark.asyncio
async def test_web_research_agent_error_handling():
    agent = WebResearchAgent(
        tavily_provider=FailingProvider(),
        anakin_provider=FailingProvider(),
    )

    input_data = WebResearchAgentInput(
        project_title="Search Drone",
        project_description="Thermal UAV.",
        max_sources=5,
    )

    output = await agent.run(input_data)
    assert output.status == "error"
    assert len(output.errors) > 0
    assert output.errors[0].code == "PROVIDER_TIMEOUT"
    assert output.errors[0].retryable is True


def test_web_research_agent_sync_execution():
    agent = WebResearchAgent(
        tavily_provider=MockTavilyProvider(),
        anakin_provider=MockAnakinProvider(),
    )

    input_data = WebResearchAgentInput(
        project_title="Synchronous Test Drone",
        project_description="Testing run_sync method.",
        max_sources=3,
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert output.sources_selected > 0
