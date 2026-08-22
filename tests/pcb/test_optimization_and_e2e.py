"""End-to-End deterministic synthetic PCB test and Thermal Placement Optimization."""

import pytest
from backend.workline.pcb.engine.builder import PCBBuilder
from backend.workline.pcb.engine.validation import PCBValidator
from backend.workline.pcb.optimization.constraints import HardConstraintChecker
from backend.workline.pcb.optimization.objective import ThermalPlacementObjective
from backend.workline.pcb.optimization.optimizer import ThermalPlacementOptimizer
from backend.workline.pcb.physics.dataset import ThermalDatasetGenerator
from backend.workline.pcb.physics.reference_solver import ReferenceThermalSolver
from backend.workline.pcb.pinn.inference import PINNInferenceEngine
from backend.workline.pcb.pinn.trainer import PINNTrainer
from backend.workline.procurement.models import BOM, BOMItem


def test_deterministic_synthetic_pcb_e2e_pipeline():
    """
    Complete Deterministic Synthetic PCB End-to-End Test:
    Board: 50 x 40 mm, 4 layers
    Components: MCU, Voltage Regulator, ADC, Sensor Connector, Communication Module
    Nets: 3V3, GND, I2C_SDA, I2C_SCL, UART_TX, UART_RX
    Power: 3.3V rail
    Pipeline: BOM -> PCB -> footprints -> nets -> constraints -> initial placement ->
              reference solver -> dataset -> PINN train -> PINN predict -> validation ->
              thermal optimization -> final validation.
    """
    # 1. Synthetic BOM
    synthetic_bom = BOM(
        bom_id="bom_synthetic_rover_pcb",
        project_id="synthetic_rover_pcb",
        items=[
            BOMItem(
                bom_item_id="item_mcu",
                component_id="comp_mcu",
                manufacturer="Espressif",
                mpn="ESP32-S3-WROOM-1",
                category="Microcontroller / Compute Unit",
                quantity=1,
                unit_price=385.0,
                extended_price=385.0,
            ),
            BOMItem(
                bom_item_id="item_reg",
                component_id="comp_reg",
                manufacturer="TI",
                mpn="LM2596S-3.3",
                category="Power Management / Regulator",
                quantity=1,
                unit_price=89.0,
                extended_price=89.0,
            ),
            BOMItem(
                bom_item_id="item_adc",
                component_id="comp_adc",
                manufacturer="TI",
                mpn="ADS1115",
                category="Sensors / ADC",
                quantity=1,
                unit_price=210.0,
                extended_price=210.0,
            ),
            BOMItem(
                bom_item_id="item_sensor",
                component_id="comp_sensor",
                manufacturer="Bosch",
                mpn="BME280",
                category="Sensors / Environmental",
                quantity=1,
                unit_price=349.0,
                extended_price=349.0,
            ),
            BOMItem(
                bom_item_id="item_conn",
                component_id="comp_conn",
                manufacturer="Molex",
                mpn="HDR-1X4",
                category="Connectors / Header",
                quantity=1,
                unit_price=45.0,
                extended_price=45.0,
            ),
        ],
        total_cost=1078.0,
    )

    # 2. Construct PCB Project
    pcb_proj = PCBBuilder.build_from_bom(
        project_id="synthetic_rover_pcb",
        bom=synthetic_bom,
        board_width=50.0,
        board_height=40.0,
    )
    assert pcb_proj.board.width == 50.0
    assert pcb_proj.board.height == 40.0
    assert len(pcb_proj.components) == 5
    assert len(pcb_proj.nets) >= 5

    # 3. Initial DRC Validation
    validator = PCBValidator()
    initial_report = validator.validate_project(pcb_proj)
    assert initial_report.passed is True

    # 4. Numerical Reference Thermal Solver
    ref_solver = ReferenceThermalSolver(nx=20, ny=15, max_iter=200)
    ref_result = ref_solver.solve(pcb_proj)
    assert ref_result.peak_temperature > 25.0
    assert ref_result.solver_name == "SIMPLIFIED REFERENCE SOLVER"

    # 5. Physics Dataset Generation
    dataset_gen = ThermalDatasetGenerator(nx=20, ny=15)
    dataset = dataset_gen.generate_dataset(pcb_proj)
    assert dataset.total_samples == 300
    assert dataset.train_count > 0

    # 6. PINN Training
    trainer = PINNTrainer(epochs=20, learning_rate=0.01)
    pinn_model, training_run = trainer.train(dataset)
    assert training_run.epochs_completed == 20
    assert training_run.validation_metrics.mae_celsius >= 0.0

    # 7. PINN Forward Inference
    inference_engine = PINNInferenceEngine(model=pinn_model)
    inf_result = inference_engine.predict_project_thermal_field(pcb_proj, nx=20, ny=15)
    assert inf_result.predicted_peak_temperature > 25.0

    # 8. Thermal Placement Optimization
    pinn_objective = ThermalPlacementObjective(pinn_engine=inference_engine)
    optimizer = ThermalPlacementOptimizer(objective=pinn_objective, max_iterations=25)
    optimized_proj, opt_result = optimizer.optimize(pcb_proj)

    assert opt_result.optimized_peak_temperature <= opt_result.initial_peak_temperature
    assert opt_result.temperature_reduction_celsius >= 0.0

    # 9. Final DRC Validation after Optimization
    final_report = validator.validate_project(optimized_proj)
    assert final_report.passed is True
