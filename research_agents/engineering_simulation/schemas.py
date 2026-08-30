"""
Pydantic data contracts and schemas for EngineeringSimulationAgent (Agent #19).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


SimulationDomainLiteral = Literal[
    "ELECTRICAL",
    "ELECTRONICS",
    "POWER",
    "THERMAL",
    "SIGNAL",
    "COMMUNICATION",
    "CONTROL",
    "MECHANICAL",
    "FLUID",
    "STRUCTURAL",
    "SOFTWARE",
    "PERFORMANCE",
    "SYSTEM",
    "NETWORK",
    "AI_ML",
]

SimulationStatusLiteral = Literal[
    "PLANNED",
    "READY",
    "RUNNING",
    "PASS",
    "FAIL",
    "ERROR",
    "BLOCKED",
    "INCONCLUSIVE",
    "STALE",
    "INVALIDATED",
]

ModelStatusLiteral = Literal[
    "DRAFT",
    "READY",
    "CALIBRATED",
    "VALIDATED",
    "STALE",
    "INVALIDATED",
]

TwinStatusLiteral = Literal[
    "DRAFT",
    "CALIBRATED",
    "VALIDATED",
    "STALE",
    "INVALIDATED",
]


class ModelAssumption(BaseModel):
    """Explicit engineering assumption recorded in a simulation model (Section 14)."""

    assumption_id: str
    model_id: str
    description: str
    source: str = "ENGINEERING_EQUATION"
    impact: str = "Medium"
    confidence: Optional[float] = 0.95


class ModelObject(BaseModel):
    """Computational simulation model representation (Section 12)."""

    model_id: str
    twin_id: str
    domain: SimulationDomainLiteral = "POWER"
    description: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    assumptions: List[ModelAssumption] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    backend: str = "python_numerical"
    backend_version: str = "1.0.0"
    status: ModelStatusLiteral = "READY"


class DigitalTwin(BaseModel):
    """Digital twin representation of a physical or subsystem design (Section 11)."""

    twin_id: str
    project_id: str
    name: str
    version: str = "v1.0.0"
    status: TwinStatusLiteral = "DRAFT"
    architecture_version: str = "v1.0.0"
    bom_version: str = "v1.0.0"
    model_ids: List[str] = Field(default_factory=list)
    parameter_set_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SimulationObject(BaseModel):
    """Simulation run specification (Section 20)."""

    simulation_id: str
    project_id: str
    model_id: str
    backend: str = "python_numerical"
    backend_version: str = "1.0.0"
    status: SimulationStatusLiteral = "PLANNED"
    inputs: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    executed_at: Optional[str] = None


class SimulationResult(BaseModel):
    """Execution output and performance metrics from a simulation run (Section 27)."""

    simulation_result_id: str
    simulation_id: str
    status: Literal["PASS", "FAIL", "ERROR", "INCONCLUSIVE"]
    outputs: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    plots: List[str] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    hash: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ScenarioObject(BaseModel):
    """Isolated what-if analysis branch (Section 32)."""

    scenario_id: str
    project_id: str
    base_version: str = "v1.0.0"
    name: str
    description: str
    changes: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    simulation_ids: List[str] = Field(default_factory=list)
    status: Literal["DRAFT", "RUNNING", "COMPLETE"] = "DRAFT"


class ParameterSweepObject(BaseModel):
    """Parameter sweep execution artifact (Section 35)."""

    sweep_id: str
    simulation_id: str
    parameter_name: str
    range_min: float
    range_max: float
    step: float
    samples: int
    method: str = "grid_search"
    results: List[Dict[str, Any]] = Field(default_factory=list)


class CalibrationObject(BaseModel):
    """Model calibration against physical measurement telemetry (Section 51)."""

    calibration_id: str
    twin_id: str
    measurement_ids: List[str] = Field(default_factory=list)
    parameters_before: Dict[str, Any] = Field(default_factory=dict)
    parameters_after: Dict[str, Any] = Field(default_factory=dict)
    method: str = "least_squares"
    error_before: Optional[float] = None
    error_after: Optional[float] = None
    status: Literal["DRAFT", "COMPLETE"] = "COMPLETE"


class SimulationInput(BaseModel):
    """Input payload for EngineeringSimulationAgent."""

    project_id: str
    user_id: str = "user_001"
    team_id: Optional[str] = None
    target_model: Optional[str] = None
    what_if_scenario: Optional[str] = None
    output_dir: Optional[str] = None


class SimulationOutput(BaseModel):
    """Output payload returned by EngineeringSimulationAgent."""

    twin: DigitalTwin
    models: List[ModelObject] = Field(default_factory=list)
    simulations: List[SimulationObject] = Field(default_factory=list)
    results: List[SimulationResult] = Field(default_factory=list)
    scenarios: List[ScenarioObject] = Field(default_factory=list)
    sweeps: List[ParameterSweepObject] = Field(default_factory=list)
    report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
