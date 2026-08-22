"""Unit tests covering the 12 PCB design rule and integrity validation checks."""

import pytest
from backend.workline.pcb.engine.builder import PCBBuilder
from backend.workline.pcb.engine.validation import PCBValidator
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.constraints import PCBConstraintItem
from backend.workline.pcb.models.footprint import Footprint, Pad
from backend.workline.pcb.models.net import Net, NetNode
from backend.workline.pcb.models.pin import Pin
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.models.thermal import ThermalComponent
from backend.workline.procurement.models import BOM, BOMItem


def test_validation_all_clean_project():
    """Test valid PCB layout passes DRC validation."""
    bom = BOM(
        bom_id="b1",
        project_id="clean_pcb",
        items=[
            BOMItem(bom_item_id="i1", component_id="c1", manufacturer="TI", mpn="LM2596", category="Power", quantity=1, unit_price=80.0, extended_price=80.0),
        ],
        total_cost=80.0,
    )
    proj = PCBBuilder.build_from_bom("clean_pcb", bom, board_width=80.0, board_height=60.0)

    validator = PCBValidator()
    report = validator.validate_project(proj)
    assert report.passed is True
    assert report.error_count == 0


def test_validation_board_boundary_violation():
    """Test check 1: component placed outside board boundary."""
    bom = BOM(bom_id="b1", project_id="p1", items=[], total_cost=0.0)
    proj = PCBBuilder.build_from_bom("p1", bom, board_width=50.0, board_height=40.0)

    # Place component off-board
    comp = PCBComponent(
        id="c_out",
        component_id="comp_1",
        reference_designator="U99",
        footprint_id="FP_QFN32",
        x=55.0, # Outside 50mm board width
        y=20.0,
    )
    proj.components[comp.id] = comp

    validator = PCBValidator()
    report = validator.validate_project(proj)
    assert report.passed is False
    assert any(v.category == "BOUNDARY" for v in report.violations)


def test_validation_component_overlap_violation():
    """Test check 2: component collision on same layer."""
    bom = BOM(bom_id="b1", project_id="p2", items=[], total_cost=0.0)
    proj = PCBBuilder.build_from_bom("p2", bom)

    # Place two components at the exact same location
    c1 = PCBComponent(id="c1", component_id="comp_1", reference_designator="U1", footprint_id="FP_SOIC8", x=20.0, y=20.0)
    c2 = PCBComponent(id="c2", component_id="comp_2", reference_designator="U2", footprint_id="FP_SOIC8", x=20.5, y=20.5)
    proj.components[c1.id] = c1
    proj.components[c2.id] = c2

    validator = PCBValidator()
    report = validator.validate_project(proj)
    assert report.passed is False
    assert any(v.category == "OVERLAP" for v in report.violations)


def test_validation_missing_footprint_and_unconnected_net():
    """Test checks 5 and 7: missing footprint and floating nets."""
    bom = BOM(bom_id="b1", project_id="p3", items=[], total_cost=0.0)
    proj = PCBBuilder.build_from_bom("p3", bom)

    # Missing footprint
    comp_bad = PCBComponent(id="c_bad", component_id="comp_x", reference_designator="U3", footprint_id="NON_EXISTENT_FP", x=20.0, y=20.0)
    proj.components[comp_bad.id] = comp_bad

    # Floating net with 1 node
    proj.nets["net_floating"] = Net(id="net_floating", name="FLOAT_NET", nodes=[NetNode(component_id="c_bad", pin_number=1)])

    validator = PCBValidator()
    report = validator.validate_project(proj)
    assert any(v.category == "FOOTPRINT" for v in report.violations)
    assert any(v.category == "NETLIST" for v in report.violations)


def test_validation_power_and_thermal_violations():
    """Test checks 9 and 10: overloaded power rail and thermal junction limits."""
    bom = BOM(bom_id="b1", project_id="p4", items=[], total_cost=0.0)
    proj = PCBBuilder.build_from_bom("p4", bom)

    # Overload power rail
    proj.power.rails["3V3"].estimated_current = 5.0 # Max is 1.5A

    # Overheated thermal component
    c_hot = PCBComponent(id="c_hot", component_id="comp_hot", reference_designator="U_HOT", footprint_id="FP_SOIC8", x=30.0, y=30.0)
    proj.components[c_hot.id] = c_hot
    proj.thermal.components[c_hot.id] = ThermalComponent(component_id=c_hot.id, power_dissipation=5.0, thermal_resistance_ja=45.0, max_junction_temperature=125.0)

    validator = PCBValidator()
    report = validator.validate_project(proj)
    assert any(v.category == "POWER" for v in report.violations)
    assert any(v.category == "THERMAL" for v in report.violations)
