"""External agent registry, trust scoring, and discovery caching."""

import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus,
    CapabilityType,
    RiskLevel,
)


class ExternalAgent(BaseModel):
    """Manifest of an external agent registered with Workline."""
    agent_id: str = Field(..., description="Unique slug identifier (e.g. 'ThermalSolver')")
    name: str = Field(..., description="Human-readable agent display name")
    description: str = Field(..., description="Description of agent features and domain")
    provider: str = Field(default="External Provider", description="Provider / Organization")
    protocol: str = Field(default="BINDU_A2A", description="Communication protocol: BINDU_A2A, CORSAIR, MOCK")
    endpoint: Optional[str] = Field(default=None, description="Network URL or service endpoint")
    version: str = Field(default="1.0.0", description="Agent implementation version")
    status: AgentStatus = Field(default=AgentStatus.AVAILABLE, description="Current availability status")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Supported capabilities")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: Optional[str] = None


class AgentTrustRecord(BaseModel):
    """Historical reliability and trust score calculation for an agent."""
    agent_id: str
    successful_tasks: int = 0
    failed_tasks: int = 0
    timeouts: int = 0
    validation_failures: int = 0
    last_used: Optional[str] = None
    trust_score: float = Field(default=1.0, description="Normalized score 0.0 - 1.0 based on historical track record")

    def recompute_score(self) -> float:
        """Recompute trust score based on weighted performance signals."""
        total = self.successful_tasks + self.failed_tasks + self.timeouts + self.validation_failures
        if total == 0:
            self.trust_score = 1.0
            return self.trust_score
        
        # Penalize timeouts and validation failures more heavily than transient failures
        penalized_points = (self.failed_tasks * 1.0) + (self.timeouts * 2.0) + (self.validation_failures * 3.0)
        success_points = self.successful_tasks * 2.0
        total_possible = total * 2.0

        score = max(0.1, min(1.0, (success_points - penalized_points + total_possible) / (2.0 * total_possible)))
        self.trust_score = round(score, 3)
        return self.trust_score


class AgentRegistry:
    """Protocol-independent thread-safe registry for external agents and capabilities."""

    def __init__(self, cache_ttl_seconds: float = 300.0):
        self._lock = threading.RLock()
        self._agents: Dict[str, ExternalAgent] = {}
        self._trust_records: Dict[str, AgentTrustRecord] = {}
        self._discovery_cache: Optional[List[ExternalAgent]] = None
        self._discovery_cache_timestamp: float = 0.0
        self._cache_ttl: float = cache_ttl_seconds
        self._initialize_default_agents()

    def _initialize_default_agents(self) -> None:
        """Seed default known agents and mock implementations."""
        mock_thermal = ExternalAgent(
            agent_id="ThermalSolver",
            name="ThermalSolver",
            description="High-precision finite element and PINN thermal solver for electronic PCBs and power stages.",
            provider="Workline Physics Lab",
            protocol="BINDU_A2A",
            endpoint="bindu://local/thermal-solver",
            version="2.1.0",
            status=AgentStatus.AVAILABLE,
            capabilities=[
                AgentCapability(
                    capability_id="thermal_simulation",
                    agent_id="ThermalSolver",
                    name="Thermal Simulation",
                    description="Simulates steady-state temperature distribution and thermal dissipation on PCB boards.",
                    capability_type=CapabilityType.THERMAL_ANALYSIS,
                    risk_level=RiskLevel.MEDIUM,
                    estimated_cost=0.05,
                    input_schema={
                        "type": "object",
                        "required": ["board_width", "board_height", "components"],
                        "properties": {
                            "board_width": {"type": "number"},
                            "board_height": {"type": "number"},
                            "ambient_temp": {"type": "number"},
                            "components": {"type": "array"},
                        },
                    },
                    output_schema={
                        "type": "object",
                        "required": ["max_temperature", "hotspots", "status"],
                        "properties": {
                            "max_temperature": {"type": "number"},
                            "hotspots": {"type": "array"},
                            "status": {"type": "string"},
                            "recommendations": {"type": "array"},
                        },
                    },
                ),
                AgentCapability(
                    capability_id="thermal_optimization",
                    agent_id="ThermalSolver",
                    name="Thermal Placement Optimization",
                    description="Optimizes component placement to eliminate localized hotspots.",
                    capability_type=CapabilityType.OPTIMIZATION,
                    risk_level=RiskLevel.HIGH,
                    estimated_cost=0.15,
                ),
            ],
        )

        bindu_code_review = ExternalAgent(
            agent_id="CodeReviewAgent",
            name="CodeReviewAgent",
            description="Static analysis, security vulnerability scanning, and MISRA/Embedded C linting.",
            provider="Bindu Agent Network",
            protocol="BINDU_A2A",
            endpoint="bindu://network/code-review",
            version="1.4.0",
            status=AgentStatus.AVAILABLE,
            capabilities=[
                AgentCapability(
                    capability_id="code_review",
                    agent_id="CodeReviewAgent",
                    name="Firmware & Driver Code Review",
                    description="Performs automated security audit and MISRA-C compliance inspection on source files.",
                    capability_type=CapabilityType.CODE_REVIEW,
                    risk_level=RiskLevel.LOW,
                    estimated_cost=0.01,
                    input_schema={"type": "object", "required": ["code"]},
                    output_schema={"type": "object", "required": ["issues", "status"]},
                )
            ],
        )

        corsair_researcher = ExternalAgent(
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

        for ag in [mock_thermal, bindu_code_review, corsair_researcher]:
            self._agents[ag.agent_id] = ag
            self._trust_records[ag.agent_id] = AgentTrustRecord(agent_id=ag.agent_id)

    def register_agent(self, agent: ExternalAgent) -> ExternalAgent:
        """Register or update an external agent manifest."""
        with self._lock:
            agent.updated_at = datetime.now(timezone.utc).isoformat()
            self._agents[agent.agent_id] = agent
            if agent.agent_id not in self._trust_records:
                self._trust_records[agent.agent_id] = AgentTrustRecord(agent_id=agent.agent_id)
            self._invalidate_discovery_cache()
            return agent

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the platform."""
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                self._trust_records.pop(agent_id, None)
                self._invalidate_discovery_cache()
                return True
            return False

    def get_agent(self, agent_id: str) -> Optional[ExternalAgent]:
        """Fetch agent manifest by ID."""
        with self._lock:
            return self._agents.get(agent_id)

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[ExternalAgent]:
        """List registered agents, optionally filtered by status."""
        with self._lock:
            if status is None:
                return list(self._agents.values())
            return [a for a in self._agents.values() if a.status == status]

    def discover_agents(
        self,
        protocol: Optional[str] = None,
        capability_type: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[ExternalAgent]:
        """Discover external agents with controlled caching."""
        with self._lock:
            now = time.time()
            if force_refresh or self._discovery_cache is None or (now - self._discovery_cache_timestamp > self._cache_ttl):
                # Refresh cache
                self._discovery_cache = list(self._agents.values())
                self._discovery_cache_timestamp = now

            results = self._discovery_cache
            if protocol:
                results = [a for a in results if a.protocol.upper() == protocol.upper()]
            if capability_type:
                cap_upper = capability_type.upper()
                results = [
                    a for a in results
                    if any(c.capability_type.value == cap_upper or c.capability_id == capability_type for c in a.capabilities)
                ]
            return results

    def get_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """Fetch all declared capabilities for a given agent."""
        with self._lock:
            agent = self._agents.get(agent_id)
            return agent.capabilities if agent else []

    def update_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update live status for an agent."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].status = status
                self._agents[agent_id].last_seen = datetime.now(timezone.utc).isoformat()
                self._invalidate_discovery_cache()

    def record_task_outcome(self, agent_id: str, outcome: str) -> None:
        """Record task outcome to update historical trust record."""
        with self._lock:
            trust = self._trust_records.setdefault(agent_id, AgentTrustRecord(agent_id=agent_id))
            trust.last_used = datetime.now(timezone.utc).isoformat()
            if outcome == "SUCCESS":
                trust.successful_tasks += 1
            elif outcome == "FAILURE":
                trust.failed_tasks += 1
            elif outcome == "TIMEOUT":
                trust.timeouts += 1
            elif outcome == "VALIDATION_FAILURE":
                trust.validation_failures += 1
            trust.recompute_score()

    def get_trust_record(self, agent_id: str) -> AgentTrustRecord:
        """Retrieve trust metrics for an agent."""
        with self._lock:
            return self._trust_records.get(agent_id, AgentTrustRecord(agent_id=agent_id))

    def _invalidate_discovery_cache(self) -> None:
        self._discovery_cache = None
        self._discovery_cache_timestamp = 0.0


# Global singleton agent registry
agent_registry = AgentRegistry()
