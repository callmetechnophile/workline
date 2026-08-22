"""Unit tests for Planning (Domain, Timeline) and Research (Research, Innovation) agents."""

import asyncio
import pytest
from backend.workline.agents.planning.domain_researcher import DomainResearcherAgent
from backend.workline.agents.planning.timeline_agent import TimelineAgent
from backend.workline.agents.research.innovation_agent import InnovationAgent
from backend.workline.agents.research.research_agent import ResearchAgent
from backend.workline.agents.shared.tools import WorklineToolSuite


def test_domain_researcher_agent():
    """Test Domain Researcher extracting requirements, problem definition, and constraints."""
    async def _run():
        tools = WorklineToolSuite()
        agent = DomainResearcherAgent(tools)
        context = {
            "task": "Design an autonomous agricultural rover with environmental sensing",
            "project": {"description": "Autonomous Agricultural Rover"},
        }
        out = await agent.execute("test_rover", context)

        assert out.agent == "domain_researcher"
        assert out.status == "COMPLETED"
        assert len(out.findings) >= 1
        assert "initial_requirements" in out.data
        assert len(out.data["initial_requirements"]) >= 3
        assert "operating_constraints" in out.data

    asyncio.run(_run())


def test_timeline_agent():
    """Test Timeline Agent milestone scheduling and BLOCKS graph edge creation."""
    async def _run():
        tools = WorklineToolSuite()
        agent = TimelineAgent(tools)
        context = {"task": "Construct rover hardware schedule"}
        out = await agent.execute("test_rover", context)

        assert out.agent == "timeline_agent"
        assert out.status == "COMPLETED"
        assert "milestones" in out.data
        assert len(out.data["milestones"]) == 5
        assert out.data["estimated_duration_weeks"] > 0
        assert "critical_path" in out.data

    asyncio.run(_run())


def test_research_agent():
    """Test Research Agent semantic search and design pattern synthesis."""
    async def _run():
        tools = WorklineToolSuite()
        agent = ResearchAgent(tools)
        context = {"task": "Research solar MPPT and telemetry for rover"}
        out = await agent.execute("test_rover", context)

        assert out.agent == "research_agent"
        assert out.status == "COMPLETED"
        assert len(out.data["papers"]) >= 2
        assert len(out.data["design_patterns"]) >= 1

    asyncio.run(_run())


def test_innovation_agent():
    """Test Innovation Agent strictly separating FACT, INFERENCE, and RECOMMENDATION."""
    async def _run():
        tools = WorklineToolSuite()
        agent = InnovationAgent(tools)
        context = {"task": "Synthesize design improvements and risks"}
        out = await agent.execute("test_rover", context)

        assert out.agent == "innovation_agent"
        assert out.status == "COMPLETED"
        data = out.data
        assert len(data["facts"]) >= 1
        assert all(f.startswith("[FACT]") for f in data["facts"])
        assert len(data["inferences"]) >= 1
        assert all(i.startswith("[INFERENCE]") for i in data["inferences"])
        assert len(data["recommendations"]) >= 1
        assert all(r.startswith("[RECOMMENDATION]") for r in data["recommendations"])

    asyncio.run(_run())
