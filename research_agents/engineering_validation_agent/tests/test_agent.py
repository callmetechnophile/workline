"""
End-to-end unit and integration tests for EngineeringValidationAgent (Agent #9).
"""

import pytest
from research_agents.engineering_validation_agent.agent import EngineeringValidationAgent
from research_agents.engineering_validation_agent.providers.mock_provider import MockEngineeringValidationProvider
from research_agents.engineering_validation_agent.schemas import EngineeringValidationAgentInput


@pytest.mark.asyncio
async def test_engineering_validation_agent_successful_run():
    agent = EngineeringValidationAgent(reasoning_provider=MockEngineeringValidationProvider())

    input_data = EngineeringValidationAgentInput(
        project={"title": "SAR Drone Verification Test", "project_id": "proj_sar_001"},
        subsystems=[{"subsystem_id": "SUB-01", "name": "Compute"}],
        component_roles=[{"role_name": "SBC", "subsystem_id": "SUB-01"}],
        interfaces=[{"source_component_id": "BOM-01", "destination_component_id": "BOM-02", "voltage_level": 3.3}],
        power_domains=[{"domain_name": "5V_MAIN", "max_current_capacity_a": 5.0, "known_load_current_a": 2.5}],
        bom={
            "bom_id": "BOM-01",
            "items": [
                {"bom_item_id": "BOM-01", "part_number": "900-13766-0000-000", "category": "SBC", "quantity": 1, "subsystem_id": "SUB-01", "known_specifications": {"operating_voltage": "5V"}},
                {"bom_item_id": "BOM-02", "part_number": "ESP32-S3", "category": "microcontroller", "quantity": 1, "subsystem_id": "SUB-01", "known_specifications": {"operating_voltage": "3.3V"}},
                {"bom_item_id": "BOM-03", "part_number": "TPS565208", "category": "DC-DC converter", "quantity": 1, "subsystem_id": "SUB-01"},
                {"bom_item_id": "BOM-04", "part_number": "CAP-1000uF", "category": "capacitor", "quantity": 1, "subsystem_id": "SUB-01"},
            ],
        },
        optimized_procurement={
            "orders": [{"items": [{"bom_item_id": "BOM-01", "purchased_quantity": 1}, {"bom_item_id": "BOM-02", "purchased_quantity": 1}]}]
        },
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert output.verdict == "READY"
    assert output.final_verdict.critical_failures == 0
    assert len(output.requirement_results) >= 1
    assert len(output.rule_results) >= 5
    assert len(output.traceability) == 4
    assert "# Engineering Design Verification Report" in output.structured_report_markdown

    # Test readiness gate ADK method
    gate = agent.is_ready_for_execution(output)
    assert gate["ready"] is True
    assert gate["verdict"] == "READY"


def test_engineering_validation_agent_sync_execution():
    agent = EngineeringValidationAgent(reasoning_provider=MockEngineeringValidationProvider())

    input_data = EngineeringValidationAgentInput(
        project={"title": "Sync Test"},
        bom={"items": [{"bom_item_id": "BOM-01", "part_number": "ESP32", "quantity": 1}]},
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert output.verdict in ("READY", "READY_WITH_WARNINGS", "BLOCKED")
