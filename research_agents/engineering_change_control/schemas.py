"""
Pydantic data contracts and schemas for EngineeringChangeControlAgent (Agent #16).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


ChangeTypeLiteral = Literal[
    "REQUIREMENT_CHANGE",
    "ARCHITECTURE_CHANGE",
    "INTERFACE_CHANGE",
    "COMPONENT_CHANGE",
    "BOM_CHANGE",
    "PROCUREMENT_CHANGE",
    "SUPPLIER_CHANGE",
    "IMPLEMENTATION_CHANGE",
    "TEST_CHANGE",
    "VALIDATION_CHANGE",
    "CONFIGURATION_CHANGE",
    "DOCUMENTATION_CHANGE",
    "PROJECT_METADATA_CHANGE",
]

ChangeSeverityLiteral = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

ChangeStatusLiteral = Literal[
    "DRAFT",
    "ANALYZING",
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "IMPLEMENTING",
    "REVALIDATING",
    "VERIFIED",
    "CANCELLED",
    "BLOCKED",
]

ApprovalTypeLiteral = Literal[
    "NO_APPROVAL",
    "USER_APPROVAL",
    "ENGINEERING_REVIEW",
    "SAFETY_REVIEW",
    "ARCHITECTURE_REVIEW",
    "PROCUREMENT_APPROVAL",
    "EXECUTION_AUTHORIZATION",
]


class ChangeRequest(BaseModel):
    """Formal engineering change request object (Section 6)."""

    change_id: str
    project_id: str
    change_type: ChangeTypeLiteral
    title: str
    description: str
    requested_by: str = "user_001"
    source_artifact: Optional[str] = None
    target_artifact: Optional[str] = None
    severity: ChangeSeverityLiteral = "MEDIUM"
    status: ChangeStatusLiteral = "DRAFT"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ArtifactVersion(BaseModel):
    """Immutable versioned artifact node in the engineering knowledge graph (Section 11)."""

    version_id: str
    artifact_id: str
    version: str
    status: Literal["draft", "validated", "superseded", "invalidated", "archived"] = "draft"
    created_by: str = "user_001"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    change_id: Optional[str] = None
    supersedes: Optional[str] = None


class ImpactObject(BaseModel):
    """Structured direct and indirect dependency impact analysis (Section 16)."""

    change_id: str
    direct_impact: List[str] = Field(default_factory=list)
    indirect_impact: List[str] = Field(default_factory=list)
    stale_artifacts: List[str] = Field(default_factory=list)
    invalidated_artifacts: List[str] = Field(default_factory=list)
    revalidation_required: List[str] = Field(default_factory=list)
    human_approval_required: bool = False
    risk: str = "MEDIUM"
    recommended_action: str = "Proceed with controlled change review."


class RiskObject(BaseModel):
    """Risk evaluation for an engineering change request (Section 29)."""

    change_id: str
    category: str = "functional"
    severity: ChangeSeverityLiteral = "MEDIUM"
    description: str
    affected_artifacts: List[str] = Field(default_factory=list)
    mitigation: str
    confidence: Optional[float] = 1.0


class ApprovalObject(BaseModel):
    """Auditable approval object for human or engineering reviews (Section 33)."""

    approval_id: str
    change_id: str
    approval_type: ApprovalTypeLiteral = "USER_APPROVAL"
    requested_from: str = "engineering_lead"
    approved_by: Optional[str] = None
    reason: str
    status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None


class ChangePlan(BaseModel):
    """Execution and revalidation plan for approved changes (Section 38)."""

    change_plan_id: str
    change_id: str
    steps: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    revalidation_steps: List[str] = Field(default_factory=list)
    qa_steps: List[str] = Field(default_factory=list)
    required_authorization: List[str] = Field(default_factory=list)
    required_approvals: List[str] = Field(default_factory=list)


class ChangeConflict(BaseModel):
    """Detection of concurrent or conflicting changes on an artifact (Section 66)."""

    conflict_id: str
    change_a: str
    change_b: str
    artifact: str
    description: str
    severity: ChangeSeverityLiteral = "HIGH"
    resolution_required: bool = True


class RollbackObject(BaseModel):
    """History-preserving forward rollback record (Section 70)."""

    rollback_id: str
    change_id: str
    target_version: str
    new_version: str
    reason: str
    approved_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ChangeControlInput(BaseModel):
    """Input payload for EngineeringChangeControlAgent."""

    project_id: str
    change_type: ChangeTypeLiteral
    title: str
    description: str
    target_artifact: Optional[str] = None
    user_id: str = "user_001"
    team_id: Optional[str] = None
    output_dir: Optional[str] = None


class ChangeControlOutput(BaseModel):
    """Output payload returned by EngineeringChangeControlAgent."""

    change_request: ChangeRequest
    impact: ImpactObject
    risks: List[RiskObject] = Field(default_factory=list)
    approval: Optional[ApprovalObject] = None
    change_plan: Optional[ChangePlan] = None
    report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
