"""
VerificationQAAgent package (Agent #12 of WorkflowGuide AI).
"""

from research_agents.verification_qa_agent.agent import VerificationQAAgent
from research_agents.verification_qa_agent.config import QAConfig, qa_config
from research_agents.verification_qa_agent.schemas import (
    ChangeObject,
    ConformanceResult,
    CorrectionReportItem,
    EvidenceObject,
    FinalQAVerdict,
    RequirementVerificationItem,
    SecurityFinding,
    TaskVerificationObject,
    TestResultObject,
    VerificationExecutionContext,
    VerificationQAAgentInput,
    VerificationQAAgentOutput,
    VerificationTraceabilityItem,
)

__all__ = [
    "VerificationQAAgent",
    "QAConfig",
    "qa_config",
    "ChangeObject",
    "TaskVerificationObject",
    "RequirementVerificationItem",
    "EvidenceObject",
    "TestResultObject",
    "SecurityFinding",
    "ConformanceResult",
    "CorrectionReportItem",
    "VerificationTraceabilityItem",
    "FinalQAVerdict",
    "VerificationExecutionContext",
    "VerificationQAAgentInput",
    "VerificationQAAgentOutput",
]
