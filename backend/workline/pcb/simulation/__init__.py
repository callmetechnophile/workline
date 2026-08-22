"""Multi-physics simulation orchestrator and cross-validation package."""

from backend.workline.pcb.simulation.solvers import (
    SimulationSolverType,
    PhysicalDomain,
    PhysicalMetric,
    SolverResult,
    SPICEElectricalSolver,
    NumericalThermalSolver,
    SIPISolver,
)
from backend.workline.pcb.simulation.cross_validator import (
    CrossValidationStatus,
    MetricComparison,
    CrossValidationReport,
    SimulationCrossValidator,
)
from backend.workline.pcb.simulation.orchestrator import (
    MultiPhysicsSimulationRun,
    SimulationOrchestrator,
)

__all__ = [
    "SimulationSolverType",
    "PhysicalDomain",
    "PhysicalMetric",
    "SolverResult",
    "SPICEElectricalSolver",
    "NumericalThermalSolver",
    "SIPISolver",
    "CrossValidationStatus",
    "MetricComparison",
    "CrossValidationReport",
    "SimulationCrossValidator",
    "MultiPhysicsSimulationRun",
    "SimulationOrchestrator",
]
