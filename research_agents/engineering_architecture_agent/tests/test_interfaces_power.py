"""
Unit tests for InterfaceDesigner and PowerArchitect services.
"""

from research_agents.engineering_architecture_agent.schemas import SubsystemItem
from research_agents.engineering_architecture_agent.services.interface_designer import InterfaceDesigner
from research_agents.engineering_architecture_agent.services.power_architect import PowerArchitect


def test_interface_and_power_domain_architecture():
    interface_designer = InterfaceDesigner()
    power_architect = PowerArchitect()

    subsystems = [
        SubsystemItem(subsystem_id="SUB-001", name="Compute Subsystem", purpose="AI compute"),
        SubsystemItem(subsystem_id="SUB-002", name="Sensing Subsystem", purpose="Sensors"),
        SubsystemItem(subsystem_id="SUB-003", name="Power Subsystem", purpose="Power"),
        SubsystemItem(subsystem_id="SUB-004", name="Control Subsystem", purpose="Autopilot"),
    ]

    interfaces = interface_designer.design_interfaces(subsystems)
    assert len(interfaces) >= 3
    if_types = {i.interface_type for i in interfaces}
    assert "SPI" in if_types
    assert "UART" in if_types
    assert "I2C" in if_types

    # Check SPI interface properties
    spi_iface = next(i for i in interfaces if i.interface_type == "SPI")
    assert spi_iface.source == "SUB-002"
    assert spi_iface.target == "SUB-001"
    assert spi_iface.voltage_logic == "3.3V"

    # Check Power Domains
    power_domains = power_architect.build_power_domains(subsystems)
    assert len(power_domains) >= 3
    rail_names = {p.name for p in power_domains}
    assert any("5.0V" in n for n in rail_names)
    assert any("3.3V" in n for n in rail_names)
    assert any("14.8V" in n for n in rail_names)
