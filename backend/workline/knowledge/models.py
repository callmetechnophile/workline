"""Core data models and enums for Engineering Knowledge and Decision Memory."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActorType(str, Enum):
    """Origin entity for knowledge entries."""
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class Actor(BaseModel):
    """Detailed provenance metadata of the creator or modifier."""
    actor_type: ActorType = ActorType.HUMAN
    actor_id: str = "user"
    name: Optional[str] = None


class DecisionCategory(str, Enum):
    """Technical domains for engineering decisions."""
    SYSTEM_ARCHITECTURE = "SYSTEM_ARCHITECTURE"
    COMPONENT_SELECTION = "COMPONENT_SELECTION"
    POWER_ARCHITECTURE = "POWER_ARCHITECTURE"
    INTERFACE = "INTERFACE"
    FIRMWARE = "FIRMWARE"
    SOFTWARE = "SOFTWARE"
    AI_MODEL = "AI_MODEL"
    DATASET = "DATASET"
    PCB = "PCB"
    THERMAL = "THERMAL"
    SIGNAL_INTEGRITY = "SIGNAL_INTEGRITY"
    PROCUREMENT = "PROCUREMENT"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    MANUFACTURING = "MANUFACTURING"
    TESTING = "TESTING"
    RELEASE = "RELEASE"


class DecisionStatus(str, Enum):
    """Lifecycle status of an engineering decision."""
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    IMPLEMENTED = "IMPLEMENTED"
    VALIDATED = "VALIDATED"


class EvidenceSourceType(str, Enum):
    """Origin of supporting engineering evidence."""
    DATASHEET = "DATASHEET"
    RESEARCH = "RESEARCH"
    SIMULATION = "SIMULATION"
    MEASUREMENT = "MEASUREMENT"
    PROCUREMENT = "PROCUREMENT"
    TEST = "TEST"
    USER_REQUIREMENT = "USER_REQUIREMENT"
    GIT_COMMIT = "GIT_COMMIT"
    OTHER = "OTHER"


class DecisionEvidence(BaseModel):
    """Documented evidence backing an engineering decision."""
    evidence_id: str
    decision_id: str
    source_type: EvidenceSourceType = EvidenceSourceType.DATASHEET
    source_id: Optional[str] = None
    title: str
    url: Optional[str] = None
    claim: str
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 1.0


class DecisionAlternative(BaseModel):
    """Evaluated but unselected or rejected technical alternative."""
    alternative_id: str
    decision_id: str
    name: str
    description: str
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)
    rejection_reason: Optional[str] = None


class EngineeringDecision(BaseModel):
    """
    Authoritative engineering decision record.
    Preserves rationale, alternatives, evidence, and versioning provenance.
    """
    decision_id: str
    project_id: str
    title: str
    description: str
    category: DecisionCategory
    status: DecisionStatus = DecisionStatus.PROPOSED
    created_by: Actor
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    problem: str = ""
    rationale: str = ""
    alternatives: List[DecisionAlternative] = Field(default_factory=list)
    selected_option: str
    constraints: List[str] = Field(default_factory=list)
    evidence: List[DecisionEvidence] = Field(default_factory=list)
    confidence: float = 1.0
    
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    git_commit: Optional[str] = None
    project_version: Optional[str] = None
    validation_status: Optional[str] = None
    implemented_objects: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RequirementCategory(str, Enum):
    """Engineering requirement domain categories."""
    FUNCTIONAL = "FUNCTIONAL"
    ELECTRICAL = "ELECTRICAL"
    MECHANICAL = "MECHANICAL"
    THERMAL = "THERMAL"
    PERFORMANCE = "PERFORMANCE"
    SOFTWARE = "SOFTWARE"
    SECURITY = "SECURITY"
    COST = "COST"
    POWER = "POWER"
    TIMING = "TIMING"
    MANUFACTURING = "MANUFACTURING"
    COMPLIANCE = "COMPLIANCE"


class RequirementPriority(str, Enum):
    """Requirement priority classifications."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RequirementStatus(str, Enum):
    """Requirement fulfillment status."""
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    IMPLEMENTED = "IMPLEMENTED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    OBSOLETE = "OBSOLETE"


class EngineeringRequirement(BaseModel):
    """Formal engineering requirement specification."""
    requirement_id: str
    project_id: str
    title: str
    description: str
    category: RequirementCategory
    priority: RequirementPriority = RequirementPriority.HIGH
    value: Optional[str] = None
    unit: Optional[str] = None
    source: str = "USER"
    status: RequirementStatus = RequirementStatus.PROPOSED
    created_by: Actor
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    satisfied_by_decisions: List[str] = Field(default_factory=list)
    implemented_by_objects: List[str] = Field(default_factory=list)
    verified_by_validations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FindingStatus(str, Enum):
    """Lifecycle state of an engineering finding or failure."""
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    WONT_FIX = "WONT_FIX"
    SUPERSEDED = "SUPERSEDED"


class FindingSeverity(str, Enum):
    """Severity classification for engineering findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class EngineeringFinding(BaseModel):
    """Engineering anomaly, validation failure, or inspection finding."""
    finding_id: str
    project_id: str
    title: str
    description: str
    category: str
    severity: FindingSeverity = FindingSeverity.HIGH
    source: str
    source_id: Optional[str] = None
    created_by: Actor
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: FindingStatus = FindingStatus.OPEN
    resolution: Optional[str] = None
    resolved_by_decision_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EngineeringLesson(BaseModel):
    """Distilled engineering lesson learned from findings or design iterations."""
    lesson_id: str
    project_id: str
    title: str
    description: str
    context: str
    cause: str
    impact: str
    recommendation: str
    derived_from_finding_id: Optional[str] = None
    created_by: Actor
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeAuditEventType(str, Enum):
    """Audit events for knowledge operations."""
    DECISION_CREATED = "DECISION_CREATED"
    DECISION_APPROVED = "DECISION_APPROVED"
    DECISION_REJECTED = "DECISION_REJECTED"
    DECISION_SUPERSEDED = "DECISION_SUPERSEDED"
    REQUIREMENT_CREATED = "REQUIREMENT_CREATED"
    REQUIREMENT_UPDATED = "REQUIREMENT_UPDATED"
    REQUIREMENT_VERIFIED = "REQUIREMENT_VERIFIED"
    FINDING_CREATED = "FINDING_CREATED"
    FINDING_RESOLVED = "FINDING_RESOLVED"
    LESSON_CREATED = "LESSON_CREATED"


class KnowledgeAuditEvent(BaseModel):
    """Immutable audit trail record for knowledge and decision operations."""
    event_id: str
    event_type: KnowledgeAuditEventType
    project_id: str
    object_id: str
    actor: Actor
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)
