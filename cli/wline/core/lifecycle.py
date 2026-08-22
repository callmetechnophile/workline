"""Engineering lifecycle state and stage definitions for Workline."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    """Lifecycle stage status."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# The canonical 36 engineering lifecycle stages in exact order
ORDERED_LIFECYCLE_STAGES = [
    ("requirements", "PROJECT REQUIREMENTS"),
    ("problem_definition", "PROBLEM DEFINITION"),
    ("operating_limits", "OPERATING LIMITS"),
    ("system_architecture", "SYSTEM ARCHITECTURE"),
    ("subsystem_decomposition", "SUBSYSTEM DECOMPOSITION"),
    ("component_selection", "COMPONENT SELECTION"),
    ("datasheet_validation", "DATASHEET VALIDATION"),
    ("power_architecture", "POWER ARCHITECTURE"),
    ("interface_mapping", "GPIO / INTERFACE MAPPING"),
    ("schematic", "SCHEMATIC"),
    ("bom", "BOM"),
    ("firmware_architecture", "FIRMWARE ARCHITECTURE"),
    ("driver_implementation", "DRIVER IMPLEMENTATION"),
    ("unit_testing", "UNIT TESTING"),
    ("power_on_validation", "POWER-ON VALIDATION"),
    ("peripheral_bring_up", "PERIPHERAL BRING-UP"),
    ("sensor_calibration", "SENSOR CALIBRATION"),
    ("actuator_validation", "ACTUATOR VALIDATION"),
    ("control_algorithm", "CONTROL ALGORITHM"),
    ("safety_logic", "SAFETY LOGIC"),
    ("integration_test", "INTEGRATION TEST"),
    ("failure_injection_test", "FAILURE-INJECTION TEST"),
    ("simulated_data_pipeline", "SIMULATED DATA PIPELINE"),
    ("telemetry_protocol", "TELEMETRY PROTOCOL"),
    ("backend", "BACKEND"),
    ("database", "DATABASE"),
    ("dashboard", "DASHBOARD"),
    ("dataset_generation", "DATASET GENERATION"),
    ("data_cleaning", "DATA CLEANING"),
    ("feature_engineering", "FEATURE ENGINEERING"),
    ("time_series_model", "TIME-SERIES MODEL"),
    ("future_expectancy", "FUTURE EXPECTANCY"),
    ("performance_analysis", "PERFORMANCE ANALYSIS"),
    ("documentation", "DOCUMENTATION"),
    ("final_validation", "FINAL VALIDATION"),
    ("release", "RELEASE"),
]


class StageState(BaseModel):
    """State representation for a single lifecycle stage."""
    id: str
    name: str
    order: int
    status: StageStatus = StageStatus.NOT_STARTED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)


class ProjectLifecycle(BaseModel):
    """Lifecycle tracking model for a Workline project."""
    current_stage: str = "requirements"
    status: str = "not_started"
    stages: Dict[str, StageState] = Field(default_factory=dict)


def create_default_lifecycle() -> ProjectLifecycle:
    """Create a pristine 36-stage lifecycle model initialized to NOT_STARTED."""
    stages: Dict[str, StageState] = {}
    prev_id: Optional[str] = None

    for order, (stage_id, stage_name) in enumerate(ORDERED_LIFECYCLE_STAGES, start=1):
        deps = [prev_id] if prev_id else []
        stages[stage_id] = StageState(
            id=stage_id,
            name=stage_name,
            order=order,
            status=StageStatus.NOT_STARTED,
            started_at=None,
            completed_at=None,
            dependencies=deps,
        )
        prev_id = stage_id

    return ProjectLifecycle(
        current_stage="requirements",
        status="not_started",
        stages=stages,
    )


def calculate_progress(lifecycle: ProjectLifecycle) -> float:
    """
    Calculate the project completion percentage based on actual stage statuses.
    Completed = 1.0 weight, In Progress = 0.5 weight.
    """
    if not lifecycle.stages:
        return 0.0

    total = len(lifecycle.stages)
    completed = 0.0

    for stage in lifecycle.stages.values():
        if stage.status == StageStatus.COMPLETED:
            completed += 1.0
        elif stage.status == StageStatus.IN_PROGRESS:
            completed += 0.5

    return round((completed / total) * 100.0, 1)
