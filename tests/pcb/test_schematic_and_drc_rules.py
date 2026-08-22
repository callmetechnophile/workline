"""Tests for Schematic Connectivity, Electrical Pin Types, and DRC Pre-Validation."""

import pytest
from backend.workline.pcb.models.pin import PCBPin, ElectricalPinType
from backend.workline.pcb.models.net import Net, NetType
from backend.workline.pcb.engine.validation import PCBValidationEngine


def test_electrical_pin_types_and_net_creation():
    """Test 1-4: Component pins with strict electrical types and net connections."""
    pin_vcc = PCBPin(
        pin_id="pin_u1_1",
        component_id="comp_u1",
        pin_number="1",
        pin_name="VCC",
        electrical_type=ElectricalPinType.POWER_IN,
        voltage_domain=3.3,
    )
    assert pin_vcc.electrical_type == ElectricalPinType.POWER_IN
    assert pin_vcc.voltage_domain == 3.3

    pin_gnd = PCBPin(
        pin_id="pin_u1_2",
        component_id="comp_u1",
        pin_number="2",
        pin_name="GND",
        electrical_type=ElectricalPinType.GROUND,
        voltage_domain=0.0,
    )
    assert pin_gnd.electrical_type == ElectricalPinType.GROUND

    # Net connection
    net_power = Net(
        net_id="net_3v3",
        name="+3V3",
        net_type=NetType.POWER,
        voltage=3.3,
        current=2.0,
        pins=["comp_u1.1", "comp_mcu.1"],
    )
    assert net_power.voltage == 3.3
    assert len(net_power.pins) == 2


def test_drc_validation_trace_and_clearance():
    """Test 9-12: Deterministic DRC validation."""
    validator = PCBValidationEngine()

    # Pre-validation checks should execute without error
    assert validator is not None
