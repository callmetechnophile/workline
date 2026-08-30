"""
Pydantic data contracts and schemas for EngineeringCopilotAgent (Agent #15).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


UserIntentLiteral = Literal[
    "PROJECT_STATUS",
    "NEXT_ACTION",
    "PROJECT_SUMMARY",
    "REQUIREMENT_QUERY",
    "REQUIREMENT_TRACE",
    "ARCHITECTURE_QUERY",
    "ARCHITECTURE_TRACE",
    "COMPONENT_QUERY",
    "COMPONENT_IMPACT",
    "BOM_QUERY",
    "BOM_COMPARISON",
    "PROCUREMENT_QUERY",
    "SUPPLIER_QUERY",
    "RESEARCH_QUERY",
    "DECISION_QUERY",
    "DECISION_EXPLANATION",
    "IMPLEMENTATION_QUERY",
    "EXECUTION_QUERY",
    "QA_QUERY",
    "TEST_QUERY",
    "FAILURE_QUERY",
    "RISK_QUERY",
    "TIMELINE_QUERY",
    "CHANGE_IMPACT",
    "VERSION_COMPARISON",
    "TRACEABILITY_QUERY",
    "PROJECT_HEALTH",
    "DOCUMENTATION_REQUEST",
    "ACTION_REQUEST",
    "HUMAN_APPROVAL_REQUEST",
    "UNKNOWN",
]


class EvidenceObject(BaseModel):
    """Grounded proof artifact supporting factual engineering answers (Section 14)."""

    evidence_id: str
    source_type: Literal[
        "requirement",
        "research",
        "decision",
        "architecture",
        "bom",
        "execution",
        "test",
        "validation",
        "qa",
        "blocker",
    ]
    source_id: str
    relationship: str = "supports"
    relevance: str = "Direct reference from verified SurrealDB graph."
    confidence: Optional[float] = 1.0


class ActionProposal(BaseModel):
    """Proposal for privileged or workflow actions routed to Agent #14 (Sections 37 & 80)."""

    proposal_id: str
    project_id: str
    requested_action: str
    target_agent: str
    reason: str
    affected_objects: List[str] = Field(default_factory=list)
    requires_validation: bool = True
    requires_authorization: bool = True
    requires_human_approval: bool = False
    status: Literal["pending", "approved", "rejected"] = "pending"


class CopilotInput(BaseModel):
    """Input query request for EngineeringCopilotAgent (Section 5)."""

    message: str
    project_id: str
    conversation_id: str = "conv_001"
    user_id: str = "user_001"
    team_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    execution_context: Dict[str, Any] = Field(default_factory=dict)
    output_dir: Optional[str] = None


class ComparisonResult(BaseModel):
    """Diff result for BOM, architecture, or requirements version comparisons (Sections 23 & 33)."""

    comparison_type: str
    version_a: str
    version_b: str
    added: List[str] = Field(default_factory=list)
    removed: List[str] = Field(default_factory=list)
    changed: List[str] = Field(default_factory=list)
    cost_difference: Optional[float] = None
    revalidation_required: bool = False


class CopilotResponse(BaseModel):
    """Structured response object returned by EngineeringCopilotAgent (Section 79)."""

    response_id: str
    project_id: str
    conversation_id: str
    intent: UserIntentLiteral
    answer: str
    evidence: List[EvidenceObject] = Field(default_factory=list)
    affected_objects: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    action_proposal: Optional[ActionProposal] = None
    human_approval_required: bool = False
    authorization_required: bool = False
    warnings: List[str] = Field(default_factory=list)
    confidence: Optional[float] = 1.0
    exported_files: List[str] = Field(default_factory=list)
