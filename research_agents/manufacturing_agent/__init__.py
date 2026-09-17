"""
Manufacturing / DFM-DFA Agent (Agent #24 / agent.24).
Design-for-Manufacturing, Design-for-Assembly, Process Selection, Tolerance GD&T,
Tooling, Variation Analysis, and Readiness Engine for WorkflowGuide AI.
"""

from research_agents.manufacturing_agent.agent import ManufacturingDFMAgent
from research_agents.manufacturing_agent.schemas import (
    CostDriverHandoff,
    DFAModel,
    DFMFinding,
    InspectionItem,
    ManufacturingDashboardData,
    ManufacturingProcess,
    ManufacturingReadiness,
    ManufacturingRecommendation,
    ProcessCapabilityComparison,
    ProcessSequence,
    ToleranceItem,
    ToolingRequirement,
    VariationData,
)

__all__ = [
    "ManufacturingDFMAgent",
    "ManufacturingProcess",
    "DFMFinding",
    "DFAModel",
    "ToleranceItem",
    "VariationData",
    "ManufacturingRecommendation",
    "CostDriverHandoff",
    "ManufacturingReadiness",
    "ProcessCapabilityComparison",
    "ToolingRequirement",
    "ProcessSequence",
    "InspectionItem",
    "ManufacturingDashboardData",
]
