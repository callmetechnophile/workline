"""
End-to-end unit and integration tests for BOMOptimizationAgent (Agent #8).
"""

import pytest
from research_agents.bom_optimization_agent.agent import BOMOptimizationAgent
from research_agents.bom_optimization_agent.providers.mock_provider import MockBOMOptimizationProvider
from research_agents.bom_optimization_agent.schemas import (
    BOMOptimizationAgentInput,
    Location,
    ProjectConstraints,
    ProjectMeta,
)


@pytest.mark.asyncio
async def test_bom_optimization_agent_successful_run():
    agent = BOMOptimizationAgent(reasoning_provider=MockBOMOptimizationProvider())

    input_data = BOMOptimizationAgentInput(
        project=ProjectMeta(
            project_id="proj_sar_drone_001",
            title="Autonomous Search and Rescue Drone",
            destination=Location(city="Bengaluru", state="Karnataka", country="India"),
            constraints=ProjectConstraints(maximum_budget=100000.0, maximum_delivery_days=7),
        ),
        bom={
            "bom_id": "BOM-SAR-001",
            "items": [
                {
                    "bom_item_id": "BOM-001",
                    "part_number": "900-13766-0000-000",
                    "manufacturer": "NVIDIA",
                    "component_name": "Jetson Orin Nano 8GB",
                    "category": "SBC",
                    "quantity": 1,
                    "subsystem_id": "SUB-001",
                    "selection_status": "selected",
                },
                {
                    "bom_item_id": "BOM-002",
                    "part_number": "500-0771-01",
                    "manufacturer": "Teledyne FLIR",
                    "component_name": "FLIR Lepton 3.5",
                    "category": "thermal camera",
                    "quantity": 1,
                    "subsystem_id": "SUB-002",
                    "selection_status": "selected",
                },
                {
                    "bom_item_id": "BOM-003",
                    "part_number": "ESP32-S3-WROOM-1-N8R8",
                    "manufacturer": "Espressif Systems",
                    "component_name": "ESP32-S3 Module",
                    "category": "microcontroller",
                    "quantity": 1,
                    "subsystem_id": "SUB-004",
                    "selection_status": "selected",
                },
                {
                    "bom_item_id": "BOM-004",
                    "part_number": "TPS565208DDCR",
                    "manufacturer": "Texas Instruments",
                    "component_name": "5V/5A Buck Regulator",
                    "category": "DC-DC converter",
                    "quantity": 1,
                    "subsystem_id": "SUB-003",
                    "selection_status": "selected",
                },
            ],
        },
        component_alternatives=[
            {
                "alternative_id": "ALT-001",
                "part_number": "SC1111",
                "manufacturer": "Raspberry Pi",
                "compatibility": "architecture_alternative",
                "reason": "Alternative SBC",
            }
        ],
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert len(output.optimized_items) == 4
    assert len(output.strategies) == 4
    assert output.selected_strategy.name in ("Lowest Landed Cost", "Fastest Delivery")
    assert output.cost_summary.total_product_cost > 0
    assert output.cost_summary.total_shipping_cost > 0
    assert output.cost_summary.total_known_landed_cost > output.cost_summary.total_product_cost
    assert len(output.orders) >= 1
    assert len(output.traceability) == 4
    assert "# Procurement Optimization Report" in output.structured_report_markdown


def test_bom_optimization_agent_sync_execution():
    agent = BOMOptimizationAgent(reasoning_provider=MockBOMOptimizationProvider())

    input_data = BOMOptimizationAgentInput(
        project=ProjectMeta(title="Sync Test Drone"),
        bom={
            "bom_id": "BOM-01",
            "items": [
                {"bom_item_id": "BOM-01", "part_number": "ESP32-S3-WROOM-1-N8R8", "component_name": "ESP32", "quantity": 1}
            ],
        },
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert len(output.optimized_items) == 1
