"""
Agent capability registry for WorkflowGuide AI (Section 14).
Registers Agents #1–#13 with capabilities, required authorization, and execution levels.
"""

from typing import Dict, List, Optional
from research_agents.project_lifecycle_orchestrator.schemas import AgentDescriptor


class AgentRegistry:
    """Central registry of all specialized engineering agents in the pipeline."""

    def __init__(self):
        self._agents: Dict[str, AgentDescriptor] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        agents = [
            AgentDescriptor(
                agent_id="Agent #1",
                agent_name="ResearchPaperAgent",
                capabilities=["research.papers", "research.arxiv", "research.freephdlabor"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #2",
                agent_name="WebResearchAgent",
                capabilities=["research.web", "research.tavily", "research.anakin"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #3",
                agent_name="DocumentProcessingAgent",
                capabilities=["document.parse", "document.extract_facts", "document.extract_entities"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #4",
                agent_name="DeepResearchAgent",
                capabilities=["research.synthesize", "research.cross_reason"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #5",
                agent_name="EngineeringSynthesisAgent",
                capabilities=["synthesis.requirements", "synthesis.decisions", "synthesis.tradeoffs"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #6",
                agent_name="EngineeringArchitectureAgent",
                capabilities=["architecture.design", "architecture.subsystems", "architecture.interfaces"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #7",
                agent_name="ComponentPlanningAgent",
                capabilities=["bom.plan", "bom.select_components"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #8",
                agent_name="BOMOptimizationAgent",
                capabilities=["bom.optimize", "procurement.landed_cost", "logistics.transit"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #9",
                agent_name="EngineeringValidationAgent",
                capabilities=["validation.design_rules", "validation.electrical", "validation.power"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #10",
                agent_name="ProjectExecutionAgent",
                capabilities=["planning.work_packages", "planning.tasks", "planning.dependencies"],
                execution_level="planning",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #11",
                agent_name="EngineeringExecutionAgent",
                capabilities=["execution.scoped", "execution.filesystem", "execution.tools"],
                required_authorization=["filesystem.write", "shell", "test_runner"],
                execution_level="isolated_execution",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #12",
                agent_name="VerificationQAAgent",
                capabilities=["qa.verify", "qa.pytest", "qa.security_scan", "qa.conformance"],
                required_authorization=["test_runner", "pytest", "security_scan"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #13",
                agent_name="EngineeringKnowledgeGraphAgent",
                capabilities=["graph.query", "graph.trace", "graph.impact", "graph.state", "graph.ingest"],
                required_authorization=["graph.read", "graph.insert", "graph.update"],
                execution_level="read_only",
                status="available",
            ),
        ]
        for ag in agents:
            self._agents[ag.agent_name] = ag
            self._agents[ag.agent_id] = ag

    def get_agent(self, identifier: str) -> Optional[AgentDescriptor]:
        return self._agents.get(identifier)

    def list_agents(self) -> List[AgentDescriptor]:
        unique = {a.agent_name: a for a in self._agents.values()}
        return list(unique.values())

    def is_agent_ready(self, agent_name: str, required_auth: Optional[List[str]] = None) -> bool:
        ag = self.get_agent(agent_name)
        if not ag or ag.status != "available":
            return False
        return True
