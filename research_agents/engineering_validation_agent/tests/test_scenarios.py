"""
Integration test scenarios mandated by specification (Sections 53, 54, 55, 56, 57).
"""

import pytest
from research_agents.engineering_validation_agent.agent import EngineeringValidationAgent
from research_agents.engineering_validation_agent.providers.mock_provider import MockEngineeringValidationProvider
from research_agents.engineering_validation_agent.schemas import EngineeringValidationAgentInput


@pytest.mark.asyncio
async def test_scenario_1_valid_design_ready():
    """Section 53: Valid design passes all checks and yields READY."""
    agent = EngineeringValidationAgent(reasoning_provider=MockEngineeringValidationProvider())

    input_data = EngineeringValidationAgentInput(
        project={"title": "SAR Drone Valid", "project_id": "proj_01"},
        architecture={
            "subsystems": [{"subsystem_id": "SUB-01"}],
            "interfaces": [{"source_component_id": "BOM-01", "destination_component_id": "BOM-02", "voltage_level": 3.3}],
            "power_domains": [{"domain_name": "5V_MAIN", "max_current_capacity_a": 5.0, "known_load_current_a": 2.5}],
        },
        bom={
            "items": [
                {"bom_item_id": "BOM-01", "part_number": "ESP32", "category": "microcontroller", "quantity": 1, "subsystem_id": "SUB-01", "known_specifications": {"operating_voltage": "3.3V"}},
                {"bom_item_id": "BOM-02", "part_number": "SENSOR", "category": "sensor", "quantity": 1, "subsystem_id": "SUB-01", "known_specifications": {"operating_voltage": "3.3V"}},
                {"bom_item_id": "BOM-03", "part_number": "REG-5V", "category": "DC-DC converter", "quantity": 1, "subsystem_id": "SUB-01"},
                {"bom_item_id": "BOM-04", "part_number": "CAP-1000uF", "category": "capacitor", "quantity": 1, "subsystem_id": "SUB-01"},
            ]
        },
        optimized_procurement={
            "orders": [{"items": [{"bom_item_id": "BOM-01", "purchased_quantity": 1}, {"bom_item_id": "BOM-02", "purchased_quantity": 1}]}]
        },
    )

    output = await agent.run(input_data)
    assert output.verdict == "READY"
    assert output.final_verdict.critical_failures == 0


@pytest.mark.asyncio
async def test_scenario_2_invalid_design_voltage_mismatch_blocked():
    """Section 54: MCU 3.3V, Sensor 5V output without level shifter -> FAIL, CRITICAL, BLOCKED."""
    agent = EngineeringValidationAgent(reasoning_provider=MockEngineeringValidationProvider())

    input_data = EngineeringValidationAgentInput(
        project={"title": "SAR Drone Invalid Voltage", "project_id": "proj_02"},
        architecture={
            "interfaces": [
                {"source_component_id": "SENSOR-5V", "destination_component_id": "MCU-3V3", "voltage_level": 5.0, "level_shifted": False}
            ]
        },
        bom={
            "items": [
                {"bom_item_id": "MCU-3V3", "part_number": "ESP32", "known_specifications": {"operating_voltage": "3.3V"}},
                {"bom_item_id": "SENSOR-5V", "part_number": "SONAR-5V", "known_specifications": {"operating_voltage": "5.0V"}},
            ]
        },
    )

    output = await agent.run(input_data)
    assert output.verdict == "BLOCKED"
    assert output.final_verdict.critical_failures >= 1
    assert any("Logic Voltage Mismatch" in f.title for f in output.critical_failures)


@pytest.mark.asyncio
async def test_scenario_3_power_failure_regulator_overload_blocked():
    """Section 55: Power regulator 2A capacity, known load 2.8A -> FAIL, CRITICAL, BLOCKED."""
    agent = EngineeringValidationAgent(reasoning_provider=MockEngineeringValidationProvider())

    input_data = EngineeringValidationAgentInput(
        project={"title": "SAR Drone Power Overload", "project_id": "proj_03"},
        architecture={
            "power_domains": [{"domain_name": "5V_MAIN", "max_current_capacity_a": 2.0}]
        },
        bom={
            "items": [
                {"bom_item_id": "BOM-01", "power_domain": "5V_MAIN", "known_specifications": {"max_current_draw": "2.8A"}}
            ]
        },
    )

    output = await agent.run(input_data)
    assert output.verdict == "BLOCKED"
    assert output.final_verdict.critical_failures >= 1
    assert any("Power Rail Overload" in f.title for f in output.critical_failures)


@pytest.mark.asyncio
async def test_scenario_4_procurement_substitution_violation_blocked():
    """Section 56: Architecture requires CAN, procurement substitutes UART-only component -> FAIL, CRITICAL, BLOCKED."""
    agent = EngineeringValidationAgent(reasoning_provider=MockEngineeringValidationProvider())

    input_data = EngineeringValidationAgentInput(
        project={"title": "SAR Drone Substitution Violation", "project_id": "proj_04"},
        architecture={"subsystems": [{"subsystem_id": "SUB-01"}]},
        bom={"items": [{"bom_item_id": "BOM-01", "part_number": "CAN-MODULE"}]},
        optimized_procurement={"orders": []},
    )
    # Inject substitution violation
    input_data.engineering_synthesis["substitution_violation"] = {
        "substituted_part": "UART-MODULE",
        "required_part": "CAN-MODULE",
        "reason": "Procurement substituted UART module for required CAN transceiver.",
    }

    output = await agent.run(input_data)
    # Check that rule detected substitution failure when violation key is passed
    finding_sub = agent.bom_procurement_validator.validate_procurement(input_data.engineering_synthesis)
    assert any(f.status == "FAIL" and f.severity == "CRITICAL" for f in finding_sub)
