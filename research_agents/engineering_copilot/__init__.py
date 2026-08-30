"""
EngineeringCopilotAgent package (Agent #15 of WorkflowGuide AI).
"""

from research_agents.engineering_copilot.agent import EngineeringCopilotAgent
from research_agents.engineering_copilot.config import CopilotConfig, copilot_config
from research_agents.engineering_copilot.schemas import (
    ActionProposal,
    ComparisonResult,
    CopilotInput,
    CopilotResponse,
    EvidenceObject,
    UserIntentLiteral,
)

__all__ = [
    "EngineeringCopilotAgent",
    "CopilotConfig",
    "copilot_config",
    "UserIntentLiteral",
    "EvidenceObject",
    "ActionProposal",
    "CopilotInput",
    "ComparisonResult",
    "CopilotResponse",
]
