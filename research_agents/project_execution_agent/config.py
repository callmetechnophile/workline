import os
from typing import List
from pydantic import BaseModel, Field


class ProjectExecutionConfig(BaseModel):
    """Configuration settings for WBS and Implementation Planning (Agent #10)."""

    agent_id: str = "Agent #10"
    agent_name: str = "ProjectExecutionAgent"
    version: str = "1.0.0"

    bedrock_model_id: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_PLANNING_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    )
    temperature: float = 0.1
    max_tokens: int = 4096

    max_work_packages: int = 12
    max_tasks_per_package: int = 20
    max_total_tasks: int = 100
    default_estimated_hours_per_task: float = 4.0

    standard_phases: List[str] = [
        "PHASE-1: System Core & Setup",
        "PHASE-2: Subsystems & Hardware Interfaces",
        "PHASE-3: Firmware & Embedded Drivers",
        "PHASE-4: Control Logic & Algorithms",
        "PHASE-5: Verification & Quality Assurance",
        "PHASE-6: Deployment & Integration",
    ]


planning_config = ProjectExecutionConfig()
