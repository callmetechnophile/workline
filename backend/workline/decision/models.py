"""Data models and enums for the Engineering Design Decision Engine."""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    RECOMMENDED = "RECOMMENDED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"


class DecisionType(str, Enum):
    COMPONENT_SELECTION = "COMPONENT_SELECTION"
    ARCHITECTURE_SELECTION = "ARCHITECTURE_SELECTION"
    PROTOCOL_SELECTION = "PROTOCOL_SELECTION"
    MATERIAL_SELECTION = "MATERIAL_SELECTION"
    TOOL_SELECTION = "TOOL_SELECTION"
    MODEL_SELECTION = "MODEL_SELECTION"
    PCB_OPTION = "PCB_OPTION"
    POWER_ARCHITECTURE = "POWER_ARCHITECTURE"
    SOFTWARE_ARCHITECTURE = "SOFTWARE_ARCHITECTURE"
    PROCUREMENT_SELECTION = "PROCUREMENT_SELECTION"
    OTHER = "OTHER"


class CriterionCategory(str, Enum):
    TECHNICAL_FIT = "TECHNICAL_FIT"
    POWER = "POWER"
    PERFORMANCE = "PERFORMANCE"
    THERMAL = "THERMAL"
    SIZE = "SIZE"
    WEIGHT = "WEIGHT"
    RELIABILITY = "RELIABILITY"
    AVAILABILITY = "AVAILABILITY"
    COST = "COST"
    LEAD_TIME = "LEAD_TIME"
    MANUFACTURER = "MANUFACTURER"
    PACKAGE = "PACKAGE"
    EFFICIENCY = "EFFICIENCY"
    COMPLEXITY = "COMPLEXITY"
    RISK = "RISK"
    DOCUMENTATION = "DOCUMENTATION"
    MAINTAINABILITY = "MAINTAINABILITY"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    LIFECYCLE = "LIFECYCLE"


class CriterionDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"
    TARGET = "TARGET"
    PREFERENCE = "PREFERENCE"


class DecisionCriterion(BaseModel):
    criterion_id: str
    name: str
    category: CriterionCategory = CriterionCategory.TECHNICAL_FIT
    weight: float = 0.20
    direction: CriterionDirection = CriterionDirection.MAXIMIZE
    mandatory: bool = False
    target_value: Optional[float] = None
    description: Optional[str] = None


class DecisionCandidate(BaseModel):
    candidate_id: str
    entity_id: str
    name: str
    eligibility_status: str = "ELIGIBLE"  # ELIGIBLE, INELIGIBLE, UNKNOWN, CONFLICTED
    score: float = 0.0
    criterion_scores: Dict[str, float] = Field(default_factory=dict)
    tradeoffs: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class DecisionTradeoff(BaseModel):
    candidate_a: str
    candidate_b: str
    criterion: str
    advantage_candidate: str
    disadvantage_candidate: str
    score_delta: float


class SensitivityAnalysis(BaseModel):
    criterion_id: str
    original_weight: float
    tested_weight: float
    original_winner: str
    new_winner: str
    is_ranking_changed: bool


class EngineeringDecision(BaseModel):
    decision_id: str
    project_id: str
    team_id: str = "default_team"
    title: str
    description: str
    status: DecisionStatus = DecisionStatus.DRAFT
    decision_type: DecisionType = DecisionType.COMPONENT_SELECTION
    selected_candidate: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)
    criteria: List[DecisionCriterion] = Field(default_factory=list)
    recommendation: Optional[str] = None
    rationale: Optional[str] = None
    confidence: float = 0.90
    stability: str = "ROBUST"  # ROBUST, MODERATELY_STABLE, SENSITIVE, UNSTABLE
    version: int = 1
    superseded_by: Optional[str] = None
    created_by: str = "engineer"
    approved_by: Optional[str] = None
    approved_at: Optional[float] = None
    rule_version: str = "electrical_rules_v1"
    knowledge_version: str = "1.0.0"
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
