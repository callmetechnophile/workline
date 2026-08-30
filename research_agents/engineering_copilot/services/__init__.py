"""Services package for EngineeringCopilotAgent."""

from research_agents.engineering_copilot.services.action_proposal_mgr import ActionProposalManager
from research_agents.engineering_copilot.services.answer_engine import AnswerEngine
from research_agents.engineering_copilot.services.comparison_engine import ComparisonEngine
from research_agents.engineering_copilot.services.evidence_collector import EvidenceCollector
from research_agents.engineering_copilot.services.file_exporter import CopilotFileExporter
from research_agents.engineering_copilot.services.lifecycle_client import ProjectLifecycleClient
from research_agents.engineering_copilot.services.query_router import EngineeringQueryRouter

__all__ = [
    "ActionProposalManager",
    "AnswerEngine",
    "ComparisonEngine",
    "EvidenceCollector",
    "CopilotFileExporter",
    "ProjectLifecycleClient",
    "EngineeringQueryRouter",
]
