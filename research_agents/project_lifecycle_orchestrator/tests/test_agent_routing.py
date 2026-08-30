"""
Unit tests for agent capability registry and routing (Sections 13–15).
"""

from research_agents.project_lifecycle_orchestrator.registry.agent_registry import AgentRegistry


def test_agent_registry_and_routing():
    registry = AgentRegistry()

    # Check Agents #1 through #13 exist
    assert registry.get_agent("ResearchPaperAgent") is not None
    assert registry.get_agent("WebResearchAgent") is not None
    assert registry.get_agent("DocumentProcessingAgent") is not None
    assert registry.get_agent("DeepResearchAgent") is not None
    assert registry.get_agent("EngineeringSynthesisAgent") is not None
    assert registry.get_agent("EngineeringArchitectureAgent") is not None
    assert registry.get_agent("ComponentPlanningAgent") is not None
    assert registry.get_agent("BOMOptimizationAgent") is not None
    assert registry.get_agent("EngineeringValidationAgent") is not None
    assert registry.get_agent("ProjectExecutionAgent") is not None
    assert registry.get_agent("EngineeringExecutionAgent") is not None
    assert registry.get_agent("VerificationQAAgent") is not None
    assert registry.get_agent("EngineeringKnowledgeGraphAgent") is not None

    # Readiness check
    assert registry.is_agent_ready("EngineeringExecutionAgent") is True
