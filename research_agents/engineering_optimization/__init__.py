"""
EngineeringOptimizationAgent package (Agent #20 of WorkflowGuide AI).
"""

from research_agents.engineering_optimization.agent import EngineeringOptimizationAgent
from research_agents.engineering_optimization.config import OptimizationConfig, optimization_config
from research_agents.engineering_optimization.schemas import (
    ConstraintObject,
    DesignCandidate,
    ObjectiveObject,
    OptimizationDecision,
    OptimizationInput,
    OptimizationObject,
    OptimizationOutput,
    OptimizationResult,
    OptimizationStatusLiteral,
    ParetoFrontierObject,
    ParetoPoint,
    RobustnessObject,
    VariableObject,
)

__all__ = [
    "EngineeringOptimizationAgent",
    "OptimizationConfig",
    "optimization_config",
    "OptimizationStatusLiteral",
    "ObjectiveObject",
    "ConstraintObject",
    "VariableObject",
    "DesignCandidate",
    "ParetoPoint",
    "ParetoFrontierObject",
    "RobustnessObject",
    "OptimizationDecision",
    "OptimizationObject",
    "OptimizationResult",
    "OptimizationInput",
    "OptimizationOutput",
]
