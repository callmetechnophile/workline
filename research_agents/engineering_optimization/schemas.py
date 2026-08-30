from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

OptimizationStatusLiteral = Literal[
    "PENDING", "RUNNING", "COMPLETE", "INFEASIBLE", "STALE", "INVALIDATED", "ERROR",
]
ConstraintTypeLiteral = Literal["HARD", "SOFT"]
ObjectiveDirectionLiteral = Literal["MINIMIZE", "MAXIMIZE"]


class ObjectiveObject(BaseModel):
    objective_id: str
    name: str
    direction: ObjectiveDirectionLiteral
    unit: str
    weight: float = 1.0
    description: str = ""


class ConstraintObject(BaseModel):
    constraint_id: str
    name: str
    constraint_type: ConstraintTypeLiteral
    expression: str
    limit: float
    unit: str
    description: str = ""
    penalty: Optional[float] = None


class VariableObject(BaseModel):
    variable_id: str
    name: str
    unit: str
    min_value: float
    max_value: float
    step: Optional[float] = None
    current_value: Optional[float] = None
    description: str = ""


class DesignCandidate(BaseModel):
    candidate_id: str
    optimization_id: str
    variable_values: Dict[str, float] = Field(default_factory=dict)
    objective_values: Dict[str, float] = Field(default_factory=dict)
    constraint_violations: Dict[str, float] = Field(default_factory=dict)
    hard_constraint_violations: List[str] = Field(default_factory=list)
    feasible: bool = True
    simulation_id: Optional[str] = None
    compliance_status: str = "UNKNOWN"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ParetoPoint(BaseModel):
    candidate_id: str
    objective_values: Dict[str, float]
    dominance_rank: int = 0


class ParetoFrontierObject(BaseModel):
    frontier_id: str
    optimization_id: str
    points: List[ParetoPoint] = Field(default_factory=list)
    dominated_count: int = 0
    infeasible_count: int = 0
    method: str = "non_dominated_sorting"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RobustnessObject(BaseModel):
    candidate_id: str
    sensitivity_map: Dict[str, float] = Field(default_factory=dict)
    worst_case_objective: Dict[str, float] = Field(default_factory=dict)
    robustness_score: float = 0.0


class CandidateSelection(BaseModel):
    selection_id: str
    optimization_id: str
    candidate_id: str
    selected_by: str
    rationale: str
    selected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OptimizationDecision(BaseModel):
    decision_id: str
    optimization_id: str
    candidate_id: str
    selected_by: str
    rationale: str
    change_request_id: Optional[str] = None
    decided_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OptimizationObject(BaseModel):
    optimization_id: str
    project_id: str
    name: str
    description: str
    objectives: List[ObjectiveObject] = Field(default_factory=list)
    variables: List[VariableObject] = Field(default_factory=list)
    constraints: List[ConstraintObject] = Field(default_factory=list)
    candidate_ids: List[str] = Field(default_factory=list)
    pareto_frontier_id: Optional[str] = None
    decision_id: Optional[str] = None
    status: OptimizationStatusLiteral = "PENDING"
    bom_version: str = "v1.0.0"
    architecture_version: str = "v1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OptimizationResult(BaseModel):
    optimization_result_id: str
    optimization_id: str
    candidates: List[DesignCandidate] = Field(default_factory=list)
    pareto_frontier: Optional[ParetoFrontierObject] = None
    recommended_candidate_id: Optional[str] = None
    recommendation_rationale: str = ""
    robustness: List[RobustnessObject] = Field(default_factory=list)
    report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OptimizationInput(BaseModel):
    project_id: str
    user_id: str = "user_001"
    team_id: Optional[str] = None
    optimization_name: Optional[str] = None
    output_dir: Optional[str] = None


class OptimizationOutput(BaseModel):
    optimization: OptimizationObject
    candidates: List[DesignCandidate] = Field(default_factory=list)
    pareto_frontier: Optional[ParetoFrontierObject] = None
    decision: Optional[OptimizationDecision] = None
    report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
