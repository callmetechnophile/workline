"""Tests for Multi-Physics Simulation Orchestrator and PINN Cross-Validation."""

import pytest
from backend.workline.pcb.simulation.solvers import (
    SPICEElectricalSolver,
    NumericalThermalSolver,
    SIPISolver,
    SimulationSolverType,
    PhysicalDomain,
    PhysicalMetric,
    SolverResult,
)
from backend.workline.pcb.simulation.cross_validator import (
    SimulationCrossValidator,
    CrossValidationReport,
)
from backend.workline.pcb.simulation.orchestrator import SimulationOrchestrator


def test_individual_solvers_execution():
    """Test SPICE, Thermal, and SI/PI solver execution."""
    spice = SPICEElectricalSolver.simulate(rail_voltage=3.3, current=2.0, trace_resistance=0.01)
    assert spice.solver_type == SimulationSolverType.SPICE
    assert spice.converged is True
    assert len(spice.metrics) == 3

    thermal = NumericalThermalSolver.simulate(ambient_temp=25.0, total_power=2.5)
    assert thermal.solver_type == SimulationSolverType.THERMAL_SOLVER
    assert thermal.converged is True
    assert len(thermal.metrics) == 2

    sipi = SIPISolver.simulate(trace_width_mm=0.2, trace_spacing_mm=0.15)
    assert sipi.solver_type == SimulationSolverType.SI_PI_SOLVER
    assert sipi.converged is True
    assert len(sipi.metrics) == 1


def test_cross_validation_pass_and_fail():
    """Test cross-validation discrepancy thresholds (<=5% PASS, >15% FAIL)."""
    ref_thermal = SolverResult(
        solver_type=SimulationSolverType.THERMAL_SOLVER,
        domain=PhysicalDomain.THERMAL,
        metrics=[
            PhysicalMetric(name="Peak_Temperature", domain=PhysicalDomain.THERMAL, value=80.0, unit="degC"),
        ],
    )

    # 1. Close surrogate prediction (82°C vs 80°C -> 2.5% delta -> PASS)
    sur_pass = SolverResult(
        solver_type=SimulationSolverType.PINN_SURROGATE,
        domain=PhysicalDomain.THERMAL,
        metrics=[
            PhysicalMetric(name="Peak_Temperature", domain=PhysicalDomain.THERMAL, value=82.0, unit="degC"),
        ],
    )
    cv_pass = SimulationCrossValidator.validate([ref_thermal], sur_pass)
    assert cv_pass.overall_status == "PASS"
    assert cv_pass.max_relative_discrepancy == 0.025
    assert len(cv_pass.comparisons) == 1

    # 2. Large discrepancy prediction (98°C vs 80°C -> 22.5% delta -> FAIL)
    sur_fail = SolverResult(
        solver_type=SimulationSolverType.PINN_SURROGATE,
        domain=PhysicalDomain.THERMAL,
        metrics=[
            PhysicalMetric(name="Peak_Temperature", domain=PhysicalDomain.THERMAL, value=98.0, unit="degC"),
        ],
    )
    cv_fail = SimulationCrossValidator.validate([ref_thermal], sur_fail)
    assert cv_fail.overall_status == "FAIL"
    assert cv_fail.max_relative_discrepancy == 0.225


def test_multi_physics_pipeline_orchestration():
    """Test end-to-end multi-physics pipeline execution."""
    run = SimulationOrchestrator.run_multi_physics_pipeline(
        project_id="rover_v2", rail_voltage=3.3, total_power=2.5
    )
    assert run.project_id == "rover_v2"
    assert len(run.results) == 4  # SPICE, Thermal, SI/PI, PINN
    assert run.cross_validation.overall_status == "PASS"
