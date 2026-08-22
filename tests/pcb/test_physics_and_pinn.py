"""Unit tests for Physics features, Reference Thermal Solver, Dataset generation, and PINN Training."""

import numpy as np
import pytest
from backend.workline.pcb.engine.builder import PCBBuilder
from backend.workline.pcb.physics.dataset import ThermalDatasetGenerator
from backend.workline.pcb.physics.features import PhysicsFeatureEngine
from backend.workline.pcb.physics.reference_solver import ReferenceThermalSolver
from backend.workline.pcb.pinn.checkpoints import CheckpointManager
from backend.workline.pcb.pinn.inference import PINNInferenceEngine
from backend.workline.pcb.pinn.loss import PINNLossCalculator
from backend.workline.pcb.pinn.metrics import PINNMetricsCalculator
from backend.workline.pcb.pinn.model import PCBThermalPINN
from backend.workline.pcb.pinn.trainer import PINNTrainer
from backend.workline.procurement.models import BOM, BOMItem


def test_physics_feature_generation():
    """Test deterministic numerical feature extraction across PCB mesh."""
    bom = BOM(
        bom_id="b1",
        project_id="test_feat_proj",
        items=[
            BOMItem(bom_item_id="i1", component_id="c1", manufacturer="TI", mpn="LM2596", category="Power Management", quantity=1, unit_price=80.0, extended_price=80.0),
        ],
        total_cost=80.0,
    )
    proj = PCBBuilder.build_from_bom("test_feat_proj", bom, board_width=50.0, board_height=40.0)

    engine = PhysicsFeatureEngine()
    features = engine.extract_features(proj, nx=10, ny=10)
    assert len(features) == 100
    assert features[0].effective_conductivity > 0.0
    assert features[0].convection_coefficient > 0.0


def test_reference_thermal_solver():
    """Test simplified 2D finite-difference heat diffusion solver."""
    bom = BOM(
        bom_id="b1",
        project_id="test_solver_proj",
        items=[
            BOMItem(bom_item_id="i1", component_id="c1", manufacturer="TI", mpn="LM2596", category="Power Management", quantity=1, unit_price=80.0, extended_price=80.0),
        ],
        total_cost=80.0,
    )
    proj = PCBBuilder.build_from_bom("test_solver_proj", bom, board_width=50.0, board_height=40.0)

    solver = ReferenceThermalSolver(nx=20, ny=15, max_iter=200)
    res = solver.solve(proj)
    assert res.solver_name == "SIMPLIFIED REFERENCE SOLVER"
    assert res.peak_temperature >= res.ambient_temperature
    assert len(res.grid_temperature) == 15
    assert len(res.grid_temperature[0]) == 20


def test_thermal_dataset_generation_with_splits():
    """Test generating training dataset with 70/15/15 splits."""
    bom = BOM(bom_id="b1", project_id="test_ds_proj", items=[], total_cost=0.0)
    proj = PCBBuilder.build_from_bom("test_ds_proj", bom, board_width=50.0, board_height=40.0)

    generator = ThermalDatasetGenerator(nx=15, ny=10)
    ds = generator.generate_dataset(proj, train_ratio=0.70, val_ratio=0.15)
    assert ds.total_samples == 150
    assert ds.train_count > 0
    assert ds.validation_count > 0
    assert ds.test_count > 0


def test_pinn_model_and_training():
    """Test PINN model forward pass, loss calculation, and training loop."""
    bom = BOM(
        bom_id="b1",
        project_id="test_pinn_proj",
        items=[
            BOMItem(bom_item_id="i1", component_id="c1", manufacturer="TI", mpn="LM2596", category="Power Management", quantity=1, unit_price=80.0, extended_price=80.0),
        ],
        total_cost=80.0,
    )
    proj = PCBBuilder.build_from_bom("test_pinn_proj", bom, board_width=50.0, board_height=40.0)

    generator = ThermalDatasetGenerator(nx=20, ny=15)
    dataset = generator.generate_dataset(proj)

    trainer = PINNTrainer(epochs=15, learning_rate=0.01)
    model, run_res = trainer.train(dataset)

    assert run_res.epochs_completed == 15
    assert run_res.validation_metrics.mae_celsius >= 0.0
    assert run_res.validation_metrics.rmse_celsius >= 0.0

    # Test PINN Inference Engine
    inference = PINNInferenceEngine(model=model)
    inf_res = inference.predict_project_thermal_field(proj, nx=20, ny=15)
    assert inf_res.predicted_peak_temperature >= 25.0
    assert len(inf_res.temperature_grid) == 15
