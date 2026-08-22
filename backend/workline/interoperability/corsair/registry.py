"""Corsair integration registry."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus,
    CapabilityType,
    RiskLevel,
)
from backend.workline.interoperability.corsair.tools import CorsairToolRegistry
from backend.workline.interoperability.registry import ExternalAgent


class CorsairRegistry:
    """Manages Corsair external integration endpoints and capabilities."""

    def __init__(self):
        self.tool_registry = CorsairToolRegistry()
        self._integrations: Dict[str, ExternalAgent] = {}
        self._seed_integrations()

    def _seed_integrations(self) -> None:
        research_agent = ExternalAgent(
            agent_id="ResearchAgent",
            name="ResearchAgent",
            description="Deep technical research and semiconductor datasheet comparison via Corsair tools.",
            provider="Corsair Integrations",
            protocol="CORSAIR",
            endpoint="corsair://tools/datasheet-research",
            version="3.0.0",
            status=AgentStatus.AVAILABLE,
            capabilities=[
                AgentCapability(
                    capability_id="research",
                    agent_id="ResearchAgent",
                    name="Semiconductor Deep Research",
                    description="Synthesizes academic papers, whitepapers, and component errata.",
                    capability_type=CapabilityType.RESEARCH,
                    risk_level=RiskLevel.LOW,
                    estimated_cost=0.02,
                    input_schema={"type": "object", "required": ["query"]},
                    output_schema={"type": "object", "required": ["summary", "references"]},
                ),
                AgentCapability(
                    capability_id="document_analysis",
                    agent_id="ResearchAgent",
                    name="Technical Document Analysis",
                    description="Parses PDF datasheets, pinout tables, and timing diagrams.",
                    capability_type=CapabilityType.DOCUMENT_ANALYSIS,
                    risk_level=RiskLevel.LOW,
                    estimated_cost=0.02,
                ),
            ],
        )
        self._integrations[research_agent.agent_id] = research_agent

    def list_integrations(self) -> List[ExternalAgent]:
        return list(self._integrations.values())

    def get_integration(self, agent_id: str) -> Optional[ExternalAgent]:
        return self._integrations.get(agent_id)
