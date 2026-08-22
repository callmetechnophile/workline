"""Unit tests for PCB models, footprint library, netlist connectivity, and BOM builder."""

import pytest
from backend.workline.pcb.engine.builder import PCBBuilder
from backend.workline.pcb.io.serializer import WLPCBSerializer
from backend.workline.pcb.models.board import Board, BoardShape, MountingHole
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.footprint import Footprint, Pad
from backend.workline.pcb.models.layer import Layer, LayerType
from backend.workline.pcb.models.net import Net, NetClass, NetNode
from backend.workline.pcb.models.pin import ElectricalType, Pin
from backend.workline.pcb.models.stackup import Stackup
from backend.workline.procurement.models import BOM, BOMItem


def test_board_and_stackup_creation():
    """Test physical board geometry, mounting holes, and multi-layer stackup."""
    board = Board(
        width=50.0,
        height=40.0,
        thickness=1.6,
        shape=BoardShape.RECTANGLE,
        layer_count=4,
        mounting_holes=[MountingHole(id="MH1", x=3.0, y=3.0, diameter=3.2)],
    )
    assert board.width == 50.0
    assert board.height == 40.0
    assert len(board.mounting_holes) == 1

    stackup = Stackup()
    assert len(stackup.layers) == 7 # 4 copper + 3 dielectric
    copper_layers = [l for l in stackup.layers if l.type in (LayerType.SIGNAL, LayerType.POWER, LayerType.GROUND)]
    assert len(copper_layers) == 4


def test_component_and_footprint_models():
    """Test PCBComponent referencing canonical component and footprint pads."""
    fp = Footprint(
        id="FP_SOIC8_TEST",
        name="SOIC-8 Test",
        package="SOIC-8",
        body_width=4.9,
        body_height=3.9,
        pads=[Pad(number=1, x=-2.0, y=-1.5), Pad(number=2, x=-2.0, y=1.5)],
    )
    assert len(fp.pads) == 2

    comp = PCBComponent(
        id="pcb_comp_u1",
        component_id="component:texas_instruments_tps62130rgtr",
        reference_designator="U1",
        value="TPS62130",
        footprint_id="FP_SOIC8_TEST",
        x=25.0,
        y=20.0,
        locked=False,
    )
    assert comp.reference_designator == "U1"
    assert comp.x == 25.0


def test_netlist_and_pin_connectivity():
    """Test net node linking and electrical classification."""
    pin_vcc = Pin(component_id="comp_u1", pin_number=1, name="VCC", electrical_type=ElectricalType.POWER)
    pin_gnd = Pin(component_id="comp_u1", pin_number=2, name="GND", electrical_type=ElectricalType.GROUND)

    net_3v3 = Net(
        id="net_3v3",
        name="VCC_3V3",
        net_class=NetClass.POWER,
        voltage=3.3,
        nodes=[
            NetNode(component_id="comp_u1", pin_number=1),
            NetNode(component_id="comp_u2", pin_number=8),
        ],
    )
    assert len(net_3v3.nodes) == 2
    assert net_3v3.voltage == 3.3


def test_pcb_builder_from_bom():
    """Test automatic PCB project construction from BOM items."""
    bom = BOM(
        bom_id="bom_test_pcb",
        project_id="test_rover_pcb",
        items=[
            BOMItem(
                bom_item_id="b1",
                component_id="comp_esp32",
                manufacturer="Espressif Systems",
                mpn="ESP32-S3-WROOM-1",
                category="Microcontroller / Compute Unit",
                quantity=1,
                unit_price=385.0,
                extended_price=385.0,
            ),
            BOMItem(
                bom_item_id="b2",
                component_id="comp_lm2596",
                manufacturer="Texas Instruments",
                mpn="LM2596S-3.3",
                category="Power Management / Regulator",
                quantity=1,
                unit_price=89.0,
                extended_price=89.0,
            ),
            BOMItem(
                bom_item_id="b3",
                component_id="comp_bme280",
                manufacturer="Bosch Sensortec",
                mpn="BME280",
                category="Sensors / Environmental",
                quantity=1,
                unit_price=349.0,
                extended_price=349.0,
            ),
        ],
        total_cost=823.0,
    )

    project = PCBBuilder.build_from_bom("test_rover_pcb", bom, board_width=50.0, board_height=40.0)
    assert project.project_id == "test_rover_pcb"
    assert len(project.components) == 3
    assert len(project.nets) >= 4
    assert project.board.width == 50.0
    assert project.board.height == 40.0


def test_wlpcb_serializer_roundtrip():
    """Test serialization and deserialization of .wlpcb format."""
    bom = BOM(bom_id="b1", project_id="p1", items=[], total_cost=0.0)
    project = PCBBuilder.build_from_bom("p1", bom)

    json_str = WLPCBSerializer.to_wlpcb_json(project)
    assert "PCBProject" in json_str or "project_id" in json_str

    reconstructed = WLPCBSerializer.from_wlpcb_json(json_str)
    assert reconstructed.project_id == project.project_id
    assert reconstructed.board.width == project.board.width
